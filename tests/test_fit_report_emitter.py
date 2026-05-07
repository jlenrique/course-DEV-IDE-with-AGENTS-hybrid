"""Tests for fit_report.emit_fit_report (Story 29-1, AC-T.7/9/12 + AC-C.1/2)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.marcus.lesson_plan.digest import compute_digest
from app.marcus.lesson_plan.event_type_registry import (
    REGISTERED_EVENT_TYPES,
    RESERVED_LOG_EVENT_TYPES,
)
from app.marcus.lesson_plan.fit_report import (
    FIT_REPORT_EMITTED_EVENT_TYPE,
    StaleFitReportError,
    deserialize_fit_report,
    emit_fit_report,
    serialize_fit_report,
)
from app.marcus.lesson_plan.log import (
    WRITER_EVENT_MATRIX,
    LessonPlanLog,
    UnauthorizedWriterError,
)
from app.marcus.lesson_plan.schema import (
    Dials,
    FitDiagnosis,
    FitReport,
    LearningModel,
    LessonPlan,
    PlanRef,
    PlanUnit,
    ScopeDecision,
)


def _make_plan() -> LessonPlan:
    unit = PlanUnit(
        unit_id="gagne-event-1",
        event_type="gagne-event-1",
        source_fitness_diagnosis="placeholder",
        scope_decision=ScopeDecision(
            state="proposed",
            scope="in-scope",
            proposed_by="system",
            _internal_proposed_by="marcus",
        ),
        weather_band="gold",
        modality_ref=None,
        rationale="",
        gaps=[],
        dials=Dials(enrichment=0.0, corroboration=0.0),
    )
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        structure={},
        plan_units=[unit],
        revision=1,
        updated_at=datetime(2026, 4, 18, tzinfo=UTC),
        digest="",
    )
    return plan.model_copy(update={"digest": compute_digest(plan)})


def _make_report(plan: LessonPlan) -> FitReport:
    return FitReport(
        source_ref="tests/fixtures/trial_corpus/canonical.md",
        plan_ref=PlanRef(
            lesson_plan_revision=plan.revision,
            lesson_plan_digest=plan.digest,
        ),
        diagnoses=[
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="ok",
            ),
        ],
        generated_at=datetime(2026, 4, 18, 12, 0, 0, tzinfo=UTC),
        irene_budget_ms=1234,
    )


def _isolated_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")


# ---------------------------------------------------------------------------
# AC-T.7 — single-writer enforcement via 31-2
# ---------------------------------------------------------------------------


def test_emit_fit_report_rejects_non_orchestrator_writer(
    tmp_path: Path,
) -> None:
    """AC-T.7 — non-orchestrator writer raises 31-2 UnauthorizedWriterError.

    29-1 adds NO redundant check; the 31-2 error bubbles up unchanged.
    """
    plan = _make_plan()
    report = _make_report(plan)
    log = _isolated_log(tmp_path)

    with pytest.raises(UnauthorizedWriterError) as exc_info:
        emit_fit_report(
            report,
            writer="marcus-intake",
            plan=plan,
            log=log,
        )

    assert "marcus-intake" in str(exc_info.value)
    assert FIT_REPORT_EMITTED_EVENT_TYPE in str(exc_info.value)
    # Confirm nothing was written.
    assert list(log.read_events()) == []


# ---------------------------------------------------------------------------
# AC-T.9 — emit-ordering negative test (M-4 rider; single-gate compensator)
# ---------------------------------------------------------------------------


def test_emit_fit_report_does_not_write_on_validation_failure(
    tmp_path: Path,
) -> None:
    """AC-T.9 — validation failure → append_event call count is zero.

    Pins the AC-B.5 "validate FIRST" ordering invariant at runtime. This
    is the single-gate-story compensator for skipping G5 party-mode
    implementation review; it pins the seam contract that a runtime
    reviewer would otherwise catch by inspection.
    """
    plan = _make_plan()
    # Build a stale-plan_ref report by bumping the revision past the plan's.
    stale_report = FitReport(
        source_ref="tests/fixtures/x.md",
        plan_ref=PlanRef(
            lesson_plan_revision=plan.revision + 99,
            lesson_plan_digest="d" * 64,
        ),
        diagnoses=[],
        generated_at=datetime(2026, 4, 18, tzinfo=UTC),
        irene_budget_ms=0,
    )

    log = _isolated_log(tmp_path)
    mock_append = MagicMock()
    # Substitute the log's append_event with a tracking mock.
    log.append_event = mock_append  # type: ignore[method-assign]

    with pytest.raises(StaleFitReportError):
        emit_fit_report(
            stale_report,
            writer="marcus-orchestrator",
            plan=plan,
            log=log,
        )

    assert mock_append.call_count == 0


# ---------------------------------------------------------------------------
# AC-T.12 — envelope/payload plan_revision tamper detection (Q-4 rider)
# ---------------------------------------------------------------------------


def test_envelope_payload_plan_revision_consistency(tmp_path: Path) -> None:
    """AC-T.12 — envelope.plan_revision == payload.plan_ref.lesson_plan_revision.

    Per AC-B.5.2 the redundancy is load-bearing tamper detection across the
    envelope/payload boundary. This test pins the invariant after emit and
    confirms equality-based read-back can detect drift if introduced.
    """
    plan = _make_plan()
    report = _make_report(plan)
    log = _isolated_log(tmp_path)

    emit_fit_report(
        report,
        writer="marcus-orchestrator",
        plan=plan,
        log=log,
    )

    events = list(log.read_events(event_types={FIT_REPORT_EMITTED_EVENT_TYPE}))
    assert len(events) == 1
    envelope = events[0]
    envelope_revision = envelope.plan_revision
    payload_revision = envelope.payload["plan_ref"]["lesson_plan_revision"]
    assert envelope_revision == payload_revision == plan.revision

    # Simulate tamper: mutate the payload revision and confirm drift is
    # trivially detectable by the same equality assertion.
    tampered_payload = dict(envelope.payload)
    tampered_payload["plan_ref"] = dict(tampered_payload["plan_ref"])
    tampered_payload["plan_ref"]["lesson_plan_revision"] = payload_revision + 1
    assert envelope_revision != tampered_payload["plan_ref"]["lesson_plan_revision"]


# ---------------------------------------------------------------------------
# AC-C.1 — emission log-replay + datetime round-trip + payload canonicalization
# ---------------------------------------------------------------------------


def test_emit_fit_report_roundtrip_via_log(tmp_path: Path) -> None:
    """AC-C.1 — emit → read_events → deserialize round-trip identity.

    M-2 + M-3 riders:
    - Canonical-payload equality compared on payload bytes (excluding the
      envelope-level non-deterministic event_id + timestamp).
    - Datetime round-trip asserts tzinfo is preserved and values equal.
    """
    plan = _make_plan()
    report = _make_report(plan)
    canonical_bytes = serialize_fit_report(report)
    log = _isolated_log(tmp_path)

    emit_fit_report(
        report,
        writer="marcus-orchestrator",
        plan=plan,
        log=log,
    )

    events = list(log.read_events(event_types={FIT_REPORT_EMITTED_EVENT_TYPE}))
    assert len(events) == 1
    envelope = events[0]

    # (a) Canonical payload bytes equality — M-3 excludes envelope-level
    # event_id + timestamp (those are outside the canonical-payload domain).
    replayed_payload_bytes = json.dumps(
        envelope.payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    assert replayed_payload_bytes == canonical_bytes

    # (b) Datetime round-trip — tzinfo preserved, equality holds.
    replayed = deserialize_fit_report(replayed_payload_bytes)
    assert replayed.generated_at.tzinfo is not None
    assert replayed.generated_at == report.generated_at

    # (c) All other FitReport fields equal the originals.
    assert replayed.schema_version == report.schema_version
    assert replayed.source_ref == report.source_ref
    assert replayed.plan_ref == report.plan_ref
    assert replayed.diagnoses == report.diagnoses
    assert replayed.irene_budget_ms == report.irene_budget_ms


# ---------------------------------------------------------------------------
# AC-C.2 — event-type registration + grammar comment (W-1 rider)
# ---------------------------------------------------------------------------


def test_fit_report_emitted_event_type_registered() -> None:
    """AC-C.2 — "fit_report.emitted" appears in the registry.

    Also verifies it's in WRITER_EVENT_MATRIX with marcus-orchestrator
    permission and that the event_type_registry file carries the taxonomy
    grammar comment (W-1 rider).
    """
    assert FIT_REPORT_EMITTED_EVENT_TYPE in RESERVED_LOG_EVENT_TYPES
    assert FIT_REPORT_EMITTED_EVENT_TYPE in REGISTERED_EVENT_TYPES
    assert FIT_REPORT_EMITTED_EVENT_TYPE in WRITER_EVENT_MATRIX
    assert WRITER_EVENT_MATRIX[FIT_REPORT_EMITTED_EVENT_TYPE] == frozenset(
        {"marcus-orchestrator"}
    )

    registry_text = (
        Path(__file__).resolve().parents[1]
        / "marcus"
        / "lesson_plan"
        / "event_type_registry.py"
    ).read_text(encoding="utf-8")
    assert "<domain_noun>.<past_tense_verb>" in registry_text
