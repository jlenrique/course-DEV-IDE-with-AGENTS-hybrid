"""Production composition adapter for scaffolded specialists."""

from __future__ import annotations

import importlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import yaml
from langgraph.checkpoint.memory import InMemorySaver

from app.marcus.orchestrator.gate_runner import assert_payload_duality_boundary
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState

DEFAULT_GRAPH_VERSION = "v42"
DEFAULT_REGISTRY_PATH = Path("state/config/dispatch-registry.yaml")
INTERRUPT_KEY = "__interrupt__"


class ProductionDispatchAdapterError(RuntimeError):
    """Raised when production envelope dispatch cannot satisfy the contract."""


class ProductionDispatchAdapter:
    """Bridge production envelope state to per-specialist scaffold scratch.

    The adapter owns envelope/cache-prefix translation. Specialists keep their
    isolated ``RunState.cache_state.cache_prefix`` contract unchanged.
    """

    def __init__(
        self,
        *,
        graph_builders: Mapping[str, Callable[[], Any]] | None = None,
        registry_path: Path = DEFAULT_REGISTRY_PATH,
    ) -> None:
        self._graph_builders = (
            dict(graph_builders)
            if graph_builders is not None
            else self._load_graph_builders(registry_path)
        )
        self.last_constructed_state: RunState | None = None
        self.last_input_payload: dict[str, Any] | None = None
        self.last_interrupts: Any = None

    def build_specialist_state(
        self,
        *,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        base_state: RunState | None = None,
        runner_supplied_payload: dict[str, Any] | None = None,
    ) -> RunState:
        """Construct the specialist's isolated RunState from envelope dependencies.

        ``runner_supplied_payload`` (Story 7a.1 / A-R3 Option A): optional
        runner-side keys merged into the cache_prefix JSON alongside upstream
        ``_payload_from_dependencies(...)`` output. Used to thread
        ``directive_path`` + ``bundle_dir`` into Texas's _act without inventing
        a synthetic specialist contribution. Runner-supplied keys WIN on
        collision with dependency_map keys.
        """
        if base_state is not None and base_state.run_id != envelope.trial_id:
            raise ProductionDispatchAdapterError(
                "base_state.run_id must match production envelope trial_id"
            )
        source = base_state or RunState(
            run_id=envelope.trial_id,
            graph_version=DEFAULT_GRAPH_VERSION,
        )
        payload = self._payload_from_dependencies(envelope, dependency_map)
        if runner_supplied_payload:
            # Amelia S3-b.1 (party review 2026-06-12): runner-keys-win was
            # silent precedence — a collision between seam and dependency
            # delivery now refuses instead of silently shadowing (the
            # first-contribution-wins genus, different chromosome).
            collisions = sorted(set(payload) & set(runner_supplied_payload))
            if collisions:
                raise ProductionDispatchAdapterError(
                    "runner_supplied_payload collides with dependency-map "
                    f"key(s) {collisions}; deliver each key through exactly "
                    "one mechanism (edge projection lands at S4)"
                )
            payload = {**payload, **runner_supplied_payload}
        assert_payload_duality_boundary(payload)
        if not dependency_map and not runner_supplied_payload and source.cache_state is not None:
            cache_state = source.cache_state
        else:
            cache_state = CacheState(
                cache_prefix=json.dumps(
                    payload,
                    sort_keys=True,
                    ensure_ascii=True,
                    separators=(",", ":"),
                    default=str,
                )
            )
        state = RunState.model_validate(
            {
                **source.model_dump(mode="python"),
                "cache_state": cache_state,
                "production_envelope": None,
            }
        )
        self.last_constructed_state = state
        self.last_input_payload = payload
        return state

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state: RunState | None = None,
        runner_supplied_payload: dict[str, Any] | None = None,
        node_id: str | None = None,
    ) -> ProductionEnvelope:
        """Invoke a scaffolded specialist and append its output to the envelope.

        ``runner_supplied_payload`` is forwarded to ``build_specialist_state``
        per A-R3 Option A. ``node_id`` keys the contribution to the dispatching
        manifest node (S2 per-node keying); the duplicate guard is node-aware —
        multi-node specialists pass it at each of their nodes (Amelia: this
        guard and the walker skip-rule changed in the same commit, or the
        first multi-node dispatch crashes live).
        """
        if envelope.get_contribution(specialist_id, node_id=node_id) is not None:
            raise ValueError(
                f"production envelope already has contribution for "
                f"{specialist_id!r} at node {node_id!r}"
            )
        state = self.build_specialist_state(
            envelope=envelope,
            dependency_map=dependency_map,
            base_state=base_state,
            runner_supplied_payload=runner_supplied_payload,
        )
        input_entries_count = state.cache_state.entries_count if state.cache_state else 0
        compiled_graph = self._compile_graph(specialist_id)
        state = self._invoke_compiled_graph(compiled_graph, state)
        output = self._extract_output(
            state,
            specialist_id=specialist_id,
            input_entries_count=input_entries_count,
        )
        contribution = SpecialistContribution.from_output(
            specialist_id=specialist_id,
            output=output,
            model_used=self._model_used(state),
            cost_usd=cost_usd,
            node_id=node_id,
        )
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(contribution)
        return updated

    def _payload_from_dependencies(
        self,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for input_key, upstream_specialist_id in dependency_map.items():
            # S2: dependency consumers want the upstream specialist's most
            # recent output (multi-node specialists contribute per node).
            contribution = envelope.latest_for_specialist(upstream_specialist_id)
            if contribution is None:
                raise ProductionDispatchAdapterError(
                    f"dependency {upstream_specialist_id!r} for input "
                    f"{input_key!r} is absent from production envelope"
                )
            payload[input_key] = contribution.output
        return payload

    def _compile_graph(self, specialist_id: str) -> Any:
        builder = self._graph_builders.get(specialist_id)
        if builder is None:
            raise ProductionDispatchAdapterError(
                f"specialist {specialist_id!r} is absent from dispatch registry"
            )
        graph = builder()
        if not hasattr(graph, "compile"):
            return graph
        try:
            return graph.compile(checkpointer=InMemorySaver())
        except TypeError:
            return graph.compile()

    @staticmethod
    def _load_graph_builders(registry_path: Path) -> dict[str, Callable[[], Any]]:
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        specialists = registry.get("specialists", {})
        builders: dict[str, Callable[[], Any]] = {}
        for specialist_id, builder_ref in specialists.items():
            module_name, function_name = str(builder_ref).split(":", 1)
            module = importlib.import_module(module_name)
            builders[str(specialist_id)] = getattr(module, function_name)
        return builders

    def _invoke_compiled_graph(self, compiled_graph: Any, state: RunState) -> RunState:
        if not callable(getattr(compiled_graph, "invoke", None)):
            raise ProductionDispatchAdapterError(
                "compiled specialist graph must expose invoke()"
            )
        config = {
            "configurable": {
                "thread_id": f"production-dispatch:{state.run_id}:{id(compiled_graph)}",
            }
        }
        try:
            result = compiled_graph.invoke(state, config=config)
        except TypeError:
            result = compiled_graph.invoke(state)
        if isinstance(result, RunState):
            self.last_interrupts = None
            return result
        if not isinstance(result, dict):
            raise ProductionDispatchAdapterError(
                "compiled specialist graph returned non-mapping state"
            )
        self.last_interrupts = result.get(INTERRUPT_KEY)
        state_payload = {
            key: value for key, value in result.items() if not str(key).startswith("__")
        }
        return RunState.model_validate(state_payload)

    @staticmethod
    def _extract_output(
        state: RunState,
        *,
        specialist_id: str,
        input_entries_count: int,
    ) -> dict[str, Any]:
        if state.cache_state is None or not state.cache_state.cache_prefix:
            raise ProductionDispatchAdapterError(
                f"{specialist_id} did not write cache_state.cache_prefix output"
            )
        if state.cache_state.entries_count <= input_entries_count:
            raise ProductionDispatchAdapterError(
                f"{specialist_id} did not advance cache_state entries_count"
            )
        try:
            output = json.loads(state.cache_state.cache_prefix)
        except json.JSONDecodeError as exc:
            raise ProductionDispatchAdapterError(
                f"{specialist_id} output cache_prefix is not valid JSON"
            ) from exc
        if not isinstance(output, dict):
            raise ProductionDispatchAdapterError(
                f"{specialist_id} output cache_prefix must decode to a mapping"
            )
        return output

    @staticmethod
    def _model_used(state: RunState) -> str:
        if state.model_resolution_trail:
            return state.model_resolution_trail[-1].resolved
        raise ProductionDispatchAdapterError(
            "specialist completed without model_resolution_trail evidence"
        )


__all__ = [
    "DEFAULT_GRAPH_VERSION",
    "DEFAULT_REGISTRY_PATH",
    "INTERRUPT_KEY",
    "ProductionDispatchAdapter",
    "ProductionDispatchAdapterError",
]
