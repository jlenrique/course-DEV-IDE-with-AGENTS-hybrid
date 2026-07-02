"""Leg-C R3 — rewired AC#4/5/6/7/13-equivalent tests at the REAL Pass-1 surface.

M-2 (binding): fixtures are generated FROM the live Part-3 baseline's on-disk
output (``irene_pass1-05B-output-verbatim.json``, trial
66ae45d5-3b6b-439b-bad9-2240a0ce0ace, 12 plan_units / 7 clusters = count_K),
sha256-pinned + drift-checked against the evidence file.

FIXTURE HONESTY: the real baseline PREDATES the source_refs emission, so the
split tests ADD synthetic ``source_refs`` via the clearly-labelled derivation
helper ``_with_synthetic_refs`` below; the plan_units themselves stay
verbatim-real. (Stated in the story Dev Notes per the work order.)
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene_pass1 import cluster_floor as cf

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "leg_c_cluster_floor"
    / "irene_pass1-05B-output-verbatim.json"
)
EVIDENCE_PATH = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "leg-c-part3-baseline-20260701T232209Z"
    / "irene_pass1-05B-output-verbatim.json"
)
# sha256 of the live baseline evidence content (M-2 pin; Winston-iii capture),
# newline-normalized (CRLF->LF) so git text-normalization on checkout cannot
# fake a drift. Raw-CRLF evidence sha for the record:
# a3b11058b7aca8499f5eab64cd8d4cb55fa15f4b1685d60da4d2ed20b1c6ddfb
BASELINE_SHA256 = "40cc43ae6fa5b1b67534130cfbb8ec71a7fdfe22e9bbc4de572e5d5cffd8550a"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _real_plan_units() -> list[dict]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload["lesson_plan"]["plan_units"]


# --------------------------------------------------------------------------- #
# CLEARLY-LABELLED FIXTURE DERIVATION: synthetic source_refs on verbatim-real  #
# plan_units (the baseline predates the anchor emission).                      #
# --------------------------------------------------------------------------- #
_SYNTHETIC_REFS_BY_UNIT: dict[str, list[str]] = {
    # claim anchors (no figure/narration markers, no numerals)
    "u01": ["physicians already possess the core traits of innovation leaders"],
    "u02": ["the clinical method mirrors the design thinking process step by step"],
    "u03": ["required reading before the intrapreneurship content"],
    "u04": ["intrapreneurship changes systems from within existing institutions"],
    # the two Design Briefs: SELF-CONTAINED figure+narration units (the party's
    # AC#9/AC#12 material — distinct units legitimately separable, D2)
    "u05": [
        "Image Prompt: a split-screen of a blank canvas beside a load-bearing blueprint",
        "Narration: inside the hospital every wall you want to move is load-bearing",
    ],
    "u06": [
        "Image Prompt: an organizational web of resources, brand, patients, and stakeholders",
        "Narration: Lam reminds us the organization already holds what you need to scale",
    ],
    "u07": ["an idea has no intrinsic value until it is vetted into an executable opportunity"],
    "u08": ["the tablet idea jumps to technology before defining the true workflow problem"],
    "u09": ["chief complaint, root cause, and desired workflow improvement define the opportunity"],
    "u10": ["first principles thinking breaks the broken workflow into fundamental truths"],
    "u11": ["part three closes by integrating the clinician innovator mindset"],
    "u12": ["which distinction separates an idea from an opportunity"],
}


def _with_synthetic_refs(
    units: list[dict], refs_by_unit: dict[str, list[str]] | None = None
) -> list[dict]:
    refs_by_unit = _SYNTHETIC_REFS_BY_UNIT if refs_by_unit is None else refs_by_unit
    out = []
    for unit in copy.deepcopy(units):
        if unit["unit_id"] in refs_by_unit:
            # deepcopy (not list()) so deliberately-malformed variants (e.g. a
            # bare string) survive as-is for the veto tests
            unit["source_refs"] = copy.deepcopy(refs_by_unit[unit["unit_id"]])
        out.append(unit)
    return out


# --------------------------------------------------------------------------- #
# M-2 sha pin + drift check                                                    #
# --------------------------------------------------------------------------- #
def test_fixture_is_sha_pinned_to_the_live_baseline() -> None:
    assert _sha256(FIXTURE_PATH) == BASELINE_SHA256, (
        "the committed fixture drifted from the sha-pinned live Part-3 baseline "
        "capture; regenerate ONLY from a new party-authorized baseline"
    )
    if EVIDENCE_PATH.is_file():
        assert _sha256(EVIDENCE_PATH) == BASELINE_SHA256, (
            "the on-disk evidence file drifted from the pinned baseline sha"
        )


def test_fixture_shape_matches_the_baseline_summary() -> None:
    units = _real_plan_units()
    assert len(units) == 12
    assert cf.count_clusters(units) == 7  # count_K
    # no offline member keys / role tags exist in real output (D1 live-confirmed)
    for unit in units:
        assert "source_points" not in unit
        assert "kind" not in unit


# --------------------------------------------------------------------------- #
# AC#4-equivalent: floor honored, split-only, byte-identity                     #
# --------------------------------------------------------------------------- #
def test_floor_honored_splits_to_n_clusters_with_byte_identity() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    witness_before = cf.flatten_plan_content(units)
    honored = cf.honor_min_cluster_floor(units, 8)

    assert cf.count_clusters(honored) == 8  # K=7 < N=8 <= T
    # byte-identity: ordered unit CONTENT unchanged (only grouping reshaped)
    assert cf.flatten_plan_content(honored) == witness_before
    # order + distinctness of unit ids preserved; NO new units minted
    ids_before = [u["unit_id"] for u in units]
    ids_after = [u["unit_id"] for u in honored]
    assert ids_after == ids_before
    assert len(set(ids_after)) == len(ids_after)

    by_id = {u["unit_id"]: u for u in honored}
    # earliest legitimate seam in plan order: c-u04 between u04 and u05
    donor_head = by_id["u04"]
    assert donor_head["cluster_id"] == "c-u04"
    assert donor_head["cluster_interstitial_count"] == 0  # recomputed after donation
    promoted = by_id["u05"]
    assert promoted["cluster_role"] == "head"
    assert promoted["cluster_id"] == "c-u04#f1"  # P4 distinct minted identity
    assert promoted["parent_slide_id"] is None
    assert promoted["cluster_interstitial_count"] == 1
    follower = by_id["u06"]
    assert follower["cluster_role"] == "interstitial"
    assert follower["cluster_id"] == "c-u04#f1"
    assert follower["parent_slide_id"] == "u05"
    # untouched clusters pass through as the SAME objects (split-only)
    assert honored[0] is units[0]  # u01 singleton
    assert by_id["u07"] is next(u for u in units if u["unit_id"] == "u07")
    # minted ids never collide
    cluster_ids = [cid for cid, _ in cf.group_plan_clusters(honored)]
    assert len(set(cluster_ids)) == len(cluster_ids)


def test_floor_at_max_reachable_uses_every_legitimate_seam() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    # 7 clusters + 5 seams (2 in c-u04, 3 in c-u07) = 12 reachable
    honored = cf.honor_min_cluster_floor(units, 12)
    assert cf.count_clusters(honored) == 12
    assert cf.flatten_plan_content(honored) == cf.flatten_plan_content(units)


def test_floor_leq_current_count_is_identity_noop() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    for floor in (1, 7):
        honored = cf.honor_min_cluster_floor(units, floor)
        assert honored == units
        assert all(a is b for a, b in zip(honored, units, strict=True))


def test_determinism_same_input_same_output() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    first = cf.honor_min_cluster_floor(units, 9)
    second = cf.honor_min_cluster_floor(copy.deepcopy(units), 9)
    assert first == second


# --------------------------------------------------------------------------- #
# AC#5/AC#12-equivalent: figure<->narration atomicity                           #
# --------------------------------------------------------------------------- #
def _atomicity_refs() -> dict[str, list[str]]:
    """Variant: u05 = a figure WITHOUT its own narration; u06 = its explaining
    narration. Only c-u04 carries valid refs (all other units keep none), so
    the bonded seam is the discriminating surface."""
    return {
        "u04": ["entrepreneurship builds new ventures while intrapreneurship changes systems"],
        "u05": ["Image Prompt: a maze rendered as a load-bearing blueprint"],
        "u06": ["Narration: every wall the intrapreneur wants to move is load-bearing"],
    }


def test_figure_never_severed_from_its_explaining_narration() -> None:
    units = _with_synthetic_refs(_real_plan_units(), _atomicity_refs())
    # c-u04 seams: u04|u05 legitimate; u05|u06 BONDED (figure-only next to its
    # narration). floor 8 -> deficit 1 -> the split lands at u04|u05 and the
    # bond survives in ONE cluster.
    honored = cf.honor_min_cluster_floor(units, 8)
    by_id = {u["unit_id"]: u for u in honored}
    assert by_id["u05"]["cluster_id"] == by_id["u06"]["cluster_id"]
    assert cf.flatten_plan_content(honored) == cf.flatten_plan_content(units)


def test_bonded_seam_is_never_used_even_under_floor_pressure() -> None:
    units = _with_synthetic_refs(_real_plan_units(), _atomicity_refs())
    # only 1 legitimate seam exists (u04|u05); a floor needing 2 must REFUSE
    # rather than sever the figure<->narration bond.
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 9)


# --------------------------------------------------------------------------- #
# AC#6/AC#13-equivalent: soft floor / veto discipline                           #
# --------------------------------------------------------------------------- #
def test_floor_too_high_refuses_with_soft_mismatch() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    with pytest.raises(cf.ClusterFloorMismatchError) as excinfo:
        cf.honor_min_cluster_floor(units, 20)  # the AC#13 live parameter
    assert isinstance(excinfo.value, SpecialistDispatchError)  # P3 recoverable
    assert excinfo.value.tag == cf.CLUSTER_FLOOR_MISMATCH_TAG
    assert "refusing to over-fragment" in str(excinfo.value)


def test_absent_refs_mean_zero_seams_never_guess_and_split() -> None:
    units = _real_plan_units()  # verbatim-real: NO source_refs anywhere
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 8)


@pytest.mark.parametrize(
    "bad_refs",
    ["not-a-list", [], [""], ["ok", "  "], ["ok", 123], [None]],
)
def test_malformed_refs_are_treated_as_absent_never_crash(bad_refs) -> None:
    refs = dict(_SYNTHETIC_REFS_BY_UNIT)
    # poison every multi-unit cluster member so no seam can be certified
    for uid in ("u04", "u05", "u06", "u07", "u08", "u09", "u10"):
        refs[uid] = bad_refs
    units = _with_synthetic_refs(_real_plan_units(), refs)
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 8)


def test_unresolvable_anchor_vetoes_when_source_is_present() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    source = "A corpus that contains none of the synthetic anchors."
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 8, extracted_source=source)


def test_resolvable_anchors_split_when_source_is_present() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    all_refs = [ref for refs in _SYNTHETIC_REFS_BY_UNIT.values() for ref in refs]
    # line-wrap the anchors: resolution is whitespace-run tolerant, verbatim
    # otherwise
    source = "\n".join(ref.replace(" ", "\n", 1) for ref in all_refs)
    honored = cf.honor_min_cluster_floor(units, 8, extracted_source=source)
    assert cf.count_clusters(honored) == 8


# --------------------------------------------------------------------------- #
# I-4: assessment / knowledge-check exemption                                  #
# --------------------------------------------------------------------------- #
def _two_unit_cluster(title_head: str, title_inter: str) -> list[dict]:
    """SYNTHETIC minimal plan (labelled): one 2-unit cluster + one singleton.

    Anchors are DISTINCT per unit (R4: a shared anchor is the duplicate-anchor
    veto's own discriminating surface — these tests target OTHER vetoes)."""
    return [
        {"unit_id": "a1", "title": title_head, "learning_objective": "lo",
         "cluster_id": "c-a", "cluster_role": "head", "cluster_position": "establish",
         "cluster_interstitial_count": 1, "parent_slide_id": None,
         "source_refs": ["a plain first claim anchor with no markers"]},
        {"unit_id": "a2", "title": title_inter, "learning_objective": "lo",
         "cluster_id": "c-a", "cluster_role": "interstitial",
         "cluster_position": "develop", "parent_slide_id": "a1",
         "source_refs": ["a plain second claim anchor with no markers"]},
        {"unit_id": "b1", "title": "Plain singleton", "learning_objective": "lo",
         "cluster_id": "c-b", "cluster_role": "head", "cluster_position": "establish",
         "cluster_interstitial_count": 0, "parent_slide_id": None,
         "source_refs": ["a plain third claim anchor with no markers"]},
    ]


def test_assessment_cluster_is_floor_exempt_by_construction() -> None:
    units = _two_unit_cluster("Part 3 Knowledge Check", "Knowledge Check Answers")
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 3)  # its only seam is exempt


