"""Opt-in, synthetic-only OpenAI Responses API adapter for offline evaluation."""

import json
import os
from http.client import HTTPException, HTTPSConnection

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
    CreativeGenerationResult,
    validate_generation_result,
)
from growthtwin.modules.ai_gateway.creative_format import (
    CREATIVE_SCHEMA,
    CREATIVE_SYSTEM_PROMPT,
)
from growthtwin.modules.content.planning import CampaignBrief

from .provider_json import load_provider_object, parse_creative_variants

OPENAI_HOST = "api.openai.com"
OPENAI_PATH = "/v1/responses"
OPENAI_MODEL = "gpt-6-luna"
OPENAI_TIMEOUT_SECONDS = 30
MAX_RESPONSE_BYTES = 65_536
MAX_OUTPUT_TOKENS = 512
MAX_REQUEST_BYTES = 4_096
OUTPUT_PRICE_PER_MILLION = 0.50
MAX_INPUT_PRICE_PER_MILLION = 0.125


class OpenAICreativeGenerator:
    """Single-request hosted adapter; it has no retry or product-route behavior."""

    def __init__(self, *, api_key: str | None = None):
        key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
        if (
            not isinstance(key, str)
            or not key.strip()
            or len(key) > 512
            or "\r" in key
            or "\n" in key
        ):
            raise ValueError("Set OPENAI_API_KEY in a secure local environment.")
        self._api_key = key
        self.generator_id = f"openai-{OPENAI_MODEL}"
        self.last_usage: dict[str, int] | None = None
        self.last_cost_usd: float | None = None
        self.last_model: str | None = None

    def request_body(self, request: CreativeGenerationRequest) -> bytes:
        if not isinstance(request, CreativeGenerationRequest):
            raise CreativeGenerationRejected("Üretim isteği geçersiz.")
        if request.synthetic_only is not True:
            raise CreativeGenerationRejected(
                "Yalnızca sentetik istekler kullanılabilir."
            )
        if not isinstance(request.brief, CampaignBrief):
            raise CreativeGenerationRejected("Kampanya brief biçimi geçersiz.")

        brief_limits = {
            "text": 2_000,
            "objective_label": 120,
            "target_audience": 240,
            "brand_context": 240,
        }
        for field, maximum in brief_limits.items():
            value = getattr(request.brief, field)
            if not isinstance(value, str) or len(value) > maximum:
                raise CreativeGenerationRejected("Sentetik brief boyutu geçersiz.")
        if not request.brief.text.strip():
            raise CreativeGenerationRejected("Sentetik brief boş olamaz.")

        brief_payload = {
            "brief": request.brief.text,
            "campaign_objective": request.brief.objective_label,
            "target_audience": request.brief.target_audience,
            "brand_or_offer": request.brief.brand_context,
        }
        body = json.dumps(
            {
                "model": OPENAI_MODEL,
                "instructions": CREATIVE_SYSTEM_PROMPT,
                "input": json.dumps(brief_payload, ensure_ascii=False),
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "store": False,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "creative_variants",
                        "strict": True,
                        "schema": CREATIVE_SCHEMA,
                    }
                },
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(body) > MAX_REQUEST_BYTES:
            raise CreativeGenerationRejected("Sentetik istek boyut sınırını aşıyor.")
        return body

    def maximum_reserved_cost(self, body: bytes) -> float:
        """Conservative per-call reservation, including tokenization margin."""

        if not isinstance(body, bytes) or len(body) > MAX_REQUEST_BYTES:
            raise ValueError("Request exceeds the fixed evaluation bound.")
        input_bound = len(body) * 2
        output_bound = MAX_OUTPUT_TOKENS
        return (
            input_bound * MAX_INPUT_PRICE_PER_MILLION
            + output_bound * OUTPUT_PRICE_PER_MILLION
        ) / 1_000_000

    def generate(self, request: CreativeGenerationRequest) -> CreativeGenerationResult:
        body = self.request_body(request)
        self.last_usage = None
        self.last_cost_usd = None
        self.last_model = None
        connection = HTTPSConnection(OPENAI_HOST, timeout=OPENAI_TIMEOUT_SECONDS)
        try:
            connection.request(
                "POST",
                OPENAI_PATH,
                body=body,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            response_body = response.read(MAX_RESPONSE_BYTES + 1)
            if response.status != 200 or len(response_body) > MAX_RESPONSE_BYTES:
                raise OSError
            payload = load_provider_object(response_body.decode("utf-8"))
            usage = payload["usage"]
            input_tokens = usage["input_tokens"]
            output_tokens = usage["output_tokens"]
            actual_model = payload.get("model")
            if (
                type(input_tokens) is not int
                or type(output_tokens) is not int
                or input_tokens < 0
                or input_tokens > len(body) * 2
                or not 0 <= output_tokens <= MAX_OUTPUT_TOKENS
                or payload.get("status") != "completed"
                or not isinstance(actual_model, str)
                or not (
                    actual_model == OPENAI_MODEL
                    or actual_model.startswith(f"{OPENAI_MODEL}-")
                )
            ):
                raise ValueError
            self.last_model = actual_model
            self.last_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
            self.last_cost_usd = round(
                (
                    input_tokens * MAX_INPUT_PRICE_PER_MILLION
                    + output_tokens * OUTPUT_PRICE_PER_MILLION
                )
                / 1_000_000,
                8,
            )
            text = "".join(
                content["text"]
                for item in payload["output"]
                if item.get("type") == "message"
                for content in item.get("content", ())
                if content.get("type") == "output_text"
            )
            variants = parse_creative_variants(text)
        except (
            KeyError,
            TypeError,
            ValueError,
            AttributeError,
            UnicodeError,
            json.JSONDecodeError,
            HTTPException,
            OSError,
        ):
            raise CreativeGenerationRejected(
                "OpenAI yanıtı alınamadı veya doğrulanamadı."
            ) from None
        finally:
            connection.close()

        result = CreativeGenerationResult(
            generator_id=self.generator_id,
            source_hash=request.source_hash,
            variants=variants,
        )
        return validate_generation_result(request, result)
