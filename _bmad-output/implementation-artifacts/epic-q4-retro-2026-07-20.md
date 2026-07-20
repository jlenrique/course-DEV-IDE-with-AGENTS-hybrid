# Epic Q4 Retrospective — Quality Scorecard Live-Wiring (R2): tile / report / HUD

**Date:** 2026-07-20 · **Facilitator:** Amelia (Developer) · **Format:** synthesized (autonomous close per operator direction "proceed with the live-wiring"; the binding Next-Epic deferred-inventory consultation per CLAUDE.md governance #1 is recorded in full below). · **Branch:** `dev/quality-scorecard-epic-2026-07-19`.

## 1. Epic summary + metrics

**3/3 stories done.** Each: fresh block-mode dev-agent RED-first → 3-layer `bmad-code-review` (Blind/Edge/Acceptance) → RED-first remediation → orchestrator re-verify → commit → push. **Preceded by a mandatory 6/6 party green-light** (the Tier-2 block-mode substrate rule), recorded in `epic-q4-party-greenlight-2026-07-20.md` (QLW-1…QLW-16).

| Story | Surface | Commit |
|---|---|---|
| Q4.1 | operator-surface `quality` tile (model + schema + assembler) | `4b96dd44` |
| Q4.2 | `production_runner` → `quality-final-report.md` run-end hook | `234bc98b` |
| Q4.3 | HUD tile render (public.py allowlist + page.py panel + client.py POLL_JS mirror + styles) | `73ab9605` |

- The completed 8-dimension scorecard is now **live-wired into the SPOC runtime**: a per-run standalone report artifact + a compact `quality` tile on the operator-surface + the HUD flight-deck render — the operator sees the honest Band + ranked leaks + trend + scorecard staleness at the accept/reject/edit decision moment.
- **Additive within `operator-surface.v1`** — no schema_version bump, no pack bump (the Epic-35 additive-row precedent held). Block-mode fired on every story; `check_pipeline_manifest_lockstep.py` exit 0 throughout (orthogonal — the shape-pin + parity + HUD tests were the real arbiters).
- **Review findings:** no BLOCKER; **2 HIGH** (Q4.3 client-side renderer parity; Q4.3/Edge top_leaks non-iterable crash), plus a spread of MED/LOW — all reworked RED-first. Q4.2's review was the cleanest (Acceptance zero findings; exactly-once/both-walks structurally enforced).
- **Test posture:** the operator-surface + hook + HUD suites all green (Q4.1 668, Q4.2 524 incl. hook 17, Q4.3 144 HUD); ruff clean, import-linter 18/0, lockstep exit 0 throughout. Q4.1/Q4.2/Q4.3 surfaces stayed disjoint (no cross-contamination).

## 2. What went well

- **The party-greenlight-before-dev gate earned its keep.** This was Tier-2 block-mode substrate; convening the core four + Cora (governance-envelope) + Audra (lockstep) up front produced the binding design (additive-v1, wire-at-the-shared-choke-point, read-committed-doc-not-signals, kill-the-/100-score) that every story then executed without relitigation. No mid-flight substrate surprises forced a kill-switch.
- **Wiring at the shared choke-points dissolved the two-walk gotcha structurally.** Q4.1's tile rides the sole-writer assembler's completion emit (both walks, zero duplication); Q4.2's `.md` is emitted only from the two-and-only-two `status="completed"` sites (terminal-only is structural, not flag-gated). The `production_runner` two-walk trap — the one that has bitten before — never materialized.
- **The clean-leaf + layer discipline held across three new consumers.** `operator_surface.py` still imports nothing from `app.quality` (the assembler does the reading via deferred import); the HUD imports nothing from `app.quality` at all (subprocess `sys.modules` guard + import-linter HUD1). `app/quality` stayed a clean leaf. The scorecard was consumed live without inverting a single layer rule.
- **The build/close vs R2-defer boundary stayed honest.** Every story shipped the offline-testable BUILD (byte-match, fail-soft, two-walk, no-inflation pins) and left the LIVE equality witness explicitly OPEN for the operator R2 trial — the R2 witness entries were UPDATED, never closed.

## 3. Challenges + key lessons (the believed-green catalog, extended to the wiring layer)

The Q1–Q3 honesty family kept generalizing — now into the *wiring and render* layer, where the review caught real defects the dev missed at every single story:

- **The server surface is not the surface the operator watches (Q4.3, HIGH).** The dev built the server-side `_quality_panel` and declared done — but `client.py`'s POLL_JS re-renders the completed brief CLIENT-SIDE from JSON every 3s, and its completed branch dropped the tile, so the tile vanished on the first poll. The story goal ("render the tile in the HUD") was unmet on the live surface. **Lesson:** for any HUD/render story, verify the DYNAMIC/poll render path, not just the cold server load; a "done" that only renders on first paint is not done.
- **Field-level type-defensiveness on the raw producer projection (Q4.3, HIGH/MED).** The HUD reads the RAW `view["proj"]` (not the allowlist-filtered view), so a corrupt `operator-surface.json` (a scalar `top_leaks`, a truthy-string `available`) crashed the whole completed render / rendered a lie. **Lesson:** a consumer must be defensive on every field even when an upstream pydantic model "guarantees" the shape — the on-disk artifact can be corrupt or a future producer can drift; never assume the producer is well-formed.
- **Make the honesty invariant structural, not by-construction (Q4.1).** `available=False` coexisting with a non-null band was possible because the rule lived only in the assembler's discipline; a `model_validator` made it structural at the contract layer. **Lesson (a Q3 echo):** if an honesty invariant matters, enforce it in the type, not by convention — a future writer will otherwise construct the lying combination.
- **Determinism-as-honesty at the emit (Q4.1/Q4.2, QLW-4).** The tile and the `.md` read the COMMITTED scorecard doc, never `app.quality.signals.*` (live env/import-linter/inventory posture) — recomputing at emit would make the surfaced posture flap on ambient state. **Lesson (the Q3.2 lesson applied to wiring):** a persisted/emitted surface reads a stable committed posture, never a volatile live recompute.
- **Atomicity + honest framing on durable artifacts (Q4.2).** The `.md` write was non-atomic (a mid-write die could leave a truncated report reading as complete, feeding the R2 witness) → atomic temp+`os.replace`; and the docstring overstated "rewind-safe = deterministic" (a later rewind reads a grown trend ledger) → softened. **Lesson:** a durable artifact that feeds a witness must be written atomically, and its determinism claims must not overstate what a moving input allows.
- **Toothless-pin vigilance carried to the render layer (Q4.3, Acceptance).** The QLW-9 "never cleaner than a committed red" guarantee was correct in code but unpinned (every test fed band "D"); a regression to a green default would have shipped green. **Lesson (the recurring one):** a correctness guarantee without a pin that REDs its regression is believed-green — pin it at every layer it's claimed.

## 4. ⚖️ BINDING deferred-inventory consultation (Next-Epic-Preparation — CLAUDE.md governance #1)

Reviewed `deferred-inventory.md` + the R2 witness register in `deferred-work.md` against Epic Q4's new substrate (the scorecard is now LIVE-WIRED into the runtime's three operator-facing surfaces). **Governing principle:** the BUILD closes now; the LIVE equality witnesses are operator-gated and stay OPEN until the R2 trial.

