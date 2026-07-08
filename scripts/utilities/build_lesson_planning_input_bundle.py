"""Build a deterministic lesson-planning input bundle for one course module."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.marcus.course_source.input_bundle import (
    build_lesson_planning_input_bundle,
    write_input_bundle,
)


def assert_output_outside_course_root(course_root: Path, output_path: Path) -> None:
    resolved_course_root = course_root.resolve()
    resolved_output = output_path.resolve()
    if resolved_output == resolved_course_root or resolved_course_root in resolved_output.parents:
        raise ValueError("output must be outside the course container")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    parser.add_argument("proposal_path", type=Path)
    parser.add_argument("--module-id", required=True)
    parser.add_argument("--operator-focus", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    assert_output_outside_course_root(args.course_root, args.output)
    bundle = build_lesson_planning_input_bundle(
        course_root=args.course_root,
        proposal_path=args.proposal_path,
        module_id=args.module_id,
        operator_focus=args.operator_focus,
    )
    write_input_bundle(bundle, args.output)
    print(f"wrote {args.output}")
    print(f"course_id={bundle.course.course_id}")
    print(f"module_id={bundle.module.module_id}")
    print(f"source_purpose={bundle.course.source_purpose}")
    print(f"gaps={len(bundle.gap_ledger)}")
    print(f"asset_records={len(bundle.asset_records)}")
    print(f"component_selection={bundle.component_selection.as_map()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
