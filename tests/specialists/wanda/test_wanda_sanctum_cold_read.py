from __future__ import annotations

from app.specialists.wanda.graph import (
    SANCTUM_DIR,
    WANDA_REFERENCES,
    _read_sanctum_digest,
    _read_wanda_references,
)


def test_wanda_sanctum_fingerprint_deterministic_graceful() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b
    if not SANCTUM_DIR.exists():
        assert digest_a == ""


def test_wanda_expertise_readme_lists_references() -> None:
    refs = _read_wanda_references()
    assert "<missing:" not in refs
    for reference_name in WANDA_REFERENCES:
        assert f"### Reference: {reference_name}" in refs
