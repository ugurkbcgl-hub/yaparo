"""Versioned owned local plan; no legacy operational fields or external work."""

from datetime import date
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.formats import number_format
from django.views.decorators.debug import sensitive_variables

from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.workspaces.creative_documents import _brand, _uuid

from . import brand_ad_selection
from .models import CampaignPlanRevision

GOALS = {
    "awareness": "Markayı tanıtmak",
    "traffic": "Site ziyaretleri",
    "leads": "Talep toplamak",
}
FIELDS = {"goal", "audience", "region", "budget_minor", "start", "end"}
MAX_BUDGET_MINOR = 999999999


def today():
    return timezone.localdate(timezone=ZoneInfo("Europe/Istanbul"))


def enabled():
    brand_ad_selection.enabled()
    if not settings.LOCAL_BRAND_CAMPAIGN_SETTINGS_ENABLED:
        raise PermissionDenied


def _text(value, maximum):
    if (
        type(value) is not str
        or not value.strip()
        or value != value.strip()
        or any(ord(c) < 32 or ord(c) in (127, 0x2028, 0x2029) for c in value)
    ):
        raise ValidationError("Tek satır, geçerli bir plan açıklaması girin.")
    try:
        if len(value.encode("utf-16-le")) // 2 > maximum:
            raise ValidationError("Plan alanı uzunluk sınırını aşıyor.")
    except UnicodeError:
        raise ValidationError("Metin kodlaması geçersiz.") from None
    return value


def validate(value):
    if type(value) is not dict or set(value) != FIELDS:
        raise ValidationError("Plan alanları doğrulanamadı.")
    if type(value["goal"]) is not str or value["goal"] not in GOALS:
        raise ValidationError("Bir plan hedefi seçin.")
    _text(value["audience"], 200)
    _text(value["region"], 100)
    if (
        type(value["budget_minor"]) is not int
        or not 1 <= value["budget_minor"] <= MAX_BUDGET_MINOR
    ):
        raise ValidationError("Geçerli bir toplam plan bütçesi girin.")
    dates = []
    for field in ("start", "end"):
        try:
            if type(value[field]) is not str:
                raise ValueError
            parsed = date.fromisoformat(value[field])
            if parsed.isoformat() != value[field]:
                raise ValueError
            dates.append(parsed)
        except (ValueError, TypeError):
            raise ValidationError(
                "Geçerli bir başlangıç ve bitiş tarihi girin."
            ) from None
    # Both endpoints count: same-day plan is one day.
    if not 1 <= (dates[1] - dates[0]).days + 1 <= 365:
        raise ValidationError("Plan süresi başlangıç dahil 1–365 gün olmalı.")
    return dict(value)


def _scope(owner, campaign_id):
    enabled()
    plan = brand_ad_selection.campaign(owner, campaign_id, lock=True)
    brand = _brand(owner, plan.brand_id, lock=True)
    if brand.workspace_id != plan.workspace_id:
        raise ValidationError("Marka ve kampanya çalışma alanı eşleşmiyor.")
    return plan


def _payload(owner, plan, values):
    return {
        "schema": "yaparo-local-campaign-plan-v1",
        "campaign_id": str(plan.pk),
        "workspace_id": str(plan.workspace_id),
        "brand_id": str(plan.brand_id),
        "owner_id": str(owner.pk),
        "currency": "TRY",
        "timezone": "Europe/Istanbul",
        "settings": validate(values),
    }


def _checked(owner, plan, row):
    if row is None:
        return None
    if type(row.payload) is not dict or "settings" not in row.payload:
        raise ValidationError("Kaydedilmiş plan doğrulanamadı.")
    expected = _payload(owner, plan, row.payload["settings"])
    if (
        row.campaign_id != plan.pk
        or row.created_by_id != owner.pk
        or type(row.version) is not int
        or not 1 <= row.version <= 2**31 - 1
        or row.payload != expected
        or row.fingerprint != digest(expected)
    ):
        raise ValidationError("Plan kaydı ve kaynak bağı eşleşmiyor.")
    return row


def read(*, owner, campaign_id):
    with transaction.atomic():
        plan = _scope(owner, campaign_id)
        return _checked(owner, plan, plan.planning_revisions.first())


@sensitive_variables()
def save(*, owner, campaign_id, expected_version, request_id, values):
    _uuid(request_id)
    if type(expected_version) is not int or not 0 <= expected_version < 2**31 - 1:
        raise ValidationError("Geçerli plan sürümü gerekli.")
    values = validate(values)
    with transaction.atomic():
        plan = _scope(owner, campaign_id)
        payload = _payload(owner, plan, values)
        existing = CampaignPlanRevision.objects.filter(request_id=request_id).first()
        if existing:
            if (
                existing.campaign_id != plan.pk
                or existing.version != expected_version + 1
                or existing.payload != payload
            ):
                raise ValidationError("İstek başka bir plan kaydında kullanılmış.")
            return _checked(owner, plan, existing)
        current = _checked(owner, plan, plan.planning_revisions.first())
        if (current.version if current else 0) != expected_version:
            raise ValidationError("Plan başka sekmede değişmiş; güncel kaydı açın.")
        # Fresh check after scope locks; historical read/replay never expires.
        if date.fromisoformat(values["start"]) < today():
            raise ValidationError("Başlangıç bugün veya sonrasında olmalı.")
        return CampaignPlanRevision.objects.create(
            campaign=plan,
            created_by=owner,
            version=expected_version + 1,
            request_id=request_id,
            payload=payload,
            fingerprint=digest(payload),
        )


def summary(row):
    if row is None:
        return None
    values = row.payload["settings"]
    start, end = date.fromisoformat(values["start"]), date.fromisoformat(values["end"])
    return {
        "version": row.version,
        "goal": GOALS[values["goal"]],
        "audience": values["audience"],
        "region": values["region"],
        "budget": number_format(
            Decimal(values["budget_minor"]) / 100, decimal_pos=2, force_grouping=True
        )
        + " TRY",
        "start": start,
        "end": end,
        "days": (end - start).days + 1,
    }


def context(owner, campaign_id):
    try:
        return {
            "campaign_setup_enabled": True,
            "saved_plan": summary(read(owner=owner, campaign_id=campaign_id)),
        }
    except PermissionDenied:
        return {"campaign_setup_enabled": False, "saved_plan": None}
