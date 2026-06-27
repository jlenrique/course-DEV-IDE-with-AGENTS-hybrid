"""P5 Step 4 — tier-4/5 default loaders wired into the shared mapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists._shared.voice_direction_map import (
    SUPPORTED_RENDER_STRATEGIES,
    VOICE_ID_FALLBACK_SOURCE,
    VoiceDirectionMapError,
    clean_default_tier,
    load_style_guide_tts_defaults,
    normalize_optional_str,
    resolve_voice_id_with_source,
    voice_selection_default_tier,
)
from app.specialists.irene.authoring.pass_2_template import VoiceDirection


def test_normalize_optional_str_collapses_blank_to_none() -> None:
    assert normalize_optional_str("") is None
    assert normalize_optional_str("   ") is None
    assert normalize_optional_str(None) is None
    assert normalize_optional_str("voice-1") == "voice-1"
    assert normalize_optional_str("  voice-1  ") == "voice-1"


def test_voice_selection_default_tier_guards_empty() -> None:
    assert voice_selection_default_tier("narrator") == {"voice_id": "narrator"}
    assert voice_selection_default_tier("") == {}
    assert voice_selection_default_tier(None) == {}


def test_supported_render_strategies_is_tts_only() -> None:
    assert frozenset({"tts"}) == SUPPORTED_RENDER_STRATEGIES


def test_load_style_guide_defaults_from_repo() -> None:
    defaults = load_style_guide_tts_defaults()
    # state/config/style_guide.yaml ships stability/similarity_boost/style/speed.
    assert defaults["similarity_boost"] == 0.75
    assert defaults["stability"] == 0.5
    assert defaults["speed"] == 1.0
    # Blank default_voice_id / model_id are dropped (clean-payload contract).
    assert "voice_id" not in defaults
    assert "model_id" not in defaults


def test_load_style_guide_defaults_custom_path(tmp_path: Path) -> None:
    sg = tmp_path / "style_guide.yaml"
    sg.write_text(
        "tool_parameters:\n"
        "  elevenlabs:\n"
        "    default_voice_id: voice-xyz\n"
        "    model_id: eleven_multilingual_v2\n"
        "    stability: 0.4\n"
        "    style: ''\n",
        encoding="utf-8",
    )
    defaults = load_style_guide_tts_defaults(sg)
    assert defaults["voice_id"] == "voice-xyz"
    assert defaults["model_id"] == "eleven_multilingual_v2"
    assert defaults["stability"] == 0.4
    assert "style" not in defaults  # blank string dropped


def test_load_style_guide_defaults_missing_file(tmp_path: Path) -> None:
    assert load_style_guide_tts_defaults(tmp_path / "nope.yaml") == {}


# M1 — clean_default_tier.
def test_clean_default_tier_drops_blank_and_none() -> None:
    raw = {"voice_id": "", "stability": "  ", "style": None, "speed": 1.0, "model_id": "m"}
    assert clean_default_tier(raw) == {"speed": 1.0, "model_id": "m"}
    assert clean_default_tier(None) == {}
    assert clean_default_tier({}) == {}


# S4 — malformed style_guide raises the typed leaf error.
def test_load_style_guide_corrupt_raises_typed_error(tmp_path: Path) -> None:
    bad = tmp_path / "style_guide.yaml"
    bad.write_text("tool_parameters: : : [unbalanced\n", encoding="utf-8")
    with pytest.raises(VoiceDirectionMapError) as exc:
        load_style_guide_tts_defaults(bad)
    assert exc.value.tag == "elevenlabs.style-guide.malformed"


# S6 — single-source voice_id resolution + provenance.
def test_resolve_voice_id_with_source_walks_tiers() -> None:
    explicit = VoiceDirection.model_validate({"elevenlabs": {"voice_id": "explicit"}})
    plain = VoiceDirection()
    assert resolve_voice_id_with_source(explicit) == (
        "explicit",
        "voice_direction.elevenlabs.voice_id",
    )
    assert resolve_voice_id_with_source(plain, segment_voice_id="seg") == (
        "seg",
        "segment voice_id",
    )
    assert resolve_voice_id_with_source(
        plain, voice_selection_default={"voice_id": "vs"}
    ) == ("vs", "voice-selection.json")
    assert resolve_voice_id_with_source(
        plain, style_guide_defaults={"voice_id": "sg"}
    ) == ("sg", "style_guide.yaml")
    assert resolve_voice_id_with_source(plain) == (None, VOICE_ID_FALLBACK_SOURCE)
