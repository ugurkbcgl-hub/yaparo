"""Generate one fixed synthetic image through a ZDR-pinned OpenRouter route."""

import argparse
import base64
import binascii
import json
import os
import sys
from datetime import datetime, timezone
from http.client import HTTPSConnection
from pathlib import Path
from uuid import uuid4

from growthtwin.modules.ai_gateway.evaluation_budget import (
    get_evaluation_budget_state,
    reserve_evaluation_cost,
    settle_evaluation_cost,
)

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


def _failure_category(error: Exception) -> tuple[str, int | None]:
    if isinstance(error, ImageEvaluationFailure):
        return error.category, error.http_status
    if isinstance(error, TimeoutError):
        return "network_timeout", None
    if isinstance(error, OSError):
        return "network_or_local_io_error", None
    if isinstance(error, (ValueError, KeyError, IndexError, TypeError)):
        return "invalid_or_unverifiable_response", None
    return "unclassified_failure", None


def _local_directory() -> Path:
    local_data = os.environ.get("LOCALAPPDATA")
    local_root = Path(local_data) if local_data else Path.home() / "AppData/Local"
    result_directory = local_root / "GrowthTwin" / "evaluations" / "visual"
    repository_root = Path(__file__).resolve().parents[3]
    resolved_directory = result_directory.resolve()
    if resolved_directory.is_relative_to(repository_root):
        raise OSError("Evaluation results must be stored outside the repository.")
    resolved_directory.mkdir(parents=True, exist_ok=True)
    return resolved_directory


def _append_jsonl(path: Path, record: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as capture:
        capture.write(json.dumps(record, separators=(",", ":")) + "\n")
        capture.flush()
        os.fsync(capture.fileno())


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


def _generate(
    api_key: str, *, prompt: str = SYNTHETIC_PROMPT
) -> tuple[bytes, str, float]:
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
        result = json.loads(response_body)
    except json.JSONDecodeError as error:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--estimate",
        action="store_true",
        help="Show the fixed request and reservation without network access.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the single pre-authorized synthetic image request.",
    )
    args = parser.parse_args()
    if args.estimate == args.run:
        parser.error("Choose exactly one of --estimate or --run.")

    if args.estimate:
        print(
            f"One {MODEL} 1K 9:16 image; list image price USD "
            f"{LIST_IMAGE_COST_USD:.4f}; local maximum reservation USD "
            f"{RESERVATION_USD:.2f}. Estimate only; no key or network used."
        )
        return 0

    if os.environ.get("GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED") != "1":
        print(
            "The verified no-reset API-key cap was not asserted by the local launcher.",
            file=sys.stderr,
        )
        return 2
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if (
        not isinstance(api_key, str)
        or not api_key.strip()
        or len(api_key) > 512
        or "\r" in api_key
        or "\n" in api_key
    ):
        print("The protected OpenRouter credential is unavailable.", file=sys.stderr)
        return 2

    run_id = uuid4().hex
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    try:
        output_directory = _local_directory()
        capture_path = output_directory / f"image-{timestamp}-{run_id[:8]}.jsonl"
        with capture_path.open("x", encoding="utf-8", newline="\n") as capture:
            capture.write(
                json.dumps(
                    {
                        "record_type": "run",
                        "run_id": run_id,
                        "started_at_utc": datetime.now(timezone.utc).isoformat(),
                        "provider": "openrouter",
                        "model": MODEL,
                        "provider_endpoint": PROVIDER,
                        "synthetic_only": True,
                        "publishable": False,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
            capture.flush()
            os.fsync(capture.fileno())
    except OSError as error:
        print(f"Could not prepare local-only output storage: {error}", file=sys.stderr)
        return 2

    try:
        ledger_path = reserve_evaluation_cost(
            RESERVATION_USD, per_request_limit_usd=RESERVATION_USD
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(
            f"Image request stopped by the local budget ledger: {error}",
            file=sys.stderr,
        )
        return 2

    print("Sending one synthetic image request; no retries or alternate providers.")
    try:
        image_bytes, image_extension, actual_cost = _generate(api_key)
    except Exception as error:
        category, http_status = _failure_category(error)
        failure_record: dict[str, object] = {
            "record_type": "failed",
            "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            "failure_category": category,
            "publishable": False,
        }
        if http_status is not None:
            failure_record["http_status"] = http_status
        try:
            _append_jsonl(capture_path, failure_record)
        except OSError:
            pass
        print(
            f"Image request failed ({category}); its local reservation remains "
            "held. Sensitive details were suppressed and no retry was made.",
            file=sys.stderr,
        )
        return 1

    try:
        settle_evaluation_cost(ledger_path, RESERVATION_USD, actual_cost)
        image_path = output_directory / (
            f"image-{timestamp}-{run_id[:8]}{image_extension}"
        )
        with image_path.open("xb") as image_file:
            image_file.write(image_bytes)
            image_file.flush()
            os.fsync(image_file.fileno())
        _append_jsonl(
            capture_path,
            {
                "record_type": "completed",
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "usage_cost_usd": actual_cost,
                "local_image_path": str(image_path),
                "publishable": False,
            },
        )
    except Exception:
        print(
            "Image generation returned, but local accounting or storage failed. "
            "Do not retry; inspect the local ledger before any further call.",
            file=sys.stderr,
        )
        return 1

    try:
        _, spent, reserved = get_evaluation_budget_state()
        print(
            f"Saved one review-only synthetic PNG locally. Provider-reported "
            f"cost: USD {actual_cost:.6f}. Local evaluation ledger: spent "
            f"USD {spent:.6f}; reserved USD {reserved:.6f}."
        )
        print(str(image_path))
    except Exception:
        print(
            "Image saved and reservation settled; local ledger summary could "
            "not be read.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
