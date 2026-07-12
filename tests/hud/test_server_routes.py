"""Route-inventory + transport tests for the GET-only HUD server (Story 35.4).

Witness set: route inventory (no non-GET, count==3), ETag/304, refuse-to-render,
healthz payload, lenient/raw passthrough (AD-6/8).
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.hud.server import create_hud_app, run_hud_server
from tests.hud._helpers import (
    build_registered_projection,
    mutate_projection_dict,
    write_projection,
    write_projection_file,
)

_MUTATING_METHODS = {"POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"}
_EXPECTED_PATHS = {"/", "/projection", "/healthz"}


@pytest.fixture
def client(run_dir, bound_trial_id) -> TestClient:
    write_projection(
        run_dir, build_registered_projection(trial_id=bound_trial_id, seq=1)
    )
    app = create_hud_app(
        trial_id=str(bound_trial_id),
        run_dir=run_dir,
        launch_nonce="nonce-abc",
        mode="session",
    )
    return TestClient(app)


# --------------------------------------------------------------------------
# Route inventory (AD-6): EXACTLY three GET routes, no mutation surface.
# --------------------------------------------------------------------------


def test_route_inventory_is_exactly_three_get_routes(run_dir, bound_trial_id) -> None:
    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    api_routes = [r for r in app.routes if isinstance(r, APIRoute)]

    assert len(api_routes) == 3, [r.path for r in api_routes]
    assert {r.path for r in api_routes} == _EXPECTED_PATHS

    for route in api_routes:
        assert route.methods == {"GET"}, (route.path, route.methods)


def test_no_route_exposes_a_mutating_verb(run_dir, bound_trial_id) -> None:
    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        assert not (methods & _MUTATING_METHODS), (getattr(route, "path", "?"), methods)


def test_no_websocket_or_mount_routes(run_dir, bound_trial_id) -> None:
    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    kinds = {type(r).__name__ for r in app.routes}
    assert "WebSocketRoute" not in kinds
    assert "Mount" not in kinds
    assert kinds <= {"APIRoute"}, kinds


def test_mutating_requests_are_rejected(client: TestClient) -> None:
    for path in _EXPECTED_PATHS:
        assert client.post(path).status_code == 405
        assert client.put(path).status_code == 405
        assert client.delete(path).status_code == 405


# --------------------------------------------------------------------------
# /healthz identity payload (AD-7).
# --------------------------------------------------------------------------


def test_healthz_returns_identity_payload(run_dir, bound_trial_id) -> None:
    app = create_hud_app(str(bound_trial_id), run_dir, "nonce-xyz", "standalone")
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {
        "trial_id": str(bound_trial_id),
        "launch_nonce": "nonce-xyz",
        "mode": "standalone",
    }


# --------------------------------------------------------------------------
# ETag / 304 (AD-6): route-implemented If-None-Match.
# --------------------------------------------------------------------------


def test_projection_first_get_is_200_with_quoted_seq_etag(client: TestClient) -> None:
    resp = client.get("/projection")
    assert resp.status_code == 200
    # RFC 9110: an entity-tag is the quoted form — pin it exactly.
    assert resp.headers["ETag"] == '"v1:1"'
    assert resp.headers["Cache-Control"] == "no-cache"
    assert resp.json()["envelope"]["status"] == "registered"


def test_conditional_get_matching_etag_is_304(client: TestClient) -> None:
    first = client.get("/projection")
    etag = first.headers["ETag"]
    second = client.get("/projection", headers={"If-None-Match": etag})
    assert second.status_code == 304
    assert second.headers["ETag"] == etag
    assert second.content == b""


def test_seq_bump_changes_etag_and_returns_200(
    client: TestClient, run_dir, bound_trial_id
) -> None:
    first = client.get("/projection")
    assert first.headers["ETag"] == '"v1:1"'

    # Producer writes a new snapshot with a bumped seq (every write bumps seq).
    write_projection(
        run_dir, build_registered_projection(trial_id=bound_trial_id, seq=2)
    )
    # The stale conditional now misses -> fresh 200 with the new ETag.
    resp = client.get("/projection", headers={"If-None-Match": '"v1:1"'})
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v1:2"'


def test_conditional_get_weak_validator_matches_304(client: TestClient) -> None:
    resp = client.get("/projection", headers={"If-None-Match": 'W/"v1:1"'})
    assert resp.status_code == 304


def test_conditional_get_comma_list_matches_304(client: TestClient) -> None:
    resp = client.get(
        "/projection", headers={"If-None-Match": '"v0:9", W/"v9:9", "v1:1"'}
    )
    assert resp.status_code == 304


def test_conditional_get_star_matches_304(client: TestClient) -> None:
    resp = client.get("/projection", headers={"If-None-Match": "*"})
    assert resp.status_code == 304


def test_conditional_get_non_matching_list_misses_200(client: TestClient) -> None:
    resp = client.get(
        "/projection", headers={"If-None-Match": '"v0:1", W/"v2:7"'}
    )
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v1:1"'


# --------------------------------------------------------------------------
# Refuse-to-render identity guard (AD-8).
# --------------------------------------------------------------------------


def test_identity_mismatch_returns_409_typed_payload(run_dir, bound_trial_id) -> None:
    other = uuid.UUID("22222222-2222-4222-8222-222222222222")
    write_projection(run_dir, build_registered_projection(trial_id=other, seq=5))
    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    client = TestClient(app)

    resp = client.get("/projection")
    assert resp.status_code == 409
    payload = resp.json()
    assert payload["refuse_to_render"] is True
    assert payload["bound"] == str(bound_trial_id)
    assert payload["found"] == str(other)


def test_matching_identity_renders(client: TestClient) -> None:
    assert client.get("/projection").status_code == 200


def test_unrecognized_snapshot_with_foreign_identity_is_409(
    run_dir, bound_trial_id
) -> None:
    """Probe case (MUST-1): lenient-parse failure must not bypass the guard.

    A valid-shaped v1 document with a FOREIGN identity.trial_id plus one
    malformed sibling field (as_of) lenient-parses to Unrecognized — but the
    raw dict still carries a perfectly readable foreign identity. Serving it
    raw 200 would render the wrong run's envelope.status (AD-8 breach).
    """
    other = uuid.UUID("22222222-2222-4222-8222-222222222222")
    proj = build_registered_projection(trial_id=other, seq=5)
    data = mutate_projection_dict(proj, as_of="not-a-timestamp")
    write_projection_file(
        run_dir, (json.dumps(data, indent=2) + "\n").encode("utf-8")
    )

    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    assert resp.status_code == 409
    payload = resp.json()
    assert payload["refuse_to_render"] is True
    assert payload["bound"] == str(bound_trial_id)
    assert payload["found"] == str(other)


def test_unrecognized_snapshot_with_foreign_top_level_trial_id_is_409(
    run_dir, bound_trial_id
) -> None:
    """MUST-1: a readable top-level trial_id is identity too — guard it."""
    other = uuid.UUID("33333333-3333-4333-8333-333333333333")
    write_projection_file(
        run_dir,
        json.dumps({"trial_id": str(other), "junk": True}).encode("utf-8"),
    )

    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    assert resp.status_code == 409
    assert resp.json()["found"] == str(other)


def test_unrecognized_snapshot_with_matching_raw_identity_serves_raw(
    run_dir, bound_trial_id
) -> None:
    """MUST-1 counterpart: matching raw identity still passes the guard."""
    proj = build_registered_projection(trial_id=bound_trial_id, seq=5)
    data = mutate_projection_dict(proj, as_of="not-a-timestamp")
    write_projection_file(
        run_dir, (json.dumps(data, indent=2) + "\n").encode("utf-8")
    )

    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    assert resp.status_code == 200
    assert resp.headers["ETag"].startswith('"unrecognized:')


# --------------------------------------------------------------------------
# Lenient consumption + raw passthrough (AD-4).
# --------------------------------------------------------------------------


def test_future_fields_projection_still_serves_200(run_dir, bound_trial_id) -> None:
    proj = build_registered_projection(trial_id=bound_trial_id, seq=3)
    data = mutate_projection_dict(proj, unknown_future_field={"added": "later"})
    data["envelope"]["speculative_added"] = "tolerated"
    raw = (json.dumps(data, indent=2) + "\n").encode("utf-8")
    write_projection_file(run_dir, raw)

    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v1:3"'
    # Zero-lie: the RAW bytes are served verbatim, unknown fields intact.
    assert resp.json()["unknown_future_field"] == {"added": "later"}


def test_unknown_schema_version_serves_raw_with_unrecognized_etag(
    run_dir, bound_trial_id
) -> None:
    proj = build_registered_projection(trial_id=bound_trial_id, seq=7)
    data = mutate_projection_dict(proj, schema_version="v99")
    raw = (json.dumps(data, indent=2) + "\n").encode("utf-8")
    write_projection_file(run_dir, raw)

    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    # Unrecognized snapshot whose raw identity MATCHES the bound trial_id is
    # served raw so the HUD can render UNRECOGNIZED literally (never coerced).
    assert resp.status_code == 200
    assert resp.headers["ETag"].startswith('"unrecognized:')
    assert resp.json()["schema_version"] == "v99"


def test_garbage_projection_serves_raw_with_unrecognized_etag(
    run_dir, bound_trial_id
) -> None:
    # MUST-1 case (b): no extractable identity at all -> passes the guard, 200.
    write_projection_file(run_dir, b"{ this is not json ")
    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    assert resp.status_code == 200
    assert resp.headers["ETag"].startswith('"unrecognized:')
    assert resp.content == b"{ this is not json "


def test_absent_projection_returns_404(run_dir, bound_trial_id) -> None:
    app = create_hud_app(str(bound_trial_id), run_dir, "n", "session")
    resp = TestClient(app).get("/projection")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "projection not found"


# --------------------------------------------------------------------------
# Flight-deck page (Story 35.5 retargeted the placeholder to the real render).
# --------------------------------------------------------------------------


def test_root_serves_flight_deck_page(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    assert "#0F172A" in body  # dark cockpit background (DESIGN.md token)
    assert "/projection" in body  # real poll loop target
    assert "If-None-Match" in body  # ETag-gated polling
    assert "<button" not in body.lower()  # zero-button (banned interaction)
    # The five stable zone containers the poll renderer replaces in place.
    for zone in ("annunciator", "identity-header", "health-strip", "main-deck", "state-trace"):
        assert f'id="{zone}"' in body
    # Story 35.5 replaced the ~130-line placeholder shell with the full
    # flight-deck render (CSS tokens + poll renderer); the line-count pin is
    # updated honestly to the real page (was `< 150`).
    assert len(body.splitlines()) > 150


def test_placeholder_shell_keys_unrecognized_off_etag_prefix(
    client: TestClient,
) -> None:
    """S4: honest UNRECOGNIZED state, keyed off the ETag — no parse-throw path.

    The shell must (a) branch on the "unrecognized:" ETag prefix BEFORE any
    resp.json() so a non-JSON 200 renders UNRECOGNIZED (never falls into
    DISCONNECTED, which is reserved for transport failure), and (b) not cache
    the etag when a render fails, so the next poll retries fresh.
    """
    body = client.get("/").text
    assert 'startsWith("unrecognized:")' in body
    assert '"UNRECOGNIZED"' in body
    # DISCONNECTED is set only in the fetch catch (transport), before any
    # body parsing happens.
    assert body.count('"DISCONNECTED"') == 1
    assert body.index('"DISCONNECTED"') < body.index("resp.json()")


# --------------------------------------------------------------------------
# Env-driven entry (S3): clear exits, never tracebacks.
# --------------------------------------------------------------------------

_HUD_ENV_VARS = ("HUD_TRIAL_ID", "HUD_RUN_DIR", "HUD_LAUNCH_NONCE", "HUD_PORT")


def test_missing_hud_trial_id_exits_with_clear_message(monkeypatch) -> None:
    for name in _HUD_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(SystemExit) as excinfo:
        run_hud_server()
    assert "HUD_TRIAL_ID" in str(excinfo.value)


def test_missing_hud_run_dir_exits_with_clear_message(monkeypatch) -> None:
    for name in _HUD_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("HUD_TRIAL_ID", str(uuid.uuid4()))
    with pytest.raises(SystemExit) as excinfo:
        run_hud_server()
    assert "HUD_RUN_DIR" in str(excinfo.value)


def test_non_integer_hud_port_exits_with_clear_message(
    monkeypatch, run_dir
) -> None:
    monkeypatch.setenv("HUD_TRIAL_ID", str(uuid.uuid4()))
    monkeypatch.setenv("HUD_RUN_DIR", str(run_dir))
    monkeypatch.setenv("HUD_LAUNCH_NONCE", "nonce-env")
    monkeypatch.setenv("HUD_PORT", "eight-thousand")
    with pytest.raises(SystemExit) as excinfo:
        run_hud_server()
    message = str(excinfo.value)
    assert "HUD_PORT" in message
    assert "eight-thousand" in message
