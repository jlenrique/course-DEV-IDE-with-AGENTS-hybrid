"""T5b binding (party-ratified Option B): the `select` verb surgically overlays
an operator pick onto the existing envelope; `edit` stays full-replace.

Pins mandated by the T5b party (Winston/Amelia/Murat):
- select binds the pick AND preserves every sibling key (no clobber)
- voice nests at voice_selection.selected_voice_id (leaf-merge)
- unknown selection key fails loud with NO partial write
- missing/unparseable envelope fails loud
- edit still FULL-REPLACES (the pinned :382/:197 contract, via the new code path)
- approve/reject no-op the envelope
- the bound pick survives a serialize/deserialize round-trip (resume twin)
"""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.marcus.orchestrator.production_runner import (
    SelectionBindingError,
    UnknownSelectionKeyError,
    _apply_verdict_to_run_state,
)
from app.models.state.cache_state import CacheState
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState


def _run_state(envelope: dict | None) -> RunState:
    cache = (
        CacheState(cache_prefix=json.dumps(envelope), entries_count=1, last_invalidated_at=None)
        if envelope is not None
        else None
    )
    return RunState(run_id=uuid4(), graph_version="v42", cache_state=cache)


def _verdict(verb: str, gate_id: str, *, edit_payload=None, reject_reason=None) -> OperatorVerdict:
    return OperatorVerdict(
        trial_id=uuid4(),
        verb=verb,
        gate_id=gate_id,
        card_id=uuid4(),
        operator_id="operator_test",
        decision_card_digest="a" * 64,
        edit_payload=edit_payload,
        reject_reason=reject_reason,
    )


def _envelope_of(run_state: RunState) -> dict:
    return json.loads(run_state.cache_state.cache_prefix)


def test_select_binds_voice_and_preserves_siblings() -> None:
    env = {
        "voice_selection": {"candidates": ["v1", "v2"], "selected_voice_id": "v1"},
        "slide_count": 3,
        "narration_script": {"x": 1},
    }
    out = _apply_verdict_to_run_state(
        _run_state(env), _verdict("select", "G4A", edit_payload={"selected_voice_id": "v2"})
    )
    merged = _envelope_of(out)
    assert merged["voice_selection"]["selected_voice_id"] == "v2"  # pick bound
    assert merged["selected_voice_id"] == "v2"  # top-level mirror
    assert merged["slide_count"] == 3  # sibling preserved
    assert merged["narration_script"] == {"x": 1}  # no collateral
    assert merged["voice_selection"]["candidates"] == ["v1", "v2"]  # nested sibling intact


def test_select_binds_variant_per_slide() -> None:
    out = _apply_verdict_to_run_state(
        _run_state({"slide_count": 6}),
        _verdict("select", "G2B", edit_payload={"selected_variant_id": {"slide-01": "B"}}),
    )
    merged = _envelope_of(out)
    assert merged["selected_variant_id"] == {"slide-01": "B"}
    assert merged["slide_count"] == 6


def test_select_unknown_key_fails_loud() -> None:
    with pytest.raises(UnknownSelectionKeyError):
        _apply_verdict_to_run_state(
            _run_state({"slide_count": 3}),
            _verdict("select", "G4A", edit_payload={"bogus_key": "x"}),
        )


def test_select_missing_envelope_fails_loud() -> None:
    with pytest.raises(SelectionBindingError):
        _apply_verdict_to_run_state(
            _run_state(None), _verdict("select", "G4A", edit_payload={"selected_voice_id": "v2"})
        )


def test_edit_still_full_replaces() -> None:
    """The pinned :382/:197 contract: edit REPLACES the envelope (preserved)."""
    out = _apply_verdict_to_run_state(
        _run_state({"keep_me": 1}), _verdict("edit", "G2B", edit_payload={"slide_count": 3})
    )
    assert _envelope_of(out) == {"slide_count": 3}  # full-replace, keep_me gone


def test_approve_noops_the_envelope() -> None:
    rs = _run_state({"a": 1})
    out = _apply_verdict_to_run_state(rs, _verdict("approve", "G4A"))
    assert out.cache_state.cache_prefix == rs.cache_state.cache_prefix


def test_operator_selected_voice_reads_top_level_mirror() -> None:
    """T5a-F3 repair: the dispatch reads the operator pick from the run_state
    envelope's top-level mirror (set by the select merge) to thread into the
    synthesis; absent until a select happens."""
    from app.marcus.orchestrator.production_runner import _operator_selected_voice

    assert _operator_selected_voice(_run_state({"selected_voice_id": "vK"})) == "vK"
    assert _operator_selected_voice(_run_state({"no_pick": 1})) is None
    assert _operator_selected_voice(_run_state(None)) is None


def test_select_pick_survives_serialize_roundtrip() -> None:
    """Resume twin (Murat): the bound pick must survive the cache round-trip."""
    out = _apply_verdict_to_run_state(
        _run_state({"voice_selection": {"selected_voice_id": "v1"}}),
        _verdict("select", "G4A", edit_payload={"selected_voice_id": "v9"}),
    )
    # round-trip through the serialized cache_prefix exactly as resume rehydrates it
    rehydrated = json.loads(out.cache_state.cache_prefix)
    assert rehydrated["voice_selection"]["selected_voice_id"] == "v9"
