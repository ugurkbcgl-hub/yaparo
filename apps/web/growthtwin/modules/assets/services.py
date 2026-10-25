"""Owner-scoped setup/read services for the closed synthetic material catalog."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from growthtwin.modules.workspaces.models import Brand

from .models import BrandMaterial, BrandMaterialVersion
from .synthetic_catalog import definitions_for_fixture


def _owner(owner):
    if not getattr(owner, "is_authenticated", False) or not getattr(
        owner, "is_active", False
    ):
        raise PermissionDenied("Etkin bir marka sahibi hesabı gereklidir.")


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


def prepare_synthetic_materials(*, owner, brand_id):
    """Create the fixed catalog once without accepting a user file or URL."""

    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        definitions = definitions_for_fixture(brand.fixture)
        existing = {
            material.source_key: material
            for material in BrandMaterial.objects.select_for_update()
            .filter(brand=brand)
            .select_related("identity")
        }
        expected = {item.source_key for item in definitions}
        if set(existing) - (expected | {f"{brand.fixture}:palette:v1"}):
            raise ValidationError("Materyal kataloğu marka örneğiyle eşleşmiyor.")
        for item in definitions:
            material = existing.get(item.source_key)
            if material is None:
                material = BrandMaterial.objects.create(
                    brand=brand,
                    identity=brand.current_identity,
                    source_key=item.source_key,
                )
                BrandMaterialVersion.objects.create(
                    material=material,
                    version=1,
                    display_name=item.display_name,
                    media_type=item.media_type,
                    byte_size=item.byte_size,
                    width=item.width,
                    height=item.height,
                    source_label=item.source_label,
                    rights_label=item.rights_label,
                    catalog_digest=item.catalog_digest,
                )
            elif (
                material.identity.brand_id != brand.pk
                or material.current_version != 1
                or not material.versions.filter(version=1).exists()
            ):
                raise ValidationError("Materyal kataloğu doğrulanamadı.")
        return list_materials(owner=owner, brand_id=brand.pk)


def list_materials(*, owner, brand_id):
    """Return only the current owner's closed catalog records for one brand."""

    brand = _brand(owner, brand_id)
    return (
        BrandMaterial.objects.filter(brand=brand, current_version=1)
        .select_related("identity")
        .prefetch_related("versions")
        .order_by("source_key")
    )
