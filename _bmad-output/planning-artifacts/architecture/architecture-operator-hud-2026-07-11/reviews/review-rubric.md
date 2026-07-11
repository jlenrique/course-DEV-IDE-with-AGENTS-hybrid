# Rubric-Walker Review — ARCHITECTURE-SPINE.md (Operator HUD — Flight Deck)

**Reviewer:** rubric walker (good-spine checklist, `.claude/skills/bmad-architecture/references/reviewer-gate.md`)
**Target:** `_bmad-output/planning-artifacts/architecture/architecture-operator-hud-2026-07-11/ARCHITECTURE-SPINE.md` (+ `.memlog.md`)
**Date:** 2026-07-11

## Gate verdict

**CONDITIONAL PASS.** This is a strong, brownfield-accurate spine — every load-bearing code claim spot-checked TRUE, all four party §5.3 mandates covered, versions verified — but it leaves the single most collision-prone dimension silent: **who writes the projection document when, and who owns `seq`**, given that AD-2, AD-10, and AD-11 together prescribe multiple write sites into one file with no merge/ownership rule. Fix that (plus the notifier lifecycle) before stories are cut.

## Brownfield spot-check results (checklist item 5) — all verified

| Claim | Verdict | Evidence |
| --- | --- | --- |
| `_persist_envelope` at `production_runner.py:221` is sole `run.json` writer | **TRUE** | Writer at :222; repo-wide grep shows all other `run.json` refs are reads or path strings (`trial.py:587` reads path, writes only `trial-start.json` at :630) |
| One bypass at ~:3501 (recover reenter) | **TRUE** | Direct `(run_dir / "run.json").write_text(...)` at :3501-3504 |
| `ProductionTrialStatus` seven statuses at `production_trial_envelope.py:19-27` | **TRUE** | Exactly seven, mixed separators (`paused-at-gate` vs `waiting_for_provider_batch`) — spine's "verbatim, mixed separators preserved" convention correctly ratifies this |
| Shape-pin exemplars exist | **TRUE** | `tests/unit/models/test_decision_card_shape_pin.py`, `tests/contracts/test_lesson_plan_json_schema_parity.py` both present |
| import-linter forbids threading in `app/gates` | **TRUE** | `pyproject.toml:187-191` — `app.gates` forbidden `["threading", "apscheduler", "schedule"]`; AD-9's placement of the watchdog outside `app/gates/` is correctly motivated |
| fastapi/uvicorn/requests/jsonschema/pydantic existing deps; pins match Stack table | **TRUE** | `pyproject.toml`: `fastapi>=0.136,<1`, `uvicorn>=0.45,<1`, `requests>=2.31,<3`, `pydantic>=2.7,<3`, `jsonschema>=4.0,<5`, `requires-python >=3.11`. Apprise correctly absent (marked new dep [ASSUMPTION]) |
| Projection path `state/config/runs/<trial_id>/` matches real runs root | **TRUE** | `app/runtime/economics.py:30` — `RUNS_ROOT = REPO_ROOT / "state" / "config" / "runs"` |

Checklist item 4 (named tech verified-current): memlog carries dated `(version)` entries — Apprise v1.9.8 (released 2026-07-04, verified 2026-07-11), Pushover pooling change 2026-05-01, ntfy rate limits, full pyproject stack sweep. **PASS.**

---

## Findings

### CRITICAL

**C1 — Projection write-site / `seq`-ownership ambiguity across AD-2, AD-10, AD-11.** *(Location: AD-2, AD-10, AD-11; checklist items 1 and 2.)*
AD-2 pins emission "inside `_persist_envelope` … every state transition … emits exactly once." AD-11 separately mandates that pre-flight/heartbeat per-item results "are written into the projection **as they complete**" — a second write site, before/outside any envelope transition. AD-10 requires a monotonically increasing `seq` but never says which writer increments it or whether a pre-flight item write bumps it. Nothing states the merge rule for the single document: if the AD-2 emission composes the projection from the envelope (its only argument is `(envelope, runs_root)`), it will **clobber the `preflight` section** an AD-11 write just landed; conversely an AD-11 read-modify-write can race an emission. These are near-certainly different stories built by different dev agents — this is exactly the "two units choose incompatibly" divergence the spine exists to fix, on the paradigm's own namesake invariant (single-writer).
*Suggested fix:* add one Rule (in AD-1 or a new AD): a single in-process `ProjectionWriter`/builder owns the file — all writes (envelope transitions, pre-flight items, state-trace appends) go through it; it alone increments `seq` on every write; it holds the last-written document (or rereads it) so section updates are merges, never regenerate-and-clobber; `_persist_envelope` and the start path both call it. State explicitly whether pre-flight writes bump `seq` (they should — the watchdog and ETag both benefit).

