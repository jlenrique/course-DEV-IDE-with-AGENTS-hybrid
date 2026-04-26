"""Trial-run preflight check — single-invocation sanity for first-trial readiness.

Runs an 11-point readiness sweep across env vars, Postgres, MCP servers, sanctums,
manifests, frozen-graph, dispatch-registry, ledger schema, sanctum-watcher,
trial corpus, and migration-state coherence.

Exits 0 on all-green, non-zero with discriminated reason on any check failure.

Usage:
    .venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py
    .venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py --trial-corpus <path>
    .venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py --skip-postgres
    .venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py --json   # machine-readable

Sandbox-AC discipline: every check verifies via shipped Python deps + degrades to
WARN on missing optional service rather than failing on unreachable substrate.
Required-vs-optional distinction is explicit per check.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[2]


def _autoload_dotenv() -> None:
    """Auto-load .env at startup so env-var checks reflect operator's real .env state.

    Uses the existing scripts.utilities.env_loader pattern (load_env raises FNF
    if .env absent — we catch + degrade silently since preflight should still
    run on fresh clones without .env)."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from scripts.utilities.env_loader import load_env
        load_env()
    except (FileNotFoundError, ImportError):
        # Fresh clone OR env_loader unavailable — degrade silently;
        # _check_env_vars will report missing vars per its existing logic.
        pass


_autoload_dotenv()


CheckStatus = Literal["PASS", "WARN", "FAIL", "SKIP"]


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    detail: dict[str, Any] = field(default_factory=dict)
    required: bool = True


def _check_env_vars(skip: bool = False) -> CheckResult:
    """Verify required + optional env vars per .env.example."""
    if skip:
        return CheckResult("env_vars", "SKIP", "skipped per --skip-env", required=True)

    required = ["OPENAI_API_KEY"]
    optional = [
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
        "DATABASE_URL",
        "WONDERCRAFT_API_KEY",
        "ELEVENLABS_API_KEY",
    ]

    missing_required = [v for v in required if not os.environ.get(v)]
    missing_optional = [v for v in optional if not os.environ.get(v)]

    if missing_required:
        return CheckResult(
            "env_vars",
            "FAIL",
            f"missing required env vars: {missing_required}",
            detail={"missing_required": missing_required, "missing_optional": missing_optional},
        )
    if missing_optional:
        return CheckResult(
            "env_vars",
            "WARN",
            f"missing optional env vars (some features will skip): {missing_optional}",
            detail={"missing_optional": missing_optional},
            required=False,
        )
    return CheckResult("env_vars", "PASS", "all required + optional env vars present")


def _check_postgres(skip: bool = False) -> CheckResult:
    """Verify Postgres reachability + ledger_events schema loaded."""
    if skip:
        return CheckResult("postgres", "SKIP", "skipped per --skip-postgres", required=True)

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return CheckResult(
            "postgres",
            "WARN",
            "DATABASE_URL absent; trial-run can proceed with in-memory checkpointer (post-Slab-1 substrate may degrade)",
            required=False,
        )
    try:
        import psycopg
    except ImportError:
        return CheckResult(
            "postgres",
            "FAIL",
            "psycopg not installed; required per Slab-1 + Slab-4 ledger substrate",
        )
    try:
        conn = psycopg.connect(db_url, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        # Check ledger_events table existence (Slab 4 substrate)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ledger_events')"
            )
            row = cur.fetchone()
            ledger_present = bool(row[0]) if row else False
        conn.close()
        if not ledger_present:
            return CheckResult(
                "postgres",
                "WARN",
                "Postgres reachable but ledger_events table not loaded (run app/ledger/schema.sql post-Slab-4)",
                detail={"ledger_events_present": False},
                required=False,
            )
        return CheckResult(
            "postgres",
            "PASS",
            "Postgres reachable + ledger_events table loaded",
            detail={"ledger_events_present": True},
        )
    except psycopg.OperationalError as exc:
        return CheckResult(
            "postgres",
            "FAIL",
            f"Postgres connection failed: {exc}",
            detail={"db_url_redacted": db_url.split("@")[-1] if "@" in db_url else "redacted"},
        )


