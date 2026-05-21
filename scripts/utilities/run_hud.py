"""Run HUD — Heads-Up Display for production runs and dev cycle tracking.

Generates an HTML dashboard that shows:
- Production run pipeline position and gate results
- Dev cycle progress (epics/stories from sprint-status.yaml)
- Critical constants, artifact status, and risk flags

Usage:
    .venv/Scripts/python -m scripts.utilities.run_hud
    .venv/Scripts/python -m scripts.utilities.run_hud --bundle-dir path/to/bundle
    .venv/Scripts/python -m scripts.utilities.run_hud --open

The HUD is a static snapshot. The output HTML includes a JS timer that
``location.reload()``s every 10 seconds, but that reload just re-serves
the same file — data only refreshes when this script runs again. The
snapshot banner at the top of the page states this explicitly so the
operator is never confused about freshness. The banner rendering also
retains a dormant ``watching=True`` path for a future re-enablement of
live-regeneration mode.
"""

from __future__ import annotations

import argparse
import html as html_mod
import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root
from scripts.utilities.hud_data_sources import (
    ActiveTrialView,
    AdhocSummaryView,
    CostEngineeringView,
    M5WindowView,
    read_active_trial,
    read_adhoc_summary,
    read_cost_engineering_state,
    read_m5_window_state,
)
from scripts.utilities.hud_per_step_summary import (
    StepSummary,
    SummaryArtifactIndex,
    derive_per_step_summaries,
    scan_bundle_summary_artifacts,
)
from scripts.utilities.pipeline_manifest import hud_steps, load_manifest
from scripts.utilities.progress_map import build_report as build_progress_report

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = project_root()
HUD_OUTPUT = ROOT / "reports" / "run-hud.html"
BUNDLES_DIR = ROOT / "course-content" / "staging" / "tracked" / "source-bundles"
SPRINT_STATUS = ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
COORDINATION_DB = ROOT / "state" / "runtime" / "coordination.db"

# Default poll interval retained for the dormant ``watching=True`` banner
# path; the watch loop that consumed it was reverted (commit 6268dc5
# follow-up) so this constant is currently inert outside render_html.
DEFAULT_WATCH_INTERVAL_SECONDS = 5.0

# ---------------------------------------------------------------------------
# Pipeline step definitions
# SYNC-WITH: state/config/pipeline-manifest.yaml
# ---------------------------------------------------------------------------

