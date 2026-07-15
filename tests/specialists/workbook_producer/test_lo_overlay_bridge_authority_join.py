"""Floors for the 38-3a LO-overlay bridge: authority-map join over marker bridge.

Trial ``a940c5eb`` rendered 6/6 LO placeholders: its plan-unit ``source_refs``
carry raw slide-title/narration strings with ZERO ``[evidence: src-NNN]``
markers, so the legacy marker bridge resolved nothing. Worse, the marker join
is cross-namespace unsound (Texas ``src-NNN`` enumerates slides only; G0
``src-NNN`` enumerates ALL corpus files), so a present marker can attach the
WRONG LO. The fix joins through the run's own digest-bound artifacts instead:

    authority row ``unit_id -> source_path``
      x G0 ``enumeration_provenance`` ``locator -> source_id``
      x ``provisional_los[].source_refs[].source_id -> objective_id``

STRUCTURAL PRECEDENCE (party W1 MUST-FIX): a present authority map disables
the marker bridge entirely; unresolved units stay unresolved (visible
placeholder + ``lo_overlay_loss``). The marker bridge runs only when the map
is absent/invalid (older runs/fixtures).

Every test pins one row of the spec's I/O & Edge-Case Matrix
(``spec-38-3a-lo-overlay-bridge-fix.md``). Fixture shapes are lifted verbatim
from run ``a940c5eb`` (paths, locators, LO/source bindings). OFFLINE ONLY:
no live LLM / network. Deterministic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.marcus.lesson_plan.slide_authority import (
    SLIDE_AUTHORITY_FILENAME,
    SlideAuthorityInvalidError,
    SourceSlideInventoryEntryV1,
    WorkbookSlideAuthorityMapV1,
    WorkbookSlideAuthorityRowV1,
    read_slide_authority_map,
    slide_authority_digest,
    write_or_validate_slide_authority_map,
)
from app.marcus.lesson_plan.slide_authority import (
    _digest as _slide_authority_canonical_digest,
)
from app.marcus.lesson_plan.workbook_enrichment import (
    lesson_plan_from_run,
    load_enrichment_card,
)
from app.specialists.workbook_producer import _act as wb_act

from ._run_fixture import collateral_present, section, write_run_json

REPO_ROOT = Path(__file__).resolve().parents[3]

# The frozen negative-witness run (READ-ONLY evidence; never mutated).
_REAL_RUN_DIR = REPO_ROOT / "runs" / "a940c5eb-1043-42c1-a2a4-8a6301b6bcf4"

# --------------------------------------------------------------------------- #
# Fixture shapes lifted verbatim from run a940c5eb                            #
# --------------------------------------------------------------------------- #

# Authority-row / inventory source paths (run-verified slide corpus).
_SLIDE_PATHS = {
    1: "slides/slide-1-the-economic-structural-reality.md",
    2: "slides/slide-2-the-human-cost-system-waste-burnout.md",
    3: "slides/slide-3-the-knowledge-explosion-new-technologies.md",
    4: "slides/slide-4-the-consumer-shift-the-digital-front-door.md",
    5: "slides/slide-5-the-leadership-gap.md",
    6: "slides/slide-6-part-2-summary.md",
}

# G0 enumeration_provenance (run-verified): src-001..005 are NON-slide corpus
# files — the cross-namespace hazard (a Texas marker `src-001` means slide 1,
# but G0 `src-001` is an assessments file).
_G0_LOCATORS = {
    "src-001": "assessments/chapter-2-knowledge-check.md",
    "src-002": "assessments/chapter-3-knowledge-check.md",
    "src-003": "README.md",
    "src-004": "references/intro-video-youtube.md",
    "src-005": "references/required-reading-beauchamp.md",
    "src-006": _SLIDE_PATHS[1],
    "src-007": _SLIDE_PATHS[2],
    "src-008": _SLIDE_PATHS[3],
    "src-009": _SLIDE_PATHS[4],
    "src-010": _SLIDE_PATHS[5],
    "src-011": _SLIDE_PATHS[6],
}

# provisional_los bindings (run-verified): lo-g0-001->src-001 ... skipping
# src-003 (README bound by no LO) ... lo-g0-005->src-006 ... lo-g0-010->src-011.
_LO_TO_SRC = {
    "lo-g0-001": "src-001",
    "lo-g0-002": "src-002",
    "lo-g0-003": "src-004",
    "lo-g0-004": "src-005",
    "lo-g0-005": "src-006",
    "lo-g0-006": "src-007",
    "lo-g0-007": "src-008",
    "lo-g0-008": "src-009",
    "lo-g0-009": "src-010",
    "lo-g0-010": "src-011",
}

# The spec's run-verified expected join for the six head units.
_EXPECTED_HEAD_MAP = {
    "u01": "lo-g0-005",
    "u02": "lo-g0-006",
    "u03": "lo-g0-007",
    "u04": "lo-g0-008",
    "u05": "lo-g0-009",
    "u06": "lo-g0-010",
}

# Marker-free plan-unit source_refs (the a940c5eb shape that broke the marker
# bridge: raw slide-title / narration strings, zero [evidence: src-NNN]).
_MARKERLESS_PLAN_UNITS: list[dict[str, Any]] = [
    {
        "unit_id": "u01",
        "cluster_role": "head",
        "source_refs": ["# **Slide 1: The Economic & Structural Reality**"],
    },
    {
        "unit_id": "u02",
        "cluster_role": "head",
        "source_refs": ["# **Slide 2: The Human Cost: System Waste & Burnout**"],
    },
    {
        "unit_id": "u03",
        "cluster_role": "head",
        "source_refs": ["# **Slide 3: The Knowledge Explosion & New Technologies**"],
    },
    {
        "unit_id": "u03i1",
        "cluster_role": "interstitial",
        "source_refs": ["In 1950, it took 50 years for medical knowledge to double;"],
    },
    {
        "unit_id": "u03i2",
        "cluster_role": "interstitial",
        "source_refs": ["We see digital health innovations reducing ER visits."],
    },
    {
        "unit_id": "u04",
        "cluster_role": "head",
        "source_refs": ["# **Slide 4: The Consumer Shift & The Digital Front Door**"],
    },
    {
        "unit_id": "u05",
        "cluster_role": "head",
        "source_refs": ["# **Slide 5: The Leadership Gap**"],
    },
    {
        "unit_id": "u06",
        "cluster_role": "head",
        "source_refs": ["# **Part 2 Summary & Knowledge Check**"],
    },
]


def _sha(label: str) -> str:
    """A syntactically valid deterministic sha256 identity for fixture fields."""
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _inventory_entry(ordinal: int) -> dict[str, Any]:
    return {
        "source_slide_id": f"slide-{ordinal}",
        "source_slide_ordinal": ordinal,
        "source_path": _SLIDE_PATHS[ordinal],
        "source_sha256": _sha(_SLIDE_PATHS[ordinal]),
    }


def _head_row(unit_id: str, final_ordinal: int, source_ordinal: int) -> dict[str, Any]:
    return {
        "final_slide_id": f"slide-{final_ordinal:02d}",
        "unit_id": unit_id,
        "source_slide_id": f"slide-{source_ordinal}",
        "source_slide_ordinal": source_ordinal,
        "source_path": _SLIDE_PATHS[source_ordinal],
        "source_sha256": _sha(_SLIDE_PATHS[source_ordinal]),
        "matched_anchors": (f"anchor for {unit_id} on slide {source_ordinal}",),
        "cluster_id": f"c-{unit_id}",
        "cluster_role": "head",
        "parent_unit_id": None,
    }


def _interstitial_row(
    unit_id: str, final_ordinal: int, parent: dict[str, Any]
) -> dict[str, Any]:
    return {
        **parent,
        "final_slide_id": f"slide-{final_ordinal:02d}",
        "unit_id": unit_id,
        "matched_anchors": (f"interstitial anchor for {unit_id}",),
        "cluster_role": "interstitial",
        "parent_unit_id": parent["unit_id"],
    }


def _authority_map(
    rows: list[dict[str, Any]], inventory: list[dict[str, Any]]
) -> WorkbookSlideAuthorityMapV1:
    """Build a fully-validated authority map (self-digest computed, no bypass)."""
    inventory_models = tuple(
        SourceSlideInventoryEntryV1.model_validate(entry) for entry in inventory
    )
    row_models = tuple(WorkbookSlideAuthorityRowV1.model_validate(row) for row in rows)
    inventory_payload = tuple(entry.model_dump(mode="json") for entry in inventory_models)
    payload: dict[str, Any] = {
        "schema_version": "workbook-slide-authority-map.v1",
        "resolver_version": "exact-anchor-source-slide.v1",
        "manifest_digest": _sha("fixture-manifest"),
        "plan_units_digest": _sha("fixture-plan-units"),
        "plan_sidecar_digest": _sha("fixture-plan-sidecar"),
        "plan_contribution_digest": _sha("fixture-plan-contribution"),
        "package_slides_digest": _sha("fixture-package-slides"),
        "package_contribution_digest": _sha("fixture-package-contribution"),
        "source_inventory": inventory_payload,
        "source_inventory_digest": _slide_authority_canonical_digest(inventory_payload),
        "rows": tuple(row.model_dump(mode="json") for row in row_models),
    }
    payload["map_digest"] = slide_authority_digest(payload, exclude_map_digest=True)
    return WorkbookSlideAuthorityMapV1.model_validate(
        {**payload, "source_inventory": inventory_models, "rows": row_models}
    )


def _live_shape_map() -> WorkbookSlideAuthorityMapV1:
    """The 8-row a940c5eb authority shape: 6 heads + u03i1/u03i2 interstitials."""
    u03 = _head_row("u03", 3, 3)
    rows = [
        _head_row("u01", 1, 1),
        _head_row("u02", 2, 2),
        u03,
        _interstitial_row("u03i1", 4, u03),
        _interstitial_row("u03i2", 5, u03),
        _head_row("u04", 6, 4),
        _head_row("u05", 7, 5),
        _head_row("u06", 8, 6),
    ]
    inventory = [_inventory_entry(ordinal) for ordinal in range(1, 7)]
    return _authority_map(rows, inventory)


def _live_shape_card() -> dict[str, Any]:
    """A g0-enrichment card mirroring the run's provenance + LO/source bindings."""
    return {
        "provisional_los": [
            {
                "objective_id": lo_id,
                "statement": f"SENTINEL-{lo_id} statement grounded in {src_id}",
                "source_refs": [{"source_id": src_id}],
            }
            for lo_id, src_id in _LO_TO_SRC.items()
        ],
        "enumeration_provenance": [
            {
                "source_id": src_id,
                "root_id": "fixture-root",
                "connector": "local_file",
                "locator": locator,
            }
            for src_id, locator in _G0_LOCATORS.items()
        ],
        "typed_components": [],
        "pedagogy_annotations": [],
        "citation_resolutions": [],
    }


