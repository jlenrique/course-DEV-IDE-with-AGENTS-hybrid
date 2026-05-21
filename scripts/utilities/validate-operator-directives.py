#!/usr/bin/env python3
"""
Validate Operator Directives

Canonical validator for operator-directives.md completeness and format.
Used by Marcus in Prompt 2A and ingestion validators.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any


def validate_operator_directives(directives_path: Path) -> dict[str, Any]:
    """Validate operator-directives.md for completeness and format."""
    if not directives_path.is_file():
        return {
            "valid": False,
            "reason": f"File not found: {directives_path}",
            "issues": [f"operator-directives.md not found at {directives_path}"],
        }

    try:
        content = directives_path.read_text(encoding="utf-8")
    except Exception as exc:
        return {
            "valid": False,
            "reason": f"Read error: {exc}",
            "issues": [f"Cannot read {directives_path}: {exc}"],
        }

    issues = []

    # Check required fields
    required_fields = [
        "run_id",
        "timestamp",
        "poll_started_utc",
        "reply_eligible_utc",
        "poll_close_utc",
        "poll_status",
        "operator",
    ]

    for field in required_fields:
        if field not in content:
            issues.append(f"Missing required field: {field}")

    # Check directive sections
    directive_sections = [
        "focus_directives",
        "exclusion_directives",
        "special_treatment_directives",
    ]

    for section in directive_sections:
        if section not in content:
            issues.append(f"Missing directive section: {section}")

    # Check poll status is valid
    if "poll_status" in content:
        status_match = re.search(r"poll_status:\s*(.+)", content)
        if status_match:
            status = status_match.group(1).strip()
            if status not in {"open", "closed-timeout", "submitted"}:
                issues.append(f"Invalid poll_status: {status}")

    # Check timestamps are ISO format
    timestamp_fields = ["timestamp", "poll_started_utc", "reply_eligible_utc", "poll_close_utc"]
    for field in timestamp_fields:
        if field in content:
            ts_match = re.search(rf"{field}:\s*(.+)", content)
            if ts_match:
                ts = ts_match.group(1).strip()
                if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts):
                    issues.append(f"Invalid timestamp format for {field}: {ts}")

    # Check for no directives acknowledgment
    if "No operator directives" not in content and not any(
        section in content for section in directive_sections
    ):
        issues.append("No directives provided and no 'No operator directives' acknowledgment")

    return {
        "valid": len(issues) == 0,
        "reason": "Valid" if len(issues) == 0 else f"{len(issues)} issues found",
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate operator-directives.md for completeness and format."
    )
    parser.add_argument(
        "--directives-path",
        type=Path,
        required=True,
        help="Path to operator-directives.md",
    )

    args = parser.parse_args(argv)

    result = validate_operator_directives(args.directives_path)

    if result["valid"]:
        print("VALID: operator-directives.md passes validation")
        return 0
    else:
        print(f"INVALID: {result['reason']}")
        for issue in result["issues"]:
            print(f"  - {issue}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
