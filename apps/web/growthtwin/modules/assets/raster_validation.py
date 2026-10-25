"""Bounded raster normalization for the isolated synthetic material experiment.

Pillow is an optional development dependency. No file, URL or provider access is
performed here. This validates image structure, not malware or legal rights.
"""

import warnings
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO

MAX_SOURCE_BYTES = 3 * 1024 * 1024
MAX_DERIVATIVE_BYTES = 8 * 1024 * 1024
MAX_EDGE = 4096
MAX_PIXELS = 4_000_000
MEDIA_FORMATS = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}


class RasterRejected(ValueError):
    """Fixed safe error: no file contents or parser diagnostics escape."""


@dataclass(frozen=True, repr=False)
class NormalizedRaster:
    png: bytes
    source_sha256: str
    derivative_sha256: str
    source_size: int
    width: int
    height: int
    tool: str


def normalize_raster(source, *, declared_media_type):
    """Verify, fully decode and copy pixels into a metadata-free RGBA PNG."""
    if (
        type(source) is not bytes
        or not 1 <= len(source) <= MAX_SOURCE_BYTES
        or type(declared_media_type) is not str
        or declared_media_type not in MEDIA_FORMATS
    ):
        raise RasterRejected("Raster input rejected.")
    # Lazy import keeps ordinary application runtime independent of the lab.
    from PIL import Image, ImageOps, __version__

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            expected = MEDIA_FORMATS[declared_media_type]
            with Image.open(BytesIO(source), formats=[expected]) as probe:
                width, height = probe.size
                if (
                    probe.format != expected
                    or getattr(probe, "n_frames", 1) != 1
                    or not 1 <= width <= MAX_EDGE
                    or not 1 <= height <= MAX_EDGE
                    or width * height > MAX_PIXELS
                ):
                    raise RasterRejected("Raster input rejected.")
                probe.verify()
            with Image.open(BytesIO(source), formats=[expected]) as decoded:
                decoded.load()
                oriented = ImageOps.exif_transpose(decoded)
                rgba = oriented.convert("RGBA")
                # A fresh image drops EXIF, comments, profiles and unknown chunks.
                with Image.frombytes("RGBA", rgba.size, rgba.tobytes()) as clean:
                    output = BytesIO()
                    clean.save(output, format="PNG", optimize=False)
                    png = output.getvalue()
                    width, height = clean.size
            if not 1 <= len(png) <= MAX_DERIVATIVE_BYTES:
                raise RasterRejected("Raster input rejected.")
    except Exception:
        raise RasterRejected("Raster input rejected.") from None
    return NormalizedRaster(
        png=png,
        source_sha256=sha256(source).hexdigest(),
        derivative_sha256=sha256(png).hexdigest(),
        source_size=len(source),
        width=width,
        height=height,
        tool=f"Pillow/{__version__}:rgba-png-v1",
    )
