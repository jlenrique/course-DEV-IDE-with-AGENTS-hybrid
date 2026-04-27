# M5 Decision

Consensus verdict: SHIP-CONDITIONAL

## Evidence Summary

- 5a.1 replay regression is green on the migrated branch substrate.
- 5a.2 proves actual-substrate control-plane parity at Tier 1 = 100% and Tier 2 = 100%, but does not prove production clone-launch equivalence.
- 5a.3 ships the amended cost-engineering foundation: strict economics schema, operator-editable cascade/pricing config, persisted per-trial cost reports, and a migrated-runtime characterization baseline.
- 5a.4 ships the 15-invariant audit matrix and FR64 cycle-complete anti-pattern annotation.
- The 15-invariant audit matrix records all 15 invariants as `PRESERVED`.
- The operator ratified the 5a.3 cascade/pricing configuration on 2026-04-26 after the fixed-roster party-mode vote.
- Batch 2 pre-trial defensibility pass (2026-04-27) adds `_bmad-output/implementation-artifacts/m5-fr-traceability-matrix.md`: 17 FR rows reviewed, 15 `TRACED`, 2 `PARTIAL`, 0 `GAP`.
- Batch 2 pre-trial defensibility pass (2026-04-27) adds `_bmad-output/implementation-artifacts/m5-nfr-assessment.md`: 11 NFRs reviewed, 11 `MET`, 0 `NOT MET`.
- Batch 2 pre-trial defensibility pass (2026-04-27) adds `_bmad-output/implementation-artifacts/5a-3-test-quality-audit.md`: 9 5a.3 test files reviewed, overall score 80/100, no file below 70.

## Inherited Conditional States

- M2: CONDITIONAL-GREEN. Wondercraft live artifact/operator addendum still pending.
- M3: CONDITIONAL-GREEN. Texas live retrieval operator window still pending.
- M4: GREEN-WITH-RIDERS. Positive ledger/Postgres query evidence and inherited repo-wide pytest debt optics remain riders.
- 5a.2 rider: control-plane parity only; production clone-launch equivalence remains unproven.
- slab-3-m5-dispatch-registry-swap: RESOLVED 2026-04-26. The live dispatch registry and frozen `v42` snapshot were both promoted from `_status: interim` to `_status: production` after import-path verification across every registered specialist.
- 5a.3 ratification: RESOLVED 2026-04-26. The operator ratified the cascade/pricing configuration at the M5 gate, so this is no longer an open condition.

## Party-Mode Verdict (6 agents)

The verbatim agent records below capture the pre-ratification vote. The post-vote
operator ratification on 2026-04-26 resolves the 5a.3 cascade/pricing condition
without changing the recorded six-agent verdict.

### Winston

Verdict: SHIP-CONDITIONAL

Verbatim response: "The migration is architecturally credible enough to move forward in a controlled form: 5a preserves all 15 invariants, replay regression is green, control-plane parity is complete on the actual substrate, and the economics contract is now stricter and operator-editable. But this is not a clean unconditional ship. M2 and M3 still carry unresolved live-evidence conditions, 5a.2 does not yet prove production clone-launch equivalence on a runnable surface, and 5a.3 still depends on operator ratification for the cascade and pricing posture. From a system design standpoint, that means the foundation is sound, while release confidence is still bounded by operational proof and governance sign-off."

Riders: Ship only as a gated release. Before broad rollout, close the Wondercraft and Texas live-evidence items, produce runnable production clone-launch parity evidence, and secure explicit operator ratification of the cascade/pricing configuration; until then, no claim of full production-equivalent migration should be made.

### Murat

Verdict: SHIP-CONDITIONAL

Verbatim response: "From a risk-based test standpoint, I do not see rollback-class evidence. Replay regression is green, actual-substrate control-plane parity is complete at Tier 1 and Tier 2, the economics/reporting contract is now stricter and characterized, and the 15-invariant matrix says behavior is preserved. But the remaining gaps are not cosmetic: M2 and M3 still depend on live operator evidence, 5a.2 does not prove production-clone launch equivalence, and 5a.3 still needs operator ratification for the cascade/pricing behavior. That combination supports a controlled ship, not an unconditional one."

