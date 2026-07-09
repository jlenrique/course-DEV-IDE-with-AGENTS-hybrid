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
from pathlib import Path

import pytest

from skills.gamma_api_mastery.scripts.gamma_operations import (
    match_pages_to_slots,
    materialize_exported_slide_paths_by_title,
    normalize_title,
    title_from_export_stem,
)

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"lone-png-bytes"

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


# ---------------------------------------------------------------------------
# Apostrophe-family deletion-joining amendment (party record §10, ratified
# 2026-07-07). Live trial a18c2a86 paused-at-error: Gamma's export slugger
# DELETES apostrophes ("Technology's" -> "Technologys-...") while the frozen
# matcher SPLIT on them ({technology, s}) — no containment edge, deterministic
# `gamma.export.brief-unmatched` for ANY apostrophe-bearing brief title.
# ---------------------------------------------------------------------------


def test_apostrophe_brief_matches_gamma_slug_live_pair_pin() -> None:
    """W1 central pin — the real a18c2a86 live pair: an apostrophe-bearing
    brief MUST bind the export page whose slug deleted the apostrophe."""
    briefs = [("slide-07", "Technology's Promise Requires Clinical Innovators")]
    pages = _pages(["7_Technologys-Promise-Requires-Clinical-Innovators"])
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    assert r.matched["slide-07"].endswith(
        "Technologys-Promise-Requires-Clinical-Innovators.png"
    )
    assert r.unmatched_keys == []
    assert r.unmatched_pages == []
    assert r.ambiguous == []


@pytest.mark.parametrize(
    "variant",
    [
        pytest.param("Technology's", id="U+0027-apostrophe"),
        pytest.param("Technology‘s", id="U+2018-left-single-quote"),
        pytest.param("Technology’s", id="U+2019-right-single-quote"),
        pytest.param("Technologyʼs", id="U+02BC-modifier-apostrophe"),
        pytest.param("Technology`s", id="U+0060-grave"),
        pytest.param("Technology´s", id="U+00B4-acute"),
        pytest.param("Technology＇s", id="U+FF07-fullwidth-via-NFKD"),
    ],
)
def test_normalize_title_apostrophe_family_joins_intra_word(variant: str) -> None:
    """W2 — every enumerated family char (plus the NFKD-folded fullwidth form)
    deletion-JOINS intra-word: it must normalize identically to the
    apostrophe-free spelling, never split into {technology, s}."""
    assert normalize_title(variant) == normalize_title("Technologys")
    assert normalize_title(variant) == "technologys"


def test_apostrophe_collision_is_ambiguous_never_silently_bound() -> None:
    """W3 collision ruling (ratified): two slots differing only by
    apostrophe-s, briefed together against a matching page, MUST surface
    ambiguity fail-loud — the slug channel destroys the distinction, so
    binding either would be false precision."""
    briefs = [
        ("slot-a", "Member's Only"),
        ("slot-b", "Members Only"),
    ]
    pages = _pages(["5_Members-Only"])
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    assert "slot-a" not in r.matched
    assert "slot-b" not in r.matched
    assert r.matched == {}
    assert r.ambiguous  # fail-loud surface non-empty, never a silent pick
    assert any(a["kind"] == "page" for a in r.ambiguous)


def test_normalize_title_apostrophe_deletes_not_spaces() -> None:
    """W4 mutant-killer: deletion-JOINS. An add-apostrophes-to-the-space-class
    mutant yields "innovator s" / tokens {innovator, s}; the contract is
    "innovators"."""
    assert normalize_title("Innovator's") == "innovators"
    assert normalize_title("Innovator's") != "innovator s"


def test_normalize_title_strips_objective_and_punctuation() -> None:
    """The frozen normalization contract underneath containment."""
    assert (
        normalize_title("The Economic & Structural Reality")
        == "the economic and structural reality"
    )
    assert normalize_title("The Leadership Gap — Analyze the mismatch") == "the leadership gap"
    assert normalize_title("The-Human-Cost-Waste-and-Burnout") == "the human cost waste and burnout"


