"""Round 5 — marshaller-finalize + bridge hardening (RED-first, real-shaped).

Exercises the FINALIZED ``_marshal_coverage_surfaces`` / ``_derive_and_write_coverage_receipt``
against the REAL G3 export + run-state shapes captured from ``3409709b`` and
``1f40a190`` (frozen in ``tests/fixtures/coverage``). The marshaller marshals NOTHING
today (both call sites pass a ``RunState`` MODEL → ``None``); these cases pin the
bilateral source-ordinal bridge, the collision guard, the fractional-degrade, the
join_provenance face, the vacuous-receipt state, and the ledger-only NonVerbatimSpan
surfacing the amendments R5-A1..A9 require.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from app.marcus.lesson_plan.coverage_receipt import load_coverage_receipt
from app.marcus.orchestrator import coverage_gate_wiring as cgw
from app.marcus.orchestrator import coverage_runner as cr

_FIXTURES = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "coverage"


# ---------------------------------------------------------------------------
# Builders — write the REAL on-disk shapes (exports + g0-enrichment) into a run dir
# ---------------------------------------------------------------------------


def _deck_row(i: int, *, slide_id: str | None = None, title: str = "", body: str = "") -> dict:
    return {
        "card_number": str(i),
        "dispatch_variant": "A",
        "display_title": title or f"Slide {i}",
        "slide_id": slide_id or f"slide-{i:02d}",
        "variant_id": "A",
        "visual_description": body,
    }


def _seg_row(i: int, *, slide_id: str | None = None, text: str = "") -> dict:
    return {
        "segment_id": f"seg-{i:02d}",
        "slide_id": slide_id or f"slide-{i:02d}",
        "narration_text": text,
    }


def _fx_deck() -> list[dict]:
    # Frozen REAL-shaped Gary export (kept at the coverage/ root, NOT under exports/ —
    # that path is gitignored). The test writes it into tmp_path/exports at runtime.
    text = (_FIXTURES / "gary-dispatch-payload.json").read_text(encoding="utf-8")
    return json.loads(text)["gary_slide_output"]


def _fx_segments() -> list[dict]:
    path = _FIXTURES / "segment-manifest-storyboard-b.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))["segments"]


def _fx_annotations() -> list[dict]:
    text = (_FIXTURES / "g0-enrichment.json").read_text(encoding="utf-8")
    return json.loads(text)["coverage_annotations"]


def _head_unit(i: int, *, unit_id: str | None = None) -> dict:
    return {"unit_id": unit_id or f"u{i:02d}", "cluster_role": "head", "scope_decision": "in-scope"}


def _point(cid: str, slide_key: str, verbatim: str, *, risk: list[str] | None = None,
           intents: list[str] | None = None) -> dict:
    return {
        "source_point_id": f"{cid}#1",
        "component_id": cid,
        "ordinal": 1,
        "slide_key": slide_key,
        "verbatim_text": verbatim,
        "risk_flags": risk or [],
        "coverage_intents": intents or ["gist_on_slide"],
        "segmentation": "assertion_level",
        "operator_signed_exclusion": False,
    }


def _annotation(cid: str, slide_key: str, points: list[dict]) -> dict:
    return {
        "component_id": cid,
        "slide_key": slide_key,
        "segmentation": "assertion_level",
        "source_points": points,
    }


def _write_run(
    run_dir: Path,
    *,
    deck: list[dict],
    segments: list[dict],
    annotations: list[dict],
    plan_units: list[dict],
    non_verbatim_spans: list[dict] | None = None,
    card_extra: dict | None = None,
) -> dict[str, Any]:
    exports = run_dir / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    (exports / "gary-dispatch-payload.json").write_text(
        json.dumps({"gary_slide_output": deck}), encoding="utf-8"
    )
    (exports / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": segments}), encoding="utf-8"
    )
    card: dict[str, Any] = {"coverage_annotations": annotations}
    if non_verbatim_spans is not None:
        card["non_verbatim_spans"] = non_verbatim_spans
    if card_extra:
        card.update(card_extra)
    (run_dir / "g0-enrichment.json").write_text(json.dumps(card), encoding="utf-8")
    # run_state dict mirrors run_state.model_dump(mode="json"): plan_units ride
    # production_envelope.contributions[*].output.lesson_plan.plan_units.
    return {
        "production_envelope": {
            "contributions": [
                {"output": {"lesson_plan": {"plan_units": plan_units}}},
            ]
        }
    }


def _rows_by_point(receipt) -> dict[str, Any]:
    return {r.source_point_id: r for r in receipt.rows}


def _load(path: Path):
    return load_coverage_receipt(json.loads(path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# (i) real-exports deck+narration JOIN -> anchors non-empty; Slide 1 covered
# ---------------------------------------------------------------------------


def test_real_exports_deck_and_narration_join(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # Reuse the FROZEN real-shaped exports + g0-enrichment fixtures.
    run_state = _write_run(
        tmp_path,
        deck=_fx_deck(),
        segments=_fx_segments(),
        annotations=_fx_annotations(),
        plan_units=[_head_unit(i) for i in range(1, 6)],
    )

    path = cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state)
    assert path is not None
    receipt = _load(path)
    rows = _rows_by_point(receipt)
    # Slide 1 joined to its OWN deck slide + narration -> covered, not missing.
    slide1 = rows["src-001#1"]
    assert slide1.anchor_resolved is True
    assert slide1.coverage_status in {"both", "covered_on_slide", "covered_in_narration"}
    assert slide1.join_provenance == "ordinal_bridged"


# ---------------------------------------------------------------------------
# (ii) clean-integer must-cover point present on its slide -> covered/both
# ---------------------------------------------------------------------------


def test_clean_integer_must_cover_covered(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    run_state = _write_run(
        tmp_path,
        deck=_fx_deck(),
        segments=_fx_segments(),
        annotations=_fx_annotations(),
        plan_units=[_head_unit(i) for i in range(1, 6)],
    )

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-002#1"]
    assert row.must_cover is True
    assert row.coverage_status in {"both", "covered_on_slide", "covered_in_narration"}
    assert row.verbatim_absent is False  # the span IS present at the anchor
    assert receipt.missing_must_cover() == ()  # nothing blocks


# ---------------------------------------------------------------------------
# (iii) cross-Part "Slide 1" collision -> diagnostic + missing/unresolved, never covered
# ---------------------------------------------------------------------------


def test_cross_part_collision_blocks_false_pass(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # Two DIFFERENT source slides both resolve to ordinal 1 (u01 and x1 trailing-1).
    deck = [
        _deck_row(1, slide_id="slide-01", body="Part one slide one boilerplate header"),
        _deck_row(2, slide_id="slide-02", body="Part two slide one boilerplate header"),
    ]
    segments = [_seg_row(1, slide_id="slide-01", text="spoken one"),
                _seg_row(2, slide_id="slide-02", text="spoken two")]
    plan_units = [_head_unit(1, unit_id="u01"), _head_unit(2, unit_id="x1")]  # both -> ordinal 1
    annotations = [
        _annotation("src-001", "Slide 1", [_point("src-001", "Slide 1", "boilerplate header")])
    ]
    run_state = _write_run(
        tmp_path, deck=deck, segments=segments, annotations=annotations, plan_units=plan_units
    )

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-001#1"]
    assert row.coverage_status == "missing"  # NEVER credited off an ambiguous slide
    assert row.join_provenance == "unresolved_locator"
    assert any("collision" in d.lower() or "ambiguous" in d.lower() for d in receipt.diagnostics)


# ---------------------------------------------------------------------------
# (iv) section-title breadcrumb + integer cards -> no false join -> missing
# ---------------------------------------------------------------------------


def test_section_title_breadcrumb_no_false_join(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    deck = [_deck_row(1, slide_id="slide-01", body="Pharmacology overview content lives here")]
    segments = [_seg_row(1, slide_id="slide-01", text="Pharmacology overview content lives here")]
    plan_units = [_head_unit(1)]
    # The annotation breadcrumb is a SECTION TITLE, not "Slide N" -> unbridgeable.
    annotations = [_annotation("src-sec", "Pharmacology Overview",
                               [_point("src-sec", "Pharmacology Overview", "content lives here")])]
    run_state = _write_run(
        tmp_path, deck=deck, segments=segments, annotations=annotations, plan_units=plan_units
    )

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-sec#1"]
    assert row.coverage_status == "missing"  # the integer card never falsely covers it
    assert row.join_provenance == "unresolved_locator"


# ---------------------------------------------------------------------------
# (v) fractional "Slide 4.5" -> missing, NEVER credited as slide 5
# ---------------------------------------------------------------------------


def test_fractional_slide_never_trailing_digits_to_five(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # The span lives on slide 5; the interstitial breadcrumb "Slide 4.5" must resolve to
    # parent 4 (which lacks the span) or degrade -> missing. It must NEVER credit slide 5.
    span = "the unique slide five only span"
    deck = [
        _deck_row(4, slide_id="slide-04", body="slide four content without the span"),
        _deck_row(5, slide_id="slide-05", body=f"slide five content carrying {span}"),
    ]
    segments = [
        _seg_row(4, slide_id="slide-04", text="four"),
        _seg_row(5, slide_id="slide-05", text="five"),
    ]
    plan_units = [_head_unit(4, unit_id="u04"), _head_unit(5, unit_id="u05")]
    annotations = [_annotation("src-int", "Slide 4.5", [_point("src-int", "Slide 4.5", span)])]
    run_state = _write_run(
        tmp_path, deck=deck, segments=segments, annotations=annotations, plan_units=plan_units
    )

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-int#1"]
    assert row.coverage_status == "missing"  # never trailing-digits to 5
    # resolved to PARENT ordinal 4 (which lacks the span) — NOT the fractional tail 5.
    assert row.join_provenance == "ordinal_bridged"


# ---------------------------------------------------------------------------
# (vi) persisted NonVerbatimSpan -> in diagnostics, NOT a missing row
# ---------------------------------------------------------------------------


def test_persisted_non_verbatim_spans_surface_in_diagnostics(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    deck = [_deck_row(1, slide_id="slide-01", body="the verbatim span is here")]
    segments = [_seg_row(1, slide_id="slide-01", text="the verbatim span is here")]
    plan_units = [_head_unit(1)]
    annotations = [
        _annotation("src-001", "Slide 1", [_point("src-001", "Slide 1", "verbatim span is here")])
    ]
    non_verbatim = [
        {
            "component_id": "src-001",
            "slide_key": "Slide 1",
            "span": "a model paraphrase that drifted",
            "reason": "not a verbatim substring",
        }
    ]
    run_state = _write_run(tmp_path, deck=deck, segments=segments, annotations=annotations,
                           plan_units=plan_units, non_verbatim_spans=non_verbatim)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    # surfaced as a DIAGNOSTIC, never a row.
    assert any("paraphrase that drifted" in d for d in receipt.diagnostics)
    assert all(r.source_point_id != "src-001#paraphrase" for r in receipt.rows)
    # the real (verbatim) point still joins.
    assert _rows_by_point(receipt)["src-001#1"].coverage_status in {
        "both", "covered_on_slide", "covered_in_narration"
    }


# ---------------------------------------------------------------------------
# (vii) BOTH walk-site invocations pass run_state.model_dump (parity)
# ---------------------------------------------------------------------------


def test_both_walk_sites_pass_model_dump_parity() -> None:
    src = (Path(__file__).resolve().parents[4] / "app" / "marcus" / "orchestrator"
           / "production_runner.py").read_text(encoding="utf-8")
    marker = "coverage_runner._derive_and_write_coverage_receipt("
    starts = [i for i in range(len(src)) if src.startswith(marker, i)]
    assert len(starts) == 2, f"expected exactly two G3 call sites, found {len(starts)}"
    for start in starts:
        # the call argument block (up to the next ~6 lines covers run_dir + gate_id + run_state)
        blob = src[start : start + 320]
        assert "run_state.model_dump(mode=\"json\")" in blob, (
            "both walk sites must pass run_state.model_dump(mode='json') (R5-A7 parity)"
        )
    # the never-true dict guard is fully deleted (no call site keeps it)
    assert "run_state if isinstance(run_state, dict) else None" not in src


# ---------------------------------------------------------------------------
# (viii) vacuous receipt (all-missing vs non-empty source) -> is_vacuous / non-pass
# ---------------------------------------------------------------------------


def test_vacuous_all_missing_receipt_is_not_a_clean_pass(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # Non-empty source-point set, but the deck/narration carry NONE of the spans (all
    # breadcrumbs are section titles -> no clean join) -> every row missing -> vacuous.
    deck = [_deck_row(1, slide_id="slide-01", body="unrelated deck text")]
    segments = [_seg_row(1, slide_id="slide-01", text="unrelated narration text")]
    plan_units = [_head_unit(1)]
    annotations = [
        _annotation("src-a", "Welcome Video", [_point("src-a", "Welcome Video", "alpha span")]),
        _annotation("src-b", "Course Intro", [_point("src-b", "Course Intro", "beta span")]),
    ]
    run_state = _write_run(
        tmp_path, deck=deck, segments=segments, annotations=annotations, plan_units=plan_units
    )

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    assert len(receipt.rows) == 2
    assert receipt.joined_row_count() == 0
    assert receipt.is_vacuous() is True


# ---------------------------------------------------------------------------
# MF3 — authoritative plan/lineage selection (wrong-plan -> swapped ordinals ->
# false-PASS). The REAL persisted package_builder slides bind slide_id -> source_ref
# explicitly, so a re-refinement plan with the same in-scope COUNT but REVERSED unit
# order can no longer swap ordinals and credit coverage from the wrong slide.
# ---------------------------------------------------------------------------


def _run_state_with_slides(plan_unit_lists: list[list[dict]], slides: list[dict]) -> dict[str, Any]:
    """A run_state.model_dump shape: N lesson_plan contributions + the REAL persisted
    package_builder ``slides`` lineage carrier."""
    contributions: list[dict[str, Any]] = [
        {"specialist_id": "irene_pass1", "node_id": f"plan-{i}",
         "output": {"lesson_plan": {"plan_units": pu}}}
        for i, pu in enumerate(plan_unit_lists)
    ]
    contributions.append(
        {"specialist_id": "package_builder", "node_id": "06", "output": {"slides": slides}}
    )
    return {"production_envelope": {"contributions": contributions}}


def test_swapped_plan_order_no_false_pass_via_real_slides(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    deck = [
        _deck_row(1, slide_id="slide-01", body="alpha is on the real first slide"),
        _deck_row(2, slide_id="slide-02", body="beta is on the real second slide"),
    ]
    segments = [_seg_row(1, slide_id="slide-01", text="one"),
                _seg_row(2, slide_id="slide-02", text="two")]
    # Authored point: Slide 2 / "alpha". alpha is NOT on slide 2 -> must be MISSING.
    annotations = [_annotation("src-x", "Slide 2", [_point("src-x", "Slide 2", "alpha")])]
    slides = [
        {"slide_id": "slide-01", "source_ref": "u01"},
        {"slide_id": "slide-02", "source_ref": "u02"},
    ]
    plan_a = [_head_unit(1, unit_id="u01"), _head_unit(2, unit_id="u02")]
    plan_b = [_head_unit(2, unit_id="u02"), _head_unit(1, unit_id="u01")]  # REVERSED order
    run_state = _run_state_with_slides([plan_a, plan_b], slides)
    _write_run(tmp_path, deck=deck, segments=segments, annotations=annotations, plan_units=plan_a)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-x#1"]
    assert row.coverage_status == "missing"  # NOT credited off the swapped plan order


def test_ambiguous_plan_without_real_slides_degrades(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # No real persisted slides -> positional re-derivation fallback. Two plans tie on
    # in-scope COUNT but differ in unit ORDER -> UNRESOLVED lineage: diagnostic +
    # degrade (force missing), never a silent wrong-plan pick.
    deck = [
        _deck_row(1, slide_id="slide-01", body="alpha is here"),
        _deck_row(2, slide_id="slide-02", body="beta is here"),
    ]
    segments = [_seg_row(1, slide_id="slide-01", text="one"),
                _seg_row(2, slide_id="slide-02", text="two")]
    annotations = [_annotation("src-x", "Slide 2", [_point("src-x", "Slide 2", "alpha")])]
    plan_a = [_head_unit(1, unit_id="u01"), _head_unit(2, unit_id="u02")]
    plan_b = [_head_unit(2, unit_id="u02"), _head_unit(1, unit_id="u01")]  # REVERSED order
    run_state = {
        "production_envelope": {
            "contributions": [
                {"output": {"lesson_plan": {"plan_units": plan_a}}},
                {"output": {"lesson_plan": {"plan_units": plan_b}}},
            ]
        }
    }
    _write_run(tmp_path, deck=deck, segments=segments, annotations=annotations, plan_units=plan_a)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-x#1"]
    assert row.coverage_status == "missing"  # degraded, never a silent wrong-plan credit
    assert any("ambiguous" in d.lower() or "lineage" in d.lower() for d in receipt.diagnostics)


# ---------------------------------------------------------------------------
# MF4 — breadcrumb prefix discrimination + known-ordinal corroboration
# ("Page N" / "Chapter N" / out-of-range "Slide N" -> NO slide credit)
# ---------------------------------------------------------------------------


def test_page_prefix_breadcrumb_no_false_join(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    span = "the supplementary handout sentence"
    deck = [_deck_row(1, slide_id="slide-01", body=f"slide one body carrying {span}")]
    segments = [_seg_row(1, slide_id="slide-01", text="one")]
    plan_units = [_head_unit(1, unit_id="u01")]
    # "Page 1" is a SUPPLEMENTARY page reference, NOT a slide reference -> must not
    # bridge to slide ordinal 1 and falsely credit against Slide 1 text.
    annotations = [_annotation("src-pg", "Page 1", [_point("src-pg", "Page 1", span)])]
    run_state = _write_run(tmp_path, deck=deck, segments=segments,
                           annotations=annotations, plan_units=plan_units)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-pg#1"]
    assert row.coverage_status == "missing"  # "Page 1" never cross-credits to Slide 1
    assert row.join_provenance == "unresolved_locator"


def test_chapter_prefix_breadcrumb_no_false_join(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    span = "the chapter reading excerpt"
    deck = [_deck_row(1, slide_id="slide-01", body=f"slide one body carrying {span}")]
    segments = [_seg_row(1, slide_id="slide-01", text="one")]
    plan_units = [_head_unit(1, unit_id="u01")]
    annotations = [_annotation("src-ch", "Chapter 1", [_point("src-ch", "Chapter 1", span)])]
    run_state = _write_run(tmp_path, deck=deck, segments=segments,
                           annotations=annotations, plan_units=plan_units)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-ch#1"]
    assert row.coverage_status == "missing"
    assert row.join_provenance == "unresolved_locator"


def test_clean_int_requires_known_ordinal_corroboration(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # "Slide 9" but the deck only has ordinal 1 (9 is NOT a known ordinal) -> the
    # clean-int path must require corroboration (same discipline as the fractional
    # path) and degrade to unresolved_locator, not a confident ordinal_bridged miss.
    deck = [_deck_row(1, slide_id="slide-01", body="only slide one exists")]
    segments = [_seg_row(1, slide_id="slide-01", text="one")]
    plan_units = [_head_unit(1, unit_id="u01")]
    annotations = [_annotation("src-9", "Slide 9", [_point("src-9", "Slide 9", "phantom span")])]
    run_state = _write_run(tmp_path, deck=deck, segments=segments,
                           annotations=annotations, plan_units=plan_units)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-9#1"]
    assert row.coverage_status == "missing"
    assert row.join_provenance == "unresolved_locator"  # not corroborated -> degrade


# ---------------------------------------------------------------------------
# SF3 — narration-side genuineness guard (R5-A1): a detail_in_narration must-cover
# point whose span is on BOTH surfaces must reach coverage_status == "both" (NOT
# covered_on_slide + narration_obligation_unmet). FAILS if narration reverts to
# keying off the raw slide_id instead of the bridged source ordinal.
# ---------------------------------------------------------------------------


def test_detail_in_narration_both_surfaces_reaches_both(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    span = "this exact teaching assertion is spoken and shown"
    deck = [_deck_row(1, slide_id="slide-01", body=span)]
    segments = [_seg_row(1, slide_id="slide-01", text=span)]
    plan_units = [_head_unit(1, unit_id="u01")]
    annotations = [
        _annotation("src-d", "Slide 1",
                    [_point("src-d", "Slide 1", span, intents=["detail_in_narration"])])
    ]
    run_state = _write_run(tmp_path, deck=deck, segments=segments,
                           annotations=annotations, plan_units=plan_units)

    receipt = _load(cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state))
    row = _rows_by_point(receipt)["src-d#1"]
    assert row.coverage_status == "both"  # narration bridged to the SAME source ordinal
    assert row.narration_obligation_unmet is False
