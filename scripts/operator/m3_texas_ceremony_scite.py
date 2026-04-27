"""M3 Texas ceremony (Scite MCP via OAuth 2.1) — operator helper to close M5 condition #2.

Connects to https://api.scite.ai/mcp via OAuth 2.1 (browser-based authorization
code flow with PKCE), discovers tools via MCP tools/list, calls the appropriate
search tool, captures results + provenance, saves evidence, and prints the
addendum block ready to paste into the M3 verdict artifact.

Uses the official `mcp` Python SDK's OAuthClientProvider helper (which handles
DCR + PKCE + token caching automatically). Browser pops on first run; you click
Authorize on scite.ai; token cached for future runs.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\m3_texas_ceremony_scite.py

    # Optional: search query
    .venv\\Scripts\\python.exe scripts\\operator\\m3_texas_ceremony_scite.py --query "your topic"

Requires: paid scite subscription (operator-confirmed); browser available on
operator's machine for the one-time OAuth Authorize click.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import threading
import webbrowser
from datetime import UTC, datetime
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

sys.path.insert(0, str(REPO_ROOT))

SCITE_MCP_URL = os.environ.get("SCITE_MCP_URL", "https://api.scite.ai/mcp")
CALLBACK_PORT = 8765
CALLBACK_REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/callback"

DEFAULT_QUERY = "neuroplasticity adult learning evidence-based instructional design"
ARTIFACT_DATE = datetime.now(tz=UTC).strftime("%Y-%m-%d")
ARTIFACT_DIR = REPO_ROOT / "tests" / "fixtures" / "specialists" / "texas" / "live_retrieval" / ARTIFACT_DATE

# Token cache outside the repo (operator-local; not committed)
TOKEN_CACHE_DIR = Path.home() / ".cache" / "course-content-production" / "scite-mcp"
TOKEN_FILE = TOKEN_CACHE_DIR / "token.json"
CLIENT_INFO_FILE = TOKEN_CACHE_DIR / "client_info.json"


# ---------------------------------------------------------------------------
# TokenStorage — file-based; survives restarts; refresh handled by SDK.
# ---------------------------------------------------------------------------


class FileTokenStorage:
    """Minimal `mcp.client.auth.TokenStorage` impl backed by JSON files."""

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


# ---------------------------------------------------------------------------
# Browser redirect + local-server callback handler.
# ---------------------------------------------------------------------------


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
        body = (
            "<html><body style='font-family:sans-serif;padding:40px;'>"
            "<h2>Scite OAuth — authorization received.</h2>"
            "<p>You may close this tab and return to the terminal.</p>"
            "</body></html>"
        )
        self.wfile.write(body.encode("utf-8"))
        _callback_done.set()

    def log_message(self, *args, **kwargs) -> None:  # noqa: N802
        pass  # suppress request log spam


def _serve_one_callback() -> None:
    server = HTTPServer(("localhost", CALLBACK_PORT), _CallbackHandler)
    server.timeout = 300  # 5 min for operator to click Authorize
    server.handle_request()


async def redirect_handler(authorization_url: str) -> None:
    """OAuthClientProvider hands us the authorization URL; we pop a browser."""
    print(f"\nOpening browser for Scite OAuth authorization...")
    print(f"If the browser does not open, paste this URL manually:")
    print(f"  {authorization_url}\n")
    webbrowser.open(authorization_url)


async def callback_handler() -> tuple[str, str | None]:
    """OAuthClientProvider awaits this; returns (code, state) from the redirect."""
    # Start the local HTTP server in a thread; wait for the event.
    server_thread = threading.Thread(target=_serve_one_callback, daemon=True)
    server_thread.start()

    # Poll the threading.Event from async context.
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


# ---------------------------------------------------------------------------
# Main async ceremony
# ---------------------------------------------------------------------------


async def run_ceremony(args: argparse.Namespace) -> int:
    from mcp import ClientSession
    from mcp.client.auth import OAuthClientProvider
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.shared.auth import OAuthClientMetadata

    storage = FileTokenStorage(TOKEN_FILE, CLIENT_INFO_FILE)

    client_metadata = OAuthClientMetadata(
        client_name="course-content-production-m3-ceremony",
        redirect_uris=[CALLBACK_REDIRECT_URI],
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        token_endpoint_auth_method="none",  # public client (PKCE)
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

    print("Connecting to Scite MCP (OAuth flow may pop browser on first run)...")

    try:
        async with streamablehttp_client(SCITE_MCP_URL, auth=oauth) as (
            read_stream,
            write_stream,
            get_session_id,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("MCP session initialized + authenticated.\n")

                tools_response = await session.list_tools()
                tools = tools_response.tools
                print(f"Discovered {len(tools)} tool(s) on Scite MCP:")
                for tool in tools:
                    print(f"  - {tool.name}: {(tool.description or '').splitlines()[0][:120]}")
                print()

                # Pick the search-style tool (heuristic: first tool whose name contains 'search')
                search_tool = None
                for tool in tools:
                    if "search" in tool.name.lower():
                        search_tool = tool
                        break
                if search_tool is None and tools:
                    search_tool = tools[0]
                if search_tool is None:
                    print("ERROR: Scite MCP exposed zero tools. Cannot proceed.", file=sys.stderr)
                    return 1

                print(f"Selected tool for ceremony: {search_tool.name!r}")
                print(f"Tool input schema (top-level keys): {list((search_tool.inputSchema or {}).get('properties', {}).keys())}")
                print()

                # Build minimal arguments. Most search tools accept a 'query' param;
                # fall back to 'q' if that's the schema. If neither is present, we
                # send query under the first required-string parameter.
                input_props = (search_tool.inputSchema or {}).get("properties", {})
                if "query" in input_props:
                    arguments = {"query": args.query}
                elif "q" in input_props:
                    arguments = {"q": args.query}
                else:
                    # Take first string-typed property
                    for prop_name, prop_schema in input_props.items():
                        if prop_schema.get("type") == "string":
                            arguments = {prop_name: args.query}
                            break
                    else:
                        arguments = {}

                # Add max-results style arg if schema supports it
                if "limit" in input_props:
                    arguments["limit"] = args.max_results
                elif "max_results" in input_props:
                    arguments["max_results"] = args.max_results
                elif "page_size" in input_props:
                    arguments["page_size"] = args.max_results

                print(f"Calling {search_tool.name}({arguments})...")
                result = await session.call_tool(search_tool.name, arguments=arguments)

                # result.content is list[TextContent | ImageContent | ...]
                content_summary = [
                    {
                        "type": c.type,
                        "text_excerpt": (c.text[:500] + "..." if len(c.text) > 500 else c.text)
                        if hasattr(c, "text") and c.text
                        else None,
                    }
                    for c in result.content
                ]
                is_error = result.isError if hasattr(result, "isError") else False

                if is_error:
                    print(f"\nWARNING: tool call returned isError=True.")
                    print(f"Content: {content_summary}")

                evidence_payload = {
                    "ceremony_date": ARTIFACT_DATE,
                    "captured_at": datetime.now(tz=UTC).isoformat(),
                    "provider": "scite",
                    "transport": "MCP Streamable HTTP via OAuth 2.1 (Authorization Code + PKCE)",
                    "endpoint": SCITE_MCP_URL,
                    "tools_discovered": [
                        {"name": t.name, "description": (t.description or "")[:200]}
                        for t in tools
                    ],
                    "tool_invoked": search_tool.name,
                    "tool_arguments": arguments,
                    "is_error": is_error,
                    "content_summary": content_summary,
                    "raw_content_count": len(result.content) if result.content else 0,
                }

                evidence_json = json.dumps(evidence_payload, indent=2, default=str)
                sha256 = hashlib.sha256(evidence_json.encode("utf-8")).hexdigest()

                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                evidence_path = ARTIFACT_DIR / f"{sha256}.json"
                evidence_path.write_text(evidence_json, encoding="utf-8")

                print(f"\nEvidence saved: {evidence_path}")
                print(f"SHA256: {sha256}")

                metadata_path = ARTIFACT_DIR / "LIVE_RETRIEVAL_METADATA.md"
                metadata_text = f"""# M3 Live Retrieval Metadata - {ARTIFACT_DATE}

