"""Deterministic course-source manifest and gap-ledger scanner."""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from app.marcus.course_source.models import (
    GapEntry,
    GapLedger,
    SourceManifest,
    SourceManifestEntry,
    SourceScope,
)
from app.marcus.course_source.registry import load_course
from app.marcus.lesson_plan.g0_enrichment import file_content_hash

GENERATED_MANIFEST_NAMES = frozenset({"source-manifest.yaml", "source-gap-ledger.yaml"})
SCAFFOLD_FILENAMES = frozenset(
    {"README.md", "COURSE.md", "MODULE.md", "course.yaml", "module.yaml", ".gitkeep"}
)
REFERENCE_NAME_MARKERS = ("syllabus",)


class CourseSourceScan(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    manifest: SourceManifest
    gap_ledger: GapLedger


def _posix(path: Path) -> str:
    return path.as_posix()


def _repo_root(course_root: Path) -> Path | None:
    try:
        repo = subprocess.run(
            ["git", "-C", str(course_root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(repo)


def _git_paths(course_root: Path, *args: str) -> frozenset[str]:
    repo_root = _repo_root(course_root)
    if repo_root is None:
        return frozenset()
    try:
        rel_root = course_root.resolve().relative_to(repo_root.resolve()).as_posix()
        result = subprocess.run(
            ["git", "-C", str(repo_root), *args, "-z", "--", rel_root],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError, ValueError):
        return frozenset()
    prefix = f"{rel_root}/"
    paths = []
    for line in result.stdout.split("\0"):
        if not line:
            continue
        if line == rel_root:
            paths.append("")
        elif line.startswith(prefix):
            paths.append(line[len(prefix) :])
    return frozenset(paths)


def _tracked_paths(course_root: Path) -> frozenset[str]:
    return _git_paths(course_root, "ls-files")


def _ignored_paths(course_root: Path) -> frozenset[str]:
    return _git_paths(course_root, "ls-files", "--others", "-i", "--exclude-standard")


def _scope_for(relative_path: str) -> SourceScope:
    parts = relative_path.split("/")
    if relative_path in {"course.yaml", "COURSE.md"}:
        return "course"
    if parts[:2] == ["sources", "shared"]:
        return "shared"
    if parts[:2] == ["sources", "course"]:
        return "course"
    if parts[0:1] == ["modules"]:
        if "lessons" in parts:
            return "lesson"
        return "module"
    return "course"


def _source_role(path: Path, scope: SourceScope) -> str:
    lower = path.name.lower()
    if path.name in SCAFFOLD_FILENAMES or path.name in GENERATED_MANIFEST_NAMES:
        return "scaffold"
    if any(marker in lower for marker in REFERENCE_NAME_MARKERS):
        return "reference"
    if scope in {"course", "shared", "module", "lesson"}:
        return "source"
    return "scaffold"


def _module_id_for(relative_path: str) -> str | None:
    parts = relative_path.split("/")
    if len(parts) >= 2 and parts[0] == "modules":
        return parts[1]
    return None


def _lesson_id_for(relative_path: str) -> str | None:
    parts = relative_path.split("/")
    if "lessons" not in parts:
        return None
    index = parts.index("lessons")
    if len(parts) > index + 2:
        return parts[index + 1]
    return None


def _file_entries(course_root: Path, course_id: str) -> list[SourceManifestEntry]:
    tracked = _tracked_paths(course_root)
    ignored = _ignored_paths(course_root) if tracked else frozenset()
    entries: list[SourceManifestEntry] = []
    for path in sorted(p for p in course_root.rglob("*") if p.is_file()):
        relative_path = _posix(path.relative_to(course_root))
        if path.name in GENERATED_MANIFEST_NAMES:
            continue
        scope = _scope_for(relative_path)
        git_status = (
            "tracked"
            if relative_path in tracked
            else "ignored"
            if relative_path in ignored
            else "untracked"
        )
        entries.append(
            SourceManifestEntry(
                path=relative_path,
                scope=scope,
                content_sha256=file_content_hash(path),
                tracked=relative_path in tracked,
                git_status=git_status,
                source_role=_source_role(path, scope),
                course_id=course_id,
                module_id=_module_id_for(relative_path),
                lesson_id=_lesson_id_for(relative_path),
                declared=path.name in {"course.yaml", "module.yaml"},
            )
        )
    return entries


def _has_non_scaffold_file(
    path: Path,
    *,
    course_root: Path,
    ignored: frozenset[str],
) -> bool:
    return any(
        child.is_file()
        and child.name not in SCAFFOLD_FILENAMES
        and child.name not in GENERATED_MANIFEST_NAMES
        and _posix(child.relative_to(course_root)) not in ignored
        for child in path.rglob("*")
    )


def _gap_summary(gaps: list[GapEntry]) -> dict[str, int]:
    return dict(sorted(Counter(gap.kind for gap in gaps).items()))


def _gaps(
    course_root: Path,
    entries: list[SourceManifestEntry],
    *,
    ignored: frozenset[str],
) -> list[GapEntry]:
    course = load_course(course_root)
    gaps: list[GapEntry] = []
    detected_modules = sorted(
        path.name for path in (course_root / "modules").iterdir() if path.is_dir()
    ) if (course_root / "modules").is_dir() else []
    declared_modules = [module.module_id for module in course.modules]
    if course.course.module_count_expected != len(detected_modules):
        gaps.append(
            GapEntry(
                kind="module_count_mismatch",
                severity="warning",
                path="modules",
                message="Detected module directory count differs from declared expectation.",
                declared=course.course.module_count_expected,
                detected=len(detected_modules),
            )
        )
    if declared_modules and sorted(declared_modules) != detected_modules:
        gaps.append(
            GapEntry(
                kind="declared_detected_drift",
                severity="warning",
                path="modules",
                message="Declared module ids differ from detected module directories.",
                declared=declared_modules,
                detected=detected_modules,
            )
        )
    for source_dir in sorted(course_root.rglob("sources")):
        if source_dir.is_dir() and not _has_non_scaffold_file(
            source_dir,
            course_root=course_root,
            ignored=ignored,
        ):
            gaps.append(
                GapEntry(
                    kind="empty_source_dir",
                    severity="info",
                    path=_posix(source_dir.relative_to(course_root)),
                    message="Source directory has no non-scaffold local source files.",
                )
            )
    for lesson_dir in sorted(course_root.rglob("lessons")):
        if lesson_dir.is_dir() and not _has_non_scaffold_file(
            lesson_dir,
            course_root=course_root,
            ignored=ignored,
        ):
            gaps.append(
                GapEntry(
                    kind="empty_lesson_dir",
                    severity="info",
                    path=_posix(lesson_dir.relative_to(course_root)),
                    message="Lesson directory has no non-scaffold local lesson source files.",
                )
            )
    real_sources = [entry for entry in entries if entry.source_role == "source"]
    if not real_sources:
        gaps.append(
            GapEntry(
                kind="source_availability",
                severity="warning",
                path="sources",
                message=(
                    "No non-scaffold local production source content detected; "
                    "reference files and syllabi do not mark the course source-complete."
                ),
            )
        )
    for availability in course.source_availability:
        if availability.status in {"pending", "missing", "unknown"}:
            gaps.append(
                GapEntry(
                    kind="source_availability",
                    severity="warning",
                    path="course.yaml",
                    message=availability.description
                    or f"Declared source availability is {availability.status}.",
                    access_note=availability.access_note,
                    declared=availability.model_dump(mode="json"),
                )
            )
    return gaps


def scan_course(course_root: Path) -> CourseSourceScan:
    course = load_course(course_root)
    tracked = _tracked_paths(course_root)
    ignored = _ignored_paths(course_root) if tracked else frozenset()
    entries = _file_entries(course_root, course.course_id)
    reproducible_entries = [entry for entry in entries if entry.git_status != "ignored"]
    gaps = _gaps(course_root, entries, ignored=ignored)
    modules_dir = course_root / "modules"
    module_directories = sorted(
        path.name for path in modules_dir.iterdir() if path.is_dir()
    ) if modules_dir.is_dir() else []
    manifest = SourceManifest(
        course_id=course.course_id,
        declared={
            "schema_version": course.schema_version,
            "course_code": course.course.code,
            "module_count_expected": course.course.module_count_expected,
            "modules": [module.module_id for module in course.modules],
            "source_purpose": course.source_purpose,
            "source_availability": [
                availability.model_dump(mode="json")
                for availability in course.source_availability
            ],
            "source_references": [
                reference.model_dump(mode="json") for reference in course.source_references
            ],
        },
        detected={
            "module_directories": module_directories,
            "source_file_count": sum(
                entry.source_role == "source" for entry in reproducible_entries
            ),
            "reference_file_count": sum(
                entry.source_role == "reference" for entry in reproducible_entries
            ),
            "scaffold_file_count": sum(
                entry.source_role == "scaffold" for entry in reproducible_entries
            ),
        },
        gap_summary=_gap_summary(gaps),
        entries=entries,
    )
    return CourseSourceScan(
        manifest=manifest,
        gap_ledger=GapLedger(course_id=course.course_id, gaps=gaps),
    )


def _dump_yaml(payload: dict) -> str:
    return yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        line_break="\n",
    )


def render_manifest_yaml(manifest: SourceManifest) -> str:
    return _dump_yaml(manifest.model_dump(mode="json"))


def render_gap_ledger_yaml(gap_ledger: GapLedger) -> str:
    return _dump_yaml(gap_ledger.model_dump(mode="json"))


def write_manifest_snapshot(scan: CourseSourceScan, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_manifest_yaml(scan.manifest), encoding="utf-8")
    return path


def write_gap_ledger(scan: CourseSourceScan, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_gap_ledger_yaml(scan.gap_ledger), encoding="utf-8")
    return path


__all__ = [
    "CourseSourceScan",
    "render_gap_ledger_yaml",
    "render_manifest_yaml",
    "scan_course",
    "write_gap_ledger",
    "write_manifest_snapshot",
]