Riders: Ship only with explicit release conditions recorded: complete the pending M2 Wondercraft and M3 Texas live operator evidence, treat 5a.2 as control-plane-only parity until a runnable production clone-launch path is exercised, and require formal operator ratification of the 5a.3 cascade/pricing configuration. I would also keep a close watch on inherited pytest debt optics and positive ledger/Postgres evidence where `DATABASE_URL` is available.

### Paige

Verdict: SHIP-CONDITIONAL

Verbatim response: "The written record is coherent enough to support shipment, but not clean enough to pretend every proof is closed. 5a.1, 5a.3, and 5a.4 read as solid and well-bounded, and the 15-invariant matrix gives a strong continuity story. But 5a.2 proves control-plane parity, not production-clone launch equivalence, and M2/M3 already carry unresolved live-operator evidence. In plain terms: the map is accurate, but two field checkpoints and one launch-path proof are still marked pending. That is a ship decision only if leadership accepts those gaps explicitly rather than by silence."

Riders: Ship only with explicit release notes stating that M2 remains conditional on the Wondercraft live artifact/operator addendum, M3 remains conditional on the Texas live retrieval operator window, 5a.2 does not yet demonstrate runnable production-clone parity, and 5a.3's cascade/pricing behavior is implemented but still awaiting operator ratification.

### Quinn-R

Verdict: SHIP-CONDITIONAL

Verbatim response: "The evidence supports shipping only within the amended, explicitly bounded claim set. I do not see a rollback-grade regression signal: 5a.1 replay regression is green, 5a.2 proves control-plane parity on actual substrate, 5a.3 lands the revised economics contract, and 5a.4 closes the invariant audit with all 15 marked preserved. But the unresolved items are not cosmetic. M2 and M3 remain conditional on live/operator evidence, 5a.2 does not prove production-clone launch equivalence, and 5a.3 still lacks operator ratification on the cascade/pricing proposal. That means ship now is defensible only if release scope is constrained to what was actually proven, with those conditions carried forward as release blockers for any broader claim."

Riders: Ship only with the record stating that production-clone parity is unproven, operator ratification for the economics/cascade model is still pending, and the inherited M2/M3 live-evidence conditions remain open. If any release note or stakeholder claim implies full production launch equivalence or final operational signoff, this verdict no longer holds.

### Amelia

Verdict: SHIP-CONDITIONAL

Verbatim response: "Branch reality supports shipment of the migrated foundation, not an unconditional green. 5a.1 replay regression is green, 5a.2 proves actual-substrate control-plane parity, 5a.3 lands the revised economics contract with characterization coverage, and 5a.4 records all 15 invariants as preserved. But the evidence set still carries unresolved external conditions: M2 and M3 remain conditional on pending live/operator windows, 5a.2 does not prove runnable production-clone launch equivalence, and 5a.3's cascade/pricing posture is implemented before operator ratification. That is enough for a conditional ship, not for clean SHIP."

Riders: Ship only if release notes explicitly bound the claim set to control-plane parity plus preserved invariants, while carrying forward the Wondercraft and Texas live-evidence conditions, the M4 `DATABASE_URL`/ledger evidence rider, and the requirement for explicit operator ratification of the 5a.3 cascade/pricing configuration.

### Dr. Quinn

Verdict: SHIP-CONDITIONAL

Verbatim response: "The migration evidence says the core system is stable enough to advance: 5a.1 replay regression is green, 5a.2 proves actual-substrate control-plane parity, 5a.3 establishes the stricter economics contract and reporting baseline, and 5a.4 records all 15 invariants as preserved. The remaining weakness is not a detected break in the migrated runtime, but unresolved proof on the live operating surface. M2 and M3 are still conditional, 5a.2 does not yet prove production clone-launch equivalence, and 5a.3 still depends on operator ratification. That combination argues against a clean SHIP, but it does not justify ROLLBACK."

Riders: Ship only under an explicit gate: close the Wondercraft live artifact/operator addendum, close the Texas live retrieval window, confirm runnable production clone-launch equivalence rather than control-plane parity alone, and obtain operator sign-off on the cascade/pricing configuration. Until then, limit exposure and do not present this as fully unconditional migration completion.

