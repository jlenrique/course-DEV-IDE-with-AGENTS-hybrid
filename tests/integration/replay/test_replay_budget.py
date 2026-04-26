from __future__ import annotations

import pytest

import app.replay.regression as regression
from app.replay.discovery import list_closed_trials
from app.replay.regression import ReplayBudgetExceeded


def _first_trial():
    trials = list_closed_trials()
    assert trials, "expected at least one replayable closed trial"
    return trials[0]


def test_replay_trial_stays_under_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    trial = _first_trial()
    clock = iter((10.0, 10.25))
    monkeypatch.setattr(regression.time, "perf_counter", lambda: next(clock))
    result = regression.replay_trial(trial, mode="fail-loud", budget_seconds=1.0)
    assert result.elapsed_seconds == pytest.approx(0.25)


def test_replay_trial_raises_when_budget_is_exceeded(monkeypatch: pytest.MonkeyPatch) -> None:
    trial = _first_trial()
    clock = iter((10.0, 25.5))
    monkeypatch.setattr(regression.time, "perf_counter", lambda: next(clock))
    with pytest.raises(ReplayBudgetExceeded):
        regression.replay_trial(trial, mode="fail-loud", budget_seconds=1.0)
