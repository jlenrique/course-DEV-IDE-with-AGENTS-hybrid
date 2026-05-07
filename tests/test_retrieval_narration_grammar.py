"""Focused tests for Story 30-5 retrieval narration grammar."""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.retrieval_narration_grammar import (
    RetrievalNarrationError,
    render_retrieval_narration,
)


def test_render_retrieval_narration_embellish_sentence() -> None:
    sentence = render_retrieval_narration(
        {
            "status": "success",
            "posture": "embellish",
            "output": {"content_added": True},
        }
    )

    assert (
        sentence
        == "I found a detail that enriches this section, and I can weave it in if you want?"
    )


@pytest.mark.parametrize(
    ("classification", "expected_phrase"),
    [
        ("supporting", "evidence that supports it"),
        ("contrasting", "evidence that challenges it"),
        ("mentioning", "a source that mentions it without fully settling it"),
    ],
)
def test_render_retrieval_narration_corroborate_classification_matrix(
    classification: str,
    expected_phrase: str,
) -> None:
    sentence = render_retrieval_narration(
        {
            "status": "success",
            "posture": "corroborate",
            "output": {"classification": classification},
        }
    )

    assert sentence == (
        f"I found {expected_phrase} for this claim, and I can anchor that nuance here if you want?"
    )


@pytest.mark.parametrize("posture", ["gap-fill", "gap_fill"])
def test_render_retrieval_narration_gap_fill_normalizes_spellings(posture: str) -> None:
    sentence = render_retrieval_narration(
        {
            "status": "success",
            "posture": posture,
            "output": {"gap_filled": True},
        }
    )

    assert (
        sentence
        == "I found source material that fills the missing background here, "
        "and I can fold it in if you want?"
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "failed", "posture": "embellish", "reason": "timeout"},
        {"status": "success", "posture": "invent", "output": {}},
        {"status": "success", "posture": "corroborate", "output": {}},
    ],
)
def test_render_retrieval_narration_rejects_invalid_inputs(payload: dict[str, object]) -> None:
    with pytest.raises(RetrievalNarrationError):
        render_retrieval_narration(payload)
