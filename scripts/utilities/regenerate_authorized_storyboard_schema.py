"""Regenerate the authorized-storyboard JSON schema."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "state" / "config" / "schemas" / (
    "authorized-storyboard.schema.json"
)

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://course-dev-ide-with-agents.local/schemas/authorized-storyboard.schema.json",
    "title": "Authorized Storyboard",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "slides"],
    "properties": {
        "schema_version": {"const": "1.0"},
        "slides": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "slide_id",
                    "title",
                    "narration_pointer",
                    "motion_pointer",
                    "quinn_r_verdict",
                    "evidence_block",
                ],
                "properties": {
                    "slide_id": {"type": "string", "minLength": 1},
                    "title": {"type": "string", "minLength": 1},
                    "narration_pointer": {"type": "string", "minLength": 1},
                    "motion_pointer": {"type": "string", "minLength": 1},
                    "quinn_r_verdict": {
                        "enum": ["advisory", "blocking", "approved"],
                    },
                    "evidence_block": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}


def main() -> int:
    SCHEMA_PATH.write_text(
        json.dumps(SCHEMA, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {SCHEMA_PATH.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
