"""Graph-compile-time lockstep validation for the pipeline manifest regime."""

from __future__ import annotations

import argparse
import fnmatch
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from app.manifest import CompileError as ManifestCompileError
from app.manifest import load as load_graph_manifest
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH, compile_run_graph
from scripts.utilities.file_helpers import project_root

LOGGER = logging.getLogger(__name__)

DEFAULT_MANIFEST_PATH = DEFAULT_RUN_MANIFEST_PATH
DEFAULT_DEV_MANIFEST_PATH = (
    project_root() / "state" / "config" / "dev-graph-manifest.yaml"
)

COMPANION_RULES: dict[str, tuple[str, ...]] = {
    "state/config/pipeline-manifest.yaml": (
        "scripts/utilities/check_pipeline_manifest_lockstep.py",
        "docs/workflow/production-prompt-pack-v4.2-*.md",
        "scripts/utilities/run_hud.py",
        "scripts/utilities/progress_map.py",
        "marcus/orchestrator/workflow_runner.py",
    ),
    "scripts/utilities/check_pipeline_manifest_lockstep.py": (
        "state/config/pipeline-manifest.yaml",
        "docs/workflow/production-prompt-pack-v4.2-*.md",
    ),
    "scripts/utilities/run_hud.py": ("state/config/pipeline-manifest.yaml",),
    "scripts/utilities/progress_map.py": ("state/config/pipeline-manifest.yaml",),
    "marcus/orchestrator/workflow_runner.py": ("state/config/pipeline-manifest.yaml",),
    "docs/workflow/production-prompt-pack-v4.2-*.md": (
        "state/config/pipeline-manifest.yaml",
        "scripts/utilities/check_pipeline_manifest_lockstep.py",
    ),
    "state/config/learning-event-schema.yaml": (
        "scripts/utilities/learning_event_capture.py",
        "state/config/pipeline-manifest.yaml",
    ),
    "scripts/utilities/learning_event_capture.py": (
        "state/config/learning-event-schema.yaml",
        "state/config/pipeline-manifest.yaml",
    ),
}


# Capability-overlay (Braid S4) honesty map: inputs whose change can stale
# state/config/capability-overlay.yaml. Checked locally via content comparison
# (generate_capability_overlay.is_stale) so the "caught locally AND in CI" claim
# holds without a false positive on a routing-neutral edit.
_CAPABILITY_OVERLAY_INPUTS: tuple[str, ...] = (
    "state/config/pipeline-manifest.yaml",
    "state/config/dispatch-registry.yaml",
    "scripts/utilities/generate_capability_overlay.py",
    "skills/bmad-agent-marcus/references/specialist-registry.yaml",
)


class LockstepError(RuntimeError):
    """Base error for graph-compile-time lockstep failures."""


class ManifestDriftError(LockstepError):
    """Raised when a trigger-path edit lacks its companion update."""


class CompileError(LockstepError):
    """Raised when graph compilation fails validation."""


class CapabilityOverlayStaleError(LockstepError):
    """Raised when a capability-overlay input changed but the overlay is stale."""


def _normalize(path: str) -> str:
    return path.replace("\\", "/")


def _load_compile_dev_graph() -> Any:
    from app.cora.graph import compile_dev_graph

    return compile_dev_graph


def _default_diff_from() -> str | None:
    base_ref = os.getenv("GITHUB_BASE_REF")
    if base_ref:
        return f"origin/{base_ref}"
    return None


def _discover_diff_files(diff_from: str | None) -> list[str]:
    base = diff_from or _default_diff_from()
    if not base:
        return []

    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=project_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        LOGGER.warning("Unable to derive diff from %s; proceeding without drift checks.", base)
        return []

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _matching_trigger_patterns(
    changed_path: str,
    trigger_patterns: tuple[str, ...],
) -> list[str]:
    return [pattern for pattern in trigger_patterns if fnmatch.fnmatch(changed_path, pattern)]


def _assert_companion_updates(
    diff_files: list[str],
    trigger_patterns: tuple[str, ...],
) -> None:
    normalized = [_normalize(path) for path in diff_files]
    changed = set(normalized)

    for changed_path in normalized:
        if not _matching_trigger_patterns(changed_path, trigger_patterns):
            continue

        required_patterns: set[str] = set()
        for trigger_pattern, companion_patterns in COMPANION_RULES.items():
            if fnmatch.fnmatch(changed_path, trigger_pattern):
                required_patterns.update(companion_patterns)

        if not required_patterns:
            continue

        if any(
            companion_path != changed_path
            and any(fnmatch.fnmatch(companion_path, pattern) for pattern in required_patterns)
            for companion_path in changed
        ):
            continue

        required = ", ".join(sorted(required_patterns))
        raise ManifestDriftError(
            f"{changed_path} changed without a required companion update. "
            f"Expected one of: {required}."
        )


