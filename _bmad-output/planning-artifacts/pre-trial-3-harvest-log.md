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

## Pre-S2 review harvest (PENDING)

_(Empty until S1 closes and pre-S2 review fires)_

---

## Post-S2 review harvest (PENDING)

_(Empty)_

---

## Pre-S3 / Post-S3 / Pre-S4 / Post-S4 / Pre-S5 / Post-S5 / Pre-S6 / Post-S6 review harvests

_(Empty; populated session-by-session)_

---

## S6 close — roll-up distribution

_(At S6 close, this section enumerates each harvest item's filing destination: anti-pattern catalog entry / deferred-inventory entry / ADR / governance JSON / CLAUDE.md amendment. After distribution, this file is marked historical-archive.)_
