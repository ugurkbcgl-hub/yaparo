"""Owned synthetic visual editor and bounded, non-retrying scene save."""

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import (
    ObjectDoesNotExist,
    RequestDataTooBig,
    ValidationError,
)
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_safe

from .creative_documents import read_document, save_document


def _document(request, brand_id, document_id):
    try:
        return read_document(
            owner=request.user, brand_id=brand_id, document_id=document_id
        )
    except ObjectDoesNotExist as error:
        raise Http404 from error


@login_required
@never_cache
@require_safe
def editor(request, brand_id, document_id):
    try:
        document = _document(request, brand_id, document_id)
    except ValidationError:
        return JsonResponse({"error": "invalid_saved_scene"}, status=409)
    response = render(
        request,
        "workspaces/document_editor.html",
        {
            "brand": document.identity.brand,
            "document": document,
            "bootstrap": {
                "scene": document.scene,
                "revision": document.revision,
                "save_url": reverse(
                    "brand_documents:save_scene", args=[brand_id, document_id]
                ),
            },
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    )
    response["Referrer-Policy"] = "no-referrer"
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate")
        result[key] = value
    return result


def _bad_constant(value):
    raise ValueError("nonfinite")


@login_required
@never_cache
@require_POST
@csrf_protect
def save_scene(request, brand_id, document_id):
    # Check scope before reading caller-controlled content.
    try:
        _document(request, brand_id, document_id)
    except ValidationError:
        return JsonResponse({"error": "invalid_saved_scene"}, status=409)
    if request.content_type != "application/json":
        return JsonResponse({"error": "json_required"}, status=415)
    try:
        if int(request.META.get("CONTENT_LENGTH") or 0) > 16000:
            raise RequestDataTooBig()
        body = request.body
        if len(body) > 16000:
            raise RequestDataTooBig()
        payload = json.loads(
            body.decode("utf-8"),
            object_pairs_hook=_unique_pairs,
            parse_constant=_bad_constant,
        )
        if type(payload) is not dict or set(payload) != {"revision", "scene"}:
            raise ValueError("invalid fields")
    except RequestDataTooBig:
        return JsonResponse({"error": "too_large"}, status=413)
    except (ValueError, UnicodeError, RecursionError):
        return JsonResponse({"error": "invalid_json"}, status=400)
    try:
        document = save_document(
            owner=request.user,
            brand_id=brand_id,
            document_id=document_id,
            expected_revision=payload["revision"],
            scene=payload["scene"],
        )
    except ObjectDoesNotExist as error:
        raise Http404 from error
    except ValidationError as error:
        status = (
            409 if getattr(error, "code", None) == "stale_document_revision" else 400
        )
        return JsonResponse({"error": "save_refused"}, status=status)
    return JsonResponse({"revision": document.revision})
