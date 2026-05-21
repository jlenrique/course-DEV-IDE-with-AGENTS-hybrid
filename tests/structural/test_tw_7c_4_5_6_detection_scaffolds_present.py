from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(REPO_ROOT / ".venv/Scripts/python.exe"), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_tw_7c_4_detector_exists_and_passes():
    script = REPO_ROOT / "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py"
    assert script.exists()

    result = _run_script(script.as_posix())
    assert result.returncode == 0
    assert '"tripwire_id": "TW-7c-4"' in result.stdout


def test_tw_7c_5_detector_exists_and_passes():
    script = REPO_ROOT / "scripts/utilities/detect_tw_7c_5_utf8_violations.py"
    assert script.exists()

    result = _run_script(script.as_posix())
    assert result.returncode == 0
    assert '"tripwire_id": "TW-7c-5"' in result.stdout


def test_tw_7c_6_detector_exists_and_dry_run_passes():
    script = REPO_ROOT / "scripts/utilities/detect_tw_7c_6_parity_flake.py"
    assert script.exists()

    result = _run_script(script.as_posix(), "--dry-run")
    assert result.returncode == 0
    assert '"tripwire_id": "TW-7c-6"' in result.stdout
