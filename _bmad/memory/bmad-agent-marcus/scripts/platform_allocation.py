"""Platform allocation intelligence for Marcus (Story G.1).

Reads allocation rules from exemplars and produces a structured recommendation
with rationale and explicit override options.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root

DEFAULT_MATRIX_PATH = (
    project_root() / "resources" / "exemplars" / "_shared" / "platform-allocation-matrix.yaml"
)
DEFAULT_COURSE_CONTEXT_PATH = project_root() / "state" / "config" / "course_context.yaml"
DEFAULT_PATTERNS_PATH = (
    project_root() / "_bmad" / "memory" / "marcus-sidecar" / "patterns.md"
)


def load_yaml_file(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at {path}")
    return data


def load_allocation_matrix(path: Path | None = None) -> dict[str, Any]:
    matrix_path = path or DEFAULT_MATRIX_PATH
    if not matrix_path.exists():
        raise FileNotFoundError(f"Allocation matrix not found: {matrix_path}")
    return load_yaml_file(matrix_path)


def load_course_code(path: Path | None = None) -> str | None:
    context_path = path or DEFAULT_COURSE_CONTEXT_PATH
    if not context_path.exists():
        return None

    context = load_yaml_file(context_path)
    course = context.get("course")
    if isinstance(course, dict):
        code = course.get("code")
        if isinstance(code, str) and code.strip():
            return code.strip()
    return None


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(value, float):
        if value in {0.0, 1.0}:
            return bool(int(value))
        raise ValueError(f"Boolean flag cannot be non-binary float: {value}")
    if isinstance(value, int):
        return bool(value)
    return False


def recommend_platform(
    content_profile: dict[str, Any],
    *,
    matrix: dict[str, Any],
    course_code: str | None = None,
) -> dict[str, Any]:
    rules = matrix.get("rules", {}) if isinstance(matrix.get("rules"), dict) else {}

    required_canvas_flags = set(rules.get("required_canvas_flags", []))
    coursearc_types = set(rules.get("preferred_coursearc_content_types", []))
    panopto_types = set(rules.get("preferred_panopto_content_types", []))
    direct_embed_types = set(rules.get("preferred_direct_embed_content_types", []))
    high_interactivity_levels = set(rules.get("high_interactivity_levels", []))
    default_platform = str(rules.get("default_platform", "canvas"))

    normalized_profile = {
        "content_type": str(content_profile.get("content_type", "")).strip(),
        "interactivity_level": str(
            content_profile.get("interactivity_level", "medium")
        ).strip(),
        "graded": _as_bool(content_profile.get("graded", False)),
        "peer_discussion": _as_bool(content_profile.get("peer_discussion", False)),
        "instructor_facilitation": _as_bool(
            content_profile.get("instructor_facilitation", False)
        ),
        "narrative_control": _as_bool(content_profile.get("narrative_control", False)),
        "accessibility_critical": _as_bool(
            content_profile.get("accessibility_critical", False)
        ),
    }

    unknown_flags = required_canvas_flags - set(normalized_profile.keys())
    if unknown_flags:
        raise KeyError(f"Matrix references unsupported required flag(s): {sorted(unknown_flags)}")

    valid_interactivity = {"low", "medium", "high", "very-high", ""}
    if normalized_profile["interactivity_level"] not in valid_interactivity:
        raise ValueError(
            "Invalid interactivity_level: "
            f"{normalized_profile['interactivity_level']}"
        )

    reasons: list[str] = []
    recommendation = default_platform

    triggered_canvas = [
        flag for flag in required_canvas_flags if normalized_profile.get(flag) is True
    ]

    if triggered_canvas:
        recommendation = "canvas"
        reasons.append(
            "Canvas required by policy because these flags are true: "
            + ", ".join(sorted(triggered_canvas))
        )
    else:
        content_type = normalized_profile["content_type"]
        interactivity_level = normalized_profile["interactivity_level"]

        if content_type in panopto_types:
            recommendation = "panopto"
            reasons.append(
                f"Content type '{content_type}' maps to Panopto for long-form video delivery"
            )
        elif content_type in direct_embed_types:
            recommendation = "direct-embed"
            reasons.append(
                f"Content type '{content_type}' maps to direct embed by allocation policy"
            )
        elif (
            content_type in coursearc_types
            or interactivity_level in high_interactivity_levels
            or normalized_profile["narrative_control"]
            or normalized_profile["accessibility_critical"]
        ):
            recommendation = "coursearc"
            if content_type in coursearc_types:
                reasons.append(
                    f"Content type '{content_type}' is preferred for CourseArc experience layer"
                )
            if interactivity_level in high_interactivity_levels:
                reasons.append(
                    f"Interactivity level '{interactivity_level}' benefits from CourseArc blocks"
                )
            if normalized_profile["narrative_control"]:
                reasons.append("Narrative control requested; CourseArc supports guided sequencing")
            if normalized_profile["accessibility_critical"]:
                reasons.append(
                    "Accessibility-critical flow requested; CourseArc offers built-in WCAG support"
                )
        else:
            recommendation = default_platform
            reasons.append(
                "No higher-priority platform criteria matched; using policy default platform"
            )

    return {
        "course_code": course_code,
        "policy_version": matrix.get("version", "unknown"),
        "recommended_platform": recommendation,
        "rationale": reasons,
        "options": {
            "accept": recommendation,
            "modify": "adjust input flags/content type and re-evaluate",
            "override": "user may override recommendation with documented reason",
        },
        "input_profile": normalized_profile,
    }


def save_allocation_decision(
    decision: dict[str, Any],
    *,
    patterns_path: Path | None = None,
) -> Path:
    path = patterns_path or DEFAULT_PATTERNS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
    content_type = decision.get("input_profile", {}).get("content_type", "unknown")
    recommended = decision.get("recommended_platform", "unknown")
    rationale = "; ".join(decision.get("rationale", []))

    line = (
        f"- {timestamp} allocation decision: content_type={content_type}, "
        f"recommended={recommended}, rationale={rationale}\n"
    )

    with path.open("a", encoding="utf-8") as f:
        f.write(line)

    return path


def _parse_json_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recommend platform allocation for a content profile."
    )
    parser.add_argument("--input-json", type=Path, help="Path to JSON profile input")
    parser.add_argument("--content-type", help="Content type token")
    parser.add_argument(
        "--interactivity-level",
        default="medium",
        choices=["low", "medium", "high", "very-high"],
        help="Interactivity level",
    )
    parser.add_argument("--graded", action="store_true")
    parser.add_argument("--peer-discussion", action="store_true")
    parser.add_argument("--instructor-facilitation", action="store_true")
    parser.add_argument("--narrative-control", action="store_true")
    parser.add_argument("--accessibility-critical", action="store_true")
    parser.add_argument("--matrix-path", type=Path, help="Override matrix YAML path")
    parser.add_argument(
        "--course-context-path",
        type=Path,
        help="Override course context YAML path",
    )
    parser.add_argument(
        "--save-pattern",
        action="store_true",
        help="Append final recommendation to Marcus sidecar patterns.",
    )
    parser.add_argument(
        "--patterns-path",
        type=Path,
        help="Override sidecar patterns.md path when saving a decision.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.input_json:
            profile = _parse_json_file(args.input_json)
        else:
            profile = {
                "content_type": args.content_type or "",
                "interactivity_level": args.interactivity_level,
                "graded": args.graded,
                "peer_discussion": args.peer_discussion,
                "instructor_facilitation": args.instructor_facilitation,
                "narrative_control": args.narrative_control,
                "accessibility_critical": args.accessibility_critical,
            }

        matrix = load_allocation_matrix(args.matrix_path)
        course_code = load_course_code(args.course_context_path)
        recommendation = recommend_platform(
            profile,
            matrix=matrix,
            course_code=course_code,
        )

        if args.save_pattern:
            save_allocation_decision(
                recommendation,
                patterns_path=args.patterns_path,
            )

        print(json.dumps(recommendation, indent=2))
        return 0
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
