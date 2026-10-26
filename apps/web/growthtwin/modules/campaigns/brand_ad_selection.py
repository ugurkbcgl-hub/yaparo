"""Owned-brand campaign planning from saved creatives; zero external actions."""

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from growthtwin.modules.workspaces import brand_ad_drafts as ads
from growthtwin.modules.workspaces.creative_documents import (
    _brand,
    _owner,
    _uuid,
    _version,
)
from growthtwin.modules.workspaces.models import BrandAdDraft

from .models import CampaignBrandAdChoice, WorkspaceCampaignDraft


def enabled():
    ads.enabled()
    if not settings.LOCAL_BRAND_CAMPAIGN_ENABLED:
        raise PermissionDenied


def campaign(owner, campaign_id, *, lock=False):
    enabled()
    _owner(owner)
    rows = WorkspaceCampaignDraft.objects
    if lock:
        rows = rows.select_for_update(of=("self",))
    return rows.get(
        pk=campaign_id,
        brand__isnull=False,
        workspace__owner=owner,
        workspace__owner__is_active=True,
        brand__workspace__owner=owner,
        brand__is_archived=False,
    )


def snapshot(ad, revision):
    if revision.draft_id != ad.pk:
        raise ValidationError("Taslak sürümü eşleşmiyor.")
    return {
        "schema": "yaparo-brand-campaign-visual-v1",
        "ad_id": str(ad.pk),
        "ad_revision": revision.revision,
        "brand_id": str(ad.brand_id),
        "identity_id": str(ad.identity_id),
        "profile": ad.profile,
        "source_fingerprint": ad.source_fingerprint,
        "source_manifest": ad.source_manifest,
        "content": ads.validate_content(revision.content),
    }


def _snapshot(owner, choice):
    ad, png = ads.checked(owner, choice.campaign.brand_id, choice.revision.draft_id)
    revision = ad.history.get(pk=choice.revision_id)
    expected = snapshot(ad, revision)
    if (
        choice.campaign.workspace_id != ad.brand.workspace_id
        or choice.snapshot != expected
    ):
        raise ValidationError("Seçilen reklamın kaynakları doğrulanamadı.")
    return expected, png


def _request(revision, request_id):
    _version(revision)
    _uuid(request_id)
    if revision >= 2**31 - 1:
        raise ValidationError("Kayıt sınırı.")


def start(*, owner, brand_id, ad_id, revision, source, request_id):
    enabled()
    _uuid(ad_id)
    _request(revision, request_id)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        ad, _ = ads.checked(owner, brand_id, ad_id)
        if source != ad.source_fingerprint:
            raise ValidationError("Kaynak değişmiş.")
        existing = (
            CampaignBrandAdChoice.objects.filter(request_id=request_id)
            .select_related("campaign", "revision")
            .first()
        )
        if existing:
            if (
                existing.kind != "create"
                or existing.version != 1
                or existing.campaign.workspace_id != brand.workspace_id
                or existing.campaign.brand_id != brand.pk
                or existing.revision.draft_id != ad.pk
                or existing.revision.revision != revision
            ):
                raise ValidationError("İstek farklı bir kampanyada kullanılmış.")
            # Read-only replay: never acquire an existing campaign lock while
            # holding brand/workspace; existing campaign paths lock campaign first.
            _snapshot(owner, existing)
            return existing
        if ad.revision != revision:
            raise ValidationError("Taslak değişmiş; güncel kaydı açın.")
        plan = WorkspaceCampaignDraft.objects.create(
            workspace=brand.workspace,
            brand=brand,
            brand_name=ad.source_manifest["brand_name"],
            name=ad.source_manifest["brand_name"],
            brief="Sentetik marka kampanya planı. "
            + ad.source_manifest["text"]["request"]["brief"]["description"],
            target_city="Ankara",
            media_budget_minor=500000,
        )
        saved = ad.history.get(revision=revision)
        return CampaignBrandAdChoice.objects.create(
            campaign=plan,
            revision=saved,
            snapshot=snapshot(ad, saved),
            version=1,
            request_id=request_id,
            kind="create",
        )


def select(
    *, owner, campaign_id, ad_id, revision, source, expected_version, request_id
):
    _uuid(ad_id)
    _request(revision, request_id)
    if type(expected_version) is not int or not 0 <= expected_version < 2**31 - 1:
        raise ValidationError("Geçerli seçim sürümü gerekli.")
    with transaction.atomic():
        plan = campaign(owner, campaign_id, lock=True)
        ad, _ = ads.checked(owner, plan.brand_id, ad_id)
        if (
            plan.workspace_id != ad.brand.workspace_id
            or source != ad.source_fingerprint
        ):
            raise ValidationError("Marka veya kaynak eşleşmiyor.")
        existing = (
            CampaignBrandAdChoice.objects.filter(request_id=request_id)
            .select_related("campaign", "revision")
            .first()
        )
        if existing:
            if (
                existing.kind != "select"
                or existing.campaign_id != plan.pk
                or existing.revision.draft_id != ad.pk
                or existing.revision.revision != revision
                or existing.version != expected_version + 1
            ):
                raise ValidationError("İstek farklı bir seçimde kullanılmış.")
            _snapshot(owner, existing)
            return existing
        current = plan.brand_ad_choices.first()
        if (
            current.version if current else 0
        ) != expected_version or ad.revision != revision:
            raise ValidationError("Taslak veya seçim değişmiş.")
        saved = ad.history.get(revision=revision)
        return CampaignBrandAdChoice.objects.create(
            campaign=plan,
            revision=saved,
            snapshot=snapshot(ad, saved),
            version=expected_version + 1,
            request_id=request_id,
            kind="select",
        )


def selected(*, owner, campaign_id, version=None):
    with transaction.atomic():
        plan = campaign(owner, campaign_id, lock=True)
        choice = plan.brand_ad_choices.select_related("campaign", "revision").first()
        if choice is None:
            raise ValidationError("Marka reklamı seçilmemiş.")
        if version is not None and (
            type(version) is not int or choice.version != version
        ):
            raise ValidationError("Seçim değişmiş; kampanyaya dönün.")
        data, png = _snapshot(owner, choice)
        return choice, data, png


def options(*, owner, campaign_id):
    plan = campaign(owner, campaign_id)
    result = []
    for ad in BrandAdDraft.objects.filter(brand_id=plan.brand_id).order_by(
        "-updated_at"
    )[:20]:
        try:
            checked, _ = ads.checked(owner, plan.brand_id, ad.pk)
        except (ValidationError, ValueError, PermissionDenied):
            continue
        result.append(checked)
    return result
