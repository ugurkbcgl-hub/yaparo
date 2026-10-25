"""Opt-in adapter for local Ollama inference with synthetic campaign briefs."""

import json
import re
from http.client import HTTPConnection, HTTPException

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

OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
OLLAMA_PATH = "/api/chat"
OLLAMA_TIMEOUT_SECONDS = 60
MAX_RESPONSE_BYTES = 65_536


class OllamaCreativeGenerator:
    """Generate local-only candidates; this adapter is not used by web routes."""

    def __init__(self, *, model: str, timeout_seconds: int = OLLAMA_TIMEOUT_SECONDS):
        if (
            not isinstance(model, str)
            or "://" in model
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}", model)
        ):
            raise ValueError("A local Ollama model name is required.")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 120:
            raise ValueError("Timeout must be an integer from 1 to 120 seconds.")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.generator_id = f"ollama-{model}"

    def generate(self, request: CreativeGenerationRequest) -> CreativeGenerationResult:
        if not isinstance(request, CreativeGenerationRequest):
            raise CreativeGenerationRejected("Üretim isteği geçersiz.")
        if request.synthetic_only is not True:
            raise CreativeGenerationRejected(
                "Yalnızca sentetik istekler kullanılabilir."
            )
        if not isinstance(request.brief, CampaignBrief):
            raise CreativeGenerationRejected("Kampanya brief biçimi geçersiz.")

        brief_limits = {
            "text": 2000,
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
                "format": CREATIVE_SCHEMA,
                "stream": False,
                "think": False,
                "options": {"temperature": 0.2, "num_predict": 512},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        connection = HTTPConnection(
            OLLAMA_HOST,
            OLLAMA_PORT,
            timeout=self.timeout_seconds,
        )
        try:
            connection.request(
                "POST",
                OLLAMA_PATH,
                body=body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            if response.status != 200:
                raise OSError
            response_body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(response_body) > MAX_RESPONSE_BYTES:
                raise OSError
            response_payload = load_provider_object(response_body.decode("utf-8"))
            content = response_payload["message"]["content"]
            variants = parse_creative_variants(content)
        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeError,
            json.JSONDecodeError,
            HTTPException,
            OSError,
        ):
            raise CreativeGenerationRejected(
                "Yerel Ollama yanıtı alınamadı veya doğrulanamadı."
            ) from None
        finally:
            connection.close()

        result = CreativeGenerationResult(
            generator_id=self.generator_id,
            source_hash=request.source_hash,
            variants=variants,
        )
        return validate_generation_result(request, result)
