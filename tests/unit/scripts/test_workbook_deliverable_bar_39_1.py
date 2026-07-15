"""Story 39.1 — deliverable-bar glossary clause + the FIVE negative pins.

Same-diff bar extension (protocol plank 5 + M-D3-2b): the glossary clause in
``_assert_completed_workbook_deliverable`` is fed mutated copies of the frozen
live shapes and every named mutant must REJECT
(``workbook-deliverable-nonconforming-despite-completed``):

  (i)   mangled title-derived headword present (the REAL 8b275e5b string)
  (ii)  bolded term with no entry (missing entry)
  (iii) orphan entry (an entry no bolded term backs)
  (iv)  uncovered term carrying a citation
  (v)   entry whose tier differs from its pool row's

Plus the row-j resolvability pin on a glossary-ONLY citation (AC-A9 seam).
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
from scripts.utilities import marcus_spoc_live_test_runner as runner
from tests.helpers.deep_dive_enrichment_37_2b import (
    RENDERED_WORKBOOK_FIXTURE,
    degraded_candidate,
    enriched_candidate,
    install_run_json,
    live_pool_entry,
    make_request,
    mutated_pool_entry,
)
from tests.helpers.glossary_39_1 import (
    glossary_only_reference_lines,
    mangled_headwords,
    swap_glossary_section,
)


def _receipt(request, *, mode: str = "live") -> DeepDiveEnrichmentExecutionReceiptV1:
    return DeepDiveEnrichmentExecutionReceiptV1(
        mode=mode,  # type: ignore[arg-type]
        calls=1 if mode == "live" else 0,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model="gpt-5" if mode == "live" else None,
        model_config_digest="sha256:" + "3" * 64,
        cost_usd=0.05 if mode == "live" else None,
    )


def _enriched_contribution(*, extra_pool_row: bool = False) -> dict:
    kwargs = {}
    if extra_pool_row:
        kwargs["pool_rows"] = (
            live_pool_entry(),
            mutated_pool_entry(citation_id="ask-a-cite-002"),
        )
    request = make_request(**kwargs)
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    contribution = build_workbook_review_contribution(result, _receipt(request))
    return json.loads(contribution.model_dump_json())


def _degraded_contribution() -> dict:
    request = make_request()
    result = compose_deep_dive_enrichment(
        request, lambda _: degraded_candidate("deep_dive_enrichment_pool_unused")
    )
    contribution = build_workbook_review_contribution(
        result, _receipt(request, mode="offline_stub")
    )
    return json.loads(contribution.model_dump_json())


def _load(contribution_payload: dict) -> WorkbookReviewContributionV1:
    return WorkbookReviewContributionV1.model_validate_json(
        json.dumps(contribution_payload, separators=(",", ":")), strict=True
    )


def _render_conforming_md(contribution_payload: dict) -> str:
    contribution = _load(contribution_payload)
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
        # P5 (row-j placement): the cited-entries block lives INSIDE the
        # ``## References`` section — exactly where the producer emits it and
        # where the bar witnesses resolvability (never at document end).
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
        base = base.replace(
            trends_marker, f"\n{cited_block}{trends_marker}", 1
        )
    return base + "\n".join(blocks)


def _emit_deliverable(run_dir: Path, markdown: str) -> None:
    exports = run_dir / "exports" / "workbooks"
    exports.mkdir(parents=True)
    (exports / "u01@1.md").write_text(markdown, encoding="utf-8")
    document = Document()
    document.add_heading("Workbook", level=0)
    document.save(str(exports / "u01@1.docx"))


def _run_dir_with(tmp_path: Path, contribution_payload: dict, markdown: str) -> Path:
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(
            ("workbook_review", "07W.3", contribution_payload, "gpt-5"),
        ),
    )
    _emit_deliverable(tmp_path, markdown)
    return tmp_path


def _assert_bar(run_dir: Path) -> None:
    runner._assert_completed_workbook_deliverable(uuid4(), run_dir)


def _assert_bar_rejects(run_dir: Path) -> None:
    with pytest.raises(runner.RunnerRefusal) as caught:
        _assert_bar(run_dir)
    assert str(caught.value) == "workbook-deliverable-nonconforming-despite-completed"


# ---------------------------------------------------------------------------
# Positive floors (the clause accepts the conforming shapes)
# ---------------------------------------------------------------------------


def test_enriched_conforming_glossary_passes(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    _run_dir_with(tmp_path, contribution, _render_conforming_md(contribution))
    _assert_bar(tmp_path)


def test_degraded_all_uncovered_glossary_passes(tmp_path: Path) -> None:
    contribution = _degraded_contribution()
    _run_dir_with(tmp_path, contribution, _render_conforming_md(contribution))
    _assert_bar(tmp_path)


def test_glossary_only_citation_conforming_passes(tmp_path: Path) -> None:
    contribution = _enriched_contribution(extra_pool_row=True)
    _run_dir_with(tmp_path, contribution, _render_conforming_md(contribution))
    _assert_bar(tmp_path)


# ---------------------------------------------------------------------------
# The FIVE negative-witness pins (AC-A7)
# ---------------------------------------------------------------------------


def test_negative_pin_i_mangled_title_derived_headword_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        "### AI\n", f"### {mangled_headwords()[0]}\n", 1
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_negative_pin_ii_bolded_term_with_no_entry_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution)
    # Remove the "governance" entry entirely (heading + its lean line).
    markdown = markdown.replace(
        "\n### governance\n\nKey term from the Deep Dive. No research row in "
        "this run's pool covers it; no definition is invented.\n",
        "\n",
        1,
    )
    assert "### governance" not in markdown
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_negative_pin_iii_orphan_entry_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        "\n## References",
        "\n### Orphaned Construct\n\nKey term from the Deep Dive. No research "
        "row in this run's pool covers it; no definition is invented.\n"
        "\n## References",
        1,
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_negative_pin_iv_uncovered_term_carrying_citation_rejects(
    tmp_path: Path,
) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        "\n### governance\n\nKey term from the Deep Dive.",
        "\n### governance\n\n**Provenance:** `ask-a-cite-001` · tier="
        "T4_peer_other\n\nKey term from the Deep Dive.",
        1,
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_negative_pin_v_tier_differing_from_pool_row_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution)
    glossary_start = markdown.index("## Research Glossary")
    references_start = markdown.index("## References", glossary_start)
    mutated_section = markdown[glossary_start:references_start].replace(
        "tier=T4_peer_other", "tier=T1_systematic"
    )
    markdown = (
        markdown[:glossary_start] + mutated_section + markdown[references_start:]
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# Row j — glossary-ONLY citation must resolve OUTSIDE the glossary section
# ---------------------------------------------------------------------------


def test_row_j_glossary_only_citation_without_reference_entry_rejects(
    tmp_path: Path,
) -> None:
    contribution = _enriched_contribution(extra_pool_row=True)
    markdown = _render_conforming_md(contribution)
    # Strip the appended reference line for the glossary-only ask-a-cite-002;
    # the glossary's own provenance line must not satisfy resolvability.
    lines = [
        line
        for line in markdown.splitlines()
        if not ("citation_id: `ask-a-cite-002`" in line and line.startswith("- "))
    ]
    markdown = "\n".join(lines)
    assert "`ask-a-cite-002`" in markdown  # still cited in the glossary entry
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# Coverage-line reconciliation (the lead line cannot lie)
# ---------------------------------------------------------------------------


def test_coverage_line_mismatch_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        "Research coverage this run: 1 of 11 terms.",
        "Research coverage this run: 11 of 11 terms.",
        1,
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# P2 — row-d′ state accuracy on the bar (degraded-covered line is MANDATORY)
# ---------------------------------------------------------------------------

_UNCOVERED_LINE = (
    "Key term from the Deep Dive. No research row in this run's pool covers "
    "it; no definition is invented."
)
_UNCOVERED_DEGRADED_LINE = (
    "Enrichment was degraded this run; a research row associates with this "
    "term but was not composed."
)


def test_p2_degraded_covered_term_with_plain_line_rejects(tmp_path: Path) -> None:
    """Degraded run, pool PRESENT, 'AI' association-covered: rendering the
    plain "no research row covers it" line is state-INACCURATE ⇒ REJECT."""
    contribution = _degraded_contribution()
    markdown = _render_conforming_md(contribution)
    assert _UNCOVERED_DEGRADED_LINE in markdown  # the conforming render
    markdown = markdown.replace(_UNCOVERED_DEGRADED_LINE, _UNCOVERED_LINE, 1)
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_p2_enriched_uncovered_term_with_degraded_line_rejects(tmp_path: Path) -> None:
    """Enriched run: a genuinely-uncovered term claiming degradation is
    equally state-inaccurate ⇒ REJECT."""
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        _UNCOVERED_LINE, _UNCOVERED_DEGRADED_LINE, 1
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# P3 — structural leanness: heading + EXACTLY one permitted line, nothing else
# ---------------------------------------------------------------------------


def test_p3_uncovered_entry_with_appended_definition_rejects(tmp_path: Path) -> None:
    """An uncovered entry carrying ANY extra body beyond its one permitted
    line (e.g. an appended fabricated definition with no citation/tier that
    the old greps could not see) ⇒ REJECT."""
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        f"\n### governance\n\n{_UNCOVERED_LINE}\n",
        f"\n### governance\n\n{_UNCOVERED_LINE}\n\n"
        "Governance is the body of policy that determines how hospital AI "
        "systems are deployed and audited.\n",
        1,
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# P4 — covered-body attribution sweep (any idiom, any line)
# ---------------------------------------------------------------------------


def test_p4_foreign_citation_token_in_covered_body_rejects(tmp_path: Path) -> None:
    """An ask-a-cite token inside a covered entry's prose that is NOT one of
    the entry's covering citation ids ⇒ REJECT (even without the Provenance
    idiom or the [marker] bracket shape)."""
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        "**AI** is a key term bolded in this workbook's Deep",
        "**AI** (see ask-a-cite-009) is a key term bolded in this workbook's Deep",
        1,
    )
    assert "ask-a-cite-009" in markdown
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# P9 — singularity: ONE glossary section, ONE coverage line (counted)
# ---------------------------------------------------------------------------


def test_p9_duplicate_glossary_section_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution) + (
        "\n## Research Glossary\n\nResearch coverage this run: 1 of 11 terms.\n"
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_p9_duplicate_coverage_line_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace(
        "Research coverage this run: 1 of 11 terms.",
        "Research coverage this run: 1 of 11 terms.\n\n"
        "Research coverage this run: 1 of 11 terms.",
        1,
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# P15 — glossary section without structured authority ⇒ REJECT (mirror R3)
# ---------------------------------------------------------------------------


def test_p15_glossary_section_without_run_json_rejects(tmp_path: Path) -> None:
    """A presentation-support MD carrying a ``## Research Glossary`` section
    with NO run.json behind it is a refusal — never a silent skip."""
    contribution = _degraded_contribution()  # marker-free deliverable
    markdown = _render_conforming_md(contribution)
    _emit_deliverable(tmp_path, markdown)
    assert not (tmp_path / "run.json").exists()
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# M-R3 — LO shippability bar (closure rider): the producer's persisted
# ``lo_overlay_loss`` record is the structured assertion surface
# ---------------------------------------------------------------------------

# The REAL a940c5eb-1043-42c1-a2a4-8a6301b6bcf4 record (the pre-fix live run:
# 6 of 6 bound objectives resolved no enrichment overlay) lifted VERBATIM from
# ``runs/a940c5eb-…/run.json`` as the negative witness.
_A940C5EB_LO_OVERLAY_LOSS = {
    "unresolved_count": 6,
    "bound_count": 6,
    "unresolved_objectives": ["u01", "u02", "u03", "u04", "u05", "u06"],
    "note": (
        "6 of 6 learning objective(s) resolved no enrichment overlay "
        "(statement/Bloom degraded to placeholder): u01, u02, u03, u04, "
        "u05, u06"
    ),
}

# The producer's degraded-LO placeholder statement + visible loss callout as
# rendered into the deliverable (MD-floor witnesses).
_LO_PLACEHOLDER_LINE = (
    "- **`u01`** — _understand_: (objective statement unresolved for `u01` — "
    "no enrichment overlay resolved this objective on this run) "
    "(served by section(s): `sec-u01`)"
)
_LO_LOSS_CALLOUT_LINE = (
    "> _Enrichment overlay loss: 6 of 6 learning objective(s) resolved no "
    "enrichment overlay (statement/Bloom degraded to placeholder): u01, u02, "
    "u03, u04, u05, u06_"
)


def _producer_output(lo_overlay_loss: dict | None) -> dict:
    """The persisted 07W refs shape (8b275e5b carries the same coordinate with
    ``\"lo_overlay_loss\": null`` — the LO-verified clean run)."""
    return {
        "workbook": {
            "asset_ref": "workbook-u01@1",
            "asset_path": "exports/workbooks/u01@1.md",
            "fulfills": "u01@1",
            "modality_ref": "workbook",
            "markdown_path": "exports/workbooks/u01@1.md",
            "docx_path": "exports/workbooks/u01@1.docx",
            "lo_overlay_loss": lo_overlay_loss,
        }
    }


def _run_dir_with_producer(
    tmp_path: Path,
    contribution_payload: dict,
    markdown: str,
    lo_overlay_loss: dict | None,
) -> Path:
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(
            ("workbook_review", "07W.3", contribution_payload, "gpt-5"),
            (
                "workbook_producer",
                "07W",
                _producer_output(lo_overlay_loss),
                "gpt-5",
            ),
        ),
    )
    _emit_deliverable(tmp_path, markdown)
    return tmp_path


