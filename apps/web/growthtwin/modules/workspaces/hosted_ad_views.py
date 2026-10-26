"""Explicit saved-output composition and bounded HTML editor forms."""

from dataclasses import asdict

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.ai_gateway.brand_tasks import digest

from . import hosted_ad_drafts as service
from .models import HostedAdDraft


class DraftForm(forms.Form):
    revision = forms.IntegerField(
        min_value=1, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    source = forms.RegexField(r"\A[0-9a-f]{64}\Z", widget=forms.HiddenInput)
    title = forms.CharField(label="Başlık", max_length=60, strip=False)
    body = forms.CharField(label="Açıklama", max_length=100, strip=False)
    cta = forms.CharField(label="Çağrı metni", max_length=30, strip=False)
    color = forms.RegexField(
        r"\A#[0-9a-fA-F]{6}\Z",
        label="Metin rengi",
        widget=forms.TextInput(attrs={"type": "color"}),
    )

    def clean(self):
        data = super().clean()
        if all(key in data for key in ("title", "body", "cta", "color")):
            service.validate_content(
                {key: data[key] for key in ("title", "body", "cta", "color")}
            )
        return data


def _closed(post, fields):
    return set(post) <= set(fields) | {"csrfmiddlewaretoken"} and all(
        len(post.getlist(key)) == 1 for key in post
    )


def _error(request, status=409):
    return render(request, "workspaces/hosted_ad_error.html", status=status)


@login_required
@never_cache
@require_safe
def choices(request):
    try:
        _, text, image, variants, _ = service.sources(request.user)
        rows = []
        for variant in variants:
            formats = []
            for profile in service.LAYOUTS:
                *_, manifest, _ = service.sources(
                    request.user, variant.key, profile=profile
                )
                formats.append(
                    {
                        "profile": profile,
                        "label": service.layout(profile)["label"],
                        "source": digest(manifest),
                        "draft": HostedAdDraft.objects.filter(
                            owner=request.user,
                            text_trial=text,
                            image_trial=image,
                            candidate_key=variant.key,
                            profile=profile,
                        ).first(),
                    }
                )
            rows.append(
                {
                    "variant": asdict(variant),
                    "formats": formats,
                }
            )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error(request)
    return render(request, "workspaces/hosted_ad_choices.html", {"rows": rows})


@login_required
@never_cache
@require_POST
@csrf_protect
def create(request):
    if not _closed(request.POST, {"candidate", "source", "profile"}):
        return _error(request, 400)
    try:
        draft = service.create_draft(
            owner=request.user,
            candidate_key=request.POST.get("candidate"),
            expected_source=request.POST.get("source"),
            profile=request.POST.get("profile", service.PROFILE),
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error(request)
    return redirect("brands:hosted_ad_editor", draft_id=draft.pk)


def _editor(request, draft, form=None, *, status=200):
    form = form or DraftForm(
        initial={
            "revision": draft.revision,
            "source": draft.source_fingerprint,
            **draft.content,
        }
    )
    image = draft.source_manifest["image"]
    geometry = service.layout(draft.profile)
    response = render(
        request,
        "workspaces/hosted_ad_editor.html",
        {
            "draft": draft,
            "form": form,
            "failed_save": status != 200,
            "layout_label": geometry["label"],
            "boot": {
                "image_url": reverse(
                    "brands:hosted_ad_image", kwargs={"draft_id": draft.pk}
                ),
                "width": geometry["width"],
                "height": geometry["height"],
                "mode": geometry["mode"],
                "source_width": image["width"],
                "source_height": image["height"],
                "sha256": image["png_sha256"],
                "content": draft.content,
                "revision": draft.revision,
                "id": str(draft.pk),
                "profile": draft.profile,
                "source_fingerprint": draft.source_fingerprint,
                "package_url": reverse(
                    "brands:hosted_ad_package",
                    kwargs={"draft_id": draft.pk, "revision": draft.revision},
                ),
                "can_export": status == 200,
            },
        },
        status=status,
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; img-src 'self' blob:; style-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    )
    return response


@login_required
@never_cache
@require_safe
def editor(request, draft_id):
    try:
        draft, _ = service.checked_draft(request.user, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error(request)
    return _editor(request, draft)


@login_required
@never_cache
@require_POST
@csrf_protect
def save(request, draft_id):
    form = DraftForm(request.POST)
    if _closed(request.POST, form.fields) and form.is_valid():
        try:
            service.save_draft(
                owner=request.user,
                draft_id=draft_id,
                expected_revision=form.cleaned_data["revision"],
                expected_source=form.cleaned_data["source"],
                content={
                    k: form.cleaned_data[k] for k in service.LIMITS | {"color": 0}
                },
            )
        except (PermissionDenied, ObjectDoesNotExist) as error:
            raise Http404 from error
        except Exception:
            pass
        else:
            return redirect("brands:hosted_ad_editor", draft_id=draft_id)
    try:
        draft, _ = service.checked_draft(request.user, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error(request)
    return _editor(request, draft, form, status=409)


@login_required
@never_cache
@require_safe
def image(request, draft_id):
    try:
        _, png = service.checked_draft(request.user, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return HttpResponse("Taslak görseli doğrulanamadı.", status=409)
    response = HttpResponse(png, content_type="image/png")
    response["Content-Length"] = str(len(png))
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@never_cache
@require_safe
def package(request, draft_id, revision):
    if request.GET:
        return _error(request, 400)
    try:
        snapshot = service.export_snapshot(
            owner=request.user, draft_id=draft_id, revision=revision
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error(request)
    response = JsonResponse(snapshot, json_dumps_params={"ensure_ascii": False})
    response["X-Content-Type-Options"] = "nosniff"
    return response
