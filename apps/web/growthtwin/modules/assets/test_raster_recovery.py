"""Run the no-input recovery exercise in its own fresh database process."""

import json
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class RasterRecoveryTests(SimpleTestCase):
    def test_refuses_reuse_inside_an_existing_django_process_before_files(self):
        from scripts.rehearse_raster_recovery import _exercise

        with self.assertRaises(ValueError):
            _exercise(Path("must-not-be-opened"))

    def test_actual_private_backup_restore_decode_and_delete(self):
        script = Path(settings.BASE_DIR) / "scripts" / "rehearse_raster_recovery.py"
        result = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True, timeout=45
        )
        self.assertEqual(0, result.returncode, "Disposable recovery exercise failed.")
        evidence = json.loads(result.stdout)
        self.assertEqual(
            {
                "ok",
                "restored_pair_matches",
                "restored_png_decoded",
                "restored_deletion_complete",
                "source_and_backup_preserved",
                "private_fixture_cleanup",
            },
            set(evidence),
        )
        self.assertTrue(all(value is True for value in evidence.values()))
