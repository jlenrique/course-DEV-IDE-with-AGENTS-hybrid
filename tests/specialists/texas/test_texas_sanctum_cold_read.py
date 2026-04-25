from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists.texas.graph import (
    TEXAS_REFERENCES,
    TEXAS_SANCTUM_LOCK_BASELINE,
    SanctumLockViolation,
    _current_sanctum_manifest,
    _read_sanctum_digest,
    _read_texas_references,
    assert_sanctum_lock,
)


def test_texas_populated_sanctum_digest_is_deterministic() -> None:
    digest_a = _read_sanctum_digest()
    digest_b = _read_sanctum_digest()
    assert digest_a
    assert digest_a == digest_b


def test_texas_reference_shape_includes_10_rows() -> None:
    refs = _read_texas_references()
    for reference_name in TEXAS_REFERENCES:
        assert f"### Reference: {reference_name}" in refs


def test_texas_sanctum_manifest_matches_pinned_lock_baseline() -> None:
    assert _current_sanctum_manifest() == TEXAS_SANCTUM_LOCK_BASELINE


def test_texas_sanctum_lock_violation_raises_named_exception(tmp_path: Path) -> None:
    (tmp_path / "BOND.md").write_text("drift", encoding="utf-8")
    with pytest.raises(SanctumLockViolation):
        assert_sanctum_lock(
            expected_manifest=TEXAS_SANCTUM_LOCK_BASELINE,
            sanctum_dir=tmp_path,
        )
