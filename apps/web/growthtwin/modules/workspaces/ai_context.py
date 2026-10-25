"""Owned snapshot → offline task envelope. No routes, API, storage or dispatch."""

from growthtwin.modules.ai_gateway.brand_tasks import (
    BrandCopyTaskRequest,
    BrandIdentityInput,
    BrandTaskContext,
    MaterialReference,
    digest,
    validate_request,
    validate_result,
)
from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
)
from growthtwin.modules.campaigns.design_preview import selected_snapshot
from growthtwin.modules.content.planning import CampaignBrief

from .design_bundle import IDENTITY_FIELDS
from .models import SYNTHETIC_BRAND_PRESETS


def _context(choice):
    document = choice.snapshot.document
    return BrandTaskContext(
        campaign_id=choice.draft_id,
        selection_id=choice.pk,
        snapshot_id=choice.snapshot_id,
        workspace_id=document.identity.brand.workspace_id,
        brand_id=document.identity.brand_id,
        identity_version=document.identity.version,
        document_id=document.pk,
        document_revision=choice.snapshot.revision,
        selection_version=choice.version,
        identity_digest=digest(
            {field: getattr(document.identity, field) for field in IDENTITY_FIELDS}
        ),
        scene_digest=digest(choice.snapshot.scene),
        materials=tuple(
            MaterialReference(
                layer_id=binding.layer_id,
                material_id=binding.material_version.material_id,
                version=binding.material_version.version,
                catalog_digest=binding.material_version.catalog_digest,
            )
            for binding in document.material_bindings.select_related(
                "material_version"
            ).order_by("layer_id")
        ),
    )


def build_selected_brand_task(*, owner, draft_id, selection_version, task_id):
    choice = selected_snapshot(
        owner=owner, draft_id=draft_id, selection_version=selection_version
    )
    brand = choice.snapshot.document.identity.brand
    # Explicit fixed fixture facts only; never silently reuse the legacy Search
    # brand/brief or treat a caller's synthetic marker as real-data permission.
    request = BrandCopyTaskRequest(
        task_id=task_id,
        context=_context(choice),
        identity=BrandIdentityInput(
            **{
                field: getattr(choice.snapshot.document.identity, field)
                for field in IDENTITY_FIELDS
            }
        ),
        creative_request=CreativeGenerationRequest(
            brief=CampaignBrief(
                text=" ".join(SYNTHETIC_BRAND_PRESETS[brand.fixture]["facts"]),
                objective="awareness",
                objective_label="Kurgusal marka tanıtımı",
                target_audience="Sentetik değerlendirme",
                brand_context=brand.name,
            ),
            synthetic_only=True,
        ),
    )
    return validate_request(request)


def validate_selected_brand_result(*, owner, draft_id, request, result):
    validate_request(request)
    expected = build_selected_brand_task(
        owner=owner,
        draft_id=draft_id,
        selection_version=request.context.selection_version,
        task_id=request.task_id,
    )
    if request.fingerprint != expected.fingerprint:
        raise CreativeGenerationRejected(
            "Görev isteği sahip olunan kaynaklarla eşleşmiyor."
        )
    return validate_result(request, result, current_context=expected.context)
