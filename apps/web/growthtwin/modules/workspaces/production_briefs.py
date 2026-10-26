"""Owned immutable brand/brief/material request snapshots, without inference."""

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from growthtwin.modules.ai_gateway.brand_briefs import (
    SCHEMA,
    validate_brief,
    validate_mock_receipt,
)
from growthtwin.modules.ai_gateway.brand_tasks import digest

from .creative_documents import _brand, _document, _scene, _uuid, _version
from .creative_materials import checked_materials
from .design_bundle import IDENTITY_FIELDS
from .models import BrandCreativeDocument, BrandProductionRequest


def enabled():
    if not settings.DEBUG or not settings.LOCAL_BRAND_PRODUCTION_BRIEF_ENABLED:
        raise PermissionDenied


def _envelope(brand, identity, snapshot, brief, request_id, version):
    document = snapshot.document
    _scene(snapshot.scene, brand.fixture)
    checked_materials(document)
    if document.material_binding_version != 1 or document.identity_id != identity.pk:
        raise ValidationError("Kaynak sürümleri kimlikle eşleşmiyor.")
    # Geometry/source identifiers are immutable for this saved document schema.
    if any(
        snapshot.scene.get(k) != document.scene.get(k)
        for k in ("schema_version", "width", "height", "format", "hero_source")
    ):
        raise ValidationError("Kaynak biçimi doğrulanamadı.")
    identity.full_clean()
    materials = []
    for binding in document.material_bindings.select_related(
        "material_version__material__identity"
    ).order_by("layer_id"):
        source = binding.material_version
        materials.append(
            {
                "layer": binding.layer_id,
                "material_id": str(source.material_id),
                "version": source.version,
                "identity_version": source.material.identity.version,
                "source_key": source.material.source_key,
                "catalog_digest": source.catalog_digest,
                "binary_verified": False,
            }
        )
    return {
        "schema": SCHEMA,
        "request_id": str(request_id),
        "brief_version": version,
        "workspace_id": str(brand.workspace_id),
        "brand_id": str(brand.pk),
        "brand_name": brand.name,
        "identity_id": str(identity.pk),
        "identity": {key: getattr(identity, key) for key in IDENTITY_FIELDS},
        "source": {
            "document_id": str(document.pk),
            "revision_id": str(snapshot.pk),
            "revision": snapshot.revision,
            "scene_digest": digest(snapshot.scene),
            "materials": materials,
        },
        "brief": validate_brief(brief),
        "language": "tr-TR",
        "execution": {"authorized": False, "max_cost_microusd": 0, "provider": None},
    }


def checked(*, owner, brand_id, request_id):
    enabled()
    _uuid(request_id)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        request = BrandProductionRequest.objects.select_related(
            "identity", "source_revision__document"
        ).get(pk=request_id, brand=brand)
        document = _document(brand, request.source_revision.document_id, lock=True)
        request.source_revision.document = document
        expected = _envelope(
            brand,
            request.identity,
            request.source_revision,
            request.brief,
            request.pk,
            request.version,
        )
        if request.envelope != expected or request.fingerprint != digest(expected):
            raise ValidationError("Üretim talebi kaynaklarıyla eşleşmiyor.")
        return request


def create(
    *,
    owner,
    brand_id,
    document_id,
    identity_version,
    document_revision,
    expected_version,
    request_id,
    brief,
):
    enabled()
    _uuid(request_id)
    _uuid(document_id)
    _version(identity_version)
    _version(document_revision)
    if type(expected_version) is not int or not 0 <= expected_version < 2**31 - 1:
        raise ValidationError("Geçerli talep sürümü gerekli.")
    brief = validate_brief(brief)
    with transaction.atomic():
        # Same brand→document graph as the existing editor/identity services.
        brand = _brand(owner, brand_id, lock=True)
        document = _document(brand, document_id, lock=True)
        existing = BrandProductionRequest.objects.filter(pk=request_id).first()
        if existing:
            if (
                existing.brand_id != brand.pk
                or existing.identity.version != identity_version
                or existing.source_revision.document_id != document.pk
                or existing.source_revision.revision != document_revision
                or existing.version != expected_version + 1
                or existing.brief != brief
            ):
                raise ValidationError("İstek başka bir bağlamda kullanılmış.")
            return checked(owner=owner, brand_id=brand.pk, request_id=request_id)
        latest = brand.production_requests.first()
        if (
            (latest.version if latest else 0) != expected_version
            or brand.current_version != identity_version
            or document.identity.version != identity_version
            or document.revision != document_revision
        ):
            raise ValidationError(
                "Marka, tasarım veya talep değişmiş; güncel formu açın."
            )
        snapshot = document.history.get(revision=document.revision)
        if snapshot.scene != document.scene:
            raise ValidationError("Tasarım kayıt geçmişi eşleşmiyor.")
        envelope = _envelope(
            brand, document.identity, snapshot, brief, request_id, expected_version + 1
        )
        return BrandProductionRequest.objects.create(
            id=request_id,
            brand=brand,
            identity=document.identity,
            source_revision=snapshot,
            version=expected_version + 1,
            brief=brief,
            envelope=envelope,
            fingerprint=digest(envelope),
        )


def options(*, owner, brand_id):
    enabled()
    brand = _brand(owner, brand_id)
    return (
        BrandCreativeDocument.objects.filter(
            identity__brand=brand,
            identity__version=brand.current_version,
            material_binding_version=1,
        )
        .select_related("identity")
        .order_by("-updated_at")[:20]
    )


def accept_mock(*, owner, brand_id, request_id, receipt):
    request = checked(owner=owner, brand_id=brand_id, request_id=request_id)
    return validate_mock_receipt(request.envelope, receipt)
