"""AC-T.1 — ModalityProducer ABC + ProductionContext + ProducedAsset shape-pin."""

from __future__ import annotations

import inspect
from pathlib import Path

import app.marcus.lesson_plan.modality_producer as mp_module
import app.marcus.lesson_plan.produced_asset as pa_module
from app.marcus.lesson_plan.modality_producer import (
    SCHEMA_VERSION as MP_SCHEMA_VERSION,
)
from app.marcus.lesson_plan.modality_producer import (
    ModalityProducer,
)
from app.marcus.lesson_plan.produced_asset import (
    SCHEMA_VERSION as PA_SCHEMA_VERSION,
)
from app.marcus.lesson_plan.produced_asset import (
    ProducedAsset,
    ProductionContext,
)

CHANGELOG = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


# ---------------------------------------------------------------------------
# Allowlists
# ---------------------------------------------------------------------------


EXPECTED_MP_MODULE_PUBLIC_NAMES = {"SCHEMA_VERSION", "ModalityProducer"}
EXPECTED_PA_MODULE_PUBLIC_NAMES = {
    "SCHEMA_VERSION",
    "ProducedAsset",
    "ProductionContext",
}


EXPECTED_PRODUCTION_CONTEXT_FIELDS = {
    "lesson_plan_revision",
    "lesson_plan_digest",
}


EXPECTED_PRODUCED_ASSET_FIELDS = {
    "asset_ref",
    "modality_ref",
    "source_plan_unit_id",
    "created_at",
    "asset_path",
    "fulfills",
}


# ---------------------------------------------------------------------------
# Module-level surface
# ---------------------------------------------------------------------------


def test_mp_module_all_matches() -> None:
    actual = set(mp_module.__all__)
    assert actual == EXPECTED_MP_MODULE_PUBLIC_NAMES


def test_pa_module_all_matches() -> None:
    actual = set(pa_module.__all__)
    assert actual == EXPECTED_PA_MODULE_PUBLIC_NAMES


def test_schema_versions_are_1_0() -> None:
    assert MP_SCHEMA_VERSION == "1.0"
    assert PA_SCHEMA_VERSION == "1.0"


# ---------------------------------------------------------------------------
# ModalityProducer ABC surface
# ---------------------------------------------------------------------------


def test_modality_producer_is_abc_with_produce_abstract() -> None:
    from abc import ABC

    assert issubclass(ModalityProducer, ABC)
    # produce is abstract
    assert "produce" in ModalityProducer.__abstractmethods__


def test_produce_signature_is_self_plan_unit_context() -> None:
    sig = inspect.signature(ModalityProducer.produce)
    params = list(sig.parameters.keys())
    assert params == ["self", "plan_unit", "context"], (
        f"ModalityProducer.produce signature drift: {params}"
    )


def test_modality_producer_has_init_subclass_enforcement() -> None:
    """M-AM-2: subclass must wire enforcement; presence is the contract pin."""
    # Declared in the class's own __dict__ (not inherited).
    assert "__init_subclass__" in ModalityProducer.__dict__


# ---------------------------------------------------------------------------
# ProductionContext shape
# ---------------------------------------------------------------------------


def test_production_context_fields_match_allowlist() -> None:
    actual = set(ProductionContext.model_fields.keys())
    assert actual == EXPECTED_PRODUCTION_CONTEXT_FIELDS


def test_production_context_config_is_extra_forbid_frozen() -> None:
    cfg = ProductionContext.model_config
    assert cfg.get("extra") == "forbid"
    assert cfg.get("frozen") is True
    assert cfg.get("validate_assignment") is True


# ---------------------------------------------------------------------------
# ProducedAsset shape
# ---------------------------------------------------------------------------


def test_produced_asset_fields_match_allowlist() -> None:
    actual = set(ProducedAsset.model_fields.keys())
    assert actual == EXPECTED_PRODUCED_ASSET_FIELDS


def test_produced_asset_config_is_extra_forbid_frozen() -> None:
    cfg = ProducedAsset.model_config
    assert cfg.get("extra") == "forbid"
    assert cfg.get("frozen") is True
    assert cfg.get("validate_assignment") is True


# ---------------------------------------------------------------------------
# fulfills regex constant
# ---------------------------------------------------------------------------


def test_fulfills_regex_pattern_pinned() -> None:
    """AC-B.7: the regex pattern is part of the contract surface."""
    from app.marcus.lesson_plan.produced_asset import _FULFILLS_REGEX

    expected = r"^[a-z0-9._-]+@(?:0|[1-9]\d*)$"
    assert _FULFILLS_REGEX.pattern == expected, (
        f"_FULFILLS_REGEX drift: {_FULFILLS_REGEX.pattern!r} != {expected!r}. "
        f"Widening requires SCHEMA_CHANGELOG bump."
    )


# ---------------------------------------------------------------------------
# SCHEMA_CHANGELOG gate
# ---------------------------------------------------------------------------


def test_schema_changelog_pins_modality_producer_abc_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "ModalityProducer ABC v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin 'ModalityProducer ABC v1.0' — "
        "AC-C.3 requires a per-family entry."
    )
    assert "Story 31-3" in text
