"""Explicit local planning link, independent of Search approval and dispatch."""

import json
from uuid import UUID

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.workspaces import hosted_ad_drafts as ads
from growthtwin.modules.workspaces.models import HostedAdDraft

from .models import CampaignHostedAdChoice, WorkspaceCampaignDraft


def campaign(owner, campaign_id, *, lock=False):
    if not settings.LOCAL_HOSTED_AD_CAMPAIGN_ENABLED:
        raise PermissionDenied
    workspace = ads.admitted_workspace(owner)
    rows = WorkspaceCampaignDraft.objects
    if lock:
        rows = rows.select_for_update(of=("self",))
    return rows.get(
        pk=campaign_id,
        brand__isnull=True,
        workspace=workspace,
        workspace__owner=owner,
        workspace__owner__is_active=True,
    )


def _snapshot(owner, choice):
    draft, png = ads.checked_draft(owner, choice.revision.draft_id)
    revision = draft.history.get(pk=choice.revision_id)
    expected = ads.snapshot_data(draft, revision.revision, revision.content)
    if (
        choice.snapshot != expected
        or draft.workspace_id != choice.campaign.workspace_id
    ):
        raise ValidationError("Seçilen kaydın kaynakları doğrulanamadı.")
    return expected, png


def select(
    *, owner, campaign_id, ad_id, revision, source, expected_version, request_id
):
    if (
        type(ad_id) is not UUID
        or not ad_id.int
        or type(request_id) is not UUID
        or not request_id.int
        or type(revision) is not int
        or not 1 <= revision < 2**31 - 1
        or type(expected_version) is not int
        or not 0 <= expected_version < 2**31 - 1
    ):
        raise ValidationError("Geçerli bir kayıt ve seçim sürümü gerekli.")
    with transaction.atomic():
        plan = campaign(owner, campaign_id, lock=True)
        ads._lock_sources(owner)
        draft, _ = ads.checked_draft(owner, ad_id, lock=True)
        if (
            draft.workspace_id != plan.workspace_id
            or source != draft.source_fingerprint
        ):
            raise ValidationError("Görsel kaynağı değişmiş.")
        existing = (
            CampaignHostedAdChoice.objects.filter(request_id=request_id)
            .select_related("revision", "campaign")
            .first()
        )
        if existing:
            if (
                existing.campaign_id != plan.pk
                or existing.revision.draft_id != draft.pk
                or existing.revision.revision != revision
                or existing.version != expected_version + 1
            ):
                raise ValidationError("İstek farklı bir seçimde kullanılmış.")
            _snapshot(owner, existing)
            return existing
        current = plan.hosted_ad_choices.first()
        if (
            current.version if current else 0
        ) != expected_version or draft.revision != revision:
            raise ValidationError("Kayıt veya seçim değişmiş; güncel seçenekleri açın.")
        saved = draft.history.get(revision=revision)
        return CampaignHostedAdChoice.objects.create(
            campaign=plan,
            revision=saved,
            snapshot=ads.snapshot_data(draft, revision, saved.content),
            version=expected_version + 1,
            request_id=request_id,
        )


def selected(*, owner, campaign_id, version=None):
    with transaction.atomic():
        plan = campaign(owner, campaign_id, lock=True)
        ads._lock_sources(owner)
        choice = plan.hosted_ad_choices.select_related("revision", "campaign").first()
        if choice is None:
            if version is not None:
                raise ValidationError("Görsel seçilmemiş.")
            return None
        if version is not None and choice.version != version:
            raise ValidationError("Görsel seçimi değişmiş; kampanyaya dönün.")
        snapshot, png = _snapshot(owner, choice)
        return choice, snapshot, png


def options(*, owner, campaign_id):
    plan = campaign(owner, campaign_id)
    rows = []
    for draft in HostedAdDraft.objects.filter(
        workspace=plan.workspace, owner=owner
    ).order_by("-updated_at")[:20]:
        try:
            checked, _ = ads.checked_draft(owner, draft.pk)
        except (ValidationError, ValueError):
            continue
        rows.append(checked)
    return rows


def selection_manifest(choice, snapshot):
    """Immutable selection identity only; current campaign names are not pinned."""
    return {
        "schema": "yaparo-campaign-ai-selection-v1",
        "campaign_id": str(choice.campaign_id),
        "workspace_id": str(choice.campaign.workspace_id),
        "choice_id": str(choice.pk),
        "selection_version": choice.version,
        "selected_at": choice.created_at.isoformat(),
        "ad_revision_id": str(choice.revision_id),
        "ad_id": snapshot["draft_id"],
        "ad_revision": snapshot["revision"],
        "profile": snapshot["profile"],
        "source_fingerprint": snapshot["source_fingerprint"],
        "snapshot_sha256": digest(snapshot),
    }


def package_snapshot(*, owner, campaign_id, version):
    choice, snapshot, _ = selected(
        owner=owner, campaign_id=campaign_id, version=version
    )
    return {
        "schema": "yaparo-campaign-ai-package-snapshot-v1",
        "campaign_selection": selection_manifest(choice, snapshot),
        "ad_json": json.dumps(
            snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
    }
