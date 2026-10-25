"""Bounded deterministic archive of one explicitly selected immutable scene."""

from django.core.exceptions import ValidationError

from growthtwin.modules.assets.durable_rasters import _enabled as material_enabled
from growthtwin.modules.workspaces.design_bundle import _build_bundle

from .design_preview import selected_snapshot


def export_selected_bundle(*, owner, draft_id, selection_version):
    material_enabled()
    choice = selected_snapshot(
        owner=owner, draft_id=draft_id, selection_version=selection_version
    )
    data = _build_bundle(
        owner=owner,
        document=choice.snapshot.document,
        scene=choice.snapshot.scene,
        revision=choice.snapshot.revision,
        selection={
            "campaign_id": choice.draft_id,
            "selection_id": choice.pk,
            "selection_version": choice.version,
            "snapshot_id": choice.snapshot_id,
            "document_revision": choice.snapshot.revision,
            "brand_id": choice.snapshot.document.identity.brand_id,
        },
    )
    # No new draft/source lock ordering. Refuse if eligibility/selection changed
    # while collecting bytes rather than returning a newer or revoked reference.
    current = selected_snapshot(
        owner=owner, draft_id=draft_id, selection_version=selection_version
    )
    if current.pk != choice.pk:
        raise ValidationError("Kampanyanın tasarım seçimi değişmiş.")
    return data
