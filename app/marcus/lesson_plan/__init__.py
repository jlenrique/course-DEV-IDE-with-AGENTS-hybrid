"""Lesson Plan schema + log + registries/ABC foundation.

Stories 31-1 (schema) + 31-2 (log write-path) + 31-3 (registries + ModalityProducer ABC).

Public surface:
    - :class:`LessonPlan`, :class:`PlanUnit`, :class:`Dials`,
      :class:`IdentifiedGap`, :class:`LearningModel`, :class:`PlanRef`.
    - :class:`ScopeDecision` with :meth:`ScopeDecision.transition_to`
      state-machine classmethod.
    - :class:`FitReport`, :class:`FitDiagnosis`.
    - :class:`EventEnvelope` + :class:`ScopeDecisionTransition` event
      primitives (log write-path lives in 31-2).
    - :func:`compute_digest`, :func:`assert_digest_matches`.
    - :mod:`event_type_registry` with the Gagne-9 labels + reserved log
      event_types.
    - **31-3 surface:** :data:`MODALITY_REGISTRY` + :class:`ModalityEntry` +
      :data:`ModalityRef` + :data:`COMPONENT_TYPE_REGISTRY` +
      :class:`ComponentTypeEntry` + :class:`ModalityProducer` ABC +
      :class:`ProductionContext` + :class:`ProducedAsset` + registry query API.

Every shape here is the reviewable contract downstream stories (31-2
log, 31-3 registries, 29-1 fit-report validator, 30-1 Marcus duality
split, 30-2b pre-packet emission, 30-3a/b 4A loop, 30-4 plan-lock
fanout, 31-5 Quinn-R gate, 32-2 envelope audit, 32-3 trial-run smoke)
read and write against.

See ``_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md``,
``_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md``, and
``_bmad-output/implementation-artifacts/31-3-registries.md`` for the
authoritative specs.
"""

from __future__ import annotations

from app.marcus.lesson_plan.component_type_registry import (
    COMPONENT_TYPE_REGISTRY,
    ComponentTypeEntry,
    get_component_type_entry,
)
from app.marcus.lesson_plan.coverage_manifest import (
    COVERAGE_MANIFEST_PATH,
    DEFAULT_COVERAGE_INVENTORY,
    CoverageInventoryEntry,
    CoverageManifest,
    CoverageManifestError,
    CoverageSummary,
    CoverageSurface,
    build_coverage_manifest,
    emit_coverage_manifest,
    render_coverage_manifest_json,
    summarize_surfaces,
    verify_assert_plan_fresh_usage,
    verify_plan_ref_fields,
)
from app.marcus.lesson_plan.coverage_manifest import (
    SCHEMA_VERSION as COVERAGE_MANIFEST_SCHEMA_VERSION,
)
from app.marcus.lesson_plan.digest import assert_digest_matches, compute_digest
from app.marcus.lesson_plan.events import (
    EventEnvelope,
    ScopeDecisionTransition,
    to_internal_actor,
)
from app.marcus.lesson_plan.fit_report import (
    FIT_REPORT_EMITTED_EVENT_TYPE,
    StaleFitReportError,
    UnknownUnitIdError,
    deserialize_fit_report,
    emit_fit_report,
    serialize_fit_report,
    validate_fit_report,
)
from app.marcus.lesson_plan.gagne_diagnostician import (
    DEFAULT_BUDGET_FALLBACK_MODE,
    DuplicateDiagnosisTargetError,
    PriorDeclinedRationale,
    UnsupportedGagneEventTypeError,
    diagnose_lesson_plan,
    diagnose_plan_unit,
)
from app.marcus.lesson_plan.log import (
    LOG_PATH,
    NAMED_MANDATORY_EVENTS,
    WRITER_EVENT_MATRIX,
    LessonPlanLog,
    LogCorruptError,
    PlanLockedPayload,
    PrePacketSnapshotPayload,
    SourceRef,
    StalePlanRefError,
    UnauthorizedWriterError,
    WriterIdentity,
    assert_plan_fresh,
)
from app.marcus.lesson_plan.modality_producer import ModalityProducer
from app.marcus.lesson_plan.modality_registry import (
    MODALITY_REGISTRY,
    ModalityEntry,
    ModalityRef,
    get_modality_entry,
    list_pending_modalities,
    list_ready_modalities,
)
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.quinn_r_gate import (
    DEFAULT_QUINN_R_GATE_OUTPUT_ROOT,
    QuinnRGateError,
    QuinnRTwoBranchResult,
    QuinnRUnitVerdict,
    emit_quinn_r_gate_artifact,
    evaluate_quinn_r_two_branch_gate,
    extract_prior_declined_rationales,
    render_quinn_r_gate_json,
)
from app.marcus.lesson_plan.schema import (
    SCHEMA_VERSION,
    Dials,
    FitDiagnosis,
    FitReport,
    IdentifiedGap,
    LearningModel,
    LessonPlan,
    PlanRef,
    PlanUnit,
    ScopeDecision,
    StaleRevisionError,
)

