"""AC-T.1 — Component Type Registry shape-pin (snapshot + allowlist + CHANGELOG gate)."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import app.marcus.lesson_plan.component_type_registry as ct_module
from app.marcus.lesson_plan.component_type_registry import (
    COMPONENT_TYPE_REGISTRY,
    SCHEMA_VERSION,
    ComponentTypeEntry,
)
from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY

CHANGELOG = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


# ---------------------------------------------------------------------------
# Allowlists
# ---------------------------------------------------------------------------


EXPECTED_MODULE_PUBLIC_NAMES = {
    "COMPONENT_TYPE_REGISTRY",
    "SCHEMA_VERSION",
    "ComponentTypeEntry",
    "get_component_type_entry",
}


EXPECTED_COMPONENT_TYPE_ENTRY_FIELDS = {
    "component_type_ref",
    "modality_refs",
    "description",
    "prompt_pack_version",
}


EXPECTED_COMPONENT_TYPE_REFS = {
    "narrated-deck",
    "motion-enabled-narrated-lesson",
}


EXPECTED_COMPOSITION = {
    "narrated-deck": ("slides",),
    "motion-enabled-narrated-lesson": ("slides", "blueprint"),
}


# ---------------------------------------------------------------------------
# Module-level surface
# ---------------------------------------------------------------------------


def test_module_all_matches_expected_public_names() -> None:
    actual = set(ct_module.__all__)
    assert actual == EXPECTED_MODULE_PUBLIC_NAMES, (
        f"component_type_registry.py __all__ drift. Missing: "
        f"{EXPECTED_MODULE_PUBLIC_NAMES - actual}. "
        f"New: {actual - EXPECTED_MODULE_PUBLIC_NAMES}."
    )


def test_schema_version_is_1_0() -> None:
    assert SCHEMA_VERSION == "1.0"


# ---------------------------------------------------------------------------
# ComponentTypeEntry shape
# ---------------------------------------------------------------------------


def test_component_type_entry_fields_match_allowlist() -> None:
    actual = set(ComponentTypeEntry.model_fields.keys())
    assert actual == EXPECTED_COMPONENT_TYPE_ENTRY_FIELDS, (
        f"ComponentTypeEntry field drift. Missing: "
        f"{EXPECTED_COMPONENT_TYPE_ENTRY_FIELDS - actual}. "
        f"New: {actual - EXPECTED_COMPONENT_TYPE_ENTRY_FIELDS}."
    )


def test_component_type_entry_config_is_extra_forbid_frozen() -> None:
    cfg = ComponentTypeEntry.model_config
    assert cfg.get("extra") == "forbid"
    assert cfg.get("frozen") is True
    assert cfg.get("validate_assignment") is True


# ---------------------------------------------------------------------------
# COMPONENT_TYPE_REGISTRY shape
# ---------------------------------------------------------------------------


def test_component_type_registry_is_mappingproxy() -> None:
    assert isinstance(COMPONENT_TYPE_REGISTRY, MappingProxyType)


def test_component_type_registry_keys_match_n2_set() -> None:
    assert set(COMPONENT_TYPE_REGISTRY.keys()) == EXPECTED_COMPONENT_TYPE_REFS


def test_component_type_registry_composition_matches_expected() -> None:
    for ct_ref, expected_mrefs in EXPECTED_COMPOSITION.items():
        entry = COMPONENT_TYPE_REGISTRY[ct_ref]
        assert entry.modality_refs == expected_mrefs, (
            f"COMPONENT_TYPE_REGISTRY[{ct_ref!r}].modality_refs drift: "
            f"expected {expected_mrefs}; got {entry.modality_refs}"
        )


def test_every_modality_ref_in_composites_is_registered() -> None:
    """AC-T.3 composition-validity invariant over the seeded registry."""
    for ct_ref, entry in COMPONENT_TYPE_REGISTRY.items():
        for mref in entry.modality_refs:
            assert mref in MODALITY_REGISTRY, (
                f"COMPONENT_TYPE_REGISTRY[{ct_ref!r}].modality_refs contains "
                f"{mref!r} which is not a key in MODALITY_REGISTRY"
            )


# ---------------------------------------------------------------------------
# SCHEMA_CHANGELOG gate
# ---------------------------------------------------------------------------


def test_schema_changelog_pins_component_type_registry_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "Component Type Registry v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin 'Component Type Registry v1.0' — "
        "AC-C.3 requires a per-family entry."
    )
    assert "Story 31-3" in text
