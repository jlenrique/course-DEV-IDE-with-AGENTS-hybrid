#!/usr/bin/env python3
"""
Operator Polling Logic for Marcus Precursor Step

Profile-aware polling for parent_slide_count and target_total_runtime_minutes.
All other parameters (avg_slide_seconds, variability, mode proportions) are
now system-derived from the experience profile.

Story 20c-15: simplified from 8-option poll to 2-input poll with feasibility loop.
"""

import time
from typing import Any


def poll_operator_for_runtime_params(
    recommendations: dict[str, Any],
    timeout_seconds: int = 900,
) -> dict[str, Any] | None:
    """Poll operator for parent_slide_count and target_total_runtime_minutes.

    Pre-fills system recommendations from the estimator. Loops on BLOCK
    feasibility until the operator provides values that pass.

    Args:
        recommendations: Dict from estimate_and_validate() with recommended values.
        timeout_seconds: Auto-close timeout (default 15 min).

    Returns:
        Dict with confirmed parent_slide_count, target_total_runtime_minutes,
        plus all derived values from the estimator. None if timeout/cancel.
    """
    print("=== MARCUS PRECURSOR POLL: Parent Slide Count & Runtime ===")
    print("Reply hold: 3 minutes minimum")
    print(f"Auto-close: {timeout_seconds // 60} minutes from now")
    print()

    print("CONTENT ANALYSIS:")
    print(f"  Word count: {recommendations['analysis']['word_count']}")
    print(f"  Sections found: {recommendations['analysis']['total_sections']}")
    print(f"  Profile: {recommendations['profile_used']}")
    print()

    rec = recommendations.get("recommendation", {})
    print("SYSTEM RECOMMENDATIONS:")
    print(f"  Parent slide count: {rec.get('recommended_parent_slide_count', 'N/A')}")
    print(f"  Parents per minute (profile): {rec.get('parents_per_minute', 'N/A')}")
    print()

    print("CURRENT VALUES:")
    print(f"  Parent slides: {recommendations['parent_slide_count']}")
    print(f"  Target runtime: {recommendations['target_total_runtime_minutes']} min")
    print(f"  Estimated total slides (derived): {recommendations['estimated_total_slides']}")
    print(f"  Avg slide seconds (derived): {recommendations['avg_slide_seconds']}s")
    print(f"  Feasibility: {recommendations['feasibility']}")
    print(f"  Word budgets: {recommendations['word_budgets']}")
    print()

    print("OPTIONS:")
    print("1. Accept current values")
    print("2. Override parent slide count")
    print("3. Override target runtime")
    print("4. Override both")
    print("5. Cancel")
    print()

    start_time = time.time()
    hold_end = start_time + 180  # 3 min hold

    while True:
        current_time = time.time()
        if current_time - start_time > timeout_seconds:
            print("POLL AUTO-CLOSED: No response within timeout.")
            return None

        if current_time < hold_end:
            remaining_hold = int(hold_end - current_time)
            print(f"Reply hold active: {remaining_hold} seconds remaining")
            time.sleep(10)
            continue

        try:
            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                return {
                    "parent_slide_count": recommendations["parent_slide_count"],
                    "target_total_runtime_minutes": recommendations["target_total_runtime_minutes"],
                    "estimated_total_slides": recommendations["estimated_total_slides"],
                    "avg_slide_seconds": recommendations["avg_slide_seconds"],
                    "feasibility": recommendations["feasibility"],
                    "profile_used": recommendations["profile_used"],
                    "word_budgets": recommendations["word_budgets"],
                }
            elif choice == "2":
                count = int(input(f"New parent slide count (current: {recommendations['parent_slide_count']}): "))
                if count < 1 or count > 50:
                    print("Parent slide count must be 1-50. Try again.")
                    continue
                return {
                    "parent_slide_count": count,
                    "target_total_runtime_minutes": recommendations["target_total_runtime_minutes"],
                    "override": "parent_slide_count",
                }
            elif choice == "3":
                runtime = float(input(f"New target runtime minutes (current: {recommendations['target_total_runtime_minutes']}): "))
                if runtime < 0.5 or runtime > 60:
                    print("Target runtime must be 0.5-60 minutes. Try again.")
                    continue
                return {
                    "parent_slide_count": recommendations["parent_slide_count"],
                    "target_total_runtime_minutes": runtime,
                    "override": "target_total_runtime_minutes",
                }
            elif choice == "4":
                count = int(input("Parent slide count: "))
                runtime = float(input("Target runtime minutes: "))
                if count < 1 or count > 50:
                    print("Parent slide count must be 1-50. Try again.")
                    continue
                if runtime < 0.5 or runtime > 60:
                    print("Target runtime must be 0.5-60 minutes. Try again.")
                    continue
                return {
                    "parent_slide_count": count,
                    "target_total_runtime_minutes": runtime,
                    "override": "both",
                }
            elif choice == "5":
                print("Poll cancelled by operator.")
                return None
            else:
                print("Invalid choice. Try again.")

        except ValueError:
            print("Invalid input. Try again.")
        except KeyboardInterrupt:
            print("\nPoll cancelled by operator.")
            return None


def check_runtime_feasibility(
    parent_slide_count: int,
    target_runtime_minutes: float,
    experience_profile: str,
    extracted_md_path: str,
    *,
    profiles_path: "Path | None" = None,
    narration_params_path: "Path | None" = None,
) -> dict[str, Any]:
    """Check feasibility using the profile-aware estimator.

    Returns the full estimator result which includes 'feasibility' (PASS/WARN/BLOCK).
    """
    from scripts.utilities.slide_count_runtime_estimator import estimate_and_validate

    kwargs: dict[str, Any] = {}
    if profiles_path is not None:
        kwargs["profiles_path"] = profiles_path
    if narration_params_path is not None:
        kwargs["narration_params_path"] = narration_params_path

    return estimate_and_validate(
        extracted_md_path,
        parent_slide_count=parent_slide_count,
        target_runtime_minutes=target_runtime_minutes,
        experience_profile=experience_profile,
        **kwargs,
    )


def validate_locked_params(params: dict[str, Any]) -> dict[str, Any]:
    """Validate that locked parameters are reasonable.

    Expects new-style params with parent_slide_count and target_total_runtime_minutes.
    """
    parent_count = params.get("parent_slide_count", 0)
    target_runtime = params.get("target_total_runtime_minutes", 0)

    basic_valid = 1 <= parent_count <= 50 and 0.5 <= target_runtime <= 60

    if not basic_valid:
        return {"valid": False, "reason": "Parameters out of valid ranges (parent_slide_count: 1-50, target_runtime: 0.5-60)"}

    feasibility = params.get("feasibility", "UNKNOWN")
    if feasibility == "BLOCK":
        return {"valid": False, "reason": "Feasibility BLOCK — re-poll required"}
    if feasibility == "WARN":
        return {"valid": True, "reason": "Feasibility WARN — operator acknowledgment required", "requires_ack": True}

    return {"valid": True, "reason": "Feasible"}


if __name__ == "__main__":
    print("Operator polling module — import and use programmatically.")
