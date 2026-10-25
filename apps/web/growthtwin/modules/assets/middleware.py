"""Pre-CSRF boundary for the body-less synthetic material catalog action.

CsrfViewMiddleware parses POST data to find its token. Reject multipart and
oversized/unknown bodies *before* that middleware so a file upload handler never
receives an attempted customer file merely because a catalog endpoint ignores
``request.FILES`` in its view.
"""

import re

from django.http import HttpResponse

_PREPARE_PATH = re.compile(
    r"\A/workspace/brands/[0-9]+/materials/(?:prepare|generate)/\Z"
)
_MAX_FORM_BODY_BYTES = 8 * 1024


class ClosedSyntheticMaterialIntakeMiddleware:
    """Permit only a small browser form body for the fixed-catalog POST."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and _PREPARE_PATH.fullmatch(request.path):
            content_type = (
                request.META.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower()
            )
            content_length = request.META.get("CONTENT_LENGTH")
            try:
                body_length = int(content_length)
            except (TypeError, ValueError):
                return HttpResponse(status=415)
            if (
                content_type != "application/x-www-form-urlencoded"
                or body_length < 1
                or body_length > _MAX_FORM_BODY_BYTES
            ):
                return HttpResponse(status=415)
        return self.get_response(request)
