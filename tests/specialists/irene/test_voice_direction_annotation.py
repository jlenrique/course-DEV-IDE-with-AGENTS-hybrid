"""Step-2 directed-voice annotation-pass pins (P5 directed-voice arc, 2026-06-27).

Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§F (IR-1, IR-2, MUR-2) + the implementation control cards (Card 1 emission,
Card 4 RED-first).

The headline guarantee (IR-1 / MUR-2): `voice_direction` is delivery METADATA
layered onto an ALREADY-FROZEN, figure-gate-passed manifest by a SEPARATE,
PURE, deterministic annotation pass. It must NEVER mutate any grounded field
(`narration_text` / `text` / `visual_references` / `behavioral_intent`). This
module pins that the pure pass:

- leaves every grounded field byte-identical pre/post (MUR-2);
- attaches a valid `voice_direction` per segment with the documented
  precedence (override > defaults > built-in) and `source` provenance;
- is deterministic (same input -> same output; no LLM, clock, randomness);
- is backward-compatible (no direction inputs still yields valid manifests).
"""

from __future__ import annotations

import json

import pytest

from app.specialists.irene.authoring.pass_2_template import VoiceDirection
from app.specialists.irene.authoring.voice_direction_annotation import (
    VoiceDirectionError,
    annotate_segments_with_voice_direction,
)


def _grounded_segments() -> list[dict[str, object]]:
    """Two frozen segment-manifest deltas carrying grounded fields only."""
    return [
        {
            "id": "seg-1",
            "slide_id": "s1",
            "narration_text": "Notice the clinician at the workstation.",
            "behavioral_intent": "credible",
            "visual_references": [{"perception_source": "s1"}],
        },
        {
            "id": "seg-2",
            "slide_id": "s2",
            "narration_text": "Burnout affects the whole care team.",
            "behavioral_intent": "concerned",
            "visual_references": [{"perception_source": "s2"}],
        },
    ]


def _grounded_subset(segment: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in segment.items() if key != "voice_direction"}


# --------------------------------------------------------------------------- #
# MUR-2 — grounding non-regression (the headline).
# --------------------------------------------------------------------------- #
def test_annotation_leaves_grounded_fields_byte_identical() -> None:
    segments = _grounded_segments()
    before = json.dumps(segments, sort_keys=True)

    result = annotate_segments_with_voice_direction(
        segments,
        defaults={"emotional_tone": "warm"},
        per_segment_overrides={"seg-2": {"emotional_tone": "concerned"}},
    )

    # Input list is NOT mutated (pure pass — read-only input).
    assert json.dumps(segments, sort_keys=True) == before

    # Every grounded field is byte-identical pre/post for every segment.
    for original, annotated in zip(segments, result, strict=True):
        assert json.dumps(_grounded_subset(annotated), sort_keys=True) == json.dumps(
            original, sort_keys=True
        )


def test_mutating_direction_never_changes_grounded_fields() -> None:
    # Two different direction inputs must produce IDENTICAL grounded subsets;
    # only the voice_direction payload may differ.
    segments = _grounded_segments()
    neutral = annotate_segments_with_voice_direction(segments)
    directed = annotate_segments_with_voice_direction(
        segments,
        defaults={"emotional_tone": "reflective", "pace": "slower"},
    )
    for a, b in zip(neutral, directed, strict=True):
        assert json.dumps(_grounded_subset(a), sort_keys=True) == json.dumps(
            _grounded_subset(b), sort_keys=True
        )
        # ...but the direction payloads DID differ (proves the pass is live).
    assert neutral[0]["voice_direction"] != directed[0]["voice_direction"]


# --------------------------------------------------------------------------- #
# Direction attached + valid contract.
# --------------------------------------------------------------------------- #
def test_each_segment_carries_a_valid_voice_direction() -> None:
    result = annotate_segments_with_voice_direction(_grounded_segments())
    for segment in result:
        assert "voice_direction" in segment
        # Round-trips through the frozen Step-1 contract.
        direction = VoiceDirection.model_validate(segment["voice_direction"])
        assert direction.schema_version == "voice-direction.v1"
        assert direction.render_strategy == "tts"


