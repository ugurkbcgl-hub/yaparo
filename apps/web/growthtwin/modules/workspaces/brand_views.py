"""Owner-scoped, synthetic brand identity screens."""

import re
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from growthtwin.modules.assets.models import MaterialRasterPair
from growthtwin.modules.assets.services import list_materials
from growthtwin.modules.workspaces.brand_forms import (
    TONES,
    BrandCreateForm,
    BrandIdentityForm,
)
from growthtwin.modules.workspaces.models import (
    Brand,
    BrandCreativeDocument,
    BrandIdentity,
    Workspace,
)
from growthtwin.modules.workspaces.services import (
    SYNTHETIC_BRAND_PRESETS,
    create_brand_for_owner,
    get_brand_for_owner,
    update_brand_identity_for_owner,
)

from .campaign_context import campaign_return_id


def _brand(owner, brand_id):
    try:
        return get_brand_for_owner(owner=owner, brand_id=brand_id)
    except ObjectDoesNotExist as error:
        raise Http404 from error


def _foreground(color):
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    luminance = sum(
        value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722))
    )
    return "#000000" if luminance > 0.179 else "#FFFFFF"


def _identity_row(identity):
    row = {
        "identity": identity,
        "tone": dict(TONES).get(identity.tone, identity.tone),
        "primary": identity.primary_color
        if re.fullmatch(r"#[0-9a-fA-F]{6}", identity.primary_color)
        else "#245C48",
        "secondary": identity.secondary_color
        if re.fullmatch(r"#[0-9a-fA-F]{6}", identity.secondary_color)
        else "#F4E8D2",
    }
    row["foreground"] = _foreground(row["secondary"])
    row["logo_foreground"] = _foreground(row["primary"])
    return row


@login_required
@never_cache
@require_safe
def brand_list(request):
    brands = Brand.objects.filter(
        workspace__owner=request.user, is_archived=False
    ).select_related("workspace")
    rows = [
        {"brand": brand, "preview": _identity_row(brand.current_identity)}
        for brand in brands
    ]
    return render(
        request,
        "workspaces/brand_list.html",
        {
            "rows": rows,
            "has_workspace": Workspace.objects.filter(owner=request.user).exists(),
        },
    )


@login_required
@never_cache
@require_POST
def prepare_workspace(request):
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        if not Workspace.objects.filter(owner=request.user).exists():
            Workspace.objects.create(
                owner=request.user, name="Örnek marka çalışma alanı"
            )
    return redirect("brands:create")


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def brand_create(request):
    form = BrandCreateForm(
        request.POST if request.method == "POST" else None, owner=request.user
    )
    if request.method == "POST" and form.is_valid():
        try:
            brand = create_brand_for_owner(
                owner=request.user,
                workspace_id=form.cleaned_data["workspace"].pk,
                fixture=form.cleaned_data["fixture"],
            )
        except ObjectDoesNotExist as error:
            raise Http404 from error
        except ValidationError:
            form.add_error(
                None, "Bu örnek şu anda eklenemiyor. Marka listesini kontrol edin."
            )
        else:
            return redirect("brands:detail", brand_id=brand.pk)
    return render(
        request,
        "workspaces/brand_form.html",
        {
            "form": form,
            "creating": True,
            "has_workspace": Workspace.objects.filter(owner=request.user).exists(),
        },
    )


@login_required
@never_cache
@require_safe
def brand_detail(request, brand_id):
    brand = _brand(request.user, brand_id)
    identities = BrandIdentity.objects.filter(brand=brand).order_by("-version")
    materials = list_materials(owner=request.user, brand_id=brand.pk)
    material_rows = []
    for material in materials:
        version = next(
            (
                item
                for item in material.versions.all()
                if item.version == material.current_version
            ),
            None,
        )
        if version is not None:
            raster = (
                MaterialRasterPair.objects.filter(version=version)
                .values("original_size", "derivative_size")
                .first()
            )
            material_rows.append(
                {
                    "material": material,
                    "version": version,
                    "raster": raster,
                    "document_request_id": uuid.uuid4(),
                }
            )
    return render(
        request,
        "workspaces/brand_detail.html",
        {
            "brand": brand,
            "preview": _identity_row(brand.current_identity),
            "history": [_identity_row(item) for item in identities],
            "preset": SYNTHETIC_BRAND_PRESETS[brand.fixture],
            "document_request_id": uuid.uuid4(),
            "campaign_return_id": campaign_return_id(request, brand.workspace_id),
            "documents": BrandCreativeDocument.objects.filter(identity__brand=brand)
            .select_related("identity")
            .order_by("-created_at"),
            "material_rows": material_rows,
            "can_generate_raster": settings.DEBUG
            and settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED,
        },
    )


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def brand_edit(request, brand_id):
    brand = _brand(request.user, brand_id)
    current = brand.current_identity
    initial = {
        name: getattr(current, name)
        for name in ("primary_color", "secondary_color", "tone", "tagline_key")
    }
    initial["expected_version"] = current.version
    form = BrandIdentityForm(
        request.POST if request.method == "POST" else None, brand=brand, initial=initial
    )
    status = 200
    if request.method == "POST" and form.is_valid():
        try:
            update_brand_identity_for_owner(
                owner=request.user, brand_id=brand.pk, **form.cleaned_data
            )
        except ObjectDoesNotExist as error:
            raise Http404 from error
        except ValidationError as error:
            form.add_error(
                None,
                "Değişiklik kaydedilemedi. Marka başka bir sekmede güncellenmiş olabilir. Güncel sürümü açıp yeniden deneyin; eski bilgiler üzerine yazılmadı.",
            )
            status = (
                409 if getattr(error, "code", None) == "stale_brand_version" else 400
            )
        else:
            return redirect("brands:detail", brand_id=brand.pk)
    return render(
        request,
        "workspaces/brand_form.html",
        {"form": form, "brand": brand, "creating": False},
        status=status,
    )
