"""Pre-CSRF boundary for closed synthetic material/design metadata actions.

CsrfViewMiddleware parses POST data to find its token. Reject multipart and
oversized/unknown bodies *before* that middleware so a file upload handler never
receives an attempted customer file merely because a catalog endpoint ignores
``request.FILES`` in its view.
"""

import re

from django.http import HttpResponse
from django.utils.cache import patch_cache_control

_PREPARE_PATH = re.compile(
    r"\A/workspace/(?:brands/[0-9]+/materials/(?:prepare|generate)|campaigns/[0-9]+/design(?:/[0-9]+/copy/apply)?)/\Z"
)
_MAX_FORM_BODY_BYTES = 8 * 1024
_DESIGN_PATH = re.compile(
    r"\A/workspace/campaigns/[0-9]+/design/(?:[0-9]+/(?:preview|image|bundle|copy|copy/apply)/)?\Z"
)
_READ_ONLY_DESIGN = re.compile(
    r"\A/workspace/campaigns/[0-9]+/design/[0-9]+/(?:preview|image|bundle|copy)/\Z"
)
_TRIAL_PATH = re.compile(
    r"\A/workspace/brands/ai-trial/(?:generate/|image/(?:generate/|content/|download/)?|drafts/(?:create/|[0-9a-f-]{36}/(?:save/|image/|revisions/[0-9]+/package\.json)?)?)?\Z"
)
_AI_VISUAL_PATH = re.compile(
    r"\A/workspace/campaigns/[0-9]+/ai-visual/(?:[0-9]+/(?:(?:preview|image)/|package\.json))?\Z"
)


def _headers(response, request):
    if (
        _DESIGN_PATH.fullmatch(request.path)
        or _TRIAL_PATH.fullmatch(request.path)
        or _AI_VISUAL_PATH.fullmatch(request.path)
    ):
        patch_cache_control(
            response, private=True, no_store=True, no_cache=True, max_age=0
        )
        response["X-Robots-Tag"] = "noindex, nofollow"
        response["Referrer-Policy"] = "same-origin"
    return response


class ClosedSyntheticMaterialIntakeMiddleware:
    """Permit only a small browser form body for closed synthetic POSTs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _AI_VISUAL_PATH.fullmatch(request.path):
            allowed = (
                ("GET", "HEAD", "POST")
                if request.path.endswith("/ai-visual/")
                else ("GET", "HEAD")
            )
            if request.method not in allowed:
                response = HttpResponse(status=405)
                response["Allow"] = ", ".join(allowed)
                return _headers(response, request)
        if _TRIAL_PATH.fullmatch(request.path):
            allowed = (
                ("POST",)
                if request.path.endswith(("/generate/", "/create/", "/save/"))
                else ("GET", "HEAD")
            )
            if request.method not in allowed:
                response = HttpResponse(status=405)
                response["Allow"] = ", ".join(allowed)
                return _headers(response, request)
        if _READ_ONLY_DESIGN.fullmatch(request.path) and request.method not in (
            "GET",
            "HEAD",
        ):
            response = HttpResponse(status=405)
            response["Allow"] = "GET, HEAD"
            return _headers(response, request)
        if request.method == "POST" and (
            _PREPARE_PATH.fullmatch(request.path)
            or _TRIAL_PATH.fullmatch(request.path)
            or _AI_VISUAL_PATH.fullmatch(request.path)
        ):
            content_type = (
                request.META.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower()
            )
            content_length = request.META.get("CONTENT_LENGTH")
            try:
                body_length = int(content_length)
            except (TypeError, ValueError):
                return _headers(HttpResponse(status=415), request)
            if (
                content_type != "application/x-www-form-urlencoded"
                or body_length < 1
                or body_length > _MAX_FORM_BODY_BYTES
            ):
                return _headers(HttpResponse(status=415), request)
        return _headers(self.get_response(request), request)
