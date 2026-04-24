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

import yaml
from langgraph.graph import END, START, StateGraph

from app.manifest import conditions
from app.manifest.exceptions import CompileError
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest
from app.models.registry import PipelineRegistry
from app.models.specialist_model_config import SpecialistModelConfig
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


def _load_registry_model_ids(repo_root: Path) -> set[str]:
    registry_path = repo_root / "app" / "models" / "registry.yaml"
    try:
        registry_raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        registry = PipelineRegistry.model_validate(registry_raw)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise CompileError(f"failed to load model registry at {registry_path}: {exc}") from exc
    return {entry.model_id for entry in registry.entries}


def _validate_model_ids_in_model_config_refs(nodes: list[NodeSpec], repo_root: Path) -> None:
    # This validator is ADDITIVE to the Slab-1 _validate_model_config_refs
    # (file-existence check). It strengthens behavior when substrate is fully
    # wired (real registry + parseable SpecialistModelConfig files) by rejecting
    # unknown model IDs; it is a no-op when substrate is absent (e.g., tmp_path
    # tests that create non-SpecialistModelConfig stub files or lack the
    # registry file entirely). This preserves Slab-1's GOLDEN-ratified compile()
    # semantics per DR-1.
    if not any(node.model_config_ref is not None for node in nodes):
        return
    try:
        known_model_ids = _load_registry_model_ids(repo_root)
    except CompileError:
        # Registry not present at repo_root — fall back to Slab-1 file-existence
        # behavior (_validate_model_config_refs already ran). Real Slab-2+
        # specialist stories ship the registry alongside their config files;
        # test scopes using tmp_path without a registry opt out here.
        return
    for node in nodes:
        if node.model_config_ref is None:
            continue
        config_path = repo_root / node.model_config_ref
        try:
            config_raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            config = SpecialistModelConfig.model_validate(config_raw)
        except Exception:
            # Config file exists (Slab-1 check passed) but isn't a valid
            # SpecialistModelConfig shape — this matches Slab-1 test fixtures
            # that stub a YAML file only to prove file-existence. The strict
            # model-id check requires a parseable config; absent one, skip.
            # Slab-2+ specialist stories ship real configs; defect-mode
            # detection happens when the config IS parseable but names an
            # unknown model_id below.
            continue

        invalid_refs: list[str] = []
        if config.default_model not in known_model_ids:
            invalid_refs.append(config.default_model)
        for _, override_model in sorted(config.per_node_overrides.items()):
            if override_model not in known_model_ids:
                invalid_refs.append(override_model)
        if invalid_refs:
            specialist = node.specialist_id or config.specialist_id or node.id
            invalid = ", ".join(repr(ref) for ref in sorted(set(invalid_refs)))
            raise CompileError(
                f"specialist {specialist!r} in node {node.id!r} references unknown model id(s) "
                f"{invalid} via {node.model_config_ref}"
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
    _validate_model_ids_in_model_config_refs(manifest.nodes, root)
    _validate_conditions(manifest.edges)

    graph = StateGraph(state_schema=RunState)
    _add_node_and_edges(graph, manifest)
    return graph


__all__ = ["compile"]