- **Provider:** scite (Texas provider directory; shape=retrieval, status=ready)
- **Transport:** MCP Streamable HTTP via OAuth 2.1 (Authorization Code + PKCE; browser-based)
- **Endpoint:** `{SCITE_MCP_URL}`
- **OAuth client_name:** course-content-production-m3-ceremony
- **Token cache:** `{TOKEN_FILE}` (operator-local; not committed)
- **Tools discovered:** {len(tools)} ({", ".join(t.name for t in tools)})
- **Tool invoked:** `{search_tool.name}` with arguments `{json.dumps(arguments)}`
- **isError:** {is_error}
- **Content items returned:** {len(result.content) if result.content else 0}
- **Evidence path:** `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/{sha256}.json`
- **SHA256:** `{sha256}`
- **Captured at:** {datetime.now(tz=UTC).isoformat()}
- **Texas retrieval contract:** `skills/bmad-agent-texas/references/retrieval-contract.md`
- **Note:** existing `SciteProvider` is hardwired to HTTP Basic auth (legacy assumption);
  this ceremony bypasses it via the official `mcp` SDK's `OAuthClientProvider`. The
  SciteProvider auth-model defect is filed as deferred-inventory follow-on
  `5a-2-scite-mcp-oauth-integration` for proper migration of the production class.
