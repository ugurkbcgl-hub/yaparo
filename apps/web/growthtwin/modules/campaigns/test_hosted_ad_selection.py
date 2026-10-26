"""Pinned owned AI visual planning references; no dispatch or provider calls."""

import json
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from threading import Barrier, Event
from unittest import mock
from urllib.parse import urlencode
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections, transaction
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from growthtwin.modules.workspaces.models import (
    HostedAdDraft,
    HostedImageTrial,
    Workspace,
)
from growthtwin.modules.workspaces.test_hosted_ad_drafts import SavedTrialsFixture

from . import hosted_ad_selection as service
from .models import CampaignDesignChoice, CampaignHostedAdChoice, WorkspaceCampaignDraft


class CampaignAdFixture(SavedTrialsFixture):
    def setUp(self):
        super().setUp()
        flag = override_settings(LOCAL_HOSTED_AD_CAMPAIGN_ENABLED=True)
        flag.enable()
        self.addCleanup(flag.disable)
        self.plan = WorkspaceCampaignDraft.objects.create(
            workspace=self.workspace,
            name="Duru görsel planı",
            brand_name="Duru Studio",
            brief="Sentetik yerel plan",
            target_city="Ankara",
            media_budget_minor=250000,
        )
        self.ad = self.create()

    def choose(self, **overrides):
        return service.select(
            **{
                "owner": self.owner,
                "campaign_id": self.plan.pk,
                "ad_id": self.ad.pk,
                "revision": self.ad.revision,
                "source": self.ad.source_fingerprint,
                "expected_version": 0,
                "request_id": uuid4(),
                **overrides,
            }
        )


