"""P5-S2 (Step 6) + Story enhanced-vo.1 (Slice 0): Irene narration consumes the
role-derived seed via a DETERMINISTIC IDENTITY JOIN on ``slide_key``.

These pin the SPECIALIST-SIDE wiring (``graph._attach_voice_direction`` +
``graph._source_slide_key_by_final`` + ``graph._role_derived_seeds_for_deltas``):
the orchestrator threads ``{"by_slide": {slide_key: voice}}`` (keyed by the
SOURCE-deck slide ordinal); the specialist resolves each FINAL segment to its TRUE
source slide via the deterministic lineage (``slide_briefs.source_ref`` +
``lesson_plan.plan_units``), stamps the resulting ``slide_key`` on every delta, and
joins ``by_slide[slide_key]`` by IDENTITY.

The blocking guarantees:
  * A4 — flag-OFF ⇒ byte-identical (the seed table is not even read);
  * A5 — card-absent (no seed table) ⇒ byte-identical to the flag-ON, non-enriched run;
  * A3 — an explicit per-segment override BEATS the role seed (precedence preserved);
  * IR-A1 (FIREWALL, BLOCKING) — ``narration_text`` is byte-identical with/without the
    role seed; the seed only ever lands under ``voice_direction``;
  * IR-A2 — a segment whose SOURCE slide has no seed takes the conservative built-in;
  * enhanced-vo.1 IDENTITY JOIN — a clustered final deck (source↔final ordinal sets
    diverge) now FIRES: N sub-slides of one clustered source slide inherit that
    source slide's seed (replaces the retired EDGE-1 fail-open);
  * enhanced-vo.1 NO-FUZZY-FALLBACK — an unresolvable ``slide_key`` fails LOUD;
  * BLIND-2 — CD ``voice_direction_defaults`` BEATS the role seed.

OFFLINE ONLY: the annotation pass is pure (no LLM/network).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from app.marcus.orchestrator import enrichment_consumption as ec
from app.specialists.irene import graph
from app.specialists.irene.authoring.pass_2_template import VoiceDirection
from app.specialists.irene.authoring.voice_direction_annotation import (
    VoiceDirectionError,
)

NARRATION_FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"


def _parsed() -> dict[str, Any]:
    """A frozen Pass-2 parse with four slide-bound narration deltas (grounded).

    Final slides slide-02 and slide-03 are a CLUSTER: both descend from SOURCE
    slide 2 (slide-03 is the interstitial slide-2-i1). slide-01 -> source 1,
    slide-06 -> source 6.
    """
    return {
        "narration_script": "full script text",
        "segment_manifest_deltas": [
            {"id": "seg-01", "slide_id": "slide-01",
             "narration_text": "Notice the clinician at the workstation.",
             "behavioral_intent": "credible", "visual_references": [{"perception_source": "s1"}]},
            {"id": "seg-02", "slide_id": "slide-02",
             "narration_text": "Costs accumulate quietly.",
             "behavioral_intent": "credible", "visual_references": [{"perception_source": "s2"}]},
            {"id": "seg-03", "slide_id": "slide-03",
             "narration_text": "Consider the redesign surface.",
             "behavioral_intent": "credible", "visual_references": [{"perception_source": "s3"}]},
            {"id": "seg-06", "slide_id": "slide-06",
             "narration_text": "Burnout affects the whole care team.",
             "behavioral_intent": "concerned", "visual_references": [{"perception_source": "s6"}]},
        ],
    }


# The deterministic source->final lineage carrier (rides Irene's Pass-2 envelope).
_LESSON_PLAN: dict[str, Any] = {
    "plan_units": [
        {"unit_id": "slide-1", "cluster_id": "c-u01", "cluster_role": "head"},
        {"unit_id": "slide-2", "cluster_id": "c-u02", "cluster_role": "head"},
        {"unit_id": "slide-2-i1", "cluster_id": "c-u02", "cluster_role": "interstitial",
         "parent_slide_id": "slide-2"},
        {"unit_id": "slide-6", "cluster_id": "c-u06", "cluster_role": "head"},
    ]
}
_SLIDE_BRIEFS: list[dict[str, Any]] = [
    {"slide_id": "slide-01", "source_ref": "slide-1"},
    {"slide_id": "slide-02", "source_ref": "slide-2"},
    {"slide_id": "slide-03", "source_ref": "slide-2-i1"},
    {"slide_id": "slide-06", "source_ref": "slide-6"},
]

# Orchestrator-projected seed table keyed by SOURCE ordinal (the slide_key).
_BY_SLIDE = {
    "1": {"emotional_tone": "reflective", "pace": "slower", "energy": "low"},
    "6": {"emotional_tone": "neutral", "pace": "slower", "energy": "medium"},
}


def _envelope(
    by_slide: dict[str, Any] | None = None,
    *,
    lesson_plan: dict[str, Any] | None = None,
    slide_briefs: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    env: dict[str, Any] = dict(extra)
    if by_slide is not None:
        env["role_derived_voice_by_slide"] = {"by_slide": by_slide}
    env["lesson_plan"] = _LESSON_PLAN if lesson_plan is None else lesson_plan
    env["slide_briefs"] = _SLIDE_BRIEFS if slide_briefs is None else slide_briefs
    return env


def _aligned() -> dict[str, Any]:
    return _envelope(_BY_SLIDE)


@pytest.fixture
def flag_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(NARRATION_FLAG, "1")


@pytest.fixture
def flag_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(NARRATION_FLAG, raising=False)


def _by_id(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {d["id"]: d for d in result["segment_manifest_deltas"]}


# --------------------------------------------------------------------------- #
# A4 — flag OFF ⇒ byte-identical even with a seed table present.
# --------------------------------------------------------------------------- #
def test_a4_flag_off_byte_identical(flag_off: None) -> None:
    parsed = _parsed()
    before = json.dumps(parsed, sort_keys=True)
    result = graph._attach_voice_direction(parsed, _aligned())
    assert json.dumps(result, sort_keys=True) == before
    assert all("voice_direction" not in d for d in result["segment_manifest_deltas"])
    # AC-A6: no slide_key leaks onto the deltas when directed voice is OFF.
    assert all("slide_key" not in d for d in result["segment_manifest_deltas"])


# --------------------------------------------------------------------------- #
# A5 — flag ON but card ABSENT (no seed table) ⇒ identical to the non-enriched run.
# --------------------------------------------------------------------------- #
def test_a5_card_absent_identical_to_non_enriched(flag_on: None) -> None:
    baseline = graph._attach_voice_direction(_parsed(), _envelope(None))
    with_empty = graph._attach_voice_direction(_parsed(), _envelope({}))
    assert json.dumps(baseline, sort_keys=True) == json.dumps(with_empty, sort_keys=True)
    for d in baseline["segment_manifest_deltas"]:
        assert d["voice_direction"]["source"] == "cd-authored"
        # No seed table ⇒ no join ⇒ no slide_key stamped (byte-identical).
        assert "slide_key" not in d


# --------------------------------------------------------------------------- #
# Role seed applied: matched SOURCE slides get the mapped role-derived direction.
# --------------------------------------------------------------------------- #
def test_role_seed_applied_to_matched_segments(flag_on: None) -> None:
    result = graph._attach_voice_direction(_parsed(), _aligned())
    by_id = _by_id(result)
    seg1 = VoiceDirection.model_validate(by_id["seg-01"]["voice_direction"])
    assert seg1.source == "role-derived" and seg1.pace == "slower"
    assert seg1.emotional_tone == "reflective"
    seg6 = VoiceDirection.model_validate(by_id["seg-06"]["voice_direction"])
    assert seg6.source == "role-derived" and seg6.pace == "slower"
    # Source slide 2 (finals slide-02/03) is unseeded ⇒ built-in.
    assert by_id["seg-02"]["voice_direction"]["source"] == "cd-authored"
    assert by_id["seg-03"]["voice_direction"]["source"] == "cd-authored"


# --------------------------------------------------------------------------- #
# IDENTITY JOIN (enhanced-vo.1) — a clustered deck FIRES: both sub-slides of one
# clustered SOURCE slide inherit that source slide's seed (replaces the retired
# EDGE-1 fail-open). slide-02 (head) + slide-03 (interstitial) share source 2.
# --------------------------------------------------------------------------- #
def test_clustered_subslides_inherit_source_seed(flag_on: None) -> None:
    by_slide = {"2": {"emotional_tone": "warm", "pace": "neutral", "energy": "high"}}
    result = graph._attach_voice_direction(_parsed(), _envelope(by_slide))
    by_id = _by_id(result)
    for seg in ("seg-02", "seg-03"):
        assert by_id[seg]["voice_direction"]["source"] == "role-derived"
        assert by_id[seg]["voice_direction"]["emotional_tone"] == "warm"
    # Sources 1 and 6 are unseeded here ⇒ built-in.
    assert by_id["seg-01"]["voice_direction"]["source"] == "cd-authored"
    assert by_id["seg-06"]["voice_direction"]["source"] == "cd-authored"


# --------------------------------------------------------------------------- #
# AC-A1 — slide_key is stamped on EVERY delta of a directed+enriched run.
# --------------------------------------------------------------------------- #
def test_slide_key_stamped_on_every_delta(flag_on: None) -> None:
    result = graph._attach_voice_direction(_parsed(), _aligned())
    by_id = _by_id(result)
    assert by_id["seg-01"]["slide_key"] == "1"
    assert by_id["seg-02"]["slide_key"] == "2"
    assert by_id["seg-03"]["slide_key"] == "2"  # interstitial -> parent source 2
    assert by_id["seg-06"]["slide_key"] == "6"


# --------------------------------------------------------------------------- #
# NO-FUZZY-FALLBACK (enhanced-vo.1) — an unresolvable slide_key fails LOUD.
# --------------------------------------------------------------------------- #
def test_unresolvable_slide_key_fails_loud(flag_on: None) -> None:
    parsed = _parsed()
    parsed["segment_manifest_deltas"].append(
        {"id": "seg-99", "slide_id": "slide-99", "narration_text": "orphan",
         "behavioral_intent": "credible", "visual_references": [{"perception_source": "s99"}]}
    )
    with pytest.raises(VoiceDirectionError):
        graph._attach_voice_direction(parsed, _aligned())


# --------------------------------------------------------------------------- #
# A3 — explicit per-segment override BEATS the role seed.
# --------------------------------------------------------------------------- #
def test_a3_override_beats_role_seed(flag_on: None) -> None:
    payload = _envelope(
        _BY_SLIDE,
        voice_direction_overrides={"seg-01": {"emotional_tone": "urgent", "pace": "faster"}},
    )
    result = graph._attach_voice_direction(_parsed(), payload)
    seg1 = VoiceDirection.model_validate(_by_id(result)["seg-01"]["voice_direction"])
    assert seg1.source == "operator-override"
    assert seg1.emotional_tone == "urgent" and seg1.pace == "faster"


# --------------------------------------------------------------------------- #
# BLIND-2 — CD voice_direction_defaults BEATS the role seed.
# --------------------------------------------------------------------------- #
def test_blind2_defaults_beat_role_seed(flag_on: None) -> None:
    payload = _envelope(_BY_SLIDE, voice_direction_defaults={"pace": "faster"})
    result = graph._attach_voice_direction(_parsed(), payload)
    seg1 = VoiceDirection.model_validate(_by_id(result)["seg-01"]["voice_direction"])
    assert seg1.source == "cd-authored"
    assert seg1.pace == "faster"  # defaults win over the role seed's slower


# --------------------------------------------------------------------------- #
# IR-A1 (FIREWALL, BLOCKING) — narration_text byte-identical with/without the seed.
# --------------------------------------------------------------------------- #
def test_ir_a1_firewall_narration_text_byte_identical(flag_on: None) -> None:
    without = graph._attach_voice_direction(_parsed(), _envelope(None))
    with_seed = graph._attach_voice_direction(_parsed(), _aligned())
    wo, ws = _by_id(without), _by_id(with_seed)
    for sid in ("seg-01", "seg-06"):
        assert wo[sid]["voice_direction"] != ws[sid]["voice_direction"]
        for key in ("narration_text", "behavioral_intent", "visual_references", "slide_id"):
            assert wo[sid][key] == ws[sid][key]
        assert "role-derived" not in ws[sid]["narration_text"]
        assert "slower" not in ws[sid]["narration_text"]


# --------------------------------------------------------------------------- #
# IR-A2 — a SOURCE slide with no seed takes the built-in (never role-derived).
# --------------------------------------------------------------------------- #
def test_ir_a2_unmatched_slide_takes_builtin(flag_on: None) -> None:
    result = graph._attach_voice_direction(_parsed(), _envelope({"1": _BY_SLIDE["1"]}))
    by_id = _by_id(result)
    assert by_id["seg-01"]["voice_direction"]["source"] == "role-derived"
    seg6 = by_id["seg-06"]["voice_direction"]
    assert seg6["source"] == "cd-authored" and seg6["pace"] == "neutral"


# --------------------------------------------------------------------------- #
# The source-lineage map + the identity-join re-key helper (unit level).
# --------------------------------------------------------------------------- #
def test_source_slide_key_by_final_resolves_cluster_lineage() -> None:
    mapping = graph._source_slide_key_by_final(_LESSON_PLAN, _SLIDE_BRIEFS)
    assert mapping == {"slide-01": "1", "slide-02": "2", "slide-03": "2", "slide-06": "6"}


def test_rekey_helper_joins_by_slide_key_identity() -> None:
    deltas = [
        {"id": "seg-01", "slide_id": "slide-01", "slide_key": "1"},
        {"id": "seg-02", "slide_id": "slide-02", "slide_key": "2"},
        {"id": "seg-06", "slide_id": "slide-06", "slide_key": "6"},
    ]
    seeds = graph._role_derived_seeds_for_deltas(deltas, _BY_SLIDE)
    assert set(seeds) == {"seg-01", "seg-06"}  # source 2 unseeded
    assert seeds["seg-01"]["pace"] == "slower"


def test_rekey_helper_none_when_nothing_seeded() -> None:
    deltas = [{"id": "seg-02", "slide_id": "slide-02", "slide_key": "2"}]
    assert graph._role_derived_seeds_for_deltas(deltas, _BY_SLIDE) is None  # source 2 unseeded
    assert graph._role_derived_seeds_for_deltas(deltas, {}) is None
    assert graph._role_derived_seeds_for_deltas(deltas, None) is None
    # A delta with no slide_key contributes no seed (never an ordinal fallback).
    assert graph._role_derived_seeds_for_deltas(
        [{"id": "seg-01", "slide_id": "slide-01"}], _BY_SLIDE
    ) is None


def test_slide_id_ordinal_reads_trailing_run() -> None:
    # The source-slide-id ordinal parser anchors on the TRAILING digit run.
    assert graph._slide_id_ordinal("slide-3") == 3
    assert graph._slide_id_ordinal("c1m1-slide-03") == 3
    assert graph._slide_id_ordinal("module-12-slide-07") == 7


# --------------------------------------------------------------------------- #
# Story concierge-leg1a (AC1) — END-TO-END, REAL producer: a synthesis narration
# slide makes the REAL orchestrator projector emit rhetorical_role on the seed,
# which rides _overlay into VoiceDirection.rhetorical_role — with NO override and
# NO default supplying it (proves de-inertion, not an A/B-probe injection).
# --------------------------------------------------------------------------- #
def _role_card() -> dict[str, Any]:
    """A frozen card whose SOURCE slide 1 = synthesis (-> contrast_emphasis) and
    SOURCE slide 6 = worked_example (-> no rhetorical emission)."""
    return {
        "typed_components": [
            {"component_id": "c1", "source_type": "narration", "locator": "Slide 1",
             "label": "x", "excerpt": "x"},
            {"component_id": "c6", "source_type": "narration", "locator": "Slide 6",
             "label": "x", "excerpt": "x"},
        ],
        "pedagogy_annotations": [
            {"component_id": "c1", "pedagogical_role": "synthesis", "teachable": True},
            {"component_id": "c6", "pedagogical_role": "worked_example", "teachable": True},
        ],
    }


def test_leg1a_real_producer_emits_rhetorical_role_end_to_end(flag_on: None) -> None:
    by_slide = ec.project_role_derived_voice_by_slide(_role_card())
    # NO voice_direction_overrides / voice_direction_defaults supply rhetorical_role.
    result = graph._attach_voice_direction(_parsed(), _envelope(by_slide))
    by_id = _by_id(result)
    seg1 = VoiceDirection.model_validate(by_id["seg-01"]["voice_direction"])
    assert seg1.rhetorical_role == "contrast_emphasis"
    # Sourced from the role-derived seed, not an override.
    assert seg1.source == "role-derived"
    # A SOURCE slide mapped to no rhetorical role emits NO rhetorical_role (its
    # tone/pace seed still applies).
    seg6 = VoiceDirection.model_validate(by_id["seg-06"]["voice_direction"])
    assert seg6.rhetorical_role is None
    assert seg6.source == "role-derived"


# --------------------------------------------------------------------------- #
# Story concierge-leg1a (AC6) — flag OFF ⇒ byte-identical even with a
# rhetorical-bearing seed table present (the seed table is not even read; no
# rhetorical_role is emitted into any byte-changing path).
# --------------------------------------------------------------------------- #
def test_leg1a_flag_off_byte_identical_with_rhetorical_seed(flag_off: None) -> None:
    by_slide = {
        "1": {"emotional_tone": "reflective", "pace": "slower", "energy": "low",
              "rhetorical_role": "contrast_emphasis"},
    }
    parsed = _parsed()
    before = json.dumps(parsed, sort_keys=True)
    result = graph._attach_voice_direction(parsed, _envelope(by_slide))
    assert json.dumps(result, sort_keys=True) == before
    assert all("voice_direction" not in d for d in result["segment_manifest_deltas"])
