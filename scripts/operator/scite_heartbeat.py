"""Scite MCP heartbeat — minimal OAuth + connect + tools/list.

Validates that the Scite MCP at https://api.scite.ai/mcp is reachable and
that OAuth 2.1 (browser-based authorization-code flow with PKCE) succeeds
end-to-end. Does NOT call any tool; just connects, lists tools, exits.

Run this BEFORE the full M3 ceremony script (m3_texas_ceremony_scite.py) to
confirm the OAuth flow works on your machine + your scite premium account.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\scite_heartbeat.py

First run: pops a browser at scite's authorize URL; you click "Authorize";
script captures the redirect on localhost:8765 and exchanges for a token.
Subsequent runs: token cached at ~/.cache/course-content-production/scite-mcp/
is reused (refresh handled by SDK).

Failure modes + interpretations:
  - Browser fails to open → URL printed to console; paste manually.
  - Authorize click rejected → check scite premium account is active.
  - 401 after authorize → token exchange failed; ping me with stderr.
  - tools/list returns []  → MCP connected but no tools exposed (unexpected).
  - tools/list returns named tools → SUCCESS; OAuth flow proven; M3
    ceremony at m3_texas_ceremony_scite.py will work.
"""

from __future__ import annotations

import asyncio
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    print("ERROR: python-dotenv not installed.", file=sys.stderr)
    sys.exit(1)

import os

SCITE_MCP_URL = os.environ.get("SCITE_MCP_URL", "https://api.scite.ai/mcp")
CALLBACK_PORT = 8765
CALLBACK_REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/callback"

TOKEN_CACHE_DIR = Path.home() / ".cache" / "course-content-production" / "scite-mcp"
TOKEN_FILE = TOKEN_CACHE_DIR / "token.json"
CLIENT_INFO_FILE = TOKEN_CACHE_DIR / "client_info.json"


# ---------------------------------------------------------------------------
# Reused-from-M3-ceremony: TokenStorage + redirect/callback handlers.
# (Kept in-script to avoid importing from a sibling operator script.)
# ---------------------------------------------------------------------------


class FileTokenStorage:
    def __init__(self, token_path: Path, client_info_path: Path) -> None:
        self.token_path = token_path
        self.client_info_path = client_info_path
        token_path.parent.mkdir(parents=True, exist_ok=True)

    async def get_tokens(self):
        from mcp.shared.auth import OAuthToken

        if not self.token_path.exists():
            return None
        try:
            data = json.loads(self.token_path.read_text(encoding="utf-8"))
            return OAuthToken.model_validate(data)
        except Exception:
            return None

    async def set_tokens(self, tokens) -> None:
        self.token_path.write_text(tokens.model_dump_json(exclude_none=True), encoding="utf-8")

    async def get_client_info(self):
        from mcp.shared.auth import OAuthClientInformationFull

        if not self.client_info_path.exists():
            return None
        try:
            data = json.loads(self.client_info_path.read_text(encoding="utf-8"))
            return OAuthClientInformationFull.model_validate(data)
        except Exception:
            return None

    async def set_client_info(self, info) -> None:
        self.client_info_path.write_text(info.model_dump_json(exclude_none=True), encoding="utf-8")


_callback_captured: dict = {}
_callback_done = threading.Event()


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if not self.path.startswith("/callback"):
            self.send_response(404)
            self.end_headers()
            return
        params = parse_qs(urlparse(self.path).query)
        _callback_captured["code"] = params.get("code", [None])[0]
        _callback_captured["state"] = params.get("state", [None])[0]
        _callback_captured["error"] = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:sans-serif;padding:40px;'>"
            b"<h2>Scite OAuth heartbeat - authorization received.</h2>"
            b"<p>You may close this tab and return to the terminal.</p>"
            b"</body></html>"
        )
        _callback_done.set()

    def log_message(self, *args, **kwargs) -> None:  # noqa: N802
        pass


def _serve_one_callback() -> None:
    server = HTTPServer(("localhost", CALLBACK_PORT), _CallbackHandler)
    server.timeout = 300
    server.handle_request()


async def redirect_handler(authorization_url: str) -> None:
    print(f"\nOpening browser for Scite OAuth authorization...")
    print(f"If browser does not open, paste this URL manually:\n  {authorization_url}\n")
    webbrowser.open(authorization_url)


