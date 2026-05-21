"""AC-T.11 — Rationale verbatim round-trip (R1 ruling amendment 16 surface).

Parametrized over the R2 S-2 + M-extra matrix: multi-line, CRLF, tab, emoji,
embedded quotes, empty, single char, single word, leading-trailing whitespace.
All preserved byte-identical through a JSON round-trip.
"""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.schema import PlanUnit, ScopeDecision


def _make_unit(rationale: str) -> PlanUnit:
    sd = ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by="marcus",
    )
    return PlanUnit(
        unit_id="gagne-event-3",
        event_type="gagne-event-3",
        source_fitness_diagnosis="ok",
        scope_decision=sd,
        weather_band="amber",
        rationale=rationale,
    )


RATIONALE_MATRIX = [
    # R1 amendment 16 original matrix
    "multi\nline\nrationale",
    "unicode café résumé naïve",
    'has "embedded double quotes"',
    # M-extra
    "windows\r\nstyle\r\nnewlines",
    "tabs\tbetween\twords",
    "emoji surface: revisit 🔬",
    # S-2 edges
    "",
    "R",
    "revisit",
    "  revisit  ",
]


@pytest.mark.parametrize("rationale", RATIONALE_MATRIX)
def test_rationale_roundtrip_preserves_byte_identical_string(rationale: str) -> None:
    pu = _make_unit(rationale)
    serialized = pu.model_dump_json()
    restored = PlanUnit.model_validate_json(serialized)
    assert restored.rationale == rationale, (
        f"Rationale drifted on round-trip. Input: {rationale!r}; "
        f"Output: {restored.rationale!r}. "
        f"Free text is stored verbatim (R1 amendment 16)."
    )


def test_rationale_empty_string_is_valid() -> None:
    pu = _make_unit("")
    assert pu.rationale == ""


def test_rationale_leading_trailing_whitespace_preserved() -> None:
    pu = _make_unit("  revisit  ")
    assert pu.rationale == "  revisit  "
    # Round-trip must ALSO preserve the whitespace.
    restored = PlanUnit.model_validate_json(pu.model_dump_json())
    assert restored.rationale == "  revisit  "
