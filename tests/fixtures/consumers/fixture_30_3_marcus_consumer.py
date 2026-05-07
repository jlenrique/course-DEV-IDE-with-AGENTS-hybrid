"""Marcus consumer fixture (Story 31-3 AC-T.6 + Q-R2-B).

Minimal import-and-usage stub demonstrating how Story 30-3 (Marcus
orchestrator 4A loop) will consume :data:`MODALITY_REGISTRY` to route
scope-delegation decisions to concrete producers.

**Q-R2-B staleness-gate-at-consumer-boundary pattern:** additionally
demonstrates that given a :class:`ProductionContext` at revision N and a
:class:`ProducedAsset` with ``fulfills="unit-X@M"``, the consumer verifies
``M == N`` before acting on the asset. Downstream 30-3 / 30-4 will
replicate this pattern.

The ``demonstrate()`` callable at module scope is the loader entry point.
"""

from __future__ import annotations

from app.marcus.lesson_plan import (
    MODALITY_REGISTRY,
    ProducedAsset,
    ProductionContext,
    get_modality_entry,
)


def _route_scope_delegation(modality_ref: str) -> str:
    """Demonstrate the routing pattern 30-3 will use at plan-lock fanout."""
    entry = get_modality_entry(modality_ref)
    if entry is None:
        return f"reject: {modality_ref!r} not in MODALITY_REGISTRY"
    if entry.status == "pending":
        return f"defer: {modality_ref!r} status=pending"
    # ready → routing would proceed to the concrete producer.
    return f"route: {modality_ref!r} status=ready"


def _staleness_gate(asset: ProducedAsset, context: ProductionContext) -> bool:
    """Q-R2-B: the staleness-gate-at-consumer-boundary pattern.

    Returns True iff the asset's fulfills-revision matches the context's
    lesson_plan_revision (i.e., asset is fresh against the current plan).
    """
    asset_revision = int(asset.fulfills.split("@", 1)[1])
    return asset_revision == context.lesson_plan_revision


def demonstrate() -> None:
    """Loader entry point. Invoked by test_consumer_fixtures_load."""
    # (1) Route a ready modality.
    assert _route_scope_delegation("blueprint") == "route: 'blueprint' status=ready"

    # (2) Defer a pending modality.
    assert _route_scope_delegation("handout") == "defer: 'handout' status=pending"

    # (3) Reject an unregistered modality.
    result = _route_scope_delegation("not-in-registry")
    assert "reject" in result

    # (4) Direct registry key-access is permitted (public Mapping).
    slides_entry = MODALITY_REGISTRY["slides"]
    assert slides_entry.status == "ready"

    # (5) Q-R2-B staleness gate: fresh asset passes, stale asset fails.
    context = ProductionContext(
        lesson_plan_revision=5,
        lesson_plan_digest="abc123def",
    )
    fresh_asset = ProducedAsset(
        asset_ref="blueprint-unit-foo-at-rev5",
        modality_ref="blueprint",
        source_plan_unit_id="unit-foo",
        asset_path="artifacts/unit-foo.md",
        fulfills="unit-foo@5",
    )
    assert _staleness_gate(fresh_asset, context) is True

    stale_asset = ProducedAsset(
        asset_ref="blueprint-unit-foo-at-rev4",
        modality_ref="blueprint",
        source_plan_unit_id="unit-foo",
        asset_path="artifacts/unit-foo-rev4.md",
        fulfills="unit-foo@4",
    )
    assert _staleness_gate(stale_asset, context) is False
