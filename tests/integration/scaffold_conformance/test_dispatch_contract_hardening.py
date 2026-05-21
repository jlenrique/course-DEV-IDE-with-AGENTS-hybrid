"""Story 2b.15 dispatch-contract-hardening test surface.

Per AC-A parametrize-collapse (Murat M-R18): one test function per shape
(input / receipt / error) parametrized over 14 specialists = 3 K-floor units
covering 42 schema classes. PLUS dispatch-registry SSOT (existence + R10
invariant + M5 swap-guard) + shared loader smoke + shared sanctum exception
smoke.
"""

from __future__ import annotations

import importlib
from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.models.dispatch import (
    AriaDispatchError,
    AriaDispatchInput,
    AriaDispatchReceipt,
    CdDispatchError,
    CdDispatchInput,
    CdDispatchReceipt,
    DesmondDispatchError,
    DesmondDispatchInput,
    DesmondDispatchReceipt,
    EnriqueDispatchError,
    EnriqueDispatchInput,
    EnriqueDispatchReceipt,
    GaryDispatchError,
    GaryDispatchInput,
    GaryDispatchReceipt,
    IreneDispatchError,
    IreneDispatchInput,
    IreneDispatchReceipt,
    KimDispatchError,
    KimDispatchInput,
    KimDispatchReceipt,
    MiraDispatchError,
    MiraDispatchInput,
    MiraDispatchReceipt,
    QuinnRDispatchError,
    QuinnRDispatchInput,
    QuinnRDispatchReceipt,
    TamaraDispatchError,
    TamaraDispatchInput,
    TamaraDispatchReceipt,
    TracyDispatchError,
    TracyDispatchInput,
    TracyDispatchReceipt,
    VeraDispatchError,
    VeraDispatchInput,
    VeraDispatchReceipt,
    VyxDispatchError,
    VyxDispatchInput,
    VyxDispatchReceipt,
    WandaDispatchError,
    WandaDispatchInput,
    WandaDispatchReceipt,
)
from app.specialists._scaffold.dispatch_loader import load_module
from app.specialists._scaffold.sanctum_exceptions import SanctumLockViolation

# ---------------------------------------------------------------------------
# Per-specialist dispatch family registry (14 specialists × 3 shapes = 42 classes).
# Each entry pins (name, input cls, receipt cls, error cls, receipt-strict-typed-field).
# Receipt-strict-typed-field is the loose-typed return-shape field from R4 deferral
# (2b.1-2b.14) that 2b.15 strict-types per AC-F.
# ---------------------------------------------------------------------------
SPECIALIST_DISPATCH_FAMILIES: tuple[
    tuple[str, type, type, type, str | None], ...
] = (
    ("aria", AriaDispatchInput, AriaDispatchReceipt, AriaDispatchError,
     "aria_storyline_spec"),
    ("cd", CdDispatchInput, CdDispatchReceipt, CdDispatchError, "cd_directive"),
    ("desmond", DesmondDispatchInput, DesmondDispatchReceipt, DesmondDispatchError,
     "desmond_handoff"),
    ("enrique", EnriqueDispatchInput, EnriqueDispatchReceipt, EnriqueDispatchError,
     "enrique_audio"),
    ("gary", GaryDispatchInput, GaryDispatchReceipt, GaryDispatchError,
     "gary_slide_output"),
    # Irene receipt strict-types BOTH irene_lesson_design AND irene_pass_2_envelope
    # per A-2b.14-R2 path-a; the parametrize axis only checks one canonical field.
    ("irene", IreneDispatchInput, IreneDispatchReceipt, IreneDispatchError,
     "irene_lesson_design"),
    ("kim", KimDispatchInput, KimDispatchReceipt, KimDispatchError, "kim_checklist"),
    ("mira", MiraDispatchInput, MiraDispatchReceipt, MiraDispatchError, "mira_prompt_set"),
    ("quinn_r", QuinnRDispatchInput, QuinnRDispatchReceipt, QuinnRDispatchError, "quinn_r_review"),
    ("tamara", TamaraDispatchInput, TamaraDispatchReceipt, TamaraDispatchError,
     "tamara_design_spec"),
    ("tracy", TracyDispatchInput, TracyDispatchReceipt, TracyDispatchError, "tracy_manifest"),
    ("vera", VeraDispatchInput, VeraDispatchReceipt, VeraDispatchError, "vera_finding"),
    ("vyx", VyxDispatchInput, VyxDispatchReceipt, VyxDispatchError, "vyx_storyboard"),
    ("wanda", WandaDispatchInput, WandaDispatchReceipt, WandaDispatchError, "wanda_audio"),
)


def test_dispatch_family_count_matches_roster() -> None:
    """Roster pinned to 14 migrated specialists per A-BLOCKER-roster-math."""
    assert len(SPECIALIST_DISPATCH_FAMILIES) == 14
    names = {entry[0] for entry in SPECIALIST_DISPATCH_FAMILIES}
    assert names == {
        "aria", "cd", "desmond", "enrique", "gary", "irene", "kim", "mira",
        "quinn_r", "tamara", "tracy", "vera", "vyx", "wanda",
    }


