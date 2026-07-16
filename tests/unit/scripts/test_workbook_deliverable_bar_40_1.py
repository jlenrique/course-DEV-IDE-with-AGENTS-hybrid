"""Story 40.1 — deliverable-bar cover clause + negative pins + M-5 battery.

Same-diff bar extension (protocol plank 5 + M-D3-2b): the cover clause in
``_assert_completed_workbook_deliverable`` asserts the persisted ``cover``
receipt on the 07W ``workbook_producer`` contribution FIRST (MD floor second)
and executes ONLY in the receipt-present branch (A-2). It is fed mutated
copies of the frozen live shapes (the committed 8b275e5b-derived cover
fixture) and every named mutant must REJECT
(``workbook-deliverable-nonconforming-despite-completed``):

  (a) a rendered section deleted from the TOC (missing entry — M-2 forward)
  (b) the hero placeholder replaced by an ``![…](…)`` image reference while
      the receipt still claims ``placeholder`` (fabricated hero claim)
  (c) the provenance run id mutated to mismatch ``run.json`` ``trial_id``
  (d) a wall-clock-mutated generation date (differs from the envelope
      ``started_at`` VALUE — M-3)
  (e) a phantom TOC entry naming no verbatim-matching rendered heading
      (M-2 reverse / matrix row j)

plus the matrix row i art-brief tripwires (schema_version mutation;
content-vs-digest mismatch) and the P9 duplicate-cover-section counter.

M-5 (named battery): the FULL ``_assert_completed_workbook_deliverable``
clause chain — every clause, INCLUDING 39-2's trends clause — runs against a
cover-bearing derived fixture built from the frozen run
``runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627``: the committed derived fixture
is the CI floor; the live-run replay leg is skip-if-absent (39-1b precedent).

A-2 regression: receipt-absent presentation-support MDs keep passing the
clause UNCHANGED (the existing 37_2b/39_1/39_1b/39_2 bar tests are the
spine-level regression bar; clause-direct tolerance is pinned here too).

OFFLINE ONLY: no live LLM / network / Gamma calls.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from docx import Document

from app.models.runtime.production_envelope import compute_output_digest
from scripts.utilities import marcus_spoc_live_test_runner as runner
from tests.helpers.deep_dive_enrichment_37_2b import (
    RENDERED_WORKBOOK_FIXTURE,
    install_run_json,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cover_40_1"
FIXTURE_MANIFEST = FIXTURE_DIR / "fixture-manifest.json"
COVER_FIXTURE_SCHEMA_VERSION = "cover-render-fixture.v1"
RUN_8B275E5B = REPO_ROOT / "runs" / "8b275e5b-ed8a-4720-8217-8ddaca4c6627"

_STEM = "u01@1"
_BRIEF_NAME = f"{_STEM}.cover-art-brief.json"


def _manifest() -> dict:
    manifest = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    # Digest-bound bump tripwire (live-shape rule): a schema drift means the
    # fixture shape changed — re-derive from the frozen run.
    assert manifest["schema_version"] == COVER_FIXTURE_SCHEMA_VERSION
    return manifest


def _fixture_bytes(name: str) -> bytes:
    manifest = _manifest()
    data = (FIXTURE_DIR / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest["files"][name]
    return data


def _rig(
    tmp_path: Path,
    *,
    mutate_md: Callable[[str], str] | None = None,
    mutate_receipt: Callable[[dict], None] | None = None,
    mutate_brief: Callable[[dict], None] | None = None,
    drop_brief: bool = False,
) -> tuple[UUID, Path]:
    """A run dir reconstructed from the committed 8b275e5b-derived fixture
    (mutated copies of frozen live shapes — never synthetic)."""
    trial = json.loads(
        _fixture_bytes("run-8b275e5b.trimmed.run.json").decode("utf-8")
    )
    if mutate_receipt is not None:
        for contribution in trial["production_envelope"]["contributions"]:
            if (
                contribution["specialist_id"] == "workbook_producer"
                and contribution.get("node_id") == "07W"
            ):
                mutate_receipt(contribution["output"]["workbook"]["cover"])
                contribution["output_digest"] = compute_output_digest(
                    contribution["output"]
                )
    (tmp_path / "run.json").write_text(
        json.dumps(trial, ensure_ascii=False), encoding="utf-8"
    )
    exports = tmp_path / "exports" / "workbooks"
    exports.mkdir(parents=True)
    markdown = _fixture_bytes(f"{_STEM}.cover.md").decode("utf-8")
    if mutate_md is not None:
        # LF-normalize before mutating (the committed fixture rides the
        # platform CRLF the producer's write_text emitted; the bar clause
        # LF-normalizes on read, so mutants may be written LF-only).
        markdown = mutate_md(markdown.replace("\r\n", "\n"))
    (exports / f"{_STEM}.md").write_text(markdown, encoding="utf-8", newline="\n")
    document = Document()
    document.add_heading("Workbook", level=0)
    document.save(str(exports / f"{_STEM}.docx"))
    if not drop_brief:
        brief = json.loads(_fixture_bytes(_BRIEF_NAME).decode("utf-8"))
        if mutate_brief is not None:
            mutate_brief(brief)
        (exports / _BRIEF_NAME).write_text(
            json.dumps(brief, sort_keys=True, ensure_ascii=True, separators=(",", ":")),
            encoding="utf-8",
        )
    return UUID(trial["trial_id"]), tmp_path


def _assert_bar(trial_id: UUID, run_dir: Path) -> None:
    runner._assert_completed_workbook_deliverable(trial_id, run_dir)


def _assert_bar_rejects(trial_id: UUID, run_dir: Path) -> None:
    with pytest.raises(runner.RunnerRefusal) as caught:
        _assert_bar(trial_id, run_dir)
    assert str(caught.value) == "workbook-deliverable-nonconforming-despite-completed"


# ---------------------------------------------------------------------------
# M-5 — named battery: the FULL clause chain on the cover-bearing derived
# fixture (committed CI floor + skip-if-absent live replay, 39-1b precedent)
# ---------------------------------------------------------------------------


def test_m5_full_clause_chain_battery_committed_derived_fixture(tmp_path: Path) -> None:
    """M-5 CI floor: EVERY clause of ``_assert_completed_workbook_deliverable``
    — deep-dive, glossary, LO-overlay, exercise (39-1b), trends (39-2), and
    the 40-1 cover clause — runs green on the committed cover-bearing fixture
    derived from frozen run 8b275e5b."""
    trial_id, run_dir = _rig(tmp_path)
    _assert_bar(trial_id, run_dir)


def test_m5_full_clause_chain_battery_live_8b275e5b_replay(tmp_path: Path) -> None:
    """M-5 live leg (skip-if-absent): replay the derivation off the real
    frozen run dir — copy, drop the legacy Ask-B stub (39-1b precedent),
    build inputs off the real brief, produce the cover-bearing deliverable,
    inject ``_sidecar_refs`` into the copied run.json, then run the FULL
    clause chain. Also pins the derived artifacts byte-identical to the
    committed fixture (fixture honesty — regenerate on intentional change)."""
    if not (RUN_8B275E5B / "run.json").is_file():
        pytest.skip("run 8b275e5b artifacts unavailable")
    from app.marcus.lesson_plan.prework_artifact import read_workbook_brief
    from app.marcus.lesson_plan.workbook_producer import WorkbookProducer
    from app.specialists.workbook_producer import _act as wb_act

    replay = tmp_path / "8b275e5b-replay"
    shutil.copytree(RUN_8B275E5B, replay)
    trial = json.loads((replay / "run.json").read_text(encoding="utf-8"))
    envelope = trial["production_envelope"]
    envelope["contributions"] = [
        c
        for c in envelope["contributions"]
        if not (
            c["specialist_id"] == "ask_b_hot_topics"
            and c.get("node_id") == "07W.4"
            and isinstance(c.get("output"), dict)
            and c["output"].get("stub_status") == "not_yet_wired"
        )
    ]
    (replay / "run.json").write_text(json.dumps(trial, ensure_ascii=False), "utf-8")
    brief = read_workbook_brief(replay)
    inputs = wb_act.build_workbook_inputs(
        replay, run_id=trial["trial_id"], validated_brief=brief
    )
    assert inputs is not None and inputs.cover_inputs is not None
    producer = WorkbookProducer(output_root=replay / "exports" / "workbooks")
    sidecar = producer.produce(
        inputs.plan_unit,
        inputs.context,
        workbook_title=inputs.workbook_title,
        spec=inputs.spec,
        segments=inputs.segments,
        source_text=inputs.source_text,
        citations=inputs.citations,
        source_ref_manifest=inputs.source_ref_manifest,
        vo_script_text=inputs.vo_script_text,
        learning_objectives=inputs.learning_objectives,
        answer_keys=inputs.answer_keys,
        further_reading=inputs.further_reading,
        research_entries=inputs.research_entries,
        research_empty_reason=inputs.research_empty_reason,
        research_omitted_note=inputs.research_omitted_note,
        glossary_articles=inputs.glossary_articles,
        glossary_empty_reason=inputs.glossary_empty_reason,
        glossary=inputs.glossary,
        research_trends=inputs.research_trends,
        research_supplements=inputs.research_supplements,
        lo_overlay_loss=inputs.lo_overlay_loss,
        exercise_overlay_loss=inputs.exercise_overlay_loss,
        pre_work=inputs.pre_work,
        encounter_mode=inputs.encounter_mode,
        render_profile=inputs.render_profile,
        workbook_brief_receipt=inputs.workbook_brief_receipt,
        deep_dive_review=inputs.deep_dive_review,
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha=trial["trial_id"][:8],
        cover_inputs=inputs.cover_inputs,
    )
    assert sidecar.cover is not None
    refs = wb_act._sidecar_refs(sidecar)
    new_output = {
        "workbook": refs,
        "workbook_producer": {
            "specialist_id": "workbook_producer",
            "docx_path": sidecar.docx_path,
            "markdown_path": sidecar.markdown_path,
        },
    }
    for c in envelope["contributions"]:
        if c["specialist_id"] == "workbook_producer" and c.get("node_id") == "07W":
            c["output"] = new_output
            c["output_digest"] = compute_output_digest(new_output)
    (replay / "run.json").write_text(json.dumps(trial, ensure_ascii=False), "utf-8")
    _assert_bar(UUID(trial["trial_id"]), replay)
    # Fixture honesty: the derived deliverable matches the committed fixture.
    manifest = _manifest()
    md_bytes = (replay / "exports" / "workbooks" / f"{_STEM}.md").read_bytes()
    brief_bytes = (replay / "exports" / "workbooks" / _BRIEF_NAME).read_bytes()
    assert hashlib.sha256(md_bytes).hexdigest() == manifest["files"][f"{_STEM}.cover.md"]
    assert (
        hashlib.sha256(brief_bytes).hexdigest() == manifest["files"][_BRIEF_NAME]
    )


# ---------------------------------------------------------------------------
# Negative-witness pins (M-D3-2b — every mutant must REJECT)
# ---------------------------------------------------------------------------


def test_pin_a_rendered_section_missing_from_toc_rejects(tmp_path: Path) -> None:
    """Pin (a): a rendered section deleted from the TOC — the Exercises entry
    line is removed while ``## Exercises`` still renders (M-2 forward)."""

    def mutate(markdown: str) -> str:
        line = "- Test yourself — `Exercises`\n"
        assert line in markdown
        return markdown.replace(line, "", 1)

    trial_id, run_dir = _rig(tmp_path, mutate_md=mutate)
    _assert_bar_rejects(trial_id, run_dir)


