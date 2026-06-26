"""S2 — compile-time composer: conditional inclusion + byte-identity + DAG fail-closed."""

from __future__ import annotations

import pytest

from app.manifest import compiler, load
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
from app.marcus.lesson_plan import composition
from app.marcus.lesson_plan.composition import CompositionError, compose_manifest
from app.models.state.component_selection import ComponentSelection

MOTION_NODE_IDS = {"07D", "07E", "07F"}


def _live_manifest():
    return load(DEFAULT_RUN_MANIFEST_PATH)


def _graph_node_ids(manifest) -> set[str]:
    graph = compiler.compile(manifest)
    return {str(n) for n in graph.nodes}


def _graph_edges(manifest) -> set[tuple[str, str]]:
    graph = compiler.compile(manifest)
    return {(str(s), str(t)) for s, t in graph.edges}


def test_full_selection_reproduces_today_graph_byte_identically() -> None:
    """The composer is a no-op when every component present today is selected.

    Composition-catalog B3 (2026-06-26): 07W is now a REAL manifest node owned by
    the ``workbook`` component, so the full graph today is deck+motion+workbook
    (production_default = deck+motion prunes 07W — see the prune test below)."""
    manifest = _live_manifest()
    composed = compose_manifest(
        manifest, ComponentSelection(deck=True, motion=True, workbook=True)
    )

    assert _graph_node_ids(composed) == _graph_node_ids(manifest)
    assert _graph_edges(composed) == _graph_edges(manifest)


def test_deck_only_excludes_motion_nodes() -> None:
    manifest = _live_manifest()
    composed = compose_manifest(manifest, ComponentSelection(deck=True, motion=False))
    node_ids = _graph_node_ids(composed)

    assert MOTION_NODE_IDS.isdisjoint(node_ids), "deck-only must not include motion nodes"
    assert "07E" not in node_ids  # the kira motion node specifically


def test_deck_only_bridges_the_motion_chain_and_keeps_deck_subset_identical() -> None:
    """Pin the current deck topology: motion chain 07C->07D->07E->07F->07G collapses
    to a single bridge 07C->07G; every other deck edge is byte-unchanged vs today."""
    manifest = _live_manifest()
    today_edges = _graph_edges(manifest)
    # Keep workbook selected so 07W stays in the graph and this test isolates the
    # MOTION-chain bridging concern (07W pruning has its own test).
    composed = compose_manifest(
        manifest, ComponentSelection(deck=True, motion=False, workbook=True)
    )
    deck_edges = _graph_edges(composed)

    # The bridge appears.
    assert ("07C", "07G") in deck_edges
    # Motion-incident edges are gone.
    for edge in {("07C", "07D"), ("07D", "07E"), ("07E", "07F"), ("07F", "07G")}:
        assert edge not in deck_edges

    # Every surviving edge between two deck nodes is unchanged vs today, and the
    # only NEW edge is the bridge.
    expected = {
        e for e in today_edges if e[0] not in MOTION_NODE_IDS and e[1] not in MOTION_NODE_IDS
    } | {("07C", "07G")}
    assert deck_edges == expected


def test_motion_selected_contains_07e_deck_only_does_not() -> None:
    manifest = _live_manifest()
    with_motion = _graph_node_ids(
        compose_manifest(manifest, ComponentSelection(deck=True, motion=True))
    )
    without = _graph_node_ids(
        compose_manifest(manifest, ComponentSelection(deck=True, motion=False))
    )
    assert "07E" in with_motion
    assert "07E" not in without


def test_workbook_adds_the_real_07w_node_distinct_from_deck_plus_motion() -> None:
    """Selecting workbook adds the REAL 07W producer node (no longer a stub)."""
    manifest = _live_manifest()
    dm = _graph_node_ids(
        compose_manifest(manifest, ComponentSelection(deck=True, motion=True))
    )
    dmw = _graph_node_ids(
        compose_manifest(
            manifest, ComponentSelection(deck=True, motion=True, workbook=True)
        )
    )
    assert dmw != dm
    assert dmw - dm == {composition.WORKBOOK_NODE_ID}
    # 07W carries the real producer specialist (dispatch routes to it).
    node_07w = next(n for n in compose_manifest(
        manifest, ComponentSelection(deck=True, motion=True, workbook=True)
    ).nodes if n.id == composition.WORKBOOK_NODE_ID)
    assert node_07w.specialist_id == "workbook_producer"


def test_fail_closed_on_unresolved_dependency() -> None:
    """motion consumes deck — selecting motion without deck must fail closed."""
    manifest = _live_manifest()
    with pytest.raises(CompositionError):
        compose_manifest(manifest, ComponentSelection(deck=False, motion=True))


def test_fail_closed_on_dependency_cycle(monkeypatch) -> None:
    """A cyclic producer->consumer DAG must never freeze a partial graph."""
    from dataclasses import replace

    frags = dict(composition.COMPONENT_FRAGMENTS)
    # Introduce a cycle: deck depends on motion, motion depends on deck.
    frags["deck"] = replace(frags["deck"], depends_on=("motion",))
    monkeypatch.setattr(composition, "COMPONENT_FRAGMENTS", frags)

    manifest = _live_manifest()
    with pytest.raises(CompositionError):
        compose_manifest(manifest, ComponentSelection(deck=True, motion=True))
