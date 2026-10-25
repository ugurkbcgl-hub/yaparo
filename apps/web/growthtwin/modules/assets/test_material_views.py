"""Closed HTTP setup boundary for the fixed synthetic material catalog."""

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from growthtwin.modules.assets.models import BrandMaterial
from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner


class MaterialCatalogViewTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.owner = users.objects.create_user(username="material-view-owner")
        self.other = users.objects.create_user(username="material-view-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Örnek alan")
        self.other_workspace = Workspace.objects.create(
            owner=self.other, name="Başka alan"
        )
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="service"
        )
        self.other_brand = create_brand_for_owner(
            owner=self.other, workspace_id=self.other_workspace.pk, fixture="service"
        )
        self.url = reverse("brands:materials_prepare", args=[self.brand.pk])

    def test_prepare_is_login_post_csrf_protected_and_has_no_upload_fields(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)
        self.assertEqual(
            self.client.post(
                self.url,
                "intent=prepare",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            302,
        )
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(self.client.put(self.url).status_code, 405)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(
            client.post(
                self.url,
                "intent=prepare",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            403,
        )
        response = self.client.post(
            self.url,
            "url=https%3A%2F%2Foutside.example%2Ffile.png&file=not-a-file",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertRedirects(response, reverse("brands:detail", args=[self.brand.pk]))
        self.assertEqual(2, BrandMaterial.objects.filter(brand=self.brand).count())

    def test_multipart_file_attempt_is_rejected_before_csrf_can_parse_it(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            self.url,
            {"file": SimpleUploadedFile("customer.png", b"not-an-image")},
        )
        self.assertEqual(response.status_code, 415)
        self.assertEqual(0, BrandMaterial.objects.filter(brand=self.brand).count())

    def test_oversized_or_unknown_body_is_rejected_before_the_view(self):
        self.client.force_login(self.owner)
        for body, content_type in (
            ("x=" + "x" * (8 * 1024), "application/x-www-form-urlencoded"),
            ("{}", "application/json"),
        ):
            with self.subTest(content_type=content_type):
                response = self.client.post(self.url, body, content_type=content_type)
                self.assertEqual(response.status_code, 415)
        self.assertEqual(0, BrandMaterial.objects.filter(brand=self.brand).count())

    def test_other_owner_is_hidden_and_brand_page_explains_closed_boundary(self):
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.post(
                self.url,
                "intent=prepare",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            404,
        )
        self.client.force_login(self.owner)
        page = self.client.get(reverse("brands:detail", args=[self.brand.pk]))
        self.assertContains(page, "Dosya yükleme, dış bağlantı, virüs tarama")
        self.assertContains(page, "Sentetik materyal kitini hazırla")
        self.client.post(
            self.url,
            "intent=prepare",
            content_type="application/x-www-form-urlencoded",
        )
        page = self.client.get(reverse("brands:detail", args=[self.brand.pk]))
        self.assertContains(page, "Yaparo sabit sentetik çizim")
        self.assertNotContains(page, "outside.example")
