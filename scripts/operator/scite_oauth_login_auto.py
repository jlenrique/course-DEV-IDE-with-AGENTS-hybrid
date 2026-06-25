"""Autonomous Scite MCP OAuth login — Playwright-driven, no manual browser step.

Scite's MCP requires OAuth 2.0 (authorization_code + PKCE; no password grant), so
a username/password cannot be exchanged for a token via a plain HTTP call. This
tool drives the REAL browser login with Playwright (the credentials come from
`.env`: `SCITE_USER_NAME` / `SCITE_PASSWORD`), completes the authorization_code +
PKCE flow against a loopback redirect, and persists the token (with refresh_token)
to `secrets/scite_oauth_token.json` (gitignored). After the first run the stored
refresh_token is reused headlessly (`scite_oauth_token.load_bearer_token`); rerun
this only if the refresh_token is revoked/expired.

NO secrets are hardcoded here — creds are read from `.env`. The interactive
sibling `scite_oauth_login.py` remains for the manual-sign-in path.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\scite_oauth_login_auto.py [--headed]
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
TOKEN_PATH = REPO_ROOT / "secrets" / "scite_oauth_token.json"
BASE = "https://api.scite.ai"
PORT = 8765
REDIRECT = f"http://localhost:{PORT}/callback"

_captured: dict[str, str] = {}


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        q = urllib.parse.urlparse(self.path)
        if q.path == "/callback":
            _captured.update({k: v[0] for k, v in urllib.parse.parse_qs(q.query).items()})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body>Authorized. You may close this tab.</body></html>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *_a) -> None:
        pass


def _pkce() -> tuple[str, str]:
    v = base64.urlsafe_b64encode(secrets.token_bytes(40)).rstrip(b"=").decode()
    c = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
    return v, c


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass
    email = os.environ.get("SCITE_USER_NAME", "").strip()
    password = os.environ.get("SCITE_PASSWORD", "").strip()
    if not email or not password:
        print("SCITE_USER_NAME / SCITE_PASSWORD must be set in .env", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed; use the interactive scite_oauth_login.py", file=sys.stderr)
        return 2

    reg = httpx.post(
        BASE + "/mcp/oauth/register",
        json={
            "client_name": "course-runner-research-leg",
            "redirect_uris": [REDIRECT],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
            "scope": "mcp",
        },
        timeout=30,
    ).json()
    cid = reg["client_id"]
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(16)
    auth_url = f"{BASE}/mcp/oauth/authorize?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIRECT,
        "code_challenge": challenge, "code_challenge_method": "S256",
        "scope": "mcp", "state": state,
    })

    srv = http.server.HTTPServer(("localhost", PORT), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    headed = "--headed" in sys.argv or True  # headed passes scite's bot-check
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        page = browser.new_context().new_page()
        page.goto(auth_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        def visible_pwd():
            try:
                el = page.query_selector("input[type=password]")
                return el if (el and el.is_visible()) else None
            except Exception:
                return None

        def click_any(selectors) -> bool:
            for s in selectors:
                try:
                    el = page.query_selector(s)
                    if el and el.is_visible():
                        el.click()
                        return True
                except Exception:
                    pass
            return False

        email_visible = page.query_selector("input[type=email]:visible, input[type=text]:visible")
        if not visible_pwd() and not email_visible:
            click_any([
                "button:has-text('Log In')", "a:has-text('Log In')", "text=/^\\s*log\\s*in\\s*$/i",
            ])
            time.sleep(3)

        for s in ["input[type=email]", "input[name=email]", "input[name=username]",
                  "input[autocomplete=username]", "input[type=text]"]:
            el = page.query_selector(s)
            if el and el.is_visible():
                el.fill(email)
                break
        if not visible_pwd():
            if not click_any([
                "button:has-text('Continue')", "button:has-text('Next')",
                "button:has-text('Log in')", "button[type=submit]",
            ]):
                page.keyboard.press("Enter")
            with contextlib.suppress(Exception):
                page.wait_for_selector("input[type=password]", state="visible", timeout=15000)
        pwd = visible_pwd()
        if pwd:
            pwd.fill(password)
            if not click_any([
                "button:has-text('Log in')", "button:has-text('Sign in')", "button[type=submit]",
            ]):
                page.keyboard.press("Enter")

        deadline = time.time() + 90
        while time.time() < deadline and "code" not in _captured:
            click_any(["button:has-text('Authorize')", "button:has-text('Allow')",
                       "button:has-text('Approve')", "text=/^\\s*authorize\\s*$/i"])
            time.sleep(1)
        browser.close()
    srv.shutdown()

    if "code" not in _captured:
        print("NO authorization code captured.", file=sys.stderr)
        return 3
    if _captured.get("state") != state:
        print("state mismatch — aborting.", file=sys.stderr)
        return 4
    tok = httpx.post(
        BASE + "/mcp/oauth/token",
        data={
            "grant_type": "authorization_code", "code": _captured["code"],
            "redirect_uri": REDIRECT, "client_id": cid, "code_verifier": verifier,
        },
        timeout=30,
    )
    if tok.status_code != 200:
        print(f"token exchange failed {tok.status_code}: {tok.text[:200]}", file=sys.stderr)
        return 5
    t = tok.json()
    rec = {
        "access_token": t["access_token"],
        "refresh_token": t.get("refresh_token"),
        "token_type": t.get("token_type", "Bearer"),
        "scope": t.get("scope", "mcp"),
        "client_id": cid,
        "expires_at": int(time.time()) + int(t.get("expires_in", 3600)),
    }
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"SUCCESS — token saved to {TOKEN_PATH.relative_to(REPO_ROOT)} "
          f"(refresh_token={'present' if rec['refresh_token'] else 'ABSENT'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
