"""Owned brand composition with saved fake outcomes and forbidden billing."""

import io
from concurrent.futures import ThreadPoolExecutor
from copy import copy
from dataclasses import replace
from threading import Barrier
from unittest import mock
from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import close_old_connections
from django.db.models.deletion import ProtectedError
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse
from PIL import Image

from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.content.creative import CreativeVariant

from . import brand_ad_drafts as ads
from . import brand_generation as generation
from . import production_briefs
from .creative_documents import create_document
from .models import BrandAdDraft, BrandAdRevision, BrandGenerationAttempt
from .test_brand_generation import GenerationFixture
from .test_brands import changed_identity


class BrandAdFixture(GenerationFixture):
    def make(self, **changes):
        name = getattr(self, "composition_brand_name", None)
        if name and self.brand.name != name:
            self.brand.name = name
            self.brand.save(update_fields=["name"])
        return super().make(**changes)

    def setUp(self):
        super().setUp()
        self.generator.generate.return_value = replace(
            self.generator.generate.return_value,
            variants=(
                CreativeVariant(
                    key="calm",
                    angle="Sade",
                    headline="Duru Seramik",
                    body="Gününe bir detay.",
                    call_to_action="Keşfet",
                ),
            ),
        )
        self.text = self.run_job()
        self.image_plan = self.make(
            expected_version=1, brief={**self.brief, "deliverable": "image"}
        )
        settings.LOCAL_BRAND_AI_APPROVED_REQUESTS[str(self.image_plan.pk)] = (
            self.image_plan.fingerprint
        )
        stream = io.BytesIO()
        Image.new("RGB", (768, 1376), "#254d9b").save(stream, format="PNG")
        with mock.patch.object(
            generation, "generate_image", return_value=(stream.getvalue(), ".png", 0.03)
        ):
            self.image = self.run_job(self.image_plan)
        assert self.text.status == self.image.status == "completed"
        gate = override_settings(LOCAL_BRAND_AD_ENABLED=True)
        gate.enable()
        self.addCleanup(gate.disable)
        self.key = self.text.output["variants"][0]["key"]
        self.offline = []
        for name in (
            "generate",
            "generate_image",
            "BrandCopyGenerator",
            "reserve_evaluation_cost",
            "settle_evaluation_cost",
        ):
            patch = mock.patch.object(
                generation,
                name,
                side_effect=AssertionError("Forbidden billing operation"),
            )
            self.offline.append(patch.start())
            self.addCleanup(patch.stop)

    def tearDown(self):
        for spy in self.offline:
            spy.assert_not_called()
        super().tearDown()

    def manifest(self):
        return ads.pair(
            self.owner, self.brand.pk, self.plan.pk, self.image_plan.pk, self.key
        )[-1]

    def ad(self, **changes):
        return ads.create(
            **(
                {
                    "owner": self.owner,
                    "brand_id": self.brand.pk,
                    "text_request": self.plan.pk,
                    "image_request": self.image_plan.pk,
                    "candidate_key": self.key,
                    "expected_source": digest(self.manifest()),
                }
                | changes
            )
        )

    def edit_ad(self, draft, **changes):
        return ads.save(
            **(
                {
                    "owner": self.owner,
                    "brand_id": self.brand.pk,
                    "draft_id": draft.pk,
                    "expected_revision": draft.revision,
                    "expected_source": draft.source_fingerprint,
                    "content": {**draft.content, "cta": "İncele"},
                }
                | changes
            )
        )


