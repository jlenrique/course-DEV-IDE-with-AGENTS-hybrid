from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path
from typing import Any

from app.specialists.vera.sensory_bridges_dispatch import (
    _load_perceive_callable,
    dispatch_to_sensory_bridges,
)


def test_dispatch_uses_importlib_loader_pattern() -> None:
    source = Path("app/specialists/vera/sensory_bridges_dispatch.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "importlib.util" in imports


def test_loader_registers_bridge_utils_module_for_runtime_resolution() -> None:
    perceive = _load_perceive_callable()
    assert callable(perceive)
    assert "skills.sensory_bridges.scripts.bridge_utils" in sys.modules


def test_dispatch_short_circuits_when_artifact_missing() -> None:
    # S0 fail-loud policy: fixture short-circuit now requires explicit opt-in.
    result = dispatch_to_sensory_bridges(
        artifact_path=None,
        source_of_truth_path=None,
        modality="image",
        gate="fidelity",
        allow_fixture=True,
    )
    assert result["confidence"] == "LOW"
    assert result["schema_version"] == "1.0"


def test_dispatch_calls_perceive_entrypoint(monkeypatch: Any, tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("artifact", encoding="utf-8")
    captured: dict[str, Any] = {}

    def _fake_perceive(**kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {
            "schema_version": "1.0",
            "modality": kwargs["modality"],
            "artifact_path": kwargs["artifact_path"],
            "confidence": "MEDIUM",
            "confidence_rationale": "ok",
            "perception_timestamp": "2026-01-01T00:00:00Z",
        }

    monkeypatch.setattr(
        "app.specialists.vera.sensory_bridges_dispatch._load_perceive_callable",
        lambda: _fake_perceive,
    )
    out = dispatch_to_sensory_bridges(
        artifact_path=artifact,
        source_of_truth_path="truth.md",
        modality="image",
        gate="fidelity",
    )
    assert captured["requesting_agent"] == "vera"
    assert out["source_of_truth_path"] == "truth.md"


def test_sensory_dispatch_loc_budget() -> None:
    source = inspect.getsource(dispatch_to_sensory_bridges)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 75
