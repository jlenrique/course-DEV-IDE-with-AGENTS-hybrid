from __future__ import annotations

from pathlib import Path

import yaml

from app.models.dispatch import (
    GaryDispatchReceipt,
    IreneDispatchInput,
    IreneDispatchReceipt,
)
from app.specialists._scaffold.dispatch_loader import load_module
from app.specialists._scaffold.sanctum_exceptions import SanctumLockViolation


def test_dispatch_registry_is_structured_interim() -> None:
    payload = yaml.safe_load(
        Path("state/config/dispatch-registry.yaml").read_text(encoding="utf-8")
    )
    assert payload["_status"] == "interim"
    assert payload["_lifecycle"]["state"] == "interim"
    assert "irene" in payload["specialists"]


def test_representative_dispatch_models_validate() -> None:
    input_model = IreneDispatchInput(pass_phase="pass-1", payload_in={"topic": "cells"})
    receipt_model = IreneDispatchReceipt(
        irene_lesson_design={"learning_objectives": ["obj-1"]},
        irene_pass_2_envelope=None,
    )
    gary_receipt = GaryDispatchReceipt(
        generation_id="gid-1",
        status="ok",
        gary_slide_output=[{"slide_id": "s1"}],
    )
    assert input_model.pass_phase == "pass-1"
    assert receipt_model.irene_lesson_design is not None
    assert gary_receipt.status == "ok"


def test_shared_dispatch_loader_loads_module(tmp_path: Path) -> None:
    module_path = tmp_path / "sample_module.py"
    module_path.write_text("VALUE = 7\n", encoding="utf-8")
    module = load_module("sample_module_for_test", module_path)
    assert module.VALUE == 7


def test_shared_sanctum_exception_is_runtime_error() -> None:
    err = SanctumLockViolation("drift")
    assert isinstance(err, RuntimeError)
