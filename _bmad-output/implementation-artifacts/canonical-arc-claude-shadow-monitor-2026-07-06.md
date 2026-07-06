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
