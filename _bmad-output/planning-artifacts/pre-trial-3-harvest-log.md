---
title: Pre-Trial-3 Cleanup Harvest Log
authoredAt: 2026-05-07
purpose: Capture session-by-session harvest items (new anti-patterns, deferred entries, ADR candidates, scope discoveries) so cross-session learnings don't leak. Rolled up at S6 close into permanent registers (specialist-anti-patterns.md, deferred-inventory.md, ADRs).
governance: Mary AM-6 amendment to pre-Trial-3 cleanup plan, ratified pre-S1 party-mode review 2026-05-07.
---

# Pre-Trial-3 Cleanup Harvest Log

Each session's post-review captures harvest items below. S6 close: distribute entries into permanent registers (anti-pattern catalog / deferred-inventory / ADRs / governance JSON) and mark this file historical-archive.

---

## Pre-S1 review harvest (2026-05-07)

Items surfaced during the 4-agent pre-S1 review that should be remembered (not lost between sessions):

1. **(Mary)** Pattern signal: when "renumber" appears in a remediation spec, ALWAYS read the actual file — renumbering rarely captures the full structural defect. Surfaced in P0-4 anti-pattern dedup (zombie heading + zombie placeholders existed beyond the bare numbering issue). **Filing target:** new harvest candidate for `specialist-anti-patterns.md` at S6 — "P5. Remediation specs that say 'renumber' without reading actual file state."

2. **(Amelia)** Discovery: legacy `marcus/` is NOT a shim — it's a partial migration. `app/marcus/lesson_plan/` and `app/marcus/intake/` do not exist; the lesson-planner / 4A foundation lives only in legacy `marcus/`. **Filing target:** post-S2 (after collapse closes), capture the migration-completeness anti-pattern: "shim packages should EITHER fully shadow legacy OR be explicitly partial with sub-package presence-check." Possible A21 / D14 Slab-7 architectural decision append.

3. **(Murat)** Discovery: `state/config/run-constants.yaml` does NOT exist at top level — confirmed during pre-S1 verification. v4.2 §04.55 lock semantics may expect a per-run-only file or a top-level template. **Filing target:** P1-25 spike already names this; resolution at S5 should produce a definitive answer. If absent-by-design, document the convention in PP-3c (S1) + Composition Spec §10 (S5).

4. **(Murat)** Discovery: `scripts/health/` directory does NOT exist; the real preflight-check substrate lives at `skills/pre-flight-check/scripts/preflight_runner.py` + `scripts/utilities/app_session_readiness.py` + `scripts/heartbeat_check.mjs` + `scripts/smoke_*.mjs`. The original cleanup plan referenced a phantom path. **Filing target:** PP-3b body cites real paths; harvest into Composition Spec §10 (S5) as "preflight surface inventory."

5. **(Paige)** Discovery: PP-2 disposition (v4.2 Marcus-module column legacy-frozen vs runtime-path-replace) is a load-bearing precondition for S4 v5 authoring. Originally framed as a P1 item; surfaced as needing pre-S4 resolution. **Filing target:** mid-S1 PP-2 disposition vote captures the policy; no permanent-register filing needed.

6. **(Mary)** Pattern signal: 11+ governance gates risks review fatigue. Asymmetric weighting (lightweight pre-review ~15 min / 2-3 voices; heavier post-review ~30 min / 4 voices) protects party-mode capacity without compromising operator's mandate. **Filing target:** governance pattern; potential CLAUDE.md amendment at S5 if proven over 6 sessions.

---

## Post-S1 review harvest (2026-05-07)

Items surfaced during S1 implementation + post-S1 4-agent review (Paige + Amelia + Murat + Mary, all GO/GO-WITH-AMENDMENTS):

1. **(Mary)** Hybrid-registry positive-pattern: when a registry contract test asserts specific keys + structure, EXTEND with a sibling block (e.g., `personas:` block alongside `specialists:`) rather than rewriting in place. Preserves contract green-state; adds new view; allows incremental migration. **Filing target:** new positive-pattern entry at S6 (likely `specialist-anti-patterns.md` §"Positive Patterns" or new doc shape). Worth A21 / Q1 framing as the inverse of A-tier anti-patterns.

2. **(Mary)** Dissolved-specialist replacement pattern (Audra→Enrique): when a specialist persona is dissolved + replaced, the API skill registry entry STAYS (preserves binding contract); the persona-name entry CHANGES + dissolved-persona moves to a `dissolved:` block with archive-pending note. Documented in 2 places today (Marcus registry + this harvest log); worth filing as canonical replacement-pattern at S6 close.

