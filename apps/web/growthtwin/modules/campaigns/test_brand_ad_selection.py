"""Brand campaign planning preserves source history and forbids external work."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from unittest import mock
from urllib.parse import urlencode
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import close_old_connections, transaction
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from growthtwin.modules.workspaces.models import Brand, Workspace
from growthtwin.modules.workspaces.test_brand_ad_drafts import BrandAdFixture

from . import brand_ad_selection as service
from .models import CampaignBrandAdChoice, WorkspaceCampaignDraft


class BrandCampaignFixture(BrandAdFixture):
    def setUp(self):
        super().setUp()
        gate = override_settings(LOCAL_BRAND_CAMPAIGN_ENABLED=True)
        gate.enable()
        self.addCleanup(gate.disable)
        self.ad_record = self.ad()
        self.create_request = uuid4()

    def begin(self, **changes):
        return service.start(
            **(
                {
                    "owner": self.owner,
                    "brand_id": self.brand.pk,
                    "ad_id": self.ad_record.pk,
                    "revision": 1,
                    "source": self.ad_record.source_fingerprint,
                    "request_id": self.create_request,
                }
                | changes
            )
        )

    def choose(self, choice, **changes):
        return service.select(
            **(
                {
                    "owner": self.owner,
                    "campaign_id": choice.campaign_id,
                    "ad_id": self.ad_record.pk,
                    "revision": self.ad_record.revision,
                    "source": self.ad_record.source_fingerprint,
                    "expected_version": choice.version,
                    "request_id": uuid4(),
                }
                | changes
            )
        )


class BrandCampaignTests(BrandCampaignFixture, TransactionTestCase):
    def test_start_replay_legacy_null_and_selected_revision_stays_pinned(self):
        legacy = WorkspaceCampaignDraft.objects.create(
            workspace=self.workspace,
            name="Eski örnek",
            brief="Sentetik",
            target_city="Ankara",
            media_budget_minor=500000,
        )
        choice = self.begin()
        self.assertIsNone(WorkspaceCampaignDraft.objects.get(pk=legacy.pk).brand_id)
        self.assertEqual(choice.campaign.brand_id, self.brand.pk)
        self.assertEqual(self.begin().pk, choice.pk)
        self.ad_record = self.edit_ad(self.ad_record)
        _, data, _ = service.selected(
            owner=self.owner, campaign_id=choice.campaign_id, version=1
        )
        self.assertEqual(data["content"]["cta"], "Keşfet")
        new = self.choose(choice)
        self.assertEqual(new.version, 2)
        self.assertEqual(self.begin().pk, choice.pk)
        self.assertEqual(WorkspaceCampaignDraft.objects.count(), 2)
        with self.assertRaises(ValidationError):
            service.selected(
                owner=self.owner, campaign_id=choice.campaign_id, version=1
            )
        self.assertEqual(
            service.selected(owner=self.owner, campaign_id=choice.campaign_id)[1][
                "content"
            ]["cta"],
            "İncele",
        )
        with self.assertRaises(ValidationError):
            CampaignBrandAdChoice.objects.update(snapshot={})

    def test_stale_source_revision_collision_and_wrong_brand_owner_refuse(self):
        for overrides in (
            {"source": "0" * 64},
            {"revision": 2},
            {"brand_id": self.service.pk},
            {"owner": self.other},
        ):
            with self.assertRaises((ValidationError, ObjectDoesNotExist)):
                self.begin(**overrides)
        self.assertFalse(WorkspaceCampaignDraft.objects.exists())
        first = self.begin()
        second = self.begin(request_id=uuid4())
        with self.assertRaises(ValidationError):
            self.choose(second, request_id=first.request_id)
        self.assertEqual(CampaignBrandAdChoice.objects.count(), 2)
        with self.assertRaises(ObjectDoesNotExist):
            service.selected(owner=self.other, campaign_id=first.campaign_id)
        with override_settings(LOCAL_BRAND_CAMPAIGN_ENABLED=False):
            with self.assertRaises(PermissionDenied):
                self.begin()

    def test_corrupt_snapshot_archive_and_foreign_workspace_refuse(self):
        choice = self.begin()
        # Corrupt via raw SQL solely to rehearse the read boundary; ORM denies it.
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE campaigns_campaignbrandadchoice SET snapshot=%s WHERE id=%s",
                ["{}", choice.pk],
            )
        with self.assertRaises(ValidationError):
            service.selected(owner=self.owner, campaign_id=choice.campaign_id)

        with connection.cursor() as cursor:
            import json

            cursor.execute(
                "UPDATE campaigns_campaignbrandadchoice SET snapshot=%s WHERE id=%s",
                [json.dumps(choice.snapshot), choice.pk],
            )
        other = Workspace.objects.create(owner=self.owner, name="Ayrı alan")
        WorkspaceCampaignDraft.objects.filter(pk=choice.campaign_id).update(
            workspace=other
        )
        with self.assertRaises(ValidationError):
            service.selected(owner=self.owner, campaign_id=choice.campaign_id)

        WorkspaceCampaignDraft.objects.filter(pk=choice.campaign_id).update(
            workspace=self.workspace
        )
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        with self.assertRaises(ObjectDoesNotExist):
            service.selected(owner=self.owner, campaign_id=choice.campaign_id)

    def test_http_confirmation_private_csrf_and_no_preview_export(self):
        self.client.force_login(self.owner)
        start = reverse(
            "brands:brand_ad_campaign_start", args=[self.brand.pk, self.ad_record.pk]
        )
        data = {
            "revision": 1,
            "source": self.ad_record.source_fingerprint,
            "request_id": self.create_request,
        }
        self.assertEqual(self.client.get(start).status_code, 405)
        self.assertEqual(
            self.client.post(
                start, urlencode(data), content_type="application/x-www-form-urlencoded"
            ).status_code,
            409,
        )
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.owner)
        self.assertEqual(
            csrf.post(
                start, urlencode(data), content_type="application/x-www-form-urlencoded"
            ).status_code,
            403,
        )
        response = self.client.post(
            start,
            urlencode({**data, "synthetic_confirmation": "on"}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        choice = CampaignBrandAdChoice.objects.get()
        image = reverse("campaigns:brand_ad_image", args=[choice.campaign_id, 1])
        self.assertIn("no-store", self.client.get(image)["Cache-Control"])
        self.assertEqual(self.client.post(image, {}).status_code, 405)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(image).status_code, 404)

    @skipUnlessDBFeature("has_select_for_update")
    def test_two_starts_same_request_create_one_campaign(self):
        barrier = Barrier(2)

        def run():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return self.begin().pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            values = [
                f.result(timeout=20) for f in [pool.submit(run), pool.submit(run)]
            ]
        self.assertEqual(values[0], values[1])
        self.assertEqual(WorkspaceCampaignDraft.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_two_selections_accept_one_expected_version(self):
        choice = self.begin()
        barrier = Barrier(2)

        def run():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    self.choose(choice)
                    return True
                except ValidationError:
                    return False
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            values = [
                f.result(timeout=20) for f in [pool.submit(run), pool.submit(run)]
            ]
        self.assertEqual(sorted(values), [False, True])

    @skipUnlessDBFeature("has_select_for_update")
    def test_selection_racing_edit_keeps_one_complete_saved_revision(self):
        choice = self.begin()
        barrier = Barrier(2)

        def edit():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                self.edit_ad(self.ad_record)
            finally:
                close_old_connections()

        def select():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    return self.choose(choice).pk
                except ValidationError:
                    return None
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            a, b = pool.submit(edit), pool.submit(select)
            a.result(timeout=20)
            b.result(timeout=20)
        selected, data, _ = service.selected(
            owner=self.owner, campaign_id=choice.campaign_id
        )
        self.assertEqual(data["content"], selected.revision.content)
        self.assertEqual(data["ad_revision"], selected.revision.revision)

    @skipUnlessDBFeature("has_select_for_update")
    def test_creation_replay_never_inverts_existing_campaign_workspace_lock(self):
        choice = self.begin()
        campaign_held, brand_held = Event(), Event()
        original = service._snapshot

        def marked(*args):
            brand_held.set()
            return original(*args)

        def legacy():
            close_old_connections()
            try:
                with transaction.atomic():
                    WorkspaceCampaignDraft.objects.select_for_update(of=("self",)).get(
                        pk=choice.campaign_id
                    )
                    campaign_held.set()
                    if not brand_held.wait(timeout=10):
                        raise AssertionError("Replay never acquired brand")
                    Workspace.objects.select_for_update().get(pk=self.workspace.pk)
            finally:
                close_old_connections()

        def replay():
            close_old_connections()
            try:
                if not campaign_held.wait(timeout=10):
                    raise AssertionError("Campaign lock missing")
                return self.begin().pk
            finally:
                close_old_connections()

        with (
            mock.patch.object(service, "_snapshot", side_effect=marked),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first, second = pool.submit(legacy), pool.submit(replay)
            self.assertEqual(second.result(timeout=20), choice.pk)
            first.result(timeout=20)
