"""Derive literal outcome semantics from server bank-valid declarations only."""

import json
from dataclasses import dataclass

from .bank import INTENT_LABELS, fields_for, outcome_label
from .contracts import ContractError, _digest
from .validation import VALIDATOR_VERSION, AcceptedBrief

VERSION = "yaparo-server-brief-analysis-v1"
DEFINITIONS = {
    "remember": ("remember_message", "Mesaj hatırlanması", "Mesajı hatırla"),
    "understand": ("understand_message", "Mesajın anlaşılması", "Bilgileri incele"),
    "traffic": ("destination_visits", "Hedef sayfa ziyaretleri", "Sayfayı ziyaret et"),
    "visit": ("physical_visits", "Fiziksel ziyaretler", "Ziyaret bilgilerini gör"),
    "contact": ("contact_requests", "İletişim talepleri", "İletişime geç"),
    "install": ("app_installs", "Uygulama indirmeleri", "Uygulamayı indir"),
    "purchase": ("completed_purchases", "Tamamlanan satın almalar", "Satın al"),
    "message": ("message_requests", "Başlatılan mesaj görüşmeleri", "Mesaj gönder"),
    "call": ("phone_calls", "Telefon aramaları", "Telefonla ara"),
    "register": ("completed_registrations", "Tamamlanan kayıtlar", "Kayıt ol"),
    "ticket": ("completed_ticket_purchases", "Tamamlanan bilet alımları", "Bilet al"),
    "lead_form": (
        "submitted_lead_requests",
        "İletilen talep formları",
        "Talebini ilet",
    ),
    "quote": ("quote_requests", "Teklif talepleri", "Teklif iste"),
    "book": ("confirmed_appointments", "Onaylanan randevular", "Randevu al"),
    "meeting": ("scheduled_meetings", "Planlanan görüşmeler", "Görüşme ayarla"),
    "apply": ("job_applications", "İş başvuruları", "Başvur"),
    "donate": (
        "completed_monetary_donations",
        "Tamamlanan para bağışları",
        "Bağış bilgilerini incele",
    ),
    "materials": (
        "received_material_contributions",
        "Teslim alınan malzeme destekleri",
        "Malzeme desteği ver",
    ),
    "volunteer": (
        "volunteer_applications",
        "Gönüllü başvuruları",
        "Gönüllü başvurusu yap",
    ),
    "share": ("content_shares", "İçerik paylaşımları", "Çağrıyı paylaş"),
    "follow": ("new_followers", "Yeni takipçiler", "Hesabı takip et"),
    "join": ("community_memberships", "Topluluk katılımları", "Topluluğa katıl"),
    "subscribe": (
        "started_subscriptions",
        "Başlatılan üyelik veya abonelikler",
        "Üyeliği başlat",
    ),
}
COMMUNICATION = dict(
    zip(
        (
            "promote",
            "sell",
            "event",
            "lead",
            "hire",
            "fundraise",
            "announce",
            "community",
            "reputation",
        ),
        (
            "product_service_intro",
            "sale_promotion",
            "event",
            "lead_request",
            "recruitment",
            "fundraising",
            "announcement",
            "membership",
            "reputation",
        ),
        strict=True,
    )
)


def _projection(intent, outcome, a):
    pair = {
        "remember": ("remember", "awareness"),
        "understand": ("understand", "awareness"),
        "traffic": ("visit_website", "traffic"),
        "call": ("call", "calls_messages"),
        "donate": ("donate", "donation"),
        "install": ("download_app", "app_install"),
    }.get(outcome)
    if outcome == "visit" and intent != "event":
        pair = ("visit_store", "store_visits")
    if outcome == "purchase" and a.get("action_checkout") in {"website", "marketplace"}:
        pair = (
            "buy_online" if a["action_checkout"] == "website" else "buy_marketplace",
            "ecommerce_purchase",
        )
    if outcome == "message" and a.get("action_message_method") == "whatsapp":
        pair = ("message_whatsapp", "calls_messages")
    if outcome == "contact":
        if a.get("action_contact") == "phone":
            pair = ("call", "calls_messages")
        elif a.get("action_contact") == "form":
            pair = ("fill_form", "lead_generation")
        elif (
            a.get("action_contact") == "message"
            and a.get("action_message_method") == "whatsapp"
        ):
            pair = ("message_whatsapp", "calls_messages")
    if outcome == "lead_form" and a.get("action_lead_method") == "form":
        pair = ("fill_form", "lead_generation")
    if outcome == "book" and a.get("action_booking") == "page":
        pair = ("book_appointment", "appointment")
    if outcome == "register" and intent == "event":
        pair = ("register_event", "event_registration")
    if outcome == "apply" and a.get("action_apply_method") in {"form", "career"}:
        pair = ("apply_job", "job_application")
    return (
        {
            "communication": COMMUNICATION[intent],
            "action": pair[0],
            "goal": pair[1],
            "scope": "taxonomy_only",
            "qualified": False,
        }
        if pair
        else None
    )


