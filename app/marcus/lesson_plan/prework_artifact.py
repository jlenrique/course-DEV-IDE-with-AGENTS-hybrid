"""Versioned, digest-bound handoff between workbook authoring and rendering."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonResult,
    DeepDiveWriterCandidate,
    compose_deep_dive_skeleton,
    offline_deep_dive_writer,
)
from app.marcus.lesson_plan.lesson_type_classifier import LessonTypeClassification
from app.marcus.lesson_plan.prework_projection import (
    PreWorkBrief,
    PromiseProjection,
    PromiseTransformRequest,
    SceneBrief,
    SceneComposeRequest,
)
from app.marcus.lesson_plan.promise_projection import PromiseGateReceipt
from app.marcus.lesson_plan.scene_extraction import SceneGateReceipt

WORKBOOK_BRIEF_FILENAME = "workbook-brief.v1.json"
WORKBOOK_RUNTIME_CONTEXT_FILENAME = "workbook-runtime-context.v1.json"
DEEP_DIVE_JOURNAL_FILENAME = "workbook-deep-dive-call.v1.json"
WORKBOOK_BRIEF_NODE_ID = "07W.1"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)


class WriterExecutionEvidence(_Strict):
    scene_calls: int = 0
    promise_calls: int = 0
    model_config_digest: str | None = None
    request_ids: tuple[str, ...] = ()


class WriterExecutionReceipt(_Strict):
    writer: Literal["scene", "promise"]
    mode: Literal["offline_stub", "live"]
    calls: Literal[0, 1]
    model: str | None = None
    model_config_digest: str | None = None
    request_id: str | None = None
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    cost_unavailable_reason: str | None = None

    @model_validator(mode="after")
    def _cost_posture(self) -> WriterExecutionReceipt:
        if self.cost_usd is not None and self.cost_unavailable_reason is not None:
            raise ValueError("cost receipt cannot carry both cost and unavailable reason")
        if (
            self.mode == "live"
            and self.calls == 1
            and self.cost_usd is None
            and not self.cost_unavailable_reason
        ):
            raise ValueError("live writer call without cost requires an explicit reason")
        return self


class DeepDiveExecutionReceiptV1(_Strict):
    schema_version: Literal["deep-dive-execution-receipt.v1"] = (
        "deep-dive-execution-receipt.v1"
    )
    writer: Literal["deep_dive"] = "deep_dive"
    mode: Literal["offline_stub", "live"]
    calls: Literal[0, 1]
    idempotency_key: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    prior_payload_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    slide_authority_map_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    model: str | None = None
    model_config_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    request_id: str | None = None
    latency_ms: float | None = Field(default=None, ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
    cost_unavailable_reason: str | None = None
    fallback_engaged: bool = False
    fallback_reason: str | None = None

    @model_validator(mode="after")
    def _cost_posture(self) -> DeepDiveExecutionReceiptV1:
        if self.cost_usd is not None and self.cost_unavailable_reason is not None:
            raise ValueError("cost receipt cannot carry both cost and unavailable reason")
        if (
            self.mode == "live"
            and self.calls == 1
            and self.cost_usd is None
            and not self.cost_unavailable_reason
        ):
            raise ValueError("live writer call without cost requires an explicit reason")
        return self

    @model_validator(mode="after")
    def _fallback_posture(self) -> DeepDiveExecutionReceiptV1:
        # The deterministic safe-construction fallback must never be silent:
        # when it engaged, the receipt carries an explicit reason; when it did
        # not, no reason may masquerade as one. This makes the fallback flag the
        # authoritative provenance signal that reconciles the calls=1/token-cost
        # evidence against the synthetic (fallback-authored) raw payload.
        if self.fallback_engaged and not self.fallback_reason:
            raise ValueError("engaged Deep Dive fallback requires an explicit reason")
        if not self.fallback_engaged and self.fallback_reason is not None:
            raise ValueError("Deep Dive fallback reason requires fallback_engaged")
        return self


def deep_dive_idempotency_key(
    *, trial_id: object, authority_digest: str, model_config_digest: str
) -> str:
    payload = {
        "trial_id": str(trial_id),
        "node_id": WORKBOOK_BRIEF_NODE_ID,
        "authority_digest": authority_digest,
        "model_config_digest": model_config_digest,
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SceneAuthoringReceipt(_Strict):
    classification: LessonTypeClassification
    gate: SceneGateReceipt
    extraction_losses: tuple[str, ...] = ()
    operator_warnings: tuple[str, ...] = ()
    introduced_terms: tuple[str, ...] = ()


class PromiseAuthoringReceipt(_Strict):
    gate: PromiseGateReceipt
    authority_refs: tuple[str, ...] = ()
    operator_warnings: tuple[str, ...] = ()


class WorkbookBriefRuntimeContext(_Strict):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )
    run_dir: Path
    course_source_root: Path | None
    encounter_mode: Literal["recorded", "live"]
    context_origin: Literal["new_start", "operator_migrated", "legacy_default"]
    writer_execution_mode: Literal["offline_stub", "live"]
    writer_evidence: WriterExecutionEvidence = WriterExecutionEvidence()
    scene_writer: Callable[[SceneComposeRequest], SceneBrief] | None = Field(
        default=None, exclude=True
    )
    promise_writer: Callable[[PromiseTransformRequest], PromiseProjection] | None = Field(
        default=None, exclude=True
    )
    deep_dive_writer: Callable[[DeepDiveSkeletonRequest], DeepDiveWriterCandidate] | None = Field(
        default=None, exclude=True
    )

    @model_validator(mode="after")
    def _valid_origin(self) -> WorkbookBriefRuntimeContext:
        if self.context_origin != "legacy_default" and self.course_source_root is None:
            raise ValueError("new_start/operator_migrated context requires course_source_root")
        if not self.run_dir.is_dir():
            raise ValueError("run_dir must be an existing directory")
        if self.course_source_root is not None and not self.course_source_root.is_dir():
            raise ValueError("course_source_root must be an existing directory")
        return self

    def persisted(self) -> dict[str, object]:
        return {
            "schema_version": "workbook-runtime-context.v1",
            "course_source_root": str(self.course_source_root.resolve())
            if self.course_source_root
            else None,
            "encounter_mode": self.encounter_mode,
            "context_origin": self.context_origin,
            "writer_execution_mode": self.writer_execution_mode,
        }


class WorkbookBriefPayloadV1(_Strict):
    schema_version: Literal["workbook-brief.v1"] = "workbook-brief.v1"
    node_id: Literal["07W.1"] = "07W.1"
    specialist_id: Literal["workbook_brief"] = "workbook_brief"
    pre_work: PreWorkBrief
    selected_seed_id: str | None
    selected_seed_ref: str | None
    lesson_type: Literal["fresh_pain", "bridge_identity", "skill_build"] | None
    archetype: Literal["external_friction", "introspective_threshold", "difficulty_practice"] | None
    promise_authority_refs: tuple[str, ...]
    encounter_mode: Literal["recorded", "live"]
    writer_execution_mode: Literal["offline_stub", "live"]
    scene_receipt: SceneAuthoringReceipt
    promise_receipt: PromiseAuthoringReceipt
    writer_receipts: tuple[WriterExecutionReceipt, WriterExecutionReceipt]
    warnings: tuple[str, ...] = ()
    known_losses: tuple[str, ...] = ()
    deep_dive_skeleton: DeepDiveSkeletonResult | None = None
    deep_dive_writer_receipt: DeepDiveExecutionReceiptV1 | None = None

    @model_validator(mode="after")
    def _reconcile(self) -> WorkbookBriefPayloadV1:
        expected = self.pre_work.provenance.known_losses
        if self.known_losses != expected:
            raise ValueError("aggregate known_losses must equal pre-work losses")
        if self.pre_work.scene.status == "authored" and self.selected_seed_ref is None:
            raise ValueError("authored Scene requires selected seed provenance")
        if self.scene_receipt.gate.failures != self.pre_work.scene.known_losses:
            raise ValueError("Scene gate failures must reconcile with Scene losses")
        if self.promise_receipt.gate.failures != self.pre_work.promise.known_losses:
            raise ValueError("Promise gate failures must reconcile with Promise losses")
        if self.promise_receipt.authority_refs != self.promise_authority_refs:
            raise ValueError("Promise authority refs must reconcile")
        if tuple(receipt.writer for receipt in self.writer_receipts) != (
            "scene",
            "promise",
        ):
            raise ValueError("writer receipts must be Scene then Promise")
        if any(receipt.mode != self.writer_execution_mode for receipt in self.writer_receipts):
            raise ValueError("writer receipt modes must equal aggregate execution mode")
        if self.pre_work.scene.status == "authored" and self.writer_receipts[0].calls != 1:
            raise ValueError("authored Scene requires one writer call")
        if self.pre_work.promise.status == "authored" and self.writer_receipts[1].calls != 1:
            raise ValueError("authored Promise requires one writer call")
        if (self.deep_dive_skeleton is None) != (self.deep_dive_writer_receipt is None):
            raise ValueError("Deep Dive skeleton and execution receipt must appear together")
        if self.deep_dive_skeleton is not None:
            assert self.deep_dive_writer_receipt is not None
            if self.deep_dive_writer_receipt.mode != self.writer_execution_mode:
                raise ValueError(
                    "Deep Dive receipt mode must equal aggregate execution mode"
                )
            expected_calls = 0 if self.writer_execution_mode == "offline_stub" else 1
            if self.deep_dive_writer_receipt.calls != expected_calls:
                raise ValueError(
                    "Deep Dive receipt calls must match aggregate execution mode"
                )
            DeepDiveSkeletonResult.model_validate(self.deep_dive_skeleton.model_dump())
            if (
                self.deep_dive_writer_receipt.slide_authority_map_digest
                != self.deep_dive_skeleton.authority.slide_authority_map_digest
            ):
                raise ValueError(
                    "Deep Dive receipt map digest must equal request authority"
                )
            if (
                self.writer_execution_mode == "offline_stub"
                and compose_deep_dive_skeleton(
                    self.deep_dive_skeleton.authority, offline_deep_dive_writer
                )
                != self.deep_dive_skeleton
            ):
                raise ValueError("offline Deep Dive skeleton must equal stub replay")
            expected = tuple(
                (vow.objective_id, vow.text) for vow in self.pre_work.promise.vows
            )
            actual = tuple(
                (item.ability_id, item.text)
                for item in self.deep_dive_skeleton.authority.abilities
            )
            if actual != expected:
                raise ValueError("Deep Dive abilities must equal authored Promise vows")
        return self


class WorkbookBriefArtifactV1(_Strict):
    payload: WorkbookBriefPayloadV1
    payload_digest: str

    @model_validator(mode="after")
    def _digest(self) -> WorkbookBriefArtifactV1:
        if self.payload_digest not in _accepted_payload_digests(self.payload):
            raise ValueError("workbook brief payload digest mismatch")
        return self


def _canonical_payload_digest(
    payload: WorkbookBriefPayloadV1, *, omit_empty_introduced_terms: bool
) -> str:
    dumped = payload.model_dump(mode="json")
    if dumped.get("deep_dive_writer_receipt") is None:
        dumped.pop("deep_dive_writer_receipt", None)
    else:
        receipt = dumped["deep_dive_writer_receipt"]
        if receipt.get("slide_authority_map_digest") is None:
            receipt.pop("slide_authority_map_digest", None)
    skeleton = dumped.get("deep_dive_skeleton")
    if skeleton is not None:
        authority = skeleton.get("authority")
        if authority is not None and authority.get("slide_authority_map_digest") is None:
            authority.pop("slide_authority_map_digest", None)
    if omit_empty_introduced_terms and not dumped["scene_receipt"].get(
        "introduced_terms"
    ):
        dumped["scene_receipt"].pop("introduced_terms", None)
    canonical = json.dumps(
        dumped,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_payload_digest(payload: WorkbookBriefPayloadV1) -> str:
    """Digest current bytes while retaining baseline pre-38.3a field defaults."""
    return _canonical_payload_digest(payload, omit_empty_introduced_terms=False)


def _accepted_payload_digests(payload: WorkbookBriefPayloadV1) -> frozenset[str]:
    current = canonical_payload_digest(payload)
    if (
        payload.deep_dive_skeleton is not None
        or payload.deep_dive_writer_receipt is not None
        or payload.scene_receipt.introduced_terms
    ):
        return frozenset((current,))
    # The first real 36.4 fixtures predate ``introduced_terms`` while the
    # immediate 38.3a baseline serialized its empty default. Read both frozen
    # legacy-null domains; all newly written artifacts use ``current``.
    return frozenset(
        (
            current,
            _canonical_payload_digest(payload, omit_empty_introduced_terms=True),
        )
    )


def workbook_brief_contribution_receipt(
    artifact: WorkbookBriefArtifactV1,
) -> dict[str, object]:
    """Return the exact contribution witness for one validated brief artifact."""
    payload = artifact.payload
    receipt: dict[str, object] = {
        "artifact_path": WORKBOOK_BRIEF_FILENAME,
        "payload_digest": artifact.payload_digest,
        "schema_version": payload.schema_version,
        "status_summary": {
            "scene": payload.pre_work.scene.status,
            "promise": payload.pre_work.promise.status,
        },
        "warning_summary": list(payload.warnings),
        "loss_summary": list(payload.known_losses),
        "node_id": payload.node_id,
        "specialist_id": payload.specialist_id,
    }
    if payload.deep_dive_skeleton is not None:
        receipt["deep_dive_summary"] = {
            "status": payload.deep_dive_skeleton.status,
            "authority_digest": payload.deep_dive_skeleton.authority_digest,
            "candidate_payload_digest": payload.deep_dive_skeleton.candidate_payload_digest,
            "execution": payload.deep_dive_writer_receipt.model_dump(mode="json"),
        }
    return receipt


def write_workbook_brief(run_dir: Path, artifact: WorkbookBriefArtifactV1) -> Path:
    target = Path(run_dir) / WORKBOOK_BRIEF_FILENAME
    if target.is_symlink():
        raise ValueError("workbook brief target may not be a symlink")
    temporary = target.with_suffix(target.suffix + ".tmp")
    _exclusive_atomic_text(temporary, artifact.model_dump_json(indent=2) + "\n")
    os.replace(temporary, target)
    return target


def read_workbook_brief(run_dir: Path) -> WorkbookBriefArtifactV1:
    path = Path(run_dir) / WORKBOOK_BRIEF_FILENAME
    if path.is_symlink():
        raise ValueError(f"invalid workbook brief coordinate/digest at {path}: symlink")
    try:
        return WorkbookBriefArtifactV1.model_validate_json(
            path.read_text(encoding="utf-8"), strict=True
        )
    except (OSError, ValueError) as exc:
        raise ValueError(f"invalid workbook brief coordinate/digest at {path}: {exc}") from exc


def write_runtime_context(context: WorkbookBriefRuntimeContext) -> Path:
    target = context.run_dir / WORKBOOK_RUNTIME_CONTEXT_FILENAME
    if target.is_symlink():
        raise ValueError("workbook runtime context target may not be a symlink")
    temporary = target.with_suffix(target.suffix + ".tmp")
    if context.course_source_root is not None:
        validate_course_source_root(context.course_source_root)
    _exclusive_atomic_text(
        temporary, json.dumps(context.persisted(), sort_keys=True, indent=2) + "\n"
    )
    os.replace(temporary, target)
    return target


def read_runtime_context(run_dir: Path) -> WorkbookBriefRuntimeContext:
    path = Path(run_dir) / WORKBOOK_RUNTIME_CONTEXT_FILENAME
    if path.is_symlink():
        raise ValueError(f"invalid workbook runtime context at {path}: symlink")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid workbook runtime context at {path}: {exc}") from exc
    if (
        not isinstance(raw, dict)
        or raw.pop("schema_version", None) != "workbook-runtime-context.v1"
    ):
        raise ValueError("invalid workbook runtime context schema")
    raw["run_dir"] = Path(run_dir)
    raw["course_source_root"] = (
        Path(raw["course_source_root"]) if raw.get("course_source_root") else None
    )
    context = WorkbookBriefRuntimeContext.model_validate(raw, strict=True)
    if context.course_source_root is not None:
        validate_course_source_root(context.course_source_root)
    return context


def validate_course_source_root(root: Path) -> Path:
    resolved = Path(root).resolve(strict=True)
    authority = (Path(__file__).resolve().parents[3] / "course-content").resolve(strict=True)
    try:
        resolved.relative_to(authority)
    except ValueError as exc:
        raise ValueError("course_source_root must remain under course-content") from exc
    if not resolved.is_dir():
        raise ValueError("course_source_root must resolve to an existing directory")
    return resolved


def validate_source_child(root: Path, child: Path) -> Path:
    resolved_root = validate_course_source_root(root)
    resolved = Path(child).resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("course source child escapes its explicit root") from exc
    return resolved


def _exclusive_atomic_text(path: Path, text: str) -> None:
    if path.is_symlink():
        raise ValueError(f"atomic temporary path is a symlink: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"atomic temporary path already exists: {path}") from exc
    try:
        if stat.S_ISLNK(os.fstat(fd).st_mode):
            raise ValueError("atomic temporary path resolved to a symlink")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            fd = -1
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if fd >= 0:
            os.close(fd)


__all__ = [
    "WORKBOOK_BRIEF_FILENAME",
    "WORKBOOK_RUNTIME_CONTEXT_FILENAME",
    "DEEP_DIVE_JOURNAL_FILENAME",
    "WriterExecutionEvidence",
    "WriterExecutionReceipt",
    "DeepDiveExecutionReceiptV1",
    "deep_dive_idempotency_key",
    "SceneAuthoringReceipt",
    "PromiseAuthoringReceipt",
    "WorkbookBriefRuntimeContext",
    "WorkbookBriefPayloadV1",
    "WorkbookBriefArtifactV1",
    "canonical_payload_digest",
    "workbook_brief_contribution_receipt",
    "read_workbook_brief",
    "write_workbook_brief",
    "write_runtime_context",
    "read_runtime_context",
    "validate_course_source_root",
    "validate_source_child",
]
