---
baseline_commit: 3a93453a
---

# Story Q3.1: Capability-honesty dimension (declared vs produced) + auto-reconciliation

Status: ready-for-dev

<!-- Epic Q3 (Partial + report-only siblings). DISPATCH #1 of Q3 (serial: Q3.1 → Q3.2 → Q3.3 → Q3.4; all touch the machine block + pin registry → serialize by rule). Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. Follows the Q1 engine + the Q2.1/Q2.2/Q2.3 sibling EXEMPLARS + ALL their review learnings + the 4 Q2-retro action items. ⚠️ PHASING-FLAG story — ship scoring + a bounded reconciliation; split the deep trial-scan if it over-balloons. -->

## Story

As **the project quality scorecard**,
I want **a Capability-honesty dimension that reconciles the front-door capability tiers (`bundle_catalog.py`) against produced reality, with its own honesty pin**,
so that **the operator sees an honest read of whether declared capability matches what the system actually produces — and a tier that lags produced reality (the DID Leak-5 pattern) is scored as a coherence gap.**

## Scope fence (read FIRST)

Q3.1 adds ONE new dimension (`capability_honesty`) reusing the Q1 engine + the Q2 sibling pattern. It does **NOT**:

- **Touch DID / cost / coverage / fidelity** (all done) — their numbers + prose + machine blocks are read-only.
- **⛔ EDIT any `bundle_catalog.py` capability TIER.** Tier bumps are **party-gated governance** (CLAUDE.md pack-versioning + the DID Leak-5 entry says so explicitly). Q3.1 SCORES the honesty of the tiers; it NEVER changes a tier (that stays `workbook-capability-tier-honesty-lag`, party-gated). CONSUME `bundle_catalog` read-only.
- **Build a full trial-artifact scanner** (PHASING FLAG). The bounded reconciliation reads the catalog tiers against a small, honest, curated produced-evidence signal; the deep "scan every trial run for produced artifacts" reconciliation is split to a follow-on if it over-balloons (Q2-retro AI-Q2d).
- **Touch Q3.2/Q3.3/Q3.4** — capability_honesty only.
- **Add module-scope `app.*` to `app/quality`** (GL-3); **wire into production_runner's live emit** (E2E rides R2, GL-10).
- Extend the Q1 machinery **only additively**.

## Honest baseline (verified — the assessment must match this)

- **`bundle_catalog.py` tiers:** `CapabilityTier` ∈ {`proven_wired`, `proven_regressed_repairable`, `mechanism_only_never_produced`}; today deck=`proven_wired`, motion=`proven_regressed_repairable`, workbook=`mechanism_only_never_produced`. There is already an honesty-gap guard (every `ComponentName` must have a tier).
- **DID Leak-5 (`workbook-capability-tier-honesty-lag`):** workbook is tiered `mechanism_only_never_produced` DESPITE real workbook MD+DOCX produced (trial `a940c5eb`, LO-verified `8b275e5b`). **The direction is CONSERVATIVE — it UNDERSTATES (fail-safe, greys the bundle), NOT an overclaim.** The honest bump is *proven-on-frozen-lesson* (Tejal P2), NOT blanket `proven_wired` (off-frozen stays an open claim). **VERIFY (not a counted leak):** motion's `proven_regressed_repairable` is likely stale the same way — re-read against live motion output; it is a VERIFY TODO, not a leak.
- **So the capability-honesty leak = the LAG (declared reality lags produced reality), even though fail-safe.** An OVERSTATING tier (claims proven while never produced) would be the worse, believed-green direction — none exist today (the ledger errs conservative).

## Acceptance Criteria

**AC1 — New `## Dimension 5 — Capability-honesty` section + machine-block entry**, mirroring the prior dimensions (why-load-bearing → rubric → assessment table `{level, derivation, signal, evidence_ref, score, max}` → ranked leaks → cadence). Machine block gains a `capability_honesty` dimension with the full field-set. Band+leaks+trend.

