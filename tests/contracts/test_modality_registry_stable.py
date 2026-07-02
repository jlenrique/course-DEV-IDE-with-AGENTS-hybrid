"""AC-T.1 — Modality Registry shape-pin (snapshot + allowlist + CHANGELOG gate).

Per R2 rider AM-1 carry-forward on 31-1/31-2: three separate contract files,
one per shape family. This file pins ``modality_registry``.

Any drift without a corresponding SCHEMA_CHANGELOG entry OR allowlist update
here fails the test.
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import get_args

import app.marcus.lesson_plan.modality_registry as modality_registry_module
from app.marcus.lesson_plan.modality_registry import (
    MODALITY_REGISTRY,
    SCHEMA_VERSION,
    ModalityEntry,
    ModalityRef,
)

CHANGELOG = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


# ---------------------------------------------------------------------------
# Allowlists (snapshot surface)
# ---------------------------------------------------------------------------


EXPECTED_MODULE_PUBLIC_NAMES = {
    "MODALITY_REGISTRY",
    "SCHEMA_VERSION",
    "ModalityEntry",
    "ModalityRef",
    "get_modality_entry",
    "list_pending_modalities",
    "list_ready_modalities",
}


EXPECTED_MODALITY_ENTRY_FIELDS = {
    "modality_ref",
    "status",
    "producer_class_path",
    "description",
}


EXPECTED_MODALITY_REFS = {
    "slides",
    "blueprint",
    "leader-guide",
    "handout",
    "classroom-exercise",
    # "workbook" — governed AC-C.4 widening at Braid S2 (2cac27b9,
    # 2026-06-25): SCHEMA_CHANGELOG "Modality Registry v1.1" entry +
    # spec-braid-s2-workbook-producer.md. Repin per
    # contracts-triage-ledger-2026-07-02 rows 8-10.
    "workbook",
}


EXPECTED_READY_MODALITIES = {"slides", "blueprint", "workbook"}
EXPECTED_PENDING_MODALITIES = {"leader-guide", "handout", "classroom-exercise"}


# ---------------------------------------------------------------------------
# Module-level surface
# ---------------------------------------------------------------------------


def test_module_all_matches_expected_public_names() -> None:
    actual = set(modality_registry_module.__all__)
    assert actual == EXPECTED_MODULE_PUBLIC_NAMES, (
        f"modality_registry.py __all__ drift. Missing: "
        f"{EXPECTED_MODULE_PUBLIC_NAMES - actual}. "
        f"New: {actual - EXPECTED_MODULE_PUBLIC_NAMES}. Update SCHEMA_CHANGELOG."
    )


def test_schema_version_is_1_1() -> None:
    # 1.0 -> 1.1 governed bump at Braid S2 (2cac27b9); SCHEMA_CHANGELOG
    # "Modality Registry v1.1 - 2026-06-25 - Braid S2 Workbook Producer".
    assert SCHEMA_VERSION == "1.1"


def test_modality_ref_literal_closed_set() -> None:
    actual = set(get_args(ModalityRef))
    assert actual == EXPECTED_MODALITY_REFS, (
        f"ModalityRef drift: {actual}. Widening requires ruling amendment + "
        f"SCHEMA_CHANGELOG bump per AC-C.4."
    )


# ---------------------------------------------------------------------------
# ModalityEntry shape
# ---------------------------------------------------------------------------


def test_modality_entry_fields_match_allowlist() -> None:
    actual = set(ModalityEntry.model_fields.keys())
    assert actual == EXPECTED_MODALITY_ENTRY_FIELDS, (
        f"ModalityEntry field drift. Missing: "
        f"{EXPECTED_MODALITY_ENTRY_FIELDS - actual}. "
        f"New: {actual - EXPECTED_MODALITY_ENTRY_FIELDS}."
    )


def test_modality_entry_config_is_extra_forbid_frozen() -> None:
    cfg = ModalityEntry.model_config
    assert cfg.get("extra") == "forbid"
    assert cfg.get("frozen") is True
    assert cfg.get("validate_assignment") is True


# ---------------------------------------------------------------------------
# MODALITY_REGISTRY shape
# ---------------------------------------------------------------------------


def test_modality_registry_is_mappingproxy() -> None:
    assert isinstance(MODALITY_REGISTRY, MappingProxyType)


def test_modality_registry_key_set_matches_expected() -> None:
    assert set(MODALITY_REGISTRY.keys()) == EXPECTED_MODALITY_REFS


def test_modality_registry_status_split_matches_expected() -> None:
    ready = {k for k, v in MODALITY_REGISTRY.items() if v.status == "ready"}
    pending = {k for k, v in MODALITY_REGISTRY.items() if v.status == "pending"}
    assert ready == EXPECTED_READY_MODALITIES
    assert pending == EXPECTED_PENDING_MODALITIES


def test_producer_class_paths_match_current_mvp_state() -> None:
    """31-4 backfills blueprint; slides/pending entries still remain null."""
    assert MODALITY_REGISTRY["slides"].producer_class_path is None
    assert (
        MODALITY_REGISTRY["blueprint"].producer_class_path
        == "app.marcus.lesson_plan.blueprint_producer.BlueprintProducer"
    )
    for key in EXPECTED_PENDING_MODALITIES:
        assert MODALITY_REGISTRY[key].producer_class_path is None, (
            f"MODALITY_REGISTRY[{key!r}].producer_class_path must remain None "
            f"for pending modalities; got "
            f"{MODALITY_REGISTRY[key].producer_class_path!r}"
        )


# ---------------------------------------------------------------------------
# SCHEMA_CHANGELOG gate
# ---------------------------------------------------------------------------


def test_schema_changelog_pins_modality_registry_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "Modality Registry v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin 'Modality Registry v1.0' — per "
        "AC-C.3 the modality registry requires its own changelog entry."
    )
    assert "Story 31-3" in text, (
        "Changelog entry must attribute to Story 31-3"
    )
