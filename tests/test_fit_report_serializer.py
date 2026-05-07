"""Tests for fit_report.serialize/deserialize_fit_report (Story 29-1, AC-T.4/5)."""

from __future__ import annotations

import random
from datetime import UTC, datetime

import pytest

from app.marcus.lesson_plan.fit_report import (
    deserialize_fit_report,
    serialize_fit_report,
)
from app.marcus.lesson_plan.schema import FitDiagnosis, FitReport, PlanRef


def _base_report(
    *,
    diagnoses: list[FitDiagnosis] | None = None,
) -> FitReport:
    return FitReport(
        source_ref="tests/fixtures/trial_corpus/canonical.md",
        plan_ref=PlanRef(
            lesson_plan_revision=3,
            lesson_plan_digest="d" * 64,
        ),
        diagnoses=diagnoses if diagnoses is not None else [],
        generated_at=datetime(2026, 4, 18, 12, 0, 0, tzinfo=UTC),
        irene_budget_ms=1234,
    )


# ---------------------------------------------------------------------------
# AC-T.4 — Serializer determinism (M-1 key-order expansion)
# ---------------------------------------------------------------------------


def test_serialize_fit_report_deterministic() -> None:
    """AC-T.4 — byte-identical across 100 invocations + key-order-independent.

    Per M-1 rider: three key-order cases are covered — forward insertion,
    reverse insertion, and fixed-seed shuffled. Without the fixed seed,
    the shuffle itself would be non-deterministic on CI.
    """
    report = _base_report(
        diagnoses=[
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="ok",
            ),
        ],
    )

    # 100-invocation byte-identity pin.
    expected = serialize_fit_report(report)
    for _ in range(100):
        assert serialize_fit_report(report) == expected

    # Key-order-independent pin — construct the same report from three
    # different field-set orders in the input dict and confirm identical
    # canonical output.
    base_dict = report.model_dump(mode="json")
    forward_keys = list(base_dict.keys())
    reverse_keys = list(reversed(forward_keys))
    rng = random.Random(42)  # fixed seed → deterministic on CI
    shuffled_keys = list(forward_keys)
    rng.shuffle(shuffled_keys)

    for order in (forward_keys, reverse_keys, shuffled_keys):
        reordered = {k: base_dict[k] for k in order}
        reconstructed = FitReport.model_validate(reordered)
        assert serialize_fit_report(reconstructed) == expected


# ---------------------------------------------------------------------------
# AC-T.5 — serialize/deserialize round-trip identity (six-case matrix)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "diagnoses",
    [
        [],
        [
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="ok",
            ),
        ],
        [
            FitDiagnosis(
                unit_id=f"gagne-event-{n}",
                fitness="sufficient",
                commentary=f"unit {n}",
            )
            for n in range(1, 4)
        ],
        [
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="ok",
                recommended_scope_decision=None,
                recommended_weather_band=None,
            ),
        ],
        [
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="Unicode commentary: \u6e2c\u8a66 \U0001f52c",
            ),
        ],
        [
            FitDiagnosis(
                unit_id="gagne-event-1",
                fitness="sufficient",
                commentary="line 1\nline 2\nline 3",
            ),
        ],
    ],
    ids=[
        "empty-diagnoses",
        "single-diagnosis",
        "multiple-diagnoses",
        "all-optional-None",
        "unicode-commentary",
        "multi-line-commentary",
    ],
)
def test_serialize_deserialize_roundtrip(
    diagnoses: list[FitDiagnosis],
) -> None:
    """AC-T.5 — serialize(deserialize(serialize(r))) == serialize(r) byte-identical."""
    report = _base_report(diagnoses=diagnoses)
    serialized = serialize_fit_report(report)
    deserialized = deserialize_fit_report(serialized)
    reserialized = serialize_fit_report(deserialized)
    assert reserialized == serialized
