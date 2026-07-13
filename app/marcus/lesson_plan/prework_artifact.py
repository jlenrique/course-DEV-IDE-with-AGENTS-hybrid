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
    deep_dive_skeleton: None = None

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
        return self


class WorkbookBriefArtifactV1(_Strict):
    payload: WorkbookBriefPayloadV1
    payload_digest: str

    @model_validator(mode="after")
    def _digest(self) -> WorkbookBriefArtifactV1:
        if self.payload_digest != canonical_payload_digest(self.payload):
            raise ValueError("workbook brief payload digest mismatch")
        return self


def canonical_payload_digest(payload: WorkbookBriefPayloadV1) -> str:
    canonical = json.dumps(
        payload.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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
    "WriterExecutionEvidence",
    "WriterExecutionReceipt",
    "SceneAuthoringReceipt",
    "PromiseAuthoringReceipt",
    "WorkbookBriefRuntimeContext",
    "WorkbookBriefPayloadV1",
    "WorkbookBriefArtifactV1",
    "canonical_payload_digest",
    "read_workbook_brief",
    "write_workbook_brief",
    "write_runtime_context",
    "read_runtime_context",
    "validate_course_source_root",
    "validate_source_child",
]
