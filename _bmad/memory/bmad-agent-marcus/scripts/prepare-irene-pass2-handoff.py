# /// script
# requires-python = ">=3.10"
# ///
"""Prepare a fresh Irene Pass 2 handoff envelope at bundle root.

This helper is the canonical Marcus-side Prompt 8 preflight. It:
- validates authoritative inputs for Irene Pass 2
- archives stale bundle-root Pass 2 outputs on rerun
- preserves exact Motion Gate-approved asset bindings
- reports non-authoritative motion leftovers without using them as inputs
- writes a fresh ``pass2-envelope.json`` plus ``pass2-prep-receipt.json``
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cluster_template_planner import (
    build_cluster_template_plan,
    load_default_template_library,
    load_operator_template_overrides,
)
from scripts.utilities.run_constants import (
    RunConstantsError,
    parse_run_constants,
    resolve_experience_profile,
)


EXPECTED_PASS2_OUTPUTS = (
    "narration-script.md",
    "segment-manifest.yaml",
    "perception-artifacts.json",
)
STALE_PASS2_FILES = (
    "pass2-envelope.json",
    "pass2-prep-receipt.json",
    *EXPECTED_PASS2_OUTPUTS,
)
ARCHIVE_SUBDIR = Path("recovery") / "archive" / "pass2-reruns"
DEFAULT_ENVELOPE_FILENAME = "pass2-envelope.json"
DEFAULT_RECEIPT_FILENAME = "pass2-prep-receipt.json"
STATIC_MOTION_PATTERN = re.compile(r"slide[-_](\d{2})", re.IGNORECASE)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUN_CONSTANTS_FILENAME = "run-constants.yaml"
STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"
GARY_CLUSTER_FIELDS = (
    "cluster_id",
    "cluster_role",
    "cluster_position",
    "develop_type",
    "interstitial_type",
    "parent_slide_id",
    "narrative_arc",
    "cluster_interstitial_count",
    "selected_template_id",
)
RUNTIME_ROW_RE = re.compile(
    r"^\|\s*(?P<slide>\d+)\s*\|\s*(?P<target>\d+(?:\.\d+)?)\s*\|\s*(?P<cumulative>\d+:\d{2})\s*\|$"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp_slug(now: datetime) -> str:
    return now.strftime("%Y%m%dT%H%M%SZ")


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object at the top level")
    return data


def _load_yaml_object(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for motion_plan.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping at the top level")
    return data


def _bundle_input(bundle_dir: Path, filename: str) -> Path:
    return bundle_dir / filename


def _parse_runtime_budget_rows(irene_pass1_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in irene_pass1_path.read_text(encoding="utf-8").splitlines():
        match = RUNTIME_ROW_RE.match(raw_line.strip())
        if not match:
            continue
        slide = int(match.group("slide"))
        target_seconds = float(match.group("target"))
        cumulative_minutes, cumulative_seconds = match.group("cumulative").split(":")
        rows.append(
            {
                "card_number": slide,
                "target_runtime_seconds": target_seconds,
                "cumulative_runtime_seconds": int(cumulative_minutes) * 60 + int(cumulative_seconds),
            }
        )
    return rows


def _load_runtime_plan(bundle_dir: Path, irene_pass1_path: Path) -> dict[str, Any] | None:
    run_constants_path = _bundle_input(bundle_dir, RUN_CONSTANTS_FILENAME)
    if not run_constants_path.is_file() and not irene_pass1_path.is_file():
        return None

    run_constants: dict[str, Any] = {}
    if run_constants_path.is_file():
        run_constants = _load_yaml_object(run_constants_path)

    runtime_plan: dict[str, Any] = {
        "parent_slide_count": run_constants.get("parent_slide_count"),
        "target_total_runtime_minutes": run_constants.get("target_total_runtime_minutes"),
        "estimated_total_slides": run_constants.get("estimated_total_slides"),
        "avg_slide_seconds": run_constants.get("avg_slide_seconds"),
    }
    if irene_pass1_path.is_file():
        per_slide_targets = _parse_runtime_budget_rows(irene_pass1_path)
        if per_slide_targets:
            runtime_plan["per_slide_targets"] = per_slide_targets
    if not any(value not in (None, "", []) for value in runtime_plan.values()):
        return None
    return runtime_plan


def _load_experience_profile_payload(bundle_dir: Path) -> tuple[str | None, dict[str, Any] | None]:
    run_constants_path = _bundle_input(bundle_dir, RUN_CONSTANTS_FILENAME)
    if not run_constants_path.is_file():
        return None, None

    raw_run_constants = _load_yaml_object(run_constants_path)
    raw_profile = raw_run_constants.get("experience_profile")
    if raw_profile is None:
        return None, None

    validation_payload = {
        "run_id": "pass2-profile-validation",
        "lesson_slug": "pass2-profile-validation",
        "bundle_path": str(bundle_dir),
        "primary_source_file": "pass2-profile-validation.pdf",
        "optional_context_assets": [],
        "theme_selection": "pass2-profile-validation",
        "theme_paramset_key": "pass2-profile-validation",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        **raw_run_constants,
    }
    parsed_run_constants = parse_run_constants(validation_payload)
    if parsed_run_constants.experience_profile is None:
        return None, None

    normalized_profile = parsed_run_constants.experience_profile
    resolved = resolve_experience_profile(normalized_profile)
    return normalized_profile, resolved


def _load_voice_direction_defaults() -> dict[str, Any]:
    if yaml is None or not STYLE_GUIDE_PATH.is_file():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8")) or {}
    elevenlabs = data.get("tool_parameters", {}).get("elevenlabs", {})
    if not isinstance(elevenlabs, dict):
        return {}
    defaults = {}
    for key in (
        "stability",
        "similarity_boost",
        "style",
        "speed",
        "use_speaker_boost",
        "emotional_variability",
        "pace_variability",
    ):
        value = elevenlabs.get(key)
        if value not in (None, ""):
            defaults[key] = value
    return defaults


def _slug_from_bundle_name(bundle_dir: Path) -> str:
    match = re.match(r"(?P<slug>.+)-\d{8}(?:-.+)?$", bundle_dir.name)
    if match:
        return match.group("slug")
    return bundle_dir.name


def _dispatch_row_lookup(dispatch_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = dispatch_payload.get("gary_slide_output", [])
    if not isinstance(rows, list):
        return {}
    lookup: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            lookup[slide_id] = row
    return lookup


def _attach_selected_template_ids_to_rows(
    gary_slide_output: list[dict[str, Any]],
    cluster_template_plan: dict[str, Any],
) -> None:
    mapping_raw = cluster_template_plan.get("selected_template_ids_by_cluster")
    mapping: dict[str, str] = {}
    if isinstance(mapping_raw, dict):
        mapping = {
            str(cluster_id): str(template_id)
            for cluster_id, template_id in mapping_raw.items()
            if str(cluster_id).strip() and str(template_id).strip()
        }
    if not mapping:
        return
    for row in gary_slide_output:
        if not isinstance(row, dict):
            continue
        cluster_id = str(row.get("cluster_id") or "").strip()
        if not cluster_id:
            continue
        selected_template_id = mapping.get(cluster_id)
        if selected_template_id:
            row["selected_template_id"] = selected_template_id


def _hydrate_cluster_rows_from_template_plan(
    gary_slide_output: list[dict[str, Any]],
    cluster_template_plan: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    clusters = cluster_template_plan.get("clusters")
    if not isinstance(clusters, list):
        return warnings
    rows_by_cluster: dict[str, list[dict[str, Any]]] = {}
    for row in gary_slide_output:
        if not isinstance(row, dict):
            continue
        cluster_id = str(row.get("cluster_id") or "").strip()
        if not cluster_id:
            continue
        rows_by_cluster.setdefault(cluster_id, []).append(row)

    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        cluster_id = str(cluster.get("cluster_id") or "").strip()
        if not cluster_id:
            continue
        cluster_rows = rows_by_cluster.get(cluster_id, [])
        if not cluster_rows:
            continue
        cluster_rows.sort(key=lambda item: int(item.get("card_number") or 10_000))
        head_row = next(
            (
                row
                for row in cluster_rows
                if str(row.get("cluster_role") or "").strip().lower() == "head"
            ),
            None,
        )
        interstitial_rows = [
            row
            for row in cluster_rows
            if str(row.get("cluster_role") or "").strip().lower() == "interstitial"
        ]
        if head_row is None:
            warnings.append(f"{cluster_id}: missing head row; template hydration skipped")
            continue

        expected_sequence = (
            cluster.get("expected_interstitial_sequence")
            if isinstance(cluster.get("expected_interstitial_sequence"), list)
            else []
        )
        expected_count = cluster.get("expected_interstitial_count")
        if isinstance(expected_count, int) and not head_row.get("cluster_interstitial_count"):
            head_row["cluster_interstitial_count"] = expected_count
        elif isinstance(expected_count, int) and int(head_row.get("cluster_interstitial_count") or 0) != expected_count:
            warnings.append(
                f"{cluster_id}: head cluster_interstitial_count={head_row.get('cluster_interstitial_count')} "
                f"differs from template expected_interstitial_count={expected_count}"
            )

        head_slide_id = str(head_row.get("slide_id") or "").strip()
        for index, interstitial_row in enumerate(interstitial_rows):
            step = expected_sequence[index] if index < len(expected_sequence) and isinstance(expected_sequence[index], dict) else {}
            expected_position = str(step.get("position") or "").strip() or None
            expected_type = str(step.get("interstitial_type") or "").strip() or None
            expected_develop = str(step.get("develop_subtype") or "").strip() or None

            current_position = str(interstitial_row.get("cluster_position") or "").strip() or None
            current_type = str(interstitial_row.get("interstitial_type") or "").strip() or None
            current_develop = str(interstitial_row.get("develop_type") or "").strip() or None

            if expected_position and not current_position:
                interstitial_row["cluster_position"] = expected_position
            elif expected_position and current_position and current_position != expected_position:
                warnings.append(
                    f"{cluster_id}:{interstitial_row.get('slide_id')}: cluster_position={current_position} "
                    f"differs from template={expected_position}"
                )

            if expected_type and not current_type:
                interstitial_row["interstitial_type"] = expected_type
            elif expected_type and current_type and current_type != expected_type:
                warnings.append(
                    f"{cluster_id}:{interstitial_row.get('slide_id')}: interstitial_type={current_type} "
                    f"differs from template={expected_type}"
                )

            if expected_develop and not current_develop:
                interstitial_row["develop_type"] = expected_develop
            elif expected_develop and current_develop and current_develop != expected_develop:
                warnings.append(
                    f"{cluster_id}:{interstitial_row.get('slide_id')}: develop_type={current_develop} "
                    f"differs from template={expected_develop}"
                )

            if head_slide_id and not interstitial_row.get("parent_slide_id"):
                interstitial_row["parent_slide_id"] = head_slide_id

            if interstitial_row.get("double_dispatch_eligible") is None:
                interstitial_row["double_dispatch_eligible"] = False

    return warnings


def _validate_cluster_template_sequence_alignment(
    gary_slide_output: list[dict[str, Any]],
    cluster_template_plan: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    clusters = cluster_template_plan.get("clusters")
    if not isinstance(clusters, list):
        return errors

    rows_by_cluster: dict[str, list[dict[str, Any]]] = {}
    for row in gary_slide_output:
        if not isinstance(row, dict):
            continue
        cluster_id = str(row.get("cluster_id") or "").strip()
        if not cluster_id:
            continue
        rows_by_cluster.setdefault(cluster_id, []).append(row)

    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        cluster_id = str(cluster.get("cluster_id") or "").strip()
        if not cluster_id:
            continue
        rows = rows_by_cluster.get(cluster_id, [])
        if not rows:
            errors.append(f"{cluster_id}: no clustered rows found for template alignment")
            continue
        rows.sort(key=lambda item: int(item.get("card_number") or 10_000))
        selected_template_id = str(cluster.get("selected_template_id") or "").strip()
        if not selected_template_id:
            errors.append(f"{cluster_id}: selected_template_id missing in cluster_template_plan")
            continue

        for row in rows:
            row_selected = str(row.get("selected_template_id") or "").strip()
            if not row_selected:
                errors.append(f"{cluster_id}:{row.get('slide_id')}: selected_template_id missing on clustered row")
            elif row_selected != selected_template_id:
                errors.append(
                    f"{cluster_id}:{row.get('slide_id')}: selected_template_id={row_selected} "
                    f"mismatch plan={selected_template_id}"
                )

        interstitial_rows = [
            row
            for row in rows
            if str(row.get("cluster_role") or "").strip().lower() == "interstitial"
        ]
        expected_count = cluster.get("expected_interstitial_count")
        if isinstance(expected_count, int) and len(interstitial_rows) != expected_count:
            errors.append(
                f"{cluster_id}: interstitial count mismatch actual={len(interstitial_rows)} "
                f"expected={expected_count}"
            )

        expected_sequence = (
            cluster.get("expected_interstitial_sequence")
            if isinstance(cluster.get("expected_interstitial_sequence"), list)
            else []
        )
        if expected_sequence and len(expected_sequence) != len(interstitial_rows):
            errors.append(
                f"{cluster_id}: expected_interstitial_sequence length={len(expected_sequence)} "
                f"does not match actual interstitial rows={len(interstitial_rows)}"
            )

        for index, row in enumerate(interstitial_rows):
            if index >= len(expected_sequence):
                break
            step = expected_sequence[index]
            if not isinstance(step, dict):
                continue
            expected_position = str(step.get("position") or "").strip()
            expected_type = str(step.get("interstitial_type") or "").strip()
            expected_develop = str(step.get("develop_subtype") or "").strip()

            current_position = str(row.get("cluster_position") or "").strip()
            current_type = str(row.get("interstitial_type") or "").strip()
            current_develop = str(row.get("develop_type") or "").strip()

            if expected_position and current_position != expected_position:
                errors.append(
                    f"{cluster_id}:{row.get('slide_id')}: cluster_position={current_position or '<missing>'} "
                    f"mismatch expected={expected_position}"
                )
            if expected_type and current_type != expected_type:
                errors.append(
                    f"{cluster_id}:{row.get('slide_id')}: interstitial_type={current_type or '<missing>'} "
                    f"mismatch expected={expected_type}"
                )
            if expected_develop and current_develop != expected_develop:
                errors.append(
                    f"{cluster_id}:{row.get('slide_id')}: develop_type={current_develop or '<missing>'} "
                    f"mismatch expected={expected_develop}"
                )
    return errors


def _resolve_slide_asset_path(file_path: str, *, bundle_dir: Path) -> Path:
    """Resolve slide asset paths from either bundle-local or repo-root-relative inputs."""
    candidate = Path(file_path)
    if candidate.is_absolute():
        return candidate.resolve()

    bundle_relative = (bundle_dir / candidate).resolve()
    if bundle_relative.is_file():
        return bundle_relative

    repo_relative = (REPO_ROOT / candidate).resolve()
    if repo_relative.is_file():
        return repo_relative

    return bundle_relative


def _normalize_slide_row(
    row: dict[str, Any],
    *,
    dispatch_row: dict[str, Any] | None,
    bundle_dir: Path,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    slide_id = str(row.get("slide_id") or "").strip()
    if not slide_id:
        errors.append("authorized-storyboard.json contains a slide without slide_id")

    card_number = row.get("card_number")
    if not isinstance(card_number, int) or card_number <= 0:
        errors.append(f"{slide_id or '<missing-slide-id>'}: card_number must be a positive integer")

    file_path = str(row.get("file_path") or "").strip()
    if not file_path:
        errors.append(f"{slide_id or '<missing-slide-id>'}: file_path is required")
        resolved_file = None
    else:
        resolved_file = _resolve_slide_asset_path(file_path, bundle_dir=bundle_dir)
        if resolved_file.suffix.lower() != ".png":
            errors.append(f"{slide_id or '<missing-slide-id>'}: file_path must end with .png")
        if not resolved_file.is_file():
            errors.append(f"{slide_id or '<missing-slide-id>'}: file_path does not exist on disk")

    source_ref = str(row.get("source_ref") or "").strip()
    if not source_ref:
        errors.append(f"{slide_id or '<missing-slide-id>'}: source_ref is required")

    normalized = {
        "slide_id": slide_id,
        "card_number": card_number,
        "file_path": str(resolved_file) if resolved_file is not None else "",
        "source_ref": source_ref,
        "visual_description": str(
            row.get("visual_description")
            or (dispatch_row.get("visual_description") if dispatch_row else "")
            or ""
        ).strip(),
        "fidelity": str(
            row.get("fidelity")
            or (dispatch_row.get("fidelity") if dispatch_row else "")
            or ""
        ).strip()
        or None,
        "literal_visual_source": row.get("literal_visual_source")
        if row.get("literal_visual_source") is not None
        else (dispatch_row.get("literal_visual_source") if dispatch_row else None),
    }

    cluster_present = any(
        row.get(field) is not None or (dispatch_row.get(field) if dispatch_row else None) is not None
        for field in GARY_CLUSTER_FIELDS
    )
    if cluster_present:
        for field in GARY_CLUSTER_FIELDS:
            if row.get(field) is not None:
                normalized[field] = row.get(field)
            elif dispatch_row and field in dispatch_row:
                normalized[field] = dispatch_row.get(field)

    return normalized, errors


def _load_authorized_slide_output(
    authorized_storyboard: dict[str, Any],
    *,
    dispatch_payload: dict[str, Any],
    bundle_dir: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    rows = authorized_storyboard.get("authorized_slides", [])
    if not isinstance(rows, list) or not rows:
        return [], ["authorized-storyboard.json must contain a non-empty authorized_slides array"]

    dispatch_lookup = _dispatch_row_lookup(dispatch_payload)
    normalized_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_slide_ids: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            errors.append("authorized-storyboard.json authorized_slides entries must be objects")
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        dispatch_row = dispatch_lookup.get(slide_id, {})
        normalized, row_errors = _normalize_slide_row(
            row,
            dispatch_row=dispatch_row,
            bundle_dir=bundle_dir,
        )
        errors.extend(row_errors)
        if slide_id in seen_slide_ids:
            errors.append(f"{slide_id}: duplicate slide_id in authorized-storyboard.json")
        seen_slide_ids.add(slide_id)
        normalized_rows.append(normalized)

    normalized_rows.sort(key=lambda item: int(item["card_number"]))
    card_sequence = [int(item["card_number"]) for item in normalized_rows if isinstance(item.get("card_number"), int)]
    if card_sequence != list(range(1, len(card_sequence) + 1)):
        errors.append("authorized winner deck card_number sequence must be contiguous and start at 1 (1..N)")

    return normalized_rows, errors


def _motion_enabled(motion_plan: dict[str, Any]) -> bool:
    if bool(motion_plan.get("motion_enabled", False)):
        return True
    rows = motion_plan.get("slides", [])
    return isinstance(rows, list) and any(
        isinstance(row, dict) and str(row.get("motion_type") or "static").strip().lower() != "static"
        for row in rows
    )


def _validate_motion_plan(
    *,
    motion_plan: dict[str, Any] | None,
    authorized_rows: list[dict[str, Any]],
    bundle_dir: Path,
) -> tuple[bool, dict[str, str], list[str], list[str]]:
    if motion_plan is None:
        return False, {}, [], []

    rows = motion_plan.get("slides", [])
    if not isinstance(rows, list):
        return False, {}, [], ["motion_plan.yaml slides must be a list"]

    motion_enabled = _motion_enabled(motion_plan)
    rows_by_slide_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            rows_by_slide_id[slide_id] = row

    errors: list[str] = []
    warnings: list[str] = []
    approved_assets: dict[str, str] = {}

    if motion_enabled:
        missing_slide_ids = [
            str(row["slide_id"])
            for row in authorized_rows
            if str(row["slide_id"]) not in rows_by_slide_id
        ]
        if missing_slide_ids:
            errors.append(
                "motion_plan.yaml is missing authorized slide coverage for: "
                + ", ".join(missing_slide_ids)
            )

    for row in authorized_rows:
        slide_id = str(row["slide_id"])
        assignment = rows_by_slide_id.get(slide_id)
        if assignment is None:
            continue
        motion_type = str(assignment.get("motion_type") or "static").strip().lower() or "static"
        motion_status = str(assignment.get("motion_status") or "").strip().lower()
        motion_asset_path = str(assignment.get("motion_asset_path") or "").strip()

        if motion_type == "static":
            if motion_asset_path or motion_status:
                warnings.append(
                    f"{slide_id}: static row still carries motion metadata; it will not be used for handoff"
                )
            continue

        if motion_status != "approved":
            errors.append(
                f"{slide_id}: non-static motion rows must be approved before Irene Pass 2"
            )
            continue
        if not motion_asset_path:
            errors.append(
                f"{slide_id}: non-static motion rows must have motion_asset_path before Irene Pass 2"
            )
            continue
        resolved_asset = Path(motion_asset_path)
        if not resolved_asset.is_absolute():
            resolved_asset = (bundle_dir / resolved_asset).resolve()
        if not resolved_asset.is_file():
            errors.append(
                f"{slide_id}: approved motion asset is not readable on disk: {motion_asset_path}"
            )
            continue
        approved_assets[slide_id] = str(resolved_asset)

    return motion_enabled, approved_assets, warnings, errors


def _detect_non_authoritative_motion_leftovers(
    *,
    bundle_dir: Path,
    authorized_rows: list[dict[str, Any]],
    approved_assets: dict[str, str],
) -> list[str]:
    motion_dir = bundle_dir / "motion"
    if not motion_dir.is_dir():
        return []

    static_card_numbers = {
        int(row["card_number"])
        for row in authorized_rows
        if str(row["slide_id"]) not in approved_assets
    }
    approved_resolved = {Path(path).resolve() for path in approved_assets.values()}
    leftovers: set[str] = set()

    candidate_files = list(motion_dir.rglob("*"))
    candidate_files.extend(bundle_dir.glob("motion-generation-slide-*.json"))
    candidate_files.extend(bundle_dir.glob("motion-generation-slide-*.progress.json"))

    for path in candidate_files:
        if not path.is_file():
            continue
        if path.resolve() in approved_resolved:
            continue
        match = STATIC_MOTION_PATTERN.search(path.name)
        if not match:
            continue
        if int(match.group(1)) in static_card_numbers:
            leftovers.add(str(path.resolve()))

    return sorted(leftovers)


def _archive_stale_outputs(
    *,
    bundle_dir: Path,
    now: datetime,
) -> tuple[Path | None, list[dict[str, str]]]:
    stale_paths = [bundle_dir / name for name in STALE_PASS2_FILES if (bundle_dir / name).exists()]
    if not stale_paths:
        return None, []

    archive_dir = bundle_dir / ARCHIVE_SUBDIR / _timestamp_slug(now)
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived: list[dict[str, str]] = []
    for source in stale_paths:
        target = archive_dir / source.name
        shutil.move(str(source), str(target))
        archived.append({"source": str(source), "archived_to": str(target)})

    return archive_dir, archived


def prepare_irene_pass2_handoff(
    bundle_dir: str | Path,
    *,
    archive_stale: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    bundle = Path(bundle_dir).resolve()
    if not bundle.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle}")

    ts = now or _utc_now()
    errors: list[str] = []
    warnings: list[str] = []

    authorized_path = _bundle_input(bundle, "authorized-storyboard.json")
    dispatch_path = _bundle_input(bundle, "gary-dispatch-result.json")
    motion_plan_path = _bundle_input(bundle, "motion_plan.yaml")
    variant_selection_path = _bundle_input(bundle, "variant-selection.json")
    operator_directives_path = _bundle_input(bundle, "operator-directives.md")
    irene_pass1_path = _bundle_input(bundle, "irene-pass1.md")
    envelope_path = _bundle_input(bundle, DEFAULT_ENVELOPE_FILENAME)
    receipt_path = _bundle_input(bundle, DEFAULT_RECEIPT_FILENAME)

    if not authorized_path.is_file():
        raise FileNotFoundError(f"authorized-storyboard.json not found in bundle: {bundle}")
    if not dispatch_path.is_file():
        raise FileNotFoundError(f"gary-dispatch-result.json not found in bundle: {bundle}")

    authorized_storyboard = _load_json_object(authorized_path)
    dispatch_payload = _load_json_object(dispatch_path)
    motion_plan = _load_yaml_object(motion_plan_path) if motion_plan_path.is_file() else None

    gary_slide_output, slide_errors = _load_authorized_slide_output(
        authorized_storyboard,
        dispatch_payload=dispatch_payload,
        bundle_dir=bundle,
    )
    errors.extend(slide_errors)

    double_dispatch = bool(
        dispatch_payload.get("generation_mode") == "double-dispatch"
        or (
            isinstance(dispatch_payload.get("double_dispatch"), dict)
            and dispatch_payload["double_dispatch"].get("enabled")
        )
    )
    if double_dispatch and not variant_selection_path.is_file():
        errors.append("variant-selection.json is required for double-dispatch Pass 2 handoff")

    if not irene_pass1_path.is_file():
        errors.append("irene-pass1.md is required before Irene Pass 2 handoff")
    if not operator_directives_path.is_file():
        warnings.append("operator-directives.md is missing; handoff will proceed without an operator directives path")

    motion_enabled, approved_assets, motion_warnings, motion_errors = _validate_motion_plan(
        motion_plan=motion_plan,
        authorized_rows=gary_slide_output,
        bundle_dir=bundle,
    )
    warnings.extend(motion_warnings)
    errors.extend(motion_errors)

    experience_profile: str | None = None
    resolved_profile: dict[str, Any] | None = None
    try:
        experience_profile, resolved_profile = _load_experience_profile_payload(bundle)
    except RunConstantsError as exc:
        errors.append(str(exc))

    non_authoritative_motion_leftovers = _detect_non_authoritative_motion_leftovers(
        bundle_dir=bundle,
        authorized_rows=gary_slide_output,
        approved_assets=approved_assets,
    )
    if non_authoritative_motion_leftovers:
        warnings.append(
            "Detected non-authoritative motion leftovers for slide(s) currently treated as static"
        )

    if errors:
        receipt = {
            "status": "fail",
            "prepared_at_utc": ts.isoformat(),
            "bundle_path": str(bundle),
            "errors": errors,
            "warnings": warnings,
            "approved_motion_assets": approved_assets,
            "non_authoritative_motion_leftovers": non_authoritative_motion_leftovers,
        }
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt

    archive_dir = None
    archived_files: list[dict[str, str]] = []
    if archive_stale:
        archive_dir, archived_files = _archive_stale_outputs(bundle_dir=bundle, now=ts)

    expected_outputs = [str(bundle / name) for name in EXPECTED_PASS2_OUTPUTS]
    runtime_plan = (
        _load_runtime_plan(bundle, irene_pass1_path)
        if irene_pass1_path.is_file()
        else None
    )
    voice_direction_defaults = _load_voice_direction_defaults()
    envelope: dict[str, Any] = {
        "run_id": str(
            dispatch_payload.get("run_id")
            or authorized_storyboard.get("run_id")
            or f"pass2-{_timestamp_slug(ts)}"
        ).strip(),
        "lesson_slug": str(
            dispatch_payload.get("lesson_slug")
            or authorized_storyboard.get("lesson_slug")
            or _slug_from_bundle_name(bundle)
        ).strip(),
        "bundle_path": str(bundle),
        "handoff_status": "prepared-pending-irene-pass2",
        "double_dispatch": double_dispatch,
        "motion_enabled": motion_enabled,
        "authorized_storyboard_path": str(authorized_path),
        "motion_plan_path": str(motion_plan_path) if motion_plan_path.is_file() else None,
        "operator_directives_path": str(operator_directives_path) if operator_directives_path.is_file() else None,
        "irene_pass1_path": str(irene_pass1_path) if irene_pass1_path.is_file() else None,
        "variant_selection_path": str(variant_selection_path) if double_dispatch and variant_selection_path.is_file() else None,
        "approved_motion_assets": approved_assets,
        "expected_outputs": expected_outputs,
        "gary_slide_output": gary_slide_output,
        "perception_artifacts": [],
        "context_paths": {
            "motion_plan": str(motion_plan_path) if motion_plan_path.is_file() else None,
        },
    }
    if runtime_plan:
        envelope["runtime_plan"] = runtime_plan
    if voice_direction_defaults:
        envelope["voice_direction_defaults"] = voice_direction_defaults
    if experience_profile is not None and resolved_profile is not None:
        envelope["experience_profile"] = experience_profile
        envelope["narration_profile_controls"] = resolved_profile["narration_profile_controls"]
    try:
        template_library = load_default_template_library()
        overrides = load_operator_template_overrides(
            operator_directives_path if operator_directives_path.is_file() else None
        )
        cluster_template_plan = build_cluster_template_plan(
            gary_slide_output=gary_slide_output,
            template_library=template_library,
            operator_overrides=overrides,
        )
        if cluster_template_plan.get("clusters"):
            _attach_selected_template_ids_to_rows(gary_slide_output, cluster_template_plan)
            warnings.extend(
                _hydrate_cluster_rows_from_template_plan(
                    gary_slide_output,
                    cluster_template_plan,
                )
            )
            errors.extend(
                _validate_cluster_template_sequence_alignment(
                    gary_slide_output,
                    cluster_template_plan,
                )
            )
            envelope["cluster_template_plan"] = cluster_template_plan
    except Exception as exc:
        warnings.append(
            f"cluster template selection advisory unavailable: {type(exc).__name__}: {exc}"
        )
    if errors:
        receipt = {
            "status": "fail",
            "prepared_at_utc": ts.isoformat(),
            "bundle_path": str(bundle),
            "errors": errors,
            "warnings": warnings,
            "approved_motion_assets": approved_assets,
            "non_authoritative_motion_leftovers": non_authoritative_motion_leftovers,
        }
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt
    literal_visual_publish = dispatch_payload.get("literal_visual_publish")
    if isinstance(literal_visual_publish, dict):
        envelope["literal_visual_publish"] = literal_visual_publish
    if motion_enabled:
        envelope["motion_perception_artifacts"] = []

    envelope_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")

    receipt = {
        "status": "prepared",
        "prepared_at_utc": ts.isoformat(),
        "bundle_path": str(bundle),
        "envelope_path": str(envelope_path),
        "expected_outputs": expected_outputs,
        "archive_dir": str(archive_dir) if archive_dir is not None else None,
        "archived_stale_outputs": archived_files,
        "double_dispatch": double_dispatch,
        "motion_enabled": motion_enabled,
        "approved_motion_assets": approved_assets,
        "non_authoritative_motion_leftovers": non_authoritative_motion_leftovers,
        "warnings": warnings,
        "errors": [],
        "next_action": "delegate-irene-pass2",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a fresh Irene Pass 2 handoff envelope")
    parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Tracked source-bundle directory containing authorized-storyboard.json",
    )
    parser.add_argument(
        "--no-archive-stale",
        action="store_true",
        help="Do not archive existing bundle-root Pass 2 outputs before writing the new envelope",
    )
    args = parser.parse_args()

    try:
        result = prepare_irene_pass2_handoff(
            args.bundle,
            archive_stale=not args.no_archive_stale,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "prepared" else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"prepare_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
