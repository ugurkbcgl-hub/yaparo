"""Owned synthetic scene persistence, pinned to one literal identity version.

No asset upload, provider, campaign binding or publication.
"""

from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .creative_scenes import SceneValidationError, seed_brand_scene, validate_scene
from .models import Brand, BrandCreativeDocument, BrandCreativeRevision


def _owner(owner):
    if not getattr(owner, "is_authenticated", False) or not getattr(
        owner, "is_active", False
    ):
        raise PermissionDenied("Etkin bir marka sahibi hesabı gereklidir.")


def _uuid(value):
    if type(value) is not UUID or not value.int:
        raise ValidationError("Geçerli bir çalışma kimliği gereklidir.")


def _version(value):
    if type(value) is not int or not 1 <= value <= 2**31 - 1:
        raise ValidationError("Geçerli bir çalışma sürümü gereklidir.")


def _brand(owner, brand_id, *, lock=False):
    _owner(owner)
    rows = Brand.objects.select_related("workspace")
    if lock:
        rows = rows.select_for_update()
    return rows.get(
        pk=brand_id,
        workspace__owner=owner,
        workspace__owner__is_active=True,
        is_archived=False,
    )


def _scene(value, fixture):
    try:
        return validate_scene(value, fixture=fixture)
    except SceneValidationError:
        raise ValidationError("Geçerli bir sentetik sahne gereklidir.") from None


def _document(brand, document_id, *, lock=False):
    rows = BrandCreativeDocument.objects.select_related(
        "identity", "identity__brand", "identity__brand__workspace"
    )
    if lock:
        rows = rows.select_for_update()
    return rows.get(pk=document_id, identity__brand=brand)


def create_document(*, owner, brand_id, expected_identity_version, request_id):
    """Create one scene, or replay the same scoped request without overwriting it."""
    _owner(owner)
    _uuid(request_id)
    _version(expected_identity_version)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        existing = (
            BrandCreativeDocument.objects.select_for_update()
            .select_related("identity", "identity__brand", "identity__brand__workspace")
            .filter(pk=request_id)
            .first()
        )
        if existing:
            if (
                existing.identity.brand_id != brand.pk
                or existing.identity.version != expected_identity_version
            ):
                raise ValidationError("Çalışma isteği başka bir bağlamda kullanılmış.")
            _scene(existing.scene, brand.fixture)
            return existing
        if brand.current_version != expected_identity_version:
            raise ValidationError(
                "Marka değişmiş. Güncel marka sürümünden yeni çalışma açın.",
                code="stale_brand_version",
            )
        identity = brand.current_identity
        try:
            scene = seed_brand_scene(
                fixture=brand.fixture,
                tagline_text=identity.tagline_text,
                primary_color=identity.primary_color,
                secondary_color=identity.secondary_color,
                logo_key=identity.logo_key,
            )
        except SceneValidationError:
            raise ValidationError(
                "Geçerli bir sentetik marka kimliği gereklidir."
            ) from None
        try:
            with transaction.atomic():
                document = BrandCreativeDocument.objects.create(
                    id=request_id, identity=identity, scene=scene
                )
        except IntegrityError:
            raise ValidationError(
                "Çalışma isteği başka bir bağlamda kullanılmış."
            ) from None
        _snapshot(document, owner, "create")
        return document


def _snapshot(document, owner, reason, restored_from=None):
    scene = _scene(document.scene, document.identity.brand.fixture)
    existing = BrandCreativeRevision.objects.filter(
        document=document, revision=document.revision
    ).first()
    if existing:
        if existing.scene != scene:
            raise ValidationError("Çalışma geçmişi kayıtla eşleşmiyor.")
        return existing
    return BrandCreativeRevision.objects.create(
        document=document,
        revision=document.revision,
        scene=scene,
        reason=reason,
        restored_from=restored_from,
        created_by=owner,
    )


def read_document(*, owner, brand_id, document_id):
    _uuid(document_id)
    brand = _brand(owner, brand_id)
    document = _document(brand, document_id)
    _scene(document.scene, brand.fixture)
    return document


def _write_document(
    document, owner, expected_revision, scene, *, reason="save", restored_from=None
):
    if document.revision != expected_revision:
        raise ValidationError(
            "Çalışma değişmiş. Güncel kaydı açın.", code="stale_document_revision"
        )
    canonical = _scene(scene, document.identity.brand.fixture)
    if canonical["schema_version"] != document.scene["schema_version"]:
        raise ValidationError("Çalışma biçimi sessizce değiştirilemez.")
    if document.scene == canonical:
        return document
    if document.revision == 2**31 - 1:
        raise ValidationError("Çalışma sürümü sınırına ulaşıldı.")
    _snapshot(document, owner, "baseline")
    changed = BrandCreativeDocument.objects.filter(
        pk=document.pk, identity_id=document.identity_id, revision=expected_revision
    ).update(scene=canonical, revision=expected_revision + 1, updated_at=timezone.now())
    if changed != 1:
        raise ValidationError(
            "Çalışma değişmiş. Güncel kaydı açın.", code="stale_document_revision"
        )
    document.refresh_from_db()
    _snapshot(document, owner, reason, restored_from)
    return document


def save_document(*, owner, brand_id, document_id, expected_revision, scene):
    _owner(owner)
    _uuid(document_id)
    _version(expected_revision)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        document = _document(brand, document_id, lock=True)
        return _write_document(document, owner, expected_revision, scene)


def read_document_snapshot(*, owner, brand_id, document_id):
    _uuid(document_id)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        document = _document(brand, document_id, lock=True)
        _scene(document.scene, brand.fixture)
        rows = list(document.history.order_by("-revision")[:50])
        if rows and (
            rows[0].revision != document.revision or rows[0].scene != document.scene
        ):
            raise ValidationError("Çalışma geçmişi kayıtla eşleşmiyor.")
        if not rows:
            return document, [
                {"revision": document.revision, "label": "Mevcut başlangıç kaydı"}
            ]
        return document, [
            {"revision": row.revision, "label": row.get_reason_display()}
            for row in rows
        ]


def document_history(*, owner, brand_id, document_id):
    return read_document_snapshot(
        owner=owner, brand_id=brand_id, document_id=document_id
    )[1]


def restore_document(
    *, owner, brand_id, document_id, expected_revision, target_revision
):
    _owner(owner)
    _uuid(document_id)
    _version(expected_revision)
    _version(target_revision)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        document = _document(brand, document_id, lock=True)
        # Resolve target inside this owned document; no global snapshot lookup.
        target = BrandCreativeRevision.objects.get(
            document=document, revision=target_revision
        )
        return _write_document(
            document,
            owner,
            expected_revision,
            target.scene,
            reason="restore",
            restored_from=target_revision,
        )
