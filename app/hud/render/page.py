"""Flight-deck render (Story 35.5; AD-12 + UX spines binding).

Pure projection→HTML render for the Operator HUD. Two public entry points:

* :func:`render_page` — the full cold-load page (server-side render on ``GET /``).
* :func:`render_zones` — the five dynamic zones as ``zone-id -> innerHTML``, the
  same strings the client poll renderer re-installs zone-by-zone.

**No I/O inside render** (AD-12): ``data`` is the already-read projection dict
(lenient-parsed to a plain dict) plus derived view state (panel state, bound
identity, ``now`` for age math). ``app.hud`` renders — it never reaches back
into the runtime, the orchestrator, or the gate machinery (import-linter HUD1).

De-scope ladder (party greenlight amendment 3+10, BINDING) applied here:
zone-scoped replacement (no granular DOM diffing); specialist chips carry
monogram/status/activity/node/last-artifact only (model-in-use + cost dropped);
health-tile drill-down history dropped; state-trace is a minimal append-only
feed. NEVER cut: gate/error/batch briefings with inline artifacts + verbatim
command blocks, deliverables summary, identity-guard states, UNRECOGNIZED.

Contract-fidelity note: the render surfaces exactly what the v1
``operator-surface`` contract carries. As of Story 35.9 that contract carries
the UX spine's richer §Projection-Demands sections directly — ``decision_card``
(gate_focus / operator_prompt / drafted_proposal + confidence / pick_context /
evidence), ``error_message`` (verbatim message + node/tag), and
``deliverables`` (component booleans + total cost + export paths). The gate /
error / completed briefings render those sections when present and degrade
gracefully (paused_gate / paused_error_tag / next_action.command) when a
verb-conditional field is absent. The former consumer-side
``specialists[].last_artifact`` deliverables synthesis is DELETED (AD-1: the
projection is the sole input; the runtime owns deliverables, not the view).
"""

from __future__ import annotations

import html as _html
from datetime import datetime
from typing import Any

from app.hud.render.client import POLL_JS
from app.hud.render.styles import CSS
from app.models.runtime.operator_surface import RUN_SETTINGS_TOGGLES

#: Stable zone container ids (the client replaces innerHTML per id).
ZONE_IDS: tuple[str, ...] = (
    "annunciator",
    "identity-header",
    "health-strip",
    "main-deck",
    "state-trace",
)

_STATUS_SYMBOL = {
    "registered": "○",  # ○
    "in-flight": "▶",  # ▶
    "paused-at-gate": "⏸",  # ⏸
    "paused-at-error": "⛔",  # ⛔
    "waiting_for_provider_batch": "⚖",  # ⚖ (external-wait glyph)
    "completed": "✓",  # ✓
    "failed": "⛔",  # ⛔
}

_ATTENTION_STATUSES = frozenset(
    {"paused-at-gate", "paused-at-error", "waiting_for_provider_batch", "failed"}
)

_DONE_STEP = frozenset(
    {"completed", "complete", "done", "pass", "passed", "ok", "exited", "success"}
)
_ACTIVE_STEP = frozenset(
    {"active", "running", "in-progress", "in_progress", "current", "walking", "in-flight"}
)


def _esc(text: Any) -> str:
    """Escape HTML special chars via stdlib (matches run_hud.py idiom)."""
    return _html.escape("" if text is None else str(text), quote=True)


# --------------------------------------------------------------------------
# Age / freshness
# --------------------------------------------------------------------------


def _parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _clock(value: Any) -> str:
    dt = _parse_dt(value)
    return dt.strftime("%H:%M:%S") if dt is not None else _esc(value)


def _age_seconds(as_of: Any, now: Any) -> float | None:
    a, n = _parse_dt(as_of), _parse_dt(now)
    if a is None or n is None:
        return None
    return (n - a).total_seconds()


def _age_stamp(as_of: Any, now: Any) -> str:
    secs = _age_seconds(as_of, now)
    clock = _clock(as_of)
    if secs is None:
        return f"as of {clock}" if clock else ""
    return f"as of {clock} · {int(secs)}s ago"


# --------------------------------------------------------------------------
# View-state derivation (pure)
# --------------------------------------------------------------------------


