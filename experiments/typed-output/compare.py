"""No-network parsing comparison, not inference/quality or cost evaluation."""

import asyncio
import json
import os
import socket
import sys
from copy import deepcopy
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from typing import Annotated
from unittest.mock import Mock, patch

os.environ["PYDANTIC_AI_NO_BANNER"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "web"))

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationResult,
    validate_generation_result,
)
from growthtwin.modules.ai_gateway.openrouter import (
    OPENROUTER_MODEL,
    OpenRouterCreativeGenerator,
)
from growthtwin.modules.ai_gateway.synthetic import (
    SyntheticTemplateGenerator,
)
from growthtwin.modules.content.creative import CreativeVariant
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_ai import Agent, models
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from scripts.evaluate_local_ollama import CASES

models.ALLOW_MODEL_REQUESTS = False


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Variant(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    key: Annotated[
        str, Field(min_length=1, max_length=80, pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    ]
    angle: Annotated[str, Field(min_length=1, max_length=80)]
    headline: Annotated[str, Field(min_length=1, max_length=80)]
    body: Annotated[str, Field(min_length=1, max_length=240)]
    call_to_action: Annotated[str, Field(min_length=1, max_length=40)]


class Output(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    variants: Annotated[list[Variant], Field(min_length=1, max_length=5)]


def direct(request, raw):
    """Exercise the EXISTING adapter with a mocked response, never a real key."""
    envelope = {
        "model": OPENROUTER_MODEL,
        "provider": "offline-fixture",
        "choices": [{"finish_reason": "stop", "message": {"content": raw}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0},
    }
    response = Mock(status=200)
    response.read.return_value = json.dumps(envelope).encode()
    with patch(
        "growthtwin.modules.ai_gateway.openrouter.HTTPSConnection"
    ) as connection:
        connection.return_value.getresponse.return_value = response
        result = OpenRouterCreativeGenerator(
            api_key="synthetic-offline-placeholder"
        ).generate(request)
        require(
            connection.return_value.request.call_count == 1,
            "Expected exactly one mocked adapter call",
        )
        return result


def typed(request, raw):
    calls = 0

    def response(messages, info):
        nonlocal calls
        calls += 1
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, raw)])

    agent = Agent(FunctionModel(response), output_type=Output, retries=0)
    agent.instrument = False
    try:
        output = agent.run_sync("Fixed synthetic parsing fixture; no inference.").output
        result = CreativeGenerationResult(
            generator_id="typed-offline-v1",
            source_hash=request.source_hash,
            variants=tuple(
                CreativeVariant(**row.model_dump()) for row in output.variants
            ),
        )
        return validate_generation_result(request, result)
    finally:
        require(calls == 1, "No retry/fan-out allowed in this comparison")


def fixtures(request):
    good = {
        "variants": [
            asdict(row)
            for row in SyntheticTemplateGenerator().generate(request).variants
        ]
    }
    yield "valid", json.dumps(good), True, True
    yield "invalid-json", "{", False, False
    yield "missing-variants", "{}", False, False
    yield "non-object-root", "[]", False, False
    raw = json.dumps(good)
    yield (
        "duplicate-root-key",
        raw[:-1] + ',"variants":' + json.dumps(good["variants"]) + "}",
        False,
        True,
    )
    yield (
        "duplicate-variant-key",
        raw.replace('"headline":', '"headline":"ignored","headline":', 1),
        False,
        True,
    )
    yield "unknown-root-field", json.dumps(good | {"published": True}), False, False
    for name, mutate in (
        ("unknown-variant-field", lambda p: p["variants"][0].update(approved=True)),
        ("wrong-field-type", lambda p: p["variants"][0].update(headline=3)),
        ("long-headline", lambda p: p["variants"][0].update(headline="x" * 81)),
        ("blank-angle", lambda p: p["variants"][0].update(angle=" ")),
        (
            "duplicate-key",
            lambda p: p["variants"][1].update(key=p["variants"][0]["key"]),
        ),
        (
            "duplicate-angle",
            lambda p: p["variants"][1].update(angle=p["variants"][0]["angle"]),
        ),
        ("empty-list", lambda p: p.update(variants=[])),
        ("too-many", lambda p: p.update(variants=p["variants"] * 2)),
    ):
        candidate = deepcopy(good)
        mutate(candidate)
        yield name, json.dumps(candidate), False, False
    unsupported = deepcopy(good)
    unsupported["variants"][0]["body"] = "Her reklam kesin kazandırır."
    yield "unsupported-claim-shaped", json.dumps(unsupported), True, True


def _compare(loop):
    require(version("pydantic-ai-slim") == "2.61.0", "Unexpected candidate version")
    rows = []
    denied_network = []

    def no_network(*args, **kwargs):
        denied_network.append(True)
        raise AssertionError("Network access forbidden during offline evaluation")

    # No DNS/socket connection, no model endpoint, no external telemetry. Install
    # and vulnerability lookup are separate operations, never part of this run.
    with (
        patch.object(socket, "create_connection", no_network),
        patch.object(socket.socket, "connect", no_network),
        patch.object(socket.socket, "connect_ex", no_network),
        patch.object(socket.socket, "sendto", no_network),
        patch.object(loop, "create_connection", no_network),
        patch.object(loop, "sock_connect", no_network),
        patch.object(loop, "create_datagram_endpoint", no_network),
        patch.object(socket, "getaddrinfo", no_network),
    ):
        for case in CASES:
            for name, raw, expected_direct, expected_typed in fixtures(case.request):
                for method, expected in (
                    (direct, expected_direct),
                    (typed, expected_typed),
                ):
                    elapsed = []
                    observations = []
                    for _ in range(3):
                        start = perf_counter()
                        try:
                            result = method(case.request, raw)
                            require(
                                result.review_required and not result.publishable,
                                "Unexpected publishing permission",
                            )
                            accepted = True
                        except (
                            CreativeGenerationRejected,
                            ValidationError,
                            UnexpectedModelBehavior,
                        ):
                            accepted = False
                        elapsed.append(perf_counter() - start)
                        observations.append(accepted)
                        require(
                            accepted is expected,
                            (
                                f"Unexpected result: {case.case_id}/{name}/{method.__name__}"
                            ),
                        )
                    rows.append(
                        {
                            "brief": case.case_id,
                            "case": name,
                            "method": method.__name__,
                            "accepted": accepted,
                            "expected": expected,
                            "observations": observations,
                            "repetitions": 3,
                            "mean_ms": round(sum(elapsed) / 3 * 1000, 3),
                        }
                    )
    require(not denied_network, "A network attempt occurred")
    return {
        "kind": "offline parsing only",
        "pydantic_ai_slim": version("pydantic-ai-slim"),
        "pydantic": version("pydantic"),
        "briefs": len(CASES),
        "cases_per_brief": len(list(fixtures(CASES[0].request))),
        "latency_comparison_valid": False,
        "total_runs": len(rows) * 3,
        "external_requests": 0,
        "provider_cost_usd": 0,
        "model_quality_measured": False,
        "rows": rows,
    }


def compare():
    # Windows asyncio needs an internal socketpair at loop creation. Initialize
    # only that runtime before forbidding every connection during the comparison.
    with asyncio.Runner() as runtime:
        runtime.get_loop()
        return _compare(runtime.get_loop())


if __name__ == "__main__":
    print(json.dumps(compare(), ensure_ascii=False, indent=2))
