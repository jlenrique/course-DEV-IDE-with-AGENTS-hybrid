"""Production-graph runner composition layer for migrated trials."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from uuid import UUID, uuid4

import yaml

from app.gates.errors import GateError
from app.gates.resume_api import (
    get_registered_decision_card,
    register_decision_card,
    resume_from_verdict,
)
from app.manifest.compiler import (
    _canonical_specialist_id,
    compile_run_graph,
    production_gate_ids,
)
from app.manifest.loader import load as load_manifest
from app.manifest.schema import NodeSpec
from app.marcus.orchestrator import (
    conversation_persistence,
    gate_runner,
    package_builders,
    pre_gate_marcus,
    specialist_summary_writer,
    storyboard_publisher,
)
from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.marcus.orchestrator.pre_gate_marcus import PreFillProposal
from app.models.decision_cards import (
    AnyDecisionCardAdapter,
    DecisionCardMeta,
    G1Card,
    G2CCard,
    G3Card,
    G4Card,
)
from app.models.decision_cards._base import DecisionCardMeta as DecisionCardBaseMeta
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.runtime.trial_economics_report import (
    AgentCostEntry,
    BudgetStatus,
    TrialEconomicsReport,
)
from app.models.state.cache_state import CacheState
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState
from app.runtime.cascade_config import ensure_pricing_covers_cascade, load_cascade, load_pricing
from app.runtime.economics import RUNS_ROOT, measure_trial_cost, record_trial_cost_report
from app.specialists.dispatch_errors import SpecialistDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
DEFAULT_GRAPH_VERSION = "v42"
LOGGER = logging.getLogger(__name__)


class MissingUpstreamContributionError(RuntimeError):
    """Raised when a dependency map names an upstream contribution that is absent."""

    def __init__(
        self,
        *,
        specialist_id: str,
        downstream_input_key: str,
        downstream_specialist_id: str,
    ) -> None:
        self.specialist_id = specialist_id
        self.downstream_input_key = downstream_input_key
        self.downstream_specialist_id = downstream_specialist_id
        super().__init__(
            "missing upstream contribution "
            f"{specialist_id!r} for downstream input {downstream_input_key!r} "
            f"while invoking {downstream_specialist_id!r}"
        )


class LegacyEnvelopeSchemaError(RuntimeError):
    """Raised when resuming a run whose envelope predates per-node keying.

    S2 (SCP 2026-06-11): production-envelope.v1 rows carry no node_id; a
    resume against them would re-dispatch every specialist (double spend)
    or half-read the walk state. Murat's characterization ruling: legacy
    envelopes are migrated explicitly or rejected loudly — never half-read.
    Per the operator's relaunch-as-cycle-2 ruling, v1 runs stay frozen as
    evidence and new cycles launch fresh.
    """


class GateBypassError(RuntimeError):
    """Raised when a production pause-point gate would be silently skipped."""


def _has_live_openai() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _has_langsmith_env() -> bool:
    return bool(os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"))


def _now() -> datetime:
    return datetime.now(UTC)


def _run_dir(trial_id: UUID | str, runs_root: Path) -> Path:
    return runs_root / str(trial_id)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def _persist_envelope(envelope: ProductionTrialEnvelope, runs_root: Path) -> Path:
    path = _run_dir(envelope.trial_id, runs_root) / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(envelope.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def _fallback_cost_report(trial_id: str) -> TrialEconomicsReport:
    cascade = load_cascade()
    pricing = load_pricing()
    ensure_pricing_covers_cascade(cascade, pricing)
    return TrialEconomicsReport(
        trial_id=trial_id,
        measured_at=_now(),
        total_cost_usd=0.0,
        per_agent_breakdown={
            "marcus": AgentCostEntry(
                agent_name="marcus",
                model_assigned=cascade.marcus.model,
                call_count=0,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
            )
        },
        per_model_breakdown={cascade.marcus.model: 0.0},
        cascade_config_digest=cascade.sha256_digest,
        pricing_table_digest=pricing.sha256_digest,
        langsmith_trace_url=None,
        drift_alerts=[],
        budget_status=BudgetStatus(state="no-cap", over_by_usd=0.0),
    )


@contextmanager
def _trial_trace_context(
    *,
    trial_id: UUID,
    preset: str,
    operator_id: str,
) -> Any:
    metadata = {
        "trial_id": str(trial_id),
        "preset": preset,
        "operator_id": operator_id,
    }
    try:
        from langsmith import tracing_context
    except ImportError:
        yield metadata
        return
    with tracing_context(metadata=metadata):
        yield metadata


def _trace_run(
    *,
    trial_id: UUID,
    specialist_id: str,
    model_id: str,
    input_tokens: int,
    output_tokens: int,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=str(uuid4()),
        trace_id=str(trial_id),
        name=f"{specialist_id} production dispatch",
        run_type="llm",
        prompt_tokens=input_tokens,
        completion_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        extra={
            "metadata": {
                "trial_id": str(trial_id),
                "specialist_id": specialist_id,
                "model_id": model_id,
            }
        },
        child_runs=[],
    )


def _trace_run_for_contribution(
    *,
    trial_id: UUID,
    contribution: SpecialistContribution,
) -> SimpleNamespace:
    usage = contribution.output.get("usage")
    input_tokens = 25
    output_tokens = 10
    if isinstance(usage, dict):
        input_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 25)
        output_tokens = int(
            usage.get("output_tokens") or usage.get("completion_tokens") or 10
        )
    return _trace_run(
        trial_id=trial_id,
        specialist_id=contribution.specialist_id,
        model_id=contribution.model_used,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _trace_run_for_pre_gate_marcus(
    *,
    trial_id: UUID,
    gate_id: str,
    proposal: PreFillProposal,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=str(uuid4()),
        trace_id=str(trial_id),
        name=f"pre-gate-marcus {gate_id}",
        run_type="llm",
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2,
        extra={
            "metadata": {
                "trial_id": str(trial_id),
                "specialist_id": "marcus",
                "node_id": "pre-gate-marcus",
                "gate_id": gate_id,
                "model_id": "gpt-5-nano",
                "decision": proposal.decision,
                "directive": proposal.directive,
            }
        },
        child_runs=[],
    )


def _trace_root(
    *,
    trial_id: UUID,
    metadata: dict[str, str],
    child_runs: list[SimpleNamespace],
) -> SimpleNamespace:
    return SimpleNamespace(
        id=str(trial_id),
        trace_id=str(trial_id),
        name="production trial",
        run_type="chain",
        extra={"metadata": metadata},
        child_runs=child_runs,
    )


def _trace_to_json(root: SimpleNamespace) -> dict[str, Any]:
    def convert(value: Any) -> Any:
        if isinstance(value, SimpleNamespace):
            return {key: convert(item) for key, item in vars(value).items()}
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        return value

    return {"root": convert(root)}


def _default_dependency_map_for(
    *,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
) -> dict[str, str]:
    """Derive the deterministic dependency fallback for undeclared manifest nodes."""
    prior_ids = [item.specialist_id for item in production_envelope.contributions]
    if not prior_ids:
        return {}
    if specialist_id == "cd" and "texas" in prior_ids:
        return {"source_bundle": "texas"}
    return {"upstream_output": prior_ids[-1]}


def _canonical_dependency_specialist_id(specialist_id: str) -> str:
    return _canonical_specialist_id(specialist_id) or specialist_id


def _normalize_dependency_map(
    *,
    dependency_map: dict[str, str],
    production_envelope: ProductionEnvelope,
) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for downstream_input_key, upstream_specialist_id in dependency_map.items():
        # Presence checks use latest_for_specialist — the intentful any-node
        # API (Winston S2-A: bare get_contribution without node_id is pinned
        # out of production call sites).
        if production_envelope.latest_for_specialist(upstream_specialist_id) is not None:
            normalized[downstream_input_key] = upstream_specialist_id
            continue
        canonical = _canonical_dependency_specialist_id(upstream_specialist_id)
        normalized[downstream_input_key] = (
            canonical
            if production_envelope.latest_for_specialist(canonical) is not None
            else upstream_specialist_id
        )
    return normalized


def _ensure_upstream_contributions_present(
    *,
    dependency_map: dict[str, str],
    production_envelope: ProductionEnvelope,
    downstream_specialist_id: str,
) -> None:
    for downstream_input_key, upstream_specialist_id in dependency_map.items():
        if production_envelope.latest_for_specialist(upstream_specialist_id) is None:
            raise MissingUpstreamContributionError(
                specialist_id=upstream_specialist_id,
                downstream_input_key=downstream_input_key,
                downstream_specialist_id=downstream_specialist_id,
            )


def _resolve_dependency_map(
    *,
    node: NodeSpec,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
) -> dict[str, str]:
    if node.dependencies:
        dependency_map = dict(node.dependencies)
    else:
        dependency_map = _default_dependency_map_for(
            specialist_id=specialist_id,
            production_envelope=production_envelope,
        )
    dependency_map = _normalize_dependency_map(
        dependency_map=dependency_map,
        production_envelope=production_envelope,
    )
    _ensure_upstream_contributions_present(
        dependency_map=dependency_map,
        production_envelope=production_envelope,
        downstream_specialist_id=specialist_id,
    )
    return dependency_map


def _card_meta(node_id: str) -> DecisionCardMeta:
    return DecisionCardMeta(
        cache_state="mixed",
        affected_nodes=[node_id],
        override_trail=[],
        reject_rate=0.0,
        party_mode_contributions=[],
        sanctum_warnings=[],
    )


def _base_card_meta(meta: DecisionCardMeta) -> DecisionCardBaseMeta:
    return DecisionCardBaseMeta(
        cache_state=meta.cache_state,
        affected_nodes=meta.affected_nodes,
        override_trail=meta.override_trail,
    )


def _build_decision_card(
    *,
    gate_id: str,
    trial_id: UUID,
    node_id: str,
    operator_id: str,
    pending_nodes: list[str],
    artifact_paths: list[Path],
    pre_fill: PreFillProposal | None = None,
    runs_root: Path = RUNS_ROOT,
) -> Any:
    drafted_proposal: dict[str, Any] = {"node_id": node_id, "operator_id": operator_id}
    if pre_fill is not None:
        drafted_proposal.update(
            {
                "decision": pre_fill.decision,
                "directive": pre_fill.directive,
                "rationale": pre_fill.rationale,
                "confidence": pre_fill.confidence,
                "confidence_signals": list(pre_fill.confidence_signals),
            }
        )
    evidence = [{"kind": "production-runner", "node_id": node_id}]
    adjacent_summary = specialist_summary_writer.load_most_recent_summary(
        trial_id=trial_id,
        runs_root=runs_root,
        before=_now(),
    )
    if adjacent_summary is not None:
        evidence.append(
            {
                "kind": "specialist-summary",
                "path": adjacent_summary.path.as_posix(),
                "content": adjacent_summary.text,
            }
        )
    common = {
        "card_id": uuid4(),
        "trial_id": trial_id,
        "created_at": _now(),
        "drafted_proposal": drafted_proposal,
        "evidence": evidence,
        "risks": [],
        "verb": "approve",
        "meta": _card_meta(node_id),
    }
    if gate_id == "G1":
        return G1Card(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            drafted_proposal=drafted_proposal,
            evidence=evidence,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            trial_summary="Production graph reached Gate 1.",
            opened_by="production_runner",
            next_nodes=pending_nodes[:3],
        )
    if gate_id == "G2C":
        return G2CCard(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            readiness_status="ready",
            blocking_issues=[],
            ready_nodes=pending_nodes[:3],
        )
    if gate_id == "G3":
        return G3Card(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            progress_percent=50.0,
            active_node_id=node_id,
            pending_nodes=pending_nodes,
            operator_prompt="Approve, edit, or reject the in-flight package.",
        )
    if gate_id == "G4":
        return G4Card(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            final_status="partial",
            artifact_paths=[path.as_posix() for path in artifact_paths],
            outcome_summary="Production graph reached closeout review.",
        )
    raise RuntimeError(f"unsupported production gate id: {gate_id}")


def _persist_conversation_turn_if_possible(
    *,
    card: Any,
    gate_id: str,
    trial_id: UUID,
    operator_id: str,
    runs_root: Path,
) -> Path | None:
    draft = getattr(card, "drafted_proposal", {}) or {}
    required = {"decision", "directive", "rationale", "confidence", "confidence_signals"}
    if not required.issubset(draft):
        return None
    if not (runs_root / str(trial_id) / "directive.yaml").is_file():
        LOGGER.debug(
            "skipping conversation turn persistence for trial %s: directive.yaml missing",
            trial_id,
        )
        return None
    return conversation_persistence.write_turn(
        trial_id=str(trial_id),
        gate_id=gate_id,
        decision_card={
            "decision": draft["decision"],
            "directive": draft["directive"],
            "rationale": draft["rationale"],
            "confidence": draft["confidence"],
            "confidence_signals": draft["confidence_signals"],
        },
        free_text_rationale=str(draft["rationale"]),
        operator_id=operator_id,
        runs_root=runs_root,
    )


def _pack_hash_binding(manifest_path: Path) -> str:
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def _conversation_chain_digest(*, trial_id: UUID, runs_root: Path) -> str:
    digest = conversation_persistence.latest_turn_digest(str(trial_id), runs_root)
    if digest is not None:
        return digest
    directive_path = runs_root / str(trial_id) / "directive.yaml"
    if directive_path.is_file():
        return hashlib.sha256(directive_path.read_bytes()).hexdigest()
    return "0" * 64


def _emit_run_summary_yaml(
    *,
    trial_id: UUID,
    terminal_gate: str,
    runs_root: Path,
    manifest_path: Path,
    langsmith_trace_id: str | None,
    silent_bypass_events: int = 0,
) -> Path:
    if silent_bypass_events != 0:
        LOGGER.debug(
            "run_summary.yaml silent_bypass_events expected 0, got %s",
            silent_bypass_events,
        )
    payload = {
        "terminal_gate": terminal_gate,
        "silent_bypass_events": silent_bypass_events,
        "specialist_roster_count": len(specialist_summary_writer.CANONICAL_SPECIALIST_IDS),
        "pack_hash_binding": _pack_hash_binding(manifest_path),
        "conversation_chain_digest": _conversation_chain_digest(
            trial_id=trial_id,
            runs_root=runs_root,
        ),
        "langsmith_trace_id": langsmith_trace_id or "skipped-no-langsmith-env",
    }
    path = _run_dir(trial_id, runs_root) / "run_summary.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    return path


def _quartile_engagement_counts(child_runs: list[SimpleNamespace]) -> tuple[int, int]:
    if not child_runs:
        return 0, 0
    quartile_size = max(1, len(child_runs) // 4)
    return len(child_runs[:quartile_size]), len(child_runs[-quartile_size:])


def _emit_engagement_decay_report(
    *,
    trial_id: UUID,
    child_runs: list[SimpleNamespace],
) -> Path:
    first_quartile, last_quartile = _quartile_engagement_counts(child_runs)
    result = gate_runner.emit_engagement_decay_report(
        trial_id=str(trial_id),
        first_quartile_events=first_quartile,
        last_quartile_events=last_quartile,
    )
    return Path(result["report_path"])


def _write_checkpoint(
    *,
    trial_id: UUID,
    runs_root: Path,
    node_index: int,
    gate_id: str,
    run_state: RunState,
    envelope: ProductionTrialEnvelope,
    manifest_path: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
) -> Path:
    path = _run_dir(trial_id, runs_root) / "checkpoint.json"
    _write_json(
        path,
        {
            "trial_id": str(trial_id),
            "next_node_index": node_index + 1,
            "gate_id": gate_id,
            "run_state": run_state.model_dump(mode="json"),
            "runner": {
                "corpus_path": envelope.corpus_path,
                "preset": envelope.preset,
                "operator_id": envelope.operator_id,
                "manifest_path": manifest_path.as_posix(),
                "allow_offline_cost_report": allow_offline_cost_report,
                "max_specialist_calls": max_specialist_calls,
            },
        },
    )
    return path


def _ensure_decision_card_registered_from_disk(
    *,
    trial_id: UUID,
    gate_id: str,
    run_dir: Path,
) -> None:
    if get_registered_decision_card(trial_id, gate_id) is not None:
        return
    decision_path = run_dir / f"decision-card-{gate_id}.json"
    if not decision_path.exists():
        return
    payload = json.loads(decision_path.read_text(encoding="utf-8"))
    issued_at_raw = payload.get("issued_at")
    if not issued_at_raw:
        raise GateError(
            "card_missing",
            "persisted DecisionCard is missing issued_at; cannot validate "
            "decision-card digest binding after registry loss",
        )
    issued_at = datetime.fromisoformat(str(issued_at_raw).replace("Z", "+00:00"))
    card = AnyDecisionCardAdapter.validate_python(payload["card"])
    stored = register_decision_card(
        card,
        issuance_timestamp=issued_at,
        server_nonce=str(payload["server_nonce"]),
    )
    if stored.digest != payload["digest"]:
        raise GateError(
            "digest_mismatch",
            "persisted DecisionCard digest does not match rehydrated card metadata",
        )


def _apply_verdict_to_run_state(
    run_state: RunState,
    verdict: OperatorVerdict,
) -> RunState:
    if verdict.verb != "edit":
        return run_state
    return run_state.model_copy(
        update={
            "cache_state": CacheState(
                cache_prefix=json.dumps(verdict.edit_payload, sort_keys=True),
                entries_count=1,
                last_invalidated_at=None,
            )
        }
    )


def _record_cost(
    *,
    trial_id: UUID,
    runs_root: Path,
    trace_root: Any | None,
    allow_offline_cost_report: bool,
) -> Path:
    if trace_root is not None:
        report = measure_trial_cost(str(trial_id), trace_root=trace_root, history=[])
    elif allow_offline_cost_report:
        report = _fallback_cost_report(str(trial_id))
    else:
        report = _fallback_cost_report(str(trial_id))
    return record_trial_cost_report(str(trial_id), report, runs_root=runs_root)


def _merge_artifact_paths(
    existing: list[Path], *candidates: Path | None
) -> list[Path]:
    """Append candidates in order, dropping Nones and duplicates.

    Multi-gate pause-and-resume re-emits stable-path artifacts
    (checkpoint.json, run_summary.yaml, the cost report) at every pause;
    without dedupe the envelope accumulates one duplicate per crossed gate.
    """
    merged: list[Path] = []
    for path in (*existing, *candidates):
        if path is None:
            continue
        candidate = Path(path)
        if candidate not in merged:
            merged.append(candidate)
    return merged


def _has_production_evidence(
    *,
    graph_step_completed: bool,
    specialist_calls: int,
    allow_offline_cost_report: bool,
) -> bool:
    return (
        graph_step_completed
        and specialist_calls > 0
        and _has_live_openai()
        and _has_langsmith_env()
        and not allow_offline_cost_report
    )


def _active_node_handler(compiled_graph: Any, node_id: str) -> Any:
    return compiled_graph.nodes[node_id].runnable.func


def _runner_payload_for_specialist(
    *,
    specialist_id: str,
    directive_path: Path | None,
    bundle_dir: Path | None,
    gate_code: str | None = None,
    production_envelope: ProductionEnvelope | None = None,
    runs_root: Path | None = None,
    trial_id: UUID | None = None,
) -> dict[str, Any] | None:
    """Build runner_supplied_payload for specialists needing runner-side context.

    Story 7a.1 / A-R3 Option A: Texas receives directive/bundle paths when
    directive composition has run.

    Trial-3 finding #10 (2026-06-11): Quinn-R receives the dispatching
    node's ``gate_code`` as ``gate_id`` (its _act selects its body from the
    payload; production dispatch previously supplied no gate context).

    S4 (party review 2026-06-12, manifest-edge-key-projection-s4 LANDED):
    content keys now flow through manifest ``dependency_projections`` — the
    S3 bridge spread is retired (its tombstone test was updated
    deliberately, per Winston S3-A). This seam carries RUNNER CONTEXT only:
    Texas's directive/bundle paths, Quinn-R's gate_id, Gary's run-dir
    ``export_dir``. Content delivery via the seam is forbidden — the
    adapter collision guard refuses any seam key that a projection or
    dependency also delivers.

    Other specialists receive None.
    """
    if specialist_id == "texas" and directive_path is not None and bundle_dir is not None:
        return {
            "directive_path": directive_path.as_posix(),
            "bundle_dir": bundle_dir.as_posix(),
        }
    # The walker passes the CANONICAL id ("quinn_r" via SPECIALIST_ALIASES),
    # not the manifest spelling ("quinn-r") — match both; the hyphen form
    # cost a second live ModeMismatchError('') crash on 2026-06-11.
    if specialist_id in {"quinn_r", "quinn-r"} and gate_code:
        return {"gate_id": gate_code}
    if specialist_id == "gary" and runs_root is not None and trial_id is not None:
        return {
            "export_dir": (runs_root / str(trial_id) / "exports" / "gary").as_posix()
        }
    return None


def _should_invoke_pre_gate_marcus(*, allow_offline_cost_report: bool) -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(
        api_key
        and not api_key.startswith("sk-test")
        and not api_key.startswith("sk-fake")
        and not allow_offline_cost_report
    )


def _pre_gate_slot_values(
    *,
    trial_id: UUID,
    gate_id: str,
    production_envelope: ProductionEnvelope,
    pending_nodes: list[str],
    artifact_paths: list[Path],
) -> dict[str, Any]:
    return {
        "trial_id": str(trial_id),
        "gate_id": gate_id,
        "upstream_contributions": [
            contribution.model_dump(mode="json")
            for contribution in production_envelope.contributions
        ],
        "pending_nodes": pending_nodes,
        "artifact_paths": [path.as_posix() for path in artifact_paths],
    }


def _invoke_pre_gate_marcus_for_gate(
    *,
    gate_id: str,
    trial_id: UUID,
    production_envelope: ProductionEnvelope,
    pending_nodes: list[str],
    artifact_paths: list[Path],
    allow_offline_cost_report: bool,
) -> PreFillProposal | None:
    if not _should_invoke_pre_gate_marcus(
        allow_offline_cost_report=allow_offline_cost_report
    ):
        return None
    slot_values = _pre_gate_slot_values(
        trial_id=trial_id,
        gate_id=gate_id,
        production_envelope=production_envelope,
        pending_nodes=pending_nodes,
        artifact_paths=artifact_paths,
    )
    return pre_gate_marcus.invoke_pre_gate_marcus(
        gate_id=gate_id,
        slot_values=slot_values,
    )


def _pause_at_gate(
    *,
    gate_id: str,
    node_id: str,
    node_index: int,
    manifest: Any,
    trial_id: UUID,
    operator_id: str,
    envelope: ProductionTrialEnvelope,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trace_metadata: dict[str, str],
    specialist_calls: int,
    graph_step_completed: bool,
    manifest_path: Path,
    runs_root: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
) -> ProductionTrialEnvelope:
    """Pause the trial at ``gate_id``: draft, card, checkpoint, persist, return.

    Extracted verbatim from the run_production_trial gate branch (Trial-3
    attempt-3 fix, 2026-06-11) so BOTH walkers share one pause implementation.
    The resume walker previously had no pause path at all — it raised
    GateBypassError at every gate in live mode, making any live trial unable
    to advance from one gate to the next (pause logic existed once, was wired
    once — the A23 fork pattern at function granularity).
    """
    pending = [item.id for item in manifest.nodes[node_index + 1 :]]
    pre_fill = _invoke_pre_gate_marcus_for_gate(
        gate_id=gate_id,
        trial_id=trial_id,
        production_envelope=production_envelope,
        pending_nodes=pending,
        artifact_paths=envelope.artifact_paths,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    if pre_fill is not None:
        child_runs.append(
            _trace_run_for_pre_gate_marcus(
                trial_id=trial_id,
                gate_id=gate_id,
                proposal=pre_fill,
            )
        )
    card = _build_decision_card(
        gate_id=gate_id,
        trial_id=trial_id,
        node_id=node_id,
        operator_id=operator_id,
        pending_nodes=pending,
        artifact_paths=envelope.artifact_paths,
        pre_fill=pre_fill,
        runs_root=runs_root,
    )
    conversation_path = _persist_conversation_turn_if_possible(
        card=card,
        gate_id=gate_id,
        trial_id=trial_id,
        operator_id=operator_id,
        runs_root=runs_root,
    )
    stored = register_decision_card(card)
    checkpoint = _write_checkpoint(
        trial_id=trial_id,
        runs_root=runs_root,
        node_index=node_index,
        gate_id=gate_id,
        run_state=run_state,
        envelope=envelope,
        manifest_path=manifest_path,
        allow_offline_cost_report=allow_offline_cost_report,
        max_specialist_calls=max_specialist_calls,
    )
    decision_path = (
        _run_dir(trial_id, runs_root) / f"decision-card-{gate_id}.json"
    )
    _write_json(
        decision_path,
        {
            "card": card.model_dump(mode="json"),
            "digest": stored.digest,
            "issued_at": stored.issued_at.astimezone(UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "server_nonce": stored.server_nonce,
            "checkpoint_path": checkpoint.as_posix(),
        },
    )
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    # A resume segment can reach the next gate with zero new child runs
    # (e.g., pre-gate-Marcus declined under a non-live key). Preserve the
    # prior segment's persisted values instead of regressing them to None.
    cost_report_path = (
        _record_cost(
            trial_id=trial_id,
            runs_root=runs_root,
            trace_root=trace_root,
            allow_offline_cost_report=allow_offline_cost_report,
        )
        if trace_root is not None or allow_offline_cost_report
        else envelope.cost_report_path
    )
    trace_path = None
    if trace_root is not None:
        trace_path = _run_dir(trial_id, runs_root) / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = (
        str(trial_id) if child_runs else envelope.langsmith_trace_id
    )
    run_summary_path = _emit_run_summary_yaml(
        trial_id=trial_id,
        terminal_gate=gate_id,
        runs_root=runs_root,
        manifest_path=manifest_path,
        langsmith_trace_id=langsmith_trace_id,
    )
    evidence = (
        _has_production_evidence(
            graph_step_completed=graph_step_completed,
            specialist_calls=specialist_calls,
            allow_offline_cost_report=allow_offline_cost_report,
        )
    )
    envelope = envelope.model_copy(
        update={
            "status": "paused-at-gate",
            "paused_gate": gate_id,
            "paused_error_tag": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": (
                "live-specialist-call-recorded"
                if evidence
                else "paused-before-live-specialist-call"
            ),
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                decision_path,
                checkpoint,
                conversation_path,
                cost_report_path,
                trace_path,
                run_summary_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def _dispatch_specialist_at_node(
    *,
    adapter: Any,
    node: NodeSpec,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trial_id: UUID,
    runs_root: Path,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> tuple[ProductionEnvelope, RunState]:
    """The single specialist-dispatch call site shared by both walkers.

    S4 part 2 (SCP 2026-06-11, Winston d.2): the start and resume walkers
    each carried a verbatim copy of this block, and every new invoke kwarg
    broke one copy or the other (finding #10; the projection_map fake
    breakage). One call site means dispatch semantics evolve in one place.
    """
    dependency_map = _resolve_dependency_map(
        node=node,
        specialist_id=specialist_id,
        production_envelope=production_envelope,
    )
    invoke_kwargs: dict[str, Any] = {
        "specialist_id": specialist_id,
        "envelope": production_envelope,
        "dependency_map": dependency_map,
        "cost_usd": 0.0,
        "base_state": run_state,
        "node_id": node.id,
    }
    if node.dependency_projections:
        invoke_kwargs["projection_map"] = node.dependency_projections
    runner_payload = _runner_payload_for_specialist(
        specialist_id=specialist_id,
        directive_path=directive_path,
        bundle_dir=bundle_dir,
        gate_code=node.gate_code,
        production_envelope=production_envelope,
        runs_root=runs_root,
        trial_id=trial_id,
    )
    if runner_payload is not None:
        invoke_kwargs["runner_supplied_payload"] = runner_payload
    production_envelope = adapter.invoke_specialist(**invoke_kwargs)
    run_state = run_state.model_copy(
        update={"production_envelope": production_envelope}
    )
    contribution = production_envelope.get_contribution(specialist_id, node_id=node.id)
    if contribution is not None:
        child_runs.append(
            _trace_run_for_contribution(
                trial_id=trial_id,
                contribution=contribution,
            )
        )
    return production_envelope, run_state


def _pause_at_error(
    *,
    error: SpecialistDispatchError,
    node_id: str,
    node_index: int,
    specialist_id: str,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trace_metadata: dict[str, str],
    last_gate_crossed: str | None,
    graph_step_completed: bool,
    specialist_calls: int,
    manifest_path: Path,
    runs_root: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> ProductionTrialEnvelope:
    """Pause the trial at a typed dispatch failure instead of killing the cycle.

    S4 part 2 (Amelia trap 1): a transient Gamma/Kling/bridge blip previously
    unwound the whole walk, so the operator paid a fresh cycle to retry one
    node. The error-pause persists everything ``trial recover`` needs to retry
    the FAILED node itself — note ``node_index`` is stored unshifted, unlike
    the gate checkpoint's ``next_node_index`` (+1), because recovery re-enters
    at the failed node rather than past a decided gate.
    """
    LOGGER.error(
        "dispatch error at manifest node %s (specialist %s): [%s] %s — "
        "pausing trial %s for recovery",
        node_id,
        specialist_id,
        error.tag,
        error,
        trial_id,
    )
    error_pause_path = _run_dir(trial_id, runs_root) / "error-pause.json"
    _write_json(
        error_pause_path,
        {
            "trial_id": str(trial_id),
            "node_index": node_index,
            "node_id": node_id,
            "specialist_id": specialist_id,
            "tag": error.tag,
            "message": str(error),
            "last_gate_crossed": last_gate_crossed,
            "run_state": run_state.model_dump(mode="json"),
            "runner": {
                "corpus_path": envelope.corpus_path,
                "preset": envelope.preset,
                "operator_id": envelope.operator_id,
                "manifest_path": manifest_path.as_posix(),
                "allow_offline_cost_report": allow_offline_cost_report,
                "max_specialist_calls": max_specialist_calls,
                "directive_path": directive_path.as_posix() if directive_path else None,
                "bundle_dir": bundle_dir.as_posix() if bundle_dir else None,
            },
        },
    )
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    # Spend already incurred this segment is recorded at the pause, exactly
    # as _pause_at_gate does — an error pause must not orphan cost evidence.
    cost_report_path = (
        _record_cost(
            trial_id=trial_id,
            runs_root=runs_root,
            trace_root=trace_root,
            allow_offline_cost_report=allow_offline_cost_report,
        )
        if trace_root is not None or allow_offline_cost_report
        else envelope.cost_report_path
    )
    trace_path = None
    if trace_root is not None:
        trace_path = _run_dir(trial_id, runs_root) / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = str(trial_id) if child_runs else envelope.langsmith_trace_id
    evidence = _has_production_evidence(
        graph_step_completed=graph_step_completed,
        specialist_calls=specialist_calls,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    envelope = envelope.model_copy(
        update={
            "status": "paused-at-error",
            "paused_gate": None,
            "paused_error_tag": error.tag,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": (
                f"paused-at-dispatch-error:{error.tag}"
            ),
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                error_pause_path,
                cost_report_path,
                trace_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def run_production_trial(
    corpus_path: Path,
    preset: Literal["production", "explore"],
    operator_id: str,
    trial_id: UUID | None = None,
    *,
    runs_root: Path = RUNS_ROOT,
    allow_offline_cost_report: bool = False,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    max_specialist_calls: int = 1,
    pause_at_gates: bool = True,
    directive_path: Path | None = None,
) -> ProductionTrialEnvelope:
    """Register, compose, and start a production trial.

    ``directive_path`` (Story 7a.1): when provided, the runner derives
    ``bundle_dir = run_dir / "bundle"`` and threads both to Texas's _act
    via ``ProductionDispatchAdapter.invoke_specialist(runner_supplied_payload=...)``
    so Texas's ``dispatch_retrieval`` is called with non-None args (closing
    trial-475 silent-bypass at line 34-40 of retrieval_dispatch.py).
    """
    if not corpus_path.exists():
        raise FileNotFoundError(f"trial input path does not exist: {corpus_path}")

    effective_trial_id = trial_id or uuid4()
    composer_run_dir = runs_root / str(effective_trial_id)
    bundle_dir: Path | None = None
    if directive_path is not None:
        bundle_dir = composer_run_dir / "bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
    production_envelope = ProductionEnvelope(trial_id=effective_trial_id)
    envelope = ProductionTrialEnvelope(
        trial_id=effective_trial_id,
        preset=preset,
        corpus_path=corpus_path.as_posix(),
        operator_id=operator_id,
        started_at=_now(),
        status="registered",
        production_clone_launch_evidence=False,
        production_clone_launch_evidence_reason="registered-no-specialist-fired",
        production_envelope=production_envelope,
    )
    _persist_envelope(envelope, runs_root)

    manifest = load_manifest(manifest_path)
    active_gate_ids = production_gate_ids(manifest)
    graph = compile_run_graph(manifest)
    adapter = ProductionDispatchAdapter()
    run_state = RunState(
        run_id=effective_trial_id,
        status="running",
        graph_version=DEFAULT_GRAPH_VERSION,
        cache_state=CacheState(
            cache_prefix=json.dumps(
                {
                    "trial_id": str(effective_trial_id),
                    "corpus_path": corpus_path.as_posix(),
                    "preset": preset,
                },
                sort_keys=True,
            ),
        ),
        production_envelope=production_envelope,
    )
    envelope = envelope.model_copy(update={"status": "in-flight"})
    _persist_envelope(envelope, runs_root)

    child_runs: list[SimpleNamespace] = []
    specialist_calls = 0
    graph_step_completed = False
    last_gate_crossed: str | None = None
    trace_metadata: dict[str, str]

    with _trial_trace_context(
        trial_id=effective_trial_id,
        preset=preset,
        operator_id=operator_id,
    ) as trace_metadata:
        for index, node in enumerate(manifest.nodes):
            handler = _active_node_handler(graph, node.id)
            node_kind = getattr(handler, "__production_node_kind__", None)
            if node_kind == "gate":
                gate_id = handler.__production_gate_id__
                if not pause_at_gates:
                    if gate_id in active_gate_ids and not allow_offline_cost_report:
                        raise GateBypassError(
                            f"refused silent bypass of gate {gate_id} at manifest node {node.id}"
                        )
                    last_gate_crossed = gate_id
                    graph_step_completed = True
                    continue
                # S5 criterion 7 (operator-ratified 2026-06-12): storyboard
                # review gates publish their ONLINE interactive pack BEFORE
                # the pause — a storyboard gate without its review surface is
                # the attempt-4 quality-theater class. Publish failure
                # error-pauses (recoverable; retry re-enters this gate node).
                try:
                    storyboard_publisher.publish_storyboard_for_gate(
                        gate_id=gate_id,
                        trial_id=str(effective_trial_id),
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id="storyboard_publisher",
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                return _pause_at_gate(
                    gate_id=gate_id,
                    node_id=node.id,
                    node_index=index,
                    manifest=manifest,
                    trial_id=effective_trial_id,
                    operator_id=operator_id,
                    envelope=envelope,
                    production_envelope=production_envelope,
                    run_state=run_state,
                    child_runs=child_runs,
                    trace_metadata=trace_metadata,
                    specialist_calls=specialist_calls,
                    graph_step_completed=graph_step_completed,
                    manifest_path=manifest_path,
                    runs_root=runs_root,
                    allow_offline_cost_report=allow_offline_cost_report,
                    max_specialist_calls=max_specialist_calls,
                )

            if (
                node_kind == "orchestration"
                and node.id in package_builders.BUILDER_NODE_IDS
                and _has_live_openai()
                and not allow_offline_cost_report
            ):
                # S3 (SCP 2026-06-11): §06 builds the Gary slide-brief
                # package as a first-class contribution at its own node
                # (pre_gate_marcus runner-invocation pattern; deterministic,
                # so it runs on the live path only, mirroring specialists).
                # WAVE-0 tranche 2 (2026-06-17): a BuilderInputError starvation
                # now error-pauses recoverably (the last live-walk dispatch leg
                # to join the family) instead of killing the trial — the pause
                # halts BEFORE the next gate, so no quality-theater path opens
                # (Murat/John adjudication; S5-crit-5 contract preserved).
                try:
                    production_envelope = package_builders.run_builder_node(
                        node_id=node.id,
                        production_envelope=production_envelope,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=package_builders.BUILDER_SPECIALIST_ID,
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if node_kind == "specialist" and specialist_calls < max_specialist_calls:
                specialist_id = handler.__production_specialist_id__
                # S2 per-node keying (SCP 2026-06-11): the skip rule guards
                # node revisits, not specialist revisits — the per-specialist
                # Path-Z rule silently skipped irene_pass1's §05/§05B jobs.
                if production_envelope.get_contribution(specialist_id, node_id=node.id) is not None:
                    LOGGER.info(
                        "manifest node %s (specialist %s) already carries its "
                        "contribution; node re-dispatch skipped per S2 "
                        "per-node idempotency contract",
                        node.id,
                        specialist_id,
                    )
                    graph_step_completed = True
                    continue
                if _has_live_openai() and not allow_offline_cost_report:
                    try:
                        production_envelope, run_state = _dispatch_specialist_at_node(
                            adapter=adapter,
                            node=node,
                            specialist_id=specialist_id,
                            production_envelope=production_envelope,
                            run_state=run_state,
                            child_runs=child_runs,
                            trial_id=effective_trial_id,
                            runs_root=runs_root,
                            directive_path=directive_path,
                            bundle_dir=bundle_dir,
                        )
                    except SpecialistDispatchError as exc:
                        return _pause_at_error(
                            error=exc,
                            node_id=node.id,
                            node_index=index,
                            specialist_id=specialist_id,
                            trial_id=effective_trial_id,
                            envelope=envelope,
                            production_envelope=production_envelope,
                            run_state=run_state,
                            child_runs=child_runs,
                            trace_metadata=trace_metadata,
                            last_gate_crossed=last_gate_crossed,
                            graph_step_completed=graph_step_completed,
                            specialist_calls=specialist_calls,
                            manifest_path=manifest_path,
                            runs_root=runs_root,
                            allow_offline_cost_report=allow_offline_cost_report,
                            max_specialist_calls=max_specialist_calls,
                            directive_path=directive_path,
                            bundle_dir=bundle_dir,
                        )
                    specialist_calls += 1
                graph_step_completed = True

    completed_at = _now()
    trace_root = _trace_root(
        trial_id=effective_trial_id,
        metadata=trace_metadata,
        child_runs=child_runs,
    ) if child_runs else None
    cost_report_path = _record_cost(
        trial_id=effective_trial_id,
        runs_root=runs_root,
        trace_root=trace_root,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    trace_path = None
    if trace_root is not None:
        trace_path = _run_dir(effective_trial_id, runs_root) / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = str(effective_trial_id) if child_runs else None
    run_summary_path = _emit_run_summary_yaml(
        trial_id=effective_trial_id,
        # Last gate actually traversed this walk; "G4" only as the legacy
        # fallback for manifests that carry no gate nodes at all.
        terminal_gate=last_gate_crossed or "G4",
        runs_root=runs_root,
        manifest_path=manifest_path,
        langsmith_trace_id=langsmith_trace_id,
    )
    engagement_report_path = _emit_engagement_decay_report(
        trial_id=effective_trial_id,
        child_runs=child_runs,
    )
    evidence = (
        _has_production_evidence(
            graph_step_completed=graph_step_completed,
            specialist_calls=specialist_calls,
            allow_offline_cost_report=allow_offline_cost_report,
        )
    )
    reason = "live-specialist-call-recorded" if evidence else "no-live-specialist-call-recorded"
    envelope = envelope.model_copy(
        update={
            "status": "completed",
            "completed_at": completed_at,
            "paused_gate": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                cost_report_path,
                trace_path,
                run_summary_path,
                engagement_report_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def resume_production_trial(
    *,
    trial_id: UUID,
    verdict: OperatorVerdict,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
) -> ProductionTrialEnvelope:
    """Validate a gate verdict and continue the persisted trial past the gate."""
    run_dir = _run_dir(trial_id, runs_root)
    envelope = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text(encoding="utf-8"),
        # Witness-mode lifecycle invariants: violations on persisted state are
        # recorded to the run's anomaly sidecar, never raised (S4p2 follow-on;
        # witness->strict flip is a post-S5 ceremony).
        context={"anomaly_sink": run_dir / "anomalies.jsonl"},
    )
    if envelope.status != "paused-at-gate":
        raise RuntimeError(
            f"trial {trial_id} is not paused at a gate; status={envelope.status!r}"
        )
    if envelope.paused_gate != verdict.gate_id:
        raise GateError(
            "checkpoint_gate_mismatch",
            f"verdict gate_id={verdict.gate_id} does not match paused_gate={envelope.paused_gate}",
        )
    if envelope.production_envelope.schema_version == "production-envelope.v1":
        raise LegacyEnvelopeSchemaError(
            f"trial {trial_id} carries a production-envelope.v1 (per-specialist "
            "keyed) envelope; v1 runs are not resumable after the S2 per-node "
            "keying migration (SCP 2026-06-11) — relaunch as a new cycle; the "
            "run dir stays frozen as evidence."
        )
    _ensure_decision_card_registered_from_disk(
        trial_id=trial_id,
        gate_id=verdict.gate_id,
        run_dir=run_dir,
    )
    checkpoint_path = run_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if checkpoint.get("trial_id") != str(trial_id) or checkpoint.get("gate_id") != verdict.gate_id:
        raise GateError(
            "checkpoint_gate_mismatch",
            "persisted checkpoint does not match the accepted verdict gate",
        )
    command = resume_from_verdict(verdict)
    runner = checkpoint.get("runner") or {}
    run_state = RunState.model_validate_json(json.dumps(checkpoint["run_state"]))
    run_state = run_state.model_copy(
        update={"production_envelope": envelope.production_envelope}
    )
    run_state = _apply_verdict_to_run_state(run_state, verdict)
    _write_json(
        run_dir / "resume-command.json",
        {
            "command": command.resume,
            "run_state": run_state.model_dump(mode="json"),
        },
    )
    if verdict.verb == "reject":
        manifest_path = Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH)
        run_summary_path = _emit_run_summary_yaml(
            trial_id=trial_id,
            terminal_gate=verdict.gate_id,
            runs_root=runs_root,
            manifest_path=manifest_path,
            langsmith_trace_id=envelope.langsmith_trace_id,
        )
        updated = envelope.model_copy(
            update={
                "status": "failed",
                "completed_at": _now(),
                "production_clone_launch_evidence_reason": "operator-rejected-at-gate",
                "artifact_paths": _merge_artifact_paths(
                    envelope.artifact_paths, run_summary_path
                ),
            }
        )
        _persist_envelope(updated, runs_root)
        return updated

    manifest_path = Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH)
    resumed_max_specialist_calls = (
        max_specialist_calls
        if max_specialist_calls is not None
        else int(runner.get("max_specialist_calls") or 1)
    )
    return _continue_production_walk(
        trial_id=trial_id,
        envelope=envelope,
        run_state=run_state,
        runner=runner,
        manifest_path=manifest_path,
        runs_root=runs_root,
        start_index=int(checkpoint["next_node_index"]),
        # The gate just approved is the last crossed until the walk traverses
        # further gates (offline mode); live mode pauses at the next gate.
        last_gate_crossed=verdict.gate_id,
        max_specialist_calls=resumed_max_specialist_calls,
        extra_artifacts=(run_dir / "resume-command.json",),
    )


def recover_production_trial(
    *,
    trial_id: UUID,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
) -> ProductionTrialEnvelope:
    """Continue an error-paused trial from the failed node — no verdict needed.

    S4 part 2 (SCP 2026-06-11, Amelia trap 1): the recovery counterpart to
    ``resume_production_trial``. Gates carry operator verdicts; dispatch-error
    pauses carry none — the operator (or a wrapper) fixes the transient cause
    and re-enters the walk at the node that failed. Idempotent with respect to
    completed work: every prior contribution is per-node keyed, so recovery
    re-dispatches only the failed node and onward.
    """
    run_dir = _run_dir(trial_id, runs_root)
    envelope = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text(encoding="utf-8"),
        # Witness-mode lifecycle invariants: violations on persisted state are
        # recorded to the run's anomaly sidecar, never raised (S4p2 follow-on;
        # witness->strict flip is a post-S5 ceremony).
        context={"anomaly_sink": run_dir / "anomalies.jsonl"},
    )
    if envelope.status != "paused-at-error":
        raise RuntimeError(
            f"trial {trial_id} is not paused at a dispatch error; "
            f"status={envelope.status!r} — `trial recover` only applies to "
            "error-paused runs (gate pauses take `trial resume` + a verdict)"
        )
    if envelope.production_envelope.schema_version == "production-envelope.v1":
        raise LegacyEnvelopeSchemaError(
            f"trial {trial_id} carries a production-envelope.v1 (per-specialist "
            "keyed) envelope; v1 runs are not recoverable after the S2 per-node "
            "keying migration (SCP 2026-06-11) — relaunch as a new cycle; the "
            "run dir stays frozen as evidence."
        )
    error_pause_path = run_dir / "error-pause.json"
    error_pause = json.loads(error_pause_path.read_text(encoding="utf-8"))
    if error_pause.get("trial_id") != str(trial_id):
        raise RuntimeError(
            "persisted error-pause record does not match the trial being "
            f"recovered: {error_pause.get('trial_id')!r} != {trial_id}"
        )
    runner = error_pause.get("runner") or {}
    run_state = RunState.model_validate_json(json.dumps(error_pause["run_state"]))
    run_state = run_state.model_copy(
        update={"production_envelope": envelope.production_envelope}
    )
    directive_path_raw = runner.get("directive_path")
    bundle_dir_raw = runner.get("bundle_dir")
    return _continue_production_walk(
        trial_id=trial_id,
        envelope=envelope,
        run_state=run_state,
        runner=runner,
        manifest_path=Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH),
        runs_root=runs_root,
        # Unshifted on purpose: recovery retries the failed node itself.
        start_index=int(error_pause["node_index"]),
        last_gate_crossed=error_pause.get("last_gate_crossed"),
        max_specialist_calls=(
            max_specialist_calls
            if max_specialist_calls is not None
            else int(runner.get("max_specialist_calls") or 1)
        ),
        directive_path=Path(directive_path_raw) if directive_path_raw else None,
        bundle_dir=Path(bundle_dir_raw) if bundle_dir_raw else None,
        non_evidence_reason="recovered-after-error-pause",
    )


def _continue_production_walk(
    *,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    run_state: RunState,
    runner: dict[str, Any],
    manifest_path: Path,
    runs_root: Path,
    start_index: int,
    last_gate_crossed: str | None,
    max_specialist_calls: int,
    directive_path: Path | None = None,
    bundle_dir: Path | None = None,
    extra_artifacts: tuple[Path, ...] = (),
    non_evidence_reason: str = "resumed-after-gate",
) -> ProductionTrialEnvelope:
    """Walk manifest nodes from ``start_index`` to the next pause or completion.

    Shared by ``resume_production_trial`` (post-verdict) and
    ``recover_production_trial`` (post-error-pause) so the continuation walk
    exists exactly once — the resume walker was already the A23 second copy
    of the start walk; a third copy for recovery was vetoed (S4 part 2,
    Winston d.2).
    """
    run_dir = _run_dir(trial_id, runs_root)
    manifest = load_manifest(manifest_path)
    graph = compile_run_graph(manifest)
    adapter = ProductionDispatchAdapter()
    production_envelope = envelope.production_envelope
    child_runs = [
        _trace_run_for_contribution(trial_id=trial_id, contribution=contribution)
        for contribution in production_envelope.contributions
        # Deterministic §06 builder rows carry no LLM spend and no pricing
        # entry; in-segment they are never traced as child runs either —
        # seeding them here crashed cost recording on any continuation past
        # a builder node (latent since S3; surfaced by the S4p2 recover walk).
        if contribution.model_used != package_builders.BUILDER_MODEL_MARKER
    ]
    specialist_calls = 0
    allow_offline_cost_report = bool(runner.get("allow_offline_cost_report", False))
    graph_step_completed = bool(production_envelope.contributions)

    with _trial_trace_context(
        trial_id=trial_id,
        preset=runner.get("preset") or envelope.preset,
        operator_id=runner.get("operator_id") or envelope.operator_id,
    ) as trace_metadata:
        for index, node in enumerate(manifest.nodes[start_index:], start=start_index):
            handler = _active_node_handler(graph, node.id)
            node_kind = getattr(handler, "__production_node_kind__", None)
            if node_kind == "gate":
                gate_id = handler.__production_gate_id__
                if allow_offline_cost_report:
                    # Offline runs traverse gates without pausing (existing
                    # contract); keep the pre-gate draft + trace append the
                    # prior code performed before continuing.
                    pending = [item.id for item in manifest.nodes[index + 1 :]]
                    pre_fill = _invoke_pre_gate_marcus_for_gate(
                        gate_id=gate_id,
                        trial_id=trial_id,
                        production_envelope=production_envelope,
                        pending_nodes=pending,
                        artifact_paths=envelope.artifact_paths,
                        allow_offline_cost_report=allow_offline_cost_report,
                    )
                    if pre_fill is not None:
                        child_runs.append(
                            _trace_run_for_pre_gate_marcus(
                                trial_id=trial_id,
                                gate_id=gate_id,
                                proposal=pre_fill,
                            )
                        )
                    last_gate_crossed = gate_id
                    graph_step_completed = True
                    continue
                # Trial-3 attempt-3 fix (2026-06-11): live resume previously
                # raised GateBypassError at EVERY gate — the pause machinery
                # existed only in the start walker, so no live trial could
                # ever advance gate-to-gate. The guard is deliberately
                # converted to the shared pause (the decided gate is never
                # revisited: start_index = checkpoint.next_node_index is
                # already past it, so this only fires at genuinely new gates).
                # S5 criterion 7: storyboard gates publish their online pack
                # before pausing — see start-walker note.
                try:
                    storyboard_publisher.publish_storyboard_for_gate(
                        gate_id=gate_id,
                        trial_id=str(trial_id),
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id="storyboard_publisher",
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                return _pause_at_gate(
                    gate_id=gate_id,
                    node_id=node.id,
                    node_index=index,
                    manifest=manifest,
                    trial_id=trial_id,
                    operator_id=runner.get("operator_id") or envelope.operator_id,
                    envelope=envelope,
                    production_envelope=production_envelope,
                    run_state=run_state,
                    child_runs=child_runs,
                    trace_metadata=trace_metadata,
                    specialist_calls=len(production_envelope.contributions),
                    graph_step_completed=graph_step_completed,
                    manifest_path=manifest_path,
                    runs_root=runs_root,
                    allow_offline_cost_report=allow_offline_cost_report,
                    max_specialist_calls=max_specialist_calls,
                )

            if (
                node_kind == "orchestration"
                and node.id in package_builders.BUILDER_NODE_IDS
                and _has_live_openai()
                and not allow_offline_cost_report
            ):
                # S3 §06 package builder — see start-walker note. WAVE-0
                # tranche 2 (2026-06-17): error-pause wrap mirrored onto the
                # recover walker so a §06 starvation pauses recoverably here
                # too — the recover path is the one most likely to re-enter a
                # still-starved node, so an unwrapped sibling would let it kill.
                try:
                    production_envelope = package_builders.run_builder_node(
                        node_id=node.id,
                        production_envelope=production_envelope,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=package_builders.BUILDER_SPECIALIST_ID,
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "specialist"
                and specialist_calls < max_specialist_calls
            ):
                specialist_id = handler.__production_specialist_id__
                # S2 per-node keying — see start-walker note.
                if production_envelope.get_contribution(specialist_id, node_id=node.id) is not None:
                    LOGGER.info(
                        "manifest node %s (specialist %s) already carries its "
                        "contribution; node re-dispatch skipped per S2 "
                        "per-node idempotency contract",
                        node.id,
                        specialist_id,
                    )
                    graph_step_completed = True
                    continue
                if _has_live_openai() and not allow_offline_cost_report:
                    try:
                        production_envelope, run_state = _dispatch_specialist_at_node(
                            adapter=adapter,
                            node=node,
                            specialist_id=specialist_id,
                            production_envelope=production_envelope,
                            run_state=run_state,
                            child_runs=child_runs,
                            trial_id=trial_id,
                            runs_root=runs_root,
                            directive_path=directive_path,
                            bundle_dir=bundle_dir,
                        )
                    except SpecialistDispatchError as exc:
                        return _pause_at_error(
                            error=exc,
                            node_id=node.id,
                            node_index=index,
                            specialist_id=specialist_id,
                            trial_id=trial_id,
                            envelope=envelope,
                            production_envelope=production_envelope,
                            run_state=run_state,
                            child_runs=child_runs,
                            trace_metadata=trace_metadata,
                            last_gate_crossed=last_gate_crossed,
                            graph_step_completed=graph_step_completed,
                            specialist_calls=specialist_calls,
                            manifest_path=manifest_path,
                            runs_root=runs_root,
                            allow_offline_cost_report=allow_offline_cost_report,
                            max_specialist_calls=max_specialist_calls,
                            directive_path=directive_path,
                            bundle_dir=bundle_dir,
                        )
                    specialist_calls += 1
                graph_step_completed = True

    completed_at = _now()
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    cost_report_path = _record_cost(
        trial_id=trial_id,
        runs_root=runs_root,
        trace_root=trace_root,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    trace_path = None
    if trace_root is not None:
        trace_path = run_dir / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = (
        str(trial_id) if child_runs else envelope.langsmith_trace_id
    )
    run_summary_path = _emit_run_summary_yaml(
        trial_id=trial_id,
        # "G4" only as the legacy fallback for walks that crossed no gate at
        # all (e.g., recovery of a pre-G1 error pause in offline mode).
        terminal_gate=last_gate_crossed or "G4",
        runs_root=runs_root,
        manifest_path=manifest_path,
        langsmith_trace_id=langsmith_trace_id,
    )
    engagement_report_path = _emit_engagement_decay_report(
        trial_id=trial_id,
        child_runs=child_runs,
    )
    evidence = _has_production_evidence(
        graph_step_completed=graph_step_completed,
        specialist_calls=len(production_envelope.contributions),
        allow_offline_cost_report=allow_offline_cost_report,
    )
    reason = "live-specialist-call-recorded" if evidence else non_evidence_reason
    updated = envelope.model_copy(
        update={
            "status": "completed",
            "completed_at": completed_at,
            "paused_gate": None,
            "paused_error_tag": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                *extra_artifacts,
                cost_report_path,
                trace_path,
                run_summary_path,
                engagement_report_path,
            ),
        }
    )
    _persist_envelope(updated, runs_root)
    return updated


__all__ = [
    "DEFAULT_MANIFEST_PATH",
    "GateBypassError",
    "MissingUpstreamContributionError",
    "recover_production_trial",
    "resume_production_trial",
    "run_production_trial",
]
