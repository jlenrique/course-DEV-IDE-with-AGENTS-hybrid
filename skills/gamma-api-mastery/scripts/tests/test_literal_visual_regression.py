"""Regression-proofing tests for literal-visual slide production (pre-feature).

These tests lock in the CURRENT literal-visual behavior BEFORE the
preintegration Git-site hosting feature is added. They guard against
accidentally breaking URL validation, diagram_card injection, or the
generate_deck_mixed_fidelity literal-visual call path when that feature
is later implemented.

Design intent
-------------
* validate_image_url is NOT mocked — it runs against real network endpoints.
* The Gamma API client IS mocked — we are not testing Gamma; we are testing
  our routing, validation, and content-assembly logic.
* Tests marked ``live_api`` require internet access but NO API credentials.
* Tests marked ``live_api_e2e`` require both internet and credentials (none here).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, _SCRIPTS_DIR)

import gamma_operations  # noqa: E402
from gamma_operations import (  # noqa: E402
    generate_deck_mixed_fidelity,
    validate_image_url,
)

# ---------------------------------------------------------------------------
# Helper shared with other test modules
# ---------------------------------------------------------------------------

def _valid_theme_resolution() -> dict:
    return {
        "requested_theme_key": "hil-2026-apc-nejal-A",
        "resolved_theme_key": "theme_abc",
        "resolved_parameter_set": "hil-2026-apc-nejal-A",
        "mapping_source": "state/config/gamma-style-presets.yaml",
        "mapping_version": "1",
        "user_confirmation": True,
    }


# ---------------------------------------------------------------------------
# Regression: validate_image_url — no network (pure logic)
# ---------------------------------------------------------------------------

class TestValidateImageUrlPureLogic:
    """Pure-logic checks that require no network access."""

    def test_rejects_non_https_url(self) -> None:
        ok, reason = validate_image_url("http://example.com/img.png")
        assert not ok
        assert "HTTPS" in reason

    def test_rejects_bare_string_that_is_not_a_url(self) -> None:
        ok, reason = validate_image_url("not-a-url")
        assert not ok

    def test_rejects_empty_string(self) -> None:
        ok, reason = validate_image_url("")
        assert not ok


# ---------------------------------------------------------------------------
# Regression: validate_image_url — live network (no credentials needed)
# ---------------------------------------------------------------------------

@pytest.mark.live_api
class TestValidateImageUrlLiveNetwork:
    """Tests that make real HTTP HEAD requests. Requires internet access."""

    # A stable, publicly accessible PNG served with correct content-type.
    # Using httpbin.org which returns image/png with a valid PNG body.
    _LIVE_PNG_URL = "https://httpbin.org/image/png"

    # A stable endpoint that returns a known non-200 status code.
    _LIVE_404_URL = "https://httpbin.org/status/404"

    def test_accepts_real_https_image_url(self) -> None:
        ok, reason = validate_image_url(self._LIVE_PNG_URL)
        assert ok, f"Expected valid image URL but got: {reason}"

    def test_rejects_url_with_non_200_status(self) -> None:
        ok, reason = validate_image_url(self._LIVE_404_URL)
        assert not ok
        assert "404" in reason

    def test_rejects_unreachable_host(self) -> None:
        # RFC 2606 reserved name — guaranteed not to resolve
        ok, reason = validate_image_url("https://no-such-host.invalid/img.png")
        assert not ok
        assert "Request failed" in reason


# ---------------------------------------------------------------------------
# Regression: generate_deck_mixed_fidelity — URL validation is not mocked
# ---------------------------------------------------------------------------

@pytest.mark.live_api
class TestLiteralVisualGenerationWithRealUrlValidation:
    """End-to-end literal-visual path with real validate_image_url.

    The Gamma API client IS mocked (we are not testing Gamma).
    validate_image_url is NOT mocked — this test confirms that:
      1. The literal-visual dispatch path calls validate_image_url for real.
      2. A valid, publicly accessible image URL passes through without error.
      3. The resulting gary_slide_output is fully populated for literal-visual.
    """

    _LIVE_PNG_URL = "https://httpbin.org/image/png"

    def test_literal_visual_slide_accepted_with_real_valid_url(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 2,
                "image_url": self._LIVE_PNG_URL,
                "placement_note": "Image-dominant layout.",
                "required": True,
            }
        ]

        mock_client = MagicMock()
        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual"},
            ]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-REGRESSION-001",
                client=mock_client,
                diagram_cards=diagram_cards,
                run_id="REGRESSION-001",
            )

        assert result["calls_made"] == 2
        output = result["gary_slide_output"]
        # card_number 2 is the literal-visual slide
        lv_slide = next(s for s in output if s["card_number"] == 2)
        assert lv_slide["card_number"] == 2
        assert lv_slide["slide_id"] == "C1-M1-PRES-REGRESSION-001-card-02"
        # fidelity lives in provenance, not in gary_slide_output
        prov = result["provenance"]
        lv_prov = next(p for p in prov if p["card_number"] == 2)
        assert lv_prov["fidelity"] == "literal-visual"

    def test_literal_visual_slide_rejected_with_invalid_url_no_mock(self) -> None:
        """Invalid URL raises ValueError without any mocking of validate_image_url."""
        slides = [
            {"slide_number": 1, "content": "Literal visual", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 1,
                "image_url": "http://example.com/bad-scheme.png",  # non-HTTPS → invalid
                "placement_note": "Image-dominant.",
                "required": True,
            }
        ]

        mock_client = MagicMock()
        with (
            patch.object(gamma_operations, "generate_slide"),
            pytest.raises(ValueError, match="image URL validation failed"),
        ):
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-REGRESSION-002",
                client=mock_client,
                diagram_cards=diagram_cards,
                run_id="REGRESSION-002",
            )
