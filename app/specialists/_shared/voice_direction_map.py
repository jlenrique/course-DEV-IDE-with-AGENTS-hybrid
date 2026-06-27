"""Pure leaf: directed-voice direction -> ElevenLabs TTS settings mapper.

FROZEN SEAM (P5 directed-voice arc, Step 1). Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§G-RECONCILED (Marcus control-card 5-tier precedence) + §F.1 OQ-B1.

This module is the single source of truth shared by Enrique (TTS dispatch,
Step 4) and Storyboard B (display parity, Step 3). It hosts a PURE MAPPER plus
CALLER-DRIVEN default loaders (Winston, Step-4 amendment):

- The MAPPER (`map_voice_direction_to_tts` / `resolve_voice_id_with_source`) stays
  pure over the import-frozen table: the tone/pace/energy -> settings table is
  loaded ONCE at import into the frozen module constant `VOICE_DIRECTION_MAP` (a
  recursively-immutable MappingProxyType view, so the frozen-neck claim is
  enforced in-process), and the mapper does NO per-call file I/O — the tier-3/4/5
  default dicts are passed IN by the caller.
- The DEFAULT LOADERS (`load_style_guide_tts_defaults` / `voice_selection_default_tier`)
  DO file I/O (tier-5 `state/config/style_guide.yaml`, tier-4 voice-selection),
  but they are invoked by the Step-4 caller (Enrique), not from inside the mapper,
  so the mapper's purity is preserved.

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

# Render strategies Enrique consumes at Step 4. `dialogue` is modeled-not-consumed
# (Text-to-Dialogue follow-on); a segment that asks for anything outside this set
# must FAIL LOUD at dispatch rather than silently render single-voice (Card 3 +
# follow-on `directed-voice-render-strategy-fail-loud-step4`).
SUPPORTED_RENDER_STRATEGIES: frozenset[str] = frozenset({"tts"})

# Repo-root style_guide.yaml = the tier-5 default source (P5 §F 5-tier precedence).
# parents: [0]=_shared [1]=specialists [2]=app [3]=repo-root.
_STYLE_GUIDE_PATH = Path(__file__).resolve().parents[3] / "state" / "config" / "style_guide.yaml"


def normalize_optional_str(value: Any) -> str | None:
    """Collapse falsy/blank strings to None (empty-voice_id call-site guard).

    Follow-on `directed-voice-step4-empty-voice-id-callsite-guard`: the Pydantic
    boundary rejects `""` voice_id, but raw default-tier strings reaching the
    mapper as `segment_voice_id=""` would still mask precedence tiers 3-5 (the
    mapper resolves on `is not None`). Normalize at the call site so the boundary
    guarantee is not lost for un-validated inputs.
    """
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class VoiceDirectionMapError(Exception):
    """Tier-5 style-guide load failed (corrupt YAML / unreadable file).

    The pure leaf cannot import Enrique's ``EnriqueActError`` (M3 + cycle), so it
    raises this typed error; the Enrique call site re-raises it as a tagged,
    recoverable ``EnriqueActError`` (S4). It carries ``tag`` so the mapping is a
    one-liner at the call site.
    """

    tag = "elevenlabs.style-guide.malformed"


def load_style_guide_tts_defaults(style_guide_path: str | Path | None = None) -> dict[str, Any]:
    """Read the tier-5 ElevenLabs defaults from `state/config/style_guide.yaml`.

    Returns only the populated TTS-settings fields (blank strings and nulls are
    dropped, matching the client's `_clean_payload` contract) keyed by the
    ElevenLabs API field names the mapper resolves. Missing file -> {} (the
    style guide is an optional default source, never a hard dependency). A
    corrupt/unreadable file raises ``VoiceDirectionMapError`` (S4) instead of a
    bare ``YAMLError``/``OSError`` escaping the dispatcher's error-pause handler.
    """
    path = Path(style_guide_path) if style_guide_path is not None else _STYLE_GUIDE_PATH
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as exc:
        raise VoiceDirectionMapError(
            f"style_guide.yaml at {path} is unreadable/corrupt: {exc}"
        ) from exc
    tool_params = data.get("tool_parameters") if isinstance(data, dict) else None
    elevenlabs = tool_params.get("elevenlabs") if isinstance(tool_params, dict) else None
    if not isinstance(elevenlabs, dict):
        return {}
    out: dict[str, Any] = {}
    # `default_voice_id` is the style-guide spelling for the tier-5 voice_id.
    voice_id = normalize_optional_str(elevenlabs.get("default_voice_id"))
    if voice_id is not None:
        out["voice_id"] = voice_id
    for field in ("model_id", "stability", "similarity_boost", "style", "speed"):
        value = elevenlabs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        out[field] = value
    return out


def voice_selection_default_tier(selected_voice_id: Any) -> dict[str, Any]:
    """Build the tier-4 default dict from a `voice-selection.json` selection.

    The selected voice is the global fallback voice_id (tier 4). Returns {} when
    the selection carries no usable voice id (guards `""`/whitespace).
    """
    voice_id = normalize_optional_str(selected_voice_id)
    return {"voice_id": voice_id} if voice_id is not None else {}


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


def clean_default_tier(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Drop None and blank-string values from a default-tier dict.

    Tier-4/5 are already cleaned at load (``load_style_guide_tts_defaults`` /
    ``voice_selection_default_tier``); tier-3 (``voice_direction_defaults``)
    arrives RAW from the payload. An uncleaned ``{"voice_id": ""}`` would mask a
    valid lower tier (the mapper resolves on ``is not None``), and an uncleaned
    ``{"stability": ""}`` would flow a blank string to the ElevenLabs API (422).
    Cleaning every default tier the SAME way closes both (M1).
    """
    if not raw:
        return {}
    out: dict[str, Any] = {}
    for key, value in raw.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        out[key] = value
    return out


# Ordered voice_id precedence labels (card's exact tiers 1->5). Kept as the
# SINGLE SOURCE so the resolved voice_id and its provenance label can never
# diverge (S6): ``map_voice_direction_to_tts`` and ``resolve_voice_id_with_source``
# both walk this same candidate list.
VOICE_ID_FALLBACK_SOURCE = "fallback default"


def _voice_id_candidates(
    direction: VoiceDirection,
    segment_voice_id: str | None,
    tier3: dict[str, Any],
    tier4: dict[str, Any],
    tier5: dict[str, Any],
) -> list[tuple[str, Any]]:
    explicit = direction.elevenlabs
    explicit_voice = getattr(explicit, "voice_id", None) if explicit is not None else None
    return [
        ("voice_direction.elevenlabs.voice_id", explicit_voice),
        ("segment voice_id", segment_voice_id),
        ("pass-2 voice_direction_defaults", tier3.get("voice_id")),
        ("voice-selection.json", tier4.get("voice_id")),
        ("style_guide.yaml", tier5.get("voice_id")),
    ]


def resolve_voice_id_with_source(
    direction: VoiceDirection,
    *,
    segment_voice_id: str | None = None,
    pass2_voice_direction_defaults: dict[str, Any] | None = None,
    voice_selection_default: dict[str, Any] | None = None,
    style_guide_defaults: dict[str, Any] | None = None,
) -> tuple[Any, str]:
    """Resolve voice_id AND the tier that supplied it, from one candidate walk.

    Returns ``(voice_id, source_label)``. The source label is one of the tier
    labels above or ``VOICE_ID_FALLBACK_SOURCE`` when no tier supplies a voice_id.
    """
    candidates = _voice_id_candidates(
        direction,
        segment_voice_id,
        pass2_voice_direction_defaults or {},
        voice_selection_default or {},
        style_guide_defaults or {},
    )
    for label, value in candidates:
        if value is not None:
            return value, label
    return None, VOICE_ID_FALLBACK_SOURCE


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

    # voice_id from the SINGLE-SOURCE resolver (S6) so resolved["voice_id"] and
    # any provenance label derived by the caller can never disagree.
    voice_id, _voice_source = resolve_voice_id_with_source(
        direction,
        segment_voice_id=segment_voice_id,
        pass2_voice_direction_defaults=tier3,
        voice_selection_default=tier4,
        style_guide_defaults=tier5,
    )
    resolved: dict[str, Any] = {
        "voice_id": voice_id,
        "model_id": _setting("model_id", None),
        "stability": _setting("stability", derived_stability),
        "similarity_boost": _setting("similarity_boost", None),
        "style": _setting("style", derived_style),
        "speed": _setting("speed", derived_speed),
    }
    return resolved


__all__ = [
    "MAP_VERSION",
    "SUPPORTED_RENDER_STRATEGIES",
    "VOICE_DIRECTION_ACTIVE_ENV",
    "VOICE_DIRECTION_MAP",
    "VOICE_ID_FALLBACK_SOURCE",
    "VoiceDirectionMapError",
    "clean_default_tier",
    "load_style_guide_tts_defaults",
    "map_voice_direction_to_tts",
    "normalize_optional_str",
    "resolve_voice_id_with_source",
    "voice_direction_active",
    "voice_selection_default_tier",
]
