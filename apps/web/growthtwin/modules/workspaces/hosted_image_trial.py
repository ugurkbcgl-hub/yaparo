"""One-shot fixed-source hosted image, bounded bytes and durable paid intent."""

import os
import struct
from decimal import Decimal
from hashlib import sha256

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.utils import timezone

from growthtwin.modules.ai_gateway.brand_sample import IMAGE_PROMPT
from growthtwin.modules.ai_gateway.evaluation_budget import (
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openrouter_image import (
    MODEL,
    PNG_SIGNATURE,
    PROVIDER,
    RESERVATION_USD,
    _image_format,
    generate_image,
)
from growthtwin.modules.assets.raster_validation import (
    MAX_DERIVATIVE_BYTES,
    MAX_EDGE,
    MAX_PIXELS,
    MAX_SOURCE_BYTES,
    normalize_raster,
)

from .hosted_trial import admitted_workspace as text_workspace
from .models import HostedImageTrial, Workspace

PROFILE = "fixed-duru-hosted-image-v1"
SOURCE_HASH = sha256(IMAGE_PROMPT.encode()).hexdigest()


def admitted_workspace(owner):
    if not settings.LOCAL_HOSTED_IMAGE_TRIAL_ENABLED:
        raise PermissionDenied
    return text_workspace(owner)


def read_trial(owner):
    workspace = admitted_workspace(owner)
    job = (
        HostedImageTrial.objects.filter(workspace=workspace)
        .defer("original", "png")
        .first()
    )
    if job is not None and (
        job.owner_id != owner.pk
        or job.profile != PROFILE
        or job.source_hash != SOURCE_HASH
    ):
        raise PermissionDenied
    return job


def checked_image(job):
    if job is None or job.status != "completed":
        raise ValueError("Image not completed")
    original, png = bytes(job.original), bytes(job.png)
    if (
        job.profile != PROFILE
        or job.source_hash != SOURCE_HASH
        or job.budget_state != "settled"
        or job.actual_usd is None
        or not 0 <= job.actual_usd <= job.reserved_usd <= Decimal("0.10")
        or job.model != MODEL
        or job.provider != PROVIDER
        or not 1 <= len(original) <= MAX_SOURCE_BYTES
        or not 24 <= len(png) <= MAX_DERIVATIVE_BYTES
        or sha256(original).hexdigest() != job.original_sha256
        or sha256(png).hexdigest() != job.png_sha256
        or not png.startswith(PNG_SIGNATURE)
        or _image_format(original)[0] != job.source_media_type
        or not 1 <= job.width <= MAX_EDGE
        or not 1 <= job.height <= MAX_EDGE
        or job.width * job.height > MAX_PIXELS
        or struct.unpack(">II", png[16:24]) != (job.width, job.height)
    ):
        raise ValueError("Image verification refused")
    return png


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
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key.strip() or len(api_key) > 512 or any(c in api_key for c in "\r\n"):
        raise PermissionDenied
    reservation = RESERVATION_USD
    with transaction.atomic():
        workspace = admitted_workspace(owner)
        Workspace.objects.select_for_update().get(
            pk=workspace.pk, owner=owner, owner__is_active=True
        )
        job, created = HostedImageTrial.objects.get_or_create(
            workspace=workspace,
            defaults={
                "owner": owner,
                "profile": PROFILE,
                "source_hash": SOURCE_HASH,
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
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="started").update(
            budget_state=budget_state
        )
        if changed != 1:
            raise ValueError("Reservation intent refused")
        ledger = reserve_evaluation_cost(reservation, per_request_limit_usd=reservation)
        budget_state = "held"
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="started").update(
            budget_state=budget_state
        )
        if changed != 1:
            raise ValueError("Reservation record refused")
        original, extension, actual_cost = generate_image(api_key, prompt=IMAGE_PROMPT)
        cost = Decimal(str(actual_cost))
        if not cost.is_finite() or not 0 <= cost <= Decimal(str(reservation)):
            raise ValueError("Unverified image cost")
        # Retain known cost even if structural validation later refuses the image.
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="started").update(
            status="received",
            actual_usd=cost,
            model=MODEL,
            provider=PROVIDER,
        )
        if changed != 1:
            raise ValueError("Cost capture refused")
        if type(original) is not bytes or not 1 <= len(original) <= MAX_SOURCE_BYTES:
            raise ValueError("Image exceeds storage bound")
        media_type, detected_extension = _image_format(original)
        if extension != detected_extension:
            raise ValueError("Unverified image format")
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="received").update(
            original=original,
            original_sha256=sha256(original).hexdigest(),
            source_media_type=media_type,
        )
        if changed != 1:
            raise ValueError("Original capture refused")
        normalized = normalize_raster(original, declared_media_type=media_type)
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="received").update(
            png=normalized.png,
            png_sha256=normalized.derivative_sha256,
            width=normalized.width,
            height=normalized.height,
            normalization_tool=normalized.tool,
        )
        if changed != 1:
            raise ValueError("Image capture refused")
        budget_state = "unknown"
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="received").update(
            budget_state=budget_state
        )
        if changed != 1:
            raise ValueError("Settlement intent refused")
        settle_evaluation_cost(ledger, reservation, float(cost))
        budget_state = "settled"
        changed = HostedImageTrial.objects.filter(pk=job.pk, status="received").update(
            status="completed", budget_state=budget_state, completed_at=timezone.now()
        )
        if changed != 1:
            raise ValueError("Completion write refused")
    except Exception:
        # No response/exception body, key or traceback enters result/log/UI.
        # If this write also fails the committed row still blocks another call.
        try:
            HostedImageTrial.objects.filter(pk=job.pk).exclude(
                status="completed"
            ).update(status="unverified", budget_state=budget_state)
        except Exception:
            pass
    return read_trial(owner)