def test_lone_png_single_slot_binds_by_cardinality(tmp_path: Path) -> None:
    """Live Gamma single-card export is a lone PNG (not a zip); N=1 must bind.

    Opaque download stems (e.g. gary_A) bind by sole-slot cardinality — party
    rider 2026-07-08: do not require title containment when N=1.
    """
    lone = tmp_path / "gary_A.png"
    lone.write_bytes(_PNG_MAGIC)
    export_dir = tmp_path / "out"
    export_dir.mkdir()
    result = materialize_exported_slide_paths_by_title(
        lone,
        requested_format="png",
        expected_slots=[("slide-01", "Module 1 Bridge to Module 2")],
        module_lesson_part="A",
        export_dir=export_dir,
        label="A",
    )
    assert result.unmatched_keys == []
    assert result.unmatched_pages == []
    assert result.ambiguous == []
    assert "slide-01" in result.matched
    bound = Path(result.matched["slide-01"])
    assert bound.is_file()
    assert bound.name.endswith("_slide-01.png")
    assert bound.read_bytes() == _PNG_MAGIC


def test_lone_png_multi_slot_fails_loud_no_positional_broadcast(tmp_path: Path) -> None:
    """Lone PNG + N>1 must NOT positionally bind; all slots unmatched."""
    lone = tmp_path / "gary_A.png"
    lone.write_bytes(_PNG_MAGIC)
    export_dir = tmp_path / "out"
    export_dir.mkdir()
    result = materialize_exported_slide_paths_by_title(
        lone,
        requested_format="png",
        expected_slots=[
            ("slide-01", "First Topic"),
            ("slide-02", "Second Topic"),
        ],
        module_lesson_part="A",
        export_dir=export_dir,
        label="A",
    )
    assert result.matched == {}
    assert sorted(result.unmatched_keys) == ["slide-01", "slide-02"]
    assert list(export_dir.glob("*.png")) == []
    assert len(result.unmatched_pages) == 1


def test_lone_png_titled_stem_single_slot_still_binds(tmp_path: Path) -> None:
    """N=1 lone PNG whose stem carries ``{N}_{Title}`` still binds."""
    lone = tmp_path / "1_Only-Topic-Here.png"
    lone.write_bytes(_PNG_MAGIC)
    export_dir = tmp_path / "out"
    export_dir.mkdir()
    result = materialize_exported_slide_paths_by_title(
        lone,
        requested_format="png",
        expected_slots=[("s1", "Only Topic Here")],
        module_lesson_part="A",
        export_dir=export_dir,
        label="A",
    )
    assert result.unmatched_keys == []
    assert "s1" in result.matched
    assert Path(result.matched["s1"]).read_bytes() == _PNG_MAGIC


def test_lone_png_titled_stem_mismatch_fails_loud(tmp_path: Path) -> None:
    """Parseable ``{N}_{Title}`` stem that fails containment must NOT force-bind."""
    lone = tmp_path / "1_Completely-Wrong-Title.png"
    lone.write_bytes(_PNG_MAGIC)
    export_dir = tmp_path / "out"
    result = materialize_exported_slide_paths_by_title(
        lone,
        requested_format="png",
        expected_slots=[("slide-01", "Only Topic Here")],
        module_lesson_part="A",
        export_dir=export_dir,
        label="A",
    )
    assert result.matched == {}
    assert result.unmatched_keys == ["slide-01"]


def test_lone_png_multi_slot_records_orphan_page(tmp_path: Path) -> None:
    """N>1 lone PNG should surface the orphan export page for diagnostics."""
    lone = tmp_path / "gary_A.png"
    lone.write_bytes(_PNG_MAGIC)
    export_dir = tmp_path / "out"
    result = materialize_exported_slide_paths_by_title(
        lone,
        requested_format="png",
        expected_slots=[
            ("slide-01", "First Topic"),
            ("slide-02", "Second Topic"),
        ],
        module_lesson_part="A",
        export_dir=export_dir,
        label="A",
    )
    assert result.matched == {}
    assert sorted(result.unmatched_keys) == ["slide-01", "slide-02"]
    assert len(result.unmatched_pages) == 1
    assert "lone-png-export" in str(result.unmatched_pages[0].get("reason", ""))


