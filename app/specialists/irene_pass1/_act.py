"""Irene Pass-1 lesson-plan coauthoring implementation."""

from __future__ import annotations

import hashlib
import inspect
import json
import logging
import os
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.collateral_spec import CollateralSpec
from app.marcus.lesson_plan.pass1_authority import (
    LEGACY_SCHEMA_VERSION,
    Pass1PlanAuthorityError,
    finalize_plan_authority,
)
from app.marcus.lesson_plan.pass1_authority import (
    assert_receipt_matches_plan as _assert_receipt_matches_plan,
)
from app.marcus.lesson_plan.pass1_authority import (
    assert_unique_plan_unit_ids as _assert_unique_plan_unit_ids,
)
from app.marcus.lesson_plan.pass1_call_journal import (
    Pass1CallJournalError,
    begin_or_resume_pass1_call,
    build_pass1_call_identity,
    complete_pass1_call,
    record_pass1_candidate_processing,
    record_pass1_dispatch_exception,
    record_pass1_response,
    response_provider_evidence,
)
from app.marcus.lesson_plan.pass1_source_span_catalog import (
    Pass1SourceSpanCatalogError,
    Pass1SourceSpanCatalogV1,
    build_pass1_source_span_catalog,
    project_pass1_source_ref_ids,
)
from app.models.pass1_source_section import Pass1AuthenticatedSourceSection
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState
from app.pass1_generation_lock import (
    Pass1GenerationLockError,
    pass1_generation_lock,
)
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary.styleguide_library import SCRIPTED_ENUM_CLASSES
from app.specialists.irene_pass1.cluster_floor import (
    ClusterFloorMismatchError,
    assert_floor_consulted,
    consume_min_cluster_floor,
)
from app.specialists.source_bundle import (
    read_extracted_source_with_sections,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"
REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-content-creator" / "references"
PASS_1_REFERENCES = (
    "cluster-planning.md",
    "cluster-decision-criteria.md",
    "cluster-narrative-arc-schema.md",
    "cluster-density-controls.md",
    "content-sequencing.md",
    "learning-objective-decomposition.md",
    "pedagogical-framework.md",
    "retrieval-intake-contract.md",
    "template-lesson-plan.md",
)

# Story 1.1: canonical cluster literals (mirror the Pass-2 template's
# ClusterRole / ClusterPosition Literal sets and the narrative-arc-schema's
# develop_type / master_behavioral_intent vocab). Kept as plain tuples to keep
# _act.py's import surface minimal (no heavy pydantic imports here).
CLUSTER_ROLES = ("head", "interstitial")
CLUSTER_POSITIONS = ("establish", "tension", "develop", "resolve")
DEVELOP_TYPES = ("deepen", "reframe", "exemplify")
MASTER_BEHAVIORAL_INTENTS = (
    "credible",
    "alarming",
    "provocative",
    "reflective",
    "moving",
    "clear-guidance",
    "attention-reset",
)
PASS_1_SYSTEM_MESSAGE = (
    "You are Irene Pass-1. Coauthor a lesson plan, slide-scope outline, and "
    "per-plan-unit ratification surface. Return strict JSON with key plan_units."
)
PASS1_MODES = {"pass-1", "irene-pass1", "irene_pass1"}
PASS2_MODES = {"pass-2", "irene-pass2", "irene_pass2"}

# Leg-C R3 AC#15 (D-0): scripted-derived payload keys the deterministic post-hoc
# honoring reads but the LLM must NEVER see. Keyed off the scripted NAMESPACE
# (the sealed registry in the CD-owned styleguide spine), never a hand-list —
# a future 2nd scripted class is auto-hidden. The FULL payload stays available
# post-hoc.
#
# D-3 byte-identity, honestly scoped (R3 remediation): with the strip + the
# floor-annotation scrub below, the model input is BYTE-IDENTICAL with and
# without a bound floor for the CREATION pass and for any pass given IDENTICAL
# incoming plans ("never re-parameterize the LLM clustering objective"). A
# refinement pass whose incoming plan was itself reshaped by honoring
# legitimately sees the honored plan — the extra clusters (minted ``#f`` ids
# included) are real downstream plan state, NOT a leak; only the floor-ENGINE-
# OWNED provenance key (``floor_subdivision_index``) is scrubbed from the
# model-visible copy so the model cannot fingerprint that a floor ran.
_LLM_HIDDEN_PAYLOAD_KEYS: frozenset[str] = frozenset(SCRIPTED_ENUM_CLASSES)

# R3 (Blind#1): floor-engine-owned plan_unit annotation keys scrubbed
# (recursively, targeted key removal) from the model-visible payload copy.
# Kept in the FULL payload + the persisted plan (provenance for the arbiter).
_FLOOR_ENGINE_ANNOTATION_KEYS: frozenset[str] = frozenset({"floor_subdivision_index"})


def _scrub_floor_annotations(value: Any) -> Any:
    """Recursively remove ``_FLOOR_ENGINE_ANNOTATION_KEYS`` from a JSON-shaped
    structure (pure: returns copies, never mutates the input)."""
    if isinstance(value, dict):
        return {
            k: _scrub_floor_annotations(v)
            for k, v in value.items()
            if k not in _FLOOR_ENGINE_ANNOTATION_KEYS
        }
    if isinstance(value, list):
        return [_scrub_floor_annotations(item) for item in value]
    return value


def _scrub_projected_source_refs(value: Any) -> Any:
    """Hide deterministic literal projections from refinement model input."""
    if isinstance(value, dict):
        result = {key: _scrub_projected_source_refs(item) for key, item in value.items()}
        units = result.get("plan_units")
        if isinstance(units, list):
            result["plan_units"] = [
                {key: item for key, item in unit.items() if key != "source_refs"}
                if isinstance(unit, dict)
                else unit
                for unit in units
            ]
        return result
    if isinstance(value, list):
        return [_scrub_projected_source_refs(item) for item in value]
    return value


class ModeMismatchError(SpecialistDispatchError):
    """Raised when Pass-1 receives a Pass-2 envelope.

    Re-based onto SpecialistDispatchError (BETA S0.1 crash-taxonomy guard
    2026-06-19) so a mode mismatch error-pauses recoverably instead of crashing
    the walk (sibling of the quinn_r 07B Trial-4 crash). Stays RuntimeError-derived.
    """

    def __init__(self, message: str, *, tag: str = "irene_pass1.mode.unresolved") -> None:
        SpecialistDispatchError.__init__(self, message, tag=tag)


class BulkRatificationError(RuntimeError):
    """Raised when an operator attempts one verdict for all plan units."""


class PlanUnitRatificationError(RuntimeError):
    """Raised when per-plan-unit ratification is incomplete or invalid."""


class Pass1AuthorityError(SpecialistDispatchError):
    """A Pass-1 plan violated durable identity or literal source authority."""

    def __init__(self, message: str) -> None:
        super().__init__(message, tag="irene-pass1.authority-invalid")


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


class _DuplicateJsonKeyError(ValueError):
    pass


class _InvalidJsonConstantError(ValueError):
    pass


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise _InvalidJsonConstantError(f"non-standard JSON constant {value!r}")


def _effective_model_config_digest(handle: Any, *, model_id: str) -> str:
    """Bind the effective non-secret provider controls used for this call."""
    explicit = getattr(handle, "model_config_digest", None)
    if isinstance(explicit, str):
        return explicit
    chat = getattr(handle, "chat", None)
    config: dict[str, Any] = {
        "model_id": model_id,
        "chat_type": type(chat).__name__,
    }
    for field in (
        "model_name",
        "model",
        "temperature",
        "max_tokens",
        "max_retries",
        "request_timeout",
        "timeout",
        "model_kwargs",
        "disabled_params",
        "output_version",
        "reasoning_effort",
    ):
        value = getattr(chat, field, None)
        if value is not None:
            config[field] = value
    entry = getattr(handle, "entry", None)
    if hasattr(entry, "model_dump"):
        config["resolution_entry"] = entry.model_dump(mode="json")
    encoded = _json_dumps(config).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _assert_prompt_fits_context(
    *, handle: Any, model_id: str, system_msg: str, user_msg: str
) -> None:
    """Fail before dispatch using a conservative byte-token upper bound."""
    from app.models.registry_check import load_registry

    entry = next(
        (item for item in load_registry().entries if item.model_id == model_id),
        None,
    )
    if entry is None:
        # Production resolution admits only registry models. Test doubles and
        # isolated adapters may use synthetic IDs with no provider dispatch.
        return
    chat = getattr(handle, "chat", None)
    completion_ceiling = (
        getattr(chat, "max_completion_tokens", None)
        or getattr(chat, "max_tokens", None)
        or 0
    )
    if not isinstance(completion_ceiling, int) or completion_ceiling < 0:
        raise Pass1AuthorityError("Irene completion-token ceiling is invalid")
    available_input_tokens = entry.context_window - completion_ceiling
    # Provider tokenizers have byte fallbacks, so UTF-8 byte length is a safe
    # upper bound on input tokens without a provider-specific tokenizer call.
    prompt_bytes = len(system_msg.encode("utf-8")) + len(user_msg.encode("utf-8"))
    chat_framing_token_upper_bound = 1024
    if (
        available_input_tokens <= chat_framing_token_upper_bound
        or prompt_bytes + chat_framing_token_upper_bound > available_input_tokens
    ):
        raise Pass1AuthorityError("Irene prompt exceeds the resolved model context budget")


def _provider_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict) or block.get("type") not in {"text", "output_text"}:
                raise Pass1AuthorityError("Irene provider returned unsupported content blocks")
            text = block.get("text")
            if not isinstance(text, str):
                raise Pass1AuthorityError("Irene provider returned a non-text content block")
            parts.append(text)
        return "".join(parts)
    raise Pass1AuthorityError("Irene provider returned unsupported content")


