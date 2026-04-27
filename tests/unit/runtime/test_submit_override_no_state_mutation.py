from __future__ import annotations

from app.runtime.override_api import get_run_state, submit_override
from tests.unit.runtime._helpers import TRIAL_ID, register_sample_run_state


def test_submit_override_does_not_mutate_run_state(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    state = register_sample_run_state()
    before = state.model_dump(mode="json")
    submit_override(TRIAL_ID, "04", "gpt-5-mini")
    after = get_run_state(TRIAL_ID).model_dump(mode="json")
    assert after == before
