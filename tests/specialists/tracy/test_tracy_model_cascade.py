from __future__ import annotations

from app.models.adapter import make_chat_model


def test_tracy_default_resolution_resolves_to_gpt_5_4() -> None:
    handle = make_chat_model(specialist_id="tracy", tier_request="reasoning")
    assert handle.entry.resolved == "gpt-5.4"
    assert handle.entry.level == "per_specialist"


def test_tracy_per_call_override_wins() -> None:
    handle = make_chat_model(
        specialist_id="tracy",
        tier_request="reasoning",
        per_call_override="gpt-5-nano",
    )
    assert handle.entry.resolved == "gpt-5-nano"
    assert handle.entry.level == "per_call"
