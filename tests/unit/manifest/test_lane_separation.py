"""Lane-separation test (AC-1.4-D).

D4 mandates Cora ⊥ Marcus lane separation as separate `StateGraph`
compilation units. The compiler accepts `lane: "run_graph"` (Marcus) and
`lane: "dev_graph"` (Cora) and produces topology consistent with the
`app.marcus` ⊥ `app.cora` import-linter Contract C1.

Instantiates a manifest with each lane value, compiles both, asserts the
resulting `StateGraph` instances do not share node references — a node
bridging lanes is a regression against C1's lane-isolation invariant.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.manifest import compile
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest


def _lane_manifest(lane: str, ids: tuple[str, ...]) -> PipelineManifest:
    return PipelineManifest.model_validate(
        {
            "schema_version": "0.1-stub",
            "lane": lane,
            "entrypoint": ids[0],
            "frozen_graph_version": "v0.1-stub",
            "nodes": [NodeSpec(id=nid) for nid in ids],
            "edges": [
                EdgeSpec.model_validate({"from": "__start__", "to": ids[0]}),
                *(
                    EdgeSpec.model_validate({"from": ids[i], "to": ids[i + 1]})
                    for i in range(len(ids) - 1)
                ),
                EdgeSpec.model_validate({"from": ids[-1], "to": "__end__"}),
            ],
        }
    )


@pytest.fixture
def _tmp_repo_root(tmp_path: Path) -> Path:
    (tmp_path / "runtime" / "graphs" / "v0.1-stub").mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_run_graph_lane_compiles(_tmp_repo_root: Path) -> None:
    run_manifest = _lane_manifest("run_graph", ("marcus_a", "marcus_b"))
    g = compile(run_manifest, repo_root=_tmp_repo_root)
    assert g is not None


def test_dev_graph_lane_compiles(_tmp_repo_root: Path) -> None:
    dev_manifest = _lane_manifest("dev_graph", ("cora_x", "cora_y"))
    g = compile(dev_manifest, repo_root=_tmp_repo_root)
    assert g is not None


def test_two_lanes_do_not_share_node_references(_tmp_repo_root: Path) -> None:
    """Compiled graphs per lane must own distinct `StateGraph` instances and node sets."""
    run_manifest = _lane_manifest("run_graph", ("marcus_a", "marcus_b"))
    dev_manifest = _lane_manifest("dev_graph", ("cora_x", "cora_y"))
    run_graph = compile(run_manifest, repo_root=_tmp_repo_root)
    dev_graph = compile(dev_manifest, repo_root=_tmp_repo_root)

    assert run_graph is not dev_graph, "compiling each lane must return a distinct StateGraph"
    # LangGraph's StateGraph exposes `.nodes` dict keyed by node id. No id may appear
    # in both lanes' graphs; bridging would be a C1 regression.
    run_ids = set(run_graph.nodes)
    dev_ids = set(dev_graph.nodes)
    assert run_ids.isdisjoint(dev_ids), (
        f"node ids must not bridge lanes; overlap={run_ids & dev_ids}"
    )
