"""B6-land: RunState.llm_execution_mode defaults + round-trip."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.models.state.run_state import RunState


def test_run_state_defaults_llm_execution_mode_realtime() -> None:
    rs = RunState(graph_version="v42")
    assert rs.llm_execution_mode == "realtime"


def test_run_state_rejects_invalid_llm_execution_mode() -> None:
    with pytest.raises(ValidationError):
        RunState(graph_version="v42", llm_execution_mode="BATCH")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        RunState(graph_version="v42", llm_execution_mode="")  # type: ignore[arg-type]


def test_run_state_llm_execution_mode_round_trips_model_dump() -> None:
    rs = RunState(graph_version="v42", llm_execution_mode="batch")
    dumped = rs.model_dump(mode="json")
    assert dumped["llm_execution_mode"] == "batch"
    restored = RunState.model_validate(dumped)
    assert restored.llm_execution_mode == "batch"
    # Legacy checkpoints without the key rehydrate as realtime.
    legacy = {k: v for k, v in dumped.items() if k != "llm_execution_mode"}
    assert RunState.model_validate(legacy).llm_execution_mode == "realtime"
    # JSON round-trip preserves opt-in.
    again = RunState.model_validate_json(json.dumps(dumped))
    assert again.llm_execution_mode == "batch"
