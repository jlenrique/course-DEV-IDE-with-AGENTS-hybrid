"""Condition-function registry for `EdgeSpec.condition` resolution.

Slab 1 stub — exposes only `"always_true"` and `"always_false"`. Full dispatch
registry lands at Slab 3. EdgeSpec entries whose `condition` value is not in
this registry raise `CompileError` at compile time.

Signature matches LangGraph's conditional-edges contract: `(state) -> str`
returning the next node id (or a branch key the compiler rewires).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ConditionFn = Callable[[Any], str]


def _always_true(_state: Any) -> str:
    """Stub condition — always routes to the first branch target."""
    return "true"


def _always_false(_state: Any) -> str:
    """Stub condition — always routes to the second branch target."""
    return "false"


CONDITION_REGISTRY: dict[str, ConditionFn] = {
    "always_true": _always_true,
    "always_false": _always_false,
}
"""Registry of allowed condition names. Slab 3 will extend; Slab 1 is stub-only."""


def resolve(name: str) -> ConditionFn:
    """Resolve a condition name to its callable; raise KeyError on unknown."""
    if name not in CONDITION_REGISTRY:
        raise KeyError(
            f"unknown condition {name!r}; "
            f"Slab 1 stub registry supports only: {sorted(CONDITION_REGISTRY)}"
        )
    return CONDITION_REGISTRY[name]


__all__ = ["CONDITION_REGISTRY", "ConditionFn", "resolve"]
