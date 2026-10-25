"""Explicit owned saved-design reference; separate from Search text/approval."""

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Subquery

from growthtwin.modules.workspaces.creative_documents import (
    _brand,
    _document,
    _owner,
    _scene,
    _uuid,
    _version,
)
from growthtwin.modules.workspaces.creative_materials import checked_materials
from growthtwin.modules.workspaces.models import (
    BrandCreativeDocument,
    BrandCreativeRevision,
)

from .models import CampaignDesignChoice, WorkspaceCampaignDraft


def _enabled():
    if not settings.DEBUG or not settings.SYNTHETIC_CAMPAIGN_DESIGN_ENABLED:
        raise PermissionDenied("Yerel tasarım seçimi kapalı.")


def owned_draft(owner, draft_id):
    _owner(owner)
    return WorkspaceCampaignDraft.objects.get(
        pk=draft_id, workspace__owner=owner, workspace__owner__is_active=True
    )


def _check_document(document):
    _scene(document.scene, document.identity.brand.fixture)
    checked_materials(document)
    if document.material_binding_version != 1:
        raise ValidationError("Kaynak sürümleri bağlı bir tasarım gereklidir.")


def _check_snapshot(document, snapshot):
    _scene(snapshot.scene, document.identity.brand.fixture)
    if any(
        snapshot.scene.get(key) != document.scene.get(key)
        for key in ("schema_version", "width", "height", "format", "hero_source")
    ):
        raise ValidationError("Seçilen kaydın kaynak biçimi doğrulanamadı.")


def select_design(
    *,
    owner,
    draft_id,
    brand_id,
    document_id,
    expected_document_revision,
    expected_selection_version,
    request_id,
):
    _enabled()
    _owner(owner)
    _uuid(document_id)
    _uuid(request_id)
    _version(expected_document_revision)
    if (
        type(expected_selection_version) is not int
        or not 0 <= expected_selection_version < 2**31 - 1
    ):
        raise ValidationError("Geçerli bir seçim sürümü gereklidir.")
    with transaction.atomic():
        # Serialize choice versions on the draft only. Source snapshots are
        # immutable; no brand/workspace/document lock is added to the legacy
        # campaign/brand lock graph. Recheck eligibility in the INSERT itself.
        draft = WorkspaceCampaignDraft.objects.select_for_update(of=("self",)).get(
            pk=draft_id,
            workspace__owner=owner,
            workspace__owner__is_active=True,
        )
        if not BrandCreativeDocument.objects.filter(
            pk=document_id,
            identity__brand_id=brand_id,
            identity__brand__workspace_id=draft.workspace_id,
        ).exists():
            raise BrandCreativeDocument.DoesNotExist
        brand = _brand(owner, brand_id)
        document = _document(brand, document_id)
        _check_document(document)
        existing = (
            CampaignDesignChoice.objects.filter(request_id=request_id)
            .select_related("snapshot")
            .first()
        )
        if existing:
            if (
                existing.draft_id != draft.pk
                or existing.version != expected_selection_version + 1
                or existing.snapshot.document_id != document.pk
                or existing.snapshot.revision != expected_document_revision
            ):
                raise ValidationError("Seçim isteği farklı bir bağlamda kullanılmış.")
            _check_snapshot(document, existing.snapshot)
            return existing
        current = draft.design_choices.first()
        if (current.version if current else 0) != expected_selection_version:
            raise ValidationError("Kampanyanın tasarım seçimi değişmiş.")
        if document.revision != expected_document_revision:
            raise ValidationError("Tasarım değişmiş; güncel kaydı yeniden seçin.")
        snapshot = BrandCreativeRevision.objects.get(
            document=document, revision=document.revision
        )
        _check_snapshot(document, snapshot)
        if snapshot.scene != document.scene:
            raise ValidationError("Tasarımın kayıt geçmişi doğrulanamadı.")
        choice = CampaignDesignChoice(
            draft=draft,
            snapshot=snapshot,
            version=expected_selection_version + 1,
            request_id=request_id,
        )
        choice.full_clean()
        eligible = BrandCreativeRevision.objects.filter(
            pk=snapshot.pk,
            document_id=document.pk,
            document__revision=expected_document_revision,
            document__identity__brand_id=brand.pk,
            document__identity__brand__workspace_id=draft.workspace_id,
            document__identity__brand__workspace__owner=owner,
            document__identity__brand__workspace__owner__is_active=True,
            document__identity__brand__is_archived=False,
        ).values("pk")[:1]
        try:
            with transaction.atomic():
                # No qualifying source yields NULL, rejected by the non-null FK.
                # bulk_create is deliberately internal after full validation;
                # it lets the FK use a scoped SELECT at the write boundary.
                choice.snapshot_id = Subquery(eligible)
                CampaignDesignChoice.objects.bulk_create([choice])
                choice.refresh_from_db()
                return choice
        except IntegrityError:
            raise ValidationError(
                "Seçim isteği başka bir bağlamda kullanılmış."
            ) from None


def current_design(*, owner, draft_id):
    _enabled()
    draft = owned_draft(owner, draft_id)
    choice_id = draft.design_choices.values_list("pk", flat=True).first()
    if choice_id is None:
        return None
    choice = CampaignDesignChoice.objects.select_related(
        "snapshot__document__identity__brand__workspace"
    ).get(
        pk=choice_id,
        draft__workspace_id=draft.workspace_id,
        draft__workspace__owner=owner,
        draft__workspace__owner__is_active=True,
        snapshot__document__identity__brand__workspace_id=draft.workspace_id,
        snapshot__document__identity__brand__workspace__owner=owner,
        snapshot__document__identity__brand__workspace__owner__is_active=True,
        snapshot__document__identity__brand__is_archived=False,
    )
    document = choice.snapshot.document
    brand = _brand(owner, document.identity.brand_id)
    if brand.workspace_id != draft.workspace_id:
        raise PermissionDenied("Tasarım bu çalışma alanında değil.")
    _check_document(document)
    _check_snapshot(document, choice.snapshot)
    return choice


def design_options(*, owner, draft_id):
    _enabled()
    draft = owned_draft(owner, draft_id)
    rows = (
        BrandCreativeDocument.objects.filter(
            identity__brand__workspace_id=draft.workspace_id,
            identity__brand__workspace__owner=owner,
            identity__brand__workspace__owner__is_active=True,
            identity__brand__is_archived=False,
            material_binding_version=1,
        )
        .select_related("identity__brand")
        .order_by("-updated_at")[:20]
    )
    result = []
    for document in rows:
        try:
            _check_document(document)
            snapshot = document.history.get(revision=document.revision)
            _check_snapshot(document, snapshot)
            if snapshot.scene != document.scene:
                continue
        except (ValidationError, BrandCreativeRevision.DoesNotExist):
            continue
        result.append(document)
    return result
