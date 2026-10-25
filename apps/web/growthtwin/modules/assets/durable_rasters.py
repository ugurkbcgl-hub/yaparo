"""Closed generated-palette persistence through a bounded database blob adapter."""

from hashlib import sha256
from io import BytesIO

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import BrandMaterial, BrandMaterialVersion, MaterialRasterPair
from .raster_validation import normalize_raster
from .services import _brand
from .synthetic_catalog import SyntheticMaterialDefinition


def _enabled():
    if not settings.DEBUG or not settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED:
        raise PermissionDenied("Synthetic raster persistence is disabled.")


def _checked(pair):
    original, derivative = bytes(pair.original), bytes(pair.derivative)
    if (
        not 1 <= len(original) <= 3 * 1024 * 1024
        or not 1 <= len(derivative) <= 8 * 1024 * 1024
        or len(original) != pair.original_size
        or len(derivative) != pair.derivative_size
        or sha256(original).hexdigest() != pair.original_sha256
        or sha256(derivative).hexdigest() != pair.derivative_sha256
    ):
        raise ValidationError("Stored synthetic raster could not be verified.")
    return pair


def create_palette_material(*, owner, brand_id):
    """Create one fixed palette sample per brand; replay keeps its pinned identity.

    Both byte objects and provenance commit with the material/version in one DB
    transaction. No filesystem or retry after an uncertain outcome is involved.
    """
    _enabled()
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        source_key = f"{brand.fixture}:palette:v1"
        existing = BrandMaterial.objects.filter(
            brand=brand, source_key=source_key
        ).first()
        if existing is not None:
            return _checked(
                MaterialRasterPair.objects.select_related("version").get(
                    version__material=existing,
                    version__version=1,
                )
            )
        from PIL import Image, ImageDraw

        identity = brand.current_identity
        with Image.new("RGB", (320, 200), identity.secondary_color) as image:
            ImageDraw.Draw(image).rounded_rectangle(
                (40, 35, 280, 165), radius=24, fill=identity.primary_color
            )
            output = BytesIO()
            image.save(output, format="PNG")
            original = output.getvalue()
        normalized = normalize_raster(original, declared_media_type="image/png")
        material = BrandMaterial.objects.create(
            brand=brand, identity=identity, source_key=source_key
        )
        definition = SyntheticMaterialDefinition(
            fixture=brand.fixture,
            source_key=source_key,
            display_name="Marka paleti · Sentetik görsel",
            media_type="image/png",
            byte_size=len(original),
            width=320,
            height=200,
            source_label="Yaparo palette-raster-v1",
            rights_label="Yalnız yerel sentetik deneme",
        )
        version = BrandMaterialVersion.objects.create(
            material=material,
            version=1,
            display_name=definition.display_name,
            media_type=definition.media_type,
            byte_size=definition.byte_size,
            width=definition.width,
            height=definition.height,
            source_label=definition.source_label,
            rights_label=definition.rights_label,
            catalog_digest=definition.catalog_digest,
        )
        return MaterialRasterPair.objects.create(
            version=version,
            original=original,
            derivative=normalized.png,
            original_sha256=normalized.source_sha256,
            derivative_sha256=normalized.derivative_sha256,
            original_size=len(original),
            derivative_size=len(normalized.png),
            tool=normalized.tool,
        )


def read_palette_material(*, owner, brand_id, material_id):
    _enabled()
    brand = _brand(owner, brand_id)
    pair = MaterialRasterPair.objects.select_related("version").get(
        version__material_id=material_id,
        version__material__brand=brand,
        version__material__brand__workspace__owner=owner,
        version__material__brand__workspace__owner__is_active=True,
        version__material__brand__is_archived=False,
        version__material__source_key=f"{brand.fixture}:palette:v1",
        version__version=1,
    )
    return _checked(pair)
