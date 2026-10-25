"""Owned, saved-only ZIP export; no archive upload or extraction."""

import json
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4
from zipfile import ZipFile

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.assets.durable_rasters import create_palette_material

from .design_bundle import export_design_bundle
from .models import BrandCreativeDocument
from .test_creative_documents import DocumentFixture


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class DesignBundleTests(DocumentFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        self.document = self.create(palette_material_id=self.pair.version.material_id)

    def export(self, **changes):
        return export_design_bundle(
            **(
                dict(
                    owner=self.owner,
                    brand_id=self.brand.pk,
                    document_id=self.document.pk,
                )
                | changes
            )
        )

    def test_archive_has_exact_saved_scene_sources_and_verified_original_derivative(
        self,
    ):
        initial_history = self.document.history.count()
        data = self.export()
        self.assertEqual(data, self.export())
        with ZipFile(BytesIO(data)) as archive:
            self.assertEqual(
                set(archive.namelist()),
                {
                    "manifest.json",
                    "scene.json",
                    "README.txt",
                    "assets/hero-original.png",
                    "assets/hero-normalized.png",
                },
            )
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["package_version"], 1)
            self.assertEqual(manifest["document"]["revision"], 1)
            self.assertEqual(
                json.loads(archive.read("scene.json")), self.document.scene
            )
            self.assertEqual(
                archive.read("assets/hero-original.png"), bytes(self.pair.original)
            )
            self.assertEqual(
                archive.read("assets/hero-normalized.png"), bytes(self.pair.derivative)
            )
            for path, proof in manifest["files"].items():
                self.assertEqual(
                    proof,
                    dict(
                        size=len(archive.read(path)),
                        sha256=sha256(archive.read(path)).hexdigest(),
                    ),
                )
            self.assertEqual(
                {s["layer_id"] for s in manifest["sources"]}, {"hero", "logo"}
            )
            self.assertEqual(manifest["font"]["bundled"], False)
            self.assertNotIn(
                self.owner.username, archive.read("manifest.json").decode()
            )
        self.assertEqual(initial_history, self.document.history.count())

    def test_fixed_v2_bundle_has_metadata_without_inventing_binary_or_hash(self):
        document = self.create(request_id=uuid4())
        with ZipFile(BytesIO(self.export(document_id=document.pk))) as archive:
            self.assertEqual(len(archive.namelist()), 3)
            manifest = json.loads(archive.read("manifest.json"))
            for source in manifest["sources"]:
                self.assertEqual(source["kind"], "fixed_renderer_metadata")
                self.assertEqual(source["files"], {})
                self.assertIsNone(source["catalog"]["byte_size"])

    def test_package_limit_refuses_entire_export_without_changing_document(self):
        with patch(
            "growthtwin.modules.workspaces.design_bundle.MAX_PACKAGE_BYTES", 4096
        ):
            with self.assertRaises(ValidationError):
                self.export()
        self.assertEqual(self.read().revision, 1)

    def test_only_committed_revision_is_exported_and_failed_export_does_not_write(self):
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Kurgusal güncel başlık"
        self.save(scene)
        with ZipFile(BytesIO(self.export())) as archive:
            self.assertEqual(
                json.loads(archive.read("manifest.json"))["document"]["revision"], 2
            )
        with patch(
            "growthtwin.modules.workspaces.design_bundle.read_palette_material",
            side_effect=ValidationError("synthetic corruption"),
        ):
            with self.assertRaises(ValidationError):
                self.export()
        self.assertEqual(self.read().revision, 2)

    def test_legacy_sources_not_invented_and_flags_fail_closed(self):
        legacy = BrandCreativeDocument.objects.create(
            id=uuid4(),
            identity=self.document.identity,
            scene=self.document.scene
            | {
                "schema_version": 2,
                "layers": self.create(request_id=uuid4()).scene["layers"],
            },
        )
        with self.assertRaises(ValidationError):
            self.export(document_id=legacy.pk)
        with self.settings(DEBUG=False), self.assertRaises(PermissionDenied):
            self.export()
        with (
            self.settings(SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=False),
            self.assertRaises(PermissionDenied),
        ):
            self.export()

    def test_route_auth_scope_headers_and_read_only_method(self):
        url = reverse("brand_documents:bundle", args=[self.brand.pk, self.document.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.owner)
        result = self.client.get(url)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result["Content-Type"], "application/zip")
        self.assertIn("no-store", result["Cache-Control"])
        self.assertEqual(result["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.client.post(url).status_code, 405)
        with self.settings(DEBUG=False):
            self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.owner)
        self.brand.is_archived = True
        self.brand.save(update_fields=["is_archived"])
        self.assertEqual(self.client.get(url).status_code, 404)
