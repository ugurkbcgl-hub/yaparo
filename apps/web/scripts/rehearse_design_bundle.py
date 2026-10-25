"""No-input fresh-DB portability proof; NOT a general archive importer.

Only reads the archive created in this process from its fabricated source DB.
No configured DB, user file, path argument, server or provider is accepted.
"""

import json
import os
import secrets
import stat
import sys
import tempfile
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.rehearse_raster_recovery import _private_windows, _require


def _exercise(root):
    from django.conf import settings as runtime_settings

    _require(not runtime_settings.configured)
    _require(not any(root.iterdir()))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.test_settings"
    os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(48)
    os.environ["POSTGRES_DB"] = "synthetic_unused"
    os.environ["POSTGRES_USER"] = "synthetic_unused"
    import config.test_settings as settings

    settings.DEBUG = True
    settings.SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED = True
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(root / "source.sqlite3"),
        }
    }
    import django

    django.setup()
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from django.db import connection
    from PIL import Image

    from growthtwin.modules.assets.durable_rasters import (
        create_palette_material,
        read_palette_material,
    )
    from growthtwin.modules.assets.models import (
        BrandMaterial,
        BrandMaterialVersion,
        MaterialRasterPair,
    )
    from growthtwin.modules.workspaces.creative_documents import (
        create_document,
        save_document,
    )
    from growthtwin.modules.workspaces.design_bundle import (
        IDENTITY_FIELDS,
        export_design_bundle,
    )
    from growthtwin.modules.workspaces.models import Workspace
    from growthtwin.modules.workspaces.services import (
        create_brand_for_owner,
        update_brand_identity_for_owner,
    )

    def new_brand(username, pk):
        owner = get_user_model().objects.create_user(pk=pk, username=username)
        workspace = Workspace.objects.create(owner=owner, name="Synthetic portability")
        return owner, create_brand_for_owner(
            owner=owner, workspace_id=workspace.pk, fixture="product"
        )

    def second_identity(owner, brand, values):
        return update_brand_identity_for_owner(
            owner=owner,
            brand_id=brand.pk,
            expected_version=1,
            **{
                field: values[field]
                for field in ("primary_color", "secondary_color", "tone", "tagline_key")
            },
        )

    try:
        call_command("migrate", interactive=False, verbosity=0)
        owner, brand = new_brand("bundle-source-fixture", 1)
        pair = create_palette_material(owner=owner, brand_id=brand.pk)
        second_identity(
            owner,
            brand,
            dict(
                primary_color="#254d9b",
                secondary_color="#eaf0ff",
                tone="energetic",
                tagline_key="daily_detail",
            ),
        )
        document = create_document(
            owner=owner,
            brand_id=brand.pk,
            expected_identity_version=2,
            request_id=uuid4(),
            palette_material_id=pair.version.material_id,
            design_format="portrait",
        )
        scene = json.loads(json.dumps(document.scene))
        scene["layers"][2]["text"] = "Özgün sentetik paket · Şığ"
        scene["layers"][0]["x"] = 180
        save_document(
            owner=owner,
            brand_id=brand.pk,
            document_id=document.pk,
            expected_revision=1,
            scene=scene,
        )
        data = export_design_bundle(
            owner=owner, brand_id=brand.pk, document_id=document.pk
        )
        with (root / "design.zip").open("xb") as output:
            output.write(data)
        connection.close()
        source_hash = sha256((root / "source.sqlite3").read_bytes()).hexdigest()
        archive_hash = sha256(data).hexdigest()
        # Read only our fresh process-generated archive; never extract paths.
        with ZipFile(BytesIO((root / "design.zip").read_bytes())) as archive:
            _require(
                set(archive.namelist())
                == {
                    "manifest.json",
                    "scene.json",
                    "README.txt",
                    "assets/hero-original.png",
                    "assets/hero-normalized.png",
                }
            )
            manifest = json.loads(archive.read("manifest.json"))
            recovered_scene = json.loads(archive.read("scene.json"))
            blobs = {path: archive.read(path) for path in manifest["files"]}
            for path, proof in manifest["files"].items():
                _require(
                    len(blobs[path]) == proof["size"]
                    and sha256(blobs[path]).hexdigest() == proof["sha256"]
                )
        _require(manifest["package_version"] == 1 and recovered_scene == scene)
        _require(
            recovered_scene["schema_version"] == 4
            and recovered_scene["format"] == "portrait"
            and (recovered_scene["width"], recovered_scene["height"]) == (800, 1000)
        )
        source = next(row for row in manifest["sources"] if row["layer_id"] == "hero")
        _require(
            source["identity"]["version"] == 1
            and manifest["document"]["identity"]["version"] == 2
        )
        connection.settings_dict["NAME"] = str(root / "target.sqlite3")
        call_command("migrate", interactive=False, verbosity=0)
        target_owner, target_brand = new_brand("bundle-target-fixture", 9001)
        _require(
            {
                field: getattr(target_brand.current_identity, field)
                for field in IDENTITY_FIELDS
            }
            == source["identity"]
        )
        target_material = BrandMaterial.objects.create(
            brand=target_brand,
            identity=target_brand.current_identity,
            source_key=source["source_key"],
        )
        target_version = BrandMaterialVersion.objects.create(
            material=target_material, **source["catalog"]
        )
        original, derivative = (
            blobs[source["files"][kind]] for kind in ("original", "normalized")
        )
        MaterialRasterPair.objects.create(
            version=target_version,
            original=original,
            derivative=derivative,
            original_sha256=sha256(original).hexdigest(),
            derivative_sha256=sha256(derivative).hexdigest(),
            original_size=len(original),
            derivative_size=len(derivative),
            tool=source["tool"],
        )
        second_identity(target_owner, target_brand, manifest["document"]["identity"])
        recovered = create_document(
            owner=target_owner,
            brand_id=target_brand.pk,
            expected_identity_version=2,
            request_id=uuid4(),
            palette_material_id=target_material.pk,
            design_format=recovered_scene.get("format"),
        )
        saved = save_document(
            owner=target_owner,
            brand_id=target_brand.pk,
            document_id=recovered.pk,
            expected_revision=1,
            scene=recovered_scene,
        )
        _require(saved.pk != document.pk and saved.scene == recovered_scene)
        checked = read_palette_material(
            owner=target_owner, brand_id=target_brand.pk, material_id=target_material.pk
        )
        _require(
            bytes(checked.original) == original
            and bytes(checked.derivative) == derivative
        )
        with Image.open(BytesIO(bytes(checked.derivative))) as image:
            image.load()
            _require(
                image.size == (320, 200)
                and image.getpixel((100, 100)) == (36, 76, 59, 255)
            )
        # The recreated workspace can export again without the source database.
        repeated = export_design_bundle(
            owner=target_owner, brand_id=target_brand.pk, document_id=recovered.pk
        )
        with ZipFile(BytesIO(repeated)) as archive:
            _require(archive.read("scene.json") == blobs["scene.json"])
            _require(archive.read("assets/hero-normalized.png") == derivative)
            target_manifest = json.loads(archive.read("manifest.json"))
            _require(
                [
                    {key: value for key, value in row.items() if key != "material_id"}
                    for row in target_manifest["sources"]
                ]
                == [
                    {key: value for key, value in row.items() if key != "material_id"}
                    for row in manifest["sources"]
                ]
            )
        connection.close()
        _require(
            sha256((root / "source.sqlite3").read_bytes()).hexdigest() == source_hash
        )
        _require(sha256((root / "design.zip").read_bytes()).hexdigest() == archive_hash)
        return {
            "scene_recreated_in_fresh_workspace": True,
            "source_identity_preserved": True,
            "png_bytes_and_pixels_match": True,
            "reexport_without_source_db": True,
            "source_db_and_archive_unchanged": True,
        }
    finally:
        connection.close()