def _lesson_plan(plan_units: list[dict[str, Any]]) -> dict[str, Any]:
    return {"plan_units": plan_units, "lesson_summary": "bridge fixture lesson"}


# Numeral-free corpus + narration (G1 non-event; same discipline as the 36-40
# terminal-fix module).
_CORPUS = "The clinician diagnoses the operational root cause before buying a fix.\n"
_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": "Innovating inside the hospital means navigating legacy systems.",
    },
    {
        "segment_id": "seg-02",
        "id": "seg-02",
        "slide_id": "slide-02",
        "narration_text": "Fall in love with the problem before committing to any solution.",
    },
]


def _make_run_dir(
    root: Path,
    *,
    collateral: dict[str, Any],
    plan_units: list[dict[str, Any]],
    enrichment_card: dict[str, Any] | None = None,
) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _SEGMENTS}, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "bundle" / "extracted.md").write_text(_CORPUS, encoding="utf-8")
    if enrichment_card is not None:
        (run_dir / "g0-enrichment.json").write_text(
            json.dumps(enrichment_card), encoding="utf-8"
        )
    write_run_json(run_dir, collateral=collateral, plan_units=plan_units)
    return run_dir


def _six_section_collateral() -> dict[str, Any]:
    return collateral_present(
        [
            section(
                f"sec-{unit_id}",
                unit_id,
                title=f"Section for {unit_id}",
                deferred_depth=f"Read-channel depth for {unit_id}.",
                narrative_intent=f"Narrative for {unit_id}.",
            )
            for unit_id in _EXPECTED_HEAD_MAP
        ]
    )