3. **(Mary)** PP-2 process-pattern: frozen-historical-anchor preservation > rewrite-in-place. When operator declares a doc "legacy-frozen authority" for a mapping/comparison axis, the disposition is BANNER + DEFER PATH-REWRITE TO NEXT-VERSION, not in-place mutation. 3/3 reviewer unanimity validated this. **Filing target:** S6 governance amendment to CLAUDE.md or composition-spec; complement to deferred-inventory governance.

4. **(Paige meta-signal)** S1 implementation harvested ZERO new substrate anti-patterns despite 12 P0 items + 6 regression-fixes. This is itself a signal — mature-substrate-cleanup has a different harvest profile than slab-close (slab-close routinely yields 1-3 new A-entries; cleanup yields process-patterns instead). **Filing target:** capture in S6 retrospective as observed pattern; potential CLAUDE.md cleanup-session governance amendment.

5. **(Murat AM-13/AM-14/AM-15)** S2 prep items captured in pre-S2 review queue (filed as queued-for-S2-spec amendments, NOT permanent harvest):
   - AM-13: S2 spec must include AC for refactoring `tests/integration/marcus/test_marcus_import_linter_contract.py::test_dispatch_contract_shim_re_export_identity` from `is`-identity assertion to legacy-package-absence assertion
   - AM-14: S2 spec must include AC for scrubbing `marcus.*` aliases from `pyproject.toml::tool.importlinter` contracts in lockstep
   - AM-15: post-S2 measurement target ~46 failures (48 - 2 Cat-6 marcus adhoc-facade entries that S2 collapse closes); deviation > ±2 triggers investigation

6. **(Mary AM-B)** S2 close-batch must include grep sweep for `marcus/` path-strings in `_bmad-output/planning-artifacts/v4.2*.md` (10 min; prevents v5 inheriting broken refs at S4 — Mary cross-session leak audit).

7. **(Operator-driven NEW CYCLE reframe 2026-05-07)** Pre-Trial-3 cleanup work executes Claude-direct (NOT bmad-dev-story Codex hand-off). The NEW CYCLE pattern from Slab 7c marathon was specific to formal bmad-dev-story discipline; cleanup work in multi-session pre-Trial-3 sprint executes Claude-direct to avoid P3 anti-pattern (operator-as-bridge friction). **Filing target:** CLAUDE.md amendment at S5 documenting Claude-direct vs Codex-NEW-CYCLE decision criteria; ratify as governance pattern alongside the multi-slab-retrospective-hygiene trigger (Mary AM-7).

---

## Pre-S2 review harvest (2026-05-07)

Items surfaced during the 3-agent pre-S2 review (Amelia + Winston + Murat):

1. **(Amelia)** Discovery: legacy `marcus/` was a partial-migration NOT a shim — `app/marcus/lesson_plan/` and `app/marcus/intake/` did not exist; canonical content for the Lesson Planner / 4A foundation lived only at top-level `marcus/`. Pre-S1 framing as "collapse direction = legacy → app" was empirically right about file presence but architecturally wrong about intent — see operator clarification below.

2. **(Operator clarification surfaced via question 2026-05-07)** The 30-1 spec ratified an INTERNAL duality (intake ↔ orchestrator) deliberately. **The operator's "marcus duality is a bug" framing referred to a DIFFERENT duality** — the EXTERNAL duality between top-level `marcus/` and `app/marcus/` filed 2026-04-26 as `migration-tech-debt-app-marcus-stub-disposition`. Two distinct dualities; only the external one was being eliminated. Internal duality (single-writer rule + Maya-as-one-voice) preserved verbatim.

3. **(Operator clarification)** The deferred-inventory entry's stated DIRECTION (delete app/marcus/, keep marcus/) was filed 2026-04-26 when app/marcus/ was a thin Slab-1 stub. Reality flipped during Slab 6/7a/7b/7c — substantial Slab 6/7 production runtime landed in app/marcus/. By S2 dispatch (2026-05-07), the right collapse direction was the OPPOSITE of the original entry: keep app/marcus/, delete legacy marcus/. Direction-of-cleanup-can-flip-over-time is itself a harvest pattern. **Filing target:** S6 governance amendment to deferred-inventory protocol — entries should declare a "direction-of-cleanup-may-flip-with-substrate-evolution" caveat.

