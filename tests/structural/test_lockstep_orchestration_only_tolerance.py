from __future__ import annotations

import copy
from pathlib import Path

import yaml

from scripts.utilities.check_pipeline_manifest_lockstep import (
    DEFAULT_PACK_PATH,
    run_check,
)
from scripts.utilities.pipeline_manifest import DEFAULT_MANIFEST_PATH


def _copy_manifest(tmp_path: Path) -> Path:
    target = tmp_path / "pipeline-manifest.yaml"
    target.write_text(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def test_lockstep_passes_with_directive_composer_orchestration_node() -> None:
    exit_code, trace = run_check(DEFAULT_MANIFEST_PATH, DEFAULT_PACK_PATH, None)

    assert exit_code == 0
    assert trace["orchestration_only_nodes"] == ["directive-composer"]


def test_non_orchestration_node_without_hud_or_pack_entry_still_fails(tmp_path: Path) -> None:
    manifest_path = _copy_manifest(tmp_path)
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    fake = copy.deepcopy(raw["nodes"][0])
    fake.update(
        {
            "id": "fake-specialist-node",
            "label": "Fake Specialist Node",
            "specialist_id": "marcus",
            "gate": False,
            "gate_code": None,
            "hud_tracked": False,
            "insertion_after": None,
            "fold_with": None,
            "fold_target": None,
        }
    )
    raw["nodes"].insert(1, fake)
    manifest_path.write_text(
        yaml.safe_dump(raw, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    exit_code, trace = run_check(manifest_path, DEFAULT_PACK_PATH, None)

    assert exit_code == 1
    assert "fake-specialist-node".upper() in trace["findings"][0]["manifest_only"]


def test_lockstep_trace_records_orchestration_only_nodes() -> None:
    exit_code, trace = run_check(DEFAULT_MANIFEST_PATH, DEFAULT_PACK_PATH, None)

    assert exit_code == 0
    assert trace["orchestration_only_nodes"] == ["directive-composer"]
