"""Navigation context stays optional, bounded and in the same owned workspace."""

from uuid import uuid4

from django.test import TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.campaigns.test_design_selection import SelectionFixture
from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner


@override_settings(DEBUG=True, SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True)
class CampaignContextTests(SelectionFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.brand_url = reverse("brands:detail", args=[self.brand.pk])
        self.create_url = reverse("brand_documents:create", args=[self.brand.pk])
        self.document_url = reverse(
            "brand_documents:detail", args=[self.brand.pk, self.document.pk]
        )

    def test_successful_create_keeps_hint_without_creating_selection(self):
        response = self.client.get(self.brand_url, {"campaign": self.draft.pk})
        self.assertEqual(response.context["campaign_return_id"], self.draft.pk)
        response = self.client.post(
            self.create_url + f"?campaign={self.draft.pk}",
            dict(
                brand_id=self.brand.pk,
                expected_identity_version=1,
                request_id=uuid4(),
                design_format="portrait",
            ),
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].endswith(f"?campaign={self.draft.pk}"))
        page = self.client.get(response["Location"])
        self.assertEqual(page.context["campaign_return_id"], self.draft.pk)
        self.assertContains(page, "Kampanyanın tasarım seçimine dön")
        self.assertFalse(self.draft.design_choices.exists())

    def test_failed_create_keeps_return_and_retry_context(self):
        response = self.client.post(
            self.create_url + f"?campaign={self.draft.pk}",
            dict(
                brand_id=self.brand.pk, expected_identity_version=99, request_id=uuid4()
            ),
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.context["campaign_return_id"], self.draft.pk)
        self.assertContains(
            response, "Kampanyanın tasarım seçimine dön", status_code=409
        )
        self.assertContains(
            response, self.brand_url + f"?campaign={self.draft.pk}", status_code=409
        )
        self.assertFalse(self.draft.design_choices.exists())

    def test_foreign_same_owner_workspace_invalid_and_disabled_hints_ignored(self):
        second = self.draft.__class__.objects.get(pk=self.draft.pk)
        second.pk = None
        second.workspace = Workspace.objects.create(
            owner=self.owner, name="Other owned workspace"
        )
        second.save()
        foreign = self.draft.__class__.objects.get(pk=self.draft.pk)
        foreign.pk = None
        foreign.workspace = self.foreign.workspace
        foreign.save()
        for value in (
            str(second.pk),
            str(foreign.pk),
            "0",
            "01",
            "-1",
            "9999999999999999999",
            "https://example.invalid/",
            "javascript:alert(1)",
        ):
            for url in (self.brand_url, self.document_url):
                response = self.client.get(url, {"campaign": value})
                self.assertIsNone(response.context["campaign_return_id"])
                self.assertNotContains(response, "Kampanyanın tasarım seçimine dön")
        for options in ({"DEBUG": False}, {"SYNTHETIC_CAMPAIGN_DESIGN_ENABLED": False}):
            with self.settings(**options):
                self.assertIsNone(
                    self.client.get(
                        self.brand_url, {"campaign": self.draft.pk}
                    ).context["campaign_return_id"]
                )

    def test_chooser_offers_only_active_same_workspace_brands(self):
        other = Workspace.objects.create(owner=self.owner, name="Other")
        extra = create_brand_for_owner(
            owner=self.owner, workspace_id=other.pk, fixture="product"
        )
        response = self.client.get(reverse("campaigns:design", args=[self.draft.pk]))
        self.assertEqual(
            {brand.pk for brand in response.context["design_brands"]},
            {self.brand.pk, self.service.pk},
        )
        self.assertNotIn(
            extra.pk, {brand.pk for brand in response.context["design_brands"]}
        )
