"""Deterministic bijective containment matching for Gamma exports.

Storyboard-correctness fix (party-ratified 2026-06-18). Pins the matcher that
replaced positional page->slide_id mapping. The central pin is the real
cycle-6 (f8da20ae) corpus: a cover-injected + topic-merged + title-rephrased
export must bind each brief to its CORRECT page BY CONTENT IDENTITY — the bug
was trusting position, so every assertion here is content-keyed, and reverting
to positional OR to naive exact-match must turn these red (kill-the-mutant).
"""

from __future__ import annotations

import random

from skills.gamma_api_mastery.scripts.gamma_operations import (
    match_pages_to_slots,
    normalize_title,
    title_from_export_stem,
)

# Real cycle-6 brief titles (carry the "— objective" tail the matcher strips).
F8_BRIEFS: list[tuple[str, str]] = [
    ("slide-01", "The Economic & Structural Reality"),
    ("slide-02", "The Human Cost: System Waste & Burnout"),
    ("slide-03", "The Knowledge Explosion & New Technologies"),
    ("slide-04", "The Consumer Shift & The Digital Front Door"),
    ("slide-05", "The Leadership Gap"),
    ("slide-06", "Case for Change Summary & Knowledge Check"),
]
# Real cycle-6 Gamma export stems: cover first, Leadership+Summary merged.
F8_STEMS = [
    "1_The-Case-for-Physician-Leadership",
    "2_The-Economic-and-Structural-Reality",
    "3_The-Human-Cost-Waste-and-Burnout",
    "4_The-Knowledge-Explosion-and-New-Technologies",
    "5_The-Consumer-Shift-and-The-Digital-Front-Door",
    "6_The-Leadership-Gap-and-the-Case-for-Change",
]


def _pages(stems: list[str]) -> list[dict]:
    return [
        {"page_index": i + 1, "title": title_from_export_stem(s), "path": f"/exp/{s}.png"}
        for i, s in enumerate(stems)
    ]


def test_f8da20ae_binds_by_title_not_position() -> None:
    """KILL-THE-MUTANT central pin. Content-keyed: a positional revert puts the
    cover on slide-01 (red); an exact-match revert fails-loud on slide-02
    ("System" dropped) and slide-05 (merge appended) (red). Only deterministic
    containment binds all five correctly + drops the cover + leaves the
    merged-away Summary unmatched."""
    r = match_pages_to_slots(pages=_pages(F8_STEMS), expected_slots=F8_BRIEFS)
    assert r.matched["slide-01"].endswith("The-Economic-and-Structural-Reality.png")
    assert r.matched["slide-02"].endswith("The-Human-Cost-Waste-and-Burnout.png")  # page⊆brief
    assert r.matched["slide-03"].endswith("The-Knowledge-Explosion-and-New-Technologies.png")
    assert r.matched["slide-04"].endswith("The-Consumer-Shift-and-The-Digital-Front-Door.png")
    # brief⊆page (Gamma appended merge text):
    assert r.matched["slide-05"].endswith("The-Leadership-Gap-and-the-Case-for-Change.png")
    assert r.unmatched_keys == ["slide-06"]  # merged away → no page
    assert [d["page_index"] for d in r.dropped_pages] == [1]  # cover, leading-dropped
    assert r.dropped_pages[0]["reason"] == "unmatched-leading-page"
    assert r.unmatched_pages == []
    assert r.ambiguous == []


def test_order_independent() -> None:
    """Shuffled page order yields identical bindings — proves no greedy/first-edge
    dependence (Amelia/Murat)."""
    base = match_pages_to_slots(pages=_pages(F8_STEMS), expected_slots=F8_BRIEFS)
    shuffled = _pages(F8_STEMS)
    random.Random(7).shuffle(shuffled)
    r = match_pages_to_slots(pages=shuffled, expected_slots=F8_BRIEFS)
    assert r.matched == base.matched
    assert sorted(r.unmatched_keys) == sorted(base.unmatched_keys)


def test_ambiguous_subset_binds_neither() -> None:
    """Murat positive adversarial: a brief that is a token-subset of TWO pages
    must raise ambiguity and bind NEITHER — never greedy-pick."""
    pages = _pages([
        "1_The-Leadership-Gap-and-the-Case-for-Change",
        "2_Closing-the-Leadership-Gap-Today",
    ])
    r = match_pages_to_slots(pages=pages, expected_slots=[("slide-x", "The Leadership Gap")])
    assert "slide-x" not in r.matched
    assert any(a["kind"] == "slot" and a["slide_id"] == "slide-x" for a in r.ambiguous)


