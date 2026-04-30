# /// script
# requires-python = ">=3.10"
# ///
"""Build a static HTML + JSON storyboard from Gary's dispatch payload.

Emits ``storyboard/storyboard.json`` and ``storyboard/index.html`` under
``--out-dir``. Use ``summarize`` to print a manifest-derived recap for
conversational approval (Marcus + operator).

**Before Irene (Pass 2):** Gary dispatch only — each row shows the slide;
the script column is *Pending (pre–Pass 2)*.

**After Irene:** pass ``--segment-manifest`` (YAML) with ``segments[]`` entries
that include ``gary_slide_id`` (or ``slide_id``) and ``narration_text`` per
``template-segment-manifest.md`` — the same row shows slide preview + script.
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import zipfile

logger = logging.getLogger("generate_storyboard")

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
_VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".m4v"}
WORD_RE = re.compile(r"\b\w+(?:[-']\w+)?\b")
_BEHAVIORAL_INTENT_COMPATIBILITY: dict[str, set[str]] = {
    "credible": {"credible", "clear-guidance", "reflective"},
    "alarming": {"credible", "alarming", "clear-guidance"},
    "provocative": {"credible", "provocative", "reflective"},
    "reflective": {"credible", "reflective", "moving", "clear-guidance"},
    "moving": {"credible", "moving", "reflective"},
    "clear-guidance": {"credible", "alarming", "clear-guidance", "attention-reset", "reflective"},
    "attention-reset": {"credible", "clear-guidance", "attention-reset"},
}
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EXPORTS_DIR = PROJECT_ROOT / "exports"
DEFAULT_PUBLISH_SUBDIR = "assets/storyboards"
_ZIP_ENTRY_TIMESTAMP = (2026, 1, 1, 0, 0, 0)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency during isolated script use
    load_dotenv = None  # type: ignore[assignment]

if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")


def _log_run_suffix(run_id: str | None) -> str:
    """Optional APP run correlation for log messages."""
    if run_id is None or not str(run_id).strip():
        return ""
    return f" run_id={str(run_id).strip()}"

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]


def load_payload(path: Path) -> dict[str, Any]:
    """Load Gary dispatch JSON or YAML."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML payload files")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Payload top level must be an object")
    return data


def _load_structured_file(path: Path) -> Any:
    """Load JSON/YAML into a Python object without forcing a dict top level."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML files")
        return yaml.safe_load(text)
    return json.loads(text)


def _sanitize_segment(value: str) -> str:
    """Normalize a filesystem/path segment while preventing traversal."""
    normalized = str(value).replace("\\", "/").strip().strip("/")
    if not normalized:
        raise ValueError("value must be a non-empty path segment")
    parts = [part for part in normalized.split("/") if part]
    if any(part in {".", ".."} for part in parts):
        raise ValueError("path segments must not contain traversal entries")
    return "/".join(parts)


def _slugify_filename(value: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in str(value))
    text = "-".join(part for part in text.split("-") if part)
    return text or "storyboard-export"


def _local_ref_to_source_path(
    raw_ref: str,
    *,
    field_name: str,
    storyboard_dir: Path,
    asset_base: Path,
) -> Path | None:
    raw_ref = str(raw_ref or "").strip()
    if not raw_ref or _is_remote_ref(raw_ref):
        return None
    if field_name in {"html_asset_ref", "preview_href", "motion_preview_href", "motion_poster_href"}:
        candidate = (storyboard_dir / raw_ref).resolve()
    else:
        ref_path = Path(raw_ref)
        candidate = ref_path.resolve() if ref_path.is_absolute() else (asset_base / ref_path).resolve()
    return candidate if candidate.is_file() else None


def _sanitize_local_display_ref(raw_ref: str, *, asset_base: Path) -> str:
    raw_ref = str(raw_ref or "").strip()
    if not raw_ref or _is_remote_ref(raw_ref):
        return raw_ref
    ref_path = Path(raw_ref)
    try:
        resolved = ref_path.resolve() if ref_path.is_absolute() else (asset_base / ref_path).resolve()
        return resolved.relative_to(asset_base.resolve()).as_posix()
    except Exception:
        return ref_path.name or raw_ref.replace("\\", "/")


def _rewrite_manifest_for_share(
    manifest: dict[str, Any],
    *,
    storyboard_dir: Path,
) -> tuple[dict[str, Any], dict[str, Path]]:
    """Return a share-safe manifest copy plus referenced local asset inventory."""
    asset_base = Path(str(manifest.get("asset_base") or storyboard_dir.parent)).resolve()
    manifest_copy = json.loads(json.dumps(manifest))
    copied_assets: dict[str, Path] = {}

    def _rewrite_node(node: Any) -> None:
        if isinstance(node, dict):
            for field_name in (
                "file_path",
                "html_asset_ref",
                "preview_href",
                "motion_preview_href",
                "motion_poster_href",
                "link",
            ):
                if field_name not in node:
                    continue
                raw_value = node.get(field_name)
                if not isinstance(raw_value, str):
                    continue
                source_path = _local_ref_to_source_path(
                    raw_value,
                    field_name=field_name,
                    storyboard_dir=storyboard_dir,
                    asset_base=asset_base,
                )
                if source_path is not None:
                    try:
                        rel_path = source_path.relative_to(asset_base).as_posix()
                    except ValueError:
                        rel_path = source_path.name
                    copied_assets[rel_path] = source_path
                    node[field_name] = rel_path
                else:
                    node[field_name] = _sanitize_local_display_ref(raw_value, asset_base=asset_base)
            for value in node.values():
                _rewrite_node(value)
        elif isinstance(node, list):
            for item in node:
                _rewrite_node(item)

    _rewrite_node(manifest_copy)
    source_payload = manifest_copy.get("source_payload")
    if isinstance(source_payload, str):
        manifest_copy["source_payload"] = _sanitize_local_display_ref(source_payload, asset_base=asset_base)
    manifest_copy["asset_base"] = "."
    return manifest_copy, copied_assets


def _write_deterministic_zip(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    entries = sorted(path for path in source_dir.rglob("*") if path.is_file())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for path in entries:
            rel = path.relative_to(source_dir).as_posix()
            info = zipfile.ZipInfo(rel)
            info.date_time = _ZIP_ENTRY_TIMESTAMP
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())


def export_storyboard_snapshot(
    manifest_path: Path,
    *,
    export_root: Path,
    export_name: str | None = None,
) -> dict[str, Any]:
    """Build a self-contained review snapshot and deterministic zip."""
    manifest_path = manifest_path.resolve()
    storyboard_dir = manifest_path.parent.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_id = str(manifest.get("run_id") or "").strip()
    snapshot_name = export_name or f"storyboard-{run_id or storyboard_dir.parent.name}"
    snapshot_name = _slugify_filename(snapshot_name)
    snapshot_dir = (export_root / snapshot_name).resolve()
    zip_path = (export_root / f"{snapshot_name}.zip").resolve()

    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)
    if zip_path.exists():
        zip_path.unlink()

    share_manifest, copied_assets = _rewrite_manifest_for_share(
        manifest,
        storyboard_dir=storyboard_dir,
    )
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, source_path in sorted(copied_assets.items()):
        destination = (snapshot_dir / Path(rel_path)).resolve()
        if snapshot_dir not in destination.parents and destination != snapshot_dir:
            raise ValueError(f"snapshot asset path escaped snapshot root: {rel_path}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)

    (snapshot_dir / "storyboard.json").write_text(
        json.dumps(share_manifest, indent=2),
        encoding="utf-8",
    )
    (snapshot_dir / "index.html").write_text(
        render_index_html_v2(share_manifest),
        encoding="utf-8",
    )
    _write_deterministic_zip(snapshot_dir, zip_path)

    return {
        "run_id": run_id or None,
        "snapshot_name": snapshot_name,
        "snapshot_dir": snapshot_dir,
        "zip_path": zip_path,
        "asset_inventory": sorted(copied_assets.keys()),
    }


def publish_snapshot_tree(
    snapshot_dir: Path,
    *,
    repo_root: Path,
    target_subdir: str,
) -> dict[str, Any]:
    """Copy a snapshot into a checked-out Pages repo without touching other paths."""
    safe_subdir = _sanitize_segment(target_subdir)
    if safe_subdir == "":
        raise ValueError("target_subdir must not be empty")
    target_dir = (repo_root / Path(safe_subdir)).resolve()
    repo_root = repo_root.resolve()
    if repo_root not in target_dir.parents:
        raise ValueError("target_subdir escaped the repository root")

    def _fingerprint_tree(root: Path) -> dict[str, bytes]:
        if not root.exists():
            return {}
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    source_fingerprint = _fingerprint_tree(snapshot_dir)
    target_fingerprint = _fingerprint_tree(target_dir)
    changed = source_fingerprint != target_fingerprint
    if not changed:
        return {
            "changed": False,
            "published_dir": target_dir,
            "target_subdir": safe_subdir,
            "file_count": len(source_fingerprint),
        }

    if target_dir.exists():
        # Replace existing publish with updated content (same run, updated storyboard).
        shutil.rmtree(target_dir)
    shutil.copytree(snapshot_dir, target_dir)
    return {
        "changed": True,
        "published_dir": target_dir,
        "target_subdir": safe_subdir,
        "file_count": len(source_fingerprint),
    }


def _discover_site_repo_url(manifest: dict[str, Any]) -> str:
    source_payload = manifest.get("source_payload")
    if not isinstance(source_payload, str) or not source_payload.strip():
        return ""
    payload_path = Path(source_payload)
    if not payload_path.exists():
        return ""
    payload = load_payload(payload_path)
    dispatch_meta = payload.get("dispatch_metadata") if isinstance(payload.get("dispatch_metadata"), dict) else {}
    return str(dispatch_meta.get("site_repo_url") or payload.get("site_repo_url") or "").strip()


def _is_remote_ref(ref: str) -> bool:
    ref = ref.strip()
    if not ref:
        return False
    parsed = urlparse(ref)
    return parsed.scheme in {"http", "https"}


def _resolve_asset_ref(
    raw_ref: str,
    *,
    storyboard_dir: Path,
    asset_base: Path,
) -> tuple[str, str]:
    """Resolve an asset/file reference to HTML-friendly path + status.

    Returns tuple: (html_asset_ref, asset_status).
    """
    raw_ref = raw_ref.strip()
    if not raw_ref:
        return "", "missing"
    if _is_remote_ref(raw_ref):
        return raw_ref, "remote"

    # Try multiple resolution paths: relative to asset_base, project root, or absolute.
    candidates = [
        (asset_base / raw_ref).resolve(),
        (PROJECT_ROOT / raw_ref).resolve(),
        Path(raw_ref).resolve(),
    ]
    for abs_candidate in candidates:
        try:
            if abs_candidate.is_file():
                rel = Path(os.path.relpath(abs_candidate, storyboard_dir)).as_posix()
                return rel, "present"
        except OSError:
            continue
    return raw_ref, "missing"


def _coalesce_attachment_value(values: list[Any]) -> Any:
    """Collapse repeated attachment field values into a single reviewer-facing value."""
    cleaned = [value for value in values if value not in (None, "", [])]
    if not cleaned:
        return None
    unique: list[Any] = []
    for value in cleaned:
        if value not in unique:
            unique.append(value)
    if len(unique) == 1:
        return unique[0]
    return " | ".join(str(value) for value in unique)


def _normalize_optional_string(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _estimate_narration_seconds(text: str, *, target_wpm: float) -> float | None:
    if target_wpm <= 0:
        return None
    words = _word_count(text)
    if words <= 0:
        return None
    return round(words * 60.0 / target_wpm, 1)


def _behavioral_intent_serves_master(
    master_behavioral_intent: str | None,
    segment_behavioral_intent: str | None,
) -> bool:
    master = str(master_behavioral_intent or "").strip().lower()
    segment = str(segment_behavioral_intent or "").strip().lower()
    if not master or not segment:
        return True
    if master == segment:
        return True
    return segment in _BEHAVIORAL_INTENT_COMPATIBILITY.get(master, set())


def _format_estimated_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    return f"{seconds:.1f}s"


def _excerpt_text(text: str, *, limit: int = 160) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)].rstrip() + "..."


def load_narration_by_slide_id(path: Path) -> dict[str, dict[str, Any]]:
    """Load segment manifest YAML; map gary_slide_id/slide_id to review attachments.

    Multiple segments per slide_id are preserved as an explicit review state
    rather than being collapsed silently.
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required for --segment-manifest (YAML) files")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Segment manifest top level must be a mapping")
    segments = raw.get("segments")
    if segments is None:
        return {}
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")

    chunks: dict[str, list[dict[str, Any]]] = {}
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        sid_raw = seg.get("gary_slide_id") or seg.get("slide_id")
        if not isinstance(sid_raw, str) or not sid_raw.strip():
            continue
        sid = sid_raw.strip()
        chunks.setdefault(sid, []).append(
            {
                "segment_id": str(seg.get("id") or "").strip() or None,
                "narration_ref": str(seg.get("narration_ref") or "").strip() or None,
                "narration_text": str(seg.get("narration_text") or "").strip(),
                "timing_role": str(seg.get("timing_role") or "").strip() or None,
                "content_density": str(seg.get("content_density") or "").strip() or None,
                "visual_detail_load": str(seg.get("visual_detail_load") or "").strip() or None,
                "duration_rationale": str(seg.get("duration_rationale") or "").strip() or None,
                "bridge_type": str(seg.get("bridge_type") or "").strip() or None,
                "behavioral_intent": str(seg.get("behavioral_intent") or "").strip() or None,
                "motion_type": str(seg.get("motion_type") or "").strip() or None,
                "motion_asset_path": str(seg.get("motion_asset_path") or "").strip() or None,
                "motion_status": str(seg.get("motion_status") or "").strip() or None,
                "motion_source": str(seg.get("motion_source") or "").strip() or None,
                "motion_duration_seconds": seg.get("motion_duration_seconds"),
                "visual_mode": str(seg.get("visual_mode") or "").strip() or None,
                "visual_file": str(seg.get("visual_file") or "").strip() or None,
                "cluster_id": _normalize_optional_string(seg.get("cluster_id")),
                "cluster_role": _normalize_optional_string(seg.get("cluster_role")),
                "cluster_position": _normalize_optional_string(seg.get("cluster_position")),
                "parent_slide_id": _normalize_optional_string(seg.get("parent_slide_id")),
                "develop_type": _normalize_optional_string(seg.get("develop_type")),
                "interstitial_type": _normalize_optional_string(seg.get("interstitial_type")),
                "isolation_target": _normalize_optional_string(seg.get("isolation_target")),
                "narrative_arc": _normalize_optional_string(seg.get("narrative_arc")),
                "master_behavioral_intent": _normalize_optional_string(
                    seg.get("master_behavioral_intent")
                ),
                "cluster_interstitial_count": seg.get("cluster_interstitial_count"),
                "visual_references": seg.get("visual_references")
                if isinstance(seg.get("visual_references"), list)
                else [],
            }
        )

    out: dict[str, dict[str, Any]] = {}
    for sid, entries in chunks.items():
        joined_narration = "\n\n---\n\n".join(
            str(entry.get("narration_text") or "").strip()
            for entry in entries
            if str(entry.get("narration_text") or "").strip()
        )
        visual_references: list[dict[str, Any]] = []
        for entry in entries:
            refs = entry.get("visual_references")
            if isinstance(refs, list):
                visual_references.extend(ref for ref in refs if isinstance(ref, dict))

        out[sid] = {
            "match_count": len(entries),
            "narration_text": joined_narration,
            "segment_ids": [
                str(entry.get("segment_id")).strip()
                for entry in entries
                if str(entry.get("segment_id") or "").strip()
            ],
            "narration_refs": [
                str(entry.get("narration_ref")).strip()
                for entry in entries
                if str(entry.get("narration_ref") or "").strip()
            ],
            "motion_type": _coalesce_attachment_value([entry.get("motion_type") for entry in entries]),
            "motion_asset_path": _coalesce_attachment_value(
                [entry.get("motion_asset_path") for entry in entries]
            ),
            "motion_status": _coalesce_attachment_value([entry.get("motion_status") for entry in entries]),
            "motion_source": _coalesce_attachment_value([entry.get("motion_source") for entry in entries]),
            "motion_duration_seconds": _coalesce_attachment_value(
                [entry.get("motion_duration_seconds") for entry in entries]
            ),
            "visual_mode": _coalesce_attachment_value([entry.get("visual_mode") for entry in entries]),
            "visual_file": _coalesce_attachment_value([entry.get("visual_file") for entry in entries]),
            "timing_role": _coalesce_attachment_value([entry.get("timing_role") for entry in entries]),
            "content_density": _coalesce_attachment_value([entry.get("content_density") for entry in entries]),
            "visual_detail_load": _coalesce_attachment_value([entry.get("visual_detail_load") for entry in entries]),
            "duration_rationale": _coalesce_attachment_value([entry.get("duration_rationale") for entry in entries]),
            "bridge_type": _coalesce_attachment_value([entry.get("bridge_type") for entry in entries]),
            "behavioral_intent": _coalesce_attachment_value([entry.get("behavioral_intent") for entry in entries]),
            "cluster_id": _coalesce_attachment_value([entry.get("cluster_id") for entry in entries]),
            "cluster_role": _coalesce_attachment_value([entry.get("cluster_role") for entry in entries]),
            "cluster_position": _coalesce_attachment_value([entry.get("cluster_position") for entry in entries]),
            "parent_slide_id": _coalesce_attachment_value([entry.get("parent_slide_id") for entry in entries]),
            "develop_type": _coalesce_attachment_value([entry.get("develop_type") for entry in entries]),
            "interstitial_type": _coalesce_attachment_value([entry.get("interstitial_type") for entry in entries]),
            "isolation_target": _coalesce_attachment_value([entry.get("isolation_target") for entry in entries]),
            "narrative_arc": _coalesce_attachment_value([entry.get("narrative_arc") for entry in entries]),
            "master_behavioral_intent": _coalesce_attachment_value(
                [entry.get("master_behavioral_intent") for entry in entries]
            ),
            "cluster_interstitial_count": _coalesce_attachment_value(
                [entry.get("cluster_interstitial_count") for entry in entries]
            ),
            "visual_references": visual_references,
        }

    return out


