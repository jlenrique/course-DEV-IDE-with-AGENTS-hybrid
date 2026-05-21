"""`ModelSelectionPolicy` — auto-select rules for the cascade fourth level (D2).

When the cascade exhausts per-call → per-specialist → registry-default
without resolution (or when `auto_select_enabled=False` blocks the
default), the selector consults this policy. Each rule is a `when`
predicate (matched against a context dict) + a preferred tier + an
ordered fallback chain of model_ids.

Conflicting rules (overlapping `when` predicates with incompatible
`prefer_tier`) surface as named validation errors at YAML load time —
silent overrides are forbidden per AC-1.3-B.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.registry import ModelTier

PolicyPredicateKey = Literal["specialist_id", "tier_request"]
"""Closed enum: predicate keys the selector may match against."""


class SelectionRule(BaseModel):
    """One auto-select rule."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    rule_id: str = Field(
        ...,
        min_length=1,
        description="Stable rule identifier; surfaced in named-conflict errors.",
    )
    when: dict[PolicyPredicateKey, str] = Field(
        ...,
        description=(
            "Predicate map (key → required value). All keys must match for the "
            "rule to fire; empty dict matches universally."
        ),
    )
    prefer_tier: ModelTier = Field(
        ...,
        description="Preferred tier to resolve from when this rule matches.",
    )
    fallback_chain: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Ordered model_id fallback chain; selector tries each in order if "
            "preferred-tier resolution fails."
        ),
    )


class ModelSelectionPolicy(BaseModel):
    """Auto-select policy = ordered list of rules.

    Cross-field invariant: rules are uniquely identified by `rule_id`; two
    rules with identical `when` predicates but different `prefer_tier`
    surface as a named conflict at construction time.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    rules: list[SelectionRule] = Field(
        default_factory=list,
        description="Ordered selection rules; first matching rule wins.",
    )

    @model_validator(mode="after")
    def _check_no_silent_conflicts(self) -> ModelSelectionPolicy:
        seen_predicates: dict[tuple[tuple[str, str], ...], tuple[str, str]] = {}
        seen_ids: set[str] = set()
        for rule in self.rules:
            if rule.rule_id in seen_ids:
                raise ValueError(
                    f"ModelSelectionPolicy: duplicate rule_id={rule.rule_id!r}; "
                    "rule_id must be unique per policy."
                )
            seen_ids.add(rule.rule_id)
            key = tuple(sorted(rule.when.items()))
            if key in seen_predicates:
                prior_id, prior_tier = seen_predicates[key]
                if prior_tier != rule.prefer_tier:
                    raise ValueError(
                        f"ModelSelectionPolicy: conflicting rules "
                        f"{prior_id!r} (prefer_tier={prior_tier!r}) and "
                        f"{rule.rule_id!r} (prefer_tier={rule.prefer_tier!r}) "
                        f"share predicate {dict(key)!r}; resolve by removing the "
                        "duplicate or making predicates non-overlapping."
                    )
            else:
                seen_predicates[key] = (rule.rule_id, rule.prefer_tier)
        return self


__all__ = ["ModelSelectionPolicy", "PolicyPredicateKey", "SelectionRule"]
