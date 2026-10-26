"""Offline owned composition; no generation, credential or budget operation."""

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from growthtwin.modules.ai_gateway.brand_tasks import digest

from . import brand_generation as generation
from .creative_documents import _brand, _uuid, _version
from .hosted_ad_drafts import validate_content
from .models import BrandAdDraft, BrandAdRevision, BrandGenerationAttempt

PROFILE = "brand-saved-ai-overlay-v1"


def enabled():
    if not settings.DEBUG or not settings.LOCAL_BRAND_AD_ENABLED:
        raise PermissionDenied


def pair(owner, brand_id, text_request, image_request, candidate_key):
    enabled()
    text = generation.read(owner, brand_id, text_request)
    image = generation.read(owner, brand_id, image_request)
    if any(
        row is None or row.status != "completed" or row.budget_state != "settled"
        for row in (text, image)
    ):
        raise ValidationError("Tamamlanmış kayıtlı metin ve görsel seçin.")
    a, b = text.request, image.request
    if (
        (text.kind, image.kind) != ("copy", "image")
        or a.identity_id != b.identity_id
        or a.source_revision_id != b.source_revision_id
    ):
        raise ValidationError("Aynı marka kimliği ve kaynak sürümü gerekli.")
    if (image.output["width"], image.output["height"]) != (768, 1376):
        raise ValidationError("Bu ilk taslak düzeni768×1376 görsel gerektirir.")
    candidate = next(
        (v for v in text.output["variants"] if v["key"] == candidate_key), None
    )
    if candidate is None:
        raise ValidationError("Kaydedilmiş bir metin seçin.")
    manifest = {
        "schema": "yaparo-brand-ad-sources-v1",
        "profile": PROFILE,
        "brand_id": str(a.brand_id),
        "identity_id": str(a.identity_id),
        "owner_id": str(owner.pk),
        "brand_name": a.envelope["brand_name"],
        "identity": a.envelope["identity"],
        "candidate": candidate,
        "text": {
            "id": str(text.pk),
            "request": a.envelope,
            "fingerprint": text.fingerprint,
            "input_hash": text.input_hash,
            "cost_usd": str(text.actual_usd),
            "output": text.output,
        },
        "image": {
            "id": str(image.pk),
            "request": b.envelope,
            "fingerprint": image.fingerprint,
            "input_hash": image.input_hash,
            "cost_usd": str(image.actual_usd),
            "output": image.output,
        },
    }
    return text, image, candidate, manifest


def _sources(owner, brand_id, text_request, image_request, candidate_key):
    # Caller holds brand first, matching the source-document lock graph.
    result = pair(owner, brand_id, text_request, image_request, candidate_key)
    list(
        BrandGenerationAttempt.objects.select_for_update()
        .filter(pk__in=[result[0].pk, result[1].pk])
        .order_by("pk")
    )
    # Re-read after acquiring job locks; no mutable result bypasses validation.
    return pair(owner, brand_id, text_request, image_request, candidate_key)


def _checked(owner, brand_id, draft_id):
    draft = BrandAdDraft.objects.get(pk=draft_id, brand_id=brand_id)
    text, image, _, manifest = _sources(
        owner,
        brand_id,
        draft.text_attempt.request_id,
        draft.image_attempt.request_id,
        draft.candidate_key,
    )
    draft = BrandAdDraft.objects.select_for_update().get(pk=draft.pk, brand_id=brand_id)
    if (
        draft.profile != PROFILE
        or draft.identity_id != text.request.identity_id
        or draft.text_attempt_id != text.pk
        or draft.image_attempt_id != image.pk
        or draft.source_manifest != manifest
        or draft.source_fingerprint != digest(manifest)
    ):
        raise ValidationError("Taslağın kaynakları doğrulanamadı.")
    validate_content(draft.content)
    if draft.history.get(revision=draft.revision).content != draft.content:
        raise ValidationError("Taslak geçmişi eşleşmiyor.")
    return draft, bytes(image.png)


def checked(owner, brand_id, draft_id):
    enabled()
    _uuid(draft_id)
    with transaction.atomic():
        _brand(owner, brand_id, lock=True)
        return _checked(owner, brand_id, draft_id)


def create(
    *, owner, brand_id, text_request, image_request, candidate_key, expected_source
):
    enabled()
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        text, image, candidate, manifest = _sources(
            owner, brand_id, text_request, image_request, candidate_key
        )
        if type(expected_source) is not str or expected_source != digest(manifest):
            raise ValidationError("Kaynak seçimi değişmiş.")
        existing = BrandAdDraft.objects.filter(
            text_attempt=text, image_attempt=image, candidate_key=candidate_key
        ).first()
        if existing:
            return _checked(owner, brand_id, existing.pk)[0]
        content = validate_content(
            {
                "title": candidate["headline"],
                "body": candidate["body"],
                "cta": candidate["call_to_action"],
                "color": manifest["identity"]["primary_color"],
            }
        )
        draft = BrandAdDraft.objects.create(
            brand=brand,
            identity=text.request.identity,
            text_attempt=text,
            image_attempt=image,
            candidate_key=candidate_key,
            profile=PROFILE,
            source_manifest=manifest,
            source_fingerprint=digest(manifest),
            content=content,
        )
        BrandAdRevision.objects.create(draft=draft, revision=1, content=content)
        return draft


def save(*, owner, brand_id, draft_id, expected_revision, expected_source, content):
    enabled()
    _uuid(draft_id)
    _version(expected_revision)
    if expected_revision >= 2**31 - 1:
        raise ValidationError("Taslak sürümü sınırı.")
    content = validate_content(content)
    with transaction.atomic():
        _brand(owner, brand_id, lock=True)
        draft, _ = _checked(owner, brand_id, draft_id)
        if (
            draft.revision != expected_revision
            or draft.source_fingerprint != expected_source
        ):
            raise ValidationError("Taslak başka sekmede değişmiş.")
        if draft.content != content:
            changed = BrandAdDraft.objects.filter(
                pk=draft.pk,
                revision=expected_revision,
                source_fingerprint=expected_source,
            ).update(
                content=content,
                revision=expected_revision + 1,
                updated_at=timezone.now(),
            )
            if changed != 1:
                raise ValidationError("Taslak değişmiş.")
            BrandAdRevision.objects.create(
                draft=draft, revision=expected_revision + 1, content=content
            )
            draft.refresh_from_db()
        return draft
