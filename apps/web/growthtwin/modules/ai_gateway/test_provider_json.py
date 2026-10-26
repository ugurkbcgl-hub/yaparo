"""No-network malformed/ambiguous JSON checks shared by all three adapters."""

import json
from copy import deepcopy
from dataclasses import asdict
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .contracts import CreativeGenerationRejected
from .ollama import OllamaCreativeGenerator
from .openai import OPENAI_MODEL, OpenAICreativeGenerator
from .openrouter import OPENROUTER_MODEL, OpenRouterCreativeGenerator
from .provider_json import (
    InvalidProviderJSON,
    load_provider_object,
    parse_creative_variants,
)
from .synthetic import SYNTHETIC_CREATIVE_REQUEST, SyntheticTemplateGenerator


def good():
    return {
        "variants": [
            asdict(row)
            for row in SyntheticTemplateGenerator()
            .generate(SYNTHETIC_CREATIVE_REQUEST)
            .variants
        ]
    }


class StrictJSONTests(SimpleTestCase):
    def test_valid_unicode_variants_and_finite_outer_metadata(self):
        payload = good()
        payload["variants"][0]["headline"] = "İğde, çömlek ve özgün örnek 🟢"
        self.assertEqual(
            parse_creative_variants(json.dumps(payload))[0].headline,
            payload["variants"][0]["headline"],
        )
        self.assertEqual(
            load_provider_object('{"metadata":{"x":0.25,"count":4},"future":true}')[
                "metadata"
            ]["x"],
            0.25,
        )

    def test_duplicate_decoded_keys_nonfinite_and_invalid_root_refuse(self):
        for raw in (
            '{"variants":[],"variants":[]}',
            '{"v":{"x":1,"x":2}}',
            '{"a":1,"\\u0061":2}',
            '{"v":NaN}',
            '{"v":Infinity}',
            '{"v":-Infinity}',
            '{"v":1e9999}',
            "[]",
            "null",
            "true",
            "1",
            "{} {}",
            "{",
            "",
            "[ " * 1100 + "] " * 1100,
            "x" * 65537,
            None,
        ):
            with self.subTest(kind=type(raw).__name__):
                with self.assertRaises(InvalidProviderJSON):
                    load_provider_object(raw)

    def test_exact_root_variant_fields_bounds_and_unicode(self):
        payload = good()
        malformed = [
            payload | {"published": True},
            {},
            {"variants": []},
            {"variants": payload["variants"] * 2},
            {"variants": {}},
            {"variants": [True]},
        ]
        for change in (
            {"headline": 3},
            {"headline": "x" * 81},
            {"body": " "},
            {"approved": True},
            {"headline": "\ud800"},
        ):
            candidate = deepcopy(payload)
            candidate["variants"][0].update(change)
            malformed.append(candidate)
        candidate = deepcopy(payload)
        del candidate["variants"][0]["angle"]
        malformed.append(candidate)
        for value in malformed:
            with self.assertRaises(InvalidProviderJSON):
                parse_creative_variants(json.dumps(value))

    def test_generic_errors_never_echo_provider_field_or_value(self):
        marker = "synthetic-private-marker"
        try:
            load_provider_object('{"' + marker + '":1,"' + marker + '":2}')
        except InvalidProviderJSON as error:
            self.assertNotIn(marker, str(error))
        else:
            self.fail("Duplicate key accepted")


class AdapterJSONTests(SimpleTestCase):
    def adapters(self):
        return (
            (
                "openai",
                OpenAICreativeGenerator(api_key="synthetic-offline-placeholder"),
            ),
            (
                "openrouter",
                OpenRouterCreativeGenerator(api_key="synthetic-offline-placeholder"),
            ),
            ("ollama", OllamaCreativeGenerator(model="qwen3:1.7b")),
        )

    def exercise(self, name, generator, content, *, outer_duplicate=False):
        if name == "openai":
            payload = {
                "status": "completed",
                "model": OPENAI_MODEL,
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": content}],
                    }
                ],
            }
        elif name == "openrouter":
            payload = {
                "model": OPENROUTER_MODEL,
                "choices": [{"finish_reason": "stop", "message": {"content": content}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0},
            }
        else:
            payload = {"message": {"content": content}}
        raw = json.dumps(payload)
        if outer_duplicate:
            raw = raw[:-1] + ',"ambiguous":1,"ambiguous":2}'
        response = Mock(status=200)
        response.read.return_value = raw.encode()
        connection_type = "HTTPConnection" if name == "ollama" else "HTTPSConnection"
        with patch(
            f"growthtwin.modules.ai_gateway.{name}.{connection_type}"
        ) as connection:
            connection.return_value.getresponse.return_value = response
            try:
                return generator.generate(SYNTHETIC_CREATIVE_REQUEST)
            finally:
                connection.return_value.close.assert_called_once()

    def test_all_adapters_keep_valid_candidates_nonpublishable(self):
        for name, generator in self.adapters():
            result = self.exercise(name, generator, json.dumps(good()))
            self.assertTrue(result.review_required)
            self.assertFalse(result.publishable)

    def test_all_adapters_refuse_unknown_root_duplicate_inner_and_ambiguous_outer(self):
        payload = good()
        duplicate = (
            json.dumps(payload)[:-1]
            + ',"variants":'
            + json.dumps(payload["variants"])
            + "}"
        )
        for name, generator in self.adapters():
            for raw, outer in (
                (json.dumps(payload | {"published": True}), False),
                (duplicate, False),
                (json.dumps(payload), True),
                ('{"variants":NaN}', False),
                ("{", False),
            ):
                with self.subTest(adapter=name):
                    with self.assertRaises(CreativeGenerationRejected):
                        self.exercise(name, generator, raw, outer_duplicate=outer)

    def test_existing_domain_duplicate_variant_guard_is_preserved(self):
        payload = good()
        payload["variants"][1]["key"] = payload["variants"][0]["key"]
        for name, generator in self.adapters():
            with self.assertRaises(CreativeGenerationRejected):
                self.exercise(name, generator, json.dumps(payload))
