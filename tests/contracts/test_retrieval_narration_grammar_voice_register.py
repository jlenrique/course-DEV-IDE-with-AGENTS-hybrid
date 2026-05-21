"""Voice-register contract tests for Story 30-5 retrieval narration grammar."""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.retrieval_narration_grammar import render_retrieval_narration


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "success", "posture": "embellish", "output": {"content_added": True}},
        {
            "status": "success",
            "posture": "corroborate",
            "output": {"classification": "supporting"},
        },
        {"status": "success", "posture": "gap-fill", "output": {"gap_filled": True}},
    ],
)
def test_retrieval_narration_sentences_follow_voice_register(
    payload: dict[str, object],
) -> None:
    sentence = render_retrieval_narration(payload)

    assert sentence.startswith("I ")
    assert sentence.endswith("?")
    assert "intake" not in sentence.lower()
    assert "orchestrator" not in sentence.lower()
