from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.runtime.override_api import OverrideTokenStaleError, apply_override, submit_override
from tests.unit.runtime._helpers import TRIAL_ID, register_sample_run_state


def test_apply_override_token_mismatch_rejected() -> None:
    register_sample_run_state()
    submit_override(TRIAL_ID, "04", "gpt-5.5")
    with pytest.raises(OverrideTokenStaleError):
        apply_override(
            {
                "trial_id": str(TRIAL_ID),
                "node_id": "04",
                "new_model": "gpt-5.5",
                "operator_id": "operator_cli",
            },
            "0" * 64,
        )


def test_apply_override_token_replay_rejected() -> None:
    register_sample_run_state()
    warning = submit_override(TRIAL_ID, "04", "gpt-5.5")
    verdict = {
        "trial_id": str(TRIAL_ID),
        "node_id": "04",
        "new_model": "gpt-5.5",
        "operator_id": "operator_cli",
    }
    apply_override(verdict, warning.confirm_token)
    with pytest.raises(OverrideTokenStaleError):
        apply_override(verdict, warning.confirm_token)


def test_apply_override_expired_token_rejected() -> None:
    register_sample_run_state()
    warning = submit_override(TRIAL_ID, "04", "gpt-5.5")
    with pytest.raises(OverrideTokenStaleError):
        apply_override(
            {
                "trial_id": str(TRIAL_ID),
                "node_id": "04",
                "new_model": "gpt-5.5",
                "operator_id": "operator_cli",
            },
            warning.confirm_token,
            now=datetime.now(UTC) + timedelta(minutes=6),
        )
