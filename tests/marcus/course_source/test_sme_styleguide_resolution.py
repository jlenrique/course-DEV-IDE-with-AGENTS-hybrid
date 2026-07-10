"""Mine 3 — per-SME styleguide / attribution / approval / voice resolution."""

from __future__ import annotations

import pytest

from app.marcus.course_source.sme_registry import (
    SmeRegistryError,
    clear_sme_registry_cache,
    profiles_diverge,
    resolve_sme_profile,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_sme_registry_cache()
    yield
    clear_sme_registry_cache()


def test_tejal_binds_named_gamma_variant() -> None:
    profile = resolve_sme_profile("tejal")
    assert profile.sme_key == "tejal"
    assert profile.styleguide_id == "hil-2026-apc-crossroads-classic"
    assert profile.fallback is False
    assert profile.unbound is False
    assert "Tejal" in profile.attribution
    assert profile.approval_route
    assert profile.voice_profile_ref.startswith("voice/")


def test_hai_and_phs_are_marked_gaps_not_tejal() -> None:
    hai = resolve_sme_profile("hai-510")
    phs = resolve_sme_profile("phs-620")
    tejal = resolve_sme_profile("tejal")
    assert hai.fallback is True and hai.styleguide_id is None
    assert phs.fallback is True and phs.styleguide_id is None
    assert hai.styleguide_id != tejal.styleguide_id
    assert phs.styleguide_id != tejal.styleguide_id
    assert "Tejal" not in (hai.attribution if hai.styleguide_id else "ok")


def test_two_smes_diverge_on_attribution_or_styleguide() -> None:
    tejal = resolve_sme_profile("Tejal")  # alias
    hai = resolve_sme_profile("Aziz Nazha")
    diverged = profiles_diverge(tejal, hai)
    assert diverged
    assert "attribution" in diverged or "styleguide_id" in diverged
    assert tejal.attribution != hai.attribution


def test_unknown_sme_hard_fails_never_silent_tejal() -> None:
    with pytest.raises(SmeRegistryError, match="unknown SME"):
        resolve_sme_profile("unknown-sme-xyz")
