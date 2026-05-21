from __future__ import annotations

import inspect

from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.pre_gate_marcus import PreFillProposal


def test_pre_gate_marcus_does_not_promote_per_specialist_gates() -> None:
    signature = inspect.signature(production_runner.run_production_trial)
    assert "gate_overrides" not in signature.parameters

    card = production_runner._build_decision_card(
        gate_id="G1",
        trial_id="12345678-1234-4234-8234-123456789abc",
        node_id="04",
        operator_id="operator_test",
        pending_nodes=["04A"],
        artifact_paths=[],
        pre_fill=PreFillProposal(
            decision="confirm",
            directive="accept-as-is",
            rationale="The gate can proceed without changing precedence.",
            confidence=0.7,
        ),
    )

    assert card.drafted_proposal["decision"] == "confirm"
    assert not hasattr(card, "gate_overrides")
