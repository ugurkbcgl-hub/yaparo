"""Authenticated views for local synthetic campaign planning."""

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import number_format
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST, require_safe

from growthtwin.modules.campaigns.brand_ad_views import (
    reference_context as brand_ad_context,
)
from growthtwin.modules.campaigns.design_views import reference_context
from growthtwin.modules.campaigns.eligibility import (
    synthetic_campaign_eligibility_preview,
)
from growthtwin.modules.campaigns.exports import (
    campaign_review_text,
    preferred_current_variant,
)
from growthtwin.modules.campaigns.forms import (
    CampaignDraftEditForm,
    CampaignDraftForm,
    CreativeVariantEditForm,
)
from growthtwin.modules.campaigns.hosted_ad_views import (
    reference_context as hosted_ad_context,
)
from growthtwin.modules.campaigns.journey import (
    campaign_journey,
    google_test_controls_available,
)
from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.planning import build_google_search_campaign_plan
from growthtwin.modules.campaigns.rehearsal import (
    perform_campaign_rehearsal,
    rehearsal_context,
)
from growthtwin.modules.campaigns.report_metrics import (
    ReportingWindow,
    unavailable_campaign_report_metrics,
)
from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    creative_source_hash_for_draft,
    edit_creative_variant_for_owner,
    generate_creative_version_for_owner,
    restore_creative_version_for_owner,
    select_preferred_creative_for_owner,
    update_campaign_draft_for_owner,
)
from growthtwin.modules.workspaces.models import Workspace

SYNTHETIC_CAMPAIGN = {
    "name": "Sentetik Ankara ev bakım kampanyası",
    "brand_name": "Başkent Ev Bakım (Sentetik)",
    "brief": "Ankara'da ev bakım ve onarım hizmeti için teklif talepleri alın.",
    "target_city": "Ankara",
    "destination_url": "https://example.invalid/ev-bakim",
    "media_budget_minor": 500_000,
}


def _workspaces_for_user(user):
    workspaces = Workspace.objects.filter(owner=user)
    if not workspaces.exists():
        Workspace.objects.create(owner=user, name="Kişisel çalışma alanı")
        workspaces = Workspace.objects.filter(owner=user)
    return workspaces


def _draft_rows(drafts):
    return [
        {
            "draft": draft,
            "budget_display": _format_budget(draft.media_budget_minor),
        }
        for draft in drafts
    ]


def _format_budget(minor_units, currency="TRY"):
    amount = Decimal(minor_units) / 100
    return f"{number_format(amount, decimal_pos=2, force_grouping=True)} {currency}"


def _format_daily_average(minor_units):
    if minor_units is None:
        return None
    amount = minor_units / 100
    return f"{number_format(amount, decimal_pos=2, force_grouping=True)} TRY"


@login_required
def campaign_list(request):
    """Show only the current user's workspace campaign drafts."""

    _workspaces_for_user(request.user)
    drafts = WorkspaceCampaignDraft.objects.owned_by(request.user).select_related(
        "workspace"
    )
    return render(
        request,
        "campaigns/list.html",
        {
            "draft_rows": _draft_rows(drafts),
            "synthetic_only": True,
            "closure_ui_enabled": settings.SYNTHETIC_CLOSURE_UI_ENABLED,
        },
    )


@login_required
def campaign_create(request):
    """Create an owner-scoped synthetic campaign draft and show its local plan."""

    workspaces = _workspaces_for_user(request.user)
    form = CampaignDraftForm(
        request.POST or None,
        workspaces=workspaces,
    )
    if request.method == "POST" and form.is_valid():
        values = form.cleaned_data
        today = timezone.localdate()
        draft = create_campaign_draft_for_owner(
            owner=request.user,
            workspace_id=values["workspace"].pk,
            name=SYNTHETIC_CAMPAIGN["name"],
            brand_name=SYNTHETIC_CAMPAIGN["brand_name"],
            brief=SYNTHETIC_CAMPAIGN["brief"],
            target_city=SYNTHETIC_CAMPAIGN["target_city"],
            destination_url=SYNTHETIC_CAMPAIGN["destination_url"],
            media_budget_minor=SYNTHETIC_CAMPAIGN["media_budget_minor"],
            currency="TRY",
            flight_start=today + timedelta(days=1),
            flight_end=today + timedelta(days=15),
        )
        generate_creative_version_for_owner(owner=request.user, draft_id=draft.pk)
        return redirect("campaigns:detail", draft_id=draft.pk)

    return render(
        request,
        "campaigns/create.html",
        {"form": form, "sample": SYNTHETIC_CAMPAIGN},
    )


