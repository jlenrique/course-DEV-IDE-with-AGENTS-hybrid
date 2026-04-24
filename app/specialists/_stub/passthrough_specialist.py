"""`passthrough_node` — Slab 1 specialist stub (AC-1.6-B).

A no-op LangGraph node that accepts any state and returns an empty dict
(so Pydantic-state reducers propagate the input state unchanged). Used by
the 1.6 migrated manifest for all 33 v4.2 steps until Slab 2 specialists
(Stories 2a.1 / 2b.*) replace per-specialist entries with real 9-node
scaffolds.

Exposed via `app.specialists._stub` — the `_stub` prefix keeps the passthrough
module out of any Slab-2+ directory scan that iterates `app.specialists.*` for
real specialist registration.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

PASSTHROUGH_SPECIALIST_ID = "_passthrough"
"""Sentinel `specialist_id` the compiler resolves to `passthrough_node`.

Not used by the migrated manifest itself (which names real specialists for
1.6 documentation value). Reserved for future test fixtures that need a
named passthrough in a manifest.
"""


def passthrough_node(state: Any) -> dict[str, Any]:
    """No-op node that returns `{}` so LangGraph's state reducer leaves state intact."""
    del state
    return {}


def make_passthrough(_specialist_id: str | None = None) -> Callable[[Any], dict[str, Any]]:
    """Factory returning `passthrough_node`; signature kept for Slab 2 extension.

    Slab 2 replaces the compiler's `_passthrough_node` helper with a resolver
    that looks up the real `app.specialists.{specialist_id}.graph` entry
    point. Until then, every specialist_id resolves here.
    """
    return passthrough_node


__all__ = ["PASSTHROUGH_SPECIALIST_ID", "make_passthrough", "passthrough_node"]
