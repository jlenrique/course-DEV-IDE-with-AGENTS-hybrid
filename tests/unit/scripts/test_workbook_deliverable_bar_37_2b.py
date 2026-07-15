"""Story 37.2b — deliverable-bar deep-dive conformance + the FIVE negative pins.

The bar (`_assert_completed_workbook_deliverable`) asserts off the structured
run artifacts FIRST (07W.3 contribution + gate receipt from ``run.json``), then
a minimal MD floor. Known-bad artifacts are mutated copies of the frozen live
shapes and every one must REJECT
(``workbook-deliverable-nonconforming-despite-completed``).
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest
from docx import Document

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DeepDiveEnrichmentExecutionReceiptV1,
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
    make_request,
)
from tests.helpers.glossary_39_1 import swap_glossary_section


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


def _enriched_contribution() -> dict:
    request = make_request()
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


def _render_conforming_md(contribution_payload: dict) -> str:
    from app.marcus.lesson_plan.deep_dive_enrichment import (
        WorkbookReviewContributionV1,
    )

    contribution = WorkbookReviewContributionV1.model_validate_json(
        json.dumps(contribution_payload, separators=(",", ":")), strict=True
    )
    base = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    # 39.1 same-diff bar extension: the frozen fixture MD carries the PRE-39.1
    # title-mangled glossary; a conforming deliverable now carries the
    # term-keyed render for this contribution (the fixture file itself stays
    # frozen/digest-pinned — the swap is in-memory).
    base = swap_glossary_section(base, contribution)
    blocks = ["", "## Deep Dive", "", render_deep_dive_markdown(contribution), ""]
    references = render_deep_dive_reference_lines(contribution)
    if references:
        # 39.1 P5 (row-j placement): the cited-entries block lives INSIDE the
        # ``## References`` section — where the producer emits it and where
        # the glossary bar witnesses resolvability.
        cited_block = "\n".join(
            ["#### Deep Dive cited entries (Ask-A, DOI)", *references, ""]
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


def _run_dir_with(
    tmp_path: Path, contribution_payload: dict | None, markdown: str
) -> Path:
    extra = ()
    if contribution_payload is not None:
        extra = (("workbook_review", "07W.3", contribution_payload, "gpt-5"),)
    install_run_json(tmp_path, ask_a_output=None, extra_contributions=extra)
    _emit_deliverable(tmp_path, markdown)
    return tmp_path


def _assert_bar(run_dir: Path) -> None:
    runner._assert_completed_workbook_deliverable(uuid4(), run_dir)


def _assert_bar_rejects(run_dir: Path) -> None:
    with pytest.raises(runner.RunnerRefusal) as caught:
        _assert_bar(run_dir)
    assert str(caught.value) == "workbook-deliverable-nonconforming-despite-completed"


def test_enriched_contribution_with_conforming_md_passes(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    _run_dir_with(tmp_path, contribution, _render_conforming_md(contribution))
    _assert_bar(tmp_path)


def test_degraded_contribution_with_honest_note_passes(tmp_path: Path) -> None:
    contribution = _degraded_contribution()
    _run_dir_with(tmp_path, contribution, _render_conforming_md(contribution))
    _assert_bar(tmp_path)


def test_legacy_stub_contribution_keeps_prior_bar_unchanged(tmp_path: Path) -> None:
    stub = {
        "stub_status": "not_yet_wired",
        "review_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }
    # 39.1: a stub contribution loads as None ⇒ the glossary must render the
    # explicit ``bold-term authority absent`` reason (matrix row d) — the
    # deep-dive clauses themselves stay unchanged.
    markdown = swap_glossary_section(
        RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8"), None
    )
    _run_dir_with(tmp_path, stub, markdown)
    _assert_bar(tmp_path)


# ---------------------------------------------------------------------------
# The FIVE negative-witness pins (protocol plank M-D3-2b + amendment M4)
# ---------------------------------------------------------------------------


def test_negative_pin_1_phantom_citation_contribution_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    for holder in (contribution["deep_dive_enrichment"]["sections"],
                   contribution["deep_dive_enrichment"]["candidate_snapshot"]["sections"]):
        for section in holder:
            for claim in section["claims"]:
                if claim["role"] == "enrichment":
                    claim["citation_refs"] = ["ask-a-cite-777"]
    _run_dir_with(tmp_path, contribution, _render_conforming_md(_enriched_contribution()))
    _assert_bar_rejects(tmp_path)


def test_negative_pin_2_enriched_status_with_zero_citations_rejects(
    tmp_path: Path,
) -> None:
    contribution = _enriched_contribution()
    for holder in (contribution["deep_dive_enrichment"]["sections"],
                   contribution["deep_dive_enrichment"]["candidate_snapshot"]["sections"]):
        for section in holder:
            section["claims"] = [
                claim for claim in section["claims"] if claim["role"] == "skeleton"
            ]
            section["prose"] = " ".join(claim["text"] for claim in section["claims"])
    _run_dir_with(tmp_path, contribution, _render_conforming_md(_enriched_contribution()))
    _assert_bar_rejects(tmp_path)


def test_negative_pin_3_marker_without_reference_entry_rejects(tmp_path: Path) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution)
    markdown = markdown.replace("#### Deep Dive cited entries (Ask-A, DOI)", "").replace(
        "citation_id: `ask-a-cite-001`", "citation_id withheld"
    )
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_negative_pin_4_enriched_claim_with_missing_section_rejects(
    tmp_path: Path,
) -> None:
    contribution = _enriched_contribution()
    markdown = _render_conforming_md(contribution).replace("## Deep Dive", "## Depths")
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


def test_negative_pin_5_degraded_status_with_stray_marker_rejects(
    tmp_path: Path,
) -> None:
    """Amendment M4: closes the only bar clause with no adversarial input."""
    contribution = _degraded_contribution()
    markdown = _render_conforming_md(contribution) + "\nStray claim. [ask-a-cite-001]\n"
    _run_dir_with(tmp_path, contribution, markdown)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# R3: the M4 stray-marker scan runs in EVERY branch of the bar
# ---------------------------------------------------------------------------


def test_r3_run_json_absent_with_stray_marker_rejects(tmp_path: Path) -> None:
    base = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    _emit_deliverable(tmp_path, base + "\nStray claim. [ask-a-cite-001]\n")
    assert not (tmp_path / "run.json").exists()
    _assert_bar_rejects(tmp_path)


def test_r3_run_json_absent_without_markers_passes(tmp_path: Path) -> None:
    """The deep-dive R3 branch itself stays permissive without markers. The MD
    is legacy-ized in-memory because 39.1 P15 now REJECTS a presentation-
    support deliverable whose glossary section has no run.json authority —
    that refusal is pinned separately in test_workbook_deliverable_bar_39_1."""
    base = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8").replace(
        runner._PRESENTATION_SUPPORT_MD_SENTINEL,
        "This legacy companion workbook carries",
        1,
    )
    _emit_deliverable(tmp_path, base)
    _assert_bar(tmp_path)


def test_p15_run_json_absent_presentation_support_glossary_rejects(
    tmp_path: Path,
) -> None:
    """39.1 P15 (mirror R3): the untouched presentation-support fixture MD —
    marker-free but carrying a glossary section — REFUSES without run.json."""
    _emit_deliverable(tmp_path, RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8"))
    _assert_bar_rejects(tmp_path)


def test_r3_contribution_absent_with_stray_marker_rejects(tmp_path: Path) -> None:
    """run.json present but NO 07W.3 review contribution at all — a marker
    still has no activated cited contribution behind it."""
    base = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    _run_dir_with(tmp_path, None, base + "\nStray claim. [ask-a-cite-001]\n")
    _assert_bar_rejects(tmp_path)


def test_r3_legacy_stub_with_stray_marker_rejects(tmp_path: Path) -> None:
    stub = {
        "stub_status": "not_yet_wired",
        "review_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }
    base = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    _run_dir_with(tmp_path, stub, base + "\nStray claim. [ask-a-cite-001]\n")
    _assert_bar_rejects(tmp_path)