async def callback_handler() -> tuple[str, str | None]:
    server_thread = threading.Thread(target=_serve_one_callback, daemon=True)
    server_thread.start()
    while not _callback_done.is_set():
        await asyncio.sleep(0.2)
    server_thread.join(timeout=5)
    if _callback_captured.get("error"):
        raise RuntimeError(f"OAuth authorization failed: {_callback_captured['error']}")
    code = _callback_captured.get("code")
    state = _callback_captured.get("state")
    if not code:
        raise RuntimeError("OAuth callback completed but no 'code' parameter received.")
    return (code, state)


async def heartbeat() -> int:
    from mcp import ClientSession
    from mcp.client.auth import OAuthClientProvider
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.shared.auth import OAuthClientMetadata

    storage = FileTokenStorage(TOKEN_FILE, CLIENT_INFO_FILE)

    client_metadata = OAuthClientMetadata(
        client_name="course-content-production-scite-heartbeat",
        redirect_uris=[CALLBACK_REDIRECT_URI],
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        token_endpoint_auth_method="none",  # PKCE
        scope=None,
    )

    oauth = OAuthClientProvider(
        server_url=SCITE_MCP_URL,
        client_metadata=client_metadata,
        storage=storage,
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
        timeout=300.0,
    )

    print("Connecting to Scite MCP...")
    print("(First run pops browser for OAuth authorize click; subsequent runs use cached token.)\n")

    try:
        async with streamablehttp_client(SCITE_MCP_URL, auth=oauth) as (
            read_stream,
            write_stream,
            _get_session_id,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("OK   - MCP session initialized + authenticated.")

                tools_response = await session.list_tools()
                tools = tools_response.tools

                print(f"OK   - tools/list returned {len(tools)} tool(s).")
                print()
                if not tools:
                    print("WARNING: zero tools exposed. MCP responded but no tools available.")
                    print("Possible: scite premium account doesn't have MCP tool access enabled.")
                    return 1

                print("Discovered tools:")
                for tool in tools:
                    desc = (tool.description or "(no description)").splitlines()[0][:120]
                    print(f"  - {tool.name}: {desc}")
                    input_schema = tool.inputSchema or {}
                    props = list(input_schema.get("properties", {}).keys())
                    if props:
                        print(f"      input properties: {props}")

                print()
                print("=" * 60)
                print("HEARTBEAT SUCCESS")
                print("=" * 60)
                print(f"Token cached at: {TOKEN_FILE}")
                print(f"Client info cached at: {CLIENT_INFO_FILE}")
                print()
                print("Next: run scripts/operator/m3_texas_ceremony_scite.py to perform the")
                print("full M3 ceremony with a real search call. Auth is now cached so the")
                print("ceremony script reuses the token (no second browser pop).")
                print()
                print("Findings worth noting:")
                print(f"- Scite MCP exposes {len(tools)} tool(s). Compare against existing")
                print("  SciteProvider's hardcoded tool name assumptions:")
                print("    _SCITE_TOOL_SEARCH = 'search'")
                print("    _SCITE_TOOL_PAPER = 'paper_metadata'")
                print("    _SCITE_TOOL_CITATIONS = 'citation_contexts'")
                print("  If discovered tool names differ, the existing SciteProvider needs an")
                print("  update beyond just OAuth migration (already filed as deferred-inventory")
                print("  entry `5a-2-scite-mcp-oauth-integration`).")
                return 0

    except Exception as exc:
        print(f"\nERROR during heartbeat: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    print("=" * 60)
    print("SCITE MCP HEARTBEAT")
    print("=" * 60)
    print(f"Endpoint:     {SCITE_MCP_URL}")
    print(f"Auth:         OAuth 2.1 + PKCE (browser-based on first run)")
    print(f"Token cache:  {TOKEN_FILE}")
    print(f"Required:     premium scite account; browser available")
    print("=" * 60)
    print()
    print("This is a CONNECTION-ONLY heartbeat. It does NOT call any tool")
    print("(no search, no scholarly retrieval). Just OAuth + tools/list.")
    print()
    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted by operator.")
        return 0

    return asyncio.run(heartbeat())


if __name__ == "__main__":
    sys.exit(main())
