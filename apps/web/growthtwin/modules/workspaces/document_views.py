"""Owner-scoped synthetic creative document forms and portable scene download."""

import json
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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

from growthtwin.modules.workspaces.creative_documents import (
    create_document,
    read_document,
    save_document,
)
from growthtwin.modules.workspaces.creative_materials import checked_materials
from growthtwin.modules.workspaces.design_bundle import export_design_bundle
from growthtwin.modules.workspaces.document_forms import (
    DocumentCreateForm,
    DocumentEditForm,
)
from growthtwin.modules.workspaces.services import get_brand_for_owner

from .campaign_context import campaign_return_id, with_campaign


def _brand(owner, brand_id):
    try:
        return get_brand_for_owner(owner=owner, brand_id=brand_id)
    except ObjectDoesNotExist as error:
        raise Http404 from error


def _document(owner, brand_id, document_id):
    try:
        return read_document(owner=owner, brand_id=brand_id, document_id=document_id)
    except ObjectDoesNotExist as error:
        raise Http404 from error


@login_required
@never_cache
@require_POST
@csrf_protect
def document_create(request, brand_id):
    brand = _brand(request.user, brand_id)
    campaign_id = campaign_return_id(request, brand.workspace_id)
    form = DocumentCreateForm(request.POST)
    if form.is_valid() and form.cleaned_data["brand_id"] == brand.pk:
        try:
            document = create_document(owner=request.user, **form.cleaned_data)
        except ObjectDoesNotExist as error:
            raise Http404 from error
        except ValidationError:
            pass
        else:
            return redirect(
                with_campaign(
                    reverse("brand_documents:detail", args=[brand.pk, document.pk]),
                    campaign_id,
                )
            )
    return render(
        request,
        "workspaces/document_detail.html",
        {"brand": brand, "create_error": True, "campaign_return_id": campaign_id},
        status=409,
    )


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
@csrf_protect
def document_detail(request, brand_id, document_id):
    brand = _brand(request.user, brand_id)
    campaign_id = campaign_return_id(request, brand.workspace_id)
    try:
        document = _document(request.user, brand.pk, document_id)
    except ValidationError:
        return HttpResponse("Çalışma doğrulanamadı. Kayıt değiştirilmedi.", status=409)
    form = DocumentEditForm(
        request.POST if request.method == "POST" else None,
        scene=document.scene,
        revision=document.revision,
    )
    status = 200
    if request.method == "POST":
        status = 409
        if form.is_valid():
            scene = deepcopy(document.scene)
            for layer in scene["layers"]:
                if layer["id"] in ("title", "subtitle"):
                    name = layer["id"]
                    layer["text"] = form.cleaned_data[name]
                    layer["color"] = form.cleaned_data[name + "_color"]
            try:
                save_document(
                    owner=request.user,
                    brand_id=brand.pk,
                    document_id=document.pk,
                    expected_revision=form.cleaned_data["expected_revision"],
                    scene=scene,
                )
            except ObjectDoesNotExist as error:
                raise Http404 from error
            except ValidationError:
                form.add_error(
                    None,
                    "Çalışma kaydedilemedi. Başka bir sekmede değişmiş olabilir. Güncel kaydı açıp yeniden deneyin; eski bilgiler üzerine yazılmadı.",
                )
            else:
                return redirect(
                    with_campaign(
                        reverse("brand_documents:detail", args=[brand.pk, document.pk]),
                        campaign_id,
                    )
                )
    layers = {layer["id"]: layer for layer in document.scene["layers"]}
    return render(
        request,
        "workspaces/document_detail.html",
        {
            "brand": brand,
            "document": document,
            "campaign_return_id": campaign_id,
            "form": form,
            "saved_title": layers["title"],
            "saved_subtitle": layers["subtitle"],
            "materials": checked_materials(document),
            "can_download_bundle": document.material_binding_version == 1
            and settings.DEBUG
            and settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED,
        },
        status=status,
    )


@login_required
@never_cache
@require_safe
def document_download(request, brand_id, document_id):
    try:
        document = _document(request.user, brand_id, document_id)
    except ValidationError:
        return HttpResponse("Çalışma doğrulanamadı. Dosya indirilmedi.", status=409)
    response = HttpResponse(
        json.dumps(document.scene, ensure_ascii=False, allow_nan=False),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="yaparo-scene-{document.pk}.json"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@never_cache
@require_safe
def document_bundle(request, brand_id, document_id):
    if not settings.DEBUG or not settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED:
        raise Http404
    try:
        data = export_design_bundle(
            owner=request.user, brand_id=brand_id, document_id=document_id
        )
    except ObjectDoesNotExist as error:
        raise Http404 from error
    except ValidationError:
        return HttpResponse(
            "Tasarım paketi doğrulanamadı. Dosya indirilmedi.", status=409
        )
    response = HttpResponse(data, content_type="application/zip")
    response["Content-Disposition"] = (
        f'attachment; filename="yaparo-design-{document_id}.zip"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Referrer-Policy"] = "no-referrer"
    return response