# --------------------------------------------------------------------------- #
# Matrix row 1 — live-run shape (a940c5eb): 6/6 resolve via the authority join #
# --------------------------------------------------------------------------- #


def test_live_run_shape_resolves_all_units_via_authority_join() -> None:
    """No markers anywhere; the authority join alone resolves every unit."""
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS),
        _live_shape_card(),
        authority_map=_live_shape_map(),
    )
    assert mapping == {
        **_EXPECTED_HEAD_MAP,
        # Interstitials ride their parent's LO (matrix row 9; harmless — only
        # section-bound objectives render).
        "u03i1": "lo-g0-007",
        "u03i2": "lo-g0-007",
    }


def test_live_run_shape_build_resolves_six_statements_and_records_no_loss(
    tmp_path: Path,
) -> None:
    """End-to-end producer inputs: 6/6 real LO statements; lo_overlay_loss None."""
    run_dir = _make_run_dir(
        tmp_path,
        collateral=_six_section_collateral(),
        plan_units=_MARKERLESS_PLAN_UNITS,
        enrichment_card=_live_shape_card(),
    )
    write_or_validate_slide_authority_map(run_dir, _live_shape_map())

    inputs = wb_act.build_workbook_inputs(run_dir, run_id="bridge-live-shape")

    assert inputs is not None
    briefs = {lo.objective_id: lo for lo in inputs.learning_objectives}
    assert set(briefs) == set(_EXPECTED_HEAD_MAP)
    for unit_id, lo_id in _EXPECTED_HEAD_MAP.items():
        # Value assertion: each unit carries ITS OWN overlay LO statement
        # (re-keyed onto the bound uNN id), not a neighbor's and no placeholder.
        assert f"SENTINEL-{lo_id}" in briefs[unit_id].statement
        assert "objective statement unresolved" not in briefs[unit_id].statement
    assert inputs.lo_overlay_loss is None


