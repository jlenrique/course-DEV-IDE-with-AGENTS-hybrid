"""Story 39.2 — deliverable-bar trends/Door-Ajar clause + negative pins.

Same-diff bar extension (protocol plank 5 + M-D3-2b): the trends clause in
``_assert_completed_workbook_deliverable`` recomputes its authority off
``run.json`` (``resolve_for_hot_topics`` → ``project_trends_from_packet``
with the ``_act.py`` production defaults — NO persisted trends receipt
exists on the 07W contribution) and is fed mutated copies of the frozen
shapes; every named mutant must REJECT
(``workbook-deliverable-nonconforming-despite-completed``):

  1. fabricated trend without packet backing (matrix row 9)
  2. unusable topic re-rendered as usable / label rewritten (row 10)
  3. empty-class packet with a populated trends render (row 11)
  4. USABLE row DROPPED from an otherwise-conformant render (row 14, M-1 —
     the silent-loss direction)

Positive floors: the conforming USABLE render off the REAL frozen 79f1920e
Ask-B extract passes; the conforming EMPTY-honest render passes (row 12 —
the M-5/J-2 designed outcome is bar-conforming, KEPT as a timeless defense
pin per A-2). W-2 pins the bar recompute defaults against the ``_act.py``
production call. M-4 (row 16) pins the presentation-support-sentinel
scoping: the section renders in the legacy profile too, and legacy-profile
deliverables are OUT of clause scope. P15 mirror: grounded-claim content
with no ``run.json`` behind it refuses; explicit-empty is tolerated.
"""

from __future__ import annotations

import ast
import inspect
import json
import re
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
from app.marcus.lesson_plan.trends_projection import trends_inputs_from_run
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
from tests.helpers.trends_39_2 import frozen_ask_b_output, swap_trends_section
from tests.unit.marcus.lesson_plan.test_trends_door_ajar_39_2 import (
    _completed_empty_ask_b_output,
)

_ASK_B_MODEL_USED = "deterministic-ask-b-hot-topics-wiring"


# ---------------------------------------------------------------------------
# Conforming-baseline rig (mirrors test_workbook_deliverable_bar_39_1b)
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


def _render_base_md(contribution_payload: dict) -> str:
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


def _producer_output() -> dict:
    return {
        "workbook": {
            "asset_ref": "workbook-u01@1",
            "asset_path": "exports/workbooks/u01@1.md",
            "fulfills": "u01@1",
            "modality_ref": "workbook",
            "markdown_path": "exports/workbooks/u01@1.md",
            "docx_path": "exports/workbooks/u01@1.docx",
            "lo_overlay_loss": None,
        }
    }


def _run_dir_with(
    tmp_path: Path,
    *,
    ask_b_output: dict | None,
    mutate=None,
    skip_trends_swap: bool = False,
) -> Path:
    """Install a run + emit the deliverable. The trends section is swapped to
    the recomputed conforming render (unless ``skip_trends_swap`` keeps the
    frozen fixture's pre-39.2 populated section as the mutant), then
    ``mutate`` (str -> str) is applied to produce the negative-witness."""
    contribution = _enriched_contribution()
    extra = [
        ("workbook_review", "07W.3", contribution, "gpt-5"),
        ("workbook_producer", "07W", _producer_output(), "gpt-5"),
    ]
    if ask_b_output is not None:
        extra.append(("ask_b_hot_topics", "07W.4", ask_b_output, _ASK_B_MODEL_USED))
    install_run_json(tmp_path, ask_a_output=None, extra_contributions=tuple(extra))
    markdown = _render_base_md(contribution)
    if not skip_trends_swap:
        markdown = swap_trends_section(markdown, tmp_path)
    if mutate is not None:
        markdown = mutate(markdown)
    _emit_deliverable(tmp_path, markdown)
    return tmp_path


def _assert_bar(run_dir: Path) -> None:
    runner._assert_completed_workbook_deliverable(uuid4(), run_dir)


def _assert_bar_rejects(run_dir: Path) -> None:
    with pytest.raises(runner.RunnerRefusal) as caught:
        _assert_bar(run_dir)
    assert str(caught.value) == "workbook-deliverable-nonconforming-despite-completed"


