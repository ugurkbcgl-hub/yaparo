"""Synthetic, workspace-owned campaign drafts."""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from growthtwin.modules.workspaces.models import Workspace


class WorkspaceCampaignDraftQuerySet(models.QuerySet):
    """Query helpers that make workspace ownership explicit at call sites."""

    def owned_by(self, user):
        return self.filter(workspace__owner=user)


class WorkspaceCampaignDraft(models.Model):
    """A locally planned campaign, separate from anonymous prototype drafts."""

    class Objective(models.TextChoices):
        LEAD_GENERATION = "lead_generation", "Lead generation"

    class Channel(models.TextChoices):
        GOOGLE_SEARCH = "google_search", "Google Search"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="campaign_drafts",
    )
    name = models.CharField(max_length=120)
    brand_name = models.CharField(max_length=120, blank=True, default="")
    brand = models.ForeignKey(
        "workspaces.Brand",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="campaign_plans",
    )
    objective = models.CharField(
        max_length=32,
        choices=Objective.choices,
        default=Objective.LEAD_GENERATION,
    )
    channel = models.CharField(
        max_length=32,
        choices=Channel.choices,
        default=Channel.GOOGLE_SEARCH,
    )
    brief = models.TextField(max_length=4000)
    target_city = models.CharField(max_length=100)
    destination_url = models.URLField(max_length=500, blank=True)
    creative_versions = models.JSONField(blank=True, default=list)
    preferred_creative_key = models.CharField(max_length=64, blank=True, default="")
    preferred_creative_version = models.PositiveIntegerField(null=True, blank=True)
    media_budget_minor = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Integer minor units; independent of GrowthTwin fees and credits.",
    )
    currency = models.CharField(max_length=3, default="TRY")
    flight_start = models.DateField(null=True, blank=True)
    flight_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceCampaignDraftQuerySet.as_manager()

    class Meta:
        ordering = ("-updated_at", "pk")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(media_budget_minor__gt=0),
                name="campaign_draft_positive_media_budget",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(flight_start__isnull=True)
                    | models.Q(flight_end__isnull=True)
                    | models.Q(flight_end__gte=models.F("flight_start"))
                ),
                name="campaign_draft_flight_dates_ordered",
            ),
        ]


class CampaignDesignChoiceQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Tasarım seçimi geçmişi değiştirilemez.")

    def delete(self):
        raise ValidationError("Tasarım seçimi geçmişi tek başına silinemez.")

    def bulk_update(self, objs, fields, **kwargs):
        raise ValidationError("Tasarım seçimi geçmişi değiştirilemez.")


class CampaignDesignChoice(models.Model):
    """Append-only local planning reference; never publishing approval."""

    draft = models.ForeignKey(
        WorkspaceCampaignDraft, on_delete=models.CASCADE, related_name="design_choices"
    )
    snapshot = models.ForeignKey(
        "workspaces.BrandCreativeRevision",
        on_delete=models.PROTECT,
        related_name="campaign_choices",
    )
    version = models.PositiveIntegerField()
    request_id = models.UUIDField(unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CampaignDesignChoiceQuerySet.as_manager()

    class Meta:
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(
                fields=("draft", "version"), name="campaign_design_version_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="campaign_design_version_positive",
            ),
        ]

    def clean(self):
        super().clean()
        if (
            self.draft_id
            and self.snapshot_id
            and self.draft.workspace_id
            != self.snapshot.document.identity.brand.workspace_id
        ):
            raise ValidationError("Tasarım aynı çalışma alanına ait olmalıdır.")

    def save(self, *args, **kwargs):
        if not self._state.adding or self.pk is not None:
            raise ValidationError("Tasarım seçimi geçmişi değiştirilemez.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Tasarım seçimi geçmişi tek başına silinemez.")


