from __future__ import annotations

from types import SimpleNamespace

import pytest
from jinja2 import UndefinedError

from app.marcus.orchestrator.pre_gate_marcus import (
    PreFillProposal,
    _parse_pre_fill_response,
    invoke_pre_gate_marcus,
    render_pre_fill_prompt,
)


def _slots() -> dict[str, object]:
    return {
        "trial_id": "trial-123",
        "gate_id": "G1",
        "upstream_contributions": [{"specialist_id": "texas"}],
        "pending_nodes": ["04A", "05"],
        "artifact_paths": ["runs/trial-123/source.md"],
    }


def test_render_pre_fill_prompt_succeeds_for_valid_gate_and_slots() -> None:
    prompt = render_pre_fill_prompt(gate_id="G1", slot_values=_slots())

    assert "pre-gate-marcus" in prompt
    assert "Trial: trial-123" in prompt
    assert '"decision": one of ["confirm", "revise", "reject", "escape"]' in prompt


def test_render_pre_fill_prompt_missing_slot_raises_undefined_error() -> None:
    slots = _slots()
    del slots["trial_id"]

    with pytest.raises(UndefinedError):
        render_pre_fill_prompt(gate_id="G1", slot_values=slots)


def test_render_pre_fill_prompt_missing_template_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError, match="g9.j2"):
        render_pre_fill_prompt(gate_id="G9", slot_values=_slots())


def test_parse_pre_fill_response_returns_proposal() -> None:
    proposal = _parse_pre_fill_response(
        """
        {
          "decision": "confirm",
          "directive": "accept-as-is",
          "rationale": "The upstream evidence is coherent enough to continue.",
          "confidence": 0.82,
          "confidence_signals": ["evidence-present", "no-blockers"]
        }
        """
    )

    assert proposal == PreFillProposal(
        decision="confirm",
        directive="accept-as-is",
        rationale="The upstream evidence is coherent enough to continue.",
        confidence=0.82,
        confidence_signals=("evidence-present", "no-blockers"),
    )


def test_parse_pre_fill_response_rejects_short_rationale() -> None:
    with pytest.raises(ValueError, match="rationale shorter"):
        _parse_pre_fill_response(
            """
            {
              "decision": "confirm",
              "directive": "accept-as-is",
              "rationale": "too short",
              "confidence": 0.9
            }
            """
        )


def test_invoke_pre_gate_marcus_uses_stub_chat_model_factory() -> None:
    class _Chat:
        def invoke(self, messages):
            assert messages[0]["role"] == "user"
            assert "Trial: trial-123" in messages[0]["content"]
            return SimpleNamespace(
                content=(
                    '{"decision": "confirm", "directive": "accept-as-is", '
                    '"rationale": "The filled prompt supports proceeding now.", '
                    '"confidence": 0.7, '
                    '"confidence_signals": ["stubbed-call"]}'
                )
            )

    def _factory(specialist_id: str):
        assert specialist_id == "marcus"
        return SimpleNamespace(chat=_Chat())

    proposal = invoke_pre_gate_marcus(
        gate_id="G1",
        slot_values=_slots(),
        chat_model_factory=_factory,
    )

    assert proposal.decision == "confirm"
    assert proposal.directive == "accept-as-is"
    assert proposal.confidence_signals == ("stubbed-call",)
