"""Closed catalog for the built-in synthetic scene illustrations.

The catalog is deliberately metadata-only.  Values describe the fixed examples
rendered by the local editor; they are not file hashes and must never be treated
as proof of a customer asset, a malware scan, or a permission to send content to
an external provider.
"""

import json
from dataclasses import dataclass
from hashlib import sha256

ALLOWED_MEDIA_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_BYTES = 3 * 1024 * 1024
MAX_WIDTH = 4096
MAX_HEIGHT = 4096


@dataclass(frozen=True)
class SyntheticMaterialDefinition:
    fixture: str
    source_key: str
    display_name: str
    media_type: str
    byte_size: int | None
    width: int
    height: int
    source_label: str
    rights_label: str

    @property
    def catalog_digest(self):
        """Hash only canonical catalog metadata, never a nonexistent file blob."""

        payload = json.dumps(
            {
                "fixture": self.fixture,
                "source_key": self.source_key,
                "display_name": self.display_name,
                "media_type": self.media_type,
                "byte_size": self.byte_size,
                "width": self.width,
                "height": self.height,
                "source_label": self.source_label,
                "rights_label": self.rights_label,
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return sha256(payload).hexdigest()


_CATALOG = (
    SyntheticMaterialDefinition(
        fixture="product",
        source_key="product:illustration:v1",
        display_name="Seramik ürün illüstrasyonu",
        media_type="image/png",
        byte_size=None,
        width=580,
        height=430,
        source_label="Yaparo sabit sentetik çizim",
        rights_label="Yalnız yerel sentetik deneme",
    ),
    SyntheticMaterialDefinition(
        fixture="product",
        source_key="product:logo:v1",
        display_name="Seramik örneği işareti",
        media_type="image/png",
        byte_size=None,
        width=275,
        height=58,
        source_label="Yaparo sabit sentetik logo",
        rights_label="Yalnız yerel sentetik deneme",
    ),
    SyntheticMaterialDefinition(
        fixture="service",
        source_key="service:illustration:v1",
        display_name="Ev bakımı illüstrasyonu",
        media_type="image/png",
        byte_size=None,
        width=580,
        height=430,
        source_label="Yaparo sabit sentetik çizim",
        rights_label="Yalnız yerel sentetik deneme",
    ),
    SyntheticMaterialDefinition(
        fixture="service",
        source_key="service:logo:v1",
        display_name="Ev bakımı örneği işareti",
        media_type="image/png",
        byte_size=None,
        width=275,
        height=58,
        source_label="Yaparo sabit sentetik logo",
        rights_label="Yalnız yerel sentetik deneme",
    ),
)


def definitions_for_fixture(fixture):
    """Return fixed, independently validated records for one synthetic fixture."""

    if type(fixture) is not str or fixture not in {"product", "service"}:
        raise ValueError("Unknown synthetic material fixture.")
    definitions = tuple(item for item in _CATALOG if item.fixture == fixture)
    if len(definitions) != 2:
        raise ValueError("Synthetic catalog is incomplete.")
    for item in definitions:
        if (
            item.media_type not in ALLOWED_MEDIA_TYPES
            or (item.byte_size is not None and not 1 <= item.byte_size <= MAX_BYTES)
            or not 1 <= item.width <= MAX_WIDTH
            or not 1 <= item.height <= MAX_HEIGHT
            or len(item.catalog_digest) != 64
        ):
            raise ValueError("Synthetic catalog is outside material limits.")
    return definitions
