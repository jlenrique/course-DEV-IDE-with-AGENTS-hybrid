"""Thin dispatch seam for Vera sensory perception."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGE_UTILS = REPO_ROOT / "skills" / "sensory-bridges" / "scripts" / "bridge_utils.py"


def _ensure_module_stub(name: str) -> None:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def _ensure_package_stubs() -> None:
    _ensure_module_stub("skills")
    _ensure_module_stub("skills.sensory_bridges")
    _ensure_module_stub("skills.sensory_bridges.scripts")


def _load_perceive_callable() -> Any:
    _ensure_package_stubs()
    module_name = "skills.sensory_bridges.scripts.bridge_utils"
    spec = importlib.util.spec_from_file_location(
        module_name,
        BRIDGE_UTILS,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load sensory bridge utils at {BRIDGE_UTILS}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.perceive


def dispatch_to_sensory_bridges(
    *,
    artifact_path: str | Path | None,
    source_of_truth_path: str | Path | None,
    modality: str,
    gate: str,
) -> dict[str, Any]:
    """Dispatch perception request to sensory-bridges `perceive` entrypoint."""
    if not artifact_path:
        return {
            "schema_version": "1.0",
            "modality": modality,
            "artifact_path": "",
            "confidence": "LOW",
            "confidence_rationale": "no artifact supplied; fixture short-circuit",
            "perception_timestamp": "2026-01-01T00:00:00Z",
            "source_of_truth_path": str(source_of_truth_path or ""),
            "extracted_text": "",
            "layout_description": "",
        }

    perceive = _load_perceive_callable()
    perceived = perceive(
        artifact_path=str(artifact_path),
        modality=modality,
        gate=gate,
        requesting_agent="vera",
    )
    if not isinstance(perceived, dict):
        raise RuntimeError("sensory-bridges perceive must return a mapping")
    perceived["source_of_truth_path"] = str(source_of_truth_path or "")
    return perceived


__all__ = ["dispatch_to_sensory_bridges"]
