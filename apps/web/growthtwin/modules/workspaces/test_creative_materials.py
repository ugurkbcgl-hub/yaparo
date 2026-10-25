"""Pinned layer provenance and source retention for new synthetic documents."""

from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from growthtwin.modules.assets.models import BrandMaterial, BrandMaterialVersion
from growthtwin.modules.assets.services import prepare_synthetic_materials

from .creative_documents import restore_document
from .creative_materials import checked_materials
from .models import BrandCreativeDocument, CreativeMaterialBinding
from .test_brands import changed_identity
from .test_creative_documents import DocumentFixture


class CreativeMaterialTests(DocumentFixture, TestCase):
    def test_new_document_binds_two_fixed_sources_and_protects_parent_removal(self):
        document = self.create()
        self.assertEqual(document.material_binding_version, 1)
        self.assertEqual(
            {r["layer_id"] for r in checked_materials(document)}, {"hero", "logo"}
        )
        binding = document.material_bindings.first()
        with self.assertRaises(ProtectedError):
            binding.material_version.material.delete()
        self.assertEqual(document.material_bindings.count(), 2)
        self.assertEqual(BrandMaterialVersion.objects.count(), 2)

    def test_binding_failure_rolls_back_document_catalog_and_history(self):
        create = CreativeMaterialBinding.objects.create

        def fail_second(**kwargs):
            if kwargs["layer_id"] == "logo":
                raise ValidationError("synthetic failure")
            return create(**kwargs)

        with patch(
            "growthtwin.modules.workspaces.creative_materials.CreativeMaterialBinding.objects.create",
            side_effect=fail_second,
        ):
            with self.assertRaises(ValidationError):
                self.create()
        self.assertFalse(BrandCreativeDocument.objects.exists())
        self.assertFalse(BrandMaterial.objects.exists())
        self.assertFalse(CreativeMaterialBinding.objects.exists())

    def test_catalog_identity_does_not_rebind_after_brand_change(self):
        prepare_synthetic_materials(owner=self.owner, brand_id=self.brand.pk)
        changed_identity(self.owner, self.brand)
        document = self.create(expected_identity_version=2)
        self.assertEqual(document.identity.version, 2)
        self.assertEqual(
            {r["identity_version"] for r in checked_materials(document)}, {1}
        )

    def test_save_restore_and_create_replay_preserve_the_same_bindings(self):
        document = self.create()
        original = list(
            document.material_bindings.values_list("pk", "material_version_id")
        )
        scene = deepcopy(document.scene)
        scene["layers"][2]["text"] = "Kurgusal yeni başlık"
        self.save(scene)
        restored = restore_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            document_id=document.pk,
            expected_revision=2,
            target_revision=1,
        )
        self.assertEqual(restored.revision, 3)
        self.assertEqual(
            list(
                self.create().material_bindings.values_list("pk", "material_version_id")
            ),
            original,
        )

    def test_legacy_replay_and_save_do_not_invent_material_provenance(self):
        initial = self.create()
        legacy_id = uuid4()
        legacy = BrandCreativeDocument.objects.create(
            id=legacy_id, identity=initial.identity, scene=initial.scene
        )
        catalog_count = BrandMaterial.objects.count()
        self.create(request_id=legacy_id)
        scene = deepcopy(legacy.scene)
        scene["layers"][2]["text"] = "Eski tasarımın düzenlemesi"
        self.save(scene, document_id=legacy_id)
        legacy.refresh_from_db()
        self.assertEqual(checked_materials(legacy), [])
        self.assertEqual(legacy.material_binding_version, 0)
        self.assertEqual(BrandMaterial.objects.count(), catalog_count)

    def test_binding_mutation_and_foreign_brand_are_rejected(self):
        document = self.create()
        binding = document.material_bindings.first()
        for call in (
            lambda: binding.delete(),
            lambda: document.material_bindings.all().delete(),
            lambda: document.material_bindings.update(layer_id="logo"),
            lambda: binding.save(),
            lambda: BrandCreativeDocument.objects.filter(pk=document.pk).update(
                material_binding_version=0
            ),
        ):
            with self.assertRaises(ValidationError):
                call()
        materials = prepare_synthetic_materials(
            owner=self.other, brand_id=self.foreign.pk
        )
        binding.material_version = materials[0].versions.get(version=1)
        with self.assertRaises(ValidationError):
            binding.clean()

    def test_missing_or_corrupt_binding_denies_read_save_and_replay(self):
        document = self.create()
        # Deliberately bypass the application API to simulate corrupted storage.
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM workspaces_creativematerialbinding WHERE id = %s",
                [document.material_bindings.first().pk],
            )
        for call in (self.read, self.create, lambda: self.save(document.scene)):
            with self.assertRaises(ValidationError):
                call()

    def test_fixed_catalog_corruption_aborts_new_document(self):
        prepare_synthetic_materials(owner=self.owner, brand_id=self.brand.pk)
        with patch(
            "growthtwin.modules.workspaces.creative_materials.definitions_for_fixture",
            return_value=(),
        ):
            with self.assertRaises(ValidationError):
                self.create()
        self.assertFalse(BrandCreativeDocument.objects.exists())
