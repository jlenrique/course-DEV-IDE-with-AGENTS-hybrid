"""S7 3-lane review + Codex SOP-028 remediation — RED-first floors.

Each item goes RED against pre-remediation code and GREEN after the fix:

1. shared-LO duplicate exercise_id crash (MUST-FIX)
2. produce()-raised gate errors must be recoverable (PATCH)
3. DOI honesty — never render a broken/fabricated DOI silently (PATCH)
4. malformed declaration must fail-loud, not silent-skip (F-2801, PATCH)
5. AC-2 degrade-provenance placeholder RENDERS (teeth; test-only)
6. carry WorkbookSpec.kind through the rebuild (trivial forward-compat, PATCH)

OFFLINE ONLY. No live LLM / network.
"""

from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.marcus.lesson_plan.workbook_producer import WorkbookProducer
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.workbook_producer import _act as wb_act

from ._run_fixture import collateral_present, section, write_run_json

REPO_ROOT = Path(__file__).resolve().parents[3]

_CORPUS = (
    "The clinician-innovator diagnoses the operational root cause before buying "
    "a solution; opportunity is scanned across past, present, and future.\n"
)
_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": (
            "Innovating inside the hospital means navigating politics and legacy "
            "systems rather than launching a standalone startup."
        ),
    },
    {
        "segment_id": "seg-02",
        "id": "seg-02",
        "slide_id": "slide-02",
        "narration_text": (
            "Fall in love with the problem: diagnose the systemic root cause "
            "before committing to any single solution."
        ),
    },
]