## Accepted Conditional Window

Accepted by the operator on 2026-04-26: treat M5 as `SHIP-CONDITIONAL` with a
7-day named window ending 2026-05-03. The remaining open conditions before
claiming unconditional migration completion are:

1. Wondercraft live artifact/operator addendum closes M2.
2. Texas live retrieval operator window closes M3.
3. ~~A real production clone-launch parity exercise closes the 5a.2 rider.~~ **REFRAMED 2026-04-27 as Slab 6 opener (see Scope Clarification below).**
4. ~~Plausible-Token Substrate Contamination remediation closes when operator runs the live-OpenAI cascade-tier smoke (added 2026-04-26 post-vote — see Verdict-Integrity Annotation below).~~ **RESOLVED 2026-04-27.** Operator ran the live smoke; all 3 cascade-tier pings PASSED (frontier `gpt-5` + mid-tier `gpt-5-mini` + narrow-task `gpt-5-nano`) in 7.00s. Bonus: the smoke test as authored had its own A16 instance (`max_completion_tokens=1` → 400 because GPT-5 reasoning consumed budget); patched in same session to `max_completion_tokens=200`. The A16 prevention pattern caught the defect at first integration attempt — exactly as the counter-pattern was designed to do.

The previously carried `slab-3-m5-dispatch-registry-swap` condition was resolved
on 2026-04-26 by promoting the live registry and frozen snapshot out of
`_status: interim`.

## Scope Clarification (added 2026-04-27 post-vote)

**3-agent party-mode ratification (Winston + Murat + Quinn-R unanimous GREEN-WITH-CONCERNS) reframes condition #3 as a Slab 6 opener, not a Slab 5a closure rider.** The MVP SHIP claim is correspondingly bounded with surgical precision (per Quinn-R Q1).

**Bounded MVP claim language (Murat M2 + Quinn-R Q1 enforced):**

> The MVP shipped at M5 includes: (a) deterministic local M3 harness + control-plane substrate (14 specialists scaffold-conformant; manifest deterministic neck; frozen v42 graph artifacts; dispatch registry promoted to production; HIL gate machinery + resume_api per FR34); (b) cost-engineering foundation (5a.3); (c) replay regression suite (5a.1); (d) head-to-head control-plane parity (5a.2 — verified against synthetic baselines, not live trials per FR51/FR52 PARTIAL traceability designations); (e) 15-invariant audit matrix (5a.4 — all 15 PRESERVED at internal-shape level); (f) honest registration shim at `app/marcus/cli/trial.py` (production_clone_launch_evidence=false; operator can register trials offline); (g) post-vote substrate remediation per A15 (Plausible-Token Substrate Contamination) and A16 (Composition-vs-Component Audit Gap) anti-patterns. The MVP does NOT include: live production-graph runner (composition layer that turns substrate into a runnable trial); deferred to Slab 6 opener `migration-6-1-production-graph-runner.md` per 2026-04-27 party-mode reframe.

**Mischaracterization at vote time (Winston W1):** the original 6-agent SHIP-CONDITIONAL vote on 2026-04-26 named condition #3 as "5a.2 production clone-launch equivalence — control-plane parity proven; runnable launch-path proof still owed." Nobody at the vote understood "production-clone-launch" to mean "we need to build new orchestration code"; everyone interpreted it as "we need a CLI launcher to invoke an existing production graph." Codex's Phase A investigation (`_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-27.md`) on 2026-04-27 was the first time anyone characterized the gap precisely: 20-40 hours of new orchestration integration across 6 missing surfaces (manifest compiler real-handler resolution; invokable graph composition; HIL gate pause/resume runtime; LangSmith trace scoping; production TrialEnvelope schema; trial lifecycle persistence). That gap was not "implement a launcher"; it was "build the composition layer that connects all the substrate components into a runnable production graph."

**Verdict-shape integrity (Winston W2 + Quinn-R Q3):** had the original 6-agent panel known Codex's 20-40h estimate, the SHIP-CONDITIONAL vote would not have flipped to RED — it would have flipped to **SHIP for bounded-MVP scope + Slab 6 opener filed for production-graph-runner**, which is exactly the post-vote reframe Option E ratifies. The verdict's substantive content survives reframing.

