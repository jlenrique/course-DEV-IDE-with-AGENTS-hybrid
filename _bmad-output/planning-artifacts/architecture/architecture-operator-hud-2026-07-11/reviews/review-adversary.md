---
review: adversary (finalize reviewer #2)
target: ../ARCHITECTURE-SPINE.md
method: construct pairs of one-level-down units that each obey every AD to the letter yet build incompatibly
date: 2026-07-11
evidence-base: production_runner.py (read), trial.py start path (read), production_trial_envelope.py (read), EXPERIENCE.md (read), pipeline-manifest.yaml + check_pipeline_manifest_lockstep.py (read), state/config listing (hud-config.yaml does not exist yet)
verdict: NOT READY — the spine's write-model has a load-bearing contradiction (AD-2's single write-point cannot produce what AD-3/AD-11 and the UX staleness budgets demand), and three more critical/high seams let letter-compliant units clash. 18 findings: 3 Critical, 6 High, 7 Low/Medium closable with new or tightened ADs; no paradigm change required.
---

# Adversarial Review — Operator HUD Architecture Spine

Attack protocol: for each seam, construct two units one level down (the epic/story cut list: ①projection contract + emission, ②HUD server + reader, ③render retarget, ④notifier + watchdog, ⑤pre-flight/heartbeat start path, ⑥legacy-reader retirement, ⑦Tier-2 manifest bump) that each satisfy every AD verbatim and still build incompatibly. Every pair found is a hole; each finding names the AD to add or tighten.

---

## CRITICAL

### F1 — `_persist_envelope` cannot see what the projection must carry

**Units:** ① projection contract vs ① emission in `_persist_envelope`.
**The letter:** AD-2 — "the projection is written inside `_persist_envelope` (production_runner.py:221)". AD-3 + Capability Map + EXPERIENCE.md §Projection Demands — the projection carries steps + walk index, pre-flight/heartbeat items, health readings with history, specialist roster activity, decision card + exact command strings, modality readings, state-trace events.
**Incompatible builds:** `_persist_envelope(envelope, runs_root)` (line 221) receives **only the envelope**. The envelope model has none of: composed manifest / walk index (local to the walk loops), pre-flight results, cost/health history, specialist activity, state-trace. Contract-unit dev models `OperatorSurfaceProjection` with those sections required (they are "demands"); emission-unit dev writes the projection from the envelope alone — the only data at the mandated call-site. Result A: Pydantic validation fails at every `_persist_envelope` call (run dies on its own instrument). Result B: emission dev makes every non-envelope section `Optional` and emits `None` — a projection that satisfies the schema and lies by omission, the exact April failure with a v1 stamp on it.
**Severity:** Critical.
**Close with:** new AD — **Projection assembler is the single writer.** A runtime-owned `OperatorSurfaceAssembler` (contract-typed, producer-instantiated per trial) accumulates sections as the walk supplies them (steps on manifest composition, preflight items as tested, health on refresh, trace on event); `_persist_envelope` calls `assembler.emit(envelope)` — the choke-point survives, but the AD must name the assembler as the entity that owns non-envelope sections, and must define per-lifecycle-stage presence rules (which sections may be absent at `registered`, which are mandatory once `in-flight`). AD-2's rule text changes from "written inside `_persist_envelope`" to "emitted via the assembler, whose transition-emit call lives inside `_persist_envelope`".

### F2 — AD-2's single write-point vs AD-11's per-item writes vs the UX staleness budgets