def _campaign_detail_response(request, draft, *, bound_edit_form=None):
    plan = build_google_search_campaign_plan(draft)
    versions = draft.creative_versions or []
    latest_creative_version = versions[-1] if versions else None
    creative_is_stale = bool(
        latest_creative_version
        and latest_creative_version.get("source_hash")
        != creative_source_hash_for_draft(draft)
    )
    creative_version = latest_creative_version if not creative_is_stale else None
    creative_version_history = (
        [
            version
            for version in versions[:-1]
            if version.get("source_hash") == creative_source_hash_for_draft(draft)
        ]
        if creative_version
        else []
    )
    variant_rows = []
    if creative_version:
        for variant in creative_version.get("variants", []):
            initial = {
                "variant_key": variant.get("key", ""),
                "version": creative_version.get("version"),
                "headline": variant.get("headline", ""),
                "body": variant.get("body", ""),
                "call_to_action": variant.get("call_to_action", ""),
            }
            form_matches = bool(
                bound_edit_form
                and bound_edit_form["variant_key"].value() == variant.get("key")
            )
            variant_rows.append(
                {
                    "variant": variant,
                    "edit_form": (
                        bound_edit_form
                        if form_matches
                        else CreativeVariantEditForm(initial=initial)
                    ),
                }
            )
    return render(
        request,
        "campaigns/detail.html",
        {
            "draft": draft,
            "plan": plan,
            **reference_context(request.user, draft.pk),
            **hosted_ad_context(request.user, draft.pk),
            **brand_ad_context(request.user, draft.pk),
            "eligibility_decision": synthetic_campaign_eligibility_preview(
                evaluated_on=timezone.localdate()
            ),
            "budget_display": _format_budget(draft.media_budget_minor),
            "daily_average_display": _format_daily_average(
                plan.daily_media_average_minor
            ),
            "creative_version": creative_version,
            "creative_version_history": creative_version_history,
            "creative_variant_rows": variant_rows,
            "creative_is_stale": creative_is_stale,
            "creative_version_count": len(versions),
            "download_variant": preferred_current_variant(draft),
            "google_test_review_enabled": google_test_controls_available(
                request, draft
            ),
            "download_stale": request.GET.get("download") == "stale",
            "rehearsal": rehearsal_context(draft),
            "rehearsal_notice": (
                request.GET.get("rehearsal")
                if request.GET.get("rehearsal") in {"updated", "changed"}
                else ""
            ),
            "preferred_creative_key": (
                draft.preferred_creative_key
                if (
                    not creative_is_stale
                    and latest_creative_version
                    and draft.preferred_creative_version
                    == latest_creative_version.get("version")
                )
                else ""
            ),
            "creative_preference_notice": (
                request.GET.get("creative_preference")
                if request.GET.get("creative_preference") in {"saved", "stale"}
                else ""
            ),
            "creative_edit_notice": (
                request.GET.get("creative_edit")
                if request.GET.get("creative_edit") in {"saved", "restored", "stale"}
                else ""
            ),
        },
    )


@never_cache
@login_required
@require_GET
def campaign_download(request, draft_id):
    """Download the owner's current selected synthetic draft for review."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user), pk=draft_id
    )
    try:
        text = campaign_review_text(
            draft,
            version_number=int(request.GET.get("version", "")),
            variant_key=request.GET.get("variant", ""),
        )
    except (ValueError, ValidationError):
        return redirect(
            f"{reverse('campaigns:detail', args=[draft.pk])}?download=stale"
        )
    response = HttpResponse(text, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="yaparo-draft-{draft.pk}'
        f'-v{draft.preferred_creative_version}.txt"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@never_cache
@login_required
def campaign_detail(request, draft_id):
    """Render an owner's local plan; cross-tenant IDs resolve as not found."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user).select_related(
            "workspace"
        ),
        pk=draft_id,
    )
    return _campaign_detail_response(request, draft)


@never_cache
@login_required
@require_safe
def campaign_journey_overview(request, draft_id):
    """Show owner-scoped stored stages without provider access or mutations."""
    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user)
        .filter(workspace__owner__is_active=True)
        .select_related("workspace"),
        pk=draft_id,
    )
    return render(
        request,
        "campaigns/journey.html",
        {
            "draft": draft,
            "journey": campaign_journey(request, draft),
            "budget_display": _format_budget(draft.media_budget_minor, draft.currency),
        },
    )


@login_required
def campaign_report(request, draft_id):
    """Show an honest report shell until verified channel data is available."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    report_window = (
        ReportingWindow(draft.flight_start, draft.flight_end)
        if draft.flight_start and draft.flight_end
        else None
    )
    return render(
        request,
        "campaigns/report.html",
        {
            "draft": draft,
            "report_metrics": unavailable_campaign_report_metrics(
                window=report_window,
                currency=draft.currency,
            ),
            "planned_report_window": report_window,
            "observed_report_window": None,
            "report_freshness_status": "Kaynak verisi yok; güncellik doğrulanamıyor",
        },
    )


@login_required
@require_POST
def campaign_generate_creatives(request, draft_id):
    """Create a provider-free synthetic creative version for the owner."""

    get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    generate_creative_version_for_owner(owner=request.user, draft_id=draft_id)
    return redirect("campaigns:detail", draft_id=draft_id)


@login_required
@require_POST
def campaign_select_preferred_creative(request, draft_id):
    """Record the owner's informational preference for one current variant."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    try:
        version_number = int(request.POST.get("version", ""))
    except (TypeError, ValueError):
        return redirect(
            f"{reverse('campaigns:detail', args=[draft_id])}?creative_preference=stale"
        )
    result = "saved"
    try:
        select_preferred_creative_for_owner(
            owner=request.user,
            draft_id=draft_id,
            version_number=version_number,
            key=request.POST.get("variant_key", ""),
        )
    except ValidationError:
        result = "stale"
    return redirect(
        f"{reverse('campaigns:detail', args=[draft.pk])}?creative_preference={result}"
    )


