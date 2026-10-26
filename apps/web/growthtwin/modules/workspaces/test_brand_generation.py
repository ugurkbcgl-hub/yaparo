"""Mocked generation, one-shot intents/accounting and owned source readback."""

import io
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, transaction
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse
from PIL import Image

from growthtwin.modules.ai_gateway.contracts import CreativeGenerationResult
from growthtwin.modules.ai_gateway.openrouter import OPENROUTER_MODEL
from growthtwin.modules.ai_gateway.synthetic import SyntheticTemplateGenerator

from . import brand_generation as service
from .models import BrandGenerationAttempt
from .test_production_briefs import ProductionBriefFixture


class GenerationFixture(ProductionBriefFixture):
    def setUp(self):
        super().setUp()
        self.plan = self.make()
        gate = override_settings(
            LOCAL_BRAND_AI_ENABLED=True,
            LOCAL_BRAND_AI_APPROVED_REQUESTS={str(self.plan.pk): self.plan.fingerprint},
        )
        gate.enable()
        self.addCleanup(gate.disable)
        env = mock.patch.dict(
            os.environ,
            {
                "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "1",
                "OPENROUTER_API_KEY": "synthetic-test-only",
            },
        )
        env.start()
        self.addCleanup(env.stop)
        request = service.text_request(self.plan)
        variants = SyntheticTemplateGenerator().generate(request).variants
        self.generator = mock.Mock(
            last_model=OPENROUTER_MODEL,
            last_provider="test-route",
            last_usage={"input_tokens": 100, "output_tokens": 100},
            last_cost_usd=0.0001,
        )
        self.generator.request_body.return_value = b"{}"
        self.generator.maximum_reserved_cost.return_value = 0.001
        self.generator.generate.return_value = CreativeGenerationResult(
            generator_id=f"openrouter-{OPENROUTER_MODEL.replace('/', '-')}",
            source_hash=request.source_hash,
            variants=variants,
        )
        self.factory = mock.patch.object(
            service, "BrandCopyGenerator", return_value=self.generator
        )
        self.factory.start()
        self.addCleanup(self.factory.stop)
        self.reserve = mock.patch.object(
            service, "reserve_evaluation_cost", return_value=Path("mock-ledger")
        )
        self.reservation = self.reserve.start()
        self.addCleanup(self.reserve.stop)
        self.settle = mock.patch.object(service, "settle_evaluation_cost")
        self.settlement = self.settle.start()
        self.addCleanup(self.settle.stop)

    def run_job(self, plan=None):
        plan = plan or self.plan
        return service.generate(self.owner, self.brand.pk, plan.pk)