### HIGH

**H1 — Notifier lifecycle/process model silent.** *(Location: AD-9; checklist item 7 — operational envelope.)*
AD-9 defines the notifier's API, inputs, channels, and import fences, but not its runtime shape: separate process? thread in the runtime session? embedded in the HUD server (which AD's dependency arrows would forbid — `notify` and `hud` may not touch each other's internals)? Who launches the projection-watcher, when does it die, what happens when it crashes? AD-7 answers all of this for the HUD server; the notifier gets nothing. Two dev agents (HUD-server story vs notifier story) can and will place it differently.
*Suggested fix:* extend AD-7 (or AD-9) to cover the notifier symmetrically — e.g., "the notifier watcher is a second runtime-session-owned child process (or thread of the HUD server process — pick one), launched by the same start path, dies with the session; crash is non-fatal to the run (fire-and-forget already implies this) but is surfaced in the projection's notification-config-echo section."

**H2 — Dependency arrows have no named enforcement mechanism.** *(Location: Design Paradigm + AD-1/AD-3; checklist item 2.)*
"The contract package imports nothing from orchestrator, hud, or notify; `app/hud/` and `app/notify/` import the contract only — never `production_runner`, never legacy readers" is the spine's structural core, and AD-3's zero-lie rule depends on it — yet no enforcement is specified. This repo's own convention is import-linter contracts (`pyproject.toml:117-358` carries ~15 of them, including the very fence AD-9 cites). Review-only enforcement is how the April HUD drifted.
*Suggested fix:* add to AD-1/AD-3's Rule (or Consistency Conventions): new import-linter `forbidden` contracts land with the packages — `app.hud` and `app.notify` forbidden from `app.marcus.orchestrator`, the legacy `hud_data_sources` reader module, coordination-db access modules, and each other; `app.models.runtime.operator_surface` forbidden from importing `app.marcus`, `app.hud`, `app.notify`. L1 evidence, same tier as the enum test.

**H3 — Projection growth unbounded; memlog's own "soft size target" assumption never made it into the spine.** *(Location: AD-1/AD-3 + Consistency Conventions; checklist items 6 (mandate d: perf/traps budget) and 8 ([ASSUMPTION] carriage).)*
The projection carries append-only state-trace events AND per-reading health history (EXPERIENCE.md §Projection Demands), and the whole document is rewritten at every transition and re-fetched on every ETag change. Over a long run this quietly rebuilds the 525KB-run.json trap the mandate (d) exists to kill. The memlog assumption roster (line 26) explicitly lists "projection soft size target (perf budget)" as an [ASSUMPTION] — but the spine text nowhere carries it. Memlog/spine drift on a claimed assumption is itself a rubric miss.
*Suggested fix:* add a Convention row or AD-1 clause: soft size budget [ASSUMPTION: e.g. ≤256KB] with the pressure valve named — state-trace and health-history sections carry a bounded window in the projection (last N entries) with the full log on disk referenced by path (AD-3 already allows by-reference paths).

### MEDIUM

**M1 — HUD/notifier logging & self-observability silent.** *(Checklist item 7 explicitly names "logging/observability of the HUD itself.")* Conventions say notifier errors go to "local log" — which log, where? Where do uvicorn/server access+error logs go; how does the operator diagnose a HUD that won't render? *Fix:* one Convention row — e.g., both services log to `state/config/runs/<trial_id>/hud-server.log` / `notify.log` (or a named logs dir), rotation story-level.

**M2 — HUD-server failure/restart behavior mid-run silent.** AD-7 gates run start on `/healthz`, but says nothing about the server dying *mid-run* (the run continues fine — projection keeps writing — but the operator's surface silently vanishes, the exact AFK failure class the brief targets). *Fix:* one sentence in AD-7: runtime detects child exit and emits `health_threshold`-class notification (the notifier is independent of the HUD server per H1's resolution, so it can still deliver), plus restart-on-demand semantics (relaunch or `trial hud`).

**M3 — Windows reader/writer contention on `os.replace` unaddressed.** Environment is a local Windows session; `os.replace` onto a file a poller has open can raise `PermissionError` on Windows (open handles without `FILE_SHARE_DELETE`). With a 2–5s poll against every-transition writes, this WILL fire eventually. *Fix:* Convention row: writer retries replace briefly with backoff; consumers open-read-close immediately and treat a torn/failed read as "keep last good + staleness banner" (never crash, never blank).

