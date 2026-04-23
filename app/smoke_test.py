"""`uv run python -m app.smoke_test` — Slab 1 substrate smoke harness.

Loads the stub pipeline manifest, compiles a one-node `StateGraph`, runs the
shared `minimal_node`, and prints `smoke ok` plus the node count. Exposes
`run_smoke()` as an importable function so Story 1.1d's parity test can call
it directly without spawning a subprocess.

The minimal `yaml.safe_load` + Pydantic shape used here is Story 1.1c scope.
Story 1.4 lands the full `app.manifest.loader` + compiler that this stub
foreshadows; do NOT inflate this module to anticipate that work.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, TypedDict

import yaml
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict, Field

from app.runtime.minimal_node import MINIMAL_NODE_NAME, minimal_node

MANIFEST_PATH: Path = (
    Path(__file__).resolve().parent.parent / "state" / "config" / "pipeline-manifest.yaml"
)


class _StubManifestNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    handler: str = Field(min_length=1)


class _StubManifestEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)


class _StubManifestGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[_StubManifestNode]
    edges: list[_StubManifestEdge]


class _StubManifest(BaseModel):
    """Slab 1 stub manifest shape. Story 1.4 introduces the production schema."""

    model_config = ConfigDict(extra="allow")  # tolerate unknown top-level keys (e.g. comments)

    schema_version: str
    graph: _StubManifestGraph


class _SmokeState(TypedDict, total=False):
    """Minimal LangGraph state dict for the no-op smoke graph.

    The output fields (`smoke`, `node`, `echo`) are declared so LangGraph's
    state-schema reducer keeps them in the final state instead of silently
    dropping unknown keys returned by ``minimal_node``.
    """

    input: str | None
    smoke: str
    node: str
    echo: Any


def _load_manifest(path: Path = MANIFEST_PATH) -> _StubManifest:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _StubManifest.model_validate(raw)


def _compile_graph(manifest: _StubManifest) -> Any:
    """Compile the one-node stub manifest into a runnable LangGraph.

    Slab 1 hard-wires the `noop -> minimal_node` resolution; Story 1.4 will
    replace this with the manifest-driven handler resolver.
    """
    builder = StateGraph(_SmokeState)
    seen_handlers: set[str] = set()
    for node in manifest.graph.nodes:
        if node.id != MINIMAL_NODE_NAME:
            raise RuntimeError(
                f"smoke: only the shared '{MINIMAL_NODE_NAME}' node is wired in Slab 1; "
                f"got node id '{node.id}'. Story 1.4 lands the full handler resolver."
            )
        builder.add_node(node.id, minimal_node)
        seen_handlers.add(node.handler)

    for edge in manifest.graph.edges:
        src = START if edge.from_ == "__start__" else edge.from_
        dst = END if edge.to == "__end__" else edge.to
        builder.add_edge(src, dst)

    return builder.compile()


def run_smoke(input_value: str | None = "ping") -> dict[str, Any]:
    """Execute the smoke graph end-to-end and return the result payload."""
    manifest = _load_manifest()
    graph = _compile_graph(manifest)
    return dict(graph.invoke({"input": input_value}))


def main(argv: list[str] | None = None) -> int:
    del argv
    result = run_smoke()
    node_count = 1  # Slab 1 stub manifest is single-node by contract
    print(f"smoke ok (nodes={node_count}, payload={result})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
