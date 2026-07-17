"""Public read-only HUD overlay — the non-leak security bar (Story 42.4).

Hermetic. No real tunnel, no long-lived server: the public app is exercised
through the existing HUD ``TestClient`` harness, and the tunnel-child spawn is a
mocked ``popen``. The headline is the POSITIVE-ALLOWLIST proof: a projection is
seeded with a unique sentinel in EVERY forbidden location, and the public
surface (the scrubbed dict, the ``/projection`` JSON, and the rendered ``/``
HTML) is asserted to contain NONE of them — while the local authority server
DOES echo them (the contrast proves the test has teeth).
"""

from __future__ import annotations

import logging
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.hud.public import (
    ALLOWED_IDENTITY,
    FORBIDDEN_SECTIONS,
    FORBIDDEN_TOP_SCALARS,
    OFFLINE_HEADLINE,
    build_public_view,
    create_public_hud_app,
)
from app.hud.server import create_hud_app
from app.marcus.orchestrator.preflight import (
    HUD_PUBLIC_URL_SENTINEL_NAME,
    PublicOverlayConfig,
    launch_public_overlay,
    public_overlay_url,
    tunnel_argv,
)
from app.models.runtime.operator_surface import (
    HUD_CONFIG_DEFAULTS,
    DecisionCardSection,
    DeliverableComponents,
    DeliverablesSection,
    DraftedProposal,
    EnvelopeSection,
    ErrorMessageSection,
    HealthReading,
    HealthSection,
    HealthTile,
    IdentitySection,
    ModalitiesSection,
    NextActionSection,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
    PreflightItem,
    PreflightSection,
    RunSettingsSection,
    SpecialistEntry,
    SpecialistsSection,
    StepEntry,
    StepsSection,
    TraceEvent,
    TraceSection,
)
from tests.hud._helpers import write_projection, write_projection_file

# --------------------------------------------------------------------------
# Sentinels — a unique token per forbidden location. A public-surface leak of
# ANY of these fails the non-leak bar (AC-2).
# --------------------------------------------------------------------------
SECRETS = {
    "nonce": "SENTINEL-LAUNCH-NONCE",
    "operator_id": "SENTINEL-OPERATOR-ID",
    "envelope_digest": "SENTINEL-ENVELOPE-DIGEST",
    "resume_command": "SENTINEL-RESUME-COMMAND --digest SENTINEL-CMD-DIGEST",
    "manifest_digest": "SENTINEL-MANIFEST-DIGEST",
    "locked_artifact": "SENTINEL-LOCKED-ARTIFACT-PATH",
    "condition": "SENTINEL-STEP-CONDITION",
    "blocker": "SENTINEL-STEP-BLOCKER",
    "gate_focus": "SENTINEL-GATE-FOCUS",
    "operator_prompt": "SENTINEL-OPERATOR-PROMPT",
    "rationale": "SENTINEL-DRAFTED-RATIONALE",
    "pick_context": "SENTINEL-PICK-CONTEXT",
    "evidence": "SENTINEL-EVIDENCE-SOURCE-TEXT",
    "error_message": "SENTINEL-ERROR-SOURCE-TEXT",
    "preflight_output": "SENTINEL-PREFLIGHT-OUTPUT",
    "specialist_artifact": "SENTINEL-SPECIALIST-ARTIFACT-PATH",
    "specialist_model": "SENTINEL-SPECIALIST-MODEL",
    "styleguide_provenance": "SENTINEL-STYLEGUIDE-PROVENANCE-PATH",
    "export_path": "SENTINEL-DELIVERABLE-EXPORT-PATH",
    "trace_detail": "SENTINEL-TRACE-DETAIL",
}

# Values the public surface IS allowed to show — proves scrubbing isn't total.
ALLOWED_VALUES = {
    "lesson": "PUBLIC-LESSON-LABEL",
    "paused_gate": "G2B",
    "step_label": "PUBLIC-STEP-LABEL",
    "specialist_name": "PUBLIC-SPECIALIST-NAME",
    "trace_event": "PUBLIC-TRACE-EVENT",
    "run_setting": "PUBLIC-RUN-SETTING",
}

_LAUNCH_NONCE = SECRETS["nonce"]


def _now() -> datetime:
    return datetime(2026, 7, 17, 12, 0, 0, tzinfo=UTC)


