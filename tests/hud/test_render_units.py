"""Render-unit tests for ``render_zones`` (Story 35.5).

The client poll renderer replaces zones by stable id and skips a zone whose
freshly-built HTML is byte-identical to what is installed (the "changed-only"
contract that preserves ``<details>`` open-state, scroll, and selection). These
tests pin the pure-Python guarantees that contract rests on: stable id set,
determinism (same input → same output), and per-zone change isolation (a change
that only affects one zone leaves the others byte-identical).
"""

from __future__ import annotations

from app.hud.render import ZONE_IDS, render_page, render_zones
from tests.hud import _render_fixtures as fx


def test_render_zones_returns_exactly_the_stable_zone_ids() -> None:
    zones = render_zones(fx.ok_data(fx.in_flight_walking()))
    assert set(zones) == set(ZONE_IDS)
    assert tuple(zones) == ZONE_IDS  # deterministic order


def test_render_zones_is_pure_and_deterministic() -> None:
    data = fx.ok_data(fx.in_flight_walking())
    first = render_zones(data)
    second = render_zones(data)
    assert first == second
    # …and did not mutate the input envelope.
    assert data["panel_state"] == "ok"
    assert data["projection"]["envelope"]["status"] == "in-flight"


def test_annunciator_change_isolates_to_dynamic_zones() -> None:
    """A trace-only edit changes the trace zone and nothing else.

    This is the exact property the JS zone-diff relies on: a projection delta
    confined to one section produces byte-identical HTML for the untouched
    zones, so the client never needlessly replaces them (preserving disclosure
    / scroll / selection there).
    """
    base = fx.in_flight_walking()
    edited = fx.in_flight_walking()
    edited["trace"] = {
        "as_of": edited["trace"]["as_of"],
        "events": edited["trace"]["events"]
        + [{"at": "2026-07-11T11:59:59+00:00", "event": "artifact write", "detail": "deck.pptx"}],
    }
    z0 = render_zones(fx.ok_data(base))
    z1 = render_zones(fx.ok_data(edited))
    assert z0["state-trace"] != z1["state-trace"]  # the trace zone changed
    for zone in ("annunciator", "identity-header", "health-strip", "main-deck"):
        assert z0[zone] == z1[zone], f"{zone} must be untouched by a trace-only edit"


def test_status_change_updates_annunciator_and_context() -> None:
    z_walk = render_zones(fx.ok_data(fx.in_flight_walking()))
    z_gate = render_zones(fx.ok_data(fx.paused_at_gate()))
    assert z_walk["annunciator"] != z_gate["annunciator"]
    assert z_walk["main-deck"] != z_gate["main-deck"]


def test_page_embeds_all_five_zone_containers() -> None:
    page = render_page(fx.ok_data(fx.in_flight_walking()))
    for zone in ZONE_IDS:
        assert f'<div id="{zone}">' in page
    # the poll renderer + its stable-id targets are present
    assert "/projection" in page
    assert "If-None-Match" in page
