from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.utilities.check_manifest_lockstep import (
    CompileError,
    check_lockstep,
    main,
)

ROOT = Path(__file__).resolve().parents[3]
LIVE_MANIFEST = ROOT / "state" / "config" / "pipeline-manifest.yaml"


def _write_manifest(tmp_path: Path, **overrides: object) -> Path:
    manifest = yaml.safe_load(LIVE_MANIFEST.read_text(encoding="utf-8"))
    manifest.update(overrides)
    path = tmp_path / "pipeline-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def test_no_drift_exits_zero() -> None:
    assert main(["README.md"]) == 0


def test_compile_error_raises(tmp_path: Path) -> None:
    broken = _write_manifest(tmp_path, frozen_graph_version="v999-missing")
    with pytest.raises(CompileError, match="compile_run_graph failed validation"):
        check_lockstep([], manifest_path=broken)


def test_dev_graph_defer_tolerant(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    dev_manifest = tmp_path / "dev-graph-manifest.yaml"
    dev_manifest.write_text("schema_version: 'dev-stub'\n", encoding="utf-8")
    with caplog.at_level("WARNING"):
        exit_code = main([], dev_manifest_path=dev_manifest)
    assert exit_code == 0
    assert "compile_dev_graph unavailable until Story 4.2" in caplog.text


def test_dev_graph_skip_logged_with_reason(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    dev_manifest = tmp_path / "dev-graph-manifest.yaml"
    dev_manifest.write_text("schema_version: 'dev-stub'\n", encoding="utf-8")
    with caplog.at_level("WARNING"):
        main([], dev_manifest_path=dev_manifest)
    assert "ModuleNotFoundError" in caplog.text