class BrandGenerationTests(GenerationFixture, TransactionTestCase):
    def test_generate_http_method_csrf_intake_and_fingerprint_guards(self):
        url = reverse("brands:production_generate", args=[self.brand.pk, self.plan.pk])
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(url).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        self.assertEqual(
            csrf_client.post(
                url,
                "fingerprint=missing",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(url, {"fingerprint": "wrong"}).status_code, 415
        )
        self.assertEqual(
            self.client.post(
                url,
                "fingerprint=wrong&csrfmiddlewaretoken=synthetic",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            409,
        )
        self.generator.generate.assert_not_called()
        self.reservation.assert_not_called()

    def test_brand_adapter_headroom_keeps_base_trial_and_reservation_bound(self):
        # Stop the fixture factory patch so this tests the real request adapter.
        self.factory.stop()
        generator = service.BrandCopyGenerator()
        body = generator.request_body(service.text_request(self.plan))
        self.assertEqual(json.loads(body)["max_tokens"], 1024)
        self.assertLess(generator.maximum_reserved_cost(body), 0.01)
        self.assertEqual(service.OpenRouterCreativeGenerator().max_output_tokens, 512)

    def test_lost_transition_stops_before_budget_and_corrupt_cap_denies_read(self):
        with mock.patch.object(service, "_transition", side_effect=ValueError):
            job = self.run_job()
        self.assertEqual(job.status, "unverified")
        self.reservation.assert_not_called()
        self.generator.generate.assert_not_called()
        BrandGenerationAttempt.objects.filter(pk=job.pk).update(reserved_usd="1")
        with self.assertRaises(ValueError):
            service.read(self.owner, self.brand.pk, self.plan.pk)

    def test_text_result_binding_capture_and_replay_once(self):
        job = self.run_job()
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.budget_state, "settled")
        self.assertEqual(job.fingerprint, self.plan.fingerprint)
        self.assertEqual(
            job.output["variants"][0]["headline"],
            self.generator.generate.return_value.variants[0].headline,
        )
        self.assertEqual(self.run_job().pk, job.pk)
        self.generator.generate.assert_called_once()
        self.reservation.assert_called_once()
        self.settlement.assert_called_once()
        self.assertFalse(self.plan.envelope["execution"]["authorized"])

    def test_missing_approval_outer_transaction_and_budget_refuse_before_call(self):
        with override_settings(LOCAL_BRAND_AI_APPROVED_REQUESTS={}):
            with self.assertRaises(PermissionDenied):
                self.run_job()
        with transaction.atomic():
            with self.assertRaises(PermissionDenied):
                self.run_job()
        self.reservation.side_effect = RuntimeError("Synthetic budget failure")
        job = self.run_job()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(self.run_job().pk, job.pk)
        self.generator.generate.assert_not_called()

    def test_timeout_keeps_single_intent_and_no_retry(self):
        self.generator.generate.side_effect = TimeoutError
        job = self.run_job()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(job.budget_state, "held")
        self.assertEqual(
            job.output["failure"], {"stage": "provider", "category": "TimeoutError"}
        )
        self.run_job()
        self.generator.generate.assert_called_once()
        self.settlement.assert_not_called()

    def test_settlement_failure_retains_received_result_and_unknown_accounting(self):
        self.settlement.side_effect = RuntimeError
        job = self.run_job()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(job.budget_state, "unknown")
        self.assertTrue(job.output["variants"])
        self.assertEqual(float(job.actual_usd), 0.0001)
        self.run_job()
        self.generator.generate.assert_called_once()

    def test_revocation_after_output_settles_but_does_not_complete(self):
        output = self.generator.generate.return_value

        def revoke(*args):
            settings.LOCAL_BRAND_AI_APPROVED_REQUESTS = {}
            return output

        self.generator.generate.side_effect = revoke
        with self.assertRaises(PermissionDenied):
            self.run_job()
        job = BrandGenerationAttempt.objects.get()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(job.budget_state, "settled")
        self.assertTrue(job.output)
        self.settlement.assert_called_once()

    def test_image_bytes_hash_source_and_private_http_read(self):
        plan = self.make(
            expected_version=1, brief={**self.brief, "deliverable": "image"}
        )
        settings.LOCAL_BRAND_AI_APPROVED_REQUESTS = {str(plan.pk): plan.fingerprint}
        stream = io.BytesIO()
        Image.new("RGB", (768, 1376), "#244c3b").save(stream, format="PNG")
        with mock.patch.object(
            service,
            "generate_image",
            return_value=(stream.getvalue(), ".png", 0.03),
        ) as image:
            job = self.run_job(plan)
            self.assertEqual(job.status, "completed")
            self.assertEqual(job.output["width"], 768)
            self.assertFalse(job.output["reference_pixels_supplied"])
            self.run_job(plan)
            image.assert_called_once()
        self.client.force_login(self.owner)
        url = reverse("brands:production_image", args=[self.brand.pk, plan.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, bytes(job.png))
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        BrandGenerationAttempt.objects.filter(pk=job.pk).update(png=b"bad")
        self.assertEqual(self.client.get(url).status_code, 409)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_image_jpeg_extension_contract_and_mismatch_blocks_settlement(self):
        plan = self.make(
            expected_version=1, brief={**self.brief, "deliverable": "image"}
        )
        settings.LOCAL_BRAND_AI_APPROVED_REQUESTS = {str(plan.pk): plan.fingerprint}
        stream = io.BytesIO()
        Image.new("RGB", (768, 1376), "#254d9b").save(stream, format="JPEG")
        with mock.patch.object(
            service, "generate_image", return_value=(stream.getvalue(), ".jpg", 0.03)
        ):
            job = self.run_job(plan)
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.output["media_type"], "image/jpeg")
        other = self.make(
            expected_version=2, brief={**self.brief, "deliverable": "image"}
        )
        settings.LOCAL_BRAND_AI_APPROVED_REQUESTS[str(other.pk)] = other.fingerprint
        self.settlement.reset_mock()
        with mock.patch.object(
            service, "generate_image", return_value=(stream.getvalue(), ".png", 0.03)
        ):
            failed = self.run_job(other)
        self.assertEqual(failed.status, "unverified")
        self.assertEqual(failed.budget_state, "held")
        self.settlement.assert_not_called()

    def test_invalid_usage_or_cost_never_looks_completed(self):
        self.generator.last_usage = {"input_tokens": 100, "output_tokens": 999999}
        job = self.run_job()
        self.assertEqual(job.status, "unverified")
        self.settlement.assert_not_called()
        self.assertEqual(
            service.read(self.owner, self.brand.pk, self.plan.pk).status, "unverified"
        )

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_clicks_share_attempt_and_one_call(self):
        def run():
            close_old_connections()
            try:
                return self.run_job().pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            values = [
                f.result(timeout=20) for f in [pool.submit(run), pool.submit(run)]
            ]
        self.assertEqual(values[0], values[1])
        self.generator.generate.assert_called_once()
        self.assertEqual(BrandGenerationAttempt.objects.count(), 1)