def test_unique_subset_binds() -> None:
    """Sibling of the ambiguity pin: the SAME brief, only one candidate page →
    binds. Kills the 'always raises ambiguous' mutant."""
    pages = _pages(["1_The-Leadership-Gap-and-the-Case-for-Change"])
    r = match_pages_to_slots(pages=pages, expected_slots=[("slide-x", "The Leadership Gap")])
    assert r.matched["slide-x"].endswith("The-Leadership-Gap-and-the-Case-for-Change.png")
    assert r.ambiguous == []


def test_distinctive_token_floor_blocks_single_token_match() -> None:
    """A 1-distinctive-token brief must NOT carry a match (Winston/Amelia floor)
    — closes 'short brief supersets an unrelated page'."""
    pages = _pages(["1_The-Leadership-Gap-and-the-Case-for-Change"])
    r = match_pages_to_slots(pages=pages, expected_slots=[("slide-y", "Leadership")])
    assert r.matched == {}
    assert r.unmatched_keys == ["slide-y"]


def test_stopword_only_overlap_does_not_match() -> None:
    """Only function words shared → no edge (stopword strip before containment)."""
    pages = _pages(["1_The-Quarterly-Revenue-Outlook"])
    r = match_pages_to_slots(pages=pages, expected_slots=[("slide-z", "The Annual Cost Review")])
    assert r.matched == {}
    assert r.unmatched_keys == ["slide-z"]


def test_bidirectional_drop_and_append_both_bind() -> None:
    """Both Gamma rephrase directions in one run: a page that DROPPED a brief word
    and a page that APPENDED words both bind uniquely."""
    briefs = [
        ("a", "The Human Cost: System Waste & Burnout"),
        ("b", "The Leadership Gap"),
    ]
    pages = _pages([
        "1_The-Human-Cost-Waste-and-Burnout",
        "2_The-Leadership-Gap-and-the-Case-for-Change",
    ])
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    # a: page⊆brief (Gamma dropped "System"); b: brief⊆page (Gamma appended).
    assert r.matched["a"].endswith("The-Human-Cost-Waste-and-Burnout.png")
    assert r.matched["b"].endswith("The-Leadership-Gap-and-the-Case-for-Change.png")
    assert r.ambiguous == []


def test_non_leading_unmatched_page_is_recorded_not_dropped() -> None:
    """A stray page AFTER a matched page is unmatched_pages (fail-loud surface),
    NOT auto-dropped — only contiguous leading cover drops."""
    briefs = [("s1", "The Economic & Structural Reality")]
    pages = _pages(["1_The-Economic-and-Structural-Reality", "2_Thank-You-and-Next-Steps"])
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    assert r.matched["s1"].endswith("The-Economic-and-Structural-Reality.png")
    assert [p["page_index"] for p in r.unmatched_pages] == [2]
    assert r.dropped_pages == []


def test_duplicate_page_index_does_not_silently_drop_a_page() -> None:
    """Blind/Edge MUST-FIX: two pages sharing a page_index (e.g. both fall back
    to the 9999 sort sentinel, or duplicate numbering) must NOT overwrite each
    other in the candidate graph. Pages are keyed by position, so both survive
    and bind to their distinct briefs."""
    pages = [
        {"page_index": 9999, "title": "Alpha Topic Detail", "path": "/a.png"},
        {"page_index": 9999, "title": "Beta Topic Detail", "path": "/b.png"},
    ]
    briefs = [("s1", "Alpha Topic Detail"), ("s2", "Beta Topic Detail")]
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    assert r.matched == {"s1": "/a.png", "s2": "/b.png"}  # neither page vanished
    assert r.unmatched_keys == []


def test_only_first_leading_unmatched_page_drops_rest_fail_loud() -> None:
    """Blind SHOULD-FIX: cap leading-cover drops at ONE. A second leading
    unmatched page is fatal (page-unmatched), not silently dropped as cover."""
    pages = _pages([
        "1_Cover-Title-Slide",            # leading cover -> dropped
        "2_Sponsor-Logos-Interstitial",   # second leading unmatched -> fail-loud
        "3_The-Economic-and-Structural-Reality",  # matches the brief
    ])
    briefs = [("s1", "The Economic & Structural Reality")]
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    assert r.matched["s1"].endswith("The-Economic-and-Structural-Reality.png")
    assert [d["page_index"] for d in r.dropped_pages] == [1]  # only the first
    assert [p["page_index"] for p in r.unmatched_pages] == [2]  # second is fatal


def test_normalize_title_strips_objective_and_punctuation() -> None:
    """The frozen normalization contract underneath containment."""
    assert (
        normalize_title("The Economic & Structural Reality")
        == "the economic and structural reality"
    )
    assert normalize_title("The Leadership Gap — Analyze the mismatch") == "the leadership gap"
    assert normalize_title("The-Human-Cost-Waste-and-Burnout") == "the human cost waste and burnout"
