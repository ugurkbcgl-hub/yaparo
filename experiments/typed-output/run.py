"""Recreate an isolated, pinned experiment and audit it; no product install."""

import json
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run():
    source = Path(__file__).resolve().parent
    child_env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(
            (
                "OPENAI_",
                "OPENROUTER_",
                "ANTHROPIC_",
                "GEMINI_",
                "GOOGLE_",
                "LOGFIRE_",
                "OTEL_",
            )
        )
    }
    child_env["PYDANTIC_AI_NO_BANNER"] = "1"
    with tempfile.TemporaryDirectory(prefix="yaparo-typed-output-") as directory:
        root = Path(directory).resolve()
        if root.parent != Path(
            tempfile.gettempdir()
        ).resolve() or not root.name.startswith("yaparo-typed-output-"):
            raise RuntimeError("Unexpected experiment path")
        venv.EnvBuilder(with_pip=True).create(root)
        python = root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--only-binary=:all:",
                "--timeout",
                "20",
                "--retries",
                "1",
                "-r",
                str(source / "requirements.txt"),
            ],
            check=True,
            env=child_env,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run([str(python), "-m", "pip", "check"], check=True, env=child_env)
        # The outer development runtime already supplies pip-audit. Audit only
        # the experiment's installed versions; no product dependency is changed.
        site = subprocess.check_output(
            [
                str(python),
                "-c",
                "import sysconfig; print(sysconfig.get_paths()['purelib'])",
            ],
            text=True,
            env=child_env,
        ).strip()
        if not Path(site).resolve().is_relative_to(root):
            raise RuntimeError("Unexpected experiment package path")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip_audit",
                "--path",
                site,
                "--progress-spinner",
                "off",
            ],
            check=True,
            env=child_env,
        )
        output = subprocess.check_output(
            [str(python), str(source / "compare.py")],
            text=True,
            encoding="utf-8",
            env=child_env,
        )
        report = json.loads(output)
        optimized = json.loads(
            subprocess.check_output(
                [str(python), "-O", str(source / "compare.py")],
                text=True,
                encoding="utf-8",
                env=child_env,
            )
        )
        keys = ("brief", "case", "method", "accepted", "expected", "observations")

        def outcomes(value):
            return [tuple(row[key] for key in keys) for row in value["rows"]]

        if outcomes(report) != outcomes(optimized):
            raise RuntimeError("Optimized comparison changed acceptance outcomes")
        report["optimized_total_runs"] = optimized["total_runs"]
        print(
            json.dumps(
                {key: value for key, value in report.items() if key != "rows"},
                sort_keys=True,
            )
        )
        return report


if __name__ == "__main__":
    run()
