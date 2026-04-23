"""End-to-end loader+compiler+invoke smoke (AC-1.4-F).

Loads the stub manifest, compiles, invokes one node, asserts the output.
Verifies the 1.1c stub-smoke payload contract (`{"smoke": "ok", ...}`) is
preserved byte-equivalently by running `app.smoke_test.run_smoke()` after
Story 1.4's schema tightening.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from langgraph.graph.state import StateGraph

from app.manifest import CompileError, compile, load
from app.smoke_test import run_smoke


def test_loader_compiler_invoke_end_to_end() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    manifest = load(repo_root / "state" / "config" / "pipeline-manifest.yaml")
    graph = compile(manifest)
    assert isinstance(graph, StateGraph)

    compiled = graph.compile()
    run_id = str(uuid4())
    result = compiled.invoke(
        {
            "run_id": run_id,
            "graph_version": "v0.1-stub",
            "status": "pending",
        }
    )
    # Slab 1 passthrough stubs return `{}`; input state flows through unchanged.
    # Slab 2 replaces passthroughs with specialists that update RunState fields.
    assert result["run_id"] == run_id
    assert result["graph_version"] == "v0.1-stub"
    assert result["status"] in {"pending", "running", "complete"}


def test_1_1c_smoke_payload_contract_preserved() -> None:
    """After 1.4's schema tightening, 1.1c's smoke path still yields `{"smoke": "ok"}`."""
    payload = run_smoke()
    assert payload["smoke"] == "ok"
    assert payload["node"] == "noop"
    assert payload["input"] == "ping"


def test_loader_compiler_fails_when_frozen_graph_dir_missing(tmp_path: Path) -> None:
    """Confirm CompileError surfaces when compiling against a repo root that lacks the dir."""
    manifest = load(
        Path(__file__).resolve().parents[3] / "state" / "config" / "pipeline-manifest.yaml"
    )
    with pytest.raises(CompileError, match="directory missing"):
        compile(manifest, repo_root=tmp_path)