def _run_settings(now: datetime) -> RunSettingsSection:
    fields = {
        name: "off"
        for name in RunSettingsSection.model_fields
        if name != "as_of"
    }
    fields["preset"] = ALLOWED_VALUES["run_setting"]
    return RunSettingsSection(as_of=now, **fields)


def build_secret_laden_projection(
    trial_id: uuid.UUID, *, seq: int = 7
) -> OperatorSurfaceProjection:
    """A paused-at-gate projection with a sentinel in EVERY forbidden location."""
    now = _now()
    return OperatorSurfaceProjection(
        seq=seq,
        progress_seq=3,
        last_progress_at=now,
        envelope_digest=SECRETS["envelope_digest"],
        as_of=now,
        identity=IdentitySection(
            as_of=now,
            trial_id=trial_id,
            lesson=ALLOWED_VALUES["lesson"],
            preset="production",
            operator_id=SECRETS["operator_id"],
        ),
        envelope=EnvelopeSection(
            as_of=now, status="paused-at-gate", paused_gate=ALLOWED_VALUES["paused_gate"]
        ),
        notifications_echo=NotificationsEchoSection(
            as_of=now, config=HUD_CONFIG_DEFAULTS, parse_status="ok"
        ),
        next_action=NextActionSection(
            as_of=now, command=SECRETS["resume_command"], pause_class="paused-at-gate"
        ),
        steps=StepsSection(
            as_of=now,
            manifest_digest=SECRETS["manifest_digest"],
            node_count=10,
            walk_index=4,
            walk_generation=1,
            entries=[
                StepEntry(
                    step_id="G2B",
                    label=ALLOWED_VALUES["step_label"],
                    stage="stage-2",
                    status="active",
                    conditions=[SECRETS["condition"]],
                    blockers=[SECRETS["blocker"]],
                    locked_artifact_summary=SECRETS["locked_artifact"],
                )
            ],
        ),
        preflight=PreflightSection(
            as_of=now,
            items=[
                PreflightItem(name="openai", state="pass", output=SECRETS["preflight_output"])
            ],
        ),
        health=HealthSection(
            as_of=now,
            tiles=[
                HealthTile(
                    as_of=now,
                    label="cost",
                    value=1.23,
                    unit="usd",
                    threshold_state="nominal",
                    history=[HealthReading(at=now, value=1.0)],
                )
            ],
        ),
        specialists=SpecialistsSection(
            as_of=now,
            roster=[
                SpecialistEntry(
                    name=ALLOWED_VALUES["specialist_name"],
                    status="active",
                    current_node="G2B",
                    model=SECRETS["specialist_model"],
                    last_artifact=SECRETS["specialist_artifact"],
                    cost_usd=0.5,
                )
            ],
        ),
        modalities=ModalitiesSection(
            as_of=now,
            llm_execution_mode="batch",
            styleguide="classic",
            styleguide_provenance=SECRETS["styleguide_provenance"],
        ),
        run_settings=_run_settings(now),
        trace=TraceSection(
            as_of=now,
            events=[
                TraceEvent(
                    at=now,
                    event=ALLOWED_VALUES["trace_event"],
                    detail=SECRETS["trace_detail"],
                )
            ],
        ),
        decision_card=DecisionCardSection(
            as_of=now,
            gate_focus=SECRETS["gate_focus"],
            operator_prompt=SECRETS["operator_prompt"],
            drafted_proposal=DraftedProposal(
                decision="accept", confidence=0.9, rationale=SECRETS["rationale"]
            ),
            pick_context=[SECRETS["pick_context"]],
            evidence=[SECRETS["evidence"]],
        ),
        error_message=ErrorMessageSection(
            as_of=now, message=SECRETS["error_message"], tag="some-tag"
        ),
        deliverables=DeliverablesSection(
            as_of=now,
            components=DeliverableComponents(deck=True),
            total_cost_usd=2.0,
            export_paths=[SECRETS["export_path"]],
        ),
    )


def _all_strings(value: Any) -> list[str]:
    """Flatten every string anywhere in a nested JSON-able structure."""
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            out.append(str(k))
            out.extend(_all_strings(v))
    elif isinstance(value, (list, tuple)):
        for item in value:
            out.extend(_all_strings(item))
    return out


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    d = tmp_path / "run"
    d.mkdir()
    return d


@pytest.fixture
def bound_trial_id() -> uuid.UUID:
    return uuid.UUID("11111111-1111-4111-8111-111111111111")


