"""Marcus orchestration supervisor preset routing.

This module adapts the Slab 3 FR27 preset switch onto the existing root
`marcus/` package without disturbing the legacy 30-x lesson-planner flow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from app.manifest.schema import PipelineManifest
from app.marcus.orchestrator.routing import RoutingDecision, route_step

SupervisorPreset = Literal["production", "explore"]
SupervisorMode = Literal["plan_and_execute", "react"]


def mode_for_preset(preset: SupervisorPreset) -> SupervisorMode:
    return "react" if preset == "explore" else "plan_and_execute"


@dataclass(slots=True)
class Supervisor:
    """Minimal manifest-driven supervisor used by Slab 3 story tests."""

    preset: SupervisorPreset
    manifest: PipelineManifest

    @property
    def mode(self) -> SupervisorMode:
        return mode_for_preset(self.preset)

    def run_step(self, state: Any) -> RoutingDecision:
        current_node = getattr(state, "current_node", None)
        decision = route_step(current_node=current_node, manifest=self.manifest)
        events = getattr(state, "events", None)
        if isinstance(events, list):
            events.append(
                {
                    "actor": "Marcus",
                    "preset": self.preset,
                    "mode": self.mode,
                    "current_node": current_node,
                    "next_node": decision.next_node_id,
                    "target_specialist": decision.target_specialist,
                }
            )
        state.current_node = decision.next_node_id
        return decision


__all__ = ["Supervisor", "SupervisorMode", "SupervisorPreset", "mode_for_preset"]
