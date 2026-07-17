"""Flight-deck render — run-settings standing readout panel (Story 42.3).

Hermetic render-layer test (no server): drives ``render_zones`` / ``render_page``
with a projection dict that carries the new ``run_settings`` section and asserts
the persistent 16-toggle readout renders labels + resolved values, from launch
through terminal, and degrades to NOTHING when the section is absent (AC-6).
"""

from __future__ import annotations

from typing import Any

from app.hud.render import render_page, render_zones
from app.models.runtime.operator_surface import RUN_SETTINGS_TOGGLES
from tests.hud import _render_fixtures as fx

_RESOLVED = {
    "component_deck": "on",
    "component_motion": "off",
    "component_workbook": "on",
    "preset": "production",
    "encounter_mode": "recorded",
    "llm_execution_mode": "batch",
    "g0_dispatch_live": "on",
    "research_dispatch_live": "off",
    "research_detective_live": "off",
    "narration_figure_fidelity_active": "off",
    "voice_direction": "expressive",
    "deck_enrichment_active": "off",
    "udac_active": "off",
    "coverage_gate": "strict",
    "trial_budget_usd": "10.00",
    "treatment_slots": "hil-2026-apc-crossroads-classic",
}


def _run_settings() -> dict[str, Any]:
    return {"as_of": "2026-07-11T11:59:55+00:00", **_RESOLVED}


def _with_settings(proj: dict[str, Any]) -> dict[str, Any]:
    proj = dict(proj)
    proj["run_settings"] = _run_settings()
    return proj


def _identity_zone(proj: dict[str, Any]) -> str:
    return render_zones(fx.ok_data(proj))["identity-header"]


def test_panel_renders_all_sixteen_labels() -> None:
    header = _identity_zone(_with_settings(fx.in_flight_walking()))
    assert 'class="run-settings"' in header
    assert "Run settings · standing readout" in header
    for _field, label in RUN_SETTINGS_TOGGLES:
        assert label in header, f"toggle label missing from readout: {label}"
    assert len(RUN_SETTINGS_TOGGLES) == 16


def test_panel_renders_resolved_values_including_off_defaults() -> None:
    header = _identity_zone(_with_settings(fx.in_flight_walking()))
    # env-absent toggles render an explicit resolved value, never hidden (AC-2)
    assert "MARCUS_UDAC_ACTIVE" in header
    assert "rs-off" in header  # an off flag styled as off
    assert "rs-on" in header  # an on flag styled as on
    assert "batch" in header  # llm execution mode value
    assert "hil-2026-apc-crossroads-classic" in header  # treatment slots value


def test_panel_is_standing_across_launch_and_terminal_statuses() -> None:
    """Visible from launch (registered/in-flight) through terminal (completed/failed)."""
    for builder in (fx.registered, fx.in_flight_walking, fx.completed, fx.failed):
        header = _identity_zone(_with_settings(builder()))
        assert 'class="run-settings"' in header, builder.__name__
        assert "MARCUS_G0_DISPATCH_LIVE" in header, builder.__name__


def test_panel_absent_when_section_missing_backcompat() -> None:
    """AC-6: a pre-42.3 surface (no run_settings) renders no readout panel and is
    otherwise unaffected."""
    header = _identity_zone(fx.in_flight_walking())  # fixtures carry no run_settings
    assert 'class="run-settings"' not in header
    # the rest of the identity header still renders normally
    assert "lesson" in header


def test_full_page_includes_the_readout() -> None:
    page = render_page(fx.ok_data(_with_settings(fx.in_flight_walking())))
    assert "Run settings · standing readout" in page
    assert "Coverage-gate family" in page