def _active_entry(steps: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(steps, dict):
        return None
    for entry in steps.get("entries") or []:
        if isinstance(entry, dict) and str(entry.get("status", "")).lower() in _ACTIVE_STEP:
            return entry
    return None


def _view(data: dict[str, Any]) -> dict[str, Any]:
    """Precompute everything both entry points need — never mutate ``data``."""
    panel_state = data.get("panel_state", "ok")
    projection = data.get("projection")
    now = data.get("now")
    proj = projection if isinstance(projection, dict) else {}
    envelope = proj.get("envelope") if isinstance(proj.get("envelope"), dict) else {}
    identity = proj.get("identity") if isinstance(proj.get("identity"), dict) else {}
    steps = proj.get("steps") if isinstance(proj.get("steps"), dict) else None
    status = envelope.get("status")
    active = _active_entry(steps)
    # "walking" iff a step is actively current; otherwise in-flight is pre-flight.
    walking = status == "in-flight" and active is not None
    return {
        "panel_state": panel_state,
        "data": data,
        "proj": proj,
        "envelope": envelope,
        "identity": identity,
        "steps": steps,
        "status": status,
        "active": active,
        "walking": walking,
        "now": now,
        "bound_trial_id": data.get("bound_trial_id", ""),
        "mode": data.get("mode", "session"),
        # Prefer a projection-carried budget so the cold-load server render and
        # the client poll agree (35.9 fold); fall back to the data envelope,
        # then the 60s default.
        "health_budget": int(
            proj.get("health_budget_seconds")
            if isinstance(proj.get("health_budget_seconds"), (int, float))
            else data.get("health_budget_seconds", 60)
        ),
    }


# --------------------------------------------------------------------------
# Zone: annunciator
# --------------------------------------------------------------------------


def _annunciator_parts(view: dict[str, Any]) -> tuple[str, str, str]:
    """Return (variant_class, symbol, text) — highest-severity current line."""
    panel = view["panel_state"]
    if panel == "feed-lost":
        secs = view["data"].get("feed_lost_seconds")
        tail = f" — {int(secs)}s SINCE LAST SNAPSHOT" if secs is not None else ""
        return "ann-feedlost", "⚠", f"HUD FEED LOST{tail}"
    if panel == "no-active-run":
        return "ann-idle", "○", "NO ACTIVE RUN — HUD BOUND TO NONE"
    if panel == "binding":
        tid = _esc(view["bound_trial_id"])
        return "ann-idle", "○", f"BINDING — {tid} · AWAITING FIRST SNAPSHOT"
    if panel == "unrecognized":
        return "ann-idle", "○", "UNRECOGNIZED"
    if panel == "refuse-to-render":
        return "ann-warning", "⛔", "RUN IDENTITY UNCERTAIN — REFUSING TO RENDER"

    env = view["envelope"]
    status = view["status"]
    if status == "paused-at-gate":
        return "ann-gate", "⏸", f"PAUSED AT GATE {_esc(env.get('paused_gate') or '?')}"
    if status == "paused-at-error":
        return "ann-error", "⛔", f"PAUSED AT ERROR — {_esc(env.get('paused_error_tag') or '?')}"
    if status == "waiting_for_provider_batch":
        batch_id = _esc(env.get("waiting_batch_id") or "?")
        return "ann-wait", "⚖", f"PARKED — PROVIDER BATCH {batch_id}"
    if status == "failed":
        return "ann-failed", "⛔", f"FAILED — {_esc(env.get('paused_error_tag') or 'run failed')}"
    if status == "completed":
        return "ann-completed", "✓", f"LANDED — completed {_clock(env.get('completed_at'))}"
    if status == "registered":
        return "ann-nominal", "○", "REGISTERED — awaiting pre-flight"
    if status == "in-flight":
        if view["walking"]:
            a = view["active"]
            return (
                "ann-nominal",
                "▶",
                f"IN FLIGHT — {_esc(a.get('step_id'))} · {_esc(a.get('label'))}",
            )
        return "ann-nominal", "◐", "PRE-FLIGHT IN PROGRESS"
    # Unknown status that still parsed — render literally, never coerce.
    return "ann-idle", "○", f"UNRECOGNIZED STATUS {_esc(status)!r}"


def _zone_annunciator(view: dict[str, Any]) -> str:
    variant, sym, text = _annunciator_parts(view)
    return (
        f'<div class="annunciator {variant}" role="status" aria-live="polite">'
        f'<span class="sym">{sym}</span><span>{text}</span></div>'
    )


# --------------------------------------------------------------------------
# Zone: identity header
# --------------------------------------------------------------------------

_BADGE_VARIANT = {
    "registered": "badge-dim",
    "in-flight": "badge-nominal",
    "completed": "badge-dim",
    "paused-at-gate": "badge-gate",
    "paused-at-error": "badge-error",
    "waiting_for_provider_batch": "badge-wait",
    "failed": "badge-failed",
}


def _chip(label: str, on: bool, *, batch: bool = False) -> str:
    cls = "chip on" if on else "chip"
    if batch:
        cls += " batch"
    return f'<span class="{cls}"><span class="dot"></span> {_esc(label)}</span>'


def _zone_identity(view: dict[str, Any]) -> str:
    ident = view["identity"]
    status = view["status"]
    if view["panel_state"] in ("no-active-run", "unrecognized", "refuse-to-render"):
        tid = _esc(view["bound_trial_id"])
        return f'<header class="id-header"><span class="mono trial">{tid}</span></header>'

    sym = _STATUS_SYMBOL.get(status, "○")
    badge_cls = _BADGE_VARIANT.get(status, "badge-dim")
    badge = (
        f'<span class="badge {badge_cls}"><span>{sym}</span> {_esc(status)}</span>'
        if status
        else ""
    )

    mods = view["proj"].get("modalities")
    mods = mods if isinstance(mods, dict) else {}
    exec_mode = str(mods.get("llm_execution_mode") or "").lower()
    styleguide = mods.get("styleguide")
    chips = (
        _chip("BATCH", "batch" in exec_mode, batch=True)
        + _chip("DETECTIVE", bool(mods.get("detective_disposition")))
        + _chip(styleguide or "styleguide", bool(styleguide))
    )

    echo = view["proj"].get("notifications_echo")
    parse_status = echo.get("parse_status") if isinstance(echo, dict) else None
    notif = ""
    if parse_status not in (None, "ok"):
        notif = f'<span class="chip warn">⚠ {_esc(parse_status)}</span>'

    age = _age_stamp(view["proj"].get("as_of"), view["now"])
    header = (
        '<header class="id-header">'
        f'<span class="mono trial">{_esc(ident.get("trial_id"))}</span>'
        f'<span class="kv">lesson <b>{_esc(ident.get("lesson"))}</b></span>'
        f'<span class="kv">preset <b>{_esc(ident.get("preset"))}</b></span>'
        f"{badge}{chips}{notif}"
        f'<span class="id-right freshness">'
        f'<span class="meta"><span class="sweep"></span>snapshot {_esc(age)}</span>'
        "</span></header>"
    )
    # Story 42.3: the full 16-toggle standing readout rides the (always-present)
    # identity zone, so it is visible from launch through every gate to terminal.
    return header + _run_settings_panel(view)


# --------------------------------------------------------------------------
# Run-settings standing readout (Story 42.3)
# --------------------------------------------------------------------------


def _rs_state(value: Any) -> str:
    """Map a resolved toggle value to a CSS state modifier (on/off/unset/value)."""
    v = str(value).strip().lower()
    if v == "on":
        return "on"
    if v == "off":
        return "off"
    if v in ("", "unset", "none"):
        return "unset"
    return "value"


def _run_settings_panel(view: dict[str, Any]) -> str:
    """Render all 16 run-defining toggles as a persistent labelled readout.

    Renders NOTHING when the projection carries no ``run_settings`` section
    (a pre-42.3 frozen surface), so old consumers are unaffected (AC-6).
    """
    rs = view["proj"].get("run_settings")
    if not isinstance(rs, dict):
        return ""
    rows = "".join(
        f'<div class="rs-item"><span class="rs-k">{_esc(label)}</span>'
        f'<span class="rs-v rs-{_rs_state(rs.get(field))}">'
        f'{_esc(rs.get(field, "—"))}</span></div>'
        for field, label in RUN_SETTINGS_TOGGLES
    )
    age = _age_stamp(rs.get("as_of"), view["now"])
    age_html = f'<span class="rs-age">{_esc(age)}</span>' if age else ""
    return (
        '<section class="run-settings" aria-label="run settings standing readout">'
        f'<div class="rs-title">Run settings · standing readout{age_html}</div>'
        f'<div class="rs-grid">{rows}</div></section>'
    )


# --------------------------------------------------------------------------
# Zone: health strip
# --------------------------------------------------------------------------


def _health_tile(tile: dict[str, Any], now: Any, budget: int, force_stale: bool) -> str:
    label = _esc(tile.get("label"))
    unit = tile.get("unit")
    value = _esc(tile.get("value"))
    if unit:
        value = f"{value} {_esc(unit)}"
    conf = tile.get("confidence")
    threshold = str(tile.get("threshold_state") or "")
    sub = ""
    if conf:
        sub = f'<span class="conf">{_esc(conf)}</span>'
    age_secs = _age_seconds(tile.get("as_of"), now)
    stale = force_stale or (age_secs is not None and age_secs > budget)
    cls = "tile"
    if threshold in ("warning", "breached"):
        cls += " warn"
    if stale:
        cls += " stale"
    body = (
        f'<div class="lbl">{label}</div>'
        f'<div class="val">{value}</div>'
        f'<div class="sub">{sub}</div>'
    )
    if stale:
        stamp = _clock(tile.get("as_of"))
        tail = f" ({int(age_secs)}s ago)" if age_secs is not None else ""
        body += f'<div class="stamp">⧗ STALE · last good {stamp}{tail}</div>'
    else:
        body += f'<div class="age">{_esc(_age_stamp(tile.get("as_of"), now))}</div>'
    return f'<div class="{cls}">{body}</div>'


def _zone_health(view: dict[str, Any]) -> str:
    if view["panel_state"] in ("no-active-run", "binding", "unrecognized", "refuse-to-render"):
        return '<section class="health" aria-label="health strip"></section>'
    health = view["proj"].get("health")
    tiles = health.get("tiles") if isinstance(health, dict) else None
    if not tiles:
        return '<section class="health" aria-label="health strip"></section>'
    force_stale = view["panel_state"] in ("stale-veil", "feed-lost")
    rows = "".join(
        _health_tile(t, view["now"], view["health_budget"], force_stale)
        for t in tiles
        if isinstance(t, dict)
    )
    return f'<section class="health" aria-label="health strip">{rows}</section>'


# --------------------------------------------------------------------------
# Zone: main deck (map + specialists + context panel)
# --------------------------------------------------------------------------


def _step_kind(entry: dict[str, Any], view: dict[str, Any]) -> str:
    status = str(entry.get("status", "")).lower()
    if entry is view["active"]:
        if view["status"] == "paused-at-gate":
            return "gate-paused"
        return "active"
    if status in _DONE_STEP:
        return "done"
    return "idle"


_STEP_MARK = {"done": "✓", "active": "▶", "gate-paused": "⏸", "idle": "○"}


def _map_node(entry: dict[str, Any], view: dict[str, Any]) -> str:
    kind = _step_kind(entry, view)
    mark = _STEP_MARK[kind]
    conditions = entry.get("conditions") or []
    blockers = entry.get("blockers") or []
    is_current = entry is view["active"]
    urgent = is_current or bool(conditions) or bool(blockers)
    open_attr = " open" if urgent else ""
    auto = ' data-auto-open="urgent"' if urgent else ""
    nid = _esc(entry.get("step_id"))
    detail_id = f"node-{nid}".replace(".", "-").replace(" ", "-")

    gate_badge = ""
    if kind == "gate-paused":
        gate = view["envelope"].get("paused_gate")
        if gate:
            gate_badge = f'<span class="gatebadge">⏸ {_esc(gate)}</span>'
    dur = ""
    if is_current and view["walking"]:
        walk = view["steps"].get("walk_index") if isinstance(view["steps"], dict) else None
        node_count = view["steps"].get("node_count") if isinstance(view["steps"], dict) else None
        if walk is not None and node_count:
            dur = f'<span class="dur">Step {_esc(walk)}/{_esc(node_count)}</span>'

    locked = entry.get("locked_artifact_summary")
    detail = (
        f'<div class="frow"><span class="k">locked artifact</span>'
        f'<span class="v mono">{_esc(locked) if locked else "no locked artifact yet"}</span></div>'
    )
    if conditions:
        detail += (
            '<div class="frow"><span class="k">conditions</span><span class="v">'
            + _esc(", ".join(str(c) for c in conditions))
            + "</span></div>"
        )
    if blockers:
        detail += (
            '<div class="frow"><span class="k">blockers</span><span class="v">'
            + _esc(", ".join(str(b) for b in blockers))
            + "</span></div>"
        )
    return (
        f'<details id="{detail_id}" data-step-summary-id="{detail_id}" '
        f'class="node {kind}"{auto}{open_attr}>'
        f'<summary><span class="mark">{mark}</span>'
        f'<span class="nid">{nid}</span>'
        f'<span class="lab">{_esc(entry.get("label"))}</span>{gate_badge}{dur}</summary>'
        f'<div class="node-detail">{detail}</div></details>'
    )


def _zone_map(view: dict[str, Any]) -> str:
    steps = view["steps"]
    if not isinstance(steps, dict):
        placeholder = (
            '<div class="map-group"><div class="map-title">Ratified workflow</div>'
            '<div class="placeholder"><span class="mark">○</span>'
            "workflow pends ratification — steps will appear here after G0R</div></div>"
        )
        return f'<section aria-label="you-are-here map">{placeholder}</section>'

    entries = [e for e in (steps.get("entries") or []) if isinstance(e, dict)]
    stage1 = [e for e in entries if e.get("stage") == "stage-1"]
    stage2 = [e for e in entries if e.get("stage") == "stage-2"]

    out = '<section aria-label="you-are-here map">'
    if stage1:
        out += (
            '<div class="map-group">'
            '<div class="map-title">Planning — intake &amp; ratification</div>'
            + "".join(_map_node(e, view) for e in stage1)
            + "</div>"
        )
    walk = steps.get("walk_index")
    node_count = steps.get("node_count")
    if stage2:
        title = "Ratified workflow"
        if node_count:
            title += f" — {_esc(node_count)} nodes"
        if walk is not None and node_count:
            title += f" · Step {_esc(walk)}/{_esc(node_count)}"
        out += (
            f'<div class="map-group"><div class="map-title">{title}</div>'
            + "".join(_map_node(e, view) for e in stage2)
            + "</div>"
        )
    else:
        n = f"{_esc(node_count)} " if node_count else ""
        out += (
            '<div class="map-group"><div class="map-title">Ratified workflow</div>'
            '<div class="placeholder"><span class="mark">○</span>'
            f"workflow pends ratification — {n}steps will appear here after G0R</div></div>"
        )
    return out + "</section>"


_SPEC_GLYPH = {
    "active": ("run", "▶"),
    "running": ("run", "▶"),
    "done": ("done", "✓"),
    "completed": ("done", "✓"),
    "degraded": ("warn", "⚠"),
    "retrying": ("warn", "⚠"),
    "awaiting": ("awaiting", "⏸"),
}


def _monogram(name: str) -> str:
    clean = "".join(ch for ch in name if ch.isalnum())
    return (clean[:2] or "??").upper()


def _specialist_chip(spec: dict[str, Any]) -> str:
    status = str(spec.get("status", "")).lower()
    cls, glyph = _SPEC_GLYPH.get(status, ("idle", "○"))
    name = str(spec.get("name") or "?")
    mono = _monogram(name)
    detail = (
        f'<div class="spec-detail">{_esc(name)} · {_esc(spec.get("status"))}'
        f'<br>node <span class="mono">{_esc(spec.get("current_node") or "—")}</span>'
        f'<br>last <span class="mono">{_esc(spec.get("last_artifact") or "—")}</span></div>'
    )
    return (
        f'<details class="spec {cls}"><summary>{_esc(mono)}'
        f'<span class="g">{glyph}</span></summary>{detail}</details>'
    )


def _zone_specialists(view: dict[str, Any]) -> str:
    specs = view["proj"].get("specialists")
    roster = specs.get("roster") if isinstance(specs, dict) else []
    roster = [s for s in (roster or []) if isinstance(s, dict)]
    if not roster:
        return ""
    chips = "".join(_specialist_chip(s) for s in roster)
    return f'<div class="spec-row" aria-label="specialist roster">{chips}</div>'


def _command_block(command: Any, caption: str) -> str:
    if not command:
        return ""
    return (
        f'<div class="cmd-cap">{_esc(caption)}</div>'
        f'<div class="cmd">{_esc(command)}</div>'
    )


def _artifacts_block(items: list[str]) -> str:
    """Inline artifacts under judgment; collapse beyond the first three."""
    if not items:
        return ""
    head = items[:3]
    tail = items[3:]
    rows = "".join(
        f'<div class="artifact"><span class="mono">{_esc(a)}</span></div>' for a in head
    )
    out = f'<div class="artifacts">{rows}</div>'
    if tail:
        more = "".join(
            f'<div class="artifact"><span class="mono">{_esc(a)}</span></div>' for a in tail
        )
        out += (
            f'<details class="more"><summary>+{len(tail)} more artifact(s)</summary>'
            f'<div class="artifacts">{more}</div></details>'
        )
    return out


def _next_action(view: dict[str, Any]) -> dict[str, Any]:
    na = view["proj"].get("next_action")
    return na if isinstance(na, dict) else {}


def _ctx_preflight(view: dict[str, Any]) -> str:
    pf = view["proj"].get("preflight")
    items = pf.get("items") if isinstance(pf, dict) else None
    rows = ""
    _cls = {"pass": "pass", "running": "run", "fail": "fail", "missed": "missed", "pending": "pend"}
    _mk = {"pass": "✓", "running": "◐", "fail": "✕", "missed": "⧗", "pending": "○"}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        state = str(item.get("state") or "pending")
        cls = _cls.get(state, "pend")
        mark = _mk.get(state, "○")
        res = item.get("output") or item.get("quota_reading") or ""
        conf = item.get("quota_confidence")
        if conf and conf != "unknown":
            res = f'{_esc(res)} · <span class="conf-inline">{_esc(conf)}</span>'
        else:
            res = _esc(res)
        lat = item.get("latency_ms")
        dur = f"{_esc(lat)}ms" if lat is not None else "—"
        failed = state in ("fail", "missed")
        open_attr = " open" if failed else ""
        auto = ' data-auto-open="urgent"' if failed else ""
        detail = (
            f'<div class="check-detail">{_esc(item.get("output"))}</div>'
            if failed and item.get("output")
            else ""
        )
        rows += (
            f'<details class="check {cls}"{auto}{open_attr}>'
            f'<summary><span class="mark">{mark}</span>'
            f'<span class="name">{_esc(item.get("name"))}</span>'
            f'<span class="res">{res}</span><span class="dur">{dur}</span></summary>'
            f"{detail}</details>"
        )
    if not rows:
        rows = '<div class="check pend"><span class="res">pre-flight pending</span></div>'
    return f'<div class="board"><div class="phase-title">Pre-flight · Readiness</div>{rows}</div>'


def _ctx_walking(view: dict[str, Any]) -> str:
    a = view["active"] or {}
    steps = view["steps"] if isinstance(view["steps"], dict) else {}
    walk = steps.get("walk_index")
    node_count = steps.get("node_count")
    step_line = ""
    if walk is not None and node_count:
        step_line = f"Step {_esc(walk)}/{_esc(node_count)} · "
    locked = a.get("locked_artifact_summary")
    fields = (
        f'<div class="frow"><span class="k">locked artifact</span>'
        f'<span class="v mono">{_esc(locked) if locked else "no locked artifact yet"}</span></div>'
    )
    for key in ("conditions", "blockers"):
        vals = a.get(key) or []
        fields += (
            f'<div class="frow"><span class="k">{key}</span><span class="v">'
            + (_esc(", ".join(str(v) for v in vals)) if vals else "none")
            + "</span></div>"
        )
    return (
        '<details class="brief" open><summary>'
        f'<div class="bt">{_esc(a.get("step_id"))} · {_esc(a.get("label"))}</div>'
        f'<div class="bm">{step_line}walk index {_esc(walk)}</div></summary>'
        f'<div class="fields">{fields}</div></details>'
    )


def _decision_card(view: dict[str, Any]) -> dict[str, Any]:
    dc = view["proj"].get("decision_card")
    return dc if isinstance(dc, dict) else {}


def _labelled_artifacts(label: str, items: list[str]) -> str:
    """A captioned collapse-beyond-3 artifacts block (skipped when empty)."""
    if not items:
        return ""
    return f'<div class="art-label">{_esc(label)}</div>{_artifacts_block(items)}'


def _ctx_gate(view: dict[str, Any]) -> str:
    env = view["envelope"]
    gate = env.get("paused_gate")
    dc = _decision_card(view)
    focus = dc.get("gate_focus")
    prompt = dc.get("operator_prompt")
    proposal = dc.get("drafted_proposal") if isinstance(dc.get("drafted_proposal"), dict) else None

    # Decision-card fields ABOVE the command block (Story 35.9). gate_focus +
    # operator_prompt + drafted_proposal + confidence, each verb-conditional.
    fields = ""
    if focus:
        fields += (
            '<div class="frow"><span class="k">gate focus</span>'
            f'<span class="v mono">{_esc(focus)}</span></div>'
        )
    if proposal:
        conf = proposal.get("confidence")
        conf_txt = f" · confidence {_esc(conf)}" if conf is not None else ""
        fields += (
            '<div class="frow"><span class="k">drafted proposal</span>'
            f'<span class="v">{_esc(proposal.get("decision"))}{conf_txt}</span></div>'
        )
        if proposal.get("rationale"):
            fields += (
                '<div class="frow"><span class="k">rationale</span>'
                f'<span class="v">{_esc(proposal.get("rationale"))}</span></div>'
            )
    fields_html = f'<div class="fields">{fields}</div>' if fields else ""

    prompt_text = _esc(prompt) if prompt else (
        f"Gate {_esc(gate)} awaits your verdict. Decide via the Marcus-SPOC "
        "surface using the command below."
    )
    # pick_context / evidence via the collapse-beyond-3 helper. Fall back to
    # the paused node's locked artifact only when the card carries no evidence.
    pick = [str(x) for x in (dc.get("pick_context") or [])]
    evidence = [str(x) for x in (dc.get("evidence") or [])]
    if not evidence:
        locked = (view["active"] or {}).get("locked_artifact_summary")
        evidence = [str(locked)] if locked else []
    artifacts = _labelled_artifacts("options", pick) + _labelled_artifacts("evidence", evidence)
    cmd = _command_block(
        _next_action(view).get("command"),
        "paste into the Marcus-SPOC surface — digest pre-filled:",
    )
    return (
        '<div class="gate-brief">'
        f'<div class="bt">⏸ Gate {_esc(gate)}</div>'
        f'<div class="bm">{_esc(_age_stamp(env.get("as_of"), view["now"]))}</div>'
        f'<div class="prompt">{prompt_text}</div>'
        f"{fields_html}{artifacts}{cmd}</div>"
    )


def _ctx_error(view: dict[str, Any]) -> str:
    env = view["envelope"]
    tag = env.get("paused_error_tag")
    steps = view["steps"] if isinstance(view["steps"], dict) else {}
    a = view["active"] or {}
    reenter = steps.get("reentered_from")
    cmd = _command_block(_next_action(view).get("command"), "recover command:")
    node = _esc(a.get("step_id"))
    walk = _esc(steps.get("walk_index"))
    reenter_v = _esc(reenter) if reenter is not None else "—"

    # Verbatim error message (Story 35.9): the error_message section carries the
    # exact runtime message + node_index + tag; render the message verbatim and
    # prefer its richer tag/node_index over the envelope fallback when present.
    em = view["proj"].get("error_message")
    em = em if isinstance(em, dict) else {}
    message = em.get("message")
    display_tag = em.get("tag") or tag
    node_index = em.get("node_index")
    node_disp = f"{node} · walk {walk}"
    if node_index is not None:
        node_disp += f" · node index {_esc(node_index)}"

    message_html = ""
    if message:
        message_html = (
            '<div class="frow"><span class="k">message</span>'
            f'<span class="v mono">{_esc(message)}</span></div>'
        )
    fields = (
        '<div class="frow"><span class="k">error tag</span>'
        f'<span class="v mono">{_esc(display_tag)}</span></div>'
        f"{message_html}"
        '<div class="frow"><span class="k">node</span>'
        f'<span class="v mono">{node_disp}</span></div>'
        '<div class="frow"><span class="k">re-entry</span>'
        f'<span class="v mono">{reenter_v}</span></div>'
    )
    return (
        '<div class="err-brief">'
        f'<div class="bt">⛔ Paused at error</div>'
        f'<div class="bm">{_esc(_age_stamp(env.get("as_of"), view["now"]))}</div>'
        f'<div class="fields">{fields}</div>{cmd}</div>'
    )


def _ctx_batch(view: dict[str, Any]) -> str:
    env = view["envelope"]
    batch = env.get("waiting_batch_id")
    cmd = _command_block(_next_action(view).get("command"), "resume command:")
    age = _esc(_age_stamp(env.get("as_of"), view["now"]))
    return (
        '<div class="batch-brief">'
        f'<div class="bt">⚖ Provider batch parked</div>'
        f'<div class="bm">batch {_esc(batch)} · {age}</div>'
        '<div class="prompt">LiteLLM provider batch — resume polls the batch. '
        "Nothing is wrong; no verdict is owed.</div>"
        f"{cmd}</div>"
    )


def _ctx_completed(view: dict[str, Any]) -> str:
    env = view["envelope"]
    # Story 35.9: deliverables come from the projection's own ``deliverables``
    # section (runtime-owned, AD-1) — the consumer-side specialists[].last_artifact
    # synthesis is GONE. Discrete export list + component chips + final cost line.
    deliv = view["proj"].get("deliverables")
    deliv = deliv if isinstance(deliv, dict) else {}

    components = deliv.get("components") if isinstance(deliv.get("components"), dict) else {}
    comp_chips = "".join(
        f'<span class="chip on"><span class="dot"></span> {_esc(name.upper())}</span>'
        for name in ("deck", "motion", "workbook")
        if components.get(name)
    )
    comp_html = f'<div class="components">{comp_chips}</div>' if comp_chips else ""

    exports = [str(p) for p in (deliv.get("export_paths") or [])]
    rows = "".join(
        f'<div class="artifact"><span class="mono">{_esc(p)}</span></div>' for p in exports
    )
    if not rows:
        rows = '<div class="artifact">see run dir for exports</div>'

    cost = ""
    total = deliv.get("total_cost_usd")
    if total is not None:
        cost = (
            '<div class="frow"><span class="k">final cost</span>'
            f'<span class="v">${_esc(total)}</span></div>'
        )
    # Story Q4.3: the compact PROJECT quality posture rides the completed brief
    # (the Q4.1 assembler populates the tile at the terminal-completion
    # choke-point). Fail-soft: absent/unavailable → an explicit unavailable tile.
    return (
        '<div class="land-brief">'
        f'<div class="bt">✓ Landed</div>'
        f'<div class="bm">completed {_clock(env.get("completed_at"))}</div>'
        f"{comp_html}"
        f'<div class="artifacts">{rows}</div><div class="fields">{cost}</div></div>'
        f"{_quality_panel(view)}"
    )


# --------------------------------------------------------------------------
# Quality tile (Story Q4.3) — READ-ONLY consumer of the Q4.1 QualitySection.
# --------------------------------------------------------------------------

#: Band → severity chip class over the A/B/C/D ladder. Unknown / missing bands
#: map to the NEUTRAL class — never ``on`` — so a garbage band can NEVER read
#: cleaner than a committed red (QLW-9). The assembler already floors an
#: unrecognized band to "D" upstream; this map only colours what it renders.
#: ``d`` (the worst committed band) gets its OWN critical/red ``crit`` chip so it
#: is visually distinct from ``c``'s amber ``warn`` — a worst-band read must not
#: look the same as a merely-cautionary one (QLW-9 at the HUD layer).
_QUALITY_BAND_CLASS = {"a": "on", "b": "on", "c": "warn", "d": "crit"}


def _quality_panel(view: dict[str, Any]) -> str:
    """Render the compact PROJECT quality posture tile (Story Q4.3).

    READ-ONLY consumer of the operator-surface ``quality`` section shipped by
    Story Q4.1 — the HUD NEVER recomputes quality (QLW-4); it renders ONLY the
    honest fields the section carries. Zero-lie / fail-soft (QLW-8, non-negotiable):
    a missing / ``None`` / malformed / ``available=False`` section renders an
    EXPLICIT "quality: unavailable" state — NEVER a fabricated band, NEVER a
    silent green absence, and NEVER a crash (every read is ``.get`` + ``_esc``).
    """
    quality = view["proj"].get("quality")
    # FIX 3: the ``available`` flag is honoured ONLY when it is the boolean
    # ``True``. A truthy-but-non-True value ("false", "no", "yes", 1, …) is NOT
    # a valid available posture — it renders the honest "unavailable" tile,
    # never a fabricated band. ``is True`` is the strict, zero-lie gate.
    if not isinstance(quality, dict) or quality.get("available") is not True:
        # QLW-8: absence/degrade is reported honestly — NOT a clean bill.
        return (
            '<section class="quality-tile unavailable" '
            'aria-label="project quality posture">'
            '<div class="bt">◍ Project quality — unavailable</div>'
            '<div class="prompt">No committed scorecard read on this run surface. '
            "This absence is reported honestly — it is NOT a clean bill of "
            "quality.</div></section>"
        )

    band = quality.get("band")
    band_cls = _QUALITY_BAND_CLASS.get(str(band or "").strip().lower(), "")
    band_chip = (
        f'<span class="chip {band_cls}"><span class="dot"></span> '
        f'band {_esc(band) if band else "—"}</span>'
    )

    fields = ""
    ranked = quality.get("ranked_leak_count")
    if ranked is not None:
        fields += (
            '<div class="frow"><span class="k">ranked leaks</span>'
            f'<span class="v">{_esc(ranked)}</span></div>'
        )
    gaps = quality.get("coverage_gaps")
    if gaps is not None:
        fields += (
            '<div class="frow"><span class="k">coverage gaps</span>'
            f'<span class="v">{_esc(gaps)}</span></div>'
        )
    trend = quality.get("trend")
    if trend:
        fields += (
            '<div class="frow"><span class="k">trend</span>'
            f'<span class="v">{_esc(trend)}</span></div>'
        )
    fields_html = f'<div class="fields">{fields}</div>' if fields else ""

    # FIX 2: ``top_leaks`` is a RAW producer-projection field — never assume it
    # is a list. A truthy non-iterable (``top_leaks: 5``) would ``TypeError`` and
    # crash the whole completed render; a bare string would char-iterate into
    # per-character rows. Coerce field-defensively: only a genuine list/tuple
    # yields leak rows, ``None`` entries are dropped (the None-label finding),
    # anything else degrades to no leak block.
    tl = quality.get("top_leaks")
    leaks = (
        [str(x) for x in tl if x is not None]
        if isinstance(tl, (list, tuple))
        else []
    )
    leaks_html = _labelled_artifacts("top leaks", leaks)

    scorecard_as_of = quality.get("scorecard_as_of")
    stamp = (
        f'<div class="bm">scorecard as of {_esc(scorecard_as_of)}</div>'
        if scorecard_as_of
        else '<div class="bm">scorecard staleness unknown</div>'
    )
    return (
        '<section class="quality-tile" aria-label="project quality posture">'
        '<div class="bt">◍ Project quality</div>'
        f"{stamp}"
        f'<div class="components">{band_chip}</div>'
        f"{fields_html}{leaks_html}</section>"
    )


def _ctx_failed(view: dict[str, Any]) -> str:
    env = view["envelope"]
    tag = env.get("paused_error_tag")
    command = _next_action(view).get("command")
    if command:
        tail = _command_block(command, "recovery command:")
    else:
        tail = '<div class="prompt">no automated recovery — see SPOC</div>'
    return (
        '<div class="fail-brief">'
        f'<div class="bt">⛔ Failed</div>'
        f'<div class="bm">{_esc(_age_stamp(env.get("as_of"), view["now"]))}</div>'
        f'<div class="fields"><div class="frow"><span class="k">reason</span>'
        f'<span class="v mono">{_esc(tag) if tag else "run failed"}</span></div></div>{tail}</div>'
    )


def _zone_context(view: dict[str, Any]) -> str:
    status = view["status"]
    if status == "paused-at-gate":
        return _ctx_gate(view)
    if status == "paused-at-error":
        return _ctx_error(view)
    if status == "waiting_for_provider_batch":
        return _ctx_batch(view)
    if status == "completed":
        return _ctx_completed(view)
    if status == "failed":
        return _ctx_failed(view)
    if status == "in-flight" and view["walking"]:
        return _ctx_walking(view)
    # registered + in-flight-preflight → the pre-flight board.
    return _ctx_preflight(view)


def _panel_message(view: dict[str, Any]) -> str:
    panel = view["panel_state"]
    data = view["data"]
    if panel == "no-active-run":
        return (
            '<div class="panel-msg"><div class="headline">NO ACTIVE RUN</div>'
            "HUD bound to none. Start a trial to begin pre-flight. "
            "No stale data from previous runs is shown.</div>"
        )
    if panel == "binding":
        return (
            '<div class="panel-msg"><div class="headline">BINDING</div>'
            f"{_esc(view['bound_trial_id'])} · awaiting first snapshot. "
            "No data rendered until the first snapshot lands.</div>"
        )
    if panel == "unrecognized":
        info = data.get("unrecognized") or {}
        sv = info.get("schema_version")
        reason = info.get("reason")
        raw = info.get("raw", "")
        sv_line = f"schema_version {_esc(sv)!r}" if sv else "schema version did not match"
        reason_line = f" — {_esc(reason)}" if reason else ""
        return (
            '<div class="panel-msg"><div class="headline">UNRECOGNIZED</div>'
            f"{sv_line}{reason_line}. Rendered literally, never coerced (zero-lie)."
            f'<div class="raw">{_esc(raw)}</div></div>'
        )
    if panel == "refuse-to-render":
        info = data.get("refuse") or {}
        bound = _esc(info.get("bound"))
        found = _esc(info.get("found"))
        return (
            '<div class="panel-msg refuse"><div class="headline">RUN IDENTITY UNCERTAIN '
            "— refusing to render</div>"
            f'<div class="raw">bound: {bound}\nfound: {found}</div>'
            "The April HUD’s silent wrong-run fallback is dead.</div>"
        )
    return ""


def _zone_main_deck(view: dict[str, Any]) -> str:
    if view["panel_state"] in ("no-active-run", "binding", "unrecognized", "refuse-to-render"):
        return f'<main class="deck-msg">{_panel_message(view)}</main>'
    left = _zone_map(view) + _zone_specialists(view)
    right = _zone_context(view)
    return (
        '<main class="deck">'
        f'<section class="mapcol">{left}</section>'
        f'<aside class="ctxcol" aria-label="context panel">{right}</aside>'
        "</main>"
    )


# --------------------------------------------------------------------------
# Zone: state-trace well
# --------------------------------------------------------------------------


def _zone_trace(view: dict[str, Any]) -> str:
    if view["panel_state"] in ("no-active-run", "binding", "unrecognized", "refuse-to-render"):
        return ""
    trace = view["proj"].get("trace")
    events = trace.get("events") if isinstance(trace, dict) else None
    events = [e for e in (events or []) if isinstance(e, dict)]
    if not events:
        body = "no events yet"
        count = 0
    else:
        lines = []
        for ev in events:
            clock = _clock(ev.get("at"))
            detail = ev.get("detail")
            line = f"{clock}  {_esc(ev.get('event'))}"
            if detail:
                line += f" · {_esc(detail)}"
            lines.append(line)
        body = "\n".join(lines)
        count = len(events)
    return (
        '<details class="trace">'
        f"<summary>State trace — {count} events · newest last</summary>"
        f"<pre>{body}</pre></details>"
    )


# --------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------


def render_zones(data: dict[str, Any]) -> dict[str, str]:
    """Return the five dynamic zones as ``zone-id -> innerHTML`` (pure)."""
    view = _view(data)
    return {
        "annunciator": _zone_annunciator(view),
        "identity-header": _zone_identity(view),
        "health-strip": _zone_health(view),
        "main-deck": _zone_main_deck(view),
        "state-trace": _zone_trace(view),
    }


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Operator HUD — {title}</title>
<style>{css}</style>
</head>
<body>
<div id="annunciator">{annunciator}</div>
<div id="identity-header">{identity}</div>
<div id="health-strip">{health}</div>
<div id="main-deck">{main}</div>
<div id="state-trace">{trace}</div>
<script>{js}</script>
</body>
</html>
"""


def render_page(data: dict[str, Any]) -> str:
    """Render the full cold-load page (server-side render on ``GET /``)."""
    zones = render_zones(data)
    title = _esc(data.get("bound_trial_id") or data.get("mode") or "flight deck")
    return _PAGE.format(
        title=title,
        css=CSS,
        js=POLL_JS,
        annunciator=zones["annunciator"],
        identity=zones["identity-header"],
        health=zones["health-strip"],
        main=zones["main-deck"],
        trace=zones["state-trace"],
    )


__all__ = ["ZONE_IDS", "render_page", "render_zones"]