def test_non_assessment_control_cluster_splits_fine() -> None:
    # the discriminating control for the exemption above
    units = _two_unit_cluster("Two beats", "Second beat")
    honored = cf.honor_min_cluster_floor(units, 3)
    assert cf.count_clusters(honored) == 3


def test_real_knowledge_check_unit_is_detected() -> None:
    # regression pin on the REAL baseline unit (I-4)
    u12 = next(u for u in _real_plan_units() if u["unit_id"] == "u12")
    assert cf._is_assessment_unit(u12)


# --------------------------------------------------------------------------- #
# invalid config (P3: recoverable typed errors)                                #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("bad_floor", [0, -1, True, "3", 2.5, None])
def test_invalid_floor_raises_typed_recoverable_error(bad_floor) -> None:
    units = _with_synthetic_refs(_real_plan_units())
    with pytest.raises(cf.InvalidFloorConfigError) as excinfo:
        cf.honor_min_cluster_floor(units, bad_floor)
    assert isinstance(excinfo.value, SpecialistDispatchError)


def test_non_list_plan_raises_typed_recoverable_error() -> None:
    with pytest.raises(cf.InvalidFloorConfigError):
        cf.honor_min_cluster_floor("not-a-list", 3)


# --------------------------------------------------------------------------- #
# D-1/D-3: dead-config guard discriminating pair (co-located with THIS module) #
# --------------------------------------------------------------------------- #
def test_dead_config_pair_consulted_is_quiet() -> None:
    units = _with_synthetic_refs(_real_plan_units())
    payload = {"min_cluster_floor": 8}
    honored, receipt = cf.consume_min_cluster_floor(payload, units)
    assert receipt.consulted and receipt.floor == 8
    assert receipt.clusters_before == 7 and receipt.clusters_after == 8
    assert cf.count_clusters(honored) == 8
    cf.assert_floor_consulted(payload, receipt)  # quiet


