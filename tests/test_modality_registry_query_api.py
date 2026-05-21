"""AC-T.3 — Registry query API + composition validity tests."""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.component_type_registry import (
    COMPONENT_TYPE_REGISTRY,
    ComponentTypeEntry,
    get_component_type_entry,
)
from app.marcus.lesson_plan.modality_registry import (
    MODALITY_REGISTRY,
    ModalityEntry,
    get_modality_entry,
    list_pending_modalities,
    list_ready_modalities,
)

# ---------------------------------------------------------------------------
# get_modality_entry: positive lookups
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "modality_ref, expected_status, expected_producer_class_path",
    [
        ("slides", "ready", None),
        (
            "blueprint",
            "ready",
            "app.marcus.lesson_plan.blueprint_producer.BlueprintProducer",
        ),
        ("leader-guide", "pending", None),
        ("handout", "pending", None),
        ("classroom-exercise", "pending", None),
    ],
)
def test_get_modality_entry_positive_lookup(
    modality_ref: str, expected_status: str, expected_producer_class_path
) -> None:
    entry = get_modality_entry(modality_ref)
    assert entry is not None
    assert isinstance(entry, ModalityEntry)
    assert entry.modality_ref == modality_ref
    assert entry.status == expected_status
    assert entry.producer_class_path == expected_producer_class_path


# ---------------------------------------------------------------------------
# get_modality_entry: negative / edge-case lookups (no raise, no warn, None)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_ref",
    [
        "nonexistent",
        "",
        "SLIDES",  # case-sensitive miss
        "Slides",
        "slides ",  # trailing whitespace
        " slides",  # leading whitespace
        "slide",  # near miss
        "narrated-deck",  # component-type, not modality
    ],
)
def test_get_modality_entry_returns_none_on_unknown(bad_ref: str) -> None:
    assert get_modality_entry(bad_ref) is None


# ---------------------------------------------------------------------------
# list_ready / list_pending
# ---------------------------------------------------------------------------


def test_list_ready_modalities_matches_expected() -> None:
    assert list_ready_modalities() == frozenset({"slides", "blueprint"})


def test_list_pending_modalities_matches_expected() -> None:
    assert list_pending_modalities() == frozenset(
        {"leader-guide", "handout", "classroom-exercise"}
    )


def test_ready_and_pending_partition_the_registry() -> None:
    ready = list_ready_modalities()
    pending = list_pending_modalities()
    assert ready | pending == frozenset(MODALITY_REGISTRY.keys())
    assert ready & pending == frozenset()


def test_list_ready_returns_frozenset() -> None:
    assert isinstance(list_ready_modalities(), frozenset)


def test_list_pending_returns_frozenset() -> None:
    assert isinstance(list_pending_modalities(), frozenset)


# ---------------------------------------------------------------------------
# get_component_type_entry
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ct_ref, expected_modality_refs",
    [
        ("narrated-deck", ("slides",)),
        ("motion-enabled-narrated-lesson", ("slides", "blueprint")),
    ],
)
def test_get_component_type_entry_positive_lookup(
    ct_ref: str, expected_modality_refs: tuple[str, ...]
) -> None:
    entry = get_component_type_entry(ct_ref)
    assert entry is not None
    assert isinstance(entry, ComponentTypeEntry)
    assert entry.component_type_ref == ct_ref
    assert entry.modality_refs == expected_modality_refs


@pytest.mark.parametrize(
    "bad_ref",
    [
        "nonexistent",
        "",
        "NARRATED-DECK",
        "narrated_deck",
        "slides",  # modality, not component-type
    ],
)
def test_get_component_type_entry_returns_none_on_unknown(bad_ref: str) -> None:
    assert get_component_type_entry(bad_ref) is None


