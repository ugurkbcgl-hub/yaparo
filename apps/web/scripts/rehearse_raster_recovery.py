"""No-input, disposable SQLite backup/restore proof for generated raster rows.

Creates a fresh private directory; never opens an existing or configured DB.
Outputs only scalar evidence. No server, provider, customer data or retry.
"""

import json
import os
import secrets
import sqlite3
import stat
import sys
import tempfile
from contextlib import closing
from hashlib import sha256
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from growthtwin.modules.assets.private_fixture_store import _private_windows


def _require(condition):
    if not condition:
        raise ValueError("Synthetic recovery verification failed.")


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
        delete_palette_material,
        read_palette_material,
    )
    from growthtwin.modules.assets.models import (
        BrandMaterial,
        BrandMaterialVersion,
        MaterialRasterPair,
    )
    from growthtwin.modules.workspaces.models import Workspace
    from growthtwin.modules.workspaces.services import create_brand_for_owner

    try:
        call_command("migrate", interactive=False, verbosity=0)
        owner = get_user_model().objects.create_user(username="recovery-fixture")
        workspace = Workspace.objects.create(owner=owner, name="Synthetic recovery")
        brand = create_brand_for_owner(
            owner=owner, workspace_id=workspace.pk, fixture="product"
        )
        pair = create_palette_material(owner=owner, brand_id=brand.pk)
        material_id = pair.version.material_id
        expected = (
            pair.original_sha256,
            pair.derivative_sha256,
            pair.original_size,
            pair.derivative_size,
            pair.version.material.identity_id,
            pair.version_id,
            pair.tool,
        )
        connection.close()
        source_hash = sha256((root / "source.sqlite3").read_bytes()).hexdigest()
        with closing(sqlite3.connect(root / "source.sqlite3")) as source:
            with closing(sqlite3.connect(root / "backup.sqlite3")) as backup:
                source.backup(backup)
        backup_hash = sha256((root / "backup.sqlite3").read_bytes()).hexdigest()
        with closing(sqlite3.connect(root / "backup.sqlite3")) as backup:
            with closing(sqlite3.connect(root / "restored.sqlite3")) as restored:
                backup.backup(restored)
        connection.settings_dict["NAME"] = str(root / "restored.sqlite3")
        restored_owner = get_user_model().objects.get(pk=owner.pk)
        recovered = read_palette_material(
            owner=restored_owner, brand_id=brand.pk, material_id=material_id
        )
        actual = (
            recovered.original_sha256,
            recovered.derivative_sha256,
            recovered.original_size,
            recovered.derivative_size,
            recovered.version.material.identity_id,
            recovered.version_id,
            recovered.tool,
        )
        _require(expected == actual)
        with Image.open(BytesIO(bytes(recovered.derivative))) as image:
            image.load()
            _require(image.size == (320, 200))
            _require(image.getpixel((100, 100)) == (36, 76, 59, 255))
        _require(
            delete_palette_material(
                owner=restored_owner, brand_id=brand.pk, material_id=material_id
            )
        )
        _require(not MaterialRasterPair.objects.exists())
        _require(not BrandMaterialVersion.objects.exists())
        _require(not BrandMaterial.objects.exists())
        _require(
            not delete_palette_material(
                owner=restored_owner, brand_id=brand.pk, material_id=material_id
            )
        )
        connection.close()
        # Deleting restored rows must not mutate either source or backup.
        with closing(sqlite3.connect(root / "source.sqlite3")) as source:
            _require(
                source.execute(
                    "SELECT COUNT(*) FROM assets_materialrasterpair"
                ).fetchone()[0]
                == 1
            )
        _require(
            sha256((root / "backup.sqlite3").read_bytes()).hexdigest() == backup_hash
        )
        _require(
            sha256((root / "source.sqlite3").read_bytes()).hexdigest() == source_hash
        )
        return {
            "restored_pair_matches": True,
            "restored_png_decoded": True,
            "restored_deletion_complete": True,
            "source_and_backup_preserved": True,
        }
    finally:
        connection.close()


def main():
    if len(sys.argv) != 1:
        print(json.dumps({"ok": False, "reason": "no_arguments_allowed"}))
        return 1
    root = Path(tempfile.mkdtemp(prefix="yaparo-raster-recovery-"))
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
        result = {"ok": False, "reason": "recovery_rehearsal_failed"}
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
            expected = {
                root / name
                for name in ("source.sqlite3", "backup.sqlite3", "restored.sqlite3")
            }
            actual = set(root.iterdir())
            _require(actual <= expected)
            for path in actual:
                entry = path.stat(follow_symlinks=False)
                _require(stat.S_ISREG(entry.st_mode) and entry.st_nlink == 1)
                _require(
                    not getattr(entry, "st_file_attributes", 0)
                    & stat.FILE_ATTRIBUTE_REPARSE_POINT
                )
            for path in actual:
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