def test_built_in_default_is_conservative() -> None:
    result = annotate_segments_with_voice_direction(_grounded_segments())
    direction = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert direction.emotional_tone == "neutral"
    assert direction.pace == "neutral"
    assert direction.energy == "medium"
    assert direction.render_strategy == "tts"
    assert direction.source == "cd-authored"


# --------------------------------------------------------------------------- #
# Precedence: override > defaults > built-in.
# --------------------------------------------------------------------------- #
def test_precedence_override_beats_defaults_beats_builtin() -> None:
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        # pace=slower (NON-neutral) so the defaults tier is distinguishable from
        # the built-in default (which is pace=neutral).
        defaults={"emotional_tone": "warm", "pace": "slower"},
        per_segment_overrides={"seg-1": {"emotional_tone": "concerned"}},
    )
    by_id = {s["id"]: s["voice_direction"] for s in result}

    # seg-1 has an explicit override -> override wins on emotional_tone,
    # defaults still supply pace (slower != built-in neutral), built-in energy.
    seg1 = VoiceDirection.model_validate(by_id["seg-1"])
    assert seg1.emotional_tone == "concerned"  # override
    assert seg1.pace == "slower"  # defaults (distinguishable from built-in)
    assert seg1.energy == "medium"  # built-in

    # seg-2 has no override -> defaults win, built-in fills the rest.
    seg2 = VoiceDirection.model_validate(by_id["seg-2"])
    assert seg2.emotional_tone == "warm"  # defaults
    assert seg2.pace == "slower"  # defaults
    assert seg2.energy == "medium"  # built-in


# --------------------------------------------------------------------------- #
# source provenance stamping.
# --------------------------------------------------------------------------- #
def test_source_provenance_stamped_correctly() -> None:
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        defaults={"emotional_tone": "warm"},
        per_segment_overrides={"seg-1": {"emotional_tone": "concerned"}},
    )
    by_id = {s["id"]: VoiceDirection.model_validate(s["voice_direction"]) for s in result}
    assert by_id["seg-1"].source == "operator-override"
    assert by_id["seg-2"].source == "cd-authored"


def test_source_builtin_only_is_cd_authored() -> None:
    result = annotate_segments_with_voice_direction(_grounded_segments())
    for segment in result:
        assert VoiceDirection.model_validate(segment["voice_direction"]).source == (
            "cd-authored"
        )


def test_role_derived_hook_seeds_direction_without_enrichment_wiring() -> None:
    # Step-6 hook: role_derived_seeds is accepted now but is NOT wired to G0
    # enrichment in graph.py yet. When a seed exists (and there is no override or
    # CD default), the direction is stamped role-derived and uses the seed value.
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        role_derived_seeds={"seg-1": {"emotional_tone": "encouraging"}},
    )
    by_id = {s["id"]: VoiceDirection.model_validate(s["voice_direction"]) for s in result}
    assert by_id["seg-1"].source == "role-derived"
    assert by_id["seg-1"].emotional_tone == "encouraging"
    # seg-2 (no seed) falls back to the conservative built-in.
    assert by_id["seg-2"].source == "cd-authored"
    assert by_id["seg-2"].emotional_tone == "neutral"


def test_override_beats_role_derived_seed() -> None:
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        per_segment_overrides={"seg-1": {"emotional_tone": "concerned"}},
        role_derived_seeds={"seg-1": {"emotional_tone": "encouraging"}},
    )
    seg1 = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert seg1.source == "operator-override"
    assert seg1.emotional_tone == "concerned"


# --------------------------------------------------------------------------- #
# Determinism.
# --------------------------------------------------------------------------- #
def test_determinism_same_input_same_output() -> None:
    kwargs = dict(
        defaults={"emotional_tone": "reflective", "pace": "slower"},
        per_segment_overrides={"seg-2": {"energy": "low"}},
    )
    first = annotate_segments_with_voice_direction(_grounded_segments(), **kwargs)
    second = annotate_segments_with_voice_direction(_grounded_segments(), **kwargs)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


# --------------------------------------------------------------------------- #
# Backward-compat: no direction inputs still validates (legacy path).
# --------------------------------------------------------------------------- #
def test_no_direction_inputs_still_attaches_valid_default() -> None:
    result = annotate_segments_with_voice_direction(_grounded_segments())
    assert len(result) == 2
    for segment in result:
        VoiceDirection.model_validate(segment["voice_direction"])