def _trends_section(markdown: str) -> str:
    start = markdown.index("\n## Research Trends\n")
    rest = markdown[start + len("\n## Research Trends\n") :]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


# ---------------------------------------------------------------------------
# Positive floors
# ---------------------------------------------------------------------------


def test_conforming_usable_door_ajar_passes(tmp_path: Path) -> None:
    """The REAL frozen 79f1920e Ask-B extract + the recomputed render: the
    bar accepts the usable Door-Ajar (matrix row 1's bar-side baseline)."""
    _run_dir_with(tmp_path, ask_b_output=frozen_ask_b_output())
    _assert_bar(tmp_path)


def test_row12_conforming_empty_class_a_passes(tmp_path: Path) -> None:
    """Matrix row 12 (M-5/J-2, KEPT per A-2): an empty-class run (a —
    contribution absent) whose MD carries the honest explicit-empty render is
    ACCEPTED — the empty-honesty rule can never be "fixed" into a refusal."""
    _run_dir_with(tmp_path, ask_b_output=None)
    _assert_bar(tmp_path)


def test_row12_conforming_empty_class_b_passes(tmp_path: Path) -> None:
    """Matrix row 12 on empty class (b): a strict ``completed_empty`` Ask-B
    contribution + the explicit-empty render is bar-conforming — the designed
    honest outcome, never a defect."""
    _run_dir_with(tmp_path, ask_b_output=_completed_empty_ask_b_output())
    _assert_bar(tmp_path)


# ---------------------------------------------------------------------------
# Negative-witness pins (M-D3-2b — every mutant must REJECT)
# ---------------------------------------------------------------------------

_FABRICATED_TREND_BLOCK = (
    "- Indexed literature signals continuing attention to **fabricated "
    "frontier**, as framed by “Fabricated”. This trend claim is "
    "research-informed from the wrangled packet row — not a forecast and "
    "not a semantic claim audit.\n"
    "  - **Provenance:** `ask-b-cite-999` · `retrieval:scite:10.9999/fab` · "
    "tier=T4_peer_other, peer-reviewed, triangulation=single_provider, "
    "confidence=medium\n\n"
)


def test_row9_fabricated_trend_without_packet_backing_rejects(tmp_path: Path) -> None:
    """Negative pin 1 (matrix row 9): a conformant deliverable mutated to add
    a trend claim whose citation id / source_ref are NOT in the packet."""

    def mutate(markdown: str) -> str:
        anchor = "#### Research trends\n\n"
        assert anchor in markdown
        return markdown.replace(anchor, anchor + _FABRICATED_TREND_BLOCK, 1)

    _run_dir_with(tmp_path, ask_b_output=frozen_ask_b_output(), mutate=mutate)
    _assert_bar_rejects(tmp_path)


def test_row10_unusable_topic_rendered_as_usable_rejects(tmp_path: Path) -> None:
    """Negative pin 2 (matrix row 10): an unusable topic surfaced INSIDE the
    usable ``#### Hot topics`` list (moved out of the Rejected block)."""

    def mutate(markdown: str) -> str:
        section = _trends_section(markdown)
        topic_line = next(
            line
            for line in section.splitlines()
            if line.startswith("- **") and "(confidence=" in line
        )
        ghost = (
            "- **model-prior ghost** (confidence=unusable) — UNUSABLE: "
            "model-prior topic with no matching wrangled row. "
            "Supporting: `ask-b-cite-001`; source_refs: "
            "`retrieval:scite:10.1000/y`.\n"
        )
        return markdown.replace(topic_line, ghost + topic_line, 1)

    _run_dir_with(tmp_path, ask_b_output=frozen_ask_b_output(), mutate=mutate)
    _assert_bar_rejects(tmp_path)


