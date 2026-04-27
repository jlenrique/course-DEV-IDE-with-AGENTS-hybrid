"""Deterministic local M3 trial harness for Slab 3 close artifacts."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.gates.resume_api import (
    build_transport_response,
    clear_resume_registry,
    register_decision_card,
    resume_from_verdict,
)
from app.models.decision_cards import DecisionCardMeta, G1Card, G2CCard, G3Card, G4Card
from app.models.state import CacheState, OperatorVerdict, RunState, SanctumFingerprint
from app.runtime.override_api import (
    apply_override,
    clear_override_registry,
    decision_card_meta_for_trial,
    get_override_ledger,
    get_run_state,
    register_run_state,
    submit_override,
)
from marcus.facade import get_facade
from marcus.orchestrator.supervisor import Supervisor

M3_TRIAL_ID = UUID("33333333-3333-4333-8333-333333333333")
M3_SESSION_ID = UUID("44444444-4444-4444-8444-444444444444")
BASE_TIME = datetime(2026, 4, 26, 16, 0, tzinfo=UTC)
SUPPORTED_GATES = ("G1", "G2C", "G3", "G4")
_UUIDS = {
    "sanctum-fingerprint": UUID("55555555-5555-4555-8555-555555555555"),
    "card:G1": UUID("66666666-6666-4666-8666-666666666666"),
    "card:G2C": UUID("77777777-7777-4777-8777-777777777777"),
    "card:G3": UUID("88888888-8888-4888-8888-888888888888"),
    "card:G4": UUID("99999999-9999-4999-8999-999999999999"),
    "verdict:G1": UUID("aaaaaaa1-aaaa-4aaa-8aaa-aaaaaaaaaaa1"),
    "verdict:G2C": UUID("aaaaaaa2-aaaa-4aaa-8aaa-aaaaaaaaaaa2"),
    "verdict:G3": UUID("aaaaaaa3-aaaa-4aaa-8aaa-aaaaaaaaaaa3"),
    "verdict:G4": UUID("aaaaaaa4-aaaa-4aaa-8aaa-aaaaaaaaaaa4"),
}


class TrialGateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    gate_id: Literal["G1", "G2C", "G3", "G4"]
    node_id: str
    card_id: UUID
    decision_card_digest: str
    verdict_verb: Literal["approve", "edit", "reject"]
    decision_card_meta: dict[str, Any]
    resume_payload: dict[str, Any]


class TrialEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: Literal["m3-trial-envelope.v1"] = "m3-trial-envelope.v1"
    trial_id: UUID
    preset: Literal["production", "explore"]
    corpus_path: str
    captured_at: datetime
    steps_completed: list[str] = Field(default_factory=list)
    gate_events: list[TrialGateEvent] = Field(default_factory=list)
    downstream_payloads: dict[str, dict[str, Any]] = Field(default_factory=dict)
    ledger_events: list[dict[str, Any]] = Field(default_factory=list)
    override_warning: dict[str, Any] | None = None
    override_event: dict[str, Any] | None = None
    run_state: dict[str, Any]


def _stable_uuid(name: str) -> UUID:
    return _UUIDS[name]


def _stable_state(trial_id: UUID = M3_TRIAL_ID) -> RunState:
    facade = get_facade()
    digest = facade.sanctum_digest
    return RunState(
        run_id=trial_id,
        status="running",
        created_at=BASE_TIME,
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=facade.state.model_resolution_trail if facade.state else [],
        model_overrides={},
        sanctum_fingerprint=SanctumFingerprint(
            content_sha256=digest,
            captured_at=BASE_TIME,
            snapshot_id=_stable_uuid("sanctum-fingerprint"),
        ),
        marcus_fingerprint=(digest, M3_SESSION_ID),
        story_states=[],
        cache_state=CacheState(
            cache_prefix="sanctum-v1-gpt54-m3",
            entries_count=8,
            last_invalidated_at=None,
        ),
    )


def _manifest():
    return get_facade()._manifest


def _node_map() -> dict[str, Any]:
    manifest = _manifest()
    return {node.id: node for node in manifest.nodes}


def _next_nodes(node_id: str) -> list[str]:
    manifest = _manifest()
    return [
        edge.to
        for edge in manifest.edges
        if edge.from_node == node_id and edge.to != "__end__"
    ]


def _card_for_gate(
    *,
    trial_id: UUID,
    gate_id: Literal["G1", "G2C", "G3", "G4"],
    node_id: str,
    step_index: int,
    meta: DecisionCardMeta,
    steps_completed: list[str],
) -> G1Card | G2CCard | G3Card | G4Card:
    created_at = BASE_TIME + timedelta(minutes=step_index)
    common = {
        "card_id": _stable_uuid(f"card:{gate_id}"),
        "trial_id": trial_id,
        "created_at": created_at,
        "drafted_proposal": {"node_id": node_id, "gate_id": gate_id},
        "evidence": [{"kind": "manifest-node", "node_id": node_id}],
        "risks": ["operator confirmation required"],
        "meta": meta,
    }
    if gate_id == "G1":
        return G1Card(
            **common,
            verb="approve",
            trial_summary="Marcus opened the trial with the production preset.",
            opened_by="marcus",
            next_nodes=_next_nodes(node_id),
        )
    if gate_id == "G2C":
        return G2CCard(
            **common,
            verb="edit",
            readiness_status="ready",
            blocking_issues=[],
            ready_nodes=["07C", "09"],
        )
    if gate_id == "G3":
        return G3Card(
            **common,
            verb="approve",
            progress_percent=72.0,
            active_node_id=node_id,
            pending_nodes=[step for step in steps_completed if step > node_id][:3],
            operator_prompt="Approve the revised storyboard packet and continue?",
        )
    return G4Card(
        **common,
        verb="approve",
        final_status="completed",
        artifact_paths=[
            "tests/fixtures/marcus/baseline_envelope/2026-04-26/envelope.json",
        ],
        outcome_summary="Marcus completed the local deterministic M3 trial run.",
    )


def _verdict_for_gate(
    *,
    trial_id: UUID,
    operator_id: str,
    gate_id: Literal["G1", "G2C", "G3", "G4"],
    card_id: UUID,
    digest: str,
    issued_at: datetime,
) -> OperatorVerdict:
    verb: Literal["approve", "edit", "reject"] = "edit" if gate_id == "G2C" else "approve"
    return OperatorVerdict(
        verdict_id=_stable_uuid(f"verdict:{gate_id}"),
        trial_id=trial_id,
        gate_id=gate_id,
        card_id=card_id,
        operator_id=operator_id,
        timestamp=issued_at + timedelta(seconds=45),
        verb=verb,
        decision_card_digest=digest,
        edit_payload=(
            {
                "change_summary": "Tighten evidence chain before Pass 2 lock.",
                "target_node": "09",
            }
            if verb == "edit"
            else None
        ),
        reject_reason=None,
    )


def run_local_m3_trial(
    *,
    preset: Literal["production", "explore"] = "production",
    corpus_path: str = "tests/fixtures/trial_corpus/README.md",
    trial_id: UUID | None = None,
    operator_id: str = "operator_cli",
) -> TrialEnvelope:
    clear_resume_registry()
    clear_override_registry()

    effective_trial_id = trial_id or M3_TRIAL_ID
    manifest = _manifest()
    nodes = _node_map()
    register_run_state(trial_id=effective_trial_id, state=_stable_state(effective_trial_id))
    supervisor = Supervisor(preset=preset, manifest=manifest)
    state = SimpleNamespace(current_node=None, events=[])

    steps_completed: list[str] = []
    gate_events: list[TrialGateEvent] = []
    ledger_events: list[dict[str, Any]] = []
    downstream_payloads: dict[str, dict[str, Any]] = {}
    edit_payloads: list[dict[str, Any]] = []
    override_warning: dict[str, Any] | None = None
    override_event: dict[str, Any] | None = None

    while True:
        decision = supervisor.run_step(state)
        node = nodes[decision.next_node_id]
        steps_completed.append(node.id)
        downstream_payloads[node.id] = {
            "step_id": node.id,
            "specialist_id": node.specialist_id,
            "operator_edits": list(edit_payloads),
        }

        gate_code = getattr(node, "gate_code", None)
        if gate_code in SUPPORTED_GATES:
            meta = decision_card_meta_for_trial(effective_trial_id)
            card = _card_for_gate(
                trial_id=effective_trial_id,
                gate_id=gate_code,
                node_id=node.id,
                step_index=len(gate_events) + 1,
                meta=meta,
                steps_completed=steps_completed,
            )
            issued_at = BASE_TIME + timedelta(minutes=len(gate_events) + 1, seconds=30)
            stored = register_decision_card(
                card,
                issuance_timestamp=issued_at,
                server_nonce=f"m3-{gate_code.lower()}",
            )
            verdict = _verdict_for_gate(
                trial_id=effective_trial_id,
                operator_id=operator_id,
                gate_id=gate_code,
                card_id=card.card_id,
                digest=stored.digest,
                issued_at=issued_at,
            )
            command = resume_from_verdict(verdict)
            response = build_transport_response(
                command=command,
                verdict=verdict,
                transport_kind="cli",
            )
            ledger_events.append(response["ledger_event"])

            if verdict.edit_payload is not None:
                edit_payloads.append(verdict.edit_payload)
                warning = submit_override(effective_trial_id, "10", "gpt-5-mini")
                override_warning = warning.model_dump(mode="json")
                event = apply_override(
                    {
                        "trial_id": str(effective_trial_id),
                        "node_id": "10",
                        "new_model": "gpt-5-mini",
                        "operator_id": operator_id,
                    },
                    warning.confirm_token,
                    now=warning.issued_at + timedelta(seconds=50),
                )
                override_event = event.model_dump(mode="json")

            gate_events.append(
                TrialGateEvent(
                    gate_id=gate_code,
                    node_id=node.id,
                    card_id=card.card_id,
                    decision_card_digest=stored.digest,
                    verdict_verb=verdict.verb,
                    decision_card_meta=response["decision_card_meta"],
                    resume_payload=response["resume"],
                )
            )

        if node.id == "15":
            break

    final_state = get_run_state(effective_trial_id).model_copy(
        update={"status": "complete", "completed_at": BASE_TIME + timedelta(hours=1)}
    )
    register_run_state(trial_id=effective_trial_id, state=final_state)
    ledger_events.extend(get_override_ledger(effective_trial_id))

    return TrialEnvelope(
        trial_id=effective_trial_id,
        preset=preset,
        corpus_path=corpus_path,
        captured_at=BASE_TIME + timedelta(hours=1),
        steps_completed=steps_completed,
        gate_events=gate_events,
        downstream_payloads=downstream_payloads,
        ledger_events=ledger_events,
        override_warning=override_warning,
        override_event=override_event,
        run_state=final_state.model_dump(mode="json"),
    )


__all__ = ["M3_TRIAL_ID", "TrialEnvelope", "TrialGateEvent", "run_local_m3_trial"]