def test_dead_config_pair_bound_but_bypassed_raises() -> None:
    payload = {"min_cluster_floor": 8}
    bypassed = cf.FloorConsumption(
        consulted=False, floor=None, clusters_before=7, clusters_after=7
    )
    with pytest.raises(cf.DeadFloorConfigError):
        cf.assert_floor_consulted(payload, bypassed)


def test_no_floor_bound_is_quiet_and_untouched() -> None:
    units = _real_plan_units()
    honored, receipt = cf.consume_min_cluster_floor({"mode": "pass-1"}, units)
    assert honored is units
    assert not receipt.consulted
    cf.assert_floor_consulted({"mode": "pass-1"}, receipt)  # quiet


# --------------------------------------------------------------------------- #
# R2 (Edge#2): Unicode/quote canonicalization on verbatim anchor matching      #
# --------------------------------------------------------------------------- #
def _quote_cluster(anchor_a: str, anchor_b: str) -> list[dict]:
    """SYNTHETIC minimal plan (labelled): one 2-unit cluster + one singleton."""
    return [
        {"unit_id": "q1", "title": "Quote head", "learning_objective": "lo",
         "cluster_id": "c-q", "cluster_role": "head", "cluster_position": "establish",
         "cluster_interstitial_count": 1, "parent_slide_id": None,
         "source_refs": [anchor_a]},
        {"unit_id": "q2", "title": "Quote beat", "learning_objective": "lo",
         "cluster_id": "c-q", "cluster_role": "interstitial",
         "cluster_position": "develop", "parent_slide_id": "q1",
         "source_refs": [anchor_b]},
        {"unit_id": "q3", "title": "Quote singleton", "learning_objective": "lo",
         "cluster_id": "c-q3", "cluster_role": "head", "cluster_position": "establish",
         "cluster_interstitial_count": 0, "parent_slide_id": None,
         "source_refs": ["Part three opens"]},
    ]


