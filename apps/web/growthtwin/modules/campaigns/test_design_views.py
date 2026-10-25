"""Closed, CSRF-safe same-workspace design choice forms and private errors."""

from unittest.mock import patch
from urllib.parse import urlencode

from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.workspaces.models import Workspace

from .design_selection import current_design
from .models import CampaignDesignChoice
from .test_design_selection import SelectionFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    },
)
class DesignViewTests(SelectionFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.url = reverse("campaigns:design", args=[self.draft.pk])

    def payload(self):
        return dict(
            brand_id=self.brand.pk,
            document_id=str(self.document.pk),
            expected_document_revision=1,
            expected_selection_version=0,
            request_id=str(self.selection_request),
        )

    def post(self, data=None, client=None):
        return (client or self.client).post(
            self.url,
            urlencode(data or self.payload()),
            content_type="application/x-www-form-urlencoded",
        )

    def test_get_no_implicit_choice_post_pins_and_repeat_does_not_duplicate(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Henüz marka ve tasarım seçilmedi")
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertFalse(CampaignDesignChoice.objects.exists())
        for _ in range(2):
            self.assertRedirects(self.post(), self.url)
        self.assertEqual(self.draft.design_choices.count(), 1)
        response = self.client.get(reverse("campaigns:detail", args=[self.draft.pk]))
        self.assertContains(response, "Seçili tasarım kaydı 1")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertContains(response, "görsel seçimi yayın onayı değildir")

    def test_flags_auth_scope_and_error_headers(self):
        for status, client in ((302, Client()),):
            response = client.get(self.url)
            self.assertEqual(response.status_code, status)
            self.assertIn("no-store", response["Cache-Control"])
        with self.settings(SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=False):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 404)
            self.assertIn("no-store", response["Cache-Control"])
        self.client.force_login(self.other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotContains(
            response, self.document.identity.brand.name, status_code=404
        )

    def test_csrf_and_invalid_stale_payload(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(self.post(client=client).status_code, 403)
        self.assertEqual(
            self.post(self.payload() | {"untrusted_proof": "yes"}).status_code, 409
        )
        self.post()
        self.assertEqual(
            self.post(
                self.payload() | {"request_id": "00000000-0000-0000-0000-000000000001"}
            ).status_code,
            409,
        )
        self.assertEqual(
            current_design(owner=self.owner, draft_id=self.draft.pk).version, 1
        )

    def test_multipart_refused_before_csrf_parser_including_zero_prefixed_route(self):
        for path in (
            self.url,
            self.url.replace(f"/{self.draft.pk}/", f"/00{self.draft.pk}/"),
        ):
            with patch.object(
                HttpRequest,
                "_load_post_and_files",
                side_effect=AssertionError("must not parse"),
            ):
                response = self.client.post(path, {"file": "synthetic-not-a-file"})
            self.assertEqual(response.status_code, 415)
            self.assertIn("no-store", response["Cache-Control"])
        response = self.client.post(
            self.url, "x" * 9000, content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 415)

    def test_editor_return_hint_is_owned_same_workspace_and_not_a_redirect(self):
        editor = reverse(
            "brand_documents:editor", args=[self.brand.pk, self.document.pk]
        )
        self.assertContains(
            self.client.get(editor, {"campaign": self.draft.pk}),
            "Kampanyanın tasarım seçimine dön",
        )
        other = self.draft.__class__.objects.get(pk=self.draft.pk)
        other.pk = None
        other.workspace = Workspace.objects.create(
            owner=self.owner, name="Other workspace"
        )
        other.save()
        for value in (
            str(other.pk),
            "9999999999999999999",
            "https://example.invalid/",
            "javascript:alert(1)",
        ):
            response = self.client.get(editor, {"campaign": value})
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "Kampanyanın tasarım seçimine dön")
