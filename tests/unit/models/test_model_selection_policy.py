"""Shape-pin tests for `ModelSelectionPolicy` (Story 1.3 AC-1.3-B)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.selection_policy import ModelSelectionPolicy, SelectionRule

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "models"


def _golden() -> dict[str, Any]:
    return json.loads(
        (_FIXTURES / "golden_model_selection_policy.json").read_text(encoding="utf-8")
    )


def test_round_trip_against_golden_fixture() -> None:
    golden = _golden()
    rebuilt = ModelSelectionPolicy.model_validate(golden).model_dump(mode="json")
    assert rebuilt == golden


def test_forbids_extra_fields_on_policy() -> None:
    payload = _golden()
    payload["bogus"] = True
    with pytest.raises(ValidationError):
        ModelSelectionPolicy.model_validate(payload)


def test_forbids_extra_fields_on_rule() -> None:
    payload = {
        "rule_id": "x",
        "when": {},
        "prefer_tier": "fast",
        "fallback_chain": ["gpt-5-nano"],
        "bogus": True,
    }
    with pytest.raises(ValidationError):
        SelectionRule.model_validate(payload)


def test_duplicate_rule_id_rejected() -> None:
    payload = {
        "rules": [
            {
                "rule_id": "dup",
                "when": {"tier_request": "fast"},
                "prefer_tier": "fast",
                "fallback_chain": ["gpt-5-nano"],
            },
            {
                "rule_id": "dup",
                "when": {"tier_request": "reasoning"},
                "prefer_tier": "reasoning",
                "fallback_chain": ["gpt-5"],
            },
        ]
    }
    with pytest.raises(ValidationError) as exc_info:
        ModelSelectionPolicy.model_validate(payload)
    assert "duplicate rule_id" in str(exc_info.value)


def test_conflicting_predicate_with_different_tier_rejected() -> None:
    payload = {
        "rules": [
            {
                "rule_id": "rule-a",
                "when": {"tier_request": "fast"},
                "prefer_tier": "fast",
                "fallback_chain": ["gpt-5-nano"],
            },
            {
                "rule_id": "rule-b",
                "when": {"tier_request": "fast"},
                "prefer_tier": "reasoning",  # CONFLICT with rule-a
                "fallback_chain": ["gpt-5"],
            },
        ]
    }
    with pytest.raises(ValidationError) as exc_info:
        ModelSelectionPolicy.model_validate(payload)
    assert "conflicting rules" in str(exc_info.value)


def test_same_predicate_same_tier_accepted() -> None:
    """Identical predicates + identical tier are not a conflict (idempotent)."""
    payload = {
        "rules": [
            {
                "rule_id": "rule-a",
                "when": {"tier_request": "fast"},
                "prefer_tier": "fast",
                "fallback_chain": ["gpt-5-nano"],
            },
            {
                "rule_id": "rule-b",
                "when": {"tier_request": "fast"},
                "prefer_tier": "fast",
                "fallback_chain": ["gpt-5-nano"],
            },
        ]
    }
    policy = ModelSelectionPolicy.model_validate(payload)
    assert len(policy.rules) == 2


def test_fallback_chain_min_length_one() -> None:
    payload = {
        "rules": [
            {
                "rule_id": "x",
                "when": {},
                "prefer_tier": "fast",
                "fallback_chain": [],  # empty = invalid
            }
        ]
    }
    with pytest.raises(ValidationError):
        ModelSelectionPolicy.model_validate(payload)


def test_rule_is_frozen() -> None:
    rule = SelectionRule.model_validate(
        {
            "rule_id": "x",
            "when": {},
            "prefer_tier": "fast",
            "fallback_chain": ["gpt-5-nano"],
        }
    )
    with pytest.raises(ValidationError):
        rule.prefer_tier = "reasoning"  # frozen=True forbids


def test_canonical_selection_policy_yaml_loads() -> None:
    """The shipped selection_policy.yaml IS valid against the schema (drift guard)."""
    import yaml

    from app.models.selector import SELECTION_POLICY_PATH

    raw = yaml.safe_load(SELECTION_POLICY_PATH.read_text(encoding="utf-8"))
    policy = ModelSelectionPolicy.model_validate(raw)
    assert len(policy.rules) >= 1