def _assert_capability_overlay_fresh(diff_files: list[str]) -> None:
    """If a capability-overlay input changed, the overlay must not be stale.

    Uses content comparison (``generate_capability_overlay.is_stale``) rather than
    a companion-touched check, so a routing-neutral edit that regenerates to a
    byte-identical overlay does NOT false-fail. This is the LOCAL half of the
    capability-overlay "caught two ways (locally + CI)" protection (the CI parity
    test is the other half).
    """
    changed = {_normalize(path) for path in diff_files}
    triggered = any(
        fnmatch.fnmatch(changed_path, pattern)
        for changed_path in changed
        for pattern in _CAPABILITY_OVERLAY_INPUTS
    )
    if not triggered:
        return
    try:
        from scripts.utilities.generate_capability_overlay import is_stale
    except ImportError:  # generator absent (defensive); CI parity remains the backstop
        return
    if is_stale():
        raise CapabilityOverlayStaleError(
            "a capability-overlay input changed but "
            "state/config/capability-overlay.yaml is stale; run "
            "`python -m scripts.utilities.generate_capability_overlay` to regenerate."
        )


def _compile_dev_graph_if_available(dev_manifest_path: Path) -> dict[str, Any]:
    if not dev_manifest_path.exists():
        return {"compiled": False, "skipped": True, "reason": "dev manifest absent"}

    try:
        compile_dev_graph = _load_compile_dev_graph()
    except ImportError as exc:
        reason = "compile_dev_graph unavailable until Story 4.2"
        LOGGER.warning("%s (%s)", reason, exc.__class__.__name__)
        return {"compiled": False, "skipped": True, "reason": reason}

    try:
        compile_dev_graph(dev_manifest_path, validation_mode=True)
    except ManifestCompileError as exc:
        raise CompileError(f"compile_dev_graph failed validation: {exc}") from exc

    return {"compiled": True, "skipped": False, "reason": None}


def check_lockstep(
    diff_files: list[str] | None = None,
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    dev_manifest_path: Path = DEFAULT_DEV_MANIFEST_PATH,
    diff_from: str | None = None,
) -> dict[str, Any]:
    """Validate graph compilation and trigger-path companion updates."""
    manifest = load_graph_manifest(manifest_path)

    try:
        compile_run_graph(manifest, validation_mode=True)
    except ManifestCompileError as exc:
        raise CompileError(f"compile_run_graph failed validation: {exc}") from exc

    dev_status = _compile_dev_graph_if_available(dev_manifest_path)

    changed_files = list(diff_files) if diff_files is not None else _discover_diff_files(diff_from)
    _assert_companion_updates(changed_files, tuple(manifest.block_mode_trigger_paths))
    _assert_capability_overlay_fresh(changed_files)

    return {
        "manifest_path": str(manifest_path),
        "diff_files": [_normalize(path) for path in changed_files],
        "compiled_run_graph": True,
        "dev_graph": dev_status,
    }


def run_check(
    diff_files: list[str] | None = None,
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    dev_manifest_path: Path = DEFAULT_DEV_MANIFEST_PATH,
    diff_from: str | None = None,
) -> tuple[int, dict[str, Any]]:
    """Return an exit code and structured payload for tests."""
    try:
        payload = check_lockstep(
            diff_files,
            manifest_path=manifest_path,
            dev_manifest_path=dev_manifest_path,
            diff_from=diff_from,
        )
    except LockstepError as exc:
        return 1, {"ok": False, "error": exc.__class__.__name__, "message": str(exc)}

    return 0, {"ok": True, **payload}


def main(
    diff_files: list[str] | None = None,
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    dev_manifest_path: Path = DEFAULT_DEV_MANIFEST_PATH,
    diff_from: str | None = None,
) -> int:
    """Return 0 on no-drift, non-zero on lockstep failure."""
    exit_code, payload = run_check(
        diff_files,
        manifest_path=manifest_path,
        dev_manifest_path=dev_manifest_path,
        diff_from=diff_from,
    )
    if exit_code != 0:
        LOGGER.error("%s: %s", payload["error"], payload["message"])
    return exit_code


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check graph compile lockstep integrity.")
    parser.add_argument("--diff-from", type=str, default=None)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--dev-manifest", type=Path, default=DEFAULT_DEV_MANIFEST_PATH)
    args = parser.parse_args(argv)
    return main(
        manifest_path=args.manifest,
        dev_manifest_path=args.dev_manifest,
        diff_from=args.diff_from,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(cli())