__all__ = [
    "COMPONENT_TYPE_REGISTRY",
    "COVERAGE_MANIFEST_PATH",
    "COVERAGE_MANIFEST_SCHEMA_VERSION",
    "DEFAULT_BUDGET_FALLBACK_MODE",
    "Dials",
    "ComponentTypeEntry",
    "CoverageInventoryEntry",
    "CoverageManifest",
    "CoverageManifestError",
    "CoverageSummary",
    "CoverageSurface",
    "DEFAULT_COVERAGE_INVENTORY",
    "DuplicateDiagnosisTargetError",
    "EventEnvelope",
    "FIT_REPORT_EMITTED_EVENT_TYPE",
    "FitDiagnosis",
    "FitReport",
    "IdentifiedGap",
    "LOG_PATH",
    "LearningModel",
    "LessonPlan",
    "LessonPlanLog",
    "LogCorruptError",
    "MODALITY_REGISTRY",
    "ModalityEntry",
    "ModalityProducer",
    "ModalityRef",
    "NAMED_MANDATORY_EVENTS",
    "PlanLockedPayload",
    "PlanRef",
    "PlanUnit",
    "PriorDeclinedRationale",
    "PrePacketSnapshotPayload",
    "ProducedAsset",
    "ProductionContext",
    "QuinnRGateError",
    "QuinnRTwoBranchResult",
    "QuinnRUnitVerdict",
    "SCHEMA_VERSION",
    "ScopeDecision",
    "ScopeDecisionTransition",
    "SourceRef",
    "StaleFitReportError",
    "StalePlanRefError",
    "StaleRevisionError",
    "UnsupportedGagneEventTypeError",
    "UnauthorizedWriterError",
    "UnknownUnitIdError",
    "WRITER_EVENT_MATRIX",
    "WriterIdentity",
    "DEFAULT_QUINN_R_GATE_OUTPUT_ROOT",
    "assert_digest_matches",
    "assert_plan_fresh",
    "build_coverage_manifest",
    "compute_digest",
    "deserialize_fit_report",
    "diagnose_lesson_plan",
    "diagnose_plan_unit",
    "emit_quinn_r_gate_artifact",
    "emit_coverage_manifest",
    "emit_fit_report",
    "evaluate_quinn_r_two_branch_gate",
    "extract_prior_declined_rationales",
    "get_component_type_entry",
    "get_modality_entry",
    "list_pending_modalities",
    "list_ready_modalities",
    "render_coverage_manifest_json",
    "render_quinn_r_gate_json",
    "serialize_fit_report",
    "summarize_surfaces",
    "to_internal_actor",
    "validate_fit_report",
    "verify_assert_plan_fresh_usage",
    "verify_plan_ref_fields",
]