def test_row10_confidence_label_rewritten_rejects(tmp_path: Path) -> None:
    """Negative pin 2 (label variant): a usable topic's rendered confidence
    label rewritten away from the recomputed value."""

    def mutate(markdown: str) -> str:
        section = _trends_section(markdown)
        match = re.search(r"\(confidence=([a-z]+)\)", section)
        assert match is not None
        rewritten = section.replace(
            f"(confidence={match.group(1)})", "(confidence=high)", 1
        )
        if rewritten == section:  # already high: rewrite downward instead
            rewritten = section.replace("(confidence=high)", "(confidence=low)", 1)
        return markdown.replace(section, rewritten, 1)

    _run_dir_with(tmp_path, ask_b_output=frozen_ask_b_output(), mutate=mutate)
    _assert_bar_rejects(tmp_path)


def test_row11_empty_packet_with_populated_render_rejects(tmp_path: Path) -> None:
    """Negative pin 3 (matrix row 11): run.json carries an empty-class Ask-B
    state while the MD renders a populated claim list (the frozen fixture's
    pre-39.2 generic-packet section, unswapped)."""
    _run_dir_with(tmp_path, ask_b_output=None, skip_trends_swap=True)
    _assert_bar_rejects(tmp_path)


def test_row11_completed_empty_with_populated_render_rejects(tmp_path: Path) -> None:
    """Negative pin 3 on empty class (b): a strict ``completed_empty`` packet
    with a populated render is equally a fabrication."""
    _run_dir_with(
        tmp_path,
        ask_b_output=_completed_empty_ask_b_output(),
        skip_trends_swap=True,
    )
    _assert_bar_rejects(tmp_path)


def test_row14_usable_row_dropped_from_render_rejects(tmp_path: Path) -> None:
    """Negative pin 4 (matrix row 14, M-1 — the silent-loss direction): the
    recompute yields a usable claim but the rendered set is missing it; the
    deliverable is otherwise conformant."""

    def mutate(markdown: str) -> str:
        section = _trends_section(markdown)
        lines = section.splitlines()
        kept = [
            line
            for line in lines
            if not (
                line.startswith("- Indexed literature signals")
                or line.startswith("  - **Provenance:**")
            )
        ]
        assert kept != lines  # the claim + provenance pair was present
        return markdown.replace(section, "\n".join(kept), 1)

    _run_dir_with(tmp_path, ask_b_output=frozen_ask_b_output(), mutate=mutate)
    _assert_bar_rejects(tmp_path)


def test_p9_duplicate_trends_section_rejects(tmp_path: Path) -> None:
    """P9 singularity: a second ``## Research Trends`` section (counted, not
    first-match) refuses."""

    def mutate(markdown: str) -> str:
        return markdown + "\n## Research Trends\n\n*(duplicate)*\n"

    _run_dir_with(tmp_path, ask_b_output=frozen_ask_b_output(), mutate=mutate)
    _assert_bar_rejects(tmp_path)


# ---------------------------------------------------------------------------
# Row 16 (M-4) — both-profiles scoping: renders in legacy, out of bar scope
# ---------------------------------------------------------------------------


def test_row16_section_renders_in_both_profiles() -> None:
    """Matrix row 16 (render half): the ``## Research Trends`` composition
    seam is unconditional in BOTH render profiles (workbook_producer.py
    appends the block after References in legacy and presentation_support
    alike)."""
    from app.marcus.lesson_plan.produced_asset import ProductionContext
    from app.marcus.lesson_plan.workbook_producer import (
        compose_workbook,
        default_prose_revoicer,
        load_transcript_segments,
        render_markdown,
    )
    from tests.unit.marcus.lesson_plan.test_trends_w3 import (
        TEJAL_MANIFEST,
        _plan,
        _spec,
    )

    segments = load_transcript_segments(TEJAL_MANIFEST)
    for profile in ("legacy", "presentation_support"):
        doc = compose_workbook(
            _plan(),
            ProductionContext(lesson_plan_revision=1, lesson_plan_digest="39-2"),
            _spec(),
            segments,
            prose_revoicer=default_prose_revoicer,
            research_trends=None,
            render_profile=profile,  # type: ignore[arg-type]
        )
        assert any(heading == "Research Trends" for _, heading, _ in doc.blocks)
        assert "## Research Trends" in render_markdown(doc)