| Deferred entry | Q4 relation | Reactivation verdict |
|---|---|---|
| `q1-4b-r2-final-report-projector-witness` (deferred-work.md) | Q4.2 landed the run-end `.md` emit | **UPDATED, not closed** (per Q4.2 AC7): "wiring landed + offline byte-match-proven; the LIVE equality-against-env-truth witness still rides the operator R2 trial." Reactivates at the next R2 operator-steered trial. |
| **`q4-2-r2-hud-quality-tile-witness`** (NEW, filed this epic) | Q4.1 tile + Q4.3 HUD render | **Filed OPEN.** On R2: assert the live tile/HUD Band/leaks/fence equal the independently-computed env truth for the run. Do NOT run a live trial to close it. |
| **`q4-1-report-coverage-gap-underlisting-robustness`** (NEW, filed by Q4.1) | Q4.1 review (Blind) | **Filed OPEN, deferred.** `report.py::leak_coverage_gaps` flags only empty leak lists, not a dimension whose listed leaks are FEWER than its declared `open_leaks` — enforced-away today by the per-dimension `len(leaks)==open_leaks` identity pins, so it is defense-in-depth hardening of the shipped `report.py`, not a live gap. Its own follow-on; NOT scorecard-epic work. |
| Q1–Q3 R2 witnesses (`q1-4a`, `q2-1..3`, `q3-*`-r2) | scored dimensions now live-wired | **Consulted; unchanged.** They ride the same R2 trial; the live-wiring makes that trial able to witness them end-to-end. Not reactivated here. |
| `reading-path-fresh-naive-holdout-pre-trial` (DID Leak-4) | the owed calibration measurement | **Consulted; NOT reactivated.** Independent of live-wiring; Q3.4 reports it OWED and Q4 surfaces that honest read on the operator surface. Its own owed epic. |

