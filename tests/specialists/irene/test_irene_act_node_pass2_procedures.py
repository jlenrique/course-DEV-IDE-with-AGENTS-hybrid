"""SF5 — Parametrized procedure-path coverage with mock-LLM (Story 2a.2).

Three Pass-2 procedure scenarios exercised against `_act` with mock LLM
responses:
1. Static-only segments (no motion): narration_script[] only
2. Motion-enabled segment: narration_script[] + segment_manifest_deltas[] with
   motion_type fields
3. Cluster-aware run: narration_script[] with cluster_role fields

These tests do NOT carry @llm_live — they use unittest.mock to inject canned
responses. Catches regressions in `_parse_pass_2_response` + `_act`'s
state-update shape across realistic procedural variants per Pass-2 procedure
branches (skills/bmad-agent-content-creator/references/pass-2-procedure.md).
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene.graph import _act, _plan


def _make_mock_response(narration: list[dict[str, Any]], deltas: list[dict[str, Any]]) -> MagicMock:
    """Build a mock chat-invoke response carrying JSON-fenced narration content."""
    payload = {"narration_script": narration, "segment_manifest_deltas": deltas}
    fenced = f"```json\n{json.dumps(payload, sort_keys=True)}\n```"
    response = MagicMock()
    response.content = fenced
    response.usage_metadata = {"input_tokens": 2048, "output_tokens": 512}
    return response


# dp-v1.1: every scenario's deltas carry visual_references joined to the
# grounded roster (s1/s2) — unjoined narration now raises Pass2GroundingError
# by design (the cycle-4 confabulation kill).
# id-integrity gate (irene-pass2-slidejoin-id-integrity-gate.md): every
# narration segment + delta carries a usable bijective ``id`` — the real
# Pass-2 emission shape the shared join keys on. Without it the id-keyed join
# collapses the deck (the 40f3a90a defect); the boundary gate now fails loud.
_REFS_S1 = [{"perception_source": "s1"}]
_REFS_S2 = [{"perception_source": "s2"}]


@pytest.mark.parametrize(
    ("scenario", "narration", "deltas"),
    [
        (
            "static-only",
            [{"id": "seg-1", "slide_id": "s1", "narration": "Welcome to the lesson."}],
            [{"id": "seg-1", "slide_id": "s1", "visual_references": _REFS_S1}],
        ),
        (
            "motion-enabled",
            [{"id": "seg-1", "slide_id": "s1", "narration": "Watch how the membrane reshapes."}],
            [
                {
                    "id": "seg-1",
                    "slide_id": "s1",
                    "motion_type": "kira_video",
                    "motion_duration_seconds": 8.0,
                    "visual_references": _REFS_S1,
                }
            ],
        ),
        (
            "cluster-aware",
            [
                {"id": "seg-1", "slide_id": "s1", "cluster_role": "head",
                 "narration": "Three core ideas..."},
                {"id": "seg-2", "slide_id": "s2", "cluster_role": "interstitial",
                 "narration": "First..."},
            ],
            [
                {"id": "seg-1", "slide_id": "s1", "visual_references": _REFS_S1},
                {"id": "seg-2", "slide_id": "s2", "visual_references": _REFS_S2},
            ],
        ),
    ],
)
def test_irene_act_handles_pass2_procedure_scenarios(
    scenario: str,
    narration: list[dict[str, Any]],
    deltas: list[dict[str, Any]],
    tmp_path: Any,
) -> None:
    """Each scenario produces a parseable IreneReturn shape after _act."""
    from tests.specialists.irene.conftest import make_grounded_pass2_payload

    envelope = make_grounded_pass2_payload(tmp_path, lesson_slug="test", scenario=scenario)
    payload_blob = json.dumps(envelope, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    plan_update = _plan(state)
    state = state.model_copy(update=plan_update)

    mock_response = _make_mock_response(narration, deltas)
    mock_chat = MagicMock()
    mock_chat.invoke.return_value = mock_response
    mock_handle = MagicMock()
    mock_handle.chat = mock_chat
    mock_handle.entry = state.model_resolution_trail[-1]

    with patch(
        "app.specialists.irene.graph.make_chat_model",
        return_value=mock_handle,
    ):
        act_update = _act(state)
    output = json.loads(act_update["cache_state"]["cache_prefix"])
    assert output["narration_script"] == narration
    assert output["segment_manifest_deltas"] == deltas
    assert output["model_id"] == "gpt-5"
    assert mock_chat.invoke.called
    # Verify the prompt was passed as a 2-message list (system + user).
    call_args = mock_chat.invoke.call_args[0][0]
    assert len(call_args) == 2
    assert call_args[0]["role"] == "system"
    assert call_args[1]["role"] == "user"
