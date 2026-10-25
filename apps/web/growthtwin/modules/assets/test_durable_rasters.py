"""Atomic binary persistence, tenant isolation and pinned source provenance."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import close_old_connections
from django.test import (
    TestCase,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)

from growthtwin.modules.workspaces.models import Brand, Workspace
from growthtwin.modules.workspaces.services import (
    create_brand_for_owner,
    update_brand_identity_for_owner,
)

from .durable_rasters import create_palette_material, read_palette_material
from .models import BrandMaterial, BrandMaterialVersion, MaterialRasterPair
from .services import prepare_synthetic_materials


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
class DurableRasterTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="raster-owner")
        self.other = get_user_model().objects.create_user(username="raster-other")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Raster fixture"
        )
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="product"
        )

    def create(self):
        return create_palette_material(owner=self.owner, brand_id=self.brand.pk)

    def test_persistence_readback_replay_and_catalog_coexist(self):
        pair = self.create()
        reopened = read_palette_material(
            owner=self.owner,
            brand_id=self.brand.pk,
            material_id=pair.version.material_id,
        )
        self.assertEqual(bytes(pair.original), bytes(reopened.original))
        self.assertEqual(bytes(pair.derivative), bytes(reopened.derivative))
        self.assertEqual(pair.original_size, pair.version.byte_size)
        self.assertEqual(pair.pk, self.create().pk)
        self.assertEqual(
            3,
            len(prepare_synthetic_materials(owner=self.owner, brand_id=self.brand.pk)),
        )
        self.assertEqual(1, MaterialRasterPair.objects.count())

    def test_later_brand_edit_preserves_old_palette_identity_and_bytes(self):
        pair = self.create()
        update_brand_identity_for_owner(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_version=1,
            primary_color="#9a3f2d",
            secondary_color="#eeeeee",
            tone="calm",
            tagline_key="daily_detail",
        )
        replay = self.create()
        self.assertEqual(1, replay.version.material.identity.version)
        self.assertEqual(bytes(pair.derivative), bytes(replay.derivative))

    def test_foreign_owner_wrong_brand_and_archived_brand_hidden(self):
        pair = self.create()
        with self.assertRaises(Brand.DoesNotExist):
            create_palette_material(owner=self.other, brand_id=self.brand.pk)
        sibling = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="service"
        )
        with self.assertRaises(MaterialRasterPair.DoesNotExist):
            read_palette_material(
                owner=self.owner,
                brand_id=sibling.pk,
                material_id=pair.version.material_id,
            )
        self.brand.is_archived = True
        self.brand.save(update_fields=["is_archived"])
        with self.assertRaises(Brand.DoesNotExist):
            self.create()

    def test_pair_failure_rolls_back_material_and_version(self):
        with patch.object(
            MaterialRasterPair.objects,
            "create",
            side_effect=ValidationError("synthetic failure"),
        ):
            with self.assertRaises(ValidationError):
                self.create()
        self.assertEqual(0, BrandMaterial.objects.count())
        self.assertEqual(0, BrandMaterialVersion.objects.count())

    def test_owner_change_between_brand_and_binary_query_refuses_bytes(self):
        pair = self.create()
        from .durable_rasters import _brand

        def changed_owner(*args, **kwargs):
            brand = _brand(*args, **kwargs)
            Workspace.objects.filter(pk=self.workspace.pk).update(owner=self.other)
            return brand

        with patch(
            "growthtwin.modules.assets.durable_rasters._brand",
            side_effect=changed_owner,
        ):
            with self.assertRaises(MaterialRasterPair.DoesNotExist):
                read_palette_material(
                    owner=self.owner,
                    brand_id=self.brand.pk,
                    material_id=pair.version.material_id,
                )

    def test_immutable_pair_and_corruption_refusal(self):
        pair = self.create()
        with self.assertRaises(ValidationError):
            pair.save()
        with self.assertRaises(ValidationError):
            MaterialRasterPair.objects.filter(pk=pair.pk).update(original=b"changed")
        pair.original = b"changed"
        with self.assertRaises(ValidationError):
            pair.clean()

    @override_settings(SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=False)
    def test_default_off_before_generation(self):
        with self.assertRaises(PermissionDenied):
            self.create()


@override_settings(DEBUG=True, SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED=True)
@skipUnlessDBFeature("has_select_for_update")
class DurableRasterRaceTests(TransactionTestCase):
    def test_competing_preparation_creates_one_pair(self):
        owner = get_user_model().objects.create_user(username="raster-race")
        workspace = Workspace.objects.create(owner=owner, name="Race")
        brand = create_brand_for_owner(
            owner=owner, workspace_id=workspace.pk, fixture="product"
        )
        barrier = Barrier(2)

        def call():
            close_old_connections()
            try:
                user = get_user_model().objects.get(pk=owner.pk)
                barrier.wait(timeout=10)
                return create_palette_material(owner=user, brand_id=brand.pk).pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call) for _ in range(2)]
            results = [future.result(timeout=20) for future in futures]
        self.assertEqual(results[0], results[1])
        self.assertEqual(1, MaterialRasterPair.objects.count())
