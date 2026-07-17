"""Story 43-3 — G2B per-slide-mode + G2M A/B variant renderers (+ the gate→renderer bridge).

Replay-only against the SYNTHETIC fixtures under ``tests/fixtures/hil_projector/``
(built to the exact ``poll_surface.display_*`` return shapes; zero live spend).

Proves:

* **AC-0 (the bridge)** — a paused gate (``G2B`` / ``G2M``) routes through
  ``GATE_TO_CONTENT_TYPE`` to its BESPOKE renderer, NOT the generic fallback, both
  at the resolver level AND end-to-end through ``trial.py::_emit_gate_surface_if_paused``.
* **AC-1** — ``render_per_slide_mode`` tables the available modes (**G2B per-slide-mode
  selection**).
* **AC-2** — ``render_variant_ab`` tables the A/B variants side-by-side (**G2M A/B
  variant selection**).
* **AC-4** — both types moved allowlist → registry (disjoint invariant holds).
* **AC-5** — no raw ``Field | Value`` dump; both renderers stay stdlib-pure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import app.marcus.cli.trial as trial
from app.marcus.cli.hil_tabular_projector import (
    GATE_TO_CONTENT_TYPE,
    KNOWN_UNRENDERED_ALLOWLIST,
    get_renderer,
    registered_content_types,
    render_gate_content,
    render_generic_gate_content,
    render_per_slide_mode,
    render_variant_ab,
    resolve_content_type,
)

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "hil_projector"
MODE_FIXTURE = FIXTURES / "poll-per-slide-mode-synthetic.json"
VARIANT_FIXTURE = FIXTURES / "poll-variant-ab-synthetic.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# AC-4 — allowlist → registry moves.
# ---------------------------------------------------------------------------


def test_renderers_are_registered_and_off_the_allowlist() -> None:
    """AC-4: ``per_slide_mode`` + ``variant_ab`` dispatch to bespoke renderers and
    have LEFT the shrink-only allowlist (disjoint invariant requires the deletion)."""
    assert "per_slide_mode" in registered_content_types()
    assert "variant_ab" in registered_content_types()
    assert "per_slide_mode" not in KNOWN_UNRENDERED_ALLOWLIST
    assert "variant_ab" not in KNOWN_UNRENDERED_ALLOWLIST
    assert get_renderer("per_slide_mode") is render_per_slide_mode
    assert get_renderer("variant_ab") is render_variant_ab


# ---------------------------------------------------------------------------
# AC-0 — the gate→content_type bridge (resolver level).
# ---------------------------------------------------------------------------


def test_bridge_maps_paused_gate_strings_to_content_types() -> None:
    """AC-0: the paused-gate string (G2B/G2M) resolves to the SEMANTIC content-type
    key a bespoke renderer is registered under."""
    assert resolve_content_type("G2B") == "per_slide_mode"
    assert resolve_content_type("G2M") == "variant_ab"
    # The poll-surface ``surface_id`` is an equally valid routing key.
    assert resolve_content_type("section_05_5_g2b_per_slide_mode") == "per_slide_mode"
    assert resolve_content_type("section_07b_g2m_per_slide_variant") == "variant_ab"


def test_bridge_unmapped_gate_falls_back_to_generic() -> None:
    """AC-0: an unmapped / empty gate resolves to ``None`` → the generic fallback
    (behavior unchanged for every gate not in the bridge)."""
    assert resolve_content_type("G0") is None
    assert resolve_content_type("G1") is None
    assert resolve_content_type("") is None
    assert resolve_content_type(None) is None
    # None routes to the generic renderer, never a bespoke one.
    assert get_renderer(resolve_content_type("G1")) is render_generic_gate_content


def test_bridge_routes_paused_gate_to_bespoke_renderer_not_generic() -> None:
    """AC-0: resolving a paused gate then fetching the renderer yields the BESPOKE
    renderer, not the generic fallback."""
    assert get_renderer(resolve_content_type("G2B")) is render_per_slide_mode
    assert get_renderer(resolve_content_type("G2M")) is render_variant_ab
    assert get_renderer(resolve_content_type("G2B")) is not render_generic_gate_content


# ---------------------------------------------------------------------------
# AC-1 — G2B per-slide-mode renderer.
# ---------------------------------------------------------------------------


def test_per_slide_mode_table_shape() -> None:
    """AC-1 (names **G2B per-slide-mode selection**): the rendered table carries the
    banner, one row per available mode, and each mode's distinguishing description."""
    content = _load(MODE_FIXTURE)
    out = render_per_slide_mode(content)

    assert "G2B per-slide-mode selection" in out
    assert "| # | Mode | Description |" in out
    # Both modes from the section_05_5 poll-surface shape, one row each.
    assert "narrated-deck" in out
    assert "motion-enabled-narrated-lesson" in out
    # Distinguishing description column (not a raw Field|Value dump).
    assert "synced voiceover" in out
    assert "motion / animation clips" in out
    # NOT the generic fallback.
    assert "| Field | Value |" not in out


