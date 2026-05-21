from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

import pytest
from pydantic import BaseModel, ConfigDict

from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)


class SyntheticVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: UUID
    surface_id: Literal["synthetic_surface"] = "synthetic_surface"
    verb: Literal["approve", "edit", "reject"]
    operator_id: str
    submitted_at: datetime
    decision_card_digest: str
    edit_payload: dict | None = None
    reject_reason: str | None = None


class MissingDigestVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: UUID
    surface_id: Literal["synthetic_surface"] = "synthetic_surface"
    verb: Literal["approve", "edit", "reject"]
    operator_id: str
    submitted_at: datetime


def test_operator_verdict_harness_accepts_conforming_variant() -> None:
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=SyntheticVerdict,
        surface_id="synthetic_surface",
    )


def test_operator_verdict_harness_rejects_shape_deviation() -> None:
    with pytest.raises(AssertionError, match="decision_card_digest"):
        assert_operator_verdict_schema_stable_across_transports(
            verdict_class=MissingDigestVerdict,
            surface_id="synthetic_surface",
        )


def test_operator_verdict_harness_rejects_surface_mismatch() -> None:
    with pytest.raises(AssertionError):
        assert_operator_verdict_schema_stable_across_transports(
            verdict_class=SyntheticVerdict,
            surface_id="different_surface",
        )


def test_synthetic_verdict_runtime_payload_is_valid() -> None:
    verdict = SyntheticVerdict(
        run_id="11111111-1111-4111-8111-111111111111",
        verb="approve",
        operator_id="operator_1",
        submitted_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        decision_card_digest="a" * 64,
    )

    assert verdict.surface_id == "synthetic_surface"