**AC2 — Signal readers + the BOUNDED auto-reconciliation** (fail-soft, read-only, clean-leaf). Criteria (signal-vs-judgment partition):
- **CH1 tier↔produced reconciliation (SIGNAL-DERIVED, the leak):** an auto-reconciliation that reads the `bundle_catalog` tiers + a small curated **produced-evidence signal** and flags a mismatch — specifically the DID Leak-5 pattern: **a component tiered `mechanism_only_never_produced` for which a produced artifact demonstrably exists** (workbook, per the recorded evidence). Honest today: workbook tier LAGS produced reality → the reconciliation flags it → **the leak** (a coherence gap; conservative/fail-safe but still a gap). Reachable close-path (if the tier is party-ratified to match reality, the reconciliation reports no mismatch → the criterion can improve — the pin must NOT block the honest upgrade); read-only (never edits the tier). Apply the **CV2/FT2 lesson**: consult the REAL mismatch condition (declared tier vs produced-evidence), not mere tier presence.
- **CH2 no-overstatement (judgment-with-evidence):** no tier claims `proven_wired` while never produced (the worse believed-green direction). Honest today: none overstate (the ledger errs conservative) → strong.
- **PHASING (bounded):** the produced-evidence signal is a small honest curated set (the recorded DID-Leak-5 evidence refs), NOT a full trial-artifact scanner. If a fuller reconciliation is wanted, ship this + a **manual-reconciliation / split TODO** filed to deferred-work. Do NOT let an unverified/unknown signal award a clean level.

**AC3 — The dimension's own honesty pin (GL-6 meta-ratchet REQUIRES it).** Register a `capability_honesty` pin in `_HONESTY_PIN_REGISTRY` + add `capability_honesty` to `_EXPECTED_CANONICAL_DIMENSION_KEYS` + the CH1 reader to `_SIGNAL_DERIVED_READERS`. The reconciliation pin is doc↔code: **the score FAILS if it claims the tiers match produced reality while the reconciliation reports a mismatch** (the epic's honesty-pin — "ties the score to the reconciliation result"). RED-under-seeded (GL-9): claim CH1 clean while the workbook lag exists → RED. Apply the **isolating-pin lesson (Q2.3 FT2):** the pin must isolate "consulted the real reconciliation" from "trusted the raw tier" — vary the produced-evidence axis while holding the tier, so a regression to tier-only can't ship green.

