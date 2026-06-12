# SCP 2026-06-11 — Trial-3 Segment Data-Plane Fix Arc (Option 2, operator-ratified)

**Status:** RATIFIED — party-mode Round 1 (Winston/Amelia/Murat/John, 4 independent subagent voices) + operator rulings, 2026-06-11.
**Trigger:** Trial-3 attempt-4 (`50b7d353`) reached G2C with 3-of-6 specialist contributions being quality theater (Gary fixture slides via silent fallback; Vera PROCEED over fixture; Quinn-R approval of placeholder slides it never received). Operator overrode weed-clearing posture: *"fix 'everything' up to and including the point of failure with Gary... Gary's issue is not a 'nit'!"*
**Posture (binding):** fix→fresh-E2E-launch cycles. After each major remediation, a NEW trial run from scratch (operator 2026-06-11: prefers an E2E run attempt after each major remediation). The trial is the campaign, not the UUID (John).

## Gap census (G0→G2C, attempt-4 evidence)

| Gap | Mechanism | Evidence |
|---|---|---|
| A | Envelope "first-contribution-wins" per-specialist keying skips multi-node specialists | irene_pass1 ran §04A only; §05 (Pass-1 fidelity) + §05B (cluster plan) silently skipped. quinn_r has 5 manifest nodes, vera 3, enrique 3. Walkers at production_runner.py ~1063/~1327; duplicate-guard in dispatch_adapter.invoke_specialist. Fifth A23/P5 instance. |
| B | §06/§6.2/§6.3/§06B compile to orchestration no-ops | compiler.py:181-193 `_orchestration_node` returns {}. Lesson-plan→slide-briefs transform does not exist. |
| C | Gary silent fixture fallback | gamma_dispatch.py:40-41 returns fixture_receipt.json when directive_path/export_dir missing. Production walk emitted placeholder slides; real path (GammaClient.generate_deck → PNG) never invoked. Third silent-fallback strike in arc (Texas cwd #2, exit-10 #3). |
| D | Manifest dependency input_keys ≠ consumer payload vocabulary | Node 7.5 declares `upstream_output: gary`; quinn_r reads `payload["slides"]`. No lockstep. Includes canonical-vs-alias id duality (quinn_r vs quinn-r) that cost a live crash 2026-06-11. |

## Unanimous design rulings (4-of-4)

1. **Per-node envelope keying.** `node_id` joins SpecialistContribution (nullable for legacy compat — Amelia); skip-guard and duplicate-guard become (canonical_id, node_id)-aware IN THE SAME COMMIT; `schema_version` added to envelope (Murat: last unversioned migration ever); same-node retry overwrites with attempt provenance; `superseded_by` audit pointers (Winston). Canonical ids stored; ALL comparisons through SPECIALIST_ALIASES.
2. **Fixture is a mode, never a fallback.** Missing input → typed raise, always. Fixture mode only via explicit injection test code sets and production_runner cannot reach. Platform-wide policy (Murat): no code path may infer test mode from absent paths/env/files; static CI grep ratchet for fixture-return branches in production modules.
3. **Provenance marking.** Artifacts carry `provenance: real | fixture`; ProductionEnvelope writer REJECTS fixture provenance unless run is flagged fixture-run; decision cards display per-contribution provenance; gates assert provenance==real.
4. **Contract lockstep.** Per-specialist `CONSUMED_PAYLOAD_KEYS`; manifest-loading contract test asserting three-way agreement (producer write keys / manifest input_keys / consumer read vocabulary); compile-time validation per Winston as the durable home. Murat: this is the meta-ratchet; lands FIRST.
5. **G2C decision card of `50b7d353` is VOID** — annotate with invalidation record citing the three void contributions; preserve envelope frozen on disk (475df528 precedent). Quinn-R's approval of content it never received additionally flags quinn_r absence-handling as untested.
6. **Tier-2 pack governance:** manifest dependency-vocabulary corrections + new §06→gary edges are structural data-plane edits post-tracked-trial under frozen-at-ship → **v4.2 → v4.3** per pipeline-manifest-regime; v4.2 stays frozen for audit. Consensus = this round (Winston proposed; no objection; operator ratified arc).

## Operator rulings

- **Fork 1 (trial disposition): RELAUNCH.** After remediation+testing of everything up to the failure point, run a fresh E2E trial from scratch (attempt-5 = Trial-3 fix→advance cycle 2). `50b7d353` frozen as before-evidence; G2C card annotated void.
- **Fork 2 (builder home): synthesis** — pure-function builder core in `app/marcus/orchestrator/package_builders.py` (Amelia: testable against the REAL irene_pass1 lesson plan + cd directive lifted from 50b7d353's envelope) invoked from REAL compiled node handlers for §06/§6.2/§6.3/§06B (Winston: manifest tells the truth; pre_gate_marcus precedent). Relaunch ruling dissolved the mid-trial topology-risk objection; both voices' conditions met.
- Spend unconstrained; racing to production-grade. Live-API test tier inverted per Murat (live at gate-crossings + nightly; cassettes per-commit, re-recorded weekly; skip-budget 0 at gate boundaries).

## Story spine (sequencing: silencers and detectors before features — Murat/John)

| Story | Content | Key tests-first |
|---|---|---|
| **S0** (ships first) | Gary fail-loud (delete silent fallback; explicit `allow_fixture` opt-in unreachable from runner) + same-day grep sweep converting other silent fallbacks in dispatch path to hard errors (conversions only, no new implementations) | RED `test_missing_directive_raises_not_fixture`; `test_fixture_requires_explicit_optin` |
| **S1** | Contract regime: CONSUMED_PAYLOAD_KEYS (quinn_r + gary first, roster incremental), manifest contract lockstep test (Ratchet-D), manifest vocabulary corrections + §06→gary dependency edges under **v4.3 bump** (read pipeline-manifest-regime at T1) | Ratchet-D red→green; alias-form case |
| **S2** | Envelope v2 per-node keying + schema_version + retry semantics + summary-writer/`get_contribution` call-site sweep | Amelia's 3 ratchets (legacy round-trip vs real 50b7d353 JSON; multi-node distinct contributions; per-node skip-guard); Murat's golden single-node + retry-attempt pins |
| **S3** | Package builders: pure functions + compiled handlers for §06/§6.2/§6.3/§06B; §06 output = first-class envelope contribution | Ratchet-B vs REAL trial lesson plan; builder-output ⊆ gary CONSUMED_PAYLOAD_KEYS |
| **S4** | Gary real Gamma path: input threading → generate_gamma_variants → PNG export; provenance field + envelope-writer rejection + gate provenance assertions | mocked-client threading test; operator-gated live micro-deck smoke (sandbox-AC discipline) |
| **S5** | Acceptance: fresh launch Trial-3 cycle-2 (attempt-5) G0→G2C. Owns the NEGATIVE test (broken brief → gate FAILS) per John — not Gary's story. | John's 6 success criteria below |
| **R** (parallel, 1h timebox) | Read-only recon: catalog fixture/fallback patterns in downstream specialists (irene §08, enrique/elevenlabs §11-12, wanda, kira, compositor §14) so cycle-3's failure point is known before spend. NO fixes. Answers operator's "unless we have dozens of such failures ahead." | n/a (report artifact) |

**Dependency spine: S0 ∥ S1 → S2 → S3 → S4 → S5.**

## S5 acceptance criteria (cycle-close; authorizes G2C→G3)

1. All three Irene Pass-1 artifacts on disk, contract-shaped (lesson plan + Pass-1 fidelity packet + cluster plan).
2. §06 emits real slide-brief packages with traceable lesson-plan provenance.
3. Gary slides are real Gamma output: generation ID logged, content derived from the Tejal lesson plan, zero fixture markers in the artifact tree.
4. Vera's verdict cites the artifact (hash/path) it judged; Quinn-R demonstrably received what it approved.
5. Negative test fired once; gate FAILED as designed.
6. Operator eyeballs slides at the G2C pause and says go.

**Explicit OUT (scope guard):** audio (§11-12), compositor (§14), Epic 15, Marcus-interactive, slide aesthetics. Advance-to-next-failure-point is the method.

---
*Party-mode record: 4 independent subagent voices 2026-06-11; full responses in session transcript. Orchestrator: Claude (consultant session). Block-mode trigger paths touched throughout — pipeline-manifest-regime.md read at T1 per story, no exceptions.*
