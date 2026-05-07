"""AC-T.2 — committed JSON Schema stays aligned with Pydantic source."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic_core import PydanticUndefined

from app.marcus.lesson_plan.coverage_manifest import CoverageManifest, CoverageSummary, CoverageSurface

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "marcus"
    / "lesson_plan"
    / "schema"
    / "coverage_manifest.v1.schema.json"
)


def test_coverage_manifest_json_schema_parity() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    defs = schema["$defs"]
    for model_name, model_cls in {
        "CoverageSurface": CoverageSurface,
        "CoverageSummary": CoverageSummary,
        "CoverageManifest": CoverageManifest,
    }.items():
        schema_def = schema if schema["title"] == model_name else defs[model_name]
        assert set(schema_def["properties"].keys()) == set(model_cls.model_fields.keys())
        expected_required = {
            name
            for name, field in model_cls.model_fields.items()
            if field.default is PydanticUndefined and field.default_factory is None
        }
        assert set(schema_def.get("required", [])) == expected_required
        assert schema_def.get("additionalProperties") is False