class CampaignAdSelectionTests(CampaignAdFixture, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.url = reverse("campaigns:hosted_ad_choose", args=[self.plan.pk])

    def test_selection_pins_history_replay_does_not_reset_or_change_campaign(self):
        before = WorkspaceCampaignDraft.objects.values().get(pk=self.plan.pk)
        choice = self.choose()
        self.ad = self.save(self.ad, title="Yeni düzenleme")
        current, snapshot, _ = service.selected(
            owner=self.owner, campaign_id=self.plan.pk, version=1
        )
        self.assertEqual(snapshot["content"]["title"], "El yapımı seramik kupalar")
        self.assertEqual(current.revision.revision, 1)
        replay = self.choose(revision=1, request_id=choice.request_id)
        self.assertEqual(replay.pk, choice.pk)
        newer = self.choose(expected_version=1)
        self.assertEqual(newer.version, 2)
        self.assertEqual(newer.snapshot["content"]["title"], "Yeni düzenleme")
        self.assertEqual(
            self.choose(revision=1, request_id=choice.request_id).pk, choice.pk
        )
        self.assertEqual(
            service.selected(owner=self.owner, campaign_id=self.plan.pk)[0].pk, newer.pk
        )
        with self.assertRaises(ValidationError):
            service.selected(owner=self.owner, campaign_id=self.plan.pk, version=1)
        self.assertEqual(
            WorkspaceCampaignDraft.objects.values().get(pk=self.plan.pk), before
        )
        self.assertFalse(CampaignDesignChoice.objects.exists())
        self.assertEqual(self.ad.history.count(), 2)

    def test_stale_revision_version_source_and_request_collision_refuse(self):
        self.ad = self.save(self.ad, title="Güncel kayıt")
        for kwargs in ({"revision": 1}, {"source": "0" * 64}, {"expected_version": 1}):
            with self.assertRaises(ValidationError):
                self.choose(**kwargs)
        choice = self.choose()
        with self.assertRaises(ValidationError):
            self.choose()
        other = WorkspaceCampaignDraft.objects.create(
            workspace=self.workspace,
            name="Diğer",
            brief="Sentetik",
            target_city="Ankara",
            media_budget_minor=100,
        )
        with self.assertRaises(ValidationError):
            self.choose(campaign_id=other.pk, request_id=choice.request_id)
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 1)

    def test_tampered_selection_or_history_refuses_and_history_is_append_only(self):
        choice = self.choose()
        with self.assertRaises(ValidationError):
            choice.save()
        with self.assertRaises(ValidationError):
            choice.delete()
        with self.assertRaises(ValidationError):
            CampaignHostedAdChoice.objects.update(snapshot={})
        with self.assertRaises(ValidationError):
            CampaignHostedAdChoice.objects.all().delete()
        # Bypass normal append-only APIs to simulate DB corruption, not a
        # supported application write. Readback must not trust stored metadata.
        CampaignHostedAdChoice._base_manager.filter(pk=choice.pk).update(snapshot={})
        with self.assertRaises(ValidationError):
            service.selected(owner=self.owner, campaign_id=self.plan.pk)
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 1)

    def test_failed_append_rolls_back(self):
        with mock.patch.object(
            CampaignHostedAdChoice.objects, "create", side_effect=RuntimeError
        ):
            with self.assertRaises(RuntimeError):
                self.choose()
        self.assertFalse(CampaignHostedAdChoice.objects.exists())
        self.assertEqual(HostedAdDraft.objects.get(pk=self.ad.pk).revision, 1)

    def test_package_pins_canonical_snapshot_and_selection_not_campaign_name(self):
        choice = self.choose()
        url = reverse(
            "campaigns:hosted_ad_package", args=[self.plan.pk, choice.version]
        )
        before = CampaignHostedAdChoice.objects.values().get(pk=choice.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        context = data["campaign_selection"]
        self.assertEqual(context["campaign_id"], str(self.plan.pk))
        self.assertEqual(context["selection_version"], choice.version)
        self.assertEqual(context["ad_revision"], 1)
        self.assertEqual(
            context["snapshot_sha256"], sha256(data["ad_json"].encode()).hexdigest()
        )
        self.assertEqual(json.loads(data["ad_json"]), choice.snapshot)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.client.head(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 405)
        self.assertEqual(self.client.get(url + "?latest=1").status_code, 400)
        self.ad = self.save(self.ad, title="Sonraki düzenleme")
        WorkspaceCampaignDraft.objects.filter(pk=self.plan.pk).update(
            name="Yeni kampanya adı"
        )
        self.assertEqual(self.client.get(url).json(), data)
        self.assertEqual(
            CampaignHostedAdChoice.objects.values().get(pk=choice.pk), before
        )
        self.choose(expected_version=1)
        self.assertEqual(self.client.get(url).status_code, 409)
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 2)

    def test_package_denies_foreign_disabled_logged_out_or_corrupt_sources(self):
        choice = self.choose()
        url = reverse(
            "campaigns:hosted_ad_package", args=[self.plan.pk, choice.version]
        )
        foreign = get_user_model().objects.create_user(
            username="foreign-campaign-package"
        )
        self.client.force_login(foreign)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.owner)
        with override_settings(LOCAL_HOSTED_AD_CAMPAIGN_ENABLED=False):
            self.assertEqual(self.client.get(url).status_code, 404)
        HostedImageTrial.objects.filter(pk=self.image.pk).update(png=b"invalid")
        self.assertEqual(self.client.get(url).status_code, 409)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 1)

    def test_flags_foreign_same_owner_other_workspace_and_inactive_refuse(self):
        choice = self.choose()
        preview = reverse(
            "campaigns:hosted_ad_preview", args=[self.plan.pk, choice.version]
        )
        for opts in (
            {"LOCAL_HOSTED_AD_CAMPAIGN_ENABLED": False},
            {"LOCAL_HOSTED_AD_DRAFT_ENABLED": False},
            {"DEBUG": False},
        ):
            with override_settings(**opts):
                self.assertEqual(self.client.get(preview).status_code, 404)
        foreign = get_user_model().objects.create_user(username="foreign-campaign-ad")
        self.client.force_login(foreign)
        self.assertEqual(self.client.get(preview).status_code, 404)
        self.client.force_login(self.owner)
        other = Workspace.objects.create(owner=self.owner, name="Other owner workspace")
        plan = WorkspaceCampaignDraft.objects.create(
            workspace=other,
            name="Other",
            brief="Synthetic",
            target_city="Ankara",
            media_budget_minor=100,
        )
        self.assertEqual(
            self.client.get(
                reverse("campaigns:hosted_ad_choose", args=[plan.pk])
            ).status_code,
            404,
        )
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        self.assertEqual(self.client.get(preview).status_code, 302)

    def test_http_csrf_preparse_duplicates_readonly_and_private_headers(self):
        page = self.client.get(self.url)
        self.assertEqual(page.status_code, 200)
        data = page.context["options"][0]["form"].initial
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.owner)
        self.assertEqual(csrf.post(self.url, data).status_code, 415)
        self.assertEqual(
            csrf.post(
                self.url,
                urlencode(data),
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                self.url,
                urlencode(data),
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            302,
        )
        self.assertEqual(
            self.client.post(
                self.url,
                urlencode(data) + "&revision=1",
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            409,
        )
        choice = CampaignHostedAdChoice.objects.get()
        for name in ("hosted_ad_preview", "hosted_ad_image"):
            url = reverse("campaigns:" + name, args=[self.plan.pk, choice.version])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("no-store", response["Cache-Control"])
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
            self.assertEqual(self.client.post(url).status_code, 405)
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 1)
        response = Client().get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("no-store", response["Cache-Control"])

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_selection_accepts_only_one_expected_version(self):
        barrier = Barrier(2)

        def select():
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                barrier.wait(timeout=8)
                try:
                    self.choose(owner=owner)
                    return "saved"
                except ValidationError:
                    return "stale"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = [
                f.result(timeout=15) for f in [pool.submit(select), pool.submit(select)]
            ]
        self.assertCountEqual(results, ["saved", "stale"])
        self.assertEqual(CampaignHostedAdChoice.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_campaign_first_lock_order_coexists_with_legacy_workspace_locks(self):
        # Legacy campaign operations lock the campaign and its joined workspace.
        # Pause that graph between rows, then let the new operation enter its
        # campaign lock. Workspace-first here would form a real PG deadlock.
        original = service.campaign
        for reading in (False, True):
            held = Event()
            entered = Event()

            def instrument(owner, campaign_id, *, lock=False):
                if lock:
                    entered.set()
                return original(owner, campaign_id, lock=lock)

            def legacy():
                close_old_connections()
                try:
                    with transaction.atomic():
                        WorkspaceCampaignDraft.objects.select_for_update(
                            of=("self",)
                        ).get(pk=self.plan.pk)
                        held.set()
                        self.assertTrue(entered.wait(8))
                        Workspace.objects.select_for_update().get(pk=self.workspace.pk)
                    return "legacy"
                finally:
                    close_old_connections()

            def current():
                close_old_connections()
                try:
                    self.assertTrue(held.wait(8))
                    owner = get_user_model().objects.get(pk=self.owner.pk)
                    if reading:
                        service.selected(owner=owner, campaign_id=self.plan.pk)
                    else:
                        self.choose(owner=owner)
                    return "current"
                finally:
                    close_old_connections()

            with (
                mock.patch.object(service, "campaign", side_effect=instrument),
                ThreadPoolExecutor(max_workers=2) as pool,
            ):
                futures = [pool.submit(legacy), pool.submit(current)]
                self.assertCountEqual(
                    [f.result(timeout=15) for f in futures], ["legacy", "current"]
                )
