"""APP session readiness checks for runtime infrastructure health.

This service validates local APP runtime prerequisites before production runs:
- SQLite coordination database presence/schema sanity
- critical state path existence and writeability
- mode_state readability when present
- import sanity for observability/reporting modules

It can optionally compose with the existing pre-flight tool check.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.util
import json
import os
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.state_management.db_init import init_database
from scripts.utilities.file_helpers import project_root

REQUIRED_DB_TABLES = {
    "production_runs",
    "agent_coordination",
    "quality_gates",
    "observability_events",
}


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    resolution: str = ""


def _now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _is_dir_writable(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    probe = path / f".write_probe_{uuid.uuid4().hex}.tmp"
    created = False
    try:
        probe.write_text("ok", encoding="utf-8")
        created = True
        return True
    except OSError:
        return False
    finally:
        if created:
            with contextlib.suppress(OSError):
                probe.unlink(missing_ok=True)


def _is_file_writable(path: Path) -> bool:
    return os.access(path, os.W_OK)


def _check_state_directory(root: Path, rel_path: str) -> CheckResult:
    target = root / rel_path
    if not target.exists():
        return CheckResult(
            name=f"state:{rel_path}",
            status="fail",
            detail=f"Missing required directory: {rel_path}",
            resolution="Run `.venv\\Scripts\\python -m scripts.state_management.init_state`.",
        )
    if not target.is_dir():
        return CheckResult(
            name=f"state:{rel_path}",
            status="fail",
            detail=f"Expected directory but found file: {rel_path}",
            resolution="Restore the expected directory structure under `state/`.",
        )
    if not _is_dir_writable(target):
        return CheckResult(
            name=f"state:{rel_path}",
            status="fail",
            detail=f"Directory is not writable: {rel_path}",
            resolution="Fix file permissions for this state directory.",
        )
    return CheckResult(
        name=f"state:{rel_path}",
        status="pass",
        detail=f"Directory exists and is writable: {rel_path}",
    )


def _check_mode_state(root: Path) -> CheckResult:
    mode_state = root / "state" / "runtime" / "mode_state.json"
    if not mode_state.exists():
        return CheckResult(
            name="mode_state",
            status="skip",
            detail="mode_state.json not present (allowed)",
            resolution="Optional: initialize mode state via `manage_mode.py status`.",
        )

    try:
        data = json.loads(mode_state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            name="mode_state",
            status="fail",
            detail=f"mode_state.json unreadable/invalid JSON: {exc}",
            resolution="Repair `state/runtime/mode_state.json` or regenerate with manage_mode.py.",
        )

    mode = data.get("mode") if isinstance(data, dict) else None

    if not _is_file_writable(mode_state):
        return CheckResult(
            name="mode_state",
            status="fail",
            detail="mode_state.json is not writable",
            resolution="Fix file permissions for state/runtime/mode_state.json.",
        )

    if mode not in {"default", "ad-hoc", None}:
        return CheckResult(
            name="mode_state",
            status="warn",
            detail=f"mode_state.json parsed but mode value is unusual: {mode}",
            resolution="Use `manage_mode.py set --mode default|ad-hoc` to normalize.",
        )

    return CheckResult(
        name="mode_state",
        status="pass",
        detail="mode_state.json is readable JSON",
    )


def _check_coordination_db(root: Path) -> CheckResult:
    db_path = root / "state" / "runtime" / "coordination.db"
    initialized = False
    repaired = False

    if not db_path.exists():
        try:
            init_database(db_path)
            initialized = True
        except Exception as exc:  # pragma: no cover - defensive
            return CheckResult(
                name="coordination_db",
                status="fail",
                detail=f"Failed to initialize coordination DB: {exc}",
                resolution=(
                    "Run `.venv\\Scripts\\python -m "
                    "scripts.state_management.init_state` and retry."
                ),
            )

    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    except sqlite3.Error as exc:
        return CheckResult(
            name="coordination_db",
            status="fail",
            detail=f"SQLite connection/schema query failed: {exc}",
            resolution="Delete corrupted DB and run state initialization again.",
        )
    finally:
        with contextlib.suppress(Exception):  # pragma: no cover - defensive
            conn.close()

    tables = {row[0] for row in rows}
    missing = sorted(REQUIRED_DB_TABLES - tables)
    if missing:
        # Idempotent repair path for partial/legacy schemas.
        conn = None
        try:
            init_database(db_path)
            repaired = True
            conn = sqlite3.connect(str(db_path))
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            tables = {row[0] for row in rows}
            missing = sorted(REQUIRED_DB_TABLES - tables)
        except sqlite3.Error as exc:
            return CheckResult(
                name="coordination_db",
                status="fail",
                detail=f"DB schema repair failed: {exc}",
                resolution="Re-run state initialization or recreate coordination.db.",
            )
        finally:
            if conn is not None:
                with contextlib.suppress(Exception):  # pragma: no cover - defensive
                    conn.close()

        if missing:
            return CheckResult(
                name="coordination_db",
                status="fail",
                detail=f"Missing required table(s): {', '.join(missing)}",
                resolution="Re-run DB initialization to restore required schema.",
            )

    if initialized:
        return CheckResult(
            name="coordination_db",
            status="pass",
            detail="coordination.db was missing and has been initialized successfully",
        )

    if repaired:
        return CheckResult(
            name="coordination_db",
            status="pass",
            detail="coordination.db schema was incomplete and has been repaired successfully",
        )

    return CheckResult(
        name="coordination_db",
        status="pass",
        detail="coordination.db present with required schema",
    )


def _load_module_from_path(module_name: str, path: Path) -> None:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def _check_bundle_run_constants(root: Path, bundle_dir: Path | None) -> CheckResult:
    """When --bundle-dir is set, require a valid run-constants.yaml if present."""
    if bundle_dir is None:
        return CheckResult(
            name="bundle_run_constants",
            status="skip",
            detail="No bundle directory supplied (optional check)",
            resolution="Pass --bundle-dir to validate frozen run-constants.yaml.",
        )

    bpath = Path(bundle_dir).resolve()
    rc_file = bpath / "run-constants.yaml"
    if not rc_file.is_file():
        return CheckResult(
            name="bundle_run_constants",
            status="skip",
            detail=f"No run-constants.yaml under {bpath.name} (optional)",
            resolution="Add run-constants.yaml when freezing a tracked run.",
        )

    try:
        from scripts.utilities.run_constants import RunConstantsError, load_run_constants

        load_run_constants(bpath, root=root, verify_paths_exist=False)
    except RunConstantsError as exc:
        return CheckResult(
            name="bundle_run_constants",
            status="fail",
            detail=str(exc),
            resolution="Repair run-constants.yaml or correct --bundle-dir relative to repo root.",
        )

    return CheckResult(
        name="bundle_run_constants",
        status="pass",
        detail="run-constants.yaml present and valid for this bundle path",
        resolution="",
    )


def _check_import_sanity(root: Path) -> CheckResult:
    base = root / "skills" / "production-coordination" / "scripts"
    targets = {
        "observability_hooks": base / "observability_hooks.py",
        "run_reporting": base / "run_reporting.py",
    }

    for module_name, path in targets.items():
        if not path.exists():
            return CheckResult(
                name="imports",
                status="fail",
                detail=f"Missing required module file: {path.relative_to(root)}",
                resolution="Restore production-coordination scripts before running production.",
            )
        try:
            _load_module_from_path(f"session_readiness_{module_name}", path)
        except Exception as exc:
            return CheckResult(
                name="imports",
                status="fail",
                detail=f"Import sanity failed for {path.name}: {type(exc).__name__}: {exc}",
                resolution="Fix import/runtime errors in production-coordination scripts.",
            )

    return CheckResult(
        name="imports",
        status="pass",
        detail="Import sanity checks passed for observability/reporting modules",
    )


def _run_preflight_phase(root: Path, *, motion_enabled: bool = False) -> CheckResult:
    preflight_module = None

    try:
        preflight_module = importlib.import_module(
            "skills.pre_flight_check.scripts.preflight_runner"
        )
    except (ImportError, ModuleNotFoundError):
        # Repo keeps this skill in a hyphenated folder name.
        preflight_path = root / "skills" / "pre-flight-check" / "scripts" / "preflight_runner.py"
        if not preflight_path.exists():
            return CheckResult(
                name="preflight_tools",
                status="fail",
                detail="Pre-flight module import failed and file path fallback was not found",
                resolution="Restore pre-flight skill module before using --with-preflight.",
            )
        try:
            module_name = "preflight_runner_fallback"
            spec = importlib.util.spec_from_file_location(module_name, preflight_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load spec for {preflight_path}")
            preflight_module = importlib.util.module_from_spec(spec)
            import sys

            sys.modules[module_name] = preflight_module
            spec.loader.exec_module(preflight_module)
        except Exception as exc:
            return CheckResult(
                name="preflight_tools",
                status="fail",
                detail=f"Pre-flight module fallback load failed: {type(exc).__name__}: {exc}",
                resolution="Restore pre-flight skill module before using --with-preflight.",
            )

    try:
        tool_status = preflight_module.ToolStatus
        run_preflight = preflight_module.run_preflight

        report = run_preflight(root, motion_enabled=motion_enabled)
    except Exception as exc:
        return CheckResult(
            name="preflight_tools",
            status="warn",
            detail=f"Pre-flight composition unavailable: {type(exc).__name__}: {exc}",
            resolution="Run pre-flight manually to validate tool connectivity.",
        )

    mcp_ready = len(report.by_status(tool_status.MCP_READY))
    api_ready = len(report.by_status(tool_status.API_READY))
    failed = len(report.by_status(tool_status.FAILED))

    if report.has_failures:
        return CheckResult(
            name="preflight_tools",
            status="warn",
            detail=(
                "Tool pre-flight completed with failures; "
                f"ready={mcp_ready + api_ready}, failures={failed}"
            ),
            resolution=(
                "Review pre-flight output and resolve tool/API "
                "issues before long production runs."
            ),
        )

    return CheckResult(
        name="preflight_tools",
        status="pass",
        detail=f"Tool pre-flight passed (ready={mcp_ready + api_ready})",
    )


def _overall_status(checks: list[CheckResult]) -> str:
    statuses = {c.status for c in checks}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def format_summary(report: dict[str, Any]) -> str:
    lines = [
        "=" * 56,
        "APP SESSION READINESS",
        "=" * 56,
    ]
    for check in report["checks"]:
        icon = {
            "pass": "+",
            "warn": "!",
            "fail": "X",
            "skip": "-",
        }.get(check["status"], "?")
        lines.append(f"{icon} {check['name']}: {check['status']} - {check['detail']}")
        if check.get("resolution"):
            lines.append(f"    Resolution: {check['resolution']}")
    lines.append("-" * 56)
    lines.append(f"OVERALL: {report['overall_status'].upper()}")
    lines.append("=" * 56)
    return "\n".join(lines)


def run_readiness(
    root: Path | None = None,
    *,
    with_preflight: bool = False,
    motion_enabled: bool = False,
    bundle_dir: Path | None = None,
) -> dict[str, Any]:
    """Run APP runtime readiness checks and return a structured report."""
    root = root or project_root()

    checks = [
        _check_coordination_db(root),
        _check_state_directory(root, "state/config"),
        _check_state_directory(root, "state/runtime"),
        _check_mode_state(root),
        _check_import_sanity(root),
        _check_bundle_run_constants(root, bundle_dir),
    ]

    if with_preflight:
        checks.append(_run_preflight_phase(root, motion_enabled=motion_enabled))

    report = {
        "timestamp": _now_iso(),
        "root": str(root),
        "overall_status": _overall_status(checks),
        "checks": [asdict(c) for c in checks],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run APP session readiness checks for runtime infrastructure."
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Repository root override (defaults to discovered project root).",
    )
    parser.add_argument(
        "--with-preflight",
        action="store_true",
        help="Compose runtime readiness with existing tool pre-flight checks.",
    )
    parser.add_argument(
        "--motion-enabled",
        action="store_true",
        help="When composing preflight, include motion-pipeline readiness checks.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=None,
        help=(
            "Optional source bundle directory. When set and run-constants.yaml exists there, "
            "validates frozen run constants against the repo root."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path to write JSON report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero exit for warn status in addition to fail.",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print JSON report only (no human summary).",
    )
    args = parser.parse_args(argv)

    report = run_readiness(
        root=args.root,
        with_preflight=args.with_preflight,
        motion_enabled=args.motion_enabled,
        bundle_dir=args.bundle_dir,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json_only:
        print(json.dumps(report, indent=2))
    else:
        print(format_summary(report))

    if report["overall_status"] == "fail":
        return 1
    if args.strict and report["overall_status"] == "warn":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
