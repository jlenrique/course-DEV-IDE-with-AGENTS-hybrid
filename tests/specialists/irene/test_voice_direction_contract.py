"""Step-1 directed-voice contract pins (P5 directed-voice arc, 2026-06-27).

Authority: `_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§G-RECONCILED (Marcus control-card override — AUTHORITATIVE over §G field
specifics), `schema_version: "voice-direction.v1"`.

Backward-compat pair is the headline DONE: a legacy segment (no voice_direction)
and a directed segment (full voice_direction) both validate. The grounding
firewall (delivery_tag isolation) is RED-pinned: delivery_tag never reaches the
figure-citation gate.
"""

from __future__ import annotations

import inspect

import pytest
from pydantic import ValidationError

from app.specialists.irene.authoring.pass_2_template import (
    DialogueTurn,
    ElevenLabsSettings,
    SegmentManifestSegment,
    VoiceDirection,
)


def _base_segment(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "seg-01",
        "slide_id": "slide-01",
        "card_number": 1,
        "narration_text": (
            "Notice the clinician at the workstation as the systems signal appears."
        ),
        "behavioral_intent": "credible",
        "visual_file": "bundle/slide-01.png",
        "visual_detail_load": "medium",
        "timing_role": "concept-build",
        "content_density": "medium",
        "duration_rationale": (
            "Medium density needs guided explanation while keeping attention on the workstation."
        ),
        "bridge_type": "none",
        "visual_references": [
            {
                "element": "Clinician at workstation",
                "location_on_slide": "center",
                "narration_cue": "clinician at the workstation",
                "perception_source": "slide-01",
            }
        ],
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# Backward-compat pair (the headline DONE).
# --------------------------------------------------------------------------- #
def test_legacy_segment_without_voice_direction_validates() -> None:
    segment = SegmentManifestSegment.model_validate(_base_segment())
    assert segment.voice_direction is None


def test_directed_segment_with_full_voice_direction_validates() -> None:
    direction = {
        "schema_version": "voice-direction.v1",
        "render_strategy": "tts",
        "delivery_intent": "warm explainer",
        "emotional_tone": "warm",
        "pace": "neutral",
        "energy": "medium",
        "delivery_tag": "[thoughtfully]",
        "pause_before_seconds": 0.5,
        "pause_after_seconds": 1.0,
        "elevenlabs": {
            "voice_id": "voice-abc",
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "model_id": "eleven_multilingual_v2",
            "speed": 1.0,
        },
        "dialogue_turns": [
            {"speaker": "narrator", "text": "Notice the clinician", "voice_id": None},
        ],
        "source": "cd-authored",
    }
    segment = SegmentManifestSegment.model_validate(
        _base_segment(voice_direction=direction)
    )
    assert segment.voice_direction is not None
    assert segment.voice_direction.schema_version == "voice-direction.v1"
    assert segment.voice_direction.render_strategy == "tts"
    assert segment.voice_direction.delivery_tag == "[thoughtfully]"
    assert segment.voice_direction.pause_before_seconds == 0.5
    assert segment.voice_direction.elevenlabs is not None
    assert segment.voice_direction.elevenlabs.speed == 1.0


def test_voice_direction_defaults_are_minimal() -> None:
    direction = VoiceDirection()
    assert direction.schema_version == "voice-direction.v1"
    assert direction.render_strategy == "tts"
    assert direction.delivery_intent is None
    assert direction.emotional_tone is None
    assert direction.delivery_tag is None
    assert direction.pause_before_seconds is None
    assert direction.dialogue_turns is None
    assert direction.source is None


def test_render_strategy_dialogue_is_schema_tolerated() -> None:
    # dialogue = schema-tolerated deferred stub (test-fenced inert); it validates.
    assert VoiceDirection(render_strategy="dialogue").render_strategy == "dialogue"
    # Any value outside the closed set fails loud.
    with pytest.raises(ValidationError):
        VoiceDirection(render_strategy="single_voice")


# --------------------------------------------------------------------------- #
# Closed-enum triple-layer red-reject (construct / assignment / model_validate).
# Spellings are the control-card enums.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("field", "good", "bad"),
    [
        ("emotional_tone", "concerned", "serious"),  # serious dropped by the card
        ("pace", "faster", "brisk"),  # brisk dropped by the card
        ("energy", "high", "extreme"),
        ("render_strategy", "tts", "single_voice"),
    ],
)
def test_closed_enum_triple_layer_red_reject(field: str, good: str, bad: str) -> None:
    # Surface 1: direct construction.
    with pytest.raises(ValidationError):
        VoiceDirection(**{field: bad})

    # Surface 2: mutation / assignment (validate_assignment=True).
    direction = VoiceDirection(**{field: good})
    with pytest.raises(ValidationError):
        setattr(direction, field, bad)

    # Surface 3: model_validate of an external payload.
    with pytest.raises(ValidationError):
        VoiceDirection.model_validate({field: bad})

    # Good value round-trips on all three.
    assert getattr(VoiceDirection(**{field: good}), field) == good
    assert getattr(VoiceDirection.model_validate({field: good}), field) == good


# --------------------------------------------------------------------------- #
# pause_before_seconds / pause_after_seconds bounds 0 <= x <= 5.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("field", ["pause_before_seconds", "pause_after_seconds"])
@pytest.mark.parametrize("bad", [-0.1, -1.0, 5.1, 9.0])
def test_pause_bounds_reject(field: str, bad: float) -> None:
    with pytest.raises(ValidationError):
        VoiceDirection(**{field: bad})


