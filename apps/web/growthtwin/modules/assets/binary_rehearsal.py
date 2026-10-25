"""Opt-in generated-raster rehearsal; no routes, uploads or durable asset writes."""

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO

from django.conf import settings
from django.core.exceptions import PermissionDenied

from growthtwin.modules.workspaces.models import Brand

from .private_fixture_store import PrivateFixtureStore
from .raster_validation import normalize_raster


@dataclass(frozen=True)
class RasterEvidence:
    source_media_type: str
    source_sha256: str
    source_bytes: int
    derivative_sha256: str
    derivative_bytes: int
    width: int
    height: int
    tool: str
    structure_verified: bool


@dataclass(frozen=True)
class BinaryRehearsalResult:
    brand_id: int
    identity_version: int
    evidence: tuple[RasterEvidence, ...]
    cleanup_verified: bool


def _brand(owner, brand_id):
    if not getattr(owner, "is_authenticated", False) or not getattr(
        owner, "is_active", False
    ):
        raise PermissionDenied("Active synthetic owner required.")
    return Brand.objects.select_related("workspace").get(
        pk=brand_id,
        workspace__owner=owner,
        workspace__owner__is_active=True,
        is_archived=False,
    )


def _generated_examples(identity):
    from PIL import Image, ImageDraw

    with Image.new("RGB", (64, 48), identity.secondary_color) as image:
        ImageDraw.Draw(image).rectangle((12, 8, 52, 40), fill=identity.primary_color)
        for media_type, format_name in (
            ("image/jpeg", "JPEG"),
            ("image/png", "PNG"),
            ("image/webp", "WEBP"),
        ):
            output = BytesIO()
            image.save(output, format=format_name)
            yield media_type, output.getvalue()


def rehearse_generated_materials(*, owner, brand_id):
    """Exercise original quarantine→normalization→readback→deletion on fixed images.

    The sole inputs identify the owned synthetic brand. Original byte input,
    filesystem paths, scan claims, provider permissions and retries are absent.
    A structure check never records a malware CLEAN result or publication READY.
    """
    if not settings.SYNTHETIC_MATERIAL_BINARY_REHEARSAL_ENABLED or not settings.DEBUG:
        raise PermissionDenied("Synthetic binary rehearsal is disabled.")
    brand = _brand(owner, brand_id)
    identity = brand.current_identity
    evidence = []
    with PrivateFixtureStore() as storage:
        for media_type, original in _generated_examples(identity):
            quarantine_key = storage.put(original)
            normalized = normalize_raster(
                storage.read(quarantine_key), declared_media_type=media_type
            )
            derivative_key = storage.put(normalized.png)
            if (
                storage.read(quarantine_key) != original
                or sha256(storage.read(derivative_key)).hexdigest()
                != normalized.derivative_sha256
            ):
                raise ValueError("Synthetic readback failed.")
            evidence.append(
                RasterEvidence(
                    source_media_type=media_type,
                    source_sha256=normalized.source_sha256,
                    source_bytes=normalized.source_size,
                    derivative_sha256=normalized.derivative_sha256,
                    derivative_bytes=len(normalized.png),
                    width=normalized.width,
                    height=normalized.height,
                    tool=normalized.tool,
                    structure_verified=True,
                )
            )
        _brand(owner, brand_id)  # Recheck owner before reporting the result.
    return BinaryRehearsalResult(
        brand_id=brand.pk,
        identity_version=identity.version,
        evidence=tuple(evidence),
        cleanup_verified=True,
    )
