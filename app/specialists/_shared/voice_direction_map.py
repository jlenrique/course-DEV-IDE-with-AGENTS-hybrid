"""Pure leaf: directed-voice direction -> ElevenLabs TTS settings mapper.

FROZEN SEAM (P5 directed-voice arc, Step 1). Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§G-RECONCILED (Marcus control-card 5-tier precedence) + §F.1 OQ-B1.

This module is the single source of truth shared by Enrique (TTS dispatch,
Step 4) and Storyboard B (display parity, Step 3). It is a PURE leaf: the
tone/pace/energy -> settings table is loaded ONCE at import into the frozen
module constant `VOICE_DIRECTION_MAP` (a recursively-immutable MappingProxyType
view, so the frozen-neck claim is enforced in-process), and
`map_voice_direction_to_tts(...)` is a pure function over that constant (no
per-call file I/O).

Import-linter fence (Winston W-A2, precedent `workbook_enrichment.py:29-35`):
this leaf does NOT import `app.marcus`. The `app.specialists` ->
`app.marcus.facade/intake/orchestrator` edge is forbidden by **import-linter
Contract M3** ("Marcus Contract M3 - app.specialists may not import app.marcus
facade/intake/orchestrator"); the VoiceDirection type is imported only under
TYPE_CHECKING so the runtime leaf stays decoupled from the irene authoring tree.

5-tier per-field precedence (§G-RECONCILED): explicit `elevenlabs.{field}` >
derived-from-direction (yaml table) > Pass-2 defaults > voice-selection default >
style-guide default. `dialogue_turns` and `render_strategy` beyond `tts` are
explicitly IGNORED here (modeled-not-consumed in v1).

INTENTIONAL Step-1 omissions from the resolved dict (NOT an oversight): the
resolved settings carry ONLY the ElevenLabs API parameters
(`voice_id/model_id/stability/similarity_boost/style/speed`).
`pause_before_seconds`/`pause_after_seconds` are deliberately absent — they are
assembly silence-padding applied at Step 3/4 stitching, not TTS params.
`delivery_tag`/`delivery_intent` are deliberately absent — `delivery_tag` is the
generation-text channel consumed at Step 4 and `delivery_intent` is
display/provenance only; neither is ever a TTS API parameter.

NOTE: this is the frozen seam only — it is NOT called from Enrique yet (Step 4).
"""

from __future__ import annotations

import os
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:  # pragma: no cover - typing only, keeps the leaf decoupled.
    from app.specialists.irene.authoring.pass_2_template import VoiceDirection

# Feature flag (default OFF). Mirrors the *_ACTIVE env-toggle idiom at
# app/marcus/orchestrator/g0_enrichment_wiring.py:104-114 — flag OFF means
# non-directed runs are byte-identical.
VOICE_DIRECTION_ACTIVE_ENV = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"

# The yaml table lives under the Enrique package (CD tunes course defaults
# there); it is loaded ONCE here into an import-frozen constant.
_MAP_PATH = Path(__file__).resolve().parent.parent / "enrique" / "voice_direction_map.yaml"

# Required top-level keys of the governance-frozen table (clear-error contract).
_REQUIRED_DIMENSIONS = ("pace", "emotional_tone", "energy")


