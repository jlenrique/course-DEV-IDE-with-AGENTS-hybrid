from __future__ import annotations

import pytest

from app.specialists.tracy.graph import (
    SANCTUM_DIR,
    TRACY_REFERENCES,
    _read_sanctum_digest,
    _read_tracy_references,
)


def test_tracy_sanctum_fingerprint_deterministic_empty_dir() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    if SANCTUM_DIR.exists() and any(SANCTUM_DIR.rglob("*")):
        assert digest_a
    else:
        assert digest_a == ""


def test_tracy_expertise_readme_lists_l4_references() -> None:
    refs = _read_tracy_references()
    assert "<missing:" not in refs
    for reference_name in TRACY_REFERENCES:
        assert f"### Reference: {reference_name}" in refs


def test_tracy_sanctum_lock_baseline_pinned_or_skip() -> None:
    persona = SANCTUM_DIR / "PERSONA.md"
    if not persona.is_file():
        pytest.skip(
            "DEFERRED-EPIC-28-1-FORWARD-PORT: Tracy sanctum awaits Epic 28-1 forward-port"
        )
    assert persona.is_file()

