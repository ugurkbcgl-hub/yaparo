"""Closed local campaign-to-design choice; no publishing or asset intake."""

from uuid import uuid4

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from growthtwin.modules.workspaces.models import Brand

from .design_selection import current_design, design_options, owned_draft, select_design


class DesignChoiceForm(forms.Form):
    brand_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    document_id = forms.UUIDField(widget=forms.HiddenInput)
    expected_document_revision = forms.IntegerField(
        min_value=1, max_value=2**31 - 1, widget=forms.HiddenInput
    )
    expected_selection_version = forms.IntegerField(
        min_value=0, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    request_id = forms.UUIDField(widget=forms.HiddenInput)


def reference_context(owner, draft_id):
    if not settings.DEBUG or not settings.SYNTHETIC_CAMPAIGN_DESIGN_ENABLED:
        return {"campaign_design_enabled": False}
    context = {"campaign_design_enabled": True}
    context["brand_copy_preview_enabled"] = (
        settings.SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED
    )
    try:
        choice = current_design(owner=owner, draft_id=draft_id)
    except (ObjectDoesNotExist, PermissionDenied, ValidationError):
        context["design_unavailable"] = True
        return context
    if choice:
        context.update(
            design_choice=choice,
            design_changed=choice.snapshot.document.revision
            != choice.snapshot.revision,
            design_title=next(
                layer["text"]
                for layer in choice.snapshot.scene["layers"]
                if layer["id"] == "title"
            ),
        )
    return context


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
@csrf_protect
def campaign_design(request, draft_id):
    if not settings.DEBUG or not settings.SYNTHETIC_CAMPAIGN_DESIGN_ENABLED:
        raise Http404
    try:
        draft = owned_draft(request.user, draft_id)
    except ObjectDoesNotExist as error:
        raise Http404 from error
    status = 200
    if request.method == "POST":
        form = DesignChoiceForm(request.POST)
        if (
            set(request.POST) <= set(form.fields) | {"csrfmiddlewaretoken"}
            and form.is_valid()
        ):
            try:
                select_design(
                    owner=request.user, draft_id=draft.pk, **form.cleaned_data
                )
            except ObjectDoesNotExist as error:
                raise Http404 from error
            except ValidationError:
                pass
            else:
                return redirect("campaigns:design", draft_id=draft.pk)
        status = 409
    current_version = (
        draft.design_choices.values_list("version", flat=True).first() or 0
    )
    options = []
    for document in design_options(owner=request.user, draft_id=draft.pk):
        options.append(
            {
                "document": document,
                "title": next(
                    layer["text"]
                    for layer in document.scene["layers"]
                    if layer["id"] == "title"
                ),
                "form": DesignChoiceForm(
                    initial=dict(
                        brand_id=document.identity.brand_id,
                        document_id=document.pk,
                        expected_document_revision=document.revision,
                        expected_selection_version=current_version,
                        request_id=uuid4(),
                    )
                ),
            }
        )
    context = reference_context(request.user, draft.pk)
    context.update(
        draft=draft,
        options=options,
        selection_error=status == 409,
        is_design_chooser=True,
        design_brands=Brand.objects.filter(
            workspace_id=draft.workspace_id,
            workspace__owner=request.user,
            workspace__owner__is_active=True,
            is_archived=False,
        ).order_by("pk")[:20],
    )
    response = render(
        request, "campaigns/design_selection.html", context, status=status
    )
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response
