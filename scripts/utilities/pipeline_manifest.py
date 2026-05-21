"""Compatibility loader for the pipeline manifest utility layer.

This module predates the Slab-1 graph-manifest substrate in ``app.manifest``.
Story 4.1 keeps the legacy utility callers stable by accepting both:

- the older ``steps``-shaped manifest fixtures used by Epic 33 utility tests
- the live graph-shaped manifest at ``state/config/pipeline-manifest.yaml``

The returned object intentionally preserves the historic ``manifest.steps``
projection so older HUD / lockstep / workflow-runner callers continue to work
without being rewritten in the same story.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from types import MappingProxyType

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.manifest import load as load_graph_manifest
from app.manifest.schema import PipelineManifest as GraphPipelineManifest
from scripts.utilities.file_helpers import project_root

DEFAULT_MANIFEST_PATH = project_root() / "state" / "config" / "pipeline-manifest.yaml"
KNOWN_SCHEMA_VERSIONS = frozenset(
    {
        "1.0",
        "0.1-stub",
        "v4.2-migration-stub",
        # Slab 7a 2026-04-28 schema bump: additive `fold_with` / `fold_target`
        # per-node fields. Pack stays v4.2; legacy projection ignores fold-flag
        # fields (compiler consumption lands in Story 7a.2).
        "v4.2-migration-stub-with-fold-flags",
    }
)


class ManifestInternalInconsistencyError(ValueError):
    """Raised when manifest links violate internal consistency rules."""


class LearningEventsConfig(BaseModel):
    """Top-level learning-event config."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_ref: str | None = None


class StepLearningEvents(BaseModel):
    """Per-step event emission topology."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    emits: bool = False
    event_types: tuple[str, ...] = ()
    schema_ref: str | None = None

    @model_validator(mode="after")
    def _validate_emit_shape(self) -> StepLearningEvents:
        if self.emits and not self.event_types:
            raise ValueError("learning_events.emits=true requires non-empty event_types")
        if not self.emits and self.event_types:
            raise ValueError("learning_events.emits=false requires empty event_types")
        return self


class StepEntry(BaseModel):
    """Single pipeline step declaration."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    gate: bool
    gate_code: str | None = None
    sub_phase_of: str | None = None
    insertion_after: str | None = None
    hud_tracked: bool = True
    pack_section_anchor: str = Field(..., min_length=1)
    pack_version: str | None = None
    rationale: str | None = None
    learning_events: StepLearningEvents = Field(default_factory=StepLearningEvents)

    @model_validator(mode="after")
    def _validate_gate_code(self) -> StepEntry:
        if self.gate and not self.gate_code:
            raise ValueError(f"step {self.id}: gate=true requires gate_code")
        if not self.gate and self.gate_code:
            raise ValueError(f"step {self.id}: gate=false must not set gate_code")
        return self


class PipelineManifest(BaseModel):
    """Legacy utility projection over the pipeline manifest."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: str
    pack_version: str
    generator_ref: str
    learning_events: LearningEventsConfig = Field(default_factory=LearningEventsConfig)
    block_mode_trigger_paths: tuple[str, ...] = ()
    steps: tuple[StepEntry, ...]
    lane: str | None = None
    entrypoint: str | None = None
    frozen_graph_version: str | None = None

    @model_validator(mode="after")
    def _validate_block_mode_trigger_paths(self) -> PipelineManifest:
        for pattern in self.block_mode_trigger_paths:
            if not isinstance(pattern, str) or not pattern.strip():
                raise ValueError("block_mode_trigger_paths entries must be non-empty strings")
            fnmatch.translate(pattern)
        return self


def _step_from_graph_node(node_index: int, graph_node: object) -> StepEntry:
    node = graph_node
    learning_events = getattr(node, "learning_events", None)
    return StepEntry(
        id=node.id,
        label=getattr(node, "label", None) or node.id,
        gate=bool(getattr(node, "gate", False)),
        gate_code=getattr(node, "gate_code", None),
        sub_phase_of=getattr(node, "sub_phase_of", None),
        insertion_after=getattr(node, "insertion_after", None),
        hud_tracked=bool(getattr(node, "hud_tracked", True)),
        pack_section_anchor=getattr(node, "pack_section_anchor", None)
        or f"{node_index + 1})",
        pack_version=getattr(node, "pack_version", None),
        rationale=getattr(node, "rationale", None),
        learning_events=StepLearningEvents(
            emits=bool(getattr(learning_events, "emits", False)),
            event_types=tuple(getattr(learning_events, "event_types", []) or ()),
            schema_ref=getattr(learning_events, "schema_ref", None),
        ),
    )


def _from_graph_manifest(manifest: GraphPipelineManifest) -> PipelineManifest:
    learning_events = manifest.learning_events
    return PipelineManifest(
        schema_version=manifest.schema_version,
        pack_version=manifest.pack_version or "",
        generator_ref=manifest.generator_ref or "",
        learning_events=LearningEventsConfig(
            schema_ref=getattr(learning_events, "schema_ref", None)
        ),
        block_mode_trigger_paths=tuple(manifest.block_mode_trigger_paths),
        steps=tuple(
            _step_from_graph_node(index, node) for index, node in enumerate(manifest.nodes)
        ),
        lane=manifest.lane,
        entrypoint=manifest.entrypoint,
        frozen_graph_version=manifest.frozen_graph_version,
    )


def _enforce_internal_invariants(manifest: PipelineManifest) -> None:
    if manifest.schema_version not in KNOWN_SCHEMA_VERSIONS:
        raise ManifestInternalInconsistencyError(
            f"Unsupported schema_version: {manifest.schema_version}"
        )

    step_ids = {step.id for step in manifest.steps}
    if len(step_ids) != len(manifest.steps):
        raise ManifestInternalInconsistencyError("Duplicate step IDs found in manifest")

    gate_codes: set[str] = set()
    for step in manifest.steps:
        if step.sub_phase_of and step.sub_phase_of not in step_ids:
            raise ManifestInternalInconsistencyError(
                f"Step {step.id} references missing sub_phase_of target {step.sub_phase_of}"
            )
        if step.insertion_after and step.insertion_after not in step_ids:
            raise ManifestInternalInconsistencyError(
                f"Step {step.id} references missing insertion_after target {step.insertion_after}"
            )
        if step.gate and step.gate_code:
            if step.gate_code in gate_codes:
                raise ManifestInternalInconsistencyError(
                    f"Duplicate gate_code detected: {step.gate_code}"
                )
            gate_codes.add(step.gate_code)


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> PipelineManifest:
    """Load and validate the pipeline manifest compatibility projection."""
    if not path.exists():
        raise FileNotFoundError(f"Pipeline manifest not found at {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ManifestInternalInconsistencyError("Pipeline manifest root must be a mapping")

    if "steps" in raw and "nodes" not in raw:
        manifest = PipelineManifest.model_validate(raw)
    else:
        manifest = _from_graph_manifest(load_graph_manifest(path))

    _enforce_internal_invariants(manifest)
    return manifest


def step_map(manifest: PipelineManifest) -> MappingProxyType[str, StepEntry]:
    """Return immutable id->step mapping."""
    return MappingProxyType({step.id: step for step in manifest.steps})


def hud_steps(manifest: PipelineManifest) -> list[dict[str, str]]:
    """Build HUD-compatible step dictionaries."""
    return [
        {"id": step.id, "name": step.label, "gate": "yes" if step.gate else "no"}
        for step in manifest.steps
        if step.hud_tracked
    ]
