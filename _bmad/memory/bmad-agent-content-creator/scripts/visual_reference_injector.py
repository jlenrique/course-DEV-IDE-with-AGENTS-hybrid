# /// script
# requires-python = ">=3.10"
# ///
"""Visual reference injection for Irene Pass 2 narration.

Story 13.2: Selects visual elements from perception artifacts and produces
structured metadata that Irene uses to weave explicit visual references
into narration scripts.  References are natural language, deictic, and
traceable to specific perception entries.

Design:
- ``load_visual_reference_params`` reads config from narration-script-parameters.yaml.
- ``extract_visual_references`` picks the best visual elements from a
  perception artifact for a given slide.
- ``validate_reference_count`` checks ±tolerance compliance.
- ``build_visual_reference_metadata`` structures references for the
  narration template and downstream manifest (Story 13.3).
- ``validate_references_traceable`` confirms every reference maps back to
  a perception artifact element.
- ``inject_visual_references`` is the per-slide orchestrator.
- ``inject_all_slides`` is the top-level entry point for a full deck.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_REFERENCES_PER_SLIDE = 2
DEFAULT_TOLERANCE = 1

PROJECT_ROOT = Path(__file__).resolve().parents[3]
NARRATION_PARAMS_PATH = PROJECT_ROOT / "state" / "config" / "narration-script-parameters.yaml"


def load_visual_reference_params(
    config_path: Path | None = None,
) -> dict[str, int]:
    """Load visual reference parameters from narration-script-parameters.yaml.

    Returns dict with 'target' and 'tolerance' keys.
    """
    path = config_path or NARRATION_PARAMS_PATH

    if not path.is_file():
        logger.warning("Config not found at %s — using defaults", path)
        return {
            "target": DEFAULT_REFERENCES_PER_SLIDE,
            "tolerance": DEFAULT_TOLERANCE,
        }

    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not available — using defaults")
        return {
            "target": DEFAULT_REFERENCES_PER_SLIDE,
            "tolerance": DEFAULT_TOLERANCE,
        }

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    visual = (data or {}).get("visual_narration", {})

    target = visual.get("visual_references_per_slide", DEFAULT_REFERENCES_PER_SLIDE)
    tolerance = visual.get("visual_references_tolerance", DEFAULT_TOLERANCE)

    if not isinstance(target, int) or target < 0:
        target = DEFAULT_REFERENCES_PER_SLIDE
    if not isinstance(tolerance, int) or tolerance < 0:
        tolerance = DEFAULT_TOLERANCE

    return {"target": target, "tolerance": tolerance}


def extract_visual_references(
    perception_artifact: dict[str, Any],
    count: int,
) -> list[dict[str, Any]]:
    """Select the best visual elements from a perception artifact.

    Prioritizes elements with richer descriptions and identifiable positions.
    Returns up to ``count`` elements (may return fewer if perception has less).
    """
    elements = perception_artifact.get("visual_elements", [])
    if not elements:
        return []

    # Score elements: prefer those with description, type, and position
    scored: list[tuple[float, int, dict]] = []
    for i, elem in enumerate(elements):
        if not isinstance(elem, dict):
            continue
        score = 0.0
        desc = elem.get("description", "")
        if desc and len(desc) > 5:
            score += 3.0
        elif desc:
            score += 1.0
        if elem.get("type"):
            score += 1.0
        if elem.get("position"):
            score += 2.0  # spatial context is valuable for deictic references
        scored.append((score, i, elem))

    # Sort by score descending, then by original order for stability
    scored.sort(key=lambda x: (-x[0], x[1]))

    selected = [elem for _, _, elem in scored[:count]]
    return selected


def validate_reference_count(
    references: list[dict[str, Any]],
    target: int,
    tolerance: int,
) -> dict[str, Any]:
    """Check that reference count is within ±tolerance of target.

    Returns:
      - valid: bool
      - actual: int
      - target: int
      - tolerance: int
      - deviation: int (signed)
    """
    actual = len(references)
    deviation = actual - target

    return {
        "valid": abs(deviation) <= tolerance,
        "actual": actual,
        "target": target,
        "tolerance": tolerance,
        "deviation": deviation,
    }


def build_visual_reference_metadata(
    references: list[dict[str, Any]],
    perception_source: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build structured metadata for each visual reference.

    Each entry contains:
      - element: what is referenced (e.g., "comparison timeline")
      - element_type: the visual element type from perception
      - location_on_slide: spatial description (e.g., "left panel")
      - perception_source_slide_id: links back to perception artifact
      - perception_element_index: index in perception's visual_elements[]
    """
    elements = perception_source.get("visual_elements", [])
    slide_id = perception_source.get("slide_id", "")

    metadata: list[dict[str, Any]] = []
    for ref in references:
        # Find the index of this element in the perception's visual_elements
        elem_index = -1
        for i, elem in enumerate(elements):
            if elem is ref:
                elem_index = i
                break

        metadata.append({
            "element": ref.get("description", "unknown element"),
            "element_type": ref.get("type", "unknown"),
            "location_on_slide": ref.get("position", ""),
            "perception_source_slide_id": slide_id,
            "perception_element_index": elem_index,
        })

    return metadata


