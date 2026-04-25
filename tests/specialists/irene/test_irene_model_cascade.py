"""AC-C — Model cascade resolves correctly at Irene's `_plan` node (Story 2a.2).

Two tests:
1. Default resolution (no override): tier_request="reasoning" + Irene's
   `model_config.yaml::default_model = "gpt-5.4"` → resolves to gpt-5.4 at
   resolution_level="per_specialist".
2. Per-call override: `make_chat_model(per_call_override="gpt-5-haiku")`
   → resolves to gpt-5-haiku at resolution_level="per_call".
"""

from __future__ import annotations

from app.models.adapter import make_chat_model


def test_irene_default_resolution_resolves_to_gpt_5_4() -> None:
    handle = make_chat_model(specialist_id="irene", tier_request="reasoning")
    assert handle.entry.resolved == "gpt-5.4"
    assert handle.entry.level == "per_specialist"
    assert handle.entry.cache_prefix_hash is not None
    assert len(handle.entry.cache_prefix_hash) == 64


def test_irene_per_call_override_resolves_to_haiku() -> None:
    handle = make_chat_model(
        specialist_id="irene",
        per_call_override="gpt-5-haiku",
        tier_request="reasoning",
    )
    assert handle.entry.resolved == "gpt-5-haiku"
    assert handle.entry.level == "per_call"
    assert handle.entry.cache_prefix_hash is not None
