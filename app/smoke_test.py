"""`uv run python -m app.smoke_test` — Slab 1 substrate smoke harness.

Loads the stub pipeline manifest via `app.manifest.loader.load()`, compiles a
one-node `StateGraph`, runs the shared `minimal_node`, and prints `smoke ok`
plus the node count. Exposes `run_smoke()` as an importable function so
Story 1.1d's parity test can call it directly without spawning a subprocess.

Story 1.4 upgrade: replaced the local ``_StubManifest`` Pydantic shape with
the production ``app.manifest.loader.load()`` entrypoint (now that 1.4 has
landed it). The smoke graph still uses ``_SmokeState`` TypedDict + direct
wiring of ``minimal_node`` so the ``{"smoke": "ok", "node": "noop"}`` payload
contract is preserved byte-equivalently. The production compiler
(``app.manifest.compiler.compile``) is not used here because it targets
``RunState`` + passthrough specialist stubs, which is correct for the
production path but would change this stub smoke's payload shape.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.manifest import PipelineManifest, load
from app.runtime.minimal_node import MINIMAL_NODE_NAME, minimal_node

MANIFEST_PATH: Path = (
    Path(__file__).resolve().parent.parent / "state" / "config" / "pipeline-manifest.yaml"
)


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


def _load_manifest(path: Path | None = None) -> PipelineManifest:
    target = path if path is not None else MANIFEST_PATH
    return load(target)


def _compile_graph(manifest: PipelineManifest) -> Any:
    """Compile the one-node stub manifest into a runnable LangGraph.

    Slab 1 hard-wires the ``noop -> minimal_node`` resolution. The production
    compiler (``app.manifest.compiler.compile``) lands in Slab 2+ with real
    specialist resolution — this harness intentionally bypasses that path so
    the smoke payload contract (``{"smoke": "ok", "node": "noop"}``) is
    preserved byte-equivalently.
    """
    builder = StateGraph(_SmokeState)
    for node in manifest.nodes:
        if node.id != MINIMAL_NODE_NAME:
            raise RuntimeError(
                f"smoke: only the shared '{MINIMAL_NODE_NAME}' node is wired in Slab 1; "
                f"got node id '{node.id}'. Production compiler (app.manifest.compiler) "
                f"handles the general case."
            )
        builder.add_node(node.id, minimal_node)

    for edge in manifest.edges:
        src = START if edge.from_node == "__start__" else edge.from_node
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
