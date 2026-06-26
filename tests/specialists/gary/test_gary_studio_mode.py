"""Studio-B (production_mode=studio) — guard + normalizer tests.

The guard is tested RED-FIRST against the REAL captured Classic fallback artifact
(the genuine adversary, not a fabricated fixture) and GREEN against the two real
Studio successes. See _bmad-output/implementation-artifacts/studio-mode-evidence/.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists.gary._act import (
    GaryActError,
    _assert_studio_image_card,
    _normalized_gamma_settings,
)
from app.specialists.gary.gamma_dispatch import GammaDispatchError

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "_bmad-output" / "implementation-artifacts" / "studio-mode-evidence"
CLASSIC = EVIDENCE / "CLASSIC-fallback-failure.png"
STUDIO_1 = EVIDENCE / "STUDIO-success-1-innovators-mindset.png"
STUDIO_2 = EVIDENCE / "STUDIO-success-2-escalating-stakes.png"


# --- Guard: fail loud on the real Classic adversary, pass on real Studio --------

def test_guard_raises_on_real_classic_fallback() -> None:
    assert CLASSIC.exists(), "real Classic adversary fixture missing"
    with pytest.raises(GammaDispatchError) as exc:
        _assert_studio_image_card(CLASSIC, slide_id="slide-01", generation_id="gen-classic")
    assert exc.value.tag == "gamma.studio.classic-fallback"
    assert "slide-01" in str(exc.value)


@pytest.mark.parametrize("png", [STUDIO_1, STUDIO_2])
def test_guard_passes_on_real_studio_cards(png: Path) -> None:
    assert png.exists(), f"real Studio fixture missing: {png.name}"
    # Must NOT raise.
    _assert_studio_image_card(png, slide_id="slide-01", generation_id="gen-studio")


def test_guard_raises_recoverable_on_unreadable_export(tmp_path: Path) -> None:
    # A zero-byte / truncated / non-PNG export must surface as a recoverable
    # GammaDispatchError (export-unreadable), NOT a bare PIL OSError that would
    # escape the dispatch error family and kill the trial (review finding EC1).
    bad = tmp_path / "zero-byte.png"
    bad.write_bytes(b"")
    with pytest.raises(GammaDispatchError) as exc:
        _assert_studio_image_card(bad, slide_id="slide-07", generation_id="gen-bad")
    assert exc.value.tag == "gamma.studio.export-unreadable"
    assert "slide-07" in str(exc.value)


# --- Normalizer: studio requires a template id; default is api (Classic) --------

def _settings(**b: object) -> dict[str, object]:
    return {"gamma_settings": [{"variant_id": "B", **b}]}


def test_studio_without_template_id_hard_fails() -> None:
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(_settings(production_mode="studio"))
    assert exc.value.tag == "gamma.settings.invalid"
    assert "studio_template_id" in str(exc.value)


def test_studio_with_template_id_normalizes() -> None:
    out = _normalized_gamma_settings(
        _settings(production_mode="studio", studio_template_id="g_nv5q4da69qiiu8q")
    )
    b = next(item for item in out if item["variant_id"] == "B")
    assert b["production_mode"] == "studio"
    assert b["studio_template_id"] == "g_nv5q4da69qiiu8q"


def test_invalid_production_mode_rejected() -> None:
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(_settings(production_mode="playwright"))
    assert exc.value.tag == "gamma.settings.invalid"


def test_default_production_mode_is_api_classic() -> None:
    # No production_mode set anywhere -> both variants default to "api" (the
    # unchanged Classic path); the studio fork is unreachable.
    out = _normalized_gamma_settings({"gamma_settings": [{"variant_id": "A"}, {"variant_id": "B"}]})
    assert all(item["production_mode"] == "api" for item in out)
