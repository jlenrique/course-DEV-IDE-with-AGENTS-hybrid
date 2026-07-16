"""Story 39.1b — deliverable-bar exercise-composition clause + negative pins.

Same-diff bar extension (protocol plank 5 + M-D3-2b): the exercise clause in
``_assert_completed_workbook_deliverable`` is fed mutated copies of the frozen
live shapes (the REAL 8b275e5b post-cap composition off the committed
live-shape fixture) and every named mutant must REJECT
(``workbook-deliverable-nonconforming-despite-completed``):

  (a) an origin-labeled group heading missing while items of that origin exist
  (b) collateral trimmed (receipt tally > 0) with no ``exercise_overlay_loss``
      record — the silent-trim mutant
  (c) an overlay (course-check) item dropped from the render
      (overlay-never-trimmed)

Plus the MD-floor desync pins (callout ⇔ record, both directions) and the
malformed-receipt refusal. Positive floors: the conforming trimmed and
zero-trim shapes pass; a pre-39.1b producer contribution (no receipt) keeps
the R3-style tolerance.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest
from docx import Document

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DeepDiveEnrichmentExecutionReceiptV1,
    WorkbookReviewContributionV1,
    build_workbook_review_contribution,
    compose_deep_dive_enrichment,
    render_deep_dive_markdown,
    render_deep_dive_reference_lines,
)
from app.marcus.lesson_plan.workbook_producer import (
    COURSE_CHECK_GROUP_LABEL,
    EXERCISE_OVERLAY_LOSS_CALLOUT,
    PRACTICE_GROUP_LABEL,
)
from scripts.utilities import marcus_spoc_live_test_runner as runner
from tests.helpers.deep_dive_enrichment_37_2b import (
    RENDERED_WORKBOOK_FIXTURE,
    enriched_candidate,
    install_run_json,
    make_request,
)
from tests.helpers.glossary_39_1 import (
    glossary_only_reference_lines,
    swap_glossary_section,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
_COMPOSITION_FIXTURE = json.loads(
    (
        REPO_ROOT
        / "tests"
        / "fixtures"
        / "exercise_merge_39_1b"
        / "composition-8b275e5b.json"
    ).read_text(encoding="utf-8")
)

# The REAL 8b275e5b loss record (as the producer persists it).
_REAL_LOSS = {
    **_COMPOSITION_FIXTURE["expected"]["loss"],
    "trimmed_exercise_ids": _COMPOSITION_FIXTURE["expected"]["trimmed_exercise_ids"],
    "note": (
        "2 of 8 collateral (Practice) exercise(s) trimmed by the exercise cap "
        "(round-robin by unit then stable id; course-check items are never "
        "trimmed): ex-u03-2, ex-u05-2"
    ),
}


def _receipt(*, trimmed: bool = True) -> dict:
    """The persisted exercise_composition receipt for the real 8b275e5b shape."""
    sections = []
    for section_id, kept in _COMPOSITION_FIXTURE["expected"]["kept_by_section"].items():
        sections.append(
            {
                "section_id": section_id,
                "practice": [ex for ex in kept if not ex.startswith("g0-")],
                "course_check": [ex for ex in kept if ex.startswith("g0-")],
            }
        )
    return {
        "sections": sections,
        "practice_total": sum(len(row["practice"]) for row in sections),
        "course_check_total": sum(len(row["course_check"]) for row in sections),
        "collateral_trimmed_count": (
            _REAL_LOSS["trimmed_count"] if trimmed else 0
        ),
    }


def _exercise_markdown(receipt: dict, *, callout: bool) -> str:
    lines = ["", "## Exercises", ""]
    for row in receipt["sections"]:
        if row["practice"]:
            lines.append(f"### {PRACTICE_GROUP_LABEL} — section `{row['section_id']}`")
            for exercise_id in row["practice"]:
                lines.append(f"#### Exercise `{exercise_id}`")
                lines.append("Bloom level: **understand**")
                lines.append("Practice intent without figures.")
                lines.append("")
        if row["course_check"]:
            lines.append(
                f"### {COURSE_CHECK_GROUP_LABEL} — section `{row['section_id']}`"
            )
            for exercise_id in row["course_check"]:
                lines.append(f"#### Exercise `{exercise_id}`")
                lines.append("Bloom level: **understand**")
                lines.append("Course-check prompt without figures.")
                lines.append("")
    if callout:
        lines.append(f"> _{EXERCISE_OVERLAY_LOSS_CALLOUT} {_REAL_LOSS['note']}_")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Conforming-baseline rig (mirrors test_workbook_deliverable_bar_39_1)
# ---------------------------------------------------------------------------


def _execution_receipt(request) -> DeepDiveEnrichmentExecutionReceiptV1:
    return DeepDiveEnrichmentExecutionReceiptV1(
        mode="live",
        calls=1,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model="gpt-5",
        model_config_digest="sha256:" + "3" * 64,
        cost_usd=0.05,
    )


def _enriched_contribution() -> dict:
    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    contribution = build_workbook_review_contribution(result, _execution_receipt(request))
    return json.loads(contribution.model_dump_json())


def _render_conforming_md(contribution_payload: dict) -> str:
    contribution = WorkbookReviewContributionV1.model_validate_json(
        json.dumps(contribution_payload, separators=(",", ":")), strict=True
    )
    base = swap_glossary_section(
        RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8"), contribution
    )
    blocks = ["", "## Deep Dive", "", render_deep_dive_markdown(contribution), ""]
    enrichment_refs = list(render_deep_dive_reference_lines(contribution))
    result = contribution.deep_dive_enrichment
    used = (
        tuple(result.gate.used_citation_ids)
        if result is not None and result.status == "enriched"
        else ()
    )
    glossary_refs = list(
        glossary_only_reference_lines(contribution, exclude_citation_ids=used)
    )
    if enrichment_refs or glossary_refs:
        cited_block = "\n".join(
            [
                "#### Deep Dive cited entries (Ask-A, DOI)",
                *enrichment_refs,
                *glossary_refs,
                "",
            ]
        )
        trends_marker = "\n## Research Trends\n"
        assert trends_marker in base
        base = base.replace(trends_marker, f"\n{cited_block}{trends_marker}", 1)
    return base + "\n".join(blocks)


def _emit_deliverable(run_dir: Path, markdown: str) -> None:
    exports = run_dir / "exports" / "workbooks"
    exports.mkdir(parents=True)
    (exports / "u01@1.md").write_text(markdown, encoding="utf-8")
    document = Document()
    document.add_heading("Workbook", level=0)
    document.save(str(exports / "u01@1.docx"))


def _producer_output(
    exercise_composition: dict | None,
    exercise_overlay_loss: dict | None,
) -> dict:
    return {
        "workbook": {
            "asset_ref": "workbook-u01@1",
            "asset_path": "exports/workbooks/u01@1.md",
            "fulfills": "u01@1",
            "modality_ref": "workbook",
            "markdown_path": "exports/workbooks/u01@1.md",
            "docx_path": "exports/workbooks/u01@1.docx",
            "lo_overlay_loss": None,
            "exercise_composition": exercise_composition,
            "exercise_overlay_loss": exercise_overlay_loss,
        }
    }


def _run_dir_with(
    tmp_path: Path,
    markdown: str,
    *,
    exercise_composition: dict | None,
    exercise_overlay_loss: dict | None,
) -> Path:
    contribution = _enriched_contribution()
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(
            ("workbook_review", "07W.3", contribution, "gpt-5"),
            (
                "workbook_producer",
                "07W",
                _producer_output(exercise_composition, exercise_overlay_loss),
                "gpt-5",
            ),
        ),
    )
    _emit_deliverable(tmp_path, markdown)
    return tmp_path


def _conforming_md(*, receipt: dict, callout: bool) -> str:
    return _render_conforming_md(_enriched_contribution()) + _exercise_markdown(
        receipt, callout=callout
    )


def _assert_bar(run_dir: Path) -> None:
    runner._assert_completed_workbook_deliverable(uuid4(), run_dir)


def _assert_bar_rejects(run_dir: Path) -> None:
    with pytest.raises(runner.RunnerRefusal) as caught:
        _assert_bar(run_dir)
    assert str(caught.value) == "workbook-deliverable-nonconforming-despite-completed"


# ---------------------------------------------------------------------------
# Positive floors
# ---------------------------------------------------------------------------


def test_conforming_trimmed_composition_passes(tmp_path: Path) -> None:
    """The REAL 8b275e5b post-cap shape: receipt + matching labels + loss
    record + callout — the bar accepts."""
    receipt = _receipt(trimmed=True)
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=True),
        exercise_composition=receipt,
        exercise_overlay_loss=dict(_REAL_LOSS),
    )
    _assert_bar(tmp_path)


def test_conforming_zero_trim_composition_passes(tmp_path: Path) -> None:
    receipt = _receipt(trimmed=False)
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=False),
        exercise_composition=receipt,
        exercise_overlay_loss=None,
    )
    _assert_bar(tmp_path)


def test_pre_39_1b_contribution_without_receipt_tolerated(tmp_path: Path) -> None:
    """R3-style tolerance: a producer contribution predating the receipt (no
    exercise_composition key, no callout in the MD) still passes."""
    contribution = _enriched_contribution()
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(
            ("workbook_review", "07W.3", contribution, "gpt-5"),
            (
                "workbook_producer",
                "07W",
                {
                    "workbook": {
                        "asset_ref": "workbook-u01@1",
                        "markdown_path": "exports/workbooks/u01@1.md",
                        "docx_path": "exports/workbooks/u01@1.docx",
                        "lo_overlay_loss": None,
                    }
                },
                "gpt-5",
            ),
        ),
    )
    _emit_deliverable(tmp_path, _render_conforming_md(contribution))
    _assert_bar(tmp_path)


# ---------------------------------------------------------------------------
# Negative pins (M-D3-2b — each mutant must REJECT)
# ---------------------------------------------------------------------------


def test_negative_pin_a_missing_course_check_label_rejects(tmp_path: Path) -> None:
    """(a) items of an origin class exist but its labeled group heading is
    absent from the render."""
    receipt = _receipt(trimmed=True)
    markdown = _conforming_md(receipt=receipt, callout=True).replace(
        f"### {COURSE_CHECK_GROUP_LABEL} — section `sec-u01`\n", "", 1
    )
    _run_dir_with(
        tmp_path,
        markdown,
        exercise_composition=receipt,
        exercise_overlay_loss=dict(_REAL_LOSS),
    )
    _assert_bar_rejects(tmp_path)


def test_negative_pin_a_missing_practice_label_rejects(tmp_path: Path) -> None:
    receipt = _receipt(trimmed=True)
    markdown = _conforming_md(receipt=receipt, callout=True).replace(
        f"### {PRACTICE_GROUP_LABEL} — section `sec-u04`\n", "", 1
    )
    _run_dir_with(
        tmp_path,
        markdown,
        exercise_composition=receipt,
        exercise_overlay_loss=dict(_REAL_LOSS),
    )
    _assert_bar_rejects(tmp_path)


def test_negative_pin_b_silent_trim_rejects(tmp_path: Path) -> None:
    """(b) the receipt tallies a collateral trim but NO exercise_overlay_loss
    record was persisted — the silent-trim mutant (callout also absent, so the
    refusal comes from the structured channel alone)."""
    receipt = _receipt(trimmed=True)
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=False),
        exercise_composition=receipt,
        exercise_overlay_loss=None,
    )
    _assert_bar_rejects(tmp_path)


def test_negative_pin_c_overlay_item_dropped_from_render_rejects(
    tmp_path: Path,
) -> None:
    """(c) overlay-never-trimmed: a course-check id the receipt carries is
    absent from the render."""
    receipt = _receipt(trimmed=True)
    markdown = _conforming_md(receipt=receipt, callout=True).replace(
        "#### Exercise `g0-src-001-c002`\n", "", 1
    )
    _run_dir_with(
        tmp_path,
        markdown,
        exercise_composition=receipt,
        exercise_overlay_loss=dict(_REAL_LOSS),
    )
    _assert_bar_rejects(tmp_path)


def test_callout_without_record_rejects(tmp_path: Path) -> None:
    """MD floor: an ``Exercise overlay loss:`` callout no structured record
    backs is a fabricated claim."""
    receipt = _receipt(trimmed=False)
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=True),
        exercise_composition=receipt,
        exercise_overlay_loss=None,
    )
    _assert_bar_rejects(tmp_path)


def test_record_without_callout_rejects(tmp_path: Path) -> None:
    """MD floor (desync, other direction): a populated loss record whose
    callout is missing from the deliverable."""
    receipt = _receipt(trimmed=True)
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=False),
        exercise_composition=receipt,
        exercise_overlay_loss=dict(_REAL_LOSS),
    )
    _assert_bar_rejects(tmp_path)


def test_loss_record_without_receipt_rejects(tmp_path: Path) -> None:
    """A loss record with NO receipt is a half-written claim (never silently
    tolerated as pre-39.1b shape)."""
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=_receipt(trimmed=True), callout=True),
        exercise_composition=None,
        exercise_overlay_loss=dict(_REAL_LOSS),
    )
    _assert_bar_rejects(tmp_path)


def test_malformed_receipt_rejects(tmp_path: Path) -> None:
    receipt = _receipt(trimmed=False)
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=False),
        exercise_composition={"sections": "not-a-list", "collateral_trimmed_count": 0},
        exercise_overlay_loss=None,
    )
    _assert_bar_rejects(tmp_path)


def test_trim_tally_mismatch_rejects(tmp_path: Path) -> None:
    """The loss record's trimmed_count must equal the receipt tally."""
    receipt = _receipt(trimmed=True)
    mismatched = dict(_REAL_LOSS)
    mismatched["trimmed_count"] = 1
    _run_dir_with(
        tmp_path,
        _conforming_md(receipt=receipt, callout=True),
        exercise_composition=receipt,
        exercise_overlay_loss=mismatched,
    )
    _assert_bar_rejects(tmp_path)
