"""Pass-2 emission lint hooks for reading-path metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.utilities.reading_path_classifier import CADENCE_TOKENS

READING_PATH_PATTERNS: tuple[str, ...] = (
    "z_pattern",
    "f_pattern",
    "center_out",
    "top_down",
    "multi_column",
    "grid_quadrant",
    "sequence_numbered",
    "split_image_text",
    "two_up_comparison",
    "text_hero_divider",
    "enumerated_process",
    "diagram_driven",
)


class Pass2EmissionLintError(ValueError):
    """Raised when Pass-2 reading-path metadata is out of contract."""


def _check_reading_path_pattern(pattern: str) -> None:
    if pattern not in READING_PATH_PATTERNS:
        raise Pass2EmissionLintError(f"out-of-vocab reading_path pattern: {pattern}")


def validate_segment_manifest(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    segments = payload.get("segments", [])
    if not isinstance(segments, list):
        return ["segments must be a list"]
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            errors.append(f"segments[{index}] must be an object")
            continue
        reading_path = segment.get("reading_path")
        if not isinstance(reading_path, dict):
            errors.append(f"segments[{index}].reading_path must be an object")
            continue
        pattern = str(reading_path.get("pattern") or "")
        try:
            _check_reading_path_pattern(pattern)
        except Pass2EmissionLintError as exc:
            errors.append(str(exc))
            continue
        if pattern in {"sequence_numbered", "enumerated_process"}:
            narration = str(segment.get("narration_text") or "").lower()
            if not any(token in narration for token in CADENCE_TOKENS[pattern]):
                errors.append(
                    f"segments[{index}] {pattern} lacks process cadence token"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate_segment_manifest(payload)
    if errors:
        for error in errors:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
