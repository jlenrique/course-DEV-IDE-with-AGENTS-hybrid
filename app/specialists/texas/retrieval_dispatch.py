"""Thin dispatch seam for Texas retrieval bundle generation (Story 2a.4)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_WRANGLER = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
DEFAULT_FIXTURE_BUNDLE = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "texas" / "fixture_bundle"
)


def _directive_corpus_cwd(directive_path: Path) -> Path:
    """Resolve the wrangler subprocess cwd from the directive's ``corpus_dir``.

    The wrangler resolves ``local_file`` locators relative to its own cwd,
    while the §02A composer emits corpus-relative locators plus a top-level
    ``corpus_dir`` field. The Story 34-1 integration ratchet pins the correct
    invocation contract (``cwd=directive.corpus_dir``); production dispatch
    must mirror it or every locator fails ``File not found`` (Trial-3
    attempt-3 crash, 2026-06-11). Falls back to ``REPO_ROOT`` when the
    directive carries no usable ``corpus_dir``.
    """
    try:
        loaded = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return REPO_ROOT
    if not isinstance(loaded, dict):
        return REPO_ROOT
    corpus_dir = loaded.get("corpus_dir")
    if not corpus_dir:
        return REPO_ROOT
    candidate = Path(str(corpus_dir))
    return candidate if candidate.is_dir() else REPO_ROOT


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
    # Absolutize both path args: cwd below is the directive's corpus_dir (so
    # corpus-relative locators resolve), which would otherwise re-anchor any
    # relative directive/bundle path the caller supplied.
    directive_arg = Path(directive_path).resolve()
    bundle_arg = Path(bundle_dir).resolve()
    command = [
        str(py),
        str(RUN_WRANGLER),
        "--directive",
        str(directive_arg),
        "--bundle-dir",
        str(bundle_arg),
        "--json",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
        timeout=30,
        cwd=str(_directive_corpus_cwd(Path(directive_path))),
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
