"""Owned local image generation and PNG readback; GET never calls a provider."""

import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from .hosted_image_trial import checked_image, generate_trial, read_trial


@login_required
@never_cache
@require_safe
def preview(request):
    try:
        job = read_trial(request.user)
        if job is not None and job.status == "completed":
            checked_image(job)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return render(request, "workspaces/hosted_trial_error.html", status=409)
    response = render(
        request,
        "workspaces/hosted_image_trial.html",
        {
            "job": job,
            "can_generate": job is None
            and bool(os.environ.get("OPENROUTER_API_KEY"))
            and os.environ.get("GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED") == "1",
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'none'; img-src 'self'; style-src 'self'; "
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
        or request.POST.get("confirm") != "fixed-duru-image"
    ):
        return render(request, "workspaces/hosted_trial_error.html", status=400)
    try:
        generate_trial(request.user)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return render(request, "workspaces/hosted_trial_error.html", status=409)
    return redirect("brands:hosted_image_trial")


@login_required
@never_cache
@require_safe
def content(request, download=False):
    try:
        png = checked_image(read_trial(request.user))
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return HttpResponse("Görsel doğrulanamadı.", status=409)
    response = HttpResponse(png, content_type="image/png")
    disposition = "attachment" if download else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="duru-studio-ai.png"'
    response["Content-Length"] = str(len(png))
    response["X-Content-Type-Options"] = "nosniff"
    return response
