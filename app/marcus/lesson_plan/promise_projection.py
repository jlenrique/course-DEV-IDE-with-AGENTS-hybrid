"""Strict ratified-objective resolution and pure Promise composition (36.3)."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN
from app.marcus.lesson_plan.learning_objective import LearningObjective
from app.marcus.lesson_plan.prework_projection import (
    NonBlankStr,
    ObjectiveInput,
    PromiseProjection,
    PromiseTransformer,
    PromiseTransformRequest,
    PromiseVow,
)
from app.marcus.lesson_plan.workbook_enrichment import lesson_plan_from_run

PROMISE_MARKER = "promise_semantics_not_authored"
_OPEN_ID = re.compile(OPEN_ID_REGEX_PATTERN)
_BASE_WARNINGS = (
    "promise_no_spoiler_operator_check",
    "promise_lo_vs_vow_operator_check",
    "promise_pertinent_ability_operator_check",
    "promise_half_rhyme_operator_check",
    "promise_mastery_overclaim_operator_check",
)


class PromiseObjectiveResolutionError(ValueError):
    """Authority artifact exists but violates its fail-loud shape contract."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)


class PromiseObjectiveResolution(_Strict):
    status: Literal["authored", "degraded", "unavailable"]
    objectives: tuple[ObjectiveInput, ...] = ()
    authority_variants: tuple[Literal["canonical_g0r", "plan_dialogue"], ...] = ()
    authority_refs: tuple[str, ...] = ()
    known_losses: tuple[str, ...] = ()
    operator_warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _honest(self) -> PromiseObjectiveResolution:
        sizes = {len(self.objectives), len(self.authority_variants), len(self.authority_refs)}
        if self.status == "authored" and (
            not self.objectives or sizes != {len(self.objectives)} or self.known_losses
        ):
            raise ValueError("authored resolution requires aligned authority and no losses")
        if self.status != "authored" and self.objectives:
            raise ValueError("ineligible resolution cannot expose partial objectives")
        if self.status != "authored" and not self.known_losses:
            raise ValueError("ineligible resolution requires a stable loss")
        return self


class PromiseProjectionRequest(_Strict):
    resolution: PromiseObjectiveResolution
    scene_context: NonBlankStr | None = None
    friction_context: NonBlankStr | None = None
    forbidden_resolution_spans: tuple[str, ...] = ()


class PromiseGateReceipt(_Strict):
    failures: tuple[str, ...] = ()


class PromiseProjectionResult(_Strict):
    projection: PromiseProjection
    gate_receipt: PromiseGateReceipt
    authority_refs: tuple[str, ...] = ()
    operator_warnings: tuple[str, ...] = ()


def _ineligible(
    status: Literal["degraded", "unavailable"], loss: str
) -> PromiseObjectiveResolution:
    return PromiseObjectiveResolution(status=status, known_losses=(loss,))


def _read_authority(path: Path) -> tuple[bytes, dict]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PromiseObjectiveResolutionError(f"ratified-los.json unreadable: {exc}") from exc
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PromiseObjectiveResolutionError("ratified-los.json malformed JSON") from exc
    if not isinstance(payload, dict):
        raise PromiseObjectiveResolutionError("ratified-los.json root must be an object")
    rows = payload.get("ratified_los")
    if not isinstance(rows, list):
        raise PromiseObjectiveResolutionError("ratified_los must be a list")
    return raw, payload


