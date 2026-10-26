"""One explicitly invoked fixed-brand AI sample; never a product route."""

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from growthtwin.modules.ai_gateway.contracts import CreativeGenerationRequest
from growthtwin.modules.ai_gateway.evaluation_budget import (
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openrouter import OpenRouterCreativeGenerator
from growthtwin.modules.content.planning import CampaignBrief
from scripts import evaluate_openrouter_image_synthetic as image_runner

FACTS = (
    "Duru Studio bu deneme için tamamen kurgusal bir seramik markasıdır.",
    "Koleksiyon el yapımı seramik kupalardan oluşur.",
    "Marka renkleri mat zeytin yeşili ve kum bejidir.",
    "Görsel yaklaşım sade gündelik sofra tasarımıdır.",
)
REQUEST = CreativeGenerationRequest(
    brief=CampaignBrief(
        text=" ".join(FACTS)
        + " Yalnız koleksiyonu keşfetmeye çağır. Fiyat, indirim, stok, teslim süresi veya sonuç garantisi belirtilmedi. Türkçe yaz; başlık kısa, gövde en fazla 90 karakter olsun.",
        objective="awareness",
        objective_label="Koleksiyonu keşfetme",
        target_audience="Seramik kupa ve sade sofra tasarımıyla ilgilenen yetişkinler",
        brand_context="Duru Studio · Kurgusal marka; sakin, sade, doğal ton",
    ),
    synthetic_only=True,
)
IMAGE_PROMPT = (
    "Create one premium editorial product photograph for Duru Studio, an entirely "
    "fictional Turkish ceramics brand. Two handmade ceramic mugs, one matte olive "
    "green and one sand beige, on a simple everyday table. Natural side light, "
    "realistic ceramic texture, refined minimal composition. Vertical 9:16. Leave "
    "the upper third uncluttered for later copy placement. No text, logos, letters, "
    "people, prices, discount badges, health claims or guarantees. No reference "
    "images or real customer data. Synthetic evaluation artwork only."
)


def append(path, record):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
        stream.flush()
        os.fsync(stream.fileno())


def run(kind):
    reservation_state = "not_created"
    try:
        if kind not in ("text", "image"):
            raise ValueError("Unknown sample kind")
        if kind == "text":
            generator = OpenRouterCreativeGenerator()
            reservation = generator.maximum_reserved_cost(
                generator.request_body(REQUEST)
            )
            if reservation > 0.01:
                raise RuntimeError("Reservation exceeds single-call ceiling")
            model = generator.model
            source_hash = REQUEST.source_hash
        else:
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if (
                not api_key.strip()
                or len(api_key) > 512
                or any(char in api_key for char in "\r\n")
            ):
                raise RuntimeError("Protected credential unavailable")
            reservation = image_runner.RESERVATION_USD
            model = image_runner.MODEL
            source_hash = hashlib.sha256(IMAGE_PROMPT.encode()).hexdigest()
        directory = Path(os.environ["LOCALAPPDATA"]) / "GrowthTwin" / "evaluations"
        if directory.resolve().is_relative_to(Path(__file__).resolve().parents[3]):
            raise RuntimeError("Capture cannot be in repository")
        directory.mkdir(parents=True, exist_ok=True)
        call_id = uuid4().hex
        path = (
            directory
            / f"brand-{kind}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{call_id[:8]}.jsonl"
        )
        with path.open("x", encoding="utf-8") as stream:
            stream.write("")
        ledger = reserve_evaluation_cost(
            reservation, per_request_limit_usd=0.01 if kind == "text" else 0.10
        )
        reservation_state = "held"
        append(
            path,
            {
                "record_type": "started",
                "call_id": call_id,
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "model": model,
                "synthetic_only": True,
                "source_hash": source_hash,
                "facts": FACTS,
                "image_prompt": IMAGE_PROMPT if kind == "image" else None,
                "reserved_usd": reservation,
                "publishable": False,
            },
        )
        if kind == "text":
            result = generator.generate(REQUEST)
            if generator.last_usage is None or generator.last_cost_usd is None:
                raise RuntimeError("Unverified accounting")
            actual_cost = generator.last_cost_usd
            details = {
                "model": generator.last_model,
                "upstream_provider": generator.last_provider,
                "usage": generator.last_usage,
                "source_hash": result.source_hash,
                "variants": [asdict(row) for row in result.variants],
            }
        else:
            image_bytes, extension, actual_cost = image_runner._generate(
                api_key, prompt=IMAGE_PROMPT
            )
            image_path = path.with_suffix(extension)
            with image_path.open("xb") as stream:
                stream.write(image_bytes)
                stream.flush()
                os.fsync(stream.fileno())
            details = {
                "model": model,
                "requested_provider": image_runner.PROVIDER,
                "source_hash": source_hash,
                "local_image_path": str(image_path),
                "image_sha256": hashlib.sha256(image_bytes).hexdigest(),
            }
        append(
            path,
            {
                "record_type": "result",
                "call_id": call_id,
                **details,
                "actual_usd": actual_cost,
                "publishable": False,
                "review_required": True,
            },
        )
        settle_evaluation_cost(ledger, reservation, actual_cost)
        reservation_state = "settled"
        append(
            path,
            {
                "record_type": "settled",
                "call_id": call_id,
                "actual_usd": actual_cost,
            },
        )
        print(
            json.dumps(
                {
                    "result": "captured",
                    "path": str(path),
                    "model": model,
                    "actual_usd": actual_cost,
                    "publishable": False,
                }
            )
        )
        return 0
    except Exception as error:
        # Never echo provider response/credential exceptions or retry. Distinguish
        # an unresolved hold from a failure after successful settlement.
        print(
            json.dumps(
                {
                    "result": "stopped",
                    "error_type": type(error).__name__,
                    "details": "suppressed",
                    "automatic_retry": False,
                    "reservation_state": reservation_state,
                }
            )
        )
        return 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("text", "image"), required=True)
    parser.add_argument("--run", action="store_true", required=True)
    args = parser.parse_args()
    return run(args.kind)


if __name__ == "__main__":
    sys.exit(main())
