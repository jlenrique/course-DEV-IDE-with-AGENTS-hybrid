from __future__ import annotations

from copy import deepcopy

import pytest

import app.replay.regression as regression
from app.replay.discovery import list_closed_trials
from app.replay.regression import SanctumFingerprintDriftError


def _first_trial():
    trials = list_closed_trials()
    assert trials, "expected at least one replayable closed trial"
    return trials[0]


def _mutate_sanctum(original_capture, ref):
    payload = deepcopy(original_capture(ref))
    payload["run_state"]["sanctum_fingerprint"]["content_sha256"] = "f" * 64
    payload["run_state"]["marcus_fingerprint"][0] = "f" * 64
    return payload


def test_fail_loud_raises_on_sanctum_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    trial = _first_trial()
    original_capture = regression._capture_trial_payload
    monkeypatch.setattr(
        regression,
        "_capture_trial_payload",
        lambda ref: _mutate_sanctum(original_capture, ref),
    )
    with pytest.raises(SanctumFingerprintDriftError):
        regression.replay_trial(trial, mode="fail-loud")


def test_warn_on_clone_normalizes_sanctum_and_logs_provenance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial = _first_trial()
    original_capture = regression._capture_trial_payload
    monkeypatch.setattr(
        regression,
        "_capture_trial_payload",
        lambda ref: _mutate_sanctum(original_capture, ref),
    )
    result = regression.replay_trial(trial, mode="warn-on-clone")
    assert result.normalized_for_clone is True
    assert result.pack_hash == result.expected_pack_hash
    assert result.provenance_log
