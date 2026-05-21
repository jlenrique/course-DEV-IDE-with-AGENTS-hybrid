"""Reference parity-contract registration placeholder for Story 7c.0b.

Downstream Story 7c.1 refactors the existing transport-parity tests onto the
DSL. This module proves import-time decorator registration without touching
those reserved test files.
"""

from __future__ import annotations

from app.parity.contracts._decorator import parity_contract


@parity_contract(
    surface_id="reference_7c0b_scaffold",
    mandatory_transports=["cli"],
    optional_transports=["http"],
)
def reference_surface_placeholder() -> str:
    return "reference_7c0b_scaffold"


__all__ = ["reference_surface_placeholder"]
