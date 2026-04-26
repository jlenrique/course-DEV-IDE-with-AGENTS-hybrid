from __future__ import annotations

from types import SimpleNamespace

from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest
from marcus.orchestrator.supervisor import Supervisor


def _manifest() -> PipelineManifest:
    return PipelineManifest.model_validate(
        {
            "schema_version": "0.1-test",
            "lane": "run_graph",
            "entrypoint": "01",
            "frozen_graph_version": "v-test",
            "nodes": [
                NodeSpec(id="01", specialist_id="alpha"),
                NodeSpec(id="02", specialist_id="beta"),
                NodeSpec(id="03", specialist_id="gamma"),
            ],
            "edges": [
                EdgeSpec.model_validate({"from": "__start__", "to": "01"}),
                EdgeSpec.model_validate({"from": "01", "to": "02"}),
                EdgeSpec.model_validate({"from": "02", "to": "03"}),
                EdgeSpec.model_validate({"from": "03", "to": "01"}),
            ],
        }
    )


def test_supervisor_runs_plan_and_execute_when_preset_production() -> None:
    state = SimpleNamespace(current_node=None, events=[])
    supervisor = Supervisor(preset="production", manifest=_manifest())

    decisions = [supervisor.run_step(state) for _ in range(3)]

    assert supervisor.mode == "plan_and_execute"
    assert [decision.target_specialist for decision in decisions] == ["alpha", "beta", "gamma"]
    assert len(state.events) == 3


def test_supervisor_runs_react_when_preset_explore() -> None:
    state = SimpleNamespace(current_node=None, events=[])
    supervisor = Supervisor(preset="explore", manifest=_manifest())

    decisions = [supervisor.run_step(state) for _ in range(3)]

    assert supervisor.mode == "react"
    assert [decision.target_specialist for decision in decisions] == ["alpha", "beta", "gamma"]
    assert len(state.events) == 3
