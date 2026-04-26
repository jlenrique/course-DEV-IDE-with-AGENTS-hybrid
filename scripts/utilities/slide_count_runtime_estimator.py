#!/usr/bin/env python3
"""
Slide Count and Runtime Estimator for Marcus Precursor Step

Profile-aware estimator that derives expansion parameters from the active
experience profile's ``cluster_expansion`` block.

Operator inputs: ``parent_slide_count`` + ``target_total_runtime_minutes``.
Everything else is system-derived from the profile.

Story 20c-15: replaces the legacy hardcoded estimator with profile-aware
feasibility triangle validation.
"""

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from scripts.utilities.file_helpers import project_root as default_project_root

EXPERIENCE_PROFILES_PATH = default_project_root() / "state" / "config" / "experience-profiles.yaml"
NARRATION_PARAMS_PATH = default_project_root() / "state" / "config" / "narration-script-parameters.yaml"

# Feasibility thresholds
MIN_AVG_SLIDE_SECONDS = 8
MAX_AVG_SLIDE_SECONDS = 90
MIN_PARENT_SLIDE_COUNT = 1
MIN_TARGET_RUNTIME_MINUTES = 0.5
OVERSHOOT_WARN_THRESHOLD = 0.05  # 5%


class EstimatorError(ValueError):
    """Invalid estimator input or missing profile data."""


