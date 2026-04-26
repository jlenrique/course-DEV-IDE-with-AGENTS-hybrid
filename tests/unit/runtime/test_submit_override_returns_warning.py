from __future__ import annotations

import logging

from app.runtime.override_api import submit_override
from app.runtime.override_warning import ModelOverrideWarning
from tests.unit.runtime._helpers import TRIAL_ID, register_sample_run_state


def test_submit_override_returns_warning_and_logs_cache_warning(caplog) -> None:
    register_sample_run_state()
    with caplog.at_level(logging.WARNING):
        warning = submit_override(TRIAL_ID, "04", "gpt-5.5")
    assert isinstance(warning, ModelOverrideWarning)
    assert warning.confirm_token
    assert warning.confirm_token == warning.confirm_token.lower()
    assert len(warning.confirm_token) == 64
    assert "runtime model override submitted" in caplog.text


def test_submit_override_idempotent_under_resubmission() -> None:
    register_sample_run_state()
    first = submit_override(TRIAL_ID, "04", "gpt-5.5")
    second = submit_override(TRIAL_ID, "04", "gpt-5.5")
    assert second.confirm_token == first.confirm_token
    assert second.warning_id == first.warning_id