# --------------------------------------------------------------------------- #
# Matrix row 2 — cross-namespace trap: authority join WINS over a marker      #
# --------------------------------------------------------------------------- #


def test_cross_namespace_trap_authority_join_wins_over_marker() -> None:
    """A plan-unit marker ``src-001`` (G0: an assessments file) must NOT win.

    Texas's marker namespace enumerates slides only, so its ``src-001`` means
    slide 1 — but G0's ``src-001`` is ``assessments/chapter-2-knowledge-check.md``
    (lo-g0-001). The authority row (u01 -> slides/slide-1-… -> src-006) must
    produce lo-g0-005; a marker gap-fill would mis-attach lo-g0-001.
    """
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": ["# **Slide 1** dual-axis chart. [evidence: src-001]"],
        }
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(plan_units), _live_shape_card(), authority_map=_live_shape_map()
    )
    assert mapping["u01"] == "lo-g0-005"
    assert mapping["u01"] != "lo-g0-001"


# --------------------------------------------------------------------------- #
# Matrix row 3 — authority map absent: legacy marker bridge, byte-identical   #
# --------------------------------------------------------------------------- #


def test_map_absent_legacy_marker_bridge_resolves_as_before() -> None:
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": ["- **Visual Format:** Dual-Axis chart. [evidence: src-006]"],
        }
    ]
    # Two-argument call: the pre-fix signature still resolves via markers.
    mapping = wb_act._unit_to_enrichment_lo_map(_lesson_plan(plan_units), _live_shape_card())
    assert mapping == {"u01": "lo-g0-005"}
    # Explicit None is the same legacy branch.
    assert (
        wb_act._unit_to_enrichment_lo_map(
            _lesson_plan(plan_units), _live_shape_card(), authority_map=None
        )
        == mapping
    )


# --------------------------------------------------------------------------- #
# Matrix row 4 — both absent: empty map (placeholders + loss downstream)      #
# --------------------------------------------------------------------------- #


def test_no_map_and_no_markers_yields_empty_map() -> None:
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), _live_shape_card(), authority_map=None
    )
    assert mapping == {}


# --------------------------------------------------------------------------- #
# Matrix row 5 — malformed sidecar: treated as absent at the call-site seam   #
# --------------------------------------------------------------------------- #


