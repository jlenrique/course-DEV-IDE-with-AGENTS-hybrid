"""Package export pins for Story 31-5."""

from __future__ import annotations

from app.marcus.lesson_plan import (
    DEFAULT_QUINN_R_GATE_OUTPUT_ROOT,
    QuinnRGateError,
    QuinnRTwoBranchResult,
    QuinnRUnitVerdict,
    emit_quinn_r_gate_artifact,
    evaluate_quinn_r_two_branch_gate,
    extract_prior_declined_rationales,
    render_quinn_r_gate_json,
)


def test_quinn_r_gate_public_exports_exist() -> None:
    assert DEFAULT_QUINN_R_GATE_OUTPUT_ROOT.endswith("quinn-r")
    assert QuinnRGateError.__name__ == "QuinnRGateError"
    assert QuinnRTwoBranchResult.__name__ == "QuinnRTwoBranchResult"
    assert QuinnRUnitVerdict.__name__ == "QuinnRUnitVerdict"
    assert callable(evaluate_quinn_r_two_branch_gate)
    assert callable(emit_quinn_r_gate_artifact)
    assert callable(extract_prior_declined_rationales)
    assert callable(render_quinn_r_gate_json)
