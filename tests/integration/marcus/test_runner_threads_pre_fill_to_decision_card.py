from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.pre_gate_marcus import PreFillProposal

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abe")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


def _proposal() -> PreFillProposal:
    return PreFillProposal(
        decision="confirm",
        directive="accept-as-is",
        rationale="The upstream state is complete enough for operator approval.",
        confidence=0.91,
        confidence_signals=("complete-evidence", "no-blockers"),
    )


def test_build_decision_card_threads_pre_fill_values() -> None:
    card = production_runner._build_decision_card(
        gate_id="G1",
        trial_id=TRIAL_ID,
        node_id="04",
        operator_id="operator_test",
        pending_nodes=["04A"],
        artifact_paths=[],
        pre_fill=_proposal(),
    )

    assert card.drafted_proposal == {
        "node_id": "04",
        "operator_id": "operator_test",
        "decision": "confirm",
        "directive": "accept-as-is",
        "rationale": "The upstream state is complete enough for operator approval.",
        "confidence": 0.91,
        "confidence_signals": ["complete-evidence", "no-blockers"],
    }


def test_build_decision_card_keeps_default_draft_without_pre_fill() -> None:
    card = production_runner._build_decision_card(
        gate_id="G1",
        trial_id=TRIAL_ID,
        node_id="04",
        operator_id="operator_test",
        pending_nodes=["04A"],
        artifact_paths=[],
    )

    assert card.drafted_proposal == {
        "node_id": "04",
        "operator_id": "operator_test",
    }


def test_runner_threads_pre_fill_to_persisted_decision_card(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-live-test")
    monkeypatch.setattr(
        production_runner.pre_gate_marcus,
        "invoke_pre_gate_marcus",
        lambda **_: _proposal(),
    )

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=0,
    )

    payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text(
            encoding="utf-8"
        )
    )
    assert envelope.status == "paused-at-gate"
    assert payload["card"]["drafted_proposal"]["directive"] == "accept-as-is"
    assert payload["card"]["drafted_proposal"]["confidence_signals"] == [
        "complete-evidence",
        "no-blockers",
    ]