def test_corrupt_sidecar_falls_back_to_marker_bridge_without_crashing(
    tmp_path: Path,
) -> None:
    """The guarded loader (SlideAuthorityInvalidError only) degrades to legacy."""
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": ["Dual-axis chart. [evidence: src-006]"],
        }
    ]
    run_dir = _make_run_dir(
        tmp_path,
        collateral=collateral_present([section("sec-u01", "u01")]),
        plan_units=plan_units,
        enrichment_card=_live_shape_card(),
    )
    (run_dir / SLIDE_AUTHORITY_FILENAME).write_text(
        '{"schema_version": "workbook-slide-authority-map.v1", CORRUPT', encoding="utf-8"
    )

    inputs = wb_act.build_workbook_inputs(run_dir, run_id="bridge-corrupt-sidecar")

    assert inputs is not None
    lo = next(o for o in inputs.learning_objectives if o.objective_id == "u01")
    # Exactly as if the map were absent: the marker bridge resolved the LO.
    assert "SENTINEL-lo-g0-005" in lo.statement
    assert inputs.lo_overlay_loss is None


# --------------------------------------------------------------------------- #
# Matrix row 6 — map present + provenance absent: NO marker gap-fill          #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("provenance", [None, []], ids=["key-absent", "empty-list"])
def test_map_present_provenance_absent_yields_empty_map_without_marker_gap_fill(
    provenance: list[dict[str, Any]] | None,
) -> None:
    """Structural precedence: markers exist but must NOT gap-fill (empty, no crash)."""
    card = _live_shape_card()
    if provenance is None:
        del card["enumeration_provenance"]
    else:
        card["enumeration_provenance"] = provenance
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": ["Dual-axis chart. [evidence: src-006]"],
        }
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(plan_units), card, authority_map=_live_shape_map()
    )
    assert mapping == {}


def test_map_present_provenance_absent_records_visible_loss_on_build(
    tmp_path: Path,
) -> None:
    """Build path: valid sidecar + provenance-less card => placeholder + loss.

    The plan unit carries a marker that WOULD resolve under the legacy bridge —
    proving the seam disables marker gap-fill when the map is present (W1).
    """
    card = _live_shape_card()
    del card["enumeration_provenance"]
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": ["Dual-axis chart. [evidence: src-006]"],
        }
    ]
    run_dir = _make_run_dir(
        tmp_path,
        collateral=collateral_present([section("sec-u01", "u01")]),
        plan_units=plan_units,
        enrichment_card=card,
    )
    write_or_validate_slide_authority_map(run_dir, _live_shape_map())

    inputs = wb_act.build_workbook_inputs(run_dir, run_id="bridge-half-state")

    assert inputs is not None
    lo = next(o for o in inputs.learning_objectives if o.objective_id == "u01")
    assert "objective statement unresolved" in lo.statement
    assert inputs.lo_overlay_loss is not None
    assert inputs.lo_overlay_loss["unresolved_count"] == 1
    assert "u01" in inputs.lo_overlay_loss["unresolved_objectives"]


# --------------------------------------------------------------------------- #
# Matrix row 7 — locator/path mismatch: unresolved, NO fallback (W2 pin)      #
# --------------------------------------------------------------------------- #


def test_locator_mismatch_stays_unresolved_with_no_marker_fallback() -> None:
    """Traversal-root-relative locators do NOT join — and nobody may "fix" this
    with suffix/fuzzy matching (exact posix-normalized equality only).
    """
    card = _live_shape_card()
    card["enumeration_provenance"] = [
        {
            "source_id": src_id,
            "root_id": "fixture-root",
            "connector": "local_file",
            # Root-relative form: exact-equality join must NOT suffix-match it.
            "locator": f"course-content/courses/tejal-apc-c1-m1-p2-trends/{locator}",
        }
        for src_id, locator in _G0_LOCATORS.items()
    ]
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": ["Dual-axis chart. [evidence: src-006]"],
        }
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(plan_units), card, authority_map=_live_shape_map()
    )
    assert mapping == {}


# --------------------------------------------------------------------------- #
# Matrix row 8 — backslashed / ./-prefixed paths normalize byte-identically   #
# --------------------------------------------------------------------------- #


