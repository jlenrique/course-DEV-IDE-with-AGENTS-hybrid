"""Step-1 directed-voice mapper pins (P5 directed-voice arc, 2026-06-27).

Authority: strawman §G-RECONCILED (5-tier per-field precedence) + §F.1 OQ-B1.
The tone/pace/energy -> TTS settings table lives in
`app/specialists/enrique/voice_direction_map.yaml`, loaded ONCE at import into a
frozen module constant; `map_voice_direction_to_tts` is a PURE function over that
constant. A shape-pin test pins the exact float outputs so the table cannot drift
silently; `map_version` is pinned.

This is the frozen seam ONLY — Enrique consumption (and the real
voice-selection.json / style_guide.yaml file reads) is Step 4 (not wired here).
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Mapping

import pytest

from app.specialists._shared import voice_direction_map as vdm
from app.specialists._shared.voice_direction_map import (
    map_voice_direction_to_tts,
    voice_direction_active,
)
from app.specialists.irene.authoring.pass_2_template import (
    DialogueTurn,
    ElevenLabsSettings,
    VoiceDirection,
)

# A tier-5 (style_guide) backstop covering every settings field.
STYLE_GUIDE = {
    "voice_id": "style-guide-voice",
    "model_id": "eleven_multilingual_v2",
    "stability": 0.50,
    "similarity_boost": 0.75,
    "style": 0.30,
    # Deliberately NOT 1.0: a distinct tier-5 fallback so a pace="neutral"
    # result of 1.0 provably comes from the table (tier 2), not fallthrough.
    "speed": 0.80,
}


# --------------------------------------------------------------------------- #
# map_version pin.
# --------------------------------------------------------------------------- #
def test_map_version_pinned() -> None:
    assert vdm.MAP_VERSION == "voice-direction-map.v1"
    assert vdm.VOICE_DIRECTION_MAP["map_version"] == "voice-direction-map.v1"


# --------------------------------------------------------------------------- #
# Mapper shape-pin: pace -> speed exact floats (control-card spellings).
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("pace", "expected_speed"),
    [("slower", 0.94), ("neutral", 1.0), ("faster", 1.1)],
)
def test_pace_maps_to_speed_shape_pin(pace: str, expected_speed: float) -> None:
    resolved = map_voice_direction_to_tts(
        VoiceDirection(pace=pace), style_guide_defaults=STYLE_GUIDE
    )
    # STYLE_GUIDE["speed"] is 0.80, so every pinned pace value (incl. neutral=1.0)
    # is provably table-derived (tier 2), not a tier-5 fallthrough.
    assert expected_speed != STYLE_GUIDE["speed"]
    assert resolved["speed"] == expected_speed


def test_pace_slower_and_faster_differ() -> None:
    slower = map_voice_direction_to_tts(
        VoiceDirection(pace="slower"), style_guide_defaults=STYLE_GUIDE
    )
    faster = map_voice_direction_to_tts(
        VoiceDirection(pace="faster"), style_guide_defaults=STYLE_GUIDE
    )
    assert slower["speed"] < faster["speed"]


# --------------------------------------------------------------------------- #
# 5-tier per-field precedence (the control-card ordering).
# --------------------------------------------------------------------------- #
def test_explicit_elevenlabs_override_wins_over_everything() -> None:
    # Tier 1 explicit beats derived (tier 2) AND every default tier.
    direction = VoiceDirection(
        energy="high",  # would derive a low stability
        elevenlabs=ElevenLabsSettings(stability=0.95),
    )
    resolved = map_voice_direction_to_tts(
        direction,
        pass2_voice_direction_defaults={"stability": 0.10},
        voice_selection_default={"stability": 0.20},
        style_guide_defaults={"stability": 0.30},
    )
    assert resolved["stability"] == 0.95


def test_derived_wins_over_default_tiers() -> None:
    # Tier 2 (derived from pace) beats tiers 3/4/5.
    resolved = map_voice_direction_to_tts(
        VoiceDirection(pace="slower"),
        pass2_voice_direction_defaults={"speed": 1.05},
        style_guide_defaults={"speed": 1.0},
    )
    assert resolved["speed"] == 0.94


def test_settings_tier_order_3_then_4_then_5() -> None:
    # No explicit, no derived: tier 3 beats tier 4 beats tier 5.
    direction = VoiceDirection()  # nothing derives stability
    t3 = map_voice_direction_to_tts(
        direction,
        pass2_voice_direction_defaults={"stability": 0.31},
        voice_selection_default={"stability": 0.32},
        style_guide_defaults={"stability": 0.33},
    )
    assert t3["stability"] == 0.31

    t4 = map_voice_direction_to_tts(
        direction,
        voice_selection_default={"stability": 0.32},
        style_guide_defaults={"stability": 0.33},
    )
    assert t4["stability"] == 0.32

    t5 = map_voice_direction_to_tts(direction, style_guide_defaults={"stability": 0.33})
    assert t5["stability"] == 0.33


def test_voice_id_5_tier_walk() -> None:
    direction_explicit = VoiceDirection(elevenlabs=ElevenLabsSettings(voice_id="t1"))
    assert (
        map_voice_direction_to_tts(
            direction_explicit,
            segment_voice_id="t2",
            pass2_voice_direction_defaults={"voice_id": "t3"},
            voice_selection_default={"voice_id": "t4"},
            style_guide_defaults={"voice_id": "t5"},
        )["voice_id"]
        == "t1"
    )

    empty = VoiceDirection()
    assert (
        map_voice_direction_to_tts(
            empty,
            segment_voice_id="t2",
            pass2_voice_direction_defaults={"voice_id": "t3"},
            voice_selection_default={"voice_id": "t4"},
            style_guide_defaults={"voice_id": "t5"},
        )["voice_id"]
        == "t2"
    )
    assert (
        map_voice_direction_to_tts(
            empty,
            pass2_voice_direction_defaults={"voice_id": "t3"},
            voice_selection_default={"voice_id": "t4"},
            style_guide_defaults={"voice_id": "t5"},
        )["voice_id"]
        == "t3"
    )
    assert (
        map_voice_direction_to_tts(
            empty,
            voice_selection_default={"voice_id": "t4"},
            style_guide_defaults={"voice_id": "t5"},
        )["voice_id"]
        == "t4"
    )
    assert (
        map_voice_direction_to_tts(empty, style_guide_defaults={"voice_id": "t5"})[
            "voice_id"
        ]
        == "t5"
    )


def test_no_defaults_resolves_to_none() -> None:
    # With nothing supplied and an empty direction, EVERY field resolves to None.
    resolved = map_voice_direction_to_tts(VoiceDirection())
    assert resolved["voice_id"] is None
    assert resolved["model_id"] is None
    assert resolved["speed"] is None
    assert resolved["stability"] is None
    assert resolved["style"] is None
    assert resolved["similarity_boost"] is None


def test_real_segment_voice_id_is_not_masked() -> None:
    # MUST-FIX regression guard: a real segment voice_id (tier 2) must flow when
    # there is no explicit elevenlabs.voice_id. (Empty-string voice_id can no
    # longer reach here — it is rejected at the model boundary.)
    resolved = map_voice_direction_to_tts(
        VoiceDirection(), segment_voice_id="real-voice", style_guide_defaults=STYLE_GUIDE
    )
    assert resolved["voice_id"] == "real-voice"


def test_energy_derives_bounded_stability_and_style() -> None:
    resolved = map_voice_direction_to_tts(
        VoiceDirection(energy="high"), style_guide_defaults=STYLE_GUIDE
    )
    assert 0.0 <= resolved["stability"] <= 1.0
    assert 0.0 <= resolved["style"] <= 1.0
    medium = map_voice_direction_to_tts(
        VoiceDirection(energy="medium"), style_guide_defaults=STYLE_GUIDE
    )
    assert resolved["stability"] < medium["stability"]
    assert resolved["style"] > medium["style"]


def test_energy_overrides_tone_on_shared_fields() -> None:
    # tone sets the base; energy overrides stability/style.
    tone_only = map_voice_direction_to_tts(
        VoiceDirection(emotional_tone="reflective"), style_guide_defaults=STYLE_GUIDE
    )
    both = map_voice_direction_to_tts(
        VoiceDirection(emotional_tone="reflective", energy="high"),
        style_guide_defaults=STYLE_GUIDE,
    )
    assert both["stability"] != tone_only["stability"]
    assert both["stability"] == vdm.VOICE_DIRECTION_MAP["energy"]["high"]["stability"]


# --------------------------------------------------------------------------- #
# dialogue_turns inert-fence: modeled-not-consumed; render_strategy beyond tts
# is ignored by the mapper.
# --------------------------------------------------------------------------- #
def test_mapper_ignores_dialogue_turns() -> None:
    plain = VoiceDirection(pace="neutral", energy="medium")
    with_turns = VoiceDirection(
        pace="neutral",
        energy="medium",
        dialogue_turns=(
            DialogueTurn(speaker="a", text="hello", voice_id=None),
            DialogueTurn(speaker="b", text="world", voice_id="vb"),
        ),
    )
    assert map_voice_direction_to_tts(
        plain, style_guide_defaults=STYLE_GUIDE
    ) == map_voice_direction_to_tts(with_turns, style_guide_defaults=STYLE_GUIDE)


def test_mapper_emits_no_dialogue_or_render_strategy_keys() -> None:
    resolved = map_voice_direction_to_tts(
        VoiceDirection(render_strategy="dialogue"), style_guide_defaults=STYLE_GUIDE
    )
    assert "dialogue_turns" not in resolved
    assert "render_strategy" not in resolved


def test_resolved_dict_carries_only_tts_api_params() -> None:
    # INTENTIONAL Step-1 omissions (distinguishable from oversight): pauses are
    # assembly silence-padding (Step 3/4), and delivery_tag/delivery_intent are
    # the generation-text / display channels (Step 4) — none are TTS API params,
    # so none appear in the resolved settings dict.
    direction = VoiceDirection(
        pace="faster",
        energy="high",
        delivery_tag="[thoughtfully]",
        delivery_intent="warm explainer",
        pause_before_seconds=1.0,
        pause_after_seconds=2.0,
    )
    resolved = map_voice_direction_to_tts(direction, style_guide_defaults=STYLE_GUIDE)
    assert set(resolved) == {
        "voice_id",
        "model_id",
        "stability",
        "similarity_boost",
        "style",
        "speed",
    }
    for omitted in (
        "pause_before_seconds",
        "pause_after_seconds",
        "delivery_tag",
        "delivery_intent",
    ):
        assert omitted not in resolved


# --------------------------------------------------------------------------- #
# Purity / import discipline: mapper does not import app.marcus; the table is
# an import-frozen module constant (no per-call file I/O).
# --------------------------------------------------------------------------- #
def _imported_module_names(module: object) -> set[str]:
    """Collect imported module names via AST (ignores docstrings/comments)."""
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


def test_mapper_module_does_not_import_app_marcus() -> None:
    # AST-level: no runtime import of app.marcus (TYPE_CHECKING import of the
    # irene VoiceDirection type is allowed; it is not app.marcus).
    imported = _imported_module_names(vdm)
    assert not any(
        name == "marcus" or name.startswith("app.marcus") for name in imported
    )


def test_table_is_import_frozen_constant_not_per_call_io() -> None:
    # AST-level: the per-call function performs no file/yaml I/O — the table is
    # resolved from the import-frozen module constant only.
    fn_tree = ast.parse(inspect.getsource(map_voice_direction_to_tts))
    forbidden_calls: list[str] = []
    for node in ast.walk(fn_tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                forbidden_calls.append("open")
            if isinstance(func, ast.Attribute) and func.attr in {
                "read_text",
                "open",
                "safe_load",
                "load",
            }:
                forbidden_calls.append(func.attr)
    assert forbidden_calls == []
    # The table is a module-level mapping constant.
    assert isinstance(vdm.VOICE_DIRECTION_MAP, Mapping)


def test_table_is_recursively_immutable() -> None:
    # Frozen-neck discipline (Winston): the loaded table cannot be mutated
    # in-process, at the top level OR in a nested block.
    with pytest.raises(TypeError):
        vdm.VOICE_DIRECTION_MAP["map_version"] = "tampered"  # type: ignore[index]
    with pytest.raises(TypeError):
        vdm.VOICE_DIRECTION_MAP["pace"]["slower"] = 0.5  # type: ignore[index]
    with pytest.raises(TypeError):
        vdm.VOICE_DIRECTION_MAP["emotional_tone"]["warm"]["stability"] = 0.99  # type: ignore[index]


# --------------------------------------------------------------------------- #
# Governance-frozen table: clear errors on a malformed/missing-key table.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("drop_key", "expected_fragment"),
    [
        ("map_version", "map_version"),
        ("pace", "pace"),
        ("emotional_tone", "emotional_tone"),
        ("energy", "energy"),
    ],
)
def test_load_map_raises_clear_error_on_missing_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    drop_key: str,
    expected_fragment: str,
) -> None:
    import yaml as _yaml

    table = {
        "map_version": "voice-direction-map.v1",
        "pace": {"slower": 0.94, "neutral": 1.0, "faster": 1.1},
        "emotional_tone": {"neutral": {"stability": 0.5, "style": 0.3}},
        "energy": {"medium": {"stability": 0.5, "style": 0.35}},
    }
    table.pop(drop_key)
    bad = tmp_path / "voice_direction_map.yaml"
    bad.write_text(_yaml.safe_dump(table), encoding="utf-8")
    monkeypatch.setattr(vdm, "_MAP_PATH", bad)

    with pytest.raises(ValueError, match=expected_fragment) as exc:
        vdm._load_map()
    assert "governance-frozen table" in str(exc.value)


def test_load_map_raises_when_dimension_is_not_a_mapping(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import yaml as _yaml

    table = {
        "map_version": "voice-direction-map.v1",
        "pace": ["not", "a", "mapping"],
        "emotional_tone": {"neutral": {"stability": 0.5, "style": 0.3}},
        "energy": {"medium": {"stability": 0.5, "style": 0.35}},
    }
    bad = tmp_path / "voice_direction_map.yaml"
    bad.write_text(_yaml.safe_dump(table), encoding="utf-8")
    monkeypatch.setattr(vdm, "_MAP_PATH", bad)

    with pytest.raises(ValueError, match="pace"):
        vdm._load_map()


# --------------------------------------------------------------------------- #
# Feature-flag helper.
# --------------------------------------------------------------------------- #
def test_voice_direction_active_default_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE", raising=False)
    assert voice_direction_active() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "Yes", "on", "ON"])
def test_voice_direction_active_truthy(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE", value)
    assert voice_direction_active() is True


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "maybe"])
def test_voice_direction_active_falsy(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE", value)
    assert voice_direction_active() is False
