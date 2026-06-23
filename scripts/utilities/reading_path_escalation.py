"""Triggered S3 catalog-guided reading-path tuple escalation."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.models.adapter import make_chat_model
from app.models.perception.perception_artifact import (
    CalloutIntent,
    ImageRoleTier,
    PerceptionArtifact,
    TextSubstructure,
)
from scripts.utilities.reading_path_derivation import derive_primary_name

LEXICON_PATH = Path(__file__).resolve().parents[2] / "state" / "config" / (
    "reading-path-escalation-lexicons.yaml"
)
DEFAULT_MODEL_ID = "gpt-5.5"
SPECIALIST_ID = "vision"
MAX_ESCALATION_RATE = 0.20

_ORDINAL_RE = re.compile(
    r"(?<![\w$])(?:step\s*)?([1-9]|[a-d])[\).:-]|\b(first|second|third|fourth)\b",
    re.I,
)


class EscalationBoundsError(AssertionError):
    """Raised when S3 escalation-rate tripwires fail."""


@dataclass(frozen=True)
class EscalationThresholds:
    """Tunable S3 predicate thresholds."""

    macro_margin: float = 0.15
    confidence_score: float = 0.70


@dataclass(frozen=True)
class EscalationDecision:
    """Frozen upstream S3 escalation decision for one artifact."""

    slide_id: str
    escalate: bool
    subpredicates: dict[str, bool]
    fired: list[str]
    trigger_reason: str
    low_conf_role_element_count: int = 0


@dataclass(frozen=True)
class EscalationRunResult:
    """S3 run output: merged artifacts plus observable ledger."""

    artifacts: list[PerceptionArtifact]
    ledger: dict[str, Any]


class LayoutDelta(BaseModel):
    """Optional D1 layout refinement."""

    model_config = ConfigDict(extra="forbid")

    two_pane: bool = False


class CalloutIntentDelta(BaseModel):
    """Optional D2 callout intent refinement."""

    model_config = ConfigDict(extra="forbid")

    element_id: str
    intent: CalloutIntent


class RoleOverride(BaseModel):
    """Optional image-role override from S3."""

    model_config = ConfigDict(extra="forbid")

    element_id: str
    role_tier: ImageRoleTier


class TupleDelta(BaseModel):
    """Structured tuple-delta returned by S3."""

    model_config = ConfigDict(extra="forbid")

    layout_delta: LayoutDelta | None = None
    callout_intents: list[CalloutIntentDelta] = Field(default_factory=list)
    process_kind: TextSubstructure | None = None
    role_overrides: list[RoleOverride] = Field(default_factory=list)


S3Client = Callable[[PerceptionArtifact, list[str]], str]


def decide_escalation(
    artifact: PerceptionArtifact,
    *,
    macro_margin: float | None = None,
    thresholds: EscalationThresholds | None = None,
) -> EscalationDecision:
    """Compute the upstream-frozen S3 escalation predicate from S1/S2 signals."""
    active_thresholds = thresholds or EscalationThresholds()
    lexicons = _load_lexicons()
    text = _artifact_text(artifact)
    low_conf_role_count = sum(1 for role in artifact.image_roles or [] if role is None)
    subpredicates = {
        "macro_margin_low": (
            macro_margin is not None and macro_margin < active_thresholds.macro_margin
        ),
        "opposition_cue_hit": "oppositional_cue" in (artifact.reading_path_flags or []),
        "callout_kind_present": _has_any_token(
            _element_kind_text(artifact), lexicons.callout_kinds
        ),
        "numbered_without_transform": (
            bool(_ORDINAL_RE.search(text))
            and not _has_any_token(text, lexicons.transform_verbs)
        ),
        "low_conf_role_elements": low_conf_role_count > 0,
        "tuple_disagreement": _has_tuple_disagreement(artifact),
        "low_confidence": (
            artifact.confidence == "LOW"
            or (
                artifact.confidence_score is not None
                and artifact.confidence_score < active_thresholds.confidence_score
            )
        ),
        "tier_candidate_hit": any(
            flag in (artifact.image_role_flags or [])
            for flag in ("tier_2_5_candidate", "tier_3_quarantined")
        ),
    }
    fired = [name for name, value in subpredicates.items() if value]
    return EscalationDecision(
        slide_id=artifact.slide_id,
        escalate=bool(fired),
        subpredicates=subpredicates,
        fired=fired,
        trigger_reason=", ".join(fired) if fired else "none",
        low_conf_role_element_count=low_conf_role_count,
    )


def build_escalation_ledger(
    artifacts: list[PerceptionArtifact],
    *,
    output_path: str | Path | None = None,
    thresholds: EscalationThresholds | None = None,
    macro_margins: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Create and optionally persist the always-on S3 escalation ledger."""
    rows: list[dict[str, Any]] = []
    for artifact in artifacts:
        decision = decide_escalation(
            artifact,
            macro_margin=(macro_margins or {}).get(artifact.slide_id),
            thresholds=thresholds,
        )
        rows.append(_ledger_row(decision))
    total = len(rows)
    ledger = {
        "total": total,
        "escalated": sum(1 for row in rows if row["escalate"]),
        "escalation_rate": (
            sum(1 for row in rows if row["escalate"]) / total if total else 0.0
        ),
        "slides": rows,
    }
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ledger


