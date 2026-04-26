"""Runtime model override flow."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import yaml

from app.models.decision_cards import DecisionCardMeta, OverrideEvent
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.runtime.override_warning import ModelOverrideWarning

_RUN_STATE_REGISTRY: dict[UUID, RunState] = {}
_PENDING_WARNINGS: dict[tuple[UUID, str, str], ModelOverrideWarning] = {}
_CONSUMED_TOKENS: set[str] = set()
_OVERRIDE_TRAIL: dict[UUID, list[OverrideEvent]] = {}
_LEDGER_EVENTS: dict[UUID, list[dict[str, object]]] = {}
_WARNING_TO_OVERRIDE: dict[str, tuple[UUID, str, str]] = {}

_MODEL_COSTS = {
    "gpt-5.4": 1.0,
    "gpt-5.5": 1.5,
    "gpt-5-haiku": 0.4,
}
_DEFAULT_MODEL = "gpt-5.4"

LOGGER = logging.getLogger(__name__)


class OverrideTokenStaleError(RuntimeError):
    pass


def _as_uuid(value: UUID | str) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))


def clear_override_registry() -> None:
    _RUN_STATE_REGISTRY.clear()
    _PENDING_WARNINGS.clear()
    _CONSUMED_TOKENS.clear()
    _OVERRIDE_TRAIL.clear()
    _LEDGER_EVENTS.clear()
    _WARNING_TO_OVERRIDE.clear()


def register_run_state(*, trial_id: UUID | str, state: RunState) -> None:
    _RUN_STATE_REGISTRY[_as_uuid(trial_id)] = state


def get_run_state(trial_id: UUID | str) -> RunState:
    return _RUN_STATE_REGISTRY[_as_uuid(trial_id)]


def get_override_ledger(trial_id: UUID | str) -> list[dict[str, object]]:
    return list(_LEDGER_EVENTS.get(_as_uuid(trial_id), []))


def current_cache_state_label(trial_id: UUID | str) -> str:
    state = get_run_state(trial_id)
    if state.cache_state is None:
        return "cold"
    if state.model_overrides:
        return "mixed"
    return "healthy"


def _manifest_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "state"
        / "config"
        / "pipeline-manifest.yaml"
    )


def _affected_nodes(node_id: str) -> list[str]:
    raw = yaml.safe_load(_manifest_path().read_text(encoding="utf-8"))
    edges = raw.get("edges", [])
    graph: dict[str, list[str]] = {}
    for edge in edges:
        graph.setdefault(edge["from"], []).append(edge["to"])
    visited: list[str] = []
    queue = [node_id]
    while queue:
        current = queue.pop(0)
        if current in visited or current == "__end__":
            continue
        visited.append(current)
        queue.extend(graph.get(current, []))
    return visited or [node_id]


def compute_cache_impact(
    trial_id: UUID | str,
    node_id: str,
    new_model: str,
) -> dict[str, object]:
    state = get_run_state(trial_id)
    current_model = state.model_overrides.get(node_id, _DEFAULT_MODEL)
    affected_nodes = _affected_nodes(node_id)
    before = current_cache_state_label(trial_id)
    after = "cold" if state.cache_state is None else "mixed"
    old_cost = _MODEL_COSTS.get(current_model, 1.0)
    new_cost = _MODEL_COSTS.get(new_model, old_cost)
    estimated_cost_delta = max(new_cost - old_cost, 0.0) * len(affected_nodes)
    return {
        "current_model": current_model,
        "estimated_cost_delta_usd": round(estimated_cost_delta, 3),
        "affected_nodes": affected_nodes,
        "cache_state_delta": {"before": before, "after": after},
    }


def _confirm_token(
    *,
    trial_id: UUID,
    node_id: str,
    new_model: str,
    current_cache_state: str,
) -> str:
    payload = {
        "trial_id": str(trial_id),
        "node_id": node_id,
        "new_model": new_model,
        "current_cache_state": current_cache_state,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def submit_override(trial_id: UUID | str, node_id: str, new_model: str) -> ModelOverrideWarning:
    trial_uuid = _as_uuid(trial_id)
    cache_state = current_cache_state_label(trial_id)
    key = (trial_uuid, node_id, new_model)
    existing = _PENDING_WARNINGS.get(key)
    if existing is not None and existing.expires_at > datetime.now(UTC):
        return existing
    impact = compute_cache_impact(trial_id, node_id, new_model)
    issued_at = datetime.now(UTC)
    warning = ModelOverrideWarning(
        trial_id=trial_uuid,
        node_id=node_id,
        requested_model=new_model,
        current_model=impact["current_model"],
        estimated_cost_delta_usd=impact["estimated_cost_delta_usd"],
        affected_nodes=impact["affected_nodes"],
        cache_state_delta=impact["cache_state_delta"],
        confirm_token=_confirm_token(
            trial_id=trial_uuid,
            node_id=node_id,
            new_model=new_model,
            current_cache_state=cache_state,
        ),
        issued_at=issued_at,
        expires_at=issued_at + timedelta(minutes=5),
    )
    _PENDING_WARNINGS[key] = warning
    _WARNING_TO_OVERRIDE[warning.confirm_token] = key
    LOGGER.warning(
        (
            "runtime model override submitted trial_id=%s node_id=%s "
            "requested_model=%s current_model=%s affected_nodes=%s cache_state=%s"
        ),
        trial_uuid,
        node_id,
        new_model,
        impact["current_model"],
        ",".join(impact["affected_nodes"]),
        impact["cache_state_delta"],
    )
    return warning


def apply_override(
    verdict: dict[str, object],
    confirm_token: str,
    *,
    now: datetime | None = None,
) -> OverrideEvent:
    try:
        trial_id = UUID(str(verdict["trial_id"]))
        node_id = str(verdict["node_id"])
        new_model = str(verdict["new_model"])
        operator_id = str(verdict["operator_id"])
    except KeyError as exc:
        raise OverrideTokenStaleError(
            f"override verdict missing required field {exc.args[0]!r}"
        ) from exc

    key = _WARNING_TO_OVERRIDE.get(confirm_token, (trial_id, node_id, new_model))
    warning = _PENDING_WARNINGS.get(key)
    current_time = now or datetime.now(UTC)
    if warning is None or warning.confirm_token != confirm_token:
        raise OverrideTokenStaleError("confirm_token does not match a pending override")
    if current_time > warning.expires_at:
        raise OverrideTokenStaleError("confirm_token has expired")
    if confirm_token in _CONSUMED_TOKENS:
        raise OverrideTokenStaleError("confirm_token was already consumed")

    state = get_run_state(trial_id)
    overrides = dict(state.model_overrides)
    previous_model = overrides.get(node_id, _DEFAULT_MODEL)
    overrides[node_id] = new_model
    updated_cache_state = (
        None
        if state.cache_state is None
        else CacheState(
            cache_prefix=state.cache_state.cache_prefix,
            entries_count=state.cache_state.entries_count,
            last_invalidated_at=current_time,
        )
    )
    updated_state = state.model_copy(
        update={
            "model_overrides": overrides,
            "cache_state": updated_cache_state,
        }
    )
    _RUN_STATE_REGISTRY[trial_id] = updated_state
    event = OverrideEvent(
        event_id=warning.warning_id,
        applied_at=current_time,
        node_id=node_id,
        previous_value={"model": previous_model},
        new_value={"model": new_model},
        operator_id=operator_id,
        confirm_token=confirm_token,
    )
    _OVERRIDE_TRAIL.setdefault(trial_id, []).append(event)
    _LEDGER_EVENTS.setdefault(trial_id, []).append(
        {
            "kind": "override",
            "trial_id": str(trial_id),
            "node_id": node_id,
            "operator_id": operator_id,
            "new_model": new_model,
            "previous_model": previous_model,
            "confirm_token": confirm_token,
        }
    )
    _CONSUMED_TOKENS.add(confirm_token)
    del _PENDING_WARNINGS[key]
    _WARNING_TO_OVERRIDE.pop(confirm_token, None)
    return event


def decision_card_meta_for_trial(trial_id: UUID | str) -> DecisionCardMeta:
    trial_uuid = _as_uuid(trial_id)
    state = get_run_state(trial_uuid)
    return DecisionCardMeta(
        cache_state=current_cache_state_label(trial_uuid),  # type: ignore[arg-type]
        affected_nodes=sorted(state.model_overrides.keys()),
        override_trail=_OVERRIDE_TRAIL.get(trial_uuid, []),
        reject_rate=0.0,
    )


__all__ = [
    "OverrideTokenStaleError",
    "apply_override",
    "clear_override_registry",
    "compute_cache_impact",
    "current_cache_state_label",
    "decision_card_meta_for_trial",
    "get_override_ledger",
    "get_run_state",
    "register_run_state",
    "submit_override",
]
