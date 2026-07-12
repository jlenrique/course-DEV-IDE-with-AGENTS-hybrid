"""Client-side poll renderer (Story 35.5) — DECISION of record.

**Decision:** the server renders the full page for the COLD load
(``render_page`` on ``GET /``); the browser then polls ``GET /projection``
(ETag ``If-None-Match``, RFC-quoted per 35.4) and re-renders the *dynamic*
zones **client-side** from the projection JSON with this small vanilla-JS
renderer, mirroring ``render_zones`` for the dynamic bits (annunciator
text+class, identity badge + freshness age, health tile values/ages, map
current-step, briefing swap). No framework, no build step, no buttons.

Replacement is **zone-scoped innerHTML** (de-scope ladder: no granular DOM
diffing). A zone is replaced only when its freshly-built HTML differs from what
is installed (content-hash compare via string equality), so ``<details>`` open
state, scroll, and an active text selection inside an *unchanged* zone all
survive. When a changed zone carries ``<details>`` we capture open-state by key
and re-apply it after replacement, with the urgency auto-expand contract
(``data-auto-open="urgent"`` → forced open) winning over remembered collapse —
carried forward verbatim from ``hud_per_step_summary.py`` / ``run_hud.py``.

This is a pure string constant (no Python imports) embedded by ``page.py``. It
is exercised live in the 35.7 witness checklist (amendment 10); the Python
``render_zones`` is the byte-pinned source of truth under golden test.
"""

from __future__ import annotations

