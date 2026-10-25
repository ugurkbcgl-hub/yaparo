"""Pinned scene/source HTTP reads never follow later edits or selections."""

from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.assets.durable_rasters import create_palette_material
from growthtwin.modules.workspaces.models import Brand, Workspace

from .test_design_selection import SelectionFixture


@override_settings(DEBUG=True, SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True)
class DesignPreviewTests(SelectionFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.select()
        self.url = reverse("campaigns:design_preview", args=[self.draft.pk, 1])
        self.image = reverse("campaigns:design_image", args=[self.draft.pk, 1])

    def test_exact_snapshot_after_live_edit_and_no_write_bootstrap(self):
        before = deepcopy(self.document.scene)
        scene = deepcopy(before)
        scene["layers"][2]["text"] = "Yeni kayıt seçilmedi"
        self.save(scene)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["bootstrap"]["scene"], before)
        self.assertEqual(
            set(response.context["bootstrap"]),
            {"scene", "selection_version", "palette_url"},
        )
        self.assertNotContains(response, "Yeni kayıt seçilmedi")
        self.assertNotContains(response, 'id="save"')
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
        self.assertEqual(self.document.history.count(), 2)
        self.assertEqual(self.draft.design_choices.count(), 1)

    def test_old_selection_address_refuses_instead_of_following_new_choice(self):
        self.select(expected_selection_version=1, request_id=uuid4())
        for url in (self.url, self.image):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 409)
            self.assertIn("no-store", response["Cache-Control"])
        fresh = reverse("campaigns:design_preview", args=[self.draft.pk, 2])
        self.assertEqual(self.client.get(fresh).status_code, 200)

    def test_flags_auth_archival_and_workspace_transfer_deny(self):
        self.assertEqual(Client().get(self.url).status_code, 302)
        self.client.force_login(self.other)
        for url in (self.url, self.image):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertIn("no-store", response["Cache-Control"])
        self.client.force_login(self.owner)
        for changes in ({"SYNTHETIC_CAMPAIGN_DESIGN_ENABLED": False}, {"DEBUG": False}):
            with self.settings(**changes):
                self.assertEqual(self.client.get(self.url).status_code, 404)
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=False)
        same_owner_workspace = Workspace.objects.create(
            owner=self.owner, name="Başka marka alanı"
        )
        Brand.objects.filter(pk=self.brand.pk).update(workspace=same_owner_workspace)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        Brand.objects.filter(pk=self.brand.pk).update(workspace=self.workspace)
        Workspace.objects.filter(pk=self.workspace.pk).update(owner=self.other)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_write_attempts_refused_before_body_parsing(self):
        for path in (self.url, self.image, self.url.replace("/1/", "/01/")):
            with patch.object(
                HttpRequest,
                "_load_post_and_files",
                side_effect=AssertionError("no intake"),
            ):
                response = self.client.post(path, {"file": "synthetic"})
            self.assertEqual(response.status_code, 405)
            self.assertEqual(response["Allow"], "GET, HEAD")
            self.assertIn("no-store", response["Cache-Control"])

    @override_settings(SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
    def test_palette_matches_pinned_source_and_flag_is_required(self):
        pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        document = self.create(
            request_id=uuid4(), palette_material_id=pair.version.material_id
        )
        self.select(
            document_id=document.pk, expected_selection_version=1, request_id=uuid4()
        )
        url = reverse("campaigns:design_image", args=[self.draft.pk, 2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, bytes(pair.derivative))
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("no-store", response["Cache-Control"])
        with self.settings(SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=False):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_non_palette_missing_selection_and_huge_version_fail_closed(self):
        self.assertEqual(self.client.get(self.image).status_code, 409)
        for version in (0, 2**80):
            self.assertEqual(
                self.client.get(
                    reverse("campaigns:design_preview", args=[self.draft.pk, version])
                ).status_code,
                409,
            )
