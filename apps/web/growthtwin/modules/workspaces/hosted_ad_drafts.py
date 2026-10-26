"""Owned, source-bound composition of saved AI outputs; no inference or spend."""

import re
from dataclasses import asdict
from uuid import UUID

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from growthtwin.modules.ai_gateway.brand_tasks import digest

from . import hosted_image_trial, hosted_trial
from .models import (
    HostedAdDraft,
    HostedAdRevision,
    HostedImageTrial,
    HostedTextTrial,
    Workspace,
)

PROFILE = "duru-saved-ai-overlay-v1"
SQUARE = "duru-saved-ai-square-v2"
PORTRAIT = "duru-saved-ai-portrait-v2"
LAYOUTS = {
    PROFILE: {
        "label": "Özgün dikey · 768 × 1376",
        "width": 768,
        "height": 1376,
        "mode": "overlay",
    },
    SQUARE: {
        "label": "Kare · 1080 × 1080",
        "width": 1080,
        "height": 1080,
        "mode": "contain",
    },
    PORTRAIT: {
        "label": "Dikey · 1080 × 1350",
        "width": 1080,
        "height": 1350,
        "mode": "contain",
    },
}
LIMITS = {"title": 60, "body": 100, "cta": 30}


def layout(profile):
    if type(profile) is not str or profile not in LAYOUTS:
        raise ValidationError("Kaydedilmiş bir reklam ölçüsü seçin.")
    return dict(LAYOUTS[profile])


def validate_content(value):
    if type(value) is not dict or set(value) != set(LIMITS) | {"color"}:
        raise ValidationError("Taslak alanları doğrulanamadı.")
    for key, maximum in LIMITS.items():
        text = value[key]
        if (
            type(text) is not str
            or not text.strip()
            or any(ord(c) < 32 or ord(c) in (127, 0x2028, 0x2029) for c in text)
        ):
            raise ValidationError("Metinleri tek satır ve gösterilen sınırda girin.")
        try:
            if len(text.encode("utf-16-le")) // 2 > maximum:
                raise ValidationError(
                    "Metin alanı sınırı aşıldı; otomatik kısaltılmadı."
                )
        except UnicodeError:
            raise ValidationError("Metin kodlaması doğrulanamadı.") from None
    if type(value["color"]) is not str or not re.fullmatch(
        r"#[0-9a-fA-F]{6}", value["color"]
    ):
        raise ValidationError("Geçerli bir metin rengi seçin.")
    return dict(value)


def admitted_workspace(owner):
    if not settings.LOCAL_HOSTED_AD_DRAFT_ENABLED:
        raise PermissionDenied
    return hosted_image_trial.admitted_workspace(owner)


def sources(owner, candidate_key=None, *, profile=PROFILE):
    geometry = layout(profile)
    workspace = admitted_workspace(owner)
    text = hosted_trial.read_trial(owner)
    image = hosted_image_trial.read_trial(owner)
    variants = hosted_trial.checked_variants(text)
    if not variants or image is None:
        raise ValidationError(
            "Önce kaydedilmiş metin ve görsel üretimlerini tamamlayın."
        )
    png = hosted_image_trial.checked_image(image)
    if text.workspace_id != workspace.pk or image.workspace_id != workspace.pk:
        raise PermissionDenied
    if candidate_key is None:
        return workspace, text, image, variants, png
    variant = next((v for v in variants if v.key == candidate_key), None)
    if variant is None:
        raise ValidationError("Kaydedilmiş bir metin seçin.")
    manifest = {
        "profile": profile,
        "workspace_id": workspace.pk,
        "owner_id": owner.pk,
        "text": {
            "id": text.pk,
            "source_hash": text.source_hash,
            "profile": text.profile,
            "model": text.model,
            "provider": text.provider,
            "cost_usd": str(text.actual_usd),
            "usage": text.usage,
            "variants": [asdict(v) for v in variants],
        },
        "image": {
            "id": image.pk,
            "source_hash": image.source_hash,
            "profile": image.profile,
            "requested_model": image.model,
            "requested_route": image.provider,
            "cost_usd": str(image.actual_usd),
            "original_sha256": image.original_sha256,
            "png_sha256": image.png_sha256,
            "width": image.width,
            "height": image.height,
            "normalization_tool": image.normalization_tool,
        },
        "candidate": asdict(variant),
    }
    if profile != PROFILE:
        manifest["layout"] = geometry
    # This profile deliberately supports the evaluated portrait, not arbitrary
    # tiny/cropped fixtures. Geometry and font limits are fixed for this layout.
    if (image.width, image.height) != (768, 1376):
        raise ValidationError("Bu görsel taslak düzeninin boyutlarına uymuyor.")
    return workspace, text, image, variant, manifest, png


