from __future__ import annotations

import hashlib

import pytest

from app.specialists.gary.graph import (
    GARY_REFERENCES,
    SANCTUM_DIR,
    _read_gary_references,
    _read_sanctum_digest,
)

GARY_SANCTUM_LOCK_BASELINE_SHA256 = (
    "84e608a6405f798eb850af6ccaf13ceff1bb2f7108cd571797d25ecf94ca5cc4"
)


def test_gary_sanctum_fingerprint_deterministic_empty_dir() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    if SANCTUM_DIR.exists() and any(SANCTUM_DIR.rglob("*")):
        assert digest_a
    else:
        assert digest_a == ""


def test_gary_expertise_readme_lists_l4_references() -> None:
    refs = _read_gary_references()
    for reference_name in GARY_REFERENCES:
        assert f"### Reference: {reference_name}" in refs
    assert "theme-template-preview.md" in refs


def test_gary_sanctum_lock_baseline_pinned_or_skip() -> None:
    persona = SANCTUM_DIR / "PERSONA.md"
    if not persona.is_file():
        pytest.skip(
            "Gary sanctum not yet first-breath-populated; rerun after operator "
            "lands PERSONA.md and full BMB persona files"
        )
    files = sorted(
        (p for p in SANCTUM_DIR.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(SANCTUM_DIR).as_posix(),
    )
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(SANCTUM_DIR).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
        digest.update(b"\0")
    baseline_sha = digest.hexdigest()
    assert baseline_sha == GARY_SANCTUM_LOCK_BASELINE_SHA256
