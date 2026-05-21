"""Per-step HUD summaries derived from existing bundle artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.pipeline_manifest import PipelineManifest, StepEntry, hud_steps

NO_LOCKED_ARTIFACT = "no locked artifact yet"


@dataclass(frozen=True)
class SummaryArtifact:
    relative_path: str
    modified_at_utc: str
    size_bytes: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepSummary:
    step_id: str
    title: str
    artifact_source: str
    captured_fields: tuple[str, ...]
    freshness_timestamp: str | None
    description: str
    missing: bool = False
    pack_version_mismatch: bool = False


@dataclass(frozen=True)
class SummaryArtifactIndex:
    by_relative_path: dict[str, SummaryArtifact] = field(default_factory=dict)
    by_name: dict[str, SummaryArtifact] = field(default_factory=dict)
    by_top_level: dict[str, SummaryArtifact] = field(default_factory=dict)
    locked_pack_version: str | None = None


def _derivation_function_name(step_id: str) -> str:
    normalized = step_id.lower().replace(".", "_")
    return f"derive_step_{normalized}_summary"


def known_derivation_step_ids(manifest: PipelineManifest) -> frozenset[str]:
    return frozenset(step["id"] for step in hud_steps(manifest))


def _read_metadata(path: Path) -> dict[str, Any]:
    try:
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            return {}
    except (OSError, json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_locked_pack_version(bundle_dir: Path, metadata: dict[str, SummaryArtifact]) -> str | None:
    pack_file = bundle_dir / "pack-version.txt"
    try:
        if pack_file.is_file():
            value = pack_file.read_text(encoding="utf-8").strip()
            if value:
                return value
    except (FileNotFoundError, PermissionError, OSError):
        return None
    run_constants = metadata.get("run-constants.yaml")
    if run_constants is None:
        return None
    version = run_constants.metadata.get("pack_version")
    return version if isinstance(version, str) and version.strip() else None


def _candidate_scan_paths(bundle_dir: Path) -> list[Path]:
    try:
        children = sorted(bundle_dir.iterdir(), key=lambda path: path.as_posix())
    except (FileNotFoundError, PermissionError, OSError):
        return []
    paths: list[Path] = []
    for child in children:
        try:
            if child.is_symlink():
                continue
            if child.is_file():
                paths.append(child)
            elif child.is_dir():
                try:
                    paths.extend(
                        sorted(
                            (grandchild for grandchild in child.iterdir() if grandchild.is_file()),
                            key=lambda path: path.as_posix(),
                        )
                    )
                except (FileNotFoundError, PermissionError, OSError):
                    continue
        except (FileNotFoundError, PermissionError, OSError):
            continue
    return paths


def scan_bundle_summary_artifacts(bundle_dir: Path) -> SummaryArtifactIndex:
    """Scan bundle artifacts once and memoize O(1) lookup indexes."""
    if not bundle_dir.exists():
        return SummaryArtifactIndex()
    by_relative_path: dict[str, SummaryArtifact] = {}
    by_name: dict[str, SummaryArtifact] = {}
    by_top_level: dict[str, SummaryArtifact] = {}
    for path in _candidate_scan_paths(bundle_dir):
        try:
            rel = path.relative_to(bundle_dir).as_posix()
            stat = path.stat()
        except (FileNotFoundError, PermissionError, OSError, ValueError):
            continue
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC).replace(microsecond=0)
        artifact = SummaryArtifact(
            relative_path=rel,
            modified_at_utc=mtime.isoformat(),
            size_bytes=stat.st_size,
            metadata=_read_metadata(path),
        )
        by_relative_path[rel] = artifact
        by_name.setdefault(path.name, artifact)
        top_level = rel.split("/", 1)[0]
        by_top_level.setdefault(top_level, artifact)
    return SummaryArtifactIndex(
        by_relative_path=by_relative_path,
        by_name=by_name,
        by_top_level=by_top_level,
        locked_pack_version=_read_locked_pack_version(bundle_dir, by_relative_path),
    )


def _match_artifact(
    patterns: tuple[str, ...],
    artifacts: SummaryArtifactIndex,
) -> SummaryArtifact | None:
    for pattern in patterns:
        normalized = pattern.strip("/")
        artifact = (
            artifacts.by_relative_path.get(normalized)
            or artifacts.by_top_level.get(normalized)
            or artifacts.by_name.get(normalized)
        )
        if artifact is not None:
            return artifact
    return None


def _fields_from_metadata(artifact: SummaryArtifact | None) -> tuple[str, ...]:
    if artifact is None or not artifact.metadata:
        return ()
    fields = tuple(sorted(str(key) for key in artifact.metadata)[:6])
    return fields


def _summary_for_step(
    step: StepEntry,
    artifacts: SummaryArtifactIndex,
    *,
    expected_pack_version: str | None,
    patterns: tuple[str, ...],
) -> StepSummary:
    artifact = _match_artifact(patterns, artifacts)
    if artifact is None:
        return StepSummary(
            step_id=step.id,
            title=f"{step.label} summary",
            artifact_source=NO_LOCKED_ARTIFACT,
            captured_fields=(),
            freshness_timestamp=None,
            description=NO_LOCKED_ARTIFACT,
            missing=True,
        )

    artifact_pack_version = artifact.metadata.get("pack_version")
    mismatch = (
        expected_pack_version is not None
        and isinstance(artifact_pack_version, str)
        and artifact_pack_version != expected_pack_version
    )
    annotation = " [pack version mismatch]" if mismatch else ""
    captured = _fields_from_metadata(artifact)
    if not captured:
        captured = ("artifact_path",)
    return StepSummary(
        step_id=step.id,
        title=f"{step.label} summary{annotation}",
        artifact_source=f"{artifact.relative_path}{annotation}",
        captured_fields=captured,
        freshness_timestamp=artifact.modified_at_utc,
        description=f"locked artifact: {artifact.relative_path}{annotation}",
        missing=False,
        pack_version_mismatch=mismatch,
    )


def _derive_with_patterns(
    step: StepEntry,
    artifacts: SummaryArtifactIndex,
    expected_pack_version: str | None,
    patterns: tuple[str, ...],
) -> StepSummary:
    return _summary_for_step(
        step,
        artifacts,
        expected_pack_version=expected_pack_version,
        patterns=patterns,
    )


def derive_step_01_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("preflight-results.json", "run-constants.yaml")
    )


def derive_step_02_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("source-authority-map.md", "source-quality-evidence.md", "metadata.json"),
    )


def derive_step_02a_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("operator-directives.md",)
    )


def derive_step_03_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("extraction-report.yaml", "ingestion-evidence.md", "result.yaml"),
    )


def derive_step_04_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("ingestion-quality-gate-receipt.md", "irene-packet.md"),
    )


def derive_step_04a_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("lesson-plan.md", "scope-lock.md", "maya-plan.json"),
    )


def derive_step_04_5_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("parent-slide-count-estimate.json", "parent-slide-count-poll.md"),
    )


def derive_step_04_55_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("slide-count-runtime-estimate.json", "run-constants.yaml"),
    )


def derive_step_4_75_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("creative-directive.yaml",)
    )


def derive_step_05_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("irene-pass1-envelope.json", "lesson-plan.md")
    )


def derive_step_05b_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("cluster-plan.yaml", "gates/gate-05B-result.yaml")
    )


def derive_step_06_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("pre-dispatch-package.json", "slide-brief.md")
    )


def derive_step_6_2_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("cluster-prompt-engineering.md",)
    )


def derive_step_6_3_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("cluster-dispatch-sequencing.yaml",)
    )


def derive_step_06b_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("literal-visual-operator-packet.md",)
    )


def derive_step_07_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("gary-slide-output.json", "gamma-export")
    )


def derive_step_7_5_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("cluster-coherence-report.json", "gates/gate-7.5-result.yaml"),
    )


def derive_step_07b_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("variant-selection.json", "gates/gate-07B-result.yaml"),
    )


def derive_step_07c_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("authorized-storyboard.json", "storyboard/storyboard.json"),
    )


def derive_step_07d_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("motion-designation.yaml",)
    )


def derive_step_07e_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("motion_plan.yaml", "motion")
    )


def derive_step_07f_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("motion-gate-receipt.json", "gates/gate-07F-result.yaml"),
    )


def derive_step_08_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("segment-manifest.yaml", "narration-script.md", "perception-artifacts.json"),
    )


def derive_step_08b_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("storyboard-b/index.html", "storyboard-b/storyboard.json"),
    )


def derive_step_09_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("pass2-envelope.json", "locked-pass2-package.json")
    )


def derive_step_10_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("fidelity-report.json", "quality-review.md")
    )


def derive_step_11_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step,
        artifacts,
        expected_pack_version,
        ("voice-selection.md", "elevenlabs-voice-profile.json"),
    )


def derive_step_11b_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("elevenlabs-input-package.json",)
    )


def derive_step_12_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("audio-manifest.json", "narration-audio")
    )


def derive_step_13_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("quinn-r-precomposition-review.md",)
    )


def derive_step_14_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("assembly-bundle", "descript-assembly-guide.md")
    )


def derive_step_14_5_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("desmond-operator-brief.md",)
    )


def derive_step_15_summary(
    step: StepEntry, artifacts: SummaryArtifactIndex, expected_pack_version: str | None
) -> StepSummary:
    return _derive_with_patterns(
        step, artifacts, expected_pack_version, ("operator-handoff.md", "descript-ready-handoff.md")
    )


def derive_per_step_summaries(
    manifest: PipelineManifest,
    artifacts: SummaryArtifactIndex,
) -> dict[str, StepSummary]:
    """Derive one summary per HUD-tracked manifest step in O(N)."""
    expected_pack_version = artifacts.locked_pack_version
    summaries: dict[str, StepSummary] = {}
    for step in manifest.steps:
        if not step.hud_tracked:
            continue
        derive = globals().get(_derivation_function_name(step.id))
        if not callable(derive):
            summaries[step.id] = _derive_with_patterns(step, artifacts, expected_pack_version, ())
            continue
        summaries[step.id] = derive(step, artifacts, expected_pack_version)
    return summaries