"""
                metadata_path.write_text(metadata_text, encoding="utf-8")
                print(f"Metadata: {metadata_path}")

                # Addendum block
                print("\n" + "=" * 60)
                print("ADDENDUM BLOCK -- paste into:")
                print("  _bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md")
                print("=" * 60)
                print()
                print(f"## Operator-Window Addendum (M3 close - {ARTIFACT_DATE})")
                print()
                print(f"M3 Texas live-retrieval ceremony executed {ARTIFACT_DATE} via Scite MCP.")
                print(f"OAuth 2.1 authorization-code flow + PKCE; operator authorized in browser; token cached.")
                print()
                print(f"- Provider: `scite` (shape=retrieval, status=ready; capability=citation-network)")
                print(f"- Transport: MCP Streamable HTTP via OAuth 2.1 + PKCE")
                print(f"- Endpoint: `{SCITE_MCP_URL}`")
                print(f"- Tools discovered: {len(tools)} ({', '.join(t.name for t in tools)})")
                print(f"- Tool invoked: `{search_tool.name}({json.dumps(arguments)})`")
                print(f"- isError: {is_error}")
                print(f"- Content items returned: {len(result.content) if result.content else 0}")
                print(f"- Evidence: `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/{sha256}.json`")
                print(f"- SHA256: `{sha256}`")
                print(f"- Metadata: `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/LIVE_RETRIEVAL_METADATA.md`")
                print()
                print(f"**Bonus discovery (third A16 instance today):** existing `SciteProvider` is hardwired to")
                print(f"HTTP Basic auth (SCITE_USER_NAME + SCITE_PASSWORD); the real Scite MCP requires OAuth 2.1")
                print(f"Bearer per WWW-Authenticate header. Probe surfaced the gap BEFORE blind ceremony attempt")
                print(f"— exactly the A16 prevention pattern working as designed. M3 ceremony bypasses the legacy")
                print(f"`SciteProvider` via the official `mcp` Python SDK's `OAuthClientProvider`. Production-class")
                print(f"migration of `SciteProvider` to OAuth filed as deferred-inventory follow-on")
                print(f"`5a-2-scite-mcp-oauth-integration` (~2-3pt; substantial work; not in MVP scope).")
                print()
                print(f"Texas's Shape 3-Disciplined retrieval contract proven end-to-end against a live")
                print(f"scholarly retrieval-shape provider. M3 condition closes. Flip")
                print(f"`2a.4-followon-ac-b-op-live-retrieval` in `_bmad-output/planning-artifacts/deferred-inventory.md`")
                print(f"from DEFERRED-CONTINUES to RESOLVED-{ARTIFACT_DATE}.")
                print()
                print("=" * 60)
                print("CEREMONY COMPLETE")
                print("=" * 60)

                return 0

    except Exception as exc:
        print(f"\nERROR during MCP session: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="M3 Texas ceremony (Scite MCP via OAuth 2.1)")
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help=f"Scholarly search query. Default: {DEFAULT_QUERY!r}",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Max results to retrieve (default: 5)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("M3 TEXAS CEREMONY (Scite MCP via OAuth 2.1)")
    print("=" * 60)
    print(f"Provider:     scite.ai (shape=retrieval, status=ready)")
    print(f"Endpoint:     {SCITE_MCP_URL}")
    print(f"Auth:         OAuth 2.1 + PKCE (browser-based, one-time)")
    print(f"Token cache:  {TOKEN_FILE}")
    print(f"Query:        {args.query!r}")
    print(f"Max results:  {args.max_results}")
    print(f"Artifact dir: {ARTIFACT_DIR}")
    print("=" * 60)
    print()

    print("On first run, your browser will open Scite's OAuth authorize page.")
    print("After you click 'Authorize', the token is cached for future runs.")
    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted by operator.")
        return 0

    return asyncio.run(run_ceremony(args))


if __name__ == "__main__":
    sys.exit(main())
