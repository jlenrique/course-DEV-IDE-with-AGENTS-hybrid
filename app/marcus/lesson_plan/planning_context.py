"""Load optional planning context for Irene Pass-1 (purpose/audience/LOs/assessment).

Merges on-disk ``planning-ratification.json`` and ``ratified-los.json`` under a
run directory. Corpus remains the only topic basis; this module only frames
emphasis. Absent artifacts → ``None`` (today's Irene behavior).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.marcus.lesson_plan.source_assessment import SourceAssessment

RATIFICATION_FILENAME = "planning-ratification.json"
RATIFIED_LOS_FILENAME = "ratified-los.json"


class PlanningContextError(ValueError):
    """Raised when planning context cannot be loaded honestly."""


class LearningObjectiveBrief(BaseModel):
    """Minimal LO shape for Pass-1 framing (not a full G0R card)."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    objective_id: str = ""
    statement: str
    bloom_level: str = ""
    status: str = "ratified"

    @field_validator("statement")
    @classmethod
    def _statement_nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("learning objective statement must be non-empty")
        return cleaned


class PlanningContext(BaseModel):
    """Structured framing threaded to Irene Pass-1 as advisory context."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["0.1"] = "0.1"
    purpose: str = ""
    audience: str = ""
    learning_objectives: tuple[LearningObjectiveBrief, ...] = Field(default_factory=tuple)
    source_assessment: SourceAssessment | None = None
    sources_present: tuple[str, ...] = Field(default_factory=tuple)
    claim_fence: str = (
        "Planning context is framing only; corpus remains the only topic basis."
    )

    def to_payload_dict(self) -> dict[str, Any]:
        """JSON-shaped dict for runner / envelope payload."""
        return self.model_dump(mode="json")

    def has_framing(self) -> bool:
        """True when any framing signal is present."""
        return bool(
            self.purpose.strip()
            or self.audience.strip()
            or self.learning_objectives
            or self.source_assessment is not None
        )


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PlanningContextError(f"{label} unreadable at {path}: {exc}") from exc
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlanningContextError(
            f"{label} malformed JSON at {path}: {exc}"
        ) from exc
    if not isinstance(loaded, dict):
        raise PlanningContextError(
            f"{label} must be a JSON object at {path}"
        )
    return loaded


def _los_from_ratified(payload: dict[str, Any]) -> tuple[LearningObjectiveBrief, ...]:
    raw_list = payload.get("ratified_los")
    if raw_list is None:
        return ()
    if not isinstance(raw_list, list):
        raise PlanningContextError(
            "ratified-los.json: ratified_los must be a list"
        )
    briefs: list[LearningObjectiveBrief] = []
    for index, item in enumerate(raw_list):
        if not isinstance(item, dict):
            raise PlanningContextError(
                f"ratified-los.json: entry {index} must be an object"
            )
        statement = str(item.get("statement") or "").strip()
        if not statement:
            continue
        briefs.append(
            LearningObjectiveBrief(
                objective_id=str(item.get("objective_id") or ""),
                statement=statement,
                bloom_level=str(item.get("bloom_level") or ""),
                status=str(item.get("status") or "ratified"),
            )
        )
    return tuple(briefs)


def _from_ratification(
    payload: dict[str, Any],
) -> tuple[str, str, SourceAssessment | None, str]:
    purpose = str(payload.get("purpose") or "").strip()
    audience = str(payload.get("audience") or "").strip()
    assessment: SourceAssessment | None = None
    raw_assessment = payload.get("source_assessment")
    if raw_assessment is not None:
        if not isinstance(raw_assessment, dict):
            raise PlanningContextError(
                "planning-ratification.json: source_assessment must be an object"
            )
        try:
            assessment = SourceAssessment.model_validate(raw_assessment)
        except Exception as exc:  # pydantic ValidationError
            raise PlanningContextError(
                f"planning-ratification.json: invalid source_assessment: {exc}"
            ) from exc
    claim_fence = str(
        payload.get("claim_fence")
        or "Planning context is framing only; corpus remains the only topic basis."
    ).strip()
    return purpose, audience, assessment, claim_fence


CoverageStatus = Literal["present", "partial", "absent"]


class PlanningContextCoverageReceipt(BaseModel):
    """Soft LO-coverage receipt emitted when planning_context is present."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["0.1"] = "0.1"
    context_present: Literal[True] = True
    lo_coverage: CoverageStatus
    supported_objective_ids: tuple[str, ...] = Field(default_factory=tuple)
    weak_or_missing_objective_ids: tuple[str, ...] = Field(default_factory=tuple)
    purpose_acknowledged: bool = False
    audience_acknowledged: bool = False
    notes: str = ""

    @model_validator(mode="after")
    def _coverage_status_matches_objective_sets(self) -> PlanningContextCoverageReceipt:
        weak = self.weak_or_missing_objective_ids
        supported = self.supported_objective_ids
        if self.lo_coverage == "present" and weak:
            raise ValueError("present LO coverage cannot contain weak or missing objectives")
        if self.lo_coverage == "partial" and not weak:
            raise ValueError("partial LO coverage requires weak or missing objectives")
        if self.lo_coverage == "absent" and (supported or not weak):
            raise ValueError(
                "absent LO coverage requires no supported objectives and at least one "
                "weak or missing objective"
            )
        return self


