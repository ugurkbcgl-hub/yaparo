"""Run the no-input, fresh-workspace portability exercise in its own process."""

import json
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class BundleRehearsalTests(SimpleTestCase):
    def test_configured_process_is_rejected_before_accessing_root(self):
        from scripts.rehearse_design_bundle import _exercise

        with self.assertRaises(ValueError):
            _exercise(Path("must-not-be-opened"))

    def test_actual_fresh_private_source_export_restore_and_reexport(self):
        result = subprocess.run(
            [
                sys.executable,
                str(Path(settings.BASE_DIR) / "scripts" / "rehearse_design_bundle.py"),
            ],
            capture_output=True,
            text=True,
            timeout=45,
        )
        self.assertEqual(result.returncode, 0, "Synthetic bundle rehearsal failed.")
        evidence = json.loads(result.stdout)
        self.assertEqual(
            set(evidence),
            {
                "ok",
                "scene_recreated_in_fresh_workspace",
                "source_identity_preserved",
                "png_bytes_and_pixels_match",
                "reexport_without_source_db",
                "source_db_and_archive_unchanged",
                "private_fixture_cleanup",
            },
        )
        self.assertTrue(all(value is True for value in evidence.values()))
