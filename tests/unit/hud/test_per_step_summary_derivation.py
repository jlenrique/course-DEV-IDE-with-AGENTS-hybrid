from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.utilities.hud_per_step_summary import (
    NO_LOCKED_ARTIFACT,
    derive_per_step_summaries,
    known_derivation_step_ids,
    scan_bundle_summary_artifacts,
)
from scripts.utilities.pipeline_manifest import hud_steps, load_manifest


@pytest.fixture
def bundle(tmp_path: Path) -> Path:
    b = tmp_path / "bundle"
    b.mkdir()
    (b / "run-constants.yaml").write_text(
        yaml.safe_dump({"run_id": "RUN-1", "pack_version": "v4.2"}),
        encoding="utf-8",
    )
    (b / "preflight-results.json").write_text('{"status":"pass"}', encoding="utf-8")
    (b / "operator-directives.md").write_text("focus_directives:\n- test\n", encoding="utf-8")
    (b / "ingestion-evidence.md").write_text("# Evidence\n", encoding="utf-8")
    (b / "irene-packet.md").write_text("# Irene Packet\n", encoding="utf-8")
    (b / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"pack_version": "older-pack", "segments": [{"id": "seg-01"}]}),
        encoding="utf-8",
    )
    return b


def test_all_manifest_hud_steps_have_known_derivation_source() -> None:
    manifest = load_manifest()
    ids = {step["id"] for step in hud_steps(manifest)}

    assert ids.issubset(known_derivation_step_ids())
    assert len(ids) == 33


@pytest.mark.parametrize(
    ("step_id", "expected_source"),
    [
        ("01", "preflight-results.json"),
        ("02A", "operator-directives.md"),
        ("03", "ingestion-evidence.md"),
        ("04", "irene-packet.md"),
        ("08", "segment-manifest.yaml"),
    ],
)
def test_representative_step_summaries_use_existing_artifacts(
    bundle: Path,
    step_id: str,
    expected_source: str,
) -> None:
    summaries = derive_per_step_summaries(load_manifest(), scan_bundle_summary_artifacts(bundle))

    summary = summaries[step_id]
    assert summary.missing is False
    assert expected_source in summary.artifact_source
    assert summary.description.startswith("locked artifact:")


@pytest.mark.parametrize("step_id", ["05", "10", "15"])
def test_missing_artifact_degrades_honestly(bundle: Path, step_id: str) -> None:
    summaries = derive_per_step_summaries(load_manifest(), scan_bundle_summary_artifacts(bundle))

    summary = summaries[step_id]
    assert summary.missing is True
    assert summary.description == NO_LOCKED_ARTIFACT
    assert summary.artifact_source == NO_LOCKED_ARTIFACT


def test_per_step_summary_handles_pack_version_mismatch(bundle: Path) -> None:
    summaries = derive_per_step_summaries(load_manifest(), scan_bundle_summary_artifacts(bundle))

    summary = summaries["08"]
    assert summary.pack_version_mismatch is True
    assert "[pack version mismatch]" in summary.description


def test_summary_copy_style_stays_short_and_consistent(bundle: Path) -> None:
    summaries = derive_per_step_summaries(load_manifest(), scan_bundle_summary_artifacts(bundle))

    for summary in summaries.values():
        assert "frozen" not in summary.description.lower()
        assert "file" not in summary.description.lower()
        assert len(summary.description.split()) <= 30
        if summary.missing:
            assert summary.description == "no locked artifact yet"
