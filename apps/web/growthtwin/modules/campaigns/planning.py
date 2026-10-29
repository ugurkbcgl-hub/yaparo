"""Provider-free, source-traceable Google Search draft preparation."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft

HEADLINE_MAX_CHARACTERS = 30
DESCRIPTION_MAX_CHARACTERS = 90


@dataclass(frozen=True)
class TextAssetDraft:
    """Editable text derived from explicit campaign fields."""

    text: str
    source_fields: tuple[str, ...]
    max_characters: int


@dataclass(frozen=True)
class GoogleSearchCampaignPlan:
    """A local preview plan; this value cannot create or publish a platform ad."""

    campaign_draft_id: int
    target_city: str
    final_url: str
    media_budget_minor: int
    daily_media_average_minor: Decimal | None
    currency: str
    flight_start: date | None
    flight_end: date | None
    headlines: tuple[TextAssetDraft, ...]
    descriptions: tuple[TextAssetDraft, ...]
    missing_requirements: tuple[str, ...]
    forecast_status: Literal["unavailable"]
    forecast_reason: str
    keyword_ideas_status: Literal["unavailable"]
    keyword_ideas_reason: str
    publication_enabled: Literal[False] = False

    @property
    def ready_for_review(self) -> bool:
        """Whether required local inputs exist for an advertiser review screen."""

        return not self.missing_requirements


def _normalize(value: str) -> str:
    return " ".join(value.split())


def _fit_text(value: str, *, max_characters: int) -> str:
    """Fit text by whole words where possible and mark any shortened result."""

    normalized = _normalize(value)
    if len(normalized) <= max_characters:
        return normalized
    if max_characters <= 1:
        return "…"[:max_characters]

    clipped = normalized[: max_characters - 1]
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    clipped = clipped.rstrip(" ,:;–—-")
    return f"{clipped or normalized[: max_characters - 1]}…"


def _text_assets(
    candidates: tuple[tuple[str, tuple[str, ...]], ...],
    *,
    max_characters: int,
) -> tuple[TextAssetDraft, ...]:
    assets = []
    seen = set()
    for value, source_fields in candidates:
        text = _fit_text(value, max_characters=max_characters)
        identity = text.casefold()
        if not text or identity in seen:
            continue
        seen.add(identity)
        assets.append(
            TextAssetDraft(
                text=text,
                source_fields=source_fields,
                max_characters=max_characters,
            )
        )
    return tuple(assets)


def build_google_search_campaign_plan(
    draft: WorkspaceCampaignDraft,
) -> GoogleSearchCampaignPlan:
    """Prepare editable assets without AI, network access, or forecast guesses."""

    brand_name = _normalize(draft.brand_name)
    city = _normalize(draft.target_city)
    brief = _normalize(draft.brief)
    headlines = _text_assets(
        tuple(
            (value, source_fields)
            for value, source_fields in (
                (brand_name, ("brand_name",)),
                (f"{city} {brand_name}", ("target_city", "brand_name")),
                (f"{brand_name} hakkında", ("brand_name",)),
            )
        ),
        max_characters=HEADLINE_MAX_CHARACTERS,
    )
    descriptions = _text_assets(
        (
            (brief, ("brief",)),
            (
                f"İşletmeyi ve hizmetlerini web sitesinde inceleyin: {brand_name}.",
                ("brand_name", "destination_url"),
            ),
        ),
        max_characters=DESCRIPTION_MAX_CHARACTERS,
    )

    missing = []
    if not brand_name:
        missing.append("İşletme veya marka adı gerekli.")
    if not city:
        missing.append("Hedef şehir gerekli.")
    if not brief:
        missing.append("Hizmet ve teklif brief'i gerekli.")
    if not draft.destination_url:
        missing.append("Reklamın gideceği web sitesi gerekli.")
    if not draft.flight_start or not draft.flight_end:
        missing.append("Başlangıç ve bitiş tarihleri gerekli.")
    if draft.media_budget_minor <= 0:
        missing.append("Pozitif toplam medya bütçesi gerekli.")
    if len(headlines) < 3:
        missing.append("En az üç farklı başlık taslağı için daha fazla girdi gerekli.")
    if len(descriptions) < 2:
        missing.append(
            "En az iki farklı açıklama taslağı için daha fazla girdi gerekli."
        )

    # Both local calendar endpoints count, consistent with owned plan settings.
    # This is a descriptive average, not a platform daily budget or spend limit.
    pacing_days = (
        (draft.flight_end - draft.flight_start).days + 1
        if draft.flight_start and draft.flight_end
        else 0
    )
    daily_media_average_minor = (
        Decimal(draft.media_budget_minor) / pacing_days if pacing_days > 0 else None
    )

    return GoogleSearchCampaignPlan(
        campaign_draft_id=draft.pk,
        target_city=city,
        final_url=draft.destination_url,
        media_budget_minor=draft.media_budget_minor,
        daily_media_average_minor=daily_media_average_minor,
        currency=draft.currency,
        flight_start=draft.flight_start,
        flight_end=draft.flight_end,
        headlines=headlines,
        descriptions=descriptions,
        missing_requirements=tuple(missing),
        forecast_status="unavailable",
        forecast_reason=(
            "Yetkili Google Ads tahmin kaynağı bağlı değil; gösterim, tıklama, "
            "maliyet ve dönüşüm tahmini üretilmedi."
        ),
        keyword_ideas_status="unavailable",
        keyword_ideas_reason=(
            "Google Keyword Planner API erişimi doğrulanmadı; anahtar kelime "
            "önerisi veya arama hacmi üretilmedi."
        ),
    )
