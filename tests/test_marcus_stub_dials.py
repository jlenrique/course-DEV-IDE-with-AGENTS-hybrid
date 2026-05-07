"""Story 30-3a — StubDialsAffordance read-only contract.

AC-T.7 — dials affordance surfaces the Sally R1 verbatim line, has no
mutator methods, and rejects runtime field assignment.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.orchestrator.stub_dials import STUB_DIALS_MARCUS_LINE, StubDialsAffordance


def test_stub_dials_is_read_only_with_verbatim_marcus_line() -> None:
    """AC-T.7 — default affordance is read-only; Marcus line is pinned verbatim."""
    affordance = StubDialsAffordance()

    # Marcus line pinned exactly (Sally R1 guardrail).
    assert affordance.marcus_line == "I'll learn to tune these next sprint."
    assert STUB_DIALS_MARCUS_LINE == "I'll learn to tune these next sprint."
    assert affordance.mode == "read-only"

    # No mutator methods.
    forbidden_methods = {"tune", "set", "update", "set_dial", "mutate"}
    present = forbidden_methods & set(dir(affordance))
    assert not present, (
        f"StubDialsAffordance must be read-only; found mutator methods: {present}"
    )

    # Frozen model — attribute assignment raises.
    with pytest.raises(ValidationError):
        affordance.mode = "writable"  # type: ignore[misc]
