"""Tests for check_pipeline_manifest_lockstep utility."""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.utilities.check_pipeline_manifest_lockstep import (
    DEFAULT_PACK_PATH,
    run_check,
)
from scripts.utilities.pipeline_manifest import DEFAULT_MANIFEST_PATH


def test_lockstep_check_runs_clean_manifest() -> None:
    exit_code, trace = run_check(DEFAULT_MANIFEST_PATH, DEFAULT_PACK_PATH, "v4.2")
    assert exit_code in {0, 1}
    assert trace["lane"] == "L1"
    assert trace["scope"] == "pipeline-lockstep"


def test_lockstep_check_structural_on_missing_manifest(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    exit_code, trace = run_check(missing, DEFAULT_PACK_PATH, "v4.2")
    assert exit_code == 2
    assert trace["closure_gate"] == "STRUCTURAL"


def test_malformed_graph_manifest_does_not_use_legacy_fallback(tmp_path: Path) -> None:
    data = yaml.safe_load(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    data["nodes"][0]["gate"] = "definitely-not-a-boolean"
    manifest_path = tmp_path / "malformed-graph.yaml"
    manifest_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    exit_code, trace = run_check(manifest_path, DEFAULT_PACK_PATH, "v4.2")
    assert exit_code == 2
    assert trace["closure_gate"] == "STRUCTURAL"


def _write_fixture_manifest(tmp_path: Path, schema_ref: str) -> Path:
    data = yaml.safe_load(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    data["learning_events"]["schema_ref"] = schema_ref
    for step in data.get("steps", []):
        learning_events = step.get("learning_events")
        if isinstance(learning_events, dict) and learning_events.get("emits"):
            learning_events["schema_ref"] = schema_ref
    manifest_path = tmp_path / "pipeline-manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return manifest_path


def test_red_path_fixtures_fail_correctly_schema_only(tmp_path: Path) -> None:
    schema = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "pipeline_manifest_drift"
        / "schema_only_drift"
        / "learning-event-schema.yaml"
    )
    root = Path(__file__).resolve().parents[1]
    manifest_path = _write_fixture_manifest(
        tmp_path, str(schema.relative_to(root).as_posix())
    )
    exit_code, trace = run_check(manifest_path, DEFAULT_PACK_PATH, "v4.2")
    assert exit_code == 1, trace
    assert any(finding["check"] in {3, 8} for finding in trace["findings"])


def test_red_path_fixtures_fail_correctly_manifest_only(tmp_path: Path) -> None:
    schema = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "pipeline_manifest_drift"
        / "manifest_only_drift"
        / "learning-event-schema.yaml"
    )
    root = Path(__file__).resolve().parents[1]
    manifest_path = _write_fixture_manifest(
        tmp_path, str(schema.relative_to(root).as_posix())
    )
    exit_code, trace = run_check(manifest_path, DEFAULT_PACK_PATH, "v4.2")
    assert exit_code == 1, trace
    assert any(finding["check"] in {3, 8} for finding in trace["findings"])
