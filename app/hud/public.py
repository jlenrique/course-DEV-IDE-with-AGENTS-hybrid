"""Public read-only HUD overlay (Story 42.4) — the non-leak security core.

The local HUD (``app.hud.server.create_hud_app``) is the AUTHORITY: GET-only,
localhost-bound, serving the RAW projection bytes (zero-lie) plus a ``/healthz``
that carries the ``launch_nonce`` secret. That surface must NEVER cross a public
tunnel.

This module builds a SEPARATE, tunnel-facing app that serves a **positive
allowlist** projection of the same live run file:

* A distinct FastAPI app (:func:`create_public_hud_app`) bound to one
  ``trial_id`` + ``run_dir`` — GET-only, zero mutation surface, and carrying
  **no secret route**: its ``/healthz`` NEVER returns ``launch_nonce``, and its
  ``/projection`` returns the ALLOWLISTED scrubbed view, never the raw bytes.
* :func:`build_public_view` — the single security seam. It builds a NEW dict by
  copying ONLY explicitly-named non-sensitive fields (a POSITIVE allowlist, not
  a denylist strip), so a field added to the projection in the future is
  DROPPED by default and can never silently ride onto the wire. Everything
  forbidden — ``launch_nonce``, ``next_action.command`` (the resume paste string
  with its pre-filled digest), the whole ``decision_card`` (operator_prompt /
  drafted_proposal / pick_context / evidence digests), ``error_message`` (the
  verbatim runtime message that can echo private source/corpus text),
  ``preflight`` outputs (paths / env-key names / API error text),
  ``deliverables`` export paths, ``envelope_digest``, per-step
  ``locked_artifact_summary``, roster ``last_artifact`` / ``model`` /
  ``cost_usd``, ``modalities.styleguide_provenance``, ``identity.operator_id`` —
  is never copied.

The tunnel that fronts this app is launched + lifecycle-coupled by
``app.marcus.orchestrator.preflight.launch_public_overlay`` (operator-gated,
config-driven — never an anonymous quick-tunnel). When no tunnel is configured
the whole overlay is simply absent and the local HUD is unchanged (AC-5).

Layer rule (import-linter): like ``app.hud.server`` this module imports the
contract + ``app.hud.data`` + ``app.hud.render`` only — never the orchestrator,
gates, or the strict producer model.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from app.hud.data import projection_etag, read_snapshot
from app.hud.render import render_page
from app.hud.render.styles import CSS
from app.models.runtime.operator_surface import (
    RUN_SETTINGS_TOGGLES,
    OperatorSurfaceProjection,
)

DEFAULT_PUBLIC_HUD_PORT = 8792
DEFAULT_BIND_HOST = "127.0.0.1"
_JSON_MEDIA_TYPE = "application/json"
_NO_CACHE = "no-cache"

# --------------------------------------------------------------------------
# The positive allowlist (AC-2 non-leak bar) — enumerated field-by-field.
#
# EACH tuple is the EXHAUSTIVE set of keys copied out of that section. A key
# not named here is DROPPED. Adding a projection field is therefore leak-safe
# by default: it does not appear on the public surface until someone adds it
# HERE (and the enumeration test forces that to be a conscious act).
# --------------------------------------------------------------------------

#: Top-level scalars. ``envelope_digest`` / ``progress_seq`` / ``last_progress_at``
#: are deliberately NOT here (``envelope_digest`` is a forbidden digest).
ALLOWED_TOP_SCALARS: tuple[str, ...] = ("schema_version", "seq", "as_of")

#: ``operator_id`` dropped (operator-only identity).
ALLOWED_IDENTITY: tuple[str, ...] = ("trial_id", "lesson", "preset", "as_of")

#: Pure run-status fields — no secret among them.
ALLOWED_ENVELOPE: tuple[str, ...] = (
    "status",
    "paused_gate",
    "paused_error_tag",
    "waiting_batch_id",
    "completed_at",
    "as_of",
)

#: Progress counters only. ``manifest_digest`` dropped (a digest).
ALLOWED_STEPS: tuple[str, ...] = (
    "node_count",
    "walk_index",
    "walk_generation",
    "reentered_from",
    "as_of",
)
#: Per-step: the you-are-here structure only. ``locked_artifact_summary``
#: (a path/summary), ``conditions`` and ``blockers`` (gate-logic hints) dropped.
ALLOWED_STEP_ENTRY: tuple[str, ...] = ("step_id", "label", "stage", "status")

#: Health tiles are cost/latency/quota numbers. ``history`` (reading list) dropped.
ALLOWED_HEALTH_TILE: tuple[str, ...] = (
    "label",
    "value",
    "unit",
    "confidence",
    "threshold_state",
    "as_of",
)

#: Ambient roster identity only. ``last_artifact`` (a path), ``model`` and
#: ``cost_usd`` dropped.
ALLOWED_SPECIALIST: tuple[str, ...] = ("name", "status", "current_node")

#: Identity chips. ``styleguide_provenance`` (a path) dropped.
ALLOWED_MODALITIES: tuple[str, ...] = (
    "llm_execution_mode",
    "detective_disposition",
    "styleguide",
    "as_of",
)

#: The 42-3 run-settings standing readout: every canonical toggle + as_of.
#: These are resolved display strings (on / off / mode names), not secrets.
ALLOWED_RUN_SETTINGS: tuple[str, ...] = tuple(
    field for field, _label in RUN_SETTINGS_TOGGLES
) + ("as_of",)

#: Trace TIMINGS only. ``detail`` dropped (free text that could echo content).
ALLOWED_TRACE_EVENT: tuple[str, ...] = ("at", "event")

#: Whole sections that NEVER cross the wire (documentation + the enumeration
#: test read this to prove intent). ``notifications_echo`` is dropped because it
#: nests the full HudConfig echo; the public viewer does not need it.
FORBIDDEN_SECTIONS: tuple[str, ...] = (
    "next_action",  # .command = resume paste string WITH pre-filled digest
    "decision_card",  # operator_prompt / drafted_proposal / pick_context / evidence
    "error_message",  # verbatim runtime message — can echo private source text
    "preflight",  # item outputs: paths, env-key names, API error text
    "deliverables",  # export_paths (filesystem layout) + costs
    "notifications_echo",  # nested HudConfig echo
)

#: Top-level scalars that are forbidden even though they are not sections.
FORBIDDEN_TOP_SCALARS: tuple[str, ...] = (
    "envelope_digest",  # a hash/digest of run.json content
    "progress_seq",
    "last_progress_at",
)


def _copy_allowed(src: Any, allowed: tuple[str, ...]) -> dict[str, Any]:
    """Return a NEW dict with ONLY ``allowed`` keys present in ``src``."""
    if not isinstance(src, Mapping):
        return {}
    return {key: src[key] for key in allowed if key in src}


def build_public_view(projection: Mapping[str, Any]) -> dict[str, Any]:
    """Project a run's operator-surface dict onto the PUBLIC allowlist (AC-2).

    Builds a brand-new dict copying only the explicitly-allowed fields. Nothing
    in :data:`FORBIDDEN_SECTIONS` / :data:`FORBIDDEN_TOP_SCALARS` — and nothing
    un-enumerated — is ever carried across. Pure; never mutates ``projection``.
    """
    if not isinstance(projection, Mapping):
        return {}

    view: dict[str, Any] = _copy_allowed(projection, ALLOWED_TOP_SCALARS)

    identity = projection.get("identity")
    if isinstance(identity, Mapping):
        view["identity"] = _copy_allowed(identity, ALLOWED_IDENTITY)

    envelope = projection.get("envelope")
    if isinstance(envelope, Mapping):
        view["envelope"] = _copy_allowed(envelope, ALLOWED_ENVELOPE)

    steps = projection.get("steps")
    if isinstance(steps, Mapping):
        steps_view = _copy_allowed(steps, ALLOWED_STEPS)
        entries = steps.get("entries")
        if isinstance(entries, list):
            steps_view["entries"] = [
                _copy_allowed(entry, ALLOWED_STEP_ENTRY)
                for entry in entries
                if isinstance(entry, Mapping)
            ]
        view["steps"] = steps_view

    health = projection.get("health")
    if isinstance(health, Mapping):
        health_view: dict[str, Any] = {}
        if "as_of" in health:
            health_view["as_of"] = health["as_of"]
        tiles = health.get("tiles")
        if isinstance(tiles, list):
            health_view["tiles"] = [
                _copy_allowed(tile, ALLOWED_HEALTH_TILE)
                for tile in tiles
                if isinstance(tile, Mapping)
            ]
        view["health"] = health_view

    specialists = projection.get("specialists")
    if isinstance(specialists, Mapping):
        spec_view: dict[str, Any] = {}
        if "as_of" in specialists:
            spec_view["as_of"] = specialists["as_of"]
        roster = specialists.get("roster")
        if isinstance(roster, list):
            spec_view["roster"] = [
                _copy_allowed(member, ALLOWED_SPECIALIST)
                for member in roster
                if isinstance(member, Mapping)
            ]
        view["specialists"] = spec_view

    modalities = projection.get("modalities")
    if isinstance(modalities, Mapping):
        view["modalities"] = _copy_allowed(modalities, ALLOWED_MODALITIES)

    run_settings = projection.get("run_settings")
    if isinstance(run_settings, Mapping):
        view["run_settings"] = _copy_allowed(run_settings, ALLOWED_RUN_SETTINGS)

    trace = projection.get("trace")
    if isinstance(trace, Mapping):
        trace_view: dict[str, Any] = {}
        if "as_of" in trace:
            trace_view["as_of"] = trace["as_of"]
        events = trace.get("events")
        if isinstance(events, list):
            trace_view["events"] = [
                _copy_allowed(event, ALLOWED_TRACE_EVENT)
                for event in events
                if isinstance(event, Mapping)
            ]
        view["trace"] = trace_view

    return view


# --------------------------------------------------------------------------
# Identity + render helpers (mirror the local server's guard, no raw leak).
# --------------------------------------------------------------------------


def _canonical_trial_id(value: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return str(value)


#: The honest idle string the stable hostname shows when no run is active.
OFFLINE_HEADLINE = "HUD offline — no active run"


def _offline_page(message: str = OFFLINE_HEADLINE) -> str:
    """A tiny, secret-free HTML page for absent / unreadable / foreign runs.

    Deliberately does NOT route through ``page.py`` — its UNRECOGNIZED panel
    would dump raw projection bytes, which must never reach the public wire.
    """
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\" />"
        '<meta name="viewport" content="width=device-width, initial-scale=1" />'
        f"<title>Operator HUD — offline</title><style>{CSS}</style></head>"
        '<body><div id="annunciator">'
        '<div class="annunciator ann-idle" role="status" aria-live="polite">'
        f'<span class="sym">○</span><span>{message}</span></div></div>'
        "</body></html>"
    )


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _public_render_data(
    run_dir: Path, bound_trial_id: str, mode: str
) -> dict[str, Any] | None:
    """Build the render envelope for the public COLD-load page, or ``None``.

    ``None`` means "not a clean, identity-matched, parsed projection" — the
    caller then serves the secret-free offline page (absent file, unreadable /
    Unrecognized snapshot, or a foreign run identity all veil, never leak).
    """
    snapshot = read_snapshot(run_dir)
    if snapshot is None:
        return None
    parsed = snapshot.parsed
    if not isinstance(parsed, OperatorSurfaceProjection):
        return None
    found = _canonical_trial_id(str(parsed.identity.trial_id))
    if found != bound_trial_id:
        return None
    return {
        "panel_state": "ok",
        "projection": build_public_view(parsed.model_dump(mode="json")),
        "bound_trial_id": bound_trial_id,
        "mode": mode,
        "now": _now_iso(),
    }


def create_public_hud_app(
    trial_id: str,
    run_dir: Path,
    mode: str = "session",
) -> FastAPI:
    """Build the tunnel-facing PUBLIC read-only app (Story 42.4).

    GET-only, zero mutation surface, NO secret route. Bound to one ``trial_id``;
    a foreign / absent / unreadable run veils to the offline page. Note the
    signature takes NO ``launch_nonce`` — the public surface has no place to put
    it, structurally (belt-and-suspenders beyond the tunnel's identity ACL).
    """
    run_dir = Path(run_dir)
    bound_trial_id = _canonical_trial_id(trial_id)

    app = FastAPI(
        title="operator-hud-public",
        version="1.0.0-story42.4",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.trial_id = trial_id
    app.state.run_dir = run_dir
    app.state.mode = mode

    @app.get("/")
    def flight_deck() -> HTMLResponse:
        data = _public_render_data(run_dir, bound_trial_id, mode)
        if data is None:
            return HTMLResponse(_offline_page())
        return HTMLResponse(render_page(data))

    @app.get("/projection")
    def projection(request: Request) -> Response:
        snapshot = read_snapshot(run_dir)
        if snapshot is None or not isinstance(
            snapshot.parsed, OperatorSurfaceProjection
        ):
            # Absent / Unrecognized → honest offline JSON, NEVER raw bytes.
            return JSONResponse(
                {"status": "offline"},
                status_code=404,
                headers={"Cache-Control": _NO_CACHE},
            )
        parsed = snapshot.parsed
        found = _canonical_trial_id(str(parsed.identity.trial_id))
        etag = f'"{projection_etag(parsed, mtime_ns=snapshot.mtime_ns)}"'
        if found != bound_trial_id:
            # Foreign run on this run-dir → veil, never render (no raw payload).
            return JSONResponse(
                {"status": "offline"},
                status_code=409,
                headers={"Cache-Control": _NO_CACHE},
            )
        inm = request.headers.get("if-none-match")
        if inm and inm.strip('"').removeprefix("W/").strip('"') == etag.strip('"'):
            return Response(
                status_code=304,
                headers={"ETag": etag, "Cache-Control": _NO_CACHE},
            )
        # Serve the ALLOWLISTED scrubbed view — a fresh dict built from the
        # parsed model, NEVER ``snapshot.raw`` (which carries every secret).
        view = build_public_view(parsed.model_dump(mode="json"))
        return JSONResponse(
            view,
            headers={"ETag": etag, "Cache-Control": _NO_CACHE},
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        # NO launch_nonce here — that secret stays localhost-only (the local
        # server's /healthz owns it). A liveness ping for the tunnel only.
        return {"status": "ok", "trial_id": trial_id, "mode": mode}

    return app


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise SystemExit(
            f"public HUD server: required environment variable {name} is not set. "
            "The overlay launcher must set HUD_TRIAL_ID and HUD_RUN_DIR."
        )
    return value


def run_public_hud_server(
    trial_id: str | None = None,
    run_dir: Path | str | None = None,
    port: int | None = None,
    mode: str | None = None,
    host: str = DEFAULT_BIND_HOST,
) -> None:
    """uvicorn entry (``python -m app.hud.public``); env-driven when unset.

    Env: ``HUD_TRIAL_ID``, ``HUD_RUN_DIR``, ``HUD_PUBLIC_PORT`` (default 8792),
    ``HUD_MODE`` (default ``session``). Note: ``HUD_LAUNCH_NONCE`` is NOT read —
    the public surface never handles the nonce.
    """
    import uvicorn

    trial_id = trial_id if trial_id is not None else _required_env("HUD_TRIAL_ID")
    run_dir = run_dir if run_dir is not None else _required_env("HUD_RUN_DIR")
    if port is None:
        raw_port = os.environ.get("HUD_PUBLIC_PORT", str(DEFAULT_PUBLIC_HUD_PORT))
        try:
            port = int(raw_port)
        except ValueError:
            raise SystemExit(
                f"public HUD server: HUD_PUBLIC_PORT must be an integer, got {raw_port!r}."
            ) from None
    if mode is None:
        mode = os.environ.get("HUD_MODE", "session")

    app = create_public_hud_app(
        trial_id=trial_id, run_dir=Path(run_dir), mode=mode
    )
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":  # pragma: no cover — process entry
    run_public_hud_server()


__all__ = [
    "ALLOWED_ENVELOPE",
    "ALLOWED_HEALTH_TILE",
    "ALLOWED_IDENTITY",
    "ALLOWED_MODALITIES",
    "ALLOWED_RUN_SETTINGS",
    "ALLOWED_SPECIALIST",
    "ALLOWED_STEPS",
    "ALLOWED_STEP_ENTRY",
    "ALLOWED_TOP_SCALARS",
    "ALLOWED_TRACE_EVENT",
    "DEFAULT_PUBLIC_HUD_PORT",
    "FORBIDDEN_SECTIONS",
    "FORBIDDEN_TOP_SCALARS",
    "OFFLINE_HEADLINE",
    "build_public_view",
    "create_public_hud_app",
    "run_public_hud_server",
]
