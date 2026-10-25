"""Pinned local choice, explicit ownership, stale input and concurrent writers."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
from threading import Barrier, Event
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.db.models.deletion import ProtectedError
from django.test import (
    TestCase,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.utils import timezone

from growthtwin.modules.workspaces.creative_documents import save_document
from growthtwin.modules.workspaces.models import Brand, BrandCreativeDocument, Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner
from growthtwin.modules.workspaces.test_creative_documents import DocumentFixture

from .design_selection import current_design, design_options, select_design
from .models import (
    CampaignDesignChoice,
    GoogleDraftApproval,
    GoogleDraftDispatch,
    WorkspaceCampaignDraft,
)
from .services import create_campaign_draft_for_owner, update_campaign_draft_for_owner
from .views import SYNTHETIC_CAMPAIGN


class SelectionFixture(DocumentFixture):
    def setUp(self):
        super().setUp()
        self.document = self.create()
        today = timezone.localdate()
        self.draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **SYNTHETIC_CAMPAIGN,
            flight_start=today + timedelta(days=1),
            flight_end=today + timedelta(days=15),
        )
        self.selection_request = uuid4()

    def select(self, **changes):
        return select_design(
            **(
                dict(
                    owner=self.owner,
                    draft_id=self.draft.pk,
                    brand_id=self.brand.pk,
                    document_id=self.document.pk,
                    expected_document_revision=1,
                    expected_selection_version=0,
                    request_id=self.selection_request,
                )
                | changes
            )
        )


@override_settings(DEBUG=True, SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True)
class DesignSelectionTests(SelectionFixture, TestCase):
    def test_old_drafts_read_without_implicit_selection_and_fields_do_not_change(self):
        before = WorkspaceCampaignDraft.objects.values().get(pk=self.draft.pk)
        self.assertIsNone(current_design(owner=self.owner, draft_id=self.draft.pk))
        self.assertEqual(
            [r.pk for r in design_options(owner=self.owner, draft_id=self.draft.pk)],
            [self.document.pk],
        )
        self.assertFalse(CampaignDesignChoice.objects.exists())
        choice = self.select()
        self.assertEqual(choice.snapshot_id, self.document.history.get(revision=1).pk)
        self.assertEqual(
            before, WorkspaceCampaignDraft.objects.values().get(pk=self.draft.pk)
        )
        self.assertFalse(GoogleDraftApproval.objects.exists())
        self.assertFalse(GoogleDraftDispatch.objects.exists())

    def test_new_edits_keep_selected_snapshot_and_old_request_cannot_reset_later_choice(
        self,
    ):
        first = self.select()
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Yeni kurgusal kayıt"
        save_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            document_id=self.document.pk,
            expected_revision=1,
            scene=scene,
        )
        selected = current_design(owner=self.owner, draft_id=self.draft.pk)
        self.assertEqual(selected.snapshot.revision, 1)
        self.assertNotEqual(selected.snapshot.scene, scene)
        second = self.select(
            expected_document_revision=2,
            expected_selection_version=1,
            request_id=uuid4(),
        )
        self.assertEqual(second.version, 2)
        self.assertEqual(self.select().pk, first.pk)
        self.assertEqual(self.draft.design_choices.first().pk, second.pk)
        self.assertEqual(self.draft.design_choices.count(), 2)

    def test_stale_document_or_choice_rejects_without_overwrite(self):
        self.select()
        with self.assertRaises(ValidationError):
            self.select(request_id=uuid4())
        scene = deepcopy(self.document.scene)
        scene["layers"][0]["x"] = 180
        self.save(scene)
        with self.assertRaises(ValidationError):
            self.select(request_id=uuid4(), expected_selection_version=1)
        self.assertEqual(self.draft.design_choices.count(), 1)

    def test_other_owner_and_other_workspace_cannot_select(self):
        with self.assertRaises(WorkspaceCampaignDraft.DoesNotExist):
            self.select(owner=self.other)
        workspace = Workspace.objects.create(
            owner=self.owner, name="Other owned workspace"
        )
        brand = create_brand_for_owner(
            owner=self.owner, workspace_id=workspace.pk, fixture="product"
        )
        document = self.create(brand_id=brand.pk, request_id=uuid4())
        with self.assertRaises(BrandCreativeDocument.DoesNotExist):
            self.select(brand_id=brand.pk, document_id=document.pk)
        self.assertFalse(CampaignDesignChoice.objects.exists())

    def test_disabled_archived_and_inactive_scopes_deny(self):
        with self.settings(DEBUG=False), self.assertRaises(PermissionDenied):
            self.select()
        with (
            self.settings(SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=False),
            self.assertRaises(PermissionDenied),
        ):
            self.select()
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        with self.assertRaises(Brand.DoesNotExist):
            self.select()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(WorkspaceCampaignDraft.DoesNotExist):
            self.select()

    def test_choice_and_snapshot_are_immutable_and_deletion_protects_source(self):
        choice = self.select()
        for call in (
            lambda: choice.save(),
            lambda: choice.delete(),
            lambda: self.draft.design_choices.update(version=2),
            lambda: self.draft.design_choices.all().delete(),
        ):
            with self.assertRaises(ValidationError):
                call()
        with self.assertRaises(ProtectedError):
            self.document.delete()
        self.assertEqual(self.document.history.count(), 1)

    def test_current_unavailable_does_not_fall_back_to_older_history(self):
        self.select()
        other_doc = self.create(brand_id=self.service.pk, request_id=uuid4())
        self.select(
            brand_id=self.service.pk,
            document_id=other_doc.pk,
            expected_selection_version=1,
            request_id=uuid4(),
        )
        Brand.objects.filter(pk=self.service.pk).update(is_archived=True)
        with self.assertRaises(CampaignDesignChoice.DoesNotExist):
            current_design(owner=self.owner, draft_id=self.draft.pk)
        self.assertEqual(self.draft.design_choices.count(), 2)

    def test_write_boundary_rechecks_revision_and_failure_rolls_back(self):
        original = CampaignDesignChoice.objects.bulk_create

        def edit_before_insert(rows, *args, **kwargs):
            scene = deepcopy(self.document.scene)
            scene["layers"][2]["text"] = "Kurgusal yarış"
            self.save(scene)
            return original(rows, *args, **kwargs)

        with patch.object(
            CampaignDesignChoice.objects, "bulk_create", side_effect=edit_before_insert
        ):
            with self.assertRaises(ValidationError):
                self.select()
        self.assertFalse(CampaignDesignChoice.objects.exists())
        with patch.object(
            CampaignDesignChoice.objects,
            "bulk_create",
            side_effect=IntegrityError("synthetic failure"),
        ):
            with self.assertRaises(ValidationError):
                self.select()
        self.assertFalse(CampaignDesignChoice.objects.exists())

    def test_exact_request_collision_other_draft_refuses(self):
        self.select()
        second = WorkspaceCampaignDraft.objects.get(pk=self.draft.pk)
        second.pk = None
        second.save()
        with self.assertRaises(ValidationError):
            self.select(draft_id=second.pk)

    def test_write_boundary_rechecks_archiving_and_owner_revocation(self):
        original = CampaignDesignChoice.objects.bulk_create

        def archived():
            Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)

        def inactive():
            get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)

        def transferred():
            Workspace.objects.filter(pk=self.workspace.pk).update(owner=self.other)

        for mutation in (archived, inactive, transferred):

            def change_before_insert(rows, *args, **kwargs):
                mutation()
                return original(rows, *args, **kwargs)

            with patch.object(
                CampaignDesignChoice.objects,
                "bulk_create",
                side_effect=change_before_insert,
            ):
                with self.assertRaises(ValidationError):
                    self.select()
            self.assertFalse(CampaignDesignChoice.objects.exists())

    def test_campaign_removal_only_removes_its_local_choice(self):
        self.select()
        self.draft.delete()
        self.assertFalse(CampaignDesignChoice.objects.exists())
        self.assertTrue(
            BrandCreativeDocument.objects.filter(pk=self.document.pk).exists()
        )


@override_settings(DEBUG=True, SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True)
@skipUnlessDBFeature("has_select_for_update")
class DesignSelectionConcurrencyTests(SelectionFixture, TransactionTestCase):
    def together(self, operation):
        barrier = Barrier(2)

        def call(i):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return operation(i)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call, i) for i in range(2)]
            return [future.result(timeout=20) for future in futures]

    def test_same_request_once(self):
        result = self.together(lambda i: self.select().pk)
        self.assertEqual(result[0], result[1])
        self.assertEqual(CampaignDesignChoice.objects.count(), 1)

    def test_competing_choices_one_winner(self):
        def choose(i):
            try:
                return self.select(request_id=uuid4()).version
            except ValidationError:
                return "stale"

        self.assertCountEqual(self.together(choose), [1, "stale"])

    def test_concurrent_document_edit_commits_and_choice_fails_at_insert(self):
        pending = Event()
        edited = Event()
        original = CampaignDesignChoice.objects.bulk_create

        def before(rows, *args, **kwargs):
            pending.set()
            if not edited.wait(10):
                raise RuntimeError("Editor did not finish")
            return original(rows, *args, **kwargs)

        def select():
            close_old_connections()
            try:
                with patch.object(
                    CampaignDesignChoice.objects, "bulk_create", side_effect=before
                ):
                    try:
                        self.select()
                        return "accepted"
                    except ValidationError:
                        return "stale"
            finally:
                close_old_connections()

        def edit():
            close_old_connections()
            try:
                if not pending.wait(10):
                    raise RuntimeError("Choice did not reach insert")
                scene = deepcopy(self.document.scene)
                scene["layers"][0]["x"] = 180
                self.save(scene)
                edited.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(select)
            b = pool.submit(edit)
            self.assertEqual(a.result(timeout=20), "stale")
            b.result(timeout=20)
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 2)
        self.assertFalse(CampaignDesignChoice.objects.exists())

    def test_legacy_campaign_edit_and_selection_do_not_add_workspace_locks(self):
        locked = Event()
        started = Event()
        locks = []

        def legacy():
            close_old_connections()
            try:
                with transaction.atomic():
                    WorkspaceCampaignDraft.objects.select_for_update(of=("self",)).get(
                        pk=self.draft.pk
                    )
                    locked.set()
                    if not started.wait(10):
                        raise RuntimeError("Choice did not start")
                    update_campaign_draft_for_owner(
                        owner=self.owner,
                        draft_id=self.draft.pk,
                        media_budget_minor=500000,
                        flight_start=self.draft.flight_start,
                        flight_end=self.draft.flight_end,
                    )
            finally:
                close_old_connections()

        def choose():
            close_old_connections()

            def track(execute, sql, params, many, context):
                if "FOR UPDATE" in sql:
                    locks.append(sql)
                return execute(sql, params, many, context)

            try:
                if not locked.wait(10):
                    raise RuntimeError("Legacy edit did not lock")
                started.set()
                with connection.execute_wrapper(track):
                    return self.select().pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(legacy)
            b = pool.submit(choose)
            a.result(timeout=20)
            self.assertIsNotNone(b.result(timeout=20))
        self.assertEqual(len(locks), 1)
        self.assertIn('OF "campaigns_workspacecampaigndraft"', locks[0])