**AC4 — GL-13 leak registration + cross-dimensional integration.** `capability_honesty` `leaks:` list (`{rank, criterion, slug, lane}`; `len == open_leaks`); ≥1 = the tier-lag leak (lane `governance` — capability honesty is a ledger/governance concern). Slug → a FIFTH namespace registry (`## Capability-Honesty Scorecard Leak Registry` / `cap_leak:`), disjoint from the other four (verify all FIVE readers don't cross-count). **Cross-link DID Leak-5** (`workbook-capability-tier-honesty-lag`) — same substrate, distinct slug/namespace, NO double-count. reconcile-by-identity covers capability. `ranked_project_leaks` aggregates all 5 dims; `leak_coverage_gaps` clean.

**AC5 — Mirror + trend + history.** Append a `capability_honesty` snapshot to `scorecard-history.jsonl` (mirror pin); trend baseline; projector NO code change.

**AC6 — Tests (hermetic + real) + honest Band + phasing TODO.** Reconciliation against fixture tiers (a seeded stale tier `mechanism_only_never_produced` + a produced-artifact evidence marker → mismatch flagged) AND the real `bundle_catalog`; the reconciliation pin RED-under-seeded; the isolating pin (Q2.3 FT2 lesson); meta-ratchet green; mirror/arithmetic/leak-identity (5 namespaces)/coverage all green. **Band honesty:** the band_note states the lag is CONSERVATIVE/fail-safe (understates) and that no tier overstates — do not read the Band as either "all capabilities proven" or "the system is broken." **Phasing:** file the split TODO (full trial-artifact-scan auto-reconciliation) + the motion VERIFY to deferred-work. **E2E:** deferred to R2 (GL-10 — file the obligation). DID/cost/coverage/fidelity pins + numbers unchanged.

## Tasks / Subtasks
- [x] **T1 — Readiness.** Re-read the scope fence (esp. ⛔ NEVER edit a tier) + honest baseline + the Q2 sibling exemplars + ALL review learnings (reachable-close-path/read-only; consult-real-predicate CV2/FT2; isolating-pin FT2; band honesty; non-empty/status/schema guards) + the 4 Q2-retro action items + the PHASING flag. Confirm no pipeline-lockstep trigger path edited (`bundle_catalog.py` is read-only).
- [x] **T2 — Signal readers + bounded reconciliation** (AC2): CH1 tier↔produced (read bundle_catalog + curated produced-evidence, flag the lag), CH2 no-overstatement; fail-soft; clean leaf.
- [x] **T3 — Rubric + assessment + machine block** (AC1); honest levels; the tier-lag leak; conservative-direction note.
- [x] **T4 — Honesty pin + registry** (AC3); the reconciliation pin + the isolating pin; RED-under-seeded.
- [x] **T5 — GL-13 leaks + cap_leak registry (5th namespace) + identity + ranked/coverage + DID-Leak-5 cross-link** (AC4).
- [x] **T6 — History mirror** (AC5) + honest band_note + phasing/motion-VERIFY TODOs.
- [x] **T7 — Tests + R2 obligation** (AC6).
- [x] **T8 — Verify.** `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; DID/cost/coverage/fidelity unchanged; ALL prior pins green.

## Dev Notes

### Verified capability seams (GL-15 — reuse read-only, do NOT rebuild or EDIT)
- `app/marcus/lesson_plan/bundle_catalog.py`: `CapabilityTier` Literal (:55), `ComponentName` (`deck`/`motion`/`workbook`), `CAPABILITY_TIERS` registry (MappingProxyType, ~:165), `ComponentCapability` (tier field ~:109), the readiness map (proven_wired→fully_proven / proven_regressed_repairable→partial / mechanism_only_never_produced→not_yet), the existing honesty-gap guard (:156).
- **DID Leak-5 evidence** (from the deferred entry): workbook produced MD+DOCX at trial `a940c5eb`, LO-verified `8b275e5b`, on the FROZEN Tejal P2 lesson → honest tier = *proven-on-frozen-lesson*. Use these as the curated produced-evidence for CH1 (bounded).
- Read `bundle_catalog` via deferred local import or plain data — NO module-scope `app.*` in `app/quality`.

### Follow the Q2 sibling EXEMPLARS + ALL review learnings (do NOT repeat any prior bug)
Q2.1/Q2.2/Q2.3 are the pattern. Apply the accumulated review fixes up front: reachable-close-path + read-only fence/reconciliation reader (CE1); **consult the real reconciliation condition, not mere presence** (CV2/FT2); **isolating pin** (FT2 — vary the produced-evidence axis to prove the reconciliation is consulted, not the raw tier); band honesty (CE band_note); non-empty/status-unavailable/schema guards; anti-drift pin if any constant is mirrored from `bundle_catalog`. Equal-weight scoring kept.

### The PHASING FLAG (Q2-retro AI-Q2d — binding here)
The epic explicitly says: "if full auto-reconciliation over-balloons, ship the scoring + a manual-reconciliation TODO and split the auto-check." Q3.1 ships the SCORING + a BOUNDED reconciliation over the curated produced-evidence (the known DID-Leak-5 pattern). A full trial-artifact-scanning reconciliation is the split TODO — file it, do NOT build it here.

### The 4 Q2-retro action items + the standing Q1 five (BINDING)
Consult-real-fail/reconciliation-predicate; isolate-the-pin; reachable-close-path + read-only; honor-the-phasing-flag; GL-13 registration; reconcile-by-identity (5 namespaces); GL-9; signal-vs-judgment honesty; R2 witness filed.

### Honesty is the bar
The workbook tier LAGS produced reality (understates) — a conservative/fail-safe coherence gap, NOT an overclaim. Say it plainly. Do not overclaim "capabilities honest/proven"; do not editorialize the fail-safe lag into "the system is broken." NEVER edit the tier (party-gated).

### Testing standards
Reuse `tests/quality/`. Hermetic fixture tiers + evidence markers + real `bundle_catalog` reads. No live calls; no `--run-live`.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q3.1] + [#GL-13/GL-15/GL-6/GL-9/GL-10 + the phasing flag] + FR10.
- [Source: docs/dev-guide/quality-scorecard-dimension-authoring.md] — the GL-13 contract.
- [Source: app/marcus/lesson_plan/bundle_catalog.py:55/109/165] — the tier registry (read-only, NEVER edit).
- [Source: deferred-inventory.md `workbook-capability-tier-honesty-lag` (DID Leak-5) + the DID Scorecard Leak Registry] — the cross-linked leak + the produced-evidence refs.
- [Source: q2-1/q2-2/q2-3 stories (done) + their review remediations] — the sibling exemplars + ALL learnings.
- [Source: epic-q2-retro-2026-07-19.md] — the 4 Q2 action items + the phasing-flag guidance.
- [Source: app/quality/{signals,scorecard,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the engine + registry to extend.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, `bmad-dev-story` workflow, RED-first discipline.

### Debug Log References

- `pytest tests/quality/ -q` → **340 passed** (was 301 pre-Q3.1; +39 new/updated).
- `ruff check app/quality/ tests/quality/` → **All checks passed** (fixed E501 in a pin docstring + SIM300 Yoda condition in the anti-drift pin).
- `lint-imports --config pyproject.toml` → **18 kept, 0 broken.**
- `test_app_quality_is_a_clean_leaf` → green (the capability reader reaches `bundle_catalog` via a DEFERRED local import; zero module-scope `app.*`).
- Governance-fence proof: `git diff --stat` on `bundle_catalog.py` / `production_runner.py` / `report.py` / `history.py` → **empty** (all consumed read-only; NO tier edited; projector unchanged).
- RED-under-seeded proofs (demonstrated live, real doc untouched — mutations on deepcopies):
  - **Reconciliation pin**: CH1 claimed `strong` while the reconciliation reports the workbook lag → `machine-block level 'strong' != reader-derived 'weak'` (RED).
  - **Isolating pin** (Q2.3 FT2 lesson): tier HELD `mechanism_only_never_produced`, produced-evidence VARIED → `produced=True` → weak; `produced=False` → strong. A raw-tier-only regression returns weak for both → RED.
- Consumer regressions clean: scorecard CLI (`scripts/utilities/quality_scorecard.py`), `test_run_summary_fence_state.py`, `test_projector_coverage_ratchet_43_10.py` all green.

### Completion Notes List

**capability_honesty (Dimension 5) — declared vs produced, scored READ-ONLY over `bundle_catalog` (GL-15, NO parallel plumbing).** Two criteria (signal-vs-judgment partition):
- **CH1 tier↔produced reconciliation — SIGNAL-DERIVED, weak (the leak).** `capability_tier_reconciliation_signal` reads the REAL `CAPABILITY_TIERS` (deferred import, read-only) against a BOUNDED curated produced-evidence set (`_CURATED_PRODUCED_EVIDENCE` — the recorded DID-Leak-5 evidence: workbook produced MD+DOCX @ `a940c5eb`, LO-verified `8b275e5b`, frozen Tejal P2). Flags the DID-Leak-5 pattern: a component tiered `mechanism_only_never_produced` for which a produced artifact demonstrably exists → `tiers_match_produced_reality=False` → `weak`. **Consults the REAL mismatch condition (declared tier vs produced-evidence), NOT mere tier presence (CV2/FT2).** Close-path reachable + read-only: a party-ratified tier that matches produced reality → coherent → strong (the pin never blocks the honest upgrade; the reader reads the real registry, not a hardcoded verdict). Registered in `_SIGNAL_DERIVED_READERS`; `level_from_signal("capability_tier_reconciliation_on", …)` owns the level.
- **CH2 no-overstatement — JUDGMENT-with-evidence, strong.** The same reconciliation reader reports `overstatement_mismatches` (a component tiered proven_* while curated evidence says NEVER produced — the worse believed-green direction). None today → `no_overstatement=True` → the ledger errs conservative. `level_from_signal` returns None for the CH2 key (no unverified signal awards a clean level).

**Band C (Σ 4/8 → 50/100). Honest band_note:** the lag is CONSERVATIVE/fail-safe (understates → greys the bundle), NOT an overclaim; no tier overstates — the note explicitly says do NOT read C as "all proven" NOR "broken", and that closing it is party-gated (Q3.1 scores it read-only, NEVER edits the tier). Equal-weight kept.

**The reconciliation honesty pin (AC3)** = the doc↔code signal-derived pin: the score FAILS if CH1 claims the tiers match produced reality while the reconciliation reports a mismatch (seen RED). **The isolating pin (AC3/AC6)** varies the produced-evidence axis while holding the tier so a regression to raw-tier-only can't ship green. Anti-drift: `_NEVER_PRODUCED_TIER` / `_PROVEN_TIERS` pinned to `bundle_catalog.CapabilityTier`'s real members.

**GL-13 (AC4):** `capability_honesty.leaks` = `[{rank:1, criterion:CH1, slug:capability-honesty-workbook-tier-lags-produced-reality, lane:governance}]`; `len==open_leaks==1`. A **FIFTH** `## Capability-Honesty Scorecard Leak Registry` / `cap_leak:` namespace, disjoint from did(5)/cost(1)/cov(1)/fid(1) — `test_five_leak_namespaces_are_disjoint_and_dont_cross_count` green. **Cross-links DID Leak-5** (`workbook-capability-tier-honesty-lag`) — SAME substrate, distinct slug/namespace, NOT double-counted. `ranked_project_leaks` now aggregates all 5 dims (9 leaks; the governance leak sorts last); `leak_coverage_gaps` clean.

**Mirror + history (AC5):** appended the `capability_honesty` snapshot to `scorecard-history.jsonl`; trend `baseline`; projector NO code change (`render_scorecard_final_report` picks up the 5th dimension automatically). GL-6 meta-ratchet now covers `capability_honesty` (`_HONESTY_PIN_REGISTRY` + `_EXPECTED_CANONICAL_DIMENSION_KEYS`).

**PHASING FLAG honored (AC2/AC6):** shipped SCORING + a BOUNDED reconciliation over the curated evidence; filed the split TODO (`q3-1-full-trial-artifact-scan-reconciliation`), the motion-VERIFY (`q3-1-motion-capability-tier-verify`, NOT a counted leak), and the R2 witness (`q3-1-r2-capability-honesty-witness`) to `deferred-work.md`.

**Prior dimensions UNCHANGED** (read-only): DID 65/B-, cost 62/B-, coverage 58/C, fidelity 58/C — numbers, prose, machine blocks untouched. All prior pins green (signal-derived-levels, all 4 leak-count + slug-identity, arithmetic, mirror, evidence-gated-upgrade, trend-computed, meta-ratchet). Sibling cross-dimensional TEST assertions that snapshot the total dimension/leak count (canonical-keys, the 4 aggregation tests) updated 4→5 dims / 8→9 leaks — no production number touched.

**Honesty judgment call:** CH1 is scored `weak` (not `partial`) even though the lag is fail-safe — mirroring the DID-C3 / cost-CE1 / coverage-CV1 / fidelity-FT1 "mechanism-exists-but-off/incoherent → weak" convention. The conservative DIRECTION is carried by the band_note + the CH1 caveat, not by softening the score; the reconciliation reports a genuine coherence gap, so `weak` is honest.

**Code-review remediation (3-layer review; Edge+Blind over-claim-clean theme; RED-first, no BLOCKER/HIGH):**
- **FIX-1 [MED] `shelf` tier handled.** `CapabilityTier` is a FOUR-value enum; `shelf` ("named but not built") ALSO asserts never-produced. Replaced the single `_NEVER_PRODUCED_TIER` with a SET `_NEVER_PRODUCED_TIERS = {mechanism_only_never_produced, shelf}`; the lag check is `tier in _NEVER_PRODUCED_TIERS`. RED proof: `shelf`+produced → lag flagged → weak (was false-clean strong). Governance fence held — did NOT edit the enum, only the read-only mirror.
- **FIX-2 [MED] enum-COVERAGE anti-drift pin.** `test_capability_mirrored_tier_constants_match_source` now asserts `members - _PROVEN_TIERS - _NEVER_PRODUCED_TIERS == set()` (every `CapabilityTier` member classified) — the meta-fix that would have caught FIX-1. RED proof: with `shelf` removed from the mirror, the pin REDs naming `['shelf']` unclassified. Guarantees a future tier reds the test (GROWTH direction).
- **FIX-3 [MED] nothing-reconciled → unavailable (the unifying over-claim-clean fix).** Added `reconciled_count` (components where tier is a readable str AND `produced` is a real bool); `reconciled_count == 0` → `status='unavailable'` (never coherent/strong). Non-bool `produced` is SURFACED in `unreconciled`, not dropped. Flipped `test_reconciliation_unknown_tier_is_not_reconciled` to assert unavailable. RED proof (4 cases): empty-evidence · all-None tiers · absent/typo'd component · non-bool produced → each `unavailable` (was `ok`/strong).
- **FIX-4 [LOW] CH2 vacuity named.** Reworded CH2's `signal.fact` (machine block + §5.6 cell): the bounded curated evidence CANNOT positively detect overstatement (no never-produced-but-proven marker exists in it) — `strong` is a human judgment that the live ledger errs conservative, not a mechanically-checked absence. Level unchanged (judgment-with-evidence strong).
- **FIX-5 [NIT] doc citation softened.** §5.6 open-leak detail cites `CAPABILITY_TIERS["workbook"].tier` symbol (no line-number range) — resilient to governance-fenced-file drift.

Post-remediation: **346 tests pass** (+6 RED tests), ruff clean, import-linter 18/0, governance fence intact (bundle_catalog + production_runner git-clean), prior 4 dims + all prior pins green (meta-ratchet, mirror, arithmetic, 5-namespace leak-identity, coverage, clean-leaf).

### File List

- `app/quality/signals.py` (modified) — capability-honesty reader section (`capability_tier_reconciliation_signal`, `_read_capability_tiers`, `capability_leak_count_signal`, `_CURATED_PRODUCED_EVIDENCE`, `_NEVER_PRODUCED_TIER`/`_PROVEN_TIERS`/`_CAPABILITY_LEAK_LINE_RE`) + `_level_ch_reconciliation` + `level_from_signal` registration + `MappingProxyType` import.
- `app/quality/scorecard.py` (modified) — `_CAPABILITY_KEY` + added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`.
- `docs/quality/project-quality-scorecard.md` (modified) — new `## Dimension 5 — Capability-honesty` prose section (§5.0/§5.5/§5.6/cadence) + `capability_honesty` machine-block entry.
- `docs/quality/scorecard-history.jsonl` (modified) — appended the `capability_honesty` baseline snapshot.
- `_bmad-output/planning-artifacts/deferred-inventory.md` (modified) — new `## Capability-Honesty Scorecard Leak Registry` (FIFTH `cap_leak:` namespace) with the tier-lag leak + DID-Leak-5 cross-link.
- `_bmad-output/implementation-artifacts/deferred-work.md` (modified) — filed the split TODO + motion-VERIFY + R2 capability-honesty witness.
- `tests/quality/test_capability_honesty_dimension.py` (new) — the reconciliation reader against fixtures + real bundle_catalog, isolating axis, close-path/read-only, level totals, leak-count, GL-13 interleave, projector-picks-it-up.
- `tests/quality/test_scorecard_honesty_pins.py` (modified) — capability pins (reconciliation-claim + RED proofs, isolating pin, leak-count + slug-identity, five-namespace disjointness, DID-Leak-5 cross-link, anti-drift, arithmetic) + registry/reader/import wiring.
- `tests/quality/test_scorecard_reader.py` (modified) — canonical-keys assertion 4→5 dims.
- `tests/quality/test_scorecard_final_report.py` (modified) — real-repo total-leak assertion 8→9.
- `tests/quality/test_cost_efficiency_dimension.py` · `tests/quality/test_coverage_honesty_dimension.py` · `tests/quality/test_fidelity_trust_dimension.py` (modified) — cross-dimensional aggregation set assertions updated to include the 5th dimension (`len(ranked)` 8→9).
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (no net change) — left at `ready-for-dev` per the launching agent's explicit instruction (Status NOT advanced to review; do NOT commit).
