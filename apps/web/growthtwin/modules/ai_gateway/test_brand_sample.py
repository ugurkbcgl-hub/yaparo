"""No-network checks for the explicitly invoked real-provider sample runner."""

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from growthtwin.modules.content.creative import CreativeVariant
from scripts import evaluate_openrouter_image_synthetic as image_runner
from scripts import generate_openrouter_brand_sample as sample


class BrandSampleTests(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.env = mock.patch.dict(
            "os.environ",
            {"LOCALAPPDATA": str(self.root), "OPENROUTER_API_KEY": "test-only-key"},
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def records(self):
        paths = list(self.root.rglob("brand-*.jsonl"))
        self.assertEqual(len(paths), 1)
        return [
            json.loads(line)
            for line in paths[0].read_text(encoding="utf-8").splitlines()
        ]

    def test_image_request_pins_privacy_provider_and_fixed_brand(self):
        payload = json.loads(image_runner._request_body(sample.IMAGE_PROMPT))
        self.assertEqual(payload["provider"]["only"], [image_runner.PROVIDER])
        self.assertFalse(payload["provider"]["allow_fallbacks"])
        self.assertTrue(payload["provider"]["zdr"])
        self.assertEqual(payload["provider"]["data_collection"], "deny")
        self.assertEqual(payload["n"], 1)
        self.assertIn("Duru Studio", payload["prompt"])

    @mock.patch.object(sample, "reserve_evaluation_cost")
    @mock.patch.object(image_runner, "_generate")
    def test_repository_output_is_refused_before_directory_creation_or_spend(
        self, generate, reserve
    ):
        repository = Path(sample.__file__).resolve().parents[3]
        forbidden = repository / ".brand-evaluation-refusal-test"
        self.assertFalse(forbidden.exists())
        with mock.patch.dict("os.environ", {"LOCALAPPDATA": str(forbidden)}):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(sample.run("image"), 2)
            with self.assertRaises(OSError):
                image_runner._local_directory()
        self.assertFalse(forbidden.exists())
        generate.assert_not_called()
        reserve.assert_not_called()

    @mock.patch.object(sample, "settle_evaluation_cost")
    @mock.patch.object(sample, "reserve_evaluation_cost", return_value=Path("ledger"))
    @mock.patch.object(image_runner, "_generate")
    def test_image_written_and_captured_before_settlement(
        self, generate, reserve, settle
    ):
        image = image_runner.PNG_SIGNATURE + b"mock-test-bytes"
        generate.return_value = image, ".png", 0.0336

        def check_before_settlement(*args):
            records = self.records()
            self.assertEqual(
                [row["record_type"] for row in records], ["started", "result"]
            )
            self.assertEqual(Path(records[1]["local_image_path"]).read_bytes(), image)

        settle.side_effect = check_before_settlement
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sample.run("image"), 0)
        generate.assert_called_once_with("test-only-key", prompt=sample.IMAGE_PROMPT)
        reserve.assert_called_once_with(0.10, per_request_limit_usd=0.10)
        settle.assert_called_once_with(Path("ledger"), 0.10, 0.0336)
        records = self.records()
        self.assertEqual(records[-1]["record_type"], "settled")
        self.assertFalse(records[1]["publishable"])
        self.assertNotIn("test-only-key", json.dumps(records))

    @mock.patch.object(sample, "settle_evaluation_cost")
    @mock.patch.object(sample, "reserve_evaluation_cost", return_value=Path("ledger"))
    @mock.patch.object(
        image_runner, "_generate", side_effect=TimeoutError("secret-body")
    )
    def test_failed_call_has_no_retry_no_settlement_and_no_exception_leak(
        self, generate, reserve, settle
    ):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(sample.run("image"), 2)
        generate.assert_called_once()
        settle.assert_not_called()
        self.assertEqual([row["record_type"] for row in self.records()], ["started"])
        self.assertNotIn("secret-body", output.getvalue())

    @mock.patch.object(sample, "settle_evaluation_cost")
    @mock.patch.object(sample, "reserve_evaluation_cost", side_effect=RuntimeError)
    @mock.patch.object(image_runner, "_generate")
    def test_budget_refusal_prevents_network(self, generate, reserve, settle):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sample.run("image"), 2)
        generate.assert_not_called()
        settle.assert_not_called()

    @mock.patch.object(sample, "settle_evaluation_cost")
    @mock.patch.object(sample, "reserve_evaluation_cost", return_value=Path("ledger"))
    @mock.patch.object(sample, "OpenRouterCreativeGenerator")
    def test_text_with_unverified_accounting_keeps_reservation(
        self, factory, reserve, settle
    ):
        generator = factory.return_value
        generator.model = "test-model"
        generator.maximum_reserved_cost.return_value = 0.001
        generator.last_usage = None
        generator.last_cost_usd = None
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sample.run("text"), 2)
        generator.generate.assert_called_once_with(sample.REQUEST)
        settle.assert_not_called()

    @mock.patch.object(sample, "reserve_evaluation_cost")
    @mock.patch.object(sample, "OpenRouterCreativeGenerator")
    def test_text_above_ceiling_is_refused_before_reservation(self, factory, reserve):
        factory.return_value.maximum_reserved_cost.return_value = 0.02
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sample.run("text"), 2)
        reserve.assert_not_called()
        factory.return_value.generate.assert_not_called()

    @mock.patch.object(sample, "settle_evaluation_cost")
    @mock.patch.object(sample, "reserve_evaluation_cost", return_value=Path("ledger"))
    @mock.patch.object(sample, "OpenRouterCreativeGenerator")
    def test_text_success_records_provenance_content_and_cost(
        self, factory, reserve, settle
    ):
        generator = factory.return_value
        generator.model = generator.last_model = "test-model"
        generator.last_provider = "test-provider"
        generator.last_usage = {"prompt_tokens": 10, "completion_tokens": 20}
        generator.last_cost_usd = 0.0001
        generator.maximum_reserved_cost.return_value = 0.001
        generator.generate.return_value = SimpleNamespace(
            source_hash=sample.REQUEST.source_hash,
            variants=(
                CreativeVariant("one", "Product", "Mugs", "Ceramic mugs", "Explore"),
            ),
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(sample.run("text"), 0)
        reserve.assert_called_once_with(0.001, per_request_limit_usd=0.01)
        settle.assert_called_once_with(Path("ledger"), 0.001, 0.0001)
        records = self.records()
        self.assertEqual(records[1]["variants"][0]["headline"], "Mugs")
        self.assertEqual(records[1]["upstream_provider"], "test-provider")
        self.assertEqual(records[-1]["record_type"], "settled")

    @mock.patch.object(sample, "settle_evaluation_cost")
    @mock.patch.object(sample, "reserve_evaluation_cost", return_value=Path("ledger"))
    @mock.patch.object(
        image_runner, "_generate", return_value=(b"test-bytes", ".jpg", 0.03)
    )
    def test_final_capture_failure_reports_already_settled(
        self, generate, reserve, settle
    ):
        original = sample.append

        def fail_final_capture(path, record):
            if record["record_type"] == "settled":
                raise OSError("private-details")
            original(path, record)

        output = io.StringIO()
        with mock.patch.object(sample, "append", side_effect=fail_final_capture):
            with redirect_stdout(output):
                self.assertEqual(sample.run("image"), 2)
        self.assertEqual(json.loads(output.getvalue())["reservation_state"], "settled")
        self.assertNotIn("private-details", output.getvalue())
        settle.assert_called_once()