def assert_escalation_rate_bounds(
    ledger: dict[str, Any],
    *,
    max_rate: float = MAX_ESCALATION_RATE,
    known_ambiguous_present: bool = False,
) -> None:
    """Tripwire over-escalation and dead zero-escalation."""
    rows = ledger.get("slides") or []
    total = int(ledger.get("total") or len(rows))
    escalated = sum(1 for row in rows if bool(row.get("escalate")))
    rate = escalated / total if total else 0.0
    if rate > max_rate:
        raise EscalationBoundsError(
            f"over-escalation: {escalated}/{total} ({rate:.2%}) exceeds {max_rate:.2%}"
        )
    if known_ambiguous_present and total and escalated == 0:
        raise EscalationBoundsError("zero-escalation: known ambiguous fixture did not fire")


def parse_tuple_delta(raw: str, *, fired: list[str]) -> TupleDelta:
    """Parse a structured S3 response and clear fields for unfired jobs."""
    try:
        data = json.loads(_strip_json(raw))
    except ValueError as exc:
        raise ValueError(f"S3 tuple-delta was not valid JSON: {exc}") from exc
    try:
        delta = TupleDelta.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"S3 tuple-delta failed validation: {exc}") from exc
    updates: dict[str, Any] = {}
    if "opposition_cue_hit" not in fired:
        updates["layout_delta"] = None
    if "callout_kind_present" not in fired:
        updates["callout_intents"] = []
    if "numbered_without_transform" not in fired:
        updates["process_kind"] = None
    if not any(
        name in fired
        for name in (
            "low_conf_role_elements",
            "tier_candidate_hit",
            "tuple_disagreement",
        )
    ):
        updates["role_overrides"] = []
    return delta.model_copy(update=updates)


def apply_tuple_delta(artifact: PerceptionArtifact, delta: TupleDelta) -> PerceptionArtifact:
    """Merge S3 tuple-delta over the S1/S2 tuple without changing scoring semantics."""
    updates: dict[str, Any] = {}
    macro_layout = artifact.macro_layout
    text_substructure = artifact.text_substructure
    if delta.layout_delta and delta.layout_delta.two_pane:
        macro_layout = "two_pane"
        text_substructure = "comparison_pair"
    if delta.process_kind in {"enumerated_process", "peer_boxes"}:
        text_substructure = delta.process_kind
    if macro_layout is not None:
        updates["macro_layout"] = macro_layout
    if text_substructure is not None:
        updates["text_substructure"] = text_substructure
    if macro_layout is not None and text_substructure is not None:
        updates["reading_path"] = derive_primary_name(macro_layout, text_substructure)
    if delta.callout_intents:
        updates["callout_intent"] = delta.callout_intents[0].intent
    if delta.role_overrides and artifact.image_roles is not None:
        updates["image_roles"] = _merge_role_overrides(
            artifact.visual_elements,
            artifact.image_roles,
            delta.role_overrides,
        )
    return artifact.model_copy(update=updates)


def run_s3_escalation(
    artifacts: list[PerceptionArtifact],
    *,
    client: S3Client | None = None,
    thresholds: EscalationThresholds | None = None,
    macro_margins: dict[str, float] | None = None,
) -> EscalationRunResult:
    """Run single-shot S3 tuple-delta escalation for every escalated artifact."""
    active_client = client or request_live_tuple_delta
    merged: list[PerceptionArtifact] = []
    rows: list[dict[str, Any]] = []
    for artifact in artifacts:
        decision = decide_escalation(
            artifact,
            macro_margin=(macro_margins or {}).get(artifact.slide_id),
            thresholds=thresholds,
        )
        row = _ledger_row(decision)
        if not decision.escalate:
            merged.append(artifact)
            rows.append(row)
            continue
        try:
            raw = active_client(artifact, decision.fired)
            delta = parse_tuple_delta(raw, fired=decision.fired)
        except (ValueError, TypeError, ValidationError) as exc:
            row["degraded"] = True
            row["degrade_reason"] = str(exc)
            merged.append(artifact)
        else:
            row["degraded"] = False
            row["delta_applied"] = True
            merged.append(apply_tuple_delta(artifact, delta))
        rows.append(row)
    total = len(rows)
    ledger = {
        "total": total,
        "escalated": sum(1 for row in rows if row["escalate"]),
        "escalation_rate": (
            sum(1 for row in rows if row["escalate"]) / total if total else 0.0
        ),
        "slides": rows,
    }
    return EscalationRunResult(artifacts=merged, ledger=ledger)


