"""`PipelineManifest` → LangGraph `StateGraph` compiler (AC-1.4-C/D/E2).

Single module, three responsibilities per spec:

1. **Topology compile** — instantiate `StateGraph(state_schema=RunState)`, add
   every node from `manifest.nodes` (resolving `specialist_id` to a stub
   passthrough in Slab 1; full resolution at Slab 2), add every edge via
   `add_edge` or `add_conditional_edges` depending on `EdgeSpec.condition`.

2. **Compile-time contract lint** — for each node that carries a
   `model_config_ref`, assert the referenced YAML file exists under the repo
   (FR25 + NFR-M2). Assert `runtime/graphs/v{frozen_graph_version}/` exists
   (stub existence check; full ceremony at Slab 4 Story 4.5). Assert every
   `EdgeSpec.condition` is a known name in the condition registry.

3. **Lane validation** — D4 requires `run_graph` vs `dev_graph` topologies to
   be separate `StateGraph` instances; the compiler accepts both lane values
   and returns the appropriate graph. The separation test lives at
   `tests/unit/manifest/test_lane_separation.py`.

Lint failures surface as `CompileError` with the offending node / edge named.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.manifest import conditions
from app.manifest.exceptions import CompileError
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest
from app.models.state.run_state import RunState


def _repo_root() -> Path:
    """Locate the repo root for resolving repo-relative paths."""
    return Path(__file__).resolve().parents[2]


def _passthrough_node(specialist_id: str | None) -> Any:
    """Return a stub callable for a node (Slab 1). Slab 2 replaces it with real specialist resolution."""  # noqa: E501
    label = specialist_id or "unresolved"

    def _handler(state: Any) -> dict[str, Any]:  # pragma: no cover — exercised via e2e test
        # Slab 1 stub: return empty partial so LangGraph's Pydantic-state reducer
        # keeps the input state intact. Real specialist resolution (Slab 2 Story
        # 2a.1) returns meaningful state updates keyed by RunState fields.
        del state
        return {}

    _handler.__name__ = f"passthrough_{label}"
    return _handler


def _validate_model_config_refs(nodes: list[NodeSpec], repo_root: Path) -> None:
    """NFR-M2 / FR25 — assert every `model_config_ref` resolves to a real file."""
    for node in nodes:
        if node.model_config_ref is None:
            continue
        ref_path = repo_root / node.model_config_ref
        if not ref_path.is_file():
            raise CompileError(
                f"node {node.id!r} model_config_ref does not resolve: {node.model_config_ref} "
                f"(expected at {ref_path})"
            )


def _validate_frozen_graph_version(frozen_graph_version: str, repo_root: Path) -> None:
    """Assert `runtime/graphs/v{version}/` exists (stub check; full ceremony at Slab 4.5)."""
    if frozen_graph_version.startswith("v"):
        dir_name = frozen_graph_version
    else:
        dir_name = f"v{frozen_graph_version}"
    graph_dir = repo_root / "runtime" / "graphs" / dir_name
    if not graph_dir.is_dir():
        raise CompileError(
            f"frozen_graph_version {frozen_graph_version!r} directory missing: "
            f"{graph_dir} (Slab 1 creates runtime/graphs/v0.1-stub; Slab 4 Story 4.5 "
            f"wires the full ceremony)"
        )


def _validate_conditions(edges: list[EdgeSpec]) -> None:
    """Assert every `EdgeSpec.condition` is a known condition name (Slab 1 stub registry)."""
    for edge in edges:
        if edge.condition is None:
            continue
        if edge.condition not in conditions.CONDITION_REGISTRY:
            raise CompileError(
                f"edge from {edge.from_node!r} to {edge.to!r} references unknown "
                f"condition {edge.condition!r}; Slab 1 stub registry supports only: "
                f"{sorted(conditions.CONDITION_REGISTRY)}"
            )


def _edge_target(name: str) -> Any:
    """Map `__start__`/`__end__` sentinels to LangGraph's START/END constants."""
    if name == "__start__":
        return START
    if name == "__end__":
        return END
    return name


def _add_node_and_edges(
    graph: StateGraph,
    manifest: PipelineManifest,
) -> None:
    """Add all nodes + edges to the StateGraph (AC-1.4-C topology compile)."""
    for node in manifest.nodes:
        graph.add_node(node.id, _passthrough_node(node.specialist_id))

    has_explicit_start_edge = any(edge.from_node == "__start__" for edge in manifest.edges)

    for edge in manifest.edges:
        src = _edge_target(edge.from_node)
        dst = _edge_target(edge.to)
        if edge.condition is None:
            graph.add_edge(src, dst)
        else:
            condition_fn = conditions.resolve(edge.condition)
            graph.add_conditional_edges(src, condition_fn, {"true": dst, "false": END})

    entry = _edge_target(manifest.entrypoint)
    # Only add an implicit START→entrypoint edge when the manifest does not already
    # declare one explicitly; avoids a duplicate-edge regression if LangGraph version
    # tightens its add_edge idempotency.
    if entry is not START and not has_explicit_start_edge:
        graph.add_edge(START, entry)


def compile(  # noqa: A001 — matches spec naming; callers use `app.manifest.compiler.compile(m)`
    manifest: PipelineManifest,
    *,
    repo_root: Path | None = None,
) -> StateGraph:
    """Compile a `PipelineManifest` into a LangGraph `StateGraph`.

    Args:
        manifest: Validated `PipelineManifest` (use `app.manifest.loader.load()` to
            load one from YAML).
        repo_root: Repo root for resolving `model_config_ref` and
            `frozen_graph_version` directory paths. Defaults to the repo root
            derived from this file's location (re-readable at call time for
            tests that monkey-patch via the keyword arg; avoids default-arg
            late-binding per hot-start gotcha #4).

    Returns:
        A `StateGraph` with state_schema=`RunState`, all nodes added, all
        edges wired, entrypoint connected. Caller invokes `.compile().invoke(...)`.

    Raises:
        CompileError: If a `model_config_ref` is missing, a condition name is
            unknown, or the `frozen_graph_version` directory does not exist.
    """
    root = repo_root if repo_root is not None else _repo_root()

    _validate_frozen_graph_version(manifest.frozen_graph_version, root)
    _validate_model_config_refs(manifest.nodes, root)
    _validate_conditions(manifest.edges)

    graph = StateGraph(state_schema=RunState)
    _add_node_and_edges(graph, manifest)
    return graph


__all__ = ["compile"]