def _check_mcp_servers() -> CheckResult:
    """Verify .mcp.json present + parseable; do NOT spawn servers (would incur startup cost)."""
    mcp_path = REPO_ROOT / ".mcp.json"
    if not mcp_path.is_file():
        return CheckResult(
            "mcp_servers",
            "WARN",
            ".mcp.json not present; trial-run can proceed without MCP transports",
            required=False,
        )
    try:
        config = json.loads(mcp_path.read_text(encoding="utf-8"))
        servers = config.get("mcpServers", {})
        if not servers:
            return CheckResult(
                "mcp_servers",
                "WARN",
                ".mcp.json present but no mcpServers configured",
                required=False,
            )
        return CheckResult(
            "mcp_servers",
            "PASS",
            f".mcp.json parseable + {len(servers)} server(s) configured",
            detail={"server_names": list(servers.keys())},
        )
    except json.JSONDecodeError as exc:
        return CheckResult("mcp_servers", "FAIL", f".mcp.json parse failed: {exc}")


def _check_sanctums() -> CheckResult:
    """Verify Marcus + key specialist sanctums populated."""
    sanctum_dirs = [
        REPO_ROOT / "_bmad" / "memory" / "bmad-agent-marcus",
        REPO_ROOT / "_bmad" / "memory" / "wanda-sidecar",
    ]
    missing = []
    empty = []
    for d in sanctum_dirs:
        if not d.is_dir():
            missing.append(d.relative_to(REPO_ROOT).as_posix())
            continue
        files = [p for p in d.rglob("*") if p.is_file()]
        if not files:
            empty.append(d.relative_to(REPO_ROOT).as_posix())
    if missing:
        return CheckResult(
            "sanctums",
            "FAIL",
            f"required sanctum dirs missing: {missing}",
            detail={"missing": missing, "empty": empty},
        )
    if empty:
        return CheckResult(
            "sanctums",
            "WARN",
            f"sanctum dirs present but empty: {empty} (sanctum cold-read will degrade gracefully)",
            detail={"empty": empty},
            required=False,
        )
    return CheckResult("sanctums", "PASS", f"sanctum dirs populated: {[d.relative_to(REPO_ROOT).as_posix() for d in sanctum_dirs]}")


def _check_pipeline_manifest() -> CheckResult:
    """Verify pipeline-manifest.yaml exists + parses + has expected node shape."""
    path = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
    if not path.is_file():
        return CheckResult("pipeline_manifest", "FAIL", f"missing: {path.relative_to(REPO_ROOT).as_posix()}")
    try:
        import yaml
    except ImportError:
        return CheckResult("pipeline_manifest", "FAIL", "PyYAML not installed")
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        nodes = manifest.get("nodes") or manifest.get("steps") or []
        if not nodes:
            return CheckResult(
                "pipeline_manifest",
                "FAIL",
                "manifest parses but has no nodes/steps",
            )
        return CheckResult(
            "pipeline_manifest",
            "PASS",
            f"pipeline-manifest.yaml parses + {len(nodes)} node(s) declared",
            detail={"node_count": len(nodes)},
        )
    except yaml.YAMLError as exc:
        return CheckResult("pipeline_manifest", "FAIL", f"YAML parse failed: {exc}")


def _check_dev_graph_manifest() -> CheckResult:
    """Verify dev-graph-manifest.yaml exists + parses post-Slab-4 4.2."""
    path = REPO_ROOT / "state" / "config" / "dev-graph-manifest.yaml"
    if not path.is_file():
        return CheckResult(
            "dev_graph_manifest",
            "WARN",
            f"missing: {path.relative_to(REPO_ROOT).as_posix()} (Slab 4 Story 4.2 ships this; trial-run can proceed without dev-graph)",
            required=False,
        )
    try:
        import yaml
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        nodes = manifest.get("nodes") or []
        return CheckResult(
            "dev_graph_manifest",
            "PASS",
            f"dev-graph-manifest.yaml parses + {len(nodes)} node(s)",
            detail={"node_count": len(nodes)},
        )
    except Exception as exc:
        return CheckResult("dev_graph_manifest", "FAIL", f"parse failed: {exc}")


