from __future__ import annotations

import inspect

import pytest
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy
from pydantic import BaseModel, ConfigDict, ValidationError

from app.runtime import retry_policy as retry_policy_module


class _RetryState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempts: int = 0
    output: int = 0


class _Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: int


def _compile_graph(node, *, retry_policy: RetryPolicy):
    builder = StateGraph(_RetryState)
    builder.add_node("retry_node", node, retry_policy=retry_policy)
    builder.set_entry_point("retry_node")
    builder.set_finish_point("retry_node")
    return builder.compile()


def test_raw_validation_error_does_not_retry() -> None:
    attempts = {"count": 0}

    def node(state: _RetryState) -> dict[str, int]:
        attempts["count"] += 1
        raw_payload = {"value": "bad"} if attempts["count"] == 1 else {"value": 7}
        payload = _Payload.model_validate(raw_payload)
        return {"attempts": attempts["count"], "output": payload.value}

    graph = _compile_graph(
        node,
        retry_policy=RetryPolicy(
            max_attempts=2,
            initial_interval=0.0,
            jitter=False,
        ),
    )

    with pytest.raises(ValidationError):
        graph.invoke({"attempts": 0, "output": 0})

    assert attempts["count"] == 1


def test_retryable_validation_wrapper_succeeds_on_retry() -> None:
    attempts = {"count": 0}

    def node(state: _RetryState) -> dict[str, int]:
        attempts["count"] += 1
        raw_payload = {"value": "bad"} if attempts["count"] == 1 else {"value": 7}
        payload = retry_policy_module.validate_for_retry(
            _Payload,
            raw_payload,
            node_name="retry_node",
        )
        return {"attempts": attempts["count"], "output": payload.value}

    graph = _compile_graph(
        node,
        retry_policy=retry_policy_module.pydantic_retry_policy(
            max_attempts=2,
            initial_interval=0.0,
            jitter=False,
        ),
    )

    result = graph.invoke({"attempts": 0, "output": 0})

    assert result["output"] == 7
    assert attempts["count"] == 2


def test_workaround_documented_in_docstring() -> None:
    doc = inspect.getdoc(retry_policy_module)

    assert doc is not None
    assert "validate_for_retry" in doc
    assert "pydantic_retry_policy" in doc
    assert "does not treat a raw Pydantic" in doc
