from __future__ import annotations

from pathlib import Path

from app.manifest.compiler import (
    _resolve_production_handler,
    production_gate_ids,
)
from app.manifest.loader import load
from app.manifest.schema import NodeSpec, PipelineManifest

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_MANIFEST = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
COMPILER = REPO_ROOT / "app" / "manifest" / "compiler.py"


def _manifest(nodes: list[NodeSpec]) -> PipelineManifest:
    return PipelineManifest.model_construct(
        schema_version="test",
        lane="run_graph",
        entrypoint="__start__",
        frozen_graph_version="v0.1-stub",
        nodes=nodes,
        edges=[],
    )


def test_production_gate_ids_from_live_manifest() -> None:
    manifest = load(LIVE_MANIFEST)

    # Arc 2 (2026-06-18): G2B (variant) + G4A (voice) woken into the surfaced set.
    assert production_gate_ids(manifest) == frozenset({"G1", "G2B", "G2C", "G3", "G4A", "G4"})


def test_production_gate_id_literal_stays_in_sync_with_manifest() -> None:
    """Drift guard (Winston P2, 2026-06-18): the runtime envelope's
    `ProductionGateId` literal is the type that lets the runner REPRESENT a
    pause at a gate. It is hand-maintained; pin it to the manifest authority so
    a future woken/retired gate that diverges fails CI here, not at a live pause.
    Mirrors the GateId pin in tests/trial/test_trial3_transcript_shape.py."""
    from typing import get_args

    from app.models.runtime.production_trial_envelope import ProductionGateId

    manifest = load(LIVE_MANIFEST)
    assert set(get_args(ProductionGateId)) == production_gate_ids(manifest)


def test_production_gate_ids_empty_manifest() -> None:
    assert production_gate_ids(_manifest([])) == frozenset()


def test_production_gate_ids_excludes_fold_with_gate() -> None:
    manifest = _manifest(
        [
            NodeSpec(id="folded", gate=True, gate_code="G0", fold_with="G1"),
            NodeSpec(id="active", gate=True, gate_code="G1"),
        ]
    )

    assert production_gate_ids(manifest) == frozenset({"G1"})


def test_production_gate_ids_excludes_fold_target_gate() -> None:
    manifest = _manifest(
        [
            NodeSpec(id="folded", gate=True, gate_code="G0", fold_target="subgraph:g1"),
            NodeSpec(id="active", gate=True, gate_code="G1"),
        ]
    )

    assert production_gate_ids(manifest) == frozenset({"G1"})


def test_compiler_has_no_hardcoded_production_gate_ids_literal() -> None:
    source = COMPILER.read_text(encoding="utf-8")

    assert "PRODUCTION_GATE_IDS" not in source
    assert 'frozenset({"G1", "G2C", "G3", "G4"})' not in source


def test_resolve_production_handler_preserves_active_pause_points() -> None:
    manifest = load(LIVE_MANIFEST)
    by_code = {node.gate_code: node for node in manifest.nodes if node.gate_code}

    for gate_code in ("G1", "G2B", "G2C", "G3", "G4A", "G4"):
        handler = _resolve_production_handler(
            by_code[gate_code],
            dispatch_registry={},
            manifest=manifest,
        )
        assert handler.__production_node_kind__ == "gate"
        assert handler.__production_gate_id__ == gate_code
