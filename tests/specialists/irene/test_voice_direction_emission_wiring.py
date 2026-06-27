"""Step-2 directed-voice EMISSION-WIRING pins (P5 directed-voice arc, 2026-06-27).

Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§F (IR-1 separate post-freeze annotation pass; IR-2 figure-gate firewall;
MUR-2 grounding-non-regression gate) + the implementation control cards.

These pins exercise the wiring of the pure annotation pass into Irene's Pass-2
emission seam in `graph.py` (after `_assert_figure_citations_within_perceived`):

- FLAG OFF (default) -> emitted manifest is BYTE-IDENTICAL to the pre-Step-2
  baseline (no `voice_direction` keys anywhere).
- FLAG ON -> each emitted segment-manifest delta carries a valid
  `voice_direction`; grounded fields are untouched.
- The figure-citation gate stays clean after annotation, and a delivery cue
  carrying an off-script figure NEVER trips the gate (direction strings never
  enter the gate).
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists._shared.voice_direction_map import VOICE_DIRECTION_ACTIVE_ENV
from app.specialists.irene.authoring.pass_2_template import VoiceDirection
from app.specialists.irene.graph import _act, _plan
from tests.specialists.irene.conftest import make_grounded_pass2_payload

_NARRATION = [
    {"id": "seg-1", "slide_id": "s1", "narration_text": "Opening on the chart."},
    {"id": "seg-2", "slide_id": "s2", "narration_text": "Closing on the team."},
]
_DELTAS = [
    {"id": "seg-1", "slide_id": "s1", "visual_references": [{"perception_source": "s1"}]},
    {"id": "seg-2", "slide_id": "s2", "visual_references": [{"perception_source": "s2"}]},
]


def _make_mock_response(
    narration: list[dict[str, Any]], deltas: list[dict[str, Any]]
) -> MagicMock:
    payload = {"narration_script": narration, "segment_manifest_deltas": deltas}
    fenced = f"```json\n{json.dumps(payload, sort_keys=True)}\n```"
    response = MagicMock()
    response.content = fenced
    response.usage_metadata = {"input_tokens": 2048, "output_tokens": 512}
    return response


def _run_act(
    payload_extra: dict[str, Any],
    *,
    narration: list[dict[str, Any]] | None = None,
    deltas: list[dict[str, Any]] | None = None,
    tmp_path: Any,
) -> dict[str, Any]:
    envelope = make_grounded_pass2_payload(tmp_path, **payload_extra)
    payload_blob = json.dumps(
        envelope, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    state = state.model_copy(update=_plan(state))

    mock_handle = MagicMock()
    mock_handle.chat = MagicMock()
    mock_handle.chat.invoke.return_value = _make_mock_response(
        narration or _NARRATION, deltas or _DELTAS
    )
    mock_handle.entry = state.model_resolution_trail[-1]
    with patch(
        "app.specialists.irene.graph.make_chat_model", return_value=mock_handle
    ):
        act_update = _act(state)
    return json.loads(act_update["cache_state"]["cache_prefix"])


# --------------------------------------------------------------------------- #
# FLAG OFF -> byte-identical (no voice_direction emitted).
# --------------------------------------------------------------------------- #
def test_flag_off_emits_no_voice_direction(monkeypatch: Any, tmp_path: Any) -> None:
    monkeypatch.delenv(VOICE_DIRECTION_ACTIVE_ENV, raising=False)
    output = _run_act(
        {
            "lesson_slug": "test",
            "voice_direction_defaults": {"emotional_tone": "warm"},
        },
        tmp_path=tmp_path,
    )
    # Deltas are byte-identical to the model's deltas — no direction attached.
    assert output["segment_manifest_deltas"] == _DELTAS
    for delta in output["segment_manifest_deltas"]:
        assert "voice_direction" not in delta


def test_flag_off_baseline_matches_no_direction_inputs(
    monkeypatch: Any, tmp_path: Any
) -> None:
    # With the flag OFF, supplying direction inputs vs none yields the SAME bytes.
    monkeypatch.delenv(VOICE_DIRECTION_ACTIVE_ENV, raising=False)
    with_inputs = _run_act(
        {"lesson_slug": "test", "voice_direction_defaults": {"emotional_tone": "warm"}},
        tmp_path=tmp_path,
    )
    without_inputs = _run_act({"lesson_slug": "test"}, tmp_path=tmp_path)
    assert json.dumps(with_inputs, sort_keys=True) == json.dumps(
        without_inputs, sort_keys=True
    )


# --------------------------------------------------------------------------- #
# FLAG ON -> each emitted delta carries a valid voice_direction.
# --------------------------------------------------------------------------- #
def test_flag_on_attaches_voice_direction_to_each_delta(
    monkeypatch: Any, tmp_path: Any
) -> None:
    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")
    output = _run_act(
        {
            "lesson_slug": "test",
            "voice_direction_defaults": {"emotional_tone": "warm", "pace": "neutral"},
            "voice_direction_overrides": {
                "seg-2": {"emotional_tone": "reflective", "pace": "slower"},
            },
        },
        tmp_path=tmp_path,
    )
    by_id = {d["id"]: d for d in output["segment_manifest_deltas"]}
    assert set(by_id) == {"seg-1", "seg-2"}

    seg1 = VoiceDirection.model_validate(by_id["seg-1"]["voice_direction"])
    assert seg1.emotional_tone == "warm"  # CD defaults
    assert seg1.source == "cd-authored"

    seg2 = VoiceDirection.model_validate(by_id["seg-2"]["voice_direction"])
    assert seg2.emotional_tone == "reflective"  # override
    assert seg2.pace == "slower"
    assert seg2.source == "operator-override"

    # Grounded delta fields untouched by the annotation.
    for delta in output["segment_manifest_deltas"]:
        assert delta["visual_references"]  # still present + non-empty
        assert "slide_id" in delta


def test_flag_on_grounded_narration_untouched(monkeypatch: Any, tmp_path: Any) -> None:
    # narration_script is never touched by the annotation pass (it annotates the
    # manifest deltas only). Prove the narration is byte-identical flag ON vs OFF.
    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")
    on = _run_act(
        {"lesson_slug": "test", "voice_direction_defaults": {"emotional_tone": "warm"}},
        tmp_path=tmp_path,
    )
    monkeypatch.delenv(VOICE_DIRECTION_ACTIVE_ENV, raising=False)
    off = _run_act({"lesson_slug": "test"}, tmp_path=tmp_path)
    assert on["narration_script"] == off["narration_script"]


# --------------------------------------------------------------------------- #
# Figure-gate firewall stays clean after annotation (IR-2).
# --------------------------------------------------------------------------- #
def test_figure_gate_clean_when_delivery_cue_carries_offscript_figure(
    monkeypatch: Any, tmp_path: Any
) -> None:
    # A delivery cue (delivery_tag / delivery_intent) carrying a figure that is
    # NOT on the slide must NOT trip the figure-citation gate, because direction
    # strings never enter narration_text. Narration text stays clean.
    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")
    output = _run_act(
        {
            "lesson_slug": "test",
            "voice_direction_overrides": {
                "seg-1": {
                    "delivery_tag": "[emphasize $5 billion]",
                    "delivery_intent": "say $9 trillion urgently",
                },
            },
        },
        tmp_path=tmp_path,
    )
    # The run completed (gate did not raise) AND the off-script figure lives only
    # in the direction payload, never in narration.
    seg1 = output["segment_manifest_deltas"][0]
    assert seg1["voice_direction"]["delivery_tag"] == "[emphasize $5 billion]"
    for seg in output["narration_script"]:
        assert "5 billion" not in seg.get("narration_text", "")
        assert "9 trillion" not in seg.get("narration_text", "")


def test_offscript_figure_in_narration_still_red_fails(
    monkeypatch: Any, tmp_path: Any
) -> None:
    # Positive control: the gate is still LIVE under flag ON — an off-script
    # figure placed in narration_text must still raise.
    from app.specialists.irene.graph import Pass2GroundingError

    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")
    bad_narration = [
        {"id": "seg-1", "slide_id": "s1", "narration_text": "Revenue hit $5 billion."},
        {"id": "seg-2", "slide_id": "s2", "narration_text": "Closing on the team."},
    ]
    with pytest.raises(Pass2GroundingError):
        _run_act(
            {"lesson_slug": "test"},
            narration=bad_narration,
            tmp_path=tmp_path,
        )


# --------------------------------------------------------------------------- #
# Two-walk determinism (Winston W-A4) — cross-walk stability.
#
# Finding (Step-2 investigation, 5a): the Irene graph has NO LangGraph
# checkpointer; on the resume/continuation walk the production runner's S2
# per-node idempotency contract (production_runner.py
# `production_envelope.get_contribution(specialist_id, node_id)` is not None ⇒
# `continue`) SKIPS re-dispatch entirely, so `_act_pass_2` does NOT re-execute —
# the resume walk reuses the captured ProductionEnvelope contribution (the baked
# annotated deltas) as-is. There is therefore no two-walk divergence bug.
#
# This pins the regression: for a fixed flag + envelope the annotated deltas are
# byte-stable across re-execution (so even if the resume walk DID re-run, it
# would not diverge), AND documents the standing constraint that the
# MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE flag must NOT flip mid-run (the second
# pin proves a flag flip WOULD change the output — which is exactly why the
# capture-once contract matters).
#
# FOLLOW-ON (UDAC / Step-8 cross-walk concern): the robust long-term fix is to
# capture the flag decision once into run state / the production envelope so both
# walks provably agree regardless of mid-run env mutation. Not needed today
# because the output is captured once and re-dispatch is skipped; filed as a
# cross-walk hardening follow-on rather than implemented here (would touch
# run_state / envelope plumbing beyond Step-2 scope).
# --------------------------------------------------------------------------- #
def test_annotated_deltas_byte_stable_across_reexecution(
    monkeypatch: Any, tmp_path: Any
) -> None:
    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")
    payload = {
        "lesson_slug": "test",
        "voice_direction_defaults": {"emotional_tone": "warm", "pace": "neutral"},
        "voice_direction_overrides": {
            "seg-2": {"emotional_tone": "reflective", "pace": "slower"},
        },
    }
    first = _run_act(payload, tmp_path=tmp_path)
    second = _run_act(payload, tmp_path=tmp_path)
    assert json.dumps(first["segment_manifest_deltas"], sort_keys=True) == json.dumps(
        second["segment_manifest_deltas"], sort_keys=True
    )
    # And the directed payload is actually present (not a vacuous match).
    assert all(
        "voice_direction" in d for d in first["segment_manifest_deltas"]
    )


def test_flag_flip_mid_run_would_change_output_documents_capture_once(
    monkeypatch: Any, tmp_path: Any
) -> None:
    # Demonstrates the hazard the capture-once contract guards: the SAME envelope
    # under flag ON vs OFF yields DIFFERENT emitted deltas. The production runner
    # captures irene's contribution once and skips re-dispatch on resume, so this
    # divergence cannot occur within a single run UNLESS the flag flips mid-run —
    # which the standing constraint forbids.
    payload = {"lesson_slug": "test", "voice_direction_defaults": {"emotional_tone": "warm"}}
    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")
    on = _run_act(payload, tmp_path=tmp_path)
    monkeypatch.delenv(VOICE_DIRECTION_ACTIVE_ENV, raising=False)
    off = _run_act(payload, tmp_path=tmp_path)
    assert on["segment_manifest_deltas"] != off["segment_manifest_deltas"]
    assert all("voice_direction" in d for d in on["segment_manifest_deltas"])
    assert all("voice_direction" not in d for d in off["segment_manifest_deltas"])
