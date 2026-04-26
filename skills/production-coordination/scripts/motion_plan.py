# /// script
# requires-python = ">=3.10"
# ///
"""Run-scoped Gate 2M motion plan helpers for Epic 14.

The motion plan is the pre-Irene source of truth for motion designations.
It binds Gate 2M choices to the Epic 12 authorized winner deck, then later
hydrates those decisions into Irene's segment manifest.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utilities.motion_budgeting import (
    MODEL_CREDIT_ESTIMATES,
    estimate_motion_credits,
    normalize_motion_mode,
)

MOTION_TYPES = {"static", "video", "animation"}
MODEL_PREFERENCES = set(MODEL_CREDIT_ESTIMATES)
RECOMMENDATION_CONFIDENCE = {"high", "medium", "low"}
DEFAULT_VIDEO_DURATION_SECONDS = 5.0
DEFAULT_ANIMATION_DURATION_SECONDS = 6.0


class MotionPlanError(ValueError):
    """Invalid Gate 2M plan or designation payload."""


def _load_storyboard_manifest(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {}
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {}
    text = manifest_path.read_text(encoding="utf-8")
    if manifest_path.suffix.lower() in {".yml", ".yaml"}:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    return data if isinstance(data, dict) else {}


def _index_storyboard_slides(storyboard_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slides = storyboard_manifest.get("slides", [])
    if not isinstance(slides, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        slide_id = str(slide.get("slide_id") or "").strip()
        if slide_id:
            out[slide_id] = slide
    return out


def _cue_matches(text: str, keywords: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [kw for kw in keywords if kw in lowered]


def _build_recommendation(
    *,
    slide_id: str,
    source_anchor: str,
    fidelity: str,
    visual_description: str,
    max_video_credits: float | None,
    consumed_video_credits: float,
    model_preference: str,
) -> tuple[dict[str, Any], float]:
    combined = " ".join(part for part in (source_anchor, visual_description, fidelity) if part).lower()
    direct_video_cues = _cue_matches(
        combined,
        (
            "video",
            "b-roll",
            "footage",
            "montage",
            "cinematic",
            "scene",
            "patient",
            "clinician",
        ),
    )
    animation_cues = _cue_matches(
        combined,
        (
            "journey",
            "roadmap",
            "flow",
            "sequence",
            "process",
            "timeline",
            "shift",
            "transition",
            "framework",
            "compare",
            "progression",
            "objective",
            "list",
        ),
    )
    framing_cues = _cue_matches(
        combined,
        (
            "framing",
            "dilemma",
            "crossroads",
            "opportunity",
            "discussion",
            "prompt",
            "future",
            "context",
            "hero",
        ),
    )

    video_score = 0
    animation_score = 0
    if fidelity == "literal-text":
        recommendation = {
            "motion_type": "static",
            "rationale": "Recommended static because this is a literal-text fidelity slide, and preserving legibility and text accuracy should take precedence over motion.",
            "source_anchor": source_anchor or slide_id,
            "confidence": "high",
            "motion_brief": None,
            "guidance_notes": None,
            "generated_at": datetime.now(UTC).isoformat(),
        }
        return recommendation, consumed_video_credits

    if fidelity == "literal-visual":
        animation_score += 35
    if fidelity == "creative":
        video_score += 15
    if direct_video_cues:
        video_score += 70
    if animation_cues:
        animation_score += 55
    if framing_cues:
        video_score += 30

    video_credits = estimate_motion_credits(DEFAULT_VIDEO_DURATION_SECONDS, model_preference)
    allow_video = max_video_credits is None or consumed_video_credits + video_credits <= max_video_credits

    if animation_score >= max(video_score + 10, 60):
        guidance_bits = ", ".join(animation_cues[:3]) or "the source-led conceptual structure"
        recommendation = {
            "motion_type": "animation",
            "rationale": f"Recommended animation because the source anchor points to a concept/process visual ({guidance_bits}), which is better served by controlled emphasis and sequencing than by live-action motion.",
            "source_anchor": source_anchor or slide_id,
            "confidence": "high" if fidelity == "literal-visual" or len(animation_cues) >= 2 else "medium",
            "motion_brief": None,
            "guidance_notes": f"Use restrained motion to reveal or emphasize {guidance_bits}; preserve the approved slide composition and avoid changing source meaning.",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        return recommendation, consumed_video_credits

    if allow_video and video_score >= max(animation_score, 55):
        cue_bits = ", ".join((direct_video_cues or framing_cues)[:3]) or "the framing language"
        recommendation = {
            "motion_type": "video",
            "rationale": f"Recommended video because the source anchor reads as a scene-setting or emotionally framed moment ({cue_bits}), where short live-action motion can add atmosphere without rewriting slide structure.",
            "source_anchor": source_anchor or slide_id,
            "confidence": "high" if direct_video_cues else "medium",
            "motion_brief": f"Create a short silent clip that reinforces {cue_bits} while staying aligned to the approved slide message.",
            "guidance_notes": None,
            "generated_at": datetime.now(UTC).isoformat(),
        }
        return recommendation, consumed_video_credits + video_credits

    recommendation = {
        "motion_type": "static",
        "rationale": "Recommended static because the source cues do not justify motion strongly enough to outweigh added production scope at Gate 2M.",
        "source_anchor": source_anchor or slide_id,
        "confidence": "medium" if fidelity in {"creative", "literal-visual"} else "low",
        "motion_brief": None,
        "guidance_notes": None,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    return recommendation, consumed_video_credits


def _base_budget(
    motion_budget: dict[str, Any] | None,
    *,
    require_max_credits: bool = False,
) -> dict[str, Any]:
    budget = motion_budget or {}
    raw_model_preference = str(budget.get("model_preference") or "std")
    model_preference = normalize_motion_mode(raw_model_preference)
    if model_preference != raw_model_preference.strip().lower():
        raise MotionPlanError(
            f"motion_budget.model_preference must be one of {sorted(MODEL_PREFERENCES)}"
        )
    max_credits = budget.get("max_credits")
    if require_max_credits and not isinstance(max_credits, (int, float)):
        raise MotionPlanError("motion_enabled requires motion_budget.max_credits")
    if require_max_credits and isinstance(max_credits, (int, float)) and float(max_credits) <= 0:
        raise MotionPlanError("motion_budget.max_credits must be a positive number")
    return {
        "max_credits": float(max_credits) if isinstance(max_credits, (int, float)) else None,
        "model_preference": model_preference,
    }


def build_motion_plan_from_authorized_storyboard(
    authorized_storyboard: dict[str, Any],
    *,
    motion_enabled: bool = False,
    motion_budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a Gate 2M motion plan from the Epic 12 winner deck."""
    slides = authorized_storyboard.get("authorized_slides", [])
    if not isinstance(slides, list) or not slides:
        raise MotionPlanError("authorized_storyboard must contain authorized_slides")

    storyboard_manifest = _load_storyboard_manifest(authorized_storyboard.get("source_manifest"))
    storyboard_by_id = _index_storyboard_slides(storyboard_manifest)
    seen_slide_ids: set[str] = set()
    plan_rows: list[dict[str, Any]] = []
    recommendation_counts = {"static": 0, "video": 0, "animation": 0}
    consumed_video_credits = 0.0
    budget = _base_budget(motion_budget, require_max_credits=motion_enabled)
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        slide_id = str(slide.get("slide_id") or "").strip()
        if not slide_id:
            raise MotionPlanError("authorized_slides entries require slide_id")
        if slide_id in seen_slide_ids:
            raise MotionPlanError(
                f"authorized_storyboard is not canonical; duplicate slide_id {slide_id!r}"
            )
        seen_slide_ids.add(slide_id)
        storyboard_row = storyboard_by_id.get(slide_id, {})
        source_anchor = str(
            storyboard_row.get("source_ref")
            or slide.get("source_ref")
            or slide_id
        ).strip()
        fidelity = str(storyboard_row.get("fidelity") or slide.get("fidelity") or "").strip().lower()
        visual_description = str(storyboard_row.get("visual_description") or "").strip()
        recommendation, consumed_video_credits = _build_recommendation(
            slide_id=slide_id,
            source_anchor=source_anchor,
            fidelity=fidelity,
            visual_description=visual_description,
            max_video_credits=budget.get("max_credits"),
            consumed_video_credits=consumed_video_credits,
            model_preference=budget["model_preference"],
        )
        recommendation_counts[recommendation["motion_type"]] += 1
        if not str(recommendation.get("rationale") or "").strip():
            raise MotionPlanError(f"slide {slide_id}: recommendation requires rationale")
        if not str(recommendation.get("source_anchor") or "").strip():
            raise MotionPlanError(f"slide {slide_id}: recommendation requires source_anchor")
        if str(recommendation.get("confidence") or "").strip().lower() not in RECOMMENDATION_CONFIDENCE:
            raise MotionPlanError(f"slide {slide_id}: recommendation confidence must be one of {sorted(RECOMMENDATION_CONFIDENCE)}")
        if recommendation["motion_type"] in {"video", "animation"} and not str(recommendation.get("source_anchor") or "").strip():
            raise MotionPlanError(f"slide {slide_id}: non-static recommendation requires source_anchor")
        plan_rows.append(
            {
                "slide_id": slide_id,
                "card_number": slide.get("card_number"),
                "motion_type": "static",
                "motion_brief": None,
                "guidance_notes": None,
                "motion_asset_path": None,
                "motion_source": None,
                "motion_duration_seconds": None,
                "motion_status": None,
                "estimated_credits": 0.0,
                "source_anchor": source_anchor,
                "recommendation": recommendation,
                "operator_override_reason": None,
            }
        )

    return {
        "motion_plan_version": 1,
        "run_id": authorized_storyboard.get("run_id"),
        "motion_enabled": motion_enabled,
        "motion_budget": budget,
        "summary": {
            "static": len(plan_rows),
            "video": 0,
            "animation": 0,
            "estimated_credits": 0.0,
            "credits_consumed": 0.0,
        },
        "recommendation_summary": {
            **recommendation_counts,
            "estimated_video_credits": round(consumed_video_credits, 2),
        },
        "slides": plan_rows,
    }