# The Part-3 corpus reality: curly apostrophes/quotes (U+2019/U+201C/U+201D),
# en/em-dashes, non-breaking spaces. An LLM emitting straight-quote anchors
# must still resolve (else every seam zeroes and the live differential
# false-vetoes).
_CURLY_SOURCE = (
    "Part three opens “The Intrapreneur’s Maze” — the "
    "load–bearing walls of the institution."
)
_STRAIGHT_SOURCE = (
    'Part three opens "The Intrapreneur\'s Maze" - the load-bearing walls of '
    "the institution."
)


def test_straight_quote_anchor_resolves_against_curly_source() -> None:
    units = _quote_cluster(
        'opens "The Intrapreneur\'s Maze"', "the load-bearing walls of the institution"
    )
    honored = cf.honor_min_cluster_floor(units, 3, extracted_source=_CURLY_SOURCE)
    assert cf.count_clusters(honored) == 3


def test_curly_anchor_resolves_against_straight_source() -> None:
    units = _quote_cluster(
        "opens “The Intrapreneur’s Maze”",
        "the load—bearing walls of the institution",
    )
    honored = cf.honor_min_cluster_floor(units, 3, extracted_source=_STRAIGHT_SOURCE)
    assert cf.count_clusters(honored) == 3


def test_genuinely_absent_anchor_still_vetoes_after_normalization() -> None:
    units = _quote_cluster(
        'opens "The Intrapreneur\'s Maze"', "an anchor that is nowhere in the source"
    )
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 3, extracted_source=_CURLY_SOURCE)


