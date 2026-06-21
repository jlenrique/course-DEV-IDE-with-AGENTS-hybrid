from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "state" / "config" / "reading-path-patterns.yaml"
SEGMENT_SCHEMA_PATH = ROOT / "state" / "config" / "schemas" / "segment-manifest.schema.json"
LINT_PATH = ROOT / "scripts" / "validators" / "pass_2_emission_lint.py"
CLASSIFIER_PATH = ROOT / "scripts" / "utilities" / "reading_path_classifier.py"
GRAMMAR_PATH = (
    ROOT
    / "skills"
    / "bmad-agent-content-creator"
    / "references"
    / "pass-2-grammar-riders-examples.md"
)

EXPECTED_PATTERNS = (
    "z_pattern",
    "f_pattern",
    "center_out",
    "top_down",
    "multi_column",
    "grid_quadrant",
    "sequence_numbered",
)


def _registry_patterns() -> tuple[str, ...]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    patterns = data.get("patterns")
    assert isinstance(patterns, list)
    return tuple(str(item["id"]) for item in patterns)


def _segment_schema_patterns() -> tuple[str, ...]:
    schema = json.loads(SEGMENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    reading_path = schema["properties"]["segments"]["items"]["properties"]["reading_path"]
    return tuple(reading_path["properties"]["pattern"]["enum"])


def _grammar_heading_patterns() -> tuple[str, ...]:
    text = GRAMMAR_PATH.read_text(encoding="utf-8")
    found = re.findall(r"^##\s+Pattern:\s+([a-z_]+)\s*$", text, flags=re.MULTILINE)
    return tuple(pattern for pattern in found if pattern in EXPECTED_PATTERNS)


def _module_tuple_literal(path: Path, name: str) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    return tuple(value)
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
        ):
            value = ast.literal_eval(node.value)
            return tuple(value)
    raise AssertionError(f"{name} not found in {path}")


def test_reading_path_pattern_lockstep() -> None:
    assert _registry_patterns() == EXPECTED_PATTERNS
    assert _segment_schema_patterns() == EXPECTED_PATTERNS
    assert _grammar_heading_patterns() == EXPECTED_PATTERNS
    assert _module_tuple_literal(CLASSIFIER_PATH, "READING_PATH_PATTERNS") == EXPECTED_PATTERNS
    assert _module_tuple_literal(LINT_PATH, "READING_PATH_PATTERNS") == EXPECTED_PATTERNS


def test_segment_manifest_schema_rejects_out_of_vocab_pattern() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SEGMENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = {
        "segments": [
            {
                "id": "seg-01",
                "slide_id": "slide-01",
                "reading_path": {"pattern": "triptych"},
            }
        ]
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
