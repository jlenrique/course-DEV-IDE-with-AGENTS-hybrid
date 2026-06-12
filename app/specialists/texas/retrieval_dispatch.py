"""Thin dispatch seam for Texas retrieval bundle generation (Story 2a.4)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from app.specialists.texas._act import BundleDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_WRANGLER = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
DEFAULT_FIXTURE_BUNDLE = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "texas" / "fixture_bundle"
)
DISPATCH_TIMEOUT_SECONDS = 30


def _directive_corpus_cwd(directive_path: Path) -> Path:
    """Resolve the wrangler subprocess cwd from the directive's ``corpus_dir``.

    The wrangler resolves ``local_file`` locators relative to its own cwd,
    while the §02A composer emits corpus-relative locators plus a top-level
    ``corpus_dir`` field. The Story 34-1 integration ratchet pins the correct
    invocation contract (``cwd=directive.corpus_dir``); production dispatch
    must mirror it or every locator fails ``File not found`` (Trial-3
    attempt-3 crash, 2026-06-11). Falls back to ``REPO_ROOT`` only when the
    directive carries NO ``corpus_dir`` (legacy directives) or cannot be
    read at all (the wrangler subprocess then fail-louds with its own
    taxonomy). A ``corpus_dir`` that is present but not a directory is a
    misconfiguration and raises instead of silently reproducing the
    attempt-3 wrong-cwd signature; a relative ``corpus_dir`` is anchored
    against ``REPO_ROOT`` so the result never depends on the process cwd.
    """
    try:
        loaded = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return REPO_ROOT
    if not isinstance(loaded, dict):
        return REPO_ROOT
    corpus_dir = loaded.get("corpus_dir")
    if not corpus_dir:
        return REPO_ROOT
    candidate = Path(str(corpus_dir))
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    if not candidate.is_dir():
        raise BundleDispatchError(
            f"directive corpus_dir is not a directory: {corpus_dir!r} "
            f"(resolved to {candidate})",
            tag="bundle.dispatch.corpus-dir-invalid",
        )
    return candidate


def _venv_python() -> Path:
    if sys.platform.startswith("win"):
        return REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    return REPO_ROOT / ".venv" / "bin" / "python"


def dispatch_retrieval(
    *,
    directive_path: str | Path | None = None,
    bundle_dir: str | Path | None = None,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    """Run Texas wrangler.

    S0 fail-loud policy (SCP 2026-06-11 segment-data-plane): missing inputs
    RAISE; the fixture bundle is reachable only via explicit ``allow_fixture``
    opt-in, which production dispatch never sets.
    """
    if not directive_path or not bundle_dir:
        if allow_fixture:
            return {
                "status": "mocked",
                "bundle_dir": str(DEFAULT_FIXTURE_BUNDLE),
                "exit_code": 0,
                "command": None,
            }
        missing = "directive_path" if not directive_path else "bundle_dir"
        raise BundleDispatchError(
            f"dispatch_retrieval missing required input: {missing}",
            tag="bundle.dispatch.input-missing",
        )

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
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=False,
            timeout=DISPATCH_TIMEOUT_SECONDS,
            cwd=str(_directive_corpus_cwd(directive_arg)),
        )
    except subprocess.TimeoutExpired as exc:
        raise BundleDispatchError(
            f"texas wrangler dispatch timed out after {DISPATCH_TIMEOUT_SECONDS}s",
            tag="bundle.dispatch.timeout",
        ) from exc
    return {
        "status": "dispatched",
        "bundle_dir": str(bundle_dir),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": command,
    }


__all__ = ["DEFAULT_FIXTURE_BUNDLE", "dispatch_retrieval"]
