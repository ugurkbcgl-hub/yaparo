"""Owner isolation and immutability for the metadata-only synthetic material kit."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from growthtwin.modules.assets.models import BrandMaterial, BrandMaterialVersion
from growthtwin.modules.assets.services import (
    list_materials,
    prepare_synthetic_materials,
)
from growthtwin.modules.assets.synthetic_catalog import (
    MAX_BYTES,
    SyntheticMaterialDefinition,
    definitions_for_fixture,
)
from growthtwin.modules.workspaces.models import Brand, Workspace
from growthtwin.modules.workspaces.services import (
    create_brand_for_owner,
    update_brand_identity_for_owner,
)


class SyntheticMaterialCatalogTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.owner = users.objects.create_user(username="material-owner")
        self.other = users.objects.create_user(username="material-other")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Materyal alanı"
        )
        self.other_workspace = Workspace.objects.create(
            owner=self.other, name="Başka materyal alanı"
        )
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="product"
        )

    def prepare(self):
        return prepare_synthetic_materials(owner=self.owner, brand_id=self.brand.pk)

    def test_prepare_creates_two_fixed_metadata_records_and_replays_idempotently(self):
        materials = list(self.prepare())
        self.assertEqual(2, len(materials))
        self.assertEqual(
            ["product:illustration:v1", "product:logo:v1"],
            [item.source_key for item in materials],
        )
        versions = [item.versions.get(version=1) for item in materials]
        self.assertEqual([1, 1], [item.current_version for item in materials])
        self.assertEqual(
            ["image/png", "image/png"], [item.media_type for item in versions]
        )
        self.assertTrue(all(len(item.catalog_digest) == 64 for item in versions))
        self.assertTrue(all(item.byte_size <= MAX_BYTES for item in versions))
        replay = list(self.prepare())
        self.assertEqual([item.pk for item in materials], [item.pk for item in replay])
        self.assertEqual(2, BrandMaterial.objects.count())
        self.assertEqual(2, BrandMaterialVersion.objects.count())

    def test_library_pins_identity_and_does_not_rebind_after_brand_changes(self):
        self.prepare()
        update_brand_identity_for_owner(
            owner=self.owner,
            brand_id=self.brand.pk,
            expected_version=1,
            primary_color="#254d9b",
            secondary_color="#eaf0ff",
            tone="energetic",
            tagline_key="daily_detail",
        )
        replay = list(self.prepare())
        self.assertEqual([1, 1], [item.identity.version for item in replay])
        self.brand.refresh_from_db()
        self.assertEqual(2, self.brand.current_version)

    def test_other_owner_anonymous_and_wrong_brand_cannot_read_or_prepare(self):
        other_brand = create_brand_for_owner(
            owner=self.other, workspace_id=self.other_workspace.pk, fixture="product"
        )
        self.prepare()
        with self.assertRaises(Brand.DoesNotExist):
            list(list_materials(owner=self.other, brand_id=self.brand.pk))
        with self.assertRaises(Brand.DoesNotExist):
            prepare_synthetic_materials(owner=self.other, brand_id=self.brand.pk)
        with self.assertRaises(Brand.DoesNotExist):
            list(list_materials(owner=self.owner, brand_id=other_brand.pk))
        with self.assertRaises(PermissionDenied):
            prepare_synthetic_materials(owner=None, brand_id=self.brand.pk)

    def test_records_and_versions_are_append_only(self):
        material = self.prepare()[0]
        version = material.versions.get(version=1)
        material.source_key = "product:logo:v1"
        with self.assertRaises(ValidationError):
            material.save()
        with self.assertRaises(ValidationError):
            BrandMaterial.objects.filter(pk=material.pk).update(current_version=2)
        version.display_name = "Başka ad"
        with self.assertRaises(ValidationError):
            version.save()
        with self.assertRaises(ValidationError):
            BrandMaterialVersion.objects.filter(pk=version.pk).delete()

    def test_definition_rejects_incomplete_or_oversized_catalog_values(self):
        original = definitions_for_fixture("product")
        oversized = SyntheticMaterialDefinition(
            **{**original[0].__dict__, "byte_size": MAX_BYTES + 1}
        )
        with patch(
            "growthtwin.modules.assets.synthetic_catalog._CATALOG",
            (oversized, original[1]),
        ):
            with self.assertRaises(ValueError):
                definitions_for_fixture("product")
        with self.assertRaises(ValueError):
            definitions_for_fixture("unknown")
