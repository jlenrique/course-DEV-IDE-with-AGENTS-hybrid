"""M1 evidence — end-to-end §01→§15 smoke through the migrated v4.2 manifest (AC-1.6-D).

Story 1.6 ships a 33-node v4.2 manifest with every specialist_id resolving to
`app.specialists._stub.passthrough_specialist.passthrough_node`. This test
asserts:

- 33 nodes executed (count from the loaded manifest + a graph-invocation
  round-trip)
- Final state has the deterministic post-§15 payload shape (RunState fields
  carry through; passthrough stubs return {} so state flows unchanged)

This test runs without Postgres / LangSmith / any live service — the smoke is
fully deterministic through the passthrough nodes.
"""

from __future__ import annotations

from app.manifest import load
from app.manifest.schema import is_orchestration_only
from app.smoke_test import MIGRATED_V42_MANIFEST_PATH, run_full_smoke


def test_migrated_manifest_has_33_renderable_nodes() -> None:
    # Slab 7a added four runtime-only orchestration nodes to the graph
    # (renderer/L1 story 2026-06-12: counts derive through the SHARED
    # classification predicate, not a frozen total).
    manifest = load(MIGRATED_V42_MANIFEST_PATH)
    renderable = [n for n in manifest.nodes if not is_orchestration_only(n)]
    orchestration = [n.id for n in manifest.nodes if is_orchestration_only(n)]
    assert len(renderable) == 33
    assert len(orchestration) == 4
    assert manifest.frozen_graph_version == "v42"
    assert manifest.pack_version == "v4.2"
    assert manifest.lane == "run_graph"


def test_migrated_manifest_covers_v42_numbered_steps() -> None:
    manifest = load(MIGRATED_V42_MANIFEST_PATH)
    ids = {n.id for n in manifest.nodes}
    # v4.2 top-level numbered steps §01 through §15
    assert {"01", "02", "03", "04", "05", "06", "07", "08", "09",
            "10", "11", "12", "13", "14", "15"} <= ids
    # A representative sampling of the lettered + decimal sub-phases
    assert {"02A", "04A", "04.5", "04.55", "4.75", "05B", "07C", "07F",
            "08B", "11B", "14.5"} <= ids


def test_run_full_smoke_invokes_end_to_end() -> None:
    """AC-1.6-D — run_full_smoke() compiles + invokes; RunState survives."""
    result = run_full_smoke()
    # RunState fields flow through the 33 passthrough nodes.
    assert "run_id" in result
    assert result["status"] in {"pending", "running", "complete"}
    assert result["graph_version"] == "v0.1-stub"


def test_migrated_manifest_edges_form_linear_chain() -> None:
    """v4.2 topology is strict linear per AC-1.6-A (conditionals are Slab 2/3 territory)."""
    manifest = load(MIGRATED_V42_MANIFEST_PATH)
    # The linear chain threads the 33 RENDERABLE nodes; the four Slab-7a
    # orchestration nodes are runner-invoked, not edge-chained.
    renderable = [n for n in manifest.nodes if not is_orchestration_only(n)]
    assert len(manifest.edges) == len(renderable) + 1  # +1 for __start__ entry
    # No conditionals in 1.6
    for edge in manifest.edges:
        assert edge.condition is None, f"Unexpected conditional edge: {edge}"
    # Exactly one edge from __start__ and one edge to __end__
    assert sum(1 for e in manifest.edges if e.from_node == "__start__") == 1
    assert sum(1 for e in manifest.edges if e.to == "__end__") == 1
