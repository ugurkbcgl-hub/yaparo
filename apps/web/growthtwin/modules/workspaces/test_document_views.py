"""Synthetic HTTP document ownership, bounded fields and revision checks."""

from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.workspaces.creative_documents import (
    create_document,
    read_document,
)
from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import (
    create_brand_for_owner,
    update_brand_identity_for_owner,
)


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class DocumentViewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="document-owner")
        self.other = get_user_model().objects.create_user(username="document-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Örnek alan")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="product"
        )
        self.document = create_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_identity_version=1,
            request_id=uuid4(),
        )
        self.client.force_login(self.owner)

    def url(self, name="detail", brand=None, document=None):
        args = [brand or self.brand.pk]
        if name != "create":
            args.append(document or self.document.pk)
        return reverse("brand_documents:" + name, args=args)

    def payload(self):
        return {
            "expected_revision": 1,
            "title": "Yeni örnek başlık",
            "subtitle": "Kurgusal örnek",
            "title_color": "#254D9B",
            "subtitle_color": "#245C48",
        }

    def test_authentication_and_methods(self):
        self.assertEqual(self.client.get(self.url("create")).status_code, 405)
        self.assertEqual(self.client.put(self.url()).status_code, 405)
        self.assertEqual(self.client.post(self.url("download")).status_code, 405)
        self.client.logout()
        for name in ("detail", "download"):
            self.assertEqual(self.client.get(self.url(name)).status_code, 302)
        self.assertEqual(self.client.post(self.url("create")).status_code, 302)

    def test_detail_shows_pinned_source_versions_without_changing_scene_download(self):
        response = self.client.get(self.url())
        self.assertContains(response, "Bu çalışmanın kaynakları")
        self.assertContains(response, "Seramik ürün illüstrasyonu")
        self.assertContains(response, "Materyal sürümü 1", count=2)
        self.assertEqual(
            self.client.get(self.url("download")).json(), self.document.scene
        )

    def test_create_replay_does_not_replace_document(self):
        request_id = uuid4()
        payload = {
            "brand_id": self.brand.pk,
            "expected_identity_version": 1,
            "request_id": str(request_id),
        }
        for _ in range(2):
            self.assertRedirects(
                self.client.post(self.url("create"), payload),
                self.url(document=request_id),
            )
        document = read_document(
            owner=self.owner, brand_id=self.brand.pk, document_id=request_id
        )
        self.assertEqual(document.revision, 1)

    def test_create_invalid_and_stale_inputs_are_generic_conflicts(self):
        for payload in (
            {
                "brand_id": self.brand.pk,
                "expected_identity_version": 1,
                "request_id": "secret-invalid-id",
            },
            {
                "brand_id": self.brand.pk + 100,
                "expected_identity_version": 1,
                "request_id": str(uuid4()),
            },
            {
                "brand_id": self.brand.pk,
                "expected_identity_version": 999,
                "request_id": str(uuid4()),
            },
        ):
            response = self.client.post(self.url("create"), payload)
            self.assertEqual(response.status_code, 409)
            self.assertNotContains(response, "secret-invalid-id", status_code=409)

    def test_get_and_download_do_not_save(self):
        before = deepcopy(self.document.scene)
        with patch(
            "growthtwin.modules.workspaces.document_views.save_document",
            side_effect=AssertionError,
        ):
            response = self.client.get(self.url())
            download = self.client.get(self.url("download"))
        self.assertContains(response, "Kaydedilmiş çalışma sürümü: 1")
        self.assertContains(response, "Bağlı marka kimliği: sürüm 1")
        self.assertContains(response, "tam tasarım veya PNG çıktısı değildir")
        self.assertEqual(download.json(), before)
        self.assertIn("attachment;", download["Content-Disposition"])
        self.assertEqual(download["X-Content-Type-Options"], "nosniff")
        for item in (response, download):
            self.assertIn("no-store", item["Cache-Control"])
        self.document.refresh_from_db()
        self.assertEqual(self.document.scene, before)
        self.assertEqual(self.document.revision, 1)

    def test_edit_only_changes_text_and_colors_and_stale_revision_conflicts(self):
        before = deepcopy(self.document.scene)
        payload = self.payload()
        payload["scene"] = '{"asset":"https://private.example"}'
        payload["identity_version"] = 999
        self.assertEqual(self.client.post(self.url(), payload).status_code, 302)
        self.document.refresh_from_db()
        expected = deepcopy(before)
        for layer in expected["layers"]:
            if layer["id"] in ("title", "subtitle"):
                layer["text"] = payload[layer["id"]]
                layer["color"] = payload[layer["id"] + "_color"]
        self.assertEqual(self.document.scene, expected)
        self.assertEqual(self.document.identity.version, 1)
        self.assertEqual(self.document.revision, 2)
        response = self.client.post(self.url(), payload)
        self.assertEqual(response.status_code, 409)
        self.document.refresh_from_db()
        self.assertEqual(self.document.scene, expected)
        self.assertEqual(self.document.revision, 2)

    def test_utf16_invalid_color_and_control_character_rejected(self):
        for key, value in (
            ("title", "😀" * 51),
            ("subtitle", "bad\x01text"),
            ("title_color", "red;background:url(https://invalid.example)"),
            ("expected_revision", 0),
        ):
            payload = self.payload()
            payload[key] = value
            self.assertEqual(self.client.post(self.url(), payload).status_code, 409)
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 1)

    def test_preview_escapes_plain_text(self):
        payload = self.payload()
        payload["title"] = '<script>alert("example")</script>'
        self.assertEqual(self.client.post(self.url(), payload).status_code, 302)
        response = self.client.get(self.url())
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("example")')
        self.assertNotContains(response, "<script")

    def test_empty_and_exact_utf16_limit_are_valid(self):
        payload = self.payload()
        payload["title"] = "😀" * 50
        payload["subtitle"] = ""
        self.assertEqual(self.client.post(self.url(), payload).status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.scene["layers"][2]["text"], payload["title"])
        self.assertEqual(self.document.scene["layers"][3]["text"], "")

    def test_invalid_persisted_scene_is_safe_conflict_not_download(self):
        with patch(
            "growthtwin.modules.workspaces.document_views.read_document",
            side_effect=ValidationError("private-persisted-value"),
        ):
            for name in ("detail", "download"):
                response = self.client.get(self.url(name))
                self.assertEqual(response.status_code, 409)
                self.assertNotContains(
                    response, "private-persisted-value", status_code=409
                )
                self.assertNotIn("Content-Disposition", response)

    def test_owner_scope_change_during_save_is_not_found(self):
        with patch(
            "growthtwin.modules.workspaces.document_views.save_document",
            side_effect=Workspace.DoesNotExist,
        ):
            self.assertEqual(
                self.client.post(self.url(), self.payload()).status_code, 404
            )

    def test_foreign_owner_and_wrong_brand_are_hidden(self):
        sibling = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="service"
        )
        for name in ("detail", "download"):
            self.assertEqual(
                self.client.get(self.url(name, brand=sibling.pk)).status_code, 404
            )
        self.assertEqual(
            self.client.post(self.url(brand=sibling.pk), self.payload()).status_code,
            404,
        )
        self.client.force_login(self.other)
        for name in ("detail", "download"):
            response = self.client.get(self.url(name))
            self.assertEqual(response.status_code, 404)
            self.assertNotContains(response, self.brand.name, status_code=404)
        self.assertEqual(self.client.post(self.url(), self.payload()).status_code, 404)
        self.assertEqual(self.client.post(self.url("create"), {}).status_code, 404)

    def test_archived_brand_document_hidden(self):
        self.brand.is_archived = True
        self.brand.save(update_fields=["is_archived"])
        for name in ("detail", "download"):
            self.assertEqual(self.client.get(self.url(name)).status_code, 404)

    def test_csrf_required_for_create_and_save(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.url(), self.payload()).status_code, 403)
        self.assertEqual(client.post(self.url("create"), {}).status_code, 403)

    def test_brand_edit_does_not_rebind_old_document(self):
        update_brand_identity_for_owner(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_version=1,
            primary_color="#254D9B",
            secondary_color="#F4E8D2",
            tone="energetic",
            tagline_key="daily_detail",
        )
        response = self.client.get(self.url())
        self.assertContains(response, "Bağlı marka kimliği: sürüm 1")
        self.assertContains(response, "Markanın güncel kimliği: sürüm 2")
        self.assertEqual(self.client.post(self.url(), self.payload()).status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.identity.version, 1)
