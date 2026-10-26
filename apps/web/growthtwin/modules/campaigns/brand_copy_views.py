"""Local candidate preview and explicit stale-safe document apply."""

from dataclasses import asdict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.ai_gateway.contracts import CreativeGenerationRejected
from growthtwin.modules.workspaces.creative_documents import read_document
from growthtwin.modules.workspaces.models import BrandIdentity

from .apply_brand_copy import apply_brand_copy, fits_scene_copy
from .brand_copy import preview_brand_copy
from .brand_copy_forms import ApplyCopyForm


@login_required
@never_cache
@require_safe
def brand_copy(request, draft_id, selection_version):
    try:
        task, result = preview_brand_copy(
            owner=request.user, draft_id=draft_id, selection_version=selection_version
        )
        document = read_document(
            owner=request.user,
            brand_id=task.context.brand_id,
            document_id=task.context.document_id,
        )
    except (ObjectDoesNotExist, PermissionDenied) as error:
        raise Http404 from error
    except (ValidationError, CreativeGenerationRejected):
        return HttpResponse(
            "Örnekler doğrulanamadı. Kampanyadaki seçimi yeniden kontrol edin.",
            status=409,
        )
    apply_enabled = settings.SYNTHETIC_BRAND_COPY_APPLY_ENABLED
    rows = []
    for variant in result.creative_result.variants:
        rows.append(
            {
                "variant": variant,
                "can_title": fits_scene_copy(variant.headline),
                "can_both": fits_scene_copy(variant.headline)
                and fits_scene_copy(variant.body),
                "form": ApplyCopyForm(
                    initial={
                        "task_id": task.task_id,
                        "request_fingerprint": task.fingerprint,
                        "candidate_key": variant.key,
                        "candidate_digest": digest(asdict(variant)),
                        "expected_revision": document.revision,
                    }
                )
                if apply_enabled
                else None,
            }
        )
    response = render(
        request,
        "campaigns/brand_copy.html",
        {
            "draft_id": draft_id,
            "selection_version": selection_version,
            "brand_name": task.creative_request.brief.brand_context,
            "identity": task.identity,
            "context": task.context,
            "tone_label": BrandIdentity.Tone(task.identity.tone).label,
            "variants": result.creative_result.variants,
            "source_text": task.creative_request.brief.text,
            "candidate_rows": rows,
            "apply_enabled": apply_enabled,
            "current_revision": document.revision,
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; form-action 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    )
    return response


@login_required
@never_cache
@require_POST
@csrf_protect
def apply_copy(request, draft_id, selection_version):
    if not settings.DEBUG or not settings.SYNTHETIC_BRAND_COPY_APPLY_ENABLED:
        raise Http404
    form = ApplyCopyForm(request.POST)
    if (
        set(request.POST) <= set(form.fields) | {"csrfmiddlewaretoken"}
        and all(len(request.POST.getlist(key)) == 1 for key in request.POST)
        and form.is_valid()
    ):
        try:
            document = apply_brand_copy(
                owner=request.user,
                draft_id=draft_id,
                selection_version=selection_version,
                **form.cleaned_data,
            )
        except (ObjectDoesNotExist, PermissionDenied) as error:
            raise Http404 from error
        except (ValidationError, CreativeGenerationRejected):
            pass
        else:
            return redirect(
                reverse(
                    "brand_documents:editor",
                    args=[document.identity.brand_id, document.pk],
                )
                + f"?campaign={draft_id}"
            )
    return render(
        request, "campaigns/brand_copy_error.html", {"draft_id": draft_id}, status=409
    )
