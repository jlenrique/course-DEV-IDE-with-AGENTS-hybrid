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
    pre_gate_marcus,
    specialist_summary_writer,
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
        if production_envelope.get_contribution(upstream_specialist_id) is not None:
            normalized[downstream_input_key] = upstream_specialist_id
            continue
        canonical = _canonical_dependency_specialist_id(upstream_specialist_id)
        normalized[downstream_input_key] = (
            canonical
            if production_envelope.get_contribution(canonical) is not None
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
        if production_envelope.get_contribution(upstream_specialist_id) is None:
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
) -> dict[str, str] | None:
    """Build runner_supplied_payload for Texas when directive composition has run.

    Story 7a.1 / A-R3 Option A: only Texas receives the runner-supplied keys.
    Other specialists receive None.
    """
    if specialist_id != "texas" or directive_path is None or bundle_dir is None:
        return None
    return {
        "directive_path": directive_path.as_posix(),
        "bundle_dir": bundle_dir.as_posix(),
    }


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
                    graph_step_completed = True
                    continue
                pending = [item.id for item in manifest.nodes[index + 1 :]]
                pre_fill = _invoke_pre_gate_marcus_for_gate(
                    gate_id=gate_id,
                    trial_id=effective_trial_id,
                    production_envelope=production_envelope,
                    pending_nodes=pending,
                    artifact_paths=envelope.artifact_paths,
                    allow_offline_cost_report=allow_offline_cost_report,
                )
                if pre_fill is not None:
                    child_runs.append(
                        _trace_run_for_pre_gate_marcus(
                            trial_id=effective_trial_id,
                            gate_id=gate_id,
                            proposal=pre_fill,
                        )
                    )
                card = _build_decision_card(
                    gate_id=gate_id,
                    trial_id=effective_trial_id,
                    node_id=node.id,
                    operator_id=operator_id,
                    pending_nodes=pending,
                    artifact_paths=envelope.artifact_paths,
                    pre_fill=pre_fill,
                    runs_root=runs_root,
                )
                conversation_path = _persist_conversation_turn_if_possible(
                    card=card,
                    gate_id=gate_id,
                    trial_id=effective_trial_id,
                    operator_id=operator_id,
                    runs_root=runs_root,
                )
                stored = register_decision_card(card)
                checkpoint = _write_checkpoint(
                    trial_id=effective_trial_id,
                    runs_root=runs_root,
                    node_index=index,
                    gate_id=gate_id,
                    run_state=run_state,
                    envelope=envelope,
                    manifest_path=manifest_path,
                    allow_offline_cost_report=allow_offline_cost_report,
                    max_specialist_calls=max_specialist_calls,
                )
                decision_path = (
                    _run_dir(effective_trial_id, runs_root)
                    / f"decision-card-{gate_id}.json"
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
                        trial_id=effective_trial_id,
                        metadata=trace_metadata,
                        child_runs=child_runs,
                    )
                    if child_runs
                    else None
                )
                cost_report_path = (
                    _record_cost(
                        trial_id=effective_trial_id,
                        runs_root=runs_root,
                        trace_root=trace_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                    )
                    if trace_root is not None or allow_offline_cost_report
                    else None
                )
                trace_path = None
                if trace_root is not None:
                    trace_path = _run_dir(effective_trial_id, runs_root) / "trace-fixture.json"
                    _write_json(trace_path, _trace_to_json(trace_root))
                langsmith_trace_id = str(effective_trial_id) if child_runs else None
                run_summary_path = _emit_run_summary_yaml(
                    trial_id=effective_trial_id,
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
                        "langsmith_trace_id": langsmith_trace_id,
                        "production_clone_launch_evidence": evidence,
                        "production_clone_launch_evidence_reason": (
                            "live-specialist-call-recorded"
                            if evidence
                            else "paused-before-live-specialist-call"
                        ),
                        "production_envelope": production_envelope,
                        "cost_report_path": cost_report_path,
                        "artifact_paths": [
                            *envelope.artifact_paths,
                            decision_path,
                            checkpoint,
                            *([conversation_path] if conversation_path is not None else []),
                            *([cost_report_path] if cost_report_path is not None else []),
                            *([trace_path] if trace_path is not None else []),
                            run_summary_path,
                        ],
                    }
                )
                _persist_envelope(envelope, runs_root)
                return envelope

            if node_kind == "specialist" and specialist_calls < max_specialist_calls:
                specialist_id = handler.__production_specialist_id__
                if production_envelope.get_contribution(specialist_id) is not None:
                    LOGGER.info(
                        "specialist %s was reached again at manifest node %s but "
                        "the production envelope already contains its contribution; "
                        "new contribution skipped per Slab 6.1 Path Z first-"
                        "contribution-wins contract",
                        specialist_id,
                        node.id,
                    )
                    graph_step_completed = True
                    continue
                if _has_live_openai() and not allow_offline_cost_report:
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
                    }
                    runner_payload = _runner_payload_for_specialist(
                        specialist_id=specialist_id,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                    if runner_payload is not None:
                        invoke_kwargs["runner_supplied_payload"] = runner_payload
                    production_envelope = adapter.invoke_specialist(**invoke_kwargs)
                    run_state = run_state.model_copy(
                        update={"production_envelope": production_envelope}
                    )
                    contribution = production_envelope.get_contribution(specialist_id)
                    if contribution is not None:
                        child_runs.append(
                            _trace_run_for_contribution(
                                trial_id=effective_trial_id,
                                contribution=contribution,
                            )
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
        terminal_gate="G4",
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
            "artifact_paths": [
                *envelope.artifact_paths,
                cost_report_path,
                *([trace_path] if trace_path is not None else []),
                run_summary_path,
                engagement_report_path,
            ],
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
        (run_dir / "run.json").read_text(encoding="utf-8")
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
                "artifact_paths": [*envelope.artifact_paths, run_summary_path],
            }
        )
        _persist_envelope(updated, runs_root)
        return updated

    manifest_path = Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH)
    manifest = load_manifest(manifest_path)
    graph = compile_run_graph(manifest)
    adapter = ProductionDispatchAdapter()
    production_envelope = envelope.production_envelope
    child_runs = [
        _trace_run_for_contribution(trial_id=trial_id, contribution=contribution)
        for contribution in production_envelope.contributions
    ]
    specialist_calls = 0
    resumed_max_specialist_calls = (
        max_specialist_calls
        if max_specialist_calls is not None
        else int(runner.get("max_specialist_calls") or 1)
    )
    allow_offline_cost_report = bool(runner.get("allow_offline_cost_report", False))
    start_index = int(checkpoint["next_node_index"])
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
                if not allow_offline_cost_report:
                    raise GateBypassError(
                        f"refused silent bypass of gate {gate_id} at manifest node {node.id}"
                    )
                graph_step_completed = True
                continue

            if (
                node_kind == "specialist"
                and specialist_calls < resumed_max_specialist_calls
            ):
                specialist_id = handler.__production_specialist_id__
                if production_envelope.get_contribution(specialist_id) is not None:
                    LOGGER.info(
                        "specialist %s was reached again at manifest node %s but "
                        "the production envelope already contains its contribution; "
                        "new contribution skipped per Slab 6.1 Path Z first-"
                        "contribution-wins contract",
                        specialist_id,
                        node.id,
                    )
                    graph_step_completed = True
                    continue
                if _has_live_openai() and not allow_offline_cost_report:
                    dependency_map = _resolve_dependency_map(
                        node=node,
                        specialist_id=specialist_id,
                        production_envelope=production_envelope,
                    )
                    production_envelope = adapter.invoke_specialist(
                        specialist_id=specialist_id,
                        envelope=production_envelope,
                        dependency_map=dependency_map,
                        cost_usd=0.0,
                        base_state=run_state,
                    )
                    run_state = run_state.model_copy(
                        update={"production_envelope": production_envelope}
                    )
                    contribution = production_envelope.get_contribution(specialist_id)
                    if contribution is not None:
                        child_runs.append(
                            _trace_run_for_contribution(
                                trial_id=trial_id,
                                contribution=contribution,
                            )
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
    langsmith_trace_id = str(trial_id) if child_runs else None
    run_summary_path = _emit_run_summary_yaml(
        trial_id=trial_id,
        terminal_gate="G4",
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
    reason = "live-specialist-call-recorded" if evidence else "resumed-after-gate"
    updated = envelope.model_copy(
        update={
            "status": "completed",
            "completed_at": completed_at,
            "paused_gate": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": [
                *envelope.artifact_paths,
                run_dir / "resume-command.json",
                cost_report_path,
                *([trace_path] if trace_path is not None else []),
                run_summary_path,
                engagement_report_path,
            ],
        }
    )
    _persist_envelope(updated, runs_root)
    return updated


__all__ = [
    "DEFAULT_MANIFEST_PATH",
    "GateBypassError",
    "MissingUpstreamContributionError",
    "resume_production_trial",
    "run_production_trial",
]
