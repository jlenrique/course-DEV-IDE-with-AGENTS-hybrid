"""AC-T.2 — Registry immutability matrix for MODALITY_REGISTRY + COMPONENT_TYPE_REGISTRY.

Parametrized over both registries × every attempted mutation operation. Each
expected to raise (TypeError from MappingProxyType or AttributeError from
missing mutation methods).
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from app.marcus.lesson_plan.component_type_registry import (
    COMPONENT_TYPE_REGISTRY,
    ComponentTypeEntry,
)
from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY, ModalityEntry

REGISTRIES_FIXTURE = pytest.mark.parametrize(
    "registry, known_key",
    [
        (MODALITY_REGISTRY, "slides"),
        (COMPONENT_TYPE_REGISTRY, "narrated-deck"),
    ],
    ids=["MODALITY_REGISTRY", "COMPONENT_TYPE_REGISTRY"],
)


@REGISTRIES_FIXTURE
def test_registry_is_mappingproxy(registry, known_key: str) -> None:  # noqa: ARG001
    assert isinstance(registry, MappingProxyType)


@REGISTRIES_FIXTURE
def test_setitem_raises_type_error(registry, known_key: str) -> None:
    with pytest.raises(TypeError):
        registry[known_key] = None  # type: ignore[index]


@REGISTRIES_FIXTURE
def test_setitem_new_key_raises_type_error(registry, known_key: str) -> None:  # noqa: ARG001
    with pytest.raises(TypeError):
        registry["brand_new_key_never_seen"] = None  # type: ignore[index]


@REGISTRIES_FIXTURE
def test_delitem_raises_type_error(registry, known_key: str) -> None:
    with pytest.raises(TypeError):
        del registry[known_key]  # type: ignore[attr-defined]


@REGISTRIES_FIXTURE
def test_clear_raises_attribute_error(registry, known_key: str) -> None:  # noqa: ARG001
    with pytest.raises(AttributeError):
        registry.clear()  # type: ignore[attr-defined]


@REGISTRIES_FIXTURE
def test_update_raises_attribute_error(registry, known_key: str) -> None:  # noqa: ARG001
    with pytest.raises(AttributeError):
        registry.update({"x": None})  # type: ignore[attr-defined]


@REGISTRIES_FIXTURE
def test_pop_raises_attribute_error(registry, known_key: str) -> None:
    with pytest.raises(AttributeError):
        registry.pop(known_key)  # type: ignore[attr-defined]


@REGISTRIES_FIXTURE
def test_popitem_raises_attribute_error(registry, known_key: str) -> None:  # noqa: ARG001
    with pytest.raises(AttributeError):
        registry.popitem()  # type: ignore[attr-defined]


@REGISTRIES_FIXTURE
def test_setdefault_raises_attribute_error(registry, known_key: str) -> None:  # noqa: ARG001
    with pytest.raises(AttributeError):
        registry.setdefault("x", None)  # type: ignore[attr-defined]


@REGISTRIES_FIXTURE
def test_attribute_set_raises(registry, known_key: str) -> None:  # noqa: ARG001
    """Attribute assignment on a MappingProxyType raises AttributeError."""
    with pytest.raises(AttributeError):
        registry.foo = "bar"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Entry-level immutability: frozen=True on ModalityEntry + ComponentTypeEntry
# ---------------------------------------------------------------------------


def test_modality_entry_is_frozen_rejects_mutation() -> None:
    """Mutating a ModalityEntry field should raise (frozen=True)."""
    entry = MODALITY_REGISTRY["slides"]
    with pytest.raises((TypeError, ValueError)):
        entry.modality_ref = "blueprint"  # type: ignore[misc]


def test_component_type_entry_is_frozen_rejects_mutation() -> None:
    entry = COMPONENT_TYPE_REGISTRY["narrated-deck"]
    with pytest.raises((TypeError, ValueError)):
        entry.component_type_ref = "hijacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Type assertions
# ---------------------------------------------------------------------------


def test_modality_registry_values_are_modality_entries() -> None:
    for entry in MODALITY_REGISTRY.values():
        assert isinstance(entry, ModalityEntry)


def test_component_type_registry_values_are_component_type_entries() -> None:
    for entry in COMPONENT_TYPE_REGISTRY.values():
        assert isinstance(entry, ComponentTypeEntry)
