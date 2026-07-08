"""Course-source substrate models and deterministic manifest scanning."""

from app.marcus.course_source.manifest_drift import ManifestDriftResult, check_manifest_snapshot
from app.marcus.course_source.manifest_scan import (
    CourseSourceScan,
    render_gap_ledger_yaml,
    render_manifest_yaml,
    scan_course,
    write_gap_ledger,
    write_manifest_snapshot,
)
from app.marcus.course_source.models import (
    CourseRecord,
    GapLedger,
    SourceManifest,
    SourceManifestEntry,
)
from app.marcus.course_source.registry import load_course

__all__ = [
    "CourseRecord",
    "CourseSourceScan",
    "GapLedger",
    "ManifestDriftResult",
    "SourceManifest",
    "SourceManifestEntry",
    "check_manifest_snapshot",
    "load_course",
    "render_gap_ledger_yaml",
    "render_manifest_yaml",
    "scan_course",
    "write_gap_ledger",
    "write_manifest_snapshot",
]
