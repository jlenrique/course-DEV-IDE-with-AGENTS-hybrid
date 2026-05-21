"""Validation tests for parameter registry schema governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SCHEMA_PATH = Path("state/config/parameter-registry-schema.yaml")
NARRATION_PARAMS_PATH = Path("state/config/narration-script-parameters.yaml")


def _load_schema() -> dict[str, Any]:
    """Load the parameter registry schema file as a mapping."""
    raw = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict), "Schema root must be a mapping"
    return raw


def _load_narration_params() -> dict[str, Any]:
    """Load narration-script-parameters config."""
    raw = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict), "Narration params root must be a mapping"
    return raw


def test_registry_schema_has_required_top_level_blocks() -> None:
    """Schema should expose governance, families, and entries blocks."""
    schema = _load_schema()
    required = {
        "schema_version",
        "families",
        "status_values",
        "required_entry_fields",
        "field_glossary",
        "strictness_policy",
        "entries",
        "examples",
    }
    missing = required - set(schema.keys())
    assert not missing, f"Missing required top-level schema keys: {sorted(missing)}"


def test_registry_entries_have_required_fields_and_unique_keys() -> None:
    """Each entry must include required fields with a unique key."""
    schema = _load_schema()
    entries = schema.get("entries")
    assert isinstance(entries, list) and entries, "entries must be a non-empty list"

    required_entry_fields = schema.get("required_entry_fields")
    assert isinstance(required_entry_fields, list) and required_entry_fields

    seen: set[str] = set()
    duplicates: set[str] = set()

    for entry in entries:
        assert isinstance(entry, dict), "each entry must be a mapping"
        for field in required_entry_fields:
            assert field in entry, f"entry missing required field `{field}`: {entry}"
        key = entry["key"]
        assert isinstance(key, str) and key.strip(), "entry key must be non-empty string"
        if key in seen:
            duplicates.add(key)
        seen.add(key)

    assert not duplicates, f"duplicate keys detected: {sorted(duplicates)}"


def test_registry_entries_match_known_families_and_statuses() -> None:
    """Entry family and status values should be constrained to registry definitions."""
    schema = _load_schema()
    entries = schema["entries"]
    families = schema["families"]
    statuses = schema["status_values"]

    assert isinstance(families, dict) and families
    assert isinstance(statuses, list) and statuses

    family_names = set(families.keys())
    status_names = set(statuses)

    for entry in entries:
        family = entry["family"]
        status = entry["status"]
        assert family in family_names, f"unknown family `{family}` in entry `{entry['key']}`"
        assert status in status_names, f"unknown status `{status}` in entry `{entry['key']}`"


def test_planned_and_implemented_entries_have_expected_metadata() -> None:
    """Planned entries should point to a story; implemented entries should point to source."""
    schema = _load_schema()
    entries = schema["entries"]

    for entry in entries:
        status = entry["status"]
        key = entry["key"]
        if status == "planned":
            assert entry.get("planned_story"), f"planned entry `{key}` missing planned_story"
        if status == "implemented":
            assert entry.get("source"), f"implemented entry `{key}` missing source"


def test_registry_examples_include_valid_and_invalid_shapes() -> None:
    """Examples should include both valid and intentionally invalid records."""
    schema = _load_schema()
    examples = schema.get("examples")
    assert isinstance(examples, dict), "examples must be a mapping"

    valid_entry = examples.get("valid_entry")
    invalid_entry = examples.get("invalid_entry_missing_status")
    assert isinstance(valid_entry, dict), "valid_entry example must be present"
    assert isinstance(invalid_entry, dict), "invalid_entry_missing_status example must be present"

    required_fields = set(schema["required_entry_fields"])
    assert required_fields.issubset(valid_entry.keys()), "valid_entry must include required fields"
    assert "status" not in invalid_entry, "invalid example should intentionally omit status"


def test_registry_covers_narration_profile_controls() -> None:
    """Registry should include each narration profile control key."""
    schema = _load_schema()
    params = _load_narration_params()

    controls = params.get("narration_profile_controls")
    assert isinstance(controls, dict) and controls, "narration_profile_controls must be a non-empty mapping"

    registered_keys = {
        entry["key"]
        for entry in schema["entries"]
        if isinstance(entry, dict) and isinstance(entry.get("key"), str)
    }
    for control_key in controls.keys():
        dotted = f"narration_profile_controls.{control_key}"
        assert dotted in registered_keys, f"registry missing narration profile control key `{dotted}`"


def test_registry_covers_required_manifest_fields() -> None:
    """Required manifest runtime fields should all be represented in registry entries."""
    schema = _load_schema()
    params = _load_narration_params()

    runtime_variability = params.get("runtime_variability")
    assert isinstance(runtime_variability, dict)
    required_fields = runtime_variability.get("required_manifest_fields")
    assert isinstance(required_fields, list) and required_fields

    registered_keys = {
        entry["key"]
        for entry in schema["entries"]
        if isinstance(entry, dict) and isinstance(entry.get("key"), str)
    }
    for field_name in required_fields:
        assert isinstance(field_name, str) and field_name.strip()
        assert field_name in registered_keys, f"registry missing required manifest field `{field_name}`"
