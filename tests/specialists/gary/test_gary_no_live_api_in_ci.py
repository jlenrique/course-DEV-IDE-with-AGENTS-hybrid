from __future__ import annotations

import subprocess
import sys

from tests.parity._sanctum_parity_base import REPO_ROOT


def test_gary_tests_have_no_live_api_imports() -> None:
    script = REPO_ROOT / "scripts" / "utilities" / "detect_live_api_in_tests.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "tests/parity/test_gary_activation_contract.py",
            "tests/specialists/gary",
            "tests/composition/test_gary_to_vera_g3_chain.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
