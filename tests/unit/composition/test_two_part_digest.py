"""S2 — two-part content-addressed digest: structure, differential, purity, byte-identity."""

from __future__ import annotations

from app.manifest import compiler, load
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
from app.marcus.lesson_plan.composition import compose_and_digest
from app.models.state.component_selection import ComponentSelection
from app.runtime.compiled_graph_digest import DIGEST_SCHEMA_VERSION

_HEX64 = 64


def _live_manifest():
    return load(DEFAULT_RUN_MANIFEST_PATH)


def _sel(**kw) -> ComponentSelection:
    return ComponentSelection(**kw)


def test_digest_has_two_parts_and_schema_version() -> None:
    d = compose_and_digest(_sel(deck=True, motion=True), manifest=_live_manifest())
    assert d.digest_schema_version == DIGEST_SCHEMA_VERSION
    assert len(d.input_closure_digest) == _HEX64
    assert len(d.composed_graph_digest) == _HEX64
    assert d.input_closure_digest != d.composed_graph_digest


def test_differential_pairwise_distinct_on_both_parts() -> None:
    m = _live_manifest()
    deck = compose_and_digest(_sel(deck=True, motion=False), manifest=m)
    dm = compose_and_digest(_sel(deck=True, motion=True), manifest=m)
    dmw = compose_and_digest(_sel(deck=True, motion=True, workbook=True), manifest=m)

    parts = [
        (x.input_closure_digest, x.composed_graph_digest) for x in (deck, dm, dmw)
    ]
    # Pairwise distinct on BOTH digest parts.
    assert len({p[0] for p in parts}) == 3, "input_closure_digests not pairwise distinct"
    assert len({p[1] for p in parts}) == 3, "composed_graph_digests not pairwise distinct"


def test_differential_distinct_on_topology() -> None:
    m = _live_manifest()
    deck = compose_and_digest(_sel(deck=True, motion=False), manifest=m)
    dm = compose_and_digest(_sel(deck=True, motion=True), manifest=m)
    dmw = compose_and_digest(_sel(deck=True, motion=True, workbook=True), manifest=m)

    assert set(deck.composed_node_ids) != set(dm.composed_node_ids)
    assert set(dm.composed_node_ids) != set(dmw.composed_node_ids)
    # motion-bundle contains the kira motion node; deck-only does not.
    assert "07E" in dm.composed_node_ids
    assert "07E" not in deck.composed_node_ids


def test_composition_is_a_pure_function() -> None:
    """Same selection => identical (input_closure_digest, composed_graph_digest)."""
    m = _live_manifest()
    a = compose_and_digest(_sel(deck=True, motion=True), manifest=m)
    b = compose_and_digest(_sel(deck=True, motion=True), manifest=m)
    assert a.input_closure_digest == b.input_closure_digest
    assert a.composed_graph_digest == b.composed_graph_digest
    # Same input_closure_digest MUST yield the same composed_graph_digest.
    assert a.input_closure_digest == b.input_closure_digest
    assert a.composed_graph_digest == b.composed_graph_digest


def test_byte_identity_full_selection_matches_raw_graph() -> None:
    """deck+motion composed node_ids/edges equal the raw (today) compiled graph."""
    m = _live_manifest()
    d = compose_and_digest(_sel(deck=True, motion=True), manifest=m)
    raw_graph = compiler.compile(m)
    raw_nodes = sorted(str(n) for n in raw_graph.nodes)
    raw_edges = sorted([str(s), str(t)] for s, t in raw_graph.edges)
    assert d.composed_node_ids == raw_nodes
    assert d.composed_edge_tuples == raw_edges
