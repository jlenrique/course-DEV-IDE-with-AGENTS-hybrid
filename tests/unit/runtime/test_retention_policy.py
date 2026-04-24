"""`RetentionPolicy` shape + YAML round-trip tests (AC-1.5-B).

Pure-Python unit tests — no Postgres dependency. Exercises four-file-lockstep:
schema, validators, YAML round-trip, cron-hint regex.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.runtime.retention_policy import (
    DEFAULT_POLICY_PATH,
    RetentionPolicy,
    load_policy,
)


def test_shipped_default_policy_loads() -> None:
    p = load_policy()
    assert p.max_thread_age_days == 30
    assert p.cleanup_cron_hint == "0 3 * * *"
    assert p.retain_completed is False
    assert p.retain_failed is True


def test_round_trip_yaml(tmp_path: Path) -> None:
    src = DEFAULT_POLICY_PATH.read_text(encoding="utf-8")
    target = tmp_path / "retention.yaml"
    target.write_text(src, encoding="utf-8")
    p = load_policy(target)
    assert p.max_thread_age_days == 30


def test_policy_rejects_bad_cron_hint() -> None:
    with pytest.raises(ValidationError, match="cleanup_cron_hint must be a 5-field"):
        RetentionPolicy(
            max_thread_age_days=30,
            cleanup_cron_hint="bad",
            retain_completed=False,
            retain_failed=True,
        )


def test_policy_rejects_zero_age() -> None:
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        RetentionPolicy(
            max_thread_age_days=0,
            cleanup_cron_hint="0 3 * * *",
            retain_completed=False,
            retain_failed=True,
        )


def test_policy_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        RetentionPolicy(
            max_thread_age_days=30,
            cleanup_cron_hint="0 3 * * *",
            retain_completed=False,
            retain_failed=True,
            ghost="x",  # type: ignore[call-arg]
        )


def test_policy_validate_assignment_rejects_bad_cron_mutation() -> None:
    p = RetentionPolicy(
        max_thread_age_days=30,
        cleanup_cron_hint="0 3 * * *",
        retain_completed=False,
        retain_failed=True,
    )
    with pytest.raises(ValidationError):
        p.cleanup_cron_hint = "not a cron"


def test_load_policy_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="retention policy file not found"):
        load_policy(tmp_path / "ghost.yaml")


def test_load_policy_non_mapping_root(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load_policy(bad)
