"""Offline provider-neutral envelope; no API dispatch, persistence or spend grant."""

import json
import re
from dataclasses import asdict, dataclass
from hashlib import sha256
from uuid import UUID

from growthtwin.modules.content.planning import CampaignBrief

from .contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
    CreativeGenerationResult,
    validate_generation_result,
)
from .profiles import BRAND_COPY_PROFILE

PROFILE_ID = BRAND_COPY_PROFILE.profile_id
ADAPTER_ID = "synthetic-template-v1"


def digest(value):
    return sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


@dataclass(frozen=True)
class MaterialReference:
    layer_id: str
    material_id: UUID
    version: int
    catalog_digest: str  # Metadata digest; not a binary hash or rights proof.


@dataclass(frozen=True)
class BrandTaskContext:
    campaign_id: int
    selection_id: int
    snapshot_id: int
    workspace_id: int
    brand_id: int
    identity_version: int
    document_id: UUID
    document_revision: int
    selection_version: int
    identity_digest: str
    scene_digest: str
    materials: tuple[MaterialReference, ...]


@dataclass(frozen=True)
class BrandIdentityInput:
    version: int
    primary_color: str
    secondary_color: str
    tone: str
    tagline_key: str
    tagline_text: str
    logo_key: str


@dataclass(frozen=True)
class BrandCopyTaskRequest:
    task_id: UUID
    context: BrandTaskContext
    creative_request: CreativeGenerationRequest
    identity: BrandIdentityInput
    schema_version: int = 1
    profile_id: str = PROFILE_ID
    allowed_adapters: tuple[str, ...] = (ADAPTER_ID,)
    max_cost_microusd: int = 0
    reservation_id: UUID | None = None

    @property
    def fingerprint(self):
        validate_request(self)
        value = asdict(self)
        value["task_id"] = str(self.task_id)
        value["context"]["document_id"] = str(self.context.document_id)
        for material in value["context"]["materials"]:
            material["material_id"] = str(material["material_id"])
        return digest(value)

    @property
    def execution_authorized(self):
        return False  # Contract data is not a credential, reservation or dispatch.


@dataclass(frozen=True)
class BrandCopyTaskResult:
    task_id: UUID
    request_fingerprint: str
    adapter_id: str
    status: str  # candidate / failed / uncertain; never approved/published.
    creative_result: CreativeGenerationResult | None = None
    reported_cost_microusd: int = 0
    schema_version: int = 1

    @property
    def publishable(self):
        return False

    @property
    def review_required(self):
        return True


def _positive(value):
    return type(value) is int and 1 <= value < 2**63


def _uuid(value):
    return type(value) is UUID and value.int != 0


def _hash(value):
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value)


def validate_request(request):
    if type(request) is not BrandCopyTaskRequest or not _uuid(request.task_id):
        raise CreativeGenerationRejected("Marka görevi geçersiz.")
    context = request.context
    if type(context) is not BrandTaskContext or not _uuid(context.document_id):
        raise CreativeGenerationRejected("Marka kaynak bağlamı geçersiz.")
    if not all(
        _positive(getattr(context, field))
        for field in (
            "campaign_id",
            "selection_id",
            "snapshot_id",
            "workspace_id",
            "brand_id",
            "identity_version",
            "document_revision",
            "selection_version",
        )
    ) or not all(
        _hash(getattr(context, field)) for field in ("identity_digest", "scene_digest")
    ):
        raise CreativeGenerationRejected("Marka kaynak sürümleri geçersiz.")
    if type(context.materials) is not tuple or len(context.materials) != 2:
        raise CreativeGenerationRejected("Marka materyal bağları geçersiz.")
    for source in context.materials:
        if (
            type(source) is not MaterialReference
            or not _uuid(source.material_id)
            or not _positive(source.version)
            or not _hash(source.catalog_digest)
        ):
            raise CreativeGenerationRejected("Materyal sürümü geçersiz.")
    if tuple(source.layer_id for source in context.materials) != ("hero", "logo"):
        raise CreativeGenerationRejected("Materyal katmanları geçersiz.")
    identity = request.identity
    if (
        type(identity) is not BrandIdentityInput
        or type(identity.version) is not int
        or identity.version != context.identity_version
    ):
        raise CreativeGenerationRejected("Marka kimliği sürümü eşleşmiyor.")
    if any(
        type(getattr(identity, field)) is not str
        or not re.fullmatch(r"#[0-9a-fA-F]{6}", getattr(identity, field))
        for field in ("primary_color", "secondary_color")
    ):
        raise CreativeGenerationRejected("Marka renkleri geçersiz.")
    if (
        identity.tone not in ("calm", "energetic", "formal")
        or any(
            type(getattr(identity, field)) is not str
            or not getattr(identity, field).strip()
            or len(getattr(identity, field)) > 100
            for field in ("tagline_key", "tagline_text", "logo_key")
        )
        or digest(asdict(identity)) != context.identity_digest
    ):
        raise CreativeGenerationRejected("Marka kimliği kaynak kaydıyla eşleşmiyor.")
    if (
        type(request.schema_version) is not int
        or request.schema_version != 1
        or request.profile_id != PROFILE_ID
        or request.allowed_adapters != (ADAPTER_ID,)
    ):
        raise CreativeGenerationRejected("Görev yetenek profili desteklenmiyor.")
    if (
        type(request.max_cost_microusd) is not int
        or request.max_cost_microusd != 0
        or request.reservation_id is not None
    ):
        raise CreativeGenerationRejected(
            "Çevrimdışı görev harcama veya rezervasyon yetkisi vermez."
        )
    inner = request.creative_request
    if (
        type(inner) is not CreativeGenerationRequest
        or inner.synthetic_only is not True
        or type(inner.brief) is not CampaignBrief
    ):
        raise CreativeGenerationRejected("Yalnız sabit sentetik brief kabul edilir.")
    if any(
        type(value) is not str or not value.strip() or len(value) > 2048
        for value in asdict(inner.brief).values()
    ):
        raise CreativeGenerationRejected("Marka brief alanları geçersiz.")
    return request


def validate_result(request, result, *, current_context):
    validate_request(request)
    if current_context != request.context:
        raise CreativeGenerationRejected("Görevin marka veya kaynak seçimi değişmiş.")
    if (
        type(result) is not BrandCopyTaskResult
        or result.task_id != request.task_id
        or result.request_fingerprint != request.fingerprint
        or result.adapter_id not in request.allowed_adapters
    ):
        raise CreativeGenerationRejected("Yanıt görev ve izinli adaptörle eşleşmiyor.")
    if type(result.schema_version) is not int or result.schema_version != 1:
        raise CreativeGenerationRejected("Görev sonuç sürümü desteklenmiyor.")
    if (
        type(result.reported_cost_microusd) is not int
        or result.reported_cost_microusd != 0
        or result.status not in ("candidate", "failed", "uncertain")
    ):
        raise CreativeGenerationRejected("Görev sonucu veya maliyet doğrulanamadı.")
    if result.status == "candidate":
        if (
            type(result.creative_result) is not CreativeGenerationResult
            or result.creative_result.generator_id != result.adapter_id
        ):
            raise CreativeGenerationRejected("Aday üretici kimliği eşleşmiyor.")
        validate_generation_result(request.creative_request, result.creative_result)
    elif result.creative_result is not None:
        raise CreativeGenerationRejected("Başarısız veya belirsiz sonuç aday içeremez.")
    return result
