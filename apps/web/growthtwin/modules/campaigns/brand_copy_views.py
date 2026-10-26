"""GET-only local candidate preview; no approval, selection or save action."""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from growthtwin.modules.ai_gateway.contracts import CreativeGenerationRejected
from growthtwin.modules.workspaces.models import BrandIdentity

from .brand_copy import preview_brand_copy


@login_required
@never_cache
@require_safe
def brand_copy(request, draft_id, selection_version):
    try:
        task, result = preview_brand_copy(
            owner=request.user, draft_id=draft_id, selection_version=selection_version
        )
    except (ObjectDoesNotExist, PermissionDenied) as error:
        raise Http404 from error
    except (ValidationError, CreativeGenerationRejected):
        return HttpResponse(
            "Örnekler doğrulanamadı. Kampanyadaki seçimi yeniden kontrol edin.",
            status=409,
        )
    response = render(
        request,
        "campaigns/brand_copy.html",
        {
            "draft_id": draft_id,
            "selection_version": selection_version,
            "brand_name": task.creative_request.brief.brand_context,
            "identity": task.identity,
            "context": task.context,
            "tone_label": BrandIdentity.Tone(task.identity.tone).label,
            "variants": result.creative_result.variants,
            "source_text": task.creative_request.brief.text,
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    )
    return response