def _invoke_chat_with_identity(
    chat: Any, messages: list[dict[str, str]], *, request_digest: str, node_id: str
) -> Any:
    """Attach durable correlation metadata when the chat interface supports it."""
    try:
        parameters = inspect.signature(chat.invoke).parameters.values()
    except (TypeError, ValueError):
        parameters = ()
    accepts_config = any(
        parameter.name == "config" or parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters
    )
    if accepts_config:
        return chat.invoke(
            messages,
            config={
                "metadata": {
                    "irene_request_digest": request_digest,
                    "irene_node_id": node_id,
                }
            },
        )
    return chat.invoke(messages)


def _validate_completed_replay(
    *,
    stored_result: dict[str, Any] | None,
    stored_identity: dict[str, Any] | None,
    expected_output: dict[str, Any],
    current_entries_count: int,
) -> dict[str, Any]:
    """Verify a completed receipt causally matches reprocessed raw evidence."""
    if not isinstance(stored_result, dict) or not isinstance(stored_identity, dict):
        raise Pass1AuthorityError("Irene completed-call journal is incomplete")
    if set(stored_identity) != {"plan_digest", "authority_digest", "output_digest"}:
        raise Pass1AuthorityError("Irene completed-call result identity is invalid")
    authority_receipt = expected_output["plan_authority_receipt"]
    if stored_identity.get("plan_digest") != authority_receipt.get(
        "plan_digest"
    ) or stored_identity.get("authority_digest") != authority_receipt.get("authority_digest"):
        raise Pass1AuthorityError("Irene completed-call authority changed on replay")
    if set(stored_result) != {"cache_state"}:
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay")
    cache_state = stored_result.get("cache_state")
    if (
        not isinstance(cache_state, dict)
        or set(cache_state) != {"cache_prefix", "entries_count"}
        or type(cache_state.get("entries_count")) is not int
        or cache_state["entries_count"] < 1
    ):
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay")
    prefix = cache_state.get("cache_prefix") if isinstance(cache_state, dict) else None
    try:
        output = json.loads(prefix) if isinstance(prefix, str) else None
    except json.JSONDecodeError as exc:
        raise Pass1AuthorityError("Irene completed-call output is unreadable") from exc
    if not isinstance(output, dict):
        raise Pass1AuthorityError("Irene completed-call output is invalid")
    stored_events = output.get("learning_events")
    if (
        not isinstance(stored_events, list)
        or len(stored_events) != 2
        or not all(isinstance(event, dict) for event in stored_events)
    ):
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay")
    event_timestamp = stored_events[0].get("timestamp")
    if not isinstance(event_timestamp, str) or any(
        event.get("timestamp") != event_timestamp for event in stored_events[1:]
    ):
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay")
    try:
        parsed_timestamp = datetime.fromisoformat(event_timestamp)
    except (TypeError, ValueError) as exc:
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay") from exc
    if (
        parsed_timestamp.tzinfo is None
        or parsed_timestamp.utcoffset() is None
        or parsed_timestamp.utcoffset().total_seconds() != 0
        or parsed_timestamp.isoformat() != event_timestamp
    ):
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay")
    expected_with_timestamp = {
        **expected_output,
        "learning_events": [
            {**event, "timestamp": event_timestamp}
            for event in expected_output["learning_events"]
        ],
    }
    canonical_output = _json_dumps(output)
    output_digest = "sha256:" + hashlib.sha256(canonical_output.encode("utf-8")).hexdigest()
    if (
        stored_identity.get("output_digest") != output_digest
        or prefix != canonical_output
        or canonical_output != _json_dumps(expected_with_timestamp)
    ):
        raise Pass1AuthorityError("Irene completed-call output disagrees with replay")
    return {
        "cache_state": {
            "cache_prefix": prefix,
            "entries_count": current_entries_count + 1,
        },
    }


def assert_unique_plan_unit_ids(plan: object) -> None:
    """Fail before normalization can hide a blank or duplicate model identity."""
    try:
        _assert_unique_plan_unit_ids(plan)
    except Pass1PlanAuthorityError as exc:
        raise Pass1AuthorityError(str(exc)) from exc


