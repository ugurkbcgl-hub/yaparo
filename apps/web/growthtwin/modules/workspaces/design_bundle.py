"""Read-only, bounded ZIP export of an owned saved synthetic design.

No importer, extraction, customer file, filesystem write or external request.
Fixed illustrations/logo are renderer metadata, not fabricated original files.
"""

import json
from hashlib import sha256
from io import BytesIO
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from django.core.exceptions import ValidationError
from django.db import transaction

from growthtwin.modules.assets.durable_rasters import _enabled, read_palette_material

from .creative_documents import _brand, _document, _scene, _uuid
from .creative_materials import checked_materials

MAX_PACKAGE_BYTES = 12 * 1024 * 1024
IDENTITY_FIELDS = (
    "version",
    "primary_color",
    "secondary_color",
    "tone",
    "tagline_key",
    "tagline_text",
    "logo_key",
)
CATALOG_FIELDS = (
    "version",
    "display_name",
    "media_type",
    "byte_size",
    "width",
    "height",
    "source_label",
    "rights_label",
    "catalog_digest",
)
README = (
    "Yaparo sentetik tasarım paketi v1\n"
    "Kaydedilmiş sahneyi, sabit kaynak bilgisini ve seçilmiş palet görselinin "
    "orijinal/normalize PNG dosyalarını içerir. Kaydedilmemiş değişiklikler ve "
    "kayıt geçmişi dahil değildir.\n"
    "Uyumlu Yaparo çizicisi gerekir: yaparo-scene-v1-v3. Sabit çizim/logo "
    "bilgisi dosya veya dosya hash'i değildir. Arial sistemde bulunmalıdır; "
    "font dosyası pakete eklenmez.\n"
    "Bu paket tek başına editör, genel içe aktarma hizmeti, hak/tarama belgesi, "
    "veritabanı yedeği veya reklam yayın paketi değildir.\n"
).encode("utf-8")


def _json(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def export_design_bundle(*, owner, brand_id, document_id):
    """Freeze one saved revision under the same owned brand/document locks."""
    _enabled()
    _uuid(document_id)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        document = _document(brand, document_id, lock=True)
        scene = _scene(document.scene, brand.fixture)
        checked_materials(document)
        if document.material_binding_version != 1:
            raise ValidationError(
                "Eski çalışmanın kaynak bağı yok; sahne JSON'unu indirin."
            )
        entries = {"scene.json": _json(scene), "README.txt": README}
        sources = []
        for binding in document.material_bindings.select_related(
            "material_version__material__identity"
        ):
            version = binding.material_version
            material = version.material
            source = {
                "layer_id": binding.layer_id,
                "material_id": str(material.pk),
                "source_key": material.source_key,
                "identity": {
                    field: getattr(material.identity, field)
                    for field in IDENTITY_FIELDS
                },
                "catalog": {field: getattr(version, field) for field in CATALOG_FIELDS},
                "kind": "fixed_renderer_metadata",
                "files": {},
            }
            if scene["schema_version"] == 3 and binding.layer_id == "hero":
                pair = read_palette_material(
                    owner=owner, brand_id=brand.pk, material_id=material.pk
                )
                if pair.version_id != version.pk:
                    raise ValidationError("Görsel sürümü kaynak bağıyla eşleşmiyor.")
                source.update(kind="generated_palette_png", tool=pair.tool)
                for kind, data in (
                    ("original", bytes(pair.original)),
                    ("normalized", bytes(pair.derivative)),
                ):
                    path = f"assets/hero-{kind}.png"
                    entries[path] = data
                    source["files"][kind] = path
            sources.append(source)
        manifest = {
            "package_version": 1,
            "renderer_contract": "yaparo-scene-v1-v3",
            "document": {
                "id": str(document.pk),
                "revision": document.revision,
                "fixture": brand.fixture,
                "identity": {
                    field: getattr(document.identity, field)
                    for field in IDENTITY_FIELDS
                },
            },
            "font": {"family": "Arial", "bundled": False, "requirement": "system_font"},
            "sources": sources,
            "files": {
                path: {"size": len(data), "sha256": sha256(data).hexdigest()}
                for path, data in entries.items()
            },
        }
        entries["manifest.json"] = _json(manifest)
        if (
            len(entries["manifest.json"]) > 65536
            or sum(map(len, entries.values())) > MAX_PACKAGE_BYTES - 4096
        ):
            raise ValidationError("Tasarım paketi boyut sınırını aşıyor.")
        output = BytesIO()
        with ZipFile(output, "w", compression=ZIP_STORED) as archive:
            for path, data in sorted(entries.items()):
                info = ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100600 << 16
                archive.writestr(info, data)
        result = output.getvalue()
        if len(result) > MAX_PACKAGE_BYTES:
            raise ValidationError("Tasarım paketi boyut sınırını aşıyor.")
        return result
