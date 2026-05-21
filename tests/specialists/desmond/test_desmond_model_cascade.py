from __future__ import annotations

from app.models.adapter import make_chat_model


def test_desmond_default_resolution_resolves_to_gpt_5_haiku() -> None:
    handle = make_chat_model(specialist_id="desmond", tier_request="fast")
    assert handle.entry.resolved == "gpt-5-nano"
    assert handle.entry.level == "per_specialist"
    assert handle.entry.cache_prefix_hash is not None


def test_desmond_per_call_override_wins() -> None:
    handle = make_chat_model(
        specialist_id="desmond",
        tier_request="fast",
        per_call_override="gpt-5",
    )
    assert handle.entry.resolved == "gpt-5"
    assert handle.entry.level == "per_call"