def checked_draft(owner, draft_id, *, lock=False):
    workspace = admitted_workspace(owner)
    if type(draft_id) is not UUID or not draft_id.int:
        raise ValidationError("Taslak kimliği doğrulanamadı.")
    rows = HostedAdDraft.objects
    if lock:
        rows = rows.select_for_update()
    draft = rows.get(pk=draft_id, workspace=workspace, owner=owner)
    _, text, image, _, manifest, png = sources(
        owner, draft.candidate_key, profile=draft.profile
    )
    if (
        draft.text_trial_id != text.pk
        or draft.image_trial_id != image.pk
        or draft.source_manifest != manifest
        or draft.source_fingerprint != digest(manifest)
    ):
        raise ValidationError("Taslağın kaynakları doğrulanamadı; yeniden bağlanmadı.")
    validate_content(draft.content)
    current = draft.history.filter(revision=draft.revision).first()
    if current is None or current.content != draft.content:
        raise ValidationError("Taslak geçmişi güncel kayıtla eşleşmiyor.")
    return draft, png


def _lock_sources(owner):
    workspace = admitted_workspace(owner)
    Workspace.objects.select_for_update().get(
        pk=workspace.pk, owner=owner, owner__is_active=True
    )
    HostedTextTrial.objects.select_for_update().get(workspace=workspace, owner=owner)
    HostedImageTrial.objects.select_for_update().get(workspace=workspace, owner=owner)


def create_draft(*, owner, candidate_key, expected_source, profile=PROFILE):
    with transaction.atomic():
        _lock_sources(owner)
        workspace, text, image, variant, manifest, _ = sources(
            owner, candidate_key, profile=profile
        )
        if type(expected_source) is not str or expected_source != digest(manifest):
            raise ValidationError("Üretim kaydı değişmiş; güncel seçenekleri açın.")
        existing = HostedAdDraft.objects.filter(
            text_trial=text,
            image_trial=image,
            candidate_key=candidate_key,
            profile=profile,
        ).first()
        if existing is not None:
            return checked_draft(owner, existing.pk)[0]
        content = validate_content(
            {
                "title": variant.headline,
                "body": variant.body,
                "cta": variant.call_to_action,
                "color": "#244c3b",
            }
        )
        draft = HostedAdDraft.objects.create(
            workspace=workspace,
            owner=owner,
            text_trial=text,
            image_trial=image,
            candidate_key=candidate_key,
            profile=profile,
            source_fingerprint=digest(manifest),
            source_manifest=manifest,
            content=content,
        )
        HostedAdRevision.objects.create(draft=draft, revision=1, content=content)
        return draft


def save_draft(*, owner, draft_id, expected_revision, expected_source, content):
    content = validate_content(content)
    if type(expected_revision) is not int or not 1 <= expected_revision < 2**31 - 1:
        raise ValidationError("Geçerli kayıt sürümü gerekli.")
    with transaction.atomic():
        _lock_sources(owner)
        draft, _ = checked_draft(owner, draft_id, lock=True)
        if (
            draft.revision != expected_revision
            or draft.source_fingerprint != expected_source
        ):
            raise ValidationError(
                "Taslak başka sekmede değişmiş; eski kayıt yazılmadı."
            )
        if draft.content == content:
            return draft
        changed = HostedAdDraft.objects.filter(
            pk=draft.pk, revision=expected_revision, source_fingerprint=expected_source
        ).update(
            content=content, revision=expected_revision + 1, updated_at=timezone.now()
        )
        if changed != 1:
            raise ValidationError("Taslak değişmiş; eski kayıt yazılmadı.")
        HostedAdRevision.objects.create(
            draft=draft, revision=expected_revision + 1, content=content
        )
        draft.refresh_from_db()
        return draft
