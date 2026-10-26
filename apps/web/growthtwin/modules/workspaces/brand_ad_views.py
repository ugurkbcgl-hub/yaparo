"""Explicit offline source selection and saved brand creative editor."""

from uuid import UUID

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.ai_gateway.brand_tasks import digest

from . import brand_ad_drafts as service
from . import brand_generation
from .creative_documents import _brand
from .hosted_ad_views import DraftForm, _closed
from .models import BrandAdDraft, BrandProductionRequest


class SelectionForm(forms.Form):
    text = forms.ChoiceField(label="Kaydedilmiş reklam metni")
    image = forms.ChoiceField(label="Kaydedilmiş AI görseli")


def _form(owner, brand_id, data=None):
    service.enabled()
    brand = _brand(owner, brand_id)
    form = SelectionForm(data)
    text, image = [("", "Seçin…")], [("", "Seçin…")]
    for plan in BrandProductionRequest.objects.filter(
        brand=brand, generation__status="completed"
    ).order_by("-version")[:20]:
        try:
            job = brand_generation.read(owner, brand_id, plan.pk)
        except Exception:
            continue
        if job.kind == "copy":
            text.extend(
                (f"{plan.pk}|{v['key']}", f"Talep {plan.version} · {v['headline']}")
                for v in job.output["variants"]
            )
        else:
            image.append(
                (str(plan.pk), f"Talep {plan.version} · Kimlik {plan.identity.version}")
            )
    form.fields["text"].choices = text
    form.fields["image"].choices = image
    return brand, form


def _selection(form):
    identifier, candidate = form.cleaned_data["text"].split("|", 1)
    return UUID(identifier), UUID(form.cleaned_data["image"]), candidate


def _error():
    return HttpResponse(
        "Taslak kaynakları doğrulanamadı. Markadan kayıtlı seçenekleri yeniden açın.",
        status=409,
    )


@login_required
@never_cache
@require_safe
def choices(request, brand_id):
    try:
        brand, form = _form(request.user, brand_id, request.GET or None)
        preview = None
        if request.GET:
            if (
                set(request.GET) != {"text", "image"}
                or any(len(request.GET.getlist(k)) != 1 for k in request.GET)
                or not form.is_valid()
            ):
                return _error()
            a, b, key = _selection(form)
            _, _, candidate, manifest = service.pair(request.user, brand_id, a, b, key)
            preview = {
                "candidate": candidate,
                "source": digest(manifest),
                "image_request": b,
                "identity": manifest["identity"],
                "brand_name": manifest["brand_name"],
            }
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return render(
        request,
        "workspaces/brand_ad_choices.html",
        {
            "brand": brand,
            "form": form,
            "preview": preview,
            "drafts": BrandAdDraft.objects.filter(brand=brand).order_by("-updated_at")[
                :20
            ],
        },
    )


@login_required
@never_cache
@require_POST
@csrf_protect
def create(request, brand_id):
    try:
        _, form = _form(request.user, brand_id, request.POST)
        if (
            not _closed(request.POST, {"text", "image", "source"})
            or not form.is_valid()
        ):
            return _error()
        a, b, key = _selection(form)
        draft = service.create(
            owner=request.user,
            brand_id=brand_id,
            text_request=a,
            image_request=b,
            candidate_key=key,
            expected_source=request.POST.get("source"),
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return redirect("brands:brand_ad_editor", brand_id=brand_id, draft_id=draft.pk)


def _editor(request, draft, form=None, status=200):
    from growthtwin.modules.campaigns.brand_ad_views import start_form

    try:
        campaign_form = start_form(draft) if status == 200 else None
    except PermissionDenied:
        campaign_form = None
    form = form or DraftForm(
        initial={
            "revision": draft.revision,
            "source": draft.source_fingerprint,
            **draft.content,
        }
    )
    manifest = draft.source_manifest
    photo = manifest["image"]["output"]
    response = render(
        request,
        "workspaces/brand_ad_editor.html",
        {
            "draft": draft,
            "form": form,
            "failed_save": status != 200,
            "campaign_form": campaign_form,
            "boot": {
                "id": str(draft.pk),
                "brand_id": str(draft.brand_id),
                "brand_name": manifest["brand_name"],
                "secondary_color": manifest["identity"]["secondary_color"],
                "content": draft.content,
                "revision": draft.revision,
                "can_export": status == 200,
                "can_use_saved": status == 200,
                "width": 768,
                "height": 1376,
                "mode": "overlay",
                "source_width": photo["width"],
                "source_height": photo["height"],
                "sha256": photo["png_sha256"],
                "image_url": reverse(
                    "brands:brand_ad_image", args=[draft.brand_id, draft.pk]
                ),
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
def editor(request, brand_id, draft_id):
    try:
        draft, _ = service.checked(request.user, brand_id, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return _editor(request, draft)


@login_required
@never_cache
@require_POST
@csrf_protect
def save(request, brand_id, draft_id):
    form = DraftForm(request.POST)
    try:
        if _closed(request.POST, form.fields) and form.is_valid():
            service.save(
                owner=request.user,
                brand_id=brand_id,
                draft_id=draft_id,
                expected_revision=form.cleaned_data["revision"],
                expected_source=form.cleaned_data["source"],
                content={
                    k: form.cleaned_data[k] for k in ("title", "body", "cta", "color")
                },
            )
            return redirect(
                "brands:brand_ad_editor", brand_id=brand_id, draft_id=draft_id
            )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        pass
    try:
        draft, _ = service.checked(request.user, brand_id, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return _editor(request, draft, form, status=409)


@login_required
@never_cache
@require_safe
def image(request, brand_id, draft_id):
    try:
        _, png = service.checked(request.user, brand_id, draft_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    response = HttpResponse(png, content_type="image/png")
    response["X-Content-Type-Options"] = "nosniff"
    return response
