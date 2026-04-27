from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.marcus.orchestrator.dispatch_adapter import (
    ProductionDispatchAdapter,
    ProductionDispatchAdapterError,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def _entry(reason: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level="registry_default",
        requested=None,
        resolved="gpt-5-nano",
        reason=reason,
        timestamp=datetime.now(UTC),
        cache_prefix_hash="a" * 64,
    )


def _contribution(specialist_id: str, output: dict[str, object]) -> SpecialistContribution:
    return SpecialistContribution(
        specialist_id=specialist_id,
        contributed_at=datetime.now(UTC),
        output=output,
        cost_usd=0.0,
        model_used="gpt-5-nano",
        output_digest=compute_output_digest(output),
    )


class _Graph:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def compile(self) -> _Graph:
        return self

    def invoke(self, state: RunState, **_: object) -> dict[str, object]:
        for node_id in (
            "receive",
            "plan",
            "act",
            "verify",
            "reflect",
            "emit_spans",
            "gate_decision",
        ):
            self.calls.append(node_id)
            if node_id == "plan":
                state = RunState.model_validate(
                    {
                        **state.model_dump(mode="python"),
                        **self._plan(state),
                    }
                )
            elif node_id == "act":
                state = RunState.model_validate(
                    {
                        **state.model_dump(mode="python"),
                        **self._act(state),
                    }
                )
        payload = state.model_dump(mode="python")
        payload["__interrupt__"] = [{"gate_id": "fake-gate"}]
        return payload

    @staticmethod
    def _plan(state: RunState) -> dict[str, object]:
        return {"model_resolution_trail": [*state.model_resolution_trail, _entry("plan")]}

    @staticmethod
    def _act(state: RunState) -> dict[str, object]:
        assert state.cache_state is not None
        payload = json.loads(state.cache_state.cache_prefix)
        return {
            "cache_state": {
                "cache_prefix": json.dumps(
                    {"received": payload, "ok": True},
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "entries_count": 1,
            },
            "model_resolution_trail": [*state.model_resolution_trail, _entry("act")],
        }


def test_input_construction_reads_dependency_map_from_envelope() -> None:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(_contribution("texas", {"bundle_reference": "bundle"}))
    adapter = ProductionDispatchAdapter()

    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={"source_bundle": "texas"},
    )

    assert state.cache_state is not None
    assert json.loads(state.cache_state.cache_prefix) == {
        "source_bundle": {"bundle_reference": "bundle"}
    }
    assert state.production_envelope is None


def test_specialist_invocation_runs_compiled_graph_through_gate_boundary() -> None:
    calls: list[str] = []
    adapter = ProductionDispatchAdapter(
        graph_builders={"cd": lambda: _Graph(calls)}
    )
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)

    updated = adapter.invoke_specialist(
        specialist_id="cd",
        envelope=envelope,
        dependency_map={},
        cost_usd=0.01,
    )

    assert calls == [
        "receive",
        "plan",
        "act",
        "verify",
        "reflect",
        "emit_spans",
        "gate_decision",
    ]
    assert adapter.last_interrupts == [{"gate_id": "fake-gate"}]
    assert [item.specialist_id for item in updated.contributions] == ["cd"]
    assert updated.contributions[0].cost_usd == 0.01


def test_output_extraction_appends_contribution_to_envelope() -> None:
    adapter = ProductionDispatchAdapter(graph_builders={"cd": lambda: _Graph([])})
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(_contribution("texas", {"status": "complete"}))

    updated = adapter.invoke_specialist(
        specialist_id="cd",
        envelope=envelope,
        dependency_map={"source_bundle": "texas"},
        cost_usd=0.02,
    )

    cd = updated.get_contribution("cd")
    assert cd is not None
    assert cd.output == {
        "received": {"source_bundle": {"status": "complete"}},
        "ok": True,
    }
    assert cd.output_digest == compute_output_digest(cd.output)
    assert [item.specialist_id for item in envelope.contributions] == ["texas"]


def test_missing_dependency_raises_before_specialist_invocation() -> None:
    adapter = ProductionDispatchAdapter(graph_builders={"cd": lambda: _Graph([])})

    with pytest.raises(ProductionDispatchAdapterError, match="absent"):
        adapter.invoke_specialist(
            specialist_id="cd",
            envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            dependency_map={"source_bundle": "texas"},
            cost_usd=0.0,
        )


def test_duplicate_specialist_contribution_raises_before_invocation() -> None:
    calls: list[str] = []
    adapter = ProductionDispatchAdapter(graph_builders={"cd": lambda: _Graph(calls)})
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(_contribution("cd", {"existing": True}))

    with pytest.raises(ValueError, match="already has contribution"):
        adapter.invoke_specialist(
            specialist_id="cd",
            envelope=envelope,
            dependency_map={},
            cost_usd=0.0,
        )
    assert calls == []


def test_base_state_trial_id_must_match_envelope() -> None:
    adapter = ProductionDispatchAdapter(graph_builders={"cd": lambda: _Graph([])})
    base_state = RunState(
        run_id=UUID("99999999-9999-4999-8999-999999999999"),
        graph_version="v42",
    )

    with pytest.raises(ProductionDispatchAdapterError, match="run_id"):
        adapter.invoke_specialist(
            specialist_id="cd",
            envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            dependency_map={},
            cost_usd=0.0,
            base_state=base_state,
        )


def test_missing_output_raises_contract_error() -> None:
    class _NoOutputGraph:
        def compile(self) -> _NoOutputGraph:
            return self

        @staticmethod
        def invoke(state: RunState, **_: object) -> dict[str, object]:
            return state.model_dump(mode="python")

    adapter = ProductionDispatchAdapter(graph_builders={"cd": _NoOutputGraph})

    with pytest.raises(ProductionDispatchAdapterError, match="entries_count"):
        adapter.invoke_specialist(
            specialist_id="cd",
            envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            dependency_map={},
            cost_usd=0.0,
        )


def test_missing_model_resolution_trail_raises_contract_error() -> None:
    class _NoModelEvidenceGraph:
        def compile(self) -> _NoModelEvidenceGraph:
            return self

        @staticmethod
        def invoke(state: RunState, **_: object) -> dict[str, object]:
            assert state.cache_state is not None
            return {
                **state.model_dump(mode="python"),
                "cache_state": {
                    "cache_prefix": json.dumps({"ok": True}),
                    "entries_count": state.cache_state.entries_count + 1,
                },
            }

    adapter = ProductionDispatchAdapter(graph_builders={"cd": _NoModelEvidenceGraph})

    with pytest.raises(ProductionDispatchAdapterError, match="model_resolution_trail"):
        adapter.invoke_specialist(
            specialist_id="cd",
            envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            dependency_map={},
            cost_usd=0.0,
        )
