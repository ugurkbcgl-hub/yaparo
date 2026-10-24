"""Identity styling compatibility and durable owned revision history."""

from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase

from . import test_creative_documents
from .creative_documents import document_history, restore_document
from .creative_scenes import (
    SceneValidationError,
    seed_scene,
    validate_scene,
)
from .models import BrandCreativeDocument, BrandCreativeRevision
from .test_brands import changed_identity


class CreativeHistoryTests(test_creative_documents.DocumentFixture, TestCase):
    def restore(self, **changes):
        return restore_document(
            **(
                dict(
                    owner=self.owner,
                    brand_id=self.brand.pk,
                    document_id=self.request_id,
                    expected_revision=2,
                    target_revision=1,
                )
                | changes
            )
        )

    def changed(self):
        document = self.create()
        scene = deepcopy(document.scene)
        scene["layers"][2]["text"] = "Yeni örnek"
        return document, self.save(scene)

    def test_palette_is_snapshot_and_brand_changes_only_affect_new_documents(self):
        document = self.create()
        self.assertEqual(2, document.scene["schema_version"])
        self.assertEqual("#f5eddf", document.scene["style"]["background_color"])
        self.assertEqual("#244c3b", document.scene["style"]["logo_color"])
        changed_identity(
            self.owner, self.brand, primary_color="#ffffff", secondary_color="#111111"
        )
        new = self.create(request_id=uuid4(), expected_identity_version=2)
        self.assertEqual("#111111", new.scene["style"]["background_color"])
        self.assertEqual("#000000", new.scene["style"]["logo_icon_color"])
        self.assertEqual(document.scene, self.read().scene)

    def test_same_brand_colors_seed_readable_text_without_losing_accent(self):
        changed_identity(
            self.owner, self.brand, primary_color="#ffffff", secondary_color="#ffffff"
        )
        document = self.create(expected_identity_version=2)
        self.assertEqual("#ffffff", document.scene["style"]["logo_color"])
        self.assertEqual("#000000", document.scene["style"]["wordmark_color"])
        self.assertEqual("#000000", document.scene["layers"][2]["color"])

    def test_save_restore_and_replay_preserve_every_committed_snapshot(self):
        original, changed = self.changed()
        self.assertEqual(
            [2, 1], list(changed.history.values_list("revision", flat=True))
        )
        restored = self.restore()
        self.assertEqual(3, restored.revision)
        self.assertEqual(original.scene, restored.scene)
        row = restored.history.get(revision=3)
        self.assertEqual("restore", row.reason)
        self.assertEqual(1, row.restored_from)
        self.assertEqual(self.owner.pk, row.created_by_id)
        with self.assertRaises(ValidationError):
            self.restore()
        self.assertEqual(changed.scene, restored.history.get(revision=2).scene)
        self.assertEqual(3, restored.history.count())

    def test_noop_does_not_create_history_and_restore_same_scene_is_noop(self):
        original = self.create()
        self.save(original.scene)
        self.assertEqual(1, original.history.count())
        restored = self.restore(expected_revision=1)
        self.assertEqual(1, restored.revision)
        self.assertEqual(1, original.history.count())

    def test_legacy_current_state_is_recorded_lazily_without_rewriting_scene(self):
        identity = self.brand.current_identity
        scene = seed_scene(
            fixture="product",
            tagline_text=identity.tagline_text,
            primary_color=identity.primary_color,
            logo_key=identity.logo_key,
        )
        BrandCreativeDocument.objects.create(
            id=self.request_id, identity=identity, scene=scene, revision=7
        )
        before = self.read()
        rows = document_history(
            owner=self.owner, brand_id=self.brand.pk, document_id=self.request_id
        )
        self.assertEqual(7, rows[0]["revision"])
        self.assertEqual(0, before.history.count())
        changed = deepcopy(scene)
        changed["layers"][2]["text"] = "Eski biçim düzenlemesi"
        saved = self.save(changed, expected_revision=7)
        self.assertEqual(1, saved.scene["schema_version"])
        self.assertEqual(scene, saved.history.get(revision=7).scene)
        self.assertEqual("baseline", saved.history.get(revision=7).reason)

    def test_schema_switch_is_refused_and_v2_style_is_strict(self):
        document = self.create()
        old = deepcopy(document.scene)
        old.pop("style")
        old["schema_version"] = 1
        with self.assertRaises(ValidationError):
            self.save(old)
        for key, value in (
            ("background_color", "url(https://invalid.test)"),
            ("font_family", "RemoteFont"),
            ("logo_color", ["#ffffff"]),
        ):
            scene = deepcopy(document.scene)
            scene["style"][key] = value
            with self.assertRaises(SceneValidationError):
                validate_scene(scene, fixture="product")
        self.assertEqual(document.scene, self.read().scene)

    def test_foreign_and_wrong_brand_cannot_restore_or_read_history(self):
        self.changed()
        for changes in (dict(owner=self.other), dict(brand_id=self.service.pk)):
            with self.assertRaises(ObjectDoesNotExist) as caught:
                self.restore(**changes)
            self.assertIn(type(caught.exception).__name__, ("DoesNotExist",))
        with self.assertRaises(ObjectDoesNotExist):
            document_history(
                owner=self.other, brand_id=self.brand.pk, document_id=self.request_id
            )
        self.assertEqual(2, self.read().revision)

    def test_history_application_api_is_append_only(self):
        document = self.create()
        row = document.history.get()
        with self.assertRaises(ValidationError):
            row.save()
        with self.assertRaises(ValidationError):
            row.delete()
        with self.assertRaises(ValidationError):
            document.history.update(scene={})
        with self.assertRaises(ValidationError):
            document.history.all().delete()
        with self.assertRaises(ValidationError):
            BrandCreativeRevision.objects.bulk_update([row], ["scene"])

    def test_snapshot_failure_rolls_back_document_pointer_and_scene(self):
        document = self.create()
        scene = deepcopy(document.scene)
        scene["layers"][2]["x"] = 99
        with patch.object(
            BrandCreativeRevision.objects,
            "create",
            side_effect=ValidationError("synthetic"),
        ):
            with self.assertRaises(ValidationError):
                self.save(scene)
        self.assertEqual(1, self.read().revision)
        self.assertEqual(document.scene, self.read().scene)
        self.assertEqual(1, document.history.count())

    def test_corrupted_history_cannot_be_silently_replaced(self):
        document = self.create()
        # Corrupting stored scene simulates an unsupported direct database write.
        altered = deepcopy(document.scene)
        altered["layers"][2]["x"] = 99
        BrandCreativeDocument.objects.filter(pk=document.pk).update(scene=altered)
        with self.assertRaises(ValidationError):
            document_history(
                owner=self.owner, brand_id=self.brand.pk, document_id=self.request_id
            )
        changed = deepcopy(altered)
        changed["layers"][2]["x"] = 100
        with self.assertRaises(ValidationError):
            self.save(changed)
        self.assertEqual(1, self.read().revision)