@pytest.mark.parametrize("field", ["pause_before_seconds", "pause_after_seconds"])
@pytest.mark.parametrize("good", [0.0, 2.5, 5.0])
def test_pause_bounds_accept(field: str, good: float) -> None:
    assert getattr(VoiceDirection(**{field: good}), field) == good


def test_elevenlabs_settings_bounds() -> None:
    # stability / similarity_boost / style are 0..1; speed is 0.7..1.2.
    for field in ("stability", "similarity_boost", "style"):
        with pytest.raises(ValidationError):
            ElevenLabsSettings(**{field: 1.1})
        with pytest.raises(ValidationError):
            ElevenLabsSettings(**{field: -0.1})
    with pytest.raises(ValidationError):
        ElevenLabsSettings(speed=0.6)
    with pytest.raises(ValidationError):
        ElevenLabsSettings(speed=1.3)
    assert ElevenLabsSettings(speed=0.7).speed == 0.7
    assert ElevenLabsSettings(speed=1.2).speed == 1.2


def test_dialogue_turn_text_carries_grounding_docstring() -> None:
    text_field = DialogueTurn.model_fields["text"]
    assert text_field.description is not None
    lowered = text_field.description.lower()
    assert "figure" in lowered
    assert "narration_text" in lowered


# --------------------------------------------------------------------------- #
# Empty-string voice_id is rejected (would short-circuit mapper precedence).
# --------------------------------------------------------------------------- #
def test_empty_voice_id_rejected_on_elevenlabs_settings() -> None:
    with pytest.raises(ValidationError):
        ElevenLabsSettings(voice_id="")
    assert ElevenLabsSettings(voice_id="voice-1").voice_id == "voice-1"


def test_empty_voice_id_rejected_on_dialogue_turn() -> None:
    with pytest.raises(ValidationError):
        DialogueTurn(speaker="a", text="hi", voice_id="")
    assert DialogueTurn(speaker="a", text="hi", voice_id="v1").voice_id == "v1"


# --------------------------------------------------------------------------- #
# Strict mode (extra="forbid") on the nested models.
# --------------------------------------------------------------------------- #
def test_nested_unknown_subkey_rejected() -> None:
    with pytest.raises(ValidationError, match="(?i)extra"):
        VoiceDirection.model_validate({"elevenlabs": {"voice_id": "v1", "bogus": 1}})
    with pytest.raises(ValidationError, match="(?i)extra"):
        VoiceDirection.model_validate(
            {"dialogue_turns": [{"speaker": "a", "text": "t", "bogus": 1}]}
        )
    with pytest.raises(ValidationError, match="(?i)extra"):
        VoiceDirection.model_validate({"unknown_top_level": 1})


# --------------------------------------------------------------------------- #
# delivery_tag: free-text generation-only cue; isolated from narration.
# --------------------------------------------------------------------------- #
def test_delivery_tag_accepts_free_text() -> None:
    # delivery_tag is free-text by design (no substring grounding) — it may carry
    # words/figures absent from narration_text without being rejected, because it
    # never reaches the figure-citation gate (isolation proven below).
    direction = {
        "schema_version": "voice-direction.v1",
        "delivery_tag": "[urgently - emphasize $5 billion]",
    }
    segment = SegmentManifestSegment.model_validate(
        _base_segment(voice_direction=direction)
    )
    assert segment.voice_direction is not None
    assert segment.voice_direction.delivery_tag == "[urgently - emphasize $5 billion]"


def test_delivery_tag_bounded_length() -> None:
    with pytest.raises(ValidationError):
        VoiceDirection(delivery_tag="x" * 121)


# --------------------------------------------------------------------------- #
# Grounding-isolation pin: the figure-citation gate reads ONLY narration_text;
# voice_direction string fields (delivery_tag, delivery_intent) never reach
# citation extraction.
# --------------------------------------------------------------------------- #
def test_figure_gate_ignores_voice_direction_string_fields() -> None:
    from app.specialists.irene.graph import (
        Pass2GroundingError,
        _assert_figure_citations_within_perceived,
    )

    roster = [{"slide_id": "slide-01", "perceived_figures": []}]

    # POSITIVE CONTROL — proves the gate is live (not a no-op): the SAME figure
    # placed IN narration_text (absent from perceived authority) MUST raise.
    with pytest.raises(Pass2GroundingError):
        _assert_figure_citations_within_perceived(
            {
                "narration_script": [
                    {
                        "slide_id": "slide-01",
                        "text": "Revenue grew to $5 billion this year.",
                    }
                ]
            },
            roster,
        )

    # DIFFERENTIAL — narration_text is held CLEAN and IDENTICAL across both
    # cases; ONLY the voice_direction payload varies. Both must pass, proving
    # voice_direction string fields are never in the citation-extraction input.
    clean_text = "Plain words only about the clinician."

    parsed_no_voice_direction = {
        "narration_script": [{"slide_id": "slide-01", "text": clean_text}]
    }
    parsed_with_voice_direction = {
        "narration_script": [
            {
                "slide_id": "slide-01",
                "text": clean_text,  # IDENTICAL to the case above.
                "voice_direction": {
                    "delivery_tag": "[say $5 billion]",
                    "delivery_intent": "say $9 trillion urgently",
                },
            }
        ]
    }
    # Neither raises — the only difference is the voice_direction payload.
    _assert_figure_citations_within_perceived(parsed_no_voice_direction, roster)
    _assert_figure_citations_within_perceived(parsed_with_voice_direction, roster)


def test_figure_gate_source_does_not_reference_voice_direction() -> None:
    from app.specialists.irene.graph import (
        _assert_figure_citations_within_perceived,
    )

    source = inspect.getsource(_assert_figure_citations_within_perceived)
    assert "voice_direction" not in source
    assert "delivery_tag" not in source
