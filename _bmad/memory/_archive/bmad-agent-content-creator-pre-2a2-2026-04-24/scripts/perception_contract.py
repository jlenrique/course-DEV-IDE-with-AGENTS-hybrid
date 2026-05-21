# /// script
# requires-python = ">=3.10"
# ///
"""Mandatory perception contract for Irene Pass 2.

Story 13.1: Enforces that perception artifacts exist (or are generated
inline) before any narration is written.  Complements the post-Pass-2
validator in ``skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py``
(Story 11.3) which confirms completeness *after* Pass 2 finishes.

Timing: Run at the START of Pass 2, before narration writing begins.

Design:
- ``validate_perception_presence`` checks the context envelope.
- ``generate_inline_perception`` invokes the image sensory bridge per slide.
- ``retry_low_confidence`` retries LOW-confidence slides once.
- ``build_perception_confirmation`` formats the structured confirmation.
- ``check_escalation_needed`` identifies slides needing Marcus intervention.
- ``enforce_perception_contract`` is the top-level orchestrator that
  validates, generates if needed, retries, and returns the final state.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from collections.abc import Callable
from typing import Any

# Type alias for perceive-like functions
PerceiveFn = Callable[..., dict[str, Any]]

logger = logging.getLogger(__name__)

# Gate used for Irene Pass 2 slide perception
IRENE_PERCEPTION_GATE = "G4"
REQUESTING_AGENT = "irene"
MAX_LOW_CONFIDENCE_RETRIES = 1


def validate_perception_presence(envelope: dict[str, Any]) -> dict[str, Any]:
    """Check whether perception_artifacts exist in the context envelope.

    Returns a result dict with:
      - present: bool
      - gary_slide_output: list (from envelope, may be empty)
      - perception_artifacts: list (from envelope, may be empty)
      - errors: list[str]
    """
    errors: list[str] = []

    gary_slide_output = envelope.get("gary_slide_output")
    perception_artifacts = envelope.get("perception_artifacts")

    if gary_slide_output is None:
        errors.append("Missing required field: gary_slide_output")
    elif not isinstance(gary_slide_output, list):
        errors.append("gary_slide_output must be an array")
        gary_slide_output = []

    if perception_artifacts is not None and not isinstance(perception_artifacts, list):
        errors.append("perception_artifacts must be an array if provided")
        perception_artifacts = []

    present = (
        isinstance(perception_artifacts, list)
        and len(perception_artifacts) > 0
    )

    return {
        "present": present,
        "gary_slide_output": gary_slide_output or [],
        "perception_artifacts": perception_artifacts or [],
        "errors": errors,
    }


def generate_inline_perception(
    gary_slide_output: list[dict[str, Any]],
    *,
    run_id: str | None = None,
    gate: str = IRENE_PERCEPTION_GATE,
    perceive_fn: PerceiveFn | None = None,
) -> list[dict[str, Any]]:
    """Invoke the image sensory bridge on each slide PNG in gary_slide_output.

    In production, the LLM does actual vision analysis and passes extracted
    data through ``perceive_fn``.  For automated/test use, callers can inject
    a ``perceive_fn`` that returns pre-built perception results.

    If ``perceive_fn`` is None, imports ``perceive`` from bridge_utils.

    Returns a list of perception artifacts (one per slide).
    """
    if perceive_fn is None:
        from skills.sensory_bridges.scripts.bridge_utils import perceive
        perceive_fn = perceive

    artifacts: list[dict[str, Any]] = []

    for slide in gary_slide_output:
        if not isinstance(slide, dict):
            continue

        file_path = slide.get("file_path", "")
        slide_id = slide.get("slide_id", "")
        card_number = slide.get("card_number")

        if not file_path:
            logger.warning(
                "Slide %s has no file_path — skipping perception",
                slide_id or card_number or "unknown",
            )
            continue

        try:
            result = perceive_fn(
                artifact_path=file_path,
                modality="image",
                gate=gate,
                requesting_agent=REQUESTING_AGENT,
                purpose=f"Pass 2 perception for slide {card_number or slide_id}",
                run_id=run_id,
            )
        except Exception as exc:
            logger.error(
                "Perception failed for slide %s: %s",
                slide_id or card_number or "unknown",
                exc,
            )
            result = {
                "confidence": "LOW",
                "confidence_rationale": f"Bridge error: {type(exc).__name__}: {exc}",
                "modality": "image",
                "artifact_path": str(file_path),
                "schema_version": "1.0",
                "perception_timestamp": "",
                "extracted_text": "",
                "layout_description": "",
                "visual_elements": [],
                "slide_title": "",
                "text_blocks": [],
            }

        result["slide_id"] = slide_id
        result["card_number"] = card_number
        result["source_image_path"] = str(file_path)
        artifacts.append(result)

    return artifacts


def retry_low_confidence(
    slide: dict[str, Any],
    perception_result: dict[str, Any],
    *,
    run_id: str | None = None,
    gate: str = IRENE_PERCEPTION_GATE,
    perceive_fn: PerceiveFn | None = None,
) -> dict[str, Any]:
    """Retry perception once for a LOW-confidence slide.

    Returns the new perception result (which may still be LOW).
    """
    if perceive_fn is None:
        from skills.sensory_bridges.scripts.bridge_utils import perceive
        perceive_fn = perceive

    file_path = slide.get("file_path", "")
    slide_id = slide.get("slide_id", "")
    card_number = slide.get("card_number")

    try:
        result = perceive_fn(
            artifact_path=file_path,
            modality="image",
            gate=gate,
            requesting_agent=REQUESTING_AGENT,
            purpose=f"Retry perception for slide {card_number or slide_id} (LOW confidence)",
            run_id=run_id,
            use_cache=False,  # bypass cache on retry
        )
    except Exception as exc:
        logger.error("Retry perception failed for slide %s: %s", slide_id or card_number, exc)
        return perception_result  # return original on failure

    result["slide_id"] = slide_id
    result["card_number"] = card_number
    result["source_image_path"] = str(file_path)
    result["retry_of"] = perception_result.get("perception_timestamp", "")
    return result


def build_perception_confirmation(
    card_number: int | str | None,
    perception_result: dict[str, Any],
) -> dict[str, str]:
    """Build a structured perception confirmation for logging.

    Returns the confirmation dict matching the universal perception protocol format.
    """
    confidence = perception_result.get("confidence", "LOW")
    layout = perception_result.get("layout_description", "")
    title = perception_result.get("slide_title", "")
    n_elements = len(perception_result.get("visual_elements", []))
    visual_complexity = perception_result.get("visual_complexity_summary", "")

    summary_parts = []
    if title:
        summary_parts.append(f"titled '{title}'")
    if layout:
        summary_parts.append(layout)
    if n_elements:
        summary_parts.append(f"{n_elements} visual element(s)")
    if visual_complexity:
        summary_parts.append(visual_complexity)

    summary = "; ".join(summary_parts) if summary_parts else "no details extracted"

    action = "escalating" if confidence == "LOW" else "proceeding"

    return {
        "artifact": str(perception_result.get("artifact_path", "")),
        "modality": "image",
        "confidence": confidence,
        "summary": f"Slide {card_number} shows {summary}. Confidence: {confidence}.",
        "gate": IRENE_PERCEPTION_GATE,
        "action": action,
    }


def check_escalation_needed(
    perception_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Identify slides with persistent LOW confidence needing Marcus escalation.

    Returns:
      - needs_escalation: bool
      - low_confidence_slides: list of slide identifiers still at LOW
      - escalation_payload: dict suitable for Marcus decision request
    """
    low_slides: list[dict[str, Any]] = []

    for result in perception_results:
        if result.get("confidence") == "LOW":
            low_slides.append({
                "slide_id": result.get("slide_id", ""),
                "card_number": result.get("card_number"),
                "confidence_rationale": result.get("confidence_rationale", ""),
                "artifact_path": result.get("artifact_path", ""),
                "was_retried": bool(result.get("retry_of")),
            })

    needs_escalation = len(low_slides) > 0

    escalation_payload = {}
    if needs_escalation:
        escalation_payload = {
            "escalation_type": "perception_low_confidence",
            "requesting_agent": REQUESTING_AGENT,
            "gate": IRENE_PERCEPTION_GATE,
            "low_confidence_slides": low_slides,
            "slide_count": len(low_slides),
            "recommended_action": "Marcus decides: proceed with caveated narration or escalate to user",
        }

    return {
        "needs_escalation": needs_escalation,
        "low_confidence_slides": low_slides,
        "escalation_payload": escalation_payload,
    }


