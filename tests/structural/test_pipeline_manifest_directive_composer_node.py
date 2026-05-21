"""Structural pin for the Story 7a.2 directive-composer manifest registration."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.manifest.loader import load

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"


def test_manifest_carries_directive_composer_node() -> None:
    manifest = load(MANIFEST_PATH)
    node = next(item for item in manifest.nodes if item.id == "directive-composer")

    assert node.specialist_id is None
    assert node.gate is False
    assert node.hud_tracked is False
    assert node.dependencies == {}
    assert node.fold_with is None
    assert node.fold_target is None


def test_manifest_schema_version_supports_fold_flags() -> None:
    manifest = load(MANIFEST_PATH)

    assert manifest.schema_version == "v4.2-migration-stub-with-fold-flags"
    assert manifest.pack_version == "v4.2"


def test_manifest_lockstep_passes_with_directive_composer_node() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "utilities" / "check_pipeline_manifest_lockstep.py"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"check_pipeline_manifest_lockstep.py failed: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
