"""Frozen-graph digest helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from app.manifest import compile_run_graph, load
from app.manifest.schema import PipelineManifest

DEFAULT_MANIFEST_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[2]
    / "runtime"
    / "graphs"
    / "v42"
    / "manifest-snapshot.yaml"
)
DEFAULT_DISPATCH_REGISTRY_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[2]
    / "runtime"
    / "graphs"
    / "v42"
    / "dispatch-registry-snapshot.yaml"
)


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _load_manifest_snapshot(
    manifest_snapshot: PipelineManifest | Path | str | None,
) -> PipelineManifest:
    if manifest_snapshot is None:
        return load(DEFAULT_MANIFEST_SNAPSHOT_PATH)
    if isinstance(manifest_snapshot, PipelineManifest):
        return manifest_snapshot
    return load(manifest_snapshot)


def _load_dispatch_snapshot(
    dispatch_registry_snapshot: dict[str, Any] | Path | str | None,
) -> dict[str, Any]:
    if dispatch_registry_snapshot is None:
        resolved = DEFAULT_DISPATCH_REGISTRY_SNAPSHOT_PATH
    elif isinstance(dispatch_registry_snapshot, dict):
        return dispatch_registry_snapshot
    else:
        resolved = Path(dispatch_registry_snapshot)
    parsed = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("dispatch registry snapshot must deserialize to a mapping")
    return parsed


def compute_compiled_graph_digest(
    manifest_snapshot: PipelineManifest | Path | str | None = None,
    *,
    pack_version: str | None = None,
    dispatch_registry_snapshot: dict[str, Any] | Path | str | None = None,
) -> str:
    """Return the canonical frozen-graph digest for the run-lane topology."""
    manifest = _load_manifest_snapshot(manifest_snapshot)
    resolved_pack_version = pack_version or manifest.pack_version
    if not resolved_pack_version:
        raise ValueError("pack_version must be provided directly or via the manifest snapshot")

    graph = compile_run_graph(manifest, validation_mode=True)
    payload = {
        "manifest_schema_version": manifest.schema_version,
        "frozen_graph_version": manifest.frozen_graph_version,
        "pack_version": resolved_pack_version,
        "node_ids": sorted(str(node_id) for node_id in graph.nodes),
        "edge_tuples": sorted([str(source), str(target)] for source, target in graph.edges),
        "dispatch_registry_snapshot": _load_dispatch_snapshot(dispatch_registry_snapshot),
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


__all__ = ["compute_compiled_graph_digest"]
