from __future__ import annotations

from app.cora import CompiledGraphHandle, compile_dev_graph
from app.cora.graph import DEFAULT_DEV_MANIFEST_PATH


def test_compile_dev_graph_returns_compiled_handle() -> None:
    handle = compile_dev_graph(DEFAULT_DEV_MANIFEST_PATH)

    assert isinstance(handle, CompiledGraphHandle)
    assert handle.thread_namespace_template.startswith("dev/")
    assert handle.thread_namespace_for("4.2") == "dev/4.2"


def test_thread_namespace_is_distinct_from_run_lane() -> None:
    handle = compile_dev_graph(DEFAULT_DEV_MANIFEST_PATH)

    assert handle.thread_namespace_for("story-42").startswith("dev/")
    assert not handle.thread_namespace_for("story-42").startswith("run/")
