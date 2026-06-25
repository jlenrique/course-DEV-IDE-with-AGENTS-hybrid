"""One-time Scite MCP OAuth login — authorization_code + PKCE (loopback).

The Scite MCP endpoint (`https://api.scite.ai/mcp`) requires OAuth 2.0 Bearer
auth. Its authorization server advertises ONLY `authorization_code` +
`refresh_token` grants (PKCE S256, public client, dynamic registration) — there
is NO password / client-credentials grant, so a username/password cannot be
exchanged for a token headlessly. This helper drives the sanctioned interactive
flow ONCE:

  register public client -> PKCE -> open browser to /authorize -> operator signs
  in to their premium scite.ai account + approves -> loopback catches the code ->
  exchange at /token -> persist {access_token, refresh_token, expiry, client_id}
  to `secrets/scite_oauth_token.json` (gitignored).

After this runs once, `scite_oauth_token.refresh_access_token()` mints fresh
Bearer tokens headlessly from the stored refresh_token — no further browser step.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\scite_oauth_login.py
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import http.server
import json
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
TOKEN_PATH = REPO_ROOT / "secrets" / "scite_oauth_token.json"

BASE = "https://api.scite.ai"
REGISTER_URL = f"{BASE}/mcp/oauth/register"
AUTHORIZE_URL = f"{BASE}/mcp/oauth/authorize"
TOKEN_URL = f"{BASE}/mcp/oauth/token"
REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
SCOPE = "mcp"

_captured: dict[str, str] = {}


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        params = urllib.parse.parse_qs(parsed.query)
        _captured.update({k: v[0] for k, v in params.items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        ok = "code" in _captured
        msg = (
            "<h2>Scite authorization captured.</h2><p>You can close this tab and "
            "return to the terminal.</p>"
            if ok
            else f"<h2>Authorization failed.</h2><pre>{_captured}</pre>"
        )
        self.wfile.write(f"<html><body>{msg}</body></html>".encode())

    def log_message(self, *_args) -> None:  # silence
        pass


def _pkce() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(40)).rstrip(b"=").decode()
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


def _register_client() -> str:
    body = {
        "client_name": "course-runner-research-leg",
        "redirect_uris": [REDIRECT_URI],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "scope": SCOPE,
    }
    r = httpx.post(REGISTER_URL, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["client_id"]


def main() -> int:
    client_id = _register_client()
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(16)

    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": SCOPE,
            "state": state,
        }
    )
    auth_url = f"{AUTHORIZE_URL}?{query}"

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), _CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print("=" * 70)
    print("SCITE MCP — one-time OAuth sign-in")
    print("=" * 70)
    print("Opening your browser. Sign in with the PREMIUM scite.ai account")
    print("(jcph@jefferson.edu) and approve access. If the browser does not")
    print("open, paste this URL manually:\n")
    print(auth_url)
    print()
    with contextlib.suppress(Exception):
        webbrowser.open(auth_url)

    deadline = time.time() + 300  # 5 min
    while time.time() < deadline and "code" not in _captured:
        time.sleep(0.5)
    server.shutdown()

    if "code" not in _captured:
        print("TIMED OUT waiting for authorization (no callback received).", file=sys.stderr)
        return 2
    if _captured.get("state") != state:
        print("STATE MISMATCH — aborting (possible CSRF).", file=sys.stderr)
        return 3

    token_resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": _captured["code"],
            "redirect_uri": REDIRECT_URI,
            "client_id": client_id,
            "code_verifier": verifier,
        },
        timeout=30,
    )
    if token_resp.status_code != 200:
        print(
            f"TOKEN EXCHANGE FAILED {token_resp.status_code}: {token_resp.text[:300]}",
            file=sys.stderr,
        )
        return 4

    tok = token_resp.json()
    expires_in = int(tok.get("expires_in", 3600))
    record = {
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "token_type": tok.get("token_type", "Bearer"),
        "scope": tok.get("scope", SCOPE),
        "client_id": client_id,
        "expires_at": int(time.time()) + expires_in,
    }
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"\nSUCCESS — token saved to {TOKEN_PATH.relative_to(REPO_ROOT)}")
    print(f"  access_token: ...{record['access_token'][-8:]} (expires in {expires_in}s)")
    print(f"  refresh_token: {'present' if record['refresh_token'] else 'ABSENT'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
