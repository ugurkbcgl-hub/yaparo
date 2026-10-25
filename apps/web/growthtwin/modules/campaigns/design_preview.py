"""Read-only access to the explicitly selected immutable scene and source."""

from django.core.exceptions import ValidationError

from growthtwin.modules.assets.durable_rasters import read_palette_material
from growthtwin.modules.workspaces.creative_documents import _scene, _version
from growthtwin.modules.workspaces.creative_scenes import uses_palette

from .design_selection import current_design


def selected_snapshot(*, owner, draft_id, selection_version):
    _version(selection_version)
    choice = current_design(owner=owner, draft_id=draft_id)
    if choice is None or choice.version != selection_version:
        raise ValidationError("Kampanyanın tasarım seçimi değişmiş veya yok.")
    _scene(choice.snapshot.scene, choice.snapshot.document.identity.brand.fixture)
    return choice


def selected_palette(*, owner, draft_id, selection_version):
    choice = selected_snapshot(
        owner=owner, draft_id=draft_id, selection_version=selection_version
    )
    if not uses_palette(choice.snapshot.scene):
        raise ValidationError("Bu seçim palet görseli kullanmıyor.")
    binding = choice.snapshot.document.material_bindings.select_related(
        "material_version__material"
    ).get(layer_id="hero")
    pair = read_palette_material(
        owner=owner,
        brand_id=choice.snapshot.document.identity.brand_id,
        material_id=binding.material_version.material_id,
    )
    if pair.version_id != binding.material_version_id:
        raise ValidationError("Seçili kaynak sürümü doğrulanamadı.")
    return bytes(pair.derivative)