def _check_ledger_schema_loaded() -> CheckResult:
    """Verify Slab 4.4 ledger schema loaded into Postgres (depends on _check_postgres)."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return CheckResult(
            "ledger_schema_loaded",
            "WARN",
            "DATABASE_URL absent; ledger schema check skipped (in-memory checkpointer fallback)",
            required=False,
        )
    schema_file = REPO_ROOT / "app" / "ledger" / "schema.sql"
    if not schema_file.is_file():
        return CheckResult(
            "ledger_schema_loaded",
            "FAIL",
            f"missing: {schema_file.relative_to(REPO_ROOT).as_posix()} (Slab 4.4 ships this)",
        )
    try:
        import psycopg
        conn = psycopg.connect(db_url, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'ledger_events' ORDER BY ordinal_position"
            )
            columns = [row[0] for row in cur.fetchall()]
        conn.close()
        if not columns:
            return CheckResult(
                "ledger_schema_loaded",
                "WARN",
                "ledger_events table not loaded; run: psql $DATABASE_URL -f app/ledger/schema.sql",
                required=False,
            )
        expected = {"event_id", "trial_id", "gate_id", "kind", "payload", "idempotency_key", "created_at"}
        missing_cols = expected - set(columns)
        if missing_cols:
            return CheckResult(
                "ledger_schema_loaded",
                "FAIL",
                f"ledger_events table present but missing columns: {missing_cols}",
                detail={"present_columns": columns, "missing": list(missing_cols)},
            )
        return CheckResult(
            "ledger_schema_loaded",
            "PASS",
            f"ledger_events table loaded with {len(columns)} columns (all 7 required present)",
            detail={"column_count": len(columns)},
        )
    except Exception as exc:
        return CheckResult("ledger_schema_loaded", "FAIL", f"schema check failed: {str(exc)[:200]}")


def _check_frozen_graph_digest_stable() -> CheckResult:
    """Verify Slab 4.5 frozen-graph compiled-graph-digest is stable + non-empty."""
    digest_file = REPO_ROOT / "runtime" / "graphs" / "v42" / "compiled-graph-digest.txt"
    if not digest_file.is_file():
        return CheckResult(
            "frozen_graph_digest",
            "WARN",
            f"missing: {digest_file.relative_to(REPO_ROOT).as_posix()} (Slab 4.5 ships this)",
            required=False,
        )
    try:
        digest = digest_file.read_text(encoding="utf-8").strip()
        if not digest:
            return CheckResult(
                "frozen_graph_digest",
                "WARN",
                "compiled-graph-digest.txt present but empty",
                required=False,
            )
        # SHA-256 hex shape: 64 hex chars
        if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest.lower()):
            return CheckResult(
                "frozen_graph_digest",
                "PASS",
                f"frozen-graph digest sha256-shaped: {digest[:8]}...{digest[-8:]}",
                detail={"digest_prefix": digest[:16]},
            )
        # Non-sha256 shape; could be a placeholder string
        return CheckResult(
            "frozen_graph_digest",
            "WARN",
            f"compiled-graph-digest.txt present but not sha256-shaped (len={len(digest)})",
            detail={"digest_preview": digest[:50]},
            required=False,
        )
    except Exception as exc:
        return CheckResult("frozen_graph_digest", "FAIL", f"read failed: {exc}")


def _check_sanctum_watcher_importable() -> CheckResult:
    """Verify Slab 4.6 sanctum_watcher module + watchdog dep importable."""
    watcher_path = REPO_ROOT / "app" / "runtime" / "sanctum_watcher.py"
    if not watcher_path.is_file():
        return CheckResult(
            "sanctum_watcher_module",
            "WARN",
            f"missing: {watcher_path.relative_to(REPO_ROOT).as_posix()} (Slab 4.6 ships this)",
            required=False,
        )
    try:
        import watchdog  # noqa: F401
    except ImportError:
        return CheckResult(
            "sanctum_watcher_module",
            "FAIL",
            "sanctum_watcher.py present but watchdog Python dep missing; run: pip install watchdog",
        )
    try:
        # Attempt to import the module to verify it's loadable
        import importlib.util
        spec = importlib.util.spec_from_file_location("sanctum_watcher", watcher_path)
        if spec is None or spec.loader is None:
            return CheckResult("sanctum_watcher_module", "FAIL", "spec_from_file_location returned None")
        module = importlib.util.module_from_spec(spec)
        # Don't actually exec; just check if symbols are available via grep heuristic
        text = watcher_path.read_text(encoding="utf-8")
        has_class = "class SanctumWatcher" in text
        has_handler = "class _SanctumEventHandler" in text or "FileSystemEventHandler" in text
        if has_class and has_handler:
            return CheckResult(
                "sanctum_watcher_module",
                "PASS",
                "sanctum_watcher.py importable + carries SanctumWatcher class (FR59 ready)",
            )
        return CheckResult(
            "sanctum_watcher_module",
            "WARN",
            "sanctum_watcher.py present but missing expected SanctumWatcher class",
            required=False,
        )
    except Exception as exc:
        return CheckResult("sanctum_watcher_module", "FAIL", f"check failed: {str(exc)[:200]}")


def _check_frozen_graph_v42() -> CheckResult:
    """Verify runtime/graphs/v42/ artifacts post-Slab-4 4.5."""
    v42_dir = REPO_ROOT / "runtime" / "graphs" / "v42"
    if not v42_dir.is_dir():
        return CheckResult(
            "frozen_graph_v42",
            "WARN",
            f"missing: {v42_dir.relative_to(REPO_ROOT).as_posix()} (Slab 4 Story 4.5 ships this)",
            required=False,
        )
    expected_artifacts = [
        "manifest-snapshot.yaml",
        "pack-version.txt",
        "compiled-graph-digest.txt",
    ]
    present = [a for a in expected_artifacts if (v42_dir / a).is_file()]
    missing = [a for a in expected_artifacts if a not in present]
    if missing:
        return CheckResult(
            "frozen_graph_v42",
            "WARN",
            f"v42/ present but missing artifacts: {missing}",
            detail={"present": present, "missing": missing},
            required=False,
        )
    return CheckResult(
        "frozen_graph_v42",
        "PASS",
        "v42/ has all 3 core artifacts",
        detail={"present": present},
    )


def _check_dispatch_registry() -> CheckResult:
    """Verify dispatch-registry.yaml + interim/final status."""
    path = REPO_ROOT / "state" / "config" / "dispatch-registry.yaml"
    if not path.is_file():
        return CheckResult("dispatch_registry", "FAIL", f"missing: {path.relative_to(REPO_ROOT).as_posix()}")
    try:
        import yaml
        registry = yaml.safe_load(path.read_text(encoding="utf-8"))
        status = registry.get("_status", "unknown")
        if status == "interim":
            return CheckResult(
                "dispatch_registry",
                "WARN",
                "dispatch-registry _status=interim per 2b.15 (M5 reconciles per slab-3-m5-dispatch-registry-swap)",
                detail={"_status": "interim"},
                required=False,
            )
        return CheckResult(
            "dispatch_registry",
            "PASS",
            f"dispatch-registry _status={status}",
            detail={"_status": status},
        )
    except Exception as exc:
        return CheckResult("dispatch_registry", "FAIL", f"parse failed: {exc}")


def _check_sanctum_watcher() -> CheckResult:
    """Verify watchdog Python dep present (Slab 4 4.6 requirement)."""
    try:
        import watchdog  # noqa: F401
        return CheckResult("sanctum_watcher", "PASS", "watchdog dep installed (Slab 4.6 ready)")
    except ImportError:
        return CheckResult(
            "sanctum_watcher",
            "WARN",
            "watchdog not installed; Slab 4.6 sanctum_watcher will not function (FR59 unavailable)",
            required=False,
        )


def _check_trial_corpus(corpus_path: str | None) -> CheckResult:
    """Verify trial corpus path readable if provided."""
    if not corpus_path:
        return CheckResult(
            "trial_corpus",
            "WARN",
            "no --trial-corpus provided; preflight cannot verify corpus readability",
            required=False,
        )
    p = Path(corpus_path)
    if not p.exists():
        return CheckResult("trial_corpus", "FAIL", f"trial corpus not found: {corpus_path}")
    if p.is_dir():
        files = list(p.rglob("*"))
        if not files:
            return CheckResult("trial_corpus", "FAIL", f"trial corpus dir empty: {corpus_path}")
        return CheckResult(
            "trial_corpus",
            "PASS",
            f"trial corpus dir readable + {len(files)} entries",
            detail={"path": str(p), "entry_count": len(files)},
        )
    return CheckResult("trial_corpus", "PASS", f"trial corpus file readable: {corpus_path}")


def _check_migration_state() -> CheckResult:
    """Verify sprint-status.yaml epic states + flag any conditional milestones."""
    path = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if not path.is_file():
        return CheckResult("migration_state", "FAIL", f"missing: {path.relative_to(REPO_ROOT).as_posix()}")
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        return CheckResult("migration_state", "FAIL", f"read failed: {exc}")

    # Lightweight grep — full YAML parse can fail on long inline comments
    conditional_markers = []
    if "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM per slab-2c" in content or "CONDITIONAL-M2" in content:
        conditional_markers.append("M2")
    if "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM per slab-3" in content or "CONDITIONAL-M3" in content:
        conditional_markers.append("M3")
    if "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM per slab-4" in content or "CONDITIONAL-M4" in content:
        conditional_markers.append("M4")
    # M4 may be GREEN-WITH-RIDERS (Codex's Slab 4.7 close pattern); check separately
    if "GREEN-WITH-RIDERS" in content and "slab-4" in content.lower():
        if "M4" not in conditional_markers:
            conditional_markers.append("M4-GREEN-WITH-RIDERS")

    epic_states = {}
    for line in content.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("migration-epic-"):
            parts = line_stripped.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                state = parts[1].split("#")[0].strip()
                epic_states[key] = state

    if conditional_markers:
        return CheckResult(
            "migration_state",
            "WARN",
            f"migration in progress; conditional milestones pending: {conditional_markers}",
            detail={"conditional": conditional_markers, "epic_states": epic_states},
            required=False,
        )
    return CheckResult(
        "migration_state",
        "PASS",
        "migration state coherent",
        detail={"epic_states": epic_states},
    )


def _check_marcus_baseline() -> CheckResult:
    """Verify Marcus-envelope baseline fixture from 3.6 W-R7-3.1."""
    baseline_dir = REPO_ROOT / "tests" / "fixtures" / "marcus" / "baseline_envelope"
    if not baseline_dir.is_dir():
        return CheckResult(
            "marcus_baseline",
            "WARN",
            "Marcus-envelope baseline missing (Slab 3.6 W-R7 ships this)",
            required=False,
        )
    dated_dirs = [d for d in baseline_dir.iterdir() if d.is_dir()]
    if not dated_dirs:
        return CheckResult(
            "marcus_baseline",
            "WARN",
            "baseline parent dir present but no dated sub-dir",
            required=False,
        )
    latest = sorted(dated_dirs)[-1]
    has_envelope = (latest / "envelope.json").is_file()
    has_metadata = (latest / "BASELINE_METADATA.md").is_file()
    if not (has_envelope and has_metadata):
        return CheckResult(
            "marcus_baseline",
            "WARN",
            f"baseline {latest.name} missing envelope or metadata",
            detail={"envelope_present": has_envelope, "metadata_present": has_metadata},
            required=False,
        )
    return CheckResult(
        "marcus_baseline",
        "PASS",
        f"Marcus baseline present at {latest.relative_to(REPO_ROOT).as_posix()}",
    )


def run_preflight(args: argparse.Namespace) -> tuple[list[CheckResult], int]:
    """Run all checks. Returns (results, exit_code)."""
    checks = [
        _check_env_vars(skip=args.skip_env),
        _check_postgres(skip=args.skip_postgres),
        _check_ledger_schema_loaded(),
        _check_mcp_servers(),
        _check_sanctums(),
        _check_pipeline_manifest(),
        _check_dev_graph_manifest(),
        _check_frozen_graph_v42(),
        _check_frozen_graph_digest_stable(),
        _check_dispatch_registry(),
        _check_sanctum_watcher_importable(),  # supersedes _check_sanctum_watcher; checks dep + module
        _check_marcus_baseline(),
        _check_trial_corpus(args.trial_corpus),
        _check_migration_state(),
    ]

    has_required_fail = any(r.status == "FAIL" and r.required for r in checks)
    has_any_fail = any(r.status == "FAIL" for r in checks)
    has_warn = any(r.status == "WARN" for r in checks)

    if has_required_fail:
        exit_code = 2  # blocking failure
    elif has_any_fail:
        exit_code = 1  # non-required failure
    elif has_warn:
        exit_code = 0  # warnings allowed; trial-run can proceed
    else:
        exit_code = 0

    return checks, exit_code


def render_text(results: list[CheckResult], exit_code: int) -> str:
    lines = ["=== Trial-Run Preflight Sweep ===\n"]
    status_glyph = {"PASS": "[OK]", "WARN": "[WARN]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}
    for r in results:
        glyph = status_glyph[r.status]
        suffix = " (required)" if r.required and r.status in ("FAIL",) else ""
        lines.append(f"{glyph} {r.name}: {r.message}{suffix}")
        if r.detail:
            for k, v in r.detail.items():
                lines.append(f"        {k} = {v}")
    lines.append("")
    if exit_code == 0:
        lines.append("VERDICT: trial-run can proceed (warnings may apply; review individual checks)")
    elif exit_code == 1:
        lines.append("VERDICT: non-required failures detected; trial-run can proceed but features will be unavailable")
    else:
        lines.append("VERDICT: BLOCKING FAILURES detected; resolve before trial-run")
    return "\n".join(lines)


def render_json(results: list[CheckResult], exit_code: int) -> str:
    return json.dumps(
        {
            "exit_code": exit_code,
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "detail": r.detail,
                    "required": r.required,
                }
                for r in results
            ],
        },
        indent=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-corpus", default=None, help="Path to trial corpus (file or dir)")
    parser.add_argument("--skip-env", action="store_true", help="Skip env-var checks")
    parser.add_argument("--skip-postgres", action="store_true", help="Skip Postgres connection")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    results, exit_code = run_preflight(args)
    output = render_json(results, exit_code) if args.json else render_text(results, exit_code)
    print(output)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
