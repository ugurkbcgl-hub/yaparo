"""Local planning history, exact money, ownership and zero operational changes."""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import mock
from urllib.parse import urlencode
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import close_old_connections, connection
from django.test import (
    Client,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from growthtwin.modules.workspaces.models import Brand, Workspace

from . import brand_ad_selection
from . import brand_settings as service
from .models import CampaignBrandAdChoice, CampaignPlanRevision, WorkspaceCampaignDraft
from .test_brand_ad_selection import BrandCampaignFixture


class PlanFixture(BrandCampaignFixture):
    def setUp(self):
        super().setUp()
        gate = override_settings(LOCAL_BRAND_CAMPAIGN_SETTINGS_ENABLED=True)
        gate.enable()
        self.addCleanup(gate.disable)
        self.camp = self.begin().campaign
        self.values = {
            "goal": "traffic",
            "audience": "Sentetik seramik meraklıları",
            "region": "İstanbul",
            "budget_minor": 250050,
            "start": service.today().isoformat(),
            "end": (service.today() + timedelta(days=6)).isoformat(),
        }
        self.nonce = uuid4()

    def save_plan(self, **changes):
        return service.save(
            **(
                {
                    "owner": self.owner,
                    "campaign_id": self.camp.pk,
                    "expected_version": 0,
                    "request_id": self.nonce,
                    "values": self.values,
                }
                | changes
            )
        )


class BrandSettingsTests(PlanFixture, TransactionTestCase):
    def test_versions_replay_and_no_legacy_or_ad_change(self):
        before = WorkspaceCampaignDraft.objects.values().get(pk=self.camp.pk)
        choice_before = list(CampaignBrandAdChoice.objects.values())
        first = self.save_plan()
        second = self.save_plan(
            expected_version=1,
            request_id=uuid4(),
            values={**self.values, "budget_minor": 500000},
        )
        self.assertEqual(second.version, 2)
        self.assertEqual(self.save_plan().pk, first.pk)
        self.assertEqual(
            service.read(owner=self.owner, campaign_id=self.camp.pk).pk, second.pk
        )
        with self.assertRaises(ValidationError):
            self.save_plan(request_id=uuid4())
        self.assertEqual(
            before, WorkspaceCampaignDraft.objects.values().get(pk=self.camp.pk)
        )
        self.assertEqual(choice_before, list(CampaignBrandAdChoice.objects.values()))
        with self.assertRaises(ValidationError):
            CampaignPlanRevision.objects.update(payload={})
        with self.assertRaises(ValidationError):
            first.delete()

    def test_closed_values_exact_budget_and_inclusive_days(self):
        from .brand_settings_views import PlanForm

        amount = PlanForm.base_fields["budget"]
        for raw in ("2500,50", "2500.50"):
            self.assertEqual(int(amount.clean(raw) * 100), 250050)
        for raw in ("2,500.50", "2500,505", "NaN"):
            with self.assertRaises(ValidationError):
                amount.clean(raw)
        for key, bad in (
            ("budget_minor", True),
            ("budget_minor", 1.5),
            ("budget_minor", 0),
            ("budget_minor", service.MAX_BUDGET_MINOR + 1),
            ("goal", []),
            ("audience", "bad\nline"),
            ("region", "\ud800"),
            ("start", "20261027"),
            ("end", (service.today() + timedelta(days=365)).isoformat()),
        ):
            with (
                self.subTest(key=key, bad=repr(bad)),
                self.assertRaises(ValidationError),
            ):
                service.validate({**self.values, key: bad})
        self.assertEqual(
            service.summary(
                self.save_plan(values={**self.values, "end": self.values["start"]})
            )["days"],
            1,
        )
        accepted = service.validate(
            {**self.values, "end": (service.today() + timedelta(days=364)).isoformat()}
        )
        self.assertEqual(accepted["budget_minor"], 250050)
        with self.assertRaises(ValidationError):
            service.validate({**self.values, "extra": True})

    def test_old_read_and_exact_replay_survive_day_change_but_new_write_refuses(self):
        row = self.save_plan()
        with mock.patch.object(
            service, "today", return_value=service.today() + timedelta(days=1)
        ):
            self.assertEqual(self.save_plan().pk, row.pk)
            self.assertEqual(
                service.read(owner=self.owner, campaign_id=self.camp.pk).pk, row.pk
            )
            with self.assertRaises(ValidationError):
                self.save_plan(expected_version=1, request_id=uuid4())

    def test_fresh_day_check_occurs_after_scope_locks(self):
        current = service.today()
        original = service._scope
        with mock.patch.object(service, "today", return_value=current) as clock:

            def late(*args):
                result = original(*args)
                clock.return_value = current + timedelta(days=1)
                return result

            with (
                mock.patch.object(service, "_scope", side_effect=late),
                self.assertRaises(ValidationError),
            ):
                self.save_plan()
        self.assertFalse(CampaignPlanRevision.objects.exists())

    def test_owner_workspace_archive_closed_flag_and_cross_campaign_nonce(self):
        first = self.save_plan()
        other = self.begin(request_id=uuid4()).campaign
        with self.assertRaises(ValidationError):
            self.save_plan(campaign_id=other.pk)
        with self.assertRaises(ObjectDoesNotExist):
            service.read(owner=self.other, campaign_id=self.camp.pk)
        workspace = Workspace.objects.create(owner=self.owner, name="Ayrı")
        WorkspaceCampaignDraft.objects.filter(pk=self.camp.pk).update(
            workspace=workspace
        )
        with self.assertRaises(ValidationError):
            service.read(owner=self.owner, campaign_id=self.camp.pk)
        WorkspaceCampaignDraft.objects.filter(pk=self.camp.pk).update(
            workspace=self.workspace
        )
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        with self.assertRaises(ObjectDoesNotExist):
            service.read(owner=self.owner, campaign_id=self.camp.pk)
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=False)
        with (
            override_settings(LOCAL_BRAND_CAMPAIGN_SETTINGS_ENABLED=False),
            self.assertRaises(PermissionDenied),
        ):
            service.read(owner=self.owner, campaign_id=self.camp.pk)
        self.assertEqual(CampaignPlanRevision.objects.get(pk=first.pk).version, 1)

    def test_corrupt_payload_does_not_fall_back_to_placeholder_budget(self):
        row = self.save_plan()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE campaigns_campaignplanrevision SET payload=%s WHERE id=%s",
                [json.dumps({**row.payload, "currency": "USD"}), row.pk],
            )
        with self.assertRaises(ValidationError):
            service.read(owner=self.owner, campaign_id=self.camp.pk)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("campaigns:list"))
        self.assertContains(response, "Plan bilgisi kullanılamıyor")
        self.assertNotContains(response, "5.000,00")
        self.assertEqual(
            self.client.get(
                reverse("campaigns:brand_setup", args=[self.camp.pk])
            ).status_code,
            409,
        )
        self.assertEqual(
            self.client.get(
                reverse("campaigns:brand_ad_choose", args=[self.camp.pk])
            ).status_code,
            409,
        )

    def test_http_localized_budget_closed_form_csrf_summary_and_routes(self):
        url = reverse("campaigns:brand_setup", args=[self.camp.pk])
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertFalse(CampaignPlanRevision.objects.exists())
        body = {
            "goal": "traffic",
            "audience": self.values["audience"],
            "region": "İstanbul",
            "budget": "2500,50",
            "start": self.values["start"],
            "end": self.values["end"],
            "expected_version": 0,
            "request_id": self.nonce,
            "synthetic_confirmation": "on",
        }
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.owner)
        self.assertEqual(
            csrf.post(
                url, urlencode(body), content_type="application/x-www-form-urlencoded"
            ).status_code,
            403,
        )
        self.assertEqual(self.client.post(url, body).status_code, 415)
        self.assertEqual(
            self.client.post(
                url,
                urlencode({**body, "extra": "no"}),
                content_type="application/x-www-form-urlencoded",
            ).status_code,
            409,
        )
        response = self.client.post(
            url, urlencode(body), content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            CampaignPlanRevision.objects.get().payload["settings"]["budget_minor"],
            250050,
        )
        summary = self.client.get(
            reverse("campaigns:brand_ad_choose", args=[self.camp.pk])
        )
        self.assertContains(summary, "2.500,50 TRY")
        self.assertIn("no-store", summary["Cache-Control"])
        self.assertContains(self.client.get(reverse("campaigns:list")), "2.500,50 TRY")
        for name in ("detail", "journey"):
            self.assertRedirects(
                self.client.get(reverse("campaigns:" + name, args=[self.camp.pk])),
                reverse("campaigns:brand_ad_choose", args=[self.camp.pk]),
            )
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_expected_version_accepts_one(self):
        barrier = Barrier(2)

        def run():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    self.save_plan(request_id=uuid4())
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
        self.assertEqual(CampaignPlanRevision.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_plan_save_and_ad_selection_share_campaign_first_lock_order(self):
        choice = self.camp.brand_ad_choices.first()
        barrier = Barrier(2)

        def run(operation):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return operation()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(run, self.save_plan)
            b = pool.submit(run, lambda: self.choose(choice))
            a.result(timeout=20)
            b.result(timeout=20)
        self.assertEqual(CampaignPlanRevision.objects.count(), 1)
        self.assertEqual(
            brand_ad_selection.selected(owner=self.owner, campaign_id=self.camp.pk)[
                0
            ].version,
            2,
        )
