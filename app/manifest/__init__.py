"""Manifest package — Slab 1 manifest-as-graph-config substrate (architecture D6).

Exports:
- `PipelineManifest` / `NodeSpec` / `EdgeSpec` / `LearningEventsConfig` /
  `StepLearningEventsConfig` / `ManifestLane` — the Pydantic schema family (AC-1.4-A)
- `load(path)` — YAML → `PipelineManifest` loader (AC-1.4-B)
- `compile(manifest)` — `PipelineManifest` → `StateGraph` compiler (AC-1.4-C/D/E2)
- `ManifestValidationError` / `CompileError` — typed error surface
"""

from app.manifest.compiler import compile  # noqa: A004 — matches spec naming
from app.manifest.exceptions import CompileError, ManifestValidationError
from app.manifest.lanes import compile_run_graph
from app.manifest.loader import load
from app.manifest.schema import (
    EdgeSpec,
    LearningEventsConfig,
    ManifestLane,
    NodeSpec,
    PipelineManifest,
    StepLearningEventsConfig,
)

__all__ = [
    "CompileError",
    "EdgeSpec",
    "LearningEventsConfig",
    "ManifestLane",
    "ManifestValidationError",
    "NodeSpec",
    "PipelineManifest",
    "StepLearningEventsConfig",
    "compile",
    "compile_run_graph",
    "load",
]