def test_row16_legacy_profile_deliverable_out_of_clause_scope(tmp_path: Path) -> None:
    """Matrix row 16 (scoping half): the SAME nonconforming shape that
    rejects on a presentation-support deliverable (row 11: empty packet +
    populated render) is out of clause scope on a legacy-profile deliverable
    — the presentation-support-sentinel scoping is pinned, not assumed."""

    def legacyize(markdown: str) -> str:
        assert runner._PRESENTATION_SUPPORT_MD_SENTINEL in markdown
        return markdown.replace(
            runner._PRESENTATION_SUPPORT_MD_SENTINEL,
            "This legacy companion workbook carries",
            1,
        )

    _run_dir_with(
        tmp_path, ask_b_output=None, mutate=legacyize, skip_trends_swap=True
    )
    _assert_bar(tmp_path)


# ---------------------------------------------------------------------------
# W-2 — defaults-drift pin (bar recompute == _act.py effective call defaults)
# ---------------------------------------------------------------------------


def test_w2_bar_recompute_defaults_equal_act_call_defaults() -> None:
    """W-2: the bar clause's recompute defaults are asserted EQUAL to the
    ``_act.py`` L1217 effective call defaults — the signature defaults of
    ``trends_inputs_from_run`` (5 / 3 / no injected topics) AND the fact the
    sole production call site passes NO overrides. If either side drifts,
    this pin fails, so the bar's recompute authority can never silently
    diverge from the production call it stands in for."""
    signature = inspect.signature(trends_inputs_from_run)
    assert signature.parameters["max_trends"].default == runner._TRENDS_BAR_MAX_TRENDS == 5
    assert (
        signature.parameters["max_hot_topics"].default
        == runner._TRENDS_BAR_MAX_HOT_TOPICS
        == 3
    )
    assert (
        tuple(signature.parameters["injected_topics"].default)
        == runner._TRENDS_BAR_INJECTED_TOPICS
        == ()
    )
    # The sole production call site (`_act.py` L1217) passes no overrides.
    from app.specialists.workbook_producer import _act as wb_act

    tree = ast.parse(Path(wb_act.__file__).read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "trends_inputs_from_run"
    ]
    assert len(calls) == 1
    assert not calls[0].keywords
    assert len(calls[0].args) == 1


# ---------------------------------------------------------------------------
# P15 mirror — no run.json: grounded content refuses, explicit-empty tolerated
# ---------------------------------------------------------------------------


def test_no_run_json_grounded_trends_content_rejects(tmp_path: Path) -> None:
    """P15 mirror (clause-direct — the glossary clause's own P15 fires first
    through the full spine): a presentation-support MD whose trends section
    carries grounded-claim content with NO ``run.json`` behind it refuses."""
    markdown = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    assert runner._PRESENTATION_SUPPORT_MD_SENTINEL in markdown
    path = tmp_path / "u01@1.md"
    path.write_text(markdown, encoding="utf-8")
    with pytest.raises(runner.RunnerRefusal):
        runner._assert_trends_door_ajar_conformant(tmp_path, [path])


def test_no_run_json_explicit_empty_section_tolerated(tmp_path: Path) -> None:
    """R3-style tolerance: the section renders in every profile/run shape, so
    bare presence (explicit-empty) is never the refusal trigger — unlike the
    glossary heading. This includes the producer's None-brief fallback copy."""
    markdown = swap_trends_section(
        RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8"), tmp_path
    )
    path = tmp_path / "u01@1.md"
    path.write_text(markdown, encoding="utf-8")
    runner._assert_trends_door_ajar_conformant(tmp_path, [path])
    # The producer-side None-brief fallback shape is tolerated too.
    fallback = re.sub(
        r"(\n## Research Trends\n)(.*?)(?=\n## )",
        "\\1\n*(no research-trends brief supplied for this artifact; "
        "recorded explicitly-empty)*\n",
        RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8"),
        count=1,
        flags=re.DOTALL,
    )
    fallback_path = tmp_path / "u01@1-fallback.md"
    fallback_path.write_text(fallback, encoding="utf-8")
    runner._assert_trends_door_ajar_conformant(tmp_path, [fallback_path])
