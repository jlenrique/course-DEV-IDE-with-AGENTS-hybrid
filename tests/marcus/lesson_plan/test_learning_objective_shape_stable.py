"""Shape-stable contract tests for the LearningObjective family (Story G0-S1).

Per checklist 8 (per-family shape-pin): each model gets its own allowlist so a
single family change fails in isolation. RED-first (written before the entity).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.learning_objective import (
    SCHEMA_VERSION,
    LearningObjective,
    SourceAdequacy,
    SourceRef,
)


def _field_names(model_cls) -> frozenset[str]:
    return frozenset(model_cls.model_fields.keys())


def _required_field_names(model_cls) -> frozenset[str]:
    return frozenset(
        name
        for name, field_info in model_cls.model_fields.items()
        if field_info.is_required()
    )


# --------------------------------------------------------------------------- #
# Field-set allowlists                                                         #
# --------------------------------------------------------------------------- #
LO_EXPECTED_FIELDS = frozenset(
    {
        "objective_id",
        "statement",
        "status",
        "confidence",
        "bloom_level",
        "source_refs",
        "adequacy",
        "origin",
        "recommendation",
    }
)
LO_REQUIRED_FIELDS = frozenset({"objective_id", "statement", "status", "confidence"})

SOURCE_REF_EXPECTED_FIELDS = frozenset({"source_id", "locator", "quoted_span"})
SOURCE_REF_REQUIRED_FIELDS = frozenset({"source_id", "locator", "quoted_span"})

ADEQUACY_EXPECTED_FIELDS = frozenset(
    {"verdict", "rationale", "missing", "suggested_followups"}
)
ADEQUACY_REQUIRED_FIELDS = frozenset({"verdict", "rationale"})


def test_learning_objective_field_set_matches_allowlist() -> None:
    assert _field_names(LearningObjective) == LO_EXPECTED_FIELDS


def test_learning_objective_required_fields_match() -> None:
    assert _required_field_names(LearningObjective) == LO_REQUIRED_FIELDS


def test_source_ref_field_set_matches_allowlist() -> None:
    assert _field_names(SourceRef) == SOURCE_REF_EXPECTED_FIELDS


def test_source_ref_required_fields_match() -> None:
    assert _required_field_names(SourceRef) == SOURCE_REF_REQUIRED_FIELDS


def test_adequacy_field_set_matches_allowlist() -> None:
    assert _field_names(SourceAdequacy) == ADEQUACY_EXPECTED_FIELDS


def test_adequacy_required_fields_match() -> None:
    assert _required_field_names(SourceAdequacy) == ADEQUACY_REQUIRED_FIELDS


# --------------------------------------------------------------------------- #
# Every model carries extra="forbid" + validate_assignment                    #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("model_cls", [LearningObjective, SourceRef, SourceAdequacy])
def test_every_model_forbids_extra_and_validates_assignment(model_cls) -> None:
    assert model_cls.model_config.get("extra") == "forbid"
    assert model_cls.model_config.get("validate_assignment") is True


def test_source_ref_is_frozen_value_object() -> None:
    assert SourceRef.model_config.get("frozen") is True


def test_learning_objective_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        LearningObjective(
            objective_id="obj-1",
            statement="s",
            status="provisional",
            confidence="medium",
            surprise="x",  # type: ignore[call-arg]
        )


def test_objective_id_is_immutable_once_minted() -> None:
    lo = LearningObjective(
        objective_id="obj-1", statement="s", status="provisional", confidence="medium"
    )
    with pytest.raises(ValidationError):
        lo.objective_id = "obj-2"


def test_schema_version_is_module_constant_not_field() -> None:
    # Ratified shape is exact: NO schema_version field on the entity.
    assert "schema_version" not in LearningObjective.model_fields
    assert SCHEMA_VERSION == "1.0"


# --------------------------------------------------------------------------- #
# Free-text verbatim fields carry NO min_length (adversarial battery)         #
# --------------------------------------------------------------------------- #
_ADVERSARIAL_STRINGS = ["", " ", "\t", "\r\n", "🙂", "x", "  lead-trail  "]


@pytest.mark.parametrize("text", _ADVERSARIAL_STRINGS)
def test_statement_is_verbatim_freetext(text: str) -> None:
    lo = LearningObjective(
        objective_id="obj-1", statement=text, status="provisional", confidence="medium"
    )
    assert lo.statement == text


@pytest.mark.parametrize("text", _ADVERSARIAL_STRINGS)
def test_adequacy_rationale_is_verbatim_freetext(text: str) -> None:
    adq = SourceAdequacy(verdict="adequate", rationale=text, missing=[])
    assert adq.rationale == text