# ---------------------------------------------------------------------------
# Composition validity parametrized over all component types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ct_ref", sorted(COMPONENT_TYPE_REGISTRY.keys()))
def test_every_composite_references_only_registered_modalities(
    ct_ref: str,
) -> None:
    """AC-B.2 invariant + AC-T.3 composition validity."""
    entry = COMPONENT_TYPE_REGISTRY[ct_ref]
    for mref in entry.modality_refs:
        assert mref in MODALITY_REGISTRY, (
            f"{ct_ref}.modality_refs contains {mref!r} not in MODALITY_REGISTRY"
        )


# ---------------------------------------------------------------------------
# AC-C.6 invariant (G6 MUST-FIX — Acceptance Auditor): status=="pending"
# implies producer_class_path is None
# ---------------------------------------------------------------------------


def test_ac_c_6_pending_status_implies_null_producer_class_path() -> None:
    """AC-C.6: model_validator rejects pending + non-null producer_class_path."""
    from pydantic import ValidationError

    from app.marcus.lesson_plan.modality_registry import ModalityEntry

    with pytest.raises(ValidationError) as exc_info:
        ModalityEntry(
            modality_ref="leader-guide",
            status="pending",
            producer_class_path="some.Producer",
            description="",
        )
    msg = str(exc_info.value)
    assert "pending" in msg
    assert "producer_class_path" in msg


def test_ac_c_6_ready_may_have_null_producer_class_path() -> None:
    """AC-C.6: ready+None is legal (backfill pattern for Gary/slides + 31-4)."""
    from app.marcus.lesson_plan.modality_registry import ModalityEntry

    entry = ModalityEntry(
        modality_ref="slides",
        status="ready",
        producer_class_path=None,
        description="",
    )
    assert entry.producer_class_path is None


def test_ac_c_6_ready_may_have_dotted_producer_class_path() -> None:
    """AC-C.6: ready+non-null is legal (post-backfill state)."""
    from app.marcus.lesson_plan.modality_registry import ModalityEntry

    entry = ModalityEntry(
        modality_ref="slides",
        status="ready",
        producer_class_path="x.y.Producer",
        description="",
    )
    assert entry.producer_class_path == "x.y.Producer"


# ---------------------------------------------------------------------------
# ProductionContext negative construction (G6 SHOULD-FIX — Acceptance Auditor)
# ---------------------------------------------------------------------------


def test_production_context_rejects_negative_revision() -> None:
    from pydantic import ValidationError

    from app.marcus.lesson_plan.produced_asset import ProductionContext

    with pytest.raises(ValidationError):
        ProductionContext(lesson_plan_revision=-1, lesson_plan_digest="x")


def test_production_context_rejects_empty_digest() -> None:
    from pydantic import ValidationError

    from app.marcus.lesson_plan.produced_asset import ProductionContext

    with pytest.raises(ValidationError):
        ProductionContext(lesson_plan_revision=0, lesson_plan_digest="")


def test_production_context_accepts_zero_revision_bootstrap() -> None:
    from app.marcus.lesson_plan.produced_asset import ProductionContext

    ctx = ProductionContext(lesson_plan_revision=0, lesson_plan_digest="x")
    assert ctx.lesson_plan_revision == 0


def test_component_type_entry_rejects_unregistered_modality_at_construction() -> None:
    """Defense in depth: Literal validation + model_validator both reject.

    At the Literal layer (ModalityRef closed set), "unregistered-modality"
    fails first. This test asserts the rejection happens — the surface layer
    is irrelevant to the consumer. The model_validator in
    ComponentTypeEntry is defense-in-depth in case ``ModalityRef`` is widened
    without updating the registry.
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        ComponentTypeEntry(
            component_type_ref="bogus",
            modality_refs=("slides", "unregistered-modality"),  # type: ignore[arg-type]
            description="",
            prompt_pack_version=None,
        )
    # Error mentions the bad value OR the closed set OR the registry check.
    msg = str(exc_info.value)
    assert (
        "unregistered-modality" in msg
        or "not a key in MODALITY_REGISTRY" in msg
    )
