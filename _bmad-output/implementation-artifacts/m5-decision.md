# M5 Decision

Consensus verdict: SHIP-CONDITIONAL

## Evidence Summary

- 5a.1 replay regression is green on the migrated branch substrate.
- 5a.2 proves actual-substrate control-plane parity at Tier 1 = 100% and Tier 2 = 100%, but does not prove production clone-launch equivalence.
- 5a.3 ships the amended cost-engineering foundation: strict economics schema, operator-editable cascade/pricing config, persisted per-trial cost reports, and a migrated-runtime characterization baseline.
- 5a.4 ships the 15-invariant audit matrix and FR64 cycle-complete anti-pattern annotation.
- The 15-invariant audit matrix records all 15 invariants as `PRESERVED`.
- The operator ratified the 5a.3 cascade/pricing configuration on 2026-04-26 after the fixed-roster party-mode vote.

## Inherited Conditional States

- M2: CONDITIONAL-GREEN. Wondercraft live artifact/operator addendum still pending.
- M3: CONDITIONAL-GREEN. Texas live retrieval operator window still pending.
- M4: GREEN-WITH-RIDERS. Positive ledger/Postgres query evidence and inherited repo-wide pytest debt optics remain riders.
- 5a.2 rider: control-plane parity only; production clone-launch equivalence remains unproven.
- slab-3-m5-dispatch-registry-swap: DEFERRED-CONTINUES. The live dispatch registry and frozen `v42` snapshot both remain `_status: interim`, so M5 cannot silently claim that swap is complete.
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
3. A real production clone-launch parity exercise closes the 5a.2 rider.
4. `slab-3-m5-dispatch-registry-swap` is resolved by promoting the live registry
   and frozen snapshot out of `_status: interim`, or else it remains an explicit
   condition on the ship record.
