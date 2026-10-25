"""Owned fixed catalog and default-off generated palette PNG boundary."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from .durable_rasters import create_palette_material, read_palette_material
from .services import prepare_synthetic_materials


@login_required
@never_cache
@require_POST
@csrf_protect
def material_prepare(request, brand_id):
    """Add only code-owned synthetic metadata; request body is intentionally unused."""

    try:
        prepare_synthetic_materials(owner=request.user, brand_id=brand_id)
    except ObjectDoesNotExist as error:
        raise Http404 from error
    except ValidationError:
        # Do not disclose catalog-internal values in a user-facing response.
        return redirect("brands:detail", brand_id=brand_id)
    return redirect("brands:detail", brand_id=brand_id)


def _raster_available():
    if not settings.DEBUG or not settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED:
        raise Http404


@login_required
@never_cache
@require_POST
@csrf_protect
def palette_generate(request, brand_id):
    _raster_available()
    try:
        create_palette_material(owner=request.user, brand_id=brand_id)
    except ObjectDoesNotExist as error:
        raise Http404 from error
    except ValidationError:
        return HttpResponse(
            "Görsel doğrulanamadı. Otomatik tekrar yapılmadı.", status=409
        )
    return redirect("brands:detail", brand_id=brand_id)


@login_required
@never_cache
@require_safe
def palette_image(request, brand_id, material_id):
    _raster_available()
    try:
        pair = read_palette_material(
            owner=request.user, brand_id=brand_id, material_id=material_id
        )
    except ObjectDoesNotExist as error:
        raise Http404 from error
    except ValidationError:
        return HttpResponse("Görsel doğrulanamadı.", status=409)
    response = HttpResponse(bytes(pair.derivative), content_type="image/png")
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = "default-src 'none'; sandbox"
    response["Content-Disposition"] = 'inline; filename="yaparo-synthetic-palette.png"'
    return response
