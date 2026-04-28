"""Per-step HUD summaries derived from existing bundle artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.pipeline_manifest import PipelineManifest, StepEntry

NO_LOCKED_ARTIFACT = "no locked artifact yet"


@dataclass(frozen=True)
class SummaryArtifact:
    relative_path: str
    modified_at_utc: str
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


_STEP_ARTIFACT_PATTERNS: dict[str, tuple[str, ...]] = {
    "01": ("preflight-results.json", "run-constants.yaml"),
    "02": ("source-authority-map.md", "source-quality-evidence.md", "metadata.json"),
    "02A": ("operator-directives.md",),
    "03": ("extraction-report.yaml", "ingestion-evidence.md", "result.yaml"),
    "04": ("ingestion-quality-gate-receipt.md", "irene-packet.md"),
    "04A": ("lesson-plan.md", "scope-lock.md", "maya-plan.json"),
    "04.5": ("parent-slide-count-estimate.json", "parent-slide-count-poll.md"),
    "04.55": ("slide-count-runtime-estimate.json", "run-constants.yaml"),
    "4.75": ("creative-directive.yaml",),
    "05": ("irene-pass1-envelope.json", "lesson-plan.md"),
    "05B": ("cluster-plan.yaml", "gates/gate-05B-result.yaml"),
    "06": ("pre-dispatch-package.json", "slide-brief.md"),
    "6.2": ("cluster-prompt-engineering.md",),
    "6.3": ("cluster-dispatch-sequencing.yaml",),
    "06B": ("literal-visual-operator-packet.md",),
    "07": ("gary-slide-output.json", "gamma-export"),
    "7.5": ("cluster-coherence-report.json", "gates/gate-7.5-result.yaml"),
    "07B": ("variant-selection.json", "gates/gate-07B-result.yaml"),
    "07C": ("authorized-storyboard.json", "storyboard/storyboard.json"),
    "07D": ("motion-designation.yaml",),
    "07E": ("motion_plan.yaml", "motion"),
    "07F": ("motion-gate-receipt.json", "gates/gate-07F-result.yaml"),
    "08": ("segment-manifest.yaml", "narration-script.md", "perception-artifacts.json"),
    "08B": ("storyboard-b/index.html", "storyboard-b/storyboard.json"),
    "09": ("pass2-envelope.json", "locked-pass2-package.json"),
    "10": ("fidelity-report.json", "quality-review.md"),
    "11": ("voice-selection.md", "elevenlabs-voice-profile.json"),
    "11B": ("elevenlabs-input-package.json",),
    "12": ("audio-manifest.json", "narration-audio"),
    "13": ("quinn-r-precomposition-review.md",),
    "14": ("assembly-bundle", "descript-assembly-guide.md"),
    "14.5": ("desmond-operator-brief.md",),
    "15": ("operator-handoff.md", "descript-ready-handoff.md"),
}


def known_derivation_step_ids() -> frozenset[str]:
    return frozenset(_STEP_ARTIFACT_PATTERNS)


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


def scan_bundle_summary_artifacts(bundle_dir: Path) -> dict[str, SummaryArtifact]:
    """Scan bundle artifacts once and memoize metadata by relative POSIX path."""
    if not bundle_dir.exists():
        return {}
    index: dict[str, SummaryArtifact] = {}
    files = (p for p in bundle_dir.rglob("*") if p.is_file())
    for path in sorted(files, key=lambda p: p.as_posix()):
        rel = path.relative_to(bundle_dir).as_posix()
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).replace(microsecond=0)
        index[rel] = SummaryArtifact(
            relative_path=rel,
            modified_at_utc=mtime.isoformat(),
            metadata=_read_metadata(path),
        )
    return index


def _match_artifact(
    patterns: tuple[str, ...],
    artifacts: dict[str, SummaryArtifact],
) -> SummaryArtifact | None:
    for pattern in patterns:
        normalized = pattern.strip("/")
        exact = artifacts.get(normalized)
        if exact is not None:
            return exact
        for rel, artifact in artifacts.items():
            if (
                rel == normalized
                or rel.startswith(normalized + "/")
                or rel.endswith("/" + normalized)
            ):
                return artifact
    return None


def _fields_from_metadata(artifact: SummaryArtifact | None) -> tuple[str, ...]:
    if artifact is None or not artifact.metadata:
        return ()
    fields = tuple(sorted(str(key) for key in artifact.metadata)[:6])
    return fields


def _summary_for_step(
    step: StepEntry,
    artifacts: dict[str, SummaryArtifact],
    *,
    expected_pack_version: str | None,
) -> StepSummary:
    patterns = _STEP_ARTIFACT_PATTERNS.get(step.id, ())
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


def derive_per_step_summaries(
    manifest: PipelineManifest,
    artifacts: dict[str, SummaryArtifact],
) -> dict[str, StepSummary]:
    """Derive one summary per HUD-tracked manifest step in O(N)."""
    expected_pack_version = manifest.pack_version or None
    summaries: dict[str, StepSummary] = {}
    for step in manifest.steps:
        if not step.hud_tracked:
            continue
        summaries[step.id] = _summary_for_step(
            step,
            artifacts,
            expected_pack_version=expected_pack_version,
        )
    return summaries