def _freeze(value: Any) -> Any:
    """Recursively wrap mappings in MappingProxyType so the table is immutable."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    return value


def _load_map() -> Any:
    with _MAP_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(
            "voice_direction_map.yaml must be a mapping (this is a "
            "governance-frozen table)"
        )
    if "map_version" not in data:
        raise ValueError(
            "voice_direction_map.yaml is missing required key 'map_version' "
            "(this is a governance-frozen table)"
        )
    for dimension in _REQUIRED_DIMENSIONS:
        if dimension not in data:
            raise ValueError(
                f"voice_direction_map.yaml is missing required key '{dimension}' "
                "(this is a governance-frozen table)"
            )
        if not isinstance(data[dimension], dict):
            raise ValueError(
                f"voice_direction_map.yaml key '{dimension}' must be a mapping "
                "(this is a governance-frozen table)"
            )
    return _freeze(data)


# Import-frozen, recursively-immutable module constant (loaded once at import).
VOICE_DIRECTION_MAP: Any = _load_map()
MAP_VERSION: str = str(VOICE_DIRECTION_MAP["map_version"])


def voice_direction_active() -> bool:
    """Return True iff directed-voice is woken (env toggle; default OFF)."""
    return os.environ.get(VOICE_DIRECTION_ACTIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _first_present(*candidates: Any) -> Any:
    for candidate in candidates:
        if candidate is not None:
            return candidate
    return None


def map_voice_direction_to_tts(
    direction: VoiceDirection,
    *,
    segment_voice_id: str | None = None,
    pass2_voice_direction_defaults: dict[str, Any] | None = None,
    voice_selection_default: dict[str, Any] | None = None,
    style_guide_defaults: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve a VoiceDirection into a flat TTS-settings dict (PURE).

    5-tier per-field precedence (§G-RECONCILED control card). For the ElevenLabs
    *settings* fields (stability/similarity_boost/style/speed/model_id) the
    ordering is:

        (1) segment ``voice_direction.elevenlabs.{field}``
        (2) derived-from-direction (the frozen yaml table: pace/energy/tone)
        (3) Pass-2 ``voice_direction_defaults``
        (4) ``voice-selection.json`` selected default
        (5) ``state/config/style_guide.yaml`` defaults

    For ``voice_id`` the ordering walks tiers 1->5 in the card's exact form:

        (1) ``elevenlabs.voice_id`` -> (2) segment ``voice_id`` ->
        (3) Pass-2 defaults -> (4) voice-selection default -> (5) style-guide.

    The card's tier-2 ("segment voice_id") only participates in voice_id
    resolution; for the other settings, tier 2 is the direction-derived value.

    NOTE: this is the frozen seam only. For Step 1 the caller passes whatever
    defaults dicts it has; the actual voice-selection.json / style_guide.yaml
    file reads are wired at Step 4. ``dialogue_turns`` and ``render_strategy``
    beyond ``tts`` are explicitly IGNORED here (modeled-not-consumed in v1).
    """
    explicit = direction.elevenlabs
    table = VOICE_DIRECTION_MAP

    tier3 = pass2_voice_direction_defaults or {}
    tier4 = voice_selection_default or {}
    tier5 = style_guide_defaults or {}

    # Derived speed from pace.
    derived_speed = table["pace"].get(direction.pace) if direction.pace else None

    # Derived stability/style: tone preset is the base; energy overrides it.
    derived_stability: Any = None
    derived_style: Any = None
    if direction.emotional_tone:
        tone_preset = table["emotional_tone"].get(direction.emotional_tone, {})
        derived_stability = tone_preset.get("stability")
        derived_style = tone_preset.get("style")
    if direction.energy:
        energy_preset = table["energy"].get(direction.energy, {})
        if energy_preset.get("stability") is not None:
            derived_stability = energy_preset["stability"]
        if energy_preset.get("style") is not None:
            derived_style = energy_preset["style"]

    def _explicit(field: str) -> Any:
        return getattr(explicit, field, None) if explicit is not None else None

    def _setting(field: str, derived: Any) -> Any:
        # Tier 1 explicit -> tier 2 derived -> tiers 3/4/5 defaults (per-field).
        return _first_present(
            _explicit(field),
            derived,
            tier3.get(field),
            tier4.get(field),
            tier5.get(field),
        )

    resolved: dict[str, Any] = {
        "voice_id": _first_present(
            _explicit("voice_id"),
            segment_voice_id,
            tier3.get("voice_id"),
            tier4.get("voice_id"),
            tier5.get("voice_id"),
        ),
        "model_id": _setting("model_id", None),
        "stability": _setting("stability", derived_stability),
        "similarity_boost": _setting("similarity_boost", None),
        "style": _setting("style", derived_style),
        "speed": _setting("speed", derived_speed),
    }
    return resolved


__all__ = [
    "MAP_VERSION",
    "VOICE_DIRECTION_ACTIVE_ENV",
    "VOICE_DIRECTION_MAP",
    "map_voice_direction_to_tts",
    "voice_direction_active",
]
