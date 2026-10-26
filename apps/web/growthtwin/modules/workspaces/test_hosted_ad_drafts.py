"""Saved AI composition boundaries, history, ownership and zero billing."""

import io
import os
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from threading import Barrier
from unittest import mock
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse
from PIL import Image, ImageDraw

from growthtwin.modules.ai_gateway.brand_sample import REQUEST
from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.ai_gateway.openrouter import OPENROUTER_MODEL
from growthtwin.modules.assets.raster_validation import normalize_raster

from . import hosted_ad_drafts as service
from . import hosted_image_trial, hosted_trial
from .models import (
    BrandCreativeDocument,
    HostedAdDraft,
    HostedAdRevision,
    HostedImageTrial,
    HostedTextTrial,
    Workspace,
)


class SavedTrialsFixture:
    def setUp(self):
        super().setUp()
        self.owner = get_user_model().objects.create_user(username="saved-ad-owner")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Synthetic saved outputs"
        )
        opts = override_settings(
            DEBUG=True,
            LOCAL_HOSTED_TEXT_TRIAL_ENABLED=True,
            LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID=self.workspace.pk,
            LOCAL_HOSTED_IMAGE_TRIAL_ENABLED=True,
            LOCAL_HOSTED_AD_DRAFT_ENABLED=True,
        )
        opts.enable()
        self.addCleanup(opts.disable)
        env = mock.patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "", "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "0"},
        )
        env.start()
        self.addCleanup(env.stop)
        self.text = HostedTextTrial.objects.create(
            workspace=self.workspace,
            owner=self.owner,
            profile=hosted_trial.PROFILE,
            source_hash=REQUEST.source_hash,
            status="completed",
            budget_state="settled",
            reserved_usd="0.001",
            actual_usd="0.00027610",
            model=OPENROUTER_MODEL,
            provider="Azure",
            usage={"input_tokens": 486, "output_tokens": 455},
            variants=[
                {
                    "key": "product",
                    "angle": "Ürün",
                    "headline": "El yapımı seramik kupalar",
                    "body": "Koleksiyonu keşfet.",
                    "call_to_action": "Keşfet",
                },
                {
                    "key": "colors",
                    "angle": "Renk",
                    "headline": "Doğal renkler",
                    "body": "Zeytin yeşili ve kum beji.",
                    "call_to_action": "Keşfet",
                },
            ],
        )
        with Image.new("RGB", (768, 1376), "#e8dfcc") as image:
            ImageDraw.Draw(image).rectangle((0, 900, 767, 1375), fill="#244c3b")
            out = io.BytesIO()
            image.save(out, format="PNG")
            original = out.getvalue()
        normalized = normalize_raster(original, declared_media_type="image/png")
        self.image = HostedImageTrial.objects.create(
            workspace=self.workspace,
            owner=self.owner,
            profile=hosted_image_trial.PROFILE,
            source_hash=hosted_image_trial.SOURCE_HASH,
            status="completed",
            budget_state="settled",
            reserved_usd="0.10",
            actual_usd="0.033625",
            model=hosted_image_trial.MODEL,
            provider=hosted_image_trial.PROVIDER,
            original=original,
            png=normalized.png,
            original_sha256=sha256(original).hexdigest(),
            png_sha256=normalized.derivative_sha256,
            source_media_type="image/png",
            width=768,
            height=1376,
            normalization_tool=normalized.tool,
        )
        self.forbidden = []
        for module, name in (
            (hosted_trial, "OpenRouterCreativeGenerator"),
            (hosted_trial, "reserve_evaluation_cost"),
            (hosted_trial, "settle_evaluation_cost"),
            (hosted_image_trial, "generate_image"),
            (hosted_image_trial, "reserve_evaluation_cost"),
            (hosted_image_trial, "settle_evaluation_cost"),
        ):
            patch = mock.patch.object(
                module,
                name,
                side_effect=AssertionError("Forbidden provider/budget call"),
            )
            self.forbidden.append(patch.start())
            self.addCleanup(patch.stop)

    def tearDown(self):
        for call in self.forbidden:
            call.assert_not_called()
        super().tearDown()

    def source(self):
        return digest(service.sources(self.owner, "product")[-2])

    def create(self):
        return service.create_draft(
            owner=self.owner, candidate_key="product", expected_source=self.source()
        )

    def save(self, draft, *, revision=None, **edits):
        return service.save_draft(
            owner=self.owner,
            draft_id=draft.pk,
            expected_revision=revision or draft.revision,
            expected_source=draft.source_fingerprint,
            content={**draft.content, **edits},
        )


