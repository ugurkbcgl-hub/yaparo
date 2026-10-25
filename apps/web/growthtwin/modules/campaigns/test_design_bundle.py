"""Selected archive uses immutable scene, exact sources and current scope."""

import json
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4
from zipfile import ZipFile

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.assets.durable_rasters import create_palette_material
from growthtwin.modules.workspaces.design_bundle import export_design_bundle
from growthtwin.modules.workspaces.models import Brand, Workspace

from .design_bundle import export_selected_bundle
from .test_design_selection import SelectionFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True,
)
class CampaignBundleTests(SelectionFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.choice = self.select()
        self.url = reverse("campaigns:design_bundle", args=[self.draft.pk, 1])
        self.client.force_login(self.owner)

    def export(self):
        return export_selected_bundle(
            owner=self.owner, draft_id=self.draft.pk, selection_version=1
        )

    def test_exact_selected_revision_after_edit_is_deterministic_and_separate_from_live_zip(
        self,
    ):
        before = self.export()
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Sonradan değişti"
        self.save(scene)
        self.assertEqual(self.export(), before)
        with ZipFile(BytesIO(before)) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(
                json.loads(archive.read("scene.json")), self.document.scene
            )
            self.assertEqual(manifest["document"]["revision"], 1)
            self.assertEqual(
                manifest["campaign_selection"],
                dict(
                    campaign_id=self.draft.pk,
                    selection_id=self.choice.pk,
                    selection_version=1,
                    snapshot_id=self.choice.snapshot_id,
                    document_revision=1,
                    brand_id=self.brand.pk,
                ),
            )
            self.assertEqual(
                set(archive.namelist()), {"scene.json", "manifest.json", "README.txt"}
            )
            for name, entry in manifest["files"].items():
                self.assertEqual(
                    entry,
                    dict(
                        size=len(archive.read(name)),
                        sha256=sha256(archive.read(name)).hexdigest(),
                    ),
                )
            self.assertNotIn(
                self.owner.username, archive.read("manifest.json").decode()
            )
        live = export_design_bundle(
            owner=self.owner, brand_id=self.brand.pk, document_id=self.document.pk
        )
        with ZipFile(BytesIO(live)) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["document"]["revision"], 2)
            self.assertNotIn("campaign_selection", manifest)
            self.assertEqual(json.loads(archive.read("scene.json")), scene)
        self.assertEqual(self.document.history.count(), 2)
        self.assertEqual(self.draft.design_choices.count(), 1)

    def test_palette_original_derivative_and_selected_portrait_are_exact(self):
        pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        document = self.create(
            request_id=uuid4(),
            palette_material_id=pair.version.material_id,
            design_format="portrait",
        )
        self.select(
            document_id=document.pk, expected_selection_version=1, request_id=uuid4()
        )
        data = export_selected_bundle(
            owner=self.owner, draft_id=self.draft.pk, selection_version=2
        )
        with ZipFile(BytesIO(data)) as archive:
            scene = json.loads(archive.read("scene.json"))
            self.assertEqual((scene["width"], scene["height"]), (800, 1000))
            self.assertEqual(
                archive.read("assets/hero-original.png"), bytes(pair.original)
            )
            self.assertEqual(
                archive.read("assets/hero-normalized.png"), bytes(pair.derivative)
            )
            manifest = json.loads(archive.read("manifest.json"))
            for name, entry in manifest["files"].items():
                self.assertEqual(
                    entry,
                    dict(
                        size=len(archive.read(name)),
                        sha256=sha256(archive.read(name)).hexdigest(),
                    ),
                )
        with self.assertRaises(ValidationError):
            self.export()

    def test_selection_change_or_archival_during_collection_refuses(self):
        from growthtwin.modules.campaigns import design_bundle

        original = design_bundle._build_bundle

        def changed(**kwargs):
            result = original(**kwargs)
            self.select(expected_selection_version=1, request_id=uuid4())
            return result

        with patch.object(design_bundle, "_build_bundle", side_effect=changed):
            with self.assertRaises(ValidationError):
                self.export()

    def test_http_scope_flags_methods_and_private_download(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn(
            'attachment; filename="yaparo-campaign-', response["Content-Disposition"]
        )
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(Client().get(self.url).status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.client.force_login(self.owner)
        for options in (
            {"DEBUG": False},
            {"SYNTHETIC_CAMPAIGN_DESIGN_ENABLED": False},
            {"SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED": False},
        ):
            with self.settings(**options):
                self.assertEqual(self.client.get(self.url).status_code, 404)
        other = Workspace.objects.create(owner=self.owner, name="Other owned workspace")
        Brand.objects.filter(pk=self.brand.pk).update(workspace=other)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        for url in (self.url, self.url.replace("/1/", "/01/")):
            with patch.object(
                HttpRequest,
                "_load_post_and_files",
                side_effect=AssertionError("no intake"),
            ):
                response = self.client.post(url, {"file": "synthetic"})
            self.assertEqual(response.status_code, 405)
            self.assertIn("no-store", response["Cache-Control"])

    def test_workspace_transfer_during_collection_returns_no_archive(self):
        from growthtwin.modules.campaigns import design_bundle

        original = design_bundle._build_bundle

        def transferred(**kwargs):
            result = original(**kwargs)
            Workspace.objects.filter(pk=self.workspace.pk).update(owner=self.other)
            return result

        with patch.object(design_bundle, "_build_bundle", side_effect=transferred):
            with self.assertRaises(ObjectDoesNotExist):
                self.export()