**FR51/FR52 PARTIAL findings honored (Murat M1):** the 2 PARTIAL FR-trace entries (FR51 replay byte-for-byte; FR52 head-to-head parity) are correctly scoped to the bounded MVP claim above — both are verified against synthetic baselines, not live production trials. Live-trial parity is Slab 6 work per `migration-6-1-production-graph-runner.md` AC-G + AC-H (composition-exercise audit per A16 counter-pattern).

**Pattern-fix discipline (Quinn-R Q3 + A16 filing):** TWO substrate gaps surfaced post-vote in the same week (A15 Plausible-Token Substrate Contamination + production-graph-runner gap), both same defect class — "audit-shape-not-integration." Anti-pattern A16 (Composition-vs-Component Audit Gap) is filed under "Post-Cycle Harvest" subheading at `docs/dev-guide/specialist-anti-patterns.md` to address the deeper structural defect. A16 counter-pattern: substrate audits MUST include at least one integration-exercise AC alongside per-component invariant checks. Future M-gate audits gain a "Composition-Exercise Audit" required dimension (alongside the "Referent-Validity Audit" added per A15).

**Resolution:** verdict promotes from SHIP-CONDITIONAL to **SHIP for bounded-MVP scope** per the language above. Conditions #1, #2, #4 remain operator-presence work (M2 ceremony + M3 ceremony + live-OpenAI smoke; ~30 min total) to close via existing M5 condition closure paths. Condition #3 is closed AS-A-CONDITION via reframe to Slab 6 opener; the underlying production-graph-runner work is now scoped, planned, and queued at `migration-6-1-production-graph-runner.md` with full bmad-create-story discipline + party-mode green-light + no time pressure + halt-and-adapt budget built in.

**3-agent ratification record (2026-04-27):**
- 🏗 Winston: GREEN-WITH-CONCERNS — Option E proceeds conditional on (a) verdict-record amendment naming the mischaracterization, (b) Slab 6 opener filed before SHIP promotion lands, (c) deferred-inventory entry preserved with Codex report cited.
- 🧪 Murat: GREEN-WITH-CONCERNS — Option E proceeds conditional on (a) MVP claim language bounded with surgical precision, (b) Slab 6 opener names production-graph-runner as first deliverable + cites Codex investigation by path + references 20-40h estimate, (c) FR51/FR52 PARTIAL designations honored explicitly.
- 🔍 Quinn-R: GREEN-WITH-CONCERNS — Option E proceeds conditional on (a) bounded-MVP claim language reviewed for precision, (b) Slab 6 opener filed before SHIP promotion lands, (c) A15 expansion / A16 filing for composition-verification defect class **before next slab opens** (without iii flips to YELLOW).

All three rider sets are honored in this clarification + the A16 filing + the Slab 6 opener spec. Verdict promotion proceeds under the bounded-MVP claim language above.

## Verdict-Integrity Annotation (added 2026-04-26 post-vote)

