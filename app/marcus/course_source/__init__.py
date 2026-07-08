"""Course-source substrate models and deterministic manifest scanning."""

from app.marcus.course_source.asset_records import (
    ASSET_KIND_RECONCILIATION,
    SCHEMA_VERSION,
    AssetKind,
    AssetRecordStatus,
    AssetReview,
    AssetSourceRef,
    CanonicalAssetRecord,
    SourceRefRole,
    canonical_asset_record_json_schema,
    emit_requirement_gap_records,
    make_lesson_lo_record,
    make_syllabus_requirement_record,
)
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
    "ASSET_KIND_RECONCILIATION",
    "SCHEMA_VERSION",
    "AssetKind",
    "AssetRecordStatus",
    "AssetReview",
    "AssetSourceRef",
    "CanonicalAssetRecord",
    "SourceRefRole",
    "canonical_asset_record_json_schema",
    "emit_requirement_gap_records",
    "make_lesson_lo_record",
    "make_syllabus_requirement_record",
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
