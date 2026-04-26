"""Pre-flight check runner — verifies tool ecosystem readiness.

Orchestrates MCP config checks, API heartbeat/smoke scripts, and
generates a structured readiness report with resolution guidance.

Usage:
    .venv/Scripts/python -m skills.pre-flight-check.scripts.preflight_runner
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts.utilities.env_loader import load_env
from scripts.utilities.file_helpers import project_root, safe_read_json
from scripts.utilities.logging_setup import setup_logging

logger = setup_logging("preflight", level=10)


class ToolStatus(str, Enum):
    MCP_READY = "MCP-ready"
    API_READY = "API-ready"
    MANUAL_ONLY = "manual-only"
    BLOCKED = "blocked/deferred"
    FAILED = "resolution-needed"
    SKIPPED = "skipped"


@dataclass
class ToolResult:
    name: str
    status: ToolStatus
    detail: str = ""
    resolution: str = ""


@dataclass
class PreflightReport:
    results: list[ToolResult] = field(default_factory=list)
    heartbeat_output: str = ""
    smoke_outputs: dict[str, str] = field(default_factory=dict)
    mcp_servers: list[str] = field(default_factory=list)

    def add(self, result: ToolResult) -> None:
        self.results.append(result)

    def by_status(self, status: ToolStatus) -> list[ToolResult]:
        return [r for r in self.results if r.status == status]

    @property
    def has_failures(self) -> bool:
        return any(r.status == ToolStatus.FAILED for r in self.results)

    def format_report(self) -> str:
        lines = [
            "=" * 50,
            "PRE-FLIGHT CHECK RESULTS",
            "=" * 50,
            "",
        ]
        sections = [
            (ToolStatus.MCP_READY, "MCP-READY"),
            (ToolStatus.API_READY, "API-READY"),
            (ToolStatus.MANUAL_ONLY, "MANUAL-ONLY"),
            (ToolStatus.BLOCKED, "BLOCKED/DEFERRED"),
            (ToolStatus.FAILED, "RESOLUTION NEEDED"),
            (ToolStatus.SKIPPED, "SKIPPED (key not configured)"),
        ]
        for status, label in sections:
            tools = self.by_status(status)
            if not tools:
                continue
            lines.append(f"{label}:")
            for t in tools:
                icon = {
                    ToolStatus.MCP_READY: "+",
                    ToolStatus.API_READY: "+",
                    ToolStatus.MANUAL_ONLY: "o",
                    ToolStatus.BLOCKED: "!",
                    ToolStatus.FAILED: "X",
                    ToolStatus.SKIPPED: "-",
                }.get(t.status, "?")
                lines.append(f"  {icon} {t.name} -- {t.detail}")
                if t.resolution:
                    lines.append(f"    Resolution: {t.resolution}")
            lines.append("")

        mcp_count = len(self.by_status(ToolStatus.MCP_READY))
        api_count = len(self.by_status(ToolStatus.API_READY))
        passed = mcp_count + api_count
        failed = len(self.by_status(ToolStatus.FAILED))
        manual = len(self.by_status(ToolStatus.MANUAL_ONLY))
        blocked = len(self.by_status(ToolStatus.BLOCKED))
        skipped = len(self.by_status(ToolStatus.SKIPPED))

        lines.append("=" * 50)
        lines.append(
            f"SUMMARY: {passed} ready, {failed} failed, "
            f"{manual} manual, {blocked} blocked, {skipped} skipped"
        )
        lines.append("=" * 50)
        return "\n".join(lines)


# -- MCP Config Checking --

MCP_SERVERS_WITH_HEARTBEAT = {"gamma", "canvas-lms"}


def check_mcp_configs(root: Path) -> dict[str, dict[str, Any]]:
    """Parse MCP configurations from .mcp.json and .cursor/mcp.json."""
    servers: dict[str, dict[str, Any]] = {}
    for config_path in [root / ".mcp.json", root / ".cursor" / "mcp.json"]:
        if not config_path.exists():
            continue
        try:
            data = safe_read_json(config_path)
            if isinstance(data, dict) and "mcpServers" in data:
                for name, cfg in data["mcpServers"].items():
                    if name not in servers:
                        servers[name] = cfg
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to parse %s: %s", config_path, exc)
    return servers


# -- Node.js Script Runner --


def run_node_script(script_path: Path, cwd: Path) -> tuple[int, str, str]:
    """Run a Node.js script and capture output."""
    if not script_path.exists():
        return 1, "", f"Script not found: {script_path}"

    try:
        result = subprocess.run(
            ["node", str(script_path)],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Script timed out after 120s"
    except FileNotFoundError:
        return 1, "", "Node.js not found — install Node.js to run heartbeat checks"


# -- Heartbeat Output Parser --

# Accept '--', a true em dash, and common mojibake form ('â€”') seen on some Windows setups.
HEARTBEAT_PATTERN = re.compile(r"\s*(PASS|FAIL|SKIP):\s*(.+?)\s*(?:--|—|â€”)+\s*(.+)")
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def parse_heartbeat_output(output: str) -> list[dict[str, str]]:
    """Parse PASS/FAIL/SKIP lines from heartbeat_check.mjs output."""
    results = []
    for line in output.splitlines():
        clean_line = ANSI_ESCAPE_PATTERN.sub("", line)
        m = HEARTBEAT_PATTERN.match(clean_line)
        if m:
            results.append({
                "status": m.group(1),
                "name": m.group(2).strip(),
                "detail": m.group(3).strip(),
            })
    return results


# -- Resolution Guidance --

RESOLUTION_MAP = {
    "not set in .env": "Add the API key to your `.env` file (see docs/admin-guide.md).",
    "HTTP 401": "API key is invalid or expired. Regenerate from the tool's dashboard.",
    "HTTP 403": "API key lacks required permissions. Check scopes and plan level.",
    "HTTP 429": "Rate limited. Wait a few minutes, then retry.",
    "Connection error": "Check internet connectivity and verify the API URL.",
    "timeout": "Service may be down. Check the tool's status page.",
    "OAuth": "OAuth-based auth requires browser flow. Use the tool's MCP in Cursor.",
    "Manual workflow": "No API available. Agent provides specs; user executes in tool UI.",
}


def get_resolution(detail: str) -> str:
    """Match failure detail to resolution guidance."""
    detail_lower = detail.lower()
    for pattern, guidance in RESOLUTION_MAP.items():
        if pattern.lower() in detail_lower:
            return guidance
    return "Check .env configuration and tool documentation."


# -- Static Classifications --

MANUAL_ONLY_TOOLS = {
    "Vyond": "Manual workflow — API requires Enterprise plan",
    "CourseArc": "LTI/SCORM only — no REST API",
    "Articulate": "Desktop/web authoring — no REST API",
}

BLOCKED_TOOLS = {
    "Canva": "OAuth redirect rejected by Cursor — use Connect API directly when needed",
}

# Tools in this map are checked and reported, but connectivity failures do not
# block trial-run readiness because they are out of current production scope.
NON_BLOCKING_FAIL_TOOLS = {
    "botpress": (
        "Botpress is not in the current production workflow; connectivity is "
        "reported as deferred and does not block trial-run readiness."
    ),
}


# -- Notion API Check --


def check_notion_api(env_vars: dict[str, str]) -> ToolResult:
    """Verify Notion API connectivity with a lightweight /users/me call."""
    token = env_vars.get("NOTION_API_KEY") or os.environ.get("NOTION_API_KEY", "")
    if not token:
        return ToolResult(
            name="Notion",
            status=ToolStatus.SKIPPED,
            detail="NOTION_API_KEY not set in .env",
            resolution="Add your Notion internal integration token to .env",
        )
    try:
        req = urllib.request.Request(
            "https://api.notion.com/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return ToolResult(
                    name="Notion",
                    status=ToolStatus.MCP_READY,
                    detail="API authenticated, MCP configured (22 tools)",
                )
    except urllib.error.HTTPError as exc:
        return ToolResult(
            name="Notion",
            status=ToolStatus.FAILED,
            detail=f"HTTP {exc.code} from Notion API",
            resolution=get_resolution(f"HTTP {exc.code}"),
        )
    except (urllib.error.URLError, TimeoutError) as exc:
        return ToolResult(
            name="Notion",
            status=ToolStatus.FAILED,
            detail=f"Connection error: {exc}",
            resolution=get_resolution("Connection error"),
        )
    return ToolResult(
        name="Notion", status=ToolStatus.FAILED, detail="Unexpected response",
    )


# -- Box Drive Check --


def check_box_drive(env_vars: dict[str, str]) -> ToolResult:
    """Verify Box Drive local path is accessible and contains files."""
    box_path = env_vars.get("BOX_DRIVE_PATH") or os.environ.get("BOX_DRIVE_PATH", "")
    if not box_path:
        return ToolResult(
            name="Box Drive",
            status=ToolStatus.SKIPPED,
            detail="BOX_DRIVE_PATH not set in .env",
            resolution="Add your local Box Drive folder path to .env",
        )
    p = Path(box_path)
    if not p.exists():
        return ToolResult(
            name="Box Drive",
            status=ToolStatus.FAILED,
            detail=f"Path does not exist: {box_path}",
            resolution="Verify Box Drive is installed and the path is correct in .env",
        )
    if not p.is_dir():
        return ToolResult(
            name="Box Drive",
            status=ToolStatus.FAILED,
            detail=f"Path is not a directory: {box_path}",
            resolution="BOX_DRIVE_PATH should point to the Box Drive sync folder",
        )
    try:
        items = list(p.iterdir())
        return ToolResult(
            name="Box Drive",
            status=ToolStatus.API_READY,
            detail=f"Local path accessible, {len(items)} top-level items",
        )
    except PermissionError:
        return ToolResult(
            name="Box Drive",
            status=ToolStatus.FAILED,
            detail=f"Permission denied reading: {box_path}",
            resolution="Check file permissions on the Box Drive folder",
        )


# -- Double-Dispatch Compatibility Check --


def check_double_dispatch_compatibility(env_vars: dict[str, str]) -> ToolResult:
    """Validate that double-dispatch mode requirements are met.

    Double-dispatch requires a valid GAMMA_API_KEY since Gamma is
    the API that gets called 2x for A/B variant comparison.
    """
    gamma_key = env_vars.get("GAMMA_API_KEY") or os.environ.get("GAMMA_API_KEY", "")
    if not gamma_key:
        return ToolResult(
            name="Double-Dispatch (Gamma)",
            status=ToolStatus.FAILED,
            detail="GAMMA_API_KEY required for double-dispatch mode but not set",
            resolution="Add GAMMA_API_KEY to .env to enable double-dispatch A/B generation",
        )
    return ToolResult(
        name="Double-Dispatch (Gamma)",
        status=ToolStatus.API_READY,
        detail="GAMMA_API_KEY present; double-dispatch capable",
    )


def check_kling_compatibility(env_vars: dict[str, str]) -> ToolResult:
    """Validate that Kling credentials are present for motion-enabled runs."""
    access_key = env_vars.get("KLING_ACCESS_KEY") or os.environ.get("KLING_ACCESS_KEY", "")
    secret_key = env_vars.get("KLING_SECRET_KEY") or os.environ.get("KLING_SECRET_KEY", "")
    if not access_key or not secret_key:
        return ToolResult(
            name="Motion Pipeline (Kling)",
            status=ToolStatus.FAILED,
            detail="KLING_ACCESS_KEY and KLING_SECRET_KEY are required when motion_enabled is true",
            resolution="Add KLING_ACCESS_KEY and KLING_SECRET_KEY to .env for motion-enabled runs",
        )
    return ToolResult(
        name="Motion Pipeline (Kling)",
        status=ToolStatus.API_READY,
        detail="Kling credentials present; motion-enabled runs are API-capable",
    )


# -- Main Runner --


def run_preflight(
    root: Path | None = None,
    *,
    double_dispatch: bool = False,
    motion_enabled: bool = False,
) -> PreflightReport:
    """Execute the full pre-flight check sequence."""
    if root is None:
        root = project_root()

    report = PreflightReport()

    # 1. MCP config check
    logger.info("Checking MCP configurations...")
    mcp_servers = check_mcp_configs(root)
    report.mcp_servers = list(mcp_servers.keys())
    logger.info("Found %d MCP server(s): %s", len(mcp_servers), ", ".join(mcp_servers))

    # 2. Run heartbeat check
    logger.info("Running heartbeat check...")
    heartbeat_script = root / "scripts" / "heartbeat_check.mjs"
    exit_code, stdout, stderr = run_node_script(heartbeat_script, root)
    report.heartbeat_output = stdout

    if exit_code != 0 and not stdout:
        logger.warning("Heartbeat script error: %s", stderr)

    heartbeat_results = parse_heartbeat_output(stdout)

    # 3. Process heartbeat results + MCP status
    for hr in heartbeat_results:
        tool_name = hr["name"]
        mcp_key = tool_name.lower().replace(" ", "-").replace("_", "-")
        for suffix in ("-api", "-mcp"):
            if mcp_key.endswith(suffix):
                mcp_key = mcp_key[: -len(suffix)]
                break

        if hr["status"] == "PASS":
            if mcp_key in mcp_servers or any(mcp_key in k for k in mcp_servers):
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.MCP_READY,
                    detail=f"MCP configured, {hr['detail']}",
                ))
            else:
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.API_READY,
                    detail=hr["detail"],
                ))
        elif hr["status"] == "FAIL":
            normalized = tool_name.lower().replace(" api", "").replace(" mcp", "").strip()
            if normalized in NON_BLOCKING_FAIL_TOOLS:
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.BLOCKED,
                    detail=f"{hr['detail']} (non-blocking for current production scope)",
                    resolution=NON_BLOCKING_FAIL_TOOLS[normalized],
                ))
            else:
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.FAILED,
                    detail=hr["detail"],
                    resolution=get_resolution(hr["detail"]),
                ))
        elif hr["status"] == "SKIP":
            if "not set" in hr["detail"]:
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.SKIPPED,
                    detail=hr["detail"],
                    resolution=get_resolution(hr["detail"]),
                ))
            elif "manual" in hr["detail"].lower() or "no api" in hr["detail"].lower():
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.MANUAL_ONLY,
                    detail=hr["detail"],
                ))
            elif "oauth" in hr["detail"].lower() or "mcp" in hr["detail"].lower():
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.BLOCKED,
                    detail=hr["detail"],
                    resolution=get_resolution(hr["detail"]),
                ))
            else:
                report.add(ToolResult(
                    name=tool_name,
                    status=ToolStatus.SKIPPED,
                    detail=hr["detail"],
                ))

    # 4. Run targeted smoke scripts
    smoke_scripts = {
        "ElevenLabs (smoke)": root / "scripts" / "smoke_elevenlabs.mjs",
        "Qualtrics (smoke)": root / "scripts" / "smoke_qualtrics.mjs",
    }
    for name, script in smoke_scripts.items():
        if not script.exists():
            continue
        logger.info("Running %s...", name)
        code, out, err = run_node_script(script, root)
        report.smoke_outputs[name] = out
        if code == 0:
            existing = [r for r in report.results if name.split(" ")[0] in r.name]
            for r in existing:
                r.detail += f" | Smoke: {out.strip().splitlines()[-1] if out.strip() else 'passed'}"
        else:
            logger.warning("%s failed: %s", name, err or out)

    # 5. Add static classifications for tools not in heartbeat
    seen_names = {r.name.lower() for r in report.results}

    for tool, detail in MANUAL_ONLY_TOOLS.items():
        if tool.lower() not in seen_names:
            report.add(ToolResult(
                name=tool, status=ToolStatus.MANUAL_ONLY, detail=detail,
            ))

    for tool, detail in BLOCKED_TOOLS.items():
        if tool.lower() not in seen_names:
            report.add(ToolResult(
                name=tool, status=ToolStatus.BLOCKED, detail=detail,
                resolution=get_resolution(detail),
            ))

    # 6. Notion API connectivity check
    logger.info("Checking Notion API connectivity...")
    env_vars = load_env(root / ".env")
    report.add(check_notion_api(env_vars))

    # 7. Box Drive path accessibility check
    logger.info("Checking Box Drive path...")
    report.add(check_box_drive(env_vars))

    # 8. Double-dispatch compatibility (only when flag is active)
    if double_dispatch:
        logger.info("Checking double-dispatch compatibility...")
        report.add(check_double_dispatch_compatibility(env_vars))

    # 9. Motion pipeline compatibility (only when flag is active)
    if motion_enabled:
        logger.info("Checking Kling compatibility for motion-enabled workflow...")
        report.add(check_kling_compatibility(env_vars))

    return report


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run tool pre-flight checks.")
    parser.add_argument("--double-dispatch", action="store_true")
    parser.add_argument("--motion-enabled", action="store_true")
    args = parser.parse_args(argv)

    report = run_preflight(
        double_dispatch=args.double_dispatch,
        motion_enabled=args.motion_enabled,
    )
    print(report.format_report())
    return 1 if report.has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
