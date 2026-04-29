from __future__ import annotations

from pathlib import Path

import yaml

MANIFEST_PATH = Path("state/config/pipeline-manifest.yaml")


def test_per_slide_subgraph_nodes_registered_as_orchestration_only() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in manifest["nodes"]}

    for node_id in ["per-slide-subgraph", "html-review-pack-emitter"]:
        node = nodes[node_id]
        assert node["specialist_id"] is None
        assert node["scaffold_node"] is None
        assert node["model_config_ref"] is None
        assert node["gate"] is False
        assert node["gate_code"] is None
        assert node["sub_phase_of"] is None
        assert node["insertion_after"] is None
        assert node["hud_tracked"] is False
        assert node["dependencies"] == {}
        assert node["fold_with"] is None
        assert node["fold_target"] is None

    assert "isolated checkpoint per slide" in nodes["per-slide-subgraph"]["rationale"]
    assert "review-pack.html" in nodes["html-review-pack-emitter"]["rationale"]
