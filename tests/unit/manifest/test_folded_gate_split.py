"""Arc 1a (2026-06-18, party-ratified): the co-located voice/variant HIL gates
were split into [content specialist] + [content-free folded gate node] so a
woken pause lands AFTER content. Pins the structural invariants (Murat A2,
drift-proof over the graph; A8 inert-when-folded) + the shared pack-exclusion
predicate, and that the original bug (a HIL gate's pause pre-content) cannot
recur.
"""

from __future__ import annotations

from pathlib import Path

from app.manifest.compiler import production_gate_ids
from app.manifest.loader import load
from app.manifest.schema import is_folded_gate, is_orchestration_only, is_pack_excluded

_MANIFEST = Path(__file__).resolve().parents[3] / "state" / "config" / "pipeline-manifest.yaml"


def _manifest():
    return load(_MANIFEST)


def test_content_free_folded_gates_follow_a_content_specialist() -> None:
    """A2 (Murat, drift-proof over the graph): every content-free folded gate
    node's sole immediate edge-predecessor is a content-producing specialist —
    i.e. the pause sits AFTER content. Stated structurally, not enumerated, so
    a future split gate is covered automatically."""
    m = _manifest()
    by_id = {n.id: n for n in m.nodes}
    content_free_gates = [n for n in m.nodes if is_folded_gate(n)]
    assert content_free_gates, "expected the Arc-1a content-free folded gate nodes"
    for gate in content_free_gates:
        preds = [e.from_node for e in m.edges if e.to == gate.id]
        assert len(preds) == 1, f"{gate.id} must have exactly one predecessor, got {preds}"
        pred = by_id.get(preds[0])
        assert pred is not None and pred.specialist_id, (
            f"{gate.id} predecessor {preds[0]} must be a content-producing specialist"
        )


def test_split_content_nodes_no_longer_carry_the_gate() -> None:
    """The bug-can't-recur pin: the 3 previously-co-located content nodes are
    pure content now; the gate_codes live on the new content-free gate nodes."""
    by_id = {n.id: n for n in _manifest().nodes}
    for content_id in ("07B", "11", "11B"):
        node = by_id[content_id]
        assert node.specialist_id, f"{content_id} stays a content specialist"
        assert node.gate is False and node.gate_code is None, (
            f"{content_id} must no longer carry a gate_code (it moved to the gate node)"
        )
    for gate_id, code in (("07B-gate", "G2B"), ("11-gate", "G4A"), ("11B-gate", "G4B")):
        node = by_id[gate_id]
        assert node.specialist_id is None and node.gate is True and node.gate_code == code


def test_folded_gates_are_inert_no_pause() -> None:
    """A8: a content-free folded gate is EXCLUDED from production_gate_ids (no
    pause; runs as a no-op pass-through). Single-control-plane: only membership
    converts folded→pause (Arc 1b)."""
    m = _manifest()
    gate_ids = production_gate_ids(m)
    for gate_id in ("07B-gate", "11-gate", "11B-gate"):
        node = next(n for n in m.nodes if n.id == gate_id)
        assert node.gate_code not in gate_ids, (
            f"{gate_id} ({node.gate_code}) must NOT be a surfaced pause while folded"
        )


def test_is_folded_gate_is_content_free_only() -> None:
    m = _manifest()
    by_id = {n.id: n for n in m.nodes}
    assert is_folded_gate(by_id["07B-gate"]) is True
    assert is_folded_gate(by_id["11-gate"]) is True
    # Content-BEARING folded gates (carry a specialist_id) are NOT matched —
    # they render + produce content; only PAUSING is folded.
    assert is_folded_gate(by_id["01"]) is False  # G0, fold_with G1, specialist marcus
    assert is_folded_gate(by_id["04A"]) is False  # G1A, fold_with G2C, specialist irene
    # Surfaced gate (fold_with None) is not folded.
    assert is_folded_gate(by_id["04"]) is False  # G1 surfaced


def test_is_pack_excluded_combines_orchestration_and_folded_gates() -> None:
    m = _manifest()
    by_id = {n.id: n for n in m.nodes}
    assert is_pack_excluded(by_id["07B-gate"]) is True  # content-free folded gate
    assert is_pack_excluded(by_id["directive-composer"]) is True  # orchestration-only
    assert is_orchestration_only(by_id["07B-gate"]) is False  # NOT orchestration (it's a gate)
    # Content-bearing nodes render → not excluded.
    assert is_pack_excluded(by_id["07B"]) is False
    assert is_pack_excluded(by_id["01"]) is False
