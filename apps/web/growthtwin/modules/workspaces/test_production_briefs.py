"""Immutable owned brand/source/brief correlation without external execution."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from unittest import mock
from urllib.parse import urlencode
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import close_old_connections
from django.db.models.deletion import ProtectedError
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from growthtwin.modules.ai_gateway.brand_briefs import (
    mock_receipt,
    validate_brief,
    validate_mock_receipt,
)

from . import production_briefs as service
from .creative_documents import create_document, save_document
from .models import Brand, BrandProductionRequest
from .test_brands import changed_identity
from .test_creative_documents import DocumentFixture


class ProductionBriefFixture(DocumentFixture):
    def setUp(self):
        super().setUp()
        flag = override_settings(DEBUG=True, LOCAL_BRAND_PRODUCTION_BRIEF_ENABLED=True)
        flag.enable()
        self.addCleanup(flag.disable)
        self.document = self.create()
        self.brief = {
            "description": "Kurgusal seramik koleksiyonunu tanıt.",
            "audience": "Türkiye'deki sentetik tasarım meraklıları",
            "objective": "awareness",
            "deliverable": "copy",
        }
        # No provider/budget boundary may be touched during any of these cases.
        self.denied = []
        for target in (
            "growthtwin.modules.ai_gateway.openrouter.OpenRouterCreativeGenerator.generate",
            "growthtwin.modules.workspaces.hosted_image_trial.generate_image",
            "growthtwin.modules.workspaces.hosted_trial.reserve_evaluation_cost",
            "growthtwin.modules.workspaces.hosted_trial.settle_evaluation_cost",
        ):
            patch = mock.patch(
                target, side_effect=AssertionError("Forbidden external boundary")
            )
            self.denied.append(patch.start())
            self.addCleanup(patch.stop)

    def tearDown(self):
        for call in self.denied:
            call.assert_not_called()
        super().tearDown()

    def make(self, **changes):
        return service.create(
            **{
                "owner": self.owner,
                "brand_id": self.brand.pk,
                "document_id": self.document.pk,
                "document_revision": 1,
                "identity_version": 1,
                "expected_version": 0,
                "request_id": uuid4(),
                "brief": self.brief,
                **changes,
            }
        )


class ProductionBriefTests(ProductionBriefFixture, TransactionTestCase):
    def test_pinned_identity_brief_scene_materials_and_mock_correlation(self):
        plan = self.make()
        self.assertEqual(
            plan.envelope["identity"]["primary_color"],
            self.document.identity.primary_color,
        )
        self.assertEqual(plan.envelope["source"]["revision"], 1)
        self.assertEqual(
            [m["layer"] for m in plan.envelope["source"]["materials"]], ["hero", "logo"]
        )
        self.assertTrue(
            all(not m["binary_verified"] for m in plan.envelope["source"]["materials"])
        )
        self.assertEqual(plan.envelope["brief"], self.brief)
        self.assertEqual(
            plan.envelope["execution"],
            {"authorized": False, "max_cost_microusd": 0, "provider": None},
        )
        receipt = mock_receipt(plan.envelope)
        self.assertEqual(
            service.accept_mock(
                owner=self.owner,
                brand_id=self.brand.pk,
                request_id=plan.pk,
                receipt=receipt,
            ),
            receipt,
        )
        changed = deepcopy(plan.envelope)
        changed["brief"]["description"] = "Başka talep"
        with self.assertRaises(ValidationError):
            service.accept_mock(
                owner=self.owner,
                brand_id=self.brand.pk,
                request_id=plan.pk,
                receipt=mock_receipt(changed),
            )

    def test_old_request_survives_identity_and_document_edit_replay_and_new_versions(
        self,
    ):
        plan = self.make()
        original = deepcopy(plan.envelope)
        scene = deepcopy(self.document.scene)
        next(layer for layer in scene["layers"] if layer["id"] == "title")["text"] = (
            "Sonraki tasarım"
        )
        save_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            document_id=self.document.pk,
            expected_revision=1,
            scene=scene,
        )
        changed_identity(self.owner, self.brand)
        old = service.checked(
            owner=self.owner, brand_id=self.brand.pk, request_id=plan.pk
        )
        self.assertEqual(old.envelope, original)
        self.assertEqual(self.make(request_id=plan.pk).pk, plan.pk)
        with self.assertRaises(ValidationError):
            self.make()
        self.brand.refresh_from_db()
        doc = create_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_identity_version=2,
            request_id=uuid4(),
        )
        new = self.make(
            document_id=doc.pk,
            identity_version=2,
            expected_version=1,
            brief={**self.brief, "description": "Yeni sürüm talebi"},
        )
        self.assertEqual(new.version, 2)
        self.assertEqual(new.identity.version, 2)
        self.assertEqual(
            service.checked(
                owner=self.owner, brand_id=self.brand.pk, request_id=plan.pk
            ).envelope,
            original,
        )

    def test_replay_collision_stale_version_and_wrong_brand_refuse(self):
        plan = self.make()
        for changes in (
            {"brief": {**self.brief, "audience": "Başka kitle"}, "request_id": plan.pk},
            {"expected_version": 0},
            {"document_revision": 2, "expected_version": 1},
        ):
            with self.assertRaises(ValidationError):
                self.make(**changes)
        with self.assertRaises(ObjectDoesNotExist):
            self.make(brand_id=self.service.pk)
        with self.assertRaises(ObjectDoesNotExist):
            self.make(owner=self.other)
        self.assertEqual(BrandProductionRequest.objects.count(), 1)

    def test_other_brand_has_own_request_versions_and_receipt_scope(self):
        first = self.make()
        doc = create_document(
            owner=self.owner,
            brand_id=self.service.pk,
            expected_identity_version=1,
            request_id=uuid4(),
        )
        second = self.make(brand_id=self.service.pk, document_id=doc.pk)
        self.assertEqual(second.version, 1)
        self.assertNotEqual(first.envelope["brand_id"], second.envelope["brand_id"])
        with self.assertRaises(ValidationError):
            service.accept_mock(
                owner=self.owner,
                brand_id=self.service.pk,
                request_id=second.pk,
                receipt=mock_receipt(first.envelope),
            )

    def test_append_only_protected_sources_corrupt_fingerprint_and_archive_refuse(self):
        plan = self.make()
        with self.assertRaises(ValidationError):
            plan.save()
        with self.assertRaises(ValidationError):
            plan.delete()
        with self.assertRaises(ValidationError):
            BrandProductionRequest.objects.update(brief={})
        with self.assertRaises(ProtectedError):
            self.document.delete()
        BrandProductionRequest._base_manager.filter(pk=plan.pk).update(
            fingerprint="0" * 64
        )
        with self.assertRaises(ValidationError):
            service.checked(
                owner=self.owner, brand_id=self.brand.pk, request_id=plan.pk
            )
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        with self.assertRaises(ObjectDoesNotExist):
            service.checked(
                owner=self.owner, brand_id=self.brand.pk, request_id=plan.pk
            )

    def test_brief_and_receipt_types_are_strict_and_no_execution_grant(self):
        self.assertEqual(
            validate_brief(
                {**self.brief, "description": "İlk paragraf.\nİkinci paragraf."}
            )["description"],
            "İlk paragraf.\nİkinci paragraf.",
        )
        for change in (
            {"description": "\ud800"},
            {"description": "😀" * 601},
            {"description": "\x00"},
            {"objective": "publish"},
            {"deliverable": "video"},
            {"extra": "value"},
        ):
            with self.assertRaises(ValidationError):
                validate_brief({**self.brief, **change})
        plan = self.make()
        for invalid in (None, {}, {**plan.envelope, "unknown": True}):
            with self.assertRaises(ValidationError):
                mock_receipt(invalid)
        for key, value in (
            ("authorized", 0),
            ("authorized", True),
            ("max_cost_microusd", False),
            ("max_cost_microusd", 1),
            ("provider", "hosted"),
        ):
            envelope = deepcopy(plan.envelope)
            envelope["execution"][key] = value
            with self.assertRaises(ValidationError):
                mock_receipt(envelope)
        receipt = mock_receipt(plan.envelope)
        for change in (
            {"cost_microusd": False},
            {"publishable": 0},
            {"publishable": True},
            {"status": "published"},
        ):
            with self.assertRaises(ValidationError):
                validate_mock_receipt(plan.envelope, {**receipt, **change})

    def test_http_capture_escape_scope_flags_csrf_and_preparse(self):
        client = Client()
        client.force_login(self.owner)
        url = reverse("brands:production_compose", args=[self.brand.pk])
        response = client.get(url)
        form = response.context["form"]
        data = {
            **form.initial,
            "source": form.fields["source"].choices[0][0],
            **self.brief,
            "description": "<script>örnek</script>",
        }
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.owner)
        self.assertEqual(
            csrf.post(
                url, urlencode(data), content_type="application/x-www-form-urlencoded"
            ).status_code,
            403,
        )
        self.assertEqual(
            client.post(url, "{}", content_type="application/json").status_code, 415
        )
        self.assertEqual(
            client.post(
                url,
                urlencode(data) + "&objective=awareness",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            409,
        )
        self.assertEqual(
            client.post(
                url, urlencode(data), content_type="application/x-www-form-urlencoded"
            ).status_code,
            302,
        )
        plan = BrandProductionRequest.objects.get()
        detail = reverse("brands:production_request", args=[self.brand.pk, plan.pk])
        page = client.get(detail)
        self.assertContains(page, "&lt;script&gt;örnek&lt;/script&gt;")
        self.assertNotContains(page, "<script>örnek</script>")
        self.assertIn("no-store", page["Cache-Control"])
        self.assertEqual(page["X-Robots-Tag"], "noindex, nofollow")
        self.assertEqual(client.post(detail).status_code, 405)
        with override_settings(LOCAL_BRAND_PRODUCTION_BRIEF_ENABLED=False):
            self.assertEqual(client.get(detail).status_code, 404)
        client.force_login(self.other)
        self.assertEqual(client.get(detail).status_code, 404)
        self.assertEqual(BrandProductionRequest.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_expected_version_appends_only_one(self):
        barrier = Barrier(2)

        def create():
            close_old_connections()
            try:
                barrier.wait(timeout=8)
                try:
                    self.make()
                    return "saved"
                except ValidationError:
                    return "stale"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = [
                f.result(timeout=15) for f in [pool.submit(create), pool.submit(create)]
            ]
        self.assertCountEqual(results, ["saved", "stale"])
        self.assertEqual(BrandProductionRequest.objects.count(), 1)