PIPELINE_STEPS: list[dict[str, str]] = hud_steps(load_manifest())


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def _find_latest_bundle(bundles_dir: Path) -> Path | None:
    """Find the most recently modified bundle directory."""
    if not bundles_dir.exists():
        return None
    bundles = sorted(
        [d for d in bundles_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    return bundles[0] if bundles else None


# ---------------------------------------------------------------------------
# Active-run bundle resolution
#
# The previous auto-detection strategy (mtime on the bundle directory) can
# pick up the wrong bundle at session start if a prior run's artifacts were
# modified more recently than the newly-created active run. The authoritative
# record of the active run is the coordination database's production_runs
# table, not mode_state.json (which only tracks default/ad-hoc mode state).
# ---------------------------------------------------------------------------


def _query_active_run_id(db_path: Path | None = None) -> str | None:
    """Return the run_id of the currently active/planning production run.

    Reads ``state/runtime/coordination.db`` in read-only mode. Selects the
    most recently updated row whose status is ``planning`` or ``active``.
    Returns ``None`` when the DB is missing, has no matching row, or cannot
    be queried (schema drift, IO error).
    """
    path = db_path or COORDINATION_DB
    if not path.exists():
        return None
    try:
        uri = f"file:{path.as_posix()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as conn:
            row = conn.execute(
                "SELECT run_id FROM production_runs "
                "WHERE status IN ('planning', 'active') "
                "ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
    except (sqlite3.DatabaseError, sqlite3.OperationalError):
        return None
    if not row:
        return None
    run_id = row[0]
    return run_id if isinstance(run_id, str) and run_id else None


def _bundle_run_id(bundle_dir: Path) -> str | None:
    """Extract the run_id declared in a bundle's run-constants.yaml.

    Accepts either canonical lowercase ``run_id`` or legacy uppercase
    ``RUN_ID`` for schema-drift tolerance. Returns ``None`` on missing
    file, malformed YAML, or missing field.
    """
    rc_path = bundle_dir / "run-constants.yaml"
    if not rc_path.exists():
        return None
    try:
        data = yaml.safe_load(rc_path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    candidate = data.get("run_id") or data.get("RUN_ID")
    return candidate if isinstance(candidate, str) and candidate else None


def _find_bundle_for_run_id(bundles_dir: Path, run_id: str) -> Path | None:
    """Return the bundle directory whose run-constants.yaml matches run_id."""
    if not bundles_dir.exists() or not run_id:
        return None
    for bundle in sorted(bundles_dir.iterdir()):
        if not bundle.is_dir():
            continue
        if _bundle_run_id(bundle) == run_id:
            return bundle
    return None


def _resolve_active_bundle(
    bundles_dir: Path,
    db_path: Path | None = None,
) -> Path | None:
    """Best bundle for the HUD: match the active run if possible, else mtime.

    Precedence:
      1. The bundle whose ``run-constants.yaml`` ``run_id`` matches the
         active row in the coordination database's ``production_runs``
         table.
      2. The most recently modified bundle directory (legacy heuristic).

    ``db_path`` is injectable for tests; production callers pass ``None``
    and the module-level ``COORDINATION_DB`` is used.
    """
    active_run_id = _query_active_run_id(db_path)
    if active_run_id:
        matched = _find_bundle_for_run_id(bundles_dir, active_run_id)
        if matched is not None:
            return matched
    return _find_latest_bundle(bundles_dir)


def _load_run_constants(bundle_dir: Path) -> dict[str, Any]:
    """Load run-constants.yaml from a bundle directory."""
    rc_path = bundle_dir / "run-constants.yaml"
    if not rc_path.exists():
        return {}
    with rc_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _load_gate_results(bundle_dir: Path) -> list[dict[str, Any]]:
    """Load all gate result sidecars from a bundle's gates/ directory."""
    gates_dir = bundle_dir / "gates"
    if not gates_dir.exists():
        return []
    results = []
    for gate_file in sorted(gates_dir.glob("gate-*-result.yaml")):
        try:
            with gate_file.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                results.append(data)
        except (yaml.YAMLError, OSError):
            continue
    return results


_MAX_ARTIFACTS = 200


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def _bundle_artifacts_listing(index: SummaryArtifactIndex) -> list[dict[str, str]]:
    """List files from the already-scanned summary artifact index."""
    artifacts = []
    for count, artifact in enumerate(
        sorted(index.by_relative_path.values(), key=lambda item: item.relative_path),
        start=1,
    ):
        if count > _MAX_ARTIFACTS:
            artifacts.append(
                {
                    "path": f"(+{count - _MAX_ARTIFACTS} more files not shown)",
                    "size": "",
                }
            )
            break
        artifacts.append(
            {
                "path": artifact.relative_path,
                "size": _format_size(artifact.size_bytes),
            }
        )
    return artifacts


def _build_pipeline_state(
    gate_results: list[dict[str, Any]],
    step_summaries: dict[str, StepSummary] | None = None,
) -> list[dict[str, Any]]:
    """Merge gate results into pipeline step definitions."""
    gate_by_id = {str(g.get("step_id", "")).upper(): g for g in gate_results}

    steps = []
    for step in PIPELINE_STEPS:
        sid = step["id"].upper()
        gate_data = gate_by_id.get(sid)
        merged = {
            "id": step["id"],
            "name": step["name"],
            "is_gate": step["gate"] == "yes",
            "result": gate_data.get("result", "not-started") if gate_data else "not-started",
            "summary": gate_data.get("summary", "") if gate_data else "",
            "timestamp": gate_data.get("timestamp", "") if gate_data else "",
            "duration": gate_data.get("duration_seconds", 0) if gate_data else 0,
            "metrics": gate_data.get("metrics", {}) if gate_data else {},
            "conditions": gate_data.get("conditions", []) if gate_data else [],
            "blockers": gate_data.get("blockers", []) if gate_data else [],
            "evidence": gate_data.get("evidence", "") if gate_data else "",
            "inputs": gate_data.get("inputs", []) if gate_data else [],
            "outputs": gate_data.get("outputs", []) if gate_data else [],
            "step_summary": step_summaries.get(step["id"]) if step_summaries else None,
        }
        steps.append(merged)
    return steps


def collect_hud_data(
    bundle_dir: Path | None = None,
    bundles_dir: Path | None = None,
    db_path: Path | None = None,
    trial_id: str | None = None,
    include_adhoc_panel: bool = True,
) -> dict[str, Any]:
    """Collect all data needed for the HUD rendering."""
    bdir = bundles_dir or BUNDLES_DIR

    if bundle_dir is None:
        bundle_dir = _resolve_active_bundle(bdir, db_path=db_path)

    run_constants: dict[str, Any] = {}
    gate_results: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    bundle_path = ""

    if bundle_dir and bundle_dir.exists():
        run_constants = _load_run_constants(bundle_dir)
        gate_results = _load_gate_results(bundle_dir)
        summary_artifacts = scan_bundle_summary_artifacts(bundle_dir)
        artifacts = _bundle_artifacts_listing(summary_artifacts)
        bundle_path = str(bundle_dir)
    else:
        summary_artifacts = SummaryArtifactIndex()

    manifest = load_manifest()
    step_summaries = derive_per_step_summaries(manifest, summary_artifacts)
    pipeline = _build_pipeline_state(gate_results, step_summaries=step_summaries)

    # Compute pipeline position
    current_step = 0
    for i, step in enumerate(pipeline):
        if step["result"] not in ("not-started",):
            current_step = i + 1

    # Count results
    passed = sum(1 for s in pipeline if s["result"] in ("pass", "conditional-pass"))
    failed = sum(1 for s in pipeline if s["result"] == "fail")
    pending = sum(1 for s in pipeline if s["result"] == "pending")
    warnings = sum(1 for s in pipeline if s["conditions"])

    # Dev cycle data from progress_map
    try:
        dev_report = build_progress_report()
    except Exception:  # noqa: BLE001 — dev panel is supplementary; never crash the HUD
        dev_report = None

    # Source freshness tracking
    now = datetime.now(tz=UTC).replace(microsecond=0)
    source_freshness: dict[str, str] = {}

    def _file_ts(p: Path, label: str) -> None:
        if p.exists():
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=UTC).replace(microsecond=0)
            source_freshness[label] = mtime.isoformat()

    _file_ts(SPRINT_STATUS, "sprint-status")
    if bundle_dir and bundle_dir.exists():
        _file_ts(bundle_dir / "run-constants.yaml", "run-constants")
        gates_dir = bundle_dir / "gates"
        if gates_dir.exists():
            gate_files = list(gates_dir.glob("gate-*-result.yaml"))
            if gate_files:
                newest = max(gate_files, key=lambda f: f.stat().st_mtime)
                _file_ts(newest, "gate-sidecars")

    active_trial = read_active_trial(trial_id)
    cost_engineering = read_cost_engineering_state()
    m5_window = read_m5_window_state()
    adhoc_summary = read_adhoc_summary() if include_adhoc_panel else None

    return {
        "generated": now.isoformat(),
        "bundle_path": bundle_path,
        "run_constants": run_constants,
        "pipeline": pipeline,
        "pipeline_summary": {
            "total_steps": len(pipeline),
            "current_step": current_step,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "warnings": warnings,
        },
        "artifacts": artifacts,
        "dev_report": dev_report,
        "source_freshness": source_freshness,
        "active_trial": active_trial,
        "cost_engineering": cost_engineering,
        "m5_window": m5_window,
        "adhoc_summary": adhoc_summary,
    }


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_STATUS_ICONS = {
    "pass": "&#x2705;",  # green check
    "conditional-pass": "&#x26A0;&#xFE0F;",  # warning
    "fail": "&#x274C;",  # red X
    "skip": "&#x23ED;&#xFE0F;",  # skip
    "pending": "&#x23F3;",  # hourglass
    "not-started": "&#x25CB;",  # open circle
}

_STATUS_CLASSES = {
    "pass": "status-pass",
    "conditional-pass": "status-warn",
    "fail": "status-fail",
    "skip": "status-skip",
    "pending": "status-pending",
    "not-started": "status-idle",
}


def _render_pipeline_step(step: dict[str, Any], is_current: bool) -> str:
    """Render a single pipeline step as HTML."""
    icon = _STATUS_ICONS.get(step["result"], "&#x25CB;")
    css = _STATUS_CLASSES.get(step["result"], "status-idle")
    current_cls = " step-current" if is_current else ""
    gate_badge = ' <span class="gate-badge">GATE</span>' if step["is_gate"] else ""

    detail_html = ""
    if step["summary"]:
        detail_html += f'<div class="step-summary">{_esc(step["summary"])}</div>'
    step_summary = step.get("step_summary")
    if isinstance(step_summary, StepSummary):
        urgent = is_current or bool(step["conditions"]) or bool(step["blockers"])
        open_attr = " open" if urgent else ""
        auto_open_attr = ' data-auto-open="urgent"' if urgent else ""
        fields = "".join(
            f"<li>{_esc(field)}</li>"
            for field in (step_summary.captured_fields or ("artifact_path",))
        )
        freshness = step_summary.freshness_timestamp or "n/a"
        detail_id = f"step-summary-{_esc(step['id']).replace('.', '-')}"
        detail_html += (
            f'<details id="{detail_id}" class="step-content-summary" '
            f'data-step-summary-id="{detail_id}"{auto_open_attr}{open_attr}>'
            f"<summary>{_esc(step_summary.title)}</summary>"
            f'<div class="step-content-summary-body">'
            f"<p>{_esc(step_summary.description)}</p>"
            f"<dl>"
            f"<dt>Artifact source</dt><dd>{_esc(step_summary.artifact_source)}</dd>"
            f"<dt>Freshness</dt><dd>{_esc(freshness)}</dd>"
            f"</dl>"
            f"<ul>{fields}</ul>"
            f"</div>"
            f"</details>"
        )
    if step["metrics"]:
        metrics_items = "".join(
            f"<li><strong>{_esc(k)}:</strong> {_esc(str(v))}</li>"
            for k, v in step["metrics"].items()
        )
        detail_html += f"<details><summary>Metrics</summary><ul>{metrics_items}</ul></details>"
    if step["conditions"]:
        cond_items = "".join(f"<li>{_esc(c)}</li>" for c in step["conditions"])
        detail_html += f'<details><summary>Conditions ({len(step["conditions"])})</summary><ul class="warn-list">{cond_items}</ul></details>'
    if step["blockers"]:
        block_items = "".join(f"<li>{_esc(b)}</li>" for b in step["blockers"])
        detail_html += f'<details open><summary>Blockers ({len(step["blockers"])})</summary><ul class="fail-list">{block_items}</ul></details>'
    if step["evidence"]:
        detail_html += f'<details><summary>Evidence</summary><pre class="evidence">{_esc(step["evidence"])}</pre></details>'
    if step["outputs"]:
        out_items = "".join(
            f"<li>{_esc(o['path'] if isinstance(o, dict) else str(o))}</li>"
            for o in step["outputs"]
        )
        detail_html += f"<details><summary>Outputs ({len(step['outputs'])})</summary><ul>{out_items}</ul></details>"

    dur = ""
    if step["duration"]:
        dur = f' <span class="duration">{step["duration"]}s</span>'

    return (
        f'<div class="step {css}{current_cls}">'
        f'<div class="step-header">'
        f'<span class="step-icon">{icon}</span>'
        f'<span class="step-id">{_esc(step["id"])}</span>'
        f'<span class="step-name">{_esc(step["name"])}{gate_badge}{dur}</span>'
        f"</div>"
        f"{detail_html}"
        f"</div>"
    )


def _render_dev_panel(dev_report: dict[str, Any] | None) -> str:
    """Render the dev cycle panel from progress_map data."""
    if not dev_report:
        return '<div class="panel-empty">Dev cycle data unavailable (sprint-status.yaml not found)</div>'

    s = dev_report.get("summary", {})
    pct = s.get("completion_pct", 0)
    bar_w = int(pct * 2)  # 200px max

    # Completed epics
    done_rows = ""
    for e in dev_report.get("completed_epics", []):
        done_rows += (
            f"<tr><td>&#x2705;</td><td>{_esc(e['id'])}</td>"
            f"<td>{_esc(e['label'])}</td><td>{e['stories']}</td></tr>"
        )

    # Active epics
    active_html = ""
    for ad in dev_report.get("you_are_here", {}).get("active_epics", []):
        c = ad.get("counts", {})
        total = sum(c.values())
        done = c.get("done", 0)
        epic_pct = round(done / total * 100) if total else 0
        bar = int(epic_pct * 1.5)  # 150px max

        details = ""
        if ad.get("in_progress"):
            details += f'<div class="epic-detail">In progress: {", ".join(ad["in_progress"])}</div>'
        if ad.get("ready_for_dev"):
            details += f'<div class="epic-detail">Ready: {", ".join(ad["ready_for_dev"])}</div>'
        if ad.get("deferred"):
            details += f'<div class="epic-detail dim">Deferred: {", ".join(ad["deferred"])}</div>'

        active_html += (
            f'<div class="active-epic">'
            f'<div class="epic-name">Epic {_esc(ad["epic_id"])}: {_esc(ad["label"])}</div>'
            f'<div class="progress-bar-container">'
            f'<div class="progress-bar-fill" style="width:{bar}px"></div>'
            f'<span class="progress-text">{done}/{total} ({epic_pct}%)</span>'
            f"</div>"
            f"{details}"
            f"</div>"
        )

    # Backlog epics
    backlog_rows = ""
    for e in dev_report.get("backlog_epics", []):
        backlog_rows += (
            f"<tr><td>&#x25CB;</td><td>{_esc(e['id'])}</td>"
            f"<td>{_esc(e['label'])}</td><td>{e['stories']}</td></tr>"
        )

    # Source health
    sh = dev_report.get("source_health", {})
    health_cls = (
        "health-clean"
        if sh.get("verdict") == "CLEAN"
        else ("health-warn" if sh.get("verdict") == "DEGRADED" else "health-fail")
    )
    health_items = ""
    for f in sh.get("findings", []):
        if f.get("level") != "ok":
            icon = "&#x26A0;&#xFE0F;" if f["level"] == "warn" else "&#x274C;"
            health_items += f'<div class="health-item">{icon} {_esc(f.get("message", ""))}</div>'

    # Risks
    risks_html = ""
    risks = dev_report.get("risks", "")
    if risks:
        risks_html = f'<div class="risks-content">{_esc(risks)}</div>'

    return f"""
    <div class="dev-overview">
      <div class="dev-bar">
        <div class="progress-bar-container wide">
          <div class="progress-bar-fill" style="width:{bar_w}px"></div>
          <span class="progress-text">{pct}% &mdash; {s.get("done_stories", 0)}/{s.get("total_stories", 0)} stories</span>
        </div>
        <div class="dev-counts">
          {s.get("done_epics", 0)} done / {s.get("active_epics", 0)} active / {s.get("backlog_epics", 0)} backlog epics
        </div>
      </div>
    </div>
    <div class="dev-section">
      <h3>Active Work</h3>
      {active_html or '<div class="dim">No active epics</div>'}
    </div>
    <details>
      <summary>Completed ({len(dev_report.get("completed_epics", []))} epics)</summary>
      <table class="epic-table"><thead><tr><th></th><th>ID</th><th>Epic</th><th>Stories</th></tr></thead>
      <tbody>{done_rows}</tbody></table>
    </details>
    <details>
      <summary>Backlog ({len(dev_report.get("backlog_epics", []))} epics)</summary>
      <table class="epic-table"><thead><tr><th></th><th>ID</th><th>Epic</th><th>Stories</th></tr></thead>
      <tbody>{backlog_rows}</tbody></table>
    </details>
    <details class="{health_cls}">
      <summary>Source Health: {sh.get("verdict", "UNKNOWN")}</summary>
      {health_items}
    </details>
    {"<details><summary>Risks / Unresolved</summary>" + risks_html + "</details>" if risks_html else ""}
    """


def _render_health_panel(
    pipeline: list[dict[str, Any]],
    dev_report: dict[str, Any] | None,
) -> str:
    """Render the System Health tab content."""
    sections = []

    # Preflight (step 01) — pulled from pipeline
    step_01 = next((s for s in pipeline if s["id"] == "01"), None)
    if step_01 and step_01["result"] != "not-started":
        icon = _STATUS_ICONS.get(step_01["result"], "&#x25CB;")
        css = _STATUS_CLASSES.get(step_01["result"], "status-idle")
        metrics_html = ""
        if step_01["metrics"]:
            for k, v in step_01["metrics"].items():
                val_str = _esc(str(v))
                check_icon = (
                    "&#x2705;"
                    if str(v).lower() in ("true", "connected", "pass", "ok")
                    else "&#x26A0;&#xFE0F;"
                )
                metrics_html += f'<div class="health-row">{check_icon} <strong>{_esc(k)}:</strong> {val_str}</div>'
        summary = step_01.get("summary", "")
        summary_html = f'<div class="step-summary">{_esc(summary)}</div>' if summary else ""
        timestamp = step_01.get("timestamp", "")
        timestamp_html = f'<div class="dim">Ran: {_esc(timestamp)}</div>' if timestamp else ""
        sections.append(
            f'<div class="health-section {css}">'
            f"<h4>{icon} Preflight</h4>"
            f"{summary_html}"
            f"{metrics_html}"
            f"{timestamp_html}"
            f"</div>"
        )
    else:
        sections.append(
            '<div class="health-section status-idle">'
            "<h4>&#x25CB; Preflight</h4>"
            '<div class="dim">Not yet run</div>'
            "</div>"
        )

    # Source health from dev report
    if dev_report:
        sh = dev_report.get("source_health", {})
        verdict = sh.get("verdict", "UNKNOWN")
        v_icon = {"CLEAN": "&#x2705;", "DEGRADED": "&#x26A0;&#xFE0F;", "FAIL": "&#x274C;"}.get(
            verdict, "&#x2753;"
        )
        v_cls = {"CLEAN": "status-pass", "DEGRADED": "status-warn", "FAIL": "status-fail"}.get(
            verdict, ""
        )
        items = ""
        for f in sh.get("findings", []):
            if f.get("level") == "ok":
                items += f'<div class="health-row">&#x2705; {_esc(f.get("check", ""))}: {_esc(f.get("message", ""))}</div>'
            elif f.get("level") == "warn":
                items += f'<div class="health-row">&#x26A0;&#xFE0F; {_esc(f.get("check", ""))}: {_esc(f.get("message", ""))}</div>'
            elif f.get("level") == "error":
                items += f'<div class="health-row">&#x274C; {_esc(f.get("check", ""))}: {_esc(f.get("message", ""))}</div>'
        sections.append(
            f'<div class="health-section {v_cls}">'
            f"<h4>{v_icon} Source Health: {_esc(verdict)}</h4>"
            f"<details><summary>Details ({sh.get('error_count', 0)} errors, {sh.get('warning_count', 0)} warnings)</summary>"
            f"{items}"
            f"</details>"
            f"</div>"
        )

    if not sections:
        return '<div class="panel-empty">No health data available</div>'

    # Overall readiness badge
    has_fail = any("status-fail" in s for s in sections)
    has_warn = any("status-warn" in s for s in sections)
    if has_fail:
        badge = '<span class="badge badge-fail">BLOCKED</span>'
    elif has_warn:
        badge = '<span class="badge badge-warn">DEGRADED</span>'
    else:
        badge = '<span class="badge badge-pass">READY</span>'

    return f'<div class="readiness-badge">{badge}</div>' + "\n".join(sections)


def _render_active_trial_panel(view: ActiveTrialView | None) -> str:
    if view is None:
        return (
            '<section class="runtime-panel">'
            "<h3>Active Trial</h3>"
            '<div class="panel-empty">No migrated-runtime trial found under state/config/runs.</div>'
            "</section>"
        )
    cost_rows = "".join(
        f"<tr><td>{_esc(agent)}</td><td>${cost:.6f}</td></tr>"
        for agent, cost in view.per_agent_cost.items()
    )
    trace = (
        f'<a href="{_esc(view.langsmith_trace_url)}">{_esc(view.langsmith_trace_url)}</a>'
        if view.langsmith_trace_url
        else '<span class="dim">unavailable</span>'
    )
    alerts = "".join(f"<li>{_esc(alert)}</li>" for alert in view.drift_alerts_last_24h)
    return f"""
    <section class="runtime-panel">
      <h3>Active Trial</h3>
      <div class="runtime-grid">
        <div><strong>Trial</strong><span>{_esc(view.trial_id)}</span></div>
        <div><strong>Status</strong><span class="badge badge-idle">{_esc(view.status)}</span></div>
        <div><strong>Step</strong><span>{_esc(view.current_step)}</span></div>
        <div><strong>Agent / Model</strong><span>{_esc(view.current_agent)} / {_esc(view.current_model)}</span></div>
      </div>
      <details open><summary>Per-agent cost</summary>
        <table class="kv-table"><tbody>{cost_rows or '<tr><td colspan="2">No cost report yet</td></tr>'}</tbody></table>
      </details>
      <div class="health-row"><strong>LangSmith:</strong> {trace}</div>
      <details><summary>Drift alerts last 24h ({len(view.drift_alerts_last_24h)})</summary>
        <ul>{alerts or "<li>No drift alerts</li>"}</ul>
      </details>
    </section>
    """


def _render_cost_engineering_panel(view: CostEngineeringView) -> str:
    cascade_rows = "".join(
        f"<tr><td>{_esc(agent)}</td><td>{_esc(model)}</td></tr>"
        for agent, model in view.cascade_preview.items()
    )
    price_rows = "".join(
        f"<tr><td>{_esc(model)}</td><td>${row['input']:.2f}</td><td>${row['output']:.2f}</td></tr>"
        for model, row in view.pricing_preview.items()
    )
    median_cost = (
        f"${view.median_trial_cost_last_5:.6f}"
        if view.median_trial_cost_last_5 is not None
        else "n/a"
    )
    budget = (
        f"${view.soft_cap_budget_usd:.2f}" if view.soft_cap_budget_usd is not None else "not set"
    )
    return f"""
    <section class="runtime-panel">
      <h3>Cost Engineering</h3>
      <div class="runtime-grid">
        <div><strong>Median trial cost</strong><span>{median_cost}</span></div>
        <div><strong>Soft cap</strong><span>{_esc(budget)}</span></div>
      </div>
      <details open><summary>Cascade preview ({len(view.cascade_preview)})</summary>
        <table class="kv-table"><tbody>{cascade_rows}</tbody></table>
      </details>
      <details><summary>Pricing table</summary>
        <table><thead><tr><th>Model</th><th>Input / 1M</th><th>Output / 1M</th></tr></thead><tbody>{price_rows}</tbody></table>
      </details>
    </section>
    """


def _render_m5_window_panel(view: M5WindowView) -> str:
    if not view.visible:
        return ""
    rows = "".join(
        f"<tr><td>{_esc(item['condition'])}</td><td>{_esc(item['status'])}</td></tr>"
        for item in view.open_conditions
    )
    return f"""
    <section class="runtime-panel">
      <h3>M5 Conditional Window</h3>
      <div class="runtime-grid">
        <div><strong>Days remaining</strong><span>{view.days_remaining}</span></div>
        <div><strong>Demotion threshold</strong><span>{_esc(view.demotion_threshold)}</span></div>
      </div>
      <table class="kv-table"><tbody>{rows}</tbody></table>
    </section>
    """


def _render_adhoc_panel(view: AdhocSummaryView | None) -> str:
    if view is None:
        return ""
    cost = (
        f"${view.total_cost_last_24h:.6f}"
        if view.total_cost_last_24h is not None
        else "inline-only"
    )
    return f"""
    <section class="runtime-panel">
      <h3>Ad-hoc Mode</h3>
      <div class="runtime-grid">
        <div><strong>Runs last 24h</strong><span>{view.run_count_last_24h}</span></div>
        <div><strong>Cost last 24h</strong><span>{_esc(cost)}</span></div>
      </div>
      <pre class="evidence">python -m app.marcus.cli ask "summarize this lesson outline" --max-tokens 500</pre>
      <div class="dim">{_esc(view.note)}</div>
    </section>
    """


def _esc(text: str) -> str:
    """Escape HTML special characters using stdlib html.escape."""
    return html_mod.escape(text, quote=True)


def _render_snapshot_banner(
    generated_iso: str,
    watching: bool,
    watch_interval_seconds: float,
) -> str:
    """Render the top-of-page banner describing data freshness.

    The banner is the single source of operator-facing truth about whether
    the HUD is a static snapshot or a live watch-mode view. The browser's
    JS auto-reload only refreshes data if the file on disk has been
    rewritten, so operators need explicit guidance about which mode is
    active.
    """
    try:
        generated_dt = datetime.fromisoformat(generated_iso)
        generated_human = generated_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        generated_human = generated_iso

    if watching:
        mode_class = "banner-live"
        mode_icon = "&#x1F7E2;"  # green circle
        mode_label = "Live"
        detail = (
            f"Watching manifest, sprint-status, mode-state, and active bundle "
            f"every {watch_interval_seconds:g}s. Regenerates on change."
        )
    else:
        mode_class = "banner-static"
        mode_icon = "&#x23F8;&#xFE0F;"  # pause
        mode_label = "Static snapshot"
        detail = (
            "Browser auto-reload re-serves this file; data only refreshes "
            "when the file on disk is rewritten. Re-run "
            "<code>python -m scripts.utilities.run_hud</code> to regenerate, "
            "or launch with <code>--watch</code> for live updates."
        )

    return (
        f'<div class="snapshot-banner {mode_class}">'
        f'<span class="banner-icon">{mode_icon}</span>'
        f'<span class="banner-label">{mode_label}</span>'
        f'<span class="banner-timestamp">Generated: {_esc(generated_human)}</span>'
        f'<span class="banner-detail">{detail}</span>'
        f"</div>"
    )


def render_html(
    data: dict[str, Any],
    *,
    watching: bool = False,
    watch_interval_seconds: float = DEFAULT_WATCH_INTERVAL_SECONDS,
) -> str:
    """Render the full HUD HTML page.

    ``watching`` and ``watch_interval_seconds`` drive the snapshot banner
    so operators can tell at a glance whether the view is live or frozen.
    """
    rc = data["run_constants"]
    ps = data["pipeline_summary"]
    pipeline = data["pipeline"]
    banner_html = _render_snapshot_banner(
        data.get("generated", ""),
        watching=watching,
        watch_interval_seconds=watch_interval_seconds,
    )

    active_trial = data.get("active_trial")
    if active_trial is not None:
        run_id = (
            f"{active_trial.trial_id[:8]} ({active_trial.status})"
        )
    else:
        run_id = rc.get("RUN_ID", "No active run")
    profile = rc.get("EXPERIENCE_PROFILE", "—")
    source = rc.get("PRIMARY_SOURCE_FILE", "—")
    bundle = data["bundle_path"] or "—"
    pct = round(ps["current_step"] / ps["total_steps"] * 100) if ps["total_steps"] else 0
    int(pct * 2)

    # Header status badges
    header_cls = ""
    if ps["failed"] > 0:
        header_cls = "header-fail"
    elif ps["warnings"] > 0:
        header_cls = "header-warn"

    # Pipeline steps HTML
    steps_html = ""
    for i, step in enumerate(pipeline):
        is_current = (i + 1) == ps["current_step"]
        steps_html += _render_pipeline_step(step, is_current)

    # Artifacts
    artifacts_html = ""
    for a in data["artifacts"]:
        artifacts_html += f"<tr><td>{_esc(a['path'])}</td><td>{_esc(a['size'])}</td></tr>"

    # Run constants display
    rc_html = ""
    for k, v in rc.items():
        rc_html += f"<tr><td>{_esc(str(k))}</td><td>{_esc(str(v))}</td></tr>"

    # Dev panel
    dev_html = _render_dev_panel(data.get("dev_report"))

    # System health panel — preflight step + source health
    health_html = _render_health_panel(pipeline, data.get("dev_report"))
    runtime_html = (
        _render_active_trial_panel(data.get("active_trial"))
        + _render_cost_engineering_panel(data["cost_engineering"])
        + _render_m5_window_panel(data["m5_window"])
        + _render_adhoc_panel(data.get("adhoc_summary"))
    )

    # Freshness bar
    freshness = data.get("source_freshness", {})
    freshness_items = ""
    max_age = 0
    for src_name, ts in freshness.items():
        if ts:
            try:
                age = (datetime.now(tz=UTC) - datetime.fromisoformat(ts)).total_seconds()
            except (ValueError, TypeError):
                age = 9999
            age_str = f"{int(age)}s ago" if age < 120 else f"{int(age / 60)}m ago"
            age_cls = "fresh" if age < 60 else ("stale-warn" if age < 300 else "stale-bad")
            freshness_items += (
                f'<span class="freshness-src {age_cls}">{_esc(src_name)}: {age_str}</span>'
            )
            max_age = max(max_age, age)
    freshness_cls = "fresh" if max_age < 60 else ("stale-warn" if max_age < 300 else "stale-bad")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HUD &mdash; {_esc(run_id)}</title>
<style>
{_CSS}
</style>
</head>
<body>

<div class="refresh-bar" id="refreshBar"></div>

{banner_html}

<div class="freshness-meter {freshness_cls}">
  <span class="freshness-label">Data freshness:</span>
  {freshness_items or '<span class="freshness-src dim">no sources tracked</span>'}
  <span class="freshness-countdown dim">Next refresh: <span id="countdown">10</span>s</span>
</div>

<header class="{header_cls}">
  <div class="header-top">
    <h1>HUD</h1>
    <div class="tab-bar">
      <button class="tab active" data-tab="health" onclick="switchTab('health')">System Health</button>
      <button class="tab" data-tab="production" onclick="switchTab('production')">Production Run</button>
      <button class="tab" data-tab="dev" onclick="switchTab('dev')">Dev Cycle</button>
    </div>
    <button class="panel-show" id="panelShow" onclick="togglePanel()" title="Show Run Context">&#x25C0; Context</button>
  </div>
  <div class="header-meta">
    <span class="meta-item"><strong>Run:</strong> {_esc(run_id)}</span>
    <span class="meta-item"><strong>Profile:</strong> {_esc(profile)}</span>
    <span class="meta-item"><strong>Source:</strong> {_esc(str(source).split("/")[-1] if source != "—" else "—")}</span>
  </div>
</header>

<div class="hud-body">
  <div class="main-content">

    <div id="tab-health" class="tab-content active">
      {health_html}
      {runtime_html}
    </div>

    <div id="tab-production" class="tab-content">
      <div class="pipeline-overview">
        <div class="progress-bar-container wide">
          <div class="progress-bar-fill" style="width:{pct}%"></div>
          <span class="progress-text">Step {ps["current_step"]} / {ps["total_steps"]} ({pct}%)</span>
        </div>
        <div class="status-badges">
          <span class="badge badge-pass">{ps["passed"]} passed</span>
          {"<span class='badge badge-fail'>" + str(ps["failed"]) + " FAILED</span>" if ps["failed"] else ""}
          {"<span class='badge badge-warn'>" + str(ps["warnings"]) + " warnings</span>" if ps["warnings"] else ""}
          <span class="badge badge-idle">{ps["total_steps"] - ps["current_step"]} remaining</span>
        </div>
      </div>

      <div class="pipeline-steps">
        {steps_html}
      </div>
    </div>

    <div id="tab-dev" class="tab-content">
      {dev_html}
    </div>

  </div>

  <aside class="run-context" id="runContext">
    <h3>Run Context <button class="panel-toggle" onclick="togglePanel()" title="Hide panel">&#x2715;</button></h3>
    <div class="context-section">
      <h4>Constants ({len(rc)})</h4>
      <table class="kv-table">
      <tbody>{rc_html}</tbody></table>
    </div>
    <div class="context-section">
      <h4>Bundle</h4>
      <div class="bundle-path">{_esc(bundle)}</div>
    </div>
    <details>
      <summary>Artifacts ({len(data["artifacts"])} files)</summary>
      <table class="kv-table">
      <tbody>{artifacts_html}</tbody></table>
    </details>
  </aside>
</div>

<script>
{_JS}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #0f172a; color: #e2e8f0; line-height: 1.5;
  max-width: 1200px; margin: 0 auto; padding: 8px 16px;
}
.hud-body {
  display: grid; grid-template-columns: 1fr 280px; gap: 16px;
}
@media (max-width: 900px) {
  .hud-body { grid-template-columns: 1fr; }
  .run-context { order: -1; }
}
.main-content { min-width: 0; overflow: hidden; }
aside.run-context {
  background: #1a2332; border-radius: 6px; padding: 10px;
  position: sticky; top: 8px; max-height: calc(100vh - 16px);
  overflow-y: auto; overflow-x: hidden; font-size: 0.78rem;
  border: 1px solid #1e293b;
  width: 280px; min-width: 280px; max-width: 280px;
}
aside.run-context table { table-layout: fixed; width: 100%; }
aside.run-context td { word-break: break-all; overflow: hidden; text-overflow: ellipsis; }
aside.run-context h3 { color: #38bdf8; font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
.panel-toggle {
  background: none; border: none; color: #64748b; cursor: pointer;
  font-size: 0.8rem; padding: 2px 6px; border-radius: 3px;
}
.panel-toggle:hover { background: #334155; color: #e2e8f0; }
.panel-show {
  display: none; background: #1e293b; border: 1px solid #334155;
  color: #94a3b8; cursor: pointer; font-size: 0.7rem;
  padding: 3px 8px; border-radius: 4px; margin-left: auto;
}
.panel-show:hover { background: #334155; color: #e2e8f0; }
.hud-body.panel-hidden { grid-template-columns: 1fr; }
.hud-body.panel-hidden .run-context { display: none; }
.hud-body.panel-hidden ~ .panel-show,
body:has(.panel-hidden) .panel-show { display: inline-block; }
aside.run-context h4 { color: #94a3b8; font-size: 0.75rem; margin: 8px 0 4px; }
.context-section { margin-bottom: 8px; }
h1 { font-size: 1.1rem; font-weight: 700; color: #38bdf8; }
h3 { font-size: 0.95rem; margin: 12px 0 6px; color: #94a3b8; }

.refresh-bar {
  position: fixed; top: 0; left: 0; height: 2px;
  background: #38bdf8; width: 0; z-index: 999;
  transition: width linear;
}

.snapshot-banner {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  padding: 6px 10px; font-size: 0.78rem;
  background: #1e293b; border-bottom: 1px solid #334155;
  border-left: 3px solid transparent; margin-bottom: 4px;
}
.snapshot-banner.banner-live { border-left-color: #22c55e; background: #052e16; }
.snapshot-banner.banner-static { border-left-color: #eab308; background: #1c1917; }
.snapshot-banner .banner-icon { font-size: 0.9rem; }
.snapshot-banner .banner-label {
  font-weight: 700; color: #f1f5f9; min-width: 120px;
}
.snapshot-banner .banner-timestamp { color: #cbd5e1; }
.snapshot-banner .banner-detail { color: #94a3b8; flex: 1 1 auto; min-width: 260px; }
.snapshot-banner code {
  background: #0f172a; color: #e2e8f0; padding: 1px 5px;
  border-radius: 3px; font-size: 0.72rem;
}

.freshness-meter {
  display: flex; align-items: center; gap: 12px;
  padding: 4px 8px; font-size: 0.7rem; color: #64748b;
  background: #0c1322; border-bottom: 1px solid #1e293b; margin-bottom: 4px;
}
.freshness-meter.stale-warn { border-bottom-color: #eab308; }
.freshness-meter.stale-bad { border-bottom-color: #ef4444; }
.freshness-label { font-weight: 600; color: #94a3b8; }
.freshness-src { padding: 1px 6px; border-radius: 3px; background: #1e293b; }
.freshness-src.fresh { color: #4ade80; }
.freshness-src.stale-warn { color: #fde047; background: #422006; }
.freshness-src.stale-bad { color: #fca5a5; background: #450a0a; }
.freshness-countdown { margin-left: auto; }

.health-section {
  padding: 8px 10px; margin: 4px 0; border-radius: 4px;
  background: #1e293b; border-left: 3px solid transparent;
}
.health-section h4 { font-size: 0.85rem; margin-bottom: 4px; }
.health-row { font-size: 0.78rem; padding: 2px 0 2px 4px; }
.readiness-badge { margin-bottom: 8px; }
.runtime-panel {
  padding: 10px; margin: 10px 0; border-radius: 4px;
  background: #111827; border: 1px solid #253244;
}
.runtime-panel h3 { color: #cbd5e1; margin-top: 0; }
.runtime-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px; margin: 6px 0 8px;
}
.runtime-grid > div {
  background: #0f172a; border: 1px solid #1e293b; border-radius: 4px;
  padding: 6px 8px; min-width: 0;
}
.runtime-grid strong {
  display: block; color: #94a3b8; font-size: 0.68rem;
  text-transform: uppercase; letter-spacing: 0;
}
.runtime-grid span { display: block; color: #e2e8f0; font-size: 0.78rem; overflow-wrap: anywhere; }
.runtime-panel a { color: #7dd3fc; overflow-wrap: anywhere; }

header {
  padding: 8px 0; border-bottom: 1px solid #1e293b; margin-bottom: 12px;
}
header.header-fail { border-bottom: 2px solid #ef4444; }
header.header-warn { border-bottom: 2px solid #eab308; }
.header-top { display: flex; align-items: center; gap: 16px; }
.header-meta { display: flex; gap: 16px; margin-top: 6px; font-size: 0.8rem; }
.meta-item { color: #94a3b8; }
.meta-item strong { color: #cbd5e1; }
.refresh-info { margin-left: auto; font-size: 0.7rem; color: #64748b; text-align: right; }

.tab-bar { display: flex; gap: 4px; }
.tab {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
}
.tab.active { background: #334155; color: #e2e8f0; border-color: #475569; }
.tab:hover { background: #334155; }
.tab-content { display: none; }
.tab-content.active { display: block; }

.pipeline-overview { margin-bottom: 12px; }
.progress-bar-container {
  background: #1e293b; border-radius: 4px; height: 20px;
  position: relative; overflow: hidden;
}
.progress-bar-container.wide { width: 200px; display: inline-block; vertical-align: middle; }
.progress-bar-fill {
  background: linear-gradient(90deg, #22c55e, #38bdf8);
  height: 100%; border-radius: 4px; transition: width 0.3s;
}
.progress-text {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 0.7rem; font-weight: 600; color: #f1f5f9; white-space: nowrap;
}

.status-badges { margin-top: 6px; display: flex; gap: 6px; }
.badge {
  font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 600;
}
.badge-pass { background: #14532d; color: #4ade80; }
.badge-fail { background: #7f1d1d; color: #fca5a5; }
.badge-warn { background: #713f12; color: #fde047; }
.badge-idle { background: #1e293b; color: #64748b; }

.pipeline-steps { display: flex; flex-direction: column; gap: 2px; }
.step {
  padding: 6px 10px; border-radius: 4px; border-left: 3px solid transparent;
  background: #1e293b; font-size: 0.82rem;
}
.step-header { display: flex; align-items: center; gap: 8px; }
.step-icon { font-size: 0.9rem; min-width: 20px; text-align: center; }
.step-id { font-weight: 700; color: #64748b; min-width: 32px; font-size: 0.75rem; }
.step-name { flex: 1; }
.gate-badge {
  font-size: 0.6rem; background: #312e81; color: #a5b4fc; padding: 1px 4px;
  border-radius: 3px; margin-left: 6px; font-weight: 700;
}
.duration { font-size: 0.7rem; color: #64748b; }

.step-current { border-left-color: #38bdf8; background: #172554; }
.status-pass { border-left-color: #22c55e; }
.status-warn { border-left-color: #eab308; }
.status-fail { border-left-color: #ef4444; background: #1c1917; }
.status-pending { border-left-color: #3b82f6; }

.step-summary { font-size: 0.75rem; color: #94a3b8; margin: 4px 0 2px 28px; }

details { margin: 4px 0; font-size: 0.8rem; }
details summary {
  cursor: pointer; padding: 4px 8px; background: #1e293b;
  border-radius: 4px; color: #94a3b8; font-weight: 600;
}
details summary:hover { background: #334155; }
details > ul, details > pre, details > table, details > div {
  padding: 6px 12px; background: #0f172a;
}
.step-content-summary-body p { margin-bottom: 6px; color: #cbd5e1; }
.step-content-summary-body dl {
  display: grid; grid-template-columns: 110px 1fr; gap: 3px 8px;
  font-size: 0.74rem; margin-bottom: 6px;
}
.step-content-summary-body dt { color: #94a3b8; font-weight: 700; }
.step-content-summary-body dd { color: #cbd5e1; overflow-wrap: anywhere; }
ul { list-style: none; padding-left: 12px; }
li::before { content: "\\2022"; color: #475569; margin-right: 6px; }
.warn-list li::before { content: "\\26A0"; color: #eab308; }
.fail-list li::before { content: "\\274C"; color: #ef4444; }

.evidence { white-space: pre-wrap; font-size: 0.75rem; color: #94a3b8; max-height: 200px; overflow-y: auto; }

table { width: 100%; border-collapse: collapse; margin: 4px 0; }
th, td { text-align: left; padding: 3px 8px; font-size: 0.75rem; }
th { color: #64748b; border-bottom: 1px solid #334155; }
td { color: #cbd5e1; border-bottom: 1px solid #1e293b; }
.kv-table td:first-child { color: #94a3b8; font-weight: 600; white-space: nowrap; }
.epic-table td:first-child { width: 24px; text-align: center; }

.bundle-path { font-size: 0.7rem; color: #64748b; padding: 4px 8px; font-family: monospace; }

.dev-overview { margin-bottom: 8px; }
.dev-bar { display: flex; align-items: center; gap: 12px; }
.dev-counts { font-size: 0.75rem; color: #64748b; }
.active-epic { padding: 6px 10px; margin: 4px 0; background: #1e293b; border-radius: 4px; }
.epic-name { font-weight: 600; font-size: 0.82rem; }
.epic-detail { font-size: 0.75rem; color: #94a3b8; margin-left: 8px; }
.dim { color: #475569; }
.panel-empty { padding: 20px; text-align: center; color: #475569; }

.health-clean summary { color: #22c55e; }
.health-warn summary { color: #eab308; }
.health-fail summary { color: #ef4444; }
.health-item { padding: 2px 8px; font-size: 0.75rem; }

.risks-content { white-space: pre-wrap; font-size: 0.75rem; color: #94a3b8; padding: 6px 8px; }
"""

# ---------------------------------------------------------------------------
# JavaScript (scroll preservation + tab switching + refresh bar)
# ---------------------------------------------------------------------------

_JS = """
function togglePanel() {
  var body = document.querySelector('.hud-body');
  var btn = document.getElementById('panelShow');
  if (body.classList.contains('panel-hidden')) {
    body.classList.remove('panel-hidden');
    if (btn) btn.style.display = 'none';
    sessionStorage.setItem('hud_panel', 'visible');
  } else {
    body.classList.add('panel-hidden');
    if (btn) btn.style.display = 'inline-block';
    sessionStorage.setItem('hud_panel', 'hidden');
  }
}

function switchTab(name, noSave) {
  document.querySelectorAll('.tab-content').forEach(function(el) {
    el.classList.remove('active');
  });
  document.querySelectorAll('.tab').forEach(function(el) {
    el.classList.remove('active');
  });
  var target = document.getElementById('tab-' + name);
  if (target) target.classList.add('active');
  document.querySelectorAll('.tab').forEach(function(el) {
    if (el.getAttribute('data-tab') === name) el.classList.add('active');
  });
  if (!noSave) sessionStorage.setItem('hud_tab', name);
}

document.addEventListener('DOMContentLoaded', function() {
  var REFRESH_SECONDS = 10;

  // Restore scroll position
  var savedScroll = sessionStorage.getItem('hud_scroll');
  if (savedScroll) window.scrollTo(0, parseInt(savedScroll));

  // Restore active tab
  var savedTab = sessionStorage.getItem('hud_tab');
  if (savedTab) switchTab(savedTab, true);

  // Restore panel visibility
  var savedPanel = sessionStorage.getItem('hud_panel');
  if (savedPanel === 'hidden') togglePanel();

  // Restore expanded details
  var savedDetails = {};
  try {
    savedDetails = JSON.parse(sessionStorage.getItem('hud_details') || '{}');
  } catch (err) {
    console.warn('Ignoring corrupt hud_details sessionStorage', err);
  }
  document.querySelectorAll('details').forEach(function(el, i) {
    var key = el.getAttribute('data-step-summary-id') || el.id || String(i);
    if (el.getAttribute('data-auto-open') === 'urgent') {
      el.open = true;
      return;
    }
    if (savedDetails[key] !== undefined) el.open = savedDetails[key];
  });

  // Animate refresh bar
  var bar = document.getElementById('refreshBar');
  if (bar) {
    bar.style.transition = 'width ' + REFRESH_SECONDS + 's linear';
    setTimeout(function() { bar.style.width = '100vw'; }, 50);
  }

  // Countdown timer
  var remaining = REFRESH_SECONDS;
  var cdEl = document.getElementById('countdown');
  if (cdEl) {
    var cdInterval = setInterval(function() {
      remaining--;
      if (cdEl) cdEl.textContent = remaining;
      if (remaining <= 0) clearInterval(cdInterval);
    }, 1000);
  }

  // Schedule refresh with state save
  setTimeout(function() {
    sessionStorage.setItem('hud_scroll', window.scrollY);
    var activeTab = document.querySelector('.tab-content.active');
    if (activeTab) sessionStorage.setItem('hud_tab', activeTab.id.replace('tab-',''));
    var details = {};
    document.querySelectorAll('details').forEach(function(el, i) {
      var key = el.getAttribute('data-step-summary-id') || el.id || String(i);
      details[key] = el.open;
    });
    sessionStorage.setItem('hud_details', JSON.stringify(details));
    location.reload();
  }, REFRESH_SECONDS * 1000);
});
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _write_snapshot(
    *,
    bundle_dir: Path | None,
    output_path: Path,
    trial_id: str | None,
    include_adhoc_panel: bool,
    watching: bool,
    watch_interval_seconds: float,
) -> None:
    data = collect_hud_data(
        bundle_dir=bundle_dir,
        trial_id=trial_id,
        include_adhoc_panel=include_adhoc_panel,
    )
    html = render_html(
        data,
        watching=watching,
        watch_interval_seconds=watch_interval_seconds,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run HUD: Heads-Up Display for production runs and dev tracking."
    )
    parser.add_argument(
        "--bundle-dir",
        type=str,
        default=None,
        help="Path to a specific source bundle directory. Auto-detects latest if omitted.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output HTML file path. Defaults to reports/run-hud.html.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated HTML in the default browser.",
    )
    parser.add_argument(
        "--trial-id",
        type=str,
        default=None,
        help="Read migrated-runtime trial state for a specific trial id.",
    )
    parser.add_argument(
        "--watch",
        type=float,
        nargs="?",
        const=30.0,
        default=None,
        metavar="SECONDS",
        help="Regenerate the HUD every N seconds (default 30).",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--no-adhoc-panel",
        action="store_true",
        help="Hide the LangSmith-backed ad-hoc summary panel.",
    )
    args = parser.parse_args(argv)

    bundle_dir = Path(args.bundle_dir) if args.bundle_dir else None
    output_path = Path(args.output) if args.output else HUD_OUTPUT
    include_adhoc_panel = not args.no_adhoc_panel
    watch_interval = 30.0 if args.watch is None else args.watch

    def _open_in_browser() -> None:
        import webbrowser

        webbrowser.open(str(output_path.resolve()))

    if args.watch is None:
        _write_snapshot(
            bundle_dir=bundle_dir,
            output_path=output_path,
            trial_id=args.trial_id,
            include_adhoc_panel=include_adhoc_panel,
            watching=False,
            watch_interval_seconds=watch_interval,
        )
        print(f"HUD written to {output_path}")
        if args.open:
            _open_in_browser()
    else:
        iteration = 0
        try:
            while True:
                iteration += 1
                _write_snapshot(
                    bundle_dir=bundle_dir,
                    output_path=output_path,
                    trial_id=args.trial_id,
                    include_adhoc_panel=include_adhoc_panel,
                    watching=True,
                    watch_interval_seconds=watch_interval,
                )
                print(f"HUD snapshot {iteration} written to {output_path}")
                if iteration == 1 and args.open:
                    _open_in_browser()
                if args.max_iterations is not None and iteration >= args.max_iterations:
                    break
                time.sleep(watch_interval)
        except KeyboardInterrupt:
            print("HUD watch stopped")


if __name__ == "__main__":
    main()
