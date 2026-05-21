"""Loader tests (AC-1.4-B).

Exercises `app.manifest.loader.load()`: success path, YAML parse error,
root-must-be-mapping error, Pydantic validation error, file-not-found.
Every error path re-raises through `ManifestValidationError` so callers have
one named type to catch.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.manifest import ManifestValidationError, load
from app.manifest.schema import PipelineManifest

# Points at the substrate stub (single-node canonical stub used by 1.1c/1.1d
# smoke); Story 1.6 migrated `state/config/pipeline-manifest.yaml` to the full
# 33-node v4.2 manifest, which has its own test suite under `tests/end_to_end/`.
_STUB_MANIFEST = (
    Path(__file__).resolve().parents[3]
    / "state"
    / "config"
    / "pipeline-manifest-substrate-stub.yaml"
)


def test_load_stub_manifest_happy_path() -> None:
    m = load(_STUB_MANIFEST)
    assert isinstance(m, PipelineManifest)
    assert m.schema_version == "0.1-stub"
    assert m.lane == "run_graph"
    assert m.entrypoint == "noop"
    assert m.frozen_graph_version == "v0.1-stub"
    assert len(m.nodes) == 1
    assert m.nodes[0].id == "noop"


def test_load_accepts_string_path(tmp_path: Path) -> None:
    src = _STUB_MANIFEST.read_text(encoding="utf-8")
    target = tmp_path / "manifest.yaml"
    target.write_text(src, encoding="utf-8")
    m = load(str(target))
    assert m.nodes[0].id == "noop"


def test_load_missing_file_raises_manifest_validation_error(tmp_path: Path) -> None:
    ghost = tmp_path / "does_not_exist.yaml"
    with pytest.raises(ManifestValidationError, match="manifest file not found"):
        load(ghost)


def test_load_yaml_parse_error_raises_manifest_validation_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("foo: [unclosed list\n", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="YAML parse failed"):
        load(bad)


def test_load_non_mapping_root_raises_manifest_validation_error(tmp_path: Path) -> None:
    bad = tmp_path / "list.yaml"
    bad.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="root must be a mapping"):
        load(bad)


def test_load_invalid_schema_raises_manifest_validation_error(tmp_path: Path) -> None:
    bad = tmp_path / "invalid.yaml"
    bad.write_text(
        'schema_version: "0.1-stub"\n'
        'lane: "run_graph"\n'
        'entrypoint: "n1"\n'
        'frozen_graph_version: "v0.1-stub"\n'
        "nodes: []\n"
        "edges: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ManifestValidationError, match="validation failed"):
        load(bad)


def test_load_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    bad = tmp_path / "unknown_field.yaml"
    bad.write_text(
        'schema_version: "0.1-stub"\n'
        'lane: "run_graph"\n'
        'entrypoint: "n1"\n'
        'frozen_graph_version: "v0.1-stub"\n'
        'nodes: [{id: "n1"}]\n'
        "edges: []\n"
        'unexpected: "drift"\n',
        encoding="utf-8",
    )
    with pytest.raises(ManifestValidationError, match="Extra inputs are not permitted"):
        load(bad)