The 6-agent SHIP-CONDITIONAL vote above was reached without anyone surfacing
the **Plausible-Token Substrate Contamination** defect (see anti-pattern
catalog A15 + condition #4 in `_bmad-output/upstream-state.md`). The cost-
engineering substrate was carrying fictitious OpenAI model identifiers across
~25 production-code surfaces; the 15-invariant audit matrix passed because it
audited *internal shape*, not *external referent validity*; no test ever
called OpenAI to verify the IDs were real.

Per Mary's party-mode position (2026-04-26 round 1), the verdict *shape*
(SHIP-CONDITIONAL) is unchanged by this discovery — a properly-informed vote
would still have produced SHIP-CONDITIONAL with the model-ID remediation
filed *as the named condition*. Per Winston's position, the *evidentiary
base* of the original vote was misleading and that fact must be recorded
explicitly so future audits do not treat the original vote as self-validating.

**Resolution:** the verdict stands as SHIP-CONDITIONAL. Condition #4 was
added to capture the post-vote discovery + the executed remediation. No
re-vote is required (Mary's read prevails on verdict shape; Winston's
concern on evidentiary integrity is honored by this annotation).

A **Referent-Validity Audit** step is added to the next gate-process
checklist: any string in shipped config naming an external provider's
resource (model ID, capability name, endpoint slug) must be verified
against a vendored catalog snapshot before any milestone vote.

## Verdict-Integrity Annotation #2 (added 2026-04-27 post-Slab-6.1-strict-AC-HALT)

A second substrate-gap finding emerged 2026-04-27 during Codex's Slab 6.1 strict-AC implementation attempt. After bmad-code-review caught the Slab 6.1 first-attempt's compose-without-invoke gap (logged as A16 instance #4), operator authorized Option 1 (strict-AC: real graph execution + checkpoint/resume + trace binding). Codex's strict-AC implementation HALTED honestly upon discovering the substrate doesn't actually admit composition: (a) every specialist's 9-node scaffold has its OWN internal `gate_decision` interrupt that fires before production-level G1; (b) the scaffold's two-phase shape (`make_chat_model` in `_plan`; `_act` consumes resolution trail) doesn't map to "single LangGraph node executes specialist work"; (c) shared `RunState.cache_state.cache_prefix` carrier is OVERWRITTEN per-specialist, not accumulated as production envelope; downstream specialists fail (e.g., `CdDirectiveParseError`) because upstream specialist output isn't visible in the carrier they expect.

This finding revealed that the M5 SHIP-CONDITIONAL vote (and the bounded-MVP SHIP reframe) implicitly assumed composition was an implementation-distance away. It wasn't. The substrate gap was a 5th pattern instance + the precipitating instance for **A17 — Substrate Designed for Isolation, Composition Assumed** (filed under Post-Cycle Harvest at `docs/dev-guide/specialist-anti-patterns.md` per Mary harvest-gate authority). Distinct defect class from A16: A16 is "we didn't audit composition"; A17 is "the substrate doesn't admit composition." A17 counter-pattern: every multi-component contract must declare a *composition mode* alongside its isolated mode at design time, with at least one composition fixture before the contract freezes.

Companion process anti-pattern **P3 — Composition-Shape Vote Without End-to-End Exercise** also filed (NEW "Process Anti-Patterns" subheading). M5 voted SHIP-CONDITIONAL on a composition assumption never exercised. P3 counter-discipline: before any composition-shape MVP/SHIP-CONDITIONAL vote, run ONE real upstream→downstream pair through the proposed substrate end-to-end. Operationalized as **Composition Smoke gate** added to slab-opener template (Quinn-R Q3 ratification).

5-agent party-mode round 2026-04-27 (Winston + Murat + Amelia + Quinn-R + Mary) ratified the substrate decision: Path A-prime (production envelope state-key alongside `cache_prefix`; specialists unchanged; dispatch adapter at runner layer marshals state). Scope-split to **Slab 6.0 (substrate)** + **Slab 6.1 (runner consumes substrate)**. Slab 6.0 opener filed at `_bmad-output/implementation-artifacts/migration-6-0-production-envelope-substrate.md` (~8pt; dual-gate per substrate_shape + invariant_preservation).

**Resolution:** the verdict still stands as bounded-MVP SHIP per the 2026-04-27 first reframe. Condition #3 in `_bmad-output/upstream-state.md` updated to point at Slab 6.0 + 6.1 sequence (was: "REFRAMED-AS-SLAB-6-OPENER"; becomes: "REFRAMED-AS-SLAB-6.0-SUBSTRATE-+-SLAB-6.1-RUNNER"). No re-vote on bounded-MVP scope is required — Mary's harvest-gate framing holds: the verdict's substantive content survives reframing because the substrate gap was never in the bounded-MVP scope. Substantive product capability (real production-graph execution) is now a 2-story sequence in Slab 6 rather than the originally-scoped single Slab 6.1 story.

Five A16 instances + 1 A17 instance + 1 P3 instance discovered in 2 days (A15 model IDs, M2 Wondercraft, M3 Scite, Slab 6.1 first attempt, Slab 6.1 strict-AC halt → A17, M5 process gap → P3). The pattern's persistence demonstrates the discipline (bmad-code-review + party-mode substrate-aware adaptation + halt-and-surface) is functioning as designed. Each finding caught at the cheapest possible moment relative to ship.