class HostedAdDraftTests(SavedTrialsFixture, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.url = reverse("brands:hosted_ad_choices")
        self.create_url = reverse("brands:hosted_ad_create")

    def post(self, url, data, client=None):
        return (client or self.client).post(
            url, urlencode(data), content_type="application/x-www-form-urlencoded"
        )

    def test_create_edit_reopen_and_replay_preserve_outputs_and_history(self):
        before_text = HostedTextTrial.objects.values().get()
        before_image = HostedImageTrial.objects.values().get()
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertFalse(HostedAdDraft.objects.exists())
        draft = self.create()
        self.assertEqual(draft.revision, 1)
        self.assertEqual(draft.source_manifest["candidate"]["key"], "product")
        draft = self.save(draft, title="Benim düzenlemem")
        replay = self.create()
        self.assertEqual(replay.pk, draft.pk)
        self.assertEqual(replay.content["title"], "Benim düzenlemem")
        self.assertEqual(
            list(replay.history.values_list("revision", flat=True)), [2, 1]
        )
        self.assertEqual(
            replay.history.get(revision=1).content["title"], "El yapımı seramik kupalar"
        )
        self.assertEqual(HostedTextTrial.objects.values().get(), before_text)
        self.assertEqual(HostedImageTrial.objects.values().get(), before_image)
        self.assertFalse(BrandCreativeDocument.objects.exists())

    def test_stale_save_does_not_overwrite_or_append(self):
        draft = self.create()
        stale = HostedAdDraft.objects.get(pk=draft.pk)
        self.save(draft, title="Yeni kayıt")
        with self.assertRaises(ValidationError):
            self.save(stale, title="Eski sekme")
        draft.refresh_from_db()
        self.assertEqual(draft.content["title"], "Yeni kayıt")
        self.assertEqual(draft.history.count(), 2)

    def test_source_change_corruption_unsettled_and_wrong_fingerprint_refuse(self):
        with self.assertRaises(ValidationError):
            service.create_draft(
                owner=self.owner, candidate_key="product", expected_source="0" * 64
            )
        draft = self.create()
        HostedImageTrial.objects.filter(pk=self.image.pk).update(png=b"bad")
        with self.assertRaises(ValueError):
            service.checked_draft(self.owner, draft.pk)
        self.assertEqual(
            self.client.get(
                reverse("brands:hosted_ad_image", args=[draft.pk])
            ).status_code,
            409,
        )
        self.assertEqual(draft.history.count(), 1)

    def test_changed_valid_text_cannot_rebind_existing_draft(self):
        draft = self.create()
        variants = list(self.text.variants)
        variants[0] = {**variants[0], "headline": "Değiştirilmiş kaynak"}
        HostedTextTrial.objects.update(variants=variants)
        with self.assertRaises(ValidationError):
            service.checked_draft(self.owner, draft.pk)
        with self.assertRaises(ValidationError):
            self.create()
        draft.refresh_from_db()
        self.assertEqual(draft.revision, 1)

    def test_flags_foreign_inactive_and_unsettled_scope_refuse(self):
        draft = self.create()
        for options in (
            {"LOCAL_HOSTED_AD_DRAFT_ENABLED": False},
            {"LOCAL_HOSTED_IMAGE_TRIAL_ENABLED": False},
            {"DEBUG": False},
        ):
            with override_settings(**options):
                self.assertEqual(self.client.get(self.url).status_code, 404)
        foreign = get_user_model().objects.create_user(username="foreign-draft-owner")
        self.client.force_login(foreign)
        self.assertEqual(
            self.client.get(
                reverse("brands:hosted_ad_editor", args=[draft.pk])
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                reverse("brands:hosted_ad_image", args=[draft.pk])
            ).status_code,
            404,
        )
        HostedTextTrial.objects.filter(pk=self.text.pk).update(budget_state="unknown")
        with self.assertRaises(ValueError):
            service.checked_draft(self.owner, draft.pk)
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            service.admitted_workspace(self.owner)

    def test_text_bounds_utf16_controls_exact_keys_and_color(self):
        valid = {
            "title": "Başlık",
            "body": "Açıklama",
            "cta": "Keşfet",
            "color": "#244c3b",
        }
        for edits in (
            {"title": "😀" * 31},
            {"body": "a\nb"},
            {"body": "\ud800"},
            {"cta": "a\u2028b"},
            {"color": "red"},
            {"extra": "value"},
            {"title": " "},
        ):
            with self.subTest(edits=repr(edits)), self.assertRaises(ValidationError):
                service.validate_content({**valid, **edits})
        self.assertEqual(
            service.validate_content({**valid, "title": "😀" * 30})["title"], "😀" * 30
        )

    def test_revision_write_failure_rolls_back_draft_and_history(self):
        with mock.patch.object(
            HostedAdRevision.objects, "create", side_effect=RuntimeError
        ):
            with self.assertRaises(RuntimeError):
                self.create()
        self.assertFalse(HostedAdDraft.objects.exists())
        draft = self.create()
        with mock.patch.object(
            HostedAdRevision.objects, "create", side_effect=RuntimeError
        ):
            with self.assertRaises(RuntimeError):
                self.save(draft, title="Must roll back")
        draft.refresh_from_db()
        self.assertEqual(draft.revision, 1)
        self.assertEqual(draft.history.count(), 1)

    def test_history_is_append_only_and_noop_does_not_append(self):
        draft = self.create()
        self.save(draft)
        self.assertEqual(draft.history.count(), 1)
        with self.assertRaises(ValidationError):
            draft.history.update(content={})
        with self.assertRaises(ValidationError):
            draft.history.first().save()
        with self.assertRaises(ValidationError):
            draft.history.first().delete()

    def test_http_create_save_private_and_html_escaping(self):
        response = self.post(
            self.create_url, {"candidate": "product", "source": self.source()}
        )
        self.assertEqual(response.status_code, 302)
        draft = HostedAdDraft.objects.get()
        response = self.post(
            reverse("brands:hosted_ad_save", args=[draft.pk]),
            {
                "revision": 1,
                "source": draft.source_fingerprint,
                **draft.content,
                "title": "<script>alert(1)</script>",
            },
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("brands:hosted_ad_editor", args=[draft.pk]))
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "\\u003Cscript\\u003E")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertIn("script-src 'self'", response["Content-Security-Policy"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    def test_preparse_csrf_methods_and_duplicate_fields(self):
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
                    self.client.post(
                        self.create_url, body, content_type=ct
                    ).status_code,
                    415,
                )
        self.assertEqual(self.client.get(self.create_url).status_code, 405)
        self.assertEqual(
            self.client.post(
                self.url, "x=y", content_type="application/x-www-form-urlencoded"
            ).status_code,
            405,
        )
        self.assertEqual(
            self.client.post(
                self.create_url,
                "candidate=product&candidate=colors",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            400,
        )
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(
            self.post(
                self.create_url,
                {"candidate": "product", "source": self.source()},
                client,
            ).status_code,
            403,
        )
        response = Client().get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertFalse(HostedAdDraft.objects.exists())

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_creates_share_one_draft_and_history(self):
        barrier = Barrier(2)
        source = self.source()

        def create():
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                barrier.wait(timeout=8)
                return service.create_draft(
                    owner=owner, candidate_key="product", expected_source=source
                ).pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(create) for _ in range(2)]
            results = [f.result(timeout=15) for f in futures]
        self.assertEqual(results[0], results[1])
        self.assertEqual(HostedAdDraft.objects.count(), 1)
        self.assertEqual(HostedAdRevision.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_saves_accept_only_one_expected_revision(self):
        draft = self.create()
        barrier = Barrier(2)

        def save(title):
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                barrier.wait(timeout=8)
                try:
                    service.save_draft(
                        owner=owner,
                        draft_id=draft.pk,
                        expected_revision=1,
                        expected_source=draft.source_fingerprint,
                        content={**draft.content, "title": title},
                    )
                    return "saved"
                except ValidationError:
                    return "stale"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(save, title) for title in ("Birinci", "İkinci")]
            results = [f.result(timeout=15) for f in futures]
        self.assertCountEqual(results, ["saved", "stale"])
        draft.refresh_from_db()
        self.assertEqual(draft.revision, 2)
        self.assertEqual(draft.history.count(), 2)
