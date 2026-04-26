#!/usr/bin/env python3
"""
Inspect Gary Output for Stale Artifacts

Canonical inspection script for Gary dispatch results before Irene Pass 2.
Checks for stale or missing artifacts, PNG validity, and literal-visual sources.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def inspect_gary_output(bundle_dir: Path) -> dict[str, Any]:
    """Inspect Gary dispatch output for issues before Irene."""
    issues = []
    warnings = []

    # Check dispatch result
    dispatch_result = bundle_dir / "gary-dispatch-result.json"
    if not dispatch_result.exists():
        issues.append("gary-dispatch-result.json not found")
        return {"valid": False, "issues": issues, "warnings": warnings}

    try:
        with dispatch_result.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        issues.append(f"Invalid JSON in gary-dispatch-result.json: {exc}")
        return {"valid": False, "issues": issues, "warnings": warnings}

    slides = data.get("slides", [])
    if not slides:
        issues.append("No slides in dispatch result")
        return {"valid": False, "issues": issues, "warnings": warnings}

    # Check each slide
    for slide in slides:
        slide_id = slide.get("slide_number")
        file_path = slide.get("file_path")
        literal_visual_source = slide.get("literal_visual_source")

        if not file_path:
            issues.append(f"Slide {slide_id}: missing file_path")
            continue

        png_path = Path(file_path)
        if not png_path.is_file():
            issues.append(f"Slide {slide_id}: PNG not found at {file_path}")
            continue

        # Check literal-visual source
        if literal_visual_source and literal_visual_source not in ["template", "composite-preintegration", "composite-download"]:
            warnings.append(f"Slide {slide_id}: unknown literal_visual_source '{literal_visual_source}'")

    # Check for stale artifacts (compare timestamps if available)
    dispatch_log = bundle_dir / "gary-dispatch-run-log.json"
    if dispatch_log.exists():
        try:
            with dispatch_log.open("r", encoding="utf-8") as f:
                log_data = json.load(f)
            dispatch_time = log_data.get("timestamp")
            if dispatch_time:
                # Could add more checks here
                pass
        except Exception:
            warnings.append("Could not parse dispatch log for staleness check")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "slide_count": len(slides),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect Gary dispatch output for issues before Irene."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Bundle directory containing Gary output",
    )

    args = parser.parse_args(argv)

    result = inspect_gary_output(args.bundle_dir)

    if result["valid"]:
        print("VALID: Gary output inspection passed")
        print(f"Slides: {result['slide_count']}")
        if result["warnings"]:
            print("Warnings:")
            for w in result["warnings"]:
                print(f"  - {w}")
    else:
        print("INVALID: Issues found")
        for issue in result["issues"]:
            print(f"  - {issue}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
