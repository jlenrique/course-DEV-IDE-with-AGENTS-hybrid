from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.gates.errors import GateError
from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
            )
        )
        return updated


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


def _pause(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    return production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )


def _verdict(tmp_path: Path, verb: str, **overrides) -> OperatorVerdict:
    payload = json.loads((tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text())
    return OperatorVerdict(
        trial_id=TRIAL_ID,
        verb=verb,
        gate_id="G1",
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=overrides.pop("digest", payload["digest"]),
        **overrides,
    )


def test_approve_verdict_resumes_execution_then_pauses_at_g2c(
    tmp_path: Path, monkeypatch
) -> None:
    """Resume after G1 verdict executes specialist nodes, then PAUSES at G2C.

    Multi-gate pause-and-resume was the `7a-2-deferred-resume-mode-multi-gate-
    pause` follow-on this test's predecessor documented; implemented 2026-06-11
    (Trial-3 attempt-3 defect #5, party-mode 4-of-4 Option-A consensus). The
    former GateBypassError raise is deliberately converted to the shared
    `_pause_at_gate` pause — silent bypass remains impossible because an
    undecided gate pauses with a registered DecisionCard, and decided gates
    are never revisited (resume starts at checkpoint.next_node_index).
    """
    _pause(tmp_path, monkeypatch)

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2C"
    card_payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").read_text()
    )
    assert card_payload["card"]["gate_id"] == "G2C"
    assert len(card_payload["digest"]) == 64


def test_edit_verdict_propagates_to_resume_state(tmp_path: Path, monkeypatch) -> None:
    """Edit verdict's payload reaches resume state; the resume then pauses at
    G2C (multi-gate pause implemented 2026-06-11). The state mutation is
    verified via the resume-command.json artifact."""
    _pause(tmp_path, monkeypatch)
    edit_payload = {"slide_count": 3}

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "edit", edit_payload=edit_payload),
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2C"
    command = json.loads((tmp_path / str(TRIAL_ID) / "resume-command.json").read_text())
    assert json.loads(command["run_state"]["cache_state"]["cache_prefix"]) == edit_payload


def test_reject_verdict_halts_trial(tmp_path: Path, monkeypatch) -> None:
    _pause(tmp_path, monkeypatch)

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "reject", reject_reason="not acceptable"),
        runs_root=tmp_path,
    )

    assert envelope.status == "failed"


def test_digest_mismatch_refuses_resume(tmp_path: Path, monkeypatch) -> None:
    _pause(tmp_path, monkeypatch)

    with pytest.raises(GateError, match="digest_mismatch"):
        production_runner.resume_production_trial(
            trial_id=TRIAL_ID,
            verdict=_verdict(tmp_path, "approve", digest="b" * 64),
            runs_root=tmp_path,
        )