def test_backslashed_and_dot_prefixed_locators_join_after_normalization() -> None:
    card = _live_shape_card()
    card["enumeration_provenance"] = [
        {
            "source_id": "src-006",
            "root_id": "fixture-root",
            "connector": "local_file",
            "locator": _SLIDE_PATHS[1].replace("/", "\\"),  # slides\slide-1-…md
        },
        {
            "source_id": "src-007",
            "root_id": "fixture-root",
            "connector": "local_file",
            "locator": f"./{_SLIDE_PATHS[2]}",  # ./slides/slide-2-…md
        },
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), card, authority_map=_live_shape_map()
    )
    assert mapping["u01"] == "lo-g0-005"
    assert mapping["u02"] == "lo-g0-006"


# --------------------------------------------------------------------------- #
# Matrix row 9 — interstitial units map to the parent's LO                    #
# --------------------------------------------------------------------------- #


def test_interstitial_units_map_to_parent_lo() -> None:
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS),
        _live_shape_card(),
        authority_map=_live_shape_map(),
    )
    assert mapping["u03"] == "lo-g0-007"
    assert mapping["u03i1"] == "lo-g0-007"
    assert mapping["u03i2"] == "lo-g0-007"


# --------------------------------------------------------------------------- #
# Matrix row 10 — first-LO-wins per src (stable duplicate discipline)         #
# --------------------------------------------------------------------------- #


def test_first_lo_wins_when_one_src_is_bound_by_multiple_los() -> None:
    card = _live_shape_card()
    card["provisional_los"].append(
        {
            "objective_id": "lo-g0-099",
            "statement": "SENTINEL-lo-g0-099 duplicate binding of src-006",
            "source_refs": [{"source_id": "src-006"}],
        }
    )
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), card, authority_map=_live_shape_map()
    )
    assert mapping["u01"] == "lo-g0-005"  # first LO binding src-006 wins


def test_one_lo_binding_multiple_srcs_resolves_each_unit_to_that_lo() -> None:
    card = _live_shape_card()
    card["provisional_los"] = [
        {
            "objective_id": "lo-g0-005",
            "statement": "SENTINEL-lo-g0-005 spans slides one and two",
            "source_refs": [{"source_id": "src-006"}, {"source_id": "src-007"}],
        }
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), card, authority_map=_live_shape_map()
    )
    assert mapping["u01"] == "lo-g0-005"
    assert mapping["u02"] == "lo-g0-005"


# --------------------------------------------------------------------------- #
# Offline replay probe — the REAL a940c5eb artifacts via production loaders   #
# --------------------------------------------------------------------------- #


def test_offline_replay_probe_real_run_a940c5eb_resolves_exact_map() -> None:
    """Environment-guarded floor on the real run (party M3): production loaders
    only (never hand-parsed JSON), asserting the spec's exact expected join.
    """
    if not _REAL_RUN_DIR.is_dir():
        pytest.skip("run a940c5eb artifacts unavailable")

    # A partial evidence dir (present but missing/invalid artifacts) must SKIP,
    # not hard-fail — the probe floors the join, not the dir's completeness.
    try:
        authority_map = read_slide_authority_map(_REAL_RUN_DIR)
    except SlideAuthorityInvalidError:
        pytest.skip("run a940c5eb slide-authority sidecar unavailable")
    card = load_enrichment_card(_REAL_RUN_DIR)
    lesson_plan = lesson_plan_from_run(_REAL_RUN_DIR)
    if card is None or lesson_plan is None:
        pytest.skip("run a940c5eb enrichment/lesson-plan artifacts unavailable")

    mapping = wb_act._unit_to_enrichment_lo_map(
        lesson_plan, card, authority_map=authority_map
    )

    # The spec's exact six-unit map (Design Notes, run-verified)...
    assert {k: v for k, v in mapping.items() if k in _EXPECTED_HEAD_MAP} == _EXPECTED_HEAD_MAP
    # ...plus the run's two interstitials riding their parent's LO (matrix row 9).
    assert mapping == {**_EXPECTED_HEAD_MAP, "u03i1": "lo-g0-007", "u03i2": "lo-g0-007"}