def resolve_promise_objectives(
    run_dir: Path,
    *,
    lesson_plan_loader: Callable[[Path], dict | None] = lesson_plan_from_run,
) -> PromiseObjectiveResolution:
    """Resolve exact operator authority while treating Irene only as lineage."""
    run_dir = Path(run_dir)
    path = run_dir / "ratified-los.json"
    if path.is_file():
        raw, payload = _read_authority(path)
        plan = lesson_plan_loader(run_dir)
    else:
        plan = lesson_plan_loader(run_dir)
        if path.is_file():
            raw, payload = _read_authority(path)
        else:
            if not isinstance(plan, dict):
                return _ineligible("unavailable", "promise_lesson_plan_lineage_absent")
            return _ineligible("unavailable", "promise_ratified_los_absent")
    if not isinstance(plan, dict):
        return _ineligible("unavailable", "promise_lesson_plan_lineage_absent")
    rows = payload["ratified_los"]
    if not rows:
        return _ineligible("unavailable", "promise_ratified_los_empty")
    provenance = plan.get("planning_provenance")
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    if (
        not isinstance(provenance, dict)
        or provenance.get("ratified_los_path") != "ratified-los.json"
        or provenance.get("ratified_los_digest") != digest
    ):
        return _ineligible("degraded", "promise_ratified_lo_lineage_unverified")

    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise PromiseObjectiveResolutionError(f"ratified_los[{index}] must be an object")
        oid, statement = row.get("objective_id"), row.get("statement")
        if (
            not isinstance(oid, str)
            or not _OPEN_ID.fullmatch(oid)
            or not isinstance(statement, str)
            or not statement.strip()
        ):
            raise PromiseObjectiveResolutionError(
                f"ratified_los[{index}] has invalid objective_id/statement"
            )
        if oid in seen:
            raise PromiseObjectiveResolutionError(f"duplicate objective_id: {oid}")
        seen.add(oid)

    classified: list[
        tuple[
            Literal["canonical_g0r", "plan_dialogue", "unratified", "dialogue_unproven"],
            LearningObjective | None,
        ]
    ] = []
    warnings: list[str] = []
    for index, row in enumerate(rows):
        assert isinstance(row, dict)  # proven by the fail-loud structural pass
        oid, statement = row.get("objective_id"), row.get("statement")
        assert isinstance(oid, str) and isinstance(statement, str)
        status = row.get("status")
        if status != "ratified":
            classified.append(("unratified", None))
            continue
        has_dialogue_evidence = "actor" in row or "source" in row
        if has_dialogue_evidence:
            if row.get("actor") != "operator" or row.get("source") != "plan-dialogue":
                classified.append(("dialogue_unproven", None))
                continue
            allowed = {"objective_id", "statement", "status", "actor", "source", "bloom_level"}
            if set(row) != allowed or row.get("bloom_level") != "":
                raise PromiseObjectiveResolutionError(
                    f"ratified_los[{index}] invalid plan-dialogue shape"
                )
            classified.append(("plan_dialogue", None))
        else:
            try:
                canonical = LearningObjective.model_validate_json(json.dumps(row), strict=True)
            except ValidationError as exc:
                raise PromiseObjectiveResolutionError(
                    f"ratified_los[{index}] invalid canonical ratified objective"
                ) from exc
            classified.append(("canonical_g0r", canonical))
            if canonical.adequacy and canonical.adequacy.verdict in ("thin", "gap"):
                warnings.append("promise_source_adequacy_operator_check")

    classifications = tuple(item[0] for item in classified)
    if "dialogue_unproven" in classifications:
        return _ineligible("degraded", "promise_plan_dialogue_authority_unproven")
    if "unratified" in classifications:
        return _ineligible("degraded", "promise_plan_not_ratified")

    objectives: list[ObjectiveInput] = []
    variants: list[Literal["canonical_g0r", "plan_dialogue"]] = []
    refs: list[str] = []
    for index, (row, classification) in enumerate(zip(rows, classifications, strict=True)):
        assert isinstance(row, dict)
        oid, statement = row["objective_id"], row["statement"]
        objectives.append(ObjectiveInput(objective_id=oid, text=statement, status="ratified"))
        assert classification in ("canonical_g0r", "plan_dialogue")
        variants.append(classification)
        refs.append(f"ratified-los.json#ratified_los/{index}")
    return PromiseObjectiveResolution(
        status="authored",
        objectives=tuple(objectives),
        authority_variants=tuple(variants),
        authority_refs=tuple(refs),
        operator_warnings=tuple(dict.fromkeys(warnings)),
    )


def _normalized(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text).casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in folded).split())


def _digits(text: str) -> Counter[str]:
    return Counter(re.findall(r"(?<!\w)\d+(?:[.,]\d+)*(?!\w)", unicodedata.normalize("NFKC", text)))


def _spoiler(vow: str, span: str) -> bool:
    a, b = _normalized(vow), _normalized(span)
    if not b:
        return False
    if b in a:
        return True
    stop = {"the", "and", "that", "this", "with", "from", "into", "your", "their", "then", "than"}
    span_tokens = {token for token in b.split() if token not in stop}
    if not span_tokens:
        return False
    shared = span_tokens & {token for token in a.split() if token not in stop}
    return len(shared) >= 4 and len(shared) / len(span_tokens) >= 0.80


