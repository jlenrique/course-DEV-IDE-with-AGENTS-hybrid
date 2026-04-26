from __future__ import annotations

import pytest

from app.replay.discovery import list_closed_trials
from app.replay.regression import replay_trial

_TRIALS = list_closed_trials()


def test_closed_trial_discovery_is_not_empty() -> None:
    assert _TRIALS, "expected at least one migration-native closed trial baseline"


@pytest.mark.parametrize("trial_ref", _TRIALS, ids=lambda ref: ref.trial_id)
def test_every_closed_trial_replays_green(trial_ref) -> None:
    result = replay_trial(trial_ref, mode="fail-loud")
    assert result.pack_hash == result.expected_pack_hash
    assert result.elapsed_seconds <= 15 * 60