# --------------------------------------------------------------------------- #
# T4 review patches — hardening pins added at step-04 adversarial review      #
# --------------------------------------------------------------------------- #


def test_legacy_marker_bridge_multi_ref_multi_marker_first_match_semantics() -> None:
    """Characterize the legacy loop (map absent): first RESOLVING marker wins.

    Semantics under characterization (byte-identical to pre-38.3a): refs scan in
    order; within a ref, markers scan in order and the first marker whose src
    resolves in ``src_to_lo`` wins; remaining refs are skipped after a match; an
    unresolvable marker earlier in the same ref does NOT block a later one.
    """
    plan_units = [
        {
            "unit_id": "u01",
            "cluster_role": "head",
            "source_refs": [
                "no marker in this ref at all",
                # src-999 is unknown; src-007 resolves -> lo-g0-006 must win.
                "[evidence: src-999] then [evidence: src-007] then [evidence: src-006]",
                # A later ref with a different resolvable marker must be ignored.
                "[evidence: src-011]",
            ],
        }
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(plan_units), _live_shape_card(), authority_map=None
    )
    assert mapping == {"u01": "lo-g0-006"}


def test_duplicate_normalized_locator_conflict_resolves_nothing_for_that_path() -> None:
    """Two provenance entries collapsing to ONE normalized key with DIFFERENT
    source_ids poison that key: visible unresolved beats ordering-dependent
    silently-wrong (T4 review). Other units keep resolving normally."""
    card = _live_shape_card()
    slide1 = "slides/slide-1-the-economic-structural-reality.md"
    card["enumeration_provenance"] = [
        entry
        for entry in card["enumeration_provenance"]
        if entry["locator"] != slide1
    ] + [
        {
            "source_id": "src-006",
            "root_id": "fixture-root",
            "connector": "local_file",
            "locator": slide1,
        },
        {
            "source_id": "src-007",
            "root_id": "fixture-root",
            "connector": "local_file",
            "locator": ".\\" + slide1.replace("/", "\\"),
        },
    ]
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), card, authority_map=_live_shape_map()
    )
    assert "u01" not in mapping  # poisoned key resolves nothing
    assert mapping["u02"] == "lo-g0-006"  # unaffected units still resolve
    # Same-source duplicate is NOT a conflict: no poisoning, u01 resolves.
    card2 = _live_shape_card()
    card2["enumeration_provenance"].append(
        {
            "source_id": "src-006",
            "root_id": "fixture-root",
            "connector": "local_file",
            "locator": ".\\" + slide1.replace("/", "\\"),
        }
    )
    mapping2 = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), card2, authority_map=_live_shape_map()
    )
    assert mapping2["u01"] == "lo-g0-005"


def test_authority_join_survives_non_dict_lesson_plan() -> None:
    """The authority branch reads only (map, card): a None/non-dict lesson plan
    must not disable an otherwise-resolvable authority join (T4 review)."""
    for lesson_plan in (None, "not-a-dict", 7):
        mapping = wb_act._unit_to_enrichment_lo_map(
            lesson_plan,  # type: ignore[arg-type]
            _live_shape_card(),
            authority_map=_live_shape_map(),
        )
        assert {k: v for k, v in mapping.items() if k in _EXPECTED_HEAD_MAP} == (
            _EXPECTED_HEAD_MAP
        )
    # The LEGACY branch still requires a dict lesson plan.
    assert (
        wb_act._unit_to_enrichment_lo_map(None, _live_shape_card(), authority_map=None)
        == {}
    )


@pytest.mark.parametrize("bad_provenance", [7, True, 3.5, "junk", {"a": 1}])
def test_non_list_enumeration_provenance_degrades_to_empty_map(
    bad_provenance: Any,
) -> None:
    """A truthy non-list ``enumeration_provenance`` must degrade (empty map),
    never raise TypeError out of the 07W leaf (T4 review)."""
    card = _live_shape_card()
    card["enumeration_provenance"] = bad_provenance
    mapping = wb_act._unit_to_enrichment_lo_map(
        _lesson_plan(_MARKERLESS_PLAN_UNITS), card, authority_map=_live_shape_map()
    )
    assert mapping == {}
