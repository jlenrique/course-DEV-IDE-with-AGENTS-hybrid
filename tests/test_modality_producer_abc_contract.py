"""AC-T.4 — ModalityProducer ABC contract tests.

M-AM-2 matrix enforced:
    (a) Full valid subclass — instantiable.
    (b) Subclass missing modality_ref ClassVar — TypeError at class-def.
    (c) Subclass missing status ClassVar — TypeError at class-def.
    (d) Wrong-type modality_ref (int) — TypeError at class-def.
    (e) Invalid status string — TypeError at class-def.
    (f) Missing produce() — ABC refuses instantiation.
"""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.modality_producer import ModalityProducer
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit, ScopeDecision

# ---------------------------------------------------------------------------
# (a) Full valid subclass — instantiable; smoke-test produce()
# ---------------------------------------------------------------------------


class _ValidProducer(ModalityProducer):
    """Test-only subclass with full valid attrs. NOT exported."""

    modality_ref = "slides"
    status = "ready"

    def produce(self, plan_unit: PlanUnit, context: ProductionContext) -> ProducedAsset:
        return ProducedAsset(
            asset_ref=f"slides-{plan_unit.unit_id}",
            modality_ref=self.modality_ref,
            source_plan_unit_id=plan_unit.unit_id,
            asset_path=f"artifacts/{plan_unit.unit_id}.md",
            fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}",
        )


def _build_minimal_plan_unit(unit_id: str = "gagne-event-3") -> PlanUnit:
    return PlanUnit(
        unit_id=unit_id,
        event_type="gagne-event-3",
        source_fitness_diagnosis="sufficient",
        scope_decision=ScopeDecision(
            state="proposed",
            scope="in-scope",
            proposed_by="system",
        ),
        weather_band="green",
        modality_ref="slides",
        rationale="test-only",
        gaps=[],
        dials=None,
    )


def test_valid_subclass_is_instantiable() -> None:
    producer = _ValidProducer()
    assert isinstance(producer, ModalityProducer)
    # G5 Murat rider: also assert ClassVars are preserved through instantiation.
    assert producer.modality_ref == "slides"
    assert producer.status == "ready"
    assert _ValidProducer.modality_ref == "slides"
    assert _ValidProducer.status == "ready"


def test_valid_subclass_produce_returns_produced_asset() -> None:
    producer = _ValidProducer()
    plan_unit = _build_minimal_plan_unit()
    context = ProductionContext(
        lesson_plan_revision=5,
        lesson_plan_digest="abc123",
    )
    asset = producer.produce(plan_unit, context)
    assert isinstance(asset, ProducedAsset)
    assert asset.source_plan_unit_id == plan_unit.unit_id
    assert asset.fulfills == "gagne-event-3@5"
    assert asset.modality_ref == "slides"
    assert asset.created_at.tzinfo is not None


# ---------------------------------------------------------------------------
# ABC / instantiation rules
# ---------------------------------------------------------------------------


def test_bare_modality_producer_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        ModalityProducer()  # type: ignore[abstract]


def test_subclass_missing_produce_cannot_be_instantiated() -> None:
    """(f) ABC rule: __abstractmethods__ enforcement at instantiation."""

    class MissingProduce(ModalityProducer):
        modality_ref = "slides"
        status = "ready"

    with pytest.raises(TypeError) as exc_info:
        MissingProduce()  # type: ignore[abstract]
    msg = str(exc_info.value)
    assert "produce" in msg or "abstract" in msg.lower()


# ---------------------------------------------------------------------------
# M-AM-2 __init_subclass__ enforcement — class-definition-time failures
# ---------------------------------------------------------------------------


def test_b_missing_modality_ref_raises_at_class_definition() -> None:
    with pytest.raises(TypeError) as exc_info:

        class BadNoModalityRef(ModalityProducer):  # noqa: F841
            status = "ready"

            def produce(self, plan_unit, context):
                ...

    assert "modality_ref" in str(exc_info.value)
    assert "ClassVar[str]" in str(exc_info.value)


def test_c_missing_status_raises_at_class_definition() -> None:
    with pytest.raises(TypeError) as exc_info:

        class BadNoStatus(ModalityProducer):  # noqa: F841
            modality_ref = "slides"

            def produce(self, plan_unit, context):
                ...

    assert "status" in str(exc_info.value)


def test_d_wrong_type_modality_ref_raises_at_class_definition() -> None:
    with pytest.raises(TypeError) as exc_info:

        class BadIntModalityRef(ModalityProducer):  # noqa: F841
            modality_ref = 42  # type: ignore[assignment]
            status = "ready"

            def produce(self, plan_unit, context):
                ...

    assert "modality_ref" in str(exc_info.value)
    assert "str" in str(exc_info.value)


def test_e_invalid_status_raises_at_class_definition() -> None:
    with pytest.raises(TypeError) as exc_info:

        class BadStatus(ModalityProducer):  # noqa: F841
            modality_ref = "slides"
            status = "invalid"  # type: ignore[assignment]

            def produce(self, plan_unit, context):
                ...

    assert "status" in str(exc_info.value)
    assert "invalid" in str(exc_info.value)


def test_e2_status_none_raises() -> None:
    """Belt-and-suspenders: None is in __dict__ but not a valid status."""
    with pytest.raises(TypeError):

        class BadStatusNone(ModalityProducer):  # noqa: F841
            modality_ref = "slides"
            status = None  # type: ignore[assignment]

            def produce(self, plan_unit, context):
                ...


# ---------------------------------------------------------------------------
# Registry-membership note: ABC does NOT enforce registry membership
# ---------------------------------------------------------------------------


def test_abc_does_not_enforce_registry_membership_at_instantiation() -> None:
    """AC-B.3 note: ABC does NOT check MODALITY_REGISTRY membership.

    This is a consumer-site concern. A subclass claiming modality_ref="unknown"
    can still be instantiated at the ABC level — the registry lookup in
    consumer code (see fixture_30_3_marcus_consumer) is where that check lives.
    """

    class UnregisteredModalityProducer(ModalityProducer):
        modality_ref = "not-in-registry-but-a-string"
        status = "ready"

        def produce(self, plan_unit, context):
            return ProducedAsset(
                asset_ref="x",
                modality_ref="slides",  # registry-valid for the asset emit
                source_plan_unit_id=plan_unit.unit_id,
                asset_path="x.md",
                fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}",
            )

    instance = UnregisteredModalityProducer()
    assert instance.modality_ref == "not-in-registry-but-a-string"
