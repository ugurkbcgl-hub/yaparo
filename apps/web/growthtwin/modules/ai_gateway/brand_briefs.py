"""Provider-neutral brief binding; metadata only, never execution authority."""

from copy import deepcopy

from django.core.exceptions import ValidationError

from .brand_tasks import digest

SCHEMA = "yaparo-brand-production-request-v1"
LIMITS = {"description": 1200, "audience": 200}
OBJECTIVES = ("awareness", "traffic", "leads")
DELIVERABLES = ("copy", "image")


def validate_brief(value):
    if type(value) is not dict or set(value) != set(LIMITS) | {
        "objective",
        "deliverable",
    }:
        raise ValidationError("Talep alanları doğrulanamadı.")
    for key, limit in LIMITS.items():
        text = value[key]
        if (
            type(text) is not str
            or not text.strip()
            or any(
                (ord(c) < 32 and not (key == "description" and c in "\t\r\n"))
                or ord(c) in (127, 0x2028, 0x2029)
                for c in text
            )
        ):
            raise ValidationError("Geçerli bir sentetik açıklama ve hedef kitle girin.")
        try:
            if len(text.encode("utf-16-le")) // 2 > limit:
                raise ValidationError("Talep alanı sınırı aşıldı.")
        except UnicodeError:
            raise ValidationError("Metin kodlaması doğrulanamadı.") from None
    if value["objective"] not in OBJECTIVES or value["deliverable"] not in DELIVERABLES:
        raise ValidationError("Desteklenen amaç ve içerik türünü seçin.")
    return dict(value)


def mock_receipt(envelope):
    """Local contract rehearsal only; does not execute a model or create content."""
    keys = {
        "schema",
        "request_id",
        "brief_version",
        "workspace_id",
        "brand_id",
        "brand_name",
        "identity_id",
        "identity",
        "source",
        "brief",
        "language",
        "execution",
    }
    if (
        type(envelope) is not dict
        or set(envelope) != keys
        or envelope.get("schema") != SCHEMA
    ):
        raise ValidationError("Yalnız yerel bağlama sözleşmesi kullanılabilir.")
    execution = envelope.get("execution")
    if (
        type(execution) is not dict
        or set(execution) != {"authorized", "max_cost_microusd", "provider"}
        or execution["authorized"] is not False
        or type(execution["max_cost_microusd"]) is not int
        or execution["max_cost_microusd"] != 0
        or execution["provider"] is not None
    ):
        raise ValidationError("Yalnız yerel bağlama sözleşmesi kullanılabilir.")
    validate_brief(envelope["brief"])
    return {
        "schema": "yaparo-brand-binding-mock-v1",
        "request_id": envelope["request_id"],
        "request_fingerprint": digest(envelope),
        "status": "binding_checked",
        "cost_microusd": 0,
        "publishable": False,
    }


def validate_mock_receipt(envelope, receipt):
    expected = mock_receipt(envelope)
    if (
        type(receipt) is not dict
        or receipt != expected
        or type(receipt.get("cost_microusd")) is not int
        or receipt.get("publishable") is not False
    ):
        raise ValidationError("Örnek sonuç üretim talebiyle eşleşmiyor.")
    return deepcopy(receipt)
