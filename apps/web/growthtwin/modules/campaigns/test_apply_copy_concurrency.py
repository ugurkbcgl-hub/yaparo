"""Actual PostgreSQL races; skipped by local SQLite, required in CI."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier, Event
from unittest.mock import patch
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature

from growthtwin.modules.workspaces.creative_documents import save_document

from .services import update_campaign_draft_for_owner
from .test_apply_brand_copy import ApplyFixture


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED=True,
    SYNTHETIC_BRAND_COPY_APPLY_ENABLED=True,
)
@skipUnlessDBFeature("has_select_for_update")
class ApplyConcurrencyTests(ApplyFixture, TransactionTestCase):
    def together(self, operations):
        barrier = Barrier(2)

        def call(operation):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    operation()
                    return "saved"
                except ValidationError:
                    return "stale"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call, operation) for operation in operations]
            return [future.result(timeout=20) for future in futures]

    def test_competing_application_creates_one_revision(self):
        self.assertCountEqual(
            self.together((self.apply, self.apply)), ["saved", "stale"]
        )
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 2)
        self.assertEqual(self.document.history.count(), 2)

    def test_editor_and_application_revision_race_has_one_winner(self):
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Concurrent editor"

        def edit():
            save_document(
                owner=self.owner,
                brand_id=self.brand.pk,
                document_id=self.document.pk,
                expected_revision=1,
                scene=scene,
            )

        self.assertCountEqual(self.together((self.apply, edit)), ["saved", "stale"])
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 2)

    def test_committed_reselection_before_update_refuses_and_rolls_back(self):
        from growthtwin.modules.campaigns import apply_brand_copy as service

        pending = Event()
        selected = Event()
        original = service._write_document

        def before(*args, **kwargs):
            pending.set()
            if not selected.wait(10):
                raise RuntimeError("Selection did not commit")
            return original(*args, **kwargs)

        def apply():
            close_old_connections()
            try:
                with patch.object(service, "_write_document", new=before):
                    try:
                        self.apply()
                        return "saved"
                    except ValidationError:
                        return "stale"
            finally:
                close_old_connections()

        def select():
            close_old_connections()
            try:
                if not pending.wait(10):
                    raise RuntimeError("Apply did not reach write")
                self.select(expected_selection_version=1, request_id=uuid4())
                selected.set()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(apply)
            b = pool.submit(select)
            self.assertEqual(a.result(timeout=20), "stale")
            b.result(timeout=20)
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 1)
        self.assertEqual(self.document.history.count(), 1)
        self.assertEqual(self.draft.design_choices.count(), 2)

    def test_legacy_campaign_edit_does_not_deadlock_with_apply(self):
        from growthtwin.modules.campaigns import apply_brand_copy as service

        locked = Event()
        legacy_started = Event()
        original = service._write_document
        locks = []

        def before(*args, **kwargs):
            locked.set()
            if not legacy_started.wait(10):
                raise RuntimeError("Legacy edit did not start")
            return original(*args, **kwargs)

        def apply():
            close_old_connections()

            def track(execute, sql, params, many, context):
                if "FOR UPDATE" in sql:
                    locks.append(sql)
                return execute(sql, params, many, context)

            try:
                with (
                    patch.object(service, "_write_document", new=before),
                    connection.execute_wrapper(track),
                ):
                    return self.apply().revision
            finally:
                close_old_connections()

        def legacy():
            close_old_connections()
            try:
                if not locked.wait(10):
                    raise RuntimeError("Apply did not lock")
                with transaction.atomic():
                    self.draft.__class__.objects.select_for_update(of=("self",)).get(
                        pk=self.draft.pk
                    )
                    legacy_started.set()
                    update_campaign_draft_for_owner(
                        owner=self.owner,
                        draft_id=self.draft.pk,
                        media_budget_minor=500000,
                        flight_start=self.draft.flight_start,
                        flight_end=self.draft.flight_end,
                    )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(apply)
            b = pool.submit(legacy)
            self.assertEqual(a.result(timeout=20), 2)
            b.result(timeout=20)
        self.assertTrue(locks)
        self.assertFalse(
            any("campaigns_workspacecampaigndraft" in sql for sql in locks)
        )
