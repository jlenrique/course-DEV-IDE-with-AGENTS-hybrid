"""Fit-report-v1 validator + serializer + emission wiring (Story 29-1).

Discipline notes:

* **Canonical caller of** :func:`emit_fit_report` **is Marcus-Orchestrator.**
  Irene produces :class:`FitReport` instances (29-2's scope) and hands them
  to Marcus via the existing orchestration seam; Irene MUST NOT import or
  call :func:`emit_fit_report` directly. Calling from any non-Marcus code
  path is a contract violation that the 31-2 single-writer enforcement
  will catch, but should never reach. AC-B.5.1 + AC-T.11 pin this.
* :class:`FitReport`, :class:`FitDiagnosis`, :class:`PlanRef` shapes are
  pinned in 31-1 :mod:`marcus.lesson_plan.schema`. This module re-exports
  them; it does NOT re-define.
* :func:`serialize_fit_report` produces canonical-JSON per AC-B.3:
  ``json.dumps(model_dump(mode="json"), sort_keys=True, ensure_ascii=True,
  separators=(",", ":"))``. The ``sort_keys`` / ``ensure_ascii`` /
  ``separators`` kwargs match :func:`marcus.lesson_plan.digest.compute_digest`.
  This serializer does NOT claim byte-identity with ``compute_digest``
  output on the same semantic content — ``compute_digest`` additionally
  strips ``None``-valued fields before serializing (``_strip_none`` step).
  If a downstream consumer needs a hash comparable to
  :attr:`LessonPlan.digest`, they should call ``compute_digest`` directly
  rather than hashing this serializer's output.
* Single-writer enforcement is owned by 31-2's
  :meth:`LessonPlanLog.append_event`. This module adds NO redundant check
  (defensive-coding-in-internal-code anti-pattern). The 31-2
  :class:`UnauthorizedWriterError` bubbles up unchanged.
* Staleness check (:class:`StaleFitReportError`) MUST run BEFORE unit_id
  check (:class:`UnknownUnitIdError`) — staleness is the root cause when
  plan structure changed across revisions. AC-B.2.1 precedence.
* Envelope ``plan_revision`` == payload ``plan_ref.lesson_plan_revision``
  is LOAD-BEARING tamper detection across the envelope/payload boundary.
  Do NOT DRY this duplication. AC-B.5.2 + AC-T.12 pin this.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from app.marcus.lesson_plan.event_type_registry import EVENT_FIT_REPORT_EMITTED
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog, WriterIdentity
from app.marcus.lesson_plan.schema import (
    FitDiagnosis,
    FitReport,
    LessonPlan,
    PlanRef,
)

logger = logging.getLogger(__name__)

__all__ = [
    "FIT_REPORT_EMITTED_EVENT_TYPE",
    "FitDiagnosis",
    "FitReport",
    "PlanRef",
    "StaleFitReportError",
    "UnknownUnitIdError",
    "deserialize_fit_report",
    "emit_fit_report",
    "serialize_fit_report",
    "validate_fit_report",
]


FIT_REPORT_EMITTED_EVENT_TYPE: str = EVENT_FIT_REPORT_EMITTED
"""Event-type string registered for fit-report emissions (AC-B.5 + AC-B.5.4).