@pytest.fixture
def public_client(run_dir: Path, bound_trial_id: uuid.UUID) -> TestClient:
    write_projection(run_dir, build_secret_laden_projection(bound_trial_id))
    app = create_public_hud_app(trial_id=str(bound_trial_id), run_dir=run_dir, mode="session")
    return TestClient(app)


# ==========================================================================
# (a) Positive-allowlist proof — NO forbidden field can render (AC-2)
# ==========================================================================


def test_build_public_view_drops_every_forbidden_sentinel(bound_trial_id: uuid.UUID) -> None:
    projection = build_secret_laden_projection(bound_trial_id).model_dump(mode="json")
    view = build_public_view(projection)

    blob = "\n".join(_all_strings(view))
    for name, secret in SECRETS.items():
        assert secret not in blob, f"public view leaked forbidden field {name!r}: {secret!r}"

    # Forbidden whole sections are absent by construction (positive allowlist).
    for section in FORBIDDEN_SECTIONS:
        assert section not in view, f"forbidden section {section!r} present on public view"
    for scalar in FORBIDDEN_TOP_SCALARS:
        assert scalar not in view, f"forbidden scalar {scalar!r} present on public view"
    assert "operator_id" not in view.get("identity", {})


def test_public_view_still_shows_allowed_values(bound_trial_id: uuid.UUID) -> None:
    projection = build_secret_laden_projection(bound_trial_id).model_dump(mode="json")
    view = build_public_view(projection)
    blob = "\n".join(_all_strings(view))
    # Not vacuous: the allowed subset really does render.
    for name, value in ALLOWED_VALUES.items():
        assert value in blob, f"public view unexpectedly dropped allowed value {name!r}"
    assert set(ALLOWED_IDENTITY) >= set(view["identity"].keys())


def test_public_projection_endpoint_and_page_leak_no_secret(public_client: TestClient) -> None:
    proj_body = public_client.get("/projection").text
    page_body = public_client.get("/").text
    for name, secret in SECRETS.items():
        assert secret not in proj_body, f"/projection leaked {name!r}"
        assert secret not in page_body, f"/ (rendered HTML) leaked {name!r}"


def test_local_authority_server_does_echo_secrets_teeth_check(
    run_dir: Path, bound_trial_id: uuid.UUID
) -> None:
    """Teeth: the LOCAL authority server serves raw bytes → secrets present.

    If this ever stops finding the sentinels, the non-leak assertions above are
    vacuous. The local server is authority (localhost) and is *meant* to carry
    them; the public overlay is the surface that must not.
    """
    write_projection(run_dir, build_secret_laden_projection(bound_trial_id))
    local = TestClient(
        create_hud_app(
            trial_id=str(bound_trial_id),
            run_dir=run_dir,
            launch_nonce=_LAUNCH_NONCE,
            mode="session",
        )
    )
    raw = local.get("/projection").text
    assert SECRETS["resume_command"] in raw
    assert SECRETS["envelope_digest"] in raw
    assert local.get("/healthz").json()["launch_nonce"] == _LAUNCH_NONCE


# ==========================================================================
# (b) Read-only guard — no write/mutation route, no secret route (AC-1)
# ==========================================================================

_MUTATING = {"POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"}


def test_public_app_is_get_only_no_mutation_surface(
    run_dir: Path, bound_trial_id: uuid.UUID
) -> None:
    app = create_public_hud_app(str(bound_trial_id), run_dir, "session")
    api_routes = [r for r in app.routes if isinstance(r, APIRoute)]
    assert api_routes, "public app has no routes"
    for route in api_routes:
        assert route.methods == {"GET"}, (route.path, route.methods)
    kinds = {type(r).__name__ for r in app.routes}
    assert "WebSocketRoute" not in kinds and "Mount" not in kinds


def test_public_app_rejects_mutating_requests(public_client: TestClient) -> None:
    for path in ("/", "/projection", "/healthz"):
        assert public_client.post(path).status_code == 405
        assert public_client.put(path).status_code == 405
        assert public_client.delete(path).status_code == 405


# ==========================================================================
# (c) Public /healthz does NOT expose launch_nonce (AC-2)
# ==========================================================================


def test_public_healthz_never_exposes_launch_nonce(public_client: TestClient) -> None:
    body = public_client.get("/healthz").json()
    assert "launch_nonce" not in body
    assert SECRETS["nonce"] not in "\n".join(_all_strings(body))
    assert body["status"] == "ok"


