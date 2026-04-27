from __future__ import annotations

import os

import pytest

from marcus.facade import get_facade


def _skip_without_openai() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY absent; ad-hoc facade live invocation skipped")


@pytest.mark.llm_live
def test_adhoc_facade_happy_path() -> None:
    _skip_without_openai()
    response = get_facade().ask(
        "Reply with the words: ad hoc ready.",
        max_tokens=20,
        trace=False,
    )
    assert response.text
    assert response.model_used == "gpt-5"
    assert response.cost_usd >= 0.0
    assert response.tokens.total_tokens >= (
        response.tokens.input_tokens + response.tokens.output_tokens
    )


@pytest.mark.llm_live
def test_adhoc_facade_cascade_override_path() -> None:
    _skip_without_openai()
    response = get_facade().ask(
        "Reply with the words: override ready.",
        cascade_override="gpt-5-nano",
        max_tokens=20,
        trace=False,
    )
    assert response.text
    assert response.model_used == "gpt-5-nano"
    assert response.cost_usd >= 0.0