class CampaignHostedAdChoice(models.Model):
    """Separate append-only hosted-trial visual planning reference."""

    campaign = models.ForeignKey(
        WorkspaceCampaignDraft,
        on_delete=models.CASCADE,
        related_name="hosted_ad_choices",
    )
    revision = models.ForeignKey(
        "workspaces.HostedAdRevision",
        on_delete=models.PROTECT,
        related_name="campaign_choices",
    )
    snapshot = models.JSONField()
    version = models.PositiveIntegerField()
    request_id = models.UUIDField(unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CampaignDesignChoiceQuerySet.as_manager()

    class Meta:
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(
                fields=("campaign", "version"), name="campaign_hosted_ad_version_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="campaign_hosted_ad_version_positive",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding or self.pk is not None:
            raise ValidationError("Görsel seçimi geçmişi değiştirilemez.")
        if self.campaign.workspace_id != self.revision.draft.workspace_id:
            raise ValidationError("Görsel aynı çalışma alanına ait olmalıdır.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Görsel seçimi geçmişi tek başına silinemez.")


class CampaignBrandAdChoice(models.Model):
    """Immutable owned-brand visual planning choice, never publishing authority."""

    campaign = models.ForeignKey(
        WorkspaceCampaignDraft,
        on_delete=models.CASCADE,
        related_name="brand_ad_choices",
    )
    revision = models.ForeignKey(
        "workspaces.BrandAdRevision",
        on_delete=models.PROTECT,
        related_name="campaign_choices",
    )
    snapshot = models.JSONField()
    version = models.PositiveIntegerField()
    request_id = models.UUIDField(unique=True, editable=False)
    kind = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CampaignDesignChoiceQuerySet.as_manager()

    class Meta:
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(
                fields=("campaign", "version"), name="campaign_brand_ad_version_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="campaign_brand_ad_positive"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding or self.pk is not None:
            raise ValidationError("Marka reklam seçimi geçmişi değiştirilemez.")
        ad = self.revision.draft
        if (
            self.kind not in ("create", "select")
            or self.campaign.brand_id != ad.brand_id
            or self.campaign.workspace_id != ad.brand.workspace_id
        ):
            raise ValidationError("Kampanya ve reklam aynı markaya ait olmalıdır.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Marka reklam seçimi geçmişi silinemez.")


class CampaignRehearsal(models.Model):
    """Synthetic lifecycle only; never authorizes external dispatch."""

    class State(models.TextChoices):
        IDLE = "idle", "Henüz başlamadı"
        RUNNING = "running", "Prova çalışıyor"
        FAILED = "failed", "Prova başarısız"
        STOPPED = "stopped", "Prova durduruldu"

    draft = models.OneToOneField(
        WorkspaceCampaignDraft, on_delete=models.CASCADE, related_name="rehearsal"
    )
    state = models.CharField(max_length=16, choices=State.choices, default=State.IDLE)
    revision = models.PositiveIntegerField(default=0)
    operation_id = models.UUIDField(null=True, blank=True)
    fingerprint = models.CharField(max_length=64, blank=True, default="")
    receipt = models.CharField(max_length=100, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)


class CampaignRehearsalEvent(models.Model):
    """Compact, immutable application history with no creative or private payload."""

    class Action(models.TextChoices):
        START = "start", "Prova başlatıldı"
        START_FAILURE = "start_failure", "Başarısızlık denendi"
        RETRY = "retry", "Prova yeniden denendi"
        STOP = "stop", "Prova durduruldu"

    rehearsal = models.ForeignKey(
        CampaignRehearsal, on_delete=models.CASCADE, related_name="events"
    )
    revision = models.PositiveIntegerField()
    action = models.CharField(max_length=16, choices=Action.choices)
    state = models.CharField(max_length=16, choices=CampaignRehearsal.State.choices)
    operation_id = models.UUIDField()
    receipt = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-revision",)
        constraints = [
            models.UniqueConstraint(
                fields=("rehearsal", "revision"), name="rehearsal_unique_event_revision"
            )
        ]


class GoogleTestCampaign(models.Model):
    """Durable intent for one local, synthetic Google test operation."""

    workspace = models.OneToOneField(
        "workspaces.Workspace",
        on_delete=models.PROTECT,
        related_name="google_test_campaign",
    )
    operation_id = models.UUIDField(unique=True)
    configuration_key = models.CharField(max_length=64)
    state = models.CharField(max_length=20, default="uncertain")
    resource_name = models.CharField(max_length=120, blank=True)
    observed_status = models.CharField(max_length=16, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class GoogleDraftApproval(models.Model):
    """Append-only snapshot approval; grants only later paused TEST dispatch."""

    draft = models.ForeignKey(
        WorkspaceCampaignDraft,
        on_delete=models.PROTECT,
        related_name="google_test_approvals",
    )
    fingerprint = models.CharField(max_length=64)
    target_key = models.CharField(max_length=64)
    payload_json = models.TextField()
    approved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("draft", "fingerprint", "target_key"),
                name="unique_google_draft_approval",
            )
        ]


class GoogleDraftDispatch(models.Model):
    """One committed external TEST intent per draft; never reset after ambiguity."""

    draft = models.OneToOneField(WorkspaceCampaignDraft, on_delete=models.PROTECT)
    approval = models.ForeignKey(GoogleDraftApproval, on_delete=models.PROTECT)
    operation_id = models.UUIDField(unique=True)
    configuration_key = models.CharField(max_length=64)
    payload_json = models.TextField()
    state = models.CharField(max_length=20, default="uncertain")
    resource_name = models.CharField(max_length=120, blank=True)
    observed_status = models.CharField(max_length=16, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