def load_cluster_coherence_by_id(path: Path) -> dict[str, dict[str, Any]]:
    """Load optional cluster coherence report(s), normalized by cluster_id."""
    raw = _load_structured_file(path)
    reports: list[Any]
    if isinstance(raw, list):
        reports = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get("cluster_reports"), list):
            reports = list(raw["cluster_reports"])
        elif isinstance(raw.get("clusters"), list):
            reports = list(raw["clusters"])
        elif isinstance(raw.get("reports"), list):
            reports = list(raw["reports"])
        else:
            reports = [raw]
    else:
        raise ValueError("cluster coherence report must be a mapping or list")

    out: dict[str, dict[str, Any]] = {}
    for item in reports:
        if not isinstance(item, dict):
            continue
        report_block = item.get("report") if isinstance(item.get("report"), dict) else item
        if not isinstance(report_block, dict):
            continue
        cluster_id = _normalize_optional_string(item.get("cluster_id")) or _normalize_optional_string(
            report_block.get("cluster_id")
        )
        if cluster_id is None:
            continue

        row_results: dict[str, dict[str, Any]] = {}
        for key in ("slide_results", "slide_reports", "interstitial_results", "rows"):
            entries = report_block.get(key)
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                row_key = _normalize_optional_string(entry.get("slide_id")) or _normalize_optional_string(
                    entry.get("row_id")
                )
                if row_key is None:
                    continue
                row_results[row_key] = {
                    "decision": _normalize_optional_string(entry.get("decision"))
                    or _normalize_optional_string(entry.get("status")),
                    "score": entry.get("score"),
                    "report_hash": _normalize_optional_string(entry.get("report_hash")),
                    "violations": entry.get("violations")
                    if isinstance(entry.get("violations"), list)
                    else [],
                }

        out[cluster_id] = {
            "cluster_id": cluster_id,
            "decision": _normalize_optional_string(report_block.get("decision"))
            or _normalize_optional_string(report_block.get("status")),
            "score": report_block.get("score"),
            "report_hash": _normalize_optional_string(report_block.get("report_hash")),
            "violations": report_block.get("violations")
            if isinstance(report_block.get("violations"), list)
            else [],
            "row_results": row_results,
        }
    return out


def _classify_cluster_duration_balance(total_seconds: float | None, average_seconds: float | None) -> str | None:
    if total_seconds is None or average_seconds is None or average_seconds <= 0:
        return None
    ratio = total_seconds / average_seconds
    if ratio < 0.85:
        return "compressed"
    if ratio > 1.15:
        return "extended"
    return "balanced"


