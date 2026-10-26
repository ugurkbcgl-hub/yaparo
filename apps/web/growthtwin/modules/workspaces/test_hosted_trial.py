"""Paid intent durability, ownership, HTTP and no-retry checks without API calls."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest import mock
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, transaction
from django.db.models.query import QuerySet
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from growthtwin.modules.ai_gateway.brand_sample import REQUEST
from growthtwin.modules.ai_gateway.contracts import CreativeGenerationResult
from growthtwin.modules.ai_gateway.openrouter import OPENROUTER_MODEL
from growthtwin.modules.content.creative import CreativeVariant

from . import hosted_trial as service
from .models import HostedTextTrial, Workspace


def fake_generator():
    generator = mock.Mock()
    generator.request_body.return_value = b"fixed-request"
    generator.maximum_reserved_cost.return_value = 0.001
    generator.last_model = OPENROUTER_MODEL
    generator.last_provider = "Azure"
    generator.last_usage = {"input_tokens": 10, "output_tokens": 20}
    generator.last_cost_usd = 0.0001
    generator.generate.return_value = CreativeGenerationResult(
        generator_id=f"openrouter-{OPENROUTER_MODEL.replace('/', '-')}",
        source_hash=REQUEST.source_hash,
        variants=(
            CreativeVariant(
                "product", "Ürün", "Seramik kupalar", "Koleksiyonu keşfet.", "Keşfet"
            ),
        ),
    )
    return generator


class HostedTrialTests(TransactionTestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="trial-owner")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Private input"
        )
        self.options = override_settings(
            DEBUG=True,
            LOCAL_HOSTED_TEXT_TRIAL_ENABLED=True,
            LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID=self.workspace.pk,
        )
        self.options.enable()
        self.addCleanup(self.options.disable)
        self.environment = mock.patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-only-key",
                "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "1",
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.generator = fake_generator()
        self.factory_patch = mock.patch.object(
            service, "OpenRouterCreativeGenerator", return_value=self.generator
        )
        self.factory = self.factory_patch.start()
        self.addCleanup(self.factory_patch.stop)
        self.reserve_patch = mock.patch.object(
            service, "reserve_evaluation_cost", return_value=Path("test-ledger")
        )
        self.reserve = self.reserve_patch.start()
        self.addCleanup(self.reserve_patch.stop)
        self.settle_patch = mock.patch.object(service, "settle_evaluation_cost")
        self.settle = self.settle_patch.start()
        self.addCleanup(self.settle_patch.stop)
        self.client.force_login(self.owner)
        self.url = reverse("brands:hosted_trial")
        self.post_url = reverse("brands:hosted_trial_generate")

    def post(self, client=None, **extra):
        return (client or self.client).post(
            self.post_url,
            urlencode({"confirm": "fixed-duru-text", **extra}),
            content_type="application/x-www-form-urlencoded",
        )

    def test_get_is_read_only_then_one_post_saves_real_profile_and_refresh_reuses(self):
        response = self.client.get(self.url)
        self.assertContains(response, "AI metinleri üret")
        self.factory.assert_not_called()
        self.assertFalse(HostedTextTrial.objects.exists())

        def check_committed_intent(request):
            self.assertFalse(service.connection.in_atomic_block)
            self.assertEqual(HostedTextTrial.objects.get().budget_state, "held")
            self.assertEqual(request, REQUEST)
            self.assertNotIn(self.workspace.name, request.brief.text)
            return fake_generator().generate.return_value

        self.generator.generate.side_effect = check_committed_intent

        def check_saved_result(*args):
            job = HostedTextTrial.objects.get()
            self.assertEqual(job.status, "received")
            self.assertEqual(job.variants[0]["headline"], "Seramik kupalar")

        self.settle.side_effect = check_saved_result
        self.assertEqual(self.post().status_code, 302)
        self.assertEqual(self.post().status_code, 302)
        response = self.client.get(self.url)
        self.assertContains(response, "Seramik kupalar")
        self.assertContains(response, "Azure")
        self.assertNotContains(response, "AI metinleri üret</button>")
        job = HostedTextTrial.objects.get()
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.budget_state, "settled")
        self.generator.generate.assert_called_once()
        self.reserve.assert_called_once_with(0.001)
        self.settle.assert_called_once()

    def test_flags_scope_and_fresh_owner_activity_refuse_before_call(self):
        for options in (
            {"DEBUG": False},
            {"LOCAL_HOSTED_TEXT_TRIAL_ENABLED": False},
            {"LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID": None},
        ):
            with override_settings(**options):
                self.assertEqual(self.client.get(self.url).status_code, 404)
                self.assertEqual(self.post().status_code, 404)
        stranger = get_user_model().objects.create_user(username="other")
        self.client.force_login(stranger)
        self.assertEqual(self.post().status_code, 404)
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            service.admitted_workspace(self.owner)
        self.factory.assert_not_called()
        self.reserve.assert_not_called()

    def test_ambient_transaction_refuses_before_paid_intent(self):
        with transaction.atomic(), self.assertRaises(PermissionDenied):
            service.generate_trial(self.owner)
        self.assertFalse(HostedTextTrial.objects.exists())
        self.factory.assert_not_called()

    def test_provider_failure_blocks_repeat_without_leaking_exception(self):
        self.generator.generate.side_effect = TimeoutError("secret-response")
        self.assertEqual(self.post().status_code, 302)
        self.assertEqual(self.post().status_code, 302)
        response = self.client.get(self.url)
        self.assertContains(response, "Sonuç henüz doğrulanmadı")
        self.assertNotContains(response, "secret-response")
        self.assertEqual(HostedTextTrial.objects.get().budget_state, "held")
        self.generator.generate.assert_called_once()
        self.settle.assert_not_called()

    def test_settlement_failure_preserves_received_output_and_unknown_state(self):
        self.settle.side_effect = RuntimeError("private-ledger-detail")
        self.post()
        job = HostedTextTrial.objects.get()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(job.budget_state, "unknown")
        self.assertTrue(job.variants)
        self.assertNotContains(self.client.get(self.url), "Seramik kupalar")
        self.post()
        self.generator.generate.assert_called_once()

    def test_settlement_commit_with_lost_acknowledgment_remains_unknown(self):
        committed = []

        def commit_then_raise(*args):
            committed.append(True)
            raise OSError("Acknowledgment lost after commit")

        self.settle.side_effect = commit_then_raise
        self.post()
        self.assertEqual(committed, [True])
        job = HostedTextTrial.objects.get()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(job.budget_state, "unknown")
        self.post()
        self.generator.generate.assert_called_once()

    def test_failure_after_settlement_records_settled_without_retry(self):
        original = QuerySet.update

        def update(queryset, **kwargs):
            if (
                queryset.model is HostedTextTrial
                and kwargs.get("status") == "completed"
            ):
                raise RuntimeError("private-storage-detail")
            return original(queryset, **kwargs)

        with mock.patch.object(QuerySet, "update", new=update):
            self.post()
        job = HostedTextTrial.objects.get()
        self.assertEqual(job.status, "unverified")
        self.assertEqual(job.budget_state, "settled")
        self.post()
        self.generator.generate.assert_called_once()

    def test_budget_refusal_and_missing_gate_make_no_provider_call(self):
        with mock.patch.dict(
            os.environ, {"GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "0"}
        ):
            self.assertEqual(self.post().status_code, 404)
        self.assertFalse(HostedTextTrial.objects.exists())
        self.reserve.side_effect = RuntimeError("budget unavailable")
        self.post()
        self.generator.generate.assert_not_called()
        self.assertEqual(HostedTextTrial.objects.get().budget_state, "unknown")

    def test_duplicate_unknown_or_unconfirmed_fields_refuse(self):
        for body in (
            "confirm=fixed-duru-text&confirm=fixed-duru-text",
            "confirm=fixed-duru-text&text=private",
            "confirm=no",
        ):
            response = self.client.post(
                self.post_url, body, content_type="application/x-www-form-urlencoded"
            )
            self.assertEqual(response.status_code, 400)
        self.factory.assert_not_called()

    def test_preparse_refusal_private_errors_methods_and_csrf(self):
        with mock.patch(
            "django.core.handlers.wsgi.WSGIRequest._load_post_and_files",
            side_effect=AssertionError("Must not parse"),
        ):
            for content_type, body in (
                ("multipart/form-data; boundary=x", "--x\r\n"),
                ("application/json", "{}"),
                ("application/x-www-form-urlencoded", "x=" + "a" * 9000),
            ):
                response = self.client.post(
                    self.post_url, body, content_type=content_type
                )
                self.assertEqual(response.status_code, 415)
                self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(self.post_url).status_code, 405)
        self.assertEqual(
            self.client.post(
                self.url, "x=y", content_type="application/x-www-form-urlencoded"
            ).status_code,
            405,
        )
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = self.post(client)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        response = Client().get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("no-store", response["Cache-Control"])
        self.generator.generate.assert_not_called()

    def test_invalid_provider_identity_is_not_persisted_or_settled(self):
        self.generator.last_provider = {"private": "detail"}
        self.post()
        self.assertEqual(HostedTextTrial.objects.get().provider, "")
        self.settle.assert_not_called()

    def test_stored_result_corruption_refuses_without_generation(self):
        self.post()
        HostedTextTrial.objects.update(variants=[{"bad": "shape"}])
        self.assertEqual(self.client.get(self.url).status_code, 409)
        self.generator.generate.assert_called_once()

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_clicks_commit_one_intent_and_dispatch_once(self):
        barrier = Barrier(2)
        self.generator.request_body.side_effect = lambda request: (
            barrier.wait(timeout=8),
            b"fixed-request",
        )[1]

        def call():
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                return service.generate_trial(owner).pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call) for _ in range(2)]
            results = [future.result(timeout=15) for future in futures]
        self.assertEqual(results[0], results[1])
        self.assertEqual(HostedTextTrial.objects.count(), 1)
        self.generator.generate.assert_called_once()
        self.reserve.assert_called_once()
