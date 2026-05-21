"""Pydantic-aware RetryPolicy helpers for LangGraph nodes.

LangGraph's default ``RetryPolicy`` does not treat a raw Pydantic
``ValidationError`` as retryable. If a node performs its own
``model_validate(...)`` call against flaky provider or tool payloads and lets
that exception escape, the graph fails on the first bad payload even when the
next attempt would succeed.

The workaround is to keep validation at the node boundary, translate
``ValidationError`` into a runtime-owned retryable exception, and pair that
node with ``pydantic_retry_policy()``.

Example:

```python
from pydantic import BaseModel

from app.runtime.retry_policy import (
    pydantic_retry_policy,
    validate_for_retry,
)


class Payload(BaseModel):
    value: int


def compose_return(state: dict[str, object]) -> dict[str, object]:
    payload = validate_for_retry(
        Payload,
        flaky_provider_call(),
        node_name="compose_return",
    )
    return {"value": payload.value}


builder.add_node(
    "compose_return",
    compose_return,
    retry_policy=pydantic_retry_policy(max_attempts=2, jitter=False),
)
```
"""

from __future__ import annotations

from typing import Any, TypeVar

from langgraph.types import RetryPolicy
from pydantic import BaseModel, ValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)


class RetryableValidationNodeError(RuntimeError):
    """Wrap a Pydantic validation failure so LangGraph can retry the node."""

    def __init__(
        self,
        *,
        node_name: str,
        model_name: str,
        error: ValidationError,
    ) -> None:
        self.node_name = node_name
        self.model_name = model_name
        self.error = error
        super().__init__(
            f"{node_name} failed {model_name} validation inside retry boundary"
        )


def validate_for_retry(
    model_type: type[ModelT],
    payload: Any,
    *,
    node_name: str,
) -> ModelT:
    """Validate payload and re-raise as a retryable runtime-owned exception."""
    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        raise RetryableValidationNodeError(
            node_name=node_name,
            model_name=model_type.__name__,
            error=exc,
        ) from exc


def pydantic_retry_policy(
    *,
    initial_interval: float = 0.5,
    backoff_factor: float = 2.0,
    max_interval: float = 128.0,
    max_attempts: int = 3,
    jitter: bool = True,
) -> RetryPolicy:
    """Return the canonical retry policy for retry-wrapped Pydantic validation."""
    return RetryPolicy(
        initial_interval=initial_interval,
        backoff_factor=backoff_factor,
        max_interval=max_interval,
        max_attempts=max_attempts,
        jitter=jitter,
        retry_on=RetryableValidationNodeError,
    )


__all__ = [
    "RetryableValidationNodeError",
    "pydantic_retry_policy",
    "validate_for_retry",
]
