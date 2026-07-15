"""B7 red-first floor: zero-provider-call replay safety in the activated reconcile.

The matching-completed Deep Dive reconcile (``_reconcile_activated_artifact``)
re-enters the writer to re-verify determinism. If the activated skeleton is
present but the completed journal was LOST, that re-entry would call the provider
again on replay (spending + breaking the zero-call replay guarantee). This floor
proves the reconcile fails loud with ``deep-dive-split-brain`` BEFORE any writer
re-entry, and that the provider is NOT re-called.

Reuses the live deep-dive harness from ``test_workbook_deep_dive_38_3a`` so the
scenario is the real orchestrator path, not a re-implementation.

OFFLINE ONLY: the ``DeepWriter`` harness is an in-memory stub (no network).
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.prework_artifact import (
    WorkbookBriefRuntimeContext,
    read_workbook_brief,
)
from app.marcus.lesson_plan.prework_projection import ObjectiveInput
from app.marcus.lesson_plan.promise_projection import PromiseObjectiveResolution
from app.marcus.orchestrator import workbook_wiring
from app.models.runtime.production_envelope import ProductionEnvelope
from app.specialists.dispatch_errors import SpecialistDispatchError
from tests.helpers.workbook_slide_authority import install_single_slide_authority
from tests.integration.marcus.test_workbook_deep_dive_38_3a import (
    ROOT,
    DeepWriter,
    PromiseWriter,
    SceneWriter,
    _authority,
)

DEEP_DIVE_JOURNAL = "workbook-deep-dive-call.v1.json"


def _live_context(tmp_path: Path, deep: DeepWriter) -> WorkbookBriefRuntimeContext:
    return WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=deep,
    )


def test_b7_activated_reconcile_without_journal_fails_before_provider(
    tmp_path: Path, monkeypatch
) -> None:
    """A matching-completed reconcile with the journal LOST fails split-brain.

    RED-first: without the ``_journal_exists`` guard the reconcile re-enters
    ``_compose_deep_dive`` and re-calls the provider (``deep.calls_made`` -> 2).
    The fix raises ``deep-dive-split-brain`` first and leaves the provider at 1.
    """
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Choose a move.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    deep = DeepWriter()
    context = _live_context(tmp_path, deep)

    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    # First live run: writes the activated skeleton + the completed journal.
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=initial,
        runtime_context=context,
    )
    artifact = read_workbook_brief(tmp_path)
    assert artifact.payload.deep_dive_skeleton is not None
    assert deep.calls_made == 1
    journal = tmp_path / DEEP_DIVE_JOURNAL
    assert journal.is_file()

    # Lose the journal, then drive the matching-completed reconcile replay.
    journal.unlink()

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-split-brain"
    # The provider was NOT re-called (zero-provider-call replay safety).
    assert deep.calls_made == 1


def test_b7_activated_reconcile_with_journal_still_replays_zero_call(
    tmp_path: Path, monkeypatch
) -> None:
    """Control: with the journal present the reconcile replays with zero calls.

    Guards against the guard being over-broad (it must not block the healthy
    matching-completed replay).
    """
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Choose a move.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    deep = DeepWriter()
    context = _live_context(tmp_path, deep)

    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=initial,
        runtime_context=context,
    )
    assert (tmp_path / DEEP_DIVE_JOURNAL).is_file()
    repeated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=envelope,
        runtime_context=context,
    )
    assert repeated is envelope
    assert deep.calls_made == 1
