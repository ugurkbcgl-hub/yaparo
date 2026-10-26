"""Owned read-only fixture candidates, never hosted AI dispatch or scene edits."""

from uuid import uuid4

from django.conf import settings
from django.core.exceptions import PermissionDenied

from growthtwin.modules.ai_gateway.brand_tasks import ADAPTER_ID, BrandCopyTaskResult
from growthtwin.modules.ai_gateway.synthetic import SyntheticTemplateGenerator
from growthtwin.modules.workspaces.ai_context import (
    build_selected_brand_task,
    validate_selected_brand_result,
)


def preview_brand_copy(*, owner, draft_id, selection_version):
    if not settings.DEBUG or not settings.SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED:
        raise PermissionDenied("Yerel örnek metin önizlemesi kapalı.")
    request = build_selected_brand_task(
        owner=owner,
        draft_id=draft_id,
        selection_version=selection_version,
        task_id=uuid4(),
    )
    result = BrandCopyTaskResult(
        task_id=request.task_id,
        request_fingerprint=request.fingerprint,
        adapter_id=ADAPTER_ID,
        status="candidate",
        creative_result=SyntheticTemplateGenerator().generate(request.creative_request),
    )
    checked = validate_selected_brand_result(
        owner=owner, draft_id=draft_id, request=request, result=result
    )
    return request, checked
