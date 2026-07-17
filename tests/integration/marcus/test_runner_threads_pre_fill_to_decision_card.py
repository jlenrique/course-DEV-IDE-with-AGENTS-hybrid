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

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abe")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    """Deterministic specialist dispatch — no live call, no billable span.

    Story 41-2: a production run fails loud on any entered, not-already-carrying
    specialist that does not dispatch, so a valid setup must dispatch the pre-G1
    specialists rather than rely on the removed silent budget-skip.
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
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a.2 — file-corpus dormant-path migration (D-kill-switch pin).

    This walk passes a README FILE as ``corpus_path`` and first-pauses at G1 on the
    dormant path. The 3b default flip wakes G0-enrichment's corpus-DIRECTORY
    enumeration, which crashes pre-gate with ``DirectiveCompositionError`` on a file
    corpus. Pinning ``MARCUS_G0_ENRICHMENT_ACTIVE`` OFF explicitly preserves the
    enrichment-orthogonal downstream subject under the flip (explicit ``"0"`` survives
    the code-default flip). TEST-ONLY: no production/default change.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


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
    # Story 41-2: the prior max_specialist_calls=0 leaned on the now-removed
    # silent budget-skip of the pre-G1 specialists. Give a real budget + a fake
    # adapter so they dispatch cleanly to G1, and stub preflight/cost so this
    # decision-card threading pin runs in the sandbox (both orthogonal to it).
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
