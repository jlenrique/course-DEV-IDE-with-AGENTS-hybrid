from __future__ import annotations

import shutil

import pytest

from app.specialists.desmond.graph import (
    DESMOND_REFERENCES,
    DESMOND_SANCTUM_LOCK_BASELINE,
    SANCTUM_DIR,
    _current_sanctum_manifest,
    _read_desmond_references,
    _read_sanctum_digest,
    assert_sanctum_lock,
)
from app.specialists.texas.graph import SanctumLockViolation


def test_desmond_sanctum_fingerprint_deterministic_populated() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    assert digest_a


def test_desmond_expertise_readme_lists_l4_references() -> None:
    refs = _read_desmond_references()
    assert "<missing:" not in refs
    for reference_name in DESMOND_REFERENCES:
        assert f"### Reference: {reference_name}" in refs


def test_desmond_sanctum_lock_baseline_pinned() -> None:
    assert_sanctum_lock()
    assert _current_sanctum_manifest() == DESMOND_SANCTUM_LOCK_BASELINE


def test_desmond_sanctum_lock_violation_raises_named_exception(tmp_path) -> None:
    mutated = tmp_path / "desmond_sanctum_mutated"
    shutil.copytree(SANCTUM_DIR, mutated)
    target = mutated / "BOND.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nmutation", encoding="utf-8")
    with pytest.raises(SanctumLockViolation):
        assert_sanctum_lock(sanctum_dir=mutated)


def test_desmond_sanctum_digest_excludes_sessions_logs(tmp_path) -> None:
    """sessions/ are append-only operational logs, not persona baseline — adding a
    new session file must NOT drift the digest/lock (else every Desmond session would
    force a set-aside/restore dance before Descript delivery). 2026-06-24 fix.
    """
    base = tmp_path / "desmond_sanctum_sessions"
    shutil.copytree(SANCTUM_DIR, base)
    digest_before = _read_sanctum_digest(base)
    sessions = base / "sessions"
    sessions.mkdir(exist_ok=True)
    (sessions / "2099-12-31.md").write_text("a brand new session log\n", encoding="utf-8")
    # A new session log does NOT change the digest...
    assert _read_sanctum_digest(base) == digest_before
    # ...and the lock still passes against the real baseline with the log present.
    assert_sanctum_lock(sanctum_dir=base)
