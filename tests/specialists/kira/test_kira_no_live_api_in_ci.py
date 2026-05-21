from __future__ import annotations

import subprocess
import sys

from tests.parity._sanctum_parity_base import REPO_ROOT


def test_kira_tests_do_not_import_live_kling_client_at_module_scope() -> None:
    script = REPO_ROOT / "scripts" / "utilities" / "detect_live_api_in_tests.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "tests/specialists/kira",
            "tests/parity/test_kira_activation_contract.py",
            "tests/composition/test_kira_to_compositor_chain.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
