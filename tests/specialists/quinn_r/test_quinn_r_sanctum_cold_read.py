from __future__ import annotations

import hashlib

import pytest

from app.specialists.quinn_r.graph import (
    QUINN_R_REFERENCES,
    SANCTUM_DIR,
    _read_quinn_r_references,
    _read_sanctum_digest,
)

QUINN_R_SANCTUM_LOCK_BASELINE_SHA256 = (
    "a8938376d98d26f2c5c3677d153e567ecdd4737ac1cb2c656849003dab462ffc"
)


def test_quinn_r_sanctum_fingerprint_deterministic_empty_dir() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    if SANCTUM_DIR.exists() and any(SANCTUM_DIR.rglob("*")):
        assert digest_a
    else:
        assert digest_a == ""


def test_quinn_r_expertise_readme_lists_references() -> None:
    refs = _read_quinn_r_references()
    assert "<missing:" not in refs
    for reference_name in QUINN_R_REFERENCES:
        assert f"### Reference: {reference_name}" in refs


def test_quinn_r_sanctum_lock_baseline_pinned_or_skip() -> None:
    persona = SANCTUM_DIR / "PERSONA.md"
    if not persona.is_file():
        pytest.skip(
            "Quinn-R sanctum not yet first-breath-populated; rerun after operator "
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
    assert digest.hexdigest() == QUINN_R_SANCTUM_LOCK_BASELINE_SHA256
