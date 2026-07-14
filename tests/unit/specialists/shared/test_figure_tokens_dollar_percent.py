"""Regression coverage for OCR dollar-prefixed percentage surfaces.

Frozen live trial 399bcd61-7779-4fa0-a592-186c3d4b4045 perceived the
slide text ``$ 5% GDP``.  The shared tokenizer formerly consumed ``$ 5`` as
bare money, so valid narration of ``5%`` false-halted at Irene Pass 2.
"""

from __future__ import annotations

import pytest

from app.specialists._shared.figure_tokens import _figures, _normalize_figure
from app.specialists.irene.graph import (
    Pass2GroundingError,
    _assert_figure_citations_within_perceived,
)
from app.specialists.quinn_r.fidelity_detector import detect_fidelity
from app.specialists.quinn_r.quality_control_dispatch import FidelityError


@pytest.mark.parametrize(
    ("surface", "expected"),
    [
        ("5%", "percent:5"),
        ("5 %", "percent:5"),
        ("$5%", "percent:5"),
        ("$ 5 %", "percent:5"),
        ("$ 5.0 %", "percent:5"),
        ("18+%", "percent:18"),
        ("18 + %", "percent:18"),
        ("$18+%", "percent:18"),
        ("$ 18+%", "percent:18"),
        ("$1,200.5%", "percent:1200.5"),
        ("18\t+\t%", "percent:18"),
        ("$\n18\n+\n%", "percent:18"),
        ("$\t5\t%", "percent:5"),
    ],
)
def test_percent_suffix_wins_over_ocr_currency_prefix(surface: str, expected: str) -> None:
    assert _figures(surface) == {expected}
    assert _normalize_figure(surface) == expected


def test_frozen_live_surface_yields_percent_tokens_only() -> None:
    text = "Rising healthcare spending $ 18+% GDP cost curve $ 5% GDP (1960)"
    assert _figures(text) == {"percent:18", "percent:5"}


@pytest.mark.parametrize(
    ("surface", "expected"),
    [
        ("$5", {"money-bare:5"}),
        ("$5.00", {"money-bare:5"}),
        ("$1,200", {"money-bare:1200"}),
        ("$5B", {"money-trillion:0.005"}),
        ("$5 billion", {"money-trillion:0.005"}),
        ("$4.5T", {"money-trillion:4.5"}),
        (
            "$760 to $935 billion; 5% GDP",
            {"money-trillion:0.76", "money-trillion:0.935", "percent:5"},
        ),
        ("5x growth alongside $5% GDP", {"multiple:5", "percent:5"}),
        ("5% of $5", {"percent:5", "money-bare:5"}),
    ],
)
def test_money_ranges_multiples_and_mixed_text_remain_typed(
    surface: str, expected: set[str]
) -> None:
    assert _figures(surface) == expected


def _irene_check(perceived: str, narration: str) -> None:
    roster = [{"slide_id": "slide-01", "perceived_figures": sorted(_figures(perceived))}]
    parsed = {"narration_script": [{"slide_id": "slide-01", "narration_text": narration}]}
    _assert_figure_citations_within_perceived(parsed, roster)


def _artifact(perceived: str) -> list[dict[str, object]]:
    return [
        {
            "slide_id": "slide-01",
            "confidence": "HIGH",
            "coverage": "perceived",
            "extracted_text": perceived,
        }
    ]


def test_dollar_prefixed_percent_grounds_at_both_fidelity_gates() -> None:
    _irene_check("$ 5% GDP", "The 1960 baseline was 5% of GDP.")
    assert detect_fidelity(
        [{"slide_id": "slide-01", "narration_text": "The baseline was 5%."}],
        _artifact("$ 5% GDP"),
    ) == {"blocking": [], "evaluated_segments": 1}


@pytest.mark.parametrize(
    ("perceived", "narration", "missing"),
    [
        ("$5", "The rate was 5%.", "percent:5"),
        ("$5%", "The fee was $5.", "money-bare:5"),
        ("$5 billion", "The fee was $5.", "money-bare:5"),
        ("5%", "The rate was 6%.", "percent:6"),
    ],
)
def test_money_percent_and_magnitude_mismatches_still_fail_both_gates(
    perceived: str, narration: str, missing: str
) -> None:
    with pytest.raises(Pass2GroundingError, match=missing):
        _irene_check(perceived, narration)
    with pytest.raises(FidelityError, match=missing):
        detect_fidelity(
            [{"slide_id": "slide-01", "narration_text": narration}],
            _artifact(perceived),
        )
