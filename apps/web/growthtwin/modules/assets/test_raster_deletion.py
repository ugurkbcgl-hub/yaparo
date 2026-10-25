"""Scoped synthetic sample removal, rollback and replay boundaries."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from growthtwin.modules.workspaces.models import Brand, Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner

from .durable_rasters import (
    create_palette_material,
    delete_palette_material,
    read_palette_material,
)
from .models import BrandMaterial, BrandMaterialVersion, MaterialRasterPair
from .services import prepare_synthetic_materials


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class RasterDeletionTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="delete-raster-owner"
        )
        self.other = get_user_model().objects.create_user(
            username="delete-raster-other"
        )
        workspace = Workspace.objects.create(owner=self.owner, name="Removal fixture")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=workspace.pk, fixture="product"
        )
        self.pair = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        self.material_id = self.pair.version.material_id

    def delete(self, **kwargs):
        values = {
            "owner": self.owner,
            "brand_id": self.brand.pk,
            "material_id": self.material_id,
        }
        values.update(kwargs)
        return delete_palette_material(**values)

    def test_removes_both_bytes_version_and_material_preserving_kit_and_brand(self):
        prepare_synthetic_materials(owner=self.owner, brand_id=self.brand.pk)
        self.assertTrue(self.delete())
        self.assertFalse(MaterialRasterPair.objects.exists())
        self.assertEqual(2, BrandMaterialVersion.objects.count())
        self.assertEqual(2, BrandMaterial.objects.count())
        self.assertEqual(1, Brand.objects.count())
        with self.assertRaises(MaterialRasterPair.DoesNotExist):
            read_palette_material(
                owner=self.owner, brand_id=self.brand.pk, material_id=self.material_id
            )

    def test_replay_cannot_delete_a_new_sample(self):
        self.assertTrue(self.delete())
        self.assertFalse(self.delete())
        replacement = create_palette_material(owner=self.owner, brand_id=self.brand.pk)
        self.assertNotEqual(self.material_id, replacement.version.material_id)
        self.assertFalse(self.delete())
        self.assertEqual(1, MaterialRasterPair.objects.count())

    def test_other_owner_and_wrong_brand_cannot_delete(self):
        with self.assertRaises(Brand.DoesNotExist):
            self.delete(owner=self.other)
        sibling = create_brand_for_owner(
            owner=self.owner, workspace_id=self.brand.workspace_id, fixture="service"
        )
        self.assertFalse(self.delete(brand_id=sibling.pk))
        self.assertEqual(1, MaterialRasterPair.objects.count())

    def test_failed_cascade_rolls_back_all_rows(self):
        from django.db.models.signals import post_delete

        def fail_after_pair_removal(**kwargs):
            raise ValidationError("simulated cascade failure")

        post_delete.connect(
            fail_after_pair_removal, sender=MaterialRasterPair, weak=False
        )
        try:
            with self.assertRaises(ValidationError):
                self.delete()
        finally:
            post_delete.disconnect(fail_after_pair_removal, sender=MaterialRasterPair)
        self.assertTrue(MaterialRasterPair.objects.filter(pk=self.pair.pk).exists())
        self.assertTrue(
            BrandMaterialVersion.objects.filter(pk=self.pair.version_id).exists()
        )
        self.assertTrue(BrandMaterial.objects.filter(pk=self.material_id).exists())

    def test_unverified_bytes_are_not_silently_removed(self):
        with patch(
            "growthtwin.modules.assets.durable_rasters._checked",
            side_effect=ValidationError("corrupt sample"),
        ):
            with self.assertRaises(ValidationError):
                self.delete()
        self.assertTrue(MaterialRasterPair.objects.exists())
