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
  file with an ``ETag`` of ``<schema_version>:<seq>``; the route implements
  the ``If-None-Match`` -> ``304`` comparison itself (Starlette's
  ``FileResponse`` sets an ETag but never returns 304, and we never stream the
  live file — AD-2/6). It serves the RAW file bytes always (zero-lie: the
  operator sees exactly what the runtime wrote), gated only by the identity
  guard, which returns ``409`` with a typed REFUSE-TO-RENDER payload on a
  bound/found ``trial_id`` mismatch (AD-8).
* ``GET /healthz``   — ``{trial_id, launch_nonce, mode}`` for the pre-flight
  identity item (AD-7): the item passes only on trial_id + nonce match, never
  a fall-through to whatever else answers the port.

Layer rule (import-linter, pyproject.toml): this module imports the contract
+ ``app.hud.data`` only — never ``app.marcus.orchestrator``, never
``scripts.utilities.hud_data_sources``, never ``app.gates``, never the strict
producer model (AD-4).
"""

from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from app.hud.data import projection_etag, read_snapshot
from app.models.runtime.operator_surface import OperatorSurfaceProjection

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


def _flight_deck_html(trial_id: str, mode: str) -> str:
    """The v1 placeholder shell — dark page + real ETag poll loop (35.5 replaces)."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Operator HUD — {trial_id}</title>
<style>
  :root {{ color-scheme: dark; }}
  html, body {{ margin: 0; height: 100%; }}
  body {{
    background: #0F172A; color: #E2E8F0;
    font: 14px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    padding: 24px;
  }}
  h1 {{ font-size: 15px; font-weight: 600; margin: 0 0 4px; color: #94A3B8; }}
  .id {{ color: #64748B; font-size: 12px; }}
  #annunciator {{ margin: 20px 0; font-size: 20px; font-weight: 600; }}
  #status {{ font-size: 13px; color: #94A3B8; }}
  #detail {{ margin-top: 16px; white-space: pre-wrap; color: #CBD5E1; font-size: 12px; }}
  .refuse {{ color: #F87171; }}
  .stale {{ color: #FBBF24; }}
</style>
</head>
<body>
  <h1>OPERATOR HUD <span class="id">· {mode} · {trial_id}</span></h1>
  <div id="annunciator">…</div>
  <div id="status">connecting…</div>
  <div id="detail"></div>
<script>
  const annunciator = document.getElementById("annunciator");
  const statusEl = document.getElementById("status");
  const detailEl = document.getElementById("detail");
  let etag = null;
  function set(annun, status, detail, cls) {{
    annunciator.textContent = annun;
    annunciator.className = cls || "";
    statusEl.textContent = status;
    detailEl.textContent = detail || "";
  }}
  async function poll() {{
    const headers = {{}};
    if (etag) headers["If-None-Match"] = etag;
    try {{
      const resp = await fetch("/projection", {{ headers, cache: "no-store" }});
      const now = new Date().toLocaleTimeString();
      if (resp.status === 304) {{ statusEl.textContent = "up to date · " + now; return; }}
      const newEtag = resp.headers.get("ETag");
      if (newEtag) etag = newEtag;
      if (resp.status === 409) {{
        const body = await resp.json();
        set("REFUSE TO RENDER", "identity mismatch",
            "bound: " + body.bound + "\\nfound: " + body.found, "refuse");
        return;
      }}
      if (resp.status === 404) {{
        set("NO PROJECTION", "waiting for runtime…", "", "stale");
        return;
      }}
      if (!resp.ok) {{ set("ERROR", "HTTP " + resp.status, "", "stale"); return; }}
      const data = await resp.json();
      const status = (data && data.envelope && data.envelope.status) || null;
      if (!status) {{
        set("UNRECOGNIZED", "schema_version " + (data && data.schema_version),
            JSON.stringify(data).slice(0, 400), "stale");
        return;
      }}
      set(status.toUpperCase(), "seq " + data.seq + " · " + now,
          "lesson: " + (data.identity && data.identity.lesson));
    }} catch (err) {{
      set("DISCONNECTED", String(err), "", "stale");
    }}
  }}
  poll();
  setInterval(poll, 3000);
</script>
</body>
</html>
"""


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
        return HTMLResponse(_flight_deck_html(trial_id, mode))

    @app.get("/projection")
    def projection(request: Request) -> Response:
        snapshot = read_snapshot(run_dir)
        if snapshot is None:
            return JSONResponse(
                {"detail": "projection not found", "trial_id": trial_id},
                status_code=404,
                headers={"Cache-Control": _NO_CACHE},
            )
        etag = projection_etag(snapshot.parsed, mtime_ns=snapshot.mtime_ns)
        # Identity guard (AD-8): only a *parsed* projection carries a trial_id
        # to check. Unrecognized snapshots have no identity to compare, so they
        # pass the guard and are served raw (zero-lie) for literal rendering.
        if isinstance(snapshot.parsed, OperatorSurfaceProjection):
            found = _canonical_trial_id(str(snapshot.parsed.identity.trial_id))
            if found != bound_trial_id:
                return JSONResponse(
                    {
                        "refuse_to_render": True,
                        "bound": bound_trial_id,
                        "found": found,
                    },
                    status_code=409,
                    headers={"ETag": etag, "Cache-Control": _NO_CACHE},
                )
        if request.headers.get("if-none-match") == etag:
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

    trial_id = trial_id if trial_id is not None else os.environ["HUD_TRIAL_ID"]
    run_dir = run_dir if run_dir is not None else os.environ["HUD_RUN_DIR"]
    launch_nonce = (
        launch_nonce if launch_nonce is not None else os.environ["HUD_LAUNCH_NONCE"]
    )
    if port is None:
        port = int(os.environ.get("HUD_PORT", DEFAULT_HUD_PORT))
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
