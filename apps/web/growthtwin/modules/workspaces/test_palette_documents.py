"""Explicit owned palette selection, immutable rendering version and private load."""

from copy import deepcopy
from uuid import uuid4

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.assets.durable_rasters import (
    create_palette_material,
    delete_palette_material,
)
from growthtwin.modules.assets.models import MaterialRasterPair

from .creative_documents import restore_document
from .creative_materials import checked_materials
from .models import BrandCreativeDocument
from .test_brands import changed_identity
from .test_creative_documents import DocumentFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True,
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    },
)
class PaletteDocumentTests(DocumentFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        self.material_id = self.pair.version.material_id

    def palette(self, **changes):
        return self.create(palette_material_id=self.material_id, **changes)

    def test_explicit_selection_binds_actual_pair_and_blocks_removal(self):
        document = self.palette()
        self.assertEqual(document.scene["schema_version"], 3)
        self.assertEqual(document.scene["layers"][0]["asset"], "product:palette:v1")
        self.assertEqual(
            document.material_bindings.get(layer_id="hero").material_version_id,
            self.pair.version_id,
        )
        self.assertTrue(
            next(r for r in checked_materials(document) if r["layer_id"] == "hero")[
                "is_raster"
            ]
        )
        with self.assertRaises(ProtectedError):
            delete_palette_material(
                owner=self.owner, brand_id=self.brand.pk, material_id=self.material_id
            )
        self.assertTrue(MaterialRasterPair.objects.filter(pk=self.pair.pk).exists())

    def test_ordinary_creation_still_uses_v2_illustration(self):
        document = self.create()
        self.assertEqual(document.scene["schema_version"], 2)
        self.assertEqual(
            document.scene["layers"][0]["asset"], "product:illustration:v1"
        )

    def test_service_brand_can_use_its_own_palette(self):
        pair = create_palette_material(owner=self.owner, brand_id=self.service.pk)
        document = self.create(
            brand_id=self.service.pk, palette_material_id=pair.version.material_id
        )
        self.assertEqual(document.scene["layers"][0]["asset"], "service:palette:v1")
        checked_materials(document)

    def test_palette_identity_remains_old_while_new_document_uses_current_style(self):
        changed_identity(self.owner, self.brand)
        document = self.palette(expected_identity_version=2)
        self.assertEqual(document.identity.version, 2)
        self.assertEqual(
            document.material_bindings.get(
                layer_id="hero"
            ).material_version.material.identity.version,
            1,
        )
        self.assertEqual(document.scene["style"]["background_color"], "#eeeeee")

    def test_replay_requires_exact_source_and_cannot_switch_existing_document(self):
        document = self.palette()
        self.assertEqual(self.palette().pk, document.pk)
        with self.assertRaises(ValidationError):
            self.create()
        fixed = self.create(request_id=uuid4())
        with self.assertRaises(ValidationError):
            self.palette(request_id=fixed.pk)

    def test_foreign_and_missing_palette_ids_never_create_a_document(self):
        foreign_pair = create_palette_material(
            owner=self.other, brand_id=self.foreign.pk
        )
        for material_id in (foreign_pair.version.material_id, uuid4()):
            with self.assertRaises(MaterialRasterPair.DoesNotExist):
                self.create(palette_material_id=material_id)
        self.assertFalse(BrandCreativeDocument.objects.exists())

    def test_disabled_flags_and_corrupt_bytes_deny_creation(self):
        for config in (
            {"DEBUG": False},
            {"SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED": False},
        ):
            with self.settings(**config), self.assertRaises(PermissionDenied):
                self.palette()
        from unittest.mock import patch

        with patch(
            "growthtwin.modules.assets.durable_rasters._checked",
            side_effect=ValidationError("synthetic invalid"),
        ):
            with self.assertRaises(ValidationError):
                self.palette()
        self.assertFalse(BrandCreativeDocument.objects.exists())

    def test_save_restore_keeps_same_raster_and_schema_changes_deny(self):
        document = self.palette()
        scene = deepcopy(document.scene)
        scene["layers"][0]["x"] = 180
        self.save(scene)
        restored = restore_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            document_id=document.pk,
            expected_revision=2,
            target_revision=1,
        )
        self.assertEqual(restored.scene, document.scene)
        downgrade = deepcopy(restored.scene)
        downgrade["schema_version"] = 2
        downgrade["layers"][0]["asset"] = "product:illustration:v1"
        foreign_source = deepcopy(restored.scene)
        foreign_source["layers"][0]["asset"] = "service:palette:v1"
        for candidate in (downgrade, foreign_source):
            with self.assertRaises(ValidationError):
                self.save(candidate, expected_revision=3)

    def test_private_bootstrap_uses_only_bound_owner_route(self):
        document = self.palette()
        self.client.force_login(self.owner)
        url = reverse("brand_documents:editor", args=[self.brand.pk, document.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("brands:palette_image", args=[self.brand.pk, self.material_id]),
        )
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_http_explicit_selection_creates_v3_and_duplicate_keeps_it(self):
        self.client.force_login(self.owner)
        url = reverse("brand_documents:create", args=[self.brand.pk])
        data = dict(
            brand_id=self.brand.pk,
            expected_identity_version=1,
            request_id=str(self.request_id),
            palette_material_id=str(self.material_id),
        )
        for _ in range(2):
            self.assertEqual(self.client.post(url, data).status_code, 302)
        self.assertEqual(self.read().scene["schema_version"], 3)

    def test_v3_cannot_claim_legacy_unbound_provenance(self):
        document = self.palette()
        unbound = BrandCreativeDocument.objects.create(
            id=uuid4(), identity=document.identity, scene=document.scene
        )
        with self.assertRaises(ValidationError):
            self.read(document_id=unbound.pk)
