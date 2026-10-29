"""Tenant isolation for workspace-owned campaign drafts."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.planning import build_google_search_campaign_plan
from growthtwin.modules.campaigns.report_metrics import (
    CampaignReportMetric,
    MetricStatus,
    MetricUnavailableReason,
    MetricUnit,
)
from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    edit_creative_variant_for_owner,
    generate_creative_version_for_owner,
    get_campaign_draft_for_owner,
    restore_creative_version_for_owner,
    select_preferred_creative_for_owner,
    update_campaign_draft_for_owner,
)
from growthtwin.modules.workspaces.models import Workspace


class CampaignPlanningCalendarTests(SimpleTestCase):
    """Pure calendar regression; unsaved drafts never query a database."""

    def plan(self, start, end, budget=30_000):
        draft = WorkspaceCampaignDraft(
            name="Synthetic date-only plan",
            brand_name="Sentetik Bakım",
            brief="Sentetik bakım hizmeti için bilgi alın.",
            target_city="Ankara",
            destination_url="https://example.test/sentetik",
            media_budget_minor=budget,
            currency="TRY",
            flight_start=start,
            flight_end=end,
        )
        return build_google_search_campaign_plan(draft)

    def test_same_day_is_one_inclusive_calendar_day(self):
        plan = self.plan(date(2026, 11, 1), date(2026, 11, 1))
        self.assertEqual(plan.daily_media_average_minor, Decimal(30_000))
        self.assertFalse(plan.publication_enabled)

    def test_multi_day_average_counts_both_endpoints(self):
        plan = self.plan(date(2026, 11, 1), date(2026, 11, 3))
        self.assertEqual(plan.daily_media_average_minor, Decimal(10_000))
        self.assertEqual(plan.media_budget_minor, 30_000)

    def test_leap_day_counts_as_calendar_day(self):
        plan = self.plan(date(2028, 2, 28), date(2028, 3, 1))
        self.assertEqual(plan.daily_media_average_minor, Decimal(10_000))

    def test_non_leap_february_has_two_inclusive_days(self):
        plan = self.plan(date(2027, 2, 28), date(2027, 3, 1))
        self.assertEqual(plan.daily_media_average_minor, Decimal(15_000))

    def test_missing_date_has_no_daily_average(self):
        for start, end in (
            (None, None),
            (date(2026, 11, 1), None),
            (None, date(2026, 11, 1)),
        ):
            with self.subTest(start=start, end=end):
                plan = self.plan(start, end)
                self.assertIsNone(plan.daily_media_average_minor)
                self.assertFalse(plan.ready_for_review)


class CampaignDraftOwnershipTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="campaign-owner")
        self.other_user = user_model.objects.create_user(username="other-owner")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Owner space")
        self.other_workspace = Workspace.objects.create(
            owner=self.other_user,
            name="Other space",
        )

    def draft_values(self):
        return {
            "name": "Synthetic home repair search campaign",
            "brand_name": "Başkent Ev Bakım",
            "brief": "Offer repair estimates in Ankara.",
            "target_city": "Ankara",
            "destination_url": "https://example.test/repair",
            "media_budget_minor": 500_000,
            "flight_start": date(2026, 10, 1),
            "flight_end": date(2026, 10, 14),
        }

    def test_owner_can_create_and_retrieve_workspace_campaign(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **self.draft_values(),
        )

        self.assertEqual(draft.workspace, self.workspace)
        self.assertEqual(
            draft.objective, WorkspaceCampaignDraft.Objective.LEAD_GENERATION
        )
        self.assertEqual(draft.channel, WorkspaceCampaignDraft.Channel.GOOGLE_SEARCH)
        self.assertEqual(draft.currency, "TRY")
        self.assertEqual(
            get_campaign_draft_for_owner(owner=self.owner, draft_id=draft.pk),
            draft,
        )

    def test_other_owner_cannot_retrieve_campaign_by_id(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **self.draft_values(),
        )

        with self.assertRaises(WorkspaceCampaignDraft.DoesNotExist):
            get_campaign_draft_for_owner(owner=self.other_user, draft_id=draft.pk)

    def test_owner_cannot_create_campaign_in_another_workspace(self):
        with self.assertRaises(Workspace.DoesNotExist):
            create_campaign_draft_for_owner(
                owner=self.owner,
                workspace_id=self.other_workspace.pk,
                **self.draft_values(),
            )

    def test_anonymous_user_cannot_create_campaign(self):
        from django.contrib.auth.models import AnonymousUser

        with self.assertRaises(PermissionDenied):
            create_campaign_draft_for_owner(
                owner=AnonymousUser(),
                workspace_id=self.workspace.pk,
                **self.draft_values(),
            )

    def test_invalid_media_budget_is_rejected_before_persistence(self):
        with self.assertRaises(ValidationError):
            create_campaign_draft_for_owner(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                **(self.draft_values() | {"media_budget_minor": 0}),
            )

        self.assertFalse(WorkspaceCampaignDraft.objects.exists())

    def test_end_date_before_start_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_campaign_draft_for_owner(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                **(
                    self.draft_values()
                    | {
                        "flight_start": date(2026, 10, 14),
                        "flight_end": date(2026, 10, 1),
                    }
                ),
            )

        self.assertFalse(WorkspaceCampaignDraft.objects.exists())

    def test_search_plan_formats_source_text_within_platform_limits(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **self.draft_values(),
        )

        plan = build_google_search_campaign_plan(draft)

        self.assertEqual(len(plan.headlines), 3)
        self.assertEqual(len(plan.descriptions), 2)
        self.assertEqual(plan.media_budget_minor, 500_000)
        self.assertEqual(plan.currency, "TRY")
        self.assertEqual(plan.target_city, "Ankara")
        self.assertTrue(all(len(asset.text) <= 30 for asset in plan.headlines))
        self.assertTrue(all(len(asset.text) <= 90 for asset in plan.descriptions))
        self.assertTrue(all(asset.source_fields for asset in plan.headlines))
        self.assertTrue(all(asset.source_fields for asset in plan.descriptions))
        self.assertTrue(plan.ready_for_review)

    def test_search_plan_never_invents_forecasts_or_enables_publication(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **self.draft_values(),
        )

        plan = build_google_search_campaign_plan(draft)

        self.assertEqual(plan.forecast_status, "unavailable")
        self.assertEqual(plan.keyword_ideas_status, "unavailable")
        self.assertFalse(hasattr(plan, "forecast_metrics"))
        self.assertFalse(plan.publication_enabled)

    def test_search_plan_explains_missing_required_inputs(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **(self.draft_values() | {"brand_name": "", "destination_url": ""}),
        )

        plan = build_google_search_campaign_plan(draft)

        self.assertFalse(plan.ready_for_review)
        self.assertTrue(
            any("İşletme veya marka" in item for item in plan.missing_requirements)
        )
        self.assertTrue(any("web sitesi" in item for item in plan.missing_requirements))


class CampaignPreviewViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="preview-owner")
        self.other_user = user_model.objects.create_user(username="preview-other")
        self.new_user = user_model.objects.create_user(username="preview-new")
        self.workspace = Workspace.objects.create(owner=self.owner, name="My space")
        self.other_workspace = Workspace.objects.create(
            owner=self.other_user,
            name="Other space",
        )

    def campaign_form_data(self, **overrides):
        values = {
            "workspace": self.workspace.pk,
            "synthetic_confirmation": "on",
        }
        return values | overrides

    def make_draft(self):
        return create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            name="Synthetic home repair campaign",
            brand_name="Başkent Ev Bakım",
            brief="Offer repair estimates in Ankara.",
            target_city="Ankara",
            destination_url="https://example.test/repair",
            media_budget_minor=500_000,
            flight_start=date(2026, 10, 1),
            flight_end=date(2026, 10, 15),
        )

    def test_campaign_workspace_requires_login(self):
        response = self.client.get(reverse("campaigns:list"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('campaigns:list')}",
        )

    def test_campaign_list_creates_personal_workspace_and_labels_synthetic_scope(self):
        self.client.force_login(self.new_user)

        response = self.client.get(reverse("campaigns:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.new_user.workspaces.filter(name="Kişisel çalışma alanı").exists()
        )
        self.assertContains(response, "Sentetik prototip")

    def test_owner_can_create_and_preview_workspace_campaign(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("campaigns:create"),
            self.campaign_form_data(
                brand_name="Gerçek şirket adı gönderilse bile kullanılmaz",
                brief="Bu alan kabul edilmemeli.",
            ),
        )

        draft = WorkspaceCampaignDraft.objects.get(workspace=self.workspace)
        self.assertEqual(draft.brand_name, "Başkent Ev Bakım (Sentetik)")
        self.assertEqual(
            draft.brief,
            "Ankara'da ev bakım ve onarım hizmeti için teklif talepleri alın.",
        )
        self.assertEqual(len(draft.creative_versions), 1)
        self.assertEqual(draft.creative_versions[0]["version"], 1)
        self.assertRedirects(response, reverse("campaigns:detail", args=[draft.pk]))
        preview = self.client.get(reverse("campaigns:detail", args=[draft.pk]))
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, "Önizleme · yayınlanmadı")
        self.assertContains(preview, "5.000,00 TRY")
        self.assertContains(preview, "Yetkili Google Ads tahmin kaynağı bağlı değil")
        self.assertContains(preview, "Farklı reklam metinleri")
        self.assertContains(preview, "Kısa tanıtım")
        self.assertContains(preview, "harici AI kullanılmadan şablonla hazırlandı")

    def test_creative_versions_are_owner_scoped_and_post_only(self):
        draft = self.make_draft()
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("campaigns:generate_creatives", args=[draft.pk])
        )

        self.assertEqual(response.status_code, 404)
        draft.refresh_from_db()
        self.assertEqual(draft.creative_versions, [])

        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("campaigns:generate_creatives", args=[draft.pk])
        )
        self.assertEqual(response.status_code, 405)
        draft.refresh_from_db()
        self.assertEqual(draft.creative_versions, [])

    def test_changed_creative_inputs_hide_old_text_until_new_version_is_created(self):
        draft = self.make_draft()
        self.client.force_login(self.owner)
        generate_creative_version_for_owner(owner=self.owner, draft_id=draft.pk)
        draft.refresh_from_db()
        original_copy = draft.creative_versions[-1]["variants"][0]["body"]

        draft.brief = "Updated synthetic offer details for Ankara."
        draft.save(update_fields=("brief",))
        stale_response = self.client.get(reverse("campaigns:detail", args=[draft.pk]))

        self.assertContains(stale_response, "Kampanya bilgileri değişti")
        self.assertNotContains(stale_response, original_copy)
        self.assertContains(stale_response, "Güncel metin sürümünü oluştur")

        generate_response = self.client.post(
            reverse("campaigns:generate_creatives", args=[draft.pk])
        )
        draft.refresh_from_db()
        self.assertRedirects(
            generate_response,
            reverse("campaigns:detail", args=[draft.pk]),
        )
        self.assertEqual(len(draft.creative_versions), 2)
        self.assertEqual(draft.creative_versions[-1]["version"], 2)
        self.assertEqual(
            draft.creative_versions[-1]["variants"][0]["body"], draft.brief
        )
        current_response = self.client.get(reverse("campaigns:detail", args=[draft.pk]))
        self.assertNotContains(current_response, "Kampanya bilgileri değişti")
        self.assertContains(current_response, draft.brief)

    def test_repeated_generation_for_unchanged_inputs_does_not_duplicate_version(self):
        draft = self.make_draft()

        first_draft, first_version = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )
        second_draft, second_version = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )

        self.assertEqual(first_version, second_version)
        self.assertEqual(first_draft.pk, second_draft.pk)
        self.assertEqual(first_version["generator_id"], "synthetic-template-v1")
        self.assertEqual(len(second_draft.creative_versions), 1)

    def test_owner_can_restore_previous_creative_as_a_new_version(self):
        draft = self.make_draft()
        _, original = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )
        edit_creative_variant_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
            version_number=original["version"],
            key="short-introduction",
            headline="Edited synthetic headline",
            body="Edited synthetic body.",
            call_to_action="Edited CTA",
        )
        draft.refresh_from_db()
        original_history = [dict(version) for version in draft.creative_versions]
        select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
            version_number=2,
            key="audience-focused",
        )

        _, restored = restore_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
            version_number=1,
        )

        draft.refresh_from_db()
        self.assertEqual(len(draft.creative_versions), 3)
        self.assertEqual(draft.creative_versions[:2], original_history)
        self.assertEqual(restored["version"], 3)
        self.assertEqual(restored["revision_type"], "owner_restore")
        self.assertEqual(restored["based_on_version"], 2)
        self.assertEqual(restored["restored_from_version"], 1)
        self.assertEqual(restored["generator_id"], original["generator_id"])
        self.assertEqual(restored["variants"], original_history[0]["variants"])
        self.assertEqual(draft.preferred_creative_key, "")
        self.assertIsNone(draft.preferred_creative_version)

    def test_creative_restore_rejects_current_stale_foreign_and_non_post_requests(self):
        draft = self.make_draft()
        _, first = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )
        edit_creative_variant_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
            version_number=first["version"],
            key="short-introduction",
            headline="Edited synthetic headline",
            body="Edited synthetic body.",
            call_to_action="Edited CTA",
        )
        self.client.force_login(self.other_user)
        url = reverse("campaigns:restore_creative", args=[draft.pk])
        self.assertEqual(self.client.post(url, {"version": "1"}).status_code, 404)

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {"version": "2"}).status_code, 302)
        draft.refresh_from_db()
        self.assertEqual(len(draft.creative_versions), 2)

        draft.brief = "Changed synthetic source."
        draft.save(update_fields=("brief",))
        response = self.client.post(url, {"version": "1"})
        self.assertRedirects(
            response,
            f"{reverse('campaigns:detail', args=[draft.pk])}?creative_edit=stale",
        )
        draft.refresh_from_db()
        self.assertEqual(len(draft.creative_versions), 2)

    def test_owner_can_prefer_a_current_creative_variant(self):
        draft = self.make_draft()
        _, version = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("campaigns:select_preferred_creative", args=[draft.pk]),
            {"variant_key": "audience-focused", "version": version["version"]},
        )

        draft.refresh_from_db()
        self.assertRedirects(
            response,
            f"{reverse('campaigns:detail', args=[draft.pk])}?creative_preference=saved",
        )
        self.assertEqual(draft.preferred_creative_key, "audience-focused")
        self.assertEqual(draft.preferred_creative_version, version["version"])
        detail = self.client.get(
            f"{reverse('campaigns:detail', args=[draft.pk])}?creative_preference=saved"
        )
        self.assertContains(detail, "Tercih edilen taslak")
        self.assertContains(detail, "İnceleme tercihin kaydedildi")
        self.assertContains(detail, "Tercih yalnızca inceleme içindir")

    def test_preference_rejects_stale_or_unknown_variant(self):
        draft = self.make_draft()
        _, version = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )
        self.client.force_login(self.owner)
        url = reverse("campaigns:select_preferred_creative", args=[draft.pk])

        self.client.post(
            url,
            {"variant_key": "made-up", "version": version["version"]},
        )
        draft.refresh_from_db()
        self.assertEqual(draft.preferred_creative_key, "")

        self.client.post(
            url,
            {"variant_key": "audience-focused", "version": "999"},
        )
        draft.refresh_from_db()
        self.assertEqual(draft.preferred_creative_key, "")

    def test_preference_is_owner_scoped_and_post_only(self):
        draft = self.make_draft()
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("campaigns:select_preferred_creative", args=[draft.pk]),
            {"variant_key": "audience-focused", "version": "1"},
        )

        self.assertEqual(response.status_code, 404)
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("campaigns:select_preferred_creative", args=[draft.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_preference_is_hidden_on_source_change_and_cleared_on_new_version(self):
        draft = self.make_draft()
        _, version = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
        )
        select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=draft.pk,
            version_number=version["version"],
            key="audience-focused",
        )
        draft.refresh_from_db()
        draft.brief = "Changed synthetic brief."
        draft.save(update_fields=("brief",))
        self.client.force_login(self.owner)

        stale_detail = self.client.get(reverse("campaigns:detail", args=[draft.pk]))

        self.assertContains(stale_detail, "Kampanya bilgileri değişti")
        self.assertNotContains(stale_detail, "Tercih edilen taslak")
        self.client.post(reverse("campaigns:generate_creatives", args=[draft.pk]))
        draft.refresh_from_db()
        self.assertEqual(draft.preferred_creative_key, "")
        self.assertIsNone(draft.preferred_creative_version)

    def test_campaign_form_rejects_other_owners_workspace(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("campaigns:create"),
            self.campaign_form_data(workspace=self.other_workspace.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(WorkspaceCampaignDraft.objects.exists())

    def test_other_owner_cannot_open_campaign_preview(self):
        draft = self.make_draft()
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("campaigns:detail", args=[draft.pk]))

        self.assertEqual(response.status_code, 404)

    def test_owner_report_shows_metrics_as_unavailable_without_a_data_source(self):
        draft = self.make_draft()
        self.client.force_login(self.owner)

        response = self.client.get(reverse("campaigns:report", args=[draft.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rapor verisi henüz bağlı değil")
        self.assertEqual(response.content.decode().count("Veri kaynağı bağlı değil"), 6)
        self.assertContains(response, "Veri kaynağı")
        self.assertContains(response, "Bağlı değil")
        self.assertContains(response, "tahmin veya performans garantisi içermez")
        metrics = response.context["report_metrics"]
        self.assertEqual(len(metrics), 6)
        self.assertTrue(
            all(isinstance(metric, CampaignReportMetric) for metric in metrics)
        )
        self.assertTrue(
            all(metric.status is MetricStatus.UNAVAILABLE for metric in metrics)
        )
        self.assertTrue(
            all(
                metric.unavailable_reason is MetricUnavailableReason.NOT_CONNECTED
                for metric in metrics
            )
        )
        self.assertEqual(metrics[0].window.start, draft.flight_start)
        self.assertEqual(metrics[-1].unit, MetricUnit.CURRENCY)
        self.assertEqual(metrics[-1].currency, draft.currency)
        self.assertIsNone(metrics[-1].source)
        self.assertIsNone(metrics[-1].observation)
        self.assertContains(response, "Planlanan kampanya dönemi")
        self.assertContains(response, "Gözlenen rapor dönemi")
        self.assertContains(response, "Henüz gözlem yok; kaynak bağlı değil")
        self.assertContains(response, "Veri güncelliği")
        self.assertContains(response, "Kaynak verisi yok; güncellik doğrulanamıyor")
        self.assertNotContains(response, "Planlanan kampanya dönemi:")

    def test_owner_report_without_flight_dates_has_no_invented_period(self):
        draft = self.make_draft()
        draft.flight_start = None
        draft.flight_end = None
        draft.save(update_fields=("flight_start", "flight_end"))
        self.client.force_login(self.owner)

        response = self.client.get(reverse("campaigns:report", args=[draft.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["report_metrics"]), 6)
        self.assertTrue(
            all(metric.window is None for metric in response.context["report_metrics"])
        )
        self.assertContains(response, "Planlanan kampanya dönemi")
        self.assertContains(response, "Belirtilmedi")
        self.assertContains(response, "Gözlenen rapor dönemi")

    def test_other_owner_cannot_open_campaign_report(self):
        draft = self.make_draft()
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("campaigns:report", args=[draft.pk]))

        self.assertEqual(response.status_code, 404)

    def test_owner_can_update_bounded_synthetic_budget_and_duration(self):
        draft = self.make_draft()
        generate_creative_version_for_owner(owner=self.owner, draft_id=draft.pk)
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("campaigns:edit", args=[draft.pk]),
            {
                "media_budget_minor": "1000000",
                "duration_days": "30",
                "synthetic_confirmation": "on",
            },
        )

        draft.refresh_from_db()
        self.assertRedirects(response, reverse("campaigns:detail", args=[draft.pk]))
        self.assertEqual(draft.media_budget_minor, 1_000_000)
        self.assertEqual((draft.flight_end - draft.flight_start).days, 30)
        self.assertEqual(draft.brief, "Offer repair estimates in Ankara.")
        self.assertEqual(len(draft.creative_versions), 1)
        detail = self.client.get(reverse("campaigns:detail", args=[draft.pk]))
        self.assertNotContains(detail, "Kampanya bilgileri değişti")

    def test_campaign_edit_rejects_unlisted_budget(self):
        draft = self.make_draft()
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("campaigns:edit", args=[draft.pk]),
            {
                "media_budget_minor": "999999",
                "duration_days": "14",
                "synthetic_confirmation": "on",
            },
        )

        draft.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(draft.media_budget_minor, 500_000)

    def test_owner_scoped_service_rejects_unlisted_synthetic_values(self):
        draft = self.make_draft()

        with self.assertRaises(ValidationError):
            update_campaign_draft_for_owner(
                owner=self.owner,
                draft_id=draft.pk,
                media_budget_minor=999_999,
                flight_start=date(2026, 10, 1),
                flight_end=date(2026, 10, 15),
            )

        draft.refresh_from_db()
        self.assertEqual(draft.media_budget_minor, 500_000)

    def test_other_owner_cannot_edit_campaign(self):
        draft = self.make_draft()
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("campaigns:edit", args=[draft.pk]))

        self.assertEqual(response.status_code, 404)

    def test_owner_must_confirm_before_campaign_delete(self):
        draft = self.make_draft()
        self.client.force_login(self.owner)

        response = self.client.post(reverse("campaigns:delete", args=[draft.pk]))

        self.assertRedirects(response, reverse("campaigns:detail", args=[draft.pk]))
        self.assertTrue(WorkspaceCampaignDraft.objects.filter(pk=draft.pk).exists())

    def test_owner_can_delete_campaign_only_after_confirmation(self):
        draft = self.make_draft()
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("campaigns:delete", args=[draft.pk]),
            {"confirm_delete": "on"},
        )

        self.assertRedirects(response, reverse("campaigns:list"))
        self.assertFalse(WorkspaceCampaignDraft.objects.filter(pk=draft.pk).exists())

    def test_campaign_delete_does_not_accept_get(self):
        draft = self.make_draft()
        self.client.force_login(self.owner)

        response = self.client.get(reverse("campaigns:delete", args=[draft.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(WorkspaceCampaignDraft.objects.filter(pk=draft.pk).exists())

    def test_other_owner_cannot_delete_campaign(self):
        draft = self.make_draft()
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("campaigns:delete", args=[draft.pk]),
            {"confirm_delete": "on"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(WorkspaceCampaignDraft.objects.filter(pk=draft.pk).exists())
