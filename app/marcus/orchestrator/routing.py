"""App-namespace wrapper over the root Marcus routing module."""

from marcus.orchestrator.routing import RoutingDecision, route_step

__all__ = ["RoutingDecision", "route_step"]