# ==========================================================================
# (d) Idle → HUD offline / no active run (AC-4)
# ==========================================================================


def test_idle_shows_offline_no_active_run(run_dir: Path, bound_trial_id: uuid.UUID) -> None:
    # No projection file written → honest offline.
    app = create_public_hud_app(str(bound_trial_id), run_dir, "session")
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert OFFLINE_HEADLINE in page.text
    assert client.get("/projection").status_code == 404


def test_foreign_run_veils_never_renders(run_dir: Path, bound_trial_id: uuid.UUID) -> None:
    # A DIFFERENT run's projection on this dir must veil, never leak/serve it.
    other = uuid.UUID("22222222-2222-4222-8222-222222222222")
    write_projection(run_dir, build_secret_laden_projection(other))
    client = TestClient(create_public_hud_app(str(bound_trial_id), run_dir, "session"))
    assert OFFLINE_HEADLINE in client.get("/").text
    assert client.get("/projection").status_code == 409
    for secret in SECRETS.values():
        assert secret not in client.get("/projection").text
        assert secret not in client.get("/").text


def test_unrecognized_snapshot_does_not_dump_raw(run_dir: Path, bound_trial_id: uuid.UUID) -> None:
    write_projection_file(run_dir, b'{"schema_version": "v9", "leak": "SENTINEL-RAW-LEAK"}')
    client = TestClient(create_public_hud_app(str(bound_trial_id), run_dir, "session"))
    assert "SENTINEL-RAW-LEAK" not in client.get("/").text
    assert "SENTINEL-RAW-LEAK" not in client.get("/projection").text
    assert OFFLINE_HEADLINE in client.get("/").text


# ==========================================================================
# (e) Localhost authority preserved when tunnel config absent (AC-5)
# ==========================================================================


def test_overlay_unconfigured_is_noop_local_hud_unchanged(
    run_dir: Path, bound_trial_id: uuid.UUID
) -> None:
    # No HUD_TUNNEL_MODE → config is None → overlay launch is a pure no-op.
    assert PublicOverlayConfig.from_env({}) is None
    assert PublicOverlayConfig.from_env({"HUD_TUNNEL_MODE": "off"}) is None

    calls: list[Any] = []

    def _popen(*a: Any, **k: Any) -> Any:  # pragma: no cover — must NOT be called
        calls.append((a, k))
        raise AssertionError("popen must not be called when overlay is unconfigured")

    result = launch_public_overlay(
        trial_id=bound_trial_id, run_dir=run_dir, config=None, popen=_popen
    )
    assert result.status == "unconfigured"
    assert result.app_proc is None and result.tunnel_proc is None
    assert calls == []

    # Local authority server is fully functional regardless.
    write_projection(run_dir, build_secret_laden_projection(bound_trial_id))
    local = TestClient(
        create_hud_app(str(bound_trial_id), run_dir, _LAUNCH_NONCE, "session")
    )
    assert local.get("/healthz").status_code == 200


# ==========================================================================
# (f) Tunnel child spawns with CREATE_NO_WINDOW on win32 (AC-1) + no quick-tunnel
# ==========================================================================


class _FakeProc:
    def __init__(self) -> None:
        self._alive = True

    def poll(self) -> int | None:
        return None if self._alive else 0


def _fake_popen_factory(records: list[dict[str, Any]]):
    def _popen(argv: list[str], **kwargs: Any) -> _FakeProc:
        records.append({"argv": argv, "kwargs": kwargs})
        return _FakeProc()

    return _popen


