from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from app.specialists.gary.gamma_dispatch import (
    DEFAULT_FIXTURE_RECEIPT,
    GammaDispatchError,
    dispatch_to_gamma,
)


def test_dispatch_does_not_call_subprocess() -> None:
    source = Path("app/specialists/gary/gamma_dispatch.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "subprocess" not in imports


def test_dispatch_short_circuits_on_no_directive() -> None:
    # S0 fail-loud policy: fixture path now requires explicit opt-in.
    receipt = dispatch_to_gamma(directive_path=None, export_dir=None, allow_fixture=True)
    assert receipt["generation_id"] == "gen-fixture-001"
    assert receipt["gary_slide_output"]
    assert DEFAULT_FIXTURE_RECEIPT.is_file()


def test_dispatch_imports_execute_generation_directly() -> None:
    from app.specialists.gary import gamma_dispatch as module

    assert callable(module.execute_generation)


def test_dispatch_handles_timeout_callee(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    directive = tmp_path / "directive.md"
    directive.write_text("hello", encoding="utf-8")

    def _timeout(*_: Any, **__: Any) -> dict[str, Any]:
        raise TimeoutError("timed out")

    monkeypatch.setattr("app.specialists.gary.gamma_dispatch.execute_generation", _timeout)
    with pytest.raises(GammaDispatchError) as exc_info:
        dispatch_to_gamma(directive_path=directive, export_dir=tmp_path / "exports")
    assert exc_info.value.tag == "receipt.parsed.timeout"
