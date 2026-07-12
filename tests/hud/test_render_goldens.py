"""Flight-deck render goldens (Story 35.5; AD-12 + UX spines binding).

The v1 golden matrix (party greenlight amendment 10): 7 envelope statuses +
4 panel states (no-active-run / unrecognized / refuse-to-render / stale-veil) +
narrowed-component-selection (amendment 11) + legacy-shaped-dir → UNRECOGNIZED.

Assertions pin the load-bearing, never-cut behaviours: distinct annunciator
text+class per status, verbatim status strings, verbatim command blocks for the
three pause classes, deliverables paths on completed, annunciator severity
ordering (stale + gate → gate wins), urgency auto-expand attributes, and
DESIGN.md token hexes present in the emitted CSS.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.hud.render import render_page, render_zones
from app.hud.server import create_hud_app
from tests.hud import _render_fixtures as fx
from tests.hud._helpers import write_projection_file

# ---- the seven envelope-status data envelopes -----------------------------

_STATUS_BUILDERS = {
    "registered": fx.registered,
    "in-flight (preflight)": fx.in_flight_preflight,
    "in-flight (walking)": fx.in_flight_walking,
    "paused-at-gate": fx.paused_at_gate,
    "paused-at-error": fx.paused_at_error,
    "waiting_for_provider_batch": fx.waiting_for_provider_batch,
    "completed": fx.completed,
    "failed": fx.failed,
}


def _zones(builder) -> dict[str, str]:
    return render_zones(fx.ok_data(builder()))


# --------------------------------------------------------------------------
# Distinct annunciator per status (success criterion 1) + verbatim status
# --------------------------------------------------------------------------


def test_every_status_annunciator_is_distinct() -> None:
    annunciators = [_zones(b)["annunciator"] for b in _STATUS_BUILDERS.values()]
    assert len(set(annunciators)) == len(annunciators), "annunciators must be distinct per status"


def test_annunciator_text_and_class_per_status() -> None:
    cases = {
        "registered": ("ann-nominal", "REGISTERED"),
        "in-flight (preflight)": ("ann-nominal", "PRE-FLIGHT IN PROGRESS"),
        "in-flight (walking)": ("ann-nominal", "IN FLIGHT — 07"),
        "paused-at-gate": ("ann-gate", "PAUSED AT GATE G4A"),
        "paused-at-error": ("ann-error", "PAUSED AT ERROR — irene.figure-contradiction"),
        "waiting_for_provider_batch": ("ann-wait", "PARKED — PROVIDER BATCH batch_abc123"),
        "completed": ("ann-completed", "LANDED — completed 14:02:11"),
        "failed": ("ann-failed", "FAILED — gary.export-timeout"),
    }
    for name, (cls, text) in cases.items():
        ann = _zones(_STATUS_BUILDERS[name])["annunciator"]
        assert cls in ann, (name, ann)
        assert text in ann, (name, ann)


def test_status_badge_renders_verbatim_strings() -> None:
    verbatims = (
        "paused-at-gate",
        "paused-at-error",
        "waiting_for_provider_batch",
        "completed",
    )
    for verbatim in verbatims:
        header = _zones(_STATUS_BUILDERS[verbatim])["identity-header"]
        assert f"</span> {verbatim}</span>" in header, (verbatim, header)


# --------------------------------------------------------------------------
# Command blocks — present + verbatim for the three pause classes (FR4/5/6/15)
# --------------------------------------------------------------------------


def test_command_blocks_present_and_verbatim() -> None:
    cases = {
        "paused-at-gate": fx.GATE_CMD,
        "paused-at-error": fx.RECOVER_CMD,
        "waiting_for_provider_batch": fx.BATCH_CMD,
    }
    for status, command in cases.items():
        deck = _zones(_STATUS_BUILDERS[status])["main-deck"]
        assert '<div class="cmd">' in deck, status
        assert command in deck, (status, command)


# --------------------------------------------------------------------------
# Deliverables summary on completed (FR16)
# --------------------------------------------------------------------------


def _land_brief(proj) -> str:
    """The completed context column (land-brief) — never the specialist chips."""
    deck = render_zones(fx.ok_data(proj))["main-deck"]
    return deck.split("ctxcol", 1)[1]


def test_completed_deck_lists_deliverable_paths() -> None:
    """Story 35.9: deliverables come from projection.deliverables, not roster."""
    brief = _land_brief(fx.completed())
    assert "land-brief" in brief
    # export paths from the deliverables section (runtime-owned)
    assert "exports/deck-export.pptx" in brief
    assert "exports/lesson-workbook.docx" in brief
    assert "exports/motion-segment-01.mp4" in brief
    # final cost line from deliverables.total_cost_usd
    assert "final cost" in brief
    assert "$0.31" in brief
    # component chips
    assert "DECK" in brief and "MOTION" in brief and "WORKBOOK" in brief


def test_completed_deliverables_are_not_synthesized_from_specialists() -> None:
    """AD-1 restoration: the land-brief never re-derives deliverables from roster.

    The specialist chips still carry ``last_artifact`` (a legitimate roster
    field); the DELETED thing is the completed briefing synthesizing its
    deliverables list from those paths. With no deliverables section the
    land-brief shows the run-dir pointer, not roster artifacts.
    """
    proj = fx.completed()
    del proj["deliverables"]
    brief = _land_brief(proj)
    assert "see run dir for exports" in brief
    # roster last_artifact paths must NOT leak into the deliverables briefing
    assert "07-gary-dispatch/deck-export.pptx" not in brief
    assert "02-texas/corpus.json" not in brief


def test_gate_briefing_renders_decision_card() -> None:
    deck = _zones(fx.paused_at_gate)["main-deck"]
    assert "gate focus" in deck
    assert "voice_selection" in deck
    assert "Approve the proposed voice" in deck  # operator_prompt verbatim
    assert "voice options: Sarah, Shannon, Stark, Mark" in deck  # pick_context
    # command block still present + verbatim (never cut)
    assert fx.GATE_CMD in deck


def test_gate_briefing_renders_drafted_proposal_and_confidence() -> None:
    proj = fx.paused_at_gate()
    proj["decision_card"] = {
        "as_of": proj["decision_card"]["as_of"],
        "gate_focus": "trial_open",
        "operator_prompt": None,
        "drafted_proposal": {
            "decision": "revise",
            "confidence": 0.72,
            "rationale": "minor taxonomy issues remain",
        },
        "pick_context": [],
        "evidence": ["production-runner (04)", "runs/x/texas.md"],
    }
    deck = render_zones(fx.ok_data(proj))["main-deck"]
    assert "drafted proposal" in deck
    assert "revise" in deck
    assert "confidence 0.72" in deck
    assert "runs/x/texas.md" in deck


def test_error_briefing_renders_verbatim_message_and_reentry() -> None:
    deck = _zones(fx.paused_at_error)["main-deck"]
    assert "scope=narration; slide slide-05 narration figures not present" in deck
    assert "irene.pass2.figure-contradiction" in deck
    assert "node index 33" in deck
    assert "re-entry" in deck
    assert fx.RECOVER_CMD in deck


# --------------------------------------------------------------------------
# Severity ordering: a stale tile plus a gate pause → gate wins.
# --------------------------------------------------------------------------


def test_gate_outranks_stale_in_annunciator() -> None:
    ann = render_zones(fx.ok_data(fx.paused_at_gate_stale()))["annunciator"]
    assert "ann-gate" in ann
    assert "PAUSED AT GATE G4A" in ann
    assert "ann-feedlost" not in ann and "STALE" not in ann
    # …but the stale tile itself still veils in the health strip.
    health = render_zones(fx.ok_data(fx.paused_at_gate_stale()))["health-strip"]
    assert "tile stale" in health
    assert "STALE · last good" in health


# --------------------------------------------------------------------------
# Urgency auto-expand contract (carried from hud_per_step_summary.py).
# --------------------------------------------------------------------------


def test_active_map_node_auto_expands() -> None:
    deck = _zones(fx.in_flight_walking)["main-deck"]
    assert 'data-auto-open="urgent"' in deck
    # the active node (07) is the current step → its <details> is open
    assert 'class="node active"' in deck
    assert 'class="node active" data-auto-open="urgent" open' in deck


def test_conditions_on_a_node_force_open_even_if_not_current() -> None:
    # The gate fixture's active node carries a condition; assert auto-open present.
    deck = _zones(fx.paused_at_gate)["main-deck"]
    assert 'data-auto-open="urgent"' in deck


# --------------------------------------------------------------------------
# Two-stage map: pre-ratification placeholder + ratified node list.
# --------------------------------------------------------------------------


def test_registered_map_shows_stage2_placeholder() -> None:
    deck = _zones(fx.registered)["main-deck"]
    assert "workflow pends ratification" in deck


def test_walking_map_shows_two_stages() -> None:
    deck = _zones(fx.in_flight_walking)["main-deck"]
    assert "Planning — intake" in deck
    assert "Ratified workflow — 47 nodes · Step 21/47" in deck


def test_narrowed_component_selection_reduced_map() -> None:
    deck = render_zones(fx.ok_data(fx.narrowed_component_selection()))["main-deck"]
    assert "07W" in deck  # workbook node
    assert "13" in deck  # motion node
    assert "Ratified workflow — 3 nodes" in deck


# --------------------------------------------------------------------------
# Health strip: staleness stamps + confidence tags + threshold ring.
# --------------------------------------------------------------------------


def test_health_strip_stamps_and_confidence() -> None:
    health = _zones(fx.in_flight_walking)["health-strip"]
    assert "as of 11:59:55 · 5s ago" in health  # age stamp on a fresh tile
    assert '<span class="conf">direct</span>' in health
    assert "tile warn" in health  # Gamma tile threshold_state == warning


def test_stale_veil_panel() -> None:
    health = render_zones(fx.stale_veil_data())["health-strip"]
    assert "tile stale" in health
    assert "⧗ STALE · last good" in health


# --------------------------------------------------------------------------
# Modality chips + specialist chips (trimmed depth per ladder).
# --------------------------------------------------------------------------


def test_modality_chips_render_all_three() -> None:
    header = _zones(fx.in_flight_walking)["identity-header"]
    assert "BATCH" in header and "chip on batch" in header  # batch active, violet dot
    assert "DETECTIVE" in header
    assert "hil-2026-apc-crossroads-classic-preserve" in header


def test_specialist_chips_are_trimmed() -> None:
    deck = _zones(fx.in_flight_walking)["main-deck"]
    assert "spec-row" in deck
    assert ">GA<" in deck  # Gary monogram
    # ladder: model-in-use + cost attribution dropped from the chip
    assert "gpt-5" not in deck
    assert "cost_usd" not in deck


# --------------------------------------------------------------------------
# State-trace well (minimal append-only feed).
# --------------------------------------------------------------------------


def test_state_trace_feed() -> None:
    trace = _zones(fx.in_flight_walking)["state-trace"]
    assert "State trace — 2 events" in trace
    assert "node 07 enter" in trace


def test_empty_trace_shows_no_events() -> None:
    trace = _zones(fx.registered)["state-trace"]
    assert "no events yet" in trace


# --------------------------------------------------------------------------
# Panel states.
# --------------------------------------------------------------------------


def test_no_active_run_panel() -> None:
    page = render_page(fx.no_active_run_data())
    assert "NO ACTIVE RUN" in page


def test_unrecognized_panel_quotes_raw_and_schema() -> None:
    page = render_page(fx.unrecognized_data())
    assert "UNRECOGNIZED" in page
    assert "v99" in page
    assert "archived legacy shape" in page  # raw value rendered literally


def test_refuse_to_render_panel() -> None:
    page = render_page(fx.refuse_to_render_data())
    assert "RUN IDENTITY UNCERTAIN" in page
    assert fx.TRIAL in page
    assert fx.OTHER in page


# --------------------------------------------------------------------------
# DESIGN.md token hexes present in the emitted CSS.
# --------------------------------------------------------------------------


def test_design_tokens_present_in_css() -> None:
    page = render_page(fx.ok_data(fx.in_flight_walking()))
    for hexv in (
        "#0F172A",  # surface-base
        "#1E293B",  # surface-raised
        "#0B1120",  # surface-inset
        "#293548",  # border-hairline
        "#E2E8F0",  # ink-primary
        "#38BDF8",  # active cyan
        "#22C55E",  # nominal green
        "#FBBF24",  # caution amber
        "#EF4444",  # warning red
        "#A78BFA",  # wait violet
        "#64748B",  # idle slate
    ):
        assert hexv in page, hexv


def test_reduced_motion_and_aria_live_present() -> None:
    page = render_page(fx.ok_data(fx.in_flight_walking()))
    assert "prefers-reduced-motion" in page
    assert 'aria-live="polite"' in page


# --------------------------------------------------------------------------
# Legacy-shaped run dir → UNRECOGNIZED (L2), via the real server route.
# --------------------------------------------------------------------------


def test_legacy_shaped_run_dir_renders_unrecognized(run_dir) -> None:
    bound = uuid.UUID(fx.TRIAL)
    # An April-era HUD shape: matching identity, but an unknown schema_version.
    legacy = (
        '{"schema_version": "april-hud-v0", "trial_id": "'
        + fx.TRIAL
        + '", "panels": {"dev_cycle": true}}'
    )
    write_projection_file(run_dir, legacy.encode("utf-8"))
    app = create_hud_app(str(bound), run_dir, "n", "session")
    resp = TestClient(app).get("/")
    assert resp.status_code == 200
    body = resp.text
    assert "UNRECOGNIZED" in body
    assert "april-hud-v0" in body  # raw value quoted literally (zero-lie)
    # Dev-Cycle / M5 panels never return as chrome — only echoed as raw text.
    assert 'class="tab' not in body
