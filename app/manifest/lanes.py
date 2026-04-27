"""Lane-specific manifest compilation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.manifest.compiler import compile as compile_manifest
from app.manifest.compiler import compile_run_graph as compile_production_manifest
from app.manifest.exceptions import CompileError
from app.manifest.loader import load
from app.manifest.schema import PipelineManifest

DEFAULT_RUN_MANIFEST_PATH = (
    Path(__file__).resolve().parents[2] / "state" / "config" / "pipeline-manifest.yaml"
)


def _coerce_manifest(manifest: PipelineManifest | Path | str | None) -> PipelineManifest:
    if manifest is None:
        return load(DEFAULT_RUN_MANIFEST_PATH)
    if isinstance(manifest, PipelineManifest):
        return manifest
    return load(manifest)


def compile_run_graph(
    manifest: PipelineManifest | Path | str | None = None,
    *,
    validation_mode: bool = False,
    repo_root: Path | None = None,
) -> Any:
    """Compile the run-lane graph from a manifest or path."""
    resolved = _coerce_manifest(manifest)
    if resolved.lane != "run_graph":
        raise CompileError(
            f"compile_run_graph requires lane='run_graph', got {resolved.lane!r}"
        )

    graph = compile_manifest(resolved, repo_root=repo_root)
    if validation_mode:
        return graph
    return graph.compile()


def compose_run_graph(
    manifest: PipelineManifest | Path | str | None = None,
    *,
    repo_root: Path | None = None,
) -> Any:
    """Compile the production run-lane graph with real dispatch handlers."""
    resolved = _coerce_manifest(manifest)
    return compile_production_manifest(resolved, repo_root=repo_root)