# ---------------------------------------------------------------------------
# Residual soft bind (party 2026-07-09) — Completion↔Complete live pin +
# cover-drop must not mute a sole content residue; F8 cover must not soft-bind.
# ---------------------------------------------------------------------------


def test_bc0f81c4_completion_complete_residual_binds_not_cover_drop() -> None:
    """Live trial bc0f81c4: brief Completion/Closure vs page Complete/Set fails
    containment; residual soft bind must commit slide-01 and must NOT drop the
    page as unmatched-leading-page (mute unmatched pages: [])."""
    briefs = [
        ("slide-01", "Module 1 Completion and Mindset Closure"),
        ("slide-02", "Assessment Bridge Overview"),
        ("slide-03", "Practice Checkpoint One"),
        ("slide-04", "Practice Checkpoint Two"),
        ("slide-05", "Next Steps and Resources"),
    ]
    stems = [
        "1_Module-1-Complete-The-Mindset-is-Set",
        "2_Assessment-Bridge-Overview",
        "3_Practice-Checkpoint-One",
        "4_Practice-Checkpoint-Two",
        "5_Next-Steps-and-Resources",
    ]
    r = match_pages_to_slots(pages=_pages(stems), expected_slots=briefs)
    assert r.matched["slide-01"].endswith("Module-1-Complete-The-Mindset-is-Set.png")
    assert sorted(r.matched) == [
        "slide-01",
        "slide-02",
        "slide-03",
        "slide-04",
        "slide-05",
    ]
    assert r.unmatched_keys == []
    assert r.dropped_pages == []
    assert r.unmatched_pages == []
    assert r.ambiguous == []


def test_residual_does_not_bind_f8_cover_to_unmatched_summary() -> None:
    """Kill-the-mutant: residual must NOT soft-bind the F8 cover to slide-06.
    Cover still drops; merged-away Summary stays unmatched."""
    r = match_pages_to_slots(pages=_pages(F8_STEMS), expected_slots=F8_BRIEFS)
    assert r.unmatched_keys == ["slide-06"]
    assert [d["page_index"] for d in r.dropped_pages] == [1]
    assert "slide-06" not in r.matched


def test_multi_residue_does_not_soft_bind() -> None:
    """Cardinality gate: two unmatched slots + two unmatched pages → no soft
    bind; both slots stay unmatched and pages surface fail-loud."""
    briefs = [
        ("slide-01", "Module 1 Completion and Mindset Closure"),
        ("slide-02", "Assessment Bridge Overview"),
        ("slide-03", "Orphan Brief Alpha Topic"),
        ("slide-04", "Orphan Brief Beta Topic"),
    ]
    stems = [
        "1_Module-1-Complete-The-Mindset-is-Set",
        "2_Assessment-Bridge-Overview",
        "3_Completely-Unrelated-Gamma-Page-One",
        "4_Completely-Unrelated-Gamma-Page-Two",
    ]
    r = match_pages_to_slots(pages=_pages(stems), expected_slots=briefs)
    # After bijective: 01 fails containment, 02 matches, 03/04 fail; pages
    # 1/3/4 unmatched → multi residue → residual must not fire.
    assert "slide-01" not in r.matched
    assert sorted(r.unmatched_keys) == ["slide-01", "slide-03", "slide-04"]
    assert len(r.unmatched_pages) + len(r.dropped_pages) == 3


def test_weak_overlap_leading_page_still_cover_drops() -> None:
    """One unmatched slot + one leading unmatched page with weak overlap only
    → soft gate fails → existing cover-drop proceeds."""
    briefs = [("s1", "The Economic & Structural Reality")]
    pages = _pages(
        [
            "1_Cover-Title-Slide",
            "2_The-Economic-and-Structural-Reality",
        ]
    )
    r = match_pages_to_slots(pages=pages, expected_slots=briefs)
    assert r.matched["s1"].endswith("The-Economic-and-Structural-Reality.png")
    assert [d["page_index"] for d in r.dropped_pages] == [1]
    assert r.unmatched_keys == []
    assert r.unmatched_pages == []

