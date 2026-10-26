"""One committed local paid intent over a fixed fictional request, no retries."""

import os
import re
from dataclasses import asdict
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.utils import timezone

from growthtwin.modules.ai_gateway.brand_sample import REQUEST
from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationResult,
    validate_generation_result,
)
from growthtwin.modules.ai_gateway.evaluation_budget import (
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openrouter import (
    OPENROUTER_MODEL,
    OpenRouterCreativeGenerator,
)
from growthtwin.modules.content.creative import CreativeVariant

from .models import HostedTextTrial, Workspace

PROFILE = "fixed-duru-hosted-text-v1"


def admitted_workspace(owner):
    workspace_id = settings.LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID
    if (
        not settings.DEBUG
        or not settings.LOCAL_HOSTED_TEXT_TRIAL_ENABLED
        or type(workspace_id) is not int
        or workspace_id < 1
        or not getattr(owner, "is_authenticated", False)
        or not owner.is_active
    ):
        raise PermissionDenied
    return Workspace.objects.get(pk=workspace_id, owner=owner, owner__is_active=True)


def read_trial(owner):
    workspace = admitted_workspace(owner)
    job = HostedTextTrial.objects.filter(workspace=workspace).first()
    if job is not None and (
        job.owner_id != owner.pk
        or job.profile != PROFILE
        or job.source_hash != REQUEST.source_hash
    ):
        raise PermissionDenied
    return job


def checked_variants(job):
    if job is None or job.status != "completed":
        return ()
    if (
        job.budget_state != "settled"
        or job.actual_usd is None
        or not 0 <= job.actual_usd <= job.reserved_usd <= Decimal("0.01")
        or job.model != OPENROUTER_MODEL
        or not re.fullmatch(r"[A-Za-z0-9 .:_/-]{1,80}", job.provider)
        or not isinstance(job.variants, list)
        or len(job.variants) > 5
        or not isinstance(job.usage, dict)
        or set(job.usage) != {"input_tokens", "output_tokens"}
        or any(type(value) is not int or value < 0 for value in job.usage.values())
        or job.usage.get("input_tokens", 0) > 8192
        or job.usage.get("output_tokens", 0) > 512
    ):
        raise ValueError("Unverified stored result")
    result = CreativeGenerationResult(
        generator_id=f"openrouter-{OPENROUTER_MODEL.replace('/', '-')}",
        source_hash=job.source_hash,
        variants=tuple(CreativeVariant(**row) for row in job.variants),
    )
    return validate_generation_result(REQUEST, result).variants


def generate_trial(owner):
    # The intent must survive any later provider/storage failure. Never execute
    # inside a caller's transaction, including ATOMIC_REQUESTS.
    if connection.in_atomic_block:
        raise PermissionDenied
    existing = read_trial(owner)
    if existing is not None:
        return existing
    if os.environ.get("GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED") != "1":
        raise PermissionDenied
    generator = OpenRouterCreativeGenerator()
    reservation = generator.maximum_reserved_cost(generator.request_body(REQUEST))
    if not 0 < reservation <= 0.01:
        raise PermissionDenied
    with transaction.atomic():
        workspace = admitted_workspace(owner)
        Workspace.objects.select_for_update().get(
            pk=workspace.pk, owner=owner, owner__is_active=True
        )
        job, created = HostedTextTrial.objects.get_or_create(
            workspace=workspace,
            defaults={
                "owner": owner,
                "profile": PROFILE,
                "source_hash": REQUEST.source_hash,
                "reserved_usd": Decimal(str(reservation)),
            },
        )
    if not created:
        # Concurrent clicks cannot both dispatch, even across sessions/processes.
        return read_trial(owner)
    budget_state = "not_reserved"
    try:
        # Recheck revoked scope immediately before reservation/dispatch.
        admitted_workspace(owner)
        budget_state = "unknown"
        changed = HostedTextTrial.objects.filter(pk=job.pk, status="started").update(
            budget_state=budget_state
        )
        if changed != 1:
            raise ValueError("Reservation intent refused")
        ledger = reserve_evaluation_cost(reservation)
        budget_state = "held"
        changed = HostedTextTrial.objects.filter(pk=job.pk, status="started").update(
            budget_state=budget_state
        )
        if changed != 1:
            raise ValueError("Reservation record refused")
        result = generator.generate(REQUEST)
        validate_generation_result(REQUEST, result)
        if (
            generator.last_model != OPENROUTER_MODEL
            or not isinstance(generator.last_provider, str)
            or not re.fullmatch(r"[A-Za-z0-9 .:_/-]{1,80}", generator.last_provider)
            or not isinstance(generator.last_usage, dict)
            or generator.last_cost_usd is None
        ):
            raise ValueError("Unverified provider metadata")
        cost = Decimal(str(generator.last_cost_usd))
        if not cost.is_finite() or not 0 <= cost <= Decimal(str(reservation)):
            raise ValueError("Unverified cost")
        changed = HostedTextTrial.objects.filter(pk=job.pk, status="started").update(
            status="received",
            actual_usd=cost,
            model=generator.last_model,
            provider=generator.last_provider,
            usage=generator.last_usage,
            variants=[asdict(row) for row in result.variants],
        )
        if changed != 1:
            raise ValueError("Result write refused")
        budget_state = "unknown"
        changed = HostedTextTrial.objects.filter(pk=job.pk, status="received").update(
            budget_state=budget_state
        )
        if changed != 1:
            raise ValueError("Settlement intent refused")
        settle_evaluation_cost(ledger, reservation, float(cost))
        budget_state = "settled"
        changed = HostedTextTrial.objects.filter(pk=job.pk, status="received").update(
            status="completed", budget_state=budget_state, completed_at=timezone.now()
        )
        if changed != 1:
            raise ValueError("Completion write refused")
    except Exception:
        # No response/exception body, key or traceback enters result/log/UI.
        # If this write also fails the committed row still blocks another call.
        try:
            HostedTextTrial.objects.filter(pk=job.pk).exclude(
                status="completed"
            ).update(status="unverified", budget_state=budget_state)
        except Exception:
            pass
    return read_trial(owner)
