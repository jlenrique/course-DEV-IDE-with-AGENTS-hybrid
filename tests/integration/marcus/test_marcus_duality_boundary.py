from __future__ import annotations

from uuid import UUID

import pytest
import yaml

from app.manifest.compiler import production_gate_ids
from app.manifest.loader import load
from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.marcus.orchestrator.gate_runner import (
    MarcusDualityBoundaryError,
    assert_marcus_duality_boundary,
)
from app.marcus.orchestrator.production_runner import (
    DEFAULT_MANIFEST_PATH,
    _emit_run_summary_yaml,
)
from app.models.runtime import ProductionEnvelope
from app.models.state.operator_verdict import OperatorVerdict

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def test_duality_boundary_rejects_mixed_state() -> None:
    with pytest.raises(MarcusDualityBoundaryError, match="must not mix"):
        assert_marcus_duality_boundary(
            orchestrator_mode_state={"graph": "production"},
            operator_handoff_state={"verdict_file": "verdict.json"},
        )


def test_dispatch_adapter_runtime_asserts_duality_boundary() -> None:
    adapter = ProductionDispatchAdapter(graph_builders={})

    with pytest.raises(MarcusDualityBoundaryError):
        adapter.build_specialist_state(
            envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            dependency_map={},
            runner_supplied_payload={
                "orchestrator_mode_state": {"node": "07C"},
                "operator_handoff_state": {"gate": "G2C"},
            },
        )


def test_dispatch_adapter_accepts_single_state_mode() -> None:
    adapter = ProductionDispatchAdapter(graph_builders={})

    state = adapter.build_specialist_state(
        envelope=ProductionEnvelope(trial_id=TRIAL_ID),
        dependency_map={},
        runner_supplied_payload={"orchestrator_mode_state": {"node": "07C"}},
    )

    assert state.production_envelope is None


def test_trial2_bypass_and_max3_invariants_hold_across_terminal_gates(tmp_path) -> None:
    run_summary = _emit_run_summary_yaml(
        trial_id=TRIAL_ID,
        terminal_gate="G3",
        runs_root=tmp_path,
        manifest_path=DEFAULT_MANIFEST_PATH,
        langsmith_trace_id=None,
    )
    payload = yaml.safe_load(run_summary.read_text(encoding="utf-8"))
    gates = production_gate_ids(load(DEFAULT_MANIFEST_PATH))

    assert payload["silent_bypass_events"] == 0
    # Arc 2 (2026-06-18): G2B (variant pick) + G4A (voice pick) woken into the
    # surfaced pause set. G0-S2 (2026-06-26): +G0E source-enrichment confirm-gate #1.
    assert gates == frozenset({"G0E", "G1", "G2B", "G2C", "G3", "G4A", "G4"})
    for gate_id in gates:
        verdict = OperatorVerdict(
            trial_id=TRIAL_ID,
            gate_id=gate_id,
            verb="edit",
            card_id=UUID("87654321-4321-4321-8321-cba987654321"),
            operator_id="operator_1",
            decision_card_digest="a" * 64,
            edit_payload={"requested_change": "tighten the operator-facing evidence"},
            revise_count=3,
        )
        assert verdict.revise_count == 3
        with pytest.raises(ValueError):
            OperatorVerdict(
                trial_id=TRIAL_ID,
                gate_id=gate_id,
                verb="edit",
                card_id=UUID("87654321-4321-4321-8321-cba987654321"),
                operator_id="operator_1",
                decision_card_digest="a" * 64,
                edit_payload={"requested_change": "one revision too many"},
                revise_count=4,
            )