def apply_motion_designations(
    motion_plan: dict[str, Any],
    designations: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Apply Gate 2M designations to the run-scoped motion plan."""
    plan = deepcopy(motion_plan)
    if not plan.get("motion_enabled", False):
        return plan

    budget = _base_budget(plan.get("motion_budget"), require_max_credits=bool(plan.get("motion_enabled", False)))
    known_slide_ids = {
        str(row.get("slide_id") or "").strip()
        for row in plan.get("slides", [])
        if isinstance(row, dict)
    }
    unknown_designations = sorted(set(designations) - known_slide_ids)
    if unknown_designations:
        raise MotionPlanError(
            "Gate 2M designation payload contains unknown slide_id values: "
            + ", ".join(unknown_designations)
        )
    missing_designations = sorted(slide_id for slide_id in known_slide_ids if slide_id not in designations)
    if missing_designations:
        raise MotionPlanError(
            "Gate 2M designation payload is incomplete; missing slide_id values: "
            + ", ".join(missing_designations)
        )
    static_count = 0
    video_count = 0
    animation_count = 0
    estimated_credits = 0.0

    for row in plan.get("slides", []):
        slide_id = str(row.get("slide_id") or "").strip()
        choice = designations.get(slide_id, {})
        motion_type_raw = choice.get("motion_type")
        motion_type = str(motion_type_raw or "").strip().lower()
        if motion_type not in MOTION_TYPES:
            raise MotionPlanError(
                f"slide {slide_id}: motion_type must be explicitly set to one of {sorted(MOTION_TYPES)}"
            )

        row["motion_type"] = motion_type
        row["motion_brief"] = choice.get("motion_brief")
        row["guidance_notes"] = choice.get("guidance_notes")
        row["operator_override_reason"] = choice.get("override_reason")
        row["motion_status"] = "pending" if motion_type != "static" else None
        row["motion_source"] = (
            "kling" if motion_type == "video" else "manual" if motion_type == "animation" else None
        )
        row["motion_duration_seconds"] = choice.get("motion_duration_seconds")
        row["motion_asset_path"] = choice.get("motion_asset_path")
        recommendation = row.get("recommendation") if isinstance(row.get("recommendation"), dict) else {}
        recommended_motion_type = str(recommendation.get("motion_type") or "").strip().lower()
        if recommended_motion_type and recommended_motion_type != motion_type:
            override_reason = str(choice.get("override_reason") or "").strip()
            if not override_reason:
                raise MotionPlanError(
                    f"slide {slide_id}: override_reason is required when operator selection differs from recommendation"
                )

        if motion_type == "static":
            row["estimated_credits"] = 0.0
            static_count += 1
            continue

        duration_seconds = row["motion_duration_seconds"]
        if not isinstance(duration_seconds, (int, float)) or float(duration_seconds) <= 0:
            duration_seconds = 5.0 if motion_type == "video" else 6.0
            row["motion_duration_seconds"] = duration_seconds

        if motion_type == "video":
            credits = estimate_motion_credits(float(duration_seconds), budget["model_preference"])
            row["estimated_credits"] = credits
            estimated_credits += credits
            video_count += 1
        else:
            row["estimated_credits"] = 0.0
            animation_count += 1

    plan["summary"] = {
        "static": static_count,
        "video": video_count,
        "animation": animation_count,
        "estimated_credits": round(estimated_credits, 2),
        "credits_consumed": float(plan.get("summary", {}).get("credits_consumed", 0.0) or 0.0),
    }
    max_credits = budget.get("max_credits")
    if isinstance(max_credits, (int, float)) and estimated_credits > float(max_credits):
        raise MotionPlanError(
            "Gate 2M designation payload exceeds motion_budget.max_credits "
            f"(estimated={round(estimated_credits, 2)}, max_credits={float(max_credits)})"
        )
    return plan


def route_motion_assignments(motion_plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return static/video/animation routing buckets from a plan."""
    routing = {"static": [], "video": [], "animation": []}
    for row in motion_plan.get("slides", []):
        if not isinstance(row, dict):
            continue
        motion_type = str(row.get("motion_type") or "static").strip().lower() or "static"
        routing.setdefault(motion_type, [])
        routing[motion_type].append(row)
    return routing


def build_designations_template(motion_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build an operator-editable designation template with recommendations."""
    template: dict[str, dict[str, Any]] = {}
    for row in motion_plan.get("slides", []):
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if not slide_id:
            continue
        recommendation = row.get("recommendation") if isinstance(row.get("recommendation"), dict) else {}
        template[slide_id] = {
            "motion_type": None,
            "motion_brief": None,
            "guidance_notes": None,
            "override_reason": None,
            "recommended_motion_type": recommendation.get("motion_type"),
            "recommendation_rationale": recommendation.get("rationale"),
            "recommendation_source_anchor": recommendation.get("source_anchor"),
            "recommendation_confidence": recommendation.get("confidence"),
            "recommended_motion_brief": recommendation.get("motion_brief"),
            "recommended_guidance_notes": recommendation.get("guidance_notes"),
        }
    return template


def load_motion_plan(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def write_motion_plan(path: str | Path, motion_plan: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(motion_plan, sort_keys=False), encoding="utf-8")
    return target


def write_designations(path: str | Path, designations: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(designations, indent=2), encoding="utf-8")
    return target


def _load_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise MotionPlanError(f"expected mapping in {path}")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Gate 2M motion plans.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", help="Build a motion plan from an authorized storyboard."
    )
    build_parser.add_argument("--authorized-storyboard", required=True, type=Path)
    build_parser.add_argument("--output", required=True, type=Path)
    build_parser.add_argument("--motion-enabled", action="store_true")
    build_parser.add_argument("--motion-budget-max-credits", type=float, default=None)
    build_parser.add_argument("--motion-budget-model-preference", default="std")
    build_parser.add_argument("--designations-output", type=Path, default=None)

    apply_parser = subparsers.add_parser(
        "apply", help="Apply Gate 2M designations to an existing motion plan."
    )
    apply_parser.add_argument("--motion-plan", required=True, type=Path)
    apply_parser.add_argument("--designations", required=True, type=Path)
    apply_parser.add_argument("--output", required=True, type=Path)

    route_parser = subparsers.add_parser(
        "route", help="Print routing buckets for an existing motion plan."
    )
    route_parser.add_argument("--motion-plan", required=True, type=Path)

    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            authorized_storyboard = _load_yaml(args.authorized_storyboard)
            motion_plan = build_motion_plan_from_authorized_storyboard(
                authorized_storyboard,
                motion_enabled=bool(args.motion_enabled),
                motion_budget={
                    "max_credits": args.motion_budget_max_credits,
                    "model_preference": args.motion_budget_model_preference,
                },
            )
            output = write_motion_plan(args.output, motion_plan)
            result = {"status": "ok", "motion_plan": str(output)}
            if args.designations_output is not None:
                designation_path = write_designations(
                    args.designations_output,
                    build_designations_template(motion_plan),
                )
                result["designations"] = str(designation_path)
            print(json.dumps(result, indent=2))
            return 0

        if args.command == "apply":
            motion_plan = load_motion_plan(args.motion_plan)
            designations = _load_yaml(args.designations)
            updated = apply_motion_designations(motion_plan, designations)
            output = write_motion_plan(args.output, updated)
            print(json.dumps({"status": "ok", "motion_plan": str(output)}, indent=2))
            return 0

        if args.command == "route":
            motion_plan = load_motion_plan(args.motion_plan)
            print(json.dumps(route_motion_assignments(motion_plan), indent=2))
            return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
