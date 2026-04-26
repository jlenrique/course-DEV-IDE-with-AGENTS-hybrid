"""Schema-shape tests for `PipelineManifest` / `NodeSpec` / `EdgeSpec` (AC-1.4-A).

Exercises the four-file-lockstep: model round-trip, forbidden-field rejection,
cross-field validators (unique node ids, entrypoint resolves, edges resolve),
and golden-fixture parity for the 3-node basic case and the v4.2-shape subset.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.manifest.schema import (
    EdgeSpec,
    LearningEventsConfig,
    NodeSpec,
    PipelineManifest,
    StepLearningEventsConfig,
)

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "manifest"


def _basic_manifest_kwargs() -> dict:
    return {
        "schema_version": "0.1-stub",
        "lane": "run_graph",
        "entrypoint": "n1",
        "frozen_graph_version": "v0.1-stub",
        "nodes": [NodeSpec(id="n1"), NodeSpec(id="n2")],
        "edges": [
            EdgeSpec.model_validate({"from": "__start__", "to": "n1"}),
            EdgeSpec.model_validate({"from": "n1", "to": "n2"}),
            EdgeSpec.model_validate({"from": "n2", "to": "__end__"}),
        ],
    }


# -------------------------------------------------------------- PipelineManifest


def test_pipeline_manifest_accepts_basic_shape() -> None:
    m = PipelineManifest(**_basic_manifest_kwargs())
    assert m.lane == "run_graph"
    assert [n.id for n in m.nodes] == ["n1", "n2"]
    assert [e.from_node for e in m.edges] == ["__start__", "n1", "n2"]


def test_pipeline_manifest_round_trip_3node() -> None:
    fixture = json.loads((_FIXTURES / "golden_pipeline_manifest_3node.json").read_text())
    m1 = PipelineManifest.model_validate(fixture)
    m2 = PipelineManifest.model_validate(json.loads(m1.model_dump_json(by_alias=True)))
    assert m1 == m2


def test_pipeline_manifest_round_trip_v42_subset() -> None:
    fixture = json.loads((_FIXTURES / "golden_pipeline_manifest_v42_subset.json").read_text())
    m = PipelineManifest.model_validate(fixture)
    assert m.pack_version == "v4.2"
    assert m.generator_ref == "scripts/generators/v42/render.py"
    assert m.learning_events is not None
    assert m.learning_events.schema_ref == "state/config/learning-event-schema.yaml"
    assert m.block_mode_trigger_paths == [
        "state/config/pipeline-manifest.yaml",
        "scripts/utilities/run_hud.py",
    ]
    # v4.2 per-node deltas land as first-class NodeSpec fields
    by_id = {n.id: n for n in m.nodes}
    assert by_id["01"].gate is True
    assert by_id["01"].gate_code == "G0"
    assert by_id["04.55"].insertion_after == "04.5"
    assert by_id["07C"].learning_events is not None
    assert by_id["07C"].learning_events.event_types == ["approval", "revision", "waiver"]


def test_pipeline_manifest_rejects_unknown_top_level_field() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PipelineManifest(
            **_basic_manifest_kwargs(),
            unexpected="value",  # type: ignore[call-arg]
        )


def test_pipeline_manifest_rejects_empty_nodes() -> None:
    kwargs = _basic_manifest_kwargs()
    kwargs["nodes"] = []
    with pytest.raises(ValidationError, match="nodes must be non-empty"):
        PipelineManifest(**kwargs)


def test_pipeline_manifest_rejects_duplicate_node_ids() -> None:
    kwargs = _basic_manifest_kwargs()
    kwargs["nodes"] = [NodeSpec(id="n1"), NodeSpec(id="n1")]
    with pytest.raises(ValidationError, match="duplicate node id"):
        PipelineManifest(**kwargs)


def test_pipeline_manifest_rejects_unresolved_entrypoint() -> None:
    kwargs = _basic_manifest_kwargs()
    kwargs["entrypoint"] = "does_not_exist"
    with pytest.raises(ValidationError, match="entrypoint 'does_not_exist'"):
        PipelineManifest(**kwargs)


def test_pipeline_manifest_accepts_start_sentinel_as_entrypoint() -> None:
    kwargs = _basic_manifest_kwargs()
    kwargs["entrypoint"] = "__start__"
    m = PipelineManifest(**kwargs)
    assert m.entrypoint == "__start__"


def test_pipeline_manifest_rejects_edge_to_unknown_node() -> None:
    kwargs = _basic_manifest_kwargs()
    kwargs["edges"].append(EdgeSpec.model_validate({"from": "n1", "to": "ghost"}))
    with pytest.raises(ValidationError, match="edge to 'ghost'"):
        PipelineManifest(**kwargs)


def test_pipeline_manifest_rejects_edge_from_unknown_node() -> None:
    kwargs = _basic_manifest_kwargs()
    kwargs["edges"].append(EdgeSpec.model_validate({"from": "ghost", "to": "n2"}))
    with pytest.raises(ValidationError, match="edge from 'ghost'"):
        PipelineManifest(**kwargs)


def test_pipeline_manifest_validate_assignment_rejects_bad_mutation() -> None:
    m = PipelineManifest(**_basic_manifest_kwargs())
    with pytest.raises(ValidationError, match="Input should be 'run_graph' or 'dev_graph'"):
        m.lane = "not_a_lane"  # type: ignore[assignment]


# -------------------------------------------------------------- NodeSpec


def test_node_spec_rationale_accepts_empty_and_whitespace() -> None:
    # Anti-pattern checklist §6 / A5 — no min_length on verbatim free-text fields.
    for value in ["", " ", "\t", "\n", "multi\nline"]:
        n = NodeSpec(id="x", rationale=value)
        assert n.rationale == value


def test_node_spec_rejects_empty_id() -> None:
    with pytest.raises(ValidationError, match="at least 1 character"):
        NodeSpec(id="")


def test_node_spec_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        NodeSpec(id="x", unexpected="value")  # type: ignore[call-arg]


def test_node_spec_learning_events_nested_shape() -> None:
    n = NodeSpec(
        id="x",
        learning_events=StepLearningEventsConfig(
            emits=True,
            event_types=["plan.locked"],
            schema_ref="a/b.yaml",
        ),
    )
    assert n.learning_events is not None
    assert n.learning_events.event_types == ["plan.locked"]


# -------------------------------------------------------------- EdgeSpec


def test_edge_spec_from_alias_populates_from_node() -> None:
    e = EdgeSpec.model_validate({"from": "a", "to": "b"})
    assert e.from_node == "a"
    # Serializes back with the YAML-facing alias
    assert json.loads(e.model_dump_json(by_alias=True))["from"] == "a"


def test_edge_spec_rejects_empty_from_and_to() -> None:
    with pytest.raises(ValidationError, match="at least 1 character"):
        EdgeSpec.model_validate({"from": "", "to": "b"})
    with pytest.raises(ValidationError, match="at least 1 character"):
        EdgeSpec.model_validate({"from": "a", "to": ""})


def test_edge_spec_condition_and_dispatch_envelope_optional() -> None:
    e = EdgeSpec.model_validate({"from": "a", "to": "b"})
    assert e.condition is None
    assert e.dispatch_envelope is None
    assert e.decision_card_schema is None

    e2 = EdgeSpec.model_validate(
        {
            "from": "a",
            "to": "b",
            "condition": "always_true",
            "dispatch_envelope": {"k": 1},
            "decision_card_schema": "app.models.decision_cards.g2c:G2CCard",
        }
    )
    assert e2.condition == "always_true"
    assert e2.dispatch_envelope == {"k": 1}
    assert e2.decision_card_schema == "app.models.decision_cards.g2c:G2CCard"


# -------------------------------------------------------------- LearningEventsConfig


def test_learning_events_config_defaults() -> None:
    cfg = LearningEventsConfig()
    assert cfg.schema_ref is None


def test_learning_events_config_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        LearningEventsConfig(ghost="x")  # type: ignore[call-arg]
