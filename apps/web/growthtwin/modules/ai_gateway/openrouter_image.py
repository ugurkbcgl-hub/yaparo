"""Bounded one-call OpenRouter image transport; no persistence or retries."""

import base64
import binascii
import json
from http.client import HTTPSConnection

from .provider_json import load_provider_object

MODEL = "google/gemini-3.1-flash-lite-image"
PROVIDER = "google-vertex/global"
RESERVATION_USD = 0.10
LIST_IMAGE_COST_USD = 0.0336
MAX_PROMPT_BYTES = 4_096
MAX_RESPONSE_BYTES = 24_000_000
MAX_IMAGE_BYTES = 16_000_000
TIMEOUT_SECONDS = 180
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
SYNTHETIC_PROMPT = (
    "Create one polished vertical advertising photograph for a fictional "
    "Turkish coffee roaster. Show a plain, unbranded 250 g terracotta coffee "
    "bag and a ceramic cup on a bright kitchen table, with subtle coastal "
    "Izmir morning light and tasteful editorial food photography. Leave the "
    "upper third uncluttered for later deterministic copy placement. No text, "
    "letters, labels, logos, trademarks, people, discount or health claims, "
    "phone numbers, guarantees, badges, or platform interface. Depict only "
    "the product and setting described. Synthetic evaluation artwork only."
)


class ImageEvaluationFailure(Exception):
    """Safe, non-sensitive category for a failed image request."""

    def __init__(self, category: str, http_status: int | None = None) -> None:
        super().__init__(category)
        self.category = category
        self.http_status = http_status


def _request_body(prompt: str = SYNTHETIC_PROMPT) -> bytes:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "resolution": "1K",
        "aspect_ratio": "9:16",
        "provider": {
            "only": [PROVIDER],
            "allow_fallbacks": False,
            "zdr": True,
            "data_collection": "deny",
        },
    }
    body = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
    if len(body) > MAX_PROMPT_BYTES:
        raise ValueError("Fixed synthetic image request exceeds its size limit.")
    return body


def _image_format(image_bytes: bytes) -> tuple[str, str]:
    if image_bytes.startswith(PNG_SIGNATURE):
        return "image/png", ".png"
    if image_bytes.startswith(JPEG_SIGNATURE):
        return "image/jpeg", ".jpg"
    if (
        len(image_bytes) >= 12
        and image_bytes[:4] == b"RIFF"
        and image_bytes[8:12] == b"WEBP"
    ):
        return "image/webp", ".webp"
    raise ImageEvaluationFailure("invalid_image_format")


def generate_image(
    api_key: str, *, prompt: str = SYNTHETIC_PROMPT
) -> tuple[bytes, str, float]:
    if (
        type(api_key) is not str
        or not api_key.strip()
        or len(api_key) > 512
        or "\r" in api_key
        or "\n" in api_key
    ):
        raise ImageEvaluationFailure("invalid_credential")
    connection = HTTPSConnection("openrouter.ai", timeout=TIMEOUT_SECONDS)
    try:
        connection.request(
            "POST",
            "/api/v1/images",
            body=_request_body(prompt),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        response = connection.getresponse()
        response_body = response.read(MAX_RESPONSE_BYTES + 1)
        if response.status != 200:
            raise ImageEvaluationFailure("http_error", response.status)
        if len(response_body) > MAX_RESPONSE_BYTES:
            raise ImageEvaluationFailure("response_too_large")
    finally:
        connection.close()

    try:
        result = load_provider_object(
            response_body.decode("utf-8"), max_bytes=MAX_RESPONSE_BYTES
        )
    except (ValueError, UnicodeError) as error:
        raise ImageEvaluationFailure("invalid_response_json") from error
    if not isinstance(result, dict):
        raise ImageEvaluationFailure("invalid_response_shape")

    data = result.get("data")
    if not isinstance(data, list) or not data:
        raise ImageEvaluationFailure("missing_image_data")
    if len(data) != 1:
        raise ImageEvaluationFailure("image_count_mismatch")

    usage = result.get("usage")
    if not isinstance(usage, dict) or "cost" not in usage:
        raise ImageEvaluationFailure("missing_usage_cost")
    cost = usage["cost"]
    if type(cost) not in (int, float):
        raise ImageEvaluationFailure("invalid_usage_cost")
    if not 0 <= cost <= RESERVATION_USD:
        raise ImageEvaluationFailure("usage_cost_out_of_bounds")

    image_record = data[0]
    if not isinstance(image_record, dict):
        raise ImageEvaluationFailure("invalid_image_record")
    encoded = image_record.get("b64_json")
    if not isinstance(encoded, str):
        raise ImageEvaluationFailure("missing_encoded_image")
    if len(encoded) > MAX_IMAGE_BYTES * 2:
        raise ImageEvaluationFailure("encoded_image_too_large")
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ImageEvaluationFailure("invalid_image_base64") from error
    if not image_bytes:
        raise ImageEvaluationFailure("invalid_image_format")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ImageEvaluationFailure("decoded_image_too_large")
    detected_media_type, extension = _image_format(image_bytes)
    declared_media_type = image_record.get("media_type")
    if declared_media_type is not None and declared_media_type != detected_media_type:
        raise ImageEvaluationFailure("image_media_type_mismatch")
    return image_bytes, extension, float(cost)
