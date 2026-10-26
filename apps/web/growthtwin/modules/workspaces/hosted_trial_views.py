"""Authenticated fixed-source real AI trial; GET never dispatches."""

import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.ai_gateway.brand_sample import FACTS

from .hosted_trial import checked_variants, generate_trial, read_trial


@login_required
@never_cache
@require_safe
def preview(request):
    try:
        job = read_trial(request.user)
        variants = checked_variants(job)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except (ValueError, TypeError):
        return render(request, "workspaces/hosted_trial_error.html", status=409)
    response = render(
        request,
        "workspaces/hosted_trial.html",
        {
            "job": job,
            "variants": variants,
            "facts": FACTS,
            "image_trial_enabled": settings.LOCAL_HOSTED_IMAGE_TRIAL_ENABLED,
            "can_generate": job is None
            and bool(os.environ.get("OPENROUTER_API_KEY"))
            and os.environ.get("GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED") == "1",
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'none'; style-src 'self'; "
        "form-action 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    )
    return response


@transaction.non_atomic_requests
@login_required
@never_cache
@require_POST
@csrf_protect
def generate(request):
    if (
        set(request.POST) - {"confirm", "csrfmiddlewaretoken"}
        or any(len(request.POST.getlist(key)) != 1 for key in request.POST)
        or request.POST.get("confirm") != "fixed-duru-text"
    ):
        return render(request, "workspaces/hosted_trial_error.html", status=400)
    try:
        generate_trial(request.user)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        # DEBUG pages must not expose credential/provider/storage exceptions.
        return render(request, "workspaces/hosted_trial_error.html", status=409)
    return redirect("brands:hosted_trial")