@pytest.mark.parametrize(
    "name,input_cls,receipt_cls,error_cls,receipt_field",
    SPECIALIST_DISPATCH_FAMILIES,
    ids=[entry[0] for entry in SPECIALIST_DISPATCH_FAMILIES],
)
def test_specialist_dispatch_input_strict(
    name: str,
    input_cls: type,
    receipt_cls: type,
    error_cls: type,
    receipt_field: str | None,
) -> None:
    """AC-A input-shape pin: each input model is strict (extra=forbid + validate_assignment)."""
    instance = input_cls()
    cfg = instance.model_config
    assert cfg.get("extra") == "forbid"
    assert cfg.get("validate_assignment") is True
    with pytest.raises(ValidationError):
        input_cls(__nonexistent_field__="x")


@pytest.mark.parametrize(
    "name,input_cls,receipt_cls,error_cls,receipt_field",
    SPECIALIST_DISPATCH_FAMILIES,
    ids=[entry[0] for entry in SPECIALIST_DISPATCH_FAMILIES],
)
def test_specialist_dispatch_receipt_strict_types_loose_field(
    name: str,
    input_cls: type,
    receipt_cls: type,
    error_cls: type,
    receipt_field: str | None,
) -> None:
    """AC-F receipt-shape pin: each receipt strict-types its R4 loose-typed return-shape field.

    Verifies the field exists on the receipt model and is optional (None default
    preserves backward-compat with envelope-carrier-hack callers).
    """
    instance = receipt_cls()
    cfg = instance.model_config
    assert cfg.get("extra") == "forbid"
    assert cfg.get("validate_assignment") is True
    if receipt_field is not None:
        assert hasattr(instance, receipt_field), (
            f"{receipt_cls.__name__} missing strict-typed field {receipt_field!r}"
        )
        assert getattr(instance, receipt_field) is None


@pytest.mark.parametrize(
    "name,input_cls,receipt_cls,error_cls,receipt_field",
    SPECIALIST_DISPATCH_FAMILIES,
    ids=[entry[0] for entry in SPECIALIST_DISPATCH_FAMILIES],
)
def test_specialist_dispatch_error_strict(
    name: str,
    input_cls: type,
    receipt_cls: type,
    error_cls: type,
    receipt_field: str | None,
) -> None:
    """AC-A error-shape pin: each error model carries (code, message) and is strict."""
    instance = error_cls(code="E_TEST", message="test")
    assert instance.code == "E_TEST"
    assert instance.message == "test"
    cfg = instance.model_config
    assert cfg.get("extra") == "forbid"
    with pytest.raises(ValidationError):
        error_cls(code="E", message="m", extra_field="x")


def test_dispatch_module_exposes_all_42_classes() -> None:
    """AC-A umbrella import: app.models.dispatch.__all__ surfaces all 42 classes (14 × 3)."""
    module = importlib.import_module("app.models.dispatch")
    assert len(module.__all__) == 42


def test_dispatch_registry_is_structured_production() -> None:
    """Dispatch registry stays structured after the M5 production promotion."""
    payload = yaml.safe_load(
        Path("state/config/dispatch-registry.yaml").read_text(encoding="utf-8")
    )
    assert payload["_status"] == "production"
    assert payload["_lifecycle"]["state"] == "production"
    assert payload["_lifecycle"]["promoted_at"] == date(2026, 4, 26)
    assert set(payload["specialists"].keys()) == {
        name for name, *_ in SPECIALIST_DISPATCH_FAMILIES
    }


def test_dispatch_registry_loaded_at_module_import() -> None:
    """AC-B R10 SSOT invariant per Murat BLOCKER M-R10/M-R13.

    Asserts registry-derived specialist names exactly match the dispatch-family
    roster — proves the YAML is the SSOT, not a hardcoded enum elsewhere.
    """
    payload = yaml.safe_load(
        Path("state/config/dispatch-registry.yaml").read_text(encoding="utf-8")
    )
    registry_specialists = set(payload["specialists"].keys())
    family_specialists = {name for name, *_ in SPECIALIST_DISPATCH_FAMILIES}
    assert registry_specialists == family_specialists, (
        "SSOT drift: dispatch-registry.yaml specialist set must equal "
        "SPECIALIST_DISPATCH_FAMILIES roster."
    )


def test_dispatch_registry_no_longer_carries_interim_marker() -> None:
    """M5 condition close: the live registry must no longer advertise interim status."""
    payload = yaml.safe_load(
        Path("state/config/dispatch-registry.yaml").read_text(encoding="utf-8")
    )
    assert payload["_status"] != "interim"


def test_shared_dispatch_loader_loads_module(tmp_path: Path) -> None:
    """AC-D shared loader smoke per W-R6 hard reactivation gate."""
    module_path = tmp_path / "sample_module.py"
    module_path.write_text("VALUE = 7\n", encoding="utf-8")
    module = load_module("sample_module_for_test", module_path)
    assert module.VALUE == 7


def test_shared_sanctum_exception_is_runtime_error() -> None:
    """AC-E shared SanctumLockViolation smoke per W-R6 hard reactivation gate."""
    err = SanctumLockViolation("drift")
    assert isinstance(err, RuntimeError)