def enforce_perception_contract(
    envelope: dict[str, Any],
    *,
    run_id: str | None = None,
    perceive_fn: PerceiveFn | None = None,
) -> dict[str, Any]:
    """Top-level orchestrator: validate, generate if needed, retry, report.

    This is the single entry point called at the start of Irene Pass 2.

    Returns:
      - status: "ready" | "escalation_needed" | "error"
      - perception_artifacts: list (final, usable for narration)
      - confirmations: list of per-slide confirmation dicts
      - escalation: escalation info if any slides need Marcus
      - errors: list[str]
    """
    # Step 1: Validate presence
    validation = validate_perception_presence(envelope)
    if validation["errors"]:
        return {
            "status": "error",
            "perception_artifacts": [],
            "confirmations": [],
            "escalation": {"needs_escalation": False, "low_confidence_slides": [], "escalation_payload": {}},
            "errors": validation["errors"],
        }

    gary_slide_output = validation["gary_slide_output"]

    # Step 2: Generate inline if absent
    if validation["present"]:
        artifacts = deepcopy(validation["perception_artifacts"])
        missing_slides = _find_missing_slides(artifacts, gary_slide_output)
        if missing_slides:
            artifacts.extend(
                generate_inline_perception(
                    missing_slides,
                    run_id=run_id,
                    perceive_fn=perceive_fn,
                )
            )
    else:
        artifacts = generate_inline_perception(
            gary_slide_output,
            run_id=run_id,
            perceive_fn=perceive_fn,
        )

    # Step 3: Retry LOW-confidence slides (one retry each)
    for i, artifact in enumerate(artifacts):
        if artifact.get("confidence") == "LOW":
            matching_slide = _find_matching_slide(artifact, gary_slide_output)
            if matching_slide is not None:
                retried = retry_low_confidence(
                    matching_slide,
                    artifact,
                    run_id=run_id,
                    perceive_fn=perceive_fn,
                )
                artifacts[i] = retried

    # Step 3b: Coverage must be complete before narration can begin.
    missing_after_generation = _find_missing_slides(artifacts, gary_slide_output)
    if missing_after_generation:
        missing_labels = [
            str(slide.get("slide_id") or slide.get("card_number") or "unknown")
            for slide in missing_after_generation
            if isinstance(slide, dict)
        ]
        return {
            "status": "error",
            "perception_artifacts": artifacts,
            "confirmations": [],
            "escalation": {"needs_escalation": False, "low_confidence_slides": [], "escalation_payload": {}},
            "errors": [
                "perception_artifacts missing required slide coverage for: "
                + ", ".join(missing_labels)
            ],
        }

    # Step 4: Build confirmations
    confirmations = []
    for artifact in artifacts:
        card_number = artifact.get("card_number")
        confirmation = build_perception_confirmation(card_number, artifact)
        confirmations.append(confirmation)

    # Step 5: Check escalation
    escalation = check_escalation_needed(artifacts)

    status = "escalation_needed" if escalation["needs_escalation"] else "ready"

    return {
        "status": status,
        "perception_artifacts": artifacts,
        "confirmations": confirmations,
        "escalation": escalation,
        "errors": [],
    }


