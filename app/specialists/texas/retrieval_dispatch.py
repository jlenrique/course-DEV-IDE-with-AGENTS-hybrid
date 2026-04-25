"""Thin dispatch seam for Texas retrieval bundle generation (Story 2a.4)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_WRANGLER = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
DEFAULT_FIXTURE_BUNDLE = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "texas" / "fixture_bundle"
)


def _venv_python() -> Path:
    if sys.platform.startswith("win"):
        return REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    return REPO_ROOT / ".venv" / "bin" / "python"


def dispatch_retrieval(
    *,
    directive_path: str | Path | None = None,
    bundle_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Run Texas wrangler or return a deterministic fixture bundle reference.

    Dev-agent paths stay deterministic and non-network by default. A live
    subprocess dispatch only occurs when both directive and bundle path are
    explicitly provided.
    """
    if not directive_path or not bundle_dir:
        return {
            "status": "mocked",
            "bundle_dir": str(DEFAULT_FIXTURE_BUNDLE),
            "exit_code": 0,
            "command": None,
        }

    py = _venv_python()
    command = [
        str(py),
        str(RUN_WRANGLER),
        "--directive",
        str(directive_path),
        "--bundle-dir",
        str(bundle_dir),
        "--json",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    return {
        "status": "dispatched",
        "bundle_dir": str(bundle_dir),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": command,
    }


__all__ = ["DEFAULT_FIXTURE_BUNDLE", "dispatch_retrieval"]
