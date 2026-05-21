"""Stub-dials affordance (Story 30-3a — Sally R1 guardrail).

Maya-facing note
----------------

Maya sees the dials as a read-only "coming soon" affordance. Marcus's
line is pinned verbatim: *"I'll learn to tune these next sprint."*

Developer discipline note
-------------------------

* **30-3a (this commit):** read-only affordance — no mutator methods, no
  tuning logic, no dial state transitions. Frozen dataclass semantics.
* **30-3b (next):** adds the tuning surface + sync reassessment cycles.

The class deliberately exposes **no** ``tune()`` / ``set()`` / ``update()``
mutator API. A contract test asserts the absence of such methods.
"""

from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

__all__: Final[tuple[str, ...]] = (
    "STUB_DIALS_MARCUS_LINE",
    "StubDialsAffordance",
)


STUB_DIALS_MARCUS_LINE: Final[str] = "I'll learn to tune these next sprint."
"""Verbatim Marcus line rendered alongside the read-only stub-dials affordance
(Sally R1 guardrail). Exact string — no emoji, no hedges, no variations."""


class StubDialsAffordance(BaseModel):
    """Read-only dials affordance surfaced at plan-drafting time.

    Frozen model with no mutator methods. Rendered in the facade's
    conversation surface as a visual placeholder; the tuning UI lands
    at Story 30-3b.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    mode: Literal["read-only"] = "read-only"
    marcus_line: Literal["I'll learn to tune these next sprint."] = Field(
        default=STUB_DIALS_MARCUS_LINE,
        description="Sally R1 guardrail — verbatim.",
    )
    dial_names: frozenset[str] = Field(
        default=frozenset(),
        description=(
            "Names of dials that will become tunable at 30-3b. Frozenset for "
            "immutability; empty default until the 30-3b spec fixes the "
            "dial-name set."
        ),
    )