# --------------------------------------------------------------------------- #
# F2 (live-diagnosed 2026-07-01): markdown/quotation DEBRIS *inside* the source #
# between anchor words. Two REAL failing pairs from the live K' run: a markdown #
# emphasis asterisk mid-phrase (``within* an existing organization``) and       #
# quotation marks between anchor words (``"Good vs. Bad" problem formulation`` #
# — R2 MAPS quote glyphs but did not REMOVE them). Emphasis chars (* _ `) and   #
# all quotation chars (straight+curly, single+double) are now REMOVED from     #
# BOTH sides; containment stays deterministic (absent anchors still veto).     #
# --------------------------------------------------------------------------- #
_ASTERISK_DEBRIS_SOURCE = (
    "Part three opens the maze. Intrapreneurship grows within* an existing "
    "organization, and the walls hold."
)
_QUOTE_DEBRIS_SOURCE = (
    'Part three opens the maze. "Good vs. Bad" problem formulation separates '
    "ideas worth pursuing, and the walls hold."
)


def test_anchor_resolves_across_markdown_emphasis_asterisk_in_source() -> None:
    """Live K' failing pair #1 (verbatim): anchor 'within an existing
    organization' vs source ``within* an existing organization``."""
    units = _quote_cluster("within an existing organization", "and the walls hold")
    honored = cf.honor_min_cluster_floor(
        units, 3, extracted_source=_ASTERISK_DEBRIS_SOURCE
    )
    assert cf.count_clusters(honored) == 3


def test_anchor_resolves_across_quotation_marks_in_source() -> None:
    """Live K' failing pair #2 (verbatim): anchor 'Good vs. Bad problem
    formulation' vs source ``"Good vs. Bad" problem formulation``."""
    units = _quote_cluster("Good vs. Bad problem formulation", "and the walls hold")
    honored = cf.honor_min_cluster_floor(
        units, 3, extracted_source=_QUOTE_DEBRIS_SOURCE
    )
    assert cf.count_clusters(honored) == 3


def test_markdown_underscore_and_backtick_debris_also_removed() -> None:
    """The full emphasis set (* _ `) is removed symmetrically from both sides."""
    units = _quote_cluster("the min_cluster_floor knob", "and the walls hold")
    source = (
        "Part three opens the maze. Turn the `min_cluster_floor` knob "
        "carefully, and the walls hold."
    )
    honored = cf.honor_min_cluster_floor(units, 3, extracted_source=source)
    assert cf.count_clusters(honored) == 3


def test_genuinely_absent_anchor_still_vetoes_against_debris_source() -> None:
    """Veto discipline intact post-removal: a paraphrased/absent anchor fails."""
    units = _quote_cluster(
        "within an existing organization", "a paraphrase that appears nowhere"
    )
    with pytest.raises(cf.ClusterFloorMismatchError):
        cf.honor_min_cluster_floor(units, 3, extracted_source=_ASTERISK_DEBRIS_SOURCE)