def _derive_cluster_groups(
    slides: list[dict[str, Any]],
    *,
    cluster_coherence_by_id: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Derive additive cluster groups from flat slide rows."""
    cluster_coherence_by_id = cluster_coherence_by_id or {}
    groups: list[dict[str, Any]] = []
    group_by_cluster_id: dict[str, dict[str, Any]] = {}
    for slide in slides:
        cluster_id = _normalize_optional_string(slide.get("cluster_id"))
        if cluster_id is None:
            continue
        group = group_by_cluster_id.get(cluster_id)
        if group is None:
            group = {
                "cluster_id": cluster_id,
                "row_ids": [],
                "slide_ids": [],
                "head_row_id": None,
                "head_slide_id": None,
                "topic_label": None,
                "narrative_arc": None,
                "master_behavioral_intent": None,
                "interstitial_count": 0,
                "interstitial_types": [],
                "estimated_runtime_seconds": None,
                "duration_balance": None,
                "coherence": cluster_coherence_by_id.get(cluster_id) or {},
            }
            groups.append(group)
            group_by_cluster_id[cluster_id] = group
        group["row_ids"].append(slide.get("row_id"))
        group["slide_ids"].append(slide.get("slide_id"))

        role = _normalize_optional_string(slide.get("cluster_role"))
        if role == "interstitial":
            group["interstitial_count"] += 1
            interstitial_type = _normalize_optional_string(slide.get("interstitial_type"))
            if interstitial_type and interstitial_type not in group["interstitial_types"]:
                group["interstitial_types"].append(interstitial_type)
        if group["head_row_id"] is None and role == "head":
            group["head_row_id"] = slide.get("row_id")
            group["head_slide_id"] = slide.get("slide_id")
            group["topic_label"] = _normalize_optional_string(slide.get("display_title")) or _normalize_optional_string(
                slide.get("slide_id")
            )
            group["narrative_arc"] = _normalize_optional_string(slide.get("narrative_arc"))
            group["master_behavioral_intent"] = _normalize_optional_string(
                slide.get("master_behavioral_intent")
            )
        elif group["head_row_id"] is None:
            group["head_row_id"] = slide.get("row_id")
            group["head_slide_id"] = slide.get("slide_id")
            group["topic_label"] = _normalize_optional_string(slide.get("display_title")) or _normalize_optional_string(
                slide.get("slide_id")
            )
        if group["narrative_arc"] is None:
            group["narrative_arc"] = _normalize_optional_string(slide.get("narrative_arc"))
        if group["master_behavioral_intent"] is None:
            group["master_behavioral_intent"] = _normalize_optional_string(
                slide.get("master_behavioral_intent")
            )

        runtime_target = slide.get("runtime_target_seconds")
        if isinstance(runtime_target, (int, float)):
            current_total = group.get("estimated_runtime_seconds")
            group["estimated_runtime_seconds"] = float(current_total or 0) + float(runtime_target)

    numeric_totals = [
        float(group["estimated_runtime_seconds"])
        for group in groups
        if isinstance(group.get("estimated_runtime_seconds"), (int, float))
    ]
    average_total = (sum(numeric_totals) / len(numeric_totals)) if numeric_totals else None
    for group in groups:
        group["duration_balance"] = _classify_cluster_duration_balance(
            float(group["estimated_runtime_seconds"])
            if isinstance(group.get("estimated_runtime_seconds"), (int, float))
            else None,
            average_total,
        )
    return groups


def _inspect_local_image_metadata(path: Path) -> dict[str, Any]:
    """Inspect local image metadata for storyboard review."""
    meta: dict[str, Any] = {
        "orientation": "unknown",
        "dimensions": None,
        "aspect_ratio": None,
    }
    from PIL import Image

    try:
        with Image.open(path) as img:
            width, height = img.size
    except Exception:  # pragma: no cover - defensive
        return meta

    if width > 0 and height > 0:
        meta["dimensions"] = {"width": width, "height": height}
        meta["aspect_ratio"] = f"{width}:{height}"
        if width > height:
            meta["orientation"] = "landscape"
        elif height > width:
            meta["orientation"] = "portrait"
        else:
            meta["orientation"] = "square"
    return meta


def _build_slide_row_id(slide_id: str, dispatch_variant: str | None, sequence: int) -> str:
    safe_slide_id = "".join(ch if ch.isalnum() else "-" for ch in slide_id).strip("-").lower()
    if not safe_slide_id:
        safe_slide_id = f"slide-{sequence}"
    if dispatch_variant:
        return f"slide-{safe_slide_id}-{dispatch_variant.lower()}"
    return f"slide-{safe_slide_id}"


def _resolve_preview_metadata(
    *,
    file_path_raw: str,
    html_asset_ref: str,
    asset_status: str,
    asset_base: Path,
) -> dict[str, Any]:
    preview_kind = "missing"
    preview_href = html_asset_ref
    orientation = "unknown"
    dimensions = None
    aspect_ratio = None

    suffix = Path(file_path_raw).suffix.lower()
    if asset_status == "missing":
        preview_kind = "missing"
    elif asset_status == "remote":
        preview_kind = "image" if suffix in _IMAGE_SUFFIXES else "link"
    elif suffix in _IMAGE_SUFFIXES:
        preview_kind = "image"
        local_path = (asset_base / file_path_raw).resolve()
        meta = _inspect_local_image_metadata(local_path)
        orientation = str(meta.get("orientation") or "unknown")
        dimensions = meta.get("dimensions")
        aspect_ratio = meta.get("aspect_ratio")
    else:
        preview_kind = "other"

    return {
        "preview_kind": preview_kind,
        "preview_href": preview_href,
        "orientation": orientation,
        "dimensions": dimensions,
        "aspect_ratio": aspect_ratio,
    }


def _resolve_motion_preview_metadata(
    *,
    motion_ref_raw: str,
    poster_ref: str,
    storyboard_dir: Path,
    asset_base: Path,
) -> dict[str, Any]:
    """Resolve motion preview metadata for Storyboard B review."""
    motion_preview_href = ""
    motion_preview_status = "missing"
    motion_preview_kind = "missing"
    motion_poster_href = poster_ref

    raw = str(motion_ref_raw or "").strip()
    if not raw:
        return {
            "motion_preview_href": motion_preview_href,
            "motion_preview_status": motion_preview_status,
            "motion_preview_kind": motion_preview_kind,
            "motion_poster_href": motion_poster_href,
        }

    motion_preview_href, motion_preview_status = _resolve_asset_ref(
        raw,
        storyboard_dir=storyboard_dir,
        asset_base=asset_base,
    )
    suffix = Path(raw).suffix.lower()
    if motion_preview_status == "missing":
        motion_preview_kind = "missing"
    elif suffix in _VIDEO_SUFFIXES:
        motion_preview_kind = "video"
    elif suffix in _IMAGE_SUFFIXES:
        motion_preview_kind = "image"
    else:
        motion_preview_kind = "link" if motion_preview_status == "remote" else "other"

    return {
        "motion_preview_href": motion_preview_href,
        "motion_preview_status": motion_preview_status,
        "motion_preview_kind": motion_preview_kind,
        "motion_poster_href": motion_poster_href,
    }


def load_related_assets(
    path: Path,
    *,
    storyboard_dir: Path,
    asset_base: Path,
) -> list[dict[str, Any]]:
    """Load optional non-slide related assets from JSON or YAML.

    Supported top-level shapes:
    - list[object]
    - {"related_assets": list[object]} (also accepts assets/items)
    """
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML related assets")
        data: Any = yaml.safe_load(text)
    else:
        data = json.loads(text)

    entries: Any = data
    if isinstance(data, dict):
        entries = data.get("related_assets")
        if entries is None:
            entries = data.get("assets")
        if entries is None:
            entries = data.get("items")
    if not isinstance(entries, list):
        raise ValueError("related assets must be a list or an object containing related_assets")

    out: list[dict[str, Any]] = []
    for idx, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"related_assets[{idx}] must be an object")

        label = str(item.get("label", "")).strip()
        if not label:
            raise ValueError(f"related_assets[{idx}].label is required")

        link_raw = str(
            item.get("link")
            or item.get("href")
            or item.get("file_path")
            or ""
        ).strip()
        if not link_raw:
            raise ValueError(f"related_assets[{idx}].link is required")

        html_asset_ref, asset_status = _resolve_asset_ref(
            link_raw,
            storyboard_dir=storyboard_dir,
            asset_base=asset_base,
        )
        out.append(
            {
                "row_kind": "related_asset",
                "sequence": idx,
                "asset_type": str(item.get("asset_type") or item.get("type") or "other").strip(),
                "label": label,
                "link": link_raw,
                "source_ref": str(item.get("source_ref") or "").strip(),
                "stage": str(item.get("stage") or "").strip(),
                "asset_status": asset_status,
                "html_asset_ref": html_asset_ref,
            }
        )
    return out


def load_storyboard_policy_meta(
    *,
    payload_path: Path,
    explicit_envelope_path: Path | None = None,
) -> dict[str, Any]:
    """Load optional runtime/script-policy metadata for Storyboard B headers."""
    envelope_path = explicit_envelope_path or (payload_path.parent / "pass2-envelope.json")
    runtime_plan: dict[str, Any] = {}
    script_policy: dict[str, Any] = {}
    voice_direction_defaults: dict[str, Any] = {}
    per_slide_runtime_targets: dict[str, Any] = {}

    if envelope_path.is_file():
        envelope = load_payload(envelope_path)
        runtime_plan_raw = envelope.get("runtime_plan")
        if isinstance(runtime_plan_raw, dict):
            runtime_plan = runtime_plan_raw
        script_policy_raw = envelope.get("script_policy")
        if isinstance(script_policy_raw, dict):
            script_policy = script_policy_raw
        voice_defaults_raw = envelope.get("voice_direction_defaults")
        if isinstance(voice_defaults_raw, dict):
            voice_direction_defaults = voice_defaults_raw
        per_slide_runtime_raw = envelope.get("per_slide_runtime_targets")
        if isinstance(per_slide_runtime_raw, dict):
            per_slide_runtime_targets = per_slide_runtime_raw

    # Backfill script-policy defaults when envelope does not carry them.
    if not script_policy and yaml is not None:
        params_path = PROJECT_ROOT / "state" / "config" / "narration-script-parameters.yaml"
        if params_path.is_file():
            params_data = yaml.safe_load(params_path.read_text(encoding="utf-8"))
            if isinstance(params_data, dict):
                script_policy = {
                    "narration_density": params_data.get("narration_density", {}),
                    "engagement_stance": params_data.get("engagement_stance", {}),
                }

    return {
        "envelope_source": envelope_path.resolve().as_posix() if envelope_path.is_file() else None,
        "runtime_plan": runtime_plan,
        "script_policy": script_policy,
        "voice_direction_defaults": voice_direction_defaults,
        "per_slide_runtime_targets": per_slide_runtime_targets,
    }


def build_manifest(
    payload: dict[str, Any],
    *,
    payload_path: Path,
    storyboard_dir: Path,
    asset_base: Path,
    narration_by_slide_id: dict[str, dict[str, Any]] | None = None,
    segment_manifest_path: Path | None = None,
    related_assets: list[dict[str, Any]] | None = None,
    run_id: str | None = None,
    storyboard_policy_meta: dict[str, Any] | None = None,
    cluster_coherence_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return manifest dict and do not write files."""
    slides_in = payload.get("gary_slide_output")
    if not isinstance(slides_in, list):
        raise ValueError("gary_slide_output must be a list")
    storyboard_dir = storyboard_dir.resolve()
    slides_out: list[dict[str, Any]] = []
    pair_map: dict[str, dict[str, Any]] = {}
    storyboard_policy_meta = storyboard_policy_meta or {}
    per_slide_runtime_targets = (
        storyboard_policy_meta.get("per_slide_runtime_targets")
        if isinstance(storyboard_policy_meta.get("per_slide_runtime_targets"), dict)
        else {}
    )
    runtime_plan = (
        storyboard_policy_meta.get("runtime_plan")
        if isinstance(storyboard_policy_meta.get("runtime_plan"), dict)
        else {}
    )
    per_slide_runtime_targets_by_card: dict[str, Any] = {}
    for entry in runtime_plan.get("per_slide_targets", []):
        if not isinstance(entry, dict):
            continue
        card_number = entry.get("card_number")
        target_runtime_seconds = entry.get("target_runtime_seconds")
        if card_number in (None, "") or target_runtime_seconds in (None, ""):
            continue
        per_slide_runtime_targets_by_card[str(card_number)] = target_runtime_seconds

    for idx, raw in enumerate(slides_in, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"gary_slide_output[{idx}] must be an object")
        slide_id = str(raw.get("slide_id", "")).strip()
        if not slide_id:
            raise ValueError(f"gary_slide_output[{idx}].slide_id is required")
        fidelity = str(raw.get("fidelity", "creative") or "creative").strip()
        card_number = raw.get("card_number")
        source_ref = str(raw.get("source_ref", "") or "").strip()
        file_path_raw = str(raw.get("file_path", "") or "").strip()
        display_title = str(raw.get("title") or raw.get("display_title") or slide_id).strip()
        dispatch_variant = str(raw.get("dispatch_variant") or "").strip().upper() or None
        selected = bool(raw.get("selected", False))
        vera_score = raw.get("vera_score")
        quinn_score = raw.get("quinn_score")
        findings = raw.get("findings") if isinstance(raw.get("findings"), list) else []
        visual_description = str(raw.get("visual_description") or "").strip()
        literal_visual_source = str(raw.get("literal_visual_source") or "").strip() or None

        html_asset_ref = ""
        asset_status = "missing"

        html_asset_ref, asset_status = _resolve_asset_ref(
            file_path_raw,
            storyboard_dir=storyboard_dir,
            asset_base=asset_base,
        )

        narration_text = ""
        narration_status = "pending"
        segment_match_count = 0
        matched_segment_ids: list[str] = []
        matched_narration_refs: list[str] = []
        matched_visual_references: list[dict[str, Any]] = []
        motion_type = None
        motion_asset_path = None
        motion_status = None
        motion_source = None
        motion_duration_seconds = None
        visual_mode = None
        visual_file = None
        timing_role = None
        content_density = None
        visual_detail_load = None
        duration_rationale = None
        bridge_type = None
        behavioral_intent = None
        cluster_id = _normalize_optional_string(raw.get("cluster_id"))
        cluster_role = _normalize_optional_string(raw.get("cluster_role"))
        cluster_position = _normalize_optional_string(raw.get("cluster_position"))
        parent_slide_id = _normalize_optional_string(raw.get("parent_slide_id"))
        develop_type = _normalize_optional_string(raw.get("develop_type"))
        interstitial_type = _normalize_optional_string(raw.get("interstitial_type"))
        isolation_target = _normalize_optional_string(raw.get("isolation_target"))
        narrative_arc = _normalize_optional_string(raw.get("narrative_arc"))
        master_behavioral_intent = _normalize_optional_string(raw.get("master_behavioral_intent"))
        cluster_interstitial_count = raw.get("cluster_interstitial_count")
        selected_template_id = _normalize_optional_string(raw.get("selected_template_id"))
        if narration_by_slide_id:
            matched = narration_by_slide_id.get(slide_id)
            if isinstance(matched, dict):
                narration_text = str(matched.get("narration_text") or "").strip()
                segment_match_count = int(matched.get("match_count") or 0)
                matched_segment_ids = [
                    str(item).strip()
                    for item in matched.get("segment_ids", [])
                    if str(item).strip()
                ]
                matched_narration_refs = [
                    str(item).strip()
                    for item in matched.get("narration_refs", [])
                    if str(item).strip()
                ]
                matched_visual_references = [
                    item
                    for item in matched.get("visual_references", [])
                    if isinstance(item, dict)
                ]
                motion_type = matched.get("motion_type")
                motion_asset_path = matched.get("motion_asset_path")
                motion_status = matched.get("motion_status")
                motion_source = matched.get("motion_source")
                motion_duration_seconds = matched.get("motion_duration_seconds")
                visual_mode = matched.get("visual_mode")
                visual_file = matched.get("visual_file")
                timing_role = matched.get("timing_role")
                content_density = matched.get("content_density")
                visual_detail_load = matched.get("visual_detail_load")
                duration_rationale = matched.get("duration_rationale")
                bridge_type = matched.get("bridge_type")
                behavioral_intent = matched.get("behavioral_intent")
                cluster_id = _normalize_optional_string(matched.get("cluster_id")) or cluster_id
                cluster_role = _normalize_optional_string(matched.get("cluster_role")) or cluster_role
                cluster_position = _normalize_optional_string(matched.get("cluster_position")) or cluster_position
                parent_slide_id = _normalize_optional_string(matched.get("parent_slide_id")) or parent_slide_id
                develop_type = _normalize_optional_string(matched.get("develop_type")) or develop_type
                interstitial_type = _normalize_optional_string(matched.get("interstitial_type")) or interstitial_type
                isolation_target = _normalize_optional_string(matched.get("isolation_target")) or isolation_target
                narrative_arc = _normalize_optional_string(matched.get("narrative_arc")) or narrative_arc
                master_behavioral_intent = (
                    _normalize_optional_string(matched.get("master_behavioral_intent"))
                    or master_behavioral_intent
                )
                cluster_interstitial_count = (
                    matched.get("cluster_interstitial_count")
                    if matched.get("cluster_interstitial_count") not in (None, "")
                    else cluster_interstitial_count
                )
                selected_template_id = (
                    _normalize_optional_string(matched.get("selected_template_id"))
                    or selected_template_id
                )
                if segment_match_count > 1:
                    narration_status = "multi_match"
                elif narration_text:
                    narration_status = "present"
                else:
                    narration_status = "no_match" if segment_manifest_path is not None else "pending"
            else:
                narration_status = "no_match" if segment_manifest_path is not None else "pending"

        preview_meta = _resolve_preview_metadata(
            file_path_raw=file_path_raw,
            html_asset_ref=html_asset_ref,
            asset_status=asset_status,
            asset_base=asset_base.resolve(),
        )
        motion_preview_meta = _resolve_motion_preview_metadata(
            motion_ref_raw=str(motion_asset_path or visual_file or ""),
            poster_ref=str(preview_meta["preview_href"] or ""),
            storyboard_dir=storyboard_dir,
            asset_base=asset_base.resolve(),
        )
        script_notes_parts: list[str] = []
        if visual_description:
            script_notes_parts.append(visual_description)
        if findings:
            script_notes_parts.append("Findings:\n- " + "\n- ".join(str(f) for f in findings))
        script_notes = "\n\n".join(part for part in script_notes_parts if part.strip())

        issue_flags: list[str] = []
        if asset_status == "missing":
            issue_flags.append("missing_asset")
        if narration_status == "multi_match":
            issue_flags.append("multi_match")
        if narration_status == "no_match":
            issue_flags.append("no_match")
        if findings:
            issue_flags.append("has_findings")

        row_id = _build_slide_row_id(slide_id, dispatch_variant, idx)
        runtime_target_seconds = per_slide_runtime_targets.get(slide_id)
        if runtime_target_seconds in (None, ""):
            runtime_target_seconds = per_slide_runtime_targets_by_card.get(str(card_number))

        slides_out.append(
            {
                "sequence": idx,
                "row_id": row_id,
                "row_kind": "slide",
                "slide_id": slide_id,
                "fidelity": fidelity,
                "dispatch_variant": dispatch_variant,
                "selected": selected,
                "card_number": card_number,
                "source_ref": source_ref,
                "file_path": file_path_raw,
                "display_title": display_title,
                "asset_status": asset_status,
                "html_asset_ref": html_asset_ref,
                "preview_kind": preview_meta["preview_kind"],
                "preview_href": preview_meta["preview_href"],
                "motion_preview_kind": motion_preview_meta["motion_preview_kind"],
                "motion_preview_href": motion_preview_meta["motion_preview_href"],
                "motion_preview_status": motion_preview_meta["motion_preview_status"],
                "motion_poster_href": motion_preview_meta["motion_poster_href"],
                "orientation": preview_meta["orientation"],
                "dimensions": preview_meta["dimensions"],
                "aspect_ratio": preview_meta["aspect_ratio"],
                "vera_score": vera_score,
                "quinn_score": quinn_score,
                "findings": findings,
                "visual_description": visual_description,
                "literal_visual_source": literal_visual_source,
                "narration_text": narration_text,
                "narration_status": narration_status,
                "segment_match_count": segment_match_count,
                "matched_segment_ids": matched_segment_ids,
                "matched_narration_refs": matched_narration_refs,
                "matched_visual_references": matched_visual_references,
                "matched_visual_reference_count": len(matched_visual_references),
                "motion_type": motion_type,
                "motion_asset_path": motion_asset_path,
                "motion_status": motion_status,
                "motion_source": motion_source,
                "motion_duration_seconds": motion_duration_seconds,
                "visual_mode": visual_mode,
                "visual_file": visual_file,
                "timing_role": timing_role,
                "content_density": content_density,
                "visual_detail_load": visual_detail_load,
                "duration_rationale": duration_rationale,
                "bridge_type": bridge_type,
                "behavioral_intent": behavioral_intent,
                "cluster_id": cluster_id,
                "cluster_role": cluster_role,
                "cluster_position": cluster_position,
                "parent_slide_id": parent_slide_id,
                "develop_type": develop_type,
                "interstitial_type": interstitial_type,
                "isolation_target": isolation_target,
                "narrative_arc": narrative_arc,
                "master_behavioral_intent": master_behavioral_intent,
                "cluster_interstitial_count": cluster_interstitial_count,
                "selected_template_id": selected_template_id,
                "runtime_target_seconds": runtime_target_seconds,
                "script_notes": script_notes,
                "issue_flags": issue_flags,
            }
        )

        if dispatch_variant:
            pair_key = str(card_number if card_number is not None else slide_id)
            pair = pair_map.setdefault(
                pair_key,
                {
                    "pair_key": pair_key,
                    "slide_id": slide_id,
                    "card_number": card_number,
                    "selected_variant": None,
                    "variants": {"A": None, "B": None},
                },
            )
            if dispatch_variant in {"A", "B"}:
                pair["variants"][dispatch_variant] = slides_out[-1]
            if selected:
                pair["selected_variant"] = dispatch_variant

    with_script_n = sum(
        1
        for s in slides_out
        if isinstance(s, dict) and s.get("narration_status") in {"present", "multi_match"}
    )
    view = "slides_with_script" if with_script_n else "slides_only"
    checkpoint_label = "Storyboard B" if view == "slides_with_script" else "Storyboard A"
    related_assets = related_assets or []
    rows: list[dict[str, Any]] = [*slides_out]
    normalized_related_assets: list[dict[str, Any]] = []
    if related_assets:
        for idx, item in enumerate(related_assets, start=1):
            row = dict(item)
            row["sequence"] = len(slides_out) + idx
            row["row_id"] = f"related-{idx}"
            row.setdefault("row_kind", "related_asset")
            normalized_related_assets.append(row)
            rows.append(row)

    missing_assets = sum(1 for s in slides_out if s.get("asset_status") == "missing")
    remote_assets = sum(1 for s in slides_out if s.get("asset_status") == "remote")
    pending_narration = sum(
        1 for s in slides_out if s.get("narration_status") in {"pending", "no_match", "multi_match"}
    )
    multi_match_narration = sum(
        1 for s in slides_out if s.get("narration_status") == "multi_match"
    )
    with_findings = sum(1 for s in slides_out if s.get("findings"))
    clustered_slide_count = sum(
        1 for s in slides_out if _normalize_optional_string(s.get("cluster_id")) is not None
    )
    fidelity_counts = dict(Counter(str(s.get("fidelity", "unknown")) for s in slides_out))
    first_slide_id = slides_out[0]["slide_id"] if slides_out else None
    last_slide_id = slides_out[-1]["slide_id"] if slides_out else None
    cluster_groups = _derive_cluster_groups(
        slides_out,
        cluster_coherence_by_id=cluster_coherence_by_id,
    )
    if cluster_coherence_by_id:
        for slide in slides_out:
            cluster_id = _normalize_optional_string(slide.get("cluster_id"))
            if cluster_id is None:
                continue
            coherence = cluster_coherence_by_id.get(cluster_id) or {}
            row_results = coherence.get("row_results") if isinstance(coherence.get("row_results"), dict) else {}
            row_key = str(slide.get("slide_id") or slide.get("row_id") or "")
            slide_coherence = row_results.get(row_key)
            if not isinstance(slide_coherence, dict):
                slide_coherence = row_results.get(str(slide.get("row_id") or ""))
            if isinstance(slide_coherence, dict):
                slide["cluster_coherence_decision"] = slide_coherence.get("decision")
                slide["cluster_coherence_score"] = slide_coherence.get("score")
                slide["cluster_coherence_report_hash"] = slide_coherence.get("report_hash")
                slide["cluster_coherence_violations"] = slide_coherence.get("violations")
                slide["cluster_coherence_source"] = "row"
            elif coherence:
                slide["cluster_coherence_decision"] = coherence.get("decision")
                slide["cluster_coherence_score"] = coherence.get("score")
                slide["cluster_coherence_report_hash"] = coherence.get("report_hash")
                slide["cluster_coherence_violations"] = coherence.get("violations")
                slide["cluster_coherence_source"] = "cluster"

    out: dict[str, Any] = {
        "storyboard_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_payload": payload_path.resolve().as_posix(),
        "asset_base": asset_base.resolve().as_posix(),
        "storyboard_view": view,
        "checkpoint_label": checkpoint_label,
        "slides": slides_out,
        "related_assets": normalized_related_assets,
        "run_id": run_id,
        "storyboard_policy": {
            "envelope_source": storyboard_policy_meta.get("envelope_source"),
            "runtime_plan": (
                storyboard_policy_meta.get("runtime_plan")
                if isinstance(storyboard_policy_meta.get("runtime_plan"), dict)
                else {}
            ),
            "script_policy": (
                storyboard_policy_meta.get("script_policy")
                if isinstance(storyboard_policy_meta.get("script_policy"), dict)
                else {}
            ),
            "voice_direction_defaults": (
                storyboard_policy_meta.get("voice_direction_defaults")
                if isinstance(storyboard_policy_meta.get("voice_direction_defaults"), dict)
                else {}
            ),
        },
        "rows": rows,
        "review_meta": {
            "total_slides": len(slides_out),
            "missing_assets": missing_assets,
            "remote_assets": remote_assets,
            "slides_with_narration": with_script_n,
            "pending_narration": pending_narration,
            "multi_match_narration": multi_match_narration,
            "related_asset_count": len(normalized_related_assets),
            "double_dispatch_enabled": bool(pair_map),
            "slides_with_findings": with_findings,
            "fidelity_counts": fidelity_counts,
            "first_slide_id": first_slide_id,
            "last_slide_id": last_slide_id,
            "cluster_group_count": len(cluster_groups),
            "clustered_slide_count": clustered_slide_count,
            "flat_slide_count": len(slides_out) - clustered_slide_count,
        },
    }
    if cluster_groups:
        out["cluster_groups"] = cluster_groups

    if pair_map:
        variant_pairs = [pair_map[k] for k in sorted(pair_map.keys(), key=lambda x: int(x) if x.isdigit() else x)]
        selected_pairs = sum(1 for pair in variant_pairs if pair.get("selected_variant"))
        out["double_dispatch"] = {
            "enabled": True,
            "selection_progress": {
                "selected": selected_pairs,
                "total": len(variant_pairs),
            },
            "variant_pairs": variant_pairs,
        }

        selected_preview: list[dict[str, Any]] = []
        for pair in variant_pairs:
            chosen = pair["selected_variant"]
            if chosen in {"A", "B"}:
                winner = pair["variants"].get(chosen)
                if isinstance(winner, dict):
                    selected_preview.append(winner)
        out["selected_full_deck_preview"] = selected_preview
    if segment_manifest_path is not None:
        out["segment_manifest_source"] = segment_manifest_path.resolve().as_posix()
    return out


def format_summary(manifest: dict[str, Any]) -> str:
    """Human-facing lines derived only from manifest (for Marcus to read aloud)."""
    slides = manifest.get("slides")
    if not isinstance(slides, list) or not slides:
        return "Storyboard summary: zero slides in manifest."

    ids = [str(s.get("slide_id", "")) for s in slides if isinstance(s, dict)]
    if not ids:
        return "Storyboard summary: zero valid slide_id entries in manifest slides."
    fids = [
        str(s.get("fidelity", "unknown"))
        for s in slides
        if isinstance(s, dict)
    ]
    review_meta = manifest.get("review_meta") if isinstance(manifest.get("review_meta"), dict) else {}
    storyboard_policy = (
        manifest.get("storyboard_policy") if isinstance(manifest.get("storyboard_policy"), dict) else {}
    )
    counts = Counter(fids)
    checkpoint_label = str(manifest.get("checkpoint_label") or "Storyboard")
    lines = [
        f"{checkpoint_label} summary: {len(slides)} slide(s).",
        f"First slide_id: {ids[0]!r}; last slide_id: {ids[-1]!r}.",
        "Fidelity counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
    ]
    missing_n = sum(
        1
        for s in slides
        if isinstance(s, dict) and s.get("asset_status") == "missing"
    )
    if missing_n:
        lines.append(f"Warning: {missing_n} slide(s) have missing local assets.")

    view = str(manifest.get("storyboard_view") or "")
    narrated = sum(
        1
        for s in slides
        if isinstance(s, dict) and s.get("narration_status") in {"present", "multi_match"}
    )
    multi_match_n = sum(
        1
        for s in slides
        if isinstance(s, dict) and s.get("narration_status") == "multi_match"
    )
    if view == "slides_with_script" or narrated:
        lines.append(
            f"Narration: {narrated}/{len(slides)} slide(s) have script text attached."
        )
    elif manifest.get("segment_manifest_source"):
        lines.append("Narration: segment manifest provided but no slide matched narration_text.")
    if multi_match_n:
        lines.append(
            f"Narration review: {multi_match_n} slide(s) have multiple segment matches and need operator resolution."
        )
    related = manifest.get("related_assets")
    if isinstance(related, list) and related:
        lines.append(f"Related assets: {len(related)} row(s) appended after slides.")
    generated_at = str(manifest.get("generated_at") or "").strip()
    if generated_at:
        lines.append(f"Generated at: {generated_at}")
    if review_meta:
        lines.append(
            "Review status: "
            f"missing_assets={review_meta.get('missing_assets', 0)}, "
            f"pending_narration={review_meta.get('pending_narration', 0)}, "
            f"multi_match_narration={review_meta.get('multi_match_narration', 0)}, "
            f"slides_with_findings={review_meta.get('slides_with_findings', 0)}"
        )
    return "\n".join(lines)


def render_index_html(manifest: dict[str, Any]) -> str:
    """Single-page table; view-only (no forms)."""
    return render_index_html_v2(manifest)
    rows_in = manifest.get("rows")
    if not isinstance(rows_in, list):
        rows_in = manifest.get("slides")
    if not isinstance(rows_in, list):
        rows_in = []
    rows: list[str] = []
    for s in rows_in:
        if not isinstance(s, dict):
            continue
        if str(s.get("row_kind") or "slide") == "related_asset":
            seq = html.escape(str(s.get("sequence", "")))
            asset_type = html.escape(str(s.get("asset_type") or "other"))
            label = html.escape(str(s.get("label") or ""))
            source_ref = html.escape(str(s.get("source_ref") or ""))
            link = html.escape(str(s.get("link") or ""))
            status = html.escape(str(s.get("asset_status") or "missing"))
            stage = html.escape(str(s.get("stage") or ""))
            href = str(s.get("html_asset_ref") or "")

            if href:
                preview = f'<a href="{html.escape(href, quote=True)}">open asset</a>'
            else:
                preview = '<strong class="missing">MISSING</strong>'

            script_cell = f"<span>{stage or 'N/A'}</span>"
            rows.append(
                "<tr>"
                f"<td>{seq}</td><td>(related)</td><td>{asset_type}</td><td></td>"
                f"<td>{preview}</td><td>{label}</td><td>{source_ref}</td>"
                f"<td>{link}</td><td>{status}</td><td>{script_cell}</td>"
                "</tr>"
            )
            continue

        seq = html.escape(str(s.get("sequence", "")))
        sid = html.escape(str(s.get("slide_id", "")))
        fid = html.escape(str(s.get("fidelity", "")))
        variant = html.escape(str(s.get("dispatch_variant") or ""))
        card = html.escape(str(s.get("card_number", "")))
        title = html.escape(str(s.get("display_title", "")))
        sref = html.escape(str(s.get("source_ref", "")))
        fpath = html.escape(str(s.get("file_path", "")))
        status = html.escape(str(s.get("asset_status", "")))
        selected_badge = "<strong>yes</strong>" if bool(s.get("selected")) else ""
        quality_text = html.escape(
            f"Vera={s.get('vera_score', 'n/a')} | Quinn={s.get('quinn_score', 'n/a')}"
        )
        ref = str(s.get("html_asset_ref", "") or "")

        if s.get("asset_status") == "present" and ref:
            preview = (
                f'<img src="{html.escape(ref, quote=True)}" '
                'alt="" style="max-width:120px;max-height:80px;object-fit:contain;" />'
            )
        elif s.get("asset_status") == "remote" and ref:
            preview = (
                f'<a href="{html.escape(ref, quote=True)}">open URL</a><br/>'
                f'<img src="{html.escape(ref, quote=True)}" '
                'alt="" style="max-width:120px;max-height:80px;object-fit:contain;" />'
            )
        else:
            preview = '<strong class="missing">MISSING</strong>'

        nstat = str(s.get("narration_status") or "pending")
        ntext = str(s.get("narration_text") or "")
        if nstat == "present" and ntext.strip():
            script_cell = (
                f'<pre class="narration-text">{html.escape(ntext)}</pre>'
            )
        else:
            script_cell = (
                '<span class="pending-script">Pending (pre-Pass 2)</span>'
            )

        rows.append(
            "<tr>"
            f"<td>{seq}</td><td>{sid}</td><td>{fid}</td><td>{variant}</td><td>{card}</td>"
            f"<td>{preview}</td><td>{title}</td><td>{sref}</td>"
            f"<td>{fpath}</td><td>{status}</td><td>{quality_text}</td><td>{selected_badge}</td><td>{script_cell}</td>"
            "</tr>"
        )

    body_rows = "\n".join(rows) if rows else "<tr><td colspan='13'>No slides</td></tr>"
    pair_section_rows: list[str] = []
    dd = manifest.get("double_dispatch") if isinstance(manifest.get("double_dispatch"), dict) else {}
    for pair in dd.get("variant_pairs", []) if isinstance(dd, dict) else []:
        if not isinstance(pair, dict):
            continue
        var_a = pair.get("variants", {}).get("A") if isinstance(pair.get("variants"), dict) else None
        var_b = pair.get("variants", {}).get("B") if isinstance(pair.get("variants"), dict) else None
        if not isinstance(var_a, dict) or not isinstance(var_b, dict):
            continue

        def _pair_preview(row: dict[str, Any]) -> str:
            href = str(row.get("html_asset_ref") or "")
            if href:
                return (
                    f'<img src="{html.escape(href, quote=True)}" '
                    'alt="" style="max-width:260px;max-height:150px;object-fit:contain;" />'
                )
            return '<strong class="missing">MISSING</strong>'

        pair_section_rows.append(
            "<tr>"
            f"<td>{html.escape(str(pair.get('card_number', '')))}</td>"
            f"<td>{_pair_preview(var_a)}</td>"
            f"<td>{_pair_preview(var_b)}</td>"
            f"<td>Vera={html.escape(str(var_a.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_a.get('quinn_score', 'n/a')))}</td>"
            f"<td>Vera={html.escape(str(var_b.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_b.get('quinn_score', 'n/a')))}</td>"
            f"<td>{html.escape(str(pair.get('selected_variant') or 'pending'))}</td>"
            "</tr>"
        )

    pair_section_html = ""
    if pair_section_rows:
        pair_section_html = (
            "<h2>Variant Selection (A/B side-by-side)</h2>"
            "<table><thead><tr>"
            "<th>card</th><th>variant A</th><th>variant B</th><th>A scores</th><th>B scores</th><th>selected</th>"
            "</tr></thead><tbody>"
            + "\n".join(pair_section_rows)
            + "</tbody></table>"
        )

    selected_preview_rows: list[str] = []
    for item in manifest.get("selected_full_deck_preview", []) if isinstance(manifest.get("selected_full_deck_preview"), list) else []:
        if not isinstance(item, dict):
            continue
        href = str(item.get("html_asset_ref") or "")
        preview = (
            f'<img src="{html.escape(href, quote=True)}" alt="" style="max-width:320px;max-height:180px;object-fit:contain;" />'
            if href
            else '<strong class="missing">MISSING</strong>'
        )
        selected_preview_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('card_number', '')))}</td>"
            f"<td>{html.escape(str(item.get('slide_id', '')))}</td>"
            f"<td>{preview}</td>"
            "</tr>"
        )

    selected_preview_html = ""
    if selected_preview_rows:
        selected_preview_html = (
            "<h2>Full-Deck Preview (selected variants)</h2>"
            "<table><thead><tr><th>card</th><th>slide_id</th><th>preview</th></tr></thead><tbody>"
            + "\n".join(selected_preview_rows)
            + "</tbody></table>"
        )
    gen_at = html.escape(str(manifest.get("generated_at", "")))
    view = html.escape(str(manifest.get("storyboard_view") or "slides_only"))
    cap = f"Storyboard (view-only) — {view} — generated {gen_at}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Storyboard review</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 1rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.5rem; vertical-align: top; }}
    th {{ background: #f4f4f4; text-align: left; }}
    .missing {{ color: #b00020; }}
    .pending-script {{ color: #666; font-style: italic; }}
    .narration-text {{
      white-space: pre-wrap; max-width: 36rem; max-height: 16rem;
      overflow: auto; margin: 0; font-family: inherit; font-size: 0.9rem;
    }}
    caption {{ text-align: left; font-weight: bold; margin-bottom: 0.5rem; }}
  </style>
</head>
<body>
    {pair_section_html}
    {selected_preview_html}
    <table>
    <caption>{cap}</caption>
    <thead>
      <tr>
                <th>#</th><th>slide_id</th><th>fidelity</th><th>variant</th><th>card</th>
        <th>preview</th><th>title</th><th>source_ref</th><th>file_path</th>
                <th>asset_status</th><th>quality</th><th>selected</th><th>narration (Pass 2)</th>
      </tr>
    </thead>
    <tbody>
{body_rows}
    </tbody>
  </table>
</body>
</html>
"""


def render_index_html_v2(manifest: dict[str, Any]) -> str:
    """Reviewer-friendly storyboard surface with static progressive enhancement."""
    slides = manifest.get("slides") if isinstance(manifest.get("slides"), list) else []
    related_assets = manifest.get("related_assets") if isinstance(manifest.get("related_assets"), list) else []
    review_meta = manifest.get("review_meta") if isinstance(manifest.get("review_meta"), dict) else {}
    storyboard_policy = (
        manifest.get("storyboard_policy") if isinstance(manifest.get("storyboard_policy"), dict) else {}
    )
    voice_direction_defaults = (
        storyboard_policy.get("voice_direction_defaults")
        if isinstance(storyboard_policy.get("voice_direction_defaults"), dict)
        else {}
    )
    dd = manifest.get("double_dispatch") if isinstance(manifest.get("double_dispatch"), dict) else {}
    cluster_review_target_wpm = 150.0
    actionable_issue_count = sum(
        1
        for slide in slides
        if isinstance(slide, dict)
        and isinstance(slide.get("issue_flags"), list)
        and len(slide.get("issue_flags")) > 0
    )
    issue_controls_disabled = actionable_issue_count == 0
    issue_checkbox_attrs = ' disabled aria-disabled="true"' if issue_controls_disabled else ""
    issue_button_attrs = ' disabled aria-disabled="true"' if issue_controls_disabled else ""
    issue_button_label = "No issues" if issue_controls_disabled else "Next issue"
    issue_label_class = "toolbar-label disabled" if issue_controls_disabled else "toolbar-label"

    def _preview_markup(item: dict[str, Any], *, size: str = "card") -> str:
        href = str(item.get("preview_href") or item.get("html_asset_ref") or "")
        preview_kind = str(item.get("preview_kind") or "missing")
        row_id = html.escape(str(item.get("row_id") or "preview"), quote=True)
        title = html.escape(str(item.get("display_title") or item.get("label") or item.get("slide_id") or "Preview"))
        img_class = "slide-thumbnail" if size == "card" else "variant-thumbnail"
        if preview_kind == "image" and href:
            escaped_href = html.escape(href, quote=True)
            return (
                f'<a class="preview-link" data-role="preview-link" data-row-id="{row_id}" '
                f'data-preview-src="{escaped_href}" href="{escaped_href}" target="_blank" rel="noopener noreferrer">'
                f'<img class="{img_class}" src="{escaped_href}" alt="{title} preview" loading="lazy" />'
                '<span class="expand-cue" aria-hidden="true">[+]</span>'
                "</a>"
            )
        if preview_kind in {"link", "other"} and href:
            escaped_href = html.escape(href, quote=True)
            return (
                f'<a class="preview-link preview-link-text" data-role="preview-link" data-row-id="{row_id}" '
                f'href="{escaped_href}" target="_blank" rel="noopener noreferrer">Open asset</a>'
            )
        return '<div class="preview-missing">Preview unavailable</div>'

    def _motion_preview_markup(item: dict[str, Any]) -> str:
        href = str(item.get("motion_preview_href") or "")
        kind = str(item.get("motion_preview_kind") or "missing")
        poster = str(item.get("motion_poster_href") or item.get("preview_href") or "")
        if kind == "video" and href:
            escaped_href = html.escape(href, quote=True)
            poster_attr = (
                f' poster="{html.escape(poster, quote=True)}"'
                if poster and not _is_remote_ref(poster)
                else ""
            )
            return (
                '<div class="motion-preview-wrap">'
                f'<video class="motion-preview" controls preload="metadata"{poster_attr}>'
                f'<source src="{escaped_href}">'
                "Your browser cannot play this motion preview."
                "</video>"
                f'<a class="motion-link" href="{escaped_href}" target="_blank" rel="noopener noreferrer">Open motion asset</a>'
                "</div>"
            )
        if kind in {"image", "link", "other"} and href:
            escaped_href = html.escape(href, quote=True)
            return (
                f'<a class="preview-link preview-link-text" href="{escaped_href}" '
                'target="_blank" rel="noopener noreferrer">Open motion asset</a>'
            )
        return '<div class="script-state">No motion preview available.</div>'

    pair_section_rows: list[str] = []
    run_id_escaped = html.escape(str(manifest.get("run_id") or ""), quote=True)
    for pair in dd.get("variant_pairs", []) if isinstance(dd, dict) else []:
        if not isinstance(pair, dict):
            continue
        var_a = pair.get("variants", {}).get("A") if isinstance(pair.get("variants"), dict) else None
        var_b = pair.get("variants", {}).get("B") if isinstance(pair.get("variants"), dict) else None
        if not isinstance(var_a, dict) or not isinstance(var_b, dict):
            continue
        cn = html.escape(str(pair.get('card_number', '')))
        pre_selected = str(pair.get('selected_variant') or '').strip().upper()
        a_cls = ' class="variant-selected"' if pre_selected == "A" else ""
        b_cls = ' class="variant-selected"' if pre_selected == "B" else ""
        pair_section_rows.append(
            f'<tr data-card="{cn}">'
            f"<td>{cn}</td>"
            f'<td{a_cls} data-variant="A">{_preview_markup(var_a, size="variant")}'
            f'<button class="pick-btn" data-card="{cn}" data-pick="A"'
            f'{" disabled" if pre_selected == "A" else ""}>Pick A</button></td>'
            f'<td{b_cls} data-variant="B">{_preview_markup(var_b, size="variant")}'
            f'<button class="pick-btn" data-card="{cn}" data-pick="B"'
            f'{" disabled" if pre_selected == "B" else ""}>Pick B</button></td>'
            f"<td>Vera={html.escape(str(var_a.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_a.get('quinn_score', 'n/a')))}</td>"
            f"<td>Vera={html.escape(str(var_b.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_b.get('quinn_score', 'n/a')))}</td>"
            f'<td class="sel-status" data-card="{cn}">{pre_selected or "pending"}</td>'
            "</tr>"
        )
    pair_section_html = ""
    if pair_section_rows:
        total_pairs = len(pair_section_rows)
        pair_section_html = (
            '<section class="variant-section">'
            "<h2>Variant Selection</h2>"
            f'<div class="sel-toolbar">'
            f'<span class="sel-progress" id="sel-progress">0 / {total_pairs} selected</span>'
            '<button class="sel-all-btn" id="sel-all-a">All A</button>'
            '<button class="sel-all-btn" id="sel-all-b">All B</button>'
            '<button class="sel-export-btn" id="sel-export" disabled>Export selection JSON</button>'
            '</div>'
            '<table class="variant-table"><thead><tr>'
            "<th>card</th><th>variant A</th><th>variant B</th><th>A scores</th><th>B scores</th><th>selected</th>"
            "</tr></thead><tbody>"
            + "\n".join(pair_section_rows)
            + "</tbody></table></section>"
            '<script>'
            'const SEL={};\n'
            f'const RUN_ID="{run_id_escaped}";\n'
            f'const TOTAL={total_pairs};\n'
            'function pick(card,v){'
            'SEL[card]=v;'
            'const row=document.querySelector(`tr[data-card="${card}"]`);'
            'if(row){'
            'row.querySelectorAll("td[data-variant]").forEach(td=>{'
            'td.classList.toggle("variant-selected",td.dataset.variant===v);'
            'const btn=td.querySelector(".pick-btn");'
            'if(btn)btn.disabled=(btn.dataset.pick===v);'
            '});'
            'const st=row.querySelector(".sel-status");if(st)st.textContent=v;'
            '}'
            'const n=Object.keys(SEL).length;'
            'document.getElementById("sel-progress").textContent=n+" / "+TOTAL+" selected";'
            'document.getElementById("sel-export").disabled=(n<TOTAL);'
            '}\n'
            'document.querySelectorAll(".pick-btn").forEach(b=>'
            'b.addEventListener("click",()=>pick(b.dataset.card,b.dataset.pick)));\n'
            'document.getElementById("sel-all-a").addEventListener("click",()=>'
            'document.querySelectorAll("tr[data-card]").forEach(r=>pick(r.dataset.card,"A")));\n'
            'document.getElementById("sel-all-b").addEventListener("click",()=>'
            'document.querySelectorAll("tr[data-card]").forEach(r=>pick(r.dataset.card,"B")));\n'
            'document.getElementById("sel-export").addEventListener("click",()=>{'
            'const out={run_id:RUN_ID,selected_at:new Date().toISOString(),selections:{}};'
            'Object.entries(SEL).sort(([a],[b])=>a-b).forEach(([k,v])=>out.selections[k]=v);'
            'const blob=new Blob([JSON.stringify(out,null,2)],{type:"application/json"});'
            'const a=document.createElement("a");a.href=URL.createObjectURL(blob);'
            'a.download="variant-selection.json";a.click();'
            '});\n'
            '</script>'
            '<style>'
            '.sel-toolbar{display:flex;gap:12px;align-items:center;margin:12px 0;flex-wrap:wrap}'
            '.sel-progress{font-weight:600;min-width:140px}'
            '.sel-all-btn,.sel-export-btn{padding:6px 14px;border:1px solid #555;border-radius:4px;'
            'background:#f0f0f0;cursor:pointer;font-size:13px}'
            '.sel-all-btn:hover,.sel-export-btn:hover:not([disabled]){background:#ddd}'
            '.sel-export-btn:disabled{opacity:.4;cursor:not-allowed}'
            '.pick-btn{display:block;margin:6px auto 0;padding:4px 16px;border:1px solid #888;'
            'border-radius:3px;background:#e8e8e8;cursor:pointer;font-size:12px}'
            '.pick-btn:hover:not([disabled]){background:#cde}'
            '.pick-btn:disabled{opacity:.4;cursor:not-allowed}'
            'td.variant-selected{outline:3px solid #2a7;background:#eafbf2}'
            '</style>'
        )

    selected_preview_rows: list[str] = []
    for item in manifest.get("selected_full_deck_preview", []) if isinstance(manifest.get("selected_full_deck_preview"), list) else []:
        if not isinstance(item, dict):
            continue
        selected_preview_rows.append(
            '<div class="selected-card">'
            f'<div class="selected-card-meta">Card {html.escape(str(item.get("card_number", "")))} | {html.escape(str(item.get("slide_id", "")))}</div>'
            f'{_preview_markup(item, size="variant")}'
            "</div>"
        )
    selected_preview_html = ""
    if selected_preview_rows:
        selected_preview_html = (
            '<section class="selected-preview-section">'
            "<h2>Authorized Deck Preview</h2>"
            '<div class="selected-preview-grid">'
            + "\n".join(selected_preview_rows)
            + "</div></section>"
        )

    checkpoint_label_raw = str(manifest.get("checkpoint_label") or "Storyboard")
    cluster_groups = manifest.get("cluster_groups") if isinstance(manifest.get("cluster_groups"), list) else []
    grouped_cluster_storyboard = checkpoint_label_raw in {"Storyboard A", "Storyboard B"} and len(cluster_groups) > 0
    storyboard_b_cluster_view = checkpoint_label_raw == "Storyboard B" and len(cluster_groups) > 0
    cluster_group_map = {
        str(group.get("cluster_id")): group
        for group in cluster_groups
        if isinstance(group, dict) and str(group.get("cluster_id") or "").strip()
    }
    slide_data_by_row_id = {
        str(slide.get("row_id") or ""): slide
        for slide in slides
        if isinstance(slide, dict) and str(slide.get("row_id") or "").strip()
    }

    def _coherence_badge_markup(decision: Any, score: Any, *, label_prefix: str = "Coherence") -> str:
        decision_text = _normalize_optional_string(decision)
        score_text = "" if score in (None, "") else f" {html.escape(str(score))}"
        if decision_text is None:
            return '<span class="badge badge-coherence badge-coherence-missing">Coherence pending</span>'
        decision_slug = html.escape(decision_text.lower())
        return (
            f'<span class="badge badge-coherence badge-coherence-{decision_slug}">'
            f'{html.escape(label_prefix)} {html.escape(decision_text.upper())}{score_text}'
            "</span>"
        )

    def _cluster_storyboard_b_summary(group: dict[str, Any], member_slides: list[dict[str, Any]]) -> dict[str, Any]:
        master_intent_raw = _normalize_optional_string(group.get("master_behavioral_intent"))
        if master_intent_raw is None:
            for member in member_slides:
                master_intent_raw = _normalize_optional_string(member.get("master_behavioral_intent"))
                if master_intent_raw:
                    break

        total_words = 0
        total_seconds = 0.0
        has_seconds = False
        mismatch_count = 0
        breakdown_items: list[str] = []
        for member in member_slides:
            narration = str(member.get("narration_text") or "").strip()
            words = _word_count(narration)
            seconds = _estimate_narration_seconds(narration, target_wpm=cluster_review_target_wpm)
            total_words += words
            if seconds is not None:
                total_seconds += seconds
                has_seconds = True
            member_intent_raw = _normalize_optional_string(member.get("behavioral_intent"))
            if not _behavioral_intent_serves_master(master_intent_raw, member_intent_raw):
                mismatch_count += 1
            breakdown_items.append(
                "<li>"
                f"<strong>{html.escape(str(member.get('slide_id') or 'n/a'))}</strong> "
                f"<span class=\"cluster-breakdown-meta\">"
                f"{html.escape(str(member.get('cluster_role') or 'slide'))} | "
                f"{html.escape(str(member.get('cluster_position') or 'n/a'))} | "
                f"{words} words | {_format_estimated_seconds(seconds)} | "
                f"intent {html.escape(str(member_intent_raw or 'n/a'))}"
                "</span></li>"
            )

        total_seconds_text = _format_estimated_seconds(total_seconds if has_seconds else None)
        mismatch_text = (
            "No intent mismatches detected."
            if mismatch_count == 0
            else f"{mismatch_count} segment intent mismatch(s) flagged."
        )
        summary_markup = (
            '<section class="cluster-storyboard-b-summary">'
            '<div class="cluster-storyboard-b-panel">'
            '<h3>Cluster timing summary</h3>'
            f'<p><strong>Total cluster duration</strong> {html.escape(total_seconds_text)} '
            f'at {cluster_review_target_wpm:.0f} WPM across {total_words} words.</p>'
            '<ul class="cluster-breakdown-list">'
            + "".join(breakdown_items)
            + "</ul></div>"
            '<div class="cluster-storyboard-b-panel">'
            '<h3>Intent and voice defaults</h3>'
            '<dl class="cluster-storyboard-b-facts">'
            f'<div><dt>Master intent</dt><dd>{html.escape(str(master_intent_raw or "n/a"))}</dd></div>'
            f'<div><dt>Intent review</dt><dd>{html.escape(mismatch_text)}</dd></div>'
            f'<div><dt>Emotional variability</dt><dd>{html.escape(str(voice_direction_defaults.get("emotional_variability") or "n/a"))}</dd></div>'
            f'<div><dt>Pace variability</dt><dd>{html.escape(str(voice_direction_defaults.get("pace_variability") or "n/a"))}</dd></div>'
            '</dl></div></section>'
        )
        return {
            "master_behavioral_intent": master_intent_raw,
            "total_words": total_words,
            "total_seconds_text": total_seconds_text,
            "mismatch_count": mismatch_count,
            "summary_markup": summary_markup,
        }

    slide_cards: list[str] = []
    card_markup_by_row_id: dict[str, str] = {}
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        issue_flags = slide.get("issue_flags") if isinstance(slide.get("issue_flags"), list) else []
        findings = slide.get("findings") if isinstance(slide.get("findings"), list) else []
        findings_markup = (
            '<ul class="finding-list">'
            + "".join(f"<li>{html.escape(str(finding))}</li>" for finding in findings)
            + "</ul>"
        ) if findings else '<p class="empty-state">No findings attached.</p>'

        narration_status = str(slide.get("narration_status") or "pending")
        narration_label = {
            "present": "Attached",
            "multi_match": "Multi-match",
            "no_match": "No match",
            "pending": "Pending (pre-Pass 2)",
        }.get(narration_status, narration_status)
        narration_text = str(slide.get("narration_text") or "").strip()
        segment_match_count = int(slide.get("segment_match_count") or 0)
        segment_summary_markup = ""
        if narration_status == "multi_match" and segment_match_count > 1:
            segment_summary_markup = (
                f'<div class="script-warning">Multiple segment-manifest matches attached '
                f'({segment_match_count}). Resolve before approval.</div>'
            )
        script_notes = str(slide.get("script_notes") or "").strip()
        script_notes_markup = (
            f'<pre class="script-notes">{html.escape(script_notes)}</pre>'
            if script_notes
            else '<div class="script-state">No script notes attached.</div>'
        )
        cluster_role_raw = _normalize_optional_string(slide.get("cluster_role"))
        bridge_type_raw = _normalize_optional_string(slide.get("bridge_type"))
        behavioral_intent_raw = _normalize_optional_string(slide.get("behavioral_intent"))
        master_behavioral_intent_raw = _normalize_optional_string(slide.get("master_behavioral_intent"))
        segment_word_count = _word_count(narration_text)
        segment_estimated_seconds = _estimate_narration_seconds(
            narration_text,
            target_wpm=cluster_review_target_wpm,
        )
        cluster_position = html.escape(str(slide.get("cluster_position") or "n/a"))
        interstitial_type = html.escape(str(slide.get("interstitial_type") or "n/a"))
        isolation_target = html.escape(str(slide.get("isolation_target") or "n/a"))
        develop_type = html.escape(str(slide.get("develop_type") or "n/a"))
        narrative_arc = html.escape(str(slide.get("narrative_arc") or "n/a"))
        cluster_id_display = html.escape(str(slide.get("cluster_id") or "n/a"))
        cluster_role_badge = (
            f'<span class="badge badge-cluster-role">cluster {html.escape(cluster_role_raw)}</span>'
            if cluster_role_raw
            else ""
        )
        coherence_badge = ""
        coherence_class = ""
        if cluster_role_raw:
            coherence_decision = _normalize_optional_string(slide.get("cluster_coherence_decision"))
            if coherence_decision:
                coherence_class = f" slide-card--coherence-{html.escape(coherence_decision.lower())}"
            coherence_badge = _coherence_badge_markup(
                slide.get("cluster_coherence_decision"),
                slide.get("cluster_coherence_score"),
                label_prefix="Review",
            )
        cluster_meta_markup = ""
        if cluster_role_raw:
            cluster_meta_markup = (
                '<div class="cluster-slide-meta">'
                f'<span><strong>Cluster</strong> {cluster_id_display}</span>'
                f'<span><strong>Position</strong> {cluster_position}</span>'
                f'<span><strong>Interstitial type</strong> {interstitial_type}</span>'
                f'<span><strong>Isolation target</strong> {isolation_target}</span>'
                f'<span><strong>Develop type</strong> {develop_type}</span>'
                f'<span><strong>Arc</strong> {narrative_arc}</span>'
                '</div>'
            )

        fidelity = html.escape(str(slide.get("fidelity") or "unknown"))
        variant = html.escape(str(slide.get("dispatch_variant") or ""))
        orientation = html.escape(str(slide.get("orientation") or "unknown"))
        row_id = html.escape(str(slide.get("row_id") or slide.get("slide_id") or ""), quote=True)
        slide_id = html.escape(str(slide.get("slide_id") or ""))
        title = html.escape(str(slide.get("display_title") or slide.get("slide_id") or ""))
        sequence = html.escape(str(slide.get("sequence") or ""))
        card_number = html.escape(str(slide.get("card_number") or ""))
        source_ref = html.escape(str(slide.get("source_ref") or ""))
        file_path = html.escape(str(slide.get("file_path") or ""))
        asset_status = html.escape(str(slide.get("asset_status") or "unknown"))
        literal_visual_source = html.escape(str(slide.get("literal_visual_source") or "n/a"))
        motion_type = html.escape(str(slide.get("motion_type") or "static"))
        motion_status = html.escape(str(slide.get("motion_status") or "n/a"))
        motion_source = html.escape(str(slide.get("motion_source") or "n/a"))
        motion_asset_path = html.escape(str(slide.get("motion_asset_path") or "n/a"))
        motion_duration_raw = slide.get("motion_duration_seconds")
        motion_duration = html.escape(
            str(motion_duration_raw if motion_duration_raw not in (None, "") else "n/a")
        )
        runtime_target_seconds = html.escape(
            str(slide.get("runtime_target_seconds") if slide.get("runtime_target_seconds") not in (None, "") else "n/a")
        )
        visual_mode = html.escape(str(slide.get("visual_mode") or "n/a"))
        visual_file = html.escape(str(slide.get("visual_file") or "n/a"))
        timing_role = html.escape(str(slide.get("timing_role") or "n/a"))
        content_density = html.escape(str(slide.get("content_density") or "n/a"))
        visual_detail_load = html.escape(str(slide.get("visual_detail_load") or "n/a"))
        duration_rationale = html.escape(str(slide.get("duration_rationale") or "n/a"))
        bridge_type = html.escape(str(bridge_type_raw or "n/a"))
        behavioral_intent = html.escape(str(behavioral_intent_raw or "n/a"))
        matched_segment_ids = [
            str(item).strip()
            for item in slide.get("matched_segment_ids", [])
            if str(item).strip()
        ]
        matched_narration_refs = [
            str(item).strip()
            for item in slide.get("matched_narration_refs", [])
            if str(item).strip()
        ]
        matched_segment_ids_markup = html.escape(", ".join(matched_segment_ids) or "n/a")
        matched_narration_refs_markup = html.escape(", ".join(matched_narration_refs) or "n/a")
        visual_reference_count = html.escape(str(slide.get("matched_visual_reference_count") or 0))
        dimensions = slide.get("dimensions") if isinstance(slide.get("dimensions"), dict) else {}
        dimensions_text = ""
        if dimensions:
            dimensions_text = f"{dimensions.get('width', '?')}×{dimensions.get('height', '?')}"
        dimensions_markup = html.escape(dimensions_text or "unknown")
        selected_markup = '<span class="badge badge-selected">selected</span>' if bool(slide.get("selected")) else ""
        issue_badges = "".join(f'<span class="badge badge-issue">{html.escape(str(flag))}</span>' for flag in issue_flags)
        variant_badge = f'<span class="badge">variant {variant}</span>' if variant else ""
        motion_badge = f'<span class="badge badge-motion">motion {motion_type}</span>' if motion_type != "static" else ""
        quality_text = html.escape(f"Vera {slide.get('vera_score', 'n/a')} | Quinn {slide.get('quinn_score', 'n/a')}")
        issue_attr = html.escape(" ".join(str(flag) for flag in issue_flags), quote=True)
        motion_summary = f"Motion: {motion_type} | {motion_status}"
        if motion_duration != "n/a":
            motion_summary += f" | {motion_duration}s"
        motion_panel_markup = ""
        if motion_type != "static":
            motion_panel_markup = (
                '<section class="motion-preview-panel">'
                '<div class="panel-label">Motion preview</div>'
                f'{_motion_preview_markup(slide)}'
                f'<div class="preview-caption">Motion asset status: <strong>{html.escape(str(slide.get("motion_preview_status") or "missing"))}</strong></div>'
                '</section>'
            )

        script_text_class = "script-text"
        script_cluster_meta_markup = ""
        script_transition_markup = ""
        script_intent_warning_markup = ""
        if storyboard_b_cluster_view and cluster_role_raw:
            if cluster_role_raw == "head":
                script_text_class += " script-text--cluster-head"
            elif cluster_role_raw == "interstitial":
                script_text_class += " script-text--cluster-interstitial"

            serves_master = _behavioral_intent_serves_master(
                master_behavioral_intent_raw,
                behavioral_intent_raw,
            )
            intent_badge_class = "badge-intent-aligned" if serves_master else "badge-intent-mismatch"
            intent_badge_text = "intent serves master" if serves_master else "intent mismatch"
            script_cluster_meta_markup = (
                '<div class="script-metadata-row">'
                f'<span class="badge">{segment_word_count} words</span>'
                f'<span class="badge">@{cluster_review_target_wpm:.0f} WPM {_format_estimated_seconds(segment_estimated_seconds)}</span>'
                f'<span class="badge">{html.escape(str(cluster_role_raw))} narration</span>'
                f'<span class="badge">timing {timing_role}</span>'
                f'<span class="badge">density {content_density}</span>'
                f'<span class="badge">position {cluster_position}</span>'
                f'<span class="badge">intent {behavioral_intent}</span>'
                f'<span class="badge {intent_badge_class}">{intent_badge_text}</span>'
                '</div>'
            )
            if not serves_master:
                script_intent_warning_markup = (
                    '<div class="behavioral-intent-warning">'
                    f'Segment intent <strong>{behavioral_intent}</strong> does not serve cluster master '
                    f'<strong>{html.escape(str(master_behavioral_intent_raw or "n/a"))}</strong>.'
                    '</div>'
                )
            if cluster_role_raw == "head" and bridge_type_raw == "cluster_boundary":
                bridge_excerpt = html.escape(
                    _excerpt_text(narration_text) or "Bridge text unavailable."
                )
                script_transition_markup = (
                    '<div class="transition-divider transition-divider--boundary">'
                    '<strong>Cluster-boundary transition</strong>'
                    f'<span>Bridge type {bridge_type}</span>'
                    f'<div class="transition-bridge-text">{bridge_excerpt}</div>'
                    '</div>'
                )
            elif cluster_role_raw == "interstitial":
                script_transition_markup = (
                    '<div class="transition-divider transition-divider--within">'
                    '<strong>Within-cluster transition</strong>'
                    f'<span>Bridge type {bridge_type}</span>'
                    '</div>'
                )

        script_markup = (
            f'{segment_summary_markup}{script_transition_markup}{script_intent_warning_markup}'
            f'{script_cluster_meta_markup}<pre class="{script_text_class}">{html.escape(narration_text)}</pre>'
            if narration_text
            else (
                f'{segment_summary_markup}{script_transition_markup}{script_intent_warning_markup}'
                f'{script_cluster_meta_markup}<div class="script-state">{html.escape(narration_label)}</div>'
            )
        )

        cluster_role_class = ""
        if cluster_role_raw == "head":
            cluster_role_class = " slide-card--cluster-head"
        elif cluster_role_raw == "interstitial":
            cluster_role_class = " slide-card--cluster-interstitial"

        slide_cards.append(
            f'<article class="slide-card{cluster_role_class}{coherence_class}" id="{row_id}" data-role="slide-card" data-slide-id="{slide_id}" '
            f'data-fidelity="{fidelity}" data-orientation="{orientation}" data-issues="{issue_attr}">'
            '<header class="slide-card-header">'
            '<div class="slide-card-title-group">'
            f'<div class="sequence-pill">#{sequence}</div>'
            '<div>'
            f'<h2 class="slide-card-title">{title}</h2>'
            f'<div class="slide-card-subtitle">{slide_id}</div>'
            '</div></div>'
            '<div class="badge-row">'
            f'<span class="badge badge-fidelity">{fidelity}</span>'
            f'{variant_badge}'
            f'{motion_badge}'
            f'{cluster_role_badge}'
            f'{coherence_badge}'
            f'<span class="badge">card {card_number or "n/a"}</span>'
            f'<span class="badge">orientation {orientation}</span>'
            f'{selected_markup}{issue_badges}'
            '</div></header>'
            f'<div class="slide-card-body{" slide-card-body--motion" if motion_type != "static" else ""}">'
            '<section class="slide-preview-panel">'
            '<div class="panel-label">Approved slide</div>'
            f'{_preview_markup(slide, size="variant" if cluster_role_raw == "interstitial" and grouped_cluster_storyboard else "card")}'
            f'<div class="preview-caption">Asset status: <strong>{asset_status}</strong> | Dimensions: <strong>{dimensions_markup}</strong></div>'
            f'<div class="preview-caption">Motion review: <strong>{html.escape(motion_summary)}</strong></div>'
            f'{cluster_meta_markup}'
            '</section>'
            f'{motion_panel_markup}'
            '<section class="slide-script-panel">'
            '<div class="panel-grid">'
            '<div class="panel">'
            '<h3>Script</h3>'
            f'<div class="script-status">Status: {html.escape(narration_label)}</div>'
            f'{script_markup}'
            '</div>'
            '<div class="panel">'
            '<h3>Script notes</h3>'
            f'{script_notes_markup}'
            '</div>'
            '</div>'
            '<details class="evidence-panel"><summary>Evidence & provenance</summary>'
            '<dl class="evidence-list">'
            f'<div><dt>Source ref</dt><dd>{source_ref or "n/a"}</dd></div>'
            f'<div><dt>File path</dt><dd>{file_path or "n/a"}</dd></div>'
            f'<div><dt>Created</dt><dd>{html.escape(str(manifest.get("generated_at") or ""))}</dd></div>'
            f'<div><dt>Literal-visual source</dt><dd>{literal_visual_source}</dd></div>'
            f'<div><dt>Matched segments</dt><dd>{matched_segment_ids_markup}</dd></div>'
            f'<div><dt>Narration refs</dt><dd>{matched_narration_refs_markup}</dd></div>'
            f'<div><dt>Visual refs</dt><dd>{visual_reference_count}</dd></div>'
            f'<div><dt>Visual mode</dt><dd>{visual_mode}</dd></div>'
            f'<div><dt>Visual file</dt><dd>{visual_file}</dd></div>'
            f'<div><dt>Motion type</dt><dd>{motion_type}</dd></div>'
            f'<div><dt>Motion status</dt><dd>{motion_status}</dd></div>'
            f'<div><dt>Motion source</dt><dd>{motion_source}</dd></div>'
            f'<div><dt>Motion duration</dt><dd>{motion_duration}</dd></div>'
            f'<div><dt>Runtime target (s)</dt><dd>{runtime_target_seconds}</dd></div>'
            f'<div><dt>Motion asset</dt><dd>{motion_asset_path}</dd></div>'
            f'<div><dt>Timing role</dt><dd>{timing_role}</dd></div>'
            f'<div><dt>Content density</dt><dd>{content_density}</dd></div>'
            f'<div><dt>Visual detail load</dt><dd>{visual_detail_load}</dd></div>'
            f'<div><dt>Bridge type</dt><dd>{bridge_type}</dd></div>'
            f'<div><dt>Behavioral intent</dt><dd>{behavioral_intent}</dd></div>'
            f'<div><dt>Duration rationale</dt><dd>{duration_rationale}</dd></div>'
            f'<div><dt>Cluster position</dt><dd>{cluster_position}</dd></div>'
            f'<div><dt>Interstitial type</dt><dd>{interstitial_type}</dd></div>'
            f'<div><dt>Isolation target</dt><dd>{isolation_target}</dd></div>'
            f'<div><dt>Quality</dt><dd>{quality_text}</dd></div>'
            '</dl>'
            '<div class="findings-block">'
            '<h4>Findings</h4>'
            f'{findings_markup}'
            '</div>'
            '</details></section></div></article>'
        )
        card_markup_by_row_id[str(slide.get("row_id") or "")] = slide_cards[-1]

    related_markup = ""
    if related_assets:
        related_rows: list[str] = []
        for asset in related_assets:
            if not isinstance(asset, dict):
                continue
            related_rows.append(
                '<article class="related-card" data-role="related-asset">'
                f'<div class="related-meta">#{html.escape(str(asset.get("sequence") or ""))} | {html.escape(str(asset.get("asset_type") or "other"))}</div>'
                f'<h3>{html.escape(str(asset.get("label") or ""))}</h3>'
                f'<div class="related-stage">{html.escape(str(asset.get("stage") or "N/A"))}</div>'
                f'<div class="related-link">{_preview_markup(asset)}</div>'
                f'<div class="related-source">{html.escape(str(asset.get("source_ref") or "n/a"))}</div>'
                '</article>'
            )
        related_markup = (
            '<section class="related-assets-section">'
            '<h2>Related assets</h2>'
            '<div class="related-assets-grid">'
            + "\n".join(related_rows)
            + "</div></section>"
        )

    generated_at = html.escape(str(manifest.get("generated_at") or ""))
    view = html.escape(str(manifest.get("storyboard_view") or "slides_only"))
    checkpoint_label = html.escape(str(manifest.get("checkpoint_label") or "Storyboard"))
    run_id = html.escape(str(manifest.get("run_id") or "unbound"))
    runtime_plan = (
        storyboard_policy.get("runtime_plan")
        if isinstance(storyboard_policy.get("runtime_plan"), dict)
        else {}
    )
    script_policy = (
        storyboard_policy.get("script_policy")
        if isinstance(storyboard_policy.get("script_policy"), dict)
        else {}
    )
    voice_direction_defaults = (
        storyboard_policy.get("voice_direction_defaults")
        if isinstance(storyboard_policy.get("voice_direction_defaults"), dict)
        else {}
    )
    runtime_total_minutes = html.escape(
        str(
            runtime_plan.get("target_total_runtime_minutes")
            or runtime_plan.get("target_total_minutes")
            or "n/a"
        )
    )
    # TODO: remove legacy fallbacks after migration from slide_runtime_average_seconds is complete
    runtime_avg_seconds = html.escape(
        str(
            runtime_plan.get("avg_slide_seconds")
            or runtime_plan.get("slide_runtime_average_seconds")
            or runtime_plan.get("target_avg_slide_seconds")
            or "n/a"
        )
    )
    runtime_variance = html.escape(
        str(
            runtime_plan.get("slide_runtime_variability_scale")
            or runtime_plan.get("target_slide_variance_seconds")
            or "n/a"
        )
    )
    narration_density_block = script_policy.get("narration_density")
    target_wpm_value: Any = None
    if isinstance(narration_density_block, dict):
        target_wpm_value = narration_density_block.get("target_wpm")
        script_narration_density = html.escape(
            str(
                target_wpm_value
                or narration_density_block.get("mean_words_per_slide")
                or "n/a"
            )
        )
    else:
        script_narration_density = html.escape(str(script_policy.get("narration_density") or "n/a"))
    target_wpm = html.escape(
        str(
            target_wpm_value
            or script_policy.get("target_wpm")
            or "n/a"
        )
    )
    engagement_stance_block = script_policy.get("engagement_stance")
    if isinstance(engagement_stance_block, dict):
        script_engagement_stance = html.escape(str(engagement_stance_block.get("posture") or "n/a"))
    else:
        script_engagement_stance = html.escape(str(script_policy.get("engagement_stance") or "n/a"))
    emotional_variability = html.escape(str(voice_direction_defaults.get("emotional_variability") or "n/a"))
    pace_variability = html.escape(str(voice_direction_defaults.get("pace_variability") or "n/a"))
    wpm_pace_coupling = html.escape(f"{target_wpm} wpm +/- pace {pace_variability}")
    policy_source = html.escape(str(storyboard_policy.get("envelope_source") or "n/a"))
    meta_badges = [
        f'<span class="meta-pill">Run {run_id}</span>',
        f'<span class="meta-pill">{checkpoint_label}</span>',
        f'<span class="meta-pill">View {view}</span>',
        f'<span class="meta-pill">Slides {review_meta.get("total_slides", len(slides))}</span>',
        f'<span class="meta-pill">Narrated {review_meta.get("slides_with_narration", 0)}</span>',
        f'<span class="meta-pill">Missing assets {review_meta.get("missing_assets", 0)}</span>',
        f'<span class="meta-pill">Target total {runtime_total_minutes} min</span>',
        f'<span class="meta-pill">Avg slide {runtime_avg_seconds}s</span>',
        f'<span class="meta-pill">Runtime variability {runtime_variance}</span>',
        f'<span class="meta-pill">Emotional variability {emotional_variability}</span>',
        f'<span class="meta-pill">Pace variability {pace_variability}</span>',
        f'<span class="meta-pill">WPM {target_wpm} +/- pace {pace_variability}</span>',
    ]
    if review_meta.get("double_dispatch_enabled"):
        meta_badges.append('<span class="meta-pill">Double dispatch</span>')
    fidelity_counts = review_meta.get("fidelity_counts") if isinstance(review_meta.get("fidelity_counts"), dict) else {}
    fidelity_markup = " | ".join(f"{html.escape(str(key))}: {html.escape(str(value))}" for key, value in sorted(fidelity_counts.items())) or "No fidelity counts"
    first_slide = html.escape(str(review_meta.get("first_slide_id") or "n/a"))
    last_slide = html.escape(str(review_meta.get("last_slide_id") or "n/a"))
    cluster_controls_html = ""
    if grouped_cluster_storyboard:
        rendered_clusters: set[str] = set()
        grouped_slide_cards: list[str] = []
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            cluster_id = _normalize_optional_string(slide.get("cluster_id"))
            if cluster_id and cluster_id in cluster_group_map:
                if cluster_id in rendered_clusters:
                    continue
                rendered_clusters.add(cluster_id)
                group = cluster_group_map[cluster_id]
                coherence = group.get("coherence") if isinstance(group.get("coherence"), dict) else {}
                member_slides = [
                    member
                    for row_id in group.get("row_ids", [])
                    for member in [slide_data_by_row_id.get(str(row_id))]
                    if isinstance(member, dict)
                ]
                cluster_storyboard_b = (
                    _cluster_storyboard_b_summary(group, member_slides)
                    if storyboard_b_cluster_view
                    else None
                )
                row_cards = [
                    card_markup_by_row_id.get(str(row_id), "")
                    for row_id in group.get("row_ids", [])
                ]
                member_cards = "".join(card for card in row_cards if card)
                interstitial_types = group.get("interstitial_types") if isinstance(group.get("interstitial_types"), list) else []
                duration_total = group.get("estimated_runtime_seconds")
                duration_text = f'{duration_total:.0f}s' if isinstance(duration_total, (int, float)) else "n/a"
                if cluster_storyboard_b is not None:
                    duration_text = str(cluster_storyboard_b["total_seconds_text"])
                duration_balance = html.escape(str(group.get("duration_balance") or "n/a"))
                interstitial_summary = html.escape(", ".join(str(item) for item in interstitial_types) or "none")
                topic_label = html.escape(str(group.get("topic_label") or group.get("head_slide_id") or cluster_id))
                narrative_arc_text = html.escape(str(group.get("narrative_arc") or "Narrative arc not provided."))
                head_slide_id = html.escape(str(group.get("head_slide_id") or "n/a"))
                cluster_summary_extra = ""
                cluster_storyboard_b_summary_markup = ""
                if cluster_storyboard_b is not None:
                    master_behavioral_intent = html.escape(
                        str(cluster_storyboard_b.get("master_behavioral_intent") or "n/a")
                    )
                    cluster_summary_extra = (
                        f'<span class="badge">Master {master_behavioral_intent}</span>'
                        f'<span class="badge">{html.escape(str(cluster_storyboard_b.get("total_words") or 0))} words</span>'
                        f'<span class="badge">@{cluster_review_target_wpm:.0f} WPM {html.escape(str(cluster_storyboard_b.get("total_seconds_text") or "n/a"))}</span>'
                        f'<span class="badge">Intent mismatches {html.escape(str(cluster_storyboard_b.get("mismatch_count") or 0))}</span>'
                        f'<span class="badge">Emotion {html.escape(str(voice_direction_defaults.get("emotional_variability") or "n/a"))}</span>'
                        f'<span class="badge">Pace {html.escape(str(voice_direction_defaults.get("pace_variability") or "n/a"))}</span>'
                    )
                    cluster_storyboard_b_summary_markup = str(cluster_storyboard_b["summary_markup"])
                grouped_slide_cards.append(
                    '<details class="cluster-group" data-role="cluster-group">'
                    '<summary class="cluster-summary">'
                    '<div class="cluster-summary-main">'
                    f'<div class="cluster-kicker">Cluster {html.escape(cluster_id)}</div>'
                    f'<h2 class="cluster-title">{topic_label}</h2>'
                    f'<p class="cluster-arc">{narrative_arc_text}</p>'
                    '</div>'
                    '<div class="cluster-summary-meta">'
                    f'{_coherence_badge_markup(coherence.get("decision"), coherence.get("score"))}'
                    f'<span class="badge">Head {head_slide_id}</span>'
                    f'<span class="badge">{html.escape(str(group.get("interstitial_count") or 0))} interstitials</span>'
                    f'<span class="badge">Types {interstitial_summary}</span>'
                    f'<span class="badge">Runtime {html.escape(duration_text)}</span>'
                    f'<span class="badge">Balance {duration_balance}</span>'
                    f'{cluster_summary_extra}'
                    '</div>'
                    '</summary>'
                    f'<div class="cluster-group-body">{cluster_storyboard_b_summary_markup}{member_cards}</div>'
                    '</details>'
                )
                continue
            grouped_slide_cards.append(card_markup_by_row_id.get(str(slide.get("row_id") or ""), ""))
        slides_markup = "\n".join(card for card in grouped_slide_cards if card) if grouped_slide_cards else '<div class="empty-state">No slides</div>'
        cluster_controls_html = (
            '<button type="button" data-role="clusters-expand">Expand all clusters</button>'
            '<button type="button" data-role="clusters-collapse">Collapse all clusters</button>'
        )
    else:
        slides_markup = "\n".join(slide_cards) if slide_cards else '<div class="empty-state">No slides</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{checkpoint_label} review</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f6f8;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #5b6472;
      --line: #d8dee8;
      --accent: #143b5d;
      --accent-soft: #dce8f4;
      --warning: #8a5300;
      --warning-soft: #fff3d6;
      --danger: #9b1c1c;
      --success-soft: #dff6e8;
      --shadow: 0 10px 25px rgba(17, 24, 39, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.5; }}
    a {{ color: var(--accent); }}
    .page {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    .summary-banner {{ background: linear-gradient(135deg, #0f2740, #1b4e73); color: #fff; border-radius: 20px; padding: 24px; box-shadow: var(--shadow); margin-bottom: 18px; }}
    .summary-banner h1 {{ margin: 0 0 8px 0; font-size: 1.9rem; }}
    .summary-banner p {{ margin: 0 0 14px 0; color: rgba(255,255,255,0.82); }}
    .meta-pill-row, .badge-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .meta-pill, .badge {{ display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 6px 12px; font-size: 0.86rem; font-weight: 600; }}
    .meta-pill {{ background: rgba(255,255,255,0.14); color: #fff; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 14px; }}
    .summary-details {{ margin-top: 10px; }}
    .summary-details > summary {{ cursor: pointer; list-style: none; display: inline-flex; align-items: center; gap: 8px; font-size: 0.88rem; color: rgba(255,255,255,0.7); font-weight: 600; padding: 4px 0; }}
    .summary-details > summary::after {{ content: " [collapse]"; font-size: 0.78rem; }}
    .summary-details:not([open]) > summary::after {{ content: " [expand]"; }}
    .summary-panel {{ background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.14); border-radius: 16px; padding: 14px; }}
    .summary-panel h2 {{ margin: 0 0 8px 0; font-size: 0.95rem; }}
    .summary-panel p {{ margin: 0; color: rgba(255,255,255,0.88); font-size: 0.9rem; }}
    .summary-panel dl {{ margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 6px 10px; }}
    .summary-panel dt {{ color: rgba(255,255,255,0.7); font-weight: 600; font-size: 0.88rem; }}
    .summary-panel dd {{ margin: 0; overflow-wrap: anywhere; font-size: 0.88rem; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 14px 16px; margin-bottom: 18px; box-shadow: var(--shadow); }}
    .toolbar input[type="search"] {{ min-width: 260px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); font: inherit; }}
    .toolbar label {{ display: inline-flex; align-items: center; gap: 8px; font-size: 0.92rem; color: var(--muted); }}
    .toolbar button {{ padding: 9px 12px; border-radius: 10px; border: 1px solid var(--line); background: #fff; cursor: pointer; font: inherit; }}
    .toolbar button.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .toolbar .disabled, .toolbar button:disabled, .toolbar input:disabled {{ opacity: 0.5; cursor: not-allowed; }}
    .slides-section {{ display: grid; gap: 18px; }}
    .slide-card, .related-card, .variant-section, .selected-preview-section, .related-assets-section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow); }}
    .slide-card {{ overflow: hidden; }}
    .slide-card[hidden] {{ display: none !important; }}
    .slide-card-header {{ display: flex; justify-content: space-between; gap: 16px; padding: 18px 20px 12px; border-bottom: 1px solid var(--line); align-items: flex-start; }}
    .slide-card-title-group {{ display: flex; gap: 14px; align-items: flex-start; }}
    .sequence-pill {{ min-width: 50px; height: 50px; display: grid; place-items: center; background: var(--accent-soft); color: var(--accent); border-radius: 14px; font-weight: 800; font-size: 1rem; }}
    .slide-card-title {{ margin: 0; font-size: 1.12rem; }}
    .slide-card-subtitle {{ color: var(--muted); margin-top: 4px; font-size: 0.92rem; }}
    .badge {{ background: #eef2f7; color: #27313f; }}
    .badge-fidelity {{ background: var(--accent-soft); color: var(--accent); }}
    .badge-motion {{ background: rgba(14, 116, 144, 0.14); color: #155e75; }}
    .badge-selected {{ background: var(--success-soft); color: #14532d; }}
    .badge-issue {{ background: var(--warning-soft); color: var(--warning); }}
    .badge-cluster-role {{ background: rgba(20, 59, 93, 0.12); color: var(--accent); }}
    .badge-coherence-pass {{ background: #dff6e8; color: #166534; }}
    .badge-coherence-warn {{ background: #fff3d6; color: #8a5300; }}
    .badge-coherence-fail {{ background: #fde2e2; color: #9b1c1c; }}
    .badge-coherence-missing {{ background: #eef2f7; color: #475569; }}
    .slide-card-body {{ display: grid; grid-template-columns: minmax(280px, 420px) minmax(0, 1fr); gap: 18px; padding: 18px 20px 20px; }}
    .cluster-group {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow); overflow: hidden; }}
    .cluster-group + .cluster-group {{ margin-top: 28px; }}
    .cluster-summary {{ list-style: none; cursor: pointer; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px; align-items: center; padding: 18px 20px; background: linear-gradient(135deg, #f8fbfd, #eef5fb); }}
    .cluster-summary::-webkit-details-marker {{ display: none; }}
    .cluster-summary::after {{ content: "[expand]"; color: var(--muted); font-size: 0.82rem; font-weight: 700; }}
    .cluster-group[open] .cluster-summary::after {{ content: "[collapse]"; }}
    .cluster-summary-main {{ min-width: 0; }}
    .cluster-kicker {{ color: var(--muted); font-size: 0.84rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
    .cluster-title {{ margin: 4px 0 6px; font-size: 1.12rem; }}
    .cluster-arc {{ margin: 0; color: var(--muted); }}
    .cluster-summary-meta {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }}
    .cluster-group-body {{ display: grid; gap: 12px; padding: 16px; border-top: 1px solid var(--line); background: #f8fafc; }}
    .cluster-storyboard-b-summary {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .cluster-storyboard-b-panel {{ background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    .cluster-storyboard-b-panel h3 {{ margin: 0 0 8px 0; font-size: 0.96rem; }}
    .cluster-storyboard-b-panel p {{ margin: 0; color: var(--ink); }}
    .cluster-breakdown-list {{ margin: 12px 0 0 18px; padding: 0; display: grid; gap: 8px; }}
    .cluster-breakdown-list li {{ color: var(--ink); }}
    .cluster-breakdown-meta {{ color: var(--muted); font-size: 0.88rem; }}
    .cluster-storyboard-b-facts {{ margin: 0; display: grid; gap: 10px; }}
    .cluster-storyboard-b-facts div {{ padding: 10px 12px; background: #f8fafc; border: 1px solid var(--line); border-radius: 12px; }}
    .cluster-storyboard-b-facts dt {{ color: var(--muted); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }}
    .cluster-storyboard-b-facts dd {{ margin: 4px 0 0; font-size: 0.95rem; overflow-wrap: anywhere; }}
    .slide-card--cluster-head .sequence-pill {{ background: #d6e8f8; }}
    .slide-card--cluster-interstitial {{ margin-left: 28px; border-left: 4px solid #c7d7e6; }}
    .slide-card--coherence-pass {{ border-left: 4px solid #16a34a; }}
    .slide-card--coherence-warn {{ border-left: 4px solid #d97706; }}
    .slide-card--coherence-fail {{ border-left: 4px solid #dc2626; }}
    .cluster-slide-meta {{ margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px 12px; color: var(--muted); font-size: 0.88rem; }}
    .cluster-slide-meta span {{ display: inline-flex; gap: 4px; }}
    .script-metadata-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 12px 0; }}
    .badge-intent-aligned {{ background: #dff6e8; color: #166534; }}
    .badge-intent-mismatch {{ background: #fde2e2; color: #9b1c1c; }}
    .panel-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 14px; }}
    .panel, .summary-panel, .related-card {{ min-width: 0; }}
    .panel {{ background: #fafbfd; border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    .panel-label, .panel h3, .evidence-panel summary, .variant-section h2, .selected-preview-section h2, .related-assets-section h2 {{ font-size: 0.98rem; font-weight: 700; margin: 0 0 10px 0; }}
    .slide-thumbnail, .variant-thumbnail {{ width: 100%; border-radius: 14px; border: 1px solid var(--line); background: #fff; box-shadow: 0 6px 18px rgba(17, 24, 39, 0.08); }}
    .slide-thumbnail {{ max-height: 280px; object-fit: contain; background: #f8fafc; }}
    .variant-thumbnail {{ max-width: 260px; max-height: 150px; object-fit: contain; }}
    .motion-preview-panel {{ margin-top: 14px; }}
    .slide-card-body--motion .slide-preview-panel {{ grid-column: 1; grid-row: 1; }}
    .slide-card-body--motion .motion-preview-panel {{ grid-column: 1; grid-row: 2; margin-top: 0; }}
    .slide-card-body--motion .slide-script-panel {{ grid-column: 2; grid-row: 1 / -1; }}
    .motion-preview-wrap {{ display: grid; gap: 8px; }}
    .motion-preview {{ width: 100%; max-height: 280px; border-radius: 14px; border: 1px solid var(--line); background: #020617; box-shadow: 0 6px 18px rgba(17, 24, 39, 0.12); }}
    .motion-link {{ font-size: 0.9rem; color: var(--accent); text-decoration: none; font-weight: 600; }}
    .preview-link {{ display: block; text-decoration: none; position: relative; }}
    .preview-link-text {{ display: inline-flex; align-items: center; justify-content: center; min-height: 120px; width: 100%; border: 1px dashed var(--line); border-radius: 14px; background: #fafafa; color: var(--accent); font-weight: 600; }}
    .expand-cue {{ position: absolute; top: 10px; right: 10px; background: rgba(15, 23, 42, 0.78); color: #fff; border-radius: 999px; padding: 4px 8px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.22); }}
    .preview-caption, .script-status, .related-stage, .related-source {{ color: var(--muted); font-size: 0.9rem; margin-top: 8px; }}
    .script-text, .script-notes {{ white-space: pre-wrap; margin: 0; font: inherit; line-height: 1.55; }}
    .script-text--cluster-head {{ background: linear-gradient(180deg, #f8fbfd 0%, #eef5fb 100%); border: 1px solid #d6e8f8; border-radius: 14px; padding: 14px; }}
    .script-text--cluster-interstitial {{ background: #fcfdff; border-left: 4px solid #bfd3e6; padding: 12px 14px; border-radius: 0 14px 14px 0; }}
    .script-warning {{ margin-bottom: 10px; padding: 10px 12px; border-radius: 10px; background: var(--warning-soft); color: var(--warning); font-size: 0.92rem; font-weight: 600; }}
    .behavioral-intent-warning {{ margin-bottom: 10px; padding: 10px 12px; border-radius: 12px; border: 1px solid #f5c2c7; background: #fff5f5; color: #9b1c1c; font-size: 0.92rem; }}
    .transition-divider {{ display: grid; gap: 4px; margin: 0 0 12px 0; padding: 10px 12px; border-radius: 12px; }}
    .transition-divider strong {{ font-size: 0.86rem; text-transform: uppercase; letter-spacing: 0.03em; }}
    .transition-divider span {{ color: var(--muted); font-size: 0.88rem; }}
    .transition-divider--within {{ background: #f8fafc; border: 1px dashed #cbd5e1; }}
    .transition-divider--boundary {{ background: linear-gradient(135deg, #fff7ed, #ffedd5); border: 1px solid #fdba74; }}
    .transition-bridge-text {{ color: var(--ink); font-size: 0.92rem; }}
    .script-state, .empty-state {{ color: var(--muted); font-style: italic; }}
    .evidence-panel {{ border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px; background: #fff; }}
    .evidence-panel summary {{ cursor: pointer; list-style: none; display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .evidence-panel summary::after {{ content: "[+]"; color: var(--muted); font-size: 0.85rem; font-weight: 700; }}
    .evidence-panel[open] summary::after {{ content: "[-]"; }}
    .evidence-list {{ margin: 12px 0 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 16px; }}
    .evidence-list dt {{ color: var(--muted); font-size: 0.85rem; font-weight: 700; }}
    .evidence-list dd {{ margin: 4px 0 0; font-size: 0.92rem; overflow-wrap: anywhere; }}
    .findings-block {{ margin-top: 14px; }}
    .finding-list {{ margin: 8px 0 0 18px; padding: 0; }}
    .variant-section, .selected-preview-section, .related-assets-section {{ padding: 18px 20px; margin-bottom: 18px; }}
    .variant-table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    .variant-table th, .variant-table td {{ border-top: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }}
    .selected-preview-grid, .related-assets-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
    .selected-card, .related-card {{ padding: 14px; }}
    .selected-card-meta, .related-meta {{ color: var(--muted); font-size: 0.86rem; margin-bottom: 8px; }}
    .preview-missing {{ display: grid; place-items: center; min-height: 140px; border-radius: 14px; border: 1px dashed var(--line); background: #fafafa; color: var(--danger); font-weight: 700; }}
    dialog.preview-dialog {{ width: min(96vw, 1400px); border: none; border-radius: 18px; padding: 0; box-shadow: 0 24px 50px rgba(17, 24, 39, 0.35); }}
    dialog::backdrop {{ background: rgba(17, 24, 39, 0.72); }}
    .dialog-body {{ background: #0f172a; color: #fff; padding: 16px; }}
    .dialog-toolbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }}
    .dialog-toolbar button {{ background: rgba(255,255,255,0.12); color: #fff; border: none; border-radius: 10px; padding: 8px 12px; cursor: pointer; }}
    .dialog-preview {{ width: 100%; max-height: 82vh; object-fit: contain; background: #020617; border-radius: 14px; }}
    .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }}
    @media (max-width: 980px) {{
      .summary-grid, .slide-card-body, .panel-grid {{ grid-template-columns: 1fr; }}
      .slide-card-header {{ flex-direction: column; }}
      .cluster-summary {{ grid-template-columns: 1fr; }}
      .cluster-summary-meta {{ justify-content: flex-start; }}
      .cluster-storyboard-b-summary {{ grid-template-columns: 1fr; }}
      .slide-card--cluster-interstitial {{ margin-left: 0; }}
      .slide-card-body--motion .slide-preview-panel,
      .slide-card-body--motion .motion-preview-panel,
      .slide-card-body--motion .slide-script-panel {{ grid-column: auto; grid-row: auto; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="summary-banner">
      <h1>{checkpoint_label} Review</h1>
      <p>Static storyboard review surface for human approval. The JSON manifest remains the source of truth; this page is a reviewer-friendly projection.</p>
      <div class="meta-pill-row">{''.join(meta_badges)}</div>
      <details class="summary-details" open>
        <summary>Run details</summary>
        <div class="summary-grid">
        <div class="summary-panel">
          <h2>Run summary</h2>
          <p>Generated at {generated_at}. Fidelity mix: {fidelity_markup}.</p>
        </div>
        <div class="summary-panel">
          <h2>Orientation data</h2>
          <dl>
            <div><dt>First slide</dt><dd>{first_slide}</dd></div>
            <div><dt>Last slide</dt><dd>{last_slide}</dd></div>
            <div><dt>Pending narration</dt><dd>{html.escape(str(review_meta.get("pending_narration", 0)))}</dd></div>
            <div><dt>Slides with findings</dt><dd>{html.escape(str(review_meta.get("slides_with_findings", 0)))}</dd></div>
          </dl>
        </div>
        <div class="summary-panel">
          <h2>Runtime and script policy</h2>
          <dl>
            <div><dt>Narration density target</dt><dd>{script_narration_density}</dd></div>
            <div><dt>Engagement stance</dt><dd>{script_engagement_stance}</dd></div>
            <div><dt>Policy source</dt><dd>{policy_source}</dd></div>
          </dl>
        </div>
        </div>
      </details>
    </section>

    {pair_section_html}
    {selected_preview_html}

    <section class="toolbar" aria-label="Storyboard controls">
      <label>
        <span class="sr-only">Search slides</span>
        <input id="search-box" type="search" placeholder="Search slide id, title, source ref" data-role="search" />
      </label>
      <button type="button" class="active" data-role="filter" data-filter="all">All</button>
      <button type="button" data-role="filter" data-filter="creative">Creative</button>
      <button type="button" data-role="filter" data-filter="literal-text">Literal-text</button>
      <button type="button" data-role="filter" data-filter="literal-visual">Literal-visual</button>
      <label class="{issue_label_class}"><input type="checkbox" id="issues-only" data-role="issues-only"{issue_checkbox_attrs} /> Show issues only</label>
      <button type="button" data-role="jump-next-issue"{issue_button_attrs}>{issue_button_label}</button>
      {cluster_controls_html}
    </section>

    <section class="slides-section" aria-label="Storyboard slides">
      {slides_markup}
    </section>

    {related_markup}
  </div>

  <dialog class="preview-dialog" id="preview-dialog">
    <div class="dialog-body">
      <div class="dialog-toolbar">
        <strong id="dialog-title">Preview</strong>
        <div>
          <a id="dialog-open" href="#" target="_blank" rel="noopener noreferrer">Open in new tab</a>
          <button type="button" id="dialog-close">Close</button>
        </div>
      </div>
      <img id="dialog-image" class="dialog-preview" alt="" />
    </div>
  </dialog>

  <script>
    (() => {{
      const cards = Array.from(document.querySelectorAll('[data-role="slide-card"]'));
      const filters = Array.from(document.querySelectorAll('[data-role="filter"]'));
      const searchBox = document.querySelector('[data-role="search"]');
      const issuesOnly = document.querySelector('[data-role="issues-only"]');
      const nextIssueBtn = document.querySelector('[data-role="jump-next-issue"]');
      const expandClustersBtn = document.querySelector('[data-role="clusters-expand"]');
      const collapseClustersBtn = document.querySelector('[data-role="clusters-collapse"]');
      const clusterGroups = Array.from(document.querySelectorAll('[data-role="cluster-group"]'));
      const dialog = document.getElementById('preview-dialog');
      const dialogImage = document.getElementById('dialog-image');
      const dialogTitle = document.getElementById('dialog-title');
      const dialogOpen = document.getElementById('dialog-open');
      const dialogClose = document.getElementById('dialog-close');
      const actionableIssueCards = cards.filter(card => Boolean((card.getAttribute('data-issues') || '').trim()));
      let activeFilter = 'all';

      function applyFilters() {{
        const query = (searchBox?.value || '').toLowerCase().trim();
        const issues = Boolean(issuesOnly?.checked);
        for (const card of cards) {{
          const haystack = card.textContent.toLowerCase();
          const fidelity = card.getAttribute('data-fidelity') || '';
          const cardIssues = (card.getAttribute('data-issues') || '').trim();
          const matchesFilter = activeFilter === 'all' || fidelity === activeFilter;
          const matchesQuery = !query || haystack.includes(query);
          const matchesIssues = !issues || Boolean(cardIssues);
          card.hidden = !(matchesFilter && matchesQuery && matchesIssues);
        }}
      }}

      for (const button of filters) {{
        button.addEventListener('click', () => {{
          activeFilter = button.getAttribute('data-filter') || 'all';
          for (const peer of filters) peer.classList.toggle('active', peer === button);
          applyFilters();
        }});
      }}
      searchBox?.addEventListener('input', applyFilters);
      if (issuesOnly && actionableIssueCards.length === 0) {{
        issuesOnly.checked = false;
      }}
      issuesOnly?.addEventListener('change', applyFilters);
      expandClustersBtn?.addEventListener('click', () => {{
        clusterGroups.forEach(group => group.setAttribute('open', 'open'));
      }});
      collapseClustersBtn?.addEventListener('click', () => {{
        clusterGroups.forEach(group => group.removeAttribute('open'));
      }});
      nextIssueBtn?.addEventListener('click', () => {{
        if (actionableIssueCards.length === 0) return;
        const next = cards.find(card => !card.hidden && (card.getAttribute('data-issues') || '').trim());
        if (next) next.scrollIntoView({{behavior: 'smooth', block: 'center'}});
      }});

      for (const link of document.querySelectorAll('[data-role="preview-link"]')) {{
        link.addEventListener('click', (event) => {{
          const href = link.getAttribute('data-preview-src');
          if (!href || !dialog || typeof dialog.showModal !== 'function') return;
          event.preventDefault();
          dialogImage.src = href;
          dialogImage.alt = link.getAttribute('data-row-id') || 'Preview';
          dialogTitle.textContent = link.closest('[data-role="slide-card"]')?.getAttribute('data-slide-id') || 'Preview';
          dialogOpen.href = href;
          dialog.showModal();
        }});
      }}
      dialogClose?.addEventListener('click', () => dialog?.close());
      dialog?.addEventListener('click', (event) => {{
        const rect = dialog.getBoundingClientRect();
        const inBounds = rect.top <= event.clientY && event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX && event.clientX <= rect.left + rect.width;
        if (!inBounds) dialog.close();
      }});

      if (window.location.hash) {{
        const target = document.getElementById(window.location.hash.slice(1));
        if (target) target.scrollIntoView();
      }}
      applyFilters();
    }})();
  </script>
</body>
</html>
"""
def write_bundle(
    manifest: dict[str, Any],
    storyboard_dir: Path,
) -> None:
    storyboard_dir.mkdir(parents=True, exist_ok=True)
    json_path = storyboard_dir / "storyboard.json"
    html_path = storyboard_dir / "index.html"
    json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    html_path.write_text(render_index_html_v2(manifest), encoding="utf-8")


def cmd_generate(args: argparse.Namespace) -> int:
    payload_path: Path = args.payload
    out_dir: Path = args.out_dir
    asset_base: Path = args.asset_base or payload_path.parent
    storyboard_dir = (out_dir / "storyboard").resolve()

    payload = load_payload(payload_path)
    segment_manifest_path: Path | None = getattr(args, "segment_manifest", None)
    narration_map: dict[str, str] | None = None
    if segment_manifest_path is not None:
        narration_map = load_narration_by_slide_id(segment_manifest_path)
    related_assets_path: Path | None = getattr(args, "related_assets", None)
    related_assets: list[dict[str, Any]] | None = None
    if related_assets_path is not None:
        related_assets = load_related_assets(
            related_assets_path,
            storyboard_dir=storyboard_dir,
            asset_base=asset_base.resolve(),
        )
    cluster_coherence_report_path: Path | None = getattr(args, "cluster_coherence_report", None)
    cluster_coherence_by_id: dict[str, dict[str, Any]] | None = None
    if cluster_coherence_report_path is not None:
        cluster_coherence_by_id = load_cluster_coherence_by_id(cluster_coherence_report_path)

    run_id: str | None = getattr(args, "run_id", None)
    pass2_envelope_path: Path | None = getattr(args, "pass2_envelope", None)
    storyboard_policy_meta = load_storyboard_policy_meta(
        payload_path=payload_path,
        explicit_envelope_path=pass2_envelope_path,
    )

    manifest = build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=asset_base.resolve(),
        narration_by_slide_id=narration_map,
        segment_manifest_path=segment_manifest_path,
        related_assets=related_assets,
        run_id=run_id,
        storyboard_policy_meta=storyboard_policy_meta,
        cluster_coherence_by_id=cluster_coherence_by_id,
    )
    write_bundle(manifest, storyboard_dir)

    missing = sum(
        1
        for s in manifest["slides"]
        if isinstance(s, dict) and s.get("asset_status") == "missing"
    )
    print(f"Wrote {storyboard_dir / 'storyboard.json'}")
    print(f"Wrote {storyboard_dir / 'index.html'}")
    if args.print_summary:
        print()
        print(format_summary(manifest))
    if args.strict and missing:
        print(f"Strict mode: {missing} missing asset(s).", file=sys.stderr)
        return 1
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    path: Path = args.manifest
    data = json.loads(path.read_text(encoding="utf-8"))
    print(format_summary(data))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    result = export_storyboard_snapshot(
        args.manifest,
        export_root=args.export_root.resolve(),
        export_name=args.export_name,
    )
    print(json.dumps(
        {
            "status": "exported",
            "snapshot_dir": str(result["snapshot_dir"]),
            "zip_path": str(result["zip_path"]),
            "asset_count": len(result["asset_inventory"]),
        },
        indent=2,
    ))
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    manifest_path: Path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    export_result = export_storyboard_snapshot(
        manifest_path,
        export_root=args.export_root.resolve(),
        export_name=args.export_name,
    )
    run_id = str(manifest.get("run_id") or export_result["snapshot_name"]).strip()
    safe_leaf = _sanitize_segment(_slugify_filename(run_id))
    site_repo_url = str(args.site_repo_url or _discover_site_repo_url(manifest)).strip()
    if not site_repo_url:
        raise ValueError("site_repo_url is required for publish (pass --site-repo-url or keep it discoverable in source_payload)")

    if not os.environ.get(args.token_env_var, "").strip():
        raise RuntimeError(
            f"Storyboard publish requires {args.token_env_var} in the environment"
        )

    gamma_scripts = PROJECT_ROOT / "skills" / "gamma-api-mastery" / "scripts"
    if str(gamma_scripts) not in sys.path:
        sys.path.insert(0, str(gamma_scripts))
    from gamma_operations import _git_auth_env, _github_pages_base_url, _run_git_command  # noqa: PLC0415

    target_subdir = f"{_sanitize_segment(args.publish_subdir)}/{safe_leaf}"
    pages_url_base = _github_pages_base_url(site_repo_url)
    git_env = _git_auth_env(os.environ[args.token_env_var].strip())
    temp_repo = Path(tempfile.mkdtemp(prefix=f"storyboard-publish-{safe_leaf}-"))

    publish_result: dict[str, Any] = {
        "changed": False,
        "file_count": 0,
    }
    try:
        _run_git_command(
            ["git", "clone", "--depth", "1", "--branch", args.site_branch, site_repo_url, str(temp_repo)],
            display_args=["git", "clone", "--depth", "1", "--branch", args.site_branch, site_repo_url, "<tempdir>"],
            env=git_env,
        )
        _run_git_command(["git", "config", "user.name", "app-marcus-bot"], cwd=temp_repo)
        _run_git_command(
            ["git", "config", "user.email", "app-marcus-bot@users.noreply.github.com"],
            cwd=temp_repo,
        )
        publish_result = publish_snapshot_tree(
            export_result["snapshot_dir"],
            repo_root=temp_repo,
            target_subdir=target_subdir,
        )
        if publish_result["changed"]:
            _run_git_command(["git", "add", target_subdir], cwd=temp_repo, env=git_env)
            status = _run_git_command(["git", "status", "--short", target_subdir], cwd=temp_repo, env=git_env)
            if status.strip():
                commit_message = f"Publish storyboard snapshot for {run_id}"
                _run_git_command(
                    ["git", "commit", "-m", commit_message],
                    cwd=temp_repo,
                    env=git_env,
                )
                _run_git_command(
                    ["git", "push", site_repo_url, f"HEAD:{args.site_branch}"],
                    cwd=temp_repo,
                    env=git_env,
                    display_args=["git", "push", site_repo_url, f"HEAD:{args.site_branch}"],
                )
        publish_url = f"{pages_url_base.rstrip('/')}/{target_subdir}/index.html"
    finally:
        if temp_repo.exists():
            shutil.rmtree(temp_repo, ignore_errors=True)

    receipt = {
        "status": "published",
        "run_id": run_id,
        "snapshot_dir": str(export_result["snapshot_dir"]),
        "zip_path": str(export_result["zip_path"]),
        "publish_url": publish_url,
        "target_subdir": target_subdir,
        "site_repo_url": site_repo_url,
        "changed": publish_result["changed"],
        "file_count": publish_result["file_count"],
    }
    receipt_path = args.export_root.resolve() / f"{export_result['snapshot_name']}-publish-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path)
    print(json.dumps(receipt, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gary dispatch → static storyboard bundle")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Build storyboard.json + index.html")
    gen.add_argument("--payload", type=Path, required=True, help="Gary dispatch JSON/YAML")
    gen.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory under which storyboard/ will be created",
    )
    gen.add_argument(
        "--asset-base",
        type=Path,
        default=None,
        help="Resolve relative file_path against this directory (default: payload parent)",
    )
    gen.add_argument(
        "--print-summary",
        action="store_true",
        help="After write, print manifest-derived summary to stdout",
    )
    gen.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any slide has asset_status missing",
    )
    gen.add_argument(
        "--segment-manifest",
        type=Path,
        default=None,
        help=(
            "Irene Pass 2 segment manifest YAML "
            "(segments[].gary_slide_id + narration_text) to attach script per slide"
        ),
    )
    gen.add_argument(
        "--related-assets",
        type=Path,
        default=None,
        help=(
            "Optional JSON/YAML file with related_assets rows to append after slides "
            "(each entry requires label + link)."
        ),
    )
    gen.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Production run ID for traceability in manifest metadata and logs.",
    )
    gen.add_argument(
        "--cluster-coherence-report",
        type=Path,
        default=None,
        help=(
            "Optional JSON/YAML cluster coherence report to decorate Storyboard A "
            "cluster headers and per-slide review state."
        ),
    )
    gen.add_argument(
        "--pass2-envelope",
        type=Path,
        default=None,
        help=(
            "Optional pass2-envelope JSON/YAML to enrich Storyboard B with "
            "runtime-plan and script-policy metadata (default: payload sibling pass2-envelope.json)."
        ),
    )
    gen.set_defaults(func=cmd_generate)

    summ = sub.add_parser("summarize", help="Print summary from existing storyboard.json")
    summ.add_argument("--manifest", type=Path, required=True)
    summ.set_defaults(func=cmd_summarize)

    exp = sub.add_parser("export", help="Build self-contained share snapshot + zip")
    exp.add_argument("--manifest", type=Path, required=True)
    exp.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORTS_DIR,
        help="Repo-root exports directory for the self-contained snapshot and zip",
    )
    exp.add_argument(
        "--export-name",
        type=str,
        default=None,
        help="Optional folder/zip stem override (default: storyboard-<RUN_ID>)",
    )
    exp.set_defaults(func=cmd_export)

    pub = sub.add_parser("publish", help="Export and publish storyboard snapshot to GitHub Pages")
    pub.add_argument("--manifest", type=Path, required=True)
    pub.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORTS_DIR,
        help="Repo-root exports directory for the self-contained snapshot and zip",
    )
    pub.add_argument(
        "--export-name",
        type=str,
        default=None,
        help="Optional folder/zip stem override (default: storyboard-<RUN_ID>)",
    )
    pub.add_argument(
        "--site-repo-url",
        type=str,
        default=None,
        help="Optional explicit Pages repository URL; otherwise discovered from source_payload when available",
    )
    pub.add_argument(
        "--publish-subdir",
        type=str,
        default=DEFAULT_PUBLISH_SUBDIR,
        help="Base subtree inside the Pages repo (default: assets/storyboards)",
    )
    pub.add_argument(
        "--site-branch",
        type=str,
        default="main",
        help="Pages repository branch to update",
    )
    pub.add_argument(
        "--token-env-var",
        type=str,
        default="GITHUB_PAGES_TOKEN",
        help="Environment variable containing the fine-grained GitHub Pages token",
    )
    pub.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