class BrandAdTests(BrandAdFixture, TransactionTestCase):
    def test_second_brand_has_independent_name_palette_and_sources(self):
        changed_identity(self.owner, self.service, primary_color="#8a2d3b")
        self.service.refresh_from_db()
        document = create_document(
            owner=self.owner,
            brand_id=self.service.pk,
            expected_identity_version=2,
            request_id=uuid4(),
        )
        plans = []
        for version, kind in enumerate(("copy", "image")):
            plan = production_briefs.create(
                owner=self.owner,
                brand_id=self.service.pk,
                document_id=document.pk,
                document_revision=1,
                identity_version=2,
                expected_version=version,
                request_id=uuid4(),
                brief={**self.brief, "deliverable": kind},
            )
            plans.append(plan)
            settings.LOCAL_BRAND_AI_APPROVED_REQUESTS[str(plan.pk)] = plan.fingerprint
            original = self.text if kind == "copy" else self.image
            BrandGenerationAttempt.objects.create(
                request=plan,
                fingerprint=plan.fingerprint,
                input_hash=generation.input_hash(plan),
                kind=kind,
                status="completed",
                budget_state="settled",
                reserved_usd=original.reserved_usd,
                actual_usd=original.actual_usd,
                output=(
                    {
                        **original.output,
                        "variants": [
                            {**v, "headline": "Özen Ev Bakımı"}
                            for v in original.output["variants"]
                        ],
                    }
                    if kind == "copy"
                    else original.output
                ),
                original=bytes(original.original),
                png=bytes(original.png),
            )
        manifest = ads.pair(
            self.owner, self.service.pk, plans[0].pk, plans[1].pk, self.key
        )[-1]
        other = ads.create(
            owner=self.owner,
            brand_id=self.service.pk,
            text_request=plans[0].pk,
            image_request=plans[1].pk,
            candidate_key=self.key,
            expected_source=digest(manifest),
        )
        self.assertEqual(other.source_manifest["brand_name"], self.service.name)
        self.assertEqual(other.content["color"], "#8a2d3b")
        self.assertEqual(other.content["title"], "Özen Ev Bakımı")
        self.assertNotEqual(other.brand_id, self.ad().brand_id)
        with self.assertRaises(ObjectDoesNotExist):
            ads.checked(self.owner, self.brand.pk, other.pk)

    def test_create_save_replay_preserves_history_identity_and_cost_provenance(self):
        draft = self.ad()
        self.assertEqual(draft.identity_id, self.plan.identity_id)
        self.assertEqual(
            draft.content["color"], self.plan.envelope["identity"]["primary_color"]
        )
        self.assertEqual(
            draft.source_manifest["image"]["cost_usd"], str(self.image.actual_usd)
        )
        edited = self.edit_ad(draft)
        self.assertEqual(edited.revision, 2)
        self.assertEqual(self.ad().content["cta"], "İncele")
        with self.assertRaises(ValidationError):
            self.edit_ad(draft)
        self.assertEqual(BrandAdRevision.objects.count(), 2)
        with self.assertRaises(ValidationError):
            BrandAdRevision.objects.update(content={})
        with self.assertRaises(ProtectedError):
            self.image.delete()
        changed_identity(self.owner, self.brand)
        self.assertEqual(
            ads.checked(self.owner, self.brand.pk, draft.pk)[0].identity_id,
            self.plan.identity_id,
        )

    def test_foreign_brand_owner_source_key_and_disabled_refuse(self):
        for overrides in (
            {"brand_id": self.service.pk},
            {"owner": self.other},
            {"candidate_key": "missing"},
            {"expected_source": "0" * 64},
        ):
            with self.assertRaises((ObjectDoesNotExist, ValidationError)):
                self.ad(**overrides)
        with override_settings(LOCAL_BRAND_AD_ENABLED=False):
            with self.assertRaises(PermissionDenied):
                self.ad()
        self.assertEqual(BrandAdDraft.objects.count(), 0)

    def test_mismatched_identity_or_source_is_not_a_pair(self):
        bad = copy(self.image)
        bad.request = copy(self.image.request)
        for field in ("identity_id", "source_revision_id"):
            original = getattr(bad.request, field)
            setattr(bad.request, field, original + 100)
            with mock.patch.object(generation, "read", side_effect=[self.text, bad]):
                with self.assertRaises(ValidationError):
                    self.manifest()
            setattr(bad.request, field, original)

    def test_corrupt_result_manifest_history_and_unsettled_job_deny_read(self):
        draft = self.ad()
        BrandAdDraft.objects.filter(pk=draft.pk).update(source_fingerprint="0" * 64)
        with self.assertRaises(ValidationError):
            ads.checked(self.owner, self.brand.pk, draft.pk)
        BrandAdDraft.objects.filter(pk=draft.pk).update(
            source_fingerprint=draft.source_fingerprint,
            content={**draft.content, "cta": "Changed"},
        )
        with self.assertRaises(ValidationError):
            ads.checked(self.owner, self.brand.pk, draft.pk)
        BrandAdDraft.objects.filter(pk=draft.pk).update(content=draft.content)
        BrandGenerationAttempt.objects.filter(pk=self.image.pk).update(
            budget_state="held"
        )
        with self.assertRaises(ValueError):
            ads.checked(self.owner, self.brand.pk, draft.pk)

    def test_http_ownership_csrf_methods_closed_forms_and_private_image(self):
        draft = self.ad()
        url = reverse("brands:brand_ad_editor", args=[self.brand.pk, draft.pk])
        image = reverse("brands:brand_ad_image", args=[self.brand.pk, draft.pk])
        save = reverse("brands:brand_ad_save", args=[self.brand.pk, draft.pk])
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.get(image)
        self.assertEqual(response.content, bytes(self.image.png))
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(save).status_code, 405)
        self.assertEqual(self.client.post(save, {}).status_code, 415)
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.owner)
        self.assertEqual(
            csrf.post(
                save, "x=1", content_type="application/x-www-form-urlencoded"
            ).status_code,
            403,
        )
        body = {
            "revision": 1,
            "source": draft.source_fingerprint,
            **draft.content,
            "extra": "forbidden",
        }
        self.assertEqual(
            self.client.post(
                save, urlencode(body), content_type="application/x-www-form-urlencoded"
            ).status_code,
            409,
        )
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(image).status_code, 404)

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_creates_reuse_one_draft(self):
        barrier = Barrier(2)

        def run():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return self.ad().pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            values = [
                f.result(timeout=20) for f in [pool.submit(run), pool.submit(run)]
            ]
        self.assertEqual(values[0], values[1])
        self.assertEqual(BrandAdDraft.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_saves_accept_one_revision(self):
        draft = self.ad()
        barrier = Barrier(2)

        def run(cta):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    self.edit_ad(draft, content={**draft.content, "cta": cta})
                    return True
                except ValidationError:
                    return False
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            values = [
                f.result(timeout=20)
                for f in [pool.submit(run, "Bir"), pool.submit(run, "İki")]
            ]
        self.assertEqual(sorted(values), [False, True])
        self.assertEqual(BrandAdRevision.objects.count(), 2)