def test_legitimate_apostrophe_anchor_still_resolves_after_removal() -> None:
    """Apostrophes are quotation chars and are removed from BOTH sides, so 'The
    Intrapreneur's Maze' (curly OR straight) still resolves against the curly
    corpus (the R2 pairs above stay green)."""
    units = _quote_cluster(
        "opens “The Intrapreneur’s Maze”",
        "the load-bearing walls of the institution",
    )
    honored = cf.honor_min_cluster_floor(units, 3, extracted_source=_CURLY_SOURCE)
    assert cf.count_clusters(honored) == 3


# --------------------------------------------------------------------------- #
# R4 (Edge#3): duplicate/cross-unit anchor reuse = unresolvable (veto)         #
# --------------------------------------------------------------------------- #
def _dup_anchor_plan() -> list[dict]:
    """SYNTHETIC (labelled): cluster c-a shares ONE anchor across both units
    (curly-vs-straight variants so the check is post-normalization); cluster
    c-b carries distinct anchors."""
    shared = "the intrapreneur’s shared anchor phrase"
    shared_straight = "the intrapreneur's shared anchor phrase"
    return [
        {"unit_id": "d1", "title": "Dup head", "learning_objective": "lo",
         "cluster_id": "c-a", "cluster_role": "head", "cluster_position": "establish",
         "cluster_interstitial_count": 1, "parent_slide_id": None,
         "source_refs": [shared]},
        {"unit_id": "d2", "title": "Dup beat", "learning_objective": "lo",
         "cluster_id": "c-a", "cluster_role": "interstitial",
         "cluster_position": "develop", "parent_slide_id": "d1",
         "source_refs": [shared_straight]},
        {"unit_id": "d3", "title": "Distinct head", "learning_objective": "lo",
         "cluster_id": "c-b", "cluster_role": "head", "cluster_position": "establish",
         "cluster_interstitial_count": 1, "parent_slide_id": None,
         "source_refs": ["a first distinct claim anchor"]},
        {"unit_id": "d4", "title": "Distinct beat", "learning_objective": "lo",
         "cluster_id": "c-b", "cluster_role": "interstitial",
         "cluster_position": "develop", "parent_slide_id": "d3",
         "source_refs": ["a second distinct claim anchor"]},
    ]


def test_duplicate_anchor_units_contribute_zero_seams() -> None:
    units = _dup_anchor_plan()
    # 2 clusters; c-a's only seam is duplicate-poisoned -> only c-b's seam
    # remains. floor 4 needs 2 seams -> REFUSE (veto over guess).
    with pytest.raises(cf.ClusterFloorMismatchError) as excinfo:
        cf.honor_min_cluster_floor(units, 4)
    # distinct diagnostic so triage sees the duplicate-anchor veto
    assert "duplicate-anchor" in str(excinfo.value)


def test_distinct_anchor_cluster_unaffected_by_duplicate_veto_elsewhere() -> None:
    units = _dup_anchor_plan()
    honored = cf.honor_min_cluster_floor(units, 3)  # deficit 1: c-b's seam serves
    assert cf.count_clusters(honored) == 3
    by_id = {u["unit_id"]: u for u in honored}
    # c-a (duplicate-poisoned) stays whole; c-b split
    assert by_id["d1"]["cluster_id"] == by_id["d2"]["cluster_id"] == "c-a"
    assert by_id["d3"]["cluster_id"] != by_id["d4"]["cluster_id"]


# --------------------------------------------------------------------------- #
# deterministic anchor-role classification (I-3 fixed vocabulary)              #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("anchor", "expected"),
    [
        ("Image Prompt: a split-screen blueprint", "figure"),
        ("![maze](assets/maze.png)", "figure"),
        ("the chart compares both pathways", "figure"),
        ("costs rose 23% across the system", "figure"),  # frozen-neck numeral hit
        ("Narration: every wall is load-bearing", "narration"),
        ("the voiceover walks the learner through it", "narration"),
        ("a plain prose statement about opportunity", "claim"),
        ("a paragraph about intrapreneurship", "claim"),  # no 'graph' substring trap
        ("Narration: the chart says costs fell", "narration"),  # narration wins
    ],
)
def test_anchor_role_classification(anchor: str, expected: str) -> None:
    role = cf.classify_anchor_role(anchor)
    assert role == expected
    assert role in cf.ANCHOR_ROLES


@pytest.mark.parametrize("bad", [None, "", "   ", 42])
def test_unverifiable_anchor_classifies_none(bad) -> None:
    assert cf.classify_anchor_role(bad) is None
