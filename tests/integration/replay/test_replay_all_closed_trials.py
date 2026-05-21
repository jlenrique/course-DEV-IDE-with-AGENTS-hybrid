from __future__ import annotations

from copy import deepcopy

import pytest

import app.replay.regression as regression
from app.replay.discovery import list_closed_trials
from app.replay.regression import (
    ManifestSnapshotDriftError,
    NoClosedTrialsDiscoveredError,
    PackHashDriftError,
)


def _first_trial():
    trials = list_closed_trials()
    assert trials, "expected at least one replayable closed trial"
    return trials[0]


def test_replay_all_closed_trials_passes_for_current_baseline() -> None:
    batch = regression.replay_all_closed_trials(mode="fail-loud")
    assert batch.passed_count > 0
    assert batch.total_count == batch.passed_count


def test_replay_all_closed_trials_raises_when_discovery_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(regression, "list_closed_trials", lambda: [])
    with pytest.raises(NoClosedTrialsDiscoveredError):
        regression.replay_all_closed_trials(mode="fail-loud")


def test_replay_trial_raises_pack_hash_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    trial = _first_trial()
    original = regression._capture_trial_payload

    def _mutated_payload(ref):
        payload = deepcopy(original(ref))
        payload["downstream_payloads"]["15"]["specialist_id"] = "mutated"
        return payload

    monkeypatch.setattr(regression, "_capture_trial_payload", _mutated_payload)
    with pytest.raises(PackHashDriftError):
        regression.replay_trial(trial, mode="fail-loud")


def test_replay_trial_raises_manifest_snapshot_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    trial = _first_trial()
    monkeypatch.setattr(regression, "_compute_live_manifest_digest", lambda: "0" * 64)
    with pytest.raises(ManifestSnapshotDriftError):
        regression.replay_trial(trial, mode="fail-loud")
