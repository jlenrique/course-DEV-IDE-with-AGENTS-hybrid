"""Flight-deck stylesheet (Story 35.5) — DESIGN.md tokens VERBATIM.

Single dark cockpit theme (no light mode — the HUD lives on a dedicated
second monitor, per DESIGN.md.Colors). Every hex here is copied verbatim from
``ux-operator-hud-2026-07-11/DESIGN.md`` front-matter; the golden tests assert
a representative subset is present so a token drift is a red test, not a silent
palette change. Pure string constant — no imports, no I/O (AD-4/12 layer rule:
``app.hud`` renders, it never reaches back into the runtime).
"""

from __future__ import annotations

# DESIGN.md tokens, verbatim, kept as named constants so the intent is legible
# and the golden token-presence assertions read against the source of truth.
SURFACE_BASE = "#0F172A"
SURFACE_RAISED = "#1E293B"
SURFACE_INSET = "#0B1120"
BORDER_HAIRLINE = "#293548"
INK_PRIMARY = "#E2E8F0"
INK_SECONDARY = "#94A3B8"
INK_DIM = "#64748B"
ACTIVE = "#38BDF8"
ACTIVE_INK = "#06263A"
STATUS_NOMINAL = "#22C55E"
STATUS_NOMINAL_DIM = "#166534"
STATUS_CAUTION = "#FBBF24"
STATUS_CAUTION_INK = "#1C1403"
STATUS_WARNING = "#EF4444"
STATUS_WARNING_INK = "#FFFFFF"
STATUS_WAIT = "#A78BFA"
STATUS_WAIT_INK = "#1E1633"
STATUS_IDLE = "#64748B"

CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
html, body { background:#0F172A; }
body {
  color:#E2E8F0;
  font-family:'Segoe UI', system-ui, sans-serif;
  font-size:14px; font-weight:400; line-height:1.5;
  min-width:1100px;
}
a { color:#94A3B8; text-decoration:underline; text-underline-offset:2px; }
.mono { font-family:'Cascadia Mono', Consolas, monospace; font-size:13px; line-height:1.5; }
.num  { font-size:16px; font-weight:600; line-height:1.2; letter-spacing:0.01em; font-variant-numeric:tabular-nums; }
.meta { font-size:12px; font-weight:400; line-height:1.4; color:#64748B; }

/* ---- Zone 1 · annunciator strip (color + shape + symbol; never hue alone) ---- */
.annunciator {
  display:flex; align-items:center; gap:12px;
  padding:12px 16px;
  font-size:20px; font-weight:700; line-height:1.2; letter-spacing:0.06em;
  transition: background 300ms ease, color 300ms ease;
}
.annunciator .sym { font-size:18px; }
.ann-nominal   { background:#0B1120; color:#64748B; }
.ann-completed { background:#0B1120; color:#22C55E; }
.ann-gate      { background:#FBBF24; color:#1C1403; }
.ann-warning, .ann-error, .ann-failed { background:#EF4444; color:#FFFFFF; }
.ann-wait      { background:#A78BFA; color:#1E1633; }
.ann-feedlost  { background:#FBBF24; color:#1C1403; }
.ann-idle      { background:#0B1120; color:#64748B; }

/* ---- Zone 2 · identity header ---- */
.id-header {
  display:flex; align-items:center; flex-wrap:wrap; gap:8px 16px;
  padding:10px 16px; border-bottom:1px solid #293548;
}
.id-header .trial { color:#94A3B8; }
.id-header .kv { color:#94A3B8; }
.id-header .kv b { color:#E2E8F0; font-weight:600; }
.badge {
  display:inline-flex; align-items:center; gap:6px;
  padding:3px 10px; border-radius:4px;
  font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase;
}
.badge-dim     { background:transparent; border:1px solid #293548; color:#94A3B8; }
.badge-nominal { background:#166534; color:#BBF7D0; }
.badge-gate    { background:#FBBF24; color:#1C1403; }
.badge-error, .badge-failed { background:#EF4444; color:#FFFFFF; }
.badge-wait    { background:#A78BFA; color:#1E1633; }
.chip {
  display:inline-flex; align-items:center; gap:7px;
  padding:3px 12px; border-radius:9999px;
  background:#1E293B; border:1px solid #293548;
  font-size:12px; line-height:1.4; color:#64748B;
}
.chip .dot { width:8px; height:8px; border-radius:9999px; border:1px solid #64748B; background:transparent; }
.chip.on { color:#E2E8F0; border-color:#64748B; }
.chip.on .dot { background:#E2E8F0; border-color:#E2E8F0; }
.chip.batch.on .dot { background:#A78BFA; border-color:#A78BFA; }
.chip.warn { color:#FBBF24; border-color:#FBBF24; }
.id-right { margin-left:auto; display:flex; gap:16px; align-items:baseline; }
.freshness .sweep {
  display:inline-block; width:6px; height:6px; border-radius:9999px;
  background:#38BDF8; margin-right:5px; animation: hud-sweep 2s ease-in-out infinite;
}
@keyframes hud-sweep { 0%,100% { opacity:0.35; } 50% { opacity:1; } }

/* ---- Zone 3 · health strip ---- */
.health { display:grid; grid-template-columns:repeat(6, 1fr); gap:8px; padding:12px 16px; }
.tile { background:#1E293B; border:1px solid #293548; border-radius:6px; padding:8px 12px; }
.tile .lbl { font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748B; }
.tile .val { font-size:16px; font-weight:600; letter-spacing:0.01em; font-variant-numeric:tabular-nums; color:#94A3B8; margin-top:2px; }
.tile .sub { font-size:12px; color:#64748B; }
.tile .age { font-size:12px; color:#64748B; margin-top:2px; }
.conf { font-family:'Cascadia Mono', Consolas, monospace; font-size:11px; color:#64748B; border:1px solid #293548; border-radius:4px; padding:0 4px; }
.tile.warn { border-color:#FBBF24; }
.tile.warn .val::after { content:" \\26A0"; color:#FBBF24; }
/* stale veil — dashed amber border, content dimmed to 60%, amber stamp */
.tile.stale { border:1px dashed #FBBF24; }
.tile.stale .lbl, .tile.stale .val, .tile.stale .sub, .tile.stale .age { opacity:0.6; }
.tile .stamp { font-size:12px; line-height:1.4; color:#FBBF24; margin-top:2px; }

/* ---- Zone 4 · main deck ---- */
.deck { display:grid; grid-template-columns:3fr 2fr; gap:16px; padding:4px 16px 12px; align-items:start; }
@media (max-width:1100px) { .deck { grid-template-columns:1fr; } }

.map-group { margin-bottom:12px; }
.map-title { font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748B; padding:6px 2px; border-bottom:1px solid #293548; margin-bottom:4px; }
.node { border-radius:6px; color:#64748B; }
.node > summary { display:flex; align-items:center; gap:10px; padding:4px 8px; cursor:pointer; list-style:none; }
.node > summary::-webkit-details-marker { display:none; }
.node .mark { width:18px; text-align:center; color:#166534; flex:none; }
.node .nid { font-family:'Cascadia Mono', Consolas, monospace; font-size:13px; min-width:118px; flex:none; }
.node .lab { flex:1; }
.node.idle .mark { color:#64748B; }
.node-detail { padding:2px 8px 8px 36px; font-size:12.5px; color:#94A3B8; }
.node-detail .k { color:#64748B; }
.gatebadge { display:inline-block; padding:0 6px; border-radius:4px; font-family:'Cascadia Mono', Consolas, monospace; font-size:11px; border:1px solid #293548; color:#64748B; }
.node.active { background:#38BDF8; color:#06263A; }
.node.active .mark { color:#06263A; }
.node.active .nid { color:#06263A; font-weight:600; }
.node.active .gatebadge { border-color:#06263A; color:#06263A; }
.node.active .dur { font-variant-numeric:tabular-nums; font-weight:600; }
/* paused gate node — master caution outranks the active-cyan accent */
.node.gate-paused { background:#FBBF24; color:#1C1403; outline:1px solid #FBBF24; outline-offset:2px; }
.node.gate-paused .mark { color:#1C1403; }
.node.gate-paused .nid { color:#1C1403; font-weight:600; }
.node.gate-paused .gatebadge { border-color:#1C1403; color:#1C1403; }
.placeholder { padding:14px 12px; border:1px dashed #293548; border-radius:6px; color:#64748B; font-size:13px; }
.placeholder .mark { margin-right:8px; }

/* specialist chip row (trimmed depth per de-scope ladder: no model/cost) */
.spec-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:14px; padding-top:10px; border-top:1px solid #293548; }
.spec { position:relative; border-radius:6px; background:#1E293B; border:1px solid #293548; }
.spec > summary { width:52px; height:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; list-style:none; font-size:13px; font-weight:600; letter-spacing:0.08em; color:#64748B; }
.spec > summary::-webkit-details-marker { display:none; }
.spec .g { position:absolute; top:2px; right:4px; font-size:10px; }
.spec.done { border-color:#166534; } .spec.done .g { color:#166534; }
.spec.run  { border-color:#38BDF8; color:#E2E8F0; } .spec.run .g { color:#38BDF8; }
.spec.warn { border-color:#FBBF24; } .spec.warn .g { color:#FBBF24; }
.spec.awaiting { border-color:#FBBF24; } .spec.awaiting .g { color:#FBBF24; }
.spec.idle .g { color:#64748B; }
.spec-detail { padding:8px 10px; font-size:12px; color:#94A3B8; border-top:1px solid #293548; }

/* right column · briefing cards */
.brief, .gate-brief, .err-brief, .batch-brief, .land-brief, .board {
  background:#1E293B; border:1px solid #293548; border-radius:8px; padding:12px 14px;
}
.brief      { border-left:3px solid #38BDF8; }
.gate-brief { border-left:3px solid #FBBF24; }
.err-brief, .fail-brief  { border-left:3px solid #EF4444; }
.batch-brief { border-left:3px solid #A78BFA; }
.land-brief  { border-left:3px solid #166534; }
.brief > summary { list-style:none; cursor:default; }
.brief > summary::-webkit-details-marker { display:none; }
.bt { font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#E2E8F0; }
.gate-brief .bt { color:#FBBF24; }
.err-brief .bt, .fail-brief .bt { color:#EF4444; }
.batch-brief .bt { color:#A78BFA; }
.land-brief .bt { color:#22C55E; }
.bm { font-size:12px; color:#94A3B8; margin-top:2px; font-variant-numeric:tabular-nums; }
.fields { margin-top:10px; border-top:1px solid #293548; padding-top:8px; }
.frow { display:flex; gap:10px; padding:2px 0; font-size:13px; }
.frow .k { color:#64748B; min-width:120px; flex:none; }
.frow .v { color:#94A3B8; }
.frow .v.mono { font-family:'Cascadia Mono', Consolas, monospace; font-size:12.5px; }
.prompt { margin-top:8px; padding-top:8px; border-top:1px solid #293548; color:#E2E8F0; }
.proposal { margin-top:8px; color:#94A3B8; }
.proposal b { color:#E2E8F0; font-weight:600; }
.artifacts { margin-top:10px; border-top:1px solid #293548; }
.artifact { padding:5px 0; border-bottom:1px solid #293548; font-size:12.5px; color:#94A3B8; }
.artifact .mono { color:#94A3B8; }
.more { margin-top:6px; }
.more > summary { cursor:pointer; color:#64748B; font-size:12px; }

/* command block — the next action; no buttons; fully selectable */
.cmd {
  margin-top:12px;
  background:#0B1120; border:1px solid #38BDF8; border-radius:6px;
  padding:10px 12px;
  font-family:'Cascadia Mono', Consolas, monospace; font-size:13px; line-height:1.5;
  color:#E2E8F0; user-select:all; overflow-wrap:anywhere; white-space:pre-wrap;
}
.cmd-cap { font-size:12px; color:#64748B; margin-top:10px; }

/* pre-flight board */
.phase-title { font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748B; padding-bottom:4px; border-bottom:1px solid #293548; }
.phase-title + .check { margin-top:4px; }
.phase2 { margin-top:14px; }
.check { padding:5px 0; border-bottom:1px solid #29354866; font-size:13px; }
.check > summary { display:flex; align-items:baseline; gap:10px; cursor:pointer; list-style:none; }
.check > summary::-webkit-details-marker { display:none; }
.check:last-child { border-bottom:none; }
.check .mark { width:16px; text-align:center; flex:none; }
.check .name { color:#E2E8F0; min-width:118px; flex:none; }
.check .res { color:#94A3B8; flex:1; }
.check .dur { font-size:12px; color:#64748B; font-variant-numeric:tabular-nums; white-space:nowrap; }
.check.pass .mark { color:#22C55E; }
.check.run  .mark { color:#38BDF8; }
.check.run  .name { color:#E2E8F0; }
.check.fail .mark { color:#EF4444; }
.check.fail .name { color:#EF4444; }
.check.missed .mark { color:#FBBF24; }
.check.pend .mark { color:#64748B; }
.check.pend .name, .check.pend .res { color:#64748B; }
.check-detail { padding:4px 0 2px 26px; font-family:'Cascadia Mono', Consolas, monospace; font-size:12px; color:#94A3B8; white-space:pre-wrap; }
.conf-inline { font-family:'Cascadia Mono', Consolas, monospace; font-size:11px; color:#64748B; border:1px solid #293548; border-radius:4px; padding:0 4px; }

/* panel-level states (no-active-run / binding / unrecognized / refuse) */
.panel-msg { margin:16px; padding:20px 18px; border:1px dashed #293548; border-radius:8px; color:#94A3B8; }
.panel-msg.refuse { border-color:#EF4444; color:#E2E8F0; }
.panel-msg .headline { font-size:15px; font-weight:600; letter-spacing:0.04em; color:#E2E8F0; }
.panel-msg .raw { margin-top:10px; background:#0B1120; border:1px solid #293548; border-radius:6px; padding:10px 12px; font-family:'Cascadia Mono', Consolas, monospace; font-size:12.5px; color:#94A3B8; white-space:pre-wrap; overflow-x:auto; }

/* ---- Zone 5 · state-trace well ---- */
.trace { margin:4px 16px 16px; background:#0B1120; border:1px solid #293548; border-radius:6px; color:#94A3B8; }
.trace > summary { padding:8px 12px; cursor:pointer; list-style:none; font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748B; }
.trace > summary::-webkit-details-marker { display:none; }
.trace pre { font-family:'Cascadia Mono', Consolas, monospace; font-size:12.5px; line-height:1.5; padding:4px 12px 12px; overflow-x:auto; color:#94A3B8; }

@media (prefers-reduced-motion: reduce) {
  .annunciator { transition:none; }
  .freshness .sweep { animation:none; }
}
"""

__all__ = ["CSS"]
