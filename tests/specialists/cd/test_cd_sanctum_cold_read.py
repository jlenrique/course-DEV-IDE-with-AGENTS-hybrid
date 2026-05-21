from __future__ import annotations

import shutil

import pytest

from app.specialists.cd.graph import (
    CD_REFERENCES,
    CD_SANCTUM_LOCK_BASELINE,
    SANCTUM_DIR,
    _current_sanctum_manifest,
    _read_cd_references,
    _read_sanctum_digest,
    assert_sanctum_lock,
)
from app.specialists.texas.graph import SanctumLockViolation


def test_cd_sanctum_fingerprint_deterministic_populated() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    assert digest_a


def test_cd_expertise_readme_lists_references() -> None:
    refs = _read_cd_references()
    assert "<missing:" not in refs
    for reference_name in CD_REFERENCES:
        assert f"### Reference: {reference_name}" in refs


def test_cd_sanctum_lock_baseline_pinned() -> None:
    assert_sanctum_lock()
    assert _current_sanctum_manifest() == CD_SANCTUM_LOCK_BASELINE


def test_cd_sanctum_lock_violation_raises_named_exception(tmp_path) -> None:
    mutated = tmp_path / "cd_sanctum_mutated"
    shutil.copytree(SANCTUM_DIR, mutated)
    target = mutated / "BOND.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nmutation", encoding="utf-8")
    with pytest.raises(SanctumLockViolation):
        assert_sanctum_lock(sanctum_dir=mutated)
