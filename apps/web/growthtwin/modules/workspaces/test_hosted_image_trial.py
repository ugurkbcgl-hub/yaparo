"""Owned image persistence, private delivery and one-shot paid boundaries."""

import io
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, local
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
from PIL import Image

from . import hosted_image_trial as service
from .models import HostedImageTrial, HostedTextTrial, Workspace


def sample_png():
    with Image.new("RGB", (64, 96), "#244c3b") as image:
        out = io.BytesIO()
        image.save(out, format="PNG")
        return out.getvalue()


class HostedImageTrialTests(TransactionTestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="image-owner")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Never send this"
        )
        options = override_settings(
            DEBUG=True,
            LOCAL_HOSTED_TEXT_TRIAL_ENABLED=True,
            LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID=self.workspace.pk,
            LOCAL_HOSTED_IMAGE_TRIAL_ENABLED=True,
        )
        options.enable()
        self.addCleanup(options.disable)
        environment = mock.patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-only-key",
                "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "1",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        self.original = sample_png()
        patches = [
            mock.patch.object(
                service,
                "generate_image",
                return_value=(self.original, ".png", 0.033625),
            ),
            mock.patch.object(
                service, "reserve_evaluation_cost", return_value=Path("test-ledger")
            ),
            mock.patch.object(service, "settle_evaluation_cost"),
        ]
        self.generate, self.reserve, self.settle = [p.start() for p in patches]
        for patch in patches:
            self.addCleanup(patch.stop)
        self.client.force_login(self.owner)
        self.url = reverse("brands:hosted_image_trial")
        self.post_url = reverse("brands:hosted_image_generate")
        self.content_url = reverse("brands:hosted_image_content")
        self.download_url = reverse("brands:hosted_image_download")

    def post(self, client=None):
        return (client or self.client).post(
            self.post_url,
            urlencode({"confirm": "fixed-duru-image"}),
            content_type="application/x-www-form-urlencoded",
        )

    def test_saved_pair_precedes_settlement_reads_and_repeat_never_redispatch(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.generate.assert_not_called()
        self.assertFalse(HostedImageTrial.objects.exists())

        def before_settle(*args):
            self.assertFalse(service.connection.in_atomic_block)
            job = HostedImageTrial.objects.get()
            self.assertEqual(job.status, "received")
            self.assertEqual(job.budget_state, "unknown")
            self.assertEqual(bytes(job.original), self.original)
            self.assertTrue(bytes(job.png).startswith(service.PNG_SIGNATURE))

        self.settle.side_effect = before_settle
        self.assertEqual(self.post().status_code, 302)
        job = HostedImageTrial.objects.get()
        self.assertEqual((job.width, job.height), (64, 96))
        self.assertEqual(job.budget_state, "settled")
        self.assertEqual(self.post().status_code, 302)
        for url in (self.url, self.content_url, self.download_url):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("no-store", response["Cache-Control"])
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        image = self.client.get(self.content_url)
        self.assertEqual(image["Content-Type"], "image/png")
        self.assertEqual(image.content, service.checked_image(job))
        self.assertIn(
            "attachment", self.client.get(self.download_url)["Content-Disposition"]
        )
        self.generate.assert_called_once_with(
            "test-only-key", prompt=service.IMAGE_PROMPT
        )
        self.reserve.assert_called_once_with(0.10, per_request_limit_usd=0.10)
        self.assertFalse(HostedTextTrial.objects.exists())

    def test_scopes_flags_fresh_activity_and_foreign_download_refuse(self):
        self.post()
        for options in (
            {"LOCAL_HOSTED_IMAGE_TRIAL_ENABLED": False},
            {"LOCAL_HOSTED_TEXT_TRIAL_ENABLED": False},
            {"DEBUG": False},
            {"LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID": None},
        ):
            with override_settings(**options):
                self.assertEqual(self.client.get(self.content_url).status_code, 404)
                self.assertEqual(self.post().status_code, 404)
        stranger = get_user_model().objects.create_user(username="foreign")
        self.client.force_login(stranger)
        self.assertEqual(self.client.get(self.download_url).status_code, 404)
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            service.read_trial(self.owner)
        self.generate.assert_called_once()

    def test_corrupt_images_and_hashes_are_not_served(self):
        self.post()
        HostedImageTrial.objects.update(png=b"bad")
        self.assertEqual(self.client.get(self.content_url).status_code, 409)
        self.assertEqual(self.client.get(self.url).status_code, 409)
        self.post()
        self.generate.assert_called_once()

    def test_invalid_decode_keeps_known_cost_original_and_no_retry(self):
        self.generate.return_value = (
            service.PNG_SIGNATURE + b"broken",
            ".png",
            0.033625,
        )
        self.post()
        job = HostedImageTrial.objects.get()
        self.assertEqual(job.status, "unverified")
        self.assertIsNotNone(job.actual_usd)
        self.assertTrue(bytes(job.original))
        self.assertFalse(bytes(job.png))
        self.assertEqual(self.client.get(self.content_url).status_code, 409)
        self.post()
        self.generate.assert_called_once()
        self.settle.assert_not_called()

    def test_oversized_response_cost_retained_but_bytes_refused(self):
        self.generate.return_value = (
            b"a" * (service.MAX_SOURCE_BYTES + 1),
            ".png",
            0.03,
        )
        self.post()
        job = HostedImageTrial.objects.get()
        self.assertIsNotNone(job.actual_usd)
        self.assertFalse(bytes(job.original))
        self.settle.assert_not_called()

    def test_provider_timeout_is_private_and_never_retried(self):
        self.generate.side_effect = TimeoutError("secret-provider-detail")
        self.post()
        self.post()
        job = HostedImageTrial.objects.get()
        self.assertEqual(job.budget_state, "held")
        self.assertEqual(job.status, "unverified")
        self.assertNotContains(self.client.get(self.url), "secret-provider-detail")
        self.generate.assert_called_once()

    def test_settlement_lost_ack_stays_unknown_and_blocks_retry(self):
        self.settle.side_effect = OSError("committed but ack lost")
        self.post()
        self.post()
        self.assertEqual(HostedImageTrial.objects.get().budget_state, "unknown")
        self.generate.assert_called_once()

    def test_failure_after_settlement_records_settled(self):
        original = QuerySet.update

        def update(queryset, **kwargs):
            if (
                queryset.model is HostedImageTrial
                and kwargs.get("status") == "completed"
            ):
                raise OSError("private")
            return original(queryset, **kwargs)

        with mock.patch.object(QuerySet, "update", new=update):
            self.post()
        self.assertEqual(HostedImageTrial.objects.get().budget_state, "settled")
        self.post()
        self.generate.assert_called_once()

    def test_ambient_transaction_and_budget_refusal_prevent_dispatch(self):
        with transaction.atomic(), self.assertRaises(PermissionDenied):
            service.generate_trial(self.owner)
        self.assertFalse(HostedImageTrial.objects.exists())
        self.reserve.side_effect = RuntimeError("budget unavailable")
        self.post()
        self.generate.assert_not_called()
        self.assertEqual(HostedImageTrial.objects.get().budget_state, "unknown")

    def test_preparse_csrf_invalid_fields_and_auth_headers(self):
        with mock.patch(
            "django.core.handlers.wsgi.WSGIRequest._load_post_and_files",
            side_effect=AssertionError,
        ):
            for ct, body in (
                ("multipart/form-data; boundary=x", "--x"),
                ("application/json", "{}"),
                ("application/x-www-form-urlencoded", "x=" + "a" * 9000),
            ):
                self.assertEqual(
                    self.client.post(self.post_url, body, content_type=ct).status_code,
                    415,
                )
        for body in (
            "confirm=fixed-duru-image&confirm=fixed-duru-image",
            "confirm=fixed-duru-image&prompt=private",
            "confirm=no",
        ):
            self.assertEqual(
                self.client.post(
                    self.post_url,
                    body,
                    content_type="application/x-www-form-urlencoded",
                ).status_code,
                400,
            )
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = self.post(client)
        self.assertEqual(response.status_code, 403)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(self.post_url).status_code, 405)
        response = Client().get(self.download_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.generate.assert_not_called()

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_clicks_dispatch_once(self):
        barrier = Barrier(2)
        state = local()
        reader = service.read_trial

        def read(owner):
            value = reader(owner)
            if not getattr(state, "started", False):
                state.started = True
                barrier.wait(timeout=8)
            return value

        def call():
            close_old_connections()
            try:
                return service.generate_trial(
                    get_user_model().objects.get(pk=self.owner.pk)
                ).pk
            finally:
                close_old_connections()

        with (
            mock.patch.object(service, "read_trial", side_effect=read),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            futures = [pool.submit(call) for _ in range(2)]
            results = [f.result(timeout=15) for f in futures]
        self.assertEqual(results[0], results[1])
        self.assertEqual(HostedImageTrial.objects.count(), 1)
        self.generate.assert_called_once()
        self.reserve.assert_called_once()