def test_overlay_children_spawn_windowless_and_named_tunnel(
    run_dir: Path, bound_trial_id: uuid.UUID
) -> None:
    config = PublicOverlayConfig.from_env(
        {
            "HUD_TUNNEL_MODE": "cloudflare",
            "HUD_TUNNEL_TOKEN": "tok-123",
            "HUD_TUNNEL_HOSTNAME": "hud.example.com",
            "HUD_PUBLIC_PORT": "8792",
        }
    )
    assert config is not None and config.mode == "cloudflare"

    records: list[dict[str, Any]] = []
    result = launch_public_overlay(
        trial_id=bound_trial_id,
        run_dir=run_dir,
        config=config,
        popen=_fake_popen_factory(records),
    )
    assert result.status == "launched"
    assert len(records) == 2  # public app child + tunnel child

    app_argv = records[0]["argv"]
    tunnel_cmd = records[1]["argv"]
    assert app_argv[1:] == ["-m", "app.hud.public"]
    # Named tunnel — NEVER the anonymous quick-tunnel --url form.
    assert "--url" not in tunnel_cmd
    assert tunnel_cmd[:4] == ["cloudflared", "tunnel", "run", "--token"]

    expected_flag = (
        subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0  # type: ignore[attr-defined]
    )
    for rec in records:
        flag = rec["kwargs"].get("creationflags", 0)
        if sys.platform == "win32":
            assert flag == expected_flag, "tunnel/app child must spawn CREATE_NO_WINDOW on win32"
        assert rec["kwargs"]["stdin"] is subprocess.DEVNULL


def test_cloudflare_without_named_credential_refuses_quick_tunnel() -> None:
    # hostname but NO token/name → must NOT degrade to an anonymous quick-tunnel.
    cfg = PublicOverlayConfig.from_env(
        {"HUD_TUNNEL_MODE": "cloudflare", "HUD_TUNNEL_HOSTNAME": "hud.example.com"}
    )
    assert cfg is None


def test_tunnel_argv_is_never_quick_tunnel() -> None:
    cf_token = tunnel_argv(
        PublicOverlayConfig(mode="cloudflare", cloudflare_token="t", public_port=8792)
    )
    cf_name = tunnel_argv(
        PublicOverlayConfig(mode="cloudflare", tunnel_name="mytunnel", public_port=8792)
    )
    ts = tunnel_argv(PublicOverlayConfig(mode="tailscale", public_port=8792))
    for argv in (cf_token, cf_name, ts):
        assert "--url" not in argv
    assert cf_token[:3] == ["cloudflared", "tunnel", "run"]
    assert cf_name == ["cloudflared", "tunnel", "run", "mytunnel"]
    assert ts[0] == "tailscale" and ts[1] == "serve"


def test_tunnel_launch_failure_degrades_reach_not_run(
    run_dir: Path, bound_trial_id: uuid.UUID
) -> None:
    config = PublicOverlayConfig(mode="cloudflare", cloudflare_token="t", public_port=8792)

    def _popen_app_ok_tunnel_fails(argv: list[str], **kwargs: Any) -> Any:
        if argv[-1].endswith("app.hud.public") or "app.hud.public" in argv:
            return _FakeProc()
        raise OSError("cloudflared not found")

    result = launch_public_overlay(
        trial_id=bound_trial_id,
        run_dir=run_dir,
        config=config,
        popen=_popen_app_ok_tunnel_fails,
    )
    # NEVER raises; app is up, tunnel failed → reach degraded, run intact.
    assert result.status == "tunnel-failed"
    assert result.app_proc is not None


# ==========================================================================
# (g) ngrok reserved-domain mode — one stable, no-login public URL (Story 42.8)
#
# ADDITIVE alongside cloudflare/tailscale. The reserved --domain makes the URL
# stable (never a random --url quick-tunnel); the authtoken is a SECRET that
# rides the child's NGROK_AUTHTOKEN env ONLY — never the argv, a log, or the URL.
# ==========================================================================

_NGROK_DOMAIN = "marcus-hud.ngrok-free.app"
_NGROK_TOKEN = "SENTINEL-NGROK-AUTHTOKEN-2xSECRET"


def test_ngrok_tunnel_argv_is_reserved_domain_never_quick_tunnel() -> None:
    # (a) mode=ngrok + domain → `ngrok http --domain=<domain> 8792`, no --url.
    cfg = PublicOverlayConfig.from_env(
        {
            "HUD_TUNNEL_MODE": "ngrok",
            "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN,
            "HUD_PUBLIC_PORT": "8792",
        }
    )
    assert cfg is not None and cfg.mode == "ngrok"
    argv = tunnel_argv(cfg)
    assert argv == ["ngrok", "http", f"--domain={_NGROK_DOMAIN}", "8792"]
    assert "--url" not in argv  # never a random per-run quick-tunnel


def test_ngrok_bin_override_is_honored() -> None:
    cfg = PublicOverlayConfig.from_env(
        {
            "HUD_TUNNEL_MODE": "ngrok",
            "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN,
            "HUD_TUNNEL_NGROK_BIN": r"C:\tools\ngrok.exe",
        }
    )
    assert cfg is not None
    assert tunnel_argv(cfg)[0] == r"C:\tools\ngrok.exe"


