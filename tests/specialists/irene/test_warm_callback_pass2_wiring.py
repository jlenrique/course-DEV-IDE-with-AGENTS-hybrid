"""Slice-2 unit tests: warm_callback authoring wired into Irene Pass-2.

Story concierge-leg1b-warm-callback (Slice 2 — wire the authoring + R7 gate into
``_act_pass_2`` behind a default-OFF flag, with an INJECTABLE renderer). NO real
LLM here — the renderer is a deterministic injected fake; the LIVE gpt-5 close-bar
is the coordinator's step. All grounding/gate/read-path helpers are the REAL ones.

Covers (RED-first):
  * flag-ON + clean connective callback ⇒ injected into canonical + rhetorical_role
    set + the real figure gate passes;
  * flag-ON + callback carrying a NEW numeral ⇒ R7 gate kept=False ⇒ DROPPED (not
    in output) + a loud audit record;
  * no grounded strictly-prior teachable anchor ⇒ NO callback (fail-safe silent);
  * a kept callback with out-of-order visual_reference ⇒ assert_callback_reading_
    path raises (07G teeth);
  * flag-OFF ⇒ ``_attach_warm_callbacks`` is a no-op (byte-identical baseline);
  * AC1 finding-d: the emitted Pass-2 package is directly validatable.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists._shared.voice_direction_map import VOICE_DIRECTION_ACTIVE_ENV
from app.specialists.irene.authoring.warm_callback_authoring import (
    WARM_CALLBACK_AUTHORING_ACTIVE_ENV,
    render_warm_callback,
    warm_callback_authoring_active,
)
from app.specialists.irene.graph import (
    Pass2GroundingError,
    Pass2ReadingPathError,
    _act,
    _assert_figure_citations_within_perceived,
    _attach_warm_callbacks,
    _plan,
    _slide_roster,
    assert_pass2_surfaces_validatable,
)

# --------------------------------------------------------------------------- #
# Fixtures — real grounding corpus + a z_pattern roster
# --------------------------------------------------------------------------- #


def _components() -> list[dict[str, Any]]:
    """A strictly-prior resolved anchor (c1) and the callback target (c2)."""
    return [
        {
            "component_id": "c1",
            "type": "slide",
            "doc_ordinal": 1,
            "locator": "deck#1",
            "resolution_status": "resolved",
            "source_text": (
                "Earlier we established the homeostasis framework and its "
                "guiding principles."
            ),
        },
        {
            "component_id": "c2",
            "type": "narration",
            "doc_ordinal": 2,
            "locator": "deck#2",
            "resolution_status": "resolved",
            "source_text": "The membrane reshapes as conditions change.",
        },
    ]


def _roster_payload() -> dict[str, Any]:
    return {
        "gary_slide_output": [
            {"slide_id": "slide-01", "visual_description": "Z layout."}
        ],
        "perception_artifacts": [
            {
                "slide_id": "slide-01",
                "confidence": "HIGH",
                "coverage": "perceived",
                "reading_path": "z_pattern",
                "visual_elements": [
                    {"id": "body", "kind": "text", "label": "body copy",
                     "bbox": [0.08, 0.55, 0.42, 0.78]},
                    {"id": "hero", "kind": "visual", "label": "right hero image",
                     "bbox": [0.58, 0.10, 0.90, 0.42]},
                    {"id": "headline", "kind": "headline", "label": "top left headline",
                     "bbox": [0.05, 0.05, 0.45, 0.18]},
                    {"id": "cta", "kind": "callout", "label": "bottom right callout",
                     "bbox": [0.58, 0.65, 0.90, 0.85]},
                ],
            }
        ],
    }


def _roster() -> list[dict[str, Any]]:
    return _slide_roster(_roster_payload())


_Z_ORDER_OK = ["headline", "hero", "body", "cta"]
_Z_ORDER_BAD = ["body", "hero"]


_DEFAULT_NARRATION = "The membrane reshapes as conditions change."


def _parsed(order: list[str], narration: str = _DEFAULT_NARRATION) -> dict[str, Any]:
    return {
        "narration_script": [
            {
                "id": "seg-01",
                "slide_id": "slide-01",
                "component_id": "c2",
                "narration_text": narration,
            }
        ],
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "slide_id": "slide-01",
                "visual_references": [
                    {"perception_source": "slide-01", "element_id": element}
                    for element in order
                ],
            }
        ],
    }


def _envelope(components: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"warm_callback_grounding": {"components": components or _components()}}


def _fake_invoke(text: str):
    """A deterministic injected renderer — returns a fixed sentence (NO LLM)."""

    def _invoke(messages: list[dict[str, str]]) -> str:
        assert messages and messages[0]["role"] == "system"
        return text

    return _invoke


def _boom_invoke(messages: list[dict[str, str]]):  # pragma: no cover - must never run
    raise AssertionError("renderer must not be invoked")


@pytest.fixture
def _flag_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WARM_CALLBACK_AUTHORING_ACTIVE_ENV, "1")


# --------------------------------------------------------------------------- #
# Renderer seam
# --------------------------------------------------------------------------- #


def test_render_warm_callback_uses_injected_invoke_and_strips() -> None:
    out = render_warm_callback(
        anchor_text="A",
        segment_context="B",
        model_invoke=_fake_invoke("  Recall how we established the framework.  \n"),
    )
    assert out == "Recall how we established the framework."


def test_flag_default_off() -> None:
    assert warm_callback_authoring_active() is False


# --------------------------------------------------------------------------- #
# Authoring wiring
# --------------------------------------------------------------------------- #


def test_clean_callback_injected_canonical_role_set_and_figure_gate_passes(
    _flag_on: None,
) -> None:
    parsed = _parsed(_Z_ORDER_OK)
    roster = _roster()

    result = _attach_warm_callbacks(
        parsed,
        _envelope(),
        roster,
        model_invoke=_fake_invoke("Recall how we established the framework."),
    )

    segment = result["narration_script"][0]
    # Callback prepended to CANONICAL narration (gate-visible field).
    assert segment["narration_text"].startswith("Recall how we established the framework.")
    assert "membrane reshapes" in segment["narration_text"]
    # rhetorical_role stamped on the delta's voice_direction.
    delta_direction = result["segment_manifest_deltas"][0]["voice_direction"]
    assert delta_direction["rhetorical_role"] == "warm_callback"
    # Loud audit record present, decision=kept, correct anchor.
    audit = result["warm_callback_audit"]
    assert len(audit) == 1
    assert audit[0]["decision"] == "kept"
    assert audit[0]["anchor_component_ids"] == ["c1"]
    # The injected canonical callback FLOWS the real figure gate without raising.
    _assert_figure_citations_within_perceived(result, roster)


def test_callback_with_new_numeral_is_dropped_with_audit(_flag_on: None) -> None:
    parsed = _parsed(_Z_ORDER_OK)
    roster = _roster()

    result = _attach_warm_callbacks(
        parsed,
        _envelope(),
        roster,
        model_invoke=_fake_invoke("Remember, that was about 40%."),
    )

    segment = result["narration_script"][0]
    # DROPPED: the unsafe callback never enters canonical narration.
    assert "40" not in segment["narration_text"]
    assert segment["narration_text"] == "The membrane reshapes as conditions change."
    # Never stripped/altered; no rhetorical_role stamped on a dropped callback.
    assert "voice_direction" not in result["segment_manifest_deltas"][0]
    # Loud audit record names the drop + the unsourced figure.
    audit = result["warm_callback_audit"]
    assert audit[0]["decision"] == "dropped"
    assert audit[0]["reason"] is not None
    assert audit[0]["audit"]["status"] == "FAIL"
    assert any(
        "40" in tok for tok in audit[0]["audit"]["unsourced"]["numerals_units"]
    )


def test_no_grounded_anchor_yields_no_callback_silent(_flag_on: None) -> None:
    # Target is c1 (the FIRST component) ⇒ nothing strictly-prior ⇒ silent.
    parsed = _parsed(_Z_ORDER_OK)
    parsed["narration_script"][0]["component_id"] = "c1"
    original = parsed["narration_script"][0]["narration_text"]
    roster = _roster()

    result = _attach_warm_callbacks(
        parsed,
        _envelope(),
        roster,
        model_invoke=_boom_invoke,  # must not even render when no anchor
    )

    assert result["narration_script"][0]["narration_text"] == original
    assert "voice_direction" not in result["segment_manifest_deltas"][0]
    assert "warm_callback_audit" not in result


def test_kept_callback_out_of_order_visual_reference_raises_07g_teeth(
    _flag_on: None,
) -> None:
    parsed = _parsed(_Z_ORDER_BAD)  # violates z_pattern monotonic scan order
    roster = _roster()

    with pytest.raises(Pass2ReadingPathError):
        _attach_warm_callbacks(
            parsed,
            _envelope(),
            roster,
            model_invoke=_fake_invoke("Recall how we established the framework."),
        )


def test_flag_off_attach_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(WARM_CALLBACK_AUTHORING_ACTIVE_ENV, raising=False)
    parsed = _parsed(_Z_ORDER_OK)
    before = json.dumps(parsed, sort_keys=True)
    roster = _roster()

    result = _attach_warm_callbacks(
        parsed, _envelope(), roster, model_invoke=_boom_invoke
    )

    assert result is parsed
    assert json.dumps(result, sort_keys=True) == before
    assert "warm_callback_audit" not in result


# --------------------------------------------------------------------------- #
# AC1 — Pass-2 package directly validatable (finding-d)
# --------------------------------------------------------------------------- #


def test_ac1_full_surface_delta_validates() -> None:
    parsed = {
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "timing_role": "bridge",
                "bridge_type": "callback",
                "visual_references": [
                    {"narration_cue": "look here", "perception_source": "slide-01"}
                ],
                "voice_direction": {"rhetorical_role": "warm_callback"},
            }
        ]
    }
    # Must not raise — the package is directly validatable.
    assert_pass2_surfaces_validatable(parsed)


def test_ac1_bad_rhetorical_role_raises() -> None:
    parsed = {
        "segment_manifest_deltas": [
            {"id": "seg-01", "voice_direction": {"rhetorical_role": "bogus_role"}}
        ]
    }
    with pytest.raises(Pass2GroundingError):
        assert_pass2_surfaces_validatable(parsed)


def test_ac1_empty_perception_source_raises() -> None:
    parsed = {
        "segment_manifest_deltas": [
            {"id": "seg-01", "visual_references": [{"perception_source": "  "}]}
        ]
    }
    with pytest.raises(Pass2GroundingError):
        assert_pass2_surfaces_validatable(parsed)


# --------------------------------------------------------------------------- #
# Flag-OFF byte-identical through the real _act node (regression)
# --------------------------------------------------------------------------- #


def _make_mock_response(narration: list[dict[str, Any]], deltas: list[dict[str, Any]]) -> MagicMock:
    payload = {"narration_script": narration, "segment_manifest_deltas": deltas}
    fenced = f"```json\n{json.dumps(payload, sort_keys=True)}\n```"
    response = MagicMock()
    response.content = fenced
    response.usage_metadata = {"input_tokens": 1, "output_tokens": 1}
    return response


def test_flag_off_act_pass2_output_byte_identical(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    monkeypatch.delenv(WARM_CALLBACK_AUTHORING_ACTIVE_ENV, raising=False)
    from tests.specialists.irene.conftest import make_grounded_pass2_payload

    # id-integrity gate: narration + delta carry a usable bijective id (the real
    # Pass-2 shape the shared join keys on); id-less would fail loud by design.
    narration = [{"id": "seg-1", "slide_id": "s1", "narration": "Welcome.", "component_id": "c2"}]
    deltas = [{"id": "seg-1", "slide_id": "s1", "visual_references": [{"perception_source": "s1"}]}]
    # Grounding present in the envelope, but the flag is OFF ⇒ no callback path.
    envelope = make_grounded_pass2_payload(
        tmp_path, lesson_slug="t", warm_callback_grounding={"components": _components()}
    )
    payload_blob = json.dumps(envelope, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    state = state.model_copy(update=_plan(state))

    mock_handle = MagicMock()
    mock_handle.chat.invoke.return_value = _make_mock_response(narration, deltas)
    mock_handle.entry = state.model_resolution_trail[-1]
    with patch("app.specialists.irene.graph.make_chat_model", return_value=mock_handle):
        out = json.loads(_act(state)["cache_state"]["cache_prefix"])

    # narration + deltas pass through UNCHANGED (no callback authored, no role stamped).
    assert out["narration_script"] == narration
    assert out["segment_manifest_deltas"] == deltas
    # Flag-OFF carrier carries NO audit key (byte-identical baseline).
    assert "warm_callback_audit" not in out


# --------------------------------------------------------------------------- #
# Carrier-robustness: the audit (KEPT + DROPPED) survives into the persisted
# output_blob / cache_prefix (T11 hand-back — AC5 LOUD audit must be durable).
# --------------------------------------------------------------------------- #


def _carrier_components() -> list[dict[str, Any]]:
    return [
        {"component_id": "c0", "type": "slide", "doc_ordinal": 1, "locator": "deck#0",
         "resolution_status": "resolved",
         "source_text": "Earlier we established the framework and its guiding principles."},
        {"component_id": "cA", "type": "narration", "doc_ordinal": 2, "locator": "deck#A",
         "resolution_status": "resolved", "source_text": "The first topic builds on it."},
        {"component_id": "cB", "type": "narration", "doc_ordinal": 3, "locator": "deck#B",
         "resolution_status": "resolved", "source_text": "The second topic continues."},
    ]


def _run_act_flag_on(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
    *,
    narration: list[dict[str, Any]],
    deltas: list[dict[str, Any]],
    renderer_returns: list[str],
    grounding: dict[str, Any] | None,
) -> dict[str, Any]:
    monkeypatch.setenv(WARM_CALLBACK_AUTHORING_ACTIVE_ENV, "1")
    from tests.specialists.irene.conftest import make_grounded_pass2_payload

    extra = {"warm_callback_grounding": grounding} if grounding is not None else {}
    envelope = make_grounded_pass2_payload(tmp_path, lesson_slug="t", **extra)
    payload_blob = json.dumps(envelope, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    state = state.model_copy(update=_plan(state))

    mock_handle = MagicMock()
    # First invoke = the main Pass-2 generation; subsequent invokes = the
    # per-segment warm_callback renderer (plain strings, no .content).
    mock_handle.chat.invoke.side_effect = [
        _make_mock_response(narration, deltas),
        *renderer_returns,
    ]
    mock_handle.entry = state.model_resolution_trail[-1]
    with patch("app.specialists.irene.graph.make_chat_model", return_value=mock_handle):
        return json.loads(_act(state)["cache_state"]["cache_prefix"])


def test_act_pass2_serializes_kept_and_dropped_audit_into_carrier(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    narration = [
        {"id": "segA", "slide_id": "s1", "component_id": "cA", "narration_text": "First topic."},
        {"id": "segB", "slide_id": "s2", "component_id": "cB", "narration_text": "Second topic."},
    ]
    deltas = [
        {"id": "segA", "slide_id": "s1",
         "visual_references": [{"perception_source": "s1", "element_id": "chart"}]},
        {"id": "segB", "slide_id": "s2",
         "visual_references": [{"perception_source": "s2", "element_id": "infographic"}]},
    ]
    out = _run_act_flag_on(
        monkeypatch, tmp_path,
        narration=narration, deltas=deltas,
        renderer_returns=[
            "Recall how we established the framework.",  # segA -> KEPT
            "Remember, that was about 40%.",            # segB -> DROPPED (new figure)
        ],
        grounding={"components": _carrier_components()},
    )

    # KEPT canonical change rides the carrier narration_script.
    seg_a = next(s for s in out["narration_script"] if s["id"] == "segA")
    assert seg_a["narration_text"].startswith("Recall how we established the framework.")
    seg_b = next(s for s in out["narration_script"] if s["id"] == "segB")
    assert "40" not in seg_b["narration_text"]  # dropped text never entered canonical

    # The audit list is DURABLE in the serialized carrier (survives json round-trip).
    audit = out["warm_callback_audit"]
    decisions = {rec["decision"] for rec in audit}
    assert decisions == {"kept", "dropped"}
    dropped = next(rec for rec in audit if rec["decision"] == "dropped")
    assert dropped["reason"] is not None
    assert dropped["audit"]["status"] == "FAIL"
    assert any("40" in tok for tok in dropped["audit"]["unsourced"]["numerals_units"])


def test_act_pass2_flag_on_no_callbacks_carrier_has_no_audit_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    # Flag ON but the segments carry NO component_id ⇒ zero callbacks ⇒ no audit key.
    # id-integrity gate: narration + delta carry a usable bijective id.
    narration = [{"id": "seg-1", "slide_id": "s1", "narration_text": "Plain."}]
    deltas = [{"id": "seg-1", "slide_id": "s1", "visual_references": [{"perception_source": "s1"}]}]
    out = _run_act_flag_on(
        monkeypatch, tmp_path,
        narration=narration, deltas=deltas,
        renderer_returns=[],
        grounding={"components": _carrier_components()},
    )
    assert out["narration_script"] == narration
    assert out["segment_manifest_deltas"] == deltas
    assert "warm_callback_audit" not in out


# --------------------------------------------------------------------------- #
# Code-review remediation — MUST-FIX M1..M4, SHOULD-FIX S1..S3
# --------------------------------------------------------------------------- #


def _audit_of(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("warm_callback_audit") or []


def test_m1_pedagogy_annotation_error_does_not_crash_pass2(_flag_on: None) -> None:
    # A grounding component missing doc_ordinal raises ValueError in the P3
    # pre-flight today; the feature must SKIP (silent) + audit, never crash.
    bad_components = [
        {"component_id": "c1", "type": "slide", "locator": "deck#1",
         "resolution_status": "resolved", "source_text": "Prior concept."},  # no doc_ordinal
        {"component_id": "c2", "type": "narration", "doc_ordinal": 2, "locator": "deck#2",
         "resolution_status": "resolved", "source_text": "Target."},
    ]
    parsed = _parsed(_Z_ORDER_OK)
    result = _attach_warm_callbacks(
        parsed, _envelope(bad_components), _roster(),
        model_invoke=_fake_invoke("Recall the framework."),
    )
    assert result["narration_script"][0]["narration_text"] == _DEFAULT_NARRATION
    assert any(rec["decision"] == "skipped" for rec in _audit_of(result))


def test_m1_renderer_exception_skips_callback_with_audit(_flag_on: None) -> None:
    def _raising(messages: list[dict[str, str]]):
        raise RuntimeError("model exploded")

    parsed = _parsed(_Z_ORDER_OK)
    result = _attach_warm_callbacks(
        parsed, _envelope(), _roster(), model_invoke=_raising
    )
    assert result["narration_script"][0]["narration_text"] == _DEFAULT_NARRATION
    skipped = [rec for rec in _audit_of(result) if rec["decision"] == "skipped"]
    assert skipped and "model exploded" in skipped[0]["reason"]


def test_m2a_injection_writes_the_gate_read_field(_flag_on: None) -> None:
    # Gate reads `text` THEN `narration_text`; a segment with BOTH must have the
    # callback land in `text` (the gate-read field), never dodge the gate.
    parsed = _parsed(_Z_ORDER_OK)
    parsed["narration_script"][0]["text"] = "Gate-read primary."
    result = _attach_warm_callbacks(
        parsed, _envelope(), _roster(),
        model_invoke=_fake_invoke("Recall how we established the framework."),
    )
    segment = result["narration_script"][0]
    assert segment["text"].startswith("Recall how we established the framework.")
    # The callback must be visible in the gate-read field.
    _assert_figure_citations_within_perceived(result, _roster())


def test_m2b_callback_figure_absent_from_current_slide_dropped_not_aborted(
    _flag_on: None,
) -> None:
    # Figure IS in the prior anchor corpus (so R7 passes) but ABSENT from the
    # current slide ⇒ block-by-omission DROP, NOT a Pass2GroundingError abort.
    components = [
        {"component_id": "c1", "type": "slide", "doc_ordinal": 1, "locator": "deck#1",
         "resolution_status": "resolved", "source_text": "Earlier we saw 40% of cases."},
        {"component_id": "c2", "type": "narration", "doc_ordinal": 2, "locator": "deck#2",
         "resolution_status": "resolved", "source_text": "Target."},
    ]
    parsed = _parsed(_Z_ORDER_OK)
    result = _attach_warm_callbacks(
        parsed, _envelope(components), _roster(),
        model_invoke=_fake_invoke("Recall the 40% we saw."),
    )
    segment = result["narration_script"][0]
    assert "40" not in segment["narration_text"]  # dropped, never injected
    dropped = [rec for rec in _audit_of(result) if rec["decision"] == "dropped"]
    assert dropped and "current-slide" in dropped[0]["reason"]
    # And the global figure gate does NOT abort (callback never reached canonical).
    _assert_figure_citations_within_perceived(result, _roster())


def test_m3_both_flags_warm_callback_role_survives_voice_direction(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    monkeypatch.setenv(VOICE_DIRECTION_ACTIVE_ENV, "1")  # BOTH flags ON
    narration = [
        {"id": "segA", "slide_id": "s1", "component_id": "cA", "narration_text": "First."}
    ]
    deltas = [
        {"id": "segA", "slide_id": "s1",
         "visual_references": [{"perception_source": "s1", "element_id": "chart"}]}
    ]
    out = _run_act_flag_on(
        monkeypatch, tmp_path,
        narration=narration, deltas=deltas,
        renderer_returns=["Recall how we established the framework."],
        grounding={"components": _carrier_components()},
    )
    delta = out["segment_manifest_deltas"][0]
    # voice_direction was rebuilt by _attach_voice_direction; the warm_callback
    # role must survive (re-stamped).
    assert delta["voice_direction"]["rhetorical_role"] == "warm_callback"


def test_m4_kept_callback_with_no_joinable_delta_is_dropped(_flag_on: None) -> None:
    # Segment id matches NO delta; slide_id matches TWO deltas ⇒ delta None ⇒ a
    # kept callback can be neither role-stamped nor 07G-teethed ⇒ must DROP.
    parsed = {
        "narration_script": [
            {"id": "segX", "slide_id": "slide-01", "component_id": "c2",
             "narration_text": _DEFAULT_NARRATION}
        ],
        "segment_manifest_deltas": [
            {"id": "d1", "slide_id": "slide-01",
             "visual_references": [{"perception_source": "slide-01", "element_id": "headline"}]},
            {"id": "d2", "slide_id": "slide-01",
             "visual_references": [{"perception_source": "slide-01", "element_id": "hero"}]},
        ],
    }
    result = _attach_warm_callbacks(
        parsed, _envelope(), _roster(),
        model_invoke=_fake_invoke("Recall how we established the framework."),
    )
    assert result["narration_script"][0]["narration_text"] == _DEFAULT_NARRATION
    for delta in result["segment_manifest_deltas"]:
        assert "voice_direction" not in delta
    dropped = [rec for rec in _audit_of(result) if rec["decision"] == "dropped"]
    assert dropped and dropped[0]["reason"] == "no-joinable-delta"


def _low_confidence_payload() -> dict[str, Any]:
    return {
        "gary_slide_output": [{"slide_id": "slide-01", "visual_description": "Z."}],
        "perception_artifacts": [
            {
                "slide_id": "slide-01",
                "confidence": "LOW",       # ⇒ roster entry carries NO reading_path
                "coverage": "low-confidence",
                "reading_path": "z_pattern",
                "visual_elements": [
                    {"id": "headline", "kind": "headline", "label": "headline",
                     "bbox": [0.05, 0.05, 0.45, 0.18]},
                ],
            }
        ],
    }


def test_s1_reading_path_missing_drops_callback_not_aborts(_flag_on: None) -> None:
    roster = _slide_roster(_low_confidence_payload())
    parsed = _parsed(["headline"])
    # No Pass2ReadingPathError — the callback is dropped (silent) for a missing
    # reading_path rather than aborting the whole run.
    result = _attach_warm_callbacks(
        parsed, _envelope(), roster,
        model_invoke=_fake_invoke("Recall how we established the framework."),
    )
    assert result["narration_script"][0]["narration_text"] == _DEFAULT_NARRATION
    dropped = [rec for rec in _audit_of(result) if rec["decision"] == "dropped"]
    assert dropped and "reading-path-missing" in dropped[0]["reason"]


def test_s2_blank_source_text_anchor_yields_no_callback(_flag_on: None) -> None:
    components = [
        {"component_id": "c1", "type": "slide", "doc_ordinal": 1, "locator": "deck#1",
         "resolution_status": "resolved", "source_text": "   "},  # blank ⇒ vacuous anchor
        {"component_id": "c2", "type": "narration", "doc_ordinal": 2, "locator": "deck#2",
         "resolution_status": "resolved", "source_text": "Target."},
    ]
    parsed = _parsed(_Z_ORDER_OK)
    result = _attach_warm_callbacks(
        parsed, _envelope(components), _roster(),
        model_invoke=_boom_invoke,  # blank anchor ⇒ must not even render
    )
    assert result["narration_script"][0]["narration_text"] == _DEFAULT_NARRATION
    assert "warm_callback_audit" not in result


def test_s3_v3_tag_leak_in_callback_is_dropped(_flag_on: None) -> None:
    parsed = _parsed(_Z_ORDER_OK)
    result = _attach_warm_callbacks(
        parsed, _envelope(), _roster(),
        model_invoke=_fake_invoke("Recall the framework [warm] we built."),
    )
    segment = result["narration_script"][0]
    assert "[warm]" not in segment["narration_text"]
    assert segment["narration_text"] == _DEFAULT_NARRATION
    dropped = [rec for rec in _audit_of(result) if rec["decision"] == "dropped"]
    assert dropped and "tag" in dropped[0]["reason"].lower()
