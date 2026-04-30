"""
Cluster template library loader/validator for Story 20c-1.

This module intentionally provides deterministic schema validation only.
Selection/scoring behavior is deferred to Story 20c-2.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

DEFAULT_TEMPLATE_PATH = Path("skills/bmad-agent-content-creator/references/cluster-templates.yaml")
REQUIRED_TEMPLATE_IDS = {
    "deep-dive",
    "contrast-pair",
    "evidence-build",
    "quick-punch",
    "cognitive-reset",
    "data-walkthrough",
    "narrative-pivot",
    "zoom-and-return",
    "framework-expose",
    "emotional-arc",
}
VALID_INTERSTITIAL_TYPES = {"reveal", "emphasis-shift", "bridge-text", "simplification", "pace-reset"}
VALID_CLUSTER_POSITIONS = {"establish", "develop", "tension", "resolve"}
VALID_DEVELOP_TYPES = {"deepen", "reframe", "exemplify"}
VALID_PACING_PROFILES = {"tight", "measured", "breathing-room"}
KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ClusterTemplateLibraryError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def load_cluster_template_library(path: Path = DEFAULT_TEMPLATE_PATH) -> Dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise ClusterTemplateLibraryError("config_missing", "pyyaml is required")
    if not path.is_file():
        raise ClusterTemplateLibraryError("config_missing", f"cluster template library not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ClusterTemplateLibraryError("config_missing", f"invalid cluster template library: {exc}") from exc
    if not isinstance(raw, dict):
        raise ClusterTemplateLibraryError("config_missing", "cluster template library must be a mapping")
    return raw


def _validate_word_range(name: str, payload: Any, errors: List[str]) -> None:
    if not isinstance(payload, list) or len(payload) != 2:
        errors.append(f"{name} must be [min,max]")
        return
    lo, hi = payload
    if not isinstance(lo, int) or not isinstance(hi, int):
        errors.append(f"{name} must contain integers")
        return
    if lo > hi:
        errors.append(f"{name} lower bound must be <= upper bound")


def _validate_template(template: Dict[str, Any], seen_ids: set[str], errors: List[str]) -> None:
    tid = str(template.get("template_id") or "").strip()
    if not tid:
        errors.append("template_id is required")
        return
    if not KEBAB_CASE_PATTERN.fullmatch(tid):
        errors.append(f"template_id must be kebab-case: {tid}")
    if tid in seen_ids:
        errors.append(f"template_id must be unique: {tid}")
    seen_ids.add(tid)

    for field in (
        "display_name",
        "purpose",
        "interstitial_sequence",
        "interstitial_count",
        "best_for",
        "avoid_when",
        "pacing_profile",
        "head_word_range",
        "interstitial_word_ranges",
    ):
        if field not in template:
            errors.append(f"{tid}.{field} is required")

    sequence = template.get("interstitial_sequence")
    if not isinstance(sequence, list) or not sequence:
        errors.append(f"{tid}.interstitial_sequence must be a non-empty list")
    else:
        if len(sequence) < 1 or len(sequence) > 3:
            errors.append(f"{tid}.interstitial_sequence length must be between 1 and 3")
        for idx, step in enumerate(sequence):
            if not isinstance(step, dict):
                errors.append(f"{tid}.interstitial_sequence[{idx}] must be an object")
                continue
            position = str(step.get("position") or "")
            interstitial_type = str(step.get("interstitial_type") or "")
            if position not in VALID_CLUSTER_POSITIONS:
                errors.append(f"{tid}.interstitial_sequence[{idx}].position invalid: {position}")
            if interstitial_type not in VALID_INTERSTITIAL_TYPES:
                errors.append(f"{tid}.interstitial_sequence[{idx}].interstitial_type invalid: {interstitial_type}")
            subtype = step.get("develop_subtype")
            if position == "develop":
                if subtype is not None and str(subtype) not in VALID_DEVELOP_TYPES:
                    errors.append(f"{tid}.interstitial_sequence[{idx}].develop_subtype invalid: {subtype}")
            elif subtype is not None:
                errors.append(f"{tid}.interstitial_sequence[{idx}].develop_subtype only allowed at develop position")

    interstitial_count = template.get("interstitial_count")
    if not isinstance(interstitial_count, int):
        errors.append(f"{tid}.interstitial_count must be an integer")
    elif isinstance(sequence, list) and len(sequence) != interstitial_count:
        errors.append(f"{tid}.interstitial_count must equal len(interstitial_sequence)")
    elif isinstance(interstitial_count, int) and (interstitial_count < 1 or interstitial_count > 3):
        errors.append(f"{tid}.interstitial_count must be between 1 and 3")

    pacing_profile = str(template.get("pacing_profile") or "")
    if pacing_profile not in VALID_PACING_PROFILES:
        errors.append(f"{tid}.pacing_profile invalid: {pacing_profile}")

    best_for = template.get("best_for")
    avoid_when = template.get("avoid_when")
    if isinstance(best_for, list) and len(best_for) == 0:
        errors.append(f"{tid}.best_for must not be empty")
    if isinstance(avoid_when, list) and len(avoid_when) == 0:
        errors.append(f"{tid}.avoid_when must not be empty")
    if not isinstance(best_for, list) or not all(isinstance(item, str) and item.strip() for item in best_for):
        errors.append(f"{tid}.best_for must be a list of non-empty strings")
    if not isinstance(avoid_when, list) or not all(isinstance(item, str) and item.strip() for item in avoid_when):
        errors.append(f"{tid}.avoid_when must be a list of non-empty strings")

    _validate_word_range(f"{tid}.head_word_range", template.get("head_word_range"), errors)
    per_position = template.get("interstitial_word_ranges")
    if not isinstance(per_position, dict):
        errors.append(f"{tid}.interstitial_word_ranges must be an object")
    else:
        for key, value in per_position.items():
            if key not in VALID_CLUSTER_POSITIONS:
                errors.append(f"{tid}.interstitial_word_ranges key invalid: {key}")
                continue
            _validate_word_range(f"{tid}.interstitial_word_ranges.{key}", value, errors)


def validate_cluster_template_library(data: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    if str(data.get("schema_version") or "") != "1.0":
        errors.append("schema_version must be '1.0'")
    templates = data.get("templates")
    if not isinstance(templates, list):
        errors.append("templates must be a list")
        return {"passed": False, "errors": errors}

    seen_ids: set[str] = set()
    for raw in templates:
        if not isinstance(raw, dict):
            errors.append("each template entry must be an object")
            continue
        _validate_template(raw, seen_ids, errors)

    missing_required = sorted(REQUIRED_TEMPLATE_IDS - seen_ids)
    if missing_required:
        errors.append(f"missing required template_id(s): {', '.join(missing_required)}")
    return {"passed": len(errors) == 0, "errors": errors}


def get_template_index(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    templates = data.get("templates")
    if not isinstance(templates, list):
        raise ClusterTemplateLibraryError("invalid_format", "templates must be a list")
    index: Dict[str, Dict[str, Any]] = {}
    for template in templates:
        if isinstance(template, dict) and template.get("template_id"):
            index[str(template["template_id"])] = template
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate cluster template library")
    parser.add_argument("--templates", type=Path, default=DEFAULT_TEMPLATE_PATH)
    args = parser.parse_args(argv)
    try:
        library = load_cluster_template_library(args.templates)
        result = validate_cluster_template_library(library)
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1
    except ClusterTemplateLibraryError as exc:
        print(json.dumps({"passed": False, "code": exc.code, "errors": [str(exc)]}, indent=2))
        return 1
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"passed": False, "code": "unexpected_error", "errors": [str(exc)]}, indent=2))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

