"""S2 MF-1 — cross-component dependency/projection handling when a producer is DESELECTED.

A KEPT consumer node may carry a ``dependency_projections`` (or ``dependencies``)
entry whose PRODUCER specialist lives in a component the selection EXCLUDED. The
proven break: node ``14`` (compositor, kept in deck-only) projects
``motion_receipts`` from ``kira`` (node ``07E``, motion) — deck-only excludes
motion, so the frozen graph carried an ORPHANED projection to an absent producer
(silent under-production at runtime).

Contract (composition.OPTIONAL_PROJECTION_KEYS):
  * producer ABSENT + input key OPTIONAL  -> PRUNE the projection/dependency
    (a deck-only compositor runs without motion_receipts);
  * producer ABSENT + input key REQUIRED  -> raise CompositionError (fail closed
    BEFORE compile — no partial graph is ever frozen).
"""

from __future__ import annotations

import pytest

from app.manifest import compiler, load
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
from app.marcus.lesson_plan import composition
from app.marcus.lesson_plan.composition import (
    CompositionError,
    compose_and_digest,
    compose_manifest,
    verify_composition_replay,
)
from app.models.state.component_selection import ComponentSelection

COMPOSITOR_NODE_ID = "14"
MOTION_RECEIPTS_KEY = "motion_receipts"


def _live_manifest():
    return load(DEFAULT_RUN_MANIFEST_PATH)


def _specialists(manifest) -> set[str]:
    return {
        canon
        for node in manifest.nodes
        if (canon := compiler._canonical_specialist_id(node.specialist_id)) is not None
    }


def _assert_no_orphan_inputs(composed, full) -> None:
    """No KEPT node may reference a producer specialist that the selection REMOVED.

    The invariant is selection-relative: a producer that existed as a node in the
    FULL manifest but is absent from the COMPOSED graph (its component was
    deselected) must not survive as an input on any kept node. Implicit/external
    producers that are never manifest nodes (e.g. package_builder) are
    selection-independent and excluded from this check."""
    removed = _specialists(full) - _specialists(composed)
    for node in composed.nodes:
        for key, producer in (node.dependencies or {}).items():
            canon = compiler._canonical_specialist_id(producer)
            assert canon not in removed, (
                f"orphan dependency on node {node.id!r}: key {key!r} -> "
                f"deselected producer {producer!r}"
            )
        for key, spec in (node.dependency_projections or {}).items():
            canon = compiler._canonical_specialist_id(spec.from_specialist)
            assert canon not in removed, (
                f"orphan projection on node {node.id!r}: key {key!r} -> "
                f"deselected producer {spec.from_specialist!r}"
            )


def test_deck_only_prunes_compositor_motion_receipts_projection() -> None:
    """RED floor (i): deck-only composes cleanly, compositor (14) is KEPT, its
    motion_receipts->kira projection is PRUNED, its other projections survive, and
    no orphan projection/dependency remains anywhere in the composition."""
    manifest = _live_manifest()
    composed = compose_manifest(manifest, ComponentSelection(deck=True, motion=False))

    node_ids = {n.id for n in composed.nodes}
    assert COMPOSITOR_NODE_ID in node_ids, "compositor must remain in a deck-only lesson"
    assert "07E" not in node_ids, "kira (07E) is motion — excluded by deck-only"

    compositor = next(n for n in composed.nodes if n.id == COMPOSITOR_NODE_ID)
    projections = compositor.dependency_projections or {}
    assert MOTION_RECEIPTS_KEY not in projections, (
        "the orphaned motion_receipts projection must be pruned from the kept compositor"
    )
    # The non-motion projections (their producers are deck-base specialists) survive.
    assert "gary_slide_output" in projections
    assert "compositor_invocation" in projections

    _assert_no_orphan_inputs(composed, manifest)


def test_deck_only_digest_is_stable_after_prune() -> None:
    """RED floor (i): the deck-only composition is deterministic + replays clean
    after the prune (no orphan destabilizes the two-part digest)."""
    selection = ComponentSelection(deck=True, motion=False)
    first = compose_and_digest(selection)
    second = compose_and_digest(selection)
    assert first.input_closure_digest == second.input_closure_digest
    assert first.composed_graph_digest == second.composed_graph_digest
    # Replay-from-record must not raise (tamper-evidence path stays green).
    verify_composition_replay(first)


def test_deck_plus_motion_retains_motion_receipts_projection() -> None:
    """The prune is selection-driven: when motion is selected, kira is present, so
    the compositor's motion_receipts projection is UNTOUCHED (byte-identity floor)."""
    manifest = _live_manifest()
    composed = compose_manifest(manifest, ComponentSelection.production_default())
    compositor = next(n for n in composed.nodes if n.id == COMPOSITOR_NODE_ID)
    assert MOTION_RECEIPTS_KEY in (compositor.dependency_projections or {})


def test_required_projection_to_excluded_component_fails_closed(monkeypatch) -> None:
    """RED floor (ii): a REQUIRED projection whose producer is excluded raises
    CompositionError BEFORE compile — no partial graph is frozen.

    We make motion_receipts REQUIRED by emptying the optional-key set; deck-only
    then has a kept compositor projecting from an absent producer (kira), which
    must fail closed rather than freeze an orphan."""
    monkeypatch.setattr(composition, "OPTIONAL_PROJECTION_KEYS", frozenset())
    manifest = _live_manifest()
    with pytest.raises(CompositionError):
        compose_manifest(manifest, ComponentSelection(deck=True, motion=False))
