"""Generate or check deterministic course-source manifest snapshots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.marcus.course_source.manifest_drift import check_manifest_snapshot
from app.marcus.course_source.manifest_scan import scan_course, write_manifest_snapshot


def _snapshot_path(course_root: Path) -> Path:
    return course_root / "source-manifest.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_roots", nargs="+", type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate source-manifest.yaml under each course root.",
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for course_root in args.course_roots:
        snapshot = _snapshot_path(course_root)
        if args.write:
            write_manifest_snapshot(scan_course(course_root), snapshot)
            print(f"wrote {snapshot.as_posix()}")
            continue
        result = check_manifest_snapshot(course_root, snapshot)
        if result.is_stale:
            exit_code = 1
            print(result.diff, file=sys.stderr)
        else:
            print(f"ok {snapshot.as_posix()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