def validate_pass1_plan_authority(
    plan: dict[str, Any],
    *,
    source_sections: tuple[Pass1AuthenticatedSourceSection, ...],
    prior_plan: dict[str, Any] | None = None,
    prior_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate exact source authority and temporal unit identity without mutation."""
    # Compatibility for direct refinement callers that predate the cumulative
    # receipt. Production dispatch always supplies the receipt after 04A.
    if prior_receipt is None and prior_plan is not None:
        try:
            prior_receipt = finalize_plan_authority(prior_plan, source_sections=source_sections)
        except Pass1PlanAuthorityError as exc:
            raise Pass1AuthorityError(str(exc)) from exc
    elif prior_receipt is not None and prior_plan is not None:
        try:
            _assert_receipt_matches_plan(prior_plan, prior_receipt)
        except Pass1PlanAuthorityError as exc:
            raise Pass1AuthorityError(str(exc)) from exc
        if prior_receipt.get("schema_version") == LEGACY_SCHEMA_VERSION:
            raise Pass1AuthorityError(
                "legacy-v1 Pass-1 authority is read-only; start an explicit fresh "
                "Pass-1 generation instead of silently upgrading a refinement"
            )
    try:
        return finalize_plan_authority(
            plan,
            source_sections=source_sections,
            prior_receipt=prior_receipt,
        )
    except Pass1PlanAuthorityError as exc:
        raise Pass1AuthorityError(str(exc)) from exc


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(
            state.cache_state.cache_prefix,
            object_pairs_hook=_unique_json_object,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("irene_pass1 cache_prefix must be valid JSON") from exc
    if not isinstance(decoded, dict):
        raise ValueError("irene_pass1 cache_prefix must decode to a mapping")
    return decoded


def enforce_pass1_mode(payload: dict[str, Any]) -> None:
    mode = payload.get("mode") or payload.get("pass_phase") or payload.get("irene_mode")
    if mode is None:
        return
    normalized = str(mode).strip().lower()
    if normalized in PASS2_MODES:
        raise ModeMismatchError("Irene Pass-1 cannot run a Pass-2 envelope")
    if normalized not in PASS1_MODES:
        raise ModeMismatchError(f"Irene Pass-1 received unsupported mode {mode!r}")


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows = []
    for path in sorted(sanctum_dir.rglob("*"), key=lambda p: p.relative_to(sanctum_dir).as_posix()):
        if path.is_file():
            rel = path.relative_to(sanctum_dir).as_posix()
            rows.append(f"{rel}\t{hashlib.sha256(path.read_bytes()).hexdigest()}")
    return "\n".join(rows)


def read_references(references_dir: Path = REFERENCES_DIR) -> str:
    parts = []
    for name in PASS_1_REFERENCES:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    return "\n\n".join(parts)


_PLANNING_CONTEXT_SECTION_MARKER = "## Operator planning context (FRAMING ONLY — not corpus)"


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _build_planning_provenance(
    *,
    context: Any,
    receipt_lo_status: str,
    run_dir: Path | None,
) -> dict[str, Any] | None:
    """Additive lesson_plan provenance pointers (Claim B SUCCESS definition).

    Digests match companion files under ``run_dir`` when present. Omit entirely
    when no planning context was consumed (caller gates that).
    """
    if run_dir is None:
        # Still emit path names from context.sources_present without digests.
        sources = list(getattr(context, "sources_present", ()) or ())
        ratification_path = (
            "planning-ratification.json" if "planning-ratification.json" in sources else None
        )
        los_path = "ratified-los.json" if "ratified-los.json" in sources else None
        return {
            "schema_version": "0.1",
            "ratification_path": ratification_path,
            "ratification_digest": None,
            "ratified_los_path": los_path,
            "ratified_los_digest": None,
            "intent_path": ("ratified-collateral-intent.yaml" if ratification_path else None),
            "intent_digest": None,
            "coverage_lo_status": receipt_lo_status,
        }
    rat_path = run_dir / "planning-ratification.json"
    los_path = run_dir / "ratified-los.json"
    intent_path = run_dir / "ratified-collateral-intent.yaml"
    return {
        "schema_version": "0.1",
        "ratification_path": ("planning-ratification.json" if rat_path.is_file() else None),
        "ratification_digest": _sha256_file(rat_path),
        "ratified_los_path": "ratified-los.json" if los_path.is_file() else None,
        "ratified_los_digest": _sha256_file(los_path),
        "intent_path": ("ratified-collateral-intent.yaml" if intent_path.is_file() else None),
        "intent_digest": _sha256_file(intent_path),
        "coverage_lo_status": receipt_lo_status,
    }


def _planning_context_section(payload: dict[str, Any]) -> str:
    """Labeled advisory framing section; empty string when context absent."""
    raw = payload.get("planning_context")
    if not isinstance(raw, dict) or not raw:
        return ""
    purpose = str(raw.get("purpose") or "").strip()
    audience = str(raw.get("audience") or "").strip()
    los = raw.get("learning_objectives")
    lo_lines: list[str] = []
    if isinstance(los, list):
        for item in los:
            if not isinstance(item, dict):
                continue
            statement = str(item.get("statement") or "").strip()
            if not statement:
                continue
            oid = str(item.get("objective_id") or "").strip()
            prefix = f"- [{oid}] " if oid else "- "
            lo_lines.append(f"{prefix}{statement}")
    assessment = raw.get("source_assessment")
    assessment_line = ""
    if isinstance(assessment, dict):
        richness = assessment.get("richness", "")
        tags = assessment.get("tags") or []
        assessment_line = f"- Source assessment richness: {richness}; tags: {tags}\n"
    return (
        f"{_PLANNING_CONTEXT_SECTION_MARKER}\n\n"
        "This block is operator/elicited FRAMING (purpose, audience, LOs, "
        "source assessment). It must NOT replace or invent topic content. "
        "The source corpus above remains the ONLY topic/source-of-truth. "
        "Use this framing to emphasize, sequence, and align learning "
        "objectives — never as a substitute corpus.\n\n"
        f"- Purpose: {purpose or '(none)'}\n"
        f"- Audience: {audience or '(none)'}\n"
        f"{assessment_line}"
        "- Learning objectives:\n" + ("\n".join(lo_lines) if lo_lines else "- (none)\n") + "\n"
    )


def assemble_pass1_prompt(
    payload: dict[str, Any],
    *,
    extracted_source: str | None,
    source_span_catalog: Pass1SourceSpanCatalogV1 | None = None,
) -> tuple[str, str]:
    upstream = payload.get("upstream_output")
    is_refinement = isinstance(upstream, dict) and isinstance(upstream.get("lesson_plan"), dict)
    # Trial-3 cycle-2 content-plane fix (2026-06-12): the prompt previously
    # carried only bundle METADATA (the quarantined 04A edge) — no corpus
    # text — and Pass-1 confabulated a lesson plan from the reference docs'
    # domain. At plan CREATION (§04A) the extracted source leads the prompt
    # and is the only planning basis. At refinement passes (§05/§05B) the
    # prior corpus-grounded plan arrives in the payload AND the corpus is
    # STILL projected alongside it — manifest nodes 05/05B declare the same
    # `dependency_projections.bundle_reference: {from: texas}` corpus
    # projection as 04A (state/config/pipeline-manifest.yaml:411-414 and
    # :429-435, dp-v1) — so `extracted_source` is non-None at refinement too
    # (R1 remediation: the earlier "corpus omitted at refinement" framing
    # from the cycle-3 error-pause predates dp-v1 and was wrong against the
    # current manifest). The `extracted_source is None` branch below is a
    # DEGRADED defensive fallback for a corpus-delivery regression, not the
    # production 05/05B shape.
    corpus_section = (
        "## Source corpus (extracted) — the ONLY planning basis\n\n"
        "Plan ONLY from the source corpus below. Reference material further "
        "down informs FORM (unit structure, scope discipline), never TOPIC.\n\n"
        f"{extracted_source}\n\n"
        if extracted_source is not None
        else "## Refinement pass — the prior corpus-grounded lesson plan in "
        "the envelope payload below is the planning basis; stay on ITS "
        "topic.\n\n"
    )
    planning_section = _planning_context_section(payload)
    catalog_section = (
        "## Exact source-span selection catalog\n\n"
        "Select only the stable span_id values below. Deterministic code will "
        "project each selected ID to the exact literal source bytes; never "
        "author, repair, paraphrase, or fuzzy-match authority text.\n\n"
        f"```json\n{_json_dumps(source_span_catalog.model_dump(mode='json'))}\n```\n\n"
        if source_span_catalog is not None
        else "## Exact source-span selection catalog\n\n"
        "No catalog was supplied; this prompt is non-executable.\n\n"
    )
    # Leg-C R3 AC#15 (D-0 strip): scripted-derived keys never reach the model's
    # view of the payload; the caller's payload dict is untouched (post-hoc
    # consumers read the floor from the FULL payload). R3 remediation: the
    # floor-engine-owned annotation key is additionally scrubbed recursively
    # (a prior floored plan riding upstream_output.lesson_plan.plan_units must
    # not fingerprint the honoring to the model; the plan's minted clusters
    # themselves stay visible — they ARE the plan).
    #
    # Planning-context handoff (BH-4): scrub planning_context from the envelope
    # JSON dump — the labeled section above is the ONLY model-facing framing
    # surface. Full payload still carries the key for receipt/audit consumers.
    model_visible_payload = _scrub_projected_source_refs(
        _scrub_floor_annotations(
            {
                k: v
                for k, v in payload.items()
                if k not in _LLM_HIDDEN_PAYLOAD_KEYS and k != "planning_context"
            }
        )
    )
    return (
        PASS_1_SYSTEM_MESSAGE,
        f"{corpus_section}"
        f"{planning_section}"
        f"{catalog_section}"
        "## Sanctum digest\n\n"
        f"{read_sanctum_digest()}\n\n"
        "## Irene Pass-1 references\n\n"
        f"{read_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{_json_dumps(model_visible_payload)}\n```\n\n"
        f"{_cluster_emission_instructions(refinement=is_refinement)}\n\n"
        f"{_fidelity_emission_instructions()}\n\n"
        f"{_collateral_emission_instructions()}",
    )


def _cluster_emission_instructions(*, refinement: bool = False) -> str:
    """Story 1.1: the additive cluster-emission contract + decision guidance.

    Requests the per-plan-unit cluster fields and embeds the chunk-by-default /
    keep-dense-singleton routing from cluster-decision-criteria.md (CD) and the
    narrative-arc vocab from cluster-narrative-arc-schema.md (NA). The detailed
    reference bodies are loaded above; this block is the actionable instruction.
    """
    refinement_contract = (
        "\n\n## Durable identity contract for this refinement\n"
        "The incoming lesson plan and prior_plan_authority_receipt are binding. "
        "For every retained unit_id, copy source_ref_ids (including order), "
        "cluster_role, and parent_slide_id EXACTLY unchanged. Title, rationale, "
        "objective wording, fidelity, and other non-identity fields may change. "
        "If consolidation or restructuring changes any identity field, REMOVE "
        "the old unit and mint a NEW unit_id that appears nowhere in the receipt "
        "(active or retired). A removed ID is retired forever and must never be "
        "reassigned. Never renumber, recycle, repair, trim, paraphrase, reorder, "
        "drop, or restore identity selections. New-unit source_ref_ids must "
        "select exact spans from one source slide in the supplied catalog.\n"
        if refinement
        else ""
    )
    return (
        'Return JSON: {"plan_units":[{\n'
        '  "unit_id":"...","title":"...","learning_objective":"...",\n'
        '  "scope_decision":"in-scope|out-of-scope","rationale":"...",\n'
        '  "cluster_id":"c-uNN",                 // every unit belongs to a '
        "cluster; singleton = its own\n"
        '  "cluster_role":"head|interstitial",\n'
        '  "cluster_position":"establish|tension|develop|resolve",\n'
        '  "narrative_arc":"From <start> to <end> through <mechanism>", '
        "// on head; inherited by members\n"
        '  "master_behavioral_intent":"credible|alarming|provocative|reflective|'
        'moving|clear-guidance|attention-reset", // on head\n'
        '  "develop_type":"deepen|reframe|exemplify|null", '
        "// develop-position interstitials only\n"
        '  "parent_slide_id":"<head unit_id>",   // interstitials only\n'
        '  "cluster_interstitial_count":<int>,     // on head (0 for a '
        "singleton/keep-dense unit)\n"
        '  "source_ref_ids":["span:sha256:<64-lower-hex>", ...] '
        "// 1-6 ordered catalog selections per unit\n"
        '}],"lesson_summary":"..."}.\n\n'
        "## Cluster decision guidance (apply the CD framework)\n"
        "- Chunk by DEFAULT a dense unit (3+ explanatory beats / high "
        "concept-density or visual-complexity or pedagogical-weight) into a "
        "head + N interstitials (N=1-3) under one shared narrative_arc, beats "
        "ordered establish -> tension -> develop -> resolve. Each interstitial "
        "is its own plan_unit with cluster_role:interstitial, "
        "parent_slide_id=head, same cluster_id.\n"
        "- KEEP DENSE (singleton, never chunk a gestalt): synthesis / "
        "big-picture / comparison (two-up) / diagram-driven / before-after / "
        "the resolve/takeaway slide whose value IS the simultaneous whole. "
        "Emit ONE plan_unit, cluster_role:head, cluster_position:establish, "
        "cluster_interstitial_count:0. keep-dense is an INPUT to the decision, "
        "never a veto applied after.\n"
        "- Singletons still carry a cluster_id (degenerate size-1 cluster).\n"
        '- SOURCE ANCHORS: every in-scope plan_unit carries "source_ref_ids" '
        "— 1-6 ordered IDs copied exactly from the supplied catalog. Select "
        "only IDs whose displayed exact text cites the passages this unit "
        "plans, and keep every unit's selections within one source slide. "
        "Never emit source_refs, free-text quotes, guessed IDs, fuzzy matches, "
        "or repaired/paraphrased authority. Anchors cite planning work already "
        "done; they never introduce new structure."
        f"{refinement_contract}"
    )


RECOGNIZED_FIDELITY = frozenset({"creative", "literal-text", "literal-visual"})
_FIDELITY_ALIASES: dict[str, str] = {
    "literal_text": "literal-text",
    "literal-text": "literal-text",
    "literal_visual": "literal-visual",
    "literal-visual": "literal-visual",
    "literal-image": "literal-visual",
    "literal_image": "literal-visual",
    "creative": "creative",
}


def _fidelity_emission_instructions() -> str:
    """Restore per-plan-unit fidelity classification (pre-migration Pass-1 contract).

    Sibling of :func:`_cluster_emission_instructions`. Requests ``fidelity`` on
    each plan_unit so Gary's literal-cohort preserve path can fire. Classification
    covers both literal-text and literal-visual; production streamlining for
    literal-visual images is a separate follow-on.
    """
    return (
        "## Per-unit fidelity classification (additive on each plan_unit)\n"
        'ALSO emit "fidelity" on EVERY plan_unit — exactly one of:\n'
        "  creative | literal-text | literal-visual\n"
        "Default is creative. Do not over-tag — most units should be creative.\n"
        "- literal-text: exact text/data must appear as written (assessment topic "
        "lists, tested statistics, accreditation terminology, dosage tables).\n"
        "- literal-visual: a specific SME-provided image/diagram must be faithfully "
        "placed (labeled charts, clinical flowcharts, framework diagrams). Tag "
        "classification only; do not invent image URLs.\n"
        "- creative: content may be enhanced by Gamma (default).\n"
        'If the envelope payload carries "fidelity_guidance", HONOR it for the '
        "named items (user guidance supplements your judgment; it does not replace "
        "independent literal needs you identify). At a refinement pass, CARRY "
        "recognized fidelity tags FORWARD from the incoming plan_units unless you "
        "deliberately reclassify."
    )


def _collateral_emission_instructions() -> str:
    """Braid S1: the additive collateral content-model emission contract (DP4).

    Sibling of :func:`_cluster_emission_instructions`. Requests a WORKBOOK
    CONTENT MODEL + a research-enrichment goals block on a top-level
    ``collateral`` key, alongside (never replacing) the plan_units / cluster
    emission. The empty case is the explicit ``declaration:"none"`` decision —
    a decision on record, not an absent key. The shapes mirror
    ``app/marcus/lesson_plan/collateral_spec.py`` (the single source of truth).
    """
    return (
        "## Workbook collateral content model (additive top-level key)\n"
        'ALSO return a top-level "collateral" object — the spec the client\'s '
        "workbook is built from. It is the read-in-depth dual-coding partner to "
        "the glance-deck: it carries the depth deferred OFF the slides so the "
        "slide voiceover can stay tight. Shape:\n"
        '{"collateral":{\n'
        '  "declaration":"present|none", // "none" = on-record decision to '
        "ship deck-only (NOT an omitted key)\n"
        '  "workbook":{ // present iff declaration=="present"\n'
        '    "sections":[{\n'
        '      "section_id":"sec-...",\n'
        '      "learning_objective_id":"<a real plan_unit id>", // REQUIRED; '
        "binds the section to a learning objective\n"
        '      "title":"...",\n'
        '      "depth_delta":{ // REQUIRED; what depth moves off the slide\n'
        '        "deferred_from_slide":"<plan_unit id>",\n'
        '        "deferred_depth":"<what depth the workbook carries>",\n'
        '        "retained_on_slide":"<what stays at glance altitude>" // optional\n'
        "      },\n"
        '      "exercises":[{ // may be empty for a pure-narrative section\n'
        '        "exercise_id":"ex-...",\n'
        '        "bloom_level":"remember|understand|apply|analyze|evaluate|create",\n'
        '        "prompt_intent":"<pedagogical intent, not the worked prompt>",\n'
        '        "answer_key_source_ref":"<a source reference slot>" // grounded; '
        "not a fabricated citation\n"
        "      }],\n"
        '      "narrative_intent":"<the fuller-narrative brief>"\n'
        "    }]\n"
        "  },\n"
        '  "research_goals":[{ // pedagogical INTENT, never a raw fetch query/URL\n'
        '    "goal_id":"rg-...",\n'
        '    "pedagogical_intent":"learner needs the primary-source basis for '
        'the 23% figure",\n'
        '    "binds_to_objective_id":"<objective id>" // optional\n'
        "  }]\n"
        "}}.\n"
        "- Express research as pedagogical INTENT, not a search query — the "
        "research wiring translates intent to fetch downstream.\n"
        "- If the lesson genuinely ships deck-only, emit "
        '{"collateral":{"declaration":"none"}} explicitly.'
    )


def _singleton_cluster_id(unit_id: str) -> str:
    """Derive a deterministic degenerate size-1 cluster id from a unit id."""
    base = str(unit_id).strip() or "unit"
    return base if base.startswith("c-") else f"c-{base}"


def normalize_clusters(plan: dict[str, Any]) -> dict[str, Any]:
    """Pure post-parse backstop that makes cluster structure downstream-valid.

    Story 1.1 (Scope item 3). PURE: returns a new dict, never mutates the input.
    LLM cluster output is variance-prone; this guarantees every plan_unit carries
    a well-formed cluster shape regardless of model sloppiness:

    PARENT LINKAGE IS AUTHORITATIVE. An interstitial's cluster membership is
    decided by its head (resolved via parent_slide_id, or — when the model
    omits it — by a matching head cluster_id), and the interstitial's cluster_id
    + narrative_arc are then derived FROM that head. This keeps the three keyed
    operations (count, arc inheritance, grouping) mutually consistent instead of
    trusting three independently-sloppy model fields (T11 code-review root-cause
    fix: cluster_id-vs-parent_slide_id key confusion, Blind+Edge MAJOR).

    Guarantees regardless of model sloppiness:
    - roles coerced FIRST (invalid -> head) so the head set reflects normalized
      roles, not raw/mis-cased values
    - every unit gets a UNIQUE cluster_id; missing/blank/duplicate unit_ids use
      an index-stable synthetic key so distinct units never collapse into one
      cluster; duplicate head cluster_ids are split
    - an interstitial with no resolvable head -> demoted to its own singleton
      head (no orphans reach Gary); a resolved interstitial inherits its head's
      cluster_id + narrative_arc
    - head cluster_position defaults to "establish" (the arc anchor); an
      interstitial's missing/invalid position -> None (never force "establish")
    - invalid develop_type / master_behavioral_intent -> None (tolerance)
    - cluster_interstitial_count recomputed on each head from actual members
    - pure (no input mutation), idempotent, never crashes
    """
    if not isinstance(plan, dict):
        return {"plan_units": []}
    raw_units = plan.get("plan_units")
    if not isinstance(raw_units, list):
        return {**plan, "plan_units": []}

    # Work on copies so the function is pure (no input mutation).
    units: list[dict[str, Any]] = [dict(u) if isinstance(u, dict) else {} for u in raw_units]

    def _uid(unit: dict[str, Any], idx: int) -> str:
        value = unit.get("unit_id")
        text = str(value).strip() if value is not None else ""
        return text or f"u{idx}"

    # Pass 1: coerce roles up front so the head set is built from normalized
    # roles (a mis-cased "Head" no longer orphans its real interstitials).
    for unit in units:
        role = unit.get("cluster_role")
        unit["cluster_role"] = role if role in CLUSTER_ROLES else "head"

        dtype = unit.get("develop_type")
        if dtype is not None and dtype not in DEVELOP_TYPES:
            unit["develop_type"] = None
        mbi = unit.get("master_behavioral_intent")
        if mbi is not None and mbi not in MASTER_BEHAVIORAL_INTENTS:
            unit["master_behavioral_intent"] = None

    # Pass 2: assign each HEAD a unique cluster_id (keep the model's if present
    # and not already taken; else derive from the head's unit_id) and index
    # the heads for parent resolution.
    used_cluster_ids: set[str] = set()
    head_by_uid: dict[str, dict[str, Any]] = {}
    head_by_cluster_id: dict[str, dict[str, Any]] = {}
    head_uid_by_cluster_id: dict[str, str] = {}
    for idx, unit in enumerate(units):
        if unit["cluster_role"] != "head":
            continue
        uid = _uid(unit, idx)
        cid = unit.get("cluster_id")
        if not (isinstance(cid, str) and cid.strip() and cid not in used_cluster_ids):
            cid = _singleton_cluster_id(uid)
            suffix = 1
            while cid in used_cluster_ids:
                suffix += 1
                cid = f"{_singleton_cluster_id(uid)}-{suffix}"
        unit["cluster_id"] = cid
        used_cluster_ids.add(cid)
        head_by_uid.setdefault(uid, unit)
        head_by_cluster_id.setdefault(cid, unit)
        head_uid_by_cluster_id.setdefault(cid, uid)

    # Pass 3: resolve each interstitial to a head (parent_slide_id first, then a
    # matching head cluster_id); inherit the head's cluster_id + arc, or demote.
    for idx, unit in enumerate(units):
        if unit["cluster_role"] != "head":
            parent = unit.get("parent_slide_id")
            head = head_by_uid.get(str(parent)) if parent is not None else None
            if head is None:
                head = head_by_cluster_id.get(str(unit.get("cluster_id")))
            if head is None:
                # Orphan -> demote to its own singleton head.
                unit["cluster_role"] = "head"
                unit.pop("parent_slide_id", None)
                uid = _uid(unit, idx)
                cid = _singleton_cluster_id(uid)
                suffix = 1
                while cid in used_cluster_ids:
                    suffix += 1
                    cid = f"{_singleton_cluster_id(uid)}-{suffix}"
                unit["cluster_id"] = cid
                used_cluster_ids.add(cid)
                head_by_uid.setdefault(uid, unit)
                head_by_cluster_id.setdefault(cid, unit)
                head_uid_by_cluster_id.setdefault(cid, uid)
            else:
                # Parent-authoritative: inherit the head's cluster_id + arc.
                head_cid = head["cluster_id"]
                unit["cluster_id"] = head_cid
                unit["parent_slide_id"] = head_uid_by_cluster_id[head_cid]
                head_arc = head.get("narrative_arc")
                if not unit.get("narrative_arc") and isinstance(head_arc, str) and head_arc.strip():
                    unit["narrative_arc"] = head_arc

    # Pass 4: position semantics — head anchors at establish; interstitial
    # missing/invalid -> None (never force an interstitial to establish).
    for unit in units:
        pos = unit.get("cluster_position")
        if unit["cluster_role"] == "head":
            unit["cluster_position"] = pos if pos in CLUSTER_POSITIONS else "establish"
        elif pos is not None and pos not in CLUSTER_POSITIONS:
            unit["cluster_position"] = None

    # Pass 5: recompute cluster_interstitial_count per head from real members
    # (cluster_id is now consistent because interstitials inherited the head's).
    interstitial_counts: dict[str, int] = {}
    for unit in units:
        if unit["cluster_role"] == "interstitial":
            cid = str(unit.get("cluster_id"))
            interstitial_counts[cid] = interstitial_counts.get(cid, 0) + 1
    for unit in units:
        if unit["cluster_role"] == "head":
            cid = str(unit.get("cluster_id"))
            unit["cluster_interstitial_count"] = interstitial_counts.get(cid, 0)

    return {**plan, "plan_units": units}


def normalize_collateral(plan: dict[str, Any]) -> dict[str, Any]:
    """Pure post-parse backstop guaranteeing a well-formed ``collateral`` block.

    Braid S1 (Scope item 3). Mirrors :func:`normalize_clusters`: PURE (returns a
    new dict, never mutates the input), idempotent, never crashes. Guarantees
    ``plan["collateral"]`` validates as a :class:`CollateralSpec` shape on BOTH
    the LLM-output path and the fallback-unit path:

    - missing / non-dict / unparseable collateral -> the explicit
      ``{"declaration": "none"}`` decision-on-record (degenerate-empty), NOT an
      absent key
    - a collateral block that fails ``CollateralSpec`` validation (e.g. a
      ``declaration:"present"`` with no usable workbook, or a malformed section)
      degrades to the ``"none"`` declaration rather than crashing the walk —
      the additive/no-regression invariant holds even on sloppy model output
    - a well-formed block is canonicalized through ``CollateralSpec`` so the
      emitted block is exactly the validated shape (sorted, defaulted)

    The producer (S2) and research wiring (S3) read the validated shape; S1's
    job is to make a well-formed instance always present.

    ``CollateralSpec`` is imported at module level (the import-anchor discipline,
    mirror Amelia-a.2) so the schema family is statically reachable in the
    import graph and cannot rot as an orphan module. Marcus Contract M3 forbids
    app.specialists importing only marcus.facade / marcus.intake /
    marcus.orchestrator — not app.marcus.lesson_plan — so this edge is allowed.
    """
    none_block = {"declaration": "none"}
    if not isinstance(plan, dict):
        return {"collateral": dict(none_block)}

    raw = plan.get("collateral")
    if not isinstance(raw, dict):
        return {**plan, "collateral": dict(none_block)}

    try:
        spec = CollateralSpec.model_validate(raw)
    except Exception as exc:
        # Never-crash backstop: degrade a malformed block to the on-record
        # deck-only declaration rather than propagating a validation error.
        # FIX-1: make the degrade OBSERVABLE. A genuine declaration:"none"
        # (or absent / non-dict, handled above) is a legitimate decision and
        # must NOT warn; but a block that *intended* a workbook — declaration
        # "present" OR a non-empty workbook payload — losing the whole workbook
        # silently collapses DP4's decision-on-record distinction. Warn (once)
        # capturing the validation error before returning the none decision.
        declared_present = raw.get("declaration") == "present"
        workbook = raw.get("workbook")
        has_workbook_payload = bool(workbook) and isinstance(workbook, dict)
        if declared_present or has_workbook_payload:
            logger.warning(
                "irene-pass1 collateral degraded to declaration:'none' — a "
                "present/workbook block failed CollateralSpec validation and "
                "was dropped: %s",
                exc,
            )
        return {**plan, "collateral": dict(none_block)}

    # Canonicalize to the validated shape (mode="json" so it round-trips through
    # CacheState's JSON cache_prefix without datetime/enum surprises).
    return {**plan, "collateral": spec.model_dump(mode="json")}


def _canonicalize_fidelity(raw: Any) -> str | None:
    """Return a recognized fidelity mode, or None to omit the key."""
    if raw is None:
        return None
    if not isinstance(raw, str):
        return None
    stripped = raw.strip()
    if not stripped:
        return None
    lowered = stripped.lower()
    aliased = _FIDELITY_ALIASES.get(lowered)
    if aliased is not None:
        return aliased
    # Hyphen/underscore-normalized lookup already covered; reject unknowns.
    if lowered in RECOGNIZED_FIDELITY:
        return lowered
    return None


def normalize_fidelity(plan: dict[str, Any]) -> dict[str, Any]:
    """Pure soft-coerce for per-unit ``fidelity`` (emit-recovery backstop).

    Recognized values (and known aliases such as ``literal-image`` →
    ``literal-visual``) are kept. Missing / empty / unknown values omit the
    key — never invent a tag from prose. PURE: returns a new plan dict.
    """
    if not isinstance(plan, dict):
        return plan
    raw_units = plan.get("plan_units")
    if not isinstance(raw_units, list):
        return plan
    units: list[Any] = []
    for unit in raw_units:
        if not isinstance(unit, dict):
            units.append(unit)
            continue
        next_unit = dict(unit)
        canonical = _canonicalize_fidelity(next_unit.get("fidelity"))
        if canonical is None:
            next_unit.pop("fidelity", None)
        else:
            next_unit["fidelity"] = canonical
        units.append(next_unit)
    return {**plan, "plan_units": units}


# R7 (Edge#4): internal marker set by parse_pass1_response when the model's
# output was NOT usable structured JSON and the single synthetic fallback unit
# was substituted. act() POPS it (never persisted / never model-visible) and
# uses it to give a bound-floor mismatch on the fallback plan a DISTINCT
# llm-format-fallback diagnostic instead of the generic
# styleguide-vs-content framing.


def _validate_raw_refinement_identity(
    parsed: dict[str, Any], prior_receipt: dict[str, Any] | None
) -> None:
    """Reject immutable refinement drift before tolerant normalization can hide it."""
    if prior_receipt is None:
        return
    prior_by_id = {
        row["unit_id"]: row
        for row in prior_receipt.get("identities", [])
        if isinstance(row, dict) and row.get("active") is True
    }
    raw_units = parsed.get("plan_units")
    if not isinstance(raw_units, list):
        return
    for unit in raw_units:
        if not isinstance(unit, dict):
            continue
        unit_id = unit.get("unit_id")
        previous = prior_by_id.get(unit_id)
        if previous is None:
            continue
        for field in ("source_ref_ids", "cluster_role", "parent_slide_id"):
            if unit.get(field) != previous.get(field):
                raise Pass1AuthorityError(
                    f"unit_id {unit_id} changed immutable {field} before normalization"
                )


def _pass1_response_frame(raw_text: str) -> tuple[str, str, int]:
    """Return candidate text, framing, and its raw-text character start."""
    json_ws = " \t\r\n"
    leading = len(raw_text) - len(raw_text.lstrip(json_ws))
    outer = raw_text.strip(json_ws)
    framing = "plain"
    candidate = outer
    candidate_start = leading
    if outer.startswith("```json") or outer.endswith("```"):
        prefix = "```json\r\n" if outer.startswith("```json\r\n") else "```json\n"
        suffix = "\r\n```" if outer.endswith("\r\n```") else "\n```"
        if not outer.startswith(prefix) or not outer.endswith(suffix):
            raise Pass1AuthorityError(
                "Irene response must be one structured JSON object"
            )
        candidate = outer[len(prefix) : -len(suffix)]
        candidate_start = leading + len(prefix)
        framing = "json-code-fence"
    return candidate, framing, candidate_start


def _decode_pass1_response_v2(raw_text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Decode one response object with the Amendment-7 framing allowance only."""
    candidate, framing, candidate_start = _pass1_response_frame(raw_text)

    action = "strict-json"
    removed_byte: str | None = None
    removed_offset: int | None = None
    try:
        parsed = json.loads(
            candidate,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateJsonKeyError as exc:
        raise Pass1AuthorityError("Irene response contains duplicate JSON keys") from exc
    except _InvalidJsonConstantError as exc:
        raise Pass1AuthorityError(
            "Irene response must be one structured JSON object"
        ) from exc
    except json.JSONDecodeError as exc:
        if exc.msg != "Extra data":
            raise Pass1AuthorityError(
                "Irene response must be one structured JSON object"
            ) from exc
        removed_index = len(candidate.rstrip(" \t\r\n")) - 1
        if removed_index < 0 or candidate[removed_index] != "}":
            raise Pass1AuthorityError(
                "Irene response must be one structured JSON object"
            ) from exc
        repaired = candidate[:removed_index] + candidate[removed_index + 1 :]
        try:
            parsed = json.loads(
                repaired,
                object_pairs_hook=_unique_json_object,
                parse_constant=_reject_json_constant,
            )
        except _DuplicateJsonKeyError as repair_exc:
            raise Pass1AuthorityError(
                "Irene response contains duplicate JSON keys"
            ) from repair_exc
        except (_InvalidJsonConstantError, json.JSONDecodeError) as repair_exc:
            raise Pass1AuthorityError(
                "Irene response must be one structured JSON object"
            ) from repair_exc
        action = "drop-one-surplus-final-rbrace"
        removed_byte = "}"
        removed_offset = len(
            raw_text[: candidate_start + removed_index].encode("utf-8")
        )
    if not isinstance(parsed, dict):
        raise Pass1AuthorityError("Irene response must be one structured JSON object")
    processing = {
        "action": action,
        "framing": framing,
        "removed_byte": removed_byte,
        "removed_offset": removed_offset,
        "processed_candidate": parsed,
    }
    return parsed, processing


def parse_pass1_response(
    raw_text: str, *, prior_receipt: dict[str, Any] | None = None
) -> dict[str, Any]:
    parsed, _processing = _decode_pass1_response_v2(raw_text)
    return _normalize_decoded_pass1_response(parsed, prior_receipt=prior_receipt)


def _normalize_decoded_pass1_response(
    parsed: dict[str, Any], *, prior_receipt: dict[str, Any] | None = None
) -> dict[str, Any]:
    if isinstance(parsed.get("plan_units"), list) and parsed["plan_units"]:
        assert_unique_plan_unit_ids(parsed)
    _validate_raw_refinement_identity(parsed, prior_receipt)
    # Normalize cluster structure on whatever the model produced (after JSON
    # parse, before the fallback-unit branch) so both LLM output and the
    # fallback unit get a well-formed cluster shape.
    parsed = normalize_clusters(parsed)
    # Braid S1: guarantee a well-formed collateral block on BOTH the LLM-output
    # path and the fallback-unit path (additive; degenerate-empty -> "none").
    parsed = normalize_collateral(parsed)
    # Fidelity emit recovery: soft-coerce recognized modes; never invent tags.
    parsed = normalize_fidelity(parsed)
    return parsed


def write_lesson_plan(plan: dict[str, Any], *, run_id: str, runs_root: Path | None = None) -> Path:
    root = runs_root or REPO_ROOT / "runs"
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "irene-pass1.md"
    # Soft-canonicalize fidelity so alias callers (literal_text / literal-image)
    # still surface a line even when they bypass parse_pass1_response.
    plan = normalize_fidelity(plan)
    # Mine 1: machine-readable companion for auto ComponentSelection derive.
    # Markdown remains the human artifact; JSON is the selection-edge input.
    json_path = run_dir / "irene-pass1.lesson-plan.json"
    json_path.write_text(
        json.dumps(plan, indent=2, ensure_ascii=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = ["# Irene Pass-1 Lesson Plan", ""]
    if plan.get("lesson_summary"):
        lines.extend([str(plan["lesson_summary"]), ""])
    for unit in plan["plan_units"]:
        lines.extend(
            [
                f"## {unit.get('unit_id', 'unit')}: {unit.get('title', 'Untitled')}",
                f"- Learning objective: {unit.get('learning_objective', '')}",
                f"- Scope decision: {unit.get('scope_decision', '')}",
                f"- Rationale: {unit.get('rationale', '')}",
            ]
        )
        # Story 1.1: cluster fields are the witness the 1.2 emission gate reads.
        # Additive — flat lines above are unchanged.
        lines.append(f"- Cluster id: {unit.get('cluster_id', '')}")
        lines.append(f"- Cluster role: {unit.get('cluster_role', '')}")
        lines.append(f"- Cluster position: {unit.get('cluster_position', '')}")
        if unit.get("narrative_arc"):
            lines.append(f"- Narrative arc: {unit['narrative_arc']}")
        if unit.get("cluster_role") == "interstitial" and unit.get("parent_slide_id"):
            lines.append(f"- Parent slide id: {unit['parent_slide_id']}")
        is_head = unit.get("cluster_role") == "head"
        if is_head and unit.get("cluster_interstitial_count") is not None:
            lines.append(f"- Cluster interstitial count: {unit['cluster_interstitial_count']}")
        raw_fidelity = unit.get("fidelity")
        if isinstance(raw_fidelity, str) and raw_fidelity in RECOGNIZED_FIDELITY:
            lines.append(f"- Fidelity: {raw_fidelity}")
        lines.append("")
    # Braid S1: additive collateral content-model section. Appended AFTER all
    # plan-unit / cluster lines so the cluster-section lines stay byte-unchanged
    # (the no-regression invariant). Absent/none collateral emits the explicit
    # deck-only declaration line; never an absent section.
    lines.extend(_collateral_artifact_lines(plan.get("collateral")))
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def write_plan_authority_receipt(
    receipt: dict[str, Any], *, run_id: str, runs_root: Path | None = None
) -> Path:
    """Atomically persist the receipt companion after authority validation."""
    root = runs_root or REPO_ROOT / "runs"
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "irene-pass1.plan-authority.json"
    if path.is_symlink():
        raise Pass1AuthorityError("plan authority sidecar coordinate is unsafe")
    serialized = (
        json.dumps(
            receipt,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )
    descriptor, temp_name = tempfile.mkstemp(
        dir=run_dir,
        prefix=".irene-pass1.plan-authority.",
        suffix=".tmp",
        text=True,
    )
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        if path.is_symlink():
            raise Pass1AuthorityError("plan authority sidecar coordinate is unsafe")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return path


def write_current_plan_artifacts(
    plan: dict[str, Any],
    receipt: dict[str, Any],
    *,
    run_id: str,
    runs_root: Path | None = None,
) -> tuple[Path, Path]:
    """Publish the current plan/receipt set with rollback on recoverable failure."""
    root = runs_root or REPO_ROOT / "runs"
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        with pass1_generation_lock(run_dir):
            return _write_current_plan_artifacts_locked(
                plan, receipt, run_id=run_id, run_dir=run_dir
            )
    except Pass1GenerationLockError as exc:
        raise Pass1AuthorityError(str(exc)) from exc


def _write_current_plan_artifacts_locked(
    plan: dict[str, Any],
    receipt: dict[str, Any],
    *,
    run_id: str,
    run_dir: Path,
) -> tuple[Path, Path]:
    targets = (
        run_dir / "irene-pass1.md",
        run_dir / "irene-pass1.lesson-plan.json",
        run_dir / "irene-pass1.plan-authority.json",
    )
    if any(path.is_symlink() or (path.exists() and not path.is_file()) for path in targets):
        raise Pass1AuthorityError("current Pass-1 artifact coordinate is unsafe")
    before = {path: path.read_bytes() if path.is_file() else None for path in targets}
    staging_root = Path(tempfile.mkdtemp(dir=run_dir.parent, prefix=f".{run_id}.pass1-generation."))
    try:
        staged_artifact = write_lesson_plan(plan, run_id=run_id, runs_root=staging_root)
        staged_authority = write_plan_authority_receipt(
            receipt, run_id=run_id, runs_root=staging_root
        )
        staged_dir = staging_root / run_id
        staged = {
            targets[0]: staged_artifact,
            targets[1]: staged_dir / "irene-pass1.lesson-plan.json",
            targets[2]: staged_authority,
        }
        for staged_path in staged.values():
            with staged_path.open("r+b") as stream:
                os.fsync(stream.fileno())
        # The receipt is the generation commit marker. Remove the old marker,
        # publish both plan projections, then publish the matching receipt last.
        targets[2].unlink(missing_ok=True)
        _fsync_directory(run_dir)
        for target in targets[:2]:
            os.replace(staged[target], target)
            _fsync_directory(run_dir)
        os.replace(staged[targets[2]], targets[2])
        _fsync_directory(run_dir)
        return targets[0], targets[2]
    except (OSError, Pass1AuthorityError) as exc:
        try:
            # Rollback is a second receipt-last publication: withdraw any
            # current marker, restore both projections durably, then restore
            # the prior marker only after those entries are committed.
            targets[2].unlink(missing_ok=True)
            _fsync_directory(run_dir)
            for path in targets[:2]:
                original = before[path]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    descriptor, restore_name = tempfile.mkstemp(
                        dir=run_dir, prefix=f".{path.name}.restore.", suffix=".tmp"
                    )
                    restore = Path(restore_name)
                    try:
                        with os.fdopen(descriptor, "wb") as stream:
                            stream.write(original)
                            stream.flush()
                            os.fsync(stream.fileno())
                        os.replace(restore, path)
                    finally:
                        restore.unlink(missing_ok=True)
                _fsync_directory(run_dir)
            prior_receipt = before[targets[2]]
            if prior_receipt is None:
                targets[2].unlink(missing_ok=True)
            else:
                descriptor, restore_name = tempfile.mkstemp(
                    dir=run_dir,
                    prefix=f".{targets[2].name}.restore.",
                    suffix=".tmp",
                )
                restore = Path(restore_name)
                try:
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(prior_receipt)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(restore, targets[2])
                finally:
                    restore.unlink(missing_ok=True)
            _fsync_directory(run_dir)
        except OSError as rollback_exc:
            raise Pass1AuthorityError(
                "current Pass-1 artifact publication and rollback failed"
            ) from rollback_exc
        if isinstance(exc, Pass1AuthorityError):
            raise
        raise Pass1AuthorityError("current Pass-1 artifact publication failed") from exc
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


def _fsync_directory(path: Path) -> None:
    """Durably order directory-entry replacements on Windows and POSIX."""
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateFileW(
            str(path),
            0x40000000,  # GENERIC_WRITE
            0x00000007,  # FILE_SHARE_READ | WRITE | DELETE
            None,
            3,  # OPEN_EXISTING
            0x02000000,  # FILE_FLAG_BACKUP_SEMANTICS
            None,
        )
        if handle == -1:
            raise OSError(ctypes.get_last_error(), "cannot open run directory")
        try:
            if not kernel32.FlushFileBuffers(handle):
                raise OSError(ctypes.get_last_error(), "cannot flush run directory")
        finally:
            kernel32.CloseHandle(handle)
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _oneline(value: Any) -> str:
    """Collapse CR/LF in a free-text field to single spaces for flat rendering.

    FIX-3 (S1->S2 seam robustness): the collateral artifact section interpolates
    free-text fields (title, narrative_intent, prompt_intent, pedagogical_intent,
    deferred_depth) into flat ``- `` / ``### `` lines that S2 parses back. A
    field carrying a newline would inject fake markdown lines. This sanitizes at
    the RENDERING SITE ONLY — the stored schema values stay verbatim.
    """
    return str(value).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")


def _collateral_artifact_lines(collateral: Any) -> list[str]:
    """Render the additive ``## Workbook collateral`` artifact section.

    Pure helper. A missing or ``declaration:"none"`` block renders the explicit
    deck-only line (the decision-on-record); a ``present`` block renders the
    workbook sections + research goals as flat, additive lines.
    """
    block = collateral if isinstance(collateral, dict) else {}
    declaration = block.get("declaration", "none")
    out: list[str] = ["## Workbook collateral", f"- Declaration: {declaration}"]
    if declaration != "present":
        out.append("- Workbook: none (lesson ships deck-only)")
        out.append("")
        return out

    workbook = block.get("workbook") or {}
    sections = workbook.get("sections") if isinstance(workbook, dict) else None
    for section in sections or []:
        if not isinstance(section, dict):
            continue
        out.append(
            f"### {section.get('section_id', 'section')}: "
            f"{_oneline(section.get('title', 'Untitled'))}"
        )
        out.append(f"- Learning objective id: {section.get('learning_objective_id', '')}")
        depth = section.get("depth_delta") or {}
        if isinstance(depth, dict):
            out.append(f"- Depth deferred from: {depth.get('deferred_from_slide', '')}")
            out.append(f"- Depth deferred: {_oneline(depth.get('deferred_depth', ''))}")
            if depth.get("retained_on_slide"):
                out.append(f"- Retained on slide: {depth['retained_on_slide']}")
        if section.get("narrative_intent"):
            out.append(f"- Narrative intent: {_oneline(section['narrative_intent'])}")
        for exercise in section.get("exercises") or []:
            if not isinstance(exercise, dict):
                continue
            out.append(
                f"- Exercise {exercise.get('exercise_id', '')} "
                f"[{exercise.get('bloom_level', '')}]: "
                f"{_oneline(exercise.get('prompt_intent', ''))} "
                f"(answer key source: {exercise.get('answer_key_source_ref', '')})"
            )
    for goal in block.get("research_goals") or []:
        if not isinstance(goal, dict):
            continue
        out.append(
            f"- Research goal {goal.get('goal_id', '')}: "
            f"{_oneline(goal.get('pedagogical_intent', ''))}"
        )
    out.append("")
    return out


def confirm_plan_units(
    plan: dict[str, Any],
    verdicts: dict[str, OperatorVerdict] | OperatorVerdict,
) -> dict[str, Any]:
    units = plan.get("plan_units", [])
    if isinstance(verdicts, OperatorVerdict):
        raise BulkRatificationError("bulk confirmation is forbidden; confirm each unit")
    if not isinstance(verdicts, dict):
        raise PlanUnitRatificationError("verdicts must be keyed by plan unit")
    locked_units = []
    for unit in units:
        unit_id = str(unit.get("unit_id", ""))
        verdict = verdicts.get(unit_id)
        if not isinstance(verdict, OperatorVerdict):
            raise PlanUnitRatificationError(f"missing OperatorVerdict for {unit_id}")
        if verdict.verb not in {"approve", "edit"}:
            raise PlanUnitRatificationError(f"unit {unit_id} rejected")
        updated = dict(unit)
        if verdict.edit_payload:
            updated.update(verdict.edit_payload)
        updated["ratified_by"] = verdict.operator_id
        updated["ratification_verdict_id"] = str(verdict.verdict_id)
        locked_units.append(updated)
    return {"plan_units": locked_units, "locked": True}


def build_learning_events(*, run_id: str, locked_scope: dict[str, Any]) -> list[dict[str, Any]]:
    now = datetime.now(UTC).isoformat()
    base = {"run_id": run_id, "gate": "G1A", "timestamp": now}
    return [
        {**base, "event_type": "scope_decision.set", "payload": locked_scope},
        {**base, "event_type": "plan.locked", "payload": {"locked_scope": locked_scope}},
    ]


def act(state: RunState, *, handle: Any, model_id: str) -> dict[str, Any]:
    payload = decode_envelope_payload(state)
    run_id = str(payload.get("run_id") or state.run_id)
    if (
        not run_id
        or run_id in {".", ".."}
        or "/" in run_id
        or "\\" in run_id
        or Path(run_id).is_absolute()
    ):
        raise Pass1AuthorityError("Irene run identity is not a contained coordinate")
    runs_root_value = payload.get("runs_root")
    runs_root = Path(str(runs_root_value)) if runs_root_value else REPO_ROOT / "runs"
    from app.models.registry_check import load_registry

    registered_model = any(entry.model_id == model_id for entry in load_registry().entries)
    chat_module = type(getattr(handle, "chat", None)).__module__
    production_handle = getattr(handle, "entry", None) is not None or chat_module.startswith(
        ("langchain", "langchain_openai")
    )
    if registered_model and production_handle:
        allowed_roots = {
            (REPO_ROOT / "runs").resolve(strict=False),
            (REPO_ROOT / "state" / "config" / "runs").resolve(strict=False),
        }
        if runs_root.resolve(strict=False) not in allowed_roots:
            raise Pass1AuthorityError("Irene production runs root is outside approved storage")
        if run_id != str(state.run_id):
            raise Pass1AuthorityError("Irene production run identity disagrees with RunState")
    run_dir = runs_root / run_id
    try:
        run_dir.resolve(strict=False).relative_to(runs_root.resolve(strict=False))
    except (OSError, ValueError) as exc:
        raise Pass1AuthorityError("Irene run coordinate escapes its runs root") from exc
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        with pass1_generation_lock(run_dir):
            return _act_locked(
                state,
                handle=handle,
                model_id=model_id,
                payload=payload,
                run_id=run_id,
                runs_root=runs_root,
            )
    except Pass1GenerationLockError as exc:
        raise Pass1AuthorityError(str(exc)) from exc


def _act_locked(
    state: RunState,
    *,
    handle: Any,
    model_id: str,
    payload: dict[str, Any],
    run_id: str,
    runs_root: Path,
) -> dict[str, Any]:
    enforce_pass1_mode(payload)
    upstream = payload.get("upstream_output")
    prior_plan = (
        upstream.get("lesson_plan")
        if isinstance(upstream, dict) and isinstance(upstream.get("lesson_plan"), dict)
        else None
    )
    raw_prior_receipt = payload.get("prior_plan_authority_receipt")
    if "prior_plan_authority_receipt" in payload and not isinstance(raw_prior_receipt, dict):
        raise Pass1AuthorityError(
            "prior_plan_authority_receipt must be a current-format authority mapping"
        )
    prior_receipt = raw_prior_receipt if isinstance(raw_prior_receipt, dict) else None
    if prior_receipt is not None:
        if prior_plan is None:
            raise Pass1AuthorityError(
                "prior_plan_authority_receipt has no matching prior lesson plan"
            )
        try:
            _assert_receipt_matches_plan(prior_plan, prior_receipt)
        except Pass1PlanAuthorityError as exc:
            raise Pass1AuthorityError(str(exc)) from exc
        if prior_receipt.get("schema_version") == LEGACY_SCHEMA_VERSION:
            raise Pass1AuthorityError(
                "legacy-v1 Pass-1 authority is read-only; start an explicit fresh "
                "Pass-1 generation instead of silently upgrading a refinement"
            )
    elif prior_plan is not None:
        raise Pass1AuthorityError(
            "current Pass-1 refinement is missing cumulative authority receipt"
        )
    extracted_source, source_sections = read_extracted_source_with_sections(payload)
    try:
        source_span_catalog = build_pass1_source_span_catalog(source_sections)
    except Pass1SourceSpanCatalogError as exc:
        raise Pass1AuthorityError(str(exc)) from exc
    if prior_receipt is not None:
        try:
            reconciled_prior_receipt = finalize_plan_authority(
                prior_plan,
                source_sections=source_sections,
                prior_receipt=prior_receipt,
            )
        except Pass1PlanAuthorityError as exc:
            raise Pass1AuthorityError(str(exc)) from exc
        if reconciled_prior_receipt != prior_receipt:
            raise Pass1AuthorityError(
                "current Pass-1 refinement receipt does not replay exactly"
            )
    system_msg, user_msg = assemble_pass1_prompt(
        payload,
        extracted_source=extracted_source,
        source_span_catalog=source_span_catalog,
    )
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
    _assert_prompt_fits_context(
        handle=handle,
        model_id=model_id,
        system_msg=system_msg,
        user_msg=user_msg,
    )
    model_config_digest = _effective_model_config_digest(handle, model_id=model_id)
    node_id = str(payload.get("manifest_node_id") or payload.get("node_id") or "direct-invocation")
    try:
        call_identity = build_pass1_call_identity(
            run_id=run_id,
            node_id=node_id,
            model_id=model_id,
            model_config_digest=model_config_digest,
            catalog_digest=source_span_catalog.catalog_digest,
            messages=messages,
        )
        resume = begin_or_resume_pass1_call(
            run_dir=runs_root / run_id,
            identity=call_identity,
        )
    except Pass1CallJournalError as exc:
        raise Pass1AuthorityError(str(exc)) from exc
    provider_evidence: dict[str, Any]
    if resume.state == "new":
        try:
            response = _invoke_chat_with_identity(
                handle.chat,
                messages,
                request_digest=call_identity["request_digest"],
                node_id=node_id,
            )
        except Exception as exc:
            try:
                record_pass1_dispatch_exception(
                    path=resume.path,
                    identity=call_identity,
                    exc=exc,
                )
            except Pass1CallJournalError as persistence_exc:
                raise Pass1AuthorityError(
                    "Irene provider call is ambiguous and its exception evidence "
                    f"could not be persisted: {persistence_exc}"
                ) from persistence_exc
            raise Pass1AuthorityError(
                f"Irene provider call outcome is ambiguous after {type(exc).__name__}"
            ) from exc
        raw_value = response.content if hasattr(response, "content") else str(response)
        try:
            raw = _provider_text(raw_value)
            unsupported_error: Pass1AuthorityError | None = None
        except Pass1AuthorityError as exc:
            raw = "[unsupported provider content shape]"
            unsupported_error = exc
        try:
            provider_evidence = response_provider_evidence(response)
        except Exception as exc:
            minimal_evidence = {
                "response_type": type(response).__name__,
                "evidence_normalization_error": type(exc).__name__,
            }
            try:
                record_pass1_response(
                    path=resume.path,
                    identity=call_identity,
                    raw_response=raw,
                    provider_evidence=minimal_evidence,
                )
            except Pass1CallJournalError as persistence_exc:
                raise Pass1AuthorityError(
                    "Irene returned-unserializable evidence persistence failed"
                ) from persistence_exc
            raise Pass1AuthorityError(
                "Irene provider response evidence could not be normalized"
            ) from exc
        if unsupported_error is not None:
            unsupported_evidence = {
                **provider_evidence,
                "unsupported_content_shape": type(raw_value).__name__,
            }
            try:
                record_pass1_response(
                    path=resume.path,
                    identity=call_identity,
                    raw_response=raw,
                    provider_evidence=unsupported_evidence,
                )
            except Pass1CallJournalError as exc:
                raise Pass1AuthorityError(
                    f"Irene unsupported-response evidence persistence failed: {exc}"
                ) from exc
            raise unsupported_error
        try:
            record_pass1_response(
                path=resume.path,
                identity=call_identity,
                raw_response=raw,
                provider_evidence=provider_evidence,
            )
        except Pass1CallJournalError as exc:
            raise Pass1AuthorityError(
                f"Irene returned-response evidence persistence failed: {exc}"
            ) from exc
    else:
        if resume.raw_response is None or resume.provider_evidence is None:
            raise Pass1AuthorityError("Irene returned-response journal is incomplete")
        raw = resume.raw_response
        provider_evidence = resume.provider_evidence
        if provider_evidence.get("unsupported_content_shape") is not None:
            raise Pass1AuthorityError("Irene provider returned unsupported content")
        if provider_evidence.get("evidence_normalization_error") is not None:
            raise Pass1AuthorityError(
                "Irene provider response evidence could not be normalized"
            )
    plan_candidate, processing = _decode_pass1_response_v2(raw)
    try:
        record_pass1_candidate_processing(
            path=resume.path,
            identity=call_identity,
            action=processing["action"],
            framing=processing["framing"],
            removed_byte=processing["removed_byte"],
            removed_offset=processing["removed_offset"],
            processed_candidate=processing["processed_candidate"],
        )
    except Pass1CallJournalError as exc:
        raise Pass1AuthorityError(
            f"Irene response-processing receipt persistence failed: {exc}"
        ) from exc
    plan = _normalize_decoded_pass1_response(
        plan_candidate, prior_receipt=prior_receipt
    )
    try:
        plan = project_pass1_source_ref_ids(plan, catalog=source_span_catalog)
    except Pass1SourceSpanCatalogError as exc:
        raise Pass1AuthorityError(str(exc)) from exc
    # Leg-C R3: deterministic post-hoc min_cluster_floor honoring on the FULL
    # payload (the LLM never saw the floor — D-0 strip above). Runs on EVERY
    # Pass-1 dispatch (04A creation AND 05/05B refinement — the manifest
    # projects the corpus to 05/05B too, so extracted_source is normally
    # non-None on all three nodes): refinement CONSOLIDATES clusters, so the
    # LATEST pass must honor. The dead-config guard (D-1/D-3) fails loud if a
    # bound floor ever bypasses this seam.
    try:
        floored_units, floor_receipt = consume_min_cluster_floor(
            payload, plan["plan_units"], extracted_source=extracted_source
        )
    except ClusterFloorMismatchError:
        raise
    assert_floor_consulted(payload, floor_receipt)
    plan = {**plan, "plan_units": floored_units}
    # Amendment 5 authority is the first post-shaping gate.  Run it before
    # planning-context assessment can persist any diagnostic sidecar; rerun
    # below after additive planning provenance is attached to bind final bytes.
    validate_pass1_plan_authority(
        plan,
        source_sections=source_sections,
        prior_plan=prior_plan,
        prior_receipt=prior_receipt,
    )
    # Planning-context handoff (2026-07-09): soft LO coverage receipt when
    # context present; fail-loud on total LO ignore (party LO policy).
    planning_coverage_receipt: dict[str, Any] | None = None
    planning_provenance: dict[str, Any] | None = None
    raw_planning = payload.get("planning_context")
    if isinstance(raw_planning, dict) and raw_planning:
        from app.marcus.lesson_plan.planning_context import (
            PlanningContext,
            assert_lo_coverage_or_fail,
            assess_lo_coverage,
        )

        context = PlanningContext.model_validate(raw_planning)
        receipt = assess_lo_coverage(context, plan)
        planning_coverage_receipt = receipt.model_dump(mode="json")
        try:
            assert_lo_coverage_or_fail(context, receipt)
        except SpecialistDispatchError:
            # ECH-09: persist coverage receipt before fail-loud so the
            # pause artifact always shows context was assessed.
            receipt_path = runs_root / run_id / "planning-context-coverage.json"
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(
                json.dumps(planning_coverage_receipt, indent=2),
                encoding="utf-8",
            )
            raise
        # Claim B SUCCESS: additive planning_provenance digests on the plan
        # (Winston pipe). Pointers only — full bodies stay in companion files.
        run_dir_for_prov = runs_root / run_id
        planning_provenance = _build_planning_provenance(
            context=context,
            receipt_lo_status=(
                "framing_only" if not context.learning_objectives else str(receipt.lo_coverage)
            ),
            run_dir=run_dir_for_prov,
        )
        if planning_provenance is not None:
            plan = {**plan, "planning_provenance": planning_provenance}
    authority_receipt = validate_pass1_plan_authority(
        plan,
        source_sections=source_sections,
        prior_plan=prior_plan,
        prior_receipt=prior_receipt,
    )
    artifact_path = runs_root / run_id / "irene-pass1.md"
    authority_path = runs_root / run_id / "irene-pass1.plan-authority.json"
    locked_scope = {"plan_units": plan["plan_units"], "locked": False}
    events = build_learning_events(run_id=run_id, locked_scope=locked_scope)
    output: dict[str, Any] = {
        "specialist_id": "irene_pass1",
        "model_id": model_id,
        "lesson_plan": plan,
        "artifact_path": str(artifact_path),
        "locked_scope": locked_scope,
        "learning_events": events,
        "plan_authority_receipt": authority_receipt,
        "plan_authority_receipt_path": str(authority_path),
        "usage": provider_evidence.get("usage_metadata"),
    }
    if planning_coverage_receipt is not None:
        output["planning_context_coverage"] = planning_coverage_receipt
    if planning_provenance is not None:
        output["planning_provenance"] = planning_provenance
    if resume.state == "completed":
        replay_result = _validate_completed_replay(
            stored_result=resume.result,
            stored_identity=resume.result_identity,
            expected_output=output,
            current_entries_count=(
                state.cache_state.entries_count if state.cache_state is not None else 0
            ),
        )
        _write_current_plan_artifacts_locked(
            plan, authority_receipt, run_id=run_id, run_dir=runs_root / run_id
        )
        return replay_result
    _write_current_plan_artifacts_locked(
        plan, authority_receipt, run_id=run_id, run_dir=runs_root / run_id
    )
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    update = {
        "cache_state": {
            "cache_prefix": _json_dumps(output),
            "entries_count": entries_count + 1,
        }
    }
    output_digest = "sha256:" + hashlib.sha256(_json_dumps(output).encode("utf-8")).hexdigest()
    try:
        complete_pass1_call(
            path=resume.path,
            identity=call_identity,
            result_identity={
                "plan_digest": authority_receipt["plan_digest"],
                "authority_digest": authority_receipt["authority_digest"],
                "output_digest": output_digest,
            },
            result=update,
        )
    except Pass1CallJournalError as exc:
        raise Pass1AuthorityError(f"Irene call completion persistence failed: {exc}") from exc
    return update


# Amelia a.2 (party review 2026-06-12): the payload contract participates in
# the act's import graph so it cannot rot as an orphan module.
from app.specialists.irene_pass1.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = [
    "BulkRatificationError",
    "CONSUMED_PAYLOAD_KEYS",
    "ModeMismatchError",
    "PASS_1_REFERENCES",
    "PASS_1_SYSTEM_MESSAGE",
    "Pass1AuthorityError",
    "PlanUnitRatificationError",
    "act",
    "assert_unique_plan_unit_ids",
    "assemble_pass1_prompt",
    "assert_floor_consulted",
    "build_learning_events",
    "confirm_plan_units",
    "consume_min_cluster_floor",
    "decode_envelope_payload",
    "enforce_pass1_mode",
    "normalize_clusters",
    "normalize_collateral",
    "normalize_fidelity",
    "parse_pass1_response",
    "read_sanctum_digest",
    "validate_pass1_plan_authority",
    "write_lesson_plan",
    "write_plan_authority_receipt",
]