**Units:** ① emission vs ⑤ pre-flight execution (and the view's staleness veil in ③).
**The letter:** AD-2 — projection written inside `_persist_envelope`, "every state transition … emits exactly once". AD-11 — pre-flight/heartbeat per-item results "are written into the projection **as they complete**". EXPERIENCE.md zero-lie rule 2 — run-state staleness budget **5s**, health tiles **60s**; Flow 1 renders rows "○ → ◐ → ✓ in real time"; Flow 2 shows "cost $0.31 · 8s ago" mid-node.
**Incompatible builds:** a pre-flight item completing is **not** an envelope transition — no `_persist_envelope` fires. Unit-⑤ dev, obeying AD-11, writes the projection file directly per item. Unit-① dev, obeying AD-2's "a direct run.json write anywhere is a defect" spirit, ships a tripwire test asserting the projection has exactly one writer call-site — and unit ⑤ fails it; or nobody ships the tripwire and two uncoordinated writers `os.replace` the same file (last-writer-wins clobbers whole sections, since each writes a full snapshot from different in-memory views). Independently: with transition-only emission, any node longer than 5s puts the run-state feed past its staleness budget — the flagship five-second glance renders **permanently amber-veiled** during nominal flight. Both units letter-compliant; the product is impossible as specced.
**Severity:** Critical.
**Close with:** tighten AD-2 into an **emission-cadence AD**: enumerate the three legal emit triggers — (a) envelope transition (inside `_persist_envelope`), (b) section update (preflight item, health refresh, trace append) via the F1 assembler, (c) a periodic freshness tick while `in-flight` at interval ≤ min staleness budget (e.g., 2s) — all funneled through **one** assembler API holding one write lock, single process. Add the tripwire as an AD-level L1 obligation: any projection write not routed through the assembler fails CI.

### F3 — Pre-flight `/healthz` gate passes against the wrong server (April fallback reborn one level up)

**Units:** ⑤ pre-flight execution vs ② HUD server + the AD-7 standalone `trial hud` CLI.
**The letter:** AD-7 — "HUD server ready (GET /healthz 200) is a pre-flight checklist item"; "a standalone `trial hud --trial-id <id>` CLI may serve an existing run dir". AD-6 — port from config key `hud.port`, default 8791.
**Incompatible builds:** both the session-child server and the standalone CLI read the same `hud.port`. Scenario: yesterday's run landed; operator ran `trial hud --trial-id <old>` for post-hoc viewing and left it up (the UX calls the page "always-on"). Today's runtime start path launches its child server — **bind fails, port taken**. Unit ⑤'s pre-flight item GETs `http://localhost:8791/healthz` → **200** — from the standalone server bound to the *old* trial. Pre-flight passes, SPOC spawns, and the always-on browser page on :8791 renders yesterday's run while today's flies dark. Every AD obeyed to the letter; the silent wrong-run fallback AD-8 exists to kill is reconstructed at the server level.
**Severity:** Critical.
**Close with:** tighten AD-7/AD-8: (a) `/healthz` returns `{trial_id, launch_nonce, mode: session|standalone}`; the pre-flight item passes only on **trial_id match** with the nonce the start path minted when it spawned the child; (b) child bind failure = pre-flight FAIL, never fall through to whatever answers the port; (c) the standalone CLI defaults to an ephemeral port and **refuses** `hud.port` if in use; (d) the L2 fixture set includes wrong-server-on-port.

---

## HIGH

### F4 — Crash between run.json persist and projection write: two documents, two truths, no reconciliation

**Units:** ① emission vs ② HUD reader / ④ notifier.
**The letter:** AD-2 — projection written "immediately after run.json persists" (two files, no transaction). AD-1/AD-3 — the projection is the **only** input downstream; "if the projection doesn't say it, downstream doesn't show it."
**Incompatible builds:** unit ① treats the projection as a derived cache of run.json (correct per AD-2 ordering); units ②/④ treat it as sole truth (correct per AD-1). Runner crashes in the window: run.json says `paused-at-gate`, projection says `in-flight`. The HUD shows IN FLIGHT, the `paused_at_gate` push never fires, and nothing ever repairs the skew — the next `_persist_envelope` only happens after the operator acts on a pause they were never told about. The watchdog eventually fires `run_stalled` (a lucky, mislabeled backstop), or doesn't if the crash also took the notifier (F7).
**Severity:** High.
**Close with:** new AD — **run.json is truth; projection is a reconciled derivation.** (a) Projection carries `envelope_digest` (sha of the run.json content it was derived from). (b) Every runner entry point — start, `continue`, recover, resume-batch, status — re-emits the projection from the current envelope before doing anything else (idempotent reconcile; cheap). (c) L2 fixture: run dir with skewed pair must render the run.json-derived state after any runner touch, and the HUD alone (no runner touch) must surface staleness, never invent agreement.

### F5 — `seq` has two owners: "write counter" vs "progress"

**Units:** ① emission vs ④ watchdog.
**The letter:** AD-10 — projection carries monotonically increasing `seq`; watchdog fires `run_stalled` when `in-flight` and "`seq` hasn't advanced within the configured budget"; "monotonicity of the single document is the heartbeat."
**Incompatible builds:** after F2's cadence fix, the producer bumps `seq` on **every** write — including the 2s freshness tick and 60s health refreshes. Unit-④ dev, obeying AD-10 verbatim, watches `seq`: it now advances forever while the walk is wedged inside a hung specialist call — **`run_stalled` can never fire**; the AD's own mechanism defeats the AD's purpose. Flip the build: producer bumps `seq` only on envelope transitions — any node longer than 600s (Gamma export, batch composition) fires a **false stall** while genuinely nominal. Both readings are the letter.
**Severity:** High.
**Close with:** tighten AD-10: split the counters — `seq` = write counter (feeds ETag, F17), `last_progress_at` + `progress_seq` = advances **only** on walk-index change, node-lifecycle event, preflight-item completion, or gate/pause/resume transition; freshness ticks and health refreshes are forbidden from bumping it (L1 test). Watchdog binds to `progress_seq` exclusively. Optionally per-node stall budgets (a batch-mode node legitimately parks; `waiting_for_provider_batch` already exempt since status ≠ `in-flight`).

### F6 — The five event classes get two independent implementations (push vs toast)

**Units:** ④ notifier vs ③ view.
**The letter:** AD-9 — the notifier "derives the five v1 event classes from projection transitions"; same AD — the on-HUD channel is "rendered from projection state, **not from the notifier**". EXPERIENCE.md — toast per enabled event class, persists until the condition clears.
**Incompatible builds:** the view must therefore re-derive the same five classes itself. Unit ④ derives `batch_pause_resumed` as the transition `waiting_for_provider_batch → in-flight`; unit ③ derives it from a state-trace event or from `last_transition_at` deltas. They drift on any edge (resume that immediately re-pauses, recover-reenter, notifier restart): phone buzzes with no toast, or toast with no push — two owners of one semantic entity, exactly the braid AD-9 exists to prevent, reintroduced between its own consumers.
**Severity:** High.
**Close with:** new AD — **event-class derivation is a contract-owned pure function.** `derive_event_transitions(prev: Projection, cur: Projection) -> list[EventClass]` lives in `app/models/runtime/operator_surface.py` (imports nothing, per the layer rule); notifier and view both import it; an L1 parity test pins the five classes against golden transition fixtures. Nobody re-implements derivation.

### F7 — The watchdog dies with the session it guards

**Units:** ④ notifier vs the AD-7 lifecycle model.
**The letter:** AD-7 — HUD server is a child of the runtime session, dies with the session. AD-9 places the watcher "in the notifier service" but pins **no lifecycle**; the natural letter-compliant build co-locates the notifier in the same session (or the same process as the HUD server).
**Incompatible builds:** unit ④ ships the notifier as a session-child thread — fully AD-compliant. The failure AD-10 exists for is "AFK while wedged": the wedge classes that hang or kill the *session* (interpreter deadlock, OOM, machine-level kill of the console) take the watchdog down with the run. The one guard designed for unattended failure is silent in exactly the unattended-failure cases. The UX "HUD FEED LOST" state covers the browser page, which pushes nothing to a phone.
**Severity:** High.
**Close with:** tighten AD-9 with an explicit lifecycle: the notifier runs as its **own process**, launched by the start path but not fate-shared with the runtime session's Python process (survives session death; exits on run terminal status + grace, or is a persistent per-machine service). Add a sixth internal condition: projection file mtime frozen while status `in-flight` **and** producer process gone → fire `run_stalled` with a "producer dead" reading. Decide and pin it; silence here guarantees the co-located build.

### F8 — Strict contract model vs "consumers tolerate unknown added fields": one model can't serve both

**Units:** ① contract vs ②/③/④ consumers.
**The letter:** AD-4 — byte-pinned schema, parity tests; repo house style (see `production_trial_envelope.py`: `extra="forbid", strict=True`) and the Pydantic-v2 checklist push the contract model to strict/forbid. Consistency Conventions — "consumers tolerate unknown *added* fields, refuse unknown `schema_version`"; UX — unknown status renders UNRECOGNIZED, "never coerced".
**Incompatible builds:** consumer devs naturally parse with the shared contract model (that's what a contract package is for). A v1.1 producer adds an optional field, or a future envelope status lands: the strict model raises `ValidationError` in the reader — the HUD white-screens or exception-loops instead of rendering UNRECOGNIZED / tolerating the field. Meanwhile the AD-5 set-equality test lives producer-side and passes. Contract unit obeyed AD-4; consumer unit obeyed "use the contract"; the tolerance convention is satisfied by neither.
**Severity:** High.
**Close with:** tighten AD-4: the contract package ships **two parse surfaces** — the strict producer model (byte-pin source) and `read_operator_surface_lenient(raw) -> Projection | Unrecognized` (ignores unknown fields, returns a typed `Unrecognized(reason, raw_value, schema_version)` on unknown `schema_version`/status instead of raising). Consumers are **forbidden** (import-linter) from parsing with the strict model. L1: lenient reader pinned against a future-fields fixture and an unknown-status fixture.

### F9 — Windows `os.replace` vs open readers: the instrument can crash the plane

**Units:** ① emission vs ② server / ④ notifier (file-handle semantics).
**The letter:** AD-2 — atomic temp + `os.replace`. AD-6 — `/projection` "serves the file". Platform is Windows (env).
**Incompatible builds:** unit ② implements `/projection` as a streaming `FileResponse` (the idiomatic FastAPI build — holds the handle across the response); unit ④ polls with plain `open()`. CPython's `open()` does not pass `FILE_SHARE_DELETE`; while any reader handle is open, the producer's `os.replace` raises `PermissionError`. That exception fires **inside `_persist_envelope`, inside the walk** — the run pauses/fails because its own HUD read at the wrong microsecond. Each unit is letter-perfect; together they make the producer's mandated atomicity mechanism a run-killer under load (2–5s poll × long run ≈ certainty).
**Severity:** High.
**Close with:** new AD — **reader/writer file discipline**: consumers read via open-read-close snapshot only (server reads bytes then responds; streaming the live file is a defect); producer wraps `os.replace` in a bounded retry (e.g., 5 × 20ms backoff); on exhaustion the projection write **logs and skips — never propagates into the walk** (mirror of the notifier fire-and-forget convention; the reconcile-on-entry from F4 plus the next tick make skips self-healing). L1 test exercises replace-under-open-reader on Windows.

---

## MEDIUM

### F10 — `hud-config.yaml`: three readers, no owner, no schema (file doesn't exist yet)

**Units:** ② server (`hud.port`, staleness budgets) vs ④ notifier (event matrix, watchdog budget) vs ① producer (Projection Demands: "notification config echo" — so the **runner** must read this file too, a dependency the layer diagram doesn't draw).
**Incompatible builds:** three units each ship their own loader and their own defaults. UX says "config unreadable → defaults active" — whose? Notifier defaults push=on, server-side echo says push=off; the header chip and the phone disagree — a zero-lie violation manufactured entirely out of config ambiguity. Verified: `state/config/hud-config.yaml` does not exist today, so whoever lands first defines it de facto.
**Severity:** Medium.
**Close with:** new AD: `HudConfig` Pydantic model + single loader + single defaults constant live in the contract package; all three units import it; defaults are defined exactly once; the config echo in the projection is produced by that same loader; schema-pin test alongside AD-4's.

### F11 — Next-action command strings: the producer composes a grammar the CLI owns

**Units:** ① emission (writes "the exact next-action command string") vs the gate/trial CLI surface (owns argparse grammar; e.g., `gate decide --card-id … --decision-card-digest …`).
**Incompatible builds:** the runner hard-codes command templates; a CLI story renames a flag or adds a required one. Both units pass their own tests; the projection now carries a command the runtime rejects when pasted — the HUD's single actionable output is wrong, with the full authority of zero-lie behind it.
**Severity:** Medium (High blast radius, low likelihood short-term).
**Close with:** tighten AD-3: command strings are produced by a **command-builder function co-located with the CLI definition** (or a contract-carried structured command + one renderer the CLI also uses); L1 test round-trips every emitted command string through the actual CLI parser (`parse_args` accepts it) for all pause classes.

### F12 — `steps` shape: composed-manifest identity and backward walk-index on recover-reenter

**Units:** ① emission (steps from the **composed**, selection-narrowed manifest; `compose_manifest` at runner:2660) vs ③ view (renders "Step 33/47", lights forward progress).
**Incompatible builds:** (a) consumer fixtures assume the full default manifest; a `ComponentSelection`-narrowed run emits fewer nodes — totals/indices disagree with what the view was pinned against. (b) recover-reenter (runner:3474-3505) moves `start_index` **backward** and drops contributions; walk index regresses. A view built on "progress is monotone" renders it as corruption or clamps it (a lie); the notifier's transition derivation (F6) may misread the re-entry as fresh progress.
**Severity:** Medium.
**Close with:** tighten AD-1/Capability Map: the `steps` section carries the composed manifest's identity (compiled-graph digest + node count) and an explicit `walk_generation`/`reentered_from` marker incremented on recover-reenter; consumers render regression as labeled re-entry; L2 golden includes a narrowed-selection run and a reenter run.

### F13 — The projection re-creates the 525KB trap it was built to escape

**Units:** ① emission (Projection Demands: append-only state-trace + per-reading health history **inside** the document) vs ② server/③ view (whole-doc ETag re-serve + full re-render on every change, every 2–5s).
**Incompatible builds:** hours-long run × per-event trace × per-tile history = multi-MB document atomically rewritten on every 2s tick (post-F2), re-shipped and re-parsed on every poll. Each unit obeys its AD; the composition is the run.json parse trap with a network hop added.
**Severity:** Medium.
**Close with:** new AD: hard caps in the contract — state-trace is a ring buffer (last N=200 events; older events exist only in logs), health history windowed per tile (last M readings); an L1 size tripwire (serialized projection > 256KB fails). If full trace must be operator-visible, it goes to a sidecar NDJSON with its own contract — explicitly deferred otherwise.

### F14 — Notifier restart: first-observation semantics undefined → double-fire or never-fire

**Units:** ④ notifier ("derives event classes from projection transitions") vs ① emission (snapshot file; transitions are not durably enumerated for the watcher).
**Incompatible builds:** notifier process restarts mid-pause (or starts after the pause landed). Build A fires `paused_at_gate` on first observation (re-buzz on every notifier restart — alarm fatigue); Build B fires only on observed *transitions* (a pause that pre-dates the watcher **never** pushes — the AFK guard silently skips the one event it existed for). Both are the letter of "derives from transitions".
**Severity:** Medium.
**Close with:** tighten AD-9: notifier persists `{last_processed_progress_seq, last_status}` in its own state file (own dir, not the run dir — single-writer rule); first-observation rule pinned per class: `paused_*`/`run_stalled` fire if the condition is active and unacknowledged in the state file; `batch_pause_resumed` fires on observed transition only. L2 fixture: restart-mid-pause.

### F15 — `run_hud.py` disposition: two units can both "own" the render shell's home

**Units:** ③ render retarget (carves the shell into `app/hud/render/`, re-points ~98 pins) vs ⑥ legacy retirement (deletes readers "from the HUD path") — while AD-14 keeps `scripts/utilities/run_hud.py` + `tests/test_run_hud.py` in `block_mode_trigger_paths` and Deferred leaves "dev-dashboard salvage … out of scope".
**Incompatible builds:** unit ③ moves the shell and the pins; unit ⑥ leaves `run_hud.py` standing as the maybe-dev-dashboard, still importing the readers unit ⑥ just deleted (import error at rest), or keeps its own copy of the shell — two divergent render shells, and `tests/test_run_hud.py` pins whichever fossil survived. Neither story's AC forces the question.
**Severity:** Medium.
**Close with:** tighten AD-12/AD-14: pin the disposition — `run_hud.py` becomes a deprecation stub (exits with a pointer to `trial hud`) or is deleted in the retire story; `tests/test_run_hud.py` moves/retires with it; the Tier-2 bump (⑦) removes/renames its trigger-path rows in the same change; import-linter forbids anything importing `hud_data_sources`.

### F16 — Start-path ordering: server needs the run dir; pre-flight needs the server; registration mints both

**Units:** ⑤ start path vs ② server launch.
**The letter:** AD-7 — server launched by the start path with explicit `trial_id`, healthz is a pre-flight item; AD-8 — never discovery, refuse on ambiguity. Today `effective_trial_id` and the run dir materialize inside `run_production_trial` (runner:2634-2652); the `registered` envelope **does** flow through `_persist_envelope` (2652), so a projection exists at registration — but only if registration precedes server launch.
**Incompatible builds:** unit ② (AD-8 strict) refuses to start unless run dir + projection exist; unit ⑤ launches the server first so "HUD server ready" can gate everything else. Deadlock — or unit ② relaxes to "bind now, dir later", quietly reintroducing a discovery-shaped wait. Both letter-compliant.
**Severity:** Medium.
**Close with:** new AD (or AD-7 rule text): pin the start sequence — mint `trial_id` → create run dir → write `registered` projection (via assembler) → launch server (dir + projection guaranteed) → run pre-flight (healthz item validates trial_id per F3) → spawn SPOC. The UX "BINDING — awaiting first snapshot" state then only covers the browser page, never the server.

---

## LOW

### F17 — ETag from mtime+size misses same-size rewrites

**Units:** ② server (ETag = mtime+size per AD-6) vs ① emission (frequent small rewrites; `seq` 41→42 is byte-length-stable; FastAPI/OS timestamp granularity varies).
**Incompatible builds:** same-size write inside timestamp granularity → 304 → the view silently skips an update while believing itself fresh — a small zero-lie leak. The document already carries the perfect ETag.
**Close with:** tighten AD-6: ETag = `schema_version:seq` (or content hash), never mtime+size.

### F18 — Tier-2 bump lists files that don't exist yet

**Units:** ⑦ manifest bump (pre-dev, party-gated, adds `app/hud/**` etc. to `block_mode_trigger_paths`) vs ①–④ (create those files later).
**Incompatible builds:** if any validator ever grows an existence check on trigger paths (the frozen-pack registry already checks existence at `check_pipeline_manifest_lockstep.py:351` — the pattern is in the codebase), the pre-dev bump fails CI until the files land; land the files first and they slipped past the regime. Verified today's checker does **not** check trigger-path existence, so this is ordering fragility, not a live break.
**Close with:** one sentence in AD-14: trigger paths MAY be registered ahead of file creation and are inert until the paths exist; the lockstep checker must never require their existence.

---

## Counts

| Severity | Count | Findings |
|---|---|---|
| Critical | 3 | F1, F2, F3 |
| High | 6 | F4, F5, F6, F7, F8, F9 |
| Medium | 7 | F10, F11, F12, F13, F14, F15, F16 |
| Low | 2 | F17, F18 |

## Disposition

The paradigm (single-writer projected read model, dumb view, command-free HUD) survives the attack — every hole closes with a new or tightened AD, none requires re-architecting. But F1/F2 are load-bearing: as written, the spine's write model cannot produce the projection its own contract demands at the freshness its own UX source requires, and any two teams implementing ① and ⑤ in good faith will collide at the projection file. Recommend: resolve F1–F9 as spine amendments (one new "assembler + emission cadence" AD absorbs F1+F2, one "reconciliation & file discipline" AD absorbs F4+F9, tightenings for the rest) before the epic cut; F10–F18 may land as AD tightenings or as named ACs on the affected stories at the architect's discretion.
