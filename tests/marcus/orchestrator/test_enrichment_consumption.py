"""P5-S2 (Step 6) RED-first floors: the orchestrator-side enrichment projection.

These pin the two deterministic consumers' SHARED projector (Winston A3/A5):
the frozen ``PEDAGOGICAL_ROLE_TO_VOICE`` map, the narration slide→component
matcher (Consumer A), and the Gary deck hint (Consumer B). Anti-tautology: every
behavioural assertion turns on an ENRICHED value the constant path cannot emit
(a sentinel LO statement, a role→pace the map alone produces). Card-absent ⇒
None/empty ⇒ the caller no-ops ⇒ byte-identical (pinned here at the projector).

OFFLINE ONLY: the projector is pure + offline (no LLM/network); these tests
never touch a model or socket.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.pedagogy_annotation import PEDAGOGY_ROLES
from app.marcus.orchestrator import enrichment_consumption as ec

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "p5_workbook_corpus" / "live_enriched_result_card.json"
)


def _load_card() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _narration_component(
    component_id: str, locator: str, role: str, *, teachable: bool = True
) -> tuple[dict[str, Any], dict[str, Any]]:
    """A minimal (typed_component, pedagogy_annotation) pair for a narration slide."""
    comp = {
        "component_id": component_id,
        "source_type": "narration",
        "locator": locator,
        "label": f"{component_id} narration",
        "excerpt": f"{component_id} excerpt",
    }
    ann = {
        "component_id": component_id,
        "pedagogical_role": role,
        "bloom": "understand",
        "lo_refs": [],
        "teachable": teachable,
    }
    return comp, ann


def _card(components: list[dict[str, Any]], annotations: list[dict[str, Any]]) -> dict[str, Any]:
    return {"typed_components": components, "pedagogy_annotations": annotations}


# --------------------------------------------------------------------------- #
# Map shape-pin (Winston A5) — the frozen role→voice table.
# --------------------------------------------------------------------------- #
def test_map_shape_pin() -> None:
    assert ec.PEDAGOGICAL_ROLE_TO_VOICE == {
        "definition": {"emotional_tone": "neutral", "pace": "neutral", "energy": "medium"},
        "motivation": {"emotional_tone": "warm", "pace": "neutral", "energy": "medium"},
        "worked_example": {"emotional_tone": "neutral", "pace": "slower", "energy": "medium"},
        "synthesis": {"emotional_tone": "reflective", "pace": "slower", "energy": "low"},
        "assessment": {"emotional_tone": "neutral", "pace": "slower", "energy": "medium"},
        "practice": {"emotional_tone": "encouraging", "pace": "neutral", "energy": "high"},
    }


# --------------------------------------------------------------------------- #
# A1 — role → voice_direction byte map (one role → exact pace+tone+source).
# --------------------------------------------------------------------------- #
def test_a1_role_to_voice_byte_map() -> None:
    # VALUES only — the annotation leaf auto-stamps source="role-derived" so an
    # explicit source in the seed cannot clobber override precedence.
    assert ec.role_to_voice_direction("synthesis") == {
        "emotional_tone": "reflective",
        "pace": "slower",
        "energy": "low",
    }
    # A role outside the closed map is the no-seed fail-safe.
    assert ec.role_to_voice_direction("other:teaser") is None
    assert ec.role_to_voice_direction(None) is None
    # The returned dict is a COPY — the frozen table can never be mutated.
    seed = ec.role_to_voice_direction("definition")
    assert seed is not None
    seed["pace"] = "faster"
    assert ec.PEDAGOGICAL_ROLE_TO_VOICE["definition"]["pace"] == "neutral"


# --------------------------------------------------------------------------- #
# A2 — TWO-ROLE differential on PACE (the guaranteed dial; Murat).
# --------------------------------------------------------------------------- #
def test_a2_two_role_pace_differential() -> None:
    # Slide 1 narration role=worked_example (pace=slower); Slide 2 role=definition
    # (pace=neutral). The emitted pace DIFFERS by role — the guaranteed signal.
    c1, a1 = _narration_component("src-001-c001", "Slide 1", "worked_example")
    c2, a2 = _narration_component("src-001-c002", "Slide 2", "definition")
    seeds = ec.project_role_derived_voice_by_slide(_card([c1, c2], [a1, a2]))
    assert seeds["1"]["pace"] == "slower"
    assert seeds["2"]["pace"] == "neutral"
    assert seeds["1"]["pace"] != seeds["2"]["pace"]


# --------------------------------------------------------------------------- #
# Narration matcher (Consumer A) on the live-enriched fixture.
# --------------------------------------------------------------------------- #
def test_matcher_on_fixture_role_diverse_slice() -> None:
    seeds = ec.project_role_derived_voice_by_slide(_load_card())
    # Slide 1: unique narration c006 (synthesis) -> slower/reflective.
    assert seeds["1"] == {
        "emotional_tone": "reflective",
        "pace": "slower",
        "energy": "low",
    }
    # Slide 6: unique narration c019 (worked_example) -> slower/neutral.
    assert seeds["6"]["pace"] == "slower"
    assert seeds["6"]["emotional_tone"] == "neutral"
    # Slide 3 has TWO eligible narration components (synthesis + worked_example) ->
    # ambiguous -> NO seed (IR-A2 fail-safe).
    assert "3" not in seeds


# --------------------------------------------------------------------------- #
# IR-A2 fail-safe — ambiguous-multi-match and no-match both yield NO seed.
# --------------------------------------------------------------------------- #
def test_ambiguous_multi_narration_yields_no_seed() -> None:
    c1, a1 = _narration_component("src-001-c001", "Slide 4", "synthesis")
    c2, a2 = _narration_component("src-001-c002", "Slide 4", "worked_example")
    seeds = ec.project_role_derived_voice_by_slide(_card([c1, c2], [a1, a2]))
    assert "4" not in seeds


def test_document_breadcrumb_locator_does_not_match() -> None:
    # A real document-structure component (no trailing "Slide N") never seeds.
    c1, a1 = _narration_component(
        "src-001-c001", "Course 1 > Module 1 > Part 1 > Page 3", "motivation"
    )
    assert ec.project_role_derived_voice_by_slide(_card([c1], [a1])) == {}


def test_non_narration_component_does_not_seed() -> None:
    # A slide-typed (not narration) component on "Slide 1" is ignored for VOICE.
    comp = {
        "component_id": "src-001-c001",
        "source_type": "slide",
        "locator": "Slide 1",
        "label": "x",
        "excerpt": "x",
    }
    ann = {"component_id": "src-001-c001", "pedagogical_role": "definition", "teachable": True}
    assert ec.project_role_derived_voice_by_slide(_card([comp], [ann])) == {}


# --------------------------------------------------------------------------- #
# A5 — card-absent ⇒ empty/None (caller no-ops ⇒ byte-identical).
# --------------------------------------------------------------------------- #
def test_card_absent_yields_empty_seeds_and_none_hint() -> None:
    assert ec.project_role_derived_voice_by_slide(None) == {}
    assert ec.project_role_derived_voice_by_slide({}) == {}
    assert ec.project_deck_enrichment_hint(None) is None
    assert ec.project_deck_enrichment_hint({}) is None


# --------------------------------------------------------------------------- #
# B1 — SENTINEL-bearing deck hint (Murat: mutate an LO statement -> verbatim).
# --------------------------------------------------------------------------- #
def test_b1_deck_hint_carries_lo_sentinel_verbatim() -> None:
    sentinel = "ENRICHED-LO-SENTINEL-quantify-redesignable-administrative-waste"
    card = _load_card()
    card["provisional_los"][0]["statement"] = sentinel
    hint = ec.project_deck_enrichment_hint(card)
    assert hint is not None
    assert sentinel in hint  # verbatim — read off the card, not reconstructed
    # The hint is a single compact token, not a prose reflow of the whole card.
    assert hint.startswith("[g0-enrichment]")


def test_b1_deck_hint_absent_when_no_sentinel() -> None:
    # A card with neither LOs nor roles produces no hint at all.
    empty = {"provisional_los": [], "pedagogy_annotations": []}
    assert ec.project_deck_enrichment_hint(empty) is None


# --------------------------------------------------------------------------- #
# Purity / determinism (Winston A5).
# --------------------------------------------------------------------------- #
def test_projection_is_pure_and_deterministic() -> None:
    card = _load_card()
    a = ec.project_role_derived_voice_by_slide(card)
    b = ec.project_role_derived_voice_by_slide(copy.deepcopy(card))
    assert a == b
    # The input card is not mutated.
    assert card == _load_card()


# --------------------------------------------------------------------------- #
# Deck flag (GARY-A4) — default OFF.
# --------------------------------------------------------------------------- #
def test_deck_flag_default_off(monkeypatch: Any) -> None:
    monkeypatch.delenv(ec.MARCUS_DECK_ENRICHMENT_ACTIVE_ENV, raising=False)
    assert ec.deck_enrichment_active() is False
    monkeypatch.setenv(ec.MARCUS_DECK_ENRICHMENT_ACTIVE_ENV, "1")
    assert ec.deck_enrichment_active() is True


# --------------------------------------------------------------------------- #
# EDGE-2 — the role→voice map is EXHAUSTIVE over the closed PedagogicalRole set.
# (The import-time guard would raise if not; this pins it as a test too.)
# --------------------------------------------------------------------------- #
def test_edge2_map_is_exhaustive_over_pedagogical_role_enum() -> None:
    assert set(ec.PEDAGOGICAL_ROLE_TO_VOICE) == set(PEDAGOGY_ROLES)


# --------------------------------------------------------------------------- #
# EDGE-3 — a teachable=False narration component is NEVER seeded (fail-open).
# --------------------------------------------------------------------------- #
def test_edge3_non_teachable_sole_narration_yields_no_seed() -> None:
    c1, a1 = _narration_component("src-001-c001", "Slide 4", "synthesis", teachable=False)
    assert ec.project_role_derived_voice_by_slide(_card([c1], [a1])) == {}


def test_edge3_teachable_true_still_seeds() -> None:
    c1, a1 = _narration_component("src-001-c001", "Slide 4", "synthesis", teachable=True)
    seeds = ec.project_role_derived_voice_by_slide(_card([c1], [a1]))
    assert seeds["4"]["pace"] == "slower"


# --------------------------------------------------------------------------- #
# EDGE-1 source side — source_slide_ordinals enumerates the card's deck slides.
# --------------------------------------------------------------------------- #
def test_source_slide_ordinals_from_fixture() -> None:
    # The fixture's Slide-N components live on slides 1, 3, 6.
    assert ec.source_slide_ordinals(_load_card()) == [1, 3, 6]
    assert ec.source_slide_ordinals(None) == []
    assert ec.source_slide_ordinals({}) == []


# --------------------------------------------------------------------------- #
# EDGE-5 — LO content (newline / " | " separator) cannot break the hint structure.
# --------------------------------------------------------------------------- #
def test_edge5_deck_hint_sanitizes_newlines_and_pipe_separator() -> None:
    card = {
        "provisional_los": [
            {"objective_id": "lo-x", "statement": "Line one\nLine two | injected boundary"}
        ],
        "pedagogy_annotations": [],
    }
    hint = ec.project_deck_enrichment_hint(card)
    assert hint is not None
    # No raw newline survives; the literal " | " token separator is neutralized so
    # only the structural separators the projector itself inserts remain.
    assert "\n" not in hint
    assert hint.count(" | ") == 0
    assert "Line one Line two / injected boundary" in hint
