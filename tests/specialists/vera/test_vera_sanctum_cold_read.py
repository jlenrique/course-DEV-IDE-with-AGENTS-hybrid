from __future__ import annotations

import hashlib

import pytest

from app.specialists.vera.graph import (
    SANCTUM_DIR,
    VERA_REFERENCES,
    _read_sanctum_digest,
    _read_vera_references,
)

VERA_SANCTUM_LOCK_BASELINE_SHA256 = (
    "7e5928c4f6f654b5d7f1882946e8f2eb0b6e79696f4e175f95f0e1d87f530ed2"
)


def test_vera_sanctum_fingerprint_deterministic_empty_dir() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    if SANCTUM_DIR.exists() and any(SANCTUM_DIR.rglob("*")):
        assert digest_a
    else:
        assert digest_a == ""


def test_vera_expertise_readme_lists_references() -> None:
    refs = _read_vera_references()
    assert "<missing:" not in refs
    for reference_name in VERA_REFERENCES:
        assert f"### Reference: {reference_name}" in refs


def test_vera_sanctum_lock_baseline_pinned_or_skip() -> None:
    persona = SANCTUM_DIR / "PERSONA.md"
    if not persona.is_file():
        pytest.skip(
            "Vera sanctum not yet first-breath-populated; rerun after operator "
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
    assert digest.hexdigest() == VERA_SANCTUM_LOCK_BASELINE_SHA256