def _destination(intent, outcome, a):
    d = dict(
        kind="none",
        channel=None,
        method=None,
        url=None,
        phone=None,
        email=None,
        address=None,
        mapUrl=None,
        required=False,
        missing=[],
        verified=False,
    )

    def link(field="action_url", kind="web"):
        d.update(kind=kind, channel="web", url=a.get(field), required=True)
        if not d["url"]:
            d["missing"].append(field)

    def phone():
        d.update(
            kind="phone", channel="phone", phone=a.get("action_phone"), required=True
        )
        if not d["phone"]:
            d["missing"].append("action_phone")

    def email():
        d.update(
            kind="email", channel="email", email=a.get("action_email"), required=True
        )
        if not d["email"]:
            d["missing"].append("action_email")

    def place(prefix):
        d.update(
            kind="location",
            channel="physical",
            address=a.get(prefix + "_address"),
            mapUrl=a.get(prefix + "_map_url"),
            required=True,
        )
        if not d["address"] and not d["mapUrl"]:
            d["missing"].append(prefix + "_address_or_map")

    def message():
        d["method"] = a.get("action_message_method")
        if d["method"] == "whatsapp":
            phone()
            d.update(kind="message", channel="whatsapp")
        elif d["method"] == "social":
            link("action_profile_url", "message")
            d["channel"] = "social"
        elif d["method"] == "email":
            email()
            d["kind"] = "message"
        else:
            d.update(kind="unresolved", required=True)
            d["missing"].append("action_message_method")

    def method(value):
        d["method"] = value
        if value in {
            "page",
            "system",
            "form",
            "career",
            "website",
            "marketplace",
            "official_page",
            "platform",
        }:
            link()
        elif value == "phone":
            phone()
        elif value == "email":
            email()
        elif value == "message":
            message()
        elif value in {"store", "dropoff"}:
            place("action_location")
        elif value in {"other", "new"}:
            d.update(kind="unresolved", required=True)
            d["missing"].append(
                "form_not_created"
                if value == "new"
                else "custom_destination_not_verified"
            )

    if outcome == "traffic":
        link()
    elif outcome == "visit":
        place("event_location" if intent == "event" else "action_location")
    elif outcome == "call":
        phone()
    elif outcome == "message":
        message()
    elif outcome in {
        "contact",
        "purchase",
        "lead_form",
        "quote",
        "book",
        "meeting",
        "register",
        "ticket",
        "join",
        "subscribe",
        "apply",
        "donate",
        "volunteer",
    }:
        key = {
            "contact": "contact",
            "purchase": "checkout",
            "lead_form": "lead_method",
            "quote": "lead_method",
            "book": "booking",
            "meeting": "booking",
            "apply": "apply_method",
            "donate": "donation_method",
            "volunteer": "volunteer_apply",
        }.get(outcome, "join_method")
        method(a.get("action_" + key))
    elif outcome == "materials":
        delivery = a.get("action_delivery")
        if delivery == "dropoff":
            place("action_location")
        elif delivery in {"pickup", "contact"}:
            message()
        else:
            method(delivery)
        d["deliveryMethod"] = delivery
    elif outcome == "follow":
        link("action_profile_url", "profile")
    elif outcome == "share":
        d.update(kind="share", url=a.get("action_share_url"), channel="user_selected")
        if not d["url"]:
            d["missing"].append("share_content_not_created")
    elif outcome == "install":
        d.update(
            kind="app_store",
            channel="app",
            method=a.get("action_app_platform"),
            required=True,
            androidUrl=a.get("action_android_url"),
            iosUrl=a.get("action_ios_url"),
        )
        for platform in ("android", "ios"):
            if d["method"] in (platform, "both") and not a.get(
                "action_" + platform + "_url"
            ):
                d["missing"].append("action_" + platform + "_url")
    return d


