"""Importlib dispatch wrapper for Quinn-R sensory-bridges access."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError

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
    spec = importlib.util.spec_from_file_location(module_name, BRIDGE_UTILS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load sensory bridge utils at {BRIDGE_UTILS}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.perceive


class SensoryBridgeDispatchError(SpecialistDispatchError):
    """Raised when perception inputs are missing (S0 fail-loud policy)."""


def dispatch_to_sensory_bridges(
    *,
    artifact_path: str | Path | None,
    modality: str,
    gate: str,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    """S0 fail-loud policy (SCP 2026-06-11): missing artifact RAISES; the
    LOW-confidence short-circuit needs explicit ``allow_fixture`` opt-in.
    Quinn-R approved slides it never received in Trial-3 attempt-4 because
    this seam silently degraded instead of refusing."""
    if not artifact_path:
        if not allow_fixture:
            raise SensoryBridgeDispatchError(
                f"dispatch_to_sensory_bridges missing required input: "
                f"artifact_path (gate={gate})",
                tag="sensory.input.missing",
            )
        return {
            "schema_version": "1.0",
            "modality": modality,
            "artifact_path": "",
            "confidence": "LOW",
            "confidence_rationale": "no artifact supplied; fixture short-circuit",
            "perception_timestamp": "2026-01-01T00:00:00Z",
            "extracted_text": "",
            "layout_description": "",
        }
    perceive = _load_perceive_callable()
    perceived = perceive(
        artifact_path=str(artifact_path),
        modality=modality,
        gate=gate,
        requesting_agent="quinn-r",
    )
    if not isinstance(perceived, dict):
        raise RuntimeError("sensory-bridges perceive must return a mapping")
    return perceived


__all__ = ["SensoryBridgeDispatchError", "dispatch_to_sensory_bridges"]