def test_pin_b_hero_image_reference_rejects(tmp_path: Path) -> None:
    """Pin (b): the hero placeholder replaced by image syntax while the
    receipt still claims ``placeholder`` — a fabricated hero claim."""
    from app.marcus.lesson_plan.workbook_producer import (
        COVER_HERO_PLACEHOLDER_MARKER,
    )

    def mutate(markdown: str) -> str:
        assert COVER_HERO_PLACEHOLDER_MARKER in markdown
        return markdown.replace(
            COVER_HERO_PLACEHOLDER_MARKER, "![Hero illustration](hero.png)", 1
        )

    trial_id, run_dir = _rig(tmp_path, mutate_md=mutate)
    _assert_bar_rejects(trial_id, run_dir)


def test_pin_c_run_id_mismatch_rejects(tmp_path: Path) -> None:
    """Pin (c): the provenance run id (rendered AND receipt, mutated in
    lockstep) mismatches ``run.json`` ``trial_id`` — only the clause's own
    source-of-truth comparison can catch it."""
    ghost = str(uuid4())
    real = json.loads(_fixture_bytes("run-8b275e5b.trimmed.run.json").decode("utf-8"))[
        "trial_id"
    ]

    def mutate_md(markdown: str) -> str:
        line = f"Production run: {real}"
        assert line in markdown
        return markdown.replace(line, f"Production run: {ghost}", 1)

    def mutate_receipt(receipt: dict) -> None:
        receipt["provenance"]["run_id"] = ghost

    trial_id, run_dir = _rig(
        tmp_path, mutate_md=mutate_md, mutate_receipt=mutate_receipt
    )
    _assert_bar_rejects(trial_id, run_dir)


