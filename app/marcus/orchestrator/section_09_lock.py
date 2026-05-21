"""Section 09 four-artifact lock enforcement."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.gates.errors import GateError
from app.marcus.orchestrator.writers.slide_content import GarySlideContent
from app.models.state._base import enforce_tz_aware

Section09ArtifactKind = Literal[
    "gary-slide-content",
    "kira-motion-plan",
    "vera-fidelity-verdict",
    "quinn-r-qa-verdict",
]
Section09FailureKind = Literal[
    "absent",
    "parse_error",
    "plan_unit_id_mismatch",
    "validation_error",
]
DEFAULT_SECTION_09_TRIPWIRE_LOG = Path("_artifacts") / "section_09_lock_tripwire.jsonl"


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class Section09LockArtifactPaths(BaseModel):
    """Expected file paths for the Section 09 lock quartet."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    gary_slide_content_path: Path = Field(
        ...,
        description="Path to the Gary slide-content artifact.",
    )
    kira_motion_plan_path: Path = Field(
        ...,
        description="Path to the Kira motion-plan artifact.",
    )
    vera_fidelity_verdict_path: Path = Field(
        ...,
        description="Path to the Vera fidelity-verdict artifact.",
    )
    quinn_r_qa_verdict_path: Path = Field(
        ...,
        description="Path to the Quinn-R QA-verdict artifact.",
    )

    @field_validator(
        "gary_slide_content_path",
        "kira_motion_plan_path",
        "vera_fidelity_verdict_path",
        "quinn_r_qa_verdict_path",
        mode="before",
    )
    @classmethod
    def _reject_blank_paths(cls, value: object) -> object:
        if isinstance(value, str):
            return Path(_strip_non_empty(value, field_name="artifact_path"))
        return value


