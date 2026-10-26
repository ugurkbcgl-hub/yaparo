"""In-site brand campaign creation, revision selection and readonly preview."""

from uuid import uuid4

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from growthtwin.modules.workspaces.hosted_ad_views import _closed

from . import brand_ad_selection as service
from . import brand_settings
from .hosted_ad_views import ChoiceForm


class StartForm(forms.Form):
    revision = forms.IntegerField(
        min_value=1, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    source = forms.RegexField(r"\A[0-9a-f]{64}\Z", widget=forms.HiddenInput)
    request_id = forms.UUIDField(widget=forms.HiddenInput)
    synthetic_confirmation = forms.BooleanField(
        label="Yalnız sentetik kampanya planı oluşturuyorum; reklam yayını ve harcama başlamaz."
    )


def start_form(ad):
    service.enabled()
    return StartForm(
        initial={
            "revision": ad.revision,
            "source": ad.source_fingerprint,
            "request_id": uuid4(),
        }
    )


def _error():
    return HttpResponse(
        "Kampanya reklam seçimi doğrulanamadı. Güncel kaydı yeniden açın.", status=409
    )


def reference_context(owner, campaign_id):
    try:
        service.campaign(owner, campaign_id)
    except (PermissionDenied, ObjectDoesNotExist):
        return {"brand_ad_campaign_enabled": False}
    return {"brand_ad_campaign_enabled": True}


@login_required
@never_cache
@require_POST
@csrf_protect
def start(request, brand_id, draft_id):
    form = StartForm(request.POST)
    if not _closed(request.POST, form.fields) or not form.is_valid():
        return _error()
    try:
        data = {
            k: v for k, v in form.cleaned_data.items() if k != "synthetic_confirmation"
        }
        choice = service.start(
            owner=request.user, brand_id=brand_id, ad_id=draft_id, **data
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return redirect("campaigns:brand_ad_choose", draft_id=choice.campaign_id)


@login_required
@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@csrf_protect
def choose(request, draft_id):
    try:
        plan = service.campaign(request.user, draft_id)
        status = 200
        if request.method == "POST":
            form = ChoiceForm(request.POST)
            if _closed(request.POST, form.fields) and form.is_valid():
                try:
                    service.select(
                        owner=request.user, campaign_id=plan.pk, **form.cleaned_data
                    )
                except (PermissionDenied, ObjectDoesNotExist):
                    raise
                except Exception:
                    pass
                else:
                    return redirect("campaigns:brand_ad_choose", draft_id=plan.pk)
            status = 409
        choice, snapshot, _ = service.selected(owner=request.user, campaign_id=plan.pk)
        rows = [
            {
                "ad": ad,
                "form": ChoiceForm(
                    initial={
                        "ad_id": ad.pk,
                        "revision": ad.revision,
                        "source": ad.source_fingerprint,
                        "expected_version": choice.version,
                        "request_id": uuid4(),
                    }
                ),
            }
            for ad in service.options(owner=request.user, campaign_id=plan.pk)
        ]
        setup_context = brand_settings.context(request.user, plan.pk)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return render(
        request,
        "campaigns/brand_ad_choice.html",
        {
            "plan": plan,
            "choice": choice,
            "snapshot": snapshot,
            "rows": rows,
            "selection_error": status == 409,
            **setup_context,
        },
        status=status,
    )


@login_required
@never_cache
@require_safe
def preview(request, draft_id, selection_version):
    try:
        choice, data, _ = service.selected(
            owner=request.user, campaign_id=draft_id, version=selection_version
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    manifest = data["source_manifest"]
    photo = manifest["image"]["output"]
    response = render(
        request,
        "campaigns/brand_ad_preview.html",
        {
            "choice": choice,
            "content": data["content"],
            "brand_name": manifest["brand_name"],
            "boot": {
                "id": data["ad_id"],
                "brand_id": data["brand_id"],
                "brand_name": manifest["brand_name"],
                "secondary_color": manifest["identity"]["secondary_color"],
                "read_only": True,
                "can_export": False,
                "campaign_id": str(choice.campaign_id),
                "selection_version": choice.version,
                "content": data["content"],
                "revision": data["ad_revision"],
                "width": 768,
                "height": 1376,
                "mode": "overlay",
                "source_width": photo["width"],
                "source_height": photo["height"],
                "sha256": photo["png_sha256"],
                "image_url": reverse(
                    "campaigns:brand_ad_image",
                    args=[choice.campaign_id, choice.version],
                ),
            },
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; img-src 'self' blob:; style-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    )
    return response


@login_required
@never_cache
@require_safe
def image(request, draft_id, selection_version):
    try:
        _, _, png = service.selected(
            owner=request.user, campaign_id=draft_id, version=selection_version
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    response = HttpResponse(png, content_type="image/png")
    response["X-Content-Type-Options"] = "nosniff"
    return response
