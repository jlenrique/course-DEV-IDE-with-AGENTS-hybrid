from __future__ import annotations

from pathlib import Path

from app.manifest import gate_topology
from app.manifest.loader import load

LIVE_MANIFEST = (
    Path(__file__).resolve().parents[3] / "state" / "config" / "pipeline-manifest.yaml"
)


def _declared_gate_nodes() -> list:
    """All declared gate nodes — the SSOT the unfolded topology enumerates."""
    manifest = load(LIVE_MANIFEST)
    return [node for node in manifest.nodes if node.gate and node.gate_code]


def test_unfolded_topology_lists_all_declared_gates() -> None:
    output = gate_topology.render_topology(unfolded=True)

    # Story 42-7 AC-3: DERIVED from the live manifest (self-maintains as gates are
    # added). Each declared gate renders exactly one "|" line, so the pipe count
    # equals the number of declared gate nodes (21 at 52-node manifest: +G0R
    # ratify-gate #2, +G0S pre-walk settings gate since the stale ==19 hardcode).
    assert output.count("|") == len(_declared_gate_nodes())
    assert "G0    | fold_with: G1" in output
    assert "G5    | fold_with: G4" in output


def test_folded_topology_lists_active_pause_points_only() -> None:
    output = gate_topology.render_topology(unfolded=False)

    # Story 42-7 AC-3: DERIVED from the live manifest. The folded view shows only
    # ACTIVE pause points — declared gates that are NOT folded (fold_with and
    # fold_target both None). Computed independently of the renderer's fold logic
    # so this stays a genuine guard, not a tautology. Arc 2 (2026-06-18) woke
    # G2B/G4A; G0-S2 added G0E; g0-enrichment S3 added G0R; 42-5 added G0S → 9.
    active_pause_points = [
        node
        for node in _declared_gate_nodes()
        if node.fold_with is None and node.fold_target is None
    ]
    assert output.count("|") == len(active_pause_points)
    assert "G0E   | pause_point" in output
    assert "G1    | pause_point" in output
    assert "G2B   | pause_point" in output
    assert "G2C   | pause_point" in output
    assert "G4A   | pause_point" in output
    assert "G0    |" not in output


def test_audit_topology_runs_without_error() -> None:
    output = gate_topology.render_audit()

    assert "code  | manifest" in output
    assert "G2M" in output