def test_pin_d_wall_clock_mutated_date_rejects(tmp_path: Path) -> None:
    """Pin (d, M-3): rendered + receipt generation dates mutated away from
    the envelope ``started_at`` VALUE (a wall-clock backfill shape)."""
    wall_clock = "2026-07-16T09:00:00+00:00"

    def mutate_md(markdown: str) -> str:
        match = re.search(r"^Generated: (\S+)$", markdown, re.MULTILINE)
        assert match is not None
        return markdown.replace(match.group(0), f"Generated: {wall_clock}", 1)

    def mutate_receipt(receipt: dict) -> None:
        receipt["provenance"]["generated_at"] = wall_clock

    trial_id, run_dir = _rig(
        tmp_path, mutate_md=mutate_md, mutate_receipt=mutate_receipt
    )
    _assert_bar_rejects(trial_id, run_dir)


def test_pin_e_phantom_toc_entry_rejects(tmp_path: Path) -> None:
    """Pin (e, M-2 reverse / matrix row j): a TOC entry naming a heading no
    rendered ``## `` line matches verbatim."""

    def mutate(markdown: str) -> str:
        anchor = "**After you watch**\n"
        assert anchor in markdown
        return markdown.replace(
            anchor, anchor + "\n- Ghost tour stop — `Ghost Section`\n", 1
        )

    trial_id, run_dir = _rig(tmp_path, mutate_md=mutate)
    _assert_bar_rejects(trial_id, run_dir)


