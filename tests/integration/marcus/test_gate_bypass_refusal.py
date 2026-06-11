from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abd")
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
        runner_supplied_payload: dict[str, str] | None = None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state, runner_supplied_payload
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


def test_active_gate_bypass_without_verdict_raises(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    with pytest.raises(
        production_runner.GateBypassError,
        match="refused silent bypass of gate G1 at manifest node 04",
    ):
        production_runner.run_production_trial(
            CORPUS,
            "production",
            "operator_test",
            trial_id=TRIAL_ID,
            runs_root=tmp_path,
            pause_at_gates=False,
        )


def test_folded_gates_do_not_raise_before_parent_pause(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G1"


def test_offline_cost_report_can_still_skip_pause_points(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        pause_at_gates=False,
        allow_offline_cost_report=True,
    )

    assert envelope.status == "completed"
    assert envelope.cost_report_path is not None


def test_resume_pauses_at_next_gate_with_full_artifacts(
    tmp_path: Path, monkeypatch
) -> None:
    """Live resume from an approved G1 PAUSES at G2C with full pause artifacts.

    REWRITES the former ``test_resume_refuses_later_gate_bypass``, which
    pinned Trial-3 attempt-3 defect #5 as a feature: the resume walker had
    no pause machinery and raised GateBypassError at every gate in live
    mode, so no live trial could ever advance gate-to-gate. The guard was
    DELIBERATELY converted into the shared ``_pause_at_gate`` pause (party-
    mode 4-of-4 Option-A consensus 2026-06-11; Murat assertion #4 "decide,
    don't drift"). Silent bypass remains impossible: an undecided gate now
    pauses with a registered DecisionCard instead of crashing the resume,
    and a decided gate is never revisited because the resume walk starts at
    checkpoint.next_node_index, which is already past it. The start-path
    bypass guard (test_active_gate_bypass_without_verdict_raises) is
    unchanged.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    manifest_path = tmp_path / "two-gate-manifest.yaml"
    manifest_path.write_text(
        """
schema_version: "1.0"
lane: "run_graph"
entrypoint: "01"
frozen_graph_version: "v42"
nodes:
  - id: "01"
    specialist_id: "texas"
  - id: "02"
    specialist_id: "marcus"
    gate: true
    gate_code: "G1"
  - id: "03"
    specialist_id: "irene"
  - id: "04"
    specialist_id: "marcus"
    gate: true
    gate_code: "G2C"
edges:
  - from: "__start__"
    to: "01"
  - from: "01"
    to: "02"
  - from: "02"
    to: "03"
  - from: "03"
    to: "04"
  - from: "04"
    to: "__end__"
""".lstrip(),
        encoding="utf-8",
    )
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=manifest_path,
        max_specialist_calls=1,
    )
    payload = json.loads((tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text())
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=payload["digest"],
    )

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=verdict,
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    # Envelope paused at the NEXT gate, not crashed, not completed.
    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2C"
    # The resume segment dispatched the intervening specialist (node 03).
    assert envelope.production_envelope.get_contribution("irene") is not None
    # Full pause artifacts: decision card on disk with registered digest.
    card_payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").read_text(
            encoding="utf-8"
        )
    )
    assert card_payload["card"]["gate_id"] == "G2C"
    assert len(card_payload["digest"]) == 64
    from app.gates.resume_api import get_registered_decision_card

    stored = get_registered_decision_card(TRIAL_ID, "G2C")
    assert stored is not None
    assert stored.digest == card_payload["digest"]
    # Checkpoint advanced to the ABSOLUTE post-G2C index (G2C is manifest
    # node index 3; next_node_index = 3 + 1). Guards the off-by-relative
    # landmine: a relative resume index would write a wrong checkpoint and
    # re-enter or skip a gate on the following resume.
    checkpoint = json.loads(
        (tmp_path / str(TRIAL_ID) / "checkpoint.json").read_text(encoding="utf-8")
    )
    assert checkpoint["gate_id"] == "G2C"
    assert checkpoint["next_node_index"] == 4
    # Persisted run.json agrees with the returned envelope.
    persisted = json.loads((tmp_path / str(TRIAL_ID) / "run.json").read_text())
    assert persisted["status"] == "paused-at-gate"
    assert persisted["paused_gate"] == "G2C"
