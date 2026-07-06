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