Single source of truth: re-exported from
:data:`marcus.lesson_plan.event_type_registry.EVENT_FIT_REPORT_EMITTED`
(party-mode 2026-04-19 follow-on consolidation, mirrors the
``PRE_PACKET_SNAPSHOT_EVENT_TYPE`` / ``EVENT_PRE_PACKET_SNAPSHOT`` chain).
Registered in :data:`marcus.lesson_plan.event_type_registry.RESERVED_LOG_EVENT_TYPES`
and :data:`marcus.lesson_plan.log.WRITER_EVENT_MATRIX` (marcus-orchestrator
only). Naming grammar: ``<domain_noun>.<past_tense_verb>``.
"""


class StaleFitReportError(ValueError):
    """Raised when ``fit_report.plan_ref`` does not match the live
    :class:`LessonPlan` (AC-B.2 + AC-B.2.1).

    Inherits :class:`ValueError` so callers can catch the broad contract
    while still distinguishing the specific domain failure. Error message
    names both sides of the mismatch.

    Precedence (AC-B.2.1): staleness precedes unit_id existence check.
    """


class UnknownUnitIdError(ValueError):
    """Raised when any ``diagnoses[*].unit_id`` is absent from the referenced
    plan's ``plan_units`` (AC-B.2).

    Raised ONLY when the ``plan_ref`` is fresh (AC-B.2.1 precedence).
    """


# Canonical-JSON kwargs lifted verbatim from
# :func:`marcus.lesson_plan.digest.compute_digest` — do NOT modify without
# a coordinated change to digest.py, since the digest of a FitReport
# embedded in a LessonPlan must match a digest computed from the serialized
# form.
_CANONICAL_JSON_KWARGS: dict = {
    "sort_keys": True,
    "ensure_ascii": True,
    "separators": (",", ":"),
}


def validate_fit_report(
    report: FitReport | dict | str,
    *,
    plan: LessonPlan,
) -> FitReport:
    """Validate a fit-report against a live :class:`LessonPlan` (AC-B.2).

    Accepts an already-constructed :class:`FitReport` instance, a plain
    ``dict``, or a JSON ``str``. Normalizes to a :class:`FitReport` via
    ``model_validate`` / ``model_validate_json`` when needed. Does NOT
    re-parse an already-constructed :class:`FitReport` instance
    (AC-B.2.2 idempotency pin — pinned by AC-T.10).

    Cross-model checks run in precedence order (AC-B.2.1):

    1. ``plan_ref.lesson_plan_revision == plan.revision`` AND
       ``plan_ref.lesson_plan_digest == plan.digest`` — mismatch raises
       :class:`StaleFitReportError` IMMEDIATELY; unit_id check is skipped
       when plan_ref is stale.
    2. Every ``diagnoses[*].unit_id`` is in
       ``{pu.unit_id for pu in plan.plan_units}`` — unknown unit_ids raise
       :class:`UnknownUnitIdError`.

    Raises:
        StaleFitReportError: ``plan_ref`` is stale (AC-B.2.1 precedence).
        UnknownUnitIdError: unit_id not on plan (only if plan_ref fresh).
        pydantic.ValidationError: Pydantic shape violation; re-raised as-is,
            never swallowed or rewrapped (29-2 callers depend on the
            standard surface).
        TypeError: ``report`` is not one of the three supported input types.
    """
    # AC-B.2.2 idempotency pin: if already a FitReport instance, do NOT
    # re-parse. Cross-model checks operate on the passed attributes directly.
    if isinstance(report, FitReport):
        normalized = report
    elif isinstance(report, dict):
        normalized = FitReport.model_validate(report)
    elif isinstance(report, str):
        normalized = FitReport.model_validate_json(report)
    else:
        raise TypeError(
            f"validate_fit_report expects FitReport, dict, or str; "
            f"got {type(report).__name__}"
        )

    # AC-B.2.1 precedence: staleness check before unit_id check.
    if (
        normalized.plan_ref.lesson_plan_revision != plan.revision
        or normalized.plan_ref.lesson_plan_digest != plan.digest
    ):
        raise StaleFitReportError(
            f"fit_report.plan_ref is stale: report carries "
            f"lesson_plan_revision={normalized.plan_ref.lesson_plan_revision} "
            f"lesson_plan_digest={normalized.plan_ref.lesson_plan_digest!r}; "
            f"live plan has "
            f"revision={plan.revision} digest={plan.digest!r}"
        )

    plan_unit_ids = {pu.unit_id for pu in plan.plan_units}
    diagnosis_ids = {d.unit_id for d in normalized.diagnoses}
    unknown_ids = diagnosis_ids - plan_unit_ids
    if unknown_ids:
        # Party-mode 2026-04-19 follow-on (29-1 #4-leak): emit only the unknown
        # unit_ids + a count of total plan units. Avoids leaking the full sorted
        # plan-unit identifier list (potentially sensitive in non-Gagne future
        # learning-model plans) into error messages and downstream logs.
        raise UnknownUnitIdError(
            f"fit_report contains diagnoses for unit_ids not in plan: "
            f"{sorted(unknown_ids)} ({len(plan_unit_ids)} unit_ids in plan)"
        )

    return normalized


def serialize_fit_report(report: FitReport) -> str:
    """Canonical-JSON serialize a :class:`FitReport` (AC-B.3).

    Produces byte-deterministic output: semantically-identical
    :class:`FitReport` instances ALWAYS produce byte-identical bytes.

    The ``sort_keys`` / ``ensure_ascii`` / ``separators`` kwargs match
    :func:`marcus.lesson_plan.digest.compute_digest`. Note: ``compute_digest``
    additionally strips ``None``-valued fields before serializing, so
    hashing this serializer's output does NOT yield a value comparable to
    :attr:`LessonPlan.digest` — see the module docstring for the rationale.

    The ``mode="json"`` argument is mandatory so ``datetime`` fields
    serialize to ISO-8601 UTC strings (not Python :class:`datetime`
    objects); without it, ``json.dumps`` would pick a non-canonical ISO
    format.
    """
    dumped = report.model_dump(mode="json")
    return json.dumps(dumped, **_CANONICAL_JSON_KWARGS)


def deserialize_fit_report(s: str) -> FitReport:
    """Inverse of :func:`serialize_fit_report` (AC-B.4).

    For any ``s`` produced by :func:`serialize_fit_report`,
    ``serialize_fit_report(deserialize_fit_report(s)) == s`` byte-identical.
    For non-canonical inputs (pretty-printed JSON, differently-ordered
    keys), deserialization succeeds if the JSON parses and the shape
    conforms, but round-trip byte-identity is NOT guaranteed.
    """
    return FitReport.model_validate_json(s)


def emit_fit_report(
    report: FitReport,
    *,
    writer: WriterIdentity,
    plan: LessonPlan,
    log: LessonPlanLog | None = None,
) -> None:
    """Append a ``fit_report.emitted`` event to the Lesson Plan log (AC-B.5).

    **Canonical caller: Marcus-Orchestrator.** Irene produces
    :class:`FitReport` instances and hands them off via the orchestration
    seam. Calling this function from any non-Marcus code path — including
    direct invocation by Irene, Tracy, or any specialist — is a contract
    violation that the 31-2 single-writer enforcement will catch, but
    should never reach. AC-T.11 grep-walks the tree to pin this at test
    time.

    Validation pipeline:

    1. :func:`validate_fit_report(report, plan=plan)` — raises
       :class:`StaleFitReportError` or :class:`UnknownUnitIdError` on
       cross-model drift; Pydantic :class:`ValidationError` on shape
       violation. Emission does NOT proceed past this step (AC-T.9).
    2. Construct :class:`EventEnvelope` with fresh ``event_id=uuid4``
       (auto-generated by default_factory), ``timestamp=now(tz=UTC)``,
       ``plan_revision=report.plan_ref.lesson_plan_revision``
       (LOAD-BEARING redundancy with payload — AC-B.5.2 tamper detection;
       AC-T.12 pins),
       ``event_type=FIT_REPORT_EMITTED_EVENT_TYPE``,
       ``payload=json.loads(serialize_fit_report(validated))`` (canonical
       payload parsed back to dict for the envelope payload field).
    3. ``log.append_event(envelope, writer)`` — 31-2 enforces
       ``writer == "marcus-orchestrator"`` and raises
       :class:`UnauthorizedWriterError` otherwise. 29-1 adds NO redundant
       check here.

    Args:
        report: The validated or validate-able fit report.
        writer: The caller's :data:`WriterIdentity`. 31-2 rejects anything
            other than ``"marcus-orchestrator"`` for this event_type. A
            typo (e.g. ``"marcus_orchestrator"`` with underscore) is
            rejected at step 3 with :class:`ValueError`, not
            :class:`UnauthorizedWriterError` (G6 SF-EC-3 on 31-2).
        plan: The live :class:`LessonPlan` snapshot to validate against.
        log: Optional :class:`LessonPlanLog` instance; defaults to the
            process-wide production log (``LessonPlanLog()``). Tests MUST
            pass a :class:`LessonPlanLog(path=tmp_path / ...)` to isolate.
            When ``None``, a :class:`logging.WARNING` is emitted to
            surface test-leakage into the production log in CI output.

    Raises:
        StaleFitReportError: surfaced by step 1 when plan_ref is stale.
        UnknownUnitIdError: surfaced by step 1 when a diagnosis names a
            unit_id absent from the plan.
        pydantic.ValidationError: surfaced by step 1 on FitReport shape
            violation (never swallowed, never rewrapped).
        TypeError: surfaced by step 1 when ``report`` is not
            :class:`FitReport` / ``dict`` / ``str``.
        ValueError: surfaced by step 3 when ``writer`` is not a
            recognized :data:`WriterIdentity` value (typo guard).
        UnauthorizedWriterError: surfaced by step 3 when a recognized
            writer is not permitted to write this event_type.
    """
    # Step 1: validate + normalize. Raises on drift; emission does NOT proceed.
    validated = validate_fit_report(report, plan=plan)

    # Step 2: build envelope.
    # AC-B.5.2 LOAD-BEARING: envelope.plan_revision MUST equal
    # payload.plan_ref.lesson_plan_revision. This duplication is tamper
    # detection across the envelope/payload boundary. Do NOT DRY.
    envelope = EventEnvelope(
        timestamp=datetime.now(tz=UTC),
        plan_revision=validated.plan_ref.lesson_plan_revision,
        event_type=FIT_REPORT_EMITTED_EVENT_TYPE,
        payload=json.loads(serialize_fit_report(validated)),
    )

    # Step 3: route through 31-2 single-writer log. NO redundant check here.
    if log is None:
        # Surface test-leakage into the production log via CI output. Tests
        # SHOULD always pass log=LessonPlanLog(path=tmp_path/...) per the
        # `log` parameter docs; this warning catches accidental omissions
        # before they contaminate state/runtime/lesson_plan_log.jsonl.
        logger.warning(
            "emit_fit_report called with log=None; falling back to default "
            "LessonPlanLog() which resolves to the process-wide production "
            "LOG_PATH. Tests MUST pass log=LessonPlanLog(path=tmp_path/...) "
            "to avoid polluting the runtime log."
        )
        target_log = LessonPlanLog()
    else:
        target_log = log
    target_log.append_event(envelope, writer)