def _find_matching_slide(
    artifact: dict[str, Any],
    gary_slide_output: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Find the gary_slide_output entry matching a perception artifact."""
    slide_id = artifact.get("slide_id", "")
    card_number = artifact.get("card_number")

    for slide in gary_slide_output:
        if not isinstance(slide, dict):
            continue
        if slide_id and slide.get("slide_id") == slide_id:
            return slide
        if card_number is not None and slide.get("card_number") == card_number:
            return slide

    return None


def _find_matching_artifact(
    slide: dict[str, Any],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Find the perception artifact matching a Gary slide row."""
    slide_id = slide.get("slide_id", "")
    card_number = slide.get("card_number")

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if slide_id and artifact.get("slide_id") == slide_id:
            return artifact
        if card_number is not None and artifact.get("card_number") == card_number:
            return artifact

    return None


def _find_missing_slides(
    artifacts: list[dict[str, Any]],
    gary_slide_output: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return Gary slides that do not yet have a matching perception artifact."""
    missing: list[dict[str, Any]] = []
    for slide in gary_slide_output:
        if not isinstance(slide, dict):
            continue
        if _find_matching_artifact(slide, artifacts) is None:
            missing.append(slide)
    return missing


def build_motion_perception_confirmation(
    segment: dict[str, Any],
    perception_result: dict[str, Any],
) -> dict[str, str]:
    """Build a structured confirmation for a motion asset perception event."""
    slide_label = (
        segment.get("gary_card_number")
        or segment.get("gary_slide_id")
        or segment.get("id")
        or "unknown"
    )
    motion_type = str(segment.get("motion_type") or "motion").strip()
    confidence = perception_result.get("confidence", "LOW")
    summary = (
        perception_result.get("temporal_event_density_summary")
        or perception_result.get("layout_description")
        or perception_result.get("slide_title")
        or "no details extracted"
    )
    return {
        "artifact": str(perception_result.get("artifact_path", "")),
        "modality": "video",
        "confidence": confidence,
        "summary": (
            f"Slide {slide_label} has motion ({motion_type}): I see {summary}. "
            f"Confidence: {confidence}."
        ),
        "gate": IRENE_PERCEPTION_GATE,
        "action": "escalating" if confidence == "LOW" else "proceeding",
    }


def enforce_motion_perception_contract(
    segments: list[dict[str, Any]],
    *,
    run_id: str | None = None,
    repo_root: str | Path | None = None,
    perceive_motion_fn: PerceiveFn | None = None,
) -> dict[str, Any]:
    """Fail closed unless approved motion assets exist and are perceived."""
    if perceive_motion_fn is None:
        from skills.sensory_bridges.scripts.bridge_utils import perceive

        perceive_motion_fn = perceive

    artifacts: list[dict[str, Any]] = []
    confirmations: list[dict[str, str]] = []
    errors: list[str] = []

    for segment in segments:
        if not isinstance(segment, dict):
            continue
        motion_type = str(segment.get("motion_type") or "static").strip().lower() or "static"
        if motion_type == "static":
            continue

        seg_id = segment.get("id", "")
        motion_asset_path = str(segment.get("motion_asset_path") or "").strip()
        motion_status = str(segment.get("motion_status") or "").strip().lower()
        if motion_status != "approved":
            errors.append(
                f"Segment {seg_id}: motion_type '{motion_type}' requires motion_status 'approved' before Irene Pass 2"
            )
            continue
        if not motion_asset_path:
            errors.append(
                f"Segment {seg_id}: motion_type '{motion_type}' requires motion_asset_path before Irene Pass 2"
            )
            continue
        resolved_motion_path = Path(motion_asset_path)
        if not resolved_motion_path.is_absolute():
            base = Path(repo_root) if repo_root is not None else Path.cwd()
            resolved_motion_path = (base / resolved_motion_path).resolve()
        if not resolved_motion_path.is_file():
            errors.append(
                f"Segment {seg_id}: approved motion asset is not readable on disk: {motion_asset_path}"
            )
            continue

        try:
            result = perceive_motion_fn(
                artifact_path=str(resolved_motion_path),
                modality="video",
                gate=IRENE_PERCEPTION_GATE,
                requesting_agent=REQUESTING_AGENT,
                purpose=f"Pass 2 motion perception for segment {seg_id}",
                run_id=run_id,
            )
        except Exception as exc:
            logger.error("Motion perception failed for segment %s: %s", seg_id or "<unknown>", exc)
            result = {
                "confidence": "LOW",
                "confidence_rationale": f"Bridge error: {type(exc).__name__}: {exc}",
                "modality": "video",
                "artifact_path": str(resolved_motion_path),
                "schema_version": "1.0",
                "perception_timestamp": "",
                "extracted_text": "",
                "layout_description": "",
                "visual_elements": [],
                "slide_title": "",
                "text_blocks": [],
            }
            errors.append(
                f"Segment {seg_id}: motion perception failed: {type(exc).__name__}: {exc}"
            )
        result["segment_id"] = seg_id
        result["slide_id"] = segment.get("gary_slide_id")
        result["card_number"] = segment.get("gary_card_number")
        result["motion_type"] = motion_type
        result["source_motion_path"] = str(resolved_motion_path)
        artifacts.append(result)
        confirmations.append(build_motion_perception_confirmation(segment, result))

    if errors:
        return {
            "status": "error",
            "motion_perception_artifacts": artifacts,
            "confirmations": confirmations,
            "escalation": {"needs_escalation": False, "low_confidence_slides": [], "escalation_payload": {}},
            "errors": errors,
        }

    escalation = check_escalation_needed(artifacts)
    status = "escalation_needed" if escalation["needs_escalation"] else "ready"
    return {
        "status": status,
        "motion_perception_artifacts": artifacts,
        "confirmations": confirmations,
        "escalation": escalation,
        "errors": [],
    }