def _significant_tokens(text: str) -> set[str]:
    """Tokens longer than 3 chars, minus a small stopword set for LO overlap."""
    stop = {
        "that",
        "this",
        "with",
        "from",
        "into",
        "have",
        "will",
        "when",
        "what",
        "which",
        "their",
        "there",
        "about",
        "after",
        "before",
        "under",
        "over",
        "than",
        "then",
        "them",
        "they",
        "were",
        "been",
        "being",
        "also",
        "only",
        "just",
        "such",
        "using",
        "used",
        "understand",
        "material",
        "introduced",
        "module",
        "learning",
        "objective",
        "objectives",
    }
    return {
        tok
        for tok in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
        if len(tok) > 3 and tok not in stop
    }


def assess_lo_coverage(
    context: PlanningContext,
    plan: dict[str, Any],
) -> PlanningContextCoverageReceipt:
    """Assess whether emitted plan units reflect context LOs (soft receipt).

    Overlap heuristic (honesty-bounded):
    - An LO is *supported* when ≥50% of its significant tokens appear in
      concatenated plan unit titles / learning_objective / rationale.
    - An LO is *touched* when it shares ≥1 significant token with the plan.
    - Tokenless LOs (after stopword filter) count as weak/missing — never
      auto-supported (ECH-01).
    - ``lo_coverage=absent`` only when no LO is even *touched* (or plan_units
      empty). Fail-loud uses absent; partial/present never fail-loud.
    """
    units = plan.get("plan_units") if isinstance(plan, dict) else None
    if not isinstance(units, list):
        units = []
    plan_text = " ".join(
        f"{u.get('title', '')} {u.get('learning_objective', '')} "
        f"{u.get('rationale', '')}"
        for u in units
        if isinstance(u, dict)
    )
    plan_tokens = _significant_tokens(plan_text)
    purpose = context.purpose.strip()
    audience = context.audience.strip()
    purpose_ack = bool(purpose) and bool(_significant_tokens(purpose) & plan_tokens)
    audience_ack = bool(audience) and bool(
        _significant_tokens(audience) & plan_tokens
    )

    if not context.learning_objectives:
        return PlanningContextCoverageReceipt(
            lo_coverage="present",
            purpose_acknowledged=purpose_ack or not purpose,
            audience_acknowledged=audience_ack or not audience,
            notes="no LOs in planning_context; framing-only receipt",
        )

    if not units:
        ids = tuple(
            lo.objective_id or f"lo-idx-{i}"
            for i, lo in enumerate(context.learning_objectives)
        )
        return PlanningContextCoverageReceipt(
            lo_coverage="absent",
            weak_or_missing_objective_ids=ids,
            purpose_acknowledged=purpose_ack,
            audience_acknowledged=audience_ack,
            notes="empty plan_units with non-empty LOs",
        )

    supported: list[str] = []
    touched: list[str] = []
    missing: list[str] = []
    for index, lo in enumerate(context.learning_objectives):
        lo_id = lo.objective_id or f"lo-idx-{index}"
        lo_tokens = _significant_tokens(lo.statement)
        if not lo_tokens:
            missing.append(lo_id)
            continue
        overlap = lo_tokens & plan_tokens
        if len(overlap) / len(lo_tokens) >= 0.5:
            supported.append(lo_id)
            touched.append(lo_id)
        elif overlap:
            touched.append(lo_id)
            missing.append(lo_id)
        else:
            missing.append(lo_id)

    if not touched:
        status: CoverageStatus = "absent"
    elif missing:
        status = "partial"
    else:
        status = "present"

    return PlanningContextCoverageReceipt(
        lo_coverage=status,
        supported_objective_ids=tuple(supported),
        weak_or_missing_objective_ids=tuple(missing),
        purpose_acknowledged=purpose_ack or not purpose,
        audience_acknowledged=audience_ack or not audience,
        notes=f"lo_coverage={status}; touched={len(touched)}/{len(context.learning_objectives)}",
    )


