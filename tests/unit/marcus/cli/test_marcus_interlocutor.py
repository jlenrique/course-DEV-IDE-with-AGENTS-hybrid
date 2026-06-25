"""S5 — Marcus interlocution REPL: offline dev-agent ACs (spec §4, amendments A1-A9).

No live model: a fake `BaseChatModel` (duck-typed `.invoke`) is constructor-injected
and the real `resume_production_trial` is replaced by a spy at the call boundary so
the LOAD-BEARING property — a hallucinating/forbidden model action drives the engine
ZERO times — is asserted directly (AC-D3a/D4). The live model + HIL drive is
operator-gated (AC-O1..O3), not exercised here.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.marcus.cli.capability_grounding import (
    build_grounding_context,
    research_token_precondition,
)
from app.marcus.cli.marcus_interlocutor import (
    GuardRefusal,
    MarcusInterlocutor,
    StructuredAction,
    validate_action_against_gate,
)

# ---------------------------------------------------------------------------
# Fakes / fixtures
# ---------------------------------------------------------------------------


class FakeChatModel:
    """Duck-typed stand-in for BaseChatModel: returns scripted JSON per invoke."""

    def __init__(self, scripted: list[str]) -> None:
        self._scripted = list(scripted)
        self.invocations: list[object] = []

    def invoke(self, messages):  # noqa: ANN001
        self.invocations.append(messages)
        payload = self._scripted.pop(0) if self._scripted else '{"intent":"chat","reply":"…"}'
        return SimpleNamespace(content=payload)


class ResumeSpy:
    """Spy for resume_production_trial; records calls + advances run.json."""

    def __init__(self, run_dir, *, final_status="completed", next_gate=None):
        self.run_dir = run_dir
        self.calls: list[dict] = []
        self._final_status = final_status
        self._next_gate = next_gate

    def __call__(self, *, trial_id, verdict, runs_root, max_specialist_calls):  # noqa: ANN001
        self.calls.append({"verb": verdict.verb, "gate_id": verdict.gate_id})
        (self.run_dir / "run.json").write_text(
            json.dumps({"status": self._final_status, "paused_gate": self._next_gate}),
            encoding="utf-8",
        )
        return SimpleNamespace(status=self._final_status, paused_gate=self._next_gate)


def _make_run(tmp_path, gate="G1"):
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({"status": "paused-at-gate", "paused_gate": gate}), encoding="utf-8"
    )
    digest = __import__("hashlib").sha256(str(trial_id).encode()).hexdigest()
    (run_dir / f"decision-card-{gate}.json").write_text(
        json.dumps({"card": {"card_id": str(uuid4())}, "digest": digest}),
        encoding="utf-8",
    )
    return trial_id, run_dir


def _grounding():
    overlay = {
        "content_hash": "hash123",
        "specialists": {
            # texas is the WIRED research-dispatch path → token-gated read (A9)
            "texas": {
                "capability_state": "wired", "rationale": "routed", "routed_at_nodes": ["02"],
            },
            "tracy": {"capability_state": "present-but-unrouted", "rationale": "not routed"},
            "canva": {"capability_state": "shelf", "rationale": "on the shelf"},
        },
    }
    return build_grounding_context(
        overlay,
        stale=False,
        research_precondition=research_token_precondition(
            scite_token_path=overlay.get("_absent_path", __import__("pathlib").Path("/no/such")),
            env={},
        ),
    )


# ---------------------------------------------------------------------------
# AC-D1 — REPL turn-loop drives the engine (DI; chat before decide)
# ---------------------------------------------------------------------------


def test_acd1_turn_loop_chats_then_drives_once(tmp_path):
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel([
        '{"intent":"chat","reply":"Here is what I can do."}',
        '{"intent":"decide","reply":"Approving.","verb":"approve"}',
    ])
    spy = ResumeSpy(run_dir, final_status="completed")
    out: list[str] = []
    inter = MarcusInterlocutor(
        trial_id,
        chat_model=fake,
        input_source=["what can you do?", "approve it", "yes"],
        output_sink=out.append,
        runs_root=tmp_path,
        grounding=_grounding(),
        resume_fn=spy,
    )
    transcript = inter.run()
    # consumed ≥1 chat turn before deciding, drove engine exactly once
    assert len(spy.calls) == 1
    assert spy.calls[0]["verb"] == "approve"
    assert any(e.action.get("intent") == "chat" for e in transcript)
    # narration rendered from the real card path
    assert any("GATE G1" in line for line in out)
    # the INJECTED fake was actually invoked (no silent fall-through, A4)
    assert len(fake.invocations) == 2


def test_acd1_injected_model_is_used_not_live_seam(tmp_path):
    """A4: the offline path uses the injected fake; the live seam is never built."""
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel(['{"intent":"chat","reply":"hi"}'])
    inter = MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["hello"], output_sink=lambda _t: None,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=ResumeSpy(run_dir),
    )
    assert inter.chat_model is fake  # identity — injected, not a default


# ---------------------------------------------------------------------------
# AC-D2 — capability grounding is FACT-bound (never up-levels)
# ---------------------------------------------------------------------------


def test_acd2_grounding_preserves_state_no_uplevel():
    g = _grounding()
    assert g.fact_for("canva").capability_state == "shelf"
    assert g.fact_for("texas").capability_state == "wired"
    # tracy stays present-but-unrouted — the precondition does NOT override it (T11 fix)
    assert g.fact_for("tracy").capability_state == "present-but-unrouted"
    assert g.fact_for("tracy").runtime_precondition is None
    rendered = g.render()
    assert "canva: shelf" in rendered
    # texas is wired BUT token-gated (no scite token / no CONSENSUS key) → honest read
    assert "BLOCKED right now pending the research token" in rendered
    assert "texas: on the run path (wired)" in rendered


def test_acd2_stale_overlay_discloses():
    overlay = {
        "content_hash": "h",
        "specialists": {"x": {"capability_state": "wired", "rationale": "r"}},
    }
    g = build_grounding_context(overlay, stale=True)
    assert "STALE-MAP DISCLOSURE" in g.render()


# ---------------------------------------------------------------------------
# AC-D3a — deterministic guard refuses unauthorized drive: ZERO engine calls
# ---------------------------------------------------------------------------


def test_acd3a_forbidden_verb_drives_zero_times(tmp_path):
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel(['{"intent":"decide","reply":"Deleting.","verb":"delete_everything"}'])
    spy = ResumeSpy(run_dir)
    out: list[str] = []
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["nuke it"], output_sink=out.append,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    assert spy.calls == []  # LOAD-BEARING: hallucinated verb never reaches the engine
    assert any("can't do that here" in line for line in out)


def test_acd3a_bad_select_key_drives_zero_times(tmp_path):
    trial_id, run_dir = _make_run(tmp_path, gate="G4A")
    # G4A allows only selected_voice_id; a rogue key must be refused by the ENGINE validator
    rogue = '{"intent":"decide","reply":"x","verb":"select","edit_payload":{"evil":"1"}}'
    fake = FakeChatModel([rogue])
    spy = ResumeSpy(run_dir)
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["pick"], output_sink=lambda _t: None,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    assert spy.calls == []


# ---------------------------------------------------------------------------
# AC-D4 — decision-mapping safety (the guard unit, reusing engine validator A1)
# ---------------------------------------------------------------------------


def test_acd4_guard_unit_rules():
    # forbidden verb
    with pytest.raises(GuardRefusal):
        validate_action_against_gate(StructuredAction(intent="decide", verb="rm"), "G1")
    # select key outside _SELECTABLE_KEYS_BY_GATE (reuses engine UnknownSelectionKeyError)
    with pytest.raises(GuardRefusal):
        validate_action_against_gate(
            StructuredAction(intent="decide", verb="select", edit_payload={"nope": 1}), "G4A"
        )
    # valid approve maps cleanly
    d = validate_action_against_gate(StructuredAction(intent="decide", verb="approve"), "G1")
    assert d.verb == "approve" and d.gate_id == "G1"
    # valid select at G4A with the allowed key
    d2 = validate_action_against_gate(
        StructuredAction(intent="decide", verb="select", edit_payload={"selected_voice_id": "v1"}),
        "G4A",
    )
    assert d2.verb == "select"
    # a chat intent is not a decision
    with pytest.raises(GuardRefusal):
        validate_action_against_gate(StructuredAction(intent="chat", reply="hi"), "G1")


def test_acd4_malformed_model_output_is_chat_never_drives(tmp_path):
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel(["this is not json at all"])
    spy = ResumeSpy(run_dir)
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["hello"], output_sink=lambda _t: None,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    assert spy.calls == []  # malformed → chat → no drive


# ---------------------------------------------------------------------------
# AC-D5 — confirm-before-forward (echoes validated verb+payload; cancel works)
# ---------------------------------------------------------------------------


def test_acd5_cancel_at_confirm_drives_zero(tmp_path):
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel(['{"intent":"decide","reply":"ok","verb":"approve"}'])
    spy = ResumeSpy(run_dir)
    out: list[str] = []
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["approve", "no wait"], output_sink=out.append,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    assert spy.calls == []  # cancelled at confirm → no drive
    assert any("Cancelled" in line for line in out)


def test_acd5_edit_payload_echoed_in_full_at_confirm(tmp_path):
    """SHOULD-FIX (T11): `edit` is full-replace + not key-validated, so the operator
    MUST see the exact payload it will write before confirming."""
    trial_id, run_dir = _make_run(tmp_path)
    payload = {"narration": "REWRITTEN", "slides": [1, 2, 3]}
    action = {"intent": "decide", "reply": "edit it", "verb": "edit", "edit_payload": payload}
    fake = FakeChatModel([json.dumps(action)])
    spy = ResumeSpy(run_dir)
    out: list[str] = []
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["edit", "no"], output_sink=out.append,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    # the full payload is surfaced in the confirm echo BEFORE any drive
    assert any("REWRITTEN" in line and "verb=edit" in line for line in out)
    assert spy.calls == []  # we said "no" → no drive


def test_acd5_confirm_echoes_validated_verb(tmp_path):
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel(['{"intent":"decide","reply":"ok","verb":"approve"}'])
    spy = ResumeSpy(run_dir, final_status="completed")
    out: list[str] = []
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["approve", "yes"], output_sink=out.append,
        runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    assert len(spy.calls) == 1
    # confirm text echoes the VALIDATED verb, not model prose
    assert any("verb=approve" in line for line in out)


# ---------------------------------------------------------------------------
# AC-D6 — transcript persisted with per-turn content
# ---------------------------------------------------------------------------


def test_acd6_transcript_persisted_with_content(tmp_path):
    trial_id, run_dir = _make_run(tmp_path)
    fake = FakeChatModel([
        '{"intent":"chat","reply":"A question answered."}',
        '{"intent":"decide","reply":"Approving.","verb":"approve"}',
    ])
    spy = ResumeSpy(run_dir, final_status="completed")
    MarcusInterlocutor(
        trial_id, chat_model=fake, input_source=["q?", "approve", "yes"],
        output_sink=lambda _t: None, runs_root=tmp_path, grounding=_grounding(), resume_fn=spy,
    ).run()
    path = run_dir / f"marcus-interlocution-{trial_id}.md"
    assert path.exists()
    body = path.read_text(encoding="utf-8")
    assert "Operator:" in body and "Marcus-SPOC:" in body and "Structured action:" in body
    assert "q?" in body  # operator turn captured verbatim
