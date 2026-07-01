"""Leg-C R3 AC#15 (D-0, J-3) — hidden-key strip at the REAL Pass-1 surface.

The D1 adjudication's D-0 finding: ``irene_pass1/_act.py`` embedded the FULL
envelope payload into the LLM-visible prompt, so a bound scripted floor LEAKED
to the model — an uncontrolled re-parameterization of the clustering objective
(violates the binding "never re-parameterize the LLM objective" amendment) and
a contamination of the live differential's control-vs-treatment input.

These pin (RED-first):

- a bound ``min_cluster_floor`` reaches NEITHER the key nor the value into the
  prompt (system or user message);
- the model-visible input is BYTE-IDENTICAL with and without a bound floor
  (Dan's byte-identity property — the deterministic post-hoc honoring is the
  ONLY delta);
- the hidden-key set is keyed off the scripted NAMESPACE
  (``SCRIPTED_ENUM_CLASSES``), never a hand-list (Dan D-0);
- the strip holds through the real ``act()`` path (recording fake handle, no
  network) — the Murat-5 zero-floor-bytes control in unit form.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act

# A distinctive value that cannot collide with reference-doc/prompt text.
_SENTINEL_FLOOR = 424242


@dataclass
class _RecordingChat:
    response_text: str
    calls: list[list[dict[str, str]]] = field(default_factory=list)

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls.append(messages)
        return SimpleNamespace(content=self.response_text, usage_metadata=None)


@dataclass
class _RecordingHandle:
    response_text: str
    chat: _RecordingChat = field(init=False)

    def __post_init__(self) -> None:
        self.chat = _RecordingChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


def _minimal_response() -> str:
    return json.dumps(
        {
            "lesson_summary": "s",
            "plan_units": [
                {
                    "unit_id": "u1",
                    "title": "T",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                    "cluster_id": "c-u1",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                    "cluster_interstitial_count": 0,
                }
            ],
            "collateral": {"declaration": "none"},
        }
    )


def test_bound_floor_key_and_value_never_reach_prompt() -> None:
    system_msg, user_msg = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1", "topic": "cells", "min_cluster_floor": _SENTINEL_FLOOR},
        extracted_source="Corpus text.",
    )
    for text in (system_msg, user_msg):
        assert "min_cluster_floor" not in text
        assert str(_SENTINEL_FLOOR) not in text


def test_prompt_byte_identical_with_and_without_floor() -> None:
    base = {"mode": "pass-1", "topic": "cells"}
    without = pass1_act.assemble_pass1_prompt(dict(base), extracted_source="Corpus.")
    with_floor = pass1_act.assemble_pass1_prompt(
        {**base, "min_cluster_floor": _SENTINEL_FLOOR}, extracted_source="Corpus."
    )
    assert without == with_floor


def test_hidden_keys_are_the_scripted_namespace() -> None:
    """Dan D-0: the strip keys off the scripted NAMESPACE (the sealed registry),
    not a hand-listed key. A future 2nd scripted class is auto-hidden."""
    from app.specialists.gary.styleguide_library import SCRIPTED_ENUM_CLASSES

    assert frozenset(SCRIPTED_ENUM_CLASSES) == pass1_act._LLM_HIDDEN_PAYLOAD_KEYS


def test_strip_does_not_mutate_the_full_payload() -> None:
    payload = {"mode": "pass-1", "min_cluster_floor": _SENTINEL_FLOOR}
    snapshot = json.dumps(payload, sort_keys=True)
    pass1_act.assemble_pass1_prompt(payload, extracted_source="Corpus.")
    # The FULL payload (floor included) stays available for post-hoc consumption.
    assert json.dumps(payload, sort_keys=True) == snapshot


def test_act_path_prompt_carries_zero_floor_bytes(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# Corpus\n\nSource.", encoding="utf-8")
    handle = _RecordingHandle(_minimal_response())
    pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-strip",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
                "min_cluster_floor": 1,  # 1 <= any real cluster count: honoring no-op
            }
        ),
        handle=handle,
        model_id="gpt-5.4",
    )
    messages = handle.chat.calls[-1]
    for message in messages:
        assert "min_cluster_floor" not in message["content"]