def _failed(
    losses: tuple[str, ...], refs: tuple[str, ...], warnings: tuple[str, ...]
) -> PromiseProjectionResult:
    return PromiseProjectionResult(
        projection=PromiseProjection(
            status="degraded", vows=(), known_losses=losses, marker=PROMISE_MARKER
        ),
        gate_receipt=PromiseGateReceipt(failures=losses),
        authority_refs=refs,
        operator_warnings=warnings,
    )


def compose_promise_projection(
    request: PromiseProjectionRequest, transformer: PromiseTransformer
) -> PromiseProjectionResult:
    """Apply pre-gates, call the injected transformer once, then fail all-or-nothing."""
    resolution = request.resolution
    warnings = tuple(dict.fromkeys((*resolution.operator_warnings, *_BASE_WARNINGS)))
    if resolution.status != "authored":
        projection = PromiseProjection(
            status=resolution.status,
            vows=(),
            known_losses=resolution.known_losses,
            marker=PROMISE_MARKER,
        )
        return PromiseProjectionResult(
            projection=projection,
            gate_receipt=PromiseGateReceipt(failures=resolution.known_losses),
            operator_warnings=warnings,
        )
    formed = PromiseTransformRequest(
        objectives=resolution.objectives,
        scene_context=request.scene_context,
        friction_context=request.friction_context,
        transformation_posture="pertinent_ability_first_move",
    )
    transformed_raw = transformer(formed)
    if not isinstance(transformed_raw, PromiseProjection):
        return _failed(
            ("promise_transformer_contract_invalid",), resolution.authority_refs, warnings
        )
    try:
        raw_vows = transformed_raw.vows
        if not isinstance(raw_vows, tuple) or any(
            not isinstance(vow, PromiseVow) for vow in raw_vows
        ):
            raise ValueError("Promise vows must be validated PromiseVow instances")
        transformed = PromiseProjection.model_validate(
            transformed_raw.model_dump(mode="python"), strict=True
        )
    except (ValidationError, TypeError, ValueError, AttributeError):
        return _failed(
            ("promise_transformer_contract_invalid",), resolution.authority_refs, warnings
        )
    if transformed.status != "authored":
        return _failed(
            ("promise_transformer_contract_invalid",), resolution.authority_refs, warnings
        )
    expected = tuple(o.objective_id for o in resolution.objectives)
    actual = tuple(v.objective_id for v in transformed.vows)
    if actual != expected:
        return _failed(("promise_objective_mapping_invalid",), resolution.authority_refs, warnings)
    failures: list[str] = []
    reserved = {"scene", "friction scale", "promise"}
    for objective, vow in zip(resolution.objectives, transformed.vows, strict=True):
        normalized = _normalized(vow.text)
        if "unresolved" in normalized.split():
            failures.append("promise_unresolved_placeholder")
        reserved_label = re.match(
            r"^\s*(?:#{1,6}\s*)?(?:scene|friction\s+scale|promise)\s*(?:[:—–-]|$)",
            unicodedata.normalize("NFKC", vow.text).casefold(),
        )
        if (
            vow.text.lstrip().startswith(("-", "*", "+", "#", ">"))
            or re.match(r"^\s*\d+[.)]\s", vow.text)
            or normalized in reserved
            or reserved_label
            or any(separator in vow.text for separator in ("\n", "\r", "\u2028", "\u2029"))
        ):
            failures.append("promise_vow_structure_invalid")
        if _digits(objective.text) != _digits(vow.text):
            failures.append("promise_numeral_mismatch")
    if failures:
        return _failed(tuple(dict.fromkeys(failures)), resolution.authority_refs, warnings)
    if any(
        _spoiler(v.text, span)
        for v in transformed.vows
        for span in request.forbidden_resolution_spans
    ):
        warnings = tuple(dict.fromkeys((*warnings, "promise_spoiler_heuristic_match")))
    return PromiseProjectionResult(
        projection=transformed,
        gate_receipt=PromiseGateReceipt(),
        authority_refs=resolution.authority_refs,
        operator_warnings=warnings,
    )


__all__ = [
    "PROMISE_MARKER",
    "PromiseGateReceipt",
    "PromiseObjectiveResolution",
    "PromiseObjectiveResolutionError",
    "PromiseProjectionRequest",
    "PromiseProjectionResult",
    "compose_promise_projection",
    "resolve_promise_objectives",
]
