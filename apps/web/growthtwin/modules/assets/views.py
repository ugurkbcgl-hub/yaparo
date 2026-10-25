"""HTTP boundary for preparing the fixed, metadata-only synthetic catalog."""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

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
