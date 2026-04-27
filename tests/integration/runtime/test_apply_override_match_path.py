from __future__ import annotations

from app.runtime.override_api import (
    apply_override,
    get_override_ledger,
    get_run_state,
    submit_override,
)
from tests.unit.runtime._helpers import TRIAL_ID, register_sample_run_state


def test_apply_override_match_path_updates_state_and_ledger(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    register_sample_run_state()
    warning = submit_override(TRIAL_ID, "04", "gpt-5-mini")
    event = apply_override(
        {
            "trial_id": str(TRIAL_ID),
            "node_id": "04",
            "new_model": "gpt-5-mini",
            "operator_id": "operator_cli",
        },
        warning.confirm_token,
    )
    state = get_run_state(TRIAL_ID)
    ledger = get_override_ledger(TRIAL_ID)

    assert state.model_overrides == {"04": "gpt-5-mini"}
    assert ledger[-1]["kind"] == "override"
    assert ledger[-1]["new_model"] == "gpt-5-mini"
    assert event.node_id == "04"