def _derive(brief):
    s = json.loads(brief.canonical_snapshot)
    intent, outcome, a = s["intent"], s["outcome"], s["answers"]
    fields = fields_for(intent, outcome, a)

    def label(field):
        value = a[field.id]
        options = dict(field.options)
        if value == "other" and field.id + "_other" in a:
            return a[field.id + "_other"]
        return (
            ", ".join(options.get(v, v) for v in value)
            if type(value) is list
            else options.get(value, str(value))
        )

    def role(name):
        return next(
            ((f, label(f)) for f in fields if f.role == name and f.id in a),
            (None, None),
        )

    projection = _projection(intent, outcome, a)
    risk = a.get("risk")
    risks = list(
        dict.fromkeys(
            (["fundraising"] if intent == "fundraise" else [])
            + ([risk] if risk else [])
        )
    )
    subject, identity, message, audience = (
        role(name) for name in ("subject", "identity", "message", "audience")
    )
    definition = DEFINITIONS[outcome]
    secondary = {
        "install": {
            "id": "activated_app_users",
            "label": "Uygulamayı etkin kullanmaya başlayanlar",
        },
        "subscribe": {
            "id": "active_subscriptions",
            "label": "Etkin üyelik veya abonelikler",
        },
        "volunteer": {
            "id": "participating_volunteers",
            "label": "Fiilen katılan gönüllüler",
        },
    }.get(outcome)
    destination = _destination(intent, outcome, a)
    unknown = [
        {"id": identifier, "status": "unverified"}
        for identifier in (
            "account_permissions",
            "measurement",
            "platform_forecast",
            "policy",
            "business_model",
            "sector",
            "source_audience",
        )
    ]
    unknown.extend(
        {"id": identifier, "status": "missing"} for identifier in destination["missing"]
    )
    if not projection:
        unknown.append({"id": "paid_outcome", "status": "unsupported"})
    if not risk:
        unknown.append({"id": "declared_risk", "status": "not_declared"})
    if a["delivery_mode"] == "unsure":
        unknown.append({"id": "usage_choice", "status": "unresolved"})
    return {
        "version": VERSION,
        "validatorVersion": VALIDATOR_VERSION,
        "valid": True,
        "sourceBinding": brief.binding,
        "validationStatus": brief.validation_status,
        "intent": intent,
        "outcome": outcome,
        "intentLabel": INTENT_LABELS[intent],
        "outcomeLabel": outcome_label(intent, outcome),
        "subject": subject[1],
        "identity": identity[1],
        "message": message[1],
        "audienceLabel": audience[1],
        "ownedAudience": a[audience[0].id] if audience[0] else None,
        "delivery": a["delivery_mode"],
        "destination": destination,
        "action": projection["action"] if projection else None,
        "goal": projection["goal"] if projection else None,
        "communication": COMMUNICATION[intent],
        "legacyProjection": projection,
        "risk": "fundraising" if intent == "fundraise" else risk,
        "riskDeclared": risk,
        "risks": risks,
        "cta": definition[2],
        "kpi": {
            "id": definition[0],
            "label": definition[1],
            "secondary": secondary,
            "measurementVerified": False,
            "forecast": None,
        },
        "usage": {
            "mode": a["delivery_mode"],
            "resolved": a["delivery_mode"] != "unsure",
            "contentOnly": a["delivery_mode"] == "content_only",
        },
        "known": [
            {
                "id": f.id,
                "label": f.label,
                "value": label(f),
                "source": "user_declaration",
                "verified": False,
            }
            for f in fields
            if f.id in a
        ],
        "sourceBusiness": None,
        "sourceSector": None,
        "sourceAudience": None,
        "unknown": unknown,
        "policy": {
            "status": "not_evaluated",
            "publishReady": False,
            "platformQualified": False,
        },
        "externalQuery": False,
        "model": None,
    }


@dataclass(frozen=True, slots=True)
class AcceptedAnalysis:
    brief: AcceptedBrief

    def __post_init__(self):
        if type(self.brief) is not AcceptedBrief:
            raise ContractError("Server-validated brief required.")

    def to_dict(self):
        """Detached literal representation; no mutable internal dictionary."""
        return _derive(self.brief)

    @property
    def binding(self):
        return _digest(self.to_dict())

    @property
    def publication_enabled(self):
        return False