4. **(Murat AM-16)** Reverse-shim during transition (NOT direct file move) was the right execution discipline for 108-150-test-import surface. Cleaner than "move + sweep + hope nothing breaks." **Filing target:** new positive-pattern entry at S6 — "Cross-namespace migrations: reverse-shim + bulk-rewrite + delete; not move-and-sweep."

---

## Post-S2 review harvest (2026-05-07)

S2 marcus/ namespace collapse completed across 7 phases (commits `343220f`, `accd226`, `195be7c`):

1. **S2 deliverables COMPLETE:**
   - Legacy `marcus/` package DELETED (40 files retired)
   - Canonical content at `app.marcus.*` (lesson_plan/intake/orchestrator/dispatch/facade)
   - 30-1 contracts preserved verbatim (17/17 tests GREEN throughout)
   - Import-linter clean (13 contracts kept; M5 collapse-guard added)
   - Operator's "no more deferrals" mandate honored
   - Deferred-inventory entry `migration-tech-debt-app-marcus-stub-disposition` CLOSED
   - D14 architecture-of-record entry authored

2. **Residual S2 work — 37 net-new test failures (vs post-S1 baseline of 48):**
   - AST-scan / file-IO / shim-era pin tests need long-tail path-string + assertion updates
   - Categories: import-linter contract count (mostly fixed at iter-3); facade-public-surface tests (fixed); composition chain tests (some still scan legacy paths); coverage-manifest / event-type-validator / fit-report-emitter tests (file scans); test_trial_run_e2e (smoke harness scans); test_marcus_orchestrator_write_api / test_lesson_plan_log_atomic_write (need investigation)
   - These are TEST CLEANUP work, not substrate work
   - **Filing target:** new deferred-inventory entry `s2-test-cleanup-residual-37` — defer to S6 housekeeping batch; non-Trial-3-blocking

3. **Mary AM-B v4.2 grep sweep attestation:** v4.2 prose contains 17 `marcus/` path-string references. Per PP-2 unanimous disposition (S1 mid-session 2026-05-07), v4.2 is declared LEGACY-FROZEN authority for the mapping checklist; the §0 banner declares the Marcus-module column as legacy historical anchor. **No v4.2 prose edits required at S2 close** — the banner-disposition pre-existing covers all path-string occurrences. v5 (forthcoming at S4) will use migrated paths exclusively. AM-B closed at S2 close per banner-disposition pre-existing coverage.

4. **Positive patterns harvested at S2:**
   - **Reverse-shim during cross-namespace migration** (Murat AM-16) — copy + reverse-shim + bulk-rewrite-imports + delete; not move-and-sweep. Preserves test-suite-green-state during transition.
   - **Namespace-mirror shim pattern** (`_sys.modules[__name__].__dict__.update({k: v for k, v in _src.__dict__.items() if not k.startswith("__")})` + `__doc__ = _src.__doc__`) re-exports non-`__all__` symbols + canonical docstrings.
   - **30-1 token preservation discipline** — programming-token strings (WriterIdentity Literal values) are PACKAGE-INDEPENDENT; the package can move without touching the strings; the strings ARE the contract.

---

## Pre-S3 / Post-S3 / Pre-S4 / Post-S4 / Pre-S5 / Post-S5 / Pre-S6 / Post-S6 review harvests

_(Empty; populated session-by-session)_

---

## Pre-S3 / Post-S3 / Pre-S4 / Post-S4 / Pre-S5 / Post-S5 / Pre-S6 / Post-S6 review harvests

_(Empty; populated session-by-session)_

---

## S6 close — roll-up distribution (executed 2026-05-08)

Per Mary pre-S6 disposition map, every harvest entry routed to its permanent home. After distribution, this file is marked **HISTORICAL-ARCHIVE**.

### Filing destinations (21 entries → permanent registers)

