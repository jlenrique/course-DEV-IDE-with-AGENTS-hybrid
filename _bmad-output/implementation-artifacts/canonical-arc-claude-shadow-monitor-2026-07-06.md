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

### SOP-002 — S1 spec pre-dispatch review (2026-07-06, fresh monitor agent)

**Artifact:** `canonical-arc-s1-cd-styleguide-resolution-emission.md` @ `6ba62ce4`. **Method:** independent code verification of every load-bearing spec claim.

**Fidelity:** spec faithful to §7 re-scope + amended W2, item-by-item verified; no smuggled scope (AC-L legitimate per arc governance §5). Spec correctly caught the SECOND stale registry block (`:211-216`) beyond §7's citation. All Context line-number claims independently verified accurate.

**Feasibility (code-verified):** (a) `runner_supplied_payload` supports D2; CD's 4.75 dependency map = `{source_bundle: texas}`, no collision. (b) `_canonicalize_cd_directive` never sees the envelope payload — block must be a sibling pure function in `_act`'s path (spec's alternative reading is REQUIRED). (c) State pins permit an optional field; `SpecialistReturn` is `extra="forbid"`; exact-payload pins (`test_texas_to_cd_chain.py:70`, `_FakeAdapter` fixtures) will trip legitimately. (d) Resolver extraction REALISTIC — `styleguide_library.py` has zero gary-internal imports (only `dispatch_errors.SpecialistDispatchError` + `scripts.utilities.file_helpers`); import-linter contracts (pyproject.toml:107-330) pass for both proposed homes; `StyleguideError` re-export preserves isinstance/except semantics. Overlay/generator ARE lockstep trigger paths; runner + cd/graph are NOT — spec's Tier-1 handling exactly right. §06 reads only `cd.output["cd_directive"]` — sibling key structurally cannot break the fold.

**Findings:**
- **F-201 (minor):** D3's `resolved` field exceeds §7's literal list — justified completion (digest needs a referent; S3 comparator needs the data). Recorded as deliberate.
- **F-202 (MATERIAL — highest risk):** no-picks default resolution had no pinned guide; gary's runtime seeds the gary-internal `DEFAULT_VARIANT_PAIR` which the resolver cannot reproduce; an invented default becomes S3's parity baseline. **Guard:** pin standard-A `hil-2026-apc-crossroads-classic` + explicit provenance string; S3 comparator keys on `status` for this case.
- **F-203 (material):** D2's "wired in BOTH walk bodies" was architecturally stale — both walks share `_dispatch_specialist_at_node` (:1924, S4-part-2 refactor); correct wiring = one `cd` branch in `_runner_payload_for_specialist` (:1386), reusing `_gamma_settings_from_directive` (:1593) + sha256 pattern (:852-854); extend the seam docstring enumeration (:1405-1412).
- **F-204 (minor):** `dispatch_adapter.py:65-71` docstring ("runner keys WIN") stale vs raising collision guard (:108-120); design against code; one-line docstring NIT permitted at T11.
- **F-205 (minor):** exact-payload pins + `extra="forbid"` will trip on runner-path tests — extend pins, NEVER weaken equality assertions; T11 Acceptance Auditor rejects any weakened assertion.
- Witness-gap notes: AC-5 must assert on the RE-LOADED envelope (persist→resume); RED-6 must obtain the projection through `_runner_payload_for_specialist`, never hand-fed.

**SOP-001 carry-forward:** F-101 CLOSED-in-spec · F-102 ADDRESSED (AC-4 + separate deferred filing) · F-103 ADDRESSED (D5) · F-104 ADDRESSED (staged design + S4 re-gate + S-flip criteria). Nothing unaddressed.

**Verdict: CONCUR-WITH-FINDINGS** — dispatch approved with F-202 + F-203 applied to the spec.

**Orchestrator disposition:** ALL applied to the spec pre-dispatch (F-202 default-guide pin; F-203 wiring-altitude rewrite + docstring-enumeration instruction; F-204/F-205 dev+T11 notes; both witness-gap hardenings folded into AC-5 and RED-6). F-201 recorded as deliberate. Dev agent dispatched on the amended spec. Next poll: SOP-003 at dev-complete.

### SOP-003 — S1 dev-complete independent verification (2026-07-06, fresh monitor agent) — RELAYED (full text in the agent transcript; condensed here)

Audit of the uncommitted dev diff. **All dev claims verified:** F-203 wiring exactly one cd branch (`production_runner.py:1444-1459`, zero per-walk); F-202 pin byte-exact; §06 fence holds against the real builder; **all four guard-touching deviations judged honest at full assertion strength** (parity cd→wired grounded in SOP-001's own verification; partial-ordering witness relocated-not-weakened; over-promise corpus coverage conserved; picker-guard refinement matched the docstring contract); pre-existing-failure claims supported (Texas-internal frames, zero S1 files on the stack); overlay regen honest; dev's green claims reproduce (20 S1 + 77 guard + 27 gary, lint 16/0, ruff clean); AC-L properly gated and NOT executed. Stash cross-check: **nothing lost** — Poll-007 of the operator's Codex ledger ("S1 diff vanished") was a stale mid-stash-window read; the ledger's 16,233-byte pre-Poll-007 history recovered to a sibling file. Findings: **F-301** picker-guard dynamic-import evasion (hardening) · **F-302** probe-corpus partial-row reactivation note · **F-303** pyproject C3 row verified in-scope-by-necessity · **F-304** schema-contract note for S3 + duplicate-variant NIT · **F-305** AC-L closes on PASS, never SKIP. **Verdict: CONCUR-WITH-FINDINGS.**

### T11 3-lane review + remediation + live witness (2026-07-06, orchestrator record)

**3-lane `bmad-code-review`** (Blind Hunter / Edge Case Hunter / Acceptance Auditor, all fresh agents): Auditor = **ACCEPT-WITH-NOTES, every offline AC/deliverable MET** (F-202/F-203/AC-5/RED-6 implemented exactly as amended; all 8 dev deviations judged truthful; 2 ratifications recorded). Blind + Edge converged independently on a real defect cluster the claim-verification pass couldn't see; Edge Case Hunter's **HIGH was execution-confirmed** (malformed/non-UTF-8 directive at the cd seam crashed the walk un-persisted instead of error-pausing). Triage: **0 decision-needed / 11 patch / 3 defer / 4 dismissed** — full detail in the story file's Review Findings section; defers in `deferred-work.md`.

**Remediation (fresh dev agent, RED-first):** all 11 patches landed — 20 new boundary tests captured RED then green (T1 crash→`SpecialistDispatchError` `cd.directive.unreadable|malformed` + read-ONCE digest discipline; T2-T4 honesty cluster → `unresolvable_pick` with evidence, default never binds over a present-but-bad pick, full verbatim echo; T5 digest attests the same bytes resolution parsed (additive `content` param on the shared resolver, gary re-export untouched); T6 lifecycle/visibility as data; T7 `errors` list in pick order; T8 AST-based picker guard incl. both evasion fixtures + import_module co-occurrence; T9 vacuous-skip removed from AC-L; T10 hygiene + path-scrub + F-302 note). One ratified judgment call: falsy `variant_id` ⇒ `unresolvable_pick`, never silent default-A. Battery: **345 passed serial AND xdist**; lint 16/0; overlay fresh.

**Orchestrator independent re-verify:** 340 passed / 1 skipped focused battery, lint-imports 16 kept / 0 broken, overlay fresh.

**AC-L LIVE WITNESS: PASSED (19.0s, real model dispatch, first-run-stands, armed run — the T9 fix guarantees this PASS is not a masked skip).** F-305 satisfied.

Next poll: SOP-004 at the S1 close commit.

### SOP-004 — S1 story-close audit (2026-07-06, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Commit integrity CLEAN:** `c24308f7` = exactly the 20-file S1 set; all three strays excluded and still untracked; pyproject carries exactly the two ratified hunks. **Post-commit green REPRODUCED:** 144 passed focused battery, lint 16/0, overlay fresh. **Remediation spot-audit (T1, T2/T3/T4, T8) ALL VERIFIED in committed code** — read-once digest discipline, honesty trichotomy with typed error accumulation, `default_provenance` only on the clean branch, AST guard at full strength with both evasion fixtures. **Live witness LEGITIMATE:** committed AC-L test has no skip path in its body (gating exclusively upstream conftest, contract-pinned); the 19.0s PASS cannot have been a masked skip; content assertions real (status, bound_guides names, byte-identical neck reproduction). **Carried findings:** F-301/302/303/305 CLOSED; F-304 substantially satisfied.

**New findings:** **F-401** (procedural) story Status line flip — EXECUTED at the flip. **F-402** (advisory) D3 schema sketch stale vs committed emission — stale-marker ADDED under D3; S3's spec must cite the committed `_styleguide_resolution_block` as schema-v1 SSOT. **F-403** (S2 MUST inherit) picker `_VARIANT_IDS` and CD `_PICK_VARIANT_VOCABULARY` are two independent {A,B} constants with import coupling structurally forbidden and NO lockstep pin — S2 carries the lockstep constraint + adds the test-level pin (a test may import both; production may not). **F-404** (S2 MUST inherit) CD's projection reads ONLY the directive both walks resolve — S2's persisted pick must land in the directive `gamma_settings[]` (reuse `write_pick_to_directive`, which already normalizes into exactly the shape CD's neck accepts), or CD audits blind and manufactures an S3 parity divergence.

**Verdict: CONCUR-WITH-FINDINGS — S1 flipped DONE; S2 opens.** SOP-005 (S2 spec pre-dispatch) must verify F-403 + F-404 are present in the S2 spec text.

### SOP-005 — S2 spec pre-dispatch review (2026-07-06, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**SOP-004 obligations BOTH DISCHARGED** (F-403 pin encoded test-level with verified constants; F-404 satisfied by construction via `commit_picker_pick`→`write_pick_to_directive`, AC-2/AC-4 close the loop). **Fidelity:** faithful to every ratified item; all Context claims independently verified. **Findings:** **F-501** (record) — the ratified "before run-dir creation" letter is literally unsatisfiable (`compose_and_write` mkdirs the run_dir and writes the directive into it); post-compose/pre-confirm-gate is the only F-404-coherent insertion; witness wording = zero SPECIALIST DISPATCH (compose itself makes one LLM call); PickerError abort leaves nothing to resume (correct S2-era shape, S4 owns the hard halt). **F-502 (MATERIAL)** — picks sidecar has NO course identity; per-course provenance underivable; additive course/corpus field threaded from `start_trial.input_path`; legacy events = no-prior-pick; never dereference directive_path. **F-503 (HIGHEST RISK)** — discriminator must NOT be `not auto_confirm` alone (existing tests would fire real gh-pages publishes/hang); injectable `picker_preflight_fn` seam on start_trial (confirm_fn precedent) + isatty-aware gating + the zero-publish non-tty witness. **F-504** — run_tag: hyphens forbidden by `_RUN_TAG_RE` at both producers; `str(trial_id)` fails loud; use `trial_id.hex` (pin it); `--selection-code` requires `--trial-id`. **F-505** — D2 `--selection-code` ruled LEGITIMATE (arc-required groundwork for S4; strengthens canonicality vs the validation-bypassing `--gamma-settings-file`) with riders (J-3 interaction test; F-504 constraint). **F-506** — (a) inline-list degrade must equal the SSOT roster; reuse-last-pick arm gets a witness post-F-502; (b) accept-recommended commit path named test via `build_selection_code`, shape-identical to pasted-code commit.

**Verdict: CONCUR-WITH-FINDINGS.** **Orchestrator disposition: ALL SIX applied to the spec text pre-dispatch** (F-501 reinterpretation recorded in D1; F-502 amendment in D3; F-503 guard + AC-8 witness in D1/ACs; F-504 rule in D1/D2; F-505 riders in D2; F-506 in D3/AC-5). Dev agent dispatched on the amended spec. Next poll: SOP-006 at dev-complete.

### SOP-006 — S2 dev-complete verification (2026-07-06, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

All SOP-005 amendments verified landed verbatim (F-503 injectable seam + isatty default exactly as mandated; F-502 threading + honest legacy degrade + sidecar append-safety; F-504 hex pins + pre-compose trial-id guard; frozen-grammar fence holds, emitter 41 green; walk-pin diff purely additive, S1 pins byte-untouched). Deviations 2/4/5 ALL judged legitimate (digest re-computation ruled NECESSARY after exhaustive consumer grep). AC-3 spot-checks reproduce; the 13 g0_enrichment_brick baseline reds root-caused to a **never-committed corpus fixture** + substrate landed "T11 owed" at `b59679ce` + stale ACTIVE_TERMINAL_GATES pin. Findings: F-601 legacy-uninjected-tests tty exposure (→ patched as P17) · F-602 transitive AC-8 witness (accepted) · F-603 lexicographic timestamp (→ patched as P12) · F-604 edit-at-gate stale digest (→ patched as P10) · **F-605 S5-MATERIAL: binding S5-open precondition recommended** (adopted — charter §8) · F-606 narration contradiction (→ patched as P9). **Verdict: CONCUR-WITH-FINDINGS.**

### T11 3-lane review + remediation + LIVE witness for S2 (2026-07-06, orchestrator record)

**3-lane review:** Auditor ACCEPT-WITH-NOTES (every offline AC/deliverable MET; all F-50x exact; fences intact; 7 deviations consistent). Blind + Edge converged on the ceremony-honesty cluster; Edge's two HIGHs both execution-confirmed (deprecated-last-pick recommendation = deterministic 3-strike abort post-compose; trial-id reuse silently clobbers an existing run record). **Triage: 0 decision-needed / 18 patch / 3 defer / 5 dismissed** (detail in the story file).

**Remediation (fresh dev agent, RED-first): 18/18** — pickability-filtered recommendations, pre-compose exists-guard (`TrialAlreadyExistsError`) + pre-compose scripted-code decode, canonical course key, corrupt-sidecar degrade, EOF/interrupt→clean PickerError, ONE `_CeremonyBudget` across all arms, honest Beat-1 reword, post-confirm-loop re-digest + pick-dropped-by-edit WARN, parsed-timestamp latest-event, scrubbed publish-error narration, unified `degraded:*` sentinel family, strengthened test assertions, confirm-prompt honors its own text, stdin∧stdout tty default + no-op preflight in 3 legacy suites, public `read_pick_events`. 24 new witnesses; 42-test file green; 218 green serial+xdist; lint 16/0; ruff clean. Process note: one stash/pop roundtrip against the no-stash instruction, self-reported, restoration verified (stash list back to 2 pre-session entries; suites green immediately after) — subsequent baselining used throwaway worktrees.

**Orchestrator re-verify:** 164 green focused; lint 16/0; the single red = the F-605 baseline pin (thrice-verified pre-existing).

**AC-L LIVE WITNESS: PASS — happy-publish path (evidence `s2-acl-liveproof-20260706T211912Z`).** Real gh-pages publish verified live (`https://jlenrique.github.io/assets/styleguide-picker/bd869b0049ad47d8907b599cb674a45a/index.html`, verify-after-push 200); Beat-1 kickoff narration rendered as ratified; real selection-code round-trip → confirm → pick committed with full provenance; directive gamma_settings + provenance block + F-502 canonical course field in the sidecar event all asserted; **walk paused cleanly at G1** (`paused-at-gate`, no error tag); trial-start digest == sha256 of FINAL directive bytes. Site pack cleaned up, 404 verified. First-run-stands; no assertion re-run. Live-leg process note: the live agent repeatedly parked on background watchers (the known anti-pattern) — the orchestrator drove completion via a direct terminal-state watcher; the driver itself ran the protocol perfectly.

Next poll: SOP-007 at the S2 close commit.

### SOP-007 — S2 story-close audit (2026-07-06, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Commit integrity CLEAN** (`037be6d3` = exactly the S2 set + evidence pack; strays excluded; sidecar diff = exactly the one live pick event; walk-pin file verified purely-additive; no run-dir leakage). **Post-commit green REPRODUCED** (47 passed serial; lint 16/0). **Live evidence INTERNALLY CONSISTENT** — single-pass driver log, no retry-to-green signature, all 8 assertions PASS with values. **P1/P2 remediation VERIFIED in committed code.** Findings: **F-701** (advisory) the cleanup receipt was overwritten by the later confirm-run — deletion-commit provenance lost though the 404 claim stands; future AC-L cleanup receipts should append. **F-702..F-705 = S3-SPEC INHERITANCE OBLIGATIONS** (SOP-008 must verify all four in the S3 spec text, alongside carried F-402 + F-304): F-702 parity clock is STATUS-KEYED (counts every run whose CD envelope status is pick-resolved, regardless of tty; pick-presence determined from the directive/envelope at CD-read time, NEVER from sidecar events — an edit at G0 can drop a committed pick); F-703 trial-start now attests FINAL directive bytes — S3's comparator cross-checks trial-start digest == CD's envelope digest to discriminate mid-walk directive mutation from genuine Gary-vs-CD divergence; F-704 pickable ≠ resolvable — the comparator resolves through the shared resolver only, never imports picker pickability; any new Gary-side vocabulary constant extends the F-403 lockstep pin; F-705 public `read_pick_events` + heterogeneous-schema tolerance + `trial_id.hex` keys + the F-605 baseline red carried in green-criteria + WARN-seed untouched (S4 owns the flip).

**Verdict: CONCUR-WITH-FINDINGS — S2 flipped DONE.** Session ends here per operator directive (WRAPUP + fresh session); S3 spec authoring is the next session's first build action, opening with SOP-008 on its spec.

### SOP-008 — S3 spec pre-dispatch review (2026-07-07, session 17, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Artifact:** `canonical-arc-s3-gary-shadow-parity.md` @ HEAD `d049453b`. **Method:** independent code verification of every load-bearing claim + one live baseline-red reproduction.

**Fidelity:** faithful to the §7 re-scoped S3 row item-by-item (phantom un-route deleted; three-outcome trichotomy exact; receipts ride Gary's contribution; three non-vacuity fixtures; both-walks witness; live teeth-witness w/ F-701 append rule). No ratified item dropped; D2/D4/D5 judged required completions of F-703/F-704, not smuggled scope. Amelia's base-layer parity semantics correctly encoded.

**Feasibility (code-verified):** F-402 key set byte-verified at `cd/graph.py:572-586` (exactly the 10 keys). `resolve_styleguide(guides=)` + `load_style_guides(content=)` signature-compatible, byte-identical on identical bytes. Projection machinery delivers present-with-None clean but HARD-RAISES on absent producer key (`dispatch_adapter.py:97-101`). `runs_root`/`trial_id` in scope at the gary branch (:1436-1443). No runner-key collisions. Exact-shape trip-points named (`test_package_builders.py:212,261,516`). Gary contribution assembly additive-safe (`_act.py:1160-1172`). Live-witness leg-2 classification HOLDS (CD block frozen at 4.75 by the per-node skip rule; Gary reads SSOT at §07 act-time). Baseline reds reproduced live at HEAD: 14 failed / 49 passed across the two named suites (consistent w/ F-605/F-705).

**Findings:** **F-801 (HIGHEST-RISK)** — spec sourced `trial_start_directive_digest` from `run.json`, which is the persisted ProductionTrialEnvelope and carries NO digest field; the attestation lives ONLY in `trial-start.json` (`trial.py:533,536`); as written, F-703's three-way check silently degrades to two-way on every production run with all spec-lettered tests green. Guard: re-point to `trial-start.json` + a mandatory non-null-digest witness. **F-802 (material)** — the manifest-projection transport hard-fails legacy/rewind-recovered envelopes whose §06 contribution predates S3 (idempotent skip means the key stays absent), colliding with W5-morph "golden bundles must not false-fail"; options (i) runner-context transport outright or (ii) keep projection + pin rewind pre-§06 + recorded fail-loud ruling, either with a committed witness. **F-803 (minor)** Tier-1 ruling SUSTAINED on sharper grounds (dp-v1 precedent; Tier-2 operative trigger unmet). **F-804 (minor)** precision nits: source constant is `CONSUMED_PAYLOAD_KEYS` (alias only in package_builders:35); gary branch :1436-1443; `_normalized_gamma_settings` extends past :560; AC-2 wording. **F-805 (minor)** audit attaches only on the `generate_gamma_variants` slides path (:1182-1183); legacy `dispatch_to_gamma` branch carries no receipt — state the fence; AC-5 harness drives the slides path (production always does — parity clock unaffected). **F-806 (minor)** AC-L leg 2 should mutate a RESOLVER-EMITTED field so BOTH `ssot_digest` and base-resolution digest diverge.

**Carry-forward disposition:** F-702 HONORED · F-703 honored-in-design, defective in one input's letter (F-801) — honored once amended · F-704 HONORED · F-705 HONORED (baseline verified live) · F-402 HONORED (byte-verified) · F-304 HONORED (AC-6 teeth).

**Verdict: CONCUR-WITH-FINDINGS** — dispatch approved once F-801 + F-802 applied to the spec text; F-803..F-806 dev/T11 notes. Next poll: SOP-009 at S3 dev-complete (verify F-801/F-802 landed as amended + AC-L rewind point consistent with the F-802 choice).

**Orchestrator disposition (recorded at relay):** ALL SIX applied to the spec text pre-dispatch — **F-801:** D4 + Context re-pointed to `run_dir/"trial-start.json"` (with the run.json-has-no-digest fact on the record) + the mandatory AC-3 non-null-digest sub-witness. **F-802: option (i) ADOPTED as the ruling** (F-501-reinterpretation precedent): `cd_styleguide_resolution` travels as CHARTERED runner context from the envelope's latest cd contribution (the established `gamma_settings`/`directive_projection` pattern for exactly this data family); NO manifest edit, NO §06 package change; lockstep regime not triggered (STOP-and-report rider if dev finds a manifest edit unavoidable); §06's existing `builder.gary.upstream-missing` fail-loud cited as the preserved "same fail-loud path" letter; mandatory AC-6 legacy-envelope clean-dispatch witness added. **F-803** moot under (i) (ruling text retained as the contingency rider). **F-804** all four precision fixes applied. **F-805** fence stated in Context + D3 + AC-5 + Out-of-scope. **F-806** encoded in AC-L leg 2. Spec flipped READY-FOR-DEV; dev agent dispatched on the amended spec. Next poll: SOP-009 at dev-complete.

### SOP-009 — S3 dev-complete independent verification (2026-07-07, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Mandatory verifications ALL PASSED (code-first, dev narrative not trusted):** F-801 landed as amended (`_trial_start_directive_digest` reads ONLY `trial-start.json`, honest None, never a raise; the AC-3 non-null witness exists TWICE — seam-level and end-to-end walk-level with the persisted receipt equal to the on-disk attestation). F-802 landed as amended (chartered runner context from `latest_for_specialist("cd")`; `git diff --stat` confirms ZERO manifest/§06 edits; the legacy witness runs the REAL gary graph through the REAL adapter with a genuinely pre-S1 cd contribution). WARN-seed byte-untouched (hunk-range proof + source-text pin + the seed demonstrably still fires).

**Spot-audit:** parity.py pure/total verified (imports hashlib/json/typing only; catch-all folds surprises into `divergence/contract-violation`; clock_eligible true on nothing but resolved∧ok/match — 9-row truth table); classification matches the ratified trichotomy with None-filtered comparable set; AC-4 witnesses non-vacuous; all four extended pins STRONGER post-extension (exact-set/exact-dict retained + value asserts); audit allowlist path-specific per S1 precedent; harness fakes signature-only.

**Suites (serial, venv):** 753 passed / 2 skipped / 4 failed — all 4 reds re-run in a throwaway `d049453b` worktree and fail identically at baseline (30-1 contract, transform-registry, 2× Texas-internal); dev touched NONE. Ruff all-pass on 16 touched/new files; lint-imports 16/0. **Diff hygiene CLEAN** (exactly the dev set + 2 orchestrator-owned docs; strays + the operator's live external-monitor ledger untouched/unstaged; `git diff --check` clean).

**Findings:** **F-901 (minor)** AC-4's `037be6d3`-equivalence is witnessed as within-tree A/B + resolver byte-identity, not a cross-commit golden — judged honestly covered; note the argument in the review record. **F-902 (minor)** touched-.py count is 16 not 15 — correct in the close commit message.

**Verdict: CONCUR-WITH-FINDINGS** (both advisory). Story must NOT flip done until the AC-L both-leg live PASS (leg-2 mutates a resolver-emitted field per F-806; rewind free per F-802 ruling; cleanup receipts APPEND per F-701). **Next poll: SOP-010 at the S3 close commit** — verify commit integrity, live-evidence single-pass consistency, and clean git-restore of the leg-2 SSOT mutation.

**Orchestrator disposition (recorded at relay):** F-901 noted in the T11 review record (the Acceptance Auditor independently reached the same equivalence ruling); F-902 will be honored in the close commit message (16 files). Parallel T11 3-lane review ran concurrently: Auditor ACCEPT-WITH-NOTES (all ACs MET, 10/10 deviations FAITHFUL), Blind Hunter no-Critical/High; Edge Case Hunter pending at relay time. Triage + RED-first remediation follow, then AC-L.

### T11 remediation + AC-L LIVE witness for S3 (2026-07-07, orchestrator record)

**3-lane review triage: 0 decision-needed / 7 patch / 1 defer / 4 dismissed / 3 notes** (Auditor ACCEPT-WITH-NOTES — every offline AC MET, all 10 dev deviations FAITHFUL, no loosened assertion; Blind no-Critical/High; Edge no-MUST-FIX after walking ten boundary families, and it execution-REFUTED Blind's same-guide false-WARN suspicion). **Remediation (fresh dev agent, RED-first): 7/7** — producer-side trial-start attestation witness (real `start_trial` write feeds the seam reader), `schema_version` strict-int gate (bool/float/str claims → contract-violation; int>1 → schema-newer), reason-keyed gap logging, whole-receipt JSON-safety + deep-decoupling + forensic crash-path detail, WARN on malformed producer digest (null stays silent — legitimate single-file shape), AC-4 canonicalizer teeth, double-resume no-re-audit witness. **Orchestrator re-verify: 725 passed / 2 pre-existing contract reds (baseline-proven), ruff all-pass, lint-imports 16/0, diff-check clean, WARN-seed marker exactly once.**

**AC-L LIVE WITNESS: BOTH LEGS PASS — frozen judges executed verbatim, first-run-stands.** Leg-1 (trial `a18c2a86`): scripted-pick start → G1 → live CD (gpt-5) → §07 real Gamma deck → paused-at-gate; judge-1 **13/13** — `ok/match`, `clock_eligible: true`, `cd_status: resolved`, three directive digests non-null + identical + equal to on-disk `trial-start.json`; **S-flip parity clock: tick 1**. Leg-2 (rewind-recover trial `4d465677`: CD kept, gary+downstream dropped, SSOT `amount: minimal→concise` mutated post-CD/pre-gary): judge-2 **10/10** — `divergence/resolution-mismatch` WARN carrying both envelopes, three digests EQUAL (genuine same-bytes disagreement; F-806 satisfied — ssot AND base-resolution digests both diverged, gary's live digest matched the prepare-time prediction), walk NOT halted; SSOT git-restored + resolver re-probed. Evidence: `evidence/s3-acl-liveproof-20260707T011735Z/` (PROOF.md + judges + verbatim outputs + 6 drivers + logs).

**Mid-witness event (on the record):** leg-1 first crossing of §07 surfaced the pre-existing `normalize_title` apostrophe defect (deterministic `brief-unmatched`; 8 Gamma decks burned across attempt-1's auto-retry×3 + one documented pre-fix recover). Orchestrator stood the live lane down, convened the focused 3-seat round (party record §10, 3/3 CONCUR-W-RIDERS), landed the ratified fix RED-first (10 witnesses; the collide-loud pin exposed a pre-fix SILENT wrong-slot binding), committed FIRST at `59a9a48a` per ratified sequencing, then authorized ONE recover. The frozen judges never executed pre-fix — the recover is the legitimate error-pause→recover product path, not retry-to-green. Total spend: 10 Gamma generations + ~$0.30 OpenAI (LangSmith-measured).

Next poll: SOP-010 at the S3 close commit.

### SOP-010 — S3 story-close audit (2026-07-07, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Commit integrity CLEAN, both commits:** `59a9a48a` = exactly the ratified 6-file matcher/governance set with all four §10 riders verified IN the diff (W1 live-pair, W2 per-char, W3 collide-loud, W4 mutant-killer; dual-pass at gamma_operations.py:1474-1495; live re-probe reproduces). `7630d091` = exactly the S3 set — **16 dev .py counted (F-902 honored)** + story + ledger + 27-file evidence pack + sidecar = 46 files. No stray in either commit; all protected untracked paths still `??`. **F-802 fence holds** (zero commits touching pipeline-manifest/package_builders). Sidecar = exactly ONE appended event, timestamp inside leg-1's start window, prior events byte-intact.

**Post-commit green REPRODUCED:** 215/215 across the touched surface (serial); lint-imports 16/0; ruff 0-new byte-verified (the 18 findings in gamma_operations.py are identical at `d049453b`).

**Live-evidence single-pass VERIFIED AGAINST THE CLOCK:** judges frozen 01:19Z (before any leg); fix committed 01:50:39Z; post-fix recover 01:51:53Z; judge-1 02:22Z; judge-2 02:25Z — **no judge output predates the fix; both pre-fix attempts failed un-judged** (error-pause→recover, not retry-to-green). Judge-facts ↔ receipts consistent: leg-1 three-way attestation non-null + identical + equal to on-disk trial-start.json, F-402 10-key set exact; leg-2 directive digests EQUAL (genuine same-bytes), gary's live digest == the prepare-time predicted post-mutation digest, WARN verbatim in the walk log, run not halted. **Mutation hygiene CLEAN** (SSOT byte-identical to `d049453b` in git and worktree). **Story flip ACCURATE** (every status-line claim checked). **Spot-audits P2+P7 at full strength in committed code.** **Baseline discipline HELD** (2 pre-existing contract reds reproduce; neither file touched).

**Findings (both advisory):** F-1001 PROOF.md "~02:19" vs authoritative 02:22 stamps — narrative precision only. F-1002 the 18 pre-existing ruff errors in gamma_operations.py — recommend a ruff-clean pass ride that file's next touch.

**Carried:** F-901 noted-in-record ✔ · F-902 honored ✔ · F-701 honored ✔ (distinct files per attempt; sidecar pure append).

**Verdict: CONCUR-WITH-FINDINGS — S3 DONE STANDS; S4 UNBLOCKS.** Next poll: **SOP-011 at S4 spec pre-dispatch**, verifying (1) the E4 clock-attestation defer explicitly weighed by the S4 author; (2) scope matches the §7 re-scoped S4 row with the committed v1 receipt schema cited as input contract; (3) F-705 WARN-seed ownership formally transfers to S4 with a byte-diff witness planned; (4) the §10 deferred filings stay filed, not silently absorbed.

**Orchestrator disposition (recorded at relay):** F-1001/F-1002 accepted as advisory (F-1002 noted for gamma_operations.py's next touch). SOP-011 obligations carried into next-session-start-here + SESSION-HANDOFF for the S4 spec author. Session-17 WRAPUP proceeds per the operator's directive (fresh session for S4).

### SOP-011 — S4 spec pre-dispatch review (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Artifact:** `canonical-arc-s4-fail-loud-flip.md` (FAIL-LOUD flip: Flip A styleguide-less WARN-seed → hard raise; Flip B parity `divergence` → hard raise; authority S-flip deferred). **Method:** independent code verification of every anchor at HEAD `13792617`; parity.py treated as frozen input contract.

**Fidelity to §7 S4 row:** MATCH — two flips, authority excluded; §1's "at trial-start" relocation to §07-pre-spend is a documented legitimate relocation (§7 supersedes §1); the spec cites `_act.py:587-597` correctly (more accurate than §7 L140's stale `:519-528`). No scope smuggled/dropped.

**Obligations (a)-(d): ALL HONORED.** (a) E4 two-way ruling SOUND — `divergence` is only reachable when comparable directive digests collapse to ≤1 (`parity.py:321-327`), so a divergence already implies present attestations agree; three-way is a clock (S-flip) concern; S4 touches `clock_eligible` nowhere (Flip A branches on `item.get("styleguide")`, Flip B on `receipt["outcome"]`; AC-7 pins it). (b) 13-key `_receipt` / 10-key `CD_STYLEGUIDE_RESOLUTION_V1_KEYS` / trichotomy all cited accurately; ZERO parity.py edits. (c) AC-2 is a genuine byte-diff witness (WARN-absent + tag + DEFAULT_VARIANT_PAIR retained + success-path untouched). (d) both §10 filings present in `deferred-inventory.md:56-57` + named Out-of-scope.

**F-1100 (highest-risk claim CONFIRMED FEASIBLE — the load-bearing trace):** `GaryActError(SpecialistDispatchError)` (`_act.py:314`) raised in the resolve/dispatch path → `act()`'s `except GaryActError` re-raises (`_act.py:1352-1354`, does NOT swallow) → `_invoke_specialist_with_retry` catches `SpecialistDispatchError` (`production_runner.py:1816`), tag ∉ `_RETRYABLE_DISPATCH_TAGS` (`:1790-1798`) → re-raises immediately → walker `_pause_at_error`. Both new tags land non-retryable deterministic error-pause BY DEFAULT; Flip B raise sits between the receipt (`:1115`) and the dispatch loop (`:1135`) = pre-spend; Flip A raises inside `:1114` = pre-spend. Structurally sound.

**F-1101 (MATERIAL, dispatch-blocking part iii):** Flip A's `else`-branch raise fires ONLY on a NAMED variant present-but-styleguide-less; it does NOT fire on empty/absent `gamma_settings` (falls back to `("A",)`, `variant_settings=None`, styleguide-less, no raise; parity then classifies `ok/status-keyed-no-picks` — AC-5 lets it proceed). Contradicts the spec's "retirement of the whole no-pick path" claim + §7 D-skip; AC-L Leg-1 built as empty gamma_settings would silently NOT fire (false negative). Remedy: (i) scope the retirement claim to the named-variant case; (ii) state the empty/declined leg is closed by a deferred trial-start pre-check; (iii) pin AC-1 + AC-L Leg-1 to a named-variant-styleguide-less payload [(iii) dispatch-blocking].

**F-1102 (MATERIAL, dispatch-blocking; S3-F801/F802-class):** `divergence/contract-violation` is ALSO the total-comparator crash fallback (`parity.py:181-195`) — post-flip a comparator SELF-CRASH on an otherwise-dispatchable envelope would HALT a run that pre-S4 WARN-shipped. Halting is defensible/correct ($0, recoverable, a broken auditor should surface) but MUST be an explicit ruling, not a silent consequence. Remedy: add the explicit "halt-on-comparator-self-crash is INTENDED" ruling to D2/AC-4.

**F-1103 (minor):** Flip-B message overstates "same directive bytes" — `resolution-mismatch` reachable with one digest present; soften to "attestations agree where both present." **F-1104 (minor):** `list_themes` (`_act.py:1107`) runs before both flips but is non-generative — AC-L should assert pre-spend on the generate/create-from-template methods and note list_themes is a permitted call.

**Verdict: CONCUR-WITH-FINDINGS** — dispatch approved once F-1101(iii) + F-1102 applied to the spec text (both cheap); F-1101(i)/(ii), F-1103, F-1104 are dev/T11 notes. No manufactured-outage trap (Leg-3 + F-802 trichotomy tolerance verified sound); no under-fire on the production named-variant path.

**Orchestrator disposition (recorded at relay):** ALL applied to the spec text pre-dispatch. **F-1101:** adopted the NARROW scope (matches the literal §7 WARN-seed; avoids the W5-morph legacy-bundle false-fail a §07 whole-dispatch chokepoint would carry) — D1 "Scope boundary" rewritten; AC-1 + AC-L Leg-1 pinned to a named-variant-styleguide-less payload (+ companion negative for empty gamma_settings); the empty/declined leg of §7 D-skip filed as the NEW deferred follow-on `styleguide-mandatory-pick-trial-start-precheck` (deferred-inventory) so it stays tracked. **F-1102:** explicit "halt-on-comparator-self-crash is INTENDED" ruling added to D2 + an AC-4 crash-fallback witness. **F-1103/F-1104:** message softened, list_themes noted. Spec flipped READY-FOR-DEV; dev dispatch cleared. Next poll: **SOP-012 at S4 dev-complete** (verify F-1101 named-variant scope landed, F-1102 crash-halt witnessed, parity.py diff empty, both new tags non-retryable).

### SOP-012 — S4 dev-complete verification (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Method:** code-first read of both flips + all 36 test adaptations; touched-suite re-run `-n 0`; baseline reproduction in a throwaway `13792617` worktree.

**Mandatory checks ALL PASS:** (1) `git diff app/styleguide/parity.py` EMPTY (AC-6). (2) Flip A landed F-1101-amended — `_act.py:587-605` raises `gamma.styleguide.unbound` ONLY on a named variant present-without-`styleguide`; empty/absent gamma_settings falls to default-A, does NOT raise (`ok/status-keyed-no-picks`); `DEFAULT_VARIANT_PAIR` retained. (3) Flip B `_act.py:1138-1147` raises `gamma.styleguide.parity-divergence` between the receipt (`:1127`) and the dispatch loop (`:1167`) — only non-generative `list_themes`/`_theme_id` precede = PRE-SPEND; parametrized 3 reasons. (4) F-1102 crash-halt via the REAL comparator crash path (`_force_comparator_crash` injects a `set` into resolved_base → the frozen comparator's own `json.dumps` raises → `divergence/contract-violation`), NOT a faked verdict. (5) both tags NON-RETRYABLE; `production_runner.py` diff EMPTY, `_RETRYABLE_DISPATCH_TAGS` unmodified; AC-8 walk-pin proves both surface as real `paused-at-error` @ node 07 (F-1100 confirmed live). (6) AC-9 teeth PRESERVED (below). (7) AC-3 success branch byte-untouched, golden pinned. (8) baseline: 2 Texas-internal reds reproduce identically at HEAD, touch no S4 file; ruff clean on 5 touched.

**AC-9 verdict — PRESERVED, not weakened:** the 31 gary tests rebind a styleguide-less variant to a synthetic guide (`_s4_seed.install_seed_resolver`) whose resolved base = `DEFAULT_VARIANT_PAIR` minus `variant_id`, so `merged={"variant_id":vid, **resolved_base}` is byte-identical → all enum/theme/packet asserts hold unchanged. `test_gary_variant_arc` excludes ONLY the `styleguide` binding key (resolver-consumed, never in the packet) — legitimate binding-vs-setting, not a loosening. Raise-expectations RELOCATED not deleted (WARN→raise conversions). The 5 S3 parity tests keep receipt-content coverage; the one now-impossible gary-level scenario's granular teeth (`clock_eligible False`, `gary_resolution_digest==canonical_resolution_digest({})`, `gary_bound_guides==[]`) VERIFIED still covered unmodified at `tests/styleguide/test_parity_comparator.py::test_status_keyed_no_picks_never_compares_the_default_seed`. No coverage silently dropped.

**Findings (both NOTES, non-blocking):** F-1200 — the `_s4_seed` autouse fixture blankets `resolve_styleguide` module-wide in `test_gary_gamma_dispatch.py`/`test_gary_studio_mode.py`; safe today but a future styleguide-less test added there would be silently coerced onto the seed path (T11 note). F-1201 — the 2 Texas-internal baseline reds carry (no S4 action; = F-1002 family).

**Verdict: CONCUR-WITH-FINDINGS** — both findings NOTES, neither RED-first-blocking. Offline diff faithful, correctly scoped, no manufactured outage, no assertion weakened. Story must NOT flip done until the AC-L live 3-leg PASS; `parity.py` diff must remain empty through commit.

### T11 3-lane bmad-code-review for S4 (2026-07-07, orchestrator record) — Blind / Edge / Acceptance

- **Acceptance Auditor: PASS** — AC-1..AC-9 all MET, no weakened assertions (independently re-verified the AC-9 relocation of the F-804 teeth). 1 NIT: `test_comparator_contract_violation_now_halts_dispatch` asserts the divergence reason via the exception message string; receipt-content coverage preserved elsewhere.
- **Blind Hunter: CLEAN** — no MUST/SHOULD correctness bugs; execution-verified pre-spend in Classic+Studio, the full `GaryActError(SpecialistDispatchError)→re-raise→non-retryable→paused-at-error` trace, reason survives in the message, `parity.py` byte-untouched. NIT-1: stale comments (`:1061`,`:1144`) claim "both envelopes ride the receipt on this contribution" — but on divergence the caller RAISES before building the gary contribution, so the receipt is discarded. NIT-2 (consequent): the operator gets tag+reason but NOT the three digests localizing the divergence.
- **Edge Case Hunter: 1 SHOULD-FIX + NITs, no MUST-FIX** — over-fire hunt clean (all tolerated states + legacy/None proceed; crash-fallback correct, unreachable by benign yaml-native input; studio fork protected; resume re-raises $0 no double-count). **SHOULD-FIX (converges with Blind NIT-1/2):** the Flip-B halt discards the parity receipt so AC-4/D2 "both envelopes reachable for triage" is UNMET, and the raised message's closing claim "Both envelopes ride the styleguide_parity receipt" is FALSE on the halt path (execution-verified: message contains no digest). Fix: interpolate a compact digest summary into the raise AND correct the wording. NITs: stale comment `:676-680` (dead unbound-studio path post-flip); coverage gaps — mixed-variant A-bound+B-unbound, empty-list `[]`, and **the E4 two-way-divergence raise (`trial_start_directive_digest=None`) — the story's load-bearing ruling, unwitnessed at the flip surface**.

**Orchestrator triage (recorded): 1 SHOULD-FIX + 3 coverage + 3 NIT to remediate RED-first; 2 monitor NOTES; 0 dismissed-as-wrong.**
- **R1 [SHOULD-FIX]** enrich the `gamma.styleguide.parity-divergence` raise message with a COMPACT DIGEST SUMMARY (cd_resolution_digest, gary_resolution_digest, cd/gary/trial_start directive digests from the receipt), and CORRECT the false "both envelopes ride the receipt" wording in the raise + the `_LOGGER.error` line + the stale comments (`:1061`,`:1144`) to state what actually survives (tag+reason+digests in the error; CD's own envelope separately recoverable from its persisted contribution). Satisfies AC-4/D2; removes the false operator-facing claim. RED-first: assert the message carries the digests and makes no "ride the receipt" claim.
- **R2 [coverage]** E4 two-way witness: a `divergence` with `trial_start_directive_digest=None` still raises Flip B (witnesses the E4 two-way ruling at the flip surface).
- **R3 [coverage]** mixed-variant A-styleguided + B-styleguide-less ⇒ raises `unbound` on B; **R4 [coverage]** `gamma_settings=[]` (empty list) ⇒ default-A proceeds, no raise.
- **R5 [NIT]** correct the stale dead-path comment `:676-680`. **R6 [NIT/F-1200]** add a guard-comment (or de-autouse) so a future styleguide-less test can't be silently coerced onto the seed path in the two blanketed modules. **R7 [Auditor NIT]** folded into R1 (the enriched message test also witnesses the contract-violation reason).
- **NOTES (no code):** F-1201 baseline reds carry; F-1200 mitigated by R6.

Next: fresh dev RED-first remediation R1-R6 → orchestrator re-verify → **AC-L live 3-leg** → commit → SOP-013 close poll.

### SOP-013 — S4 story-close audit (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed; full text in agent transcript)

**Target:** close commit `63369c99` (base `13792617`). **All 8 checks PASS.**
(1) Commit integrity — exactly the S4 set; NO stray committed (workbooks-test, 3 operator monitor ledgers, goal launcher, both `runs/` strays all still untracked; `git ls-files` shows no run dirs committed). (2) `git diff 13792617 63369c99 -- app/styleguide/parity.py` EMPTY + `production_runner.py` EMPTY — both byte-frozen. (3) `_RETRYABLE_DISPATCH_TAGS` unmodified; neither new tag present. (4) sidecar = exactly ONE appended line (leg-3 pick, run_id 4fe6073f), prior 4 intact. (5) live-evidence single-pass: judges frozen 04:13:57Z BEFORE earliest leg 04:14:50Z; each ran once; no retry-to-green; Leg-1 unbound 12/12, Leg-2 divergence→ERROR 16/16 (genuine same-bytes divergence — three directive digests EQUAL `ff90c166…`, resolution digests differ from the F-806 `amount minimal→concise` mutation), Leg-3 happy 15/15 (real deck `npkNxi1NwrKbfPj3NU61I`, `ok/match`, walk proceeded). (6) yaml git-clean (leg-2 mutation reverted). (7) DONE-line every claim evidence-supported; deferred-inventory closes the fail-loud-flip + files the precheck complement. (8) post-commit green: gary+composition 249 passed/1 skip, styleguide 54 passed; the ~21 F-605 g0-battery reds are the separately-tracked S5-open precondition S4 neither touches nor fixes.
**Adversarial cross-checks resolved:** committed `_act.py` flip strings byte-identical to the walk-log ERROR messages the judges asserted (tested code IS committed code); run dirs live under gitignored `state/config/runs/`, none committed.

**Verdict: CONCUR (clean — no findings). S4 DONE STANDS.** Arc may proceed to the pre-S5 g0-battery story (owns the F-605 corpus-fixture commit + ACTIVE_TERMINAL_GATES refresh — the binding S5-open precondition). Next poll: SOP-014 at the pre-S5 g0-battery story's pre-dispatch.

---

## ✅ S4 CLOSED (canonical-arc, session 18) — FAIL-LOUD flip live-proven both legs + happy anti-outage; commit `63369c99` pushed. Arc: S0·S1·S2·S3·S4 CLOSED. Next: pre-S5 g0-battery precondition → S5 → S6.

### SOP-014 — pre-S5 g0-battery baseline spec pre-dispatch review (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Artifact:** `canonical-arc-pre-s5-g0-battery-baseline.md`. **Method:** code-first at HEAD `63369c99`; ran the two governing dirs.

**PASS findings:** F-1403 fixture shape fully determined by the offline pre-pass (`_split_components` one-component-per-heading; `_offline_pre_pass` one provisional-LO-per-file auto-grounded) → D1's constraint list ACCURATE, ONE-file corpus sufficient, "1 H1 + 3 H2" → exactly 4 components (H1 counts), LO provenance satisfied by construction. F-1404 pin refresh legitimate (`G0R` real addition at `b59679ce`; pin maintained at `e5e24ad3` but not `b59679ce` → code current/test stale; refresh test-to-code, keep full exact tuple). F-1405 no gitignore trap (`.gitignore` excludes `**/private/`, `staging/`, binary media — NOT `.md`; `git check-ignore` on the lesson.md → exit 1; confirms CREATE-`.md` over re-point-to-`.docx` was right). F-1406 scope sound (AC-5 holds; offline-only proportionate; T11 discharged by the green battery — subject to F-1401).

**F-1401 [MEDIUM, applied]:** corpus-absence reds are **15 not 13** — +2 in `test_irene_refinement_brick.py` (`test_ac_s3_6_wiring_reads_gate1_provisional_los_and_refines`, `test_full_two_gate_offline_refines_and_ratifies`), same `studio-smoke-min` cause, fixture-resolved. These ARE the two-gate offline refine+ratify path the T11-discharge argument leans on → added to AC-1 + RED-first.
**F-1402 [MEDIUM, applied]:** 2 INDEPENDENT pre-existing drift reds remain after the fix, NOT corpus-absence, NOT this story's job: `test_front_door_selection_threading::test_run_summary_pack_hash_default_is_byte_identical_to_raw` (manifest pack_hash mismatch) + `test_run_summary_yaml_emit::test_clean_trial_run_summary_populated` (specialist_roster_count 17≠12). AC-4 now names them as expected residual + forbids touching manifest/roster (AC-5/lockstep guard). "~21" reconciled to 18-at-HEAD → 2 residual after fix. Filed as follow-ons.

**Verdict: CONCUR-WITH-FINDINGS** — no BLOCK; both are spec-clarity fixes (applied pre-dispatch). The g0-enrichment substrate is green-ready; the missing fixture is the whole gap, exactly as §8 diagnosed. Next poll: SOP-015 at dev-complete (verify 18→2, no manifest/roster touch, corpus tracked+fresh-clone-green).

### SOP-015 — pre-S5 g0-battery baseline STORY-CLOSE audit (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Commit `a1158385`. All 7 checks PASS, no findings.** (1) commit = exactly 5 files {studio-smoke-min/lesson.md, the pin test, story spec, arc ledger, deferred-inventory}, no stray (all 7 strays still untracked). (2) `git show a1158385 -- app/ pipeline-manifest.yaml` EMPTY. (3) 18→2: `tests/integration/marcus/ tests/unit/marcus/cli/ -n 0` = 2 failed/466 passed — residual EXACTLY the 2 named drift reds (pack_hash + roster_count 17≠12). (4) fixture HONEST — genuine 1 H1 + 3 H2 outline; brick tests consume it structurally (≥4 components, anchored, verbatim excerpts); spot-run `-k "g0_enrichment_brick or irene_refinement_brick"` 75 passed incl. the 2 two-gate refine+ratify tests. (5) pin asserts the FULL exact tuple (G0R annotated, not weakened). (6) `git ls-files` tracks the lesson.md, `check-ignore` exit 1 — fresh clone greens. (7) §8 precondition MET.

**Verdict: CONCUR. pre-S5 g0-battery DONE. S5 (G0 canonical) UNBLOCKS.** Next poll: SOP-016 at the S5 spec pre-dispatch.

---

## ✅ pre-S5 g0-battery CLOSED (session 18) — 18→2, S5-open precondition MET; commit `a1158385` pushed. Arc: S0·S1·S2·S3·S4 + S5-precondition CLOSED. Next: S5 (G0 canonical, M/L — likely 3a migration / 3b flip split) → S6.

### SOP-016 — S5-3a first-pause-migration spec pre-dispatch review (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Artifact:** `canonical-arc-s5-3a-first-pause-migration.md`. **Method:** code-first at `a1158385`; independently re-derived the blast radius across ALL of `tests/`.

**F-1601 [HIGH, blocking — APPLIED]:** the spec's grep scope (`tests/integration/marcus/` + `tests/composition/`) was one dir too narrow — **`tests/marcus/orchestrator/test_start_walk_no_motion.py:90`** asserts `paused_gate=="G1"` on the REAL `run_production_trial`, offline (no live marker, runs in the default suite), traverses the same env-gated G0E branch (`production_runner.py:2414-2424`) → RED at the 3b flip. A missed suite = a broken 3b. Added to the 3a migration set (now 8 offline suites).
**F-1602 [MEDIUM — APPLIED]:** `tests/live/test_production_trial_smoke_with_gate.py:40` (`@live`, `paused_gate=="G1"`) — doesn't break the offline suite but 3b's live witness leg must migrate it; named as a 3b handoff in Out-of-scope.
**F-1603..F-1608 [INFO, confirmed]:** exclusions all correct (`marcus_duality_boundary` full-set; `run_summary_yaml_emit` = drift-red follow-on; ledger/seam synthetic fixtures; resume-suite synthetic single-gate manifests; unit input-constructions). No shared first-pause helper in any conftest (per-suite migration stands). Split SOUND (8 offline + 1 live >> A2 N>5, no helper to collapse). M1 rubric SOUND — AC-1 env-independence is genuinely the OPPOSITE of both-worlds-green vanity (each test pins ONE env, asserts the DISTINCT walk it drives). Scope-fence CLEAN — `g0_enrichment_active()` reads the env directly (test-settable via monkeypatch, no prod change); **bonus: G0R rides the SAME env var** (`irene_refinement_active()` delegates to `g0_enrichment_active()`) so one pin wakes both G0E+G0R. AC-5 parity-pin preservation adequate (first-pause assertion structurally separable from the S3/S4 teeth).

**Verdict: CONCUR-WITH-FINDINGS** — F-1601 (blocking) + F-1602 applied pre-dispatch; the rest concur. Dev T1 must re-grep across ALL `tests/`. Next poll: SOP-017 at 3a dev-complete.

### SOP-017 — S5-3a dev-complete + CLOSE verification (2026-07-07, session 18, fresh monitor agent; absorbs 3-lane for the test-only diff) — RELAYED (condensed)

**Commit `721cce04` (base `a1158385`). CONCUR-WITH-FINDINGS — all confirmatory, no remediation.**
F-1701 commit clean: exactly {8 migrated test files + spec + ledger}; `git show 721cce04 -- app/ state/config/` EMPTY; parity.py + manifest untouched; 7 strays still untracked. F-1702 disposition HONEST: all 8 pin `setenv("MARCUS_G0_ENRICHMENT_ACTIVE","0")` (explicit "0", never delenv — survives 3b's code-default flip; verified against `g0_enrichment_active()` :123-130); `git diff --numstat` = ZERO removed lines every file; no D-delete; no weakened/deleted assertion. F-1703 parity preserved: `test_gary_parity_walk_pin.py` 16 added/0 removed, S3/S4 teeth byte-unchanged, parity.py frozen. F-1704 coverage-deferral to 3b LEGITIMATE: the offline suites pass a FILE (`trial_corpus/README.md`) but the G0E path needs a corpus DIRECTORY (`_walk_corpus_files`), so a canonical G0E-first assertion can't be driven without a fence-violating change — the dev correctly refused; **3b's named obligation (already in the 3b spec AC-L(a)): a canonical G0E→G0R→G1 witness on a corpus DIRECTORY, unset-env post-flip**. F-1705 robustness: 61 pass at default-OFF AND forced-ON; 19-RED load-bearing witness reproduced at base (matches spec). F-1706 zero new baseline reds (696 passed / 4 pre-existing = 2 drift + slab_7a unicode + texas_to_cd_chain, all reproduced at base).

**Verdict: CONCUR. S5-3a DONE STANDS. 3b UNBLOCKS.** Next poll: SOP-018 at the 3b spec pre-dispatch.

---

## ✅ S5-3a CLOSED (session 18) — first-pause migration, env-independence for 8 offline suites, test-only, 0 new reds; commit `721cce04` pushed. Arc: S0·S1·S2·S3·S4 + S5-precondition + S5-3a CLOSED. Next: S5-3b (default flip + live G0E/G0R witness).

### SOP-018 — S5-3b default-flip spec pre-dispatch review (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Verdict: CONCUR-WITH-FINDINGS.** Spec fundamentally sound: flip target EXACT (`g0_enrichment_active` :123-130; `irene_refinement_active` delegates → one flip wakes G0R); **Tier-1 GENUINELY held** (`pipeline-manifest.yaml:166-261` already defines g0-enrichment/G0E/irene-refinement/G0R nodes + edges `__start__→g0-enrichment-gate→g0-ratify-gate→01` :1031-1037 — the flip is a runtime toggle, no manifest edit); **D2 blast radius correctly framed** as a T1 discovery with the right STOP guard — monitor independently corroborated the residual is ~0-5 (synthetic-single-gate-manifest tests are immune; the real-manifest full-walk pins were already 3a-migrated; `error_pause_recover:116` even carries a "keeps first pause G1 under the 3b default flip" comment). **F-1801 (HIGH)** — "live in production" under-specified AND absent (no production code sets `MARCUS_G0_DISPATCH_LIVE`; runner AND-gates it at `production_runner.py:2649-2653`; only evidence drivers arm it) → raised the "canonical = structure vs content" interpretation to the party. F-1802 (MED) truth-table incomplete. F-1803/1804/1805 (LOW) dev-authority refinements. Protected invariants LOW-risk (Beats fire before node 01; shim already accepts G0E/G0R verbs).

### F-1801 PARTY RATIFICATION — focused 4-seat round (2026-07-07, session 18) — 4/4 RATIFY-A, no dissent, no impasse

**Winston (architecture) / John (PM, decision-owner) / Murat (test) / Dan (CD) — ALL RATIFY-A.** Decision: the operator directive "canonical — performed on every run with HIL input" binds on the **HIL GATES (structure)**, not on live-LLM content every run. **Reading A:** G0E/G0R HIL gates + deterministic recorded enrichment canonical EVERY run; live LLM enrichment operator-ARMED (`g0_dispatch_live` stays default-OFF — matches the `MARCUS_RESEARCH_DISPATCH_LIVE` precedent; keeps 3b Tier-1; hermetic/reproducible default). Reading B (forced live every run) rejected (scope-creep, corrupts the hermetic default). **Convergent reasoning:** John — "HIL input" = human at the gates, not live tokens; (A) is losslessly upgradeable, party-ratifiable not operator-escalation. Winston — B conflates "loop canonical" (structural, what 3b flips) with "content live" (cost/determinism policy); symmetry with research-wiring; fix the silent-deterministic trap via LEGIBILITY (stamp resolved mode into bundle, fail-loud) not by forcing live. Murat — the M-wit's "separate default-witness for dispatch_live deterministic path with a receipt" ALREADY presupposes (A); B corrupts the hermetic default test path. Dan — deterministic enrichment is a legitimate HIL surface (value = a real editable starting object, not the pre-pass being smart; source-detail→Gamma invariant is agnostic to live-vs-deterministic) **with a NON-NEGOTIABLE caveat: the deterministic default MUST surface a "richer live enrichment available — arm the flag" affordance at G0E/G0R** (else a silent content-quality ceiling).
**Ratified riders (all applied to the 3b spec):** (1) arming = first-class `marcus_spoc` `--g0-dispatch-live` CLI flag/preset (env var = impl seam + dev escape hatch); (2) STAMP resolved enrichment mode (`live`|`deterministic-recorded`) into the run bundle/ledger, fail-loud on ambiguity; (3) Dan's "live-available" affordance at the gate; (4) AC-L two-lane witness (hermetic deterministic + receipt + $0 // armed live via the REAL CLI switch + real LLM receipt + divergence guard); (5) FILE `g0-production-default-dispatch-live-decision` as a future Tier-2 operator-vision follow-on (NOT 3b).

**Verdict: CONCUR — 3b spec amended, dev dispatch cleared.** Next poll: SOP-019 at 3b dev-complete.

### S5-3b dev STOP + RE-SCOPE party round (2026-07-07, session 18) — 3-seat consensus, no impasse

**3b dev correctly hit the STOP gate.** T1 flip-and-sweep found the TRUE flip blast radius = **24 tests / 9 suites BEYOND the 3a-8** (total 32), all ONE class: they pass a README FILE as `corpus_path`, which only worked while G0-enrichment was a dormant no-op; the flip wakes G0E's corpus-DIRECTORY enumeration → `DirectiveCompositionError` pre-gate. SOP-018's ~0-5 estimate was materially wrong (blind to the real-manifest+file-corpus IMPLICIT contract — retro note: the estimator needs a "who relies on a dormant node being a no-op?" lens, not just first-pause reachability). 22 are downstream-subject tests; 2 are feature-flag tests whose "default-OFF byte-identical" contract the flip INVERTS. Flip CODE is sound (D1 truth-table proven — enumerated falsy kill-switch set, unset/empty/whitespace/`maybe`→True; Tier-1 held, manifest+parity untouched; 3a-8 green; D3 narration+affordance + D4 mode-stamp/CLI-arm landed offline). Dev did NOT migrate — parked, reported.

**Re-scope round (Winston/Murat/John — the 3 relevant lenses):**
- **John (PM, decision-owner): RATIFY-B** — split into a separate **S5-3a.2** migration story that lands+closes FIRST (flag OFF), then 3b re-runs clean. M1 migration-before-flip is literal; the monitor's estimate miss argues for MORE separation (isolate migration behind its own green gate); a migration-free flip commit is auditable in isolation; velocity cost marginal (one root cause).
- **Murat (test): Q1 = (i)** per-suite explicit kill-switch pins (`setenv("MARCUS_G0_ENRICHMENT_ACTIVE","0")`, 3a-style) for the 22 downstream — subject-preserving, no over-pin; REJECT (ii) directory-fixture (coupling — forces the woken path) and (iii) broad autouse (over-pin risk). Guardrail: dev confirms per-suite enrichment-orthogonality before pinning; a misfiled canonical-path test gets a directory fixture instead. **Q2 = genuine RE-CONTRACT** the 2 feature-flag tests (their premise is inverted — a pin = both-worlds-green vanity): re-home the legacy default-OFF assertion behind explicit `setenv 0` + a NEW positive default-ON witness. **Binding: a 24-row test-disposition ledger** (22 pins + 2 re-contracts, each spawning a default-ON witness) — no test reaches 3a.2-green without a row.
- **Winston (architecture): SPLIT (concurs B)** — strangler-fig, migrate consumers first, flip last. **PLUS a filed production follow-on** (#1): a lone file is not the canonical corpus (corpus=directory), so test-migration is the honest fix — but a real operator pointing a run at a single file gets an opaque `DirectiveCompositionError` deep in G0E (fail-loud-but-NOT-legible gap). Min fix: validate corpus_path at the SPOC boundary, reject a bare file early with a clear message; the graceful-one-file-corpus option framed for John/operator. File regardless of test path (improves the real SPOC runtime — earns its place under the guardrail).

**Ratified plan:** (1) file S5-3a.2 (migration-only, per Murat's dispositions + 24-row ledger, green under BOTH flag states, flag stays OFF); (2) file the production follow-on `g0-single-file-corpus-opaque-crash-legibility`; (3) close 3a.2; (4) unpark 3b (re-apply the preserved flip patch on the migrated baseline → near-empty flip commit + two-lane live witness). 3b flip work preserved (patch + test in scratchpad). Next poll: SOP-019 at the S5-3a.2 spec pre-dispatch.

### SOP-019 — S5-3a.2 file-corpus-migration spec pre-dispatch review (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Method:** independently reproduced the causation-isolated FULL-`tests/` sweep (`-n 0`, process `MARCUS_G0_ENRICHMENT_ACTIVE=1` vs `=0`, ~8.5 min each, 6600+ tests), `ON-fail ∖ OFF-fail`, then isolated-re-ran every surprise ON+OFF to separate flip-causation from pollution.

**F-1901 [HIGH, applied]:** the set is **25 not 24** — a 23rd downstream flip-caused test missed: `tests/parity/test_trial_475_directive_composition_regression.py::test_start_trial_threads_composed_directive_to_texas_dispatch` (isolated-ON fail / isolated-OFF pass, unambiguous). In `tests/parity/` — OUTSIDE the earlier grep scope (same miss-class as F-1601). **F-1902 [MED, applied]:** it's a SECOND mechanism — trial_475 uses a VALID DIRECTORY corpus, flip-caused by first-pause relocation to G0E (`texas_payloads == []` :391), NOT a file-corpus crash; the spec's "all share ONE root cause" was wrong; AC-1 RED generalized. **F-1903 [MED, applied]:** AC-6 must score by CAUSATION-ISOLATION — 2 full-ON reds are non-flip-caused noise (`test_ac11…` cross-suite pollution + `test_real_tejal_workbook_docx_witness` docx OSError on the untracked workbooks-test/ stray) + a tz flake; named. **F-1905 [applied]:** g0 default-ON witness uses a DIRECTORY corpus via `setenv("1")`; irene parity witness → skip-until-3b (un-skip carried to 3b). **F-1904 [applied]:** T1 = full-tree causation-isolated sweep, not a list/grep. **F-1907 [confirming]:** completeness PROVEN — process-env sim faithful for env-untouched tests; EXACTLY 2 `delenv` sites tree-wide (the 2 feature-flag tests) + no conftest env manip → sweep(23) + read(2) = 25 complete. **F-1906 [confirming]:** the 22 reproduce exactly; dispositions honest; all 23 downstream genuinely enrichment-orthogonal; NONE misfiled; AC-4 test-only scope-fence sound; `setenv("0")` survives the real flip; the production single-file-corpus follow-on correctly filed not folded.

**Verdict: CONCUR-WITH-FINDINGS** — flip code + dispositions sound; F-1901 (25th) + F-1902/1903/1905/1904 applied pre-dispatch. Next poll: SOP-020 at 3a.2 dev-complete (verify 23 pins + 2 re-contracts, ledger=25 rows, `git diff -- app/ state/config/` empty, AC-6 causation-isolated zero-flip-reds, trial_475 pinned).

### SOP-020 — S5-3a.2 CLOSE verification (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Commit `3eff93da` (base `721cce04`). CONCUR-WITH-FINDINGS — S5-3a.2 DONE STANDS; 3b UNBLOCKS flip-ready.**
F-2001 commit integrity CLEAN: exactly 14 files (10 migrated tests + 3a.2 spec + parked 3b spec + ledger + deferred-inventory); `git show 3eff93da -- app/ state/config/` EMPTY (AC-4 held); all strays untracked. F-2002 25-set fully migrated, dispositions HONEST: 8 files' file-scoped autouse `setenv("0")` pins cover the 23 downstream (incl. `test_trial_475::test_start_trial_threads…`, F-1901 23rd, first-pause-relocation mechanism); the 2 re-contracts GENUINE not mechanical — g0 renamed `test_ac_s2_5_kill_switch_off…` (legacy behind `setenv("0")`) + NEW `test_ac_s2_5_default_on_wakes_g0e_first_pause` (`setenv("1")` on DIRECTORY corpus, green now); irene renamed `test_ac_s3_6_kill_switch_off_parity…` + NEW `test_ac_s3_6_default_on_parity_with_s2` (`@pytest.mark.skip` un-skip-at-3b). No assertion weakened/deleted. **F-2003 AC-6 flip-readiness = ZERO flip-caused reds:** full `tests/ -n 0` forced-ON 81-fail vs forced-OFF 82-fail → ON-only red set (in-ON ∧ not-in-OFF) is EMPTY; the 3 migrated-file forced-ON reds (pack_hash drift + roster_count drift + `test_trial_475_silent_bypass` Texas-internal) all isolation-confirmed to ALSO fail at forced-OFF = NOT flip-caused; NO 26th exists. F-2004 3a-8 hold GREEN both worlds (61 passed/1 skip at =1 AND =0). F-2005 (informational, non-blocking): the ~81-82 full-SERIAL-run baseline reds (manifest/import-linter/schema-pin/HUD/gate-fold structural + live/psycopg/env-gated + unicode/tz/docx-stray) are a pre-existing dirty-working-tree property, flag-independent, NOT introduced by 3a.2.

**Verdict: CONCUR — S5-3a.2 DONE STANDS. S5-3b UNBLOCKS with a clean flip-ready baseline (the default flip introduces no new red).**

---

## ✅ S5-3a.2 CLOSED (session 18) — 25 tests env-independent, ZERO flip-caused reds remain (3b flip-ready); commit `3eff93da` pushed. **Arc: S0·S1·S2·S3·S4 + S5-precondition + S5-3a + S5-3a.2 CLOSED (4 stories this session).** NEXT: unpark S5-3b (re-implement flip RED-first from spec → SOP + 3-lane → two-lane LIVE witness → close) → S6 Tracy. Un-skip obligation: `test_ac_s3_6_default_on_parity_with_s2` un-skips when the 3b flip lands.

### SOP-021 — S5-3b flip dev-complete verification (2026-07-07, session 18, fresh monitor agent; absorbs 3-lane for the small production diff) — RELAYED (condensed)

**Method:** code-first on the APPLIED working-tree diff (dev completed + reported; verified independently). **CONCUR — no RED-first remediation before AC-L.**
F-2101 D1 truth-table EXACT: `G0_ENRICHMENT_KILL_SWITCH = frozenset({"0","false","no","off"})` (`:157`), predicate `... not in KILL_SWITCH` (NOT `not in truthy`); 47/47 truth-table tests pass; `irene_refinement_active` delegates. F-2102 Tier-1 held (manifest + parity EMPTY; exactly 3 files + 1 new test). F-2103 mode-stamp fail-loud REAL: `resolve_enrichment_mode(model_id)` raises ValueError on unrecognized (not silent), derived from `result.model_id` (content truth, not the flag), stamped on BOTH receipts (`card_payload` + bundle `output`). F-2104 CLI arm `--g0-dispatch-live` store_true → sets `MARCUS_G0_DISPATCH_LIVE=1` only when passed; `g0_dispatch_live()` default-OFF unchanged (Reading A; no production-default-ON). F-2105 affordance appends ONLY when mode==deterministic-recorded; Beats 2-3 narration; pre-node-01 chat only (VO↔on-screen + source-detail untouched). F-2106 un-skip `test_ac_s3_6_default_on_parity_with_s2` PASSES. F-2107 zero flip-induced reds: `tests/integration/marcus/` at code-default-ON = 417 passed/2 skipped/2 failed; both brick suites 77/77; the 2 fails (pack_hash + roster_count 17≠12) reproduce IDENTICALLY at `=0` (dormant) → flip-INDEPENDENT pre-existing drift (the roster-count red — prime flip-suspect since the flip wakes G0E/G0R specialists — persists dormant, confirming static-roster drift orthogonal to this diff). NITs (cosmetic, non-blocking): redundant local `import os` in main(); a near-dead model_id narration fallback. **Verdict: CONCUR — cleared to the orchestrator's AC-L two-lane live witness.**

### SOP-022 — S5-3b STORY-CLOSE audit (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Commit `3404dc1d` (base `6961eeac`). CONCUR — S5-3b DONE STANDS; S5 (G0 canonical) COMPLETE.**
F-2201 commit integrity CLEAN: exactly 31 in-scope files (the flip + marcus_spoc + irene un-skip + new truth-table test + 3b spec + ledger + 26-file AC-L evidence pack). F-2202 frozen paths EMPTY (`git show 3404dc1d -- pipeline-manifest.yaml parity.py` empty — Tier-1 + parity frozen). F-2203 no stray committed. F-2204 flip real: `g0_enrichment_active` = `not in KILL_SWITCH{0,false,no,off}` (default-ON); irene delegates; `resolve_enrichment_mode` raises on unrecognized id; `g0_dispatch_live` default-OFF (no production-default-ON). **F-2205 live-evidence single-pass VERIFIED: judges frozen 08:05:33Z before both lanes; recomputed judge sha256 from the COMMITTED blobs MATCH the frozen manifest exactly (judge_a f0cf3ebb…, judge_b 4443bc18…); each ran once; NO retry-to-green.** JUDGE-a 8/8 (env absent by name, first pause G0E not G1, G0E→G0R→G1, receipt deterministic-recorded, $0), JUDGE-b 4/4 (armed gpt-5 pre-pass, receipt live, divergence guard holds). F-2206 anomalies honest+non-defect (CLI status-mask driver-fixed before any judge; MARCUS_G0_DISPATCH_LIVE arms Irene by design). F-2207 post-commit green (72 + 51 passed). F-2208 un-skip cashed. F-2209 S5 split ancestry contiguous (3a `721cce04` + 3a.2 `3eff93da` ancestors of 3b `3404dc1d`).

**Verdict: CONCUR. S5-3b DONE STANDS. S5 (G0 canonical) COMPLETE (3a+3a.2+3b, live-proven, all pushed).** NEXT: S6 Tracy Scite-canonical.

---

## ✅✅ S5 (G0 CANONICAL) COMPLETE (session 18) — 3a `721cce04` + 3a.2 `3eff93da` + 3b `3404dc1d` (live-proven 2-lane), all pushed. Operator directive "G0 enrichment canonical on every run with HIL input" REALIZED (Reading A). **Arc: S0·S1·S2·S3·S4 + S5-precondition + S5 ALL CLOSED. 5 stories closed this session.** NEXT: S6 Tracy → S7 (⛔ operator spec checkpoint) → S8 composed proof.

### SOP-023 — S6 Tracy/Scite-canonical spec pre-dispatch review (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Verdict: CONCUR-WITH-FINDINGS.** Both load-bearing premises CODE-CONFIRMED. F-2301 the `ready[:2]` selector bug is EXACTLY real — ran `list_providers(shape=retrieval)` live: sorted ready = `['consensus','gamma_docs','scite']`, `ready[:2]` picks consensus+gamma_docs, EXCLUDES scite (`research_wiring.py:128`); D2 fix seam-located (scope `selected` to `['scite']`; `cross_validate=len>1`→False cleanly). F-2302 M-wit LIVE-FEASIBLE NOW: SciteProvider ready+auto-registered; `secrets/scite_oauth_token.json` refreshed today; `.env` has both creds; `TexasRow.source_id` IS the DOI (`scite_provider.py:489-491`, DOI-first); `retrieval:scite:{DOI}`→doi.org resolvable; no hidden blocker. F-2303 one-flag structure CONFIRMED (research fires unconditionally at both walk sites `production_runner.py:2587/3317`, no `research_active()` gate — contrast g0 at :2630 which HAS a structure gate; only `_research_dispatch_live()` gates the live call); D1 default-ON kill-switch right. F-2307 Tier-1 CONFIRMED (research_wiring/production_runner not block_mode_trigger_paths members). F-2306 J1 fence narrow + skip-witness name valid (`consensus-provider-live-enablement`, `research-dispatch-flag-retirement` both in deferred-inventory). **F-2304 [MEDIUM, applied] blast-radius UNDERCOUNT:** a 2nd assert-dormant test `test_ac_d2_two_walk_parity_fires_on_real_continuation` (`:237`) runs a REAL walk through 04.55 with a gap, does NOT pin the flag, stubs only ProductionDispatchAdapter NOT the retrieval adapter → post-flip + live .env creds = **REAL PAID Scite call / network hang in the offline suite**; must pin OFF/fake-adapter; dev MUST run the S5-style full-tree causation-isolation sweep (the ~3+1 is a floor). **F-2305 [LOW, applied]** D4 seam named: creds precondition at `run_research_wiring` ENTRY (replacing the `:265-275` silent fail-soft). F-2308 [INFO] minor line drift (source_id `contracts.py:112`; select_posture `:128`).

**Applied to the spec: AC-5 full-tree sweep + the 2nd dormant test + the live-paid-call safety warning; D4 seam named; RED-first T1 = sweep-with-pin-first.** Next poll: SOP-024 at S6 dev-complete.

### SOP-024 + 3-lane T11 for S6 (2026-07-07, session 18) — RELAYED (condensed)

**SOP-024 CONCUR-WITH-FINDINGS** (fresh monitor; no live Scite call). 4 load-bearing legs CONFIRMED: D1 flip truth-table (`_research_dispatch_live` = `not in {0,false,no,off}`, `production_runner.py:127-132`); D2 Scite-canonical selector (`research_wiring.py:149-161` filters to `scite`, excludes consensus+gamma_docs, `cross_validate` False, deterministic; scite-empty→`RetrievalProviderUnavailableError` caught fail-soft); D3 idempotency (`:398-404` early-return, dispatch count stable); D4 degrade precondition at `run_research_wiring` entry (`:421-440`, gated `dispatch_live ∧ …∧ not _scite_creds_present()`, present+empty+marker+relogin, no live call, doesn't block the real path). Tier-1 + parity EMPTY. **F-2402 audit-test claim VERIFIED TRUE** (`test_live_dispatch_python_scope_is_bounded` diffs working-tree vs HEAD → clears on commit; semantic detector GREEN — no new live-dispatch call site). No flip-caused reds; live-leak bounded (only the S6 fake adapter emits gaps; every gap-bearing runner walk pins OFF/fakes-adapter).

**3-lane T11:** Acceptance Auditor AC-1..5 MET (truth-table real, AC-2 teeth genuine, AC-4 all 5 properties, migrations byte-honest, safety pins correct); Blind+Edge; SOP-024. **Convergent findings:**
- **R1 [MUST-FIX, Blind/Edge M1]:** the D4 degrade path RECORDS a 04.55 contribution → the D3 idempotency guard (`:398-404`) then short-circuits any RESUME → the relogin-offer's "re-auth + resume to enrich" (`:317-322`) CANNOT re-dispatch (operator re-auths, resumes, gets the same empty result). Fix: a `degraded==True` contribution is NOT-complete → re-dispatch on resume.
- **R2 [MUST-FIX, all 3 lanes / F-2401 / Auditor-S2 / Edge-S2]:** D5 `narrate_research_result` (`marcus_spoc.py:234`) defined + unit-tested but NEVER invoked in the SPOC flow — dead helper; operator never sees the post-04.55 result (AC-6 vacuously met). Fix: wire it into the resume flow (inspect the 04.55 contribution) + a transcript/integration assertion; reconcile the stale G1 "no gap-fill research was needed" line (`:1236-1237`) now contradicting default-ON.
- **R3 [SHOULD-FIX, Blind/Edge S1]:** `_scite_creds_present()` (`:284-297`) returns True on Basic-only creds, but the real Scite MCP requires OAuth Bearer (rejects Basic) → bearer-expired + `.env` Basic → passes → doomed Basic call → 401 → silent-empty (bypasses D4 marker) OR non-DispatchError httpx crash of the continuation walk (walk sites catch only CitationFidelityError). Fix: gate the canonical live path on Bearer only.
- **R4 [SHOULD-FIX, Auditor]:** AC-3 idempotency test env-coupled (relies on ambient creds) — force creds present.
- **R5 [NIT]:** stale "default OFF" comments (`:2595`,`:3324`); + F-2402 add `PERMITTED_PYTHON_DIFFS` allowlist entry for the S6 files (match the live-dispatch-change convention).

**Orchestrator triage: 2 MUST-FIX (R1 degrade-resume, R2 dead-narration) + 2 SHOULD-FIX (R3 Basic-creds, R4 test) + R5 NIT → RED-first remediation before AC-L.** Verified-clean (no action): D1/D2/D3/D4 cores, load_bearer_token never raises, scite-deregister handled. Next: remediation → orchestrator re-verify → AC-L two-lane live witness → SOP-025 close.

### S6 AC-L LIVE witness = HONEST RED (2026-07-07, session 18) — a real production defect surfaced (S3/S4 precedent)

**Lane-a JUDGE-a FAIL (1/7); lane-b blocked by the same root cause. NO retry-to-green; NO fake-gap injection; NO G1A workaround. S6 does NOT close on this evidence.**
**The defect (code-VERIFIED by the orchestrator):** the §04.55 research dispatch is UNREACHABLE on any real production walk. `has_research_goals()` (`research_wiring.py:277-279`) + `IreneTracyBridge.process_plan_locked` (`irene_bridge.py:27`) both gate on `unit.get("identified_gaps")` (the Gagne `IdentifiedGap` model on `plan_units[]`). But the real Irene-Pass-1 producer emits research intent as **`collateral.research_goals[]`** (`irene_pass1/_act.py:290-314`, a top-level additive object) and NEVER populates `plan_units[].identified_gaps` — only the smoke-test harness (`trial_smoke_harness.py:117`) / a manual G1A operator edit does. So `has_research_goals()`→False→no Scite dispatch. **Research enrichment is structurally non-functional on the canonical auto-approve run.** The live witness proved it: real Irene-Pass-1 (gpt-5.4 ×3, $0.286) produced 5 real corpus-grounded research_goals on tejal-apc-c1-m1-p2-trends, yet zero dispatched (all 11 in-scope units `identified_gaps=[]`). Corpus-independent (structural). Positives proven live: D1 flip active (`MARCUS_RESEARCH_DISPATCH_LIVE` absent→dispatch_live True), Scite Bearer creds present, providers `['consensus','gamma_docs','scite']`, D5 `narrate_research_result` invoked (rendered the empty-state correctly). **Test-integrity insight (Murat-relevant):** the offline suite is GREEN because every research test INJECTS `identified_gaps` via the smoke harness — the tests never exercised the real `collateral.research_goals`-populated path. Evidence: `s6-acl-liveproof-20260707T093933Z/` (PROOF.md + defect-evidence.json w/ the 5 goals verbatim + frozen judges). Judges frozen 09:40:33Z; ran once. Spend $0.303 (LLM; $0 Scite — no dispatch, the point).
**Disposition:** convened a focused re-scope party (Winston/John/Murat) on: (Q1) fix approach — consumer-side dual-read of `collateral.research_goals` (A) vs producer-side gap-synthesis (B); (Q2) in-S6-scope-fix-then-recover vs separate-story-block. Fix is dispatch-REACHABILITY plumbing (J1 research-quality fence respected). Party verdict + disposition to follow.

### S6 research-bridge defect RE-SCOPE party (2026-07-07, session 18) — 3/3 consensus, no impasse

**Winston/John/Murat — unanimous.** **Fix A (consumer-side dual-read), IN S6's scope; recover the witness.**
- **Winston (arch): Fix A.** `collateral.research_goals[]` is the SOURCE OF TRUTH for research intent (real Irene emits it; the producer spec says "the research wiring translates intent to fetch"). Fix A = `has_research_goals()` + `IreneTracyBridge` ALSO read `collateral.research_goals[]`, mapping each `{goal_id, pedagogical_intent, binds_to_objective_id}` → a `RetrievalIntent` (research_goal is a CLEANER fit than IdentifiedGap — purpose-built). Additive; touches neither producer nor Gagne model; respects Tracy-intent/Texas-fetch locality. **Fix B REJECTED** (synthesizes IdentifiedGap → commingles real+synthetic gaps [provenance loss/sync hazard] AND is FORCED to invent gap_type/enrichment_type = a J1-fenced QUALITY decision). **RISK FLAG (binding on the fix): MECHANICAL field-carry ONLY** — carry pedagogical_intent (seed, never a query) + binds_to_objective_id (target) + goal_id (provenance), STOP; the instant it decides research KIND or relevance it crosses into J1 quality. Let downstream posture-selection + Texas decide quality unchanged.
- **John (PM, decision-owner): RATIFY-A.** The M-wit is binding + deliberately chosen as S6's DoD; a canonical flip wired to a gate the real producer never satisfies is hollow paper-green. Reachability is CONSTITUTIVE of "make research canonical," not a follow-on; dispatch-reachability plumbing is squarely in J1 (research QUALITY stays out) — scope doesn't expand, the same commit finally does what it claimed. Party-decidable, not operator-escalation (scope interpretation within a ratified story; strengthens the bar). **Recover-the-witness = NOT retry-to-green** (frozen judges never executed against a fixed dispatch = honest STRUCTURAL error-pause). Guardrails: judges+thresholds stay frozen; fresh auto-approve walk, first-run-stands; **if recovered RED on QUALITY (goals dispatch but no resolvable DOI) → real quality finding, OUT of S6 per J1 → postmortem + separate decision, not an S6 blocker.**
- **Murat (test): the offline green was a FALSE witness** (every research test injected identified_gaps via the smoke harness → never exercised the real `collateral.research_goals` path). The fix MUST carry **`test_real_irene_pass1_shape_reaches_research_bridge`** (build an envelope with `collateral.research_goals=[≥1]` + `plan_units[].identified_gaps==[]` ASSERTED EMPTY → `has_research_goals` True + §04.55 dispatch fires + dispatched provenance traces to `collateral.research_goals` NOT identified_gaps) + negative twin **`test_empty_research_goals_does_not_dispatch`**; **BAN the smoke-harness identified_gaps injection from that test module.** Re-witness = error-pause→recover, fresh frozen judges, first-run-stands. **Re-witness PRECONDITION: Irene must emit ≥1 `collateral.research_goals` on the fresh live run** (non-deterministic LLM; a zero-goal run is an INVALID witness → re-run, not a fail).

**Disposition: S6 gains D7 (the Fix-A bridge, mechanical field-carry) + AC-7 (Murat's anti-regression tests) + the amended AC-L recover-witness close. Dev dispatched. Filed:** `research-quality-resolvable-doi-yield` follow-on (if the recovered witness dispatches but yields no resolvable DOI — J1 quality, out of S6).

### S6 AC-L RECOVER witness (post-D7) = BOTH LANES GREEN (2026-07-07, session 18)

**Lane-a JUDGE-a PASS 8/8; Lane-b JUDGE-b PASS 4/4 + R1 re-dispatch bonus. Fresh frozen judges (10:20:23Z pre-lane, re-verified match), each run ONCE, NO retry-to-green. S6 CLOSES.**
D7 works LIVE: §04.55 fired a REAL Scite dispatch **via the D7 `collateral.research_goals` path** — proven 3 ways: the locked plan carried 0 in-scope `identified_gaps` + 4 Irene-emergent `collateral.research_goals` (rg-01..04) → the identified_gaps path yields nothing, so the dispatch could ONLY be D7; every RetrievalIntent carries its `research_goal_id` on a scite-only provider hint; 5 cited DOIs minted, G2 fidelity passed (unsourced=0), narration surfaced "5 cited sources", walk reached G2B. **Resolvable DOI content-inspected: `10.1038/ijo.2010.252` → doi.org HTTP 200 → nature.com "Relative contribution of energy intake and energy expenditure to childhood obesity…" (Int. J. Obesity); `source_ref==retrieval:scite:10.1038/ijo.2010.252`.** Lane-b: Bearer forced absent → D4 degrade fired at node ENTRY (no dispatch), present-empty + visible "credentials unavailable" marker + relogin offer + degrade narration, $0, walk proceeded; R1 BONUS: restore creds → resume → 04.55 RE-DISPATCHED (degrade contribution falls through the guard). Spend ~$0.648 LLM (this witness) + ~$0.303 (RED witness) ≈ $0.95; MARCUS_G0_DISPATCH_LIVE kept unset.
**Honest process note (session-13 lesson recurred):** the orchestrator's "agent died → resume it" was WRONG — the original background lane-a walk was a mid-G1-resume SNAPSHOT, still alive; it completed at 10:28 (4 cited rows) while the resume completed at 10:31 (5 rows). BOTH walks independently fired a real Scite dispatch via D7 with the SAME primary DOI + both reached G2B → the collision REINFORCES D7-reachability (proved twice), verdict unaffected; judged the intact resume-walk once. Cost: one extra live dispatch (cost not a constraint). Lesson: check a background agent's run state before assuming death + resuming (don't race a live walk).
**S6 DONE. Arc: S0·S1·S2·S3·S4·S5·S6 ALL CLOSED live-proven.** Next poll: SOP-025 at the S6 close commit → then fully-spawned party concurrence (the arc's final-substrate close + the goal DONE-SIGNAL).

### SOP-025 — S6 STORY-CLOSE audit (2026-07-07, session 18, fresh monitor agent) — RELAYED (condensed)

**Commit `a55fd73d`. CONCUR — S6 DONE STANDS; arc substrate spine S0·S1·S2·S3·S4·S5·S6 COMPLETE + live-proven. Corroborates the goal's final party concurrence.**
All 6 checks PASS. #1 commit integrity: exactly the S6 set (code + audit allowlist + test file + spec + ledger + BOTH evidence packs); `git show a55fd73d -- pipeline-manifest.yaml parity.py` EMPTY (Tier-1 + parity frozen); strays untracked. #2 fix real in committed code: `_research_dispatch_live` default-ON kill-switch; selector `LITERATURE_RESEARCH_PROVIDER="scite"`; `_scite_creds_present` Bearer-only; D4 degrade at entry (:506-509); R1 `not _is_degraded_contribution` re-dispatch (:481); **D7 dual-read (:488-495) — `in_scope_with_gaps = identified_gaps OR research_goals`, bridge shapes collateral.research_goals mechanically (goal_id→provenance, pedagogical_intent→seed, binds_to_objective_id→target, NO quality decision)**; `narrate_research_result` wired (def :236 + call :1340). #3 recover-witness single-pass: judges frozen 10:20:23Z pre-lane, **recomputed sha256 MATCH the committed blobs** (judge_a 30bbe88e, judge_b e902381c), each ran once, no retry-to-green; JUDGE-a 8/8 (D7-path dispatch, 0 identified_gaps + 4 research_goals, DOI 10.1038/ijo.2010.252 → doi.org 200 → nature.com content-inspected, source_ref retrieval:scite:{DOI}, G2 unsourced=0); JUDGE-b 4/4 + R1 bonus; concurrency-collision honest + verdict-unaffected (both walks same primary DOI via D7); honest-RED first witness confirmed. #4 AC-7 anti-regression committed (real-Irene-shape + negative twin + union + smoke-harness-ban). #5 post-commit green 64 passed/1 skip. #6 arc DONE. Findings F-2501/F-2502 INFO only. **VERDICT: CONCUR.**

### 🎯 DONE-SIGNAL — fully-spawned party CONCURRENCE (2026-07-07, session 18) — 4/4 UNANIMOUS, corroborated by SOP-025

**The final task in scope (S6) is ACCOMPLISHED + VALIDATED — live-proven, committed (`a55fd73d`), pushed (origin 0/0). Fully-spawned canonical-core party CONCURS unanimously; SOP-025 close poll corroborates. GOAL COMPLETE.**
- **Winston (Architect): CONCUR** — D7 consumer-side dual-read architecturally correct (additive consumer seam; J1 fence holds STRUCTURALLY; source-of-truth on collateral.research_goals; Tracy-intent/Texas-fetch locality preserved); Tier-1 held; S0-S6 spine coheres, no debt. Non-blocking follow-on named: unify identified_gaps + collateral.research_goals at the producer (out of S6; beside research-quality-resolvable-doi-yield).
- **John (PM, decision-owner): CONCUR** — M-wit met FUNCTIONALLY not on paper (real dispatch → resolvable DOI 10.1038/ijo.2010.252, provenance proven 3 ways = D7 path only); honest-RED→D7→recover the right + only product outcome (genuine SPOC fix, not proofing accommodation); J1 fence respected end-to-end; arc shippable. DONE-SIGNAL granted; arc clear to S7 (⛔ operator workbook checkpoint).
- **Murat (Test Architect): CONCUR** — recover witness a legitimate error-pause→recover (judge sha256 byte-match to frozen manifest, first-run-stands, no retry-to-green); AC-7 closes the false-witness gap (executable smoke-harness-injection ban → defect class can't recur); concurrency-collision honest + verdict-strengthening; arc-wide live-witness discipline held. "Fire the DONE-SIGNAL."
- **Amelia (Developer): CONCUR** — flip/selector/D4/D7 correct; both review-found defects (R1 degrade-recovery, R3 Basic-creds) genuinely fixed at the seam; safe (own pinned run: no live-Scite leak; Tier-1; ruff clean); no blocking debt (follow-ons filed; research-quality-resolvable-doi-yield moot — DOI resolved). "DONE-SIGNAL concurrence granted."
- **SOP-025 (shadow-monitor close poll): CONCUR** — commit integrity clean, fix real in committed code, recover-witness single-pass sha-verified, AC-7 committed, post-commit green 64/1-skip, arc complete.

**ARC COMPLETE: Canonical Production Conversation — S0·S1·S2·S3·S4·S5·S6 ALL CLOSED + LIVE-PROVEN.** Every built-but-dormant ceremony (styleguide pick, CD resolution, Gary parity + FAIL-LOUD, G0 enrichment, Tracy/research Scite-canonical) is now a STANDING property of a canonical Marcus-SPOC run. NEXT: S7 (workbook — ⛔ operator review/edit/approval checkpoint BEFORE dev dispatch) + S8 (composed proof). OWED: KG/ONBOARDING regen (~3 sessions).
---

## SOP-026 - S7 Phase-1 workbook-generalization spec pre-dispatch review (2026-07-07 12:19 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** `_bmad-output/implementation-artifacts/canonical-arc-s7-workbook-generalization.md` plus the current workbook producer, collateral schema, research wiring, bundle catalog, and composition seams. Branch `dev/workbook-2026-07-06` is synced to origin; the S7 spec is currently untracked, with unrelated strays still excluded. Review was read-only except for this monitor ledger update.

**Verdict: CONCUR-WITH-FINDINGS; do not dispatch dev until the P1 amendments below are applied.** The Phase-1 fence is directionally right: S7 is producer generalization, not the Phase-2 lesson-plan-as-rationale platform; it correctly keeps learner-ready prose, semantic audit, word-form numeric coverage, collateral-to-selection, course/SME registry, course purpose, and projector family out of scope. The material gaps are contract precision at the producer/citation/selection seams.

**F-2601 [P1] DOI rendering can pass without G2 actually auditing the DOI entries.** The spec requires research_entries to render and "G2 passes" (`canonical-arc-s7-workbook-generalization.md:47`), but current `WorkbookProducer.produce()` runs G2 only over `citations` + `source_ref_manifest` (`app/marcus/lesson_plan/workbook_producer.py:891-895`). The live DOI block renders separately from `research_entries` (`workbook_producer.py:690-702`). A dev could satisfy visible DOI rendering while the DOI source_refs are outside citation fidelity. **Required amendment:** AC-4 must say every rendered research_entry `source_ref` is included in the citation audit manifest, and G2 fails if a rendered research DOI lacks its source_ref/hash. Add a RED test that deletes/corrupts one research source_ref from the manifest and proves G2 fails.

**F-2602 [P1] `declaration=="none"` is underspecified when the workbook graph is already selected.** D3 says `declaration=="none"` ships deck-only (`canonical-arc-s7-workbook-generalization.md:32`), while S7 explicitly leaves `collateral -> ComponentSelection` derivation to Phase 2 (`:21`). Today the operator-picked `narrated-deck-with-workbook` bundle includes workbook (`app/marcus/lesson_plan/bundle_catalog.py:228-232`), and 07W is pruned only by component selection (`app/marcus/lesson_plan/composition.py:73-77, 128-135`). **Required amendment:** specify the exact 07W behavior for `declaration=="none"` under a selected workbook bundle: pre-dispatch prune, explicit skipped contribution/sidecar, or no-op return. Add a negative twin proving no stale workbook artifact and no invalid specialist return contract.

**F-2603 [P2] CollateralSpec vs G0 enrichment precedence remains ambiguous.** The spec properly flags the SSOT fork (`canonical-arc-s7-workbook-generalization.md:18`), but D2/AC-2 still say "collateral + enrichment" without a conflict rule (`:29`, `:45`). Current enriched projection consumes the G0 card (`app/marcus/lesson_plan/workbook_enrichment.py:296-307`); current 07W does not consume `lesson_plan["collateral"]`. **Required amendment:** pin deterministic precedence before dispatch. Recommended: `CollateralSpec` owns intended artifact structure and LO/section bindings; G0 enrichment supplies deterministic resolved content slots, exercises, readings, and citations; mismatches/orphans either fail loud at zero-blueprint/structural mismatch or degrade with recorded provenance for per-section missing data. Add synthetic conflict witnesses: collateral section absent from enrichment, enrichment extra LO/section, and title/depth mismatch.

**F-2604 [P2] "Each DOI bound to the claim/segment it supports" overreaches the current S6 payload.** D4 requires each DOI to be bound to the claim/segment it supports (`canonical-arc-s7-workbook-generalization.md:35`). Current S6 `CitedResearchEntry` carries citation_id/source_ref/provider/source_id/title/source_hash only (`app/marcus/orchestrator/research_citation.py:51-62`); workbook `ResearchEntry.supports_segment_id` is optional (`app/marcus/lesson_plan/workbook_producer.py:240-246`). **Required amendment:** either relax S7 Phase 1 to "render DOI with source_ref/provider/citation_id and optional support binding if present," or name a deterministic binding source from the envelope. Do not let 07W infer semantic claim support; that crosses into the deferred semantic-audit/quality arc.

**Open questions for the S7 party before dev dispatch:**
- Which exact non-tejal live corpus is the AC-L witness? The spec says "operator-named" (`canonical-arc-s7-workbook-generalization.md:51`); naming it before dispatch avoids a late invalid witness.
- Should S7 update only the 07W adapter to read `research_entries_from_envelope()` (`app/marcus/orchestrator/research_wiring.py:632-642`), or also update the producer G2 contract? Monitor recommendation: both. Visible DOI rendering without G2 coverage is too weak for S7 close.

**Recommendations:** amend the spec in-place before green-light; keep Tier-1/no-manifest-edit as written; keep Irene producer edits out of scope unless the party explicitly re-scopes; require the first dev task to be a RED-first test set for F-2601/F-2602/F-2603 before implementation. Once amended, proceed to fresh dev RED-first under the existing T11 rhythm.

---

## SOP-027 - S7 amended-spec re-poll (2026-07-07 12:42 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** amended `_bmad-output/implementation-artifacts/canonical-arc-s7-workbook-generalization.md`, branch/status/log, canonical ledger tail, and the code lines behind the newly named tejal-metadata leak. No production/test/story artifact was edited by this monitor; this entry is the only write.

**Verdict: CONCUR. S7 Phase-1 spec is now cleared for fresh-dev RED-first, with one operator input still needed before the AC-L live leg.** No new commits are present; HEAD remains `1c3df92d` / origin synced. The S7 spec remains untracked, but it is materially amended and marked ready for RED-first. No dev or evidence artifacts are visible yet.

**F-2601 CLOSED AT SPEC LEVEL.** D4/AC-4 now explicitly requires every rendered `research_entry.source_ref` to enter the G2 citation audit manifest and requires a RED corruption/deletion test that forces G2 red. This closes the prior "visible DOI but unaudited DOI" hole.

**F-2602 CLOSED AT SPEC LEVEL.** D3/AC-3 now specifies `declaration=="none"` under a selected workbook bundle as an explicit skipped/no-op contribution with valid empty specialist return contract, no stale artifact, and no fabricated scaffold. This is the right S7-local behavior while the `collateral -> ComponentSelection` prune remains Phase-2.

**F-2603 CLOSED AT SPEC LEVEL.** D2/AC-2 now pins precedence: `CollateralSpec` owns intended artifact structure and LO/section bindings; G0 enrichment is a deterministic resolution overlay for exercises/readings/citations. The spec also requires conflict witnesses for collateral-vs-enrichment mismatch.

**F-2604 CLOSED AT SPEC LEVEL.** D4/AC-4 now says DOI rows render `source_ref`/`provider`/`citation_id`, and `supports_segment_id` only if already present. The producer must not infer semantic claim/segment support; that remains in the deferred semantic-audit arc.

**New positive catch folded by the S7 party:** the spec now names the reachable live-path tejal leak in `_plan_unit_and_context`: `_DEFAULT_UNIT_ID="tejal-apc-c1-m1-p2-trends"` plus hardcoded `event_type="present-trends"` / macro-trends diagnosis render into the workbook H1/overview (`_act.py:74, 487-505`; `workbook_producer.py:498, 507`). I independently verified those code lines. AC-1/AC-L now include header/title leak checks; this is material and correctly in-scope for S7.

**Remaining open input:** the AC-L corpus is still operator-named. The amended spec correctly makes that a live-leg input, not a dev RED-first blocker. Before AC-L, name a non-tejal, literature-rich corpus likely to produce Irene collateral plus at least one research_goal.

**Recommendation:** proceed to fresh dev RED-first. First monitor dev-poll should verify the promised RED set exists before implementation credit: tejal header leak, CollateralSpec provenance/precedence, `declaration=="none"` no-op return, research_entries under G2 with corrupted-source red, and full-tree token/baseline sweep.

---

## SOP-028 - S7 fresh-dev diff poll (2026-07-07 13:22 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** current uncommitted S7 production/test diff, branch/status/log, recent artifacts, and course-content status. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** HEAD remains `1c3df92d` / origin synced; no commits yet. Fresh S7 dev work is now visible in `app/specialists/workbook_producer/_act.py`, `workbook_enrichment.py`, `workbook_producer.py`, `collateral_spec.py` + schema/changelog and producer tests. The diff also shows generated/stray artifacts and a course-content rename/untracked directory that need disposition before commit.

**Positive verification:** The implementation is directionally aligned with SOP-027. It removes the tejal constant assembly from the reachable producer, generalizes plan-unit metadata, adds `WorkbookSpec.kind`, reads run.json through model-layer helpers in `workbook_enrichment.py`, treats enrichment as a resolution overlay, folds research DOI source_refs into G2, renders `citation_id`, records an explicit empty research reason, adds no-op skip behavior for `declaration=="none"`, and adds a new S7 RED-floor test module covering AC-1/2/3/4.

**F-2801 [P1] Unknown/malformed collateral declarations silently skip instead of failing loud.** In `_act.py`, after reading a collateral dict, the code returns `None` for any `declaration != "present"` that is not exactly `"none"` (`return None  # unknown declaration => conservative skip`). That means a malformed persisted `collateral` object such as `{"declaration":"workbook"}` records a valid skip rather than surfacing a producer/contract error. The spec only grants skip to absent collateral or explicit `declaration=="none"`; a present-but-invalid collateral dict should be fail-loud, especially because `CollateralSpec` has `extra="forbid"` and a closed declaration enum. **Recommendation:** change the branch to validate the dict unless it is exactly absent or `"none"`; if validation fails, raise `WorkbookProducerActError` with the blueprint/unresolvable tag. Add a RED test for unknown declaration and malformed collateral shape.

**F-2802 [P2] Course-content rename/untracked corpus material needs explicit disposition before commit.** `git status` shows `R course-content/courses/tejal-c1m1-p3-opportunity/... -> course-content/courses/tejal-c1m1-p3-opportunity-raw/...` plus an untracked `course-content/courses/tejal-c1m1-p3-opportunity/` directory. This is outside the narrow producer/test/schema diff and is also tejal-named, so it is not the pending non-tejal AC-L witness corpus. **Recommendation:** before staging, either document why this content move is in S7 scope or exclude/revert it from the commit. Do not let accidental course-content reshaping ride with the producer-generalization story.

**Evidence gap to verify at next poll:** I see S7 RED-floor tests in the tree, but no committed or ledgered test-output evidence yet. The next monitor dev-poll should verify the RED-first record and focused green output for: tejal header leak, CollateralSpec authority/precedence, `declaration=="none"` no-op, malformed declaration fail-loud after F-2801 remediation, research_entries under G2 with corrupted-source red, and the token/baseline sweep.

**Verdict: CONCUR-WITH-FINDINGS.** The core implementation shape is promising and addresses F-2601..F-2604 in code, but F-2801 should be remediated before story-close, and F-2802 must be explicitly dispositioned before commit hygiene can pass.

---

## SOP-029 - S7 remediation re-poll (2026-07-07 14:12 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** current uncommitted S7 diff, `_act.py` declaration handling, new `test_workbook_s7_remediation.py`, course-content status, branch/log. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** HEAD remains `1c3df92d`; no S7 commit yet. The dev lane has added a remediation test module and updated `_act.py` beyond SOP-028, including 3-lane review remediation items.

**F-2801 CLOSED IN CODE/TEST SHAPE.** `_act.py` no longer silently skips unknown declarations. The legal skip remains absent collateral or explicit `declaration=="none"`; any other malformed/unknown collateral dict now goes through `CollateralSpec.model_validate()` and raises `WorkbookProducerActError` tagged `workbook-producer.blueprint.unresolvable` on validation failure. `test_workbook_s7_remediation.py` includes the F-2801 remediation floor. Next close poll still needs test-output evidence, but the code shape addresses the finding.

**F-2802 REMAINS OPEN.** `git status` still shows a tracked rename from `course-content/courses/tejal-c1m1-p3-opportunity/...` to `course-content/courses/tejal-c1m1-p3-opportunity-raw/...` plus an untracked replacement `course-content/courses/tejal-c1m1-p3-opportunity/` directory. This remains outside the narrow producer/test/schema surface and still needs explicit disposition before staging/commit.

**Additional dev-lane signal:** the new remediation test file names several 3-lane fixes beyond Codex SOP-028: shared-LO duplicate exercise IDs, recoverable wrapping for `produce()` gate failures, malformed DOI omission with provenance, explicit degrade-provenance rendering, and carrying `WorkbookSpec.kind` through rebuild. These are plausible hardening items; the next monitor poll should verify they are either all in scope via the 3-lane review record or explicitly recorded in the story close notes.

**Verdict: CONCUR-WITH-FINDINGS.** F-2801 is resolved at code/test-shape level; F-2802 remains the active commit-hygiene blocker. Still waiting on focused test evidence, RED-first record, AC-L corpus naming, live witness, commit, and close poll.

---

## SOP-030 - S7 AC-L live-witness start poll (2026-07-07 14:52 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, evidence directory `_bmad-output/implementation-artifacts/evidence/s7-acl-liveproof-20260707T185105Z/`, live Python processes, and the AC-L driver. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** HEAD remains `1c3df92d`; no S7 commit yet. A new AC-L evidence directory exists with `.ts`, `s7_acl_driver.py`, `driver-log.txt`, and `walk-log.txt`. At this poll the logs are still empty and no `s7-acl-facts.json`, copied workbook, or `PROOF.md` exists yet. A Python process started at 14:52 local appears to be running the live-witness lane. **Do not score AC-L yet.**

**Driver intent observed:** the driver starts a real production trial on `course-content/courses/tejal-c1m1-p3-opportunity` with `narrated-deck-with-workbook`, default-ON enrichment/research, standard-A styleguide pick, HIL auto-approval loop, and evidence capture for workbook MD/DOCX, collateral, research entries, DOI resolution, and no-tejal-leak checks. It explicitly keeps `MARCUS_G0_DISPATCH_LIVE` unset (deterministic G0 pre-pass), leaves `MARCUS_G0_ENRICHMENT_ACTIVE` and `MARCUS_RESEARCH_DISPATCH_LIVE` unset (default-ON), and uses a 3000s watchdog.

**Open finding carried:** F-2802 remains open at this snapshot: the same course-content rename/untracked replacement directory is still visible in `git status`. If the driver uses that untracked replacement corpus intentionally as the AC-L witness, the final commit still needs explicit disposition for what is staged vs excluded and why.

**Verdict: IN-PROGRESS / NO PASS YET.** Wait for the live driver to finish and produce facts/proof before claiming AC-L. Next poll should inspect `s7-acl-facts.json`, workbook artifacts, driver/walk logs, DOI resolution, no-tejal leak result, G1/G2/G3/AC-5/AC-8 status, and whether F-2802 was resolved.

---

## SOP-031 - S7 AC-L live-witness progress poll (2026-07-07 15:02 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, evidence directory `_bmad-output/implementation-artifacts/evidence/s7-acl-liveproof-20260707T185105Z/`, driver/walk logs, live Python processes, and run state under `state/config/runs/40f3a90a-60fc-4c0d-b4a7-db51b03bb24e/`. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** AC-L is still in progress and not scoreable. Driver log shows the real Part-3 composed run started, reached and approved G0E, G0R, G1, and G2B, then reached G2C and began `resume approve G2C`. The persisted run state currently reports `status=paused-at-gate`, `paused_gate=G2C`, `paused_error_tag=None`; no `s7-acl-facts.json`, copied workbook, or proof file exists yet. Python processes from the 14:52 local launch are still present.

**Positive progress:** The live run has exercised default-ON G0E/G0R and research/Gamma/Kling surfaces far enough to produce real run artifacts under `state/config/runs/40f3a90a-60fc-4c0d-b4a7-db51b03bb24e/`, including `g0-enrichment.json`, `irene-refinement.json`, `ratified-los.json`, `cost-report.*`, `decision-card-G2C.json`, Gary export, and motion output. This is useful progress but not AC-L completion.

**New hygiene note:** `state/config/gamma-styleguide-picks.jsonl` is now modified by the live witness, presumably from the scripted standard-A styleguide pick. This is expected runtime evidence, but it must be dispositioned at commit time like other live-run artifacts; do not stage it accidentally unless the story explicitly treats it as evidence.

**Open finding carried:** F-2802 remains open; the course-content rename/untracked replacement directory is still visible. The live witness uses `course-content/courses/tejal-c1m1-p3-opportunity` as its corpus path, so the final close must explain whether this untracked replacement corpus is intended evidence/input and whether any tracked rename belongs in the S7 commit.

**Verdict: IN-PROGRESS / NO PASS YET.** Continue waiting for the driver to finish. Next poll should score only after facts/proof/workbook artifacts exist and should verify no retry-to-green, DOI resolution, no tejal header leak, 07W contribution, and G1/G2/G3/AC-5/AC-8 results.

---

## SOP-032 - S7 AC-L live-witness honest RED (2026-07-07 15:22 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, completed evidence directory `_bmad-output/implementation-artifacts/evidence/s7-acl-liveproof-20260707T185105Z/`, `driver-log.txt`, `s7-acl-facts.json`, `cost-report.json`, and current uncommitted status. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** AC-L has produced a scoreable first-run result, and it is not a pass. Trial `40f3a90a-60fc-4c0d-b4a7-db51b03bb24e` reached the workbook leg but ended `paused-at-error` with final error tag `workbook-producer.segment-manifest.empty`. The evidence shows no workbook contribution, no workbook markdown path, and no workbook docx path. This is an honest live RED, not a close witness.

**Positive proof retained:** the run still proves important S7 preconditions. The real composed path advanced through G0E, G0R, G1, G2B, G2C, G3, G4, and G4A before 07W failure. Irene emitted `collateral.declaration=present`, `kind=deck-companion-workbook`, five collateral sections, two research goals, and three research entries. Primary DOI `10.3991/ijac.v17i2.45555` resolved over HTTP 200 to the journal page. This supports the conclusion that the failure is at the 07W workbook-production integration boundary, not at collateral or research generation.

**Live RED diagnosis:** `workbook-producer.segment-manifest.empty` means the current S7 producer path is still dependent on a segment manifest that is absent or empty for the composed Part-3 live run. Because no workbook artifact was produced, AC-L cannot yet score the no-tejal workbook leak check, DOI workbook rendering, G2 workbook citation coverage, or DOCX/MD output requirements. Do not claim AC-L pass on collateral/research success alone.

**Open finding carried:** F-2802 remains open. The course-content rename/untracked replacement directory is still visible, and the live witness used `course-content/courses/tejal-c1m1-p3-opportunity`. `state/config/gamma-styleguide-picks.jsonl` also remains a live-runtime modification requiring explicit disposition. These are commit-hygiene blockers until staged/excluded intentionally.

**Recommendations:** treat this as first-run-stands RED evidence. Remediate the 07W segment source contract: either make the producer consume the production envelope/transcript source available in the composed run, or make the expected segment manifest path/creation explicit before 07W dispatch. Then rerun AC-L as a recover witness, preserving the original error-pause evidence. Keep S7 open until a live run produces the workbook artifacts and passes the S7 assertions.

**Verdict: AC-L HONEST RED / S7 NOT CLOSE-READY.** The team has useful live evidence and a narrowed integration defect, but S7 Phase 1 cannot close until the workbook leg recovers and passes.

---

## SOP-033 - S7 roadblock advisory: segment manifest contract mismatch (2026-07-07 15:36 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** the AC-L error-pause facts, current `_act.py` segment loader, and live run artifact `state/config/runs/40f3a90a-60fc-4c0d-b4a7-db51b03bb24e/exports/segment-manifest-storyboard-b.yaml`. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**Roadblock refinement:** the live run's storyboard-B segment manifest is not missing and is not byte-empty. It exists at the expected `_act.py` default path (`exports/segment-manifest-storyboard-b.yaml`), is 7706 bytes, and contains 9 `segments` rows with `slide_id` values `slide-01` through `slide-09` and non-empty `narration_text`. The reason `_load_segments()` yields `workbook-producer.segment-manifest.empty` is that every row has blank `segment_id` and blank `id`; the loader computes `seg_id = segment_id or id`, then silently skips the row when `seg_id` is blank. In this production artifact shape, `slide_id` is the only stable segment key.

**Recommendation to Claude agents:** treat this as a contract mismatch at the 07W adapter, not as a reason to synthesize proof-only data. The shortest product-aligned recovery is RED-first:

1. Add a failing fixture/test for the actual production manifest shape: top-level `segments`, blank `segment_id`/`id`, present `slide_id`, present `narration_text`. Expected behavior: 07W loads the rows using `slide_id` as the deterministic segment id/source anchor, not `empty`.
2. Patch `_load_segments()` to prefer `segment_id`, then `id`, then `slide_id` when `slide_id` is present and non-empty. If all three are absent, keep fail-loud/malformed behavior. Also keep fail-loud if narration text is absent; do not fabricate transcript prose.
3. Keep the upstream question open but non-blocking for S7: the manifest producer probably should populate `segment_id`, but S7 can legitimately accept the production manifest's `slide_id` as the workbook transcript anchor because the figure mapping and source refs already key off `slide_id`.
4. Do not repair this by changing the AC-L driver, copying VTTs into a synthetic manifest, or bypassing G1/AC-5. The recovery witness must prove the real production run artifact can feed 07W.

**Second-order caution:** the same manifest currently has 9 rows but only 1 unique narration string. That may be a separate upstream Enrique/compositor/G5 issue, or it may be acceptable for this composed proof depending on the segment contract. Do not bundle a speculative fix into the segment-id remediation. First make 07W consume the real manifest shape; then let the existing workbook gates score transcript coverage/fidelity honestly. If repeated narration later fails a gate, route it to the producer of the narration/manifest artifact rather than masking it in 07W.

**Open finding carried:** F-2802 remains open. The course-content rename/untracked replacement directory and the modified `state/config/gamma-styleguide-picks.jsonl` still need explicit commit disposition.

**Verdict: ROADBLOCK ACTIONABLE.** The failure has a narrow RED-first recovery path: accept `slide_id` as the production segment identity fallback, preserve fail-loud for truly malformed rows, rerun AC-L as a recover witness, and keep the original honest RED evidence.

---

## SOP-034 - S7 roadblock re-poll: upstream Irene id-integrity story opened (2026-07-07 15:52 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, new untracked story `_bmad-output/implementation-artifacts/irene-pass2-slidejoin-id-integrity-gate.md`, S7 spec tail, retry-tag wiring in `app/marcus/orchestrator/production_runner.py`, and existing Irene/narration-join references. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** no new commit and no recover evidence yet. HEAD remains `1c3df92d`; the S7 AC-L evidence pack remains the latest live proof and is still honest RED. The new Irene id-integrity story is the only material new signal.

**Concurrence on direction:** the new story is the stronger product fix and should supersede the 07W-local fallback as the primary remediation. SOP-033 correctly found that 07W dropped manifest rows because `segment_id`/`id` were blank while `slide_id` was present. The new story traces the real upstream cause: Irene Pass-2 emitted id-less narration/deltas; `join_narration_segments()` collapsed everything under the empty key; the publisher wrote a manifest with 9 `slide_id`s but blank ids and repeated narration; 07W merely exposed the corruption late. Fixing this at the Pass-2 boundary protects Enrique audio, G5 QA, storyboard publish, and 07W. A 07W-only `slide_id` fallback would risk accepting a corrupted lesson-wide narration artifact.

**Verified claims:** `irene.pass2.slide-join-failed` is already in `_RETRYABLE_DISPATCH_TAGS`, with `_MAX_DISPATCH_RETRIES = 3`, so reusing that tag for the new id-integrity gate is mechanically plausible. The existing tests already assert that tag for the current roster-grounding path; the new story's requirement for distinct detail substrings is important so tests do not pass vacuously on the old gate.

**F-3401 [P1] Close language still says "non-tejal" while the resolved AC-L corpus is Tejal Part 3.** The S7 spec still says "real non-tejal workbook" / "first non-tejal workbook" in multiple places, and the new Irene story repeats that wording. But the resolved AC-L corpus is `course-content/courses/tejal-c1m1-p3-opportunity/...`: Tejal Module-1 Part 3, same SME/course, different lesson from the baked-in Part 2 constants. This is not a blocker to proving producer generalization off the frozen Part-2 hardcoding, but it is a blocker to truthful close wording. **Required correction before close:** replace "first non-tejal workbook" with language such as "first non-baked-in / non-Part-2 Tejal workbook produced in-graph" or choose a genuinely non-Tejal corpus and rerun. Do not let the close record overclaim new-SME/non-Tejal proof.

**Recommendation to Claude agents:** proceed with the Irene id-integrity story RED-first exactly as scoped: pure `_assert_join_id_integrity(parsed)` after backfills; AC-1 id-less fixture where roster grounding stays silent; AC-2 duplicate-id/non-bijective fixture; AC-3 valid repeated text with distinct ids passes; AC-4 proves the pre-fix join collapse; AC-5 retryable tag + `narration_join.py` byte-frozen + pipeline manifest diff empty. After green/review, recover by dropping node-08 Irene and node-08B publish contributions and re-dispatching only `08 -> 08B -> 07W`; do not forward-walk through audio again and do not hand-inject ids.

**Open findings carried:** F-2802 remains open for course-content rename/untracked corpus disposition and `state/config/gamma-styleguide-picks.jsonl` runtime modification. S7 remains not close-ready until the upstream fix is green, the recover witness produces workbook MD/DOCX, the close wording is corrected, and commit hygiene is clean.

**Verdict: GO-WITH-FINDING.** The roadblock is now better framed as an upstream Irene Pass-2 id-integrity defect that S7 live proof surfaced. Fix that first; keep S7 open; correct the Tejal/non-Tejal wording before any close claim.

---

## SOP-035 - S7 wording re-poll + no-code movement (2026-07-07 16:02 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, S7 spec, Irene id-integrity story, evidence directory list, and timestamps for `app/specialists/irene/graph.py` plus the Irene grounding test file. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** no implementation movement yet. `app/specialists/irene/graph.py` and `tests/specialists/irene/test_irene_pass2_grounding_fail_loud.py` are unchanged; no new evidence pack exists; no commit exists. The latest live proof remains S7 AC-L honest RED.

**F-3401 PARTIALLY REMEDIATED.** The Irene id-integrity story now carries the correct close language: it says the recover witness is "first in-graph workbook off a different lesson" and explicitly forbids "first non-tejal workbook." The S7 close-language honesty guard now also states the correct claim: producer generalization off frozen `tejal-apc-c1-m1-p2-trends`, first workbook from a different Tejal Part 3 lesson, not cross-SME/non-Tejal generalization.

**F-3401 STILL OPEN UNTIL STALE SPEC LINES ARE CLEANED.** The S7 spec still contains stale "non-tejal" language in at least the party-scope opening, AC-1 phrasing, and the T11 gate line ("AC-L LIVE (first non-tejal in-graph workbook...)"). These lines conflict with the corrected honesty guard and can still leak into close notes or party summaries. **Recommendation:** before any close poll, normalize all S7 status/scope/gate wording to "different lesson from the baked-in Tejal Part 2" or "non-baked-in lesson," and reserve "non-Tejal" for the Phase-2/cross-SME arc.

**Roadblock status:** the upstream Irene id-integrity story remains the right recovery path. Next material monitor signal should be RED-first tests/code in `app/specialists/irene/graph.py` and `tests/specialists/irene/test_irene_pass2_grounding_fail_loud.py`, then focused green output, review, and recover witness.

**Open findings carried:** F-2802 remains open for course-content rename/untracked corpus disposition and `state/config/gamma-styleguide-picks.jsonl`. S7 remains not close-ready until the upstream fix is implemented, recover witness produces workbook MD/DOCX, F-3401 stale wording is fully cleaned, and commit hygiene is clean.

**Verdict: NO CLOSE / WAITING ON DEV.** The story docs are moving in the right direction, but there is not yet code, test, recover-witness, or commit evidence to score.

---

## SOP-036 - Irene id-integrity RED-first test poll (2026-07-07 16:12 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, latest evidence directories, `tests/specialists/irene/test_irene_pass2_grounding_fail_loud.py` diff, Irene graph timestamp, S7 wording grep, and current story timestamps. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** RED-first test work has started, but implementation has not. `tests/specialists/irene/test_irene_pass2_grounding_fail_loud.py` is modified at 16:12 and now imports `_assert_join_id_integrity`; `app/specialists/irene/graph.py` remains unchanged from 2026-07-02, so the new test file should be red until the pure gate is implemented. No new evidence pack or commit exists.

**Positive verification:** the added tests are aligned with the Irene id-integrity story and the live defect:
- AC-1 id-less-after-backfill fixture with valid roster-matching `perception_source`s; explicitly asserts `_assert_narration_joins_roster(...)` stays silent and the new id gate fires with `id-less after backfill`.
- AC-2 duplicate/non-bijective id fixture; expects `id-join non-bijective` and distinguishes it from the id-less branch.
- AC-3 valid known-good `joined_pass2_response()` and identical narration text with distinct ids both pass; identical text with shared id fires.
- AC-4 demonstrates the pre-fix `join_narration_segments()` collapse: distinct slide ids flood to the last narration text.
- AC-5 asserts `irene.pass2.slide-join-failed` remains in `_RETRYABLE_DISPATCH_TAGS`.

This is the right RED-floor shape: it tests the upstream corruption boundary, keeps `join_narration_segments` observational/byte-frozen, and avoids a 07W-only workaround.

**F-3401 remains open.** The S7 honesty guard and Irene carry story are corrected, but stale "non-tejal" language remains in S7 party-scope, AC-1, DOI-leg note, and the T11 gate line. This is not blocking RED-first implementation, but it is still a close-record risk.

**Open findings carried:** F-2802 remains open for course-content rename/untracked corpus disposition and `state/config/gamma-styleguide-picks.jsonl`. S7 remains not close-ready until the Irene gate implementation lands, focused tests go green, review passes, the recover witness produces workbook MD/DOCX, F-3401 stale wording is fully cleaned, and commit hygiene is clean.

**Verdict: GOOD RED-FIRST START / NOT IMPLEMENTED YET.** Proceed to implement `_assert_join_id_integrity(parsed)` in `app/specialists/irene/graph.py`, call it after the existing backfills and before/alongside roster validation, preserve the retry tag, and keep the shared narration join frozen.

---

## SOP-037 - Irene id-integrity implementation-shape poll (2026-07-07 16:22 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, evidence directories, `app/specialists/irene/graph.py` diff, Irene grounding/procedure/warm-callback test diffs, and S7 wording grep. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** the upstream Irene id-integrity implementation has landed in working tree shape. No commit and no recover evidence exist yet. The latest live proof remains the S7 AC-L honest RED.

**Positive verification:** `graph.py` now defines pure `_assert_join_id_integrity(parsed)` and calls it in `_act_pass_2` after `backfill_delta_ids`, `backfill_delta_ids_from_roster`, and `_assert_narration_joins_roster(...)`. The gate:
- returns silently when there is no `narration_script`;
- raises `Pass2GroundingError(tag="irene.pass2.slide-join-failed")` for any narration segment or delta lacking a usable id, with the distinct `id-less after backfill` detail;
- raises the same retryable tag for duplicate narration ids, with the distinct `id-join non-bijective` detail;
- keys bijectivity on id cardinality, not `narration_text`, preserving the false-fire guard for repeated prose under distinct ids.

**Test-shape verification:** the added RED-floor tests from SOP-036 remain present, and existing Irene procedure/warm-callback fixtures were updated to carry bijective ids where they are intended to represent valid Pass-2 output. This is consistent with the new fail-loud contract rather than weakening the gate.

**Residual verification still required:** no test-output evidence is visible in the repo yet. Before the Irene story can close, the team still owes focused green output for the new gate tests, existing Pass-2/narration-join suites, retry-tag membership, and the Tier-1/protected-path checks (`narration_join.py` byte-frozen and `git diff -- state/config/pipeline-manifest.yaml` empty). Then the S7 recover witness must regenerate a valid storyboard-B manifest and produce workbook MD/DOCX through 07W.

**F-3401 remains open.** Stale "non-tejal" wording still remains in the S7 party-scope opening, AC-1 text, DOI-leg note, and T11 line. The corrected honesty guard is good, but the stale lines should be cleaned before close.

**Open findings carried:** F-2802 remains open for course-content rename/untracked corpus disposition and `state/config/gamma-styleguide-picks.jsonl`. S7 remains not close-ready until focused tests pass, review passes, the recover witness succeeds, stale wording is cleaned, and commit hygiene is clean.

**Verdict: IMPLEMENTED IN SHAPE / WAITING ON EVIDENCE.** The upstream fix now matches the monitor recommendation and the Irene story. Next material signal should be test-output evidence, review findings/remediation, and the `08 -> 08B -> 07W` recover witness.

---

## SOP-038 - S7 AC-L post-fix witness start poll (2026-07-07 17:02 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, new evidence directory `_bmad-output/implementation-artifacts/evidence/s7-acl-recover-liveproof-20260707T205600Z/`, `driver-log.txt`, `walk-log.txt`, the new driver script, live Python processes, and current run state under `state/config/runs/4c64db93-af02-41a2-9ef8-a7559b37e72f/`. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** a new post-fix live witness is in progress and not scoreable. Evidence directory `s7-acl-recover-liveproof-20260707T205600Z` contains `s7_acl_recover_driver.py`, `driver-log.txt`, and `walk-log.txt`; no facts JSON, proof file, workbook MD, or workbook DOCX exists yet. Trial `4c64db93-af02-41a2-9ef8-a7559b37e72f` is currently `paused-at-gate` at `G1` with no error tag, and Python processes from the 16:56 local launch are still running.

**Positive progress:** the new walk has started on `course-content/courses/tejal-c1m1-p3-opportunity` with `narrated-deck-with-workbook`, default-ON enrichment/research, standard-A pick, and has already passed through G0E and G0R to G1. This is useful forward movement after the Irene id-integrity implementation.

**F-3801 [P1] The "recover" witness appears to be a fresh full trial, not the scoped surgical recover.** The driver script name/evidence directory says recover, but the code creates `TRIAL_ID = uuid4()` and calls `start_trial(...)` on a new run, with comments saying "FULL composed Part-3 walk." That is not the Irene story's specified recovery path of dropping node-08/node-08B from the frozen failed trial `40f3a90a...` and re-dispatching only `08 -> 08B -> 07W`. If this new run passes, it may be valid as a fresh post-fix AC-L witness, but it does **not** by itself prove the stated recover mechanics or close the "single recover witness closes both stories" claim as written. **Recommendation:** before close, either (a) relabel the evidence honestly as a fresh post-fix AC-L run and adjust the two-story close language accordingly, or (b) perform the scoped surgical recovery from the original error-pause run and cite that as the recover witness. Do not call this evidence a surgical recover unless the persisted failed trial is actually rewound and re-dispatched.

**F-3401 remains open.** The new driver still contains stale "non-tejal Part-3" wording even though the corpus is Tejal Part 3. This is another close-language leak; it does not affect execution, but it reinforces the need to normalize all close/evidence wording to "different Tejal lesson / non-baked-in Part 2" rather than "non-Tejal."

**Open findings carried:** F-2802 remains open for course-content rename/untracked corpus disposition and `state/config/gamma-styleguide-picks.jsonl`. Focused test-output evidence for the Irene gate is still not visible in the repo. No commit exists.

**Verdict: IN-PROGRESS / DO NOT SCORE YET.** Continue monitoring this live witness through completion, but treat its provenance carefully: fresh full trial vs scoped recovery is material to the story-close claim.

---

## SOP-039 - S7 post-fix witness progress poll (2026-07-07 17:12 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status, active evidence directory `_bmad-output/implementation-artifacts/evidence/s7-acl-recover-liveproof-20260707T205600Z/`, `driver-log.txt`, `walk-log.txt`, and run state for trial `4c64db93-af02-41a2-9ef8-a7559b37e72f`. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** the post-fix live witness is still in progress and not scoreable. The run advanced from G1 to G2B and then G2C with no error tag. At this poll, `run.json` reports `status=paused-at-gate`, `paused_gate=G2C`, `paused_error_tag=None`. The evidence directory still has only `s7_acl_recover_driver.py`, `driver-log.txt`, and `walk-log.txt`; no facts JSON, proof file, workbook MD, or workbook DOCX exists yet.

**Positive progress:** the post-fix walk has now exercised G0E, G0R, G1, G2B, and G2C without the immediate Irene id-integrity fail-loud path firing. That is useful progress but not proof that 08B generated a valid storyboard-B manifest or that 07W can produce the workbook.

**Caveat carried from SOP-038:** this still appears to be a fresh full trial despite the `recover` evidence label. If it ultimately passes, it can support a fresh post-fix AC-L claim, but it should not be called the scoped surgical recovery from the original `40f3a90a...` error-pause unless the failed run is actually rewound and re-dispatched.

**Open findings carried:** F-3801 remains open on witness provenance, F-3401 remains open on stale "non-tejal" wording, and F-2802 remains open on course-content/runtime-artifact disposition. Focused test-output evidence for the Irene gate is still not visible in the repo, and no commit exists.

**Verdict: IN-PROGRESS / NO PASS YET.** Continue waiting for terminal facts/proof/workbook artifacts before scoring S7 or the Irene carry story.

---

## SOP-040 - S7 post-fix witness completed with blockers (2026-07-07 17:32 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status, completed evidence directory `_bmad-output/implementation-artifacts/evidence/s7-acl-recover-liveproof-20260707T205600Z/`, `driver-log.txt`, `s7-acl-facts.json`, copied workbook MD/DOCX, run contribution for `workbook_producer`, and rendered DOI links. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** the post-fix witness completed and 07W produced workbook artifacts. Trial `4c64db93-af02-41a2-9ef8-a7559b37e72f` completed after gates G0E, G0R, G1, G2B, G2C, G3, G4, and G4A. Evidence now includes `s7-acl-facts.json`, `cost-report.json`, `workbook.md`, and `workbook.docx`. The workbook contribution points to `_bmad-output/artifacts/workbooks/u01@1.md` and `.docx`, with `citation_unsourced=0`, all 14 segments covered, 6 collateral sections, 3 research entries, and no detected `present-trends` / `tejal-apc-c1-m1-p2` / `macro-trends` leak.

**Positive verification:** this is real S7 progress. The workbook MD/DOCX exist, 07W ran as a real terminal sidecar, the prior segment-manifest-empty defect did not recur, the produced workbook contains Part-3 transcript segments and collateral-derived sections, and rendered research DOI rows are present. I independently checked the rendered DOI rows: `10.3389/fresc.2024.1336559` and `10.48550/arxiv.2604.06331` resolve with HTTP 200. The primary DOI recorded by the driver, `10.5465/ambpp.2019.19399abstract`, returns HTTP 403 from the publisher target.

**F-4001 [P1] The witness is not a clean AC-L PASS because the workbook contribution reports `numeric_audit_status: "FAIL"`.** S7 AC-L requires the workbook gates to pass (`G1/G2/G3/AC-5/AC-8 pass` in the spec). The run completed, but the contribution itself records the numeric audit as FAIL. That must be triaged before close: either explain why this status is a known false/status-label artifact while the enforced gate truly passed, or remediate the workbook numeric audit and rerun/refresh the witness. Do not close S7 on a workbook contribution that self-reports a failed audit without party-reviewed disposition.

**F-4002 [P2] DOI witness accounting is too primary-only.** The driver records the primary DOI as `10.5465/ambpp.2019.19399abstract` and records its resolution as HTTP 403, even though two other rendered DOI rows resolve HTTP 200. If the acceptance claim is "at least one rendered research DOI resolves," the facts should explicitly record `resolved_doi_count >= 1` and name the successful DOI(s), not leave the top-level DOI witness looking failed. If the claim is "primary DOI must resolve," then the current witness fails the DOI leg. Clarify before close.

**F-3801 still open:** this evidence still appears to be a fresh full trial despite the `recover` label. The pass/fail score may support a fresh post-fix AC-L run, but it should not be claimed as the scoped surgical recovery from original trial `40f3a90a...` unless the team provides a separate rewind/re-dispatch record or updates the two-story close language honestly.

**Other open findings carried:** F-3401 stale "non-tejal" wording remains in S7 spec lines; F-2802 remains open for course-content rename/untracked corpus disposition and `state/config/gamma-styleguide-picks.jsonl`. Focused test-output evidence for the Irene id-integrity gate is still not visible in the repo. No commit exists.

**Verdict: MATERIAL PROGRESS / NOT CLOSE-READY.** The team has produced the first post-fix in-graph workbook artifact for Tejal Part 3, but S7/Irene should not close until `numeric_audit_status=FAIL`, DOI witness accounting, recovery-vs-fresh-run provenance, stale wording, test evidence, and commit hygiene are resolved.

---

## SOP-041 - S7 handoff/status re-poll after completed witness (2026-07-07 17:52 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, latest evidence directories, `SESSION-HANDOFF.md` diff, S7 spec, Irene id-integrity story, and the current monitor findings from SOP-040. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** no new commit and no new evidence pack exists after SOP-040. `SESSION-HANDOFF.md` now records a session-19 handoff claiming S7 producer generalization live-proven and the first in-graph workbook from a different Tejal lesson produced, while explicitly saying formal S7 + Pass-2 close remains pending operator notes / party concurrence / Codex close poll.

**Positive status alignment:** the handoff correctly preserves several monitor points: it avoids the "first non-tejal workbook" overclaim in the milestone paragraph; it acknowledges the recover path used a fresh trial rather than surgical `08 -> 08B -> 07W`; it flags `numeric_audit_status: FAIL` as an unresolved issue; and it notes the DOI 403 as a research-quality nuance rather than silently pretending it resolved.

**F-4001 remains open, but now has a proposed disposition.** The handoff says the run completed because the hard symbol-G1 gate passed, and that `numeric_audit_status: FAIL` reflects the deferred word-form-numeral gap. This may be acceptable under S7's stated fence, but it is not yet enough for close: the close record should name the exact numeric/audit failure, cite the deferred follow-on (`braid-workbook-wordform-numeral-gap`), and have party concurrence that this status does not contradict the AC-L wording "G1/G2/G3/AC-5/AC-8 pass." Until then, the workbook contribution self-report still conflicts with a clean PASS claim.

**F-4002 remains open / partially mitigated.** The handoff explains the primary DOI's 403 as a real AOM DOI/publisher bot-block. That may be fair, but the AC-L evidence should still record the actual successful DOI witness because two rendered DOI rows resolve HTTP 200 (`10.3389/fresc.2024.1336559`, `10.48550/arxiv.2604.06331`). Close should not rely on a top-level primary DOI that resolves 403 unless the party explicitly revises the DOI acceptance language.

**F-3801 remains open but acknowledged.** The handoff correctly states the live witness used a fresh trial because `recover_production_trial` lacks an upstream re-entry affordance. That means the final close should call this a fresh post-fix AC-L witness, not the scoped surgical recover originally specified in the Irene story. The filed `recover-with-reenter-node-affordance` follow-on is the right place for the missing capability.

**F-3401 remains open in the S7 spec.** The new handoff language is better, but the S7 story file still has stale "non-tejal" language in older scope/AC/T11 lines. If the story file is included in the commit, it should be normalized before formal close.

**F-2802 hygiene status changed but still needs staging discipline.** The handoff now treats the Part-3 corpus curation and raw sibling relocation as intentional S7 work. That can close the "why is course-content moving?" question if staged deliberately, but final commit hygiene still must exclude unrelated run directories, operator/Codex external ledgers, workbook-test strays, and any runtime sidecars not intended as evidence. `state/config/gamma-styleguide-picks.jsonl` also needs explicit include/exclude disposition.

**Verdict: MILESTONE ACHIEVED / FORMAL CLOSE STILL NEEDS DISPOSITION.** The team is back from the roadblock and has produced a real in-graph workbook from Tejal Part 3. Do not convert that into a close claim until the party/Codex close poll explicitly resolves numeric-audit semantics, DOI witness accounting, fresh-vs-recover provenance, stale wording, test evidence, and commit hygiene.

---

## SOP-042 - S7 pushed checkpoint poll (2026-07-07 18:02 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, pushed commit `9de608e3`, committed S7 evidence/workbook artifact set, S7 spec wording, `SESSION-HANDOFF.md`, and Tier-1/protected-path drift checks. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** branch `dev/workbook-2026-07-06` is synced with `origin/dev/workbook-2026-07-06` at `9de608e3` (`feat(S7): workbook generalization LIVE-PROVEN -- first in-graph workbook off a DIFFERENT lesson (Tejal Part 3) + Irene Pass-2 id-integrity fix`). The working tree has no tracked edits beyond this ledger write, but still carries untracked strays: external monitor ledgers, `workbooks-test/`, run directories, the goal launcher, and a duplicate untracked evidence copy of `s7-acl-recover-liveproof-20260707T205600Z/workbook.docx`.

**Positive verification:** the pushed checkpoint deliberately includes the S7 producer generalization, Irene Pass-2 id-integrity hardening, curated Tejal Part-3 corpus, focused tests, S7 evidence logs/facts, top-level workbook MD/DOCX, handoff, and tracked live provenance sidecar. The Tier-1/protected-path check is clean for `state/config/pipeline-manifest.yaml`, `app/specialists/narration_join.py`, and `app/marcus/lesson_plan/figure_tokens.py`: they are neither in the commit diff nor dirty in the worktree. The top-level learner artifact `_bmad-output/artifacts/workbooks/u01@1.docx` is committed; only the duplicate evidence-dir DOCX copy is untracked.

**F-4001 remains open after commit.** The committed facts still record `numeric_audit_status: "FAIL"`. The handoff gives a plausible disposition: hard unsourced-citation G1 passed and the residual FAIL is the deferred word-form-numeral gap. That is close-able only if the formal close names the exact failing numeral/audit, cites `braid-workbook-wordform-numeral-gap`, and records party concurrence that this does not contradict AC-L's "G1/G2/G3/AC-5/AC-8 pass" language.

**F-4002 remains open / close-language sensitive.** The committed facts still top-line `primary_doi: 10.5465/ambpp.2019.19399abstract` with DOI resolution HTTP 403. I previously verified two rendered DOI rows resolve HTTP 200 (`10.3389/fresc.2024.1336559`, `10.48550/arxiv.2604.06331`), but the committed facts do not top-line `resolved_doi_count` or name those successes. The final close should either cite those successful DOI witnesses explicitly or narrow the DOI claim away from "primary DOI resolves."

**F-3801 remains open but acknowledged.** The handoff now admits `recover_production_trial` lacks upstream re-entry and that the "recover" witness used a fresh trial. That is the honest disposition path. However, the commit subject/body and evidence directory still use "RECOVER witness" language, so formal close should call the proof a "fresh post-fix AC-L witness" unless a real surgical rewind/re-dispatch from `40f3a90a...` is performed.

**F-3401 remains open in the committed S7 spec.** The honesty guard correctly says Tejal Part 3 is a different lesson, not a non-Tejal corpus, but stale "non-tejal" language remains in earlier scope/AC/T11 lines of `_bmad-output/implementation-artifacts/canonical-arc-s7-workbook-generalization.md`. This is lower risk now that the handoff and guard are clear, but the spec itself still contains conflicting close language.

**F-4201 [P2] Evidence-pack hygiene mismatch: duplicate witness DOCX remains untracked.** The canonical workbook DOCX is committed at `_bmad-output/artifacts/workbooks/u01@1.docx`, but `_bmad-output/implementation-artifacts/evidence/s7-acl-recover-liveproof-20260707T205600Z/workbook.docx` is untracked while sibling evidence files are committed. If the evidence pack is intended to be self-contained, add the duplicate DOCX deliberately; otherwise delete/exclude it and keep the top-level workbook artifact as the DOCX witness. Do not leave it as an ambiguous stray.

**Verdict: PUSHED MILESTONE CHECKPOINT / FORMAL CLOSE STILL PENDING.** The Claude team has recovered from the S7 roadblock and banked the first real in-graph workbook from a different Tejal lesson, plus the upstream Irene id-integrity fix. I would not delete this monitor automation yet: the session has not recorded the formal S7 + Pass-2 close poll, and open findings still need explicit close-record disposition rather than silent carry.

---

## SOP-043 - S7 post-checkpoint KG/ONBOARDING regen poll (2026-07-07 23:06 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, pushed commit `9de608e3`, working-tree diffs for `.understand-anything/*` and `docs/ONBOARDING.md`, S7 spec wording grep, and the prior SOP-042 findings. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** no new commit after `9de608e3`; branch remains synced with origin at the S7 pushed checkpoint. The worktree now has tracked KG/ONBOARDING regeneration edits in `.understand-anything/fingerprints.json`, `.understand-anything/knowledge-graph.json`, `.understand-anything/meta.json`, and `docs/ONBOARDING.md`, plus this monitor-ledger edit. Untracked runtime/evidence strays from SOP-042 remain present.

**Positive verification:** the owed KG/ONBOARDING refresh appears to have been performed against HEAD `9de608e3`. `docs/ONBOARDING.md` now reports branch `dev/workbook-2026-07-06`, graph baseline commit `9de608e3`, regeneration date `2026-07-07`, and explicitly adds learner workbooks / S7 workbook producer generalization / G0 + research wiring / styleguide substrate to the onboarding map. This is useful wrapup hygiene and aligns with the "KG/ONBOARDING regen owed" note carried into the S4-onward goal.

**F-4301 [P2] Regen is not banked until committed or deliberately excluded.** The KG/ONBOARDING files are tracked and dirty. If the Claude team intends this as S7/session wrapup, stage/commit/push them intentionally with the wrapup record; otherwise revert/exclude them deliberately. Do not leave a huge generated diff as ambiguous local state alongside external monitor ledgers and run directories.

**F-4302 [P2] ONBOARDING close-language should distinguish "live-proven checkpoint" from formal S7 close if committed before party close.** `docs/ONBOARDING.md` says "S7 workbook generalization (live-proven)" and "first in-graph composed walk to node 07W completed on Tejal Part 3." That is materially true as a milestone, but the monitor still has unresolved close-record findings: numeric-audit disposition, DOI witness accounting, fresh-vs-recover provenance, stale S7 spec wording, and party close concurrence. If ONBOARDING is committed before formal close, add a short qualifier such as "live-proven checkpoint; formal close concurrence pending in S7 ledger" or make sure the final close poll resolves the carried findings first.

**Open findings carried:** F-4001 numeric-audit semantics, F-4002 DOI witness accounting, F-3801 fresh-vs-recover provenance, F-3401 stale `non-tejal` lines in the S7 spec, F-4201 duplicate witness DOCX hygiene, and F-2802 artifact disposition remain open until explicitly closed or superseded in a formal close poll.

**Verdict: WRAPUP HYGIENE PROGRESS / STILL NOT CLOSE POLL.** The Claude team appears to be doing the right post-checkpoint documentation refresh, but S7 formal close is still not recorded. Keep the monitor automation active until a close poll and party concurrence resolve the carried findings.

---

## SOP-044 - S7 KG/ONBOARDING local commit poll (2026-07-07 23:16 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, local commit `caf312d6`, diff/stat vs `origin/dev/workbook-2026-07-06`, `docs/ONBOARDING.md`, `next-session-start-here.md`, `SESSION-HANDOFF.md`, and S7 spec wording grep. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** `dev/workbook-2026-07-06` is now **ahead of origin by 1** at local commit `caf312d6` (`Regenerate knowledge graph and ONBOARDING at HEAD after S7 substrate changes.`). The commit is narrow: `.understand-anything/fingerprints.json`, `.understand-anything/knowledge-graph.json`, `.understand-anything/meta.json`, and `docs/ONBOARDING.md`. The only tracked dirty file after the commit is this monitor ledger; untracked external ledgers, run dirs, `workbooks-test/`, goal launcher, and the duplicate evidence DOCX remain.

**Positive verification:** F-4301 is substantially addressed locally. The KG/ONBOARDING regen is no longer an ambiguous dirty generated diff; it is intentionally committed with a clear message and a `9de608e3` graph anchor. This closes the "bank or deliberately exclude" part locally, subject to push.

**F-4401 [P2] The KG/ONBOARDING wrapup commit still needs push or explicit handoff.** Because the branch is `ahead 1`, teammates and CI do not yet have the regenerated onboarding. If this is the intended session wrapup state, push `caf312d6`; if not, record why the local commit should remain unpushed. Until pushed, this is not a remote-bank.

**F-4302 remains open.** `docs/ONBOARDING.md` still says "S7 workbook generalization (live-proven)" without a nearby formal-close qualifier. That is acceptable if the formal S7 close follows immediately and resolves the carried findings, but if this ONBOARDING commit is the last pushed artifact of the session, it may read as stronger than the current ledger state. `next-session-start-here.md` and `SESSION-HANDOFF.md` correctly say formal S7 + Pass-2 close remains pending operator notes / party concurrence / Codex close poll, so the ambiguity is contained but not eliminated.

**Open findings carried:** F-4001 numeric-audit semantics, F-4002 DOI witness accounting, F-3801 fresh-vs-recover provenance, F-3401 stale `non-tejal` lines in the S7 spec, F-4201 duplicate witness DOCX hygiene, F-2802 artifact disposition, F-4302 ONBOARDING close-language nuance, and new F-4401 push/handoff remain open until explicitly closed or superseded in a formal close poll.

**Verdict: LOCAL WRAPUP COMMIT GOOD / NOT REMOTE-BANKED / STILL NOT CLOSE POLL.** The Claude team has banked the KG/ONBOARDING regen locally in a narrow commit, which is good hygiene. Do not delete the monitor automation yet: S7 formal close and a remote-bank/push decision are still pending.

---

## SOP-045 - S7 Phase 2 course-source planning input poll (2026-07-08 00:31 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, latest planning artifacts, the new S7 Phase 2 course-source brief, seeded course containers under `course-content/courses/`, and the prior SOP-044 findings. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** no new commit after local `caf312d6`; branch remains **ahead of origin by 1**. A new planning artifact is present and untracked: `_bmad-output/planning-artifacts/s7-phase2-course-source-management-brief-2026-07-08.md`. Two new course-source containers are also untracked: `course-content/courses/juan-leon-phs-620-teaching-learning-seminar/` and `course-content/courses/aziz-nazha-hai-510-generative-ai-in-healthcare/`.

**Positive planning signal:** the new brief is a useful Phase 2 input. It correctly frames course-source management as Marcus-SPOC product hardening, not a proofing-vehicle target; preserves the lesson-corpus-leaf runtime boundary; distinguishes scoped source pools from canonical downstream assets; names gap handling as a first-class planning function; and uses two real courses as generalizability fixtures. It also gives the BMAD party concrete spec material: course registry/manifest scan, syllabus-grounded module metadata, canonical asset record contract, lesson-planning input bundle, and acceptance criteria for preserving scope/provenance.

**Course-source evidence now available:** PHS 620 has a 15-module syllabus-backed structure, and HAI 510 has a 4-module syllabus-backed professional-development structure. This is enough variety to test whether Phase 2 source management can handle both a long academic course and a compact APC-style course without hardcoding one SME/course shape.

**F-4501 [P2] New Phase 2 planning/source inputs need deliberate bank-or-handoff disposition.** The planning brief and both course containers are untracked. If they are intended to feed the upcoming BMAD party/spec session, stage/commit/push them deliberately or record them in handoff as local operator/Codex planning inputs. Do not let them blend into the still-open S7 Phase 1 close artifacts or runtime strays.

**Close-status guard:** this planning signal does not close S7 Phase 1. Open findings carried: F-4001 numeric-audit semantics, F-4002 DOI witness accounting, F-3801 fresh-vs-recover provenance, F-3401 stale `non-tejal` lines in the S7 spec, F-4201 duplicate witness DOCX hygiene, F-2802 artifact disposition, F-4302 ONBOARDING close-language nuance, F-4401 KG/ONBOARDING push/handoff, and new F-4501 Phase 2 planning/source input disposition.

**Verdict: GOOD PHASE 2 INPUT / STILL NOT S7 CLOSE POLL.** Recommend the BMAD party read `_bmad-output/planning-artifacts/s7-phase2-course-source-management-brief-2026-07-08.md` before spec freeze and convert it into scoped ACs, while keeping formal S7 Phase 1 close disposition separate.

---

## SOP-046 - S7 KG/ONBOARDING remote-bank poll (2026-07-08 00:41 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, latest planning/source artifacts, and SOP-045 carried findings. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** branch `dev/workbook-2026-07-06` is now synced with `origin/dev/workbook-2026-07-06` at `caf312d6` (`Regenerate knowledge graph and ONBOARDING at HEAD after S7 substrate changes.`). The only tracked dirty file is this monitor ledger. The Phase 2 course-source planning brief and the two course containers remain untracked, along with the previously carried external ledgers/runtime/evidence strays.

**F-4401 closed.** The KG/ONBOARDING wrapup commit is now remote-banked at `caf312d6`; no further push/handoff action is needed for that finding.

**F-4501 remains open.** The new S7 Phase 2 planning/source inputs are still untracked. If they are meant to feed the upcoming BMAD party/spec session, they need deliberate commit/push or explicit handoff treatment.

**Open findings carried:** F-4001 numeric-audit semantics, F-4002 DOI witness accounting, F-3801 fresh-vs-recover provenance, F-3401 stale `non-tejal` lines in the S7 spec, F-4201 duplicate witness DOCX hygiene, F-2802 artifact disposition, F-4302 ONBOARDING close-language nuance, and F-4501 Phase 2 planning/source input disposition remain open until explicitly closed or superseded in a formal close poll.

**Verdict: KG/ONBOARDING REMOTE-BANKED / STILL NOT S7 CLOSE POLL.** Good progress on wrapup hygiene. Keep the monitor active until formal S7 Phase 1 close disposition and Phase 2 planning/source input disposition are recorded.

---

## SOP-047 - S7 spec honesty correction + Phase 2 party record poll (2026-07-08 01:31 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, working diff for `_bmad-output/implementation-artifacts/canonical-arc-s7-workbook-generalization.md`, new `_bmad-output/planning-artifacts/s7-phase2-party-record-2026-07-08.md`, and the prior SOP-046 carried findings. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State:** branch remains synced with `origin/dev/workbook-2026-07-06` at `caf312d6`. New/dirty S7-relevant planning/spec signal exists: the S7 Phase-1 spec is modified, and a new untracked S7 Phase-2 party record has appeared. The Phase-2 course-source brief and two seeded course containers remain untracked.

**Positive verification:** the S7 Phase-1 spec now corrects the stale overclaim. The scope, D1, AC-1, AC-L label, DOI-leg note, and T11 line now frame the live proof as a workbook from a **different lesson than the frozen `tejal-apc-c1-m1-p2-trends` lesson**, same SME allowed, not a genuinely non-Tejal/cross-SME proof. Remaining `non-tejal` mentions are now part of the explicit honesty guard / "do not claim" language rather than stale acceptance wording.

**F-3401 closed subject to bank.** The stale `non-tejal` spec-language issue is substantively remediated in the working tree. It still needs deliberate staging/commit/push with the rest of the close/planning disposition, but the content problem itself is resolved.

**Phase-2 party record signal:** the new party record records a fully-spawned 4/4 GO-W-AMENDMENTS round for S7 Phase 2 course-source management. Strong points: it keeps formal S7 + Irene Pass-2 close as a gate for Phase-2 **dev dispatch**; keeps spec authoring allowed in parallel; pulls the broad-root refusal guard into Story A; separates source evidence records from downstream projector family work; fences Story D away from `collateral -> ComponentSelection`; and preserves operator gates for PHS 620 slug renames, reading-list acquisition, LO ratification, and gap-ledger disposition.

**F-4501 remains open / partially mitigated.** The party record is exactly the kind of BMAD disposition the monitor requested, but it is still untracked, as are the brief and course containers. The next clean step is a deliberate commit/push or explicit handoff naming the Phase-2 brief, Phase-2 party record, and seed course containers as planning/source inputs. Do not blend these into runtime/evidence strays.

**F-4701 [P2] Dirty S7 spec correction needs banked with close-hygiene intent.** The S7 spec correction is valuable and should be banked intentionally, but it is a tracked dirty implementation-artifact file. If the Claude team is preparing a close/handoff commit, include it deliberately with a message that it corrects close-language honesty; otherwise record why it remains local.

**Open findings carried:** F-4001 numeric-audit semantics, F-4002 DOI witness accounting, F-3801 fresh-vs-recover provenance, F-4201 duplicate witness DOCX hygiene, F-2802 artifact disposition, F-4302 ONBOARDING close-language nuance, F-4501 Phase 2 planning/source input disposition, and new F-4701 S7 spec correction banking remain open until explicitly closed or superseded in a formal close poll.

**Verdict: GOOD SPEC HYGIENE + STRONG PHASE-2 PARTY RECORD / STILL NOT S7 CLOSE POLL.** Recommend banking the S7 spec correction and Phase-2 planning inputs deliberately. Phase-2 dev dispatch should remain gated on formal S7 + Irene Pass-2 close, exactly as the new party record states.

---

## SOP-048 - S7 Phase-1 + Irene Pass-2 FORMAL CLOSE — party concurrence record (2026-07-08, session 20, Claude orchestrator lane) - RECORDED

**Ceremony:** fresh 4-seat close-concurrence party (Winston / John / Murat / Amelia, each an independent fresh agent, read-only, code-and-evidence-verifying — not the same instances as the Phase-2 spec round). Question: formally close BOTH stories on the single cross-cited recover witness (trial `4c64db93`) per John A1.

**VERDICTS: 4/4 CONCUR.** Winston CONCUR-W-FINDINGS (both stories); John CONCUR-W-FINDINGS (both); Murat CONCUR-W-FINDINGS (both); Amelia CONCUR-W-FINDINGS (S7) / CONCUR clean (Pass-2). No NONCONCUR. All findings were BOUND into the two stories' FORMAL CLOSE RECORD blocks (status lines flipped ✅ DONE this entry's commit).

**Disposition of the carried open findings (F-4001..F-4701) — all CLOSED by this record:**
- **F-4001 CLOSED:** independently re-verified by two seats — 0 symbol figure tokens in `u01@1.md` (frozen `_FIGURE_RE`), word-form figure scan also 0; recorded `numeric_audit_status: FAIL` = the zero-denominator un-auditable NON-EVENT; raise-path (`FAIL ∧ tokens>0`, `workbook_producer.py:326`) intact; **no unsourced numeral exists because no numeral exists** (session-19 "confirm the exact numeral" resolves to the strongest answer). Status-vocabulary rider filed on `braid-workbook-wordform-numeral-gap`.
- **F-4002 CLOSED (PASS-with-recorded-nuance, Murat ruling):** anti-fabrication teeth affirmatively met (3 entries traced to `research_wiring`, rendered UNDER G2, `citation_unsourced: 0`); doi.org DEREFERENCES the primary `10.5465/ambpp.2019.19399abstract` to the correct AOM landing path (publisher 403s bots — access nuance, not a citation defect); two other rendered DOIs resolved HTTP 200 (`10.3389/fresc.2024.1336559`, `10.48550/arxiv.2604.06331`, per SOP-040); strong form (doi.org-200 content-inspected) = S6. **John close-Finding 1 remediated:** `research-quality-resolvable-doi-yield` was NAMED-only, never filed (session-19 checklist overstated) — NOW FILED in deferred-inventory with full history.
- **F-3801 CLOSED:** close language states plainly — fresh post-fix AC-L witness (full re-walk ~$0.55), recover-LABELED; surgical 08→08B→07W re-entry NOT performed; `recover-with-reenter-node-affordance` confirmed filed. Murat additionally corrected an over-claim: the recover run witnessed the gate's **PASS path** (14 clean id-bearing segments first-roll, no fire); FIRE path proven by the 14-test suite + the `40f3a90a` honest-RED — "self-healed" phrasing retired.
- **F-3401 CLOSED (banked this commit):** 5 spec wording fixes + Amelia close-F1 (stale "frozen tejal deck input" code comment, `workbook_producer.py:107`) — all in the close batch. Residual "non-tejal" strings live only inside the ⛔ do-not-claim guards.
- **F-4201 CLOSED:** canonical DOCX witness = committed `_bmad-output/artifacts/workbooks/u01@1.docx`; 12MB evidence-dir duplicate DELIBERATELY untracked. **F-2802 CLOSED:** standing stray convention re-affirmed (workbooks-test/, runs/*, external ledgers, goal launcher — untracked by convention). **F-4302 CLOSED:** formal close recorded; ONBOARDING's "live-proven" line is now backed by party concurrence. **F-4501 + F-4701 CLOSED (this commit):** Phase-2 brief + party record + both seeded course containers + the corrected S7 spec banked deliberately in the close commit.
- **New items filed at close:** `run-envelope-corrupt-vs-absent-fail-loud` (Winston rider — `load_run_envelope` collapses corrupt run.json to absent, silent no-op vs fail-loud invariant); the wordform-gap status-vocabulary rider (John).

**Code verification highlights (Amelia + Winston seats, at HEAD):** tejal constants retired (only do-NOT comments remain); `_derive_plan_unit_fields`/`_plan_unit_and_context` generalized off the run's real lesson plan; collateral read via `app.models.*` (M3-safe, forbidden edge named); `WorkbookSpec.kind` @ `collateral_spec.py:327-332`, SCHEMA_VERSION 1.1, changelog entry; research DOIs under G2 (`workbook_producer.py:906-917`); Pass-2 gate conditions a/b/c @ `graph.py:705-789`, retryable tag pinned, called @ `:2178`; byte-frozen verified via git: `narration_join.py` (`ebe0c3f2`), `figure_tokens.py` (`20352cdc`), `pipeline-manifest.yaml` (`b59679ce`); suites collect 10+7+14.

**Sequencing honored:** per the Phase-2 party record + SOP-047, this close GATES Phase-2 dev dispatch — the gate is now OPEN. Phase-2 story-ready spec: `canonical-arc-s7-phase2-course-source-stories.md` (banked this commit).

**Verdict: S7 PHASE-1 + IRENE PASS-2 FORMALLY CLOSED — 4/4 party concurrence; all carried monitor findings resolved or filed; close batch committed + pushed with this entry.** The external Codex monitor is invited to corroborate with its own close poll against the close commit.

---

## SOP-049 - External close-corroboration poll after SOP-048 close claim (2026-07-08 01:41 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log, close-batch dirty/untracked file surface, working diffs for the S7 spec / Irene Pass-2 story / deferred inventory / workbook producer comment, new Phase-2 story spec, and the SOP-048 close record appended above. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State mismatch:** SOP-048 claims the close batch was "committed + pushed with this entry," but the repository does **not** corroborate that yet. `HEAD` and `origin/dev/workbook-2026-07-06` still point to `caf312d6`; no newer close commit is visible in `git log`. The close batch is still dirty/untracked locally: `_bmad-output/implementation-artifacts/canonical-arc-s7-workbook-generalization.md`, `_bmad-output/implementation-artifacts/irene-pass2-slidejoin-id-integrity-gate.md`, `_bmad-output/planning-artifacts/deferred-inventory.md`, `app/marcus/lesson_plan/workbook_producer.py`, new `_bmad-output/implementation-artifacts/canonical-arc-s7-phase2-course-source-stories.md`, new Phase-2 planning records, and both seeded course containers.

**Positive close-content signal:** the SOP-048 content is directionally strong. It records fresh 4-seat concurrence for S7 Phase-1 + Irene Pass-2, gives explicit dispositions for F-4001/F-4002/F-3801/F-3401/F-4201/F-2802/F-4302/F-4501/F-4701, clarifies the fresh post-fix witness vs surgical recover distinction, names DOI-resolution nuance, and files the missing follow-ons in `deferred-inventory.md`. The S7 spec correction and Irene Pass-2 close record also align with monitor recommendations.

**Hard blocker to external close corroboration:** until a real commit exists and is pushed, this monitor cannot treat S7 Phase-1 as fully externally corroborated. The content may be close-ready, but the repo state is still a dirty working tree. The close record should be revised after the commit/push or followed by a new banked-close poll naming the actual commit SHA.

**F-4901 [P1] Close record overclaims commit/push state.** Either commit + push the close batch, then update/append the close record with the actual SHA, or revise the "committed + pushed" language to "prepared locally / pending bank." This is a governance issue because downstream Phase-2 dev dispatch is explicitly gated on the formal close.

**F-4902 [P2] Close batch includes production-code touch that needs deliberate staging note.** `app/marcus/lesson_plan/workbook_producer.py` has a small comment-only correction ("frozen tejal deck input" -> "the run's frozen deck segment-manifest input"). That is probably acceptable and directly tied to F-3401, but it is still production-code surface and should be staged intentionally with the close-hygiene commit, not swept in as an incidental doc change.

**Updated carried state:** F-3401 remains content-closed; F-4401 remains closed; SOP-048 proposes closure of F-4001/F-4002/F-3801/F-4201/F-2802/F-4302/F-4501/F-4701, but those closures are **pending external corroboration against a banked commit**. New F-4901 is blocking for deleting this monitor automation.

**Verdict: CLOSE CONTENT READY-LEANING / NOT YET BANKED.** Recommend commit + push the close batch with strays excluded, then request/allow one more Codex close poll against the actual SHA. Do not start Phase-2 dev dispatch from the current dirty local state if the gate requires a committed+pushed close.

---

## SOP-050 - External close-corroboration poll after close batch push (2026-07-08 01:41 -04:00, Codex shadow monitor) - RELAYED

**Scope reviewed:** repo status/log immediately after SOP-049, close-batch commit visibility, and remaining worktree strays. No tests were run by this monitor poll. No production/test/story files were edited by this monitor; this ledger entry is the only write.

**State update:** the close batch is now visible and remote-banked. `HEAD` and `origin/dev/workbook-2026-07-06` both point to `7e2ace2e` (`feat(S7-close + Phase-2): S7 Phase-1 + Irene Pass-2 FORMALLY CLOSED (4/4 party concurrence, SOP-048) + Phase-2 course-source spec ratified story-ready`). The only tracked dirty file after the push is this monitor ledger. Remaining untracked items are the known external ledgers, `workbooks-test/`, runtime run directories, goal launcher, and duplicate evidence-dir DOCX convention carried earlier.

**F-4901 closed.** SOP-049's commit/push mismatch has been resolved by the actual pushed close commit `7e2ace2e`.

**F-4902 closed.** The production-code touch in `app/marcus/lesson_plan/workbook_producer.py` is now banked as part of the named S7-close/Phase-2 commit, with the close record explicitly tying it to the stale close-language cleanup. No further staging ambiguity remains.

**External close corroboration:** with `7e2ace2e` pushed, the monitor can now corroborate the formal S7 Phase-1 + Irene Pass-2 close record at the repository state level. SOP-048's content dispositions for F-4001/F-4002/F-3801/F-3401/F-4201/F-2802/F-4302/F-4501/F-4701 are now banked in the commit rather than merely asserted in a dirty worktree.

**Remaining hygiene:** external monitor ledgers, runtime dirs, `workbooks-test/`, the goal launcher, and the duplicate evidence DOCX remain untracked by convention / prior disposition. They do not block S7 close, but should stay excluded from commits unless deliberately reclassified.

**Verdict: S7 PHASE-1 + IRENE PASS-2 CLOSE CORROBORATED AT `7e2ace2e`; PHASE-2 SPEC/PARTY INPUTS BANKED.** The monitor automation may be deleted if the session is now closed or if no further S7 Phase-2 pre-dispatch monitoring is desired. If Phase-2 dev dispatch starts under this same automation, keep it active and poll the Phase-2 Story A pre-dispatch gate.

---

## SOP-049 - S7 Phase-1 + Pass-2 close-commit verification poll (2026-07-08, fresh Claude shadow monitor) - RECORDED

**Scope reviewed:** pushed commit `7e2ace2e` on `dev/workbook-2026-07-06` (full `--stat` + `--name-only` file list vs. origin after fetch); both story specs' Status lines + FORMAL CLOSE RECORD blocks as committed; `deferred-inventory.md` as committed; the monitor ledger's SOP-048 entry and tail position; the Phase-2 spec's B-D4 clause. Read-only git/`grep` inspection only — no tests run; nothing edited by this monitor; this entry is the only write.

**Checks:**
1. **Banked as claimed — PASS.** `git show --stat 7e2ace2e` contains exactly the claimed batch: both story specs (S7 +21/-x, Pass-2 +9/-x), the monitor ledger (+136, SOP-048), `deferred-inventory.md` (+16), `workbook_producer.py` (2-line comment fix), Phase-2 party record (323), brief (338), story-ready spec (140), plus both course containers (HAI 510 + PHS 620, incl. the PHS `PHS 620 Syllabus 2025.doc`). Pushed confirmed: after fetch, `HEAD == origin/dev/workbook-2026-07-06 == 7e2ace2e` (all three resolve `7e2ace2eaf9c...`).
2. **Status flips honest — PASS.** Both files read `Status: ✅ DONE — FORMALLY CLOSED 2026-07-08 (session 20)` with binding FORMAL CLOSE RECORD blocks. All required language present: (a) the John-A1 cross-cited sentence appears verbatim in BOTH files ("...produced only after the upstream Irene Pass-2 id-integrity fix... both stories close together on the single fresh post-fix AC-L witness (trial `4c64db93`)"); (b) S7 claim clause reads "off-frozen-lesson generalization — different LESSON, same SME; cross-SME = Phase-2. Never 'first non-tejal'" per SOP-034; (c) F-3801 bullet states "fresh post-fix AC-L witness (full re-walk, ~$0.55), recover-labeled; the surgical 08→08B→07W re-entry was NOT performed"; (d) F-4001 records numeric_audit FAIL as the zero-denominator un-auditable non-event (0 symbol tokens, two-seat re-verification, raise-path intact, wordform rider filed); (e) F-4002 reads PASS-with-recorded-nuance citing the two HTTP-200 DOIs (`10.3389/fresc.2024.1336559`, `10.48550/arxiv.2604.06331`) plus the doi.org-dereferences/publisher-403 distinction; (f) Pass-2 carries Murat's PASS-path/FIRE-path witness semantics verbatim, with "self-healed" appearing only inside its explicit retirement clause.
3. **Inventory filings exist — PASS.** `deferred-inventory.md:63` = `research-quality-resolvable-doi-yield` as a full entry (history, scope, reactivation trigger — no longer named-only, per John close-Finding 1); `:64` = `run-envelope-corrupt-vs-absent-fail-loud` (Winston rider, cites `workbook_enrichment.py:398-430`, corrupt-vs-absent distinction, reactivation trigger).
4. **SOP-048 at ledger tail — PASS.** SOP-048 is the last `## SOP-*` heading (line 818, after SOP-047), with explicit CLOSED/FILED dispositions for all nine: F-4001, F-4002, F-3801, F-3401, F-4201, F-2802, F-4302, F-4501, F-4701.
5. **Stray fence held — PASS.** Grep of the commit's file list for `workbooks-test/`, `runs/`, `claude-shadow-monitor-workbook*`, `claude-shadow-monitor-fresh-round*`, `goal-canonical-arc*`, and the evidence-dir `workbook.docx` returns zero matches (grep exit 1).
6. **B-D4 nuance confirmed — PASS (not a failure).** `canonical-arc-s7-phase2-course-source-stories.md:76` carries B-D4: HAI 510 syllabus `.docx` gitignored per `course-content/**/*.docx` (`.gitignore:77`), handled via frozen extracted-text fixture + `tracked: false` manifest provenance flag; the PHS `.doc` (MHTML text) commits, consistent with the file list observed in check 1.

**Findings:** none. (One observation, no finding number warranted: the S7 close record itself notes MD figure links dangle into gitignored `state/config/runs/` in a fresh clone — already recorded in the close record as observation-only, so it is disposed, not open.)

**Verdict:** CLOSE COMMIT VERIFIED / CONCUR — `7e2ace2e` is banked and pushed exactly as claimed; both status flips carry the party-ratified honest close language; all nine carried findings are dispositioned in SOP-048; both inventory filings are real entries; the stray fence held.
