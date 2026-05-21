"""`uv run python -m app.smoke_test` — Slab 1 substrate smoke harness.

Two invocation modes:

- **Substrate smoke** (default; no flag) — loads
  `state/config/pipeline-manifest-substrate-stub.yaml`, wires a one-node graph
  against `minimal_node`, and prints `smoke ok`. Byte-equivalent to the 1.1c
  payload contract (`{"smoke": "ok", "node": "noop", "echo": "ping"}`) that
  1.1d's transport-parity tests + 1.1c's CLI smoke depend on.
- **Full pipeline smoke** (`--full`) — loads `state/config/pipeline-manifest.yaml`
  (the 33-node migrated v4.2 manifest from Story 1.6) and invokes
  `app.manifest.compiler.compile()` to run §01→§15 end-to-end through
  `app.specialists._stub.passthrough_specialist.passthrough_node`. M1 acceptance
  evidence; Slab 2 specialist migrations replace passthroughs with real scaffolds.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.manifest import PipelineManifest, compile, load
from app.runtime.minimal_node import MINIMAL_NODE_NAME, minimal_node

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBSTRATE_STUB_MANIFEST_PATH: Path = (
    REPO_ROOT / "state" / "config" / "pipeline-manifest-substrate-stub.yaml"
)
MIGRATED_V42_MANIFEST_PATH: Path = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

# Backward-compat alias — 1.1d transport-parity tests imported `MANIFEST_PATH`
# directly. Keep it pointing at the substrate stub so those tests remain green.
MANIFEST_PATH: Path = SUBSTRATE_STUB_MANIFEST_PATH


class _SmokeState(TypedDict, total=False):
    """Minimal LangGraph state dict for the no-op substrate smoke graph."""

    input: str | None
    smoke: str
    node: str
    echo: Any


def _load_manifest(path: Path | None = None) -> PipelineManifest:
    target = path if path is not None else SUBSTRATE_STUB_MANIFEST_PATH
    return load(target)


def _compile_substrate_graph(manifest: PipelineManifest) -> Any:
    """Compile the single-node substrate-stub manifest using `minimal_node`.

    Kept distinct from the production compiler so the 1.1c substrate payload
    contract (`{"smoke": "ok", "node": "noop", "echo": "ping"}`) is preserved
    byte-equivalent. The production compiler targets `RunState` + passthrough
    specialist stubs, which is the correct shape for `--full` but would change
    this substrate smoke's payload.
    """
    builder = StateGraph(_SmokeState)
    for node in manifest.nodes:
        if node.id != MINIMAL_NODE_NAME:
            raise RuntimeError(
                f"smoke: only the shared '{MINIMAL_NODE_NAME}' node is wired in the "
                f"substrate stub; got node id '{node.id}'. Use `--full` to run the "
                f"migrated 33-node manifest via the production compiler."
            )
        builder.add_node(node.id, minimal_node)

    for edge in manifest.edges:
        src = START if edge.from_node == "__start__" else edge.from_node
        dst = END if edge.to == "__end__" else edge.to
        builder.add_edge(src, dst)

    return builder.compile()


def run_smoke(input_value: str | None = "ping") -> dict[str, Any]:
    """Execute the substrate-stub graph end-to-end (1.1c / 1.1d contract)."""
    manifest = _load_manifest()
    graph = _compile_substrate_graph(manifest)
    return dict(graph.invoke({"input": input_value}))


def run_full_smoke() -> dict[str, Any]:
    """Execute the migrated v4.2 33-node graph end-to-end (Story 1.6 AC-1.6-C).

    Loads the migrated manifest, compiles via the production `app.manifest.compiler`
    (RunState state_schema + passthrough specialist resolution), invokes from
    the entrypoint, and returns the final state dict. All 33 nodes run.
    """
    manifest = load(MIGRATED_V42_MANIFEST_PATH)
    graph = compile(manifest)
    compiled = graph.compile()
    result = compiled.invoke(
        {
            "run_id": str(uuid4()),
            "graph_version": "v0.1-stub",
            "status": "pending",
        }
    )
    return dict(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.smoke_test")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the migrated v4.2 33-node manifest end-to-end (Story 1.6).",
    )
    args = parser.parse_args(argv)

    if args.full:
        result = run_full_smoke()
        manifest = load(MIGRATED_V42_MANIFEST_PATH)
        print(f"smoke ok (full, nodes={len(manifest.nodes)}, payload={result})")
        return 0

    result = run_smoke()
    node_count = 1  # substrate stub manifest is single-node by contract
    print(f"smoke ok (nodes={node_count}, payload={result})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
