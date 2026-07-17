from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.pre_gate_marcus import PreFillProposal
from app.models.runtime import ProductionEnvelope, SpecialistContribution

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abf")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    """Deterministic specialist dispatch — no live call, no billable span.

    Story 41-2: a production run now fails loud on any entered, not-already-
    carrying specialist that does not dispatch, so a valid production-run setup
    must actually dispatch the pre-G1 specialists (texas@02/03) rather than lean
    on the old silent-skip. This fake stands in for the real adapter under a
    sufficient specialist-call budget.
    """

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        cost_usd: float = 0.0,
        node_id: str | None = None,
        **_kwargs: object,
    ) -> ProductionEnvelope:
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used="fixture",
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


@pytest.fixture(autouse=True)
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a — flip-robustness pin (D-migrate-canonical, pin OFF).

    The subject is the pre-gate-marcus trace shape at the FIRST gate (one LLM
    child-run named ``pre-gate-marcus G1``). Pinning ``MARCUS_G0_ENRICHMENT_ACTIVE``
    OFF explicitly keeps the first gate G1 under the 3b default flip; the pre-gate
    trace assertion is orthogonal to G0-enrichment. Explicit ``"0"`` survives the
    code-default flip.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


def test_pre_gate_marcus_trace_records_single_invocation_per_gate(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-live-test")
    monkeypatch.setattr(
        production_runner.pre_gate_marcus,
        "invoke_pre_gate_marcus",
        lambda **_: PreFillProposal(
            decision="confirm",
            directive="accept-as-is",
            rationale="The trace fixture should record one pre-gate call.",
            confidence=0.8,
            confidence_signals=("trace-pin",),
        ),
    )
    # Story 41-2: the prior setup used max_specialist_calls=0 to avoid dispatching
    # the pre-G1 specialists (no adapter mock), relying on the now-removed silent
    # budget-skip. Give a real budget + a fake adapter so texas@02/03 dispatch
    # cleanly to G1, and stub preflight/cost so this trace-shape pin runs in the
    # sandbox (the subject is the pre-gate-marcus trace, orthogonal to both).
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    monkeypatch.setattr(
        production_runner,
        "_run_start_preflight_gate",
        lambda *_a, **_k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    monkeypatch.setattr(
        production_runner,
        "_record_cost",
        lambda **_k: tmp_path / str(TRIAL_ID) / "cost-report.json",
    )

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )

    trace_path = tmp_path / str(TRIAL_ID) / "trace-fixture.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    child_runs = trace["root"]["child_runs"]
    pre_gate_runs = [
        run for run in child_runs if run["extra"]["metadata"].get("node_id") == "pre-gate-marcus"
    ]

    assert envelope.paused_gate == "G1"
    assert len(pre_gate_runs) == 1
    assert pre_gate_runs[0]["name"] == "pre-gate-marcus G1"
    assert pre_gate_runs[0]["run_type"] == "llm"
