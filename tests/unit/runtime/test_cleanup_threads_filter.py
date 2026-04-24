"""`_threads_to_delete` filter logic — unit test, no Postgres (AC-1.5-C filter rules).

Isolates the retain_completed / retain_failed decision logic from the SQL
round-trip so we can assert filter behavior without DATABASE_URL.
"""

from __future__ import annotations

from app.runtime.cleanup_threads import _threads_to_delete
from app.runtime.retention_policy import RetentionPolicy


def _policy(*, retain_completed: bool, retain_failed: bool) -> RetentionPolicy:
    return RetentionPolicy(
        max_thread_age_days=30,
        cleanup_cron_hint="0 3 * * *",
        retain_completed=retain_completed,
        retain_failed=retain_failed,
    )


def test_default_policy_retains_failed_deletes_completed() -> None:
    candidates = [
        ("t1", "completed"),
        ("t2", "failed"),
        ("t3", "running"),
    ]
    policy = _policy(retain_completed=False, retain_failed=True)
    assert _threads_to_delete(candidates, policy) == ["t1", "t3"]


def test_retain_both_deletes_nothing() -> None:
    candidates = [("t1", "completed"), ("t2", "failed")]
    policy = _policy(retain_completed=True, retain_failed=True)
    assert _threads_to_delete(candidates, policy) == []


def test_retain_neither_deletes_all() -> None:
    candidates = [("t1", "completed"), ("t2", "failed"), ("t3", "running")]
    policy = _policy(retain_completed=False, retain_failed=False)
    assert _threads_to_delete(candidates, policy) == ["t1", "t2", "t3"]


def test_unknown_status_always_eligible_for_deletion() -> None:
    """`unknown` status isn't in the retain set; old enough = delete."""
    candidates = [("t1", "unknown"), ("t2", "unusual")]
    policy = _policy(retain_completed=False, retain_failed=True)
    assert _threads_to_delete(candidates, policy) == ["t1", "t2"]


def test_empty_candidates_returns_empty() -> None:
    policy = _policy(retain_completed=False, retain_failed=True)
    assert _threads_to_delete([], policy) == []
