"""Course-source manifest drift checks."""

from __future__ import annotations

import difflib
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.marcus.course_source.manifest_scan import render_manifest_yaml, scan_course


def _reproducible_snapshot_text(text: str) -> str:
    import yaml

    from app.marcus.course_source.models import SourceManifest

    if not text:
        return ""
    manifest = SourceManifest.model_validate(yaml.safe_load(text))
    manifest.entries = [
        entry for entry in manifest.entries if entry.git_status != "ignored"
    ]
    return render_manifest_yaml(manifest)


class ManifestDriftResult(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    is_stale: bool
    diff: str = ""


def check_manifest_snapshot(course_root: Path, snapshot_path: Path) -> ManifestDriftResult:
    expected_raw = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else ""
    expected = _reproducible_snapshot_text(expected_raw)
    actual = _reproducible_snapshot_text(render_manifest_yaml(scan_course(course_root).manifest))
    if expected == actual:
        return ManifestDriftResult(is_stale=False)
    diff = "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=snapshot_path.as_posix(),
            tofile=f"{course_root.as_posix()} (regenerated)",
        )
    )
    return ManifestDriftResult(is_stale=True, diff=diff)


__all__ = ["ManifestDriftResult", "check_manifest_snapshot"]