def main():
    if len(sys.argv) != 1:
        print(json.dumps({"ok": False, "reason": "no_arguments_allowed"}))
        return 1
    root = Path(tempfile.mkdtemp(prefix="yaparo-design-bundle-"))
    identity = root.stat().st_dev, root.stat().st_ino
    result = {"ok": False}
    try:
        if os.name == "nt":
            _private_windows(root)
        else:
            root.chmod(0o700)
        result.update(_exercise(root))
        result["ok"] = True
    except Exception:
        result = {"ok": False, "reason": "bundle_rehearsal_failed"}
    finally:
        try:
            info = root.stat(follow_symlinks=False)
            _require(
                stat.S_ISDIR(info.st_mode) and (info.st_dev, info.st_ino) == identity
            )
            _require(
                not getattr(info, "st_file_attributes", 0)
                & stat.FILE_ATTRIBUTE_REPARSE_POINT
            )
            files = set(root.iterdir())
            _require(
                files
                <= {
                    root / name
                    for name in ("source.sqlite3", "target.sqlite3", "design.zip")
                }
            )
            for path in files:
                entry = path.stat(follow_symlinks=False)
                _require(stat.S_ISREG(entry.st_mode) and entry.st_nlink == 1)
                _require(
                    not getattr(entry, "st_file_attributes", 0)
                    & stat.FILE_ATTRIBUTE_REPARSE_POINT
                )
            for path in files:
                path.unlink()
            root.rmdir()
            result["private_fixture_cleanup"] = True
        except Exception:
            result["ok"] = False
            result["private_fixture_cleanup"] = False
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