class Section09LockArtifactRef(BaseModel):
    """Digest-bound reference to one locked artifact."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    artifact_kind: Section09ArtifactKind = Field(
        ...,
        description="Closed Section 09 artifact kind.",
    )
    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier carried by this artifact.",
    )
    artifact_digest: str = Field(
        ...,
        pattern=r"^[0-9a-f]{64}$",
        description="Lowercase sha256 digest of the artifact bytes.",
    )
    artifact_path: Path = Field(..., description="Path to the locked artifact.")

    @field_validator("plan_unit_id", mode="before")
    @classmethod
    def _strip_plan_unit_id(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="plan_unit_id")
        return value


class Section09LockResult(BaseModel):
    """Success result for the Section 09 lock quartet."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    lock_status: Literal["locked"] = Field(
        default="locked",
        description="Success-only lock status. Failures raise GateError.",
    )
    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Shared plan-unit identifier for the locked quartet.",
    )
    gary_slide_content: Section09LockArtifactRef = Field(
        ...,
        description="Locked Gary slide-content artifact reference.",
    )
    kira_motion_plan: Section09LockArtifactRef = Field(
        ...,
        description="Locked Kira motion-plan artifact reference.",
    )
    vera_fidelity_verdict: Section09LockArtifactRef = Field(
        ...,
        description="Locked Vera fidelity-verdict artifact reference.",
    )
    quinn_r_qa_verdict: Section09LockArtifactRef = Field(
        ...,
        description="Locked Quinn-R QA-verdict artifact reference.",
    )
    locked_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timezone-aware lock timestamp.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator("plan_unit_id", mode="before")
    @classmethod
    def _strip_plan_unit_id(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="plan_unit_id")
        return value

    @field_validator("locked_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


class _PlanUnitOnlyArtifact(BaseModel):
    """Fallback parser for lock-relevant producer artifacts."""

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    plan_unit_id: str = Field(..., min_length=1)

    @field_validator("plan_unit_id", mode="before")
    @classmethod
    def _strip_plan_unit_id(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="plan_unit_id")
        return value


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def _append_section_09_tripwire(
    *,
    plan_unit_id: str,
    failure_kind: Section09FailureKind,
    failed_artifact_kind: Section09ArtifactKind,
    tripwire_log_path: Path | None,
) -> None:
    fired_at = _now_utc().isoformat()
    _append_jsonl(
        tripwire_log_path or DEFAULT_SECTION_09_TRIPWIRE_LOG,
        {
            "event": "section_09_lock_failure",
            "failed_artifact_kind": failed_artifact_kind,
            "failure_kind": failure_kind,
            "fired_at": fired_at,
            "plan_unit_id": plan_unit_id,
            "schema_version": 1,
        },
    )


def _fail(
    *,
    plan_unit_id: str,
    failure_kind: Section09FailureKind,
    failed_artifact_kind: Section09ArtifactKind,
    message: str,
    tripwire_log_path: Path | None,
) -> None:
    _append_section_09_tripwire(
        plan_unit_id=plan_unit_id,
        failure_kind=failure_kind,
        failed_artifact_kind=failed_artifact_kind,
        tripwire_log_path=tripwire_log_path,
    )
    raise GateError("section_09_lock_failure", message)


def _load_json_artifact(
    *,
    expected_plan_unit_id: str,
    artifact_kind: Section09ArtifactKind,
    path: Path,
    tripwire_log_path: Path | None,
) -> tuple[str, Section09LockArtifactRef]:
    if not path.exists():
        _fail(
            plan_unit_id=expected_plan_unit_id,
            failure_kind="absent",
            failed_artifact_kind=artifact_kind,
            message=f"Section 09 lock artifact is absent: {artifact_kind}",
            tripwire_log_path=tripwire_log_path,
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(
            plan_unit_id=expected_plan_unit_id,
            failure_kind="parse_error",
            failed_artifact_kind=artifact_kind,
            message=f"Section 09 lock artifact is not valid JSON: {artifact_kind}",
            tripwire_log_path=tripwire_log_path,
        )
        raise AssertionError("unreachable") from exc
    try:
        if artifact_kind == "gary-slide-content":
            parsed = GarySlideContent.model_validate(payload)
        else:
            parsed = _PlanUnitOnlyArtifact.model_validate(payload)
    except ValidationError as exc:
        _fail(
            plan_unit_id=expected_plan_unit_id,
            failure_kind="validation_error",
            failed_artifact_kind=artifact_kind,
            message=f"Section 09 lock artifact failed validation: {artifact_kind}",
            tripwire_log_path=tripwire_log_path,
        )
        raise AssertionError("unreachable") from exc
    artifact_plan_unit_id = parsed.plan_unit_id
    return artifact_plan_unit_id, Section09LockArtifactRef(
        artifact_kind=artifact_kind,
        plan_unit_id=artifact_plan_unit_id,
        artifact_digest=_digest(path),
        artifact_path=path,
    )


def enforce_section_09_lock(
    plan_unit_id: str,
    artifact_paths: Section09LockArtifactPaths,
    *,
    tripwire_log_path: Path | None = None,
) -> Section09LockResult:
    """Require the four Section 09 artifacts to exist and share plan_unit_id."""

    normalized_plan_unit_id = _strip_non_empty(
        plan_unit_id,
        field_name="plan_unit_id",
    )
    loaded = {
        "gary_slide_content": _load_json_artifact(
            expected_plan_unit_id=normalized_plan_unit_id,
            artifact_kind="gary-slide-content",
            path=artifact_paths.gary_slide_content_path,
            tripwire_log_path=tripwire_log_path,
        ),
        "kira_motion_plan": _load_json_artifact(
            expected_plan_unit_id=normalized_plan_unit_id,
            artifact_kind="kira-motion-plan",
            path=artifact_paths.kira_motion_plan_path,
            tripwire_log_path=tripwire_log_path,
        ),
        "vera_fidelity_verdict": _load_json_artifact(
            expected_plan_unit_id=normalized_plan_unit_id,
            artifact_kind="vera-fidelity-verdict",
            path=artifact_paths.vera_fidelity_verdict_path,
            tripwire_log_path=tripwire_log_path,
        ),
        "quinn_r_qa_verdict": _load_json_artifact(
            expected_plan_unit_id=normalized_plan_unit_id,
            artifact_kind="quinn-r-qa-verdict",
            path=artifact_paths.quinn_r_qa_verdict_path,
            tripwire_log_path=tripwire_log_path,
        ),
    }
    plan_unit_ids = {item[0] for item in loaded.values()}
    if plan_unit_ids != {normalized_plan_unit_id}:
        _fail(
            plan_unit_id=normalized_plan_unit_id,
            failure_kind="plan_unit_id_mismatch",
            failed_artifact_kind="gary-slide-content",
            message="Section 09 lock artifacts do not share the requested plan_unit_id",
            tripwire_log_path=tripwire_log_path,
        )
    refs = {name: item[1] for name, item in loaded.items()}
    return Section09LockResult(
        plan_unit_id=normalized_plan_unit_id,
        gary_slide_content=refs["gary_slide_content"],
        kira_motion_plan=refs["kira_motion_plan"],
        vera_fidelity_verdict=refs["vera_fidelity_verdict"],
        quinn_r_qa_verdict=refs["quinn_r_qa_verdict"],
    )


__all__ = [
    "DEFAULT_SECTION_09_TRIPWIRE_LOG",
    "Section09ArtifactKind",
    "Section09FailureKind",
    "Section09LockArtifactPaths",
    "Section09LockArtifactRef",
    "Section09LockResult",
    "enforce_section_09_lock",
]
