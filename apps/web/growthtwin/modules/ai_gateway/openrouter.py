"""Opt-in, synthetic-only OpenRouter adapter for bounded evaluation."""

import json
import os
from http.client import HTTPException, HTTPSConnection

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
    CreativeGenerationResult,
    ProviderResponseUnverified,
    validate_generation_result,
)
from growthtwin.modules.ai_gateway.creative_format import (
    CREATIVE_SCHEMA,
    CREATIVE_SYSTEM_PROMPT,
)
from growthtwin.modules.content.planning import CampaignBrief

from .provider_json import load_provider_object, parse_creative_variants

OPENROUTER_HOST = "openrouter.ai"
OPENROUTER_PATH = "/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-6-luna"
GEMINI_EVALUATION_MODEL = "google/gemini-3.8-flash"
OPENROUTER_TIMEOUT_SECONDS = 30
MAX_RESPONSE_BYTES = 65_536
MAX_OUTPUT_TOKENS = 512
GEMINI_MAX_OUTPUT_TOKENS = 1_536
MAX_REQUEST_BYTES = 4_096
OUTPUT_PRICE_PER_MILLION = 0.50
MAX_INPUT_PRICE_PER_MILLION = 0.125
MODEL_PRICE_CAPS = {
    OPENROUTER_MODEL: (MAX_INPUT_PRICE_PER_MILLION, OUTPUT_PRICE_PER_MILLION),
    # Standard catalog prices (without temporary discounts) bound this trial.
    GEMINI_EVALUATION_MODEL: (0.75, 3.75),
}
MODEL_OUTPUT_TOKEN_CAPS = {
    OPENROUTER_MODEL: MAX_OUTPUT_TOKENS,
    GEMINI_EVALUATION_MODEL: GEMINI_MAX_OUTPUT_TOKENS,
}


class OpenRouterCreativeGenerator:
    """Single-request hosted adapter with no retries or product-route use."""

    def __init__(self, *, api_key: str | None = None, model: str = OPENROUTER_MODEL):
        if model not in MODEL_PRICE_CAPS:
            raise ValueError(
                "The requested OpenRouter evaluation model is not allowed."
            )
        key = api_key if api_key is not None else os.environ.get("OPENROUTER_API_KEY")
        if (
            not isinstance(key, str)
            or not key.strip()
            or len(key) > 512
            or "\r" in key
            or "\n" in key
        ):
            raise ValueError("Set OPENROUTER_API_KEY in a secure local environment.")
        self._api_key = key
        self.model = model
        self.max_output_tokens = MODEL_OUTPUT_TOKEN_CAPS[model]
        self.max_input_price_per_million, self.output_price_per_million = (
            MODEL_PRICE_CAPS[model]
        )
        self.generator_id = f"openrouter-{model.replace('/', '-')}"
        self.last_usage: dict[str, int] | None = None
        self.last_cost_usd: float | None = None
        self.last_model: str | None = None
        self.last_provider: str | None = None

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
                "model": self.model,
                "messages": [
                    {"role": "system", "content": CREATIVE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(brief_payload, ensure_ascii=False),
                    },
                ],
                "max_tokens": self.max_output_tokens,
                "stream": False,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "creative_variants",
                        "strict": True,
                        "schema": CREATIVE_SCHEMA,
                    },
                },
                "provider": {
                    "data_collection": "deny",
                    "zdr": True,
                    "require_parameters": True,
                    "max_price": {
                        "prompt": self.max_input_price_per_million,
                        "completion": self.output_price_per_million,
                    },
                },
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(body) > MAX_REQUEST_BYTES:
            raise CreativeGenerationRejected("Sentetik istek boyut sınırını aşıyor.")
        return body

    def maximum_reserved_cost(self, body: bytes) -> float:
        """Reserve the bounded upper cost before dispatching a request."""

        if not isinstance(body, bytes) or len(body) > MAX_REQUEST_BYTES:
            raise ValueError("Request exceeds the fixed evaluation bound.")
        input_bound = len(body) * 2
        output_bound = self.max_output_tokens
        return (
            input_bound * self.max_input_price_per_million
            + output_bound * self.output_price_per_million
        ) / 1_000_000

    def generate(self, request: CreativeGenerationRequest) -> CreativeGenerationResult:
        body = self.request_body(request)
        self.last_usage = None
        self.last_cost_usd = None
        self.last_model = None
        self.last_provider = None
        connection = HTTPSConnection(
            OPENROUTER_HOST, timeout=OPENROUTER_TIMEOUT_SECONDS
        )
        try:
            connection.request(
                "POST",
                OPENROUTER_PATH,
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
            input_tokens = usage["prompt_tokens"]
            output_tokens = usage["completion_tokens"]
            actual_model = payload.get("model")
            actual_cost = usage["cost"]
            finish_reason = payload["choices"][0]["finish_reason"]
            if (
                type(input_tokens) is not int
                or type(output_tokens) is not int
                or input_tokens < 0
                or input_tokens > len(body) * 2
                or not 0 <= output_tokens <= self.max_output_tokens
                or type(actual_cost) not in (int, float)
                or not 0 <= actual_cost <= self.maximum_reserved_cost(body)
                or finish_reason != "stop"
                or not isinstance(actual_model, str)
                or not (
                    actual_model == self.model
                    or actual_model.startswith(f"{self.model}:")
                )
            ):
                raise ValueError
            self.last_model = actual_model
            self.last_provider = payload.get("provider")
            self.last_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
            self.last_cost_usd = round(float(actual_cost), 8)
            variants = parse_creative_variants(
                payload["choices"][0]["message"]["content"]
            )
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
            raise ProviderResponseUnverified(
                "OpenRouter yanıtı alınamadı veya doğrulanamadı."
            ) from None
        finally:
            connection.close()

        result = CreativeGenerationResult(
            generator_id=self.generator_id,
            source_hash=request.source_hash,
            variants=variants,
        )
        return validate_generation_result(request, result)
