"""Cora dev-graph manifest loader and compiler."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

import yaml
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from app.manifest.exceptions import CompileError, ManifestValidationError
from app.models.state.story_state import StoryState

DEFAULT_DEV_MANIFEST_PATH = (
    Path(__file__).resolve().parents[2] / "state" / "config" / "dev-graph-manifest.yaml"
)


class DevGraphNodeSpec(BaseModel):
    """One Cora dev-graph node."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    handler: str = Field(..., min_length=1)


class DevGraphEdgeSpec(BaseModel):
    """One directed edge in the Cora dev-graph manifest."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        strict=True,
        populate_by_name=True,
    )

    from_node: str = Field(..., alias="from", min_length=1)
    to: str = Field(..., min_length=1)


class DevGraphManifest(BaseModel):
    """Strict manifest for the Cora dev-lane graph."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        strict=True,
        populate_by_name=True,
    )

    schema_version: str = Field(..., min_length=1)
    nodes: list[DevGraphNodeSpec] = Field(..., alias="dev_nodes", min_length=1)
    edges: list[DevGraphEdgeSpec] = Field(default_factory=list, alias="dev_edges")
    thread_namespace: str = Field(..., min_length=1)

    @field_validator("thread_namespace")
    @classmethod
    def _thread_namespace_must_target_dev_lane(cls, value: str) -> str:
        if not value.startswith("dev/"):
            raise ValueError("thread_namespace must start with 'dev/'")
        if "{story_id}" not in value:
            raise ValueError("thread_namespace must include '{story_id}' placeholder")
        return value

    @model_validator(mode="after")
    def _validate_topology(self) -> DevGraphManifest:
        node_ids = {node.id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("duplicate node id in dev graph manifest")

        sentinels = {"__start__", "__end__"}
        for edge in self.edges:
            if edge.from_node not in node_ids and edge.from_node not in sentinels:
                raise ValueError(f"edge from {edge.from_node!r} does not resolve to a node id")
            if edge.to not in node_ids and edge.to not in sentinels:
                raise ValueError(f"edge to {edge.to!r} does not resolve to a node id")
        return self


@dataclass(frozen=True)
class CompiledGraphHandle:
    """Compiled Cora graph plus its thread-namespace template."""

    graph: Any
    manifest: DevGraphManifest
    thread_namespace_template: str

    def thread_namespace_for(self, story_id: str) -> str:
        return self.thread_namespace_template.format(story_id=story_id)


def _edge_target(name: str) -> Any:
    if name == "__start__":
        return START
    if name == "__end__":
        return END
    return name


def _resolve_handler(handler_ref: str) -> Any:
    try:
        module_name, attr_name = handler_ref.split(":", maxsplit=1)
    except ValueError as exc:
        raise CompileError(
            f"handler ref {handler_ref!r} must use '<module>:<callable>' syntax"
        ) from exc
    module = import_module(module_name)
    try:
        handler = getattr(module, attr_name)
    except AttributeError as exc:
        raise CompileError(f"handler {handler_ref!r} does not resolve") from exc
    if not callable(handler):
        raise CompileError(f"handler {handler_ref!r} is not callable")
    return handler


def load_dev_graph_manifest(path: Path | str = DEFAULT_DEV_MANIFEST_PATH) -> DevGraphManifest:
    """Load a `DevGraphManifest` from YAML."""
    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise ManifestValidationError(
            f"dev graph manifest file not found: {manifest_path} "
            f"(cwd-resolved: {manifest_path.resolve()})"
        )
    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(raw_text)
    except (OSError, yaml.YAMLError) as exc:
        raise ManifestValidationError(
            f"dev graph manifest parse failed at {manifest_path}: {exc}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ManifestValidationError(
            f"dev graph manifest root must be a mapping (got {type(parsed).__name__})"
        )
    try:
        return DevGraphManifest.model_validate(parsed)
    except ValidationError as exc:
        raise ManifestValidationError(
            f"dev graph manifest validation failed at {manifest_path}:\n{exc}"
        ) from exc


def format_thread_namespace(story_id: str) -> str:
    """Return the concrete checkpoint namespace for one story."""
    return f"dev/{story_id}"


def _coerce_manifest(
    manifest: DevGraphManifest | Path | str | None,
) -> DevGraphManifest:
    if manifest is None:
        return load_dev_graph_manifest(DEFAULT_DEV_MANIFEST_PATH)
    if isinstance(manifest, DevGraphManifest):
        return manifest
    return load_dev_graph_manifest(manifest)


def _build_graph(manifest: DevGraphManifest) -> StateGraph:
    graph = StateGraph(state_schema=StoryState)
    for node in manifest.nodes:
        graph.add_node(node.id, _resolve_handler(node.handler))

    explicit_start = any(edge.from_node == "__start__" for edge in manifest.edges)
    for edge in manifest.edges:
        graph.add_edge(_edge_target(edge.from_node), _edge_target(edge.to))

    if manifest.nodes and not explicit_start:
        graph.add_edge(START, manifest.nodes[0].id)
    return graph


def compile_dev_graph(
    manifest: DevGraphManifest | Path | str | None = None,
    *,
    validation_mode: bool = False,
) -> StateGraph | CompiledGraphHandle:
    """Compile the Cora dev graph from a strict dev manifest."""
    resolved = _coerce_manifest(manifest)
    graph = _build_graph(resolved)
    if validation_mode:
        return graph
    return CompiledGraphHandle(
        graph=graph.compile(),
        manifest=resolved,
        thread_namespace_template=resolved.thread_namespace,
    )


__all__ = [
    "CompiledGraphHandle",
    "DEFAULT_DEV_MANIFEST_PATH",
    "DevGraphManifest",
    "compile_dev_graph",
    "format_thread_namespace",
    "load_dev_graph_manifest",
]
