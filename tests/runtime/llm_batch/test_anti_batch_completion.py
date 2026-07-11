"""Hermetic guard: product adapter must not use litellm.batch_completion."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter
from app.runtime.llm_batch.errors import LlmBatchError

ADAPTER_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "runtime"
    / "llm_batch"
    / "adapter.py"
)


def test_adapter_source_never_calls_batch_completion() -> None:
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name == "batch_completion" or name.endswith(".batch_completion"):
                hits.append(f"call:{name}")
        if isinstance(node, ast.Attribute) and node.attr == "batch_completion":
            hits.append(f"attr:{node.attr}")
    assert hits == [], hits


def _call_name(func: ast.AST) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = _call_name(func.value)
        return f"{base}.{func.attr}" if base else func.attr
    return ""


def test_adapter_rejects_injected_batch_completion_callable() -> None:
    def batch_completion(*_a: object, **_k: object) -> None:
        return None

    with pytest.raises(LlmBatchError) as exc_info:
        LiteLlmBatchAdapter(create_batch_fn=batch_completion)  # type: ignore[arg-type]
    assert exc_info.value.tag == "llm_batch.forbidden.batch_completion"
