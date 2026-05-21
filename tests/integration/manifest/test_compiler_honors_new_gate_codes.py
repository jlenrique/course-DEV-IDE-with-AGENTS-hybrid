from __future__ import annotations

from app.manifest.compiler import RUNTIME_GATE_IDS, compile
from app.manifest.schema import NodeSpec, PipelineManifest

EXPECTED_RUNTIME_IDS = frozenset(
    {
        "G0",
        "G0A",
        "G0B",
        "G1",
        "G1A",
        "G1.5",
        "G2",
        "G2B",
        "G2C",
        "G2M",
        "G2.5",
        "G2F",
        "G3",
        "G3B",
        "G4",
        "G4A",
        "G4B",
        "G5",
    }
)


def _manifest_for(gate_id: str) -> PipelineManifest:
    return PipelineManifest(
        schema_version="test",
        lane="run_graph",
        entrypoint="gate-node",
        frozen_graph_version="v0.1-stub",
        nodes=[
            NodeSpec(
                id="gate-node",
                gate=True,
                gate_code=gate_id,
            )
        ],
        edges=[],
    )


def test_compiler_declares_7c_4a_runtime_gate_set() -> None:
    assert RUNTIME_GATE_IDS == EXPECTED_RUNTIME_IDS


def test_compiler_accepts_every_7c_4a_runtime_gate_code() -> None:
    for gate_id in sorted(EXPECTED_RUNTIME_IDS):
        graph = compile(_manifest_for(gate_id))
        assert "gate-node" in graph.nodes
