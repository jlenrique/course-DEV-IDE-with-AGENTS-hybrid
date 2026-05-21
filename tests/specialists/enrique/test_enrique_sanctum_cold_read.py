from __future__ import annotations

from app.specialists.enrique.graph import (
    ENRIQUE_REFERENCES,
    SANCTUM_DIR,
    _read_enrique_references,
    _read_sanctum_digest,
)


def test_enrique_sanctum_fingerprint_deterministic() -> None:
    digest_a = _read_sanctum_digest(SANCTUM_DIR)
    digest_b = _read_sanctum_digest(SANCTUM_DIR)
    assert digest_a == digest_b


def test_enrique_expertise_readme_lists_references() -> None:
    refs = _read_enrique_references()
    assert "<missing:" not in refs
    for reference_name in ENRIQUE_REFERENCES:
        assert f"### Reference: {reference_name}" in refs
