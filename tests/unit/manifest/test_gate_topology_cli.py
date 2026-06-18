from __future__ import annotations

from app.manifest import gate_topology


def test_unfolded_topology_lists_all_declared_gates() -> None:
    output = gate_topology.render_topology(unfolded=True)

    assert output.count("|") == 18
    assert "G0    | fold_with: G1" in output
    assert "G5    | fold_with: G4" in output


def test_folded_topology_lists_active_pause_points_only() -> None:
    output = gate_topology.render_topology(unfolded=False)

    # Arc 2 (2026-06-18): G2B (variant) + G4A (voice) woken → 6 active pause
    # points (was 4: G1/G2C/G3/G4).
    assert output.count("|") == 6
    assert "G1    | pause_point" in output
    assert "G2B   | pause_point" in output
    assert "G2C   | pause_point" in output
    assert "G4A   | pause_point" in output
    assert "G0    |" not in output


def test_audit_topology_runs_without_error() -> None:
    output = gate_topology.render_audit()

    assert "code  | manifest" in output
    assert "G2M" in output
