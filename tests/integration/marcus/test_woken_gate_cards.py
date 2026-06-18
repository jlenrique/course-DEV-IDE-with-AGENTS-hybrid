"""Arc 2 (2026-06-18): the woken variant/voice HIL gates build valid decision
cards instead of crashing, and are intentionally NOT storyboard gates.

Before Arc 2, `_build_decision_card` raised `RuntimeError("unsupported
production gate id")` for G2B/G4A (green-light BLOCKER). These pins prove the
card path is live for the two woken gates and guard the storyboard-roster
boundary (Edge Case Hunter AC-9).
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.storyboard_publisher import STORYBOARD_GATES
from app.models.decision_cards import G2BCard, G4ACard

_TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
_REPO_ROOT = Path(__file__).resolve().parents[3]


def _build(gate_id: str, node_id: str, tmp_path: Path):
    return production_runner._build_decision_card(
        gate_id=gate_id,
        trial_id=_TRIAL_ID,
        node_id=node_id,
        operator_id="operator_test",
        pending_nodes=["07C", "07D"],
        artifact_paths=[],
        runs_root=tmp_path,
    )


def test_build_decision_card_g2b_does_not_crash(tmp_path: Path) -> None:
    card = _build("G2B", "07B-gate", tmp_path)
    assert isinstance(card, G2BCard)
    assert card.gate_id == "G2B"
    assert card.gate_focus == "variant_selection"
    assert card.operator_prompt  # non-empty
    assert card.selected_variant_id is None  # default-accept until the operator picks
    # pick_context carries the adjacent evaluation the operator picks FROM
    # (at minimum the production-runner evidence entry).
    assert card.pick_context, "G2B card must surface pick context (review-finding remediation)"


def test_build_decision_card_g4a_does_not_crash(tmp_path: Path) -> None:
    card = _build("G4A", "11-gate", tmp_path)
    assert isinstance(card, G4ACard)
    assert card.gate_id == "G4A"
    assert card.gate_focus == "voice_selection"
    assert card.operator_prompt
    assert card.selected_voice_id is None
    assert card.pick_context, "G4A card must surface pick context (review-finding remediation)"


def test_pick_context_surfaces_the_real_adjacent_evaluation(tmp_path: Path, monkeypatch) -> None:
    """Murat P2 (2026-06-18): the bare `assert card.pick_context` passes on the
    always-present production-runner stub even when NO specialist evaluation
    surfaced. This proves the operator actually SEES the quinn-r evaluation —
    when an adjacent specialist summary exists, it lands in pick_context."""
    from datetime import UTC, datetime

    from app.models.state.specialist_summary_artifacts import AdjacentSummary

    summary = AdjacentSummary(
        path=tmp_path / "07B-quinn_r.md",
        text="VARIANT EVALUATION: slide-1 → variant-A (clearest); slide-2 → variant-B",
        timestamp_utc=datetime.now(UTC),
    )
    monkeypatch.setattr(
        production_runner.specialist_summary_writer,
        "load_most_recent_summary",
        lambda **_: summary,
    )
    card = _build("G2B", "07B-gate", tmp_path)
    summary_entries = [e for e in card.pick_context if e.get("kind") == "specialist-summary"]
    assert summary_entries, "the adjacent quinn-r evaluation must surface in pick_context"
    assert summary_entries[0]["content"] == summary.text


def test_every_surfaced_gate_has_a_pre_gate_template() -> None:
    """Live-path guard (Blind Spot BLOCKER #1): a surfaced production gate
    crashes at the live pause if its pre-gate-marcus template is missing. Every
    gate in production_gate_ids MUST have docs/conversational-gates/<gate>.j2."""
    from app.manifest.compiler import production_gate_ids
    from app.manifest.loader import load
    from app.marcus.orchestrator.pre_gate_marcus import TEMPLATE_DIR

    manifest = load(_REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml")
    missing = [
        gid
        for gid in production_gate_ids(manifest)
        if not (TEMPLATE_DIR / f"{gid.lower()}.j2").exists()
    ]
    assert missing == [], f"surfaced gates without a pre-gate template (live crash): {missing}"


def test_every_surfaced_gate_has_a_cli_shim() -> None:
    """Live-path guard (Blind Spot MUST-FIX #2): the operator needs a CLI shim
    to submit a verdict at every surfaced gate."""
    from app.manifest.compiler import production_gate_ids
    from app.manifest.loader import load
    from app.marcus.cli.gate_shims._shim_parser import ACTIVE_TERMINAL_GATES

    manifest = load(_REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml")
    missing = [gid for gid in production_gate_ids(manifest) if gid not in ACTIVE_TERMINAL_GATES]
    assert missing == [], f"surfaced gates with no operator CLI shim: {missing}"


def test_woken_gates_are_not_storyboard_gates() -> None:
    # A variant/voice pick must NOT demand a Gary storyboard pack; a future
    # roster edit that added G2B/G4A here would silently break the pause.
    assert "G2B" not in STORYBOARD_GATES
    assert "G4A" not in STORYBOARD_GATES
