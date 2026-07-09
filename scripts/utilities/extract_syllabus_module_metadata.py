"""Emit deterministic syllabus-derived module metadata proposals."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.marcus.course_source.syllabus_metadata import (
    build_module_metadata_proposal,
    render_module_metadata_yaml,
)


def assert_output_outside_course_root(course_root: Path, output_path: Path) -> None:
    resolved_course_root = course_root.resolve()
    resolved_output = output_path.resolve()
    if resolved_output == resolved_course_root or resolved_course_root in resolved_output.parents:
        raise ValueError("output must be outside the course container")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    parser.add_argument("syllabus_path", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-learning-objectives", type=int, required=True)
    parser.add_argument("--required-title", default=None)
    args = parser.parse_args()

    assert_output_outside_course_root(args.course_root, args.output)
    proposal = build_module_metadata_proposal(
        args.course_root,
        args.syllabus_path,
        expected_learning_objective_count=args.expected_learning_objectives,
        required_title=args.required_title,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_module_metadata_yaml(proposal), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"extraction_status={proposal.extraction_status}")
    print(f"course_learning_objectives={len(proposal.course_learning_objectives)}")
    print(f"modules={len(proposal.modules)}")
    return 0 if proposal.extraction_status == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