def request_live_tuple_delta(
    artifact: PerceptionArtifact,
    fired: list[str],
    *,
    model_id: str = DEFAULT_MODEL_ID,
    timeout_seconds: float = 60.0,
) -> str:
    """Make the single live >=gpt-5.5 S3 tuple-delta call."""
    handle = make_chat_model(
        SPECIALIST_ID,
        per_call_override=model_id,
        temperature=0.0,
    )
    messages = [
        SystemMessage(
            content=(
                "You are a catalog-guided reading-path tuple arbiter. Return only "
                "the requested JSON tuple-delta. Do not volunteer fields for jobs "
                "not listed in fired."
            )
        ),
        HumanMessage(content=_tuple_delta_prompt(artifact, fired)),
    ]
    response = handle.chat.bind(timeout=timeout_seconds).invoke(messages)
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    return json.dumps(content)


@dataclass(frozen=True)
class _Lexicons:
    opposition: tuple[str, ...]
    transform_verbs: tuple[str, ...]
    callout_kinds: tuple[str, ...]


def _load_lexicons() -> _Lexicons:
    data = yaml.safe_load(LEXICON_PATH.read_text(encoding="utf-8")) or {}
    return _Lexicons(
        opposition=tuple(str(item).lower() for item in data.get("opposition", [])),
        transform_verbs=tuple(str(item).lower() for item in data.get("transform_verbs", [])),
        callout_kinds=tuple(str(item).lower() for item in data.get("callout_kinds", [])),
    )


def _ledger_row(decision: EscalationDecision) -> dict[str, Any]:
    return {
        "slide_id": decision.slide_id,
        "escalate": decision.escalate,
        "subpredicates": decision.subpredicates,
        "fired": decision.fired,
        "trigger_reason": decision.trigger_reason,
        "low_conf_role_element_count": decision.low_conf_role_element_count,
    }


def _artifact_text(artifact: PerceptionArtifact) -> str:
    parts = [
        artifact.slide_title,
        artifact.layout_description,
        artifact.extracted_text,
        *[
            item if isinstance(item, str) else " ".join(str(value) for value in item.values())
            for item in artifact.text_blocks
        ],
        _element_kind_text(artifact),
    ]
    return " ".join(part for part in parts if part).lower()


def _element_kind_text(artifact: PerceptionArtifact) -> str:
    return " ".join(
        " ".join(
            str(raw.get(field) or "")
            for field in ("id", "kind", "type", "label", "text", "title", "description")
        )
        for raw in artifact.visual_elements
    ).lower()


def _has_any_token(text: str, tokens: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(token in normalized for token in tokens)


def _has_tuple_disagreement(artifact: PerceptionArtifact) -> bool:
    roles = artifact.image_roles or []
    for index, raw in enumerate(artifact.visual_elements):
        emitted_role = raw.get("role_tier")
        if emitted_role in {"1", "2", "2_5", "3", "4"} and index < len(roles):
            classified_role = roles[index]
            if classified_role is not None and emitted_role != classified_role:
                return True
        for field in ("macro_layout", "text_substructure", "narration_cadence"):
            emitted = raw.get(field)
            classified = getattr(artifact, field, None)
            if emitted is not None and classified is not None and emitted != classified:
                return True
    return False


def _strip_json(raw: str) -> str:
    stripped = raw.strip()
    if "```" in stripped:
        fence = "```json" if "```json" in stripped else "```"
        start = stripped.find(fence) + len(fence)
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    if not stripped.startswith("{"):
        first = stripped.find("{")
        last = stripped.rfind("}")
        if first != -1 and last > first:
            stripped = stripped[first : last + 1]
    return stripped


def _merge_role_overrides(
    visual_elements: list[dict[str, Any]],
    image_roles: list[ImageRoleTier | None],
    overrides: list[RoleOverride],
) -> list[ImageRoleTier | None]:
    merged = list(image_roles)
    index_by_id = {
        str(raw.get("id") or raw.get("element_id") or "").strip(): index
        for index, raw in enumerate(visual_elements)
    }
    for override in overrides:
        index = index_by_id.get(override.element_id)
        if index is None or index >= len(merged):
            continue
        if merged[index] is None:
            continue
        merged[index] = override.role_tier
    return merged


def _tuple_delta_prompt(artifact: PerceptionArtifact, fired: list[str]) -> str:
    return (
        "Return EXACTLY this JSON shape: "
        '{"layout_delta":{"two_pane":true}|null,'
        '"callout_intents":[{"element_id":"id","intent":"invite_response|challenge_quiz|directive_cta"}],'
        '"process_kind":"enumerated_process|peer_boxes"|null,'
        '"role_overrides":[{"element_id":"id","role_tier":"1|2|2_5|3|4"}]}.\n'
        f"slide_id: {artifact.slide_id}\n"
        f"fired: {json.dumps(fired)}\n"
        f"artifact: {artifact.model_dump_json()}\n"
        "Only answer questions implied by fired. Use null/empty arrays for unfired jobs."
    )


__all__ = [
    "EscalationBoundsError",
    "EscalationDecision",
    "EscalationRunResult",
    "EscalationThresholds",
    "TupleDelta",
    "apply_tuple_delta",
    "assert_escalation_rate_bounds",
    "build_escalation_ledger",
    "decide_escalation",
    "parse_tuple_delta",
    "request_live_tuple_delta",
    "run_s3_escalation",
]
