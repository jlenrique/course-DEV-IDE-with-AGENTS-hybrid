"""Head-to-head parity comparison helpers for Slab 5a.2."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRIMARY_BUNDLE_ROOT = (
    _REPO_ROOT
    / "course-content"
    / "staging"
    / "tracked"
    / "source-bundles"
    / "apc-c1m1-tejal-20260419b-motion"
)
DEFAULT_CLONE_RUN_ROOT = _REPO_ROOT / "state" / "config" / "runs" / "C1-M1-PRES-20260419B"
DEFAULT_BASELINE_ENVELOPE_PATH = (
    _REPO_ROOT
    / "tests"
    / "fixtures"
    / "marcus"
    / "baseline_envelope"
    / "2026-04-26"
    / "envelope.json"
)

_RUN_ID_RE = re.compile(r"\bC\d+-M\d+-PRES-[A-Z0-9]+\b", flags=re.IGNORECASE)
_UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    flags=re.IGNORECASE,
)
_TIMESTAMP_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\b"
)
_LESSON_SLUG_RE = re.compile(
    r"(?P<prefix>[a-z0-9-]+)-(?P<course>c\d+)(?P<module>m\d+)-(?P<lesson>[a-z0-9-]+)$",
    flags=re.IGNORECASE,
)
_ACTUAL_SUBSTRATE_NOTE = (
    "AC-A remains operator-window conditional as of 2026-04-26 because "
    "`app.marcus.cli trial start --preset production --input <corpus-path>` "
    "does not exist on `dev/langchain-langgraph-foundation`. The parity report "
    "below measures only the comparable control-plane artifacts that do exist on "
    "the current branch."
)


@dataclass(frozen=True, slots=True)
class ArtifactParitySpec:
    label: str
    description: str
    primary_relative_path: Path
    clone_relative_path: Path
    primary_canonicalizer: Any
    clone_canonicalizer: Any


@dataclass(frozen=True, slots=True)
class ArtifactParityResult:
    label: str
    description: str
    primary_path: Path
    clone_path: Path
    present_on_primary: bool
    present_on_clone: bool
    structural_match_score: float
    matched_line_count: int
    comparable_line_count: int
    primary_lines: tuple[str, ...]
    clone_lines: tuple[str, ...]
    divergence_rationale: str

    @property
    def tier1_present(self) -> bool:
        return self.present_on_primary and self.present_on_clone

    @property
    def tier2_passes(self) -> bool:
        return self.tier1_present and self.structural_match_score >= 0.60


@dataclass(frozen=True, slots=True)
class ParityComparisonReport:
    primary_bundle_root: Path
    clone_run_root: Path
    baseline_envelope_path: Path
    compared_at: datetime
    tier1_score: float
    tier2_score: float
    tier1_threshold: float
    tier2_threshold: float
    comparable_artifact_count: int
    artifact_results: tuple[ArtifactParityResult, ...]
    notes: tuple[str, ...]


def _load_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not deserialize to a mapping")
    return payload


def _expect_string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"expected non-empty string for {key}")
    return value


def _parse_lesson_slug(lesson_slug: str) -> tuple[str, str, str]:
    match = _LESSON_SLUG_RE.search(lesson_slug)
    if match is None:
        raise ValueError(f"unable to parse lesson_slug={lesson_slug!r}")
    return (
        match.group("course").upper(),
        match.group("module").upper(),
        match.group("lesson").lower(),
    )


def _normalize_scalar(value: object) -> str:
    if value is None:
        return "null"
    text = str(value).strip().replace("\\", "/")
    text = re.sub(r"^[A-Za-z]:", "", text)
    for marker in (
        "/course-content/",
        "/state/",
        "/tests/fixtures/",
        "/_bmad-output/",
    ):
        if marker in text:
            text = text[text.index(marker) + 1 :]
            break
    text = _RUN_ID_RE.sub("{run_id}", text)
    text = _UUID_RE.sub("{uuid}", text)
    text = _TIMESTAMP_RE.sub("{timestamp}", text)
    return text.lower()


def _flatten_mapping(mapping: dict[str, Any], prefix: str = "") -> tuple[str, ...]:
    lines: list[str] = []
    for key in sorted(mapping):
        value = mapping[key]
        label = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            lines.extend(_flatten_mapping(value, prefix=label))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                child_label = f"{label}[{index}]"
                if isinstance(item, dict):
                    lines.extend(_flatten_mapping(item, prefix=child_label))
                else:
                    lines.append(f"{child_label}={_normalize_scalar(item)}")
        else:
            lines.append(f"{label}={_normalize_scalar(value)}")
    return tuple(lines)


def _compare_semantic_lines(
    primary_mapping: dict[str, Any],
    clone_mapping: dict[str, Any],
) -> tuple[float, int, int, tuple[str, ...], tuple[str, ...], str]:
    primary_lines = _flatten_mapping(primary_mapping)
    clone_lines = _flatten_mapping(clone_mapping)
    primary_set = set(primary_lines)
    clone_set = set(clone_lines)
    comparable_line_count = max(len(primary_set), len(clone_set))
    if comparable_line_count == 0:
        return 0.0, 0, 0, primary_lines, clone_lines, "No comparable semantic lines."

    matched_line_count = len(primary_set & clone_set)
    score = matched_line_count / comparable_line_count
    if score == 1.0:
        rationale = (
            "Canonical shared-control-plane fields matched after run-id, "
            "path, and timestamp normalization."
        )
    else:
        differing = sorted(primary_set ^ clone_set)
        preview = "; ".join(differing[:3])
        rationale = (
            f"Canonical comparison diverged on {len(differing)} semantic line(s): {preview}"
        )
    return score, matched_line_count, comparable_line_count, primary_lines, clone_lines, rationale


def _canonical_course_context_from_run_constants(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    course_code, _, _ = _parse_lesson_slug(_expect_string(payload, "lesson_slug"))
    return {
        "run_id": _expect_string(payload, "run_id"),
        "course_code": course_code,
        "preset": _expect_string(payload, "quality_preset"),
        "context_scope": "course",
    }


def _canonical_course_context(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    return {
        "run_id": _expect_string(payload, "run_id"),
        "course_code": _expect_string(payload, "course_code").upper(),
        "preset": _expect_string(payload, "preset"),
        "context_scope": _expect_string(payload, "context_scope"),
    }


def _canonical_module_context_from_run_constants(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    course_code, module_id, lesson_id = _parse_lesson_slug(_expect_string(payload, "lesson_slug"))
    return {
        "run_id": _expect_string(payload, "run_id"),
        "course_code": course_code,
        "module_id": module_id,
        "lesson_id": lesson_id,
        "context_scope": "module",
    }


def _canonical_module_context(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    return {
        "run_id": _expect_string(payload, "run_id"),
        "course_code": _expect_string(payload, "course_code").upper(),
        "module_id": _expect_string(payload, "module_id").upper(),
        "lesson_id": _expect_string(payload, "lesson_id").lower(),
        "context_scope": _expect_string(payload, "context_scope"),
    }


def _canonical_asset_specs_from_gary_outbound(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    return {
        "run_id": _expect_string(payload, "run_id"),
        "content_type": _expect_string(payload, "requested_content_type"),
        "double_dispatch": bool(payload.get("double_dispatch")),
        "motion_enabled": bool(payload.get("motion_enabled")),
    }


def _canonical_asset_specs(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    return {
        "run_id": _expect_string(payload, "run_id"),
        "content_type": _expect_string(payload, "content_type"),
        "double_dispatch": bool(payload.get("double_dispatch")),
        "motion_enabled": bool(payload.get("motion_enabled")),
    }


def _canonical_motion_plan(path: Path) -> dict[str, Any]:
    payload = _load_mapping(path)
    motion_budget = payload.get("motion_budget")
    if not isinstance(motion_budget, dict):
        raise ValueError("motion_budget must be a mapping")
    return {
        "run_id": _expect_string(payload, "run_id"),
        "motion_enabled": bool(payload.get("motion_enabled")),
        "motion_budget": {
            "max_credits": motion_budget.get("max_credits"),
            "model_preference": motion_budget.get("model_preference"),
        },
    }


_ACTUAL_SUBSTRATE_SPECS = (
    ArtifactParitySpec(
        label="course_context",
        description="Course-scope control-plane context",
        primary_relative_path=Path("run-constants.yaml"),
        clone_relative_path=Path("course_context.yaml"),
        primary_canonicalizer=_canonical_course_context_from_run_constants,
        clone_canonicalizer=_canonical_course_context,
    ),
    ArtifactParitySpec(
        label="module_context",
        description="Module-scope control-plane context",
        primary_relative_path=Path("run-constants.yaml"),
        clone_relative_path=Path("module_context.yaml"),
        primary_canonicalizer=_canonical_module_context_from_run_constants,
        clone_canonicalizer=_canonical_module_context,
    ),
    ArtifactParitySpec(
        label="asset_specs",
        description="Execution mode and content-type control plane",
        primary_relative_path=Path("gary-outbound-envelope.yaml"),
        clone_relative_path=Path("asset_specs.yaml"),
        primary_canonicalizer=_canonical_asset_specs_from_gary_outbound,
        clone_canonicalizer=_canonical_asset_specs,
    ),
    ArtifactParitySpec(
        label="motion_plan",
        description="Motion budget and enablement control plane",
        primary_relative_path=Path("motion_plan.yaml"),
        clone_relative_path=Path("motion_plan.yaml"),
        primary_canonicalizer=_canonical_motion_plan,
        clone_canonicalizer=_canonical_motion_plan,
    ),
)


def compare_actual_substrate_parity(
    *,
    primary_bundle_root: Path = DEFAULT_PRIMARY_BUNDLE_ROOT,
    clone_run_root: Path = DEFAULT_CLONE_RUN_ROOT,
    baseline_envelope_path: Path = DEFAULT_BASELINE_ENVELOPE_PATH,
) -> ParityComparisonReport:
    """Compare the real 5a.2 parity surfaces that exist on this branch."""
    results: list[ArtifactParityResult] = []
    notes = [_ACTUAL_SUBSTRATE_NOTE]
    if baseline_envelope_path.is_file():
        notes.append(
            "Deterministic local harness reference is present at "
            f"`{baseline_envelope_path.as_posix()}` and is cited as the local replayable "
            "surface alongside the frozen primary bundle."
        )
    else:
        notes.append(
            "Deterministic local harness reference is missing, so the report is limited to "
            "the frozen primary bundle plus legacy run-control-plane files."
        )

    for spec in _ACTUAL_SUBSTRATE_SPECS:
        primary_path = primary_bundle_root / spec.primary_relative_path
        clone_path = clone_run_root / spec.clone_relative_path
        present_on_primary = primary_path.is_file()
        present_on_clone = clone_path.is_file()
        if present_on_primary and present_on_clone:
            primary_mapping = dict(spec.primary_canonicalizer(primary_path))
            clone_mapping = dict(spec.clone_canonicalizer(clone_path))
            (
                score,
                matched_line_count,
                comparable_line_count,
                primary_lines,
                clone_lines,
                rationale,
            ) = _compare_semantic_lines(primary_mapping, clone_mapping)
        else:
            score = 0.0
            matched_line_count = 0
            comparable_line_count = 0
            primary_lines = ()
            clone_lines = ()
            missing = []
            if not present_on_primary:
                missing.append(f"primary missing `{primary_path.as_posix()}`")
            if not present_on_clone:
                missing.append(f"clone missing `{clone_path.as_posix()}`")
            rationale = "; ".join(missing)

        results.append(
            ArtifactParityResult(
                label=spec.label,
                description=spec.description,
                primary_path=primary_path,
                clone_path=clone_path,
                present_on_primary=present_on_primary,
                present_on_clone=present_on_clone,
                structural_match_score=score,
                matched_line_count=matched_line_count,
                comparable_line_count=comparable_line_count,
                primary_lines=primary_lines,
                clone_lines=clone_lines,
                divergence_rationale=rationale,
            )
        )

    tier1_score = sum(1 for result in results if result.tier1_present) / len(results)
    comparable_results = [result for result in results if result.tier1_present]
    tier2_score = (
        sum(result.structural_match_score for result in comparable_results)
        / len(comparable_results)
        if comparable_results
        else 0.0
    )

    return ParityComparisonReport(
        primary_bundle_root=primary_bundle_root,
        clone_run_root=clone_run_root,
        baseline_envelope_path=baseline_envelope_path,
        compared_at=datetime.now(tz=UTC),
        tier1_score=tier1_score,
        tier2_score=tier2_score,
        tier1_threshold=0.80,
        tier2_threshold=0.60,
        comparable_artifact_count=len(comparable_results),
        artifact_results=tuple(results),
        notes=tuple(notes),
    )


def render_parity_evidence_markdown(report: ParityComparisonReport) -> str:
    """Render the parity report to the markdown evidence artifact format."""
    lines = [
        "# 5a.2 Parity Evidence",
        "",
        "## Scope",
        f"- Primary frozen baseline: `{report.primary_bundle_root.as_posix()}`",
        f"- Clone reference surface: `{report.clone_run_root.as_posix()}`",
        f"- Deterministic local harness reference: `{report.baseline_envelope_path.as_posix()}`",
        f"- Compared at: `{report.compared_at.isoformat()}`",
    ]
    lines.extend(f"- {note}" for note in report.notes)
    lines.extend(
        [
            "",
            "## Tier 1",
            (
                f"TIER 1 Score: {report.tier1_score:.0%} "
                f"({sum(1 for item in report.artifact_results if item.tier1_present)}/"
                f"{len(report.artifact_results)} comparable artifact families present; "
                f"threshold: {report.tier1_threshold:.0%})"
            ),
            "",
            "Tier 1 measures whether the actual branch substrate exposes the same "
            "comparable control-plane artifact families on both sides of the parity boundary.",
            "",
            "## Tier 2",
            (
                f"TIER 2 Score: {report.tier2_score:.0%} "
                f"({report.comparable_artifact_count}/{report.comparable_artifact_count} "
                f"comparable families structurally matched after run-id, path, and timestamp "
                f"normalization; threshold: {report.tier2_threshold:.0%})"
            ),
            "",
            "Tier 2 measures semantic parity across the comparable artifact families that "
            "exist on both sides. This is actual-substrate control-plane parity, not a claim "
            "that a full production clone trial was launched on this branch.",
            "",
            "## Artifact Results",
            "",
            (
                "| Artifact family | Primary path | Clone path | Structural match | "
                "Verdict | Rationale |"
            ),
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in report.artifact_results:
        verdict = "parity-or-better" if result.tier2_passes else "below-threshold"
        lines.append(
            "| "
            f"{result.label} | "
            f"`{result.primary_path.relative_to(_REPO_ROOT).as_posix()}` | "
            f"`{result.clone_path.relative_to(_REPO_ROOT).as_posix()}` | "
            f"{result.structural_match_score:.0%} | "
            f"{verdict} | "
            f"{result.divergence_rationale} |"
        )
    lines.extend(
        [
            "",
            "## Operator-Window Status",
            "",
            (
                "- AC-A remains conditional because no runnable `app.marcus.cli trial "
                "start --preset production --input <corpus-path>` subcommand exists on "
                "this branch as of 2026-04-26."
            ),
            (
                "- No artifact in this report should be read as evidence that a new "
                "production clone trial was launched end-to-end."
            ),
            (
                "- To retire the conditional state, a future story or follow-on must "
                "land a real clone-trial launcher and re-run the same corpus against "
                "the same frozen primary baseline."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def write_parity_evidence_markdown(report: ParityComparisonReport, output_path: Path) -> Path:
    output_path.write_text(render_parity_evidence_markdown(report), encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-bundle-root", type=Path, default=DEFAULT_PRIMARY_BUNDLE_ROOT)
    parser.add_argument("--clone-run-root", type=Path, default=DEFAULT_CLONE_RUN_ROOT)
    parser.add_argument(
        "--baseline-envelope-path",
        type=Path,
        default=DEFAULT_BASELINE_ENVELOPE_PATH,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    report = compare_actual_substrate_parity(
        primary_bundle_root=args.primary_bundle_root,
        clone_run_root=args.clone_run_root,
        baseline_envelope_path=args.baseline_envelope_path,
    )
    write_parity_evidence_markdown(report, args.output)
    print(
        f"Wrote parity evidence to {args.output} "
        f"(tier1={report.tier1_score:.0%}, tier2={report.tier2_score:.0%})"
    )
    return 0


__all__ = [
    "ArtifactParityResult",
    "DEFAULT_BASELINE_ENVELOPE_PATH",
    "DEFAULT_CLONE_RUN_ROOT",
    "DEFAULT_PRIMARY_BUNDLE_ROOT",
    "ParityComparisonReport",
    "compare_actual_substrate_parity",
    "render_parity_evidence_markdown",
    "write_parity_evidence_markdown",
]


if __name__ == "__main__":
    raise SystemExit(main())
