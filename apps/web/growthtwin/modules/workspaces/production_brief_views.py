"""Owned synthetic brief capture and separately admitted one-shot generation."""

from uuid import UUID, uuid4

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from . import brand_generation
from . import production_briefs as service
from .creative_documents import _brand


class BriefForm(forms.Form):
    source = forms.ChoiceField(label="Kaynak tasarım ve kayıt sürümü")
    description = forms.CharField(
        label="Ne üretelim?",
        max_length=1200,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    audience = forms.CharField(label="Kime hitap edecek?", max_length=200, strip=False)
    objective = forms.ChoiceField(
        label="Amaç",
        choices=(
            ("awareness", "Tanıtım"),
            ("traffic", "Ziyaret"),
            ("leads", "Talep toplama"),
        ),
    )
    deliverable = forms.ChoiceField(
        label="İçerik türü",
        choices=(("copy", "Reklam metni"), ("image", "Reklam görseli")),
    )
    identity_version = forms.IntegerField(
        min_value=1, max_value=2**31 - 1, widget=forms.HiddenInput
    )
    expected_version = forms.IntegerField(
        min_value=0, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    request_id = forms.UUIDField(widget=forms.HiddenInput)


def _error():
    return HttpResponse(
        "Talep kaynakları doğrulanamadı. Marka sayfasından güncel kaydı açın.",
        status=409,
    )


@login_required
@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@csrf_protect
@sensitive_post_parameters("description", "audience")
def compose(request, brand_id):
    try:
        service.enabled()
        brand = _brand(request.user, brand_id)
        documents = list(service.options(owner=request.user, brand_id=brand_id))
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    latest = brand.production_requests.first()
    form = BriefForm(
        request.POST if request.method == "POST" else None,
        initial={
            "identity_version": brand.current_version,
            "expected_version": latest.version if latest else 0,
            "request_id": uuid4(),
            "objective": "awareness",
            "deliverable": "copy",
        },
    )
    form.fields["source"].choices = [
        (
            f"{doc.pk}@{doc.revision}",
            f"Tasarım {index} · Kayıt {doc.revision} · Kimlik {doc.identity.version}",
        )
        for index, doc in enumerate(documents, 1)
    ]
    status = 200
    if request.method == "POST":
        closed = set(request.POST) <= set(form.fields) | {
            "csrfmiddlewaretoken"
        } and all(len(request.POST.getlist(k)) == 1 for k in request.POST)
        if closed and form.is_valid():
            data = form.cleaned_data
            doc_id, revision = data["source"].split("@")
            try:
                plan = service.create(
                    owner=request.user,
                    brand_id=brand.pk,
                    document_id=UUID(doc_id),
                    document_revision=int(revision),
                    identity_version=data["identity_version"],
                    expected_version=data["expected_version"],
                    request_id=data["request_id"],
                    brief={
                        key: data[key]
                        for key in (
                            "description",
                            "audience",
                            "objective",
                            "deliverable",
                        )
                    },
                )
            except (PermissionDenied, ObjectDoesNotExist) as error:
                raise Http404 from error
            except Exception:
                pass
            else:
                return redirect(
                    "brands:production_request", brand_id=brand.pk, request_id=plan.pk
                )
        status = 409
    return render(
        request,
        "workspaces/production_brief_form.html",
        {
            "brand": brand,
            "form": form,
            "has_documents": bool(documents),
            "documents": documents,
            "failed": status == 409,
            "requests": brand.production_requests.select_related("identity").all()[:20],
        },
        status=status,
    )


@login_required
@never_cache
@require_safe
def detail(request, brand_id, request_id):
    try:
        plan = service.checked(
            owner=request.user, brand_id=brand_id, request_id=request_id
        )
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    job = None
    can_generate = False
    try:
        job = brand_generation.read(request.user, brand_id, request_id)
        can_generate = True
    except (PermissionDenied, ObjectDoesNotExist):
        pass
    except Exception:
        return _error()
    return render(
        request,
        "workspaces/production_brief_detail.html",
        {"plan": plan, "generation": job, "can_generate": can_generate},
    )


@login_required
@never_cache
@require_POST
@csrf_protect
def generate(request, brand_id, request_id):
    try:
        plan = brand_generation.admitted(request.user, brand_id, request_id)
        if (
            set(request.POST) != {"fingerprint", "csrfmiddlewaretoken"}
            or any(len(request.POST.getlist(k)) != 1 for k in request.POST)
            or request.POST["fingerprint"] != plan.fingerprint
        ):
            return _error()
        brand_generation.generate(request.user, brand_id, request_id)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    return redirect(
        "brands:production_request", brand_id=brand_id, request_id=request_id
    )


@login_required
@never_cache
@require_safe
def generated_image(request, brand_id, request_id):
    try:
        job = brand_generation.read(request.user, brand_id, request_id)
        if job is None or job.status != "completed" or job.kind != "image":
            return _error()
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return _error()
    response = HttpResponse(bytes(job.png), content_type="image/png")
    response["X-Content-Type-Options"] = "nosniff"
    return response