POLL_JS = r"""
(function () {
  "use strict";
  var POLL_MS = 3000;
  var etag = null;
  var lastZones = {};

  function esc(s) {
    if (s === null || s === undefined) return "";
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
  }
  function parseDt(v) {
    if (!v) return null;
    var d = new Date(String(v).replace("Z", "+00:00"));
    return isNaN(d.getTime()) ? null : d;
  }
  function clock(v) {
    var d = parseDt(v);
    if (!d) return esc(v);
    function p(n) { return (n < 10 ? "0" : "") + n; }
    return p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds());
  }
  function ageStamp(asOf, now) {
    var a = parseDt(asOf), n = parseDt(now);
    var c = clock(asOf);
    if (!a || !n) return c ? "as of " + c : "";
    return "as of " + c + " · " + Math.floor((n - a) / 1000) + "s ago";
  }

  var STATUS_SYMBOL = {
    "registered": "○", "in-flight": "▶", "paused-at-gate": "⏸",
    "paused-at-error": "⛔", "waiting_for_provider_batch": "⚖",
    "completed": "✓", "failed": "⛔"
  };
  var BADGE = {
    "registered": "badge-dim", "in-flight": "badge-nominal", "completed": "badge-dim",
    "paused-at-gate": "badge-gate", "paused-at-error": "badge-error",
    "waiting_for_provider_batch": "badge-wait", "failed": "badge-failed"
  };
  var DONE = ["completed", "complete", "done", "pass", "passed", "ok", "exited", "success"];
  var ACTIVE = ["active", "running", "in-progress", "in_progress", "current", "walking", "in-flight"];

  function activeEntry(steps) {
    if (!steps || !steps.entries) return null;
    for (var i = 0; i < steps.entries.length; i++) {
      var e = steps.entries[i];
      if (e && ACTIVE.indexOf(String(e.status || "").toLowerCase()) >= 0) return e;
    }
    return null;
  }

  // ---- annunciator ----
  function annunciator(d, now) {
    var env = d.envelope || {}, st = env.status, steps = d.steps;
    var a = activeEntry(steps), walking = st === "in-flight" && a;
    var cls = "ann-nominal", sym = "▶", text = "";
    if (st === "paused-at-gate") { cls = "ann-gate"; sym = "⏸"; text = "PAUSED AT GATE " + esc(env.paused_gate || "?"); }
    else if (st === "paused-at-error") { cls = "ann-error"; sym = "⛔"; text = "PAUSED AT ERROR — " + esc(env.paused_error_tag || "?"); }
    else if (st === "waiting_for_provider_batch") { cls = "ann-wait"; sym = "⚖"; text = "PARKED — PROVIDER BATCH " + esc(env.waiting_batch_id || "?"); }
    else if (st === "failed") { cls = "ann-failed"; sym = "⛔"; text = "FAILED — " + esc(env.paused_error_tag || "run failed"); }
    else if (st === "completed") { cls = "ann-completed"; sym = "✓"; text = "LANDED — completed " + clock(env.completed_at); }
    else if (st === "registered") { cls = "ann-nominal"; sym = "○"; text = "REGISTERED — awaiting pre-flight"; }
    else if (st === "in-flight") {
      if (walking) { sym = "▶"; text = "IN FLIGHT — " + esc(a.step_id) + " · " + esc(a.label); }
      else { sym = "◐"; text = "PRE-FLIGHT IN PROGRESS"; }
    } else { cls = "ann-idle"; sym = "○"; text = "UNRECOGNIZED STATUS '" + esc(st) + "'"; }
    return '<div class="annunciator ' + cls + '" role="status" aria-live="polite">' +
      '<span class="sym">' + sym + '</span><span>' + text + "</span></div>";
  }

  // ---- identity header ----
  function chip(label, on, batch) {
    var c = on ? "chip on" : "chip";
    if (batch) c += " batch";
    return '<span class="' + c + '"><span class="dot"></span> ' + esc(label) + "</span>";
  }
  function identity(d, now) {
    var id = d.identity || {}, st = (d.envelope || {}).status;
    var sym = STATUS_SYMBOL[st] || "○", bc = BADGE[st] || "badge-dim";
    var badge = st ? '<span class="badge ' + bc + '"><span>' + sym + "</span> " + esc(st) + "</span>" : "";
    var m = d.modalities || {}, mode = String(m.llm_execution_mode || "").toLowerCase();
    var chips = chip("BATCH", mode.indexOf("batch") >= 0, true) +
      chip("DETECTIVE", !!m.detective_disposition, false) +
      chip(m.styleguide || "styleguide", !!m.styleguide, false);
    var echo = d.notifications_echo || {}, notif = "";
    if (echo.parse_status && echo.parse_status !== "ok")
      notif = '<span class="chip warn">⚠ ' + esc(echo.parse_status) + "</span>";
    return '<header class="id-header">' +
      '<span class="mono trial">' + esc(id.trial_id) + "</span>" +
      '<span class="kv">lesson <b>' + esc(id.lesson) + "</b></span>" +
      '<span class="kv">preset <b>' + esc(id.preset) + "</b></span>" +
      badge + chips + notif +
      '<span class="id-right freshness"><span class="meta"><span class="sweep"></span>snapshot ' +
      esc(ageStamp(d.as_of, now)) + "</span></span></header>";
  }

  // ---- health strip ----
  function health(d, now, budget) {
    var h = d.health, tiles = (h && h.tiles) || [];
    if (!tiles.length) return '<section class="health" aria-label="health strip"></section>';
    var out = "";
    for (var i = 0; i < tiles.length; i++) {
      var t = tiles[i]; if (!t) continue;
      var val = esc(t.value) + (t.unit ? " " + esc(t.unit) : "");
      var thr = String(t.threshold_state || "");
      var a = parseDt(t.as_of), n = parseDt(now);
      var secs = (a && n) ? Math.floor((n - a) / 1000) : null;
      var stale = secs !== null && secs > budget;
      var cls = "tile" + (thr === "warning" || thr === "breached" ? " warn" : "") + (stale ? " stale" : "");
      var body = '<div class="lbl">' + esc(t.label) + "</div>" +
        '<div class="val">' + val + "</div>" +
        '<div class="sub">' + (t.confidence ? '<span class="conf">' + esc(t.confidence) + "</span>" : "") + "</div>";
      if (stale) body += '<div class="stamp">⧗ STALE · last good ' + clock(t.as_of) + " (" + secs + "s ago)</div>";
      else body += '<div class="age">' + esc(ageStamp(t.as_of, now)) + "</div>";
      out += '<div class="' + cls + '">' + body + "</div>";
    }
    return '<section class="health" aria-label="health strip">' + out + "</section>";
  }

  // ---- map + context ----
  var STEP_MARK = { "done": "✓", "active": "▶", "gate-paused": "⏸", "idle": "○" };
  function stepKind(e, active, st) {
    if (e === active) return st === "paused-at-gate" ? "gate-paused" : "active";
    if (DONE.indexOf(String(e.status || "").toLowerCase()) >= 0) return "done";
    return "idle";
  }
  function mapNode(e, active, d) {
    var st = (d.envelope || {}).status, kind = stepKind(e, active, st);
    var cond = e.conditions || [], block = e.blockers || [];
    var urgent = e === active || cond.length || block.length;
    var openAttr = urgent ? " open" : "", auto = urgent ? ' data-auto-open="urgent"' : "";
    var nid = esc(e.step_id), did = ("node-" + nid).replace(/[. ]/g, "-");
    var gb = "";
    if (kind === "gate-paused" && (d.envelope || {}).paused_gate)
      gb = '<span class="gatebadge">⏸ ' + esc(d.envelope.paused_gate) + "</span>";
    var locked = e.locked_artifact_summary;
    var detail = '<div class="frow"><span class="k">locked artifact</span><span class="v mono">' +
      (locked ? esc(locked) : "no locked artifact yet") + "</span></div>";
    if (cond.length) detail += '<div class="frow"><span class="k">conditions</span><span class="v">' + esc(cond.join(", ")) + "</span></div>";
    if (block.length) detail += '<div class="frow"><span class="k">blockers</span><span class="v">' + esc(block.join(", ")) + "</span></div>";
    return '<details id="' + did + '" data-step-summary-id="' + did + '" class="node ' + kind + '"' + auto + openAttr + ">" +
      '<summary><span class="mark">' + STEP_MARK[kind] + '</span><span class="nid">' + nid +
      '</span><span class="lab">' + esc(e.label) + "</span>" + gb + "</summary>" +
      '<div class="node-detail">' + detail + "</div></details>";
  }
  function mapZone(d) {
    var steps = d.steps;
    if (!steps) return '<section aria-label="you-are-here map"><div class="map-group">' +
      '<div class="map-title">Ratified workflow</div><div class="placeholder"><span class="mark">○</span>' +
      "workflow pends ratification — steps will appear here after G0R</div></div></section>";
    var active = activeEntry(steps), entries = steps.entries || [];
    var s1 = [], s2 = [], i;
    for (i = 0; i < entries.length; i++) { if (entries[i].stage === "stage-1") s1.push(entries[i]); else if (entries[i].stage === "stage-2") s2.push(entries[i]); }
    var out = '<section aria-label="you-are-here map">';
    if (s1.length) { out += '<div class="map-group"><div class="map-title">Planning — intake &amp; ratification</div>'; for (i = 0; i < s1.length; i++) out += mapNode(s1[i], active, d); out += "</div>"; }
    var title = "Ratified workflow" + (steps.node_count ? " — " + esc(steps.node_count) + " nodes" : "");
    if (steps.walk_index !== undefined && steps.node_count) title += " · Step " + esc(steps.walk_index) + "/" + esc(steps.node_count);
    if (s2.length) { out += '<div class="map-group"><div class="map-title">' + title + "</div>"; for (i = 0; i < s2.length; i++) out += mapNode(s2[i], active, d); out += "</div>"; }
    else out += '<div class="map-group"><div class="map-title">Ratified workflow</div><div class="placeholder"><span class="mark">○</span>workflow pends ratification — steps will appear here after G0R</div></div>';
    return out + "</section>";
  }
  var SPEC_GLYPH = { "active": ["run", "▶"], "running": ["run", "▶"], "done": ["done", "✓"], "completed": ["done", "✓"], "degraded": ["warn", "⚠"], "retrying": ["warn", "⚠"], "awaiting": ["awaiting", "⏸"] };
  function specialists(d) {
    var s = d.specialists, roster = (s && s.roster) || [];
    if (!roster.length) return "";
    var out = "";
    for (var i = 0; i < roster.length; i++) {
      var sp = roster[i], g = SPEC_GLYPH[String(sp.status || "").toLowerCase()] || ["idle", "○"];
      var mono = (String(sp.name || "??").replace(/[^a-zA-Z0-9]/g, "").slice(0, 2) || "??").toUpperCase();
      out += '<details class="spec ' + g[0] + '"><summary>' + esc(mono) + '<span class="g">' + g[1] + "</span></summary>" +
        '<div class="spec-detail">' + esc(sp.name) + " · " + esc(sp.status) +
        '<br>node <span class="mono">' + esc(sp.current_node || "—") + "</span>" +
        '<br>last <span class="mono">' + esc(sp.last_artifact || "—") + "</span></div></details>";
    }
    return '<div class="spec-row" aria-label="specialist roster">' + out + "</div>";
  }
  function cmdBlock(cmd, cap) {
    if (!cmd) return "";
    return '<div class="cmd-cap">' + esc(cap) + '</div><div class="cmd">' + esc(cmd) + "</div>";
  }
  function context(d, now) {
    var env = d.envelope || {}, st = env.status, na = d.next_action || {};
    var active = activeEntry(d.steps);
    if (st === "paused-at-gate") {
      var locked = active && active.locked_artifact_summary;
      var art = locked ? '<div class="artifacts"><div class="artifact"><span class="mono">' + esc(locked) + "</span></div></div>" : "";
      return '<div class="gate-brief"><div class="bt">⏸ Gate ' + esc(env.paused_gate) + "</div>" +
        '<div class="bm">' + esc(ageStamp(env.as_of, now)) + "</div>" +
        '<div class="prompt">Gate ' + esc(env.paused_gate) + " awaits your verdict. Decide via the Marcus-SPOC surface using the command below.</div>" +
        art + cmdBlock(na.command, "paste into the Marcus-SPOC surface — digest pre-filled:") + "</div>";
    }
    if (st === "paused-at-error") {
      var steps = d.steps || {};
      return '<div class="err-brief"><div class="bt">⛔ Paused at error</div>' +
        '<div class="bm">' + esc(ageStamp(env.as_of, now)) + "</div><div class=\"fields\">" +
        '<div class="frow"><span class="k">error tag</span><span class="v mono">' + esc(env.paused_error_tag) + "</span></div>" +
        '<div class="frow"><span class="k">node</span><span class="v mono">' + esc(active && active.step_id) + " · walk " + esc(steps.walk_index) + "</span></div>" +
        "</div>" + cmdBlock(na.command, "recover command:") + "</div>";
    }
    if (st === "waiting_for_provider_batch") {
      return '<div class="batch-brief"><div class="bt">⚖ Provider batch parked</div>' +
        '<div class="bm">batch ' + esc(env.waiting_batch_id) + " · " + esc(ageStamp(env.as_of, now)) + "</div>" +
        '<div class="prompt">LiteLLM provider batch — resume polls the batch. Nothing is wrong; no verdict is owed.</div>' +
        cmdBlock(na.command, "resume command:") + "</div>";
    }
    if (st === "completed") {
      var roster = (d.specialists && d.specialists.roster) || [], rows = "";
      for (var i = 0; i < roster.length; i++) if (roster[i].last_artifact) rows += '<div class="artifact"><span class="mono">' + esc(roster[i].last_artifact) + "</span></div>";
      if (!rows) rows = '<div class="artifact">see run dir for exports</div>';
      return '<div class="land-brief"><div class="bt">✓ Landed</div><div class="bm">completed ' + clock(env.completed_at) + "</div>" +
        '<div class="artifacts">' + rows + "</div></div>";
    }
    if (st === "failed") {
      var tail = na.command ? cmdBlock(na.command, "recovery command:") : '<div class="prompt">no automated recovery — see SPOC</div>';
      return '<div class="fail-brief"><div class="bt">⛔ Failed</div><div class="bm">' + esc(ageStamp(env.as_of, now)) + "</div>" +
        '<div class="fields"><div class="frow"><span class="k">reason</span><span class="v mono">' + esc(env.paused_error_tag || "run failed") + "</span></div></div>" + tail + "</div>";
    }
    if (st === "in-flight" && active) {
      var steps2 = d.steps || {}, lk = active.locked_artifact_summary;
      var fields = '<div class="frow"><span class="k">locked artifact</span><span class="v mono">' + (lk ? esc(lk) : "no locked artifact yet") + "</span></div>";
      return '<details class="brief" open><summary><div class="bt">' + esc(active.step_id) + " · " + esc(active.label) + "</div>" +
        '<div class="bm">walk index ' + esc(steps2.walk_index) + '</div></summary><div class="fields">' + fields + "</div></details>";
    }
    // registered / preflight
    var pf = d.preflight, items = (pf && pf.items) || [], out = "";
    var CLS = { "pass": "pass", "running": "run", "fail": "fail", "missed": "missed", "pending": "pend" };
    var MK = { "pass": "✓", "running": "◐", "fail": "✕", "missed": "⧗", "pending": "○" };
    for (var j = 0; j < items.length; j++) {
      var it = items[j], state = String(it.state || "pending");
      var res = esc(it.output || it.quota_reading || "");
      if (it.quota_confidence && it.quota_confidence !== "unknown") res += ' · <span class="conf-inline">' + esc(it.quota_confidence) + "</span>";
      out += '<details class="check ' + (CLS[state] || "pend") + '"><summary><span class="mark">' + (MK[state] || "○") +
        '</span><span class="name">' + esc(it.name) + '</span><span class="res">' + res +
        '</span><span class="dur">' + (it.latency_ms != null ? esc(it.latency_ms) + "ms" : "—") + "</span></summary></details>";
    }
    if (!out) out = '<div class="check pend"><span class="res">pre-flight pending</span></div>';
    return '<div class="board"><div class="phase-title">Pre-flight · Readiness</div>' + out + "</div>";
  }
  function mainDeck(d, now) {
    return '<main class="deck"><section class="mapcol">' + mapZone(d) + specialists(d) +
      '</section><aside class="ctxcol" aria-label="context panel">' + context(d, now) + "</aside></main>";
  }
  function trace(d) {
    var t = d.trace, events = (t && t.events) || [];
    if (!events.length) return '<details class="trace"><summary>State trace — 0 events · newest last</summary><pre>no events yet</pre></details>';
    var lines = [];
    for (var i = 0; i < events.length; i++) {
      var ev = events[i], line = clock(ev.at) + "  " + esc(ev.event);
      if (ev.detail) line += " · " + esc(ev.detail);
      lines.push(line);
    }
    return '<details class="trace"><summary>State trace — ' + events.length + " events · newest last</summary><pre>" + lines.join("\n") + "</pre></details>";
  }

  // ---- zone-scoped replacement (preserve disclosure / scroll / selection) ----
  function selectionInside(el) {
    var sel = window.getSelection && window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return false;
    return el.contains(sel.anchorNode);
  }
  function applyZone(id, htmlStr) {
    if (lastZones[id] === htmlStr) return;            // unchanged → never touch (keeps selection/scroll)
    var el = document.getElementById(id);
    if (!el) return;
    if (selectionInside(el) && lastZones[id] !== undefined) return;  // hold a live selection
    var open = {};
    el.querySelectorAll("details").forEach(function (dEl, i) {
      open[dEl.getAttribute("data-step-summary-id") || dEl.id || String(i)] = dEl.open;
    });
    el.innerHTML = htmlStr;
    el.querySelectorAll("details").forEach(function (dEl, i) {
      var key = dEl.getAttribute("data-step-summary-id") || dEl.id || String(i);
      if (dEl.getAttribute("data-auto-open") === "urgent") { dEl.open = true; return; }
      if (open[key] !== undefined) dEl.open = open[key];
    });
    lastZones[id] = htmlStr;
  }
  function setAnnun(cls, text) {
    var el = document.getElementById("annunciator");
    if (el) el.innerHTML = '<div class="annunciator ' + cls + '" role="status" aria-live="polite"><span class="sym">•</span><span>' + esc(text) + "</span></div>";
  }
  function renderZones(d) {
    var now = new Date().toISOString();
    applyZone("annunciator", annunciator(d, now));
    applyZone("identity-header", identity(d, now));
    applyZone("health-strip", health(d, now, 60));
    applyZone("main-deck", mainDeck(d, now));
    applyZone("state-trace", trace(d));
  }

  async function poll() {
    var headers = {};
    if (etag) headers["If-None-Match"] = etag;
    var resp;
    try {
      resp = await fetch("/projection", { headers: headers, cache: "no-store" });
    } catch (err) {
      // Transport failure only — never a render/parse fault.
      setAnnun("ann-feedlost", "DISCONNECTED" + " · " + err);
      return;
    }
    if (resp.status === 304) return;
    var newEtag = resp.headers.get("ETag");
    if (resp.status === 409) {
      etag = newEtag;
      var body = await resp.json();
      setAnnun("ann-warning", "RUN IDENTITY UNCERTAIN — refusing to render (bound " + body.bound + " · found " + body.found + ")");
      return;
    }
    if (resp.status === 404) { setAnnun("ann-idle", "BINDING — awaiting first snapshot"); return; }
    if (!resp.ok) { setAnnun("ann-feedlost", "HUD FEED LOST — HTTP " + resp.status); return; }
    var bare = (newEtag || "").replace(/^[Ww]\//, "").replace(/"/g, "");
    if (bare.startsWith("unrecognized:")) {
      // Honest state keyed off the ETag — non-JSON / unknown-schema 200s render
      // UNRECOGNIZED literally, never a parse-throw into the transport branch.
      var text = await resp.text();
      etag = newEtag;
      setAnnun("ann-idle", "UNRECOGNIZED" + " · " + text.slice(0, 200));
      return;
    }
    var data;
    try {
      data = await resp.json();
    } catch (err2) {
      etag = null;  // render failed: do not cache, retry fresh next poll
      setAnnun("ann-idle", "UNRECOGNIZED" + " · body did not parse");
      return;
    }
    etag = newEtag;
    if (!data || !data.envelope || !data.envelope.status) {
      setAnnun("ann-idle", "UNRECOGNIZED" + " · schema_version " + (data && data.schema_version));
      return;
    }
    renderZones(data);
  }

  poll();
  setInterval(poll, POLL_MS);
})();
"""

__all__ = ["POLL_JS"]
