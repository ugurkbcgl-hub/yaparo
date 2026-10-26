"""Read-only offline candidates remain bound and never edit a saved scene."""

from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch
from uuid import uuid4

from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.ai_gateway.synthetic import SyntheticTemplateGenerator
from growthtwin.modules.workspaces.models import Brand, Workspace

from .brand_copy import preview_brand_copy
from .test_design_selection import SelectionFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED=True,
)
class BrandCopyTests(SelectionFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.select()
        self.client.force_login(self.owner)
        self.url = reverse("campaigns:brand_copy", args=[self.draft.pk, 1])

    def test_bound_candidates_no_writes_live_user_edits_preserved(self):
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Kullanıcının korunan düzenlemesi"
        self.save(scene)
        draft = self.draft.__class__.objects.values().get(pk=self.draft.pk)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["variants"]), 3)
        self.assertEqual(response.context["context"].brand_id, self.brand.pk)
        self.assertEqual(response.context["context"].document_revision, 1)
        self.assertEqual(response.context["brand_name"], self.brand.name)
        self.document.refresh_from_db()
        self.assertEqual(self.document.scene, scene)
        self.assertEqual(self.document.history.count(), 2)
        self.assertEqual(self.draft.design_choices.count(), 1)
        self.assertEqual(
            self.draft.__class__.objects.values().get(pk=self.draft.pk), draft
        )
        self.assertContains(response, "kurgusal şablon örnekleridir")
        self.assertNotIn("<form", response.content.decode().split("<main", 1)[1])
        self.assertNotContains(response, "<script")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertIn("script-src 'none'", response["Content-Security-Policy"])

    def test_disabled_flags_and_foreign_scope_refuse_before_generator(self):
        for options in (
            {"DEBUG": False},
            {"SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED": False},
            {"SYNTHETIC_CAMPAIGN_DESIGN_ENABLED": False},
        ):
            with (
                self.settings(**options),
                patch.object(SyntheticTemplateGenerator, "generate") as generate,
            ):
                self.assertEqual(self.client.get(self.url).status_code, 404)
                generate.assert_not_called()
        self.assertEqual(Client().get(self.url).status_code, 302)
        self.client.force_login(self.other)
        with patch.object(SyntheticTemplateGenerator, "generate") as generate:
            self.assertEqual(self.client.get(self.url).status_code, 404)
            generate.assert_not_called()
        self.client.force_login(self.owner)
        other = Workspace.objects.create(owner=self.owner, name="Other owned workspace")
        Brand.objects.filter(pk=self.brand.pk).update(workspace=other)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_changed_selection_and_archive_refuse(self):
        self.select(expected_selection_version=1, request_id=uuid4())
        self.assertEqual(self.client.get(self.url).status_code, 409)
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        self.assertEqual(
            self.client.get(
                reverse("campaigns:brand_copy", args=[self.draft.pk, 2])
            ).status_code,
            404,
        )

    def test_selection_changes_during_generation_return_no_candidates(self):
        original = SyntheticTemplateGenerator.generate

        def changed(generator, request):
            result = original(generator, request)
            self.select(expected_selection_version=1, request_id=uuid4())
            return result

        with patch.object(SyntheticTemplateGenerator, "generate", new=changed):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 409)
        self.assertNotContains(response, "Örnek 1", status_code=409)

    def test_candidate_text_is_escaped_even_when_shape_is_valid(self):
        original = SyntheticTemplateGenerator.generate

        def markup(generator, request):
            result = original(generator, request)
            first = replace(
                result.variants[0], headline='<script>alert("fixture")</script>'
            )
            return replace(result, variants=(first,) + result.variants[1:])

        with patch.object(SyntheticTemplateGenerator, "generate", new=markup):
            response = self.client.get(self.url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script")

    def test_unsafe_methods_refuse_before_csrf_body_parsing(self):
        for url in (self.url, self.url.replace("/1/", "/01/")):
            with patch.object(
                HttpRequest,
                "_load_post_and_files",
                side_effect=AssertionError("No intake"),
            ):
                response = self.client.post(url, {"file": "synthetic"})
            self.assertEqual(response.status_code, 405)
            self.assertIn("no-store", response["Cache-Control"])

    def test_service_remains_zero_cost_unapproved_template(self):
        task, result = preview_brand_copy(
            owner=self.owner, draft_id=self.draft.pk, selection_version=1
        )
        self.assertEqual(task.max_cost_microusd, 0)
        self.assertFalse(task.execution_authorized)
        self.assertTrue(result.review_required)
        self.assertFalse(result.publishable)
