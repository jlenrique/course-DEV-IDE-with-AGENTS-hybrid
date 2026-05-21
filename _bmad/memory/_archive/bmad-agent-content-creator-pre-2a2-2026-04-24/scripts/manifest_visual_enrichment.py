# /// script
# requires-python = ">=3.10"
# ///
"""Segment manifest visual reference enrichment (Story 13.3).

Merges visual reference metadata from ``visual_reference_injector`` (Story
13.2) into segment manifest entries, adding ``narration_cue`` for each
reference and providing manifest-level traceability validation.

Downstream consumers:
- Vera G4 uses ``visual_references`` to validate narration-to-visual alignment.
- Quinn-R flags references pointing to non-existent perception elements.
- Compositor includes visual reference cues in the Descript Assembly Guide.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

MOTION_TYPES = {"static", "video", "animation"}
MOTION_SOURCES = {"kling", "manual"}
MOTION_STATUSES = {"pending", "generated", "imported", "approved"}


def enrich_segment_with_visual_references(
    segment: dict[str, Any],
    slide_injection_result: dict[str, Any],
    *,
    narration_cues: list[str] | None = None,
) -> dict[str, Any]:
    """Merge visual reference metadata into a single manifest segment.

    Args:
        segment: A segment dict from the manifest (must have at least 'id').
        slide_injection_result: Output from ``inject_visual_references`` for
            the corresponding slide (Story 13.2).
        narration_cues: Optional list of exact narration phrases, one per
            visual reference.  If not provided, cues default to empty strings
            (to be populated by Irene during narration writing).

    Returns:
        The segment dict with ``visual_references`` added.
    """
    injection_refs = slide_injection_result.get("visual_references", [])
    cues = narration_cues or [""] * len(injection_refs)

    visual_references: list[dict[str, str]] = []
    for i, ref in enumerate(injection_refs):
        visual_references.append({
            "element": ref.get("element", ""),
            "location_on_slide": ref.get("location_on_slide", ""),
            "narration_cue": cues[i] if i < len(cues) else "",
            "perception_source": ref.get("perception_source_slide_id", ""),
        })

    segment["visual_references"] = visual_references
    return segment


def enrich_manifest(
    segments: list[dict[str, Any]],
    injection_results: list[dict[str, Any]],
    *,
    narration_cues_by_segment: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    """Enrich all segments in a manifest with visual references.

    Matches segments to injection results by ``gary_slide_id`` when present.
    Falls back to segment index order only when slide identity is absent.

    Args:
        segments: List of manifest segment dicts.
        injection_results: List of per-slide results from
            ``inject_visual_references`` or ``inject_all_slides``.
        narration_cues_by_segment: Optional mapping of segment id →
            list of narration cue phrases.

    Returns:
        The segments list with ``visual_references`` added to each.
    """
    cues_map = narration_cues_by_segment or {}

    # Build lookup: slide_id → injection result
    injection_by_slide: dict[str, dict[str, Any]] = {}
    for result in injection_results:
        sid = result.get("slide_id", "")
        if sid:
            injection_by_slide[sid] = result

    for i, segment in enumerate(segments):
        seg_id = segment.get("id", "")
        gary_slide_id = segment.get("gary_slide_id", "")

        # Match by explicit slide identity first. Only fall back to positional
        # matching when the segment does not declare a slide identity at all.
        injection = injection_by_slide.get(gary_slide_id) if gary_slide_id else None
        if injection is None and not gary_slide_id and i < len(injection_results):
            injection = injection_results[i]

        if injection is not None:
            cues = cues_map.get(seg_id)
            enrich_segment_with_visual_references(
                segment, injection, narration_cues=cues,
            )
        else:
            segment["visual_references"] = []

    return segments


def apply_motion_plan_to_segments(
    segments: list[dict[str, Any]],
    motion_plan: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Hydrate Epic 14 motion fields into manifest segments.

    The Gate 2M source of truth is a run-scoped motion plan keyed by
    ``slide_id``. Manifest segments are enriched later during Irene Pass 2,
    when they finally exist as concrete YAML rows.
    """
    motion_enabled = bool(motion_plan.get("motion_enabled", False)) if isinstance(motion_plan, dict) else False
    plan_rows = motion_plan.get("slides", []) if isinstance(motion_plan, dict) else []
    by_slide_id: dict[str, dict[str, Any]] = {}
    for row in plan_rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            by_slide_id[slide_id] = row

    if motion_enabled and not by_slide_id:
        raise ValueError("motion_enabled runs require motion_plan slide coverage before manifest hydration")

    missing_slide_ids: list[str] = []
    if motion_enabled:
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            slide_id = str(segment.get("gary_slide_id") or "").strip()
            if not slide_id or slide_id not in by_slide_id:
                missing_slide_ids.append(slide_id or "<missing>")
        if missing_slide_ids:
            raise ValueError(
                "motion_plan is missing Gate 2M assignments for slide_ids: "
                + ", ".join(sorted(set(missing_slide_ids)))
            )

    for segment in segments:
        if not isinstance(segment, dict):
            continue
        slide_id = str(segment.get("gary_slide_id") or "").strip()
        assignment = by_slide_id.get(slide_id)

        if assignment is None:
            segment["motion_type"] = "static"
            segment["motion_asset_path"] = None
            segment["motion_source"] = None
            segment["motion_duration_seconds"] = None
            segment["motion_brief"] = None
            segment["motion_status"] = None
            continue

        motion_type = str(assignment.get("motion_type") or "static").strip().lower() or "static"
        segment["motion_type"] = motion_type
        segment["motion_asset_path"] = assignment.get("motion_asset_path")
        segment["motion_source"] = assignment.get("motion_source")
        segment["motion_duration_seconds"] = assignment.get("motion_duration_seconds")
        segment["motion_brief"] = assignment.get("motion_brief")
        segment["motion_status"] = assignment.get("motion_status")

    return segments