def test_segment_without_id_gets_default_direction() -> None:
    # An id-less delta cannot match a per-segment override; it still receives the
    # defaults+built-in direction (no crash). The override here is keyed to a REAL
    # segment id (seg-2) so it does NOT trip the unmatched-key guard.
    segments = [
        {"slide_id": "s1", "narration_text": "Text.", "visual_references": []},
        {"id": "seg-2", "slide_id": "s2", "narration_text": "T2.", "visual_references": []},
    ]
    result = annotate_segments_with_voice_direction(
        segments,
        defaults={"emotional_tone": "warm"},
        per_segment_overrides={"seg-2": {"emotional_tone": "concerned"}},
    )
    idless = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert idless.emotional_tone == "warm"  # defaults (no id -> no override)
    assert idless.source == "cd-authored"
    seg2 = VoiceDirection.model_validate(result[1]["voice_direction"])
    assert seg2.emotional_tone == "concerned"  # override reached its real id
    assert seg2.source == "operator-override"


def test_full_palette_values_round_trip() -> None:
    # Audition-rubric §4 palette: neutral baseline / reflective / warm / concerned.
    palette = {
        "seg-1": {"emotional_tone": "neutral", "pace": "neutral", "energy": "medium"},
        "seg-2": {"emotional_tone": "reflective", "pace": "slower", "energy": "low"},
    }
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        per_segment_overrides=palette,
    )
    by_id = {s["id"]: VoiceDirection.model_validate(s["voice_direction"]) for s in result}
    assert by_id["seg-1"].emotional_tone == "neutral"
    assert by_id["seg-2"].emotional_tone == "reflective"
    assert by_id["seg-2"].pace == "slower"
    assert by_id["seg-2"].energy == "low"


# --------------------------------------------------------------------------- #
# Remediation 1 — provenance reflects VALUE-contribution, not key-presence.
# `source` is the audit field UDAC trusts: a tier may only claim it if it
# actually drove a non-None value into the merged direction.
# --------------------------------------------------------------------------- #
def test_empty_override_does_not_claim_operator_override() -> None:
    # An empty {} override contributes nothing -> it must NOT stamp
    # operator-override; defaults (which DO contribute) own the provenance.
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        defaults={"emotional_tone": "warm"},
        per_segment_overrides={"seg-1": {}},
    )
    seg1 = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert seg1.source == "cd-authored"  # NOT operator-override
    assert seg1.emotional_tone == "warm"  # defaults drove the value


def test_all_none_override_does_not_claim_operator_override() -> None:
    # An all-None override ({"pace": None}) contributes nothing.
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        defaults={"emotional_tone": "warm"},
        per_segment_overrides={"seg-1": {"pace": None, "energy": None}},
    )
    seg1 = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert seg1.source == "cd-authored"


def test_all_none_defaults_does_not_claim_cd_authored() -> None:
    # All-None defaults contribute nothing; a contributing role-seed wins source.
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        defaults={"emotional_tone": None},
        role_derived_seeds={"seg-1": {"emotional_tone": "encouraging"}},
    )
    seg1 = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert seg1.source == "role-derived"
    assert seg1.emotional_tone == "encouraging"


def test_contributing_tier_is_stamped_when_override_has_real_value() -> None:
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        defaults={"emotional_tone": "warm"},
        per_segment_overrides={"seg-1": {"energy": "high"}},
    )
    seg1 = VoiceDirection.model_validate(result[0]["voice_direction"])
    assert seg1.source == "operator-override"  # override DID contribute
    assert seg1.energy == "high"


# --------------------------------------------------------------------------- #
# Remediation 7b — an explicit `source` carried in a layer overrides the
# computed provenance (operator may stamp provenance deliberately).
# --------------------------------------------------------------------------- #
def test_explicit_source_in_layer_overrides_computed() -> None:
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        per_segment_overrides={
            "seg-1": {"emotional_tone": "warm", "source": "role-derived"},
        },
    )
    seg1 = VoiceDirection.model_validate(result[0]["voice_direction"])
    # Computed would be operator-override; the explicit layer source wins.
    assert seg1.source == "role-derived"


