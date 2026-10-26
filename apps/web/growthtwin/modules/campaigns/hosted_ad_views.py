"""Closed owner-scoped choice and version-pinned read-only visual preview."""

from uuid import uuid4

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_safe

from growthtwin.modules.workspaces import hosted_ad_drafts as ads

from . import hosted_ad_selection as service


class ChoiceForm(forms.Form):
    ad_id = forms.UUIDField(widget=forms.HiddenInput)
    revision = forms.IntegerField(
        min_value=1, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    source = forms.RegexField(r"\A[0-9a-f]{64}\Z", widget=forms.HiddenInput)
    expected_version = forms.IntegerField(
        min_value=0, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    request_id = forms.UUIDField(widget=forms.HiddenInput)


def _error():
    return HttpResponse(
        "Görsel seçimi doğrulanamadı. Kampanyaya dönüp güncel seçenekleri açın.",
        status=409,
    )


def reference_context(owner, campaign_id):
    try:
        service.campaign(owner, campaign_id)
    except (PermissionDenied, ObjectDoesNotExist):
        return {"hosted_ad_campaign_enabled": False}
    return {"hosted_ad_campaign_enabled": True}


@login_required
@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@csrf_protect
def choose(request, draft_id):
    try:
        plan = service.campaign(request.user, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    status = 200
    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if (
            set(request.POST) <= set(form.fields) | {"csrfmiddlewaretoken"}
            and all(len(request.POST.getlist(key)) == 1 for key in request.POST)
            and form.is_valid()
        ):
            try:
                service.select(
                    owner=request.user, campaign_id=plan.pk, **form.cleaned_data
                )
            except (PermissionDenied, ObjectDoesNotExist) as error:
                raise Http404 from error
            except Exception:
                pass
            else:
                return redirect("campaigns:hosted_ad_choose", draft_id=plan.pk)
        status = 409
    try:
        current = service.selected(owner=request.user, campaign_id=plan.pk)
        version = current[0].version if current else 0
        rows = []
        for ad in service.options(owner=request.user, campaign_id=plan.pk):
            rows.append(
                {
                    "ad": ad,
                    "label": ads.layout(ad.profile)["label"],
                    "form": ChoiceForm(
                        initial={
                            "ad_id": ad.pk,
                            "revision": ad.revision,
                            "source": ad.source_fingerprint,
                            "expected_version": version,
                            "request_id": uuid4(),
                        }
                    ),
                }
            )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return render(
        request,
        "campaigns/hosted_ad_choice.html",
        {
            "draft": plan,
            "options": rows,
            "current": current[0] if current else None,
            "selected_content": current[1]["content"] if current else None,
            "selection_error": status == 409,
        },
        status=status,
    )


@login_required
@never_cache
@require_safe
def preview(request, draft_id, selection_version):
    try:
        choice, snapshot, _ = service.selected(
            owner=request.user, campaign_id=draft_id, version=selection_version
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    image = snapshot["source_manifest"]["image"]
    geometry = snapshot["layout"]
    response = render(
        request,
        "campaigns/hosted_ad_preview.html",
        {
            "choice": choice,
            "content": snapshot["content"],
            "layout_label": geometry["label"],
            "boot": {
                "id": snapshot["draft_id"],
                "revision": snapshot["revision"],
                "read_only": True,
                "can_export": True,
                "profile": snapshot["profile"],
                "source_fingerprint": snapshot["source_fingerprint"],
                "selection": service.selection_manifest(choice, snapshot),
                "package_url": reverse(
                    "campaigns:hosted_ad_package", args=[draft_id, choice.version]
                ),
                "content": snapshot["content"],
                "width": geometry["width"],
                "height": geometry["height"],
                "mode": geometry["mode"],
                "source_width": image["width"],
                "source_height": image["height"],
                "sha256": image["png_sha256"],
                "image_url": reverse(
                    "campaigns:hosted_ad_image", args=[draft_id, choice.version]
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


@login_required
@never_cache
@require_safe
def package(request, draft_id, selection_version):
    if request.GET:
        return HttpResponse(status=400)
    try:
        data = service.package_snapshot(
            owner=request.user, campaign_id=draft_id, version=selection_version
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    response = JsonResponse(data, json_dumps_params={"ensure_ascii": False})
    response["X-Content-Type-Options"] = "nosniff"
    return response
