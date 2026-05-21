from __future__ import annotations

from pathlib import Path

import yaml

MANIFEST_PATH = Path("state/config/pipeline-manifest.yaml")


def test_pre_gate_marcus_node_registered_as_orchestration_only() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in manifest["nodes"]}

    node = nodes["pre-gate-marcus"]

    assert node["specialist_id"] is None
    assert node["scaffold_node"] is None
    assert node["model_config_ref"] is None
    assert node["dependencies"] == {}
    assert node["gate"] is False
    assert node["gate_code"] is None
    assert node["sub_phase_of"] is None
    assert node["insertion_after"] is None
    assert node["hud_tracked"] is False
    assert node["pack_section_anchor"] == "0.5)"
    assert node["pack_version"] == "v4.2"
    assert node["fold_with"] is None
    assert node["fold_target"] is None
    assert "single LLM call site" in node["rationale"]
