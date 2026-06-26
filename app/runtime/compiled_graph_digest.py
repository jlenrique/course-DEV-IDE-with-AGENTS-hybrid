"""Frozen-graph digest helpers.

Two digest generations co-exist:

* The legacy single-string :func:`compute_compiled_graph_digest` (node_ids +
  edge_tuples + versions + dispatch_snapshot of the WHOLE manifest snapshot),
  used by the Slab-5a replay regression harness. Unchanged.
* The S2 **two-part content-addressed digest** (:class:`TwoPartDigest`) for
  compile-time composition. Each composed run freezes its own composition, so
  the digest captures both (a) the content-addressed compile-input CLOSURE
  (selection + per-component CONTENT hashes + composer/model/pack versions) and
  (b) the canonicalized composed-graph topology. ``digest_schema_version`` is
  embedded so legacy 4-field digests are never silently compared against the
  two-part record (Murat binding).
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from app.manifest import compile_run_graph, load
from app.manifest.schema import PipelineManifest

DIGEST_SCHEMA_VERSION = "2.0"
"""Schema version for the two-part content-addressed digest (S2).

A bump here is a Tier-2 governance act (ceremony change + party consensus). The
verify path REFUSES to compare any record whose ``digest_schema_version`` does
not match this constant, so a legacy single-string digest (no schema version)
or an older two-part record can never silently pass replay.
"""

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


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize_json_value(inner) for key, inner in value.items()}
    if isinstance(value, list | tuple):
        return [_normalize_json_value(inner) for inner in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    return value


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        _normalize_json_value(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def canonical_sha256(payload: dict[str, Any]) -> str:
    """SHA-256 of the canonical-JSON (sorted keys, stable, hashseed-independent)."""
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


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


class TwoPartDigestMismatchError(RuntimeError):
    """Raised when a recomputed two-part digest does not match a recorded one.

    The base tamper-evidence error for the S2 composition digest. Composition
    wraps this in its own ``CompositionReplayError`` so callers can catch either
    the runtime-primitive or the composition-level surface.
    """


class TwoPartDigest(BaseModel):
    """The S2 two-part content-addressed composition digest + its audit closure.

    Both digests embed :data:`DIGEST_SCHEMA_VERSION`. The record persists the
    full compile-input closure so replay can re-resolve -> recompute -> compare
    (Murat replay-from-audit floor): the recorded ``input_closure_digest`` and
    ``composed_graph_digest`` are the tamper-evidence anchors; the surrounding
    fields document what they were computed over.
    """

    model_config = ConfigDict(extra="forbid")

    digest_schema_version: str = Field(default=DIGEST_SCHEMA_VERSION)
    composer_version: str
    component_selection: dict[str, bool]
    component_content_hashes: dict[str, str]
    component_versions: dict[str, str]
    model_config_closure: list[list[str]] = Field(default_factory=list)
    frozen_graph_version: str
    pack_version: str | None = None
    input_closure_digest: str
    composed_graph_digest: str
    composed_node_ids: list[str] = Field(default_factory=list)
    composed_edge_tuples: list[list[str]] = Field(default_factory=list)
    composed_node_versions: dict[str, str | None] = Field(default_factory=dict)


def assert_two_part_digests_match(recorded: TwoPartDigest, recomputed: TwoPartDigest) -> None:
    """Raise :class:`TwoPartDigestMismatchError` unless ``recomputed`` matches ``recorded``.

    Refuses up-front if ``recorded`` does not carry the current
    :data:`DIGEST_SCHEMA_VERSION` — a legacy or stale-schema record is NEVER
    silently compared (Murat binding).
    """
    if recorded.digest_schema_version != DIGEST_SCHEMA_VERSION:
        raise TwoPartDigestMismatchError(
            f"refusing to compare a record with digest_schema_version="
            f"{recorded.digest_schema_version!r}; current is {DIGEST_SCHEMA_VERSION!r} "
            "(legacy/stale digests are never silently compared)"
        )
    if recomputed.input_closure_digest != recorded.input_closure_digest:
        raise TwoPartDigestMismatchError(
            f"input_closure_digest drift: expected {recorded.input_closure_digest}, "
            f"got {recomputed.input_closure_digest}"
        )
    if recomputed.composed_graph_digest != recorded.composed_graph_digest:
        raise TwoPartDigestMismatchError(
            f"composed_graph_digest drift: expected {recorded.composed_graph_digest}, "
            f"got {recomputed.composed_graph_digest}"
        )


__all__ = [
    "DIGEST_SCHEMA_VERSION",
    "TwoPartDigest",
    "TwoPartDigestMismatchError",
    "assert_two_part_digests_match",
    "canonical_sha256",
    "compute_compiled_graph_digest",
]