def validate_manifest_motion_fields(
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate Epic 14 motion fields with additive defaults.

    Static segments remain backward compatible. Non-static segments fail closed
    if they do not yet point to a concrete motion asset before Irene/compositor
    consume the manifest.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for segment in segments:
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("id", "")
        motion_type = str(segment.get("motion_type") or "static").strip().lower() or "static"
        asset_path = segment.get("motion_asset_path")
        motion_source = segment.get("motion_source")
        motion_status = segment.get("motion_status")
        duration = segment.get("motion_duration_seconds")

        if motion_type not in MOTION_TYPES:
            errors.append(
                f"Segment {seg_id}: motion_type '{motion_type}' must be one of {sorted(MOTION_TYPES)}"
            )
            continue

        if motion_type == "static":
            continue

        if not isinstance(asset_path, str) or not asset_path.strip():
            errors.append(
                f"Segment {seg_id}: motion_type '{motion_type}' requires motion_asset_path before Irene Pass 2"
            )
        if motion_source not in MOTION_SOURCES:
            errors.append(
                f"Segment {seg_id}: motion_type '{motion_type}' requires motion_source in {sorted(MOTION_SOURCES)}"
            )
        if motion_status not in MOTION_STATUSES:
            errors.append(
                f"Segment {seg_id}: motion_type '{motion_type}' requires motion_status in {sorted(MOTION_STATUSES)}"
            )
        if duration is not None and (not isinstance(duration, (int, float)) or float(duration) <= 0):
            errors.append(
                f"Segment {seg_id}: motion_duration_seconds must be a positive number when present"
            )
        if duration is None:
            warnings.append(
                f"Segment {seg_id}: motion_type '{motion_type}' has no motion_duration_seconds yet"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_manifest_visual_references(
    segments: list[dict[str, Any]],
    perception_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate that all visual references in the manifest are traceable.

    Checks:
    - Each reference's ``perception_source`` exists in perception_artifacts
    - Each reference's ``element`` exists in that perception's visual_elements
    - Each reference has a non-empty ``narration_cue`` (warns if empty)
    - Each non-empty ``narration_cue`` appears in the segment's narration_text

    Returns:
      - valid: bool
      - errors: list of error strings (traceability failures)
      - warnings: list of warning strings (missing narration_cues)
    """
    # Build lookup: slide_id → set of element descriptions
    perception_elements: dict[str, set[str]] = {}
    perception_slide_ids: set[str] = set()
    for artifact in perception_artifacts:
        if not isinstance(artifact, dict):
            continue
        sid = artifact.get("slide_id", "")
        perception_slide_ids.add(sid)
        elements = artifact.get("visual_elements", [])
        descs = set()
        for elem in elements:
            if isinstance(elem, dict):
                desc = elem.get("description", "")
                if desc:
                    descs.add(desc)
        perception_elements[sid] = descs

    errors: list[str] = []
    warnings: list[str] = []

    for segment in segments:
        seg_id = segment.get("id", "")
        refs = segment.get("visual_references", [])
        narration_text = str(segment.get("narration_text") or "")

        for ref in refs:
            if not isinstance(ref, dict):
                continue

            source = ref.get("perception_source", "")
            element = ref.get("element", "")
            cue = ref.get("narration_cue", "")

            # Check perception source exists
            if source and source not in perception_slide_ids:
                errors.append(
                    f"Segment {seg_id}: perception_source '{source}' not found in perception artifacts"
                )
            elif source and element:
                available = perception_elements.get(source, set())
                if element not in available:
                    errors.append(
                        f"Segment {seg_id}: element '{element}' not found in perception for slide '{source}'"
                    )

            # Warn on missing narration_cue
            if not cue:
                warnings.append(
                    f"Segment {seg_id}: visual reference to '{element}' has no narration_cue"
                )
            elif cue not in narration_text:
                errors.append(
                    f"Segment {seg_id}: narration_cue '{cue}' not found in narration_text"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_visual_cue_coherence(
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Irene self-check: verify visual_cue text aligns with visual_references.

    For each segment that has both a ``visual_cue`` field and a
    ``visual_references`` list, checks that the visual_cue description is
    substantively reflected in at least one visual_references element
    description.  This catches drift where Irene writes a visual_cue that
    does not correspond to any perception-grounded visual reference.

    Returns:
      - valid: bool
      - errors: list of error strings (hard coherence failures)
      - warnings: list of warning strings (soft mismatches)
    """
    errors: list[str] = []
    warnings: list[str] = []

    for segment in segments:
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("id", "")
        visual_cue = str(segment.get("visual_cue") or "").strip()
        refs = segment.get("visual_references", [])

        if not visual_cue or not isinstance(refs, list) or not refs:
            continue

        # Check if any visual_references element description overlaps with
        # the visual_cue text (case-insensitive substring match).
        cue_lower = visual_cue.lower()
        matched = False
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            element = str(ref.get("element") or "").strip().lower()
            if element and element in cue_lower:
                matched = True
                break
            if element and cue_lower in element:
                matched = True
                break

        if not matched:
            warnings.append(
                f"Segment {seg_id}: visual_cue '{visual_cue}' does not match any "
                f"visual_references element description — review for coherence"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