| Harvest entry | Filing destination | Status |
|---|---|---|
| Pre-S1 #1 (Mary "renumber-without-reading") | `specialist-anti-patterns.md` (folded into A19 scanner-staleness counter-pattern) | LANDED |
| Pre-S1 #2 (Amelia partial-migration discovery) | Architecture-of-record D14 (S2 close) | CLOSED-AT-S2 |
| Pre-S1 #3 (Murat run-constants absent) | architecture doc D-Log spike resolution; deferred-inventory P1-25 | LANDED-AT-S5 |
| Pre-S1 #4 (Murat scripts/health phantom) | v4.2 PP-3 preamble cited real `skills/pre-flight-check/` paths | CLOSED-AT-S1 |
| Pre-S1 #5 (Paige PP-2 disposition) | v4.2 + v5 banner | CLOSED-AT-S1 |
| Pre-S1 #6 (Mary asymmetric weighting) | DEFERRED to next multi-slab retrospective — needs 2-instance evidence base | DEFERRED |
| Post-S1 #1 (hybrid-registry positive-pattern) | Sources-of-truth.md S5 row + Marcus registry comment + S5 commit body | LANDED-AT-S5 |
| Post-S1 #2 (Audra→Enrique replacement-pattern) | v5 banner + sources-of-truth.md + Marcus registry comment | LANDED-AT-S4 |
| Post-S1 #3 (PP-2 frozen-historical-anchor) | DEFERRED to next multi-slab retrospective — needs 2-instance evidence base | DEFERRED |
| Post-S1 #4 (cleanup zero-substrate-harvest signal) | `cross-trial-learnings.md` §B by-methodology — added at S6 | LANDED-AT-S6 |
| Post-S1 #5 (Murat AM-13/14/15) | S2 substrate work + S6 housekeeping-2 land | CLOSED-AT-S6 |
| Post-S1 #6 (Mary AM-B v4.2 grep sweep) | Banner-disposition pre-existing | CLOSED-AT-S2 |
| Post-S1 #7 (Claude-direct vs Codex NEW CYCLE) | CLAUDE.md amendment "Cleanup-arc execution mode" | LANDED-AT-S6 |
| Pre-S2 #1 (Amelia partial-migration repeat) | DEDUP — see Pre-S1 #2 | DEDUP |
| Pre-S2 #2 (operator clarification on duality) | architecture doc D14 entry | LANDED-AT-S2 |
| Pre-S2 #3 (direction-of-cleanup-can-flip) | CLAUDE.md amendment "Direction-of-cleanup-may-flip caveat" | LANDED-AT-S6 |
| Pre-S2 #4 (Murat reverse-shim positive-pattern) | architecture doc D14 + S2 commit body | LANDED-AT-S2 |
| Post-S2 #1 (S2 deliverables COMPLETE) | Historical record only | NO-FILING |
| Post-S2 #2 (37 net-new test failures) | deferred-inventory `s2-test-cleanup-residual-37` (38 items post-correction) | LANDED-AT-S2 |
| Post-S2 #3 (Mary AM-B v4.2 sweep attestation) | Historical record + cited in §10 Decision Log | LANDED-AT-S5 |
| Post-S2 #4 (positive patterns trio) | Sources-of-truth.md + S5 commit body + cross-trial-learnings | LANDED-AT-S5 |

### Roll-up tally

- **17 LANDED** in permanent registers across S1-S6
- **2 DEFERRED** to next multi-slab retrospective (Pre-S1 #6 + Post-S1 #3 lack 2-instance evidence base)
- **1 DEDUP** (Pre-S2 #1)
- **1 NO-FILING** (Post-S2 #1; historical record only)

### Cross-trial-learnings.md addition (Post-S1 #4)

The Paige meta-signal "S1 implementation harvested ZERO new substrate anti-patterns despite 12 P0 items + 6 regression-fixes" is itself a cross-trial-style observation about cleanup-session profiles. Filed at `cross-trial-learnings.md §B by-methodology` as: *"cleanup-session harvest profile differs from slab-close — slab-close routinely yields A-entries; cleanup yields process-patterns + governance amendments."*

### File status: HISTORICAL-ARCHIVE

This file is now historical-archive. Future cleanup arcs author their own harvest log following this precedent. New harvest items land directly in permanent registers per the methodology §7 four-question routing — the harvest log was a transient staging ground for the pre-Trial-3 cleanup arc only.

**S6 close commit:** TBD (this commit + final all-7 ratification commit).
**Cleanup arc duration:** 2026-05-07 → 2026-05-08 (single-day intensive across 6 sessions).
**Cleanup arc total commits:** ~25 commits across S1 (`725f55f`+`11f0bf4`) → S2 (`343220f`→`e48e107`) → S3 (`288c1ed`+`473928c`) → S4 (`a713112`+`ca31f8d`) → S5 (`59f4e12`+`13f1458`+`a3c35c3`) → S6 (`7111633`+TBD).
