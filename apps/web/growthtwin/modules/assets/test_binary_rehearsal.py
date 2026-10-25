"""Actual private temporary storage and scoped generated-byte rehearsal."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase, override_settings

from growthtwin.modules.workspaces.models import Brand, Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner

from .binary_rehearsal import rehearse_generated_materials
from .models import BrandMaterial
from .private_fixture_store import PrivateFixtureStore


class BinaryRehearsalTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="binary-owner")
        self.other = get_user_model().objects.create_user(username="binary-other")
        workspace = Workspace.objects.create(owner=self.owner, name="Binary fixture")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=workspace.pk, fixture="product"
        )

    def run_rehearsal(self, owner=None):
        return rehearse_generated_materials(
            owner=owner or self.owner, brand_id=self.brand.pk
        )

    def test_default_closed_before_storage_creation(self):
        with patch(
            "growthtwin.modules.assets.binary_rehearsal.PrivateFixtureStore",
            side_effect=AssertionError,
        ):
            with self.assertRaises(PermissionDenied):
                self.run_rehearsal()

    @override_settings(SYNTHETIC_MATERIAL_BINARY_REHEARSAL_ENABLED=True, DEBUG=True)
    def test_actual_generated_files_readback_cleanup_and_no_durable_rows(self):
        result = self.run_rehearsal()
        self.assertTrue(result.cleanup_verified)
        self.assertEqual(1, result.identity_version)
        self.assertEqual(3, len(result.evidence))
        self.assertEqual(
            {"image/jpeg", "image/png", "image/webp"},
            {row.source_media_type for row in result.evidence},
        )
        self.assertTrue(
            all(
                row.structure_verified and row.source_bytes > 0
                for row in result.evidence
            )
        )
        self.assertEqual(0, BrandMaterial.objects.count())

    @override_settings(SYNTHETIC_MATERIAL_BINARY_REHEARSAL_ENABLED=True, DEBUG=True)
    def test_foreign_owner_and_archived_brand_denied_before_files(self):
        with patch(
            "growthtwin.modules.assets.binary_rehearsal.PrivateFixtureStore",
            side_effect=AssertionError,
        ):
            with self.assertRaises(Brand.DoesNotExist):
                self.run_rehearsal(self.other)
            self.brand.is_archived = True
            self.brand.save(update_fields=["is_archived"])
            with self.assertRaises(Brand.DoesNotExist):
                self.run_rehearsal()

    def test_private_store_removes_original_and_derivative_on_failure(self):
        root = None
        with self.assertRaisesMessage(RuntimeError, "simulated parser failure"):
            with PrivateFixtureStore() as storage:
                root = storage._root
                storage.put(b"original")
                storage.put(b"derivative")
                raise RuntimeError("simulated parser failure")
        self.assertFalse(root.exists())

    def test_store_bound_and_unknown_key(self):
        with PrivateFixtureStore() as storage:
            with self.assertRaises(ValueError):
                storage.put(b"x" * (8 * 1024 * 1024 + 1))
            with self.assertRaises(KeyError):
                storage.read("../outside")
            for _ in range(6):
                key = storage.put(b"synthetic")
                self.assertEqual(b"synthetic", storage.read(key))
            with self.assertRaises(ValueError):
                storage.put(b"extra")