def assert_lo_coverage_or_fail(
    context: PlanningContext,
    receipt: PlanningContextCoverageReceipt,
) -> None:
    """Fail loud on total LO ignore when context carries non-empty LOs."""
    from app.specialists.dispatch_errors import SpecialistDispatchError

    if not context.learning_objectives:
        return
    if receipt.lo_coverage == "absent":
        raise SpecialistDispatchError(
            "planning_context learning objectives were totally ignored by "
            f"Irene Pass-1 plan (coverage=absent; missing="
            f"{list(receipt.weak_or_missing_objective_ids)})",
            tag="irene_pass1.planning_context.lo_ignore",
        )


def load_planning_context(run_dir: Path) -> PlanningContext | None:
    """Load and merge planning artifacts from ``run_dir``.

    Merge rules (party 2026-07-09):
    - ``ratified-los.json`` authoritative for LO list when non-empty
    - ``planning-ratification.json`` authoritative for purpose/audience/assessment
    - empty must not overwrite present
    - if ``ratified-los.json`` also carries non-empty purpose/audience that
      conflicts with ratification → fail loud
    - neither file → ``None``
    - malformed → ``PlanningContextError``
    """
    run_dir = Path(run_dir)
    ratification_path = run_dir / RATIFICATION_FILENAME
    los_path = run_dir / RATIFIED_LOS_FILENAME
    has_ratification = ratification_path.is_file()
    has_los = los_path.is_file()
    if not has_ratification and not has_los:
        return None

    sources: list[str] = []
    purpose = ""
    audience = ""
    assessment: SourceAssessment | None = None
    claim_fence = (
        "Planning context is framing only; corpus remains the only topic basis."
    )
    objectives: tuple[LearningObjectiveBrief, ...] = ()

    if has_ratification:
        sources.append(RATIFICATION_FILENAME)
        rat_payload = _read_json(ratification_path, label=RATIFICATION_FILENAME)
        purpose, audience, assessment, claim_fence = _from_ratification(rat_payload)

    if has_los:
        sources.append(RATIFIED_LOS_FILENAME)
        los_payload = _read_json(los_path, label=RATIFIED_LOS_FILENAME)
        objectives = _los_from_ratified(los_payload)
        # Conflict check: ratified-los may optionally carry purpose/audience
        # (future); non-empty conflict with ratification fails loud.
        los_purpose = str(los_payload.get("purpose") or "").strip()
        los_audience = str(los_payload.get("audience") or "").strip()
        if los_purpose and purpose and los_purpose != purpose:
            raise PlanningContextError(
                "conflicting non-empty purpose between "
                "planning-ratification.json and ratified-los.json"
            )
        if los_audience and audience and los_audience != audience:
            raise PlanningContextError(
                "conflicting non-empty audience between "
                "planning-ratification.json and ratified-los.json"
            )
        if los_purpose and not purpose:
            purpose = los_purpose
        if los_audience and not audience:
            audience = los_audience

    ctx = PlanningContext(
        purpose=purpose,
        audience=audience,
        learning_objectives=objectives,
        source_assessment=assessment,
        sources_present=tuple(sources),
        claim_fence=claim_fence,
    )
    if not ctx.has_framing():
        # Both files present but empty of usable framing — treat as absent.
        return None
    return ctx


__all__ = [
    "LearningObjectiveBrief",
    "PlanningContext",
    "PlanningContextCoverageReceipt",
    "PlanningContextError",
    "RATIFICATION_FILENAME",
    "RATIFIED_LOS_FILENAME",
    "assess_lo_coverage",
    "assert_lo_coverage_or_fail",
    "load_planning_context",
]
