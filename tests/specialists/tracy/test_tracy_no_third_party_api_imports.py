from __future__ import annotations

import subprocess
import sys

from tests.parity._sanctum_parity_base import REPO_ROOT


def test_tracy_tests_do_not_import_third_party_api_clients() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/utilities/detect_live_api_in_tests.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