# ---------------------------------------------------------------------------
# Row i — art-brief schema/digest tripwires (AC 6(iv))
# ---------------------------------------------------------------------------


def test_row_i_art_brief_schema_version_mutation_rejects(tmp_path: Path) -> None:
    def mutate_brief(brief: dict) -> None:
        brief["schema_version"] = "workbook-cover-art-brief.v2"

    trial_id, run_dir = _rig(tmp_path, mutate_brief=mutate_brief)
    _assert_bar_rejects(trial_id, run_dir)


def test_row_i_art_brief_content_digest_mismatch_rejects(tmp_path: Path) -> None:
    def mutate_brief(brief: dict) -> None:
        brief["themes"] = ["laundered theme"]  # content changed, digest stale

    trial_id, run_dir = _rig(tmp_path, mutate_brief=mutate_brief)
    _assert_bar_rejects(trial_id, run_dir)


def test_row_i_art_brief_file_missing_rejects(tmp_path: Path) -> None:
    trial_id, run_dir = _rig(tmp_path, drop_brief=True)
    _assert_bar_rejects(trial_id, run_dir)


# ---------------------------------------------------------------------------
# Singularity + witness-presence counters
# ---------------------------------------------------------------------------


def test_duplicate_cover_section_rejects(tmp_path: Path) -> None:
    """The cover headings are counted, not first-matched (P9 idiom)."""

    def mutate(markdown: str) -> str:
        return markdown + "\n## Cover\n\n*(duplicate)*\n"

    trial_id, run_dir = _rig(tmp_path, mutate_md=mutate)
    _assert_bar_rejects(trial_id, run_dir)


def test_receipt_with_no_presentation_support_render_rejects(tmp_path: Path) -> None:
    """A cover receipt whose deliverable set carries NO presentation-support
    render has no witness for its claim — refuse (mirror of the fabricated
    claim direction; the receipt-present branch demands a covered MD)."""

    def mutate(markdown: str) -> str:
        assert runner._PRESENTATION_SUPPORT_MD_SENTINEL in markdown
        return markdown.replace(
            runner._PRESENTATION_SUPPORT_MD_SENTINEL,
            "This legacy companion workbook carries",
            1,
        )

    trial_id, run_dir = _rig(tmp_path, mutate_md=mutate)
    with pytest.raises(runner.RunnerRefusal):
        runner._assert_cover_conformant(
            run_dir, [run_dir / "exports" / "workbooks" / f"{_STEM}.md"]
        )


# ---------------------------------------------------------------------------
# A-2 — receipt-absent tolerance (clause-direct; the 37_2b/39_1/39_1b/39_2
# bar-test modules are the spine-level regression bar)
# ---------------------------------------------------------------------------


def test_a2_no_run_json_passes_unchanged(tmp_path: Path) -> None:
    markdown = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    assert runner._PRESENTATION_SUPPORT_MD_SENTINEL in markdown
    path = tmp_path / f"{_STEM}.md"
    path.write_text(markdown, encoding="utf-8")
    runner._assert_cover_conformant(tmp_path, [path])  # tolerance: no refusal


def test_a2_receipt_absent_presentation_support_md_passes_unchanged(
    tmp_path: Path,
) -> None:
    """RENDERED_WORKBOOK_FIXTURE + a run.json whose 07W refs carry NO cover
    key (the pre-40.1 persisted shape) — the clause returns without asserting
    (R3-style tolerance, A-2 BLOCKING)."""
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(
            (
                "workbook_producer",
                "07W",
                {
                    "workbook": {
                        "asset_ref": f"workbook-{_STEM}",
                        "markdown_path": f"exports/workbooks/{_STEM}.md",
                        "docx_path": f"exports/workbooks/{_STEM}.docx",
                        "lo_overlay_loss": None,
                    }
                },
                "gpt-5",
            ),
        ),
    )
    markdown = RENDERED_WORKBOOK_FIXTURE.read_text(encoding="utf-8")
    path = tmp_path / f"{_STEM}.md"
    path.write_text(markdown, encoding="utf-8")
    runner._assert_cover_conformant(tmp_path, [path])  # tolerance: no refusal
