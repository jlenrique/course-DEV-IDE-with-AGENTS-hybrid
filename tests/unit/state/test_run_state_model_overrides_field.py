from __future__ import annotations

from app.models.state import RunState


def test_run_state_model_overrides_defaults_empty() -> None:
    state = RunState(graph_version="v0.1-stub")
    assert state.model_overrides == {}


def test_run_state_round_trip_with_model_overrides() -> None:
    state = RunState(
        graph_version="v0.1-stub",
        model_overrides={"04": "gpt-5-mini"},
    )
    round_tripped = RunState.model_validate(state.model_dump(mode="json"))
    assert round_tripped.model_overrides == {"04": "gpt-5-mini"}
