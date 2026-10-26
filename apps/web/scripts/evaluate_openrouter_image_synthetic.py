"""Generate one fixed synthetic image through a ZDR-pinned OpenRouter route."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from growthtwin.modules.ai_gateway.evaluation_budget import (
    get_evaluation_budget_state,
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openrouter_image import (  # noqa: F401
    JPEG_SIGNATURE,
    LIST_IMAGE_COST_USD,
    MAX_IMAGE_BYTES,
    MAX_PROMPT_BYTES,
    MAX_RESPONSE_BYTES,
    MODEL,
    PNG_SIGNATURE,
    PROVIDER,
    RESERVATION_USD,
    SYNTHETIC_PROMPT,
    TIMEOUT_SECONDS,
    ImageEvaluationFailure,
    _image_format,
    _request_body,
)
from growthtwin.modules.ai_gateway.openrouter_image import (
    generate_image as _generate,
)


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