# --------------------------------------------------------------------------- #
# Remediation 2 — fail-loud WITH CONTEXT on a bad override/defaults value.
# The tagged error names the segment id + the offending key and flags the
# DELIVERY-METADATA layer (not the LLM script) as at fault.
# --------------------------------------------------------------------------- #
def test_invalid_enum_value_raises_tagged_error_with_segment_id() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            per_segment_overrides={"seg-1": {"emotional_tone": "exuberant"}},
        )
    message = str(exc.value)
    assert "seg-1" in message
    assert "emotional_tone" in message
    assert exc.value.tag == "irene.voice_direction.invalid-direction"


def test_unknown_key_in_override_raises() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            per_segment_overrides={"seg-1": {"bogus_field": "x"}},
        )
    assert "seg-1" in str(exc.value)


def test_wrong_type_in_override_raises() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            per_segment_overrides={
                "seg-1": {"elevenlabs": {"stability": "not-a-float"}},
            },
        )
    assert "seg-1" in str(exc.value)


def test_empty_voice_id_in_override_raises() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            per_segment_overrides={"seg-1": {"elevenlabs": {"voice_id": ""}}},
        )
    assert "seg-1" in str(exc.value)


def test_invalid_defaults_value_raises_for_each_affected_segment() -> None:
    # A bad CD default surfaces as a tagged error too (delivery layer at fault).
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            defaults={"pace": "warp-speed"},
        )
    assert exc.value.tag == "irene.voice_direction.invalid-direction"
    assert "pace" in str(exc.value)


# --------------------------------------------------------------------------- #
# Remediation 3 — fail-loud on an override/seed keyed to a NON-EXISTENT segment
# id (operator typo -> lost intent). UDAC no-silent-fallback.
# --------------------------------------------------------------------------- #
def test_unmatched_override_key_raises() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            per_segment_overrides={"seg-99": {"emotional_tone": "warm"}},
        )
    message = str(exc.value)
    assert "seg-99" in message
    assert exc.value.tag == "irene.voice_direction.unmatched-segment-id"


def test_unmatched_seed_key_raises() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(
            _grounded_segments(),
            role_derived_seeds={"ghost-seg": {"emotional_tone": "warm"}},
        )
    assert "ghost-seg" in str(exc.value)


def test_all_keys_matched_does_not_raise() -> None:
    result = annotate_segments_with_voice_direction(
        _grounded_segments(),
        per_segment_overrides={"seg-1": {"emotional_tone": "warm"}},
        role_derived_seeds={"seg-2": {"emotional_tone": "reflective"}},
    )
    assert len(result) == 2


# --------------------------------------------------------------------------- #
# Remediation 4 — overrides/seeds match the segment `id` ONLY (never slide_id).
# A key that collides with some segment's slide_id must NOT mis-apply across
# id-spaces.
# --------------------------------------------------------------------------- #
def test_override_matches_id_not_slide_id() -> None:
    # seg A: id=x, slide_id=y ; seg B: id=y, slide_id=z. An override keyed "y"
    # must apply to B (whose id is y) and NEVER to A (whose slide_id is y).
    segments = [
        {"id": "x", "slide_id": "y", "narration_text": "A.", "visual_references": []},
        {"id": "y", "slide_id": "z", "narration_text": "B.", "visual_references": []},
    ]
    result = annotate_segments_with_voice_direction(
        segments,
        per_segment_overrides={"y": {"emotional_tone": "concerned"}},
    )
    seg_a = VoiceDirection.model_validate(result[0]["voice_direction"])
    seg_b = VoiceDirection.model_validate(result[1]["voice_direction"])
    # A (slide_id == "y") did NOT pick up the override -> built-in neutral.
    assert seg_a.emotional_tone == "neutral"
    assert seg_a.source == "cd-authored"
    # B (id == "y") did.
    assert seg_b.emotional_tone == "concerned"
    assert seg_b.source == "operator-override"


# --------------------------------------------------------------------------- #
# Remediation 6 — the pure leaf is robust to a non-dict delta (clear error, not
# a bare AttributeError).
# --------------------------------------------------------------------------- #
def test_non_dict_segment_raises_clear_error() -> None:
    with pytest.raises(VoiceDirectionError) as exc:
        annotate_segments_with_voice_direction(["not-a-dict"])  # type: ignore[list-item]
    assert exc.value.tag == "irene.voice_direction.non-dict-segment"