def test_ngrok_absent_domain_is_inert() -> None:
    # (b) mode=ngrok but NO reserved domain → unconfigured (never a quick-tunnel).
    assert PublicOverlayConfig.from_env({"HUD_TUNNEL_MODE": "ngrok"}) is None
    assert (
        PublicOverlayConfig.from_env(
            {"HUD_TUNNEL_MODE": "ngrok", "HUD_TUNNEL_NGROK_AUTHTOKEN": _NGROK_TOKEN}
        )
        is None
    )


def test_ngrok_child_spawns_windowless_and_registers_teardown(
    run_dir: Path, bound_trial_id: uuid.UUID, monkeypatch: pytest.MonkeyPatch
) -> None:
    # (c) the ngrok child spawns CREATE_NO_WINDOW on win32 AND registers the
    # 42-2 status-aware teardown (same lifecycle owner as the cloudflare child).
    from app.marcus.orchestrator import preflight as preflight_mod

    cfg = PublicOverlayConfig.from_env(
        {"HUD_TUNNEL_MODE": "ngrok", "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN}
    )
    assert cfg is not None

    registered: list[Any] = []
    monkeypatch.setattr(
        preflight_mod.atexit,
        "register",
        lambda fn, *a, **k: registered.append((fn, a, k)),
    )

    records: list[dict[str, Any]] = []
    result = launch_public_overlay(
        trial_id=bound_trial_id,
        run_dir=run_dir,
        config=cfg,
        popen=_fake_popen_factory(records),
    )
    assert result.status == "launched"
    assert len(records) == 2  # public app child + ngrok tunnel child
    assert records[0]["argv"][1:] == ["-m", "app.hud.public"]
    assert records[1]["argv"] == ["ngrok", "http", f"--domain={_NGROK_DOMAIN}", "8792"]

    expected_flag = (
        subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0  # type: ignore[attr-defined]
    )
    for rec in records:
        if sys.platform == "win32":
            assert rec["kwargs"].get("creationflags", 0) == expected_flag
        assert rec["kwargs"]["stdin"] is subprocess.DEVNULL

    # Both children hung on the 42-2 status-aware teardown (survives pause).
    torn = [fn for fn, _a, _k in registered]
    assert torn.count(preflight_mod._status_aware_teardown) == 2


def test_ngrok_authtoken_flows_via_child_env_never_argv_or_log(
    run_dir: Path, bound_trial_id: uuid.UUID, caplog: pytest.LogCaptureFixture
) -> None:
    # authtoken from HUD_TUNNEL_NGROK_AUTHTOKEN → NGROK_AUTHTOKEN on the child env;
    # NEVER on the argv, in a log line, or on the surfaced URL (secret hygiene).
    cfg = PublicOverlayConfig.from_env(
        {
            "HUD_TUNNEL_MODE": "ngrok",
            "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN,
            "HUD_TUNNEL_NGROK_AUTHTOKEN": _NGROK_TOKEN,
        }
    )
    assert cfg is not None and cfg.ngrok_authtoken == _NGROK_TOKEN

    records: list[dict[str, Any]] = []
    with caplog.at_level(logging.DEBUG, logger="app.marcus.orchestrator.preflight"):
        result = launch_public_overlay(
            trial_id=bound_trial_id,
            run_dir=run_dir,
            config=cfg,
            popen=_fake_popen_factory(records),
        )
    assert result.status == "launched"

    # The tunnel child's env carries the token — the ONLY place it lives.
    tunnel_env = records[1]["kwargs"]["env"]
    assert tunnel_env["NGROK_AUTHTOKEN"] == _NGROK_TOKEN

    # It is NEVER on the argv, in the surfaced URL, or in any log message.
    assert _NGROK_TOKEN not in " ".join(records[1]["argv"])
    assert _NGROK_TOKEN not in (result.public_url or "")
    assert _NGROK_TOKEN not in (public_overlay_url(cfg) or "")
    assert _NGROK_TOKEN not in caplog.text
    # And it never leaks onto the emitted URL sentinel file.
    assert _NGROK_TOKEN not in (run_dir / HUD_PUBLIC_URL_SENTINEL_NAME).read_text(
        encoding="utf-8"
    )


def test_ngrok_absent_authtoken_leaves_child_env_to_ngrok_own_config(
    run_dir: Path, bound_trial_id: uuid.UUID, monkeypatch: pytest.MonkeyPatch
) -> None:
    # No HUD_TUNNEL_NGROK_AUTHTOKEN → no NGROK_AUTHTOKEN overlay; the child falls
    # back to the operator's own ngrok.yml (`ngrok config add-authtoken`).
    monkeypatch.delenv("NGROK_AUTHTOKEN", raising=False)
    cfg = PublicOverlayConfig.from_env(
        {"HUD_TUNNEL_MODE": "ngrok", "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN}
    )
    assert cfg is not None and cfg.ngrok_authtoken is None

    records: list[dict[str, Any]] = []
    launch_public_overlay(
        trial_id=bound_trial_id,
        run_dir=run_dir,
        config=cfg,
        popen=_fake_popen_factory(records),
    )
    assert "NGROK_AUTHTOKEN" not in records[1]["kwargs"]["env"]


def test_ngrok_stable_url_surfaced_logged_and_emitted(
    run_dir: Path, bound_trial_id: uuid.UUID, caplog: pytest.LogCaptureFixture
) -> None:
    # (e) the reserved-domain URL = https://<domain>, constant run-to-run, and it
    # is surfaced: returned on the handles, logged, and emitted to the sentinel.
    cfg = PublicOverlayConfig.from_env(
        {"HUD_TUNNEL_MODE": "ngrok", "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN}
    )
    assert cfg is not None
    assert public_overlay_url(cfg) == f"https://{_NGROK_DOMAIN}"

    records: list[dict[str, Any]] = []
    with caplog.at_level(logging.INFO, logger="app.marcus.orchestrator.preflight"):
        result = launch_public_overlay(
            trial_id=bound_trial_id,
            run_dir=run_dir,
            config=cfg,
            popen=_fake_popen_factory(records),
        )
    assert result.public_url == f"https://{_NGROK_DOMAIN}"
    assert f"https://{_NGROK_DOMAIN}" in caplog.text
    emitted = (run_dir / HUD_PUBLIC_URL_SENTINEL_NAME).read_text(encoding="utf-8")
    assert emitted == f"https://{_NGROK_DOMAIN}"


def test_ngrok_mode_keeps_readonly_nonleak_scrub_and_public_app(
    run_dir: Path, bound_trial_id: uuid.UUID
) -> None:
    # (d) ngrok changes only the tunnel; the public surface is the SAME scrubbed
    # app (app.hud.public) and the non-leak allowlist still drops every secret.
    cfg = PublicOverlayConfig.from_env(
        {"HUD_TUNNEL_MODE": "ngrok", "HUD_TUNNEL_NGROK_DOMAIN": _NGROK_DOMAIN}
    )
    assert cfg is not None

    records: list[dict[str, Any]] = []
    launch_public_overlay(
        trial_id=bound_trial_id,
        run_dir=run_dir,
        config=cfg,
        popen=_fake_popen_factory(records),
    )
    # Same read-only public app child — no ngrok-specific surface was introduced.
    assert records[0]["argv"][1:] == ["-m", "app.hud.public"]

    # The scrub is mode-independent: the public view still drops every sentinel.
    projection = build_secret_laden_projection(bound_trial_id).model_dump(mode="json")
    blob = "\n".join(_all_strings(build_public_view(projection)))
    for name, secret in SECRETS.items():
        assert secret not in blob, f"ngrok-mode public view leaked {name!r}"


def test_existing_modes_unaffected_by_ngrok_addition() -> None:
    # Hard fence: cloudflare/tailscale still parse + build named tunnels; the
    # ngrok addition is purely additive (operator picks via HUD_TUNNEL_MODE).
    cf = PublicOverlayConfig.from_env(
        {"HUD_TUNNEL_MODE": "cloudflare", "HUD_TUNNEL_TOKEN": "tok"}
    )
    ts = PublicOverlayConfig.from_env({"HUD_TUNNEL_MODE": "tailscale"})
    assert cf is not None and cf.mode == "cloudflare"
    assert ts is not None and ts.mode == "tailscale"
    assert tunnel_argv(cf)[:3] == ["cloudflared", "tunnel", "run"]
    assert tunnel_argv(ts)[:2] == ["tailscale", "serve"]
