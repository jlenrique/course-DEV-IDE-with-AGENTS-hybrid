from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.manifest.compiler import compile_run_graph
from app.manifest.exceptions import CompileError
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest


def _manifest(nodes: list[NodeSpec]) -> PipelineManifest:
    return PipelineManifest(
        schema_version="test",
        lane="run_graph",
        entrypoint="01",
        frozen_graph_version="v42",
        nodes=nodes,
        edges=[
            EdgeSpec(from_node="__start__", to=nodes[0].id),
            *[
                EdgeSpec(from_node=left.id, to=right.id)
                for left, right in zip(nodes, nodes[1:], strict=False)
            ],
            EdgeSpec(from_node=nodes[-1].id, to="__end__"),
        ],
    )


def test_schema_accepts_empty_dependencies_field() -> None:
    node = NodeSpec(id="01", specialist_id="texas", dependencies={})

    assert node.dependencies == {}


def test_schema_accepts_declared_dependencies_field() -> None:
    node = NodeSpec(
        id="02",
        specialist_id="cd",
        dependencies={"source_bundle": "texas"},
    )

    assert node.dependencies == {"source_bundle": "texas"}


def test_schema_rejects_non_dict_dependencies_shape() -> None:
    with pytest.raises(ValidationError, match="dependencies"):
        NodeSpec.model_validate(
            {
                "id": "02",
                "specialist_id": "cd",
                "dependencies": ["source_bundle", "texas"],
            }
        )


def test_schema_rejects_circular_dependencies_at_compile_time() -> None:
    manifest = _manifest(
        [
            NodeSpec(
                id="01",
                specialist_id="alpha",
                dependencies={"upstream_output": "beta"},
            ),
            NodeSpec(
                id="02",
                specialist_id="beta",
                dependencies={"upstream_output": "alpha"},
            ),
        ]
    )

    with pytest.raises(CompileError, match="circular dependency"):
        compile_run_graph(manifest, dispatch_registry={})


def test_schema_rejects_alias_normalized_circular_dependencies_at_compile_time() -> None:
    manifest = _manifest(
        [
            NodeSpec(
                id="01",
                specialist_id="quinn-r",
                dependencies={"upstream_output": "kira"},
            ),
            NodeSpec(
                id="02",
                specialist_id="kira",
                dependencies={"upstream_output": "quinn_r"},
            ),
        ]
    )

    with pytest.raises(CompileError, match="kira -> quinn_r -> kira"):
        compile_run_graph(
            manifest,
            dispatch_registry={
                "quinn_r": "app.specialists.quinn_r.graph:build_quinn_r_graph",
                "kira": "app.specialists.kira.graph:build_kira_graph",
            },
        )
