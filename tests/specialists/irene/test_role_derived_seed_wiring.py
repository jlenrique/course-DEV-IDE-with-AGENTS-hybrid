"""P5-S2 (Step 6) RED-first floors: Irene narration consumes the role-derived seed.

These pin the SPECIALIST-SIDE wiring (``graph._attach_voice_direction`` +
``graph._role_derived_seeds_for_deltas``): the orchestrator threads
``{"by_slide": {ordinal: voice}, "source_slide_ordinals": [...]}``; the specialist
aligns it to THIS pass's frozen segment deltas — GUARDED by the EDGE-1 source↔final
ordinal-space divergence check — then threads it into the pure annotation leaf.

The blocking guarantees:
  * A4 — flag-OFF ⇒ byte-identical (the seed table is not even read);
  * A5 — card-absent (no seed table) ⇒ byte-identical to the flag-ON, non-enriched run;
  * A3 — an explicit per-segment override BEATS the role seed (precedence preserved);
  * IR-A1 (FIREWALL, BLOCKING) — ``narration_text`` is byte-identical with/without the
    role seed; the seed only ever lands under ``voice_direction``;
  * IR-A2 — a segment whose slide has no seed takes the conservative built-in default;
  * EDGE-1 — a clustered / dropped / shifted final deck (source↔final ordinal sets
    diverge) ⇒ NO role-derived seeds applied (FAIL OPEN to neutral), never a mis-seed;
  * EDGE-4 — a numeric-PREFIXED slide_id (``c1m1-slide-06``) keys on the TRAILING ordinal;
  * BLIND-2 — CD ``voice_direction_defaults`` BEATS the role seed.

OFFLINE ONLY: the annotation pass is pure (no LLM/network).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from app.specialists.irene import graph
from app.specialists.irene.authoring.pass_2_template import VoiceDirection

NARRATION_FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"


def _parsed() -> dict[str, Any]:
    """A frozen Pass-2 parse with four slide-bound narration deltas (grounded)."""
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


# Orchestrator-projected seed table (VALUES only — the leaf stamps source).
_BY_SLIDE = {
    "1": {"emotional_tone": "reflective", "pace": "slower", "energy": "low"},
    "6": {"emotional_tone": "neutral", "pace": "slower", "energy": "medium"},
}
# The four deltas above span source slide ordinals {1, 2, 3, 6}; an ALIGNED run
# threads exactly that set so the EDGE-1 divergence guard passes.
_SOURCE_ORDS = [1, 2, 3, 6]


def _threaded(by_slide: dict[str, Any], source_ordinals: list[int]) -> dict[str, Any]:
    return {"by_slide": by_slide, "source_slide_ordinals": source_ordinals}


def _aligned() -> dict[str, Any]:
    return {"role_derived_voice_by_slide": _threaded(_BY_SLIDE, _SOURCE_ORDS)}


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


# --------------------------------------------------------------------------- #
# A5 — flag ON but card ABSENT (no seed table) ⇒ identical to the non-enriched run.
# --------------------------------------------------------------------------- #
def test_a5_card_absent_identical_to_non_enriched(flag_on: None) -> None:
    baseline = graph._attach_voice_direction(_parsed(), {})
    with_empty = graph._attach_voice_direction(
        _parsed(), {"role_derived_voice_by_slide": _threaded({}, [])}
    )
    assert json.dumps(baseline, sort_keys=True) == json.dumps(with_empty, sort_keys=True)
    for d in baseline["segment_manifest_deltas"]:
        assert d["voice_direction"]["source"] == "cd-authored"


# --------------------------------------------------------------------------- #
# Role seed applied: matched slides get the mapped role-derived direction.
# --------------------------------------------------------------------------- #
def test_role_seed_applied_to_matched_segments(flag_on: None) -> None:
    result = graph._attach_voice_direction(_parsed(), _aligned())
    by_id = _by_id(result)
    seg1 = VoiceDirection.model_validate(by_id["seg-01"]["voice_direction"])
    assert seg1.source == "role-derived" and seg1.pace == "slower"
    assert seg1.emotional_tone == "reflective"
    seg6 = VoiceDirection.model_validate(by_id["seg-06"]["voice_direction"])
    assert seg6.source == "role-derived" and seg6.pace == "slower"
    # Unseeded slides (2, 3) take the built-in.
    assert by_id["seg-02"]["voice_direction"]["source"] == "cd-authored"


# --------------------------------------------------------------------------- #
# A3 — explicit per-segment override BEATS the role seed.
# --------------------------------------------------------------------------- #
def test_a3_override_beats_role_seed(flag_on: None) -> None:
    payload = {
        **_aligned(),
        "voice_direction_overrides": {"seg-01": {"emotional_tone": "urgent", "pace": "faster"}},
    }
    result = graph._attach_voice_direction(_parsed(), payload)
    seg1 = VoiceDirection.model_validate(_by_id(result)["seg-01"]["voice_direction"])
    assert seg1.source == "operator-override"
    assert seg1.emotional_tone == "urgent" and seg1.pace == "faster"


# --------------------------------------------------------------------------- #
# BLIND-2 — CD voice_direction_defaults BEATS the role seed.
# --------------------------------------------------------------------------- #
def test_blind2_defaults_beat_role_seed(flag_on: None) -> None:
    payload = {**_aligned(), "voice_direction_defaults": {"pace": "faster"}}
    result = graph._attach_voice_direction(_parsed(), payload)
    seg1 = VoiceDirection.model_validate(_by_id(result)["seg-01"]["voice_direction"])
    assert seg1.source == "cd-authored"
    assert seg1.pace == "faster"  # defaults win over the role seed's slower


# --------------------------------------------------------------------------- #
# IR-A1 (FIREWALL, BLOCKING) — narration_text byte-identical with/without the seed.
# --------------------------------------------------------------------------- #
def test_ir_a1_firewall_narration_text_byte_identical(flag_on: None) -> None:
    without = graph._attach_voice_direction(_parsed(), {})
    with_seed = graph._attach_voice_direction(_parsed(), _aligned())
    wo, ws = _by_id(without), _by_id(with_seed)
    for sid in ("seg-01", "seg-06"):
        assert wo[sid]["voice_direction"] != ws[sid]["voice_direction"]
        for key in ("narration_text", "behavioral_intent", "visual_references", "slide_id"):
            assert wo[sid][key] == ws[sid][key]
        assert "role-derived" not in ws[sid]["narration_text"]
        assert "slower" not in ws[sid]["narration_text"]


# --------------------------------------------------------------------------- #
# IR-A2 — a slide with no seed takes the built-in default (never role-derived).
# --------------------------------------------------------------------------- #
def test_ir_a2_unmatched_slide_takes_builtin(flag_on: None) -> None:
    result = graph._attach_voice_direction(
        _parsed(), {"role_derived_voice_by_slide": _threaded({"1": _BY_SLIDE["1"]}, _SOURCE_ORDS)}
    )
    by_id = _by_id(result)
    assert by_id["seg-01"]["voice_direction"]["source"] == "role-derived"
    seg6 = by_id["seg-06"]["voice_direction"]
    assert seg6["source"] == "cd-authored" and seg6["pace"] == "neutral"


# --------------------------------------------------------------------------- #
# EDGE-1 — divergence guard: clustered / shifted final deck ⇒ FAIL OPEN.
# --------------------------------------------------------------------------- #
def test_edge1_clustered_deck_fails_open(flag_on: None) -> None:
    # Pass-1 clustering renumbered a 4-source-slide deck into SEVEN final slides.
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": [
            {"id": f"seg-0{n}", "slide_id": f"slide-0{n}",
             "narration_text": f"Slide {n}.", "behavioral_intent": "x", "visual_references": []}
            for n in range(1, 8)
        ],
    }
    result = graph._attach_voice_direction(parsed, _aligned())  # source {1,2,3,6} != {1..7}
    # FAIL OPEN: no role-derived source anywhere — every segment is the built-in.
    for d in result["segment_manifest_deltas"]:
        assert d["voice_direction"]["source"] == "cd-authored"


def test_edge1_shifted_ordinal_fails_open(flag_on: None) -> None:
    # A drop+renumber shifts source slide 6 to final slide 5: same count, different set.
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": [
            {"id": "seg-01", "slide_id": "slide-01", "narration_text": "a",
             "behavioral_intent": "x", "visual_references": []},
            {"id": "seg-02", "slide_id": "slide-02", "narration_text": "b",
             "behavioral_intent": "x", "visual_references": []},
            {"id": "seg-03", "slide_id": "slide-03", "narration_text": "c",
             "behavioral_intent": "x", "visual_references": []},
            {"id": "seg-05", "slide_id": "slide-05", "narration_text": "d",
             "behavioral_intent": "x", "visual_references": []},
        ],
    }
    result = graph._attach_voice_direction(parsed, _aligned())  # {1,2,3,6} != {1,2,3,5}
    for d in result["segment_manifest_deltas"]:
        assert d["voice_direction"]["source"] == "cd-authored"


def test_edge1_aligned_deck_applies_seeds(flag_on: None) -> None:
    # The aligned base case still works (the guard does not over-fire).
    result = graph._attach_voice_direction(_parsed(), _aligned())
    assert _by_id(result)["seg-01"]["voice_direction"]["source"] == "role-derived"


# --------------------------------------------------------------------------- #
# The re-key helper itself (guard + EDGE-4 anchored trailing parser).
# --------------------------------------------------------------------------- #
def test_rekey_helper_applies_on_alignment() -> None:
    deltas = [
        {"id": "seg-01", "slide_id": "slide-01"},
        {"id": "seg-06", "slide_id": "slide-06"},
    ]
    seeds = graph._role_derived_seeds_for_deltas(deltas, _threaded(_BY_SLIDE, [1, 6]))
    assert set(seeds) == {"seg-01", "seg-06"}
    assert seeds["seg-01"]["pace"] == "slower"


def test_rekey_helper_fails_open_on_divergence() -> None:
    deltas = [
        {"id": "seg-01", "slide_id": "slide-01"},
        {"id": "seg-06", "slide_id": "slide-06"},
    ]
    # source ords {1,2,3,6} but the deck only has {1,6} -> divergence -> None.
    assert graph._role_derived_seeds_for_deltas(deltas, _threaded(_BY_SLIDE, [1, 2, 3, 6])) is None
    # Malformed / missing pieces -> None (byte-identical).
    assert graph._role_derived_seeds_for_deltas(deltas, None) is None
    assert graph._role_derived_seeds_for_deltas(deltas, {}) is None
    assert graph._role_derived_seeds_for_deltas(deltas, {"by_slide": {}}) is None
    assert graph._role_derived_seeds_for_deltas(deltas, {"by_slide": _BY_SLIDE}) is None  # no ords


def test_edge4_numeric_prefixed_slide_id_keys_on_trailing_ordinal() -> None:
    # A numeric-PREFIXED slide_id must read the TRAILING ordinal, not the prefix.
    deltas = [
        {"id": "seg-01", "slide_id": "c1m1-slide-01"},
        {"id": "seg-06", "slide_id": "module-1-slide-06"},
    ]
    seeds = graph._role_derived_seeds_for_deltas(deltas, _threaded(_BY_SLIDE, [1, 6]))
    assert set(seeds) == {"seg-01", "seg-06"}
    assert seeds["seg-06"]["pace"] == "slower"
    # Helper-level: trailing digit run wins.
    assert graph._slide_id_ordinal("c1m1-slide-03") == 3
    assert graph._slide_id_ordinal("module-12-slide-07") == 7
