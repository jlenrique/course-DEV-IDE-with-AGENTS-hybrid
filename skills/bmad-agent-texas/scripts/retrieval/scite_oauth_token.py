"""Scite MCP OAuth token store + headless refresh.

The Scite MCP server requires OAuth 2.0 Bearer auth (no password grant). A
one-time interactive sign-in (`scripts/operator/scite_oauth_login.py`) persists
`{access_token, refresh_token, expires_at, client_id}` to a gitignored token
file. This module loads that file and mints a fresh Bearer token on demand,
refreshing via the stored `refresh_token` when the access token is near expiry
(refresh_token grant IS headless — no browser step after the first sign-in).

Contract (deliberately narrow so `SciteProvider` stays transport-agnostic):
    load_bearer_token() -> str | None   # ready-to-use access token, or None

Returns None (never raises) when no token file exists / is malformed / refresh
fails, so the provider degrades to its HTTP-Basic fallback exactly as before.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

# Resolve the repo root from this file: .../skills/bmad-agent-texas/scripts/retrieval/
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_TOKEN_PATH = _REPO_ROOT / "secrets" / "scite_oauth_token.json"

TOKEN_URL = "https://api.scite.ai/mcp/oauth/token"
# Refresh when fewer than this many seconds remain on the access token.
_REFRESH_SKEW_SECONDS = 120


def _token_path() -> Path:
    """Token file location; override via SCITE_OAUTH_TOKEN_PATH (tests)."""
    override = os.environ.get("SCITE_OAUTH_TOKEN_PATH")
    return Path(override) if override else _DEFAULT_TOKEN_PATH


def _read_record(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_record(path: Path, record: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    except OSError:
        pass  # best-effort persistence; a non-writable cache is non-fatal


def _is_fresh(record: dict[str, Any], *, now: float) -> bool:
    expires_at = record.get("expires_at")
    if not isinstance(expires_at, (int, float)):
        return False
    return (expires_at - now) > _REFRESH_SKEW_SECONDS


def _refresh(record: dict[str, Any], path: Path, *, now: float) -> dict[str, Any] | None:
    """Exchange the stored refresh_token for a new access token (headless)."""
    refresh_token = record.get("refresh_token")
    client_id = record.get("client_id")
    if not refresh_token or not client_id:
        return None
    try:
        resp = httpx.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
            },
            timeout=30,
        )
    except httpx.HTTPError:
        return None
    if resp.status_code != 200:
        return None
    try:
        tok = resp.json()
    except ValueError:
        return None
    access_token = tok.get("access_token")
    if not access_token:
        return None
    new_record = dict(record)
    new_record["access_token"] = access_token
    # Some servers rotate the refresh_token; keep the new one if present.
    if tok.get("refresh_token"):
        new_record["refresh_token"] = tok["refresh_token"]
    new_record["expires_at"] = int(now) + int(tok.get("expires_in", 3600))
    _write_record(path, new_record)
    return new_record


def load_bearer_token(*, now: float | None = None) -> str | None:
    """Return a ready-to-use Scite Bearer access token, or None.

    Reads the persisted token file, refreshing via the stored refresh_token
    when the access token is near expiry. Never raises — returns None when no
    usable token can be produced, so callers fall back to HTTP-Basic auth.
    """
    now = time.time() if now is None else now
    path = _token_path()
    record = _read_record(path)
    if record is None:
        return None
    if _is_fresh(record, now=now):
        token = record.get("access_token")
        return token if isinstance(token, str) and token else None
    refreshed = _refresh(record, path, now=now)
    if refreshed is None:
        # Stale and un-refreshable: surface the (expired) token anyway only if
        # it still has *some* validity is not possible to know — return None so
        # the caller degrades rather than sending a known-expired Bearer.
        return None
    token = refreshed.get("access_token")
    return token if isinstance(token, str) and token else None


__all__ = ["load_bearer_token"]
