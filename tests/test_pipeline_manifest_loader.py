"""Tests for pipeline manifest loader."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.utilities.pipeline_manifest import (
    ManifestInternalInconsistencyError,
    load_manifest,
)


def test_manifest_loads_and_validates() -> None:
    manifest = load_manifest()
    assert manifest.schema_version == "v4.2-migration-stub"
    assert manifest.pack_version == "v4.2"
    assert len(manifest.steps) >= 30


def test_manifest_rejects_extra_fields(tmp_path: Path) -> None:
    manifest_file = tmp_path / "pipeline-manifest.yaml"
    manifest_file.write_text(
        """
schema_version: "1.0"
pack_version: "v4.2"
generator_ref: test
learning_events: {schema_ref: null}
steps:
  - id: "01"
    label: "A"
    gate: true
    gate_code: "G0"
    sub_phase_of: null
    insertion_after: null
    hud_tracked: true
    pack_section_anchor: "1)"
    bad_field: "nope"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_manifest(manifest_file)


def test_manifest_raises_on_missing_insertion_target(tmp_path: Path) -> None:
    manifest_file = tmp_path / "pipeline-manifest.yaml"
    manifest_file.write_text(
        """
schema_version: "1.0"
pack_version: "v4.2"
generator_ref: test
learning_events: {schema_ref: null}
steps:
  - id: "01"
    label: "A"
    gate: true
    gate_code: "G0"
    sub_phase_of: null
    insertion_after: "NOPE"
    hud_tracked: true
    pack_section_anchor: "1)"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ManifestInternalInconsistencyError):
        load_manifest(manifest_file)




def test_manifest_accepts_rationale_field(tmp_path: Path) -> None:
    manifest_file = tmp_path / "pipeline-manifest.yaml"
    manifest_file.write_text(
        textwrap.dedent(
            """
            schema_version: "1.0"
            pack_version: "v4.2"
            generator_ref: test
            learning_events: {schema_ref: null}
            steps:
              - id: "01"
                label: "A"
                gate: true
                gate_code: "G0"
                sub_phase_of: null
                insertion_after: null
                hud_tracked: true
                pack_section_anchor: "1)"
                rationale: "Why this section exists"
            """
        ).strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_file)
    assert manifest.steps[0].rationale == "Why this section exists"


def test_manifest_defaults_rationale_to_none(tmp_path: Path) -> None:
    manifest_file = tmp_path / "pipeline-manifest.yaml"
    manifest_file.write_text(
        textwrap.dedent(
            """
            schema_version: "1.0"
            pack_version: "v4.2"
            generator_ref: test
            learning_events: {schema_ref: null}
            steps:
              - id: "01"
                label: "A"
                gate: true
                gate_code: "G0"
                sub_phase_of: null
                insertion_after: null
                hud_tracked: true
                pack_section_anchor: "1)"
            """
        ).strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_file)
    assert manifest.steps[0].rationale is None


def test_manifest_accepts_block_mode_trigger_paths(tmp_path: Path) -> None:
    manifest_file = tmp_path / "pipeline-manifest.yaml"
    manifest_file.write_text(
        textwrap.dedent(
            """
            schema_version: "1.0"
            pack_version: "v4.2"
            generator_ref: test
            learning_events: {schema_ref: null}
            block_mode_trigger_paths:
              - "state/config/pipeline-manifest.yaml"
              - "docs/workflow/*.md"
            steps:
              - id: "01"
                label: "A"
                gate: true
                gate_code: "G0"
                sub_phase_of: null
                insertion_after: null
                hud_tracked: true
                pack_section_anchor: "1)"
            """
        ).strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_file)
    assert "state/config/pipeline-manifest.yaml" in manifest.block_mode_trigger_paths


def test_manifest_rejects_empty_block_mode_trigger_paths(tmp_path: Path) -> None:
    manifest_file = tmp_path / "pipeline-manifest.yaml"
    manifest_file.write_text(
        textwrap.dedent(
            """
            schema_version: "1.0"
            pack_version: "v4.2"
            generator_ref: test
            learning_events: {schema_ref: null}
            block_mode_trigger_paths:
              - ""
            steps:
              - id: "01"
                label: "A"
                gate: true
                gate_code: "G0"
                sub_phase_of: null
                insertion_after: null
                hud_tracked: true
                pack_section_anchor: "1)"
            """
        ).strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_manifest(manifest_file)
