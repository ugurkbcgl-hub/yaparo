"""Fixed-source material provenance without changing v1/v2 scene rendering."""

from django.core.exceptions import ValidationError

from growthtwin.modules.assets.models import BrandMaterialVersion
from growthtwin.modules.assets.services import prepare_synthetic_materials
from growthtwin.modules.assets.synthetic_catalog import definitions_for_fixture

from .models import CreativeMaterialBinding


def bind_materials(document, owner):
    """Called only inside the owned document creation transaction/brand lock."""
    prepare_synthetic_materials(owner=owner, brand_id=document.identity.brand_id)
    for layer in document.scene["layers"]:
        if layer["type"] == "image":
            version = BrandMaterialVersion.objects.get(
                material__brand_id=document.identity.brand_id,
                material__source_key=layer["asset"],
                version=1,
            )
            CreativeMaterialBinding.objects.create(
                document=document, layer_id=layer["id"], material_version=version
            )
    checked_materials(document)


def checked_materials(document):
    """Return safe metadata; missing, foreign or contradictory binding denies."""
    rows = list(
        document.material_bindings.select_related(
            "material_version__material__identity"
        )
    )
    if document.material_binding_version == 0 and not rows:
        return []  # Legacy scenes are never retroactively rebound.
    if document.material_binding_version != 1 or len(rows) != 2:
        raise ValidationError("Çalışmanın materyal bağları doğrulanamadı.")
    definitions = {
        item.source_key: item
        for item in definitions_for_fixture(document.identity.brand.fixture)
    }
    layers = {
        layer["id"]: layer["asset"]
        for layer in document.scene["layers"]
        if layer["type"] == "image"
    }
    if {row.layer_id for row in rows} != set(layers):
        raise ValidationError("Çalışmanın materyal katmanları doğrulanamadı.")
    result = []
    for row in rows:
        row.clean()
        version = row.material_version
        definition = definitions.get(layers[row.layer_id])
        if (
            definition is None
            or version.material.source_key != definition.source_key
            or any(
                getattr(version, field) != getattr(definition, field)
                for field in (
                    "display_name",
                    "media_type",
                    "byte_size",
                    "width",
                    "height",
                    "source_label",
                    "rights_label",
                    "catalog_digest",
                )
            )
        ):
            raise ValidationError("Materyal sürümü sabit kaynakla eşleşmiyor.")
        result.append(
            {
                "layer_id": row.layer_id,
                "display_name": version.display_name,
                "version": version.version,
                "identity_version": version.material.identity.version,
            }
        )
    return result
