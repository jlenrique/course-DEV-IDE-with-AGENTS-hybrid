# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Generate a skeleton production plan from content type and module structure.

Reads the course context YAML to resolve module/lesson hierarchy, then
produces a markdown production plan with specialist sequencing, checkpoint
gates, and dependency ordering appropriate for the requested content type.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


WORKFLOW_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "references" / "workflow-templates.yaml"


def load_workflow_templates(workflow_template_path: Path = WORKFLOW_TEMPLATE_PATH) -> dict[str, dict[str, Any]]:
    """Load workflow templates from the canonical Marcus registry."""
    if yaml is None:
        msg = "pyyaml is required to load workflow templates"
        raise RuntimeError(msg)

    with open(workflow_template_path, encoding="utf-8") as handle:
        registry = yaml.safe_load(handle) or {}

    templates = registry.get("workflow_templates")
    if not isinstance(templates, dict) or not templates:
        msg = f"Invalid or empty workflow template registry: {workflow_template_path}"
        raise ValueError(msg)

    return templates


def build_workflow_lookup(workflow_templates: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Build requested content type -> canonical workflow id lookup."""
    lookup: dict[str, str] = {}
    for template_id, workflow in workflow_templates.items():
        keys = [template_id, *workflow.get("aliases", [])]
        for key in keys:
            if key in lookup and lookup[key] != template_id:
                msg = f"Duplicate workflow key detected: {key}"
                raise ValueError(msg)
            lookup[key] = template_id
    return lookup


def resolve_workflow(
    content_type: str,
    workflow_templates: dict[str, dict[str, Any]],
    workflow_lookup: dict[str, str],
) -> tuple[str, dict[str, Any]] | tuple[None, None]:
    """Resolve aliases to canonical workflow ids."""
    template_id = workflow_lookup.get(content_type)
    if template_id is None:
        return None, None
    return template_id, workflow_templates[template_id]


def select_workflow_variant(content_type: str, *, motion_enabled: bool = False) -> str:
    """Resolve the narrated lesson workflow variant from the run flag.

    The static narrated export remains the default. Motion is additive and
    promoted explicitly when the run flag is on.
    """
    if content_type == "narrated-lesson-with-video-or-animation" and not motion_enabled:
        return "narrated-deck-video-export"
    if content_type == "narrated-deck-video-export" and motion_enabled:
        return "narrated-lesson-with-video-or-animation"
    return content_type


def load_course_context(course_context_path: Path) -> dict | None:
    """Load course context YAML if available."""
    if not course_context_path.exists():
        return None
    if yaml is None:
        print("Warning: pyyaml not available, skipping course context", file=sys.stderr)
        return None
    with open(course_context_path) as f:
        return yaml.safe_load(f)


def generate_plan(
    content_type: str,
    module_id: str | None = None,
    lesson_id: str | None = None,
    course_context: dict | None = None,
    workflow_templates: dict[str, dict[str, Any]] | None = None,
    motion_enabled: bool = False,
) -> str:
    """Generate a markdown production plan for the given content type and scope.

    Args:
        content_type: One of the known workflow template ids or aliases.
        module_id: Optional module identifier for scope.
        lesson_id: Optional lesson identifier for scope.
        course_context: Optional course context dictionary from YAML.
        workflow_templates: Optional workflow template registry override.

    Returns:
        Markdown string with the production plan.
    """
    workflow_templates = workflow_templates or load_workflow_templates()
    workflow_lookup = build_workflow_lookup(workflow_templates)
    effective_content_type = select_workflow_variant(content_type, motion_enabled=motion_enabled)
    template_id, workflow = resolve_workflow(
        effective_content_type, workflow_templates, workflow_lookup
    )
    if not workflow or not template_id:
        available = ", ".join(sorted(workflow_lookup.keys()))
        return f"Unknown content type: {content_type}\n\nAvailable types: {available}"

    lines: list[str] = []
    lines.append(f"# Production Plan: {workflow['label']}")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Content Type:** {workflow['label']}")
    lines.append(f"**Workflow Template:** {template_id}")

    if module_id:
        lines.append(f"**Module:** {module_id}")
    if lesson_id:
        lines.append(f"**Lesson:** {lesson_id}")

    if course_context and module_id:
        modules = course_context.get("modules", {})
        module_info = modules.get(module_id, {})
        if module_info:
            lines.append(f"**Module Title:** {module_info.get('title', 'Unknown')}")
            if lesson_id:
                lessons = module_info.get("lessons", {})
                lesson_info = lessons.get(lesson_id, {})
                if lesson_info:
                    lines.append(f"**Lesson Title:** {lesson_info.get('title', 'Unknown')}")
                    objectives = lesson_info.get("learning_objectives", [])
                    if objectives:
                        lines.append("\n**Learning Objectives:**")
                        for obj in objectives:
                            lines.append(f"- {obj}")

    lines.append("\n## Production Stages\n")
    lines.append("| # | Stage | Specialist | Description | Status |")
    lines.append("|---|-------|-----------|-------------|--------|")

    for i, stage in enumerate(workflow["stages"], 1):
        specialist = stage["specialist"]
        if specialist == "human":
            specialist = "**USER REVIEW**"
        lines.append(f"| {i} | {stage['stage']} | {specialist} | {stage['description']} | pending |")

    lines.append("\n## Pre-Production Checklist\n")
    lines.append("- [ ] Style bible consulted (`resources/style-bible/`)")
    lines.append("- [ ] Exemplar library checked (`resources/exemplars/`)")
    lines.append("- [ ] Learning objectives confirmed")
    lines.append("- [ ] Asset-lesson pairing established")
    lines.append("- [ ] Source materials gathered (if applicable)")

    lines.append("\n## Notes\n")
    lines.append("- All quality gates reference the style bible as primary rubric")
    lines.append("- User checkpoints require explicit approval before proceeding")
    lines.append("- Asset-lesson pairing is verified before marking any stage complete")

    return "\n".join(lines)


def main() -> None:
    workflow_templates = load_workflow_templates()
    workflow_lookup = build_workflow_lookup(workflow_templates)

    parser = argparse.ArgumentParser(
        description="Generate a skeleton production plan from content type and module structure.",
        epilog="Outputs a markdown production plan to stdout.",
    )
    parser.add_argument(
        "content_type",
        choices=sorted(workflow_lookup.keys()),
        help="Type of content or workflow alias to produce.",
    )
    parser.add_argument(
        "--module",
        type=str,
        default=None,
        help="Module identifier (e.g., M1, M2).",
    )
    parser.add_argument(
        "--lesson",
        type=str,
        default=None,
        help="Lesson identifier within the module.",
    )
    parser.add_argument(
        "--course-context",
        type=Path,
        default=None,
        help="Path to course_context.yaml. Default: state/config/course_context.yaml",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output as JSON instead of markdown.",
    )
    parser.add_argument(
        "--motion-enabled",
        action="store_true",
        help="Select the motion-enhanced narrated workflow variant when applicable.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic info to stderr.",
    )
    args = parser.parse_args()

    course_context_path = args.course_context
    if course_context_path is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        course_context_path = project_root / "state" / "config" / "course_context.yaml"

    course_context = load_course_context(course_context_path)

    if args.verbose:
        print(f"Content type: {args.content_type}", file=sys.stderr)
        print(f"Course context path: {course_context_path}", file=sys.stderr)
        print(f"Course context loaded: {course_context is not None}", file=sys.stderr)

    try:
        effective_content_type = select_workflow_variant(
            args.content_type, motion_enabled=args.motion_enabled
        )
        template_id, workflow = resolve_workflow(
            effective_content_type, workflow_templates, workflow_lookup
        )
        if not workflow or not template_id:
            msg = f"Unknown workflow template or alias: {args.content_type}"
            raise ValueError(msg)

        if args.output_json:
            output = {
                "content_type": template_id,
                "requested_content_type": args.content_type,
                "effective_content_type": effective_content_type,
                "motion_enabled": args.motion_enabled,
                "label": workflow["label"],
                "aliases": workflow.get("aliases", []),
                "module": args.module,
                "lesson": args.lesson,
                "stages": workflow["stages"],
                "generated_at": datetime.now().isoformat(),
            }
            json.dump(output, sys.stdout, indent=2)
            print()
        else:
            plan = generate_plan(
                content_type=args.content_type,
                module_id=args.module,
                lesson_id=args.lesson,
                course_context=course_context,
                workflow_templates=workflow_templates,
                motion_enabled=args.motion_enabled,
            )
            print(plan)
        sys.exit(0)
    except Exception as e:
        error = {"error": str(e), "timestamp": datetime.now().isoformat()}
        json.dump(error, sys.stderr, indent=2)
        print(file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
