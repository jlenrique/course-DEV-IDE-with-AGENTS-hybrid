"""Story 43-4 — G4A voice-candidate selection renderer (+ the gate→renderer bridge).

Replay-only against the SYNTHETIC fixture ``poll-voice-candidates-synthetic.json``
under ``tests/fixtures/hil_projector/`` (built by invoking the REAL ``G4ACard`` model
— the card body the runner surfaces at a paused G4A ``11-gate``; zero live spend).

Proves:

* **AC-1** — ``render_voice_candidates`` tables the candidate voices one row per
  candidate with distinguishing fields (**G4A voice-candidate selection**).
* **AC-2 (the bridge)** — a paused ``G4A`` gate routes through
  ``GATE_TO_CONTENT_TYPE`` to the BESPOKE renderer, NOT the generic fallback, both at
  the resolver level AND end-to-end through ``trial.py::_emit_gate_surface_if_paused``.
* **AC-4** — ``voice_candidates`` moved allowlist → registry (disjoint invariant holds).
* **AC-5** — no raw ``Field | Value`` dump; the renderer stays stdlib-pure and
  tolerates BOTH the bare card body AND the nested ``decision_card`` display shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import app.marcus.cli.trial as trial
from app.marcus.cli.hil_tabular_projector import (
    KNOWN_UNRENDERED_ALLOWLIST,
    get_renderer,
    registered_content_types,
    render_gate_content,
    render_generic_gate_content,
    render_voice_candidates,
    resolve_content_type,
)

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "hil_projector"
VOICE_FIXTURE = FIXTURES / "poll-voice-candidates-synthetic.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# AC-4 — allowlist → registry move.
# ---------------------------------------------------------------------------


def test_renderer_is_registered_and_off_the_allowlist() -> None:
    """AC-4: ``voice_candidates`` dispatches to the bespoke renderer and has LEFT the
    shrink-only allowlist (disjoint invariant requires the deletion)."""
    assert "voice_candidates" in registered_content_types()
    assert "voice_candidates" not in KNOWN_UNRENDERED_ALLOWLIST
    assert get_renderer("voice_candidates") is render_voice_candidates


# ---------------------------------------------------------------------------
# AC-2 — the gate→content_type bridge (resolver level).
# ---------------------------------------------------------------------------


def test_bridge_maps_paused_g4a_gate_to_voice_candidates() -> None:
    """AC-2: the paused-gate string (G4A) and the section_11 poll-surface
    ``surface_id`` both resolve to the SEMANTIC ``voice_candidates`` key."""
    assert resolve_content_type("G4A") == "voice_candidates"
    assert resolve_content_type("section_11_g4a_voice_selection") == "voice_candidates"


def test_bridge_routes_paused_g4a_to_bespoke_renderer_not_generic() -> None:
    """AC-2: resolving the paused G4A gate then fetching the renderer yields the
    BESPOKE renderer, not the generic fallback."""
    assert get_renderer(resolve_content_type("G4A")) is render_voice_candidates
    assert get_renderer(resolve_content_type("G4A")) is not render_generic_gate_content


# ---------------------------------------------------------------------------
# AC-1 — G4A voice-candidate table shape.
# ---------------------------------------------------------------------------


def test_voice_candidates_table_shape() -> None:
    """AC-1 (names **G4A voice-candidate selection**): the rendered table carries the
    banner, one row per candidate voice, and each voice's distinguishing fields
    (name / voice_id / gender / accent / use-case)."""
    content = _load(VOICE_FIXTURE)
    out = render_voice_candidates(content)

    assert "G4A voice-candidate selection" in out
    assert "| # | Voice | voice_id | Gender | Accent | Use case | Sel |" in out
    # 4 candidate voices, one row each — names + voice_ids present. Long names are
    # width-capped (rider R5), so assert on truncation-safe distinctive prefixes.
    assert "Sarah - Mature, Reassuring, Confident" in out
    assert "Shannon - Modern Professional" in out
    assert "Stark - Classic American Voice" in out
    assert "Mark - ConvoAI" in out
    for voice_id in (
        "EXAVITQu4vr4xnSDxMaL",
        "0GoLoBHogFMTLhDROxLD",
        "W6zuQRTYRBdAK8ypjo5V",
        "1SM7GgM6IMuvQlz2BwM3",
    ):
        assert voice_id in out
    # Distinguishing characteristics columns (not a raw Field|Value dump).
    assert "female" in out
    assert "informative_educational" in out
    assert "4 candidate(s)" in out
    # No pick made yet -> default-accept note.
    assert "no pick yet (default-accept)" in out
    # NOT the generic fallback.
    assert "| Field | Value |" not in out


def test_voice_candidates_dispatch_through_render_gate_content() -> None:
    """AC-1: dispatch via the registry (``content_type='voice_candidates'``) yields
    the bespoke table, not the generic Field|Value fallback."""
    content = _load(VOICE_FIXTURE)
    out = render_gate_content(content, content_type="voice_candidates")
    assert "G4A voice-candidate selection" in out
    assert "| Field | Value |" not in out


# ---------------------------------------------------------------------------
# AC-5 — robustness: tolerate the nested display shape AND the bare card body;
#        tolerate the bare voice_candidates id list with no options block.
# ---------------------------------------------------------------------------


def test_voice_candidates_accepts_nested_display_shape() -> None:
    """AC-5: the renderer tolerates the section_11
    ``display_voice_candidates``-style shape (the card body nested under
    ``decision_card``), not only the bare card body."""
    card = _load(VOICE_FIXTURE)
    nested = {
        "surface_id": "section_11_g4a_voice_selection",
        "voice_selection_id": card["card_id"],
        "decision_card_digest": card["decision_card_digest"],
        "decision_card": card,
    }
    out = render_voice_candidates(nested)
    assert "G4A voice-candidate selection" in out
    assert "Sarah - Mature, Reassuring, Confident" in out
    assert "| Field | Value |" not in out


def test_voice_candidates_falls_back_to_bare_id_list() -> None:
    """AC-5: a card carrying only the bare ``voice_candidates`` id list (no adjacent
    ``pick_context`` voice-options block) still tables one row per candidate id."""
    content = {
        "voice_candidates": ["voiceAAA", "voiceBBB"],
        "selected_voice_id": "voiceBBB",
        "pick_context": [{"kind": "production-runner", "node_id": "11-gate"}],
    }
    out = render_voice_candidates(content)
    assert "G4A voice-candidate selection" in out
    assert "2 candidate(s)" in out
    assert "voiceAAA" in out
    assert "voiceBBB" in out
    # The selected voice is marked; the pick note names it.
    assert "selected voiceBBB" in out
    assert "| Field | Value |" not in out


# ---------------------------------------------------------------------------
# AC-2 (end-to-end) — a PAUSED G4A gate routes to the bespoke renderer via trial.py.
# ---------------------------------------------------------------------------


def _write_paused_run(
    tmp_path: Path, *, gate: str, card_body: dict[str, Any]
) -> dict[str, Any]:
    """Materialize a minimal paused-at-gate run dir + payload for the given gate."""
    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"decision-card-{gate}.json").write_text(
        json.dumps({"card": card_body}, indent=2), encoding="utf-8"
    )
    return {
        "status": "paused-at-gate",
        "trial_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
        "paused_gate": gate,
        "operator_id": "operator",
        "run_registry_path": str(run_dir / "run-registry.json"),
    }


def test_paused_g4a_routes_to_bespoke_voice_renderer_via_trial(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC-2 (end-to-end): a paused G4A fixture emitted through
    ``trial.py::_emit_gate_surface_if_paused`` reaches the BESPOKE voice-candidate
    renderer (its banner appears on stderr), NOT the generic Field|Value fallback."""
    card_body = _load(VOICE_FIXTURE)
    payload = _write_paused_run(tmp_path, gate="G4A", card_body=card_body)

    trial._emit_gate_surface_if_paused(payload, runs_root=tmp_path)

    err = capsys.readouterr().err
    assert "G4A voice-candidate selection" in err  # bespoke renderer fired
    assert "Sarah - Mature, Reassuring, Confident" in err
    assert "EXAVITQu4vr4xnSDxMaL" in err
    assert "| Field | Value |" not in err  # generic fallback did NOT fire
