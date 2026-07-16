"""Story 40.1 — intake + receipt plumbing for the cover producer.

Covers the ``_act.py`` half: ``build_workbook_inputs`` supplies
``cover_inputs`` on the presentation_support branch ONLY (run-identity read
via the W-1 reader; cheap read-only SME probe; configured deck reference),
and ``_sidecar_refs`` carries the additive ``cover`` key so the receipt rides
the 07W ``workbook_producer`` contribution into ``run.json``.

OFFLINE ONLY: no live LLM / network. Deterministic throughout.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from app.marcus.lesson_plan.prework_artifact import read_workbook_brief
from app.specialists.workbook_producer import _act as wb_act
from app.specialists.workbook_producer._act import (
    _deck_reference,
    _sidecar_refs,
    _sme_name_from_corpus,
)
from tests.helpers.deep_dive_enrichment_37_2b import install_brief

from ._run_fixture import collateral_present, section, write_run_json

_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": (
            "Healthcare delivery is shifting toward proactive, population-focused "
            "models and clinician leadership."
        ),
    },
]
_CORPUS = (
    "Healthcare delivery shifts toward proactive, population-focused models and "
    "clinician leadership; administrative friction is a redesignable surface.\n"
    "Administrative activity consumes 25% of clinical time.\n"
)


def _make_run_dir(root: Path) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _SEGMENTS}, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "bundle" / "extracted.md").write_text(_CORPUS, encoding="utf-8")
    write_run_json(
        run_dir,
        collateral=collateral_present(
            [
                section(
                    "sec-a",
                    "lo-a",
                    title="Section A",
                    deferred_depth=(
                        "the redesignable administrative friction surface deferred "
                        "off the glance deck"
                    ),
                    narrative_intent=(
                        "The fuller systems-design narrative carried by the read "
                        "channel beyond the heard narration."
                    ),
                    exercises=[
                        {
                            "exercise_id": "ex-a1",
                            "bloom_level": "analyze",
                            "prompt_intent": "Practice intent without figures.",
                            "answer_key_source_ref": "src-ref-a1",
                        }
                    ],
                )
            ]
        ),
        plan_units=[{"unit_id": "u-cover-fixture"}],
        lesson_summary="cover intake fixture lesson",
    )
    return run_dir


# --------------------------------------------------------------------------- #
# cover_inputs: presentation_support branch only                               #
# --------------------------------------------------------------------------- #


def test_legacy_intake_supplies_no_cover_inputs(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path)
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="cover401")
    assert inputs is not None
    assert inputs.render_profile == "legacy"
    assert inputs.cover_inputs is None


def test_presentation_support_intake_supplies_cover_inputs(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path)
    install_brief(run_dir)
    brief = read_workbook_brief(run_dir)
    inputs = wb_act.build_workbook_inputs(
        run_dir, run_id="cover401", validated_brief=brief
    )
    assert inputs is not None
    assert inputs.render_profile == "presentation_support"
    cover_inputs = inputs.cover_inputs
    assert cover_inputs is not None
    # The W-1 reader ran against the REAL persisted run.json.
    identity = cover_inputs.run_identity
    assert identity is not None and identity["status"] == "ok"
    raw = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert identity["trial_id"] == raw["trial_id"]
    assert identity["corpus_path"] == raw["corpus_path"]
    # Models-used pairs collected for the RECEIPT only (J-2).
    assert {row["specialist_id"] for row in identity["models_used"]} == {"irene_pass1"}
    # Deck reference = the configured manifest relpath (no bundle metadata here).
    assert cover_inputs.deck_reference == "exports/segment-manifest-storyboard-b.yaml"
    # SME not cheaply derivable on this rig -> honest None (renders the
    # explicit "not recorded" line, never fabricated).
    assert cover_inputs.sme_name is None


# --------------------------------------------------------------------------- #
# Cheap read-only derivation helpers                                           #
# --------------------------------------------------------------------------- #


def test_sme_name_from_corpus_reads_course_yaml(tmp_path: Path) -> None:
    assert _sme_name_from_corpus(None) is None
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    assert _sme_name_from_corpus(corpus) is None  # no course.yaml -> honest None
    (corpus / "course.yaml").write_text(
        yaml.safe_dump({"sme": {"name": "Dr. Tejal Fixture"}}), encoding="utf-8"
    )
    assert _sme_name_from_corpus(corpus) == "Dr. Tejal Fixture"
    (corpus / "course.yaml").write_text("- not a mapping\n", encoding="utf-8")
    assert _sme_name_from_corpus(corpus) is None  # malformed -> None, non-raising
    (corpus / "course.yaml").write_text(":::: not yaml [", encoding="utf-8")
    assert _sme_name_from_corpus(corpus) is None


def test_deck_reference_carries_bundle_identity_when_present(tmp_path: Path) -> None:
    relpath = "exports/segment-manifest-storyboard-b.yaml"
    assert _deck_reference(tmp_path, relpath) == relpath
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "metadata.json").write_text(
        json.dumps({"directive_sha256": "948d3375c58c57ea647d03e22877941a"}),
        encoding="utf-8",
    )
    assert _deck_reference(tmp_path, relpath) == f"{relpath} (source bundle 948d3375c58c)"
    (bundle / "metadata.json").write_text("not json", encoding="utf-8")
    assert _deck_reference(tmp_path, relpath) == relpath  # non-raising degrade


# --------------------------------------------------------------------------- #
# Receipt plumbing: the additive ``cover`` key on the sidecar refs             #
# --------------------------------------------------------------------------- #


def test_sidecar_refs_carries_additive_cover_key(tmp_path: Path) -> None:
    from app.marcus.lesson_plan.workbook_producer import WorkbookProducer

    run_dir = _make_run_dir(tmp_path)
    install_brief(run_dir)
    brief = read_workbook_brief(run_dir)
    inputs = wb_act.build_workbook_inputs(
        run_dir, run_id="cover401", validated_brief=brief
    )
    assert inputs is not None
    output_root = run_dir / "exports" / "workbooks"
    producer = WorkbookProducer(output_root=output_root)
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
        reuse_sha="cover401",
        cover_inputs=inputs.cover_inputs,
    )
    refs: dict[str, Any] = _sidecar_refs(sidecar)
    assert "cover" in refs
    receipt = refs["cover"]
    assert receipt is not None and receipt["hero"] == "placeholder"
    # The receipt's provenance run id / date came from the persisted envelope
    # (never wall-clock) and the art-brief path points at the written sidecar.
    raw = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert receipt["provenance"]["run_id"] == raw["trial_id"]
    assert receipt["provenance"]["date_source"] == "run.json:started_at"
    art_brief_path = receipt["art_brief"]["path"]
    assert art_brief_path and art_brief_path.endswith(".cover-art-brief.json")
    brief_file = output_root / Path(art_brief_path).name
    payload = json.loads(brief_file.read_text(encoding="utf-8"))
    assert payload["self_digest"] == receipt["art_brief"]["digest"]
    # Every other refs key is untouched (additive-only change).
    for key in (
        "asset_ref",
        "markdown_path",
        "docx_path",
        "exercise_composition",
        "exercise_overlay_loss",
        "lo_overlay_loss",
    ):
        assert key in refs


def test_legacy_produce_emits_no_cover_receipt_and_no_art_brief(tmp_path: Path) -> None:
    from app.marcus.lesson_plan.workbook_producer import WorkbookProducer

    run_dir = _make_run_dir(tmp_path)
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="cover401")
    assert inputs is not None and inputs.render_profile == "legacy"
    output_root = run_dir / "exports" / "workbooks"
    producer = WorkbookProducer(output_root=output_root)
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
        research_supplements=inputs.research_supplements,
        lo_overlay_loss=inputs.lo_overlay_loss,
        exercise_overlay_loss=inputs.exercise_overlay_loss,
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="cover401",
        cover_inputs=inputs.cover_inputs,
    )
    assert sidecar.cover is None
    assert sidecar.art_brief_path is None
    assert _sidecar_refs(sidecar)["cover"] is None
    assert not list(output_root.glob("*.cover-art-brief.json"))