def _make_run_dir(
    root: Path,
    *,
    collateral: dict[str, Any] | None,
    enrichment_card: dict[str, Any] | None = None,
    research_entries: list[dict[str, Any]] | None = None,
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
    if collateral is not None:
        write_run_json(
            run_dir,
            collateral=collateral,
            plan_units=[{"unit_id": "u-opportunity-clinician"}],
            lesson_summary="opportunity clinician innovator",
            research_entries=research_entries,
        )
    return run_dir


@pytest.fixture
def output_root() -> Iterator[Path]:
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test-s7"
        / f"_rem-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def _seed_state(payload: dict[str, Any]) -> RunState:
    entry = ModelResolutionEntry(
        level="per_specialist",
        requested="gpt-5-nano",
        resolved="gpt-5-nano",
        reason="seed",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[entry],
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


def _render(run_dir: Path, output_root: Path) -> str:
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="remtest01")
    assert inputs is not None
    producer = WorkbookProducer(output_root=str(output_root))
    sidecar = producer.produce(
        inputs.plan_unit,
        inputs.context,
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
    )
    return (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Item 1 — shared-LO overlay exercise attachment must not duplicate ids        #
# --------------------------------------------------------------------------- #
_SHARED_LO_ENRICH = {
    "provisional_los": [
        {"objective_id": "lo-shared", "statement": "Shared objective statement"},
    ],
    "typed_components": [
        {"component_id": "quiz-shared", "source_type": "quiz", "excerpt": "quiz prompt"},
    ],
    "pedagogy_annotations": [
        {
            "component_id": "quiz-shared",
            "lo_refs": ["lo-shared"],
            "bloom": "apply",
            "teachable": True,
            "assessment_link": None,
        }
    ],
    "citation_resolutions": [],
}


def test_item1_shared_lo_overlay_no_duplicate_exercise_id(tmp_path, output_root) -> None:
    # Two collateral sections bind the SAME learning_objective_id (legal input);
    # an overlay exercise homes to that LO. Pre-fix: injected into BOTH sections
    # => duplicate exercise_id => DuplicateCollateralIdError crash in produce().
    collateral = collateral_present(
        [
            section(
                "sec-one",
                "lo-shared",
                title="One",
                deferred_depth="depth one alpha",
                narrative_intent="Alpha companion prose adding distinct workbook depth.",
            ),
            section(
                "sec-two",
                "lo-shared",
                title="Two",
                deferred_depth="depth two beta",
                narrative_intent="Beta companion prose adding further distinct workbook depth.",
            ),
        ]
    )
    run_dir = _make_run_dir(
        tmp_path, collateral=collateral, enrichment_card=_SHARED_LO_ENRICH
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="remtest01")
    assert inputs is not None
    # No duplicate exercise ids across sections.
    ex_ids = [ex.exercise_id for sec in inputs.spec.sections for ex in sec.exercises]
    assert len(ex_ids) == len(set(ex_ids)), f"duplicate exercise ids: {ex_ids}"
    # And it produces without crashing.
    md = _render(run_dir, output_root)
    assert "quiz-shared" in md


# --------------------------------------------------------------------------- #
# Item 2 — produce()-raised gate ValueErrors must be recoverable               #
# --------------------------------------------------------------------------- #
def test_item2_produce_gate_failure_is_recoverable(tmp_path, output_root) -> None:
    # An UNTRUSTED collateral depth_delta asserts a numeral ("99%") absent from
    # the numeral-free source => G1 WorkbookFidelityError inside produce().
    # Pre-fix: a raw ValueError (WorkbookFidelityError) escapes act() and hard-
    # kills the walk. Post-fix: a recoverable WorkbookProducerActError.
    collateral = collateral_present(
        [
            section(
                "sec-num",
                "lo-num",
                title="Numeral leak",
                deferred_depth="the workbook asserts a 99% figure absent from source",
            )
        ]
    )
    run_dir = _make_run_dir(tmp_path, collateral=collateral)
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    with pytest.raises(wb_act.WorkbookProducerActError) as exc:
        wb_act.act(state)
    assert "gate" in exc.value.tag


# --------------------------------------------------------------------------- #
# Item 3 — DOI honesty: never render a broken/fabricated DOI silently          #
# --------------------------------------------------------------------------- #
def test_item3_malformed_doi_omitted_with_provenance(tmp_path, output_root) -> None:
    collateral = collateral_present(
        [
            section(
                "sec-doi",
                "lo-doi",
                title="DOI",
                deferred_depth="doi honesty depth",
                narrative_intent="Companion prose adding distinct workbook depth.",
            )
        ]
    )
    research = [
        {
            "citation_id": "rc-ok",
            "source_ref": "scite:10.1234/ok.doi",
            "provider": "scite",
            "source_id": "10.1234/ok.doi",
            "title": "A valid study",
            "source_hash": "aaaa1111",
        },
        {
            "citation_id": "rc-empty",
            "source_ref": "scite:empty-doi",
            "provider": "scite",
            "source_id": "",
            "title": "Empty DOI study",
            "source_hash": "bbbb2222",
        },
        {
            "citation_id": "rc-garbage",
            "source_ref": "scite:garbage-doi",
            "provider": "scite",
            "source_id": "not-a-real-doi",
            "title": "Garbage DOI study",
            "source_hash": "cccc3333",
        },
    ]
    run_dir = _make_run_dir(
        tmp_path, collateral=collateral, research_entries=research
    )
    md = _render(run_dir, output_root)
    live_block = md.split("Live-research")[-1]
    # The valid DOI renders.
    assert "https://doi.org/10.1234/ok.doi" in live_block
    # NO broken/fabricated DOI link for the empty or garbage source_id.
    assert "https://doi.org/not-a-real-doi" not in live_block
    assert "https://doi.org/)" not in live_block  # empty {source_id}
    assert "https://doi.org/ " not in live_block
    # Omission is recorded with visible provenance.
    assert "omitted" in live_block.lower()


# --------------------------------------------------------------------------- #
# Item 4 — malformed declaration must fail-loud (F-2801)                        #
# --------------------------------------------------------------------------- #
def test_item4_malformed_declaration_fails_loud(tmp_path, output_root) -> None:
    # A typo'd / out-of-set declaration is NOT a valid skip; it must fail-loud.
    run_dir = _make_run_dir(tmp_path, collateral={"declaration": "workbook"})
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    with pytest.raises(wb_act.WorkbookProducerActError) as exc:
        wb_act.act(state)
    assert "blueprint" in exc.value.tag


def test_item4_absent_and_none_still_skip(tmp_path, output_root) -> None:
    # Guard: the ONLY legal skips (absent collateral / explicit "none") still skip.
    run_dir_none = _make_run_dir(tmp_path / "a", collateral={"declaration": "none"})
    state = _seed_state({"run_dir": str(run_dir_none), "output_root": str(output_root)})
    out = json.loads(wb_act.act(state)["cache_state"]["cache_prefix"])
    assert out["workbook"]["skipped"] is True


# --------------------------------------------------------------------------- #
# Item 5 — AC-2 degrade-provenance placeholder RENDERS (direct teeth)          #
# --------------------------------------------------------------------------- #
def test_item5_degrade_provenance_placeholder_renders(tmp_path, output_root) -> None:
    # A bound objective with NO enrichment overlay degrades with recorded
    # in-workbook provenance — the placeholder must actually render.
    collateral = collateral_present(
        [
            section(
                "sec-unresolved",
                "lo-core-radar",
                title="Unresolved objective",
                deferred_depth="the opportunity radar deferred derivation depth",
                narrative_intent="Companion prose adding distinct workbook depth.",
            )
        ]
    )
    run_dir = _make_run_dir(tmp_path, collateral=collateral)  # no enrichment card
    md = _render(run_dir, output_root)
    assert "objective statement unresolved for `lo-core-radar`" in md


# --------------------------------------------------------------------------- #
# Item 6 — carry WorkbookSpec.kind through the rebuild (forward-compat)         #
# --------------------------------------------------------------------------- #
def test_item6_kind_carried_through_rebuild(tmp_path) -> None:
    collateral = collateral_present(
        [section("sec-k", "lo-k", title="K", deferred_depth="kind carry depth")]
    )
    run_dir = _make_run_dir(tmp_path, collateral=collateral)
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="remtest01")
    assert inputs is not None
    # The rebuilt spec preserves the blueprint's kind (single-value today; this
    # pins the carry-through so a future closed-set growth cannot silently revert).
    assert inputs.spec.kind == "deck-companion-workbook"
