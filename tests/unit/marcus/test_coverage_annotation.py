"""T4 — coverage segmentation + derived-first intent pass (OFFLINE).

Mirrors the P3 test split: the deterministic OFFLINE pass + the live PARSE/BUILD
helpers exercised against a CANNED gpt-5 response fixture. NO live LLM/network — the
real gpt-5 segmentation is the orchestrator's job (T8). The model only cuts spans;
risk flags + intents are asserted DETERMINISTIC (AC5/AC7).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.coverage_annotation import (
    COVERAGE_LIVE_MODEL,
    COVERAGE_OFFLINE_MODEL,
    COVERAGE_REQUEST_TIMEOUT_S,
    MAX_ASSERTIONS_PER_BLOCK,
    CoverageAnnotation,
    CoverageIncompleteError,
    CoverageNotShippableError,
    NonVerbatimSpan,
    assert_segmentation_complete,
    assert_v1_shippable,
    build_coverage_annotations,
    build_coverage_from_rows,
    detect_incomplete_segmentation,
    detect_non_verbatim_spans,
    detect_risk_flags,
    extract_coverage_rows,
    load_coverage_annotation,
    reanchor_verbatim_span,
)
from app.marcus.lesson_plan.source_point import SourcePoint

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "coverage" / "live_segmentation_response.json"
_TS = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)

_NOTES_1 = (
    "U.S. healthcare spending reached $5.2 trillion in 2024. "
    "Independent practice fell drastically while hospital employment surged. "
    "You cannot just optimize your own clinic."
)

# c002's source notes — the fixture's c002 assertions are EXACT copied spans of this
# block (no paraphrase). The first sentence carries a negation ("is not a personal
# failing") → negation risk + verbatim floor (preserves the offending test's intent).
_NOTES_2 = (
    "Physician burnout is not a personal failing but a system-level problem. "
    "Administrative burden increased sharply over the past decade."
)


def _narration_rec(cid: str = "src-001-c001", notes: str = _NOTES_1, **extra) -> dict:
    rec = {
        "component_id": cid, "type": "narration",
        "locator": "Module 1 > Slide 1", "excerpt": notes,
    }
    rec.update(extra)
    return rec


# --------------------------------------------------------------------------- #
# Deterministic risk detection (AC5)
# --------------------------------------------------------------------------- #


def test_detect_numeric_and_dosing() -> None:
    assert "numeric" in detect_risk_flags("reached $5.2 trillion in 2024")
    assert set(detect_risk_flags("administer 5 mg daily")) >= {"numeric", "dosing"}


def test_detect_negation_and_comparator() -> None:
    assert "negation" in detect_risk_flags("this is not a personal failing")
    assert "comparator" in detect_risk_flags("burden increased more than before")


def test_fix5_contraction_negations_caught() -> None:
    # FIX 5: negative contractions ("don't", "isn't", "won't", "doesn't", "can't",
    # "shouldn't", …) must trip the `negation` flag → verbatim_required floor. A
    # "don't exceed 5 mg" safety claim previously escaped (no flag → not must_cover).
    assert "negation" in detect_risk_flags("don't exceed 5 mg")
    for phrase in (
        "isn't safe", "won't help", "doesn't apply", "can't reuse", "shouldn't dose",
        "didn't improve", "wasn't tested",
    ):
        assert "negation" in detect_risk_flags(phrase), phrase
    # curly-apostrophe variant normalizes to the same floor
    assert "negation" in detect_risk_flags("don’t exceed the dose")


def test_detect_exemplary_and_clinical_gated() -> None:
    assert "exemplary_language" in detect_risk_flags("such as sepsis")
    # clinical_claim only when a lexicon is injected (deferred ontology leg)
    assert "clinical_claim" not in detect_risk_flags("sepsis is dangerous")
    assert "clinical_claim" in detect_risk_flags(
        "sepsis is dangerous", clinical_terms=frozenset({"sepsis"})
    )


# --------------------------------------------------------------------------- #
# Offline pass (AC2/AC3 — assertion unit + derived intents)
# --------------------------------------------------------------------------- #


def test_offline_pass_segments_only_narration() -> None:
    comps = [
        _narration_rec(),
        {"component_id": "src-001-c009", "type": "slide", "locator": "Slide 1", "excerpt": "x. y."},
    ]
    anns = build_coverage_annotations(comps, generated_at=_TS)
    assert len(anns) == 1
    ann = anns[0]
    assert ann.component_id == "src-001-c001"
    assert ann.transform_model == COVERAGE_OFFLINE_MODEL
    assert ann.segmentation == "assertion_level"
    assert ann.is_v1_shippable()
    # three sentences → three source points, ordinals 1..3
    assert [sp.ordinal for sp in ann.source_points] == [1, 2, 3]
    assert all(isinstance(sp, SourcePoint) for sp in ann.source_points)


def test_offline_points_carry_derived_risk_and_verbatim_floor() -> None:
    ann = build_coverage_annotations([_narration_rec()], generated_at=_TS)[0]
    first = ann.source_points[0]
    assert "numeric" in first.risk_flags  # "$5.2 trillion ... 2024"
    assert first.verbatim_required is True  # numeric → floor
    # the verbatim span is preserved (identity keys on the span, not a paraphrase)
    assert "5.2 trillion" in first.verbatim_text


def test_offline_intents_force_both_when_lo_load_bearing() -> None:
    ann = build_coverage_annotations(
        [_narration_rec(lo_refs=["lo-g0-001"])], generated_at=_TS
    )[0]
    # LO-load-bearing → BOTH surfaces on every point
    for sp in ann.source_points:
        assert set(sp.coverage_intents) == {"gist_on_slide", "detail_in_narration"}


def test_offline_pass_byte_stable_across_runs() -> None:
    a = build_coverage_annotations([_narration_rec()], generated_at=_TS)
    b = build_coverage_annotations([_narration_rec()], generated_at=_TS)
    assert [x.model_dump(mode="json") for x in a] == [y.model_dump(mode="json") for y in b]


# --------------------------------------------------------------------------- #
# Live PARSE/BUILD via canned fixture (AC-OP2 offline-tested; no live call)
# --------------------------------------------------------------------------- #


def test_extract_rows_from_canned_fixture() -> None:
    content = _FIXTURE.read_text(encoding="utf-8")
    rows = extract_coverage_rows(content)
    assert [r["component_id"] for r in rows] == ["src-001-c001", "src-001-c002"]


def test_extract_rows_tolerates_fences_and_prose() -> None:
    body = "Here you go:\n```json\n" + _FIXTURE.read_text(encoding="utf-8") + "\n```\nDone."
    rows = extract_coverage_rows(body)
    assert len(rows) == 2


def test_extract_rows_degrades_on_garbage() -> None:
    assert extract_coverage_rows("not json at all") == []
    assert extract_coverage_rows("") == []


def test_build_from_rows_assigns_deterministic_risk_and_live_model() -> None:
    rows = json.loads(_FIXTURE.read_text(encoding="utf-8"))["blocks"]
    # The component excerpts CONTAIN the fixture assertions VERBATIM (F-012: the live
    # guard re-anchors against the source excerpt, so this now proves the happy path —
    # substring → accepted — instead of accepting a paraphrase against notes="ignored").
    components = [
        _narration_rec("src-001-c001", notes=_NOTES_1),
        _narration_rec("src-001-c002", notes=_NOTES_2),
    ]
    anns = build_coverage_from_rows(rows, components, generated_at=_TS, clinical_terms=None)
    by_id = {a.component_id: a for a in anns}
    assert set(by_id) == {"src-001-c001", "src-001-c002"}
    assert by_id["src-001-c001"].transform_model == COVERAGE_LIVE_MODEL
    # the negation assertion in c002 carries a negation risk + verbatim floor
    neg_point = by_id["src-001-c002"].source_points[0]
    assert "negation" in neg_point.risk_flags
    assert neg_point.verbatim_required is True
    # every accepted point is genuinely verbatim against its source excerpt (no paraphrase)
    for sp in by_id["src-001-c001"].source_points:
        assert sp.verbatim_text in _NOTES_1
    for sp in by_id["src-001-c002"].source_points:
        assert sp.verbatim_text in _NOTES_2
    # nothing was dropped — the fixture is now all exact substrings
    assert detect_non_verbatim_spans(rows, components) == ()


def test_build_from_rows_clamps_over_segmentation() -> None:
    # Spans must be VERBATIM substrings of the excerpt (F-012 guard) so the test
    # isolates the over-segmentation clamp, not the verbatim drop.
    spans = [f"s{i}." for i in range(30)]
    excerpt = " ".join(spans)
    over = [{"component_id": "src-001-c001", "assertions": spans}]
    anns = build_coverage_from_rows(
        over,
        [_narration_rec("src-001-c001", notes=excerpt)],
        generated_at=_TS,
        clinical_terms=None,
    )
    assert len(anns[0].source_points) == MAX_ASSERTIONS_PER_BLOCK


def test_build_from_rows_skips_unknown_component() -> None:
    rows = [{"component_id": "ghost", "assertions": ["a."]}]
    out = build_coverage_from_rows(
        rows, [_narration_rec("src-001-c001")], generated_at=_TS, clinical_terms=None
    )
    assert out == ()


# --------------------------------------------------------------------------- #
# F-012 — the LIVE path must REFUSE a model paraphrase as a verbatim identity
# anchor. The verbatim source span (AC-OP2-DET), never an LLM paraphrase, keys
# identity. Exact substring → accept; whitespace/quote drift → re-anchor to the
# byte-exact source slice; paraphrase/fabrication → DROP + structured diagnostic.
# --------------------------------------------------------------------------- #


def test_build_from_rows_accepts_exact_substring_verbatim() -> None:
    span = "Independent practice fell drastically while hospital employment surged."
    rows = [{"component_id": "src-001-c001", "assertions": [span]}]
    components = [_narration_rec("src-001-c001", notes=_NOTES_1)]
    anns = build_coverage_from_rows(rows, components, generated_at=_TS, clinical_terms=None)
    sp = anns[0].source_points[0]
    assert sp.verbatim_text == span  # byte-identical to the source slice
    assert sp.verbatim_text in _NOTES_1
    assert detect_non_verbatim_spans(rows, components) == ()


def test_build_from_rows_drops_non_verbatim_paraphrase_keeps_verbatim() -> None:
    verbatim = "Independent practice fell drastically while hospital employment surged."
    paraphrase = "Doctors increasingly work for large hospital systems rather than alone."
    rows = [{"component_id": "src-001-c001", "assertions": [verbatim, paraphrase]}]
    components = [_narration_rec("src-001-c001", notes=_NOTES_1)]
    anns = build_coverage_from_rows(rows, components, generated_at=_TS, clinical_terms=None)
    vts = [sp.verbatim_text for a in anns for sp in a.source_points]
    assert verbatim in vts  # the genuine span survives
    assert paraphrase not in vts  # the paraphrase is DROPPED, never minted
    # ordinals are contiguous over ACCEPTED spans only (the drop leaves no gap)
    assert [sp.ordinal for sp in anns[0].source_points] == [1]
    # the structured non-verbatim diagnostic surfaces the dropped paraphrase
    dropped = detect_non_verbatim_spans(rows, components)
    assert [d.span for d in dropped] == [paraphrase]
    assert isinstance(dropped[0], NonVerbatimSpan)
    assert dropped[0].component_id == "src-001-c001"


def test_build_from_rows_reanchors_whitespace_and_quote_normalized() -> None:
    # The source excerpt carries a curly apostrophe (U+2019) and an internal line
    # break; the model normalized both away (straight ' + collapsed whitespace). The
    # span must RE-ANCHOR to the BYTE-EXACT source slice, NOT the model's normalized
    # string — identity keys on the verbatim source span.
    excerpt = "You can’t just optimize your\nown clinic."
    model_span = "You can't just optimize your own clinic."
    rows = [{"component_id": "src-001-c001", "assertions": [model_span]}]
    components = [_narration_rec("src-001-c001", notes=excerpt)]
    anns = build_coverage_from_rows(rows, components, generated_at=_TS, clinical_terms=None)
    sp = anns[0].source_points[0]
    assert sp.verbatim_text == excerpt  # byte-exact source slice
    assert sp.verbatim_text != model_span  # NOT the model's normalized wording
    assert "’" in sp.verbatim_text  # curly apostrophe preserved
    assert "\n" in sp.verbatim_text  # source line break preserved
    assert detect_non_verbatim_spans(rows, components) == ()


def test_build_from_rows_all_spans_non_verbatim_flags_fix3_incomplete() -> None:
    # A component whose EVERY span is non-verbatim drops to zero accepted points; the
    # existing FIX-3 incomplete-segmentation signal must still catch it (non-empty
    # notes, zero produced) so the ledger can't be silently emptied.
    rows = [
        {
            "component_id": "src-001-c001",
            "assertions": [
                "This is a complete fabrication about something unrelated entirely.",
                "Another paraphrase that shares no verbatim span with the notes.",
            ],
        }
    ]
    components = [_narration_rec("src-001-c001", notes=_NOTES_1)]
    anns = build_coverage_from_rows(rows, components, generated_at=_TS, clinical_terms=None)
    assert anns == ()  # all spans dropped → no annotation minted
    dropped = detect_non_verbatim_spans(rows, components)
    assert len(dropped) == 2
    # FIX-3 still fires: non-empty notes, zero produced points
    incomplete = detect_incomplete_segmentation(components, anns)
    assert len(incomplete) == 1
    assert incomplete[0].component_id == "src-001-c001"
    with pytest.raises(CoverageIncompleteError, match="src-001-c001"):
        assert_segmentation_complete(components, anns)


def test_reanchor_verbatim_span_unit() -> None:
    # exact substring → returned unchanged
    assert reanchor_verbatim_span("fell drastically", _NOTES_1) == "fell drastically"
    # whitespace/quote drift → byte-exact ORIGINAL slice (curly apostrophe preserved)
    excerpt = "We can’t\nignore it."
    assert reanchor_verbatim_span("We can't ignore it.", excerpt) == excerpt
    # paraphrase/fabrication → None (dropped)
    assert reanchor_verbatim_span("totally invented sentence", _NOTES_1) is None


# --------------------------------------------------------------------------- #
# Model invariants (Irene caveat: segmentation stamp load-bearing)
# --------------------------------------------------------------------------- #


def test_annotation_rejects_foreign_source_point() -> None:
    foreign = SourcePoint(
        source_point_id="other#1", component_id="other", ordinal=1, slide_key="Slide 1",
        verbatim_text="x", coverage_intents=("gist_on_slide",), segmentation="assertion_level",
    )
    with pytest.raises(ValidationError, match="join-key integrity"):
        CoverageAnnotation(
            component_id="src-001-c001", slide_key="Slide 1",
            source_points=(foreign,), segmentation="assertion_level",
        )


def test_annotation_rejects_segmentation_grain_mismatch() -> None:
    point = SourcePoint(
        source_point_id="src-001-c001#1", component_id="src-001-c001", ordinal=1,
        slide_key="Slide 1", verbatim_text="x", coverage_intents=("gist_on_slide",),
        segmentation="assertion_level",
    )
    with pytest.raises(ValidationError, match="load-bearing"):
        CoverageAnnotation(
            component_id="src-001-c001", slide_key="Slide 1",
            source_points=(point,), segmentation="block_level_v1",
        )


# --------------------------------------------------------------------------- #
# FIX 3 — segmentation that yields nothing for a non-empty note block is SURFACED
# --------------------------------------------------------------------------- #


def test_fix3_incomplete_segmentation_is_surfaced_not_swallowed() -> None:
    # A non-empty note-bearing component whose live segmentation yields ZERO
    # assertions (parse failure / empty/malformed response) must NOT silently vanish
    # into an empty ledger — that is indistinguishable from "0 holes" and is
    # toothless. The incompleteness is an explicit, structured signal.
    components = [_narration_rec("src-001-c001", notes=_NOTES_1)]
    # rows == [] models extract_coverage_rows() degrading on a malformed response
    anns = build_coverage_from_rows([], components, generated_at=_TS, clinical_terms=None)
    assert anns == ()  # nothing produced
    incomplete = detect_incomplete_segmentation(components, anns)
    assert len(incomplete) == 1
    assert incomplete[0].component_id == "src-001-c001"
    # and the orchestrator-callable assert raises a typed error it can surface
    with pytest.raises(CoverageIncompleteError, match="src-001-c001"):
        assert_segmentation_complete(components, anns)


def test_fix3_empty_note_block_is_not_incomplete() -> None:
    # A genuinely empty note block producing zero assertions is NOT incompleteness.
    components = [_narration_rec("src-001-c001", notes="   ")]
    anns = build_coverage_annotations(components, generated_at=_TS)
    assert detect_incomplete_segmentation(components, anns) == ()
    assert_segmentation_complete(components, anns)  # does not raise


def test_fix3_complete_segmentation_passes() -> None:
    components = [_narration_rec("src-001-c001", notes=_NOTES_1)]
    anns = build_coverage_annotations(components, generated_at=_TS)
    assert detect_incomplete_segmentation(components, anns) == ()
    assert_segmentation_complete(components, anns)


# --------------------------------------------------------------------------- #
# FIX 4 — assertion_level is enforced; block_level_v1 is never a v1 ship state
# --------------------------------------------------------------------------- #


def test_fix4_block_level_v1_is_rejected_by_ship_gate() -> None:
    point = SourcePoint(
        source_point_id="src-001-c001#1", component_id="src-001-c001", ordinal=1,
        slide_key="Slide 1", verbatim_text="x", coverage_intents=("gist_on_slide",),
        segmentation="block_level_v1",
    )
    block_ann = CoverageAnnotation(
        component_id="src-001-c001", slide_key="Slide 1", source_points=(point,),
        segmentation="block_level_v1", generated_at=_TS,
    )
    assert block_ann.is_v1_shippable() is False
    with pytest.raises(CoverageNotShippableError, match="block_level_v1"):
        assert_v1_shippable((block_ann,))


def test_fix4_assertion_level_passes_ship_gate() -> None:
    anns = build_coverage_annotations([_narration_rec()], generated_at=_TS)
    assert_v1_shippable(anns)  # does not raise


# --------------------------------------------------------------------------- #
# FIX 6 — the default live-leg chat model binds a hard per-request timeout
# --------------------------------------------------------------------------- #


def test_fix6_make_chat_model_binds_request_timeout_and_no_retries() -> None:
    # FIX 6: the default fallback path must bind a hard per-request timeout +
    # max_retries=0 (AC-OP2), else a slow gpt-5 reasoning call hangs. Construction
    # only — NO live/network call (mirrors the adapter's own construction-only tests).
    from app.models.adapter import make_chat_model

    handle = make_chat_model(
        COVERAGE_LIVE_MODEL, request_timeout=COVERAGE_REQUEST_TIMEOUT_S, max_retries=0
    )
    assert handle.chat.request_timeout == COVERAGE_REQUEST_TIMEOUT_S
    assert handle.chat.max_retries == 0


def test_annotation_round_trip_load() -> None:
    ann = build_coverage_annotations([_narration_rec()], generated_at=_TS)[0]
    assert load_coverage_annotation(ann.model_dump(mode="json")) == ann