def _load_profile(
    experience_profile: str,
    profiles_path: Path = EXPERIENCE_PROFILES_PATH,
) -> dict[str, Any]:
    """Load and validate a named experience profile with cluster_expansion."""
    if yaml is None:
        raise EstimatorError("pyyaml is required")
    if not profiles_path.is_file():
        raise EstimatorError(f"Experience profiles file not found: {profiles_path}")
    try:
        raw = yaml.safe_load(profiles_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise EstimatorError(f"Invalid YAML in {profiles_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise EstimatorError(f"Expected mapping at root of {profiles_path}")

    profiles = raw.get("profiles")
    if not isinstance(profiles, dict):
        raise EstimatorError(f"Missing 'profiles' mapping in {profiles_path}")

    normalized = experience_profile.strip().lower()
    profile = profiles.get(normalized)
    if not isinstance(profile, dict):
        raise EstimatorError(f"Unknown experience profile: {experience_profile!r}")

    cluster_expansion = profile.get("cluster_expansion")
    if not isinstance(cluster_expansion, dict):
        raise EstimatorError(
            f"Experience profile {experience_profile!r} missing required 'cluster_expansion' block"
        )

    # Validate required keys
    required_keys = [
        "avg_interstitials_per_cluster",
        "interstitial_range",
        "singleton_ratio",
        "cluster_head_word_range",
        "interstitial_word_range",
    ]
    for key in required_keys:
        if key not in cluster_expansion:
            raise EstimatorError(
                f"cluster_expansion missing required key '{key}' in profile {experience_profile!r}"
            )

    return profile


def _load_target_wpm(narration_params_path: Path = NARRATION_PARAMS_PATH) -> float:
    """Load target_wpm from narration-script-parameters.yaml."""
    if yaml is None:
        return 150.0  # fallback
    if not narration_params_path.is_file():
        return 150.0  # fallback
    try:
        raw = yaml.safe_load(narration_params_path.read_text(encoding="utf-8"))
        return float(raw.get("narration_density", {}).get("target_wpm", 150))
    except Exception:
        return 150.0


def _analyze_content(extracted_md_path: str) -> dict[str, Any]:
    """Analyze extracted.md for word count and section structure."""
    with open(extracted_md_path, encoding="utf-8") as f:
        content = f.read()

    words = re.findall(r"\b\w+\b", content)
    word_count = len(words)

    slide_headers = re.findall(r"^Slide \d+:", content, re.MULTILINE)
    major_sections = re.findall(r"^## .*$", content, re.MULTILINE)
    part_headers = re.findall(r"^Part \d+:", content, re.MULTILINE)

    section_count = len(slide_headers) + len(major_sections) + len(part_headers)

    return {
        "word_count": word_count,
        "slide_headers_found": len(slide_headers),
        "major_sections_found": len(major_sections),
        "part_headers_found": len(part_headers),
        "total_sections": section_count,
    }


def _run_feasibility_triangle(
    parent_slide_count: int,
    target_runtime_minutes: float,
    estimated_total_slides: float,
    avg_slide_seconds: float,
    target_runtime_seconds: float,
) -> dict[str, Any]:
    """Run the 5-condition feasibility triangle.

    Returns dict with 'result' (PASS/WARN/BLOCK) and 'details' list.
    """
    details: list[dict[str, Any]] = []
    has_block = False
    has_warn = False

    # Condition 1: Runtime fit
    total_slide_time = estimated_total_slides * avg_slide_seconds
    overshoot = (total_slide_time - target_runtime_seconds) / target_runtime_seconds if target_runtime_seconds > 0 else 0
    if overshoot > OVERSHOOT_WARN_THRESHOLD:
        details.append({
            "condition": 1,
            "name": "runtime_fit",
            "result": "BLOCK",
            "message": f"Estimated slide time {total_slide_time:.0f}s exceeds target {target_runtime_seconds:.0f}s by {overshoot * 100:.1f}% (>{OVERSHOOT_WARN_THRESHOLD * 100}%)",
        })
        has_block = True
    elif overshoot > 0:
        details.append({
            "condition": 1,
            "name": "runtime_fit",
            "result": "WARN",
            "message": f"Estimated slide time {total_slide_time:.0f}s exceeds target {target_runtime_seconds:.0f}s by {overshoot * 100:.1f}% (within {OVERSHOOT_WARN_THRESHOLD * 100}% tolerance)",
        })
        has_warn = True
    else:
        details.append({
            "condition": 1,
            "name": "runtime_fit",
            "result": "PASS",
            "message": f"Estimated slide time {total_slide_time:.0f}s within target {target_runtime_seconds:.0f}s",
        })

    # Condition 2: Minimum slide duration
    if avg_slide_seconds < MIN_AVG_SLIDE_SECONDS:
        details.append({
            "condition": 2,
            "name": "min_slide_duration",
            "result": "BLOCK",
            "message": f"Average slide duration {avg_slide_seconds:.1f}s below minimum {MIN_AVG_SLIDE_SECONDS}s",
        })
        has_block = True
    else:
        details.append({
            "condition": 2,
            "name": "min_slide_duration",
            "result": "PASS",
            "message": f"Average slide duration {avg_slide_seconds:.1f}s >= {MIN_AVG_SLIDE_SECONDS}s",
        })

    # Condition 3: Maximum slide duration
    if avg_slide_seconds > MAX_AVG_SLIDE_SECONDS:
        details.append({
            "condition": 3,
            "name": "max_slide_duration",
            "result": "BLOCK",
            "message": f"Average slide duration {avg_slide_seconds:.1f}s exceeds maximum {MAX_AVG_SLIDE_SECONDS}s",
        })
        has_block = True
    else:
        details.append({
            "condition": 3,
            "name": "max_slide_duration",
            "result": "PASS",
            "message": f"Average slide duration {avg_slide_seconds:.1f}s <= {MAX_AVG_SLIDE_SECONDS}s",
        })

    # Condition 4: Minimum parent count
    if parent_slide_count < MIN_PARENT_SLIDE_COUNT:
        details.append({
            "condition": 4,
            "name": "min_parent_count",
            "result": "BLOCK",
            "message": f"Parent slide count {parent_slide_count} below minimum {MIN_PARENT_SLIDE_COUNT}",
        })
        has_block = True
    else:
        details.append({
            "condition": 4,
            "name": "min_parent_count",
            "result": "PASS",
            "message": f"Parent slide count {parent_slide_count} >= {MIN_PARENT_SLIDE_COUNT}",
        })

    # Condition 5: Minimum runtime
    if target_runtime_minutes < MIN_TARGET_RUNTIME_MINUTES:
        details.append({
            "condition": 5,
            "name": "min_runtime",
            "result": "BLOCK",
            "message": f"Target runtime {target_runtime_minutes} min below minimum {MIN_TARGET_RUNTIME_MINUTES} min",
        })
        has_block = True
    else:
        details.append({
            "condition": 5,
            "name": "min_runtime",
            "result": "PASS",
            "message": f"Target runtime {target_runtime_minutes} min >= {MIN_TARGET_RUNTIME_MINUTES} min",
        })

    if has_block:
        result = "BLOCK"
    elif has_warn:
        result = "WARN"
    else:
        result = "PASS"

    return {"result": result, "details": details}


def estimate_and_validate(
    extracted_md_path: str,
    parent_slide_count: int,
    target_runtime_minutes: float,
    experience_profile: str,
    *,
    profiles_path: Path = EXPERIENCE_PROFILES_PATH,
    narration_params_path: Path = NARRATION_PARAMS_PATH,
) -> dict[str, Any]:
    """Profile-aware slide count estimation and feasibility validation.

    Args:
        extracted_md_path: Path to the extracted.md file.
        parent_slide_count: Operator-provided head (parent) slide count.
        target_runtime_minutes: Operator-provided target total runtime.
        experience_profile: Active experience profile name (e.g. 'visual-led').
        profiles_path: Path to experience-profiles.yaml (for testing).
        narration_params_path: Path to narration-script-parameters.yaml (for testing).

    Returns:
        Dict with parent_slide_count, estimated_total_slides, target_total_runtime_minutes,
        avg_slide_seconds, feasibility, feasibility_details, profile_used, word_budgets,
        analysis, recommendation.
    """
    profile = _load_profile(experience_profile, profiles_path)
    cluster_expansion = profile["cluster_expansion"]

    avg_interstitials = float(cluster_expansion["avg_interstitials_per_cluster"])
    singleton_ratio = float(cluster_expansion["singleton_ratio"])
    head_word_range = cluster_expansion["cluster_head_word_range"]
    interstitial_word_range = cluster_expansion["interstitial_word_range"]

    # Advisory for recommendation
    estimator_advisory = cluster_expansion.get("estimator_advisory", {})
    parents_per_minute = float(estimator_advisory.get("parents_per_minute", 1.5))

    # Derive estimated total slides
    estimated_total_slides = parent_slide_count * (1 + avg_interstitials * (1 - singleton_ratio))

    # Derive avg_slide_seconds
    target_runtime_seconds = target_runtime_minutes * 60
    avg_slide_seconds = target_runtime_seconds / estimated_total_slides if estimated_total_slides > 0 else 0

    # Run feasibility triangle
    feasibility = _run_feasibility_triangle(
        parent_slide_count=parent_slide_count,
        target_runtime_minutes=target_runtime_minutes,
        estimated_total_slides=estimated_total_slides,
        avg_slide_seconds=avg_slide_seconds,
        target_runtime_seconds=target_runtime_seconds,
    )

    # Content analysis
    analysis = _analyze_content(extracted_md_path)

    # System recommendation: derive parent count from content
    target_wpm = _load_target_wpm(narration_params_path)
    word_count = analysis["word_count"]
    if target_wpm > 0 and parents_per_minute > 0:
        words_per_parent = target_wpm * (60 / parents_per_minute)
        recommended_parents = max(1, round(word_count / words_per_parent)) if words_per_parent > 0 else 1
    else:
        recommended_parents = max(1, analysis["total_sections"])

    return {
        "parent_slide_count": parent_slide_count,
        "estimated_total_slides": round(estimated_total_slides, 1),
        "target_total_runtime_minutes": target_runtime_minutes,
        "avg_slide_seconds": round(avg_slide_seconds, 1),
        "feasibility": feasibility["result"],
        "feasibility_details": feasibility["details"],
        "profile_used": experience_profile,
        "word_budgets": {
            "cluster_head_word_range": list(head_word_range),
            "interstitial_word_range": list(interstitial_word_range),
        },
        "analysis": analysis,
        "recommendation": {
            "recommended_parent_slide_count": recommended_parents,
            "parents_per_minute": parents_per_minute,
            "target_wpm": target_wpm,
        },
    }


def analyze_content_for_slides(
    extracted_md_path: str,
    max_slides: int | None = None,
) -> dict[str, Any]:
    """Legacy backward-compatible wrapper.

    Calls the content analysis directly and returns the legacy result shape.
    Existing callers that don't pass an experience_profile will still work.
    """
    analysis = _analyze_content(extracted_md_path)
    word_count = analysis["word_count"]
    section_count = analysis["total_sections"]

    recommended_slides = max(section_count, 1)
    if max_slides is not None:
        recommended_slides = min(recommended_slides, max_slides)

    narration_minutes = word_count / 150
    slide_time_minutes = recommended_slides * 0.75
    total_runtime_minutes = round(narration_minutes + slide_time_minutes, 1)
    if total_runtime_minutes < 1:
        total_runtime_minutes = 1.0

    return {
        "recommended_slide_count": recommended_slides,
        "estimated_total_runtime_minutes": total_runtime_minutes,
        "word_count": word_count,
        "average_slide_runtime_seconds": 45,
        "runtime_variability_scale": 0.5,
        "recommended_mode_proportions": {
            "creative": 0.4,
            "literal_text": 0.3,
            "literal_visual": 0.3,
        },
        "analysis": analysis,
    }


def main():
    """CLI interface for slide count and runtime estimation."""
    import argparse

    parser = argparse.ArgumentParser(description="Profile-aware slide count and runtime estimator")
    parser.add_argument("extracted_md_path", help="Path to extracted.md")
    parser.add_argument("--parent-slides", type=int, default=None, help="Operator parent slide count")
    parser.add_argument("--target-runtime", type=float, default=None, help="Target total runtime in minutes")
    parser.add_argument("--experience-profile", type=str, default=None, help="Experience profile name")
    parser.add_argument("--max-slides", type=int, default=None, help="(Legacy) Operator ceiling for slide count")
    args = parser.parse_args()

    if args.parent_slides is not None and args.target_runtime is not None and args.experience_profile is not None:
        result = estimate_and_validate(
            args.extracted_md_path,
            parent_slide_count=args.parent_slides,
            target_runtime_minutes=args.target_runtime,
            experience_profile=args.experience_profile,
        )
        print("Profile-Aware Slide Count and Runtime Estimation:")
        print(f"  Profile: {result['profile_used']}")
        print(f"  Parent slides (operator): {result['parent_slide_count']}")
        print(f"  Estimated total slides (derived): {result['estimated_total_slides']}")
        print(f"  Target runtime: {result['target_total_runtime_minutes']} min")
        print(f"  Avg slide seconds (derived): {result['avg_slide_seconds']}s")
        print(f"  Feasibility: {result['feasibility']}")
        for detail in result["feasibility_details"]:
            print(f"    [{detail['result']}] {detail['name']}: {detail['message']}")
        print(f"  Word budgets: {result['word_budgets']}")
        print(f"  System recommendation: {result['recommendation']['recommended_parent_slide_count']} parents")
    else:
        result = analyze_content_for_slides(args.extracted_md_path, max_slides=args.max_slides)
        print("Slide Count and Runtime Recommendations:")
        print(f"  Recommended slides: {result['recommended_slide_count']}")
        print(f"  Estimated total runtime: {result['estimated_total_runtime_minutes']} minutes")
        print(f"  Word count: {result['word_count']}")
        print(f"  Average slide runtime: {result['average_slide_runtime_seconds']} seconds")
        print(f"  Runtime variability scale: {result['runtime_variability_scale']}")


if __name__ == "__main__":
    main()