def validate_references_traceable(
    reference_metadata: list[dict[str, Any]],
    perception_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Confirm every reference maps to a specific perception artifact element.

    Returns:
      - traceable: bool (all references have valid sources)
      - untraceable: list of reference descriptions that couldn't be linked
    """
    # Build lookup: slide_id -> set of element descriptions
    perception_elements: dict[str, set[str]] = {}
    for artifact in perception_artifacts:
        if not isinstance(artifact, dict):
            continue
        sid = artifact.get("slide_id", "")
        elements = artifact.get("visual_elements", [])
        descs = set()
        for elem in elements:
            if isinstance(elem, dict):
                desc = elem.get("description", "")
                if desc:
                    descs.add(desc)
        perception_elements[sid] = descs

    untraceable: list[str] = []
    for ref in reference_metadata:
        source_sid = ref.get("perception_source_slide_id", "")
        element_desc = ref.get("element", "")

        available = perception_elements.get(source_sid, set())
        if element_desc not in available:
            untraceable.append(element_desc)

    return {
        "traceable": len(untraceable) == 0,
        "untraceable": untraceable,
    }


def inject_visual_references(
    perception_artifact: dict[str, Any],
    *,
    target: int = DEFAULT_REFERENCES_PER_SLIDE,
    tolerance: int = DEFAULT_TOLERANCE,
) -> dict[str, Any]:
    """Per-slide orchestrator: extract references, validate count, build metadata.

    Returns:
      - slide_id: str
      - card_number: int | None
      - visual_references: list of reference metadata dicts
      - count_validation: count compliance result
    """
    refs = extract_visual_references(perception_artifact, target)
    count_result = validate_reference_count(refs, target, tolerance)
    metadata = build_visual_reference_metadata(refs, perception_artifact)

    return {
        "slide_id": perception_artifact.get("slide_id", ""),
        "card_number": perception_artifact.get("card_number"),
        "visual_references": metadata,
        "count_validation": count_result,
    }


def inject_all_slides(
    perception_artifacts: list[dict[str, Any]],
    *,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """Top-level entry point: inject visual references for all slides.

    Loads parameters from config, processes each slide, and reports compliance.

    Returns:
      - status: "compliant" | "non_compliant"
      - params: loaded parameters
      - slides: list of per-slide results
      - compliance_summary: overall count compliance stats
    """
    params = load_visual_reference_params(config_path)
    target = params["target"]
    tolerance = params["tolerance"]

    slides: list[dict[str, Any]] = []
    compliant_count = 0
    non_compliant_count = 0

    for artifact in perception_artifacts:
        if not isinstance(artifact, dict):
            continue
        result = inject_visual_references(
            artifact, target=target, tolerance=tolerance,
        )
        slides.append(result)
        if result["count_validation"]["valid"]:
            compliant_count += 1
        else:
            non_compliant_count += 1

    traceability = validate_references_traceable(
        [ref for s in slides for ref in s["visual_references"]],
        perception_artifacts,
    )

    status = "compliant" if non_compliant_count == 0 and traceability["traceable"] else "non_compliant"

    return {
        "status": status,
        "params": params,
        "slides": slides,
        "compliance_summary": {
            "total_slides": len(slides),
            "compliant": compliant_count,
            "non_compliant": non_compliant_count,
        },
        "traceability": traceability,
    }
