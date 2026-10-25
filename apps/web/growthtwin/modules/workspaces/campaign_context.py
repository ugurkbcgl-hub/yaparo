"""Optional typed navigation hint; never selection, approval or a redirect URL."""

import re

from django.conf import settings


def campaign_return_id(request, workspace_id):
    value = request.GET.get("campaign", "")
    if (
        not settings.DEBUG
        or not settings.SYNTHETIC_CAMPAIGN_DESIGN_ENABLED
        or not re.fullmatch(r"[1-9][0-9]{0,18}", value)
        or int(value) > 2**63 - 1
    ):
        return None
    from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft

    return (
        WorkspaceCampaignDraft.objects.filter(
            pk=int(value),
            workspace_id=workspace_id,
            workspace__owner=request.user,
            workspace__owner__is_active=True,
        )
        .values_list("pk", flat=True)
        .first()
    )


def with_campaign(url, campaign_id):
    return url + f"?campaign={campaign_id}" if campaign_id else url
