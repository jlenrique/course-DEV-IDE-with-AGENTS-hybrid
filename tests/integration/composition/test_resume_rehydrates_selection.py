"""S2 — two-walk resume: the continuation walk REHYDRATES component_selection from
the frozen run record and NEVER re-composes/re-defaults (the two-walk trap)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.component_selection import ComponentSelection
from app.models.state.operator_verdict import OperatorVerdict

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")

_REAL_SHAPED_OUTPUTS: dict[str, dict] = {
    "irene_pass1": {
        "lesson_plan": {
            "plan_units": [
                {
                    "unit_id": "PU-1",
                    "title": "Unit",
                    "learning_objective": "Objective",
                    "scope_decision": "in-scope",
                }
            ]
        }
    },
    "cd": {"cd_directive": {"experience_profile": "text-led"}},
}


class _FakeAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
        runner_supplied_payload: dict | None = None,
        projection_map: dict | None = None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state, runner_supplied_payload, projection_map
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=_REAL_SHAPED_OUTPUTS.get(specialist_id, {"specialist_id": specialist_id}),
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
                node_id=node_id,
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
        max_specialist_calls=12,
    )


def _verdict(tmp_path: Path, verb: str, *, gate_id: str = "G1") -> OperatorVerdict:
    payload = json.loads(
        (tmp_path / str(TRIAL_ID) / f"decision-card-{gate_id}.json").read_text()
    )
    return OperatorVerdict(
        trial_id=TRIAL_ID,
        verb=verb,
        gate_id=gate_id,
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=payload["digest"],
    )


def test_start_walk_persists_component_selection(tmp_path: Path, monkeypatch) -> None:
    _pause(tmp_path, monkeypatch)
    checkpoint = json.loads(
        (tmp_path / str(TRIAL_ID) / "checkpoint.json").read_text(encoding="utf-8")
    )
    selection = checkpoint["run_state"]["component_selection"]
    assert selection == {"deck": True, "motion": True, "workbook": False}


def test_resume_rehydrates_frozen_selection_and_never_re_defaults(
    tmp_path: Path, monkeypatch
) -> None:
    _pause(tmp_path, monkeypatch)

    # After the start walk, poison the default: if the continuation walk
    # re-defaults instead of rehydrating the frozen selection, this raises.
    def _boom() -> ComponentSelection:
        raise AssertionError("continuation walk re-defaulted instead of rehydrating")

    monkeypatch.setattr(ComponentSelection, "production_default", staticmethod(_boom))

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )
    # The continuation walk recomposed the SAME (motion-bearing) graph and reached
    # the woken G2B variant pick — exactly as a non-composed run would.
    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2B"


def test_resume_command_run_state_carries_same_selection(
    tmp_path: Path, monkeypatch
) -> None:
    _pause(tmp_path, monkeypatch)
    production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )
    command = json.loads(
        (tmp_path / str(TRIAL_ID) / "resume-command.json").read_text(encoding="utf-8")
    )
    assert command["run_state"]["component_selection"] == {
        "deck": True,
        "motion": True,
        "workbook": False,
    }
