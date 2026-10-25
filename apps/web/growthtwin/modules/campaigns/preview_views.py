"""Private, GET-only campaign snapshot preview; no write or publication path."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from growthtwin.modules.workspaces.creative_scenes import uses_palette

from .design_bundle import export_selected_bundle
from .design_preview import selected_palette, selected_snapshot


@login_required
@never_cache
@require_safe
def preview(request, draft_id, selection_version):
    try:
        choice = selected_snapshot(
            owner=request.user, draft_id=draft_id, selection_version=selection_version
        )
    except (ObjectDoesNotExist, PermissionDenied) as error:
        raise Http404 from error
    except ValidationError:
        return HttpResponse(
            "Seçim değişmiş veya doğrulanamıyor. Kampanyaya dönün.", status=409
        )
    scene = choice.snapshot.scene
    response = render(
        request,
        "campaigns/design_preview.html",
        {
            "choice": choice,
            "scene": scene,
            "bundle_enabled": settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED,
            "bootstrap": {
                "scene": scene,
                "selection_version": choice.version,
                "palette_url": reverse(
                    "campaigns:design_image", args=[draft_id, choice.version]
                )
                if uses_palette(scene)
                else None,
            },
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "base-uri 'none'; frame-ancestors 'none'"
    )
    return response


@login_required
@never_cache
@require_safe
def bundle(request, draft_id, selection_version):
    try:
        data = export_selected_bundle(
            owner=request.user, draft_id=draft_id, selection_version=selection_version
        )
    except (ObjectDoesNotExist, PermissionDenied) as error:
        raise Http404 from error
    except ValidationError:
        return HttpResponse(
            "Paket hazırlanamadı. Seçili kaydı yeniden kontrol edin.", status=409
        )
    response = HttpResponse(data, content_type="application/zip")
    response["Content-Disposition"] = (
        f'attachment; filename="yaparo-campaign-{draft_id}-selection-{selection_version}.zip"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@never_cache
@require_safe
def image(request, draft_id, selection_version):
    try:
        data = selected_palette(
            owner=request.user, draft_id=draft_id, selection_version=selection_version
        )
    except (ObjectDoesNotExist, PermissionDenied) as error:
        raise Http404 from error
    except ValidationError:
        return HttpResponse(status=409)
    response = HttpResponse(data, content_type="image/png")
    response["X-Content-Type-Options"] = "nosniff"
    return response
