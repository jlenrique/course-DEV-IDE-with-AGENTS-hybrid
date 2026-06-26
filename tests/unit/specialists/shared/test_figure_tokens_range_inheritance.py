"""Range-aware unit inheritance for the shared figure tokenizer.

Authority: pass2-figure-citation-gate false-positive on trial
6a103b6c-943f-4e53-90e1-95c915c7194c slide-03.

Root cause: a money RANGE whose low endpoint elides the magnitude unit
("$760 to $935 billion") tokenized the low endpoint as a *bare* dollar amount
(``money-bare:760``) while the rendered slide / perceived authority carried the
unit on both endpoints ("$760 billion to $935 billion" ->
``money-trillion:0.76``). The narration spoke a figure that IS on the slide,
but the tokenizer's magnitude class mismatched, so the figure-citation gate
false-fired.

The fix makes the LOW endpoint of a range inherit the magnitude unit of the
unit-bearing HIGH endpoint. It must NOT loosen the gate: the *number* still has
to be present in the perceived authority; only the magnitude unit is inherited
within the range span.
"""

from __future__ import annotations

import pytest

from app.specialists._shared.figure_tokens import _figures
from app.specialists.irene.graph import (
    Pass2GroundingError,
    _assert_figure_citations_within_perceived,
)

# Perceived authority for the real slide-03: prose reads
# "$760 billion to $935 billion" -> both endpoints carry the unit.
SLIDE03_PERCEIVED = sorted(_figures("$760 billion to $935 billion annually"))


def test_low_endpoint_inherits_unit_from_high_endpoint() -> None:
    """RED: '$760 to $935 billion' must tokenize both endpoints as billions."""
    assert _figures("$760 to $935 billion") == {
        "money-trillion:0.76",
        "money-trillion:0.935",
    }


@pytest.mark.parametrize(
    "phrasing",
    [
        "$760 to $935 billion",
        "between $760 and $935 billion",
        "$760 through $935 billion",
        "$760-$935 billion",
    ],
)
def test_unit_elided_range_grounds_to_perceived_slide(phrasing: str) -> None:
    """The canonical false-positive: narration range endpoint IS on the slide."""
    figures = _figures(phrasing)
    assert figures <= set(SLIDE03_PERCEIVED), (
        f"{phrasing!r} -> {sorted(figures)} not grounded to {SLIDE03_PERCEIVED}"
    )


def test_gate_passes_for_unit_elided_range_present_on_slide() -> None:
    """Gate must NOT fire when the spoken range endpoint is the slide figure."""
    roster = [{"slide_id": "slide-03", "perceived_figures": SLIDE03_PERCEIVED}]
    parsed = {
        "narration_script": [
            {
                "slide_id": "slide-03",
                "text": "The U.S. wastes $760 to $935 billion annually in healthcare.",
            }
        ]
    }
    # Must not raise.
    _assert_figure_citations_within_perceived(parsed, roster)


def test_gate_still_fires_for_number_absent_from_slide() -> None:
    """GUARD: inheritance changes the UNIT, never the NUMBER. A number that is
    nowhere on the slide must still be flagged — the gate is not loosened."""
    roster = [{"slide_id": "slide-03", "perceived_figures": SLIDE03_PERCEIVED}]
    parsed = {
        "narration_script": [
            {
                "slide_id": "slide-03",
                "text": "The U.S. wastes $5 to $935 billion annually.",
            }
        ]
    }
    with pytest.raises(Pass2GroundingError) as exc:
        _assert_figure_citations_within_perceived(parsed, roster)
    assert "money-trillion:0.005" in str(exc.value)


def test_standalone_bare_money_is_not_inherited() -> None:
    """A bare '$760' that is NOT a range endpoint stays bare (no unit invented)."""
    assert _figures("a flat fee of $760") == {"money-bare:760"}


def test_existing_normalization_unchanged() -> None:
    """Regression: non-range tokenization behavior is preserved."""
    assert _figures("$760 billion") == {"money-trillion:0.76"}
    assert _figures("$2 trillion") == {"money-trillion:2"}
    assert _figures("25%") == {"percent:25"}
    assert _figures("3x") == {"multiple:3"}