**Consultation outcome:** no entry is reactivated *as epic work*. Q4 filed two new operator-gated R2 witnesses + one `report.py` robustness follow-on; all stay OPEN. The live-wiring does not preempt merge-to-master or the fresh-naive-holdout measurement.

## 5. Next steps + action items

**The scorecard is now BUILT end-to-end AND live-wired.** What remains is operator-gated verification and the standing owed items — no further wiring stories are in scope.

**Action items (Q4 additions; the Q1–Q3 set still stands):**
1. **AI-Q4a: For any HUD/render story, verify the DYNAMIC/poll render path (client-side), not just cold server load** — a "done" that renders only on first paint is not done (the Q4.3 client.py HIGH). Owner: dev + review. Status: open.
2. **AI-Q4b: A consumer must be field-level type-defensive on a raw producer projection** — never assume an upstream pydantic model's shape; the on-disk artifact can be corrupt or a future producer can drift (the Q4.3 raw-projection HIGH). Owner: dev + review. Status: open.
3. **AI-Q4c: Enforce honesty invariants structurally (a validator), not by construction** — a future writer will otherwise build the lying combination (the Q4.1 model_validator). Owner: dev. Status: open.
4. **AI-Q4d: A durable artifact that feeds a witness must be written atomically, and determinism claims must not overstate a moving input** (the Q4.2 atomic-write + docstring lessons). Owner: dev + review. Status: open.
5. **(Standing) AI-Q1a…e + AI-Q2a…d + AI-Q3a…d** — the full believed-green catalog (consult-real-FAIL-predicate; isolate-the-pin; reachable-close-path; determinism-as-honesty; declared≠verified-clean; guard-the-authority; toothless-pin vigilance). Status: open.

## 6. Readiness assessment

- **Testing & quality:** ✅ all offline suites green (operator-surface/hook/HUD), ruff + import-linter (18/0), lockstep exit 0; every honesty guarantee pinned RED-under-seeded; the layer rules + clean-leaf held across three new live consumers. **Live E2E honestly DEFERRED to R2** (two witnesses OPEN) — no surface claims live-proven.
- **Deployment/integration:** the scorecard now renders into the operator-facing runtime (report artifact + operator-surface tile + HUD flight deck). The block-mode trigger paths were touched under the regime, additive-within-v1, no pack/schema bump.
- **Branch:** `dev/quality-scorecard-epic-2026-07-19` — Q1+Q2+Q3 (8 dimensions) + Q4 (live-wiring) through `73ab9605`. **Merge-to-master is the operator's call.**
- **Honest residual (carried):** the LIVE equality witnesses are unproven until the operator R2 trial; the `report.py` under-listing robustness is a filed follow-on (enforced-away today); the fresh-naive-holdout measurement remains owed.

**Verdict:** Epic Q4 is complete and solid — the 8-dimension scorecard is now live-wired into the SPOC runtime on all three operator-facing surfaces, additively and honestly, with the layer/clean-leaf discipline intact. The adversarial review caught real wiring defects the dev missed at every story — most importantly the client-side render gap that would have made the tile invisible on the surface the operator actually watches — proving the review layer earns its keep on wiring work too. The build is done; the live equality witnesses and merge-to-master are the operator's next calls.
