from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

from app.specialists.quinn_r.quality_control_dispatch import (
    run_postcomposition_validators,
    run_precomposition_validators,
)
from app.specialists.quinn_r.sensory_bridges_dispatch import dispatch_to_sensory_bridges


def test_sensory_wrapper_uses_importlib_loader() -> None:
    source = Path("app/specialists/quinn_r/sensory_bridges_dispatch.py").read_text(
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


def test_quality_wrapper_uses_importlib_loader() -> None:
    source = Path("app/specialists/quinn_r/quality_control_dispatch.py").read_text(
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


def test_sensory_dispatch_short_circuit_when_artifact_missing() -> None:
    out = dispatch_to_sensory_bridges(artifact_path=None, modality="image", gate="qrr")
    assert out["confidence"] == "LOW"


def test_precomposition_short_circuit_when_no_artifacts() -> None:
    out = run_precomposition_validators(artifact_paths=[])
    assert out["status"] == "skipped"


def test_postcomposition_short_circuit_when_no_artifact() -> None:
    out = run_postcomposition_validators(artifact_path=None)
    assert out["status"] == "skipped"


def test_dispatch_wrapper_loc_budgets() -> None:
    for fn in (
        dispatch_to_sensory_bridges,
        run_precomposition_validators,
        run_postcomposition_validators,
    ):
        source = inspect.getsource(fn)
        logical_lines = [line for line in source.splitlines() if line.strip()]
        assert len(logical_lines) <= 75


def test_postcomposition_invokes_loaded_modules(monkeypatch: Any, tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("### Title\nSome content", encoding="utf-8")

    class _Accessibility:
        @staticmethod
        def run_accessibility_check(_: str) -> dict[str, Any]:
            return {"status": "pass"}

    class _Brand:
        @staticmethod
        def run_brand_validation(_: str) -> dict[str, Any]:
            return {"status": "pass"}

    class _Visual:
        @staticmethod
        def validate_visual_fill(_: str) -> dict[str, Any]:
            return {"passed": True}

    def _loader(name: str, _: str) -> Any:
        if "accessibility_checker" in name:
            return _Accessibility()
        if "brand_validator" in name:
            return _Brand()
        return _Visual()

    monkeypatch.setattr(
        "app.specialists.quinn_r.quality_control_dispatch._load_module",
        _loader,
    )
    out = run_postcomposition_validators(artifact_path=str(artifact))
    assert out["status"] == "ok"
    assert out["dimension_scores"]["accessibility"] == "PASS"
    assert out["dimension_scores"]["brand"] == "PASS"
    assert out["dimension_scores"]["composition"] == "PASS"
