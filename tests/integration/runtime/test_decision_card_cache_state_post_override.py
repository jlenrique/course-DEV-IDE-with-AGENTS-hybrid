from __future__ import annotations

from app.runtime.override_api import apply_override, decision_card_meta_for_trial, submit_override
from tests.unit.runtime._helpers import TRIAL_ID, register_sample_run_state


def test_decision_card_cache_state_healthy_without_override() -> None:
    register_sample_run_state()
    meta = decision_card_meta_for_trial(TRIAL_ID)
    assert meta.cache_state == "healthy"


def test_decision_card_cache_state_mixed_after_override(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    register_sample_run_state()
    warning = submit_override(TRIAL_ID, "04", "gpt-5-mini")
    apply_override(
        {
            "trial_id": str(TRIAL_ID),
            "node_id": "04",
            "new_model": "gpt-5-mini",
            "operator_id": "operator_cli",
        },
        warning.confirm_token,
    )
    meta = decision_card_meta_for_trial(TRIAL_ID)
    assert meta.cache_state == "mixed"
    assert meta.affected_nodes == ["04"]


def test_decision_card_cache_state_cold_without_cache_prefix() -> None:
    register_sample_run_state(cache_state=None)
    meta = decision_card_meta_for_trial(TRIAL_ID)
    assert meta.cache_state == "cold"
