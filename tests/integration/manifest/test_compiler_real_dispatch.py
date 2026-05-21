from __future__ import annotations

from pathlib import Path

from app.manifest.compiler import compile_run_graph
from app.manifest.loader import load

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"


def _handler(graph, node_id: str):
    return graph.nodes[node_id].runnable.func


def test_active_specialist_nodes_resolve_to_dispatch_registry_builders() -> None:
    manifest = load(MANIFEST)
    graph = compile_run_graph(manifest)

    expected = {
        "03": "app.specialists.texas.graph:build_texas_graph",
        "07": "app.specialists.gary.graph:build_gary_graph",
        "07E": "app.specialists.kira.graph:build_kira_graph",
        "08": "app.specialists.irene.graph:build_irene_graph",
        "12": "app.specialists.enrique.graph:build_enrique_graph",
        "14.5": "app.specialists.desmond.graph:build_desmond_graph",
    }
    for node_id, builder_ref in expected.items():
        handler = _handler(graph, node_id)
        assert handler.__production_node_kind__ == "specialist"
        assert handler.__production_specialist_builder_ref__ == builder_ref
        assert not handler.__name__.startswith("passthrough_")


def test_production_gate_nodes_resolve_to_gate_emitters() -> None:
    manifest = load(MANIFEST)
    graph = compile_run_graph(manifest)

    expected = {"04": "G1", "07C": "G2C", "09": "G3", "10": "G4"}
    for node_id, gate_id in expected.items():
        handler = _handler(graph, node_id)
        assert handler.__production_node_kind__ == "gate"
        assert handler.__production_gate_id__ == gate_id
        assert not handler.__name__.startswith("passthrough_")


def test_unmigrated_orchestration_nodes_are_explicit_not_passthrough() -> None:
    manifest = load(MANIFEST)
    graph = compile_run_graph(manifest)

    handler = _handler(graph, "01")
    assert handler.__production_node_kind__ == "orchestration"
    assert handler.__production_resolution_reason__ == "specialist-not-in-dispatch-registry"
    assert not handler.__name__.startswith("passthrough_")
