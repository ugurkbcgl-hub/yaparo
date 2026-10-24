"""Owned saved synthetic documents retain immutable brand identity provenance."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from unittest.mock import patch
from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, close_old_connections, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature

from .creative_documents import create_document, read_document, save_document
from .models import Brand, BrandCreativeDocument, BrandIdentity, Workspace
from .services import create_brand_for_owner
from .test_brands import changed_identity


class DocumentFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="document-owner")
        self.other = get_user_model().objects.create_user(username="document-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Örnek")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="product"
        )
        self.service = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="service"
        )
        other_workspace = Workspace.objects.create(owner=self.other, name="Başka")
        self.foreign = create_brand_for_owner(
            owner=self.other, workspace_id=other_workspace.pk, fixture="product"
        )
        self.request_id = uuid4()

    def create(self, **changes):
        return create_document(
            **(
                dict(
                    owner=self.owner,
                    brand_id=self.brand.pk,
                    expected_identity_version=1,
                    request_id=self.request_id,
                )
                | changes
            )
        )

    def read(self, **changes):
        return read_document(
            **(
                dict(
                    owner=self.owner,
                    brand_id=self.brand.pk,
                    document_id=self.request_id,
                )
                | changes
            )
        )

    def save(self, scene, **changes):
        return save_document(
            **(
                dict(
                    owner=self.owner,
                    brand_id=self.brand.pk,
                    document_id=self.request_id,
                    expected_revision=1,
                    scene=scene,
                )
                | changes
            )
        )


class CreativeDocumentTests(DocumentFixture, TestCase):
    def test_creation_pins_identity_literals_and_has_no_campaign_binding(self):
        document = self.create()
        identity = self.brand.current_identity
        self.assertEqual(document.pk, self.request_id)
        self.assertEqual(document.identity_id, identity.pk)
        self.assertEqual(document.revision, 1)
        self.assertEqual(document.scene["fixture"], "product")
        self.assertEqual(document.scene["layers"][2]["text"], identity.tagline_text)
        self.assertEqual(document.scene["layers"][2]["color"], identity.primary_color)
        self.assertEqual(document.scene["layers"][1]["asset"], identity.logo_key)
        self.assertIsNotNone(document.created_at)
        self.assertIsNotNone(document.updated_at)
        self.assertEqual(document.identity.brand.workspace.owner_id, self.owner.pk)
        self.assertFalse(hasattr(document, "campaign_id"))

    def test_same_request_reuses_latest_saved_scene_without_reset(self):
        initial = self.create()
        scene = deepcopy(initial.scene)
        scene["layers"][2]["text"] = "Kurgusal düzenleme"
        saved = self.save(scene)
        repeated = self.create()
        self.assertEqual(saved.pk, repeated.pk)
        self.assertEqual(saved.scene, repeated.scene)
        self.assertEqual(saved.revision, repeated.revision)
        self.assertEqual(saved.updated_at, repeated.updated_at)
        self.assertEqual(1, BrandCreativeDocument.objects.count())

    def test_request_collision_across_same_owner_brands_never_reassigns_document(self):
        original = self.create()
        with self.assertRaises(ValidationError):
            self.create(brand_id=self.service.pk)
        original.refresh_from_db()
        self.assertEqual(original.identity.brand_id, self.brand.pk)
        self.assertEqual(original.scene["fixture"], "product")

    def test_foreign_owner_cannot_create_read_or_save_document(self):
        document = self.create()
        for call in (
            lambda: self.create(owner=self.other),
            lambda: self.read(owner=self.other),
            lambda: self.save(document.scene, owner=self.other),
            lambda: self.create(brand_id=self.foreign.pk),
        ):
            with self.assertRaises(Brand.DoesNotExist):
                call()
        with self.assertRaises(ValidationError):
            self.create(owner=self.other, brand_id=self.foreign.pk)
        self.assertEqual(1, BrandCreativeDocument.objects.count())

    def test_same_owner_wrong_brand_cannot_read_or_save_document(self):
        document = self.create()
        for call in (
            lambda: self.read(brand_id=self.service.pk),
            lambda: self.save(document.scene, brand_id=self.service.pk),
        ):
            with self.assertRaises(BrandCreativeDocument.DoesNotExist):
                call()

    def test_same_fixture_different_owned_workspace_is_not_document_scope(self):
        document = self.create()
        workspace = Workspace.objects.create(owner=self.owner, name="İkinci")
        second = create_brand_for_owner(
            owner=self.owner, workspace_id=workspace.pk, fixture="product"
        )
        with self.assertRaises(BrandCreativeDocument.DoesNotExist):
            self.read(brand_id=second.pk)
        with self.assertRaises(ValidationError):
            self.create(brand_id=second.pk)
        self.assertEqual(document.identity.brand_id, self.brand.pk)

    def test_anonymous_and_inactive_owner_are_rejected_before_writes(self):
        document = self.create()
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        for owner in (AnonymousUser(), self.owner):
            for call in (
                lambda: self.create(owner=owner),
                lambda: self.read(owner=owner),
                lambda: self.save(document.scene, owner=owner),
            ):
                with self.assertRaises(PermissionDenied):
                    call()
        self.assertEqual(1, BrandCreativeDocument.objects.count())

    def test_database_owner_deactivation_denies_stale_authenticated_object(self):
        document = self.create()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        for call in (
            self.create,
            self.read,
            lambda: self.save(document.scene),
        ):
            with self.assertRaises(Brand.DoesNotExist):
                call()

    def test_archive_denies_create_replay_read_save_but_preserves_document(self):
        document = self.create()
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        for call in (self.create, self.read, lambda: self.save(document.scene)):
            with self.assertRaises(Brand.DoesNotExist):
                call()
        self.assertEqual(1, BrandCreativeDocument.objects.count())

    def test_identity_edit_does_not_change_old_document_and_old_work_can_save(self):
        old = self.create()
        old_scene = deepcopy(old.scene)
        changed_identity(self.owner, self.brand, tagline_key="daily_detail")
        replay = self.create()
        self.assertEqual(replay.identity_id, old.identity_id)
        self.assertEqual(self.read().scene, old_scene)
        with self.assertRaises(ValidationError) as stale:
            self.create(request_id=uuid4())
        self.assertEqual(stale.exception.code, "stale_brand_version")
        new = self.create(request_id=uuid4(), expected_identity_version=2)
        self.assertNotEqual(old.identity_id, new.identity_id)
        self.assertNotEqual(
            old.scene["layers"][2]["text"], new.scene["layers"][2]["text"]
        )
        edit = deepcopy(old.scene)
        edit["layers"][2]["x"] = 77
        saved = self.save(edit)
        self.assertEqual(saved.identity_id, old.identity_id)
        self.assertEqual(saved.revision, 2)
        with self.assertRaises(ValidationError):
            self.create(expected_identity_version=2)

    def test_save_increments_revision_while_noop_preserves_timestamp(self):
        document = self.create()
        repeated = self.save(document.scene)
        self.assertEqual(repeated.revision, 1)
        self.assertEqual(repeated.updated_at, document.updated_at)
        scene = deepcopy(document.scene)
        scene["layers"][0]["x"] = 121
        saved = self.save(scene)
        self.assertEqual(saved.revision, 2)
        scene["layers"][0]["x"] = 122
        self.assertEqual(self.read().scene["layers"][0]["x"], 121)
        self.assertEqual(self.read().identity_id, document.identity_id)

    def test_stale_save_is_denied_even_when_scene_matches_current(self):
        document = self.create()
        scene = deepcopy(document.scene)
        scene["layers"][0]["x"] = 121
        saved = self.save(scene)
        with self.assertRaises(ValidationError) as stale:
            self.save(saved.scene)
        self.assertEqual(stale.exception.code, "stale_document_revision")
        self.assertEqual(self.read().revision, 2)

    def test_malformed_scene_cross_fixture_and_external_assets_leave_original(self):
        document = self.create()
        invalid = [None, {}, document.scene | {"fixture": "service"}]
        altered = deepcopy(document.scene)
        altered["layers"][0]["asset"] = "https://invalid.test/asset.svg"
        invalid.append(altered)
        for scene in invalid:
            with self.assertRaises(ValidationError):
                self.save(scene)
        self.assertEqual(self.read().scene, document.scene)
        self.assertEqual(self.read().revision, 1)

    def test_invalid_uuid_and_versions_rejected_without_new_documents(self):
        for request_id in (None, str(uuid4()), UUID(int=0), 1):
            with self.assertRaises(ValidationError):
                self.create(request_id=request_id)
        for version in (None, 0, True, "1", 2**31):
            with self.assertRaises(ValidationError):
                self.create(expected_identity_version=version)
        self.assertEqual(0, BrandCreativeDocument.objects.count())
        document = self.create()
        for version in (None, 0, True, "1", 2**31):
            with self.assertRaises(ValidationError):
                self.save(document.scene, expected_revision=version)

    def test_unknown_document_and_corrupt_scene_fail_closed(self):
        with self.assertRaises(BrandCreativeDocument.DoesNotExist):
            self.read()
        document = self.create()
        BrandCreativeDocument.objects.filter(pk=document.pk).update(scene={})
        with self.assertRaises(ValidationError):
            self.read()
        with self.assertRaises(ValidationError):
            self.create()

    def test_identity_relation_cannot_be_reassigned_by_application_model_api(self):
        document = self.create()
        alternate = self.service.current_identity
        document.identity = alternate
        with self.assertRaises(ValidationError):
            document.save()
        with self.assertRaises(ValidationError):
            BrandCreativeDocument.objects.filter(pk=document.pk).update(
                identity=alternate
            )
        with self.assertRaises(ValidationError):
            BrandCreativeDocument.objects.bulk_update([document], fields=["identity"])
        self.assertEqual(self.read().identity.brand_id, self.brand.pk)

    def test_document_protects_original_identity_and_brand_from_deletion(self):
        self.create()
        with self.assertRaises(ProtectedError):
            Brand.objects.filter(pk=self.brand.pk).delete()
        self.assertEqual(3, BrandIdentity.objects.count())

    def test_revision_database_constraint_and_exhaustion(self):
        document = self.create()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    BrandCreativeDocument.objects.filter(pk=document.pk).update(
                        revision=0
                    )
        BrandCreativeDocument.objects.filter(pk=document.pk).update(revision=2**31 - 1)
        self.assertEqual(
            self.save(document.scene, expected_revision=2**31 - 1).revision, 2**31 - 1
        )
        changed = deepcopy(document.scene)
        changed["layers"][0]["x"] = 99
        with self.assertRaises(ValidationError):
            self.save(changed, expected_revision=2**31 - 1)

    def test_failed_create_rolls_back_without_touching_identity(self):
        identity_count = BrandIdentity.objects.count()
        with patch.object(
            BrandCreativeDocument.objects,
            "create",
            side_effect=IntegrityError("Fabricated collision"),
        ):
            with self.assertRaises(ValidationError):
                self.create()
        self.assertEqual(0, BrandCreativeDocument.objects.count())
        self.assertEqual(identity_count, BrandIdentity.objects.count())


@skipUnlessDBFeature("has_select_for_update")
class CreativeDocumentConcurrencyTests(DocumentFixture, TransactionTestCase):
    def together(self, operation):
        barrier = Barrier(2)

        def call():
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                barrier.wait(timeout=10)
                return operation(owner)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call) for _ in range(2)]
            return [future.result(timeout=20) for future in futures]

    def test_competing_replays_create_only_one_document(self):
        result = self.together(lambda owner: self.create(owner=owner).pk)
        self.assertEqual(result[0], result[1])
        self.assertEqual(1, BrandCreativeDocument.objects.count())

    def test_competing_saves_have_one_winner_and_one_stale_revision(self):
        initial = self.create()
        scene = deepcopy(initial.scene)
        scene["layers"][0]["x"] = 99

        def save(owner):
            try:
                return self.save(scene, owner=owner).revision
            except ValidationError as error:
                return error.code

        self.assertCountEqual([2, "stale_document_revision"], self.together(save))
        self.assertEqual(self.read().revision, 2)

    def test_competing_restores_append_once_and_preserve_later_snapshot(self):
        from .creative_documents import restore_document

        initial = self.create()
        scene = deepcopy(initial.scene)
        scene["layers"][0]["x"] = 99
        self.save(scene)

        def restore(owner):
            try:
                return restore_document(
                    owner=owner,
                    brand_id=self.brand.pk,
                    document_id=self.request_id,
                    expected_revision=2,
                    target_revision=1,
                ).revision
            except ValidationError as error:
                return error.code

        self.assertCountEqual([3, "stale_document_revision"], self.together(restore))
        document = self.read()
        self.assertEqual(initial.scene, document.scene)
        self.assertEqual(
            [3, 2, 1], list(document.history.values_list("revision", flat=True))
        )
        self.assertEqual(scene, document.history.get(revision=2).scene)
