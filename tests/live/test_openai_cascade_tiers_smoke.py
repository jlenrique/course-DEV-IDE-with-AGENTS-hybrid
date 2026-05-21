"""Live-OpenAI cascade-tier smoke — one cheap ping per cascade tier to confirm
each model ID is real and the operator's API key reaches the provider.

Gated by `pytest -m live` AND requires `OPENAI_API_KEY` set in env. Each call
uses `max_tokens=1` to keep cost minimal (~$0.0001 per tier; ~$0.0003 total
per full run). Asserts response shape + non-zero token usage; does NOT assert
content (purpose is "the model ID resolves at OpenAI", not behavior validation).

Per the 2026-04-26 post-vote substrate-aware remediation: this gate must pass
before the operator runs the first real trial. The 6-agent M5 SHIP-CONDITIONAL
verdict was made without anyone calling OpenAI — fictitious model IDs survived
all internal-shape audits because the tokens parsed and lint-checked clean.
This test is the cheapest possible referent-validity gate.

Run via:

    pytest tests/live/test_openai_cascade_tiers_smoke.py -m live -q

Skips cleanly when OPENAI_API_KEY is absent.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


@pytest.mark.parametrize(
    "model_id",
    ["gpt-5", "gpt-5-mini", "gpt-5-nano"],
    ids=["frontier", "mid-tier", "narrow-task"],
)
def test_openai_cascade_tier_responds(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
    model_id: str,
) -> None:
    """One cheap ping per cascade tier; confirms model_id is real + key works."""

    api_key = env_value("OPENAI_API_KEY")
    pytest.importorskip("openai")
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    def _call() -> object:
        # max_completion_tokens=200 (not 1): GPT-5 family models have built-in
        # extended reasoning that consumes part of the token budget before
        # producing visible output. max_completion_tokens=1 produces a 400
        # "could not finish because output limit was reached" because reasoning
        # alone consumes >1 token. 200 is safe headroom (~$0.001-0.002 per call,
        # still trivial for a smoke test). This is anti-pattern A16
        # (Composition-vs-Component Audit Gap) — the smoke test was authored
        # without ever running against real GPT-5, so referent-validity wasn't
        # exercised end-to-end. Discovered 2026-04-27 in operator session.
        return client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "ping"}],
            max_completion_tokens=200,
        )

    response, _elapsed = timed_call(_call)
    assert response.choices, f"{model_id}: no choices in response"
    assert response.choices[0].message.role == "assistant"
    assert response.usage is not None
    assert response.usage.total_tokens > 0
