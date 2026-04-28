from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.utilities import hud_per_step_summary as summaries_module
from scripts.utilities.hud_per_step_summary import (
    NO_LOCKED_ARTIFACT,
    derive_per_step_summaries,
    known_derivation_step_ids,
    scan_bundle_summary_artifacts,
)
from scripts.utilities.pipeline_manifest import hud_steps, load_manifest

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def bundle(tmp_path: Path) -> Path:
    b = tmp_path / "bundle"
    b.mkdir()
    (b / "run-constants.yaml").write_text(
        yaml.safe_dump({"run_id": "RUN-1", "pack_version": "v4.2"}),
        encoding="utf-8",
    )
    (b / "pack-version.txt").write_text("v4.2\n", encoding="utf-8")
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

    assert ids == known_derivation_step_ids(manifest)
    assert len(ids) == 33


def test_each_manifest_step_has_pinned_derivation_function() -> None:
    manifest = load_manifest()
    for step in hud_steps(manifest):
        function_name = summaries_module._derivation_function_name(step["id"])
        assert callable(getattr(summaries_module, function_name, None)), step["id"]


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


def test_pack_version_mismatch_compares_to_bundle_locked_not_live_manifest(
    bundle: Path,
) -> None:
    (bundle / "pack-version.txt").write_text("historical-pack\n", encoding="utf-8")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"pack_version": "historical-pack", "segments": [{"id": "seg-01"}]}),
        encoding="utf-8",
    )

    summaries = derive_per_step_summaries(load_manifest(), scan_bundle_summary_artifacts(bundle))

    assert summaries["08"].pack_version_mismatch is False


def test_derivation_o_n_complexity(bundle: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scan_calls = 0
    match_calls = 0
    real_candidate_scan_paths = summaries_module._candidate_scan_paths
    real_match_artifact = summaries_module._match_artifact

    def counted_scan(path: Path):
        nonlocal scan_calls
        scan_calls += 1
        return real_candidate_scan_paths(path)

    def counted_match(patterns, artifacts):
        nonlocal match_calls
        match_calls += 1
        return real_match_artifact(patterns, artifacts)

    monkeypatch.setattr(summaries_module, "_candidate_scan_paths", counted_scan)
    monkeypatch.setattr(summaries_module, "_match_artifact", counted_match)

    artifact_index = scan_bundle_summary_artifacts(bundle)
    summaries = derive_per_step_summaries(load_manifest(), artifact_index)

    assert scan_calls == 1
    assert match_calls == len(summaries)
    assert match_calls == len(hud_steps(load_manifest()))


def test_summary_copy_style_stays_short_and_consistent(bundle: Path) -> None:
    summaries = derive_per_step_summaries(load_manifest(), scan_bundle_summary_artifacts(bundle))

    for summary in summaries.values():
        assert "frozen" not in summary.description.lower()
        assert "file" not in summary.description.lower()
        assert len(summary.description.split()) <= 30
        if summary.missing:
            assert summary.description == "no locked artifact yet"


def test_check_pipeline_manifest_lockstep_runs_via_direct_invocation() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/utilities/check_pipeline_manifest_lockstep.py",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
