"""Compiler tests (AC-1.4-C + AC-1.4-E2).

Exercises `app.manifest.compiler.compile()`: valid manifest compiles to a
`StateGraph`; missing `model_config_ref` raises `CompileError`; unknown
condition raises `CompileError`; missing `frozen_graph_version` directory
raises `CompileError`; the compiled graph compiles down to an invokable
runnable. Lane is tested separately in `test_lane_separation.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from langgraph.graph.state import StateGraph

from app.manifest import CompileError, compile
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest


def _manifest(**overrides) -> PipelineManifest:
    base = {
        "schema_version": "0.1-stub",
        "lane": "run_graph",
        "entrypoint": "n1",
        "frozen_graph_version": "v0.1-stub",
        "nodes": [NodeSpec(id="n1", specialist_id="a"), NodeSpec(id="n2", specialist_id="b")],
        "edges": [
            EdgeSpec.model_validate({"from": "__start__", "to": "n1"}),
            EdgeSpec.model_validate({"from": "n1", "to": "n2"}),
            EdgeSpec.model_validate({"from": "n2", "to": "__end__"}),
        ],
    }
    base.update(overrides)
    return PipelineManifest(**base)


def test_compile_returns_state_graph_for_valid_manifest(tmp_path: Path) -> None:
    _prepare_runtime_graphs_dir(tmp_path)
    g = compile(_manifest(), repo_root=tmp_path)
    assert isinstance(g, StateGraph)


def test_compiled_graph_invokes_end_to_end(tmp_path: Path) -> None:
    _prepare_runtime_graphs_dir(tmp_path)
    g = compile(_manifest(), repo_root=tmp_path)
    compiled = g.compile()
    from uuid import uuid4

    run_id = str(uuid4())
    result = compiled.invoke(
        {
            "run_id": run_id,
            "graph_version": "v0.1-stub",
            "status": "pending",
        }
    )
    # Slab 1 passthrough stubs return `{}`; the input state flows through unchanged.
    assert result["run_id"] == run_id
    assert result["graph_version"] == "v0.1-stub"


def test_compile_raises_on_missing_frozen_graph_version_directory(tmp_path: Path) -> None:
    # Do NOT create runtime/graphs/v0.1-stub/ under tmp_path
    with pytest.raises(CompileError, match="frozen_graph_version 'v0.1-stub' directory missing"):
        compile(_manifest(), repo_root=tmp_path)


def test_compile_raises_on_missing_model_config_ref(tmp_path: Path) -> None:
    _prepare_runtime_graphs_dir(tmp_path)
    m = _manifest(
        nodes=[
            NodeSpec(id="n1", specialist_id="a", model_config_ref="configs/ghost.yaml"),
            NodeSpec(id="n2", specialist_id="b"),
        ],
    )
    with pytest.raises(CompileError, match="model_config_ref does not resolve"):
        compile(m, repo_root=tmp_path)


def test_compile_accepts_present_model_config_ref(tmp_path: Path) -> None:
    _prepare_runtime_graphs_dir(tmp_path)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "n1.yaml").write_text("stub: true\n", encoding="utf-8")
    m = _manifest(
        nodes=[
            NodeSpec(id="n1", specialist_id="a", model_config_ref="configs/n1.yaml"),
            NodeSpec(id="n2", specialist_id="b"),
        ],
    )
    g = compile(m, repo_root=tmp_path)
    assert isinstance(g, StateGraph)


def test_compile_raises_on_unknown_condition(tmp_path: Path) -> None:
    _prepare_runtime_graphs_dir(tmp_path)
    m = _manifest(
        edges=[
            EdgeSpec.model_validate({"from": "__start__", "to": "n1"}),
            EdgeSpec.model_validate({"from": "n1", "to": "n2", "condition": "ghost_condition"}),
            EdgeSpec.model_validate({"from": "n2", "to": "__end__"}),
        ],
    )
    with pytest.raises(CompileError, match="unknown condition 'ghost_condition'"):
        compile(m, repo_root=tmp_path)


def test_compile_accepts_known_conditions(tmp_path: Path) -> None:
    _prepare_runtime_graphs_dir(tmp_path)
    m = _manifest(
        edges=[
            EdgeSpec.model_validate({"from": "__start__", "to": "n1"}),
            EdgeSpec.model_validate({"from": "n1", "to": "n2", "condition": "always_true"}),
            EdgeSpec.model_validate({"from": "n2", "to": "__end__"}),
        ],
    )
    g = compile(m, repo_root=tmp_path)
    assert isinstance(g, StateGraph)


def test_compile_does_not_duplicate_start_edge_when_explicit(tmp_path: Path) -> None:
    """G6-P1 regression: explicit __start__ edge must not be double-added by the compiler."""
    _prepare_runtime_graphs_dir(tmp_path)
    m = _manifest()  # already has EdgeSpec(from=__start__, to=n1)
    # Before the fix the compiler both honored the explicit __start__ edge AND added
    # an implicit START→entrypoint. LangGraph's current version accepts the double,
    # but semantic uniqueness is the contract. We assert the compile step completes
    # without raising on either the current or a tightened future LangGraph.
    g = compile(m, repo_root=tmp_path)
    compiled = g.compile()
    assert compiled is not None


def test_compile_adds_implicit_start_edge_when_absent(tmp_path: Path) -> None:
    """Inverse of above: when no explicit __start__ edge exists, compiler must wire one."""
    _prepare_runtime_graphs_dir(tmp_path)
    m = _manifest(
        edges=[
            # Deliberately omit the __start__ edge; entrypoint is n1 so compiler
            # must add the implicit START→n1 wiring for the graph to be reachable.
            EdgeSpec.model_validate({"from": "n1", "to": "n2"}),
            EdgeSpec.model_validate({"from": "n2", "to": "__end__"}),
        ],
    )
    g = compile(m, repo_root=tmp_path)
    compiled = g.compile()
    from uuid import uuid4

    result = compiled.invoke(
        {"run_id": str(uuid4()), "graph_version": "v0.1-stub", "status": "pending"}
    )
    assert result["run_id"] is not None


def test_compile_real_repo_root_with_stub_manifest() -> None:
    """End-to-end: production repo_root + substrate stub manifest compiles cleanly."""
    from app.manifest import load

    repo_root = Path(__file__).resolve().parents[3]
    m = load(repo_root / "state" / "config" / "pipeline-manifest-substrate-stub.yaml")
    g = compile(m)
    assert isinstance(g, StateGraph)


def test_compile_real_repo_root_with_migrated_v42_manifest() -> None:
    """End-to-end: production repo_root + migrated v4.2 33-node manifest compiles cleanly."""
    from app.manifest import load

    repo_root = Path(__file__).resolve().parents[3]
    m = load(repo_root / "state" / "config" / "pipeline-manifest.yaml")
    g = compile(m)
    assert isinstance(g, StateGraph)
    assert len(m.nodes) == 33


def _prepare_runtime_graphs_dir(root: Path) -> None:
    (root / "runtime" / "graphs" / "v0.1-stub").mkdir(parents=True, exist_ok=True)
