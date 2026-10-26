"""Explicit stale-safe offline candidate write; no campaign reselection/dispatch."""

from copy import deepcopy
from dataclasses import asdict

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q, Subquery

from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.workspaces.ai_context import validate_selected_brand_result
from growthtwin.modules.workspaces.creative_documents import (
    _brand,
    _document,
    _version,
    _write_document,
)
from growthtwin.modules.workspaces.creative_scenes import SceneValidationError, _text

from .brand_copy import preview_brand_copy
from .models import CampaignDesignChoice


def fits_scene_copy(text):
    try:
        _text(text)
    except SceneValidationError:
        return False
    return True


def apply_brand_copy(
    *,
    owner,
    draft_id,
    selection_version,
    task_id,
    request_fingerprint,
    candidate_key,
    candidate_digest,
    expected_revision,
    fields,
):
    if not settings.DEBUG or not settings.SYNTHETIC_BRAND_COPY_APPLY_ENABLED:
        raise PermissionDenied("Yerel örnek metin uygulama kapalı.")
    _version(expected_revision)
    if fields not in ("title", "title_subtitle"):
        raise ValidationError("Uygulanacak metin alanları geçersiz.")
    request, result = preview_brand_copy(
        owner=owner,
        draft_id=draft_id,
        selection_version=selection_version,
        task_id=task_id,
    )
    if request.fingerprint != request_fingerprint:
        raise ValidationError("Görev kaynağı değişmiş.")
    candidate = next(
        (row for row in result.creative_result.variants if row.key == candidate_key),
        None,
    )
    if candidate is None or digest(asdict(candidate)) != candidate_digest:
        raise ValidationError("Aday metin değişmiş.")
    if not fits_scene_copy(candidate.headline) or (
        fields == "title_subtitle" and not fits_scene_copy(candidate.body)
    ):
        raise ValidationError(
            "Aday metin tasarım alanına sığmıyor; metin kısaltılmadı."
        )
    with transaction.atomic():
        # Match the existing editor brand/workspace/document lock order. Never
        # lock the draft here: legacy campaign editing locks draft/workspace.
        brand = _brand(owner, request.context.brand_id, lock=True)
        document = _document(brand, request.context.document_id, lock=True)
        validate_selected_brand_result(
            owner=owner, draft_id=draft_id, request=request, result=result
        )
        scene = deepcopy(document.scene)
        for layer in scene["layers"]:
            if layer["id"] == "title":
                layer["text"] = candidate.headline
            elif layer["id"] == "subtitle" and fields == "title_subtitle":
                layer["text"] = candidate.body
        if scene == document.scene:
            raise ValidationError(
                "Seçilen metinler tasarımda zaten aynı; yeni kayıt oluşturulmadı."
            )
        latest = (
            CampaignDesignChoice.objects.filter(draft_id=draft_id)
            .order_by("-version")
            .values("pk")[:1]
        )
        eligible = CampaignDesignChoice.objects.filter(
            pk=request.context.selection_id,
            pk__in=Subquery(latest),
            draft_id=draft_id,
            version=selection_version,
            snapshot_id=request.context.snapshot_id,
            snapshot__document_id=document.pk,
            draft__workspace_id=request.context.workspace_id,
            draft__workspace__owner=owner,
            draft__workspace__owner__is_active=True,
            snapshot__document__identity__brand_id=brand.pk,
            snapshot__document__identity__brand__workspace_id=request.context.workspace_id,
            snapshot__document__identity__brand__workspace__owner=owner,
            snapshot__document__identity__brand__workspace__owner__is_active=True,
            snapshot__document__identity__brand__is_archived=False,
        ).values("snapshot__document_id")[:1]
        return _write_document(
            document,
            owner,
            expected_revision,
            scene,
            eligibility=Q(pk=Subquery(eligible)),
        )
