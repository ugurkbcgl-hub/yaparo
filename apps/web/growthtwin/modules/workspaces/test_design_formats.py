"""Immutable new-design formats with legacy scene compatibility."""

import json
from copy import deepcopy
from io import BytesIO
from uuid import uuid4
from zipfile import ZipFile

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.assets.durable_rasters import create_palette_material

from .creative_documents import restore_document
from .creative_scenes import SceneValidationError, validate_scene
from .design_bundle import export_design_bundle
from .models import BrandCreativeDocument
from .test_creative_documents import DocumentFixture


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class DesignFormatTests(DocumentFixture, TestCase):
    def test_new_formats_and_both_source_types_pin_dimensions(self):
        pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        for format_name, height in (("square", 800), ("portrait", 1000)):
            for material_id in (None, pair.version.material_id):
                doc = self.create(
                    request_id=uuid4(),
                    design_format=format_name,
                    palette_material_id=material_id,
                )
                self.assertEqual(
                    (
                        doc.scene["schema_version"],
                        doc.scene["width"],
                        doc.scene["height"],
                    ),
                    (4, 800, height),
                )
                self.assertEqual(
                    doc.scene["hero_source"],
                    "palette" if material_id else "illustration",
                )
                self.assertEqual(doc.material_bindings.count(), 2)
                self.read(document_id=doc.pk)

    def test_omitted_format_keeps_legacy_square_creation_contract(self):
        self.assertEqual(self.create().scene["schema_version"], 2)

    def test_invalid_format_is_rejected_without_new_document(self):
        for value in ("landscape", "", [], True, 4):
            with self.assertRaises(ValidationError):
                self.create(design_format=value)
        self.assertFalse(BrandCreativeDocument.objects.exists())

    def test_same_request_cannot_change_format_or_revert_to_implicit_legacy(self):
        doc = self.create(design_format="portrait")
        self.assertEqual(self.create(design_format="portrait").pk, doc.pk)
        for value in ("square", None):
            with self.assertRaises(ValidationError):
                self.create(design_format=value)

    def test_save_restore_and_bundle_preserve_format_and_source(self):
        pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        doc = self.create(
            design_format="portrait", palette_material_id=pair.version.material_id
        )
        scene = deepcopy(doc.scene)
        scene["layers"][2]["y"] = 880
        self.save(scene)
        with ZipFile(
            BytesIO(
                export_design_bundle(
                    owner=self.owner, brand_id=self.brand.pk, document_id=doc.pk
                )
            )
        ) as archive:
            self.assertEqual(json.loads(archive.read("scene.json"))["height"], 1000)
            self.assertEqual(
                json.loads(archive.read("manifest.json"))["renderer_contract"],
                "yaparo-scene-v1-v4",
            )
            self.assertEqual(
                archive.read("assets/hero-normalized.png"), bytes(pair.derivative)
            )
        restored = restore_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            document_id=doc.pk,
            expected_revision=2,
            target_revision=1,
        )
        self.assertEqual(restored.scene, doc.scene)
        swapped = deepcopy(restored.scene)
        swapped.update(format="square", height=800)
        with self.assertRaises(ValidationError):
            self.save(swapped, expected_revision=3)
        swapped = deepcopy(restored.scene)
        swapped["hero_source"] = "illustration"
        swapped["layers"][0]["asset"] = "product:illustration:v1"
        with self.assertRaises(ValidationError):
            self.save(swapped, expected_revision=3)

    def test_strict_v4_shape_dimensions_source_and_y_bounds(self):
        doc = self.create(design_format="portrait")
        for changes in (
            {"height": 800},
            {"height": 1000.0},
            {"width": True},
            {"format": []},
            {"hero_source": "url"},
            {"extra": 1},
        ):
            with self.assertRaises(SceneValidationError):
                validate_scene(doc.scene | changes, fixture="product")
        for key in ("format", "hero_source"):
            scene = deepcopy(doc.scene)
            del scene[key]
            with self.assertRaises(SceneValidationError):
                validate_scene(scene, fixture="product")
        for value in (900,):
            scene = deepcopy(doc.scene)
            scene["layers"][0]["y"] = value
            validate_scene(scene, fixture="product")
        scene["layers"][0]["y"] = 901
        with self.assertRaises(SceneValidationError):
            validate_scene(scene, fixture="product")

    def test_http_explicit_choice_and_invalid_choice(self):
        self.client.force_login(self.owner)
        url = reverse("brand_documents:create", args=[self.brand.pk])
        data = dict(
            brand_id=self.brand.pk,
            expected_identity_version=1,
            request_id=str(self.request_id),
            design_format="portrait",
        )
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.assertEqual(self.read().scene["format"], "portrait")
        self.assertEqual(
            self.client.post(
                url, data | {"request_id": str(uuid4()), "design_format": "arbitrary"}
            ).status_code,
            409,
        )