**M4 — The one open question lives only in the memlog; the spine has no Open Questions section.** Memlog line 27 (does the runtime start path have a natural child-process launch + phase-02 heartbeat point?) is a real undecided dimension of AD-7/AD-11. Checklist: every owned dimension must be "decided, deferred, or an open question" **in the spine**. *Fix:* add an "Open Items" line under Deferred (or a section) carrying it, marked dev-phase discovery.

**M5 — Sound-channel execution locus unspecified.** AD-9 lists "sound" as a channel; nobody says whether it plays in the browser page (HUD view — but then it's not a notifier channel) or on the host from the notifier process. Two devs will pick differently. *Fix:* one clause — e.g., sound is a view-side behavior driven by projection/notification state (keeps the notifier headless), or host-side via notifier; pick one.

### LOW

**L1 — Paradigm prose vs diagram wording nit.** "`app/hud/` … import the contract only" strictly contradicts the diagram's `HUDSERVER --> HUDVIEW` edge (server imports the view's render/data). Intent is clearly "hud and notify never import each other or the producer" — say that.

**L2 — ETag = mtime+size can miss a same-size rewrite within mtime granularity.** `seq` is already in the document (AD-10) — deriving ETag from `seq` (or including it) is strictly stronger and free.

**L3 — AD-2's "a direct run.json write anywhere is a defect" has no tripwire.** Cheap to pin: a grep-lint or unit test asserting `production_runner.py` contains exactly one `run.json` write expression (or that all writes route through `_persist_envelope`). Same spirit as the AD-5 reverse tripwire.

**L4 — Multi-trial-per-session identity unstated.** AD-7 server binds one `trial_id` and survives run completion for the session; if the operator starts a second trial in the same session, is a second server launched on another port, or rebound? Probably story-level, but one sentence prevents a guess.

**L5 — Frontmatter `status: draft`.** Complete otherwise (name/type/purpose/altitude/paradigm/scope/binds/sources/companions all present); flip to ratified at finalize or the field lies.

---

## Checklist walk (summary)

1. **Divergence points fixed, none missed:** mostly excellent — the contract/dual-pin/identity/retire-path/transport calls each kill a named April failure — but C1 (projection write-site/seq ownership), H1 (notifier lifecycle), M5 (sound locus) are silent divergence points between plausible story pairs. **CONDITIONAL.**
2. **Every AD Rule enforceable + prevents its divergence:** AD-2/4/5/6/8/13/14 have named tests/tripwires. AD-1/AD-3's import discipline has no mechanism (H2); AD-2's "defect anywhere" has no tripwire (L3). **CONDITIONAL.**
3. **Deferred cannot let two units diverge:** clean — every deferred item is either bounded by a contract rule (SSE must not change the projection; heartbeat mechanics bounded by AD-11 confidence rules) or genuinely config-level. **PASS.**
4. **Named tech verified-current:** memlog dated version entries for Apprise/Pushover/ntfy + full pyproject sweep; Stack table matches pyproject exactly. **PASS.**
5. **Ratifies brownfield:** all six spot-checks TRUE (table above); also correctly ratifies runs-root path, two-walk gotcha, xdist serial/live marking, Tier-2 manifest governance per CLAUDE.md lockstep regime. **PASS.**
6. **Driving inputs covered:** party §5.3 (a) → AD-1/2/4; (b) → AD-6 (+ lifecycle decided in AD-7 as the plan demanded); (c) → AD-8 + retire story; (d) → AD-3 + mtime-gated conventions (LangSmith out, run.json parse banned outright — stronger than asked), except the projection's own size budget (H3). EXPERIENCE.md §Projection Demands: all ten bullets land via AD-3's incorporation-by-reference plus the Capability Map (identity/preflight/steps/next-action/health/state-trace rows all present); the reference is made binding by the dual shape-pins, so acceptable. **PASS with H3.**
7. **Every owned dimension decided/deferred/open — operational envelope:** deployment (local, child of runtime session) ✓, ports ✓, config ✓, credentials ✓, HUD-server lifecycle ✓ — but notifier lifecycle (H1), HUD logging (M1), mid-run failure/restart (M2), Windows file contention (M3), and the memlog-only open question (M4) are silent/misplaced. **CONDITIONAL.**
8. **Mermaid/frontmatter/[ASSUMPTION]:** Mermaid `graph TD` valid (quoted labels, `-.push.->` dotted-labeled edge legal). Frontmatter complete (L5 status nit). [ASSUMPTION] tags properly carried for port/CLI/stall-budget/Apprise — one memlog assumption (size target) dropped (folded into H3). **PASS with nits.**

## Disposition recommendation

Autofix at Finalize: C1, H1, H2, H3 (each is a one-clause Rule addition, no redesign), M1–M5 one-liners. L1–L5 at author's discretion. Nothing here requires reopening an ADOPTED party mandate — every fix composes on top of them.
