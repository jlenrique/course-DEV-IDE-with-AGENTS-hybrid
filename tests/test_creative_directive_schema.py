"""Contract checks for Creative Director directive schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts.utilities.creative_directive_validator import validate_creative_directive

JSON_SCHEMA_PATH = Path("state/config/schemas/creative-directive.schema.json")
YAML_SCHEMA_PATH = Path("state/config/schemas/creative-directive.schema.yaml")
NARRATION_PARAMS_PATH = Path("state/config/narration-script-parameters.yaml")


def _load_json_schema() -> dict[str, Any]:
    payload = json.loads(JSON_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _load_yaml_schema() -> dict[str, Any]:
    payload = yaml.safe_load(YAML_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _load_narration_params() -> dict[str, Any]:
    payload = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_json_schema_has_required_contract_shape() -> None:
    schema = _load_json_schema()
    required = set(schema["required"])
    assert required == {
        "schema_version",
        "experience_profile",
        "slide_mode_proportions",
        "narration_profile_controls",
        "creative_rationale",
    }
    assert schema["additionalProperties"] is False


def test_yaml_schema_has_matching_required_top_level_fields() -> None:
    schema_json = _load_json_schema()
    schema_yaml = _load_yaml_schema()
    assert set(schema_yaml["required_top_level_fields"]) == set(schema_json["required"])


def test_slide_mode_required_keys_match_between_schemas() -> None:
    schema_json = _load_json_schema()
    schema_yaml = _load_yaml_schema()
    json_keys = set(schema_json["properties"]["slide_mode_proportions"]["required"])
    yaml_keys = set(schema_yaml["slide_mode_proportions"]["required_keys"])
    assert json_keys == yaml_keys == {"literal-text", "literal-visual", "creative"}


def test_narration_profile_control_keys_match_expanded_contract() -> None:
    schema_json = _load_json_schema()
    schema_yaml = _load_yaml_schema()
    params = _load_narration_params()
    expected = set(params["narration_profile_controls"].keys())
    json_keys = set(schema_json["properties"]["narration_profile_controls"]["required"])
    yaml_keys = set(schema_yaml["narration_profile_controls"]["required_keys"])
    assert json_keys == yaml_keys == expected


def test_slide_mode_sum_rule_accepts_valid_distribution() -> None:
    directive = {
        "schema_version": "1.0",
        "experience_profile": "visual-led",
        "slide_mode_proportions": {
            "literal-text": 0.15,
            "literal-visual": 0.25,
            "creative": 0.60,
        },
        "narration_profile_controls": {
            "narrator_source_authority": "source-grounded",
            "slide_content_density": "adaptive",
            "elaboration_budget": "medium",
            "connective_weight": "balanced",
            "callback_frequency": "moderate",
            "visual_narration_coupling": "balanced",
            "rhetorical_richness": "balanced",
            "vocabulary_register": "professional",
            "arc_awareness": "medium",
            "narrative_tension": "medium",
            "emotional_coloring": "neutral",
        },
        "creative_rationale": "Emphasize visual motion for engagement.",
    }
    assert validate_creative_directive(directive) == []


@pytest.mark.parametrize(
    "modes",
    [
        {"literal-text": 0.2, "literal-visual": 0.2, "creative": 0.2},
        {"literal-text": True, "literal-visual": 0.4, "creative": 0.6},
    ],
)
def test_slide_mode_sum_rule_rejects_invalid_distribution(modes: dict[str, Any]) -> None:
    directive = {
        "schema_version": "1.0",
        "experience_profile": "text-led",
        "slide_mode_proportions": modes,
        "narration_profile_controls": {
            "narrator_source_authority": "slide-led",
            "slide_content_density": "dense",
            "elaboration_budget": "low",
            "connective_weight": "balanced",
            "callback_frequency": "moderate",
            "visual_narration_coupling": "balanced",
            "rhetorical_richness": "balanced",
            "vocabulary_register": "professional",
            "arc_awareness": "medium",
            "narrative_tension": "medium",
            "emotional_coloring": "neutral",
        },
        "creative_rationale": "Prioritize literal textual continuity.",
    }
    errors = validate_creative_directive(directive)
    assert errors
