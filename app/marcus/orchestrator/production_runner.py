"""Production-graph runner composition layer for migrated trials."""

from __future__ import annotations

import json
import logging
import os
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from uuid import UUID, uuid4

from app.gates.errors import GateError
from app.gates.resume_api import (
    get_registered_decision_card,
    register_decision_card,
    resume_from_verdict,
)
from app.manifest.compiler import (
    PRODUCTION_GATE_IDS,
    _canonical_specialist_id,
    compile_run_graph,
)
from app.manifest.loader import load as load_manifest
from app.manifest.schema import NodeSpec
from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.models.decision_cards import (
    AnyDecisionCardAdapter,
    DecisionCardMeta,
    G1Card,
    G2CCard,
    G3Card,
    G4Card,
)
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


def _build_decision_card(
    *,
    gate_id: str,
    trial_id: UUID,
    node_id: str,
    operator_id: str,
    pending_nodes: list[str],
    artifact_paths: list[Path],
) -> Any:
    common = {
        "card_id": uuid4(),
        "trial_id": trial_id,
        "created_at": _now(),
        "drafted_proposal": {"node_id": node_id, "operator_id": operator_id},
        "evidence": [{"kind": "production-runner", "node_id": node_id}],
        "risks": [],
        "verb": "approve",
        "meta": _card_meta(node_id),
    }
    if gate_id == "G1":
        return G1Card(
            **common,
            trial_summary="Production graph reached Gate 1.",
            opened_by="production_runner",
            next_nodes=pending_nodes[:3],
        )
    if gate_id == "G2C":
        return G2CCard(
            **common,
            readiness_status="ready",
            blocking_issues=[],
            ready_nodes=pending_nodes[:3],
        )
    if gate_id == "G3":
        return G3Card(
            **common,
            progress_percent=50.0,
            active_node_id=node_id,
            pending_nodes=pending_nodes,
            operator_prompt="Approve, edit, or reject the in-flight package.",
        )
    if gate_id == "G4":
        return G4Card(
            **common,
            final_status="partial",
            artifact_paths=[path.as_posix() for path in artifact_paths],
            outcome_summary="Production graph reached closeout review.",
        )
    raise RuntimeError(f"unsupported production gate id: {gate_id}")


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
) -> ProductionTrialEnvelope:
    """Register, compose, and start a production trial."""
    if not corpus_path.exists():
        raise FileNotFoundError(f"trial input path does not exist: {corpus_path}")

    effective_trial_id = trial_id or uuid4()
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
                if not pause_at_gates:
                    graph_step_completed = True
                    continue
                gate_id = handler.__production_gate_id__
                pending = [item.id for item in manifest.nodes[index + 1 :]]
                card = _build_decision_card(
                    gate_id=gate_id,
                    trial_id=effective_trial_id,
                    node_id=node.id,
                    operator_id=operator_id,
                    pending_nodes=pending,
                    artifact_paths=envelope.artifact_paths,
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
                        "langsmith_trace_id": str(effective_trial_id)
                        if child_runs
                        else None,
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
                            *([cost_report_path] if cost_report_path is not None else []),
                            *([trace_path] if trace_path is not None else []),
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
            "langsmith_trace_id": str(effective_trial_id) if child_runs else None,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": [
                *envelope.artifact_paths,
                cost_report_path,
                *([trace_path] if trace_path is not None else []),
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
        updated = envelope.model_copy(
            update={
                "status": "failed",
                "completed_at": _now(),
                "production_clone_launch_evidence_reason": "operator-rejected-at-gate",
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
        for node in manifest.nodes[start_index:]:
            handler = _active_node_handler(graph, node.id)
            node_kind = getattr(handler, "__production_node_kind__", None)
            if node_kind == "gate":
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
            "langsmith_trace_id": str(trial_id) if child_runs else None,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": [
                *envelope.artifact_paths,
                run_dir / "resume-command.json",
                cost_report_path,
                *([trace_path] if trace_path is not None else []),
            ],
        }
    )
    _persist_envelope(updated, runs_root)
    return updated


__all__ = [
    "DEFAULT_MANIFEST_PATH",
    "MissingUpstreamContributionError",
    "PRODUCTION_GATE_IDS",
    "resume_production_trial",
    "run_production_trial",
]
