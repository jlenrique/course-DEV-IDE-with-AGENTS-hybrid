# Claude Shadow Monitor — Canonical Production Conversation arc (session 16, 2026-07-06)

**Instituted:** operator directive 2026-07-06 ("review at all major intervals of task completions the findings and recommendation of our shadow monitor (in a new claude shadow monitor report freshly created for this dev session)").
**Pattern precedent:** `marcus-claude-shadow-monitor-2026-06-29.md` (Claude monitor) + the Codex SOP ledgers (2026-07-03/04). The Codex monitor is NOT armed this session; this ledger is the session's independent lane.

## Protocol (binding for this session)

- **Monitor identity:** a FRESH independent Claude agent spawned per poll (fresh eyes each time — no accumulated rationalization), read-only over the repo, writing ONLY to this ledger (via the orchestrator relaying its findings verbatim into this file).
- **Scope fence (per the two-actor discipline + session-12/13 collision forensics):** the monitor does NOT run session-START, does NOT pick up queued goals, does NOT edit code/tests/docs, does NOT commit. It may run read-only commands (git log/diff/status, focused pytest, ruff) to verify claims independently.
- **Poll cadence:** SOP-numbered entries at every major task-completion interval — story spec ready-for-dev, dev-agent completion, post-code-review remediation, story close/commit, and every arc-level gate (party rounds, live proofs, done-signal).
- **Verdict grammar:** each SOP entry ends CONCUR / CONCUR-WITH-FINDINGS / OBJECT, with findings F-NNN numbered and carried forward until closed.
- **Orchestrator obligation:** the dev lane (Claude main session) READS the latest SOP entry before proceeding past the interval it covers, and records disposition of every open F-NNN.

## Arc context (frozen reference for monitor polls)

Branch `dev/workbook-2026-07-06`. Green-light party record: `_bmad-output/planning-artifacts/canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md` (+ §6 S0 addendum). W2 seam contract: `styleguide-binding-cd-contract-2026-07-06.md`. Story spine S0✅ → S1 (CD ResolvedCreativeDirective contract) → S2 (picker wiring) → S3 (CD live) → S4 (FAIL-LOUD) → S5 (G0 canonical) → S6 (Tracy canonical) → S7 (workbook generalization) → S8 (composed proof).

---

## SOP entries

### SOP-000 — ledger instituted (2026-07-06, orchestrator)
Baseline: HEAD `63eac137` (S0 complete, pushed, 0/0 with origin). Worktree clean at institution. No dev-agent work dispatched yet. First monitor poll (SOP-001) fires when the S1 story spec reaches ready-for-dev.

### SOP-001 — S1/S3 premise audit (2026-07-06, fresh monitor agent; fired EARLY — pre-spec — after an Explore lane found the green-light's CD premise stale)

**Trigger:** Explore-lane report contradicted the ratified premise ("Trial-3 dispatch routes around CD"). Monitor independently verified claims C1–C6 before any spec is authored on them.

**Verification results (all line numbers independently located):**
- **C1 CONFIRMED** — `dispatch-registry.yaml:13` maps cd → `build_cd_graph` under `_status: production`.
- **C2 CONFIRMED** — specialist-dispatch branch (`production_runner.py:2557-2610` start walk, `3284+` continuation) is fully generic; NO cd-specific skip/quarantine/stub anywhere in the orchestrator; only cd-conditional is the dependency fallback at `production_runner.py:371`.
- **C3 CONFIRMED** — `cd/graph.py:388-459` `_act` is a real live-LLM node (cascade-resolved `tier_request="fast"`, not hard-pinned gpt-5); writes `cd_directive` `{schema_version, experience_profile, slide_mode_proportions, narration_profile_controls, creative_rationale}`; 9-node scaffold conformant. Trial-3 fix comments evidence prior live dispatch.
- **C4 REFUTED (F-101, material)** — CD's output IS consumed today: `package_builders.py:221-236` does `latest_for_specialist("cd")`, **fails loud** (`builder.gary.upstream-missing`) if absent, and `build_gary_briefs` (92-157) validates `experience_profile` and renders Experience profile / Creative rationale / Slide-mode proportions into the deck-level instruction text that reaches Gary via the §06→07 projections. `run_builder_node` invoked in BOTH walks (2346/2360, 3080/3090). **CD is load-bearing, not orphaned.** (Secondary: `writers/theme_resolution.py` carries `experience_profile_id` but has no production caller — dormant.)
- **C5 CONFIRMED** — picker→`gamma_settings[]`→Gary `resolve_styleguide` works without CD; WARN-seed at `_act.py:519-528` with the literal "fail-loud deferred to cd-envelope-authoring" marker.
- **C6 CONFIRMED** — THREE runtime SSOT readers: orchestrator (`production_runner.py:94`, Leg-C floor), Gary (`styleguide_library.py:34/157`), picker (`styleguide_picker.py:69/256/291/997`; `picker_html_emitter.py:198` arguably a fourth).
- **Registry staleness CONFIRMED** — `specialist-registry.yaml:87-93` stale in BOTH directions: CD is neither routed-around nor unconsumed.

**Findings:**
- **F-101** — CD is load-bearing at §06 (see C4 REFUTED). "CD activation" framing is wrong; S1 must be re-scoped and `specialist-registry.yaml:87-93` corrected in-scope.
- **F-102** — Specialist-internal `interrupt()` is non-blocking by construction: `dispatch_adapter._invoke_compiled_graph` (240-265) records `__interrupt__` into `self.last_interrupts` — **write-only in production** (only tests read it; `tests/composition/test_texas_to_cd_chain.py:71` pins the behavior). Sub-graph is never resumed → **`finalize`/`handoff` never execute in production dispatch for ANY specialist.** CD is already operator-invisible at §4.75 (no-new-ceremony satisfied by status quo); any S1 design placing real work in `gate_decision`/`finalize`/`handoff` silently never runs.
- **F-103** — CD-at-4.75 is pinned in committed walk tests only via `_FakeAdapter` canned outputs; the real CD graph is pinned only in composition/unit tests with a fake LLM. NO committed real-walk+real-graph pin; no live-LLM CD test. S1 AC should add the real-CD-graph-in-walk pin.
- **F-104 (heaviest)** — Pick-time vs resolution-time ordering: CD runs at §4.75; under the CURRENT Leg-D flow a pick can land later (G2B-era surface); Gary resolving at §07 after the final pick is precisely why the protected source-detail→Gamma invariant is safe today. Full W2 ("CD = single runtime resolution point") without solving ordering risks binding a stale/absent pick — a protected-invariant regression in service of an architecture diagram.

**Monitor recommendation:** option **(b) staged toward (a)** — S1: CD additionally emits the layering manifest + bound-styleguide resolution as DATA in its contribution (extend the deterministic `_canonicalize_cd_directive` neck); Gary gains a **shadow-parity check** (resolves as today, compares against CD's envelope, WARNs on divergence — the ratified flag-OFF+teeth-witness pattern). Authority flip (Gary consumes envelope; yaml readers collapse) deferred to a later story once parity holds across live runs.

**Verdict: CONCUR-WITH-FINDINGS** — author the S1 spec on corrected facts, with a re-scope round before dev opens; the round must weigh F-101/F-102/F-104 explicitly.

**Orchestrator disposition (recorded at relay):** re-scope round convened (Winston/Dan/Amelia) with F-101..F-104 as premises. Orchestrator note passed to the round: the ratified S2 moves the pick to TRIAL-START (persisted pre-run-dir), which materially reduces F-104's ordering exposure for the arc's end-state — but mid-arc sequencing and the three-reader collapse remain the round's call.
