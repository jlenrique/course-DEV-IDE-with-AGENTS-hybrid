"""P3 — Irene pass-1 pedagogical annotation overlay (offline surface).

Murat's full RED-first surface: 10 offline behavioural specs + 3 M5 fault gates
that prove the wiring-time end-to-end guard fires. NO live LLM/network — the
offline deterministic pass is what these exercise (the live leg is the
orchestrator's job).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.g0_enrichment import (
    CitationResolution,
    Dissent,
    G0EnrichmentResult,
    IndependentParse,
    ReconcileView,
)
from app.marcus.lesson_plan.learning_objective import LearningObjective
from app.marcus.lesson_plan.pedagogy_annotation import (
    LOAD_BEARING_TYPES,
    SKIP_TYPES,
    PedagogyAnnotation,
    _build_live_annotations,
    _extract_pedagogy_rows,
    _normalize_enum_value,
    assert_p2_frontmatter_present,
    assert_pedagogy_referential_invariant,
    assert_pedagogy_teachable_consistency,
    build_pedagogy_annotations,
    compute_teaches_after,
    derive_teachable,
    is_annotatable,
    load_pedagogy_annotation,
    pedagogy_annotation_json_schema,
)
from app.marcus.lesson_plan.source_type import SOURCE_TYPES, TypedComponent
from app.marcus.orchestrator import g0_enrichment_wiring as gw

_FIXED_TS = datetime(2026, 6, 27, 12, 0, 0, tzinfo=UTC)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CORPUS = _REPO_ROOT / "tests" / "fixtures" / "pass0_citation_corpus"


# --------------------------------------------------------------------------- #
# Builders
# --------------------------------------------------------------------------- #


def _tc(component_id: str, *, source_type: str = "slide", parent: str = "src-001",
        locator: str = "Doc > X", flagged_ungrounded: bool = False) -> TypedComponent:
    return TypedComponent(
        component_id=component_id,
        parent_source_id=parent,
        source_type=source_type,  # type: ignore[arg-type]
        label="lbl",
        locator=locator,
        excerpt="verbatim excerpt",
        flagged_ungrounded=flagged_ungrounded,
    )


def _lo(objective_id: str) -> LearningObjective:
    return LearningObjective(
        objective_id=objective_id, statement="s", status="provisional", confidence="low"
    )


def _ann(component_id: str = "src-001-c001", **over: object) -> PedagogyAnnotation:
    base: dict[str, object] = dict(
        component_id=component_id,
        bloom="understand",
        pedagogical_role="definition",
        teachable=True,
        rationale="r",
        generated_at=_FIXED_TS,
    )
    base.update(over)
    return PedagogyAnnotation(**base)  # type: ignore[arg-type]


def _result(
    typed: list[TypedComponent],
    los: list[LearningObjective],
    anns: list[PedagogyAnnotation],
) -> G0EnrichmentResult:
    parents = {t.parent_source_id for t in typed}
    return G0EnrichmentResult(
        corpus_fingerprint="f" * 64,
        model_id="offline-marker",
        typed_components=typed,
        provisional_los=los,
        reconcile=ReconcileView(
            n_files_in=len(parents),
            n_files_covered=len(parents),
            n_files_ignored=0,
            n_components=len(typed),
            n_flagged=sum(1 for t in typed if t.flagged_unconsumed),
        ),
        dissents=[Dissent(against="src-001", marcus_position="a defensible alternative")],
        pedagogy_annotations=tuple(anns),
        independent_parse=IndependentParse(proposal={}, ts=_FIXED_TS),
    )


def _rec(component_id: str, *, type: str = "slide", doc_ordinal: int = 1,
         resolution_status: str = "resolved", locator: str = "Doc > X",
         provisional_los: list[str] | None = None) -> dict[str, object]:
    return {
        "component_id": component_id,
        "type": type,
        "doc_ordinal": doc_ordinal,
        "resolution_status": resolution_status,
        "locator": locator,
        "provisional_los": provisional_los or [],
    }


# =========================================================================== #
# 1 — lo_refs ⊆ provisional_los.objective_id (wiring referential invariant)
# =========================================================================== #


def test_1_lo_refs_must_be_subset_of_provisional_los() -> None:
    typed = [_tc("src-001-c001")]
    los = [_lo("lo-g0-001")]
    # RED: a fabricated lo_ref not in the LO set.
    bad = _result(typed, los, [_ann(lo_refs=("lo-g0-999",))])
    with pytest.raises(ValueError, match="lo_ref"):
        assert_pedagogy_referential_invariant(bad)
    # GREEN: a valid subset passes.
    ok = _result(typed, los, [_ann(lo_refs=("lo-g0-001",))])
    assert_pedagogy_referential_invariant(ok)


# =========================================================================== #
# 2 — assessment_link ∈ component_ids ∪ {None}
# =========================================================================== #


def test_2_assessment_link_must_be_a_component_or_none() -> None:
    typed = [_tc("src-001-c001"), _tc("src-001-c002")]
    los: list[LearningObjective] = []
    with pytest.raises(ValueError, match="assessment_link"):
        assert_pedagogy_referential_invariant(
            _result(typed, los, [_ann(assessment_link="ghost")])
        )
    assert_pedagogy_referential_invariant(
        _result(typed, los, [_ann(assessment_link="src-001-c002")])
    )
    assert_pedagogy_referential_invariant(_result(typed, los, [_ann(assessment_link=None)]))


# =========================================================================== #
# 3 — teaches_after ids must exist
# =========================================================================== #


def test_3_teaches_after_ids_must_exist() -> None:
    typed = [_tc("src-001-c001")]
    with pytest.raises(ValueError, match="teaches_after"):
        assert_pedagogy_referential_invariant(
            _result(typed, [], [_ann(teaches_after=("does-not-exist",))])
        )


# =========================================================================== #
# 4 — closed-enum 3-surface red-reject for bloom + pedagogical_role
# =========================================================================== #


def test_4_bloom_red_reject_construction() -> None:
    with pytest.raises(ValidationError):
        _ann(bloom="synthesizing")


def test_4_bloom_red_reject_json_schema_enum() -> None:
    enum = pedagogy_annotation_json_schema()["properties"]["bloom"]["enum"]
    assert "synthesizing" not in enum
    assert "understand" in enum


def test_4_bloom_red_reject_rehydration_loader() -> None:
    payload = _ann().model_dump(mode="json")
    payload["bloom"] = "synthesizing"
    with pytest.raises(ValidationError):
        load_pedagogy_annotation(payload)


def test_4_role_red_reject_construction() -> None:
    with pytest.raises(ValidationError):
        _ann(pedagogical_role="lecturing")


def test_4_role_red_reject_json_schema_enum() -> None:
    enum = pedagogy_annotation_json_schema()["properties"]["pedagogical_role"]["enum"]
    assert "lecturing" not in enum
    assert "assessment" in enum


def test_4_role_red_reject_rehydration_loader() -> None:
    payload = _ann().model_dump(mode="json")
    payload["pedagogical_role"] = "lecturing"
    with pytest.raises(ValidationError):
        load_pedagogy_annotation(payload)


# =========================================================================== #
# 5 — teachable derivation + M8 divergence (front-matter wins)
# =========================================================================== #


def test_5_teachable_derivation() -> None:
    assert derive_teachable("ungrounded") is False
    assert derive_teachable("failed") is False
    assert derive_teachable("resolved") is True


def test_5_frontmatter_resolution_status_wins_over_citation() -> None:
    # A flagged_ungrounded component whose citation verdict says "resolved": the
    # FRONT-MATTER resolution_status must win (M8) → ungrounded → teachable False.
    comp = _tc("src-001-c001", flagged_ungrounded=True)
    citation = CitationResolution(
        component_id="src-001-c001",
        resolution_status="resolved",
        resolved_ref={"title": "t", "doi": "10.1/x", "access_url": "u"},
    )
    records = gw._build_pedagogy_frontmatter([comp], (citation,), [])
    assert records[0]["resolution_status"] == "ungrounded"  # front matter, not citation
    assert derive_teachable(records[0]["resolution_status"]) is False
    anns = build_pedagogy_annotations(records, [], generated_at=_FIXED_TS)
    assert anns[0].teachable is False


# =========================================================================== #
# 6 — teaches_after determinism + mandatory tie fixture (locator secondary key)
# =========================================================================== #


def test_6_teaches_after_is_byte_identical_across_runs() -> None:
    recs = [_rec(f"c{i}", doc_ordinal=i, locator=f"L{i}") for i in range(1, 6)]
    target = recs[3]
    assert compute_teaches_after(target, recs) == compute_teaches_after(target, recs)
    assert compute_teaches_after(target, recs) == ("c1", "c2", "c3")
    # whole-build determinism (fixed generated_at) → byte-identical annotation set.
    a = build_pedagogy_annotations(recs, [], generated_at=_FIXED_TS)
    b = build_pedagogy_annotations(recs, [], generated_at=_FIXED_TS)
    assert a == b


def test_6_tie_breaks_on_locator_then_stable() -> None:
    # Two components in the SAME file with EQUAL doc_ordinal: locator is the
    # secondary key. "A-earlier" < "Z-later" → c-b precedes c-a deterministically.
    rec_a = _rec("c-a", doc_ordinal=5, locator="Z-later")
    rec_b = _rec("c-b", doc_ordinal=5, locator="A-earlier")
    both = [rec_a, rec_b]
    assert compute_teaches_after(rec_a, both) == ("c-b",)  # b ordered before a
    assert compute_teaches_after(rec_b, both) == ()  # nothing before b
    # stable across argument order.
    assert compute_teaches_after(rec_a, [rec_b, rec_a]) == ("c-b",)


# =========================================================================== #
# 7 — pre-flight hard-fail on raw source (3 sub-fixtures), BEFORE annotation
# =========================================================================== #


def test_7_preflight_missing_doc_ordinal_is_hard_fail() -> None:
    rec = _rec("c1")
    del rec["doc_ordinal"]
    with pytest.raises(ValueError, match="doc_ordinal"):
        build_pedagogy_annotations([rec], [])


def test_7_preflight_missing_resolution_status_is_hard_fail() -> None:
    rec = _rec("c1")
    del rec["resolution_status"]
    with pytest.raises(ValueError, match="resolution_status"):
        build_pedagogy_annotations([rec], [])


def test_7_preflight_provisional_los_lacking_objective_id_is_hard_fail() -> None:
    with pytest.raises(ValueError, match="objective_id"):
        build_pedagogy_annotations([_rec("c1")], [{"statement": "no id"}])


def test_7_preflight_rejects_non_numeric_doc_ordinal() -> None:
    with pytest.raises(ValueError, match="doc_ordinal"):
        assert_p2_frontmatter_present([_rec("c1", doc_ordinal="3")], [])  # type: ignore[arg-type]


# =========================================================================== #
# 8 — rationale required + bounded (<=240)
# =========================================================================== #


def test_8_rationale_empty_is_red() -> None:
    with pytest.raises(ValidationError):
        _ann(rationale="")
    with pytest.raises(ValidationError):
        _ann(rationale="   ")


def test_8_rationale_too_long_is_red() -> None:
    with pytest.raises(ValidationError):
        _ann(rationale="x" * 241)


def test_8_rationale_valid_bounded_is_green() -> None:
    ann = _ann(rationale="x" * 240)
    assert len(ann.rationale) == 240


# =========================================================================== #
# 9 — coverage/skip determinism (7 annotated, 3 skipped)
# =========================================================================== #


def test_9_coverage_annotates_load_bearing_skips_skip_types() -> None:
    assert LOAD_BEARING_TYPES.isdisjoint(SKIP_TYPES)
    records = []
    ordinal = 1
    for t in sorted(LOAD_BEARING_TYPES) + sorted(SKIP_TYPES):
        records.append(_rec(f"c-{t}", type=t, doc_ordinal=ordinal))
        ordinal += 1
    anns = build_pedagogy_annotations(records, [], generated_at=_FIXED_TS)
    annotated = {a.component_id for a in anns}
    assert annotated == {f"c-{t}" for t in LOAD_BEARING_TYPES}
    for t in SKIP_TYPES:
        assert is_annotatable(t) is False
        assert f"c-{t}" not in annotated
    assert len(anns) == len(LOAD_BEARING_TYPES)


# =========================================================================== #
# 10 — companion-removed regression (explicit reject, not silent drop)
# =========================================================================== #


def test_10_companion_absent_from_schema() -> None:
    assert "companion" not in pedagogy_annotation_json_schema()["properties"]


def test_10_companion_payload_is_rejected_not_dropped() -> None:
    payload = _ann().model_dump(mode="json")
    payload["companion"] = {"anything": "here"}
    with pytest.raises(ValidationError):
        load_pedagogy_annotation(payload)
    with pytest.raises(ValidationError):
        _ann(companion="x")


# =========================================================================== #
# M5 fault gates — prove the end-to-end guard fires
# =========================================================================== #


def test_m5a_fabricated_lo_ref_red_at_assemble_validate_path() -> None:
    result = _result([_tc("src-001-c001")], [_lo("lo-g0-001")],
                     [_ann(lo_refs=("lo-g0-002",))])
    with pytest.raises(ValueError, match="lo_ref"):
        assert_pedagogy_referential_invariant(result)


def test_m5b_fabricated_assessment_link_red_at_assemble_validate_path() -> None:
    result = _result([_tc("src-001-c001")], [], [_ann(assessment_link="src-999-c999")])
    with pytest.raises(ValueError, match="assessment_link"):
        assert_pedagogy_referential_invariant(result)


def test_m5c_teachable_tamper_contradiction_is_red() -> None:
    # Force teachable=True on a front-matter-`failed` component → the consistency
    # check catches the contradiction the build path can never produce.
    records = [_rec("src-001-c001", resolution_status="failed")]
    tampered = [_ann("src-001-c001", teachable=True)]
    with pytest.raises(ValueError, match="teachable contradiction"):
        assert_pedagogy_teachable_consistency(tampered, records)
    # The honest build yields teachable=False for the same component (no contradiction).
    honest = build_pedagogy_annotations(records, [], generated_at=_FIXED_TS)
    assert honest[0].teachable is False
    assert_pedagogy_teachable_consistency(honest, records)


# =========================================================================== #
# MF-2 — taxonomy partition is exhaustive + disjoint over the closed source set
# =========================================================================== #


def test_mf2_partition_is_exhaustive_and_disjoint() -> None:
    # Exhaustive over the closed source taxonomy + the 'other' escape hatch, and
    # disjoint. A future taxonomy addition fails RED here until P3 assigns it.
    assert LOAD_BEARING_TYPES.isdisjoint(SKIP_TYPES)
    assert (SOURCE_TYPES | {"other"}) == (LOAD_BEARING_TYPES | SKIP_TYPES)


def test_mf2_specific_dispositions() -> None:
    # Marcus-ruled dispositions.
    assert "exercise_lab" in LOAD_BEARING_TYPES  # hands-on instructional activity
    assert "rubric" in SKIP_TYPES  # grading instrument; pointed-at, not taught
    # 'learning_objective' is a phantom — NOT a member of the closed source set.
    assert "learning_objective" not in (LOAD_BEARING_TYPES | SKIP_TYPES)
    assert "learning_objective" not in SOURCE_TYPES
    assert len(LOAD_BEARING_TYPES) == 8
    assert len(SKIP_TYPES) == 3
    assert is_annotatable("exercise_lab") is True
    assert is_annotatable("rubric") is False


# =========================================================================== #
# MF-1 — live per-row guard: one bad LLM field never aborts the whole pass
# =========================================================================== #


def _live_recs() -> list[dict[str, object]]:
    return [
        _rec("c1", type="slide", doc_ordinal=1),
        _rec("c2", type="quiz", doc_ordinal=2),
        _rec("c3", type="workbook", doc_ordinal=3),
        _rec("c4", type="slide", doc_ordinal=4),
    ]


def test_mf1_live_loop_salvages_near_misses_and_skips_unsalvageable() -> None:
    recs = _live_recs()
    by_id = {r["component_id"]: r for r in recs}
    rows = [
        # good row
        {"component_id": "c1", "bloom": "understand",
         "pedagogical_role": "definition", "rationale": "ok"},
        # out-of-vocab bloom -> clamps to the offline default for a quiz (apply)
        {"component_id": "c2", "bloom": "comprehension", "pedagogical_role": "assessment"},
        # space-in-role -> normalized to worked_example (valid)
        {"component_id": "c3", "bloom": "apply", "pedagogical_role": "worked example"},
        # missing bloom -> falls back to the offline default for a slide (understand)
        {"component_id": "c4", "pedagogical_role": "definition"},
        # missing component_id -> unsalvageable -> skipped (not raised)
        {"bloom": "understand", "pedagogical_role": "definition"},
    ]
    anns = _build_live_annotations(
        rows,
        by_id=by_id,
        valid_lo_ids=set(),
        component_ids=set(by_id),
        components=recs,
        transform_version="ped-v1",
        when=_FIXED_TS,
    )
    by_cid = {a.component_id for a in anns}
    assert by_cid == {"c1", "c2", "c3", "c4"}  # all 4 salvaged, 5th skipped
    assert len(anns) == 4
    got = {a.component_id: a for a in anns}
    assert got["c2"].bloom == "apply"  # clamped bloom -> quiz offline default
    assert got["c3"].pedagogical_role == "worked_example"  # space normalized
    assert got["c4"].bloom == "understand"  # missing bloom -> slide offline default


def test_live_salvages_component_id_echoed_as_whole_line() -> None:
    # LIVE-FOUND (Stage-1): the model sometimes echoes the entire Components line
    # ("c1 (type=slide, locator=…)") as component_id. The parser must salvage the
    # leading token and still produce the annotation, not skip the row.
    recs = [_rec("c1", type="slide", doc_ordinal=1)]
    rows = [
        {"component_id": "c1 (type=slide, locator=Part 1 > Page 3 > Slide 1)",
         "bloom": "understand", "pedagogical_role": "definition"},
    ]
    anns = _build_live_annotations(
        rows, by_id={"c1": recs[0]}, valid_lo_ids=set(), component_ids={"c1"},
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert len(anns) == 1
    assert anns[0].component_id == "c1"  # salvaged to the bare id


def test_mf1_one_bad_role_does_not_abort_the_pass() -> None:
    # A row whose role is unsalvageable still produces a valid annotation (falls
    # back to the offline default) rather than aborting every other annotation.
    recs = [_rec("c1", type="slide", doc_ordinal=1)]
    rows = [{"component_id": "c1", "bloom": "understand", "pedagogical_role": "lecturing"}]
    anns = _build_live_annotations(
        rows, by_id={"c1": recs[0]}, valid_lo_ids=set(), component_ids={"c1"},
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert len(anns) == 1
    assert anns[0].pedagogical_role == "definition"  # slide offline default


# =========================================================================== #
# S-1 — tolerant JSON extraction (fences / prose / content-blocks / degrade)
# =========================================================================== #


def test_s1_strips_json_code_fences() -> None:
    content = '```json\n{"annotations": [{"component_id": "c1"}]}\n```'
    rows = _extract_pedagogy_rows(content)
    assert rows == [{"component_id": "c1"}]


def test_s1_extracts_object_from_surrounding_prose() -> None:
    content = 'Sure! Here is the result: {"annotations": []} — hope that helps.'
    assert _extract_pedagogy_rows(content) == []


def test_s1_handles_content_block_list() -> None:
    content = [{"type": "text", "text": '{"annotations": [{"component_id": "c1"}]}'}]
    assert _extract_pedagogy_rows(content) == [{"component_id": "c1"}]


def test_s1_degrades_to_empty_on_garbage_no_crash() -> None:
    assert _extract_pedagogy_rows("not json at all") == []
    assert _extract_pedagogy_rows("[1, 2, 3]") == []  # non-object payload
    assert _extract_pedagogy_rows("") == []
    assert _extract_pedagogy_rows(None) == []


def test_s1_normalize_enum_value() -> None:
    from app.marcus.lesson_plan.pedagogy_annotation import (
        PEDAGOGY_BLOOM_LEVELS,
        PEDAGOGY_ROLES,
    )

    assert _normalize_enum_value("Understand", PEDAGOGY_BLOOM_LEVELS) == "understand"
    assert _normalize_enum_value("worked example", PEDAGOGY_ROLES) == "worked_example"
    assert _normalize_enum_value("comprehension", PEDAGOGY_BLOOM_LEVELS) is None
    assert _normalize_enum_value(None, PEDAGOGY_BLOOM_LEVELS) is None


# =========================================================================== #
# S-2 / S-3 / NIT — lo_ref format filter, no char-splat, dedup
# =========================================================================== #


def test_s2_lo_ref_format_filter_drops_admitted_but_malformed_id() -> None:
    recs = [_rec("c1", type="slide", doc_ordinal=1)]
    # 'weird-id' is admitted to valid_lo_ids but fails the lo-g0-NNN format -> it
    # must drop individually (not abort construction of the whole annotation).
    rows = [{"component_id": "c1", "bloom": "understand",
             "pedagogical_role": "definition", "lo_refs": ["lo-g0-001", "weird-id"]}]
    anns = _build_live_annotations(
        rows, by_id={"c1": recs[0]}, valid_lo_ids={"lo-g0-001", "weird-id"},
        component_ids={"c1"}, components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert anns[0].lo_refs == ("lo-g0-001",)


def test_s3_string_fields_are_not_char_splatted() -> None:
    recs = [_rec("c1", type="slide", doc_ordinal=1)]
    rows = [{"component_id": "c1", "bloom": "understand", "pedagogical_role": "definition",
             "lo_refs": "lo-g0-001", "prerequisite_concepts": "abc"}]
    anns = _build_live_annotations(
        rows, by_id={"c1": recs[0]}, valid_lo_ids={"lo-g0-001"},
        component_ids={"c1"}, components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert anns[0].lo_refs == ()  # string -> () not ('l','o','-',...)
    assert anns[0].prerequisite_concepts == ()  # string -> () not ('a','b','c')


def test_nit_lo_refs_deduped() -> None:
    recs = [_rec("c1", type="slide", doc_ordinal=1)]
    rows = [{"component_id": "c1", "bloom": "understand", "pedagogical_role": "definition",
             "lo_refs": ["lo-g0-001", "lo-g0-001"]}]
    anns = _build_live_annotations(
        rows, by_id={"c1": recs[0]}, valid_lo_ids={"lo-g0-001"},
        component_ids={"c1"}, components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert anns[0].lo_refs == ("lo-g0-001",)


# =========================================================================== #
# S-4 — assessment_link: full component-id membership + self-link drop
# =========================================================================== #


def test_s4_assessment_link_against_full_component_set_and_self_link() -> None:
    recs = [_rec("c1", type="quiz", doc_ordinal=1), _rec("c2", type="slide", doc_ordinal=2)]
    by_id = {r["component_id"]: r for r in recs}  # both annotatable here
    # valid link to ANOTHER component survives
    ok = _build_live_annotations(
        [{"component_id": "c1", "bloom": "apply", "pedagogical_role": "assessment",
          "assessment_link": "c2"}],
        by_id=by_id, valid_lo_ids=set(), component_ids=set(by_id),
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert ok[0].assessment_link == "c2"
    # ghost link drops to None
    ghost = _build_live_annotations(
        [{"component_id": "c1", "bloom": "apply", "pedagogical_role": "assessment",
          "assessment_link": "ghost"}],
        by_id=by_id, valid_lo_ids=set(), component_ids=set(by_id),
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert ghost[0].assessment_link is None
    # self-link drops to None
    selfish = _build_live_annotations(
        [{"component_id": "c1", "bloom": "apply", "pedagogical_role": "assessment",
          "assessment_link": "c1"}],
        by_id=by_id, valid_lo_ids=set(), component_ids=set(by_id),
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert selfish[0].assessment_link is None


def test_s4_assessment_link_to_nonannotatable_component_survives() -> None:
    # The link target may be a NON-annotatable component (full id set, not the
    # annotatable-only set). c2 is a reference_citation (skipped) but is a real id.
    recs = [_rec("c1", type="quiz", doc_ordinal=1),
            _rec("c2", type="reference_citation", doc_ordinal=2)]
    by_id = {"c1": recs[0]}  # only annotatable rows (what the live pass passes)
    component_ids = {"c1", "c2"}  # but the FULL set includes c2
    anns = _build_live_annotations(
        [{"component_id": "c1", "bloom": "apply", "pedagogical_role": "assessment",
          "assessment_link": "c2"}],
        by_id=by_id, valid_lo_ids=set(), component_ids=component_ids,
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert anns[0].assessment_link == "c2"


# =========================================================================== #
# S-5 — fail-safe teachable whitelist (unknown status -> NOT teachable)
# =========================================================================== #


def test_s5_unknown_status_is_not_teachable_failsafe() -> None:
    assert derive_teachable("resolved") is True
    assert derive_teachable("ungrounded") is False
    assert derive_teachable("failed") is False
    assert derive_teachable("pending") is False  # unknown -> fail safe
    assert derive_teachable(None) is False


# =========================================================================== #
# NIT — pre-flight hard-fails a record missing component_id
# =========================================================================== #


def test_nit_preflight_missing_component_id_is_hard_fail() -> None:
    rec = _rec("c1")
    del rec["component_id"]
    with pytest.raises(ValueError, match="component_id"):
        assert_p2_frontmatter_present([rec], [])


# =========================================================================== #
# S-6 — build-path coverage: invariant wired in + valid link survives
# =========================================================================== #


def test_s6a_referential_invariant_is_wired_into_build_path(monkeypatch) -> None:
    # Prove assert_pedagogy_referential_invariant actually runs inside
    # build_enrichment_result: inject an annotation with a fabricated
    # assessment_link and confirm the FULL build path raises RED.
    def _fake_attach(*_a: object, **_k: object) -> tuple[PedagogyAnnotation, ...]:
        return (
            PedagogyAnnotation(
                component_id="any",
                bloom="understand",
                pedagogical_role="definition",
                teachable=True,
                rationale="fabricated",
                assessment_link="ghost-not-a-component",
                generated_at=_FIXED_TS,
            ),
        )

    monkeypatch.setattr(gw, "_attach_pedagogy_annotations", _fake_attach)
    with pytest.raises(ValueError, match="assessment_link"):
        gw.build_enrichment_result(corpus_dir=_CORPUS, dispatch_live=False)


def test_s6a_clean_offline_build_passes_the_invariant(tmp_path: Path) -> None:
    # The honest offline build path produces annotations that satisfy the
    # referential invariant (it is called inside build_enrichment_result; re-assert).
    # A tiny corpus with annotatable (keyword-typed) files so the overlay is non-empty.
    (tmp_path / "narration-intro.md").write_text("# Intro\nnarration body", encoding="utf-8")
    (tmp_path / "quiz-check.md").write_text("# Quiz\nQ1?", encoding="utf-8")
    result = gw.build_enrichment_result(corpus_dir=tmp_path, dispatch_live=False)
    assert result.pedagogy_annotations  # non-empty overlay
    assert_pedagogy_referential_invariant(result)  # no raise


def test_s6b_valid_assessment_link_survives_to_a_passing_result() -> None:
    # A valid assessment_link from the row helper rides into a result the
    # referential invariant accepts.
    typed = [_tc("src-001-c001", source_type="quiz"), _tc("src-001-c002")]
    recs = [_rec("src-001-c001", type="quiz", doc_ordinal=1),
            _rec("src-001-c002", type="slide", doc_ordinal=2)]
    by_id = {r["component_id"]: r for r in recs}
    anns = _build_live_annotations(
        [{"component_id": "src-001-c001", "bloom": "apply",
          "pedagogical_role": "assessment", "assessment_link": "src-001-c002"}],
        by_id=by_id, valid_lo_ids=set(), component_ids=set(by_id),
        components=recs, transform_version="ped-v1", when=_FIXED_TS,
    )
    assert anns[0].assessment_link == "src-001-c002"
    assert_pedagogy_referential_invariant(_result(typed, [], list(anns)))