@login_required
@require_POST
def campaign_edit_creative(request, draft_id):
    """Save a bounded text edit as a new owner-scoped synthetic version."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user).select_related(
            "workspace"
        ),
        pk=draft_id,
    )
    form = CreativeVariantEditForm(request.POST)
    if not form.is_valid():
        current_versions = draft.creative_versions or []
        current_version = current_versions[-1] if current_versions else None
        if not current_version or not any(
            variant.get("key") == form["variant_key"].value()
            for variant in current_version.get("variants", [])
        ):
            return redirect(
                f"{reverse('campaigns:detail', args=[draft.pk])}?creative_edit=stale"
            )
        return _campaign_detail_response(request, draft, bound_edit_form=form)
    try:
        edit_creative_variant_for_owner(
            owner=request.user,
            draft_id=draft_id,
            version_number=form.cleaned_data["version"],
            key=form.cleaned_data["variant_key"],
            headline=form.cleaned_data["headline"],
            body=form.cleaned_data["body"],
            call_to_action=form.cleaned_data["call_to_action"],
        )
    except ValidationError:
        return redirect(
            f"{reverse('campaigns:detail', args=[draft.pk])}?creative_edit=stale"
        )
    return redirect(
        f"{reverse('campaigns:detail', args=[draft.pk])}?creative_edit=saved"
    )


@login_required
@require_POST
def campaign_restore_creative(request, draft_id):
    """Restore an owner's prior creative snapshot as a new version."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    try:
        version_number = int(request.POST.get("version", ""))
        restore_creative_version_for_owner(
            owner=request.user,
            draft_id=draft.pk,
            version_number=version_number,
        )
    except (TypeError, ValueError, ValidationError):
        return redirect(
            f"{reverse('campaigns:detail', args=[draft.pk])}?creative_edit=stale"
        )
    return redirect(
        f"{reverse('campaigns:detail', args=[draft.pk])}?creative_edit=restored"
    )


@login_required
def campaign_edit(request, draft_id):
    """Change only bounded synthetic budget and duration options."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    initial_duration = (
        (draft.flight_end - draft.flight_start).days
        if draft.flight_start and draft.flight_end
        else 14
    )
    form = CampaignDraftEditForm(
        request.POST or None,
        initial={
            "media_budget_minor": str(draft.media_budget_minor),
            "duration_days": str(initial_duration),
            "synthetic_confirmation": True,
        },
    )
    if request.method == "POST" and form.is_valid():
        today = timezone.localdate()
        update_campaign_draft_for_owner(
            owner=request.user,
            draft_id=draft.pk,
            media_budget_minor=int(form.cleaned_data["media_budget_minor"]),
            flight_start=today + timedelta(days=1),
            flight_end=today
            + timedelta(days=1 + int(form.cleaned_data["duration_days"])),
        )
        return redirect("campaigns:detail", draft_id=draft.pk)

    return render(
        request,
        "campaigns/edit.html",
        {"draft": draft, "form": form},
    )


@login_required
@require_POST
def campaign_rehearsal(request, draft_id):
    """Apply an owner-scoped fake-channel action without external dispatch."""

    get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user), pk=draft_id
    )
    result = "updated"
    try:
        perform_campaign_rehearsal(
            owner=request.user,
            draft_id=draft_id,
            action=request.POST.get("action", ""),
            expected_revision=int(request.POST.get("revision", "")),
            expected_fingerprint=request.POST.get("fingerprint", ""),
        )
    except (ValueError, ValidationError):
        result = "changed"
    return redirect(
        f"{reverse('campaigns:detail', args=[draft_id])}"
        f"?rehearsal={result}#publishing-rehearsal"
    )


@login_required
@require_POST
def campaign_delete(request, draft_id):
    """Remove only the authenticated owner's draft, and only on POST."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    if request.POST.get("confirm_delete") != "on":
        return redirect("campaigns:detail", draft_id=draft.pk)
    try:
        draft.delete()
    except ProtectedError:
        return HttpResponse(
            "Bu taslağın korunması gereken işlem veya seçim geçmişi var. Geçmişi korumak için silinmedi.",
            status=409,
        )
    return redirect("campaigns:list")
