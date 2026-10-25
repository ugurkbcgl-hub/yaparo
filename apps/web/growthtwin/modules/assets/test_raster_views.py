"""Owner-only PNG serving and closed generation form boundary."""

from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner

from .models import MaterialRasterPair


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class RasterViewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="raster-view-owner")
        self.other = get_user_model().objects.create_user(username="raster-view-other")
        workspace = Workspace.objects.create(owner=self.owner, name="Raster view")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=workspace.pk, fixture="product"
        )
        self.generate_url = reverse("brands:palette_generate", args=[self.brand.pk])
        self.client.force_login(self.owner)

    def generate(self, client=None):
        return (client or self.client).post(
            self.generate_url,
            "intent=prepare",
            content_type="application/x-www-form-urlencoded",
        )

    def test_generate_display_and_private_png_decode(self):
        self.assertEqual(302, self.generate().status_code)
        pair = MaterialRasterPair.objects.get()
        page = self.client.get(reverse("brands:detail", args=[self.brand.pk]))
        self.assertContains(page, "Marka paleti · Sentetik görsel")
        url = reverse(
            "brands:palette_image", args=[self.brand.pk, pair.version.material_id]
        )
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual("image/png", response["Content-Type"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual("nosniff", response["X-Content-Type-Options"])
        with Image.open(BytesIO(response.content)) as image:
            image.load()
            self.assertEqual((320, 200), image.size)
            self.assertEqual((36, 76, 59, 255), image.getpixel((100, 100)))
        self.client.force_login(self.other)
        self.assertEqual(404, self.client.get(url).status_code)
        self.assertEqual(404, self.generate().status_code)

    def test_csrf_and_method_checks(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        self.assertEqual(403, self.generate(csrf_client).status_code)
        self.assertEqual(405, self.client.get(self.generate_url).status_code)
        self.assertEqual(0, MaterialRasterPair.objects.count())

    def test_multipart_rejected_before_upload_parser(self):
        with patch(
            "django.http.multipartparser.MultiPartParser.parse",
            side_effect=AssertionError,
        ):
            response = self.client.post(
                self.generate_url,
                {"file": SimpleUploadedFile("example.png", b"arbitrary")},
            )
        self.assertEqual(415, response.status_code)

    @override_settings(SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=False)
    def test_disabled_form_and_endpoint(self):
        self.assertEqual(404, self.generate().status_code)
        self.assertNotContains(
            self.client.get(reverse("brands:detail", args=[self.brand.pk])),
            "Örnek palet görselini hazırla",
        )