def test_mr3_negative_witness_a940c5eb_lo_overlay_loss_rejects(
    tmp_path: Path,
) -> None:
    """NEGATIVE-WITNESS pin: the real a940c5eb 6/6-unresolved record on the
    persisted contribution REFUSES the deliverable off the STRUCTURED channel
    alone (the MD is otherwise fully conforming), naming the objectives."""
    contribution = _enriched_contribution()
    _run_dir_with_producer(
        tmp_path,
        contribution,
        _render_conforming_md(contribution),
        dict(_A940C5EB_LO_OVERLAY_LOSS),
    )
    with pytest.raises(runner.RunnerRefusal) as caught:
        _assert_bar(tmp_path)
    assert str(caught.value) == "workbook-deliverable-nonconforming-despite-completed"
    notes = "\n".join(getattr(caught.value, "__notes__", []))
    for objective in _A940C5EB_LO_OVERLAY_LOSS["unresolved_objectives"]:
        assert objective in notes


def test_mr3_clean_8b275e5b_shape_passes(tmp_path: Path) -> None:
    """The LO-verified clean shape (8b275e5b: contribution present,
    ``lo_overlay_loss`` null, placeholder-free MD) passes the bar."""
    contribution = _enriched_contribution()
    _run_dir_with_producer(
        tmp_path, contribution, _render_conforming_md(contribution), None
    )
    _assert_bar(tmp_path)


def test_mr3_placeholder_in_md_without_record_rejects(tmp_path: Path) -> None:
    """MD floor: the placeholder copy on a presentation-support deliverable
    while the persisted contribution's record is null ⇒ REFUSE (desync)."""
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution) + f"\n{_LO_PLACEHOLDER_LINE}\n"
    _run_dir_with_producer(tmp_path, contribution, markdown, None)
    _assert_bar_rejects(tmp_path)


def test_mr3_loss_callout_in_md_without_record_rejects(tmp_path: Path) -> None:
    """MD floor: an ``Enrichment overlay loss`` callout no structured record
    backs ⇒ REFUSE (a callout can only be minted by a populated record)."""
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution) + f"\n{_LO_LOSS_CALLOUT_LINE}\n"
    _run_dir_with_producer(tmp_path, contribution, markdown, None)
    _assert_bar_rejects(tmp_path)
