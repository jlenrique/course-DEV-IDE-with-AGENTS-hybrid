from __future__ import annotations

from app.models.adapter import make_chat_model


def test_aria_default_resolution_resolves_to_gpt_5_4() -> None:
    handle = make_chat_model(specialist_id="aria", tier_request="fast")
    assert handle.entry.resolved == "gpt-5.4"
    assert handle.entry.level == "per_specialist"


def test_aria_per_call_override_wins() -> None:
    handle = make_chat_model(
        specialist_id="aria",
        tier_request="fast",
        per_call_override="gpt-5-haiku",
    )
    assert handle.entry.resolved == "gpt-5-haiku"
    assert handle.entry.level == "per_call"
