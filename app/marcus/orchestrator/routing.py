"""Manifest-driven Marcus specialist routing."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.manifest.schema import PipelineManifest


class RoutingDecision(BaseModel):
    """One manifest-resolved step transition."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    current_node_id: str
    next_node_id: str
    target_specialist: str
    dispatch_envelope: dict[str, Any] | None = Field(default=None)
    decision_card_schema: str | None = Field(default=None)


def route_step(*, current_node: str | None, manifest: PipelineManifest) -> RoutingDecision:
    from_node = current_node or "__start__"
    edge = next(
        (candidate for candidate in manifest.edges if candidate.from_node == from_node),
        None,
    )
    if edge is None:
        raise ValueError(f"No routing edge found from node {from_node!r}")
    target_node = next(
        (node for node in manifest.nodes if node.id == edge.to),
        None,
    )
    if target_node is None:
        raise ValueError(f"Manifest edge targets unknown node {edge.to!r}")
    if not target_node.specialist_id:
        raise ValueError(
            f"Manifest node {target_node.id!r} has no specialist_id for routing"
        )
    return RoutingDecision(
        current_node_id=from_node,
        next_node_id=target_node.id,
        target_specialist=target_node.specialist_id,
        dispatch_envelope=edge.dispatch_envelope,
        decision_card_schema=edge.decision_card_schema,
    )


__all__ = ["RoutingDecision", "route_step"]
