"""GET-only localhost HUD server (Story 35.4; ADs 6/7/8).

A FastAPI app exposing **exactly three GET routes** and no mutation surface
whatsoever (AD-6: a POST/PUT/DELETE/PATCH/WebSocket/mount route on this app is
a defect regardless of intent — the read-only, zero-button guarantee is
structural, not policy). The app binds ONE ``trial_id`` at launch (explicit
argument from the runtime start path — never discovery, AD-8) and refuses to
render any projection whose identity does not match.

Routes:

* ``GET /``          — the flight-deck page. This is the v1 placeholder shell
  (a minimal dark page with a real ETag poll loop). Story 35.5 retargets the
  full render into ``app/hud/render/``; this shell exists so the poll
  transport is exercised end-to-end from 35.4.
* ``GET /projection`` — a read-then-respond byte snapshot of the projection
  file with a quoted ``ETag`` of ``"<schema_version>:<seq>"``; the route
  implements the ``If-None-Match`` -> ``304`` comparison itself (Starlette's
  ``FileResponse`` sets an ETag but never returns 304, and we never stream the
  live file — AD-2/6). It serves the RAW file bytes always (zero-lie: the
  operator sees exactly what the runtime wrote), gated only by the identity
  guard, which returns ``409`` with a typed REFUSE-TO-RENDER payload on a
  bound/found ``trial_id`` mismatch (AD-8) — including a best-effort raw
  extraction on Unrecognized snapshots so a readable foreign identity can
  never ride a lenient-parse failure past the guard.
* ``GET /healthz``   — ``{trial_id, launch_nonce, mode}`` for the pre-flight
  identity item (AD-7): the item passes only on trial_id + nonce match, never
  a fall-through to whatever else answers the port.

Layer rule (import-linter, pyproject.toml): this module imports the contract
+ ``app.hud.data`` only — never ``app.marcus.orchestrator``, never
``scripts.utilities.hud_data_sources``, never ``app.gates``, never the strict
producer model (AD-4).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from app.hud.data import projection_etag, read_snapshot
from app.hud.render import render_page
from app.models.runtime.operator_surface import OperatorSurfaceProjection, Unrecognized

DEFAULT_HUD_PORT = 8791
DEFAULT_BIND_HOST = "127.0.0.1"
_JSON_MEDIA_TYPE = "application/json"
_NO_CACHE = "no-cache"


def _canonical_trial_id(value: str) -> str:
    """Canonicalize a trial_id string for identity comparison.

    Uses the UUID canonical form when parseable (so hyphenation / case never
    manufacture a false mismatch); falls back to the raw string otherwise so a
    non-UUID bound id still compares deterministically.
    """
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return str(value)


def _raw_identity_trial_id(raw: bytes) -> str | None:
    """Best-effort trial_id extraction from an *Unrecognized* snapshot (AD-8).

    A snapshot the lenient reader rejects (unknown schema_version, malformed
    field, unknown status) may still be a readable JSON dict carrying another
    run's identity — serving it raw would let the placeholder shell render the
    WRONG run's envelope.status (probe-proven identity-guard bypass). So the
    guard does its own best-effort read: ``identity.trial_id`` first, then a
    top-level ``trial_id``. Returns ``None`` only when no identity is truly
    extractable (non-JSON bytes, non-dict document, absent/blank/non-string
    ids) — only then may the snapshot pass the guard and be served raw.
    """
    try:
        data = json.loads(raw)
    except ValueError:  # includes JSONDecodeError + UnicodeDecodeError
        return None
    if not isinstance(data, dict):
        return None
    identity = data.get("identity")
    if isinstance(identity, dict):
        candidate = identity.get("trial_id")
        if isinstance(candidate, str) and candidate.strip():
            return candidate
    candidate = data.get("trial_id")
    if isinstance(candidate, str) and candidate.strip():
        return candidate
    return None


def _quote_etag(core: str) -> str:
    """Wrap the content-derived ETag core in RFC 9110 quotes (``"v1:1"``)."""
    return f'"{core}"'


def _if_none_match_matches(header_value: str | None, etag: str) -> bool:
    """RFC 9110 ``If-None-Match`` comparison against our quoted strong ETag.

    Handles the forms real clients send: weak validators (``W/"v1:1"`` —
    weak comparison is the correct semantic for If-None-Match), comma-separated
    candidate lists, and the ``*`` wildcard. Quotes are stripped from both
    sides so a bare legacy value still compares.
    """
    if not header_value:
        return False
    current = etag.strip('"')
    for candidate in header_value.split(","):
        candidate = candidate.strip()
        if not candidate:
            continue
        if candidate == "*":
            return True
        if candidate.startswith(("W/", "w/")):
            candidate = candidate[2:]
        if candidate.strip('"') == current:
            return True
    return False


def _flight_deck_data(
    run_dir: Path,
    bound_trial_id: str,
    mode: str,
) -> dict:
    """Build the render envelope for the COLD-load page (Story 35.5).

    Mirrors the ``/projection`` identity guard so the first paint is honest and
    never renders a foreign run: absent snapshot -> ``binding``; a parsed
    projection whose identity matches -> ``ok`` (rendered from the parsed model
    dump — the JS then re-renders from the raw ``/projection`` bytes each poll);
    an identity mismatch -> ``refuse-to-render``; an ``Unrecognized`` snapshot
    with no foreign identity -> ``unrecognized`` (raw value quoted, zero-lie).

    Pure with respect to the render layer: the only I/O is the one snapshot read
    (open-read-close via :func:`read_snapshot`); ``render_page`` itself never
    does I/O.
    """
    base: dict = {"bound_trial_id": bound_trial_id, "mode": mode, "projection": None}
    snapshot = read_snapshot(run_dir)
    if snapshot is None:
        base["panel_state"] = "binding"
        return base

    parsed = snapshot.parsed
    if isinstance(parsed, OperatorSurfaceProjection):
        found = _canonical_trial_id(str(parsed.identity.trial_id))
        if found != bound_trial_id:
            base["panel_state"] = "refuse-to-render"
            base["refuse"] = {"bound": bound_trial_id, "found": found}
            return base
        base["panel_state"] = "ok"
        base["projection"] = parsed.model_dump(mode="json")
        return base

    # Unrecognized snapshot — guard identity first (a foreign readable id must
    # veil, never render), then render UNRECOGNIZED literally.
    raw_trial_id = _raw_identity_trial_id(snapshot.raw)
    if raw_trial_id is not None:
        found = _canonical_trial_id(raw_trial_id)
        if found != bound_trial_id:
            base["panel_state"] = "refuse-to-render"
            base["refuse"] = {"bound": bound_trial_id, "found": found}
            return base
    reason = parsed.reason if isinstance(parsed, Unrecognized) else "unparseable projection"
    schema_version = parsed.schema_version if isinstance(parsed, Unrecognized) else None
    base["panel_state"] = "unrecognized"
    base["unrecognized"] = {
        "raw": snapshot.raw.decode("utf-8", errors="replace")[:2000],
        "schema_version": schema_version,
        "reason": reason,
    }
    return base


def create_hud_app(
    trial_id: str,
    run_dir: Path,
    launch_nonce: str,
    mode: str = "session",
) -> FastAPI:
    """Build the GET-only HUD app bound to exactly one ``trial_id`` (AD-6/7/8).

    ``docs_url``/``redoc_url``/``openapi_url`` are disabled so the route
    inventory is EXACTLY the three GET routes below — the auto-mounted
    ``/docs`` + ``/openapi.json`` would otherwise add GET routes that muddy the
    zero-mutation-surface proof (and are useless on a read-only view anyway).
    """
    run_dir = Path(run_dir)
    bound_trial_id = _canonical_trial_id(trial_id)

    app = FastAPI(
        title="operator-hud",
        version="1.0.0-story35.4",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.trial_id = trial_id
    app.state.run_dir = run_dir
    app.state.launch_nonce = launch_nonce
    app.state.mode = mode

    @app.get("/")
    def flight_deck() -> HTMLResponse:
        data = _flight_deck_data(run_dir, bound_trial_id, mode)
        return HTMLResponse(render_page(data))

    @app.get("/projection")
    def projection(request: Request) -> Response:
        snapshot = read_snapshot(run_dir)
        if snapshot is None:
            return JSONResponse(
                {"detail": "projection not found", "trial_id": trial_id},
                status_code=404,
                headers={"Cache-Control": _NO_CACHE},
            )
        etag = _quote_etag(
            projection_etag(snapshot.parsed, mtime_ns=snapshot.mtime_ns)
        )
        # Identity guard (AD-8): a *parsed* projection carries its trial_id
        # directly; an Unrecognized snapshot gets a best-effort raw extraction
        # so a valid-looking dict with another run's identity can NEVER slip
        # past the guard just because one sibling field failed lenient parse.
        # Only a snapshot with no extractable identity is served raw unguarded.
        found: str | None = None
        if isinstance(snapshot.parsed, OperatorSurfaceProjection):
            found = _canonical_trial_id(str(snapshot.parsed.identity.trial_id))
        else:
            raw_trial_id = _raw_identity_trial_id(snapshot.raw)
            if raw_trial_id is not None:
                found = _canonical_trial_id(raw_trial_id)
        if found is not None and found != bound_trial_id:
            return JSONResponse(
                {
                    "refuse_to_render": True,
                    "bound": bound_trial_id,
                    "found": found,
                },
                status_code=409,
                headers={"ETag": etag, "Cache-Control": _NO_CACHE},
            )
        if _if_none_match_matches(request.headers.get("if-none-match"), etag):
            return Response(
                status_code=304,
                headers={"ETag": etag, "Cache-Control": _NO_CACHE},
            )
        # Serve the RAW bytes the runtime wrote — never a re-serialization, so
        # the operator sees exactly what is on disk (zero-lie). No streaming
        # FileResponse: bytes already in hand, handle already closed (AD-2/6).
        return Response(
            content=snapshot.raw,
            media_type=_JSON_MEDIA_TYPE,
            headers={"ETag": etag, "Cache-Control": _NO_CACHE},
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {
            "trial_id": trial_id,
            "launch_nonce": launch_nonce,
            "mode": mode,
        }

    return app


def _required_env(name: str) -> str:
    """Read a required env var; exit with a clear message when absent (S3).

    The HUD launches as a subprocess of the runtime start path — a missing
    env var there must surface as one legible line the operator can act on,
    never a ``KeyError`` traceback.
    """
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise SystemExit(
            f"HUD server: required environment variable {name} is not set. "
            "The runtime start path (Story 35.3) must launch this process "
            "with HUD_TRIAL_ID, HUD_RUN_DIR and HUD_LAUNCH_NONCE."
        )
    return value


def run_hud_server(
    trial_id: str | None = None,
    run_dir: Path | str | None = None,
    launch_nonce: str | None = None,
    port: int | None = None,
    mode: str | None = None,
    host: str = DEFAULT_BIND_HOST,
) -> None:
    """uvicorn entry (``python -m app.hud.server``); env-driven when unset.

    Env: ``HUD_TRIAL_ID``, ``HUD_RUN_DIR``, ``HUD_LAUNCH_NONCE``,
    ``HUD_PORT`` (default 8791), ``HUD_MODE`` (default ``session``). The
    runtime start path (Story 35.3) launches this as a subprocess with those
    env vars set.
    """
    import uvicorn

    trial_id = trial_id if trial_id is not None else _required_env("HUD_TRIAL_ID")
    run_dir = run_dir if run_dir is not None else _required_env("HUD_RUN_DIR")
    launch_nonce = (
        launch_nonce if launch_nonce is not None else _required_env("HUD_LAUNCH_NONCE")
    )
    if port is None:
        raw_port = os.environ.get("HUD_PORT", str(DEFAULT_HUD_PORT))
        try:
            port = int(raw_port)
        except ValueError:
            raise SystemExit(
                f"HUD server: HUD_PORT must be an integer port number, "
                f"got {raw_port!r}."
            ) from None
    if mode is None:
        mode = os.environ.get("HUD_MODE", "session")

    app = create_hud_app(
        trial_id=trial_id,
        run_dir=Path(run_dir),
        launch_nonce=launch_nonce,
        mode=mode,
    )
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":  # pragma: no cover — process entry
    run_hud_server()


__all__ = [
    "DEFAULT_BIND_HOST",
    "DEFAULT_HUD_PORT",
    "create_hud_app",
    "run_hud_server",
]