def test_per_slide_mode_dispatch_through_render_gate_content() -> None:
    """AC-1: dispatch via the registry (``content_type='per_slide_mode'``) yields the
    bespoke table, not the generic Field|Value fallback."""
    content = _load(MODE_FIXTURE)
    out = render_gate_content(content, content_type="per_slide_mode")
    assert "G2B per-slide-mode selection" in out
    assert "| Field | Value |" not in out


# ---------------------------------------------------------------------------
# AC-2 — G2M A/B variant renderer.
# ---------------------------------------------------------------------------


def test_variant_ab_table_shape() -> None:
    """AC-2 (names **G2M A/B variant selection**): the rendered table carries the
    banner and one row per slide with A/B variants side-by-side."""
    content = _load(VARIANT_FIXTURE)
    out = render_variant_ab(content)

    assert "G2M A/B variant selection" in out
    assert "| # | slide_id | Variant A | Variant B |" in out
    # The 4 synthetic slides awaiting A/B selection, one row each.
    for node in ("slide-node-01", "slide-node-02", "slide-node-03", "slide-node-04"):
        assert node in out
    assert "4 slide(s)" in out
    assert "| Field | Value |" not in out


def test_variant_ab_dispatch_through_render_gate_content() -> None:
    """AC-2: dispatch via the registry (``content_type='variant_ab'``) yields the
    bespoke table, not the generic Field|Value fallback."""
    content = _load(VARIANT_FIXTURE)
    out = render_gate_content(content, content_type="variant_ab")
    assert "G2M A/B variant selection" in out
    assert "| Field | Value |" not in out


# ---------------------------------------------------------------------------
# AC-5 — robustness: tolerate the nested-payload OR direct-payload shape.
# ---------------------------------------------------------------------------


def test_per_slide_mode_accepts_direct_payload() -> None:
    """AC-5: the renderer tolerates being handed the ``per_slide_mode_payload``
    mapping directly (not only the full display shape)."""
    payload = _load(MODE_FIXTURE)["per_slide_mode_payload"]
    out = render_per_slide_mode(payload)
    assert "G2B per-slide-mode selection" in out
    assert "narrated-deck" in out


def test_variant_ab_accepts_direct_payload() -> None:
    """AC-5: the renderer tolerates being handed the ``per_slide_variant_payload``
    mapping directly (falls back to ``ready_nodes`` for the slide list)."""
    payload = _load(VARIANT_FIXTURE)["per_slide_variant_payload"]
    out = render_variant_ab(payload)
    assert "G2M A/B variant selection" in out
    assert "slide-node-01" in out


# ---------------------------------------------------------------------------
# AC-0 (end-to-end) — a PAUSED gate routes to the bespoke renderer via trial.py.
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


def test_paused_g2b_routes_to_bespoke_mode_renderer_via_trial(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC-0 (end-to-end): a paused G2B fixture emitted through
    ``trial.py::_emit_gate_surface_if_paused`` reaches the BESPOKE per-slide-mode
    renderer (its banner appears on stderr), NOT the generic Field|Value fallback."""
    card_body = _load(MODE_FIXTURE)
    payload = _write_paused_run(tmp_path, gate="G2B", card_body=card_body)

    trial._emit_gate_surface_if_paused(payload, runs_root=tmp_path)

    err = capsys.readouterr().err
    assert "G2B per-slide-mode selection" in err  # bespoke renderer fired
    assert "narrated-deck" in err
    assert "| Field | Value |" not in err  # generic fallback did NOT fire


def test_paused_g2m_routes_to_bespoke_variant_renderer_via_trial(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC-0 (end-to-end): a paused G2M fixture reaches the BESPOKE A/B variant
    renderer (its banner appears on stderr), NOT the generic fallback."""
    card_body = _load(VARIANT_FIXTURE)
    payload = _write_paused_run(tmp_path, gate="G2M", card_body=card_body)

    trial._emit_gate_surface_if_paused(payload, runs_root=tmp_path)

    err = capsys.readouterr().err
    assert "G2M A/B variant selection" in err  # bespoke renderer fired
    assert "slide-node-01" in err
    assert "| Field | Value |" not in err  # generic fallback did NOT fire


def test_bridge_is_the_full_declared_map() -> None:
    """AC-0: the bridge maps exactly the declared gates (both the paused-gate string
    and the poll-surface ``surface_id`` forms), nothing stale. State pin — updated in
    lockstep as each bespoke story adds its gate (43-4 added the two G4A forms)."""
    assert GATE_TO_CONTENT_TYPE == {
        "G2B": "per_slide_mode",
        "section_05_5_g2b_per_slide_mode": "per_slide_mode",
        "G2M": "variant_ab",
        "section_07b_g2m_per_slide_variant": "variant_ab",
        # Story 43-4 — G4A voice-candidate selection (section_11 woken 11-gate).
        "G4A": "voice_candidates",
        "section_11_g4a_voice_selection": "voice_candidates",
    }
