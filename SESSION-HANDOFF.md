# Session close 2026-07-20 — PROJECT QUALITY SCORECARD **DEV COMPLETE** (Q3.4 + Q3 close + Epic Q4 live-wiring) → **MERGED TO MASTER**

**Final class:** S (substrate: `app/quality/`, `operator_surface.py` + assembler + schema, `production_runner.py`, `app/hud/**`, tests). **Branch:** `dev/quality-scorecard-epic-2026-07-19` (HEAD `9cbf2512`, pushed). **MERGED TO MASTER** `656e6241` (`--no-ff`, pushed `origin/master`). **Opened as:** continuation of the 2026-07-19 planning close (which deferred dev to a fresh session); operator directed autonomous DEV of the scorecard, then "merge to master" + this WRAPUP.

## What was completed

- **The 8-dimension Project Quality Scorecard is BUILT end-to-end and LIVE-WIRED into the SPOC runtime, and the whole arc is MERGED TO MASTER.**
- **Epic Q3 closed (4 report/score dimensions):** Q3.1 capability-honesty (C/50), Q3.2 tracker-coherence (D/38, GL-7 fully-computed), Q3.3 lane-discipline (B/75, GL-16 shipped-dep), Q3.4 calibration (D/25, REPORT-ONLY — the 8th/final dimension). Q3.4 dev + 3-layer review this session; the review hardened the SIGNATURE never-imply-measured pin (gate-on-owed-state; scan the §8 authority not just the mirror; the aggressive regex broadenings were REBUTTED by the honest text). Epic Q3 retrospective at `epic-q3-retro-2026-07-19.md`.
- **Epic Q4 — Quality Scorecard Live-Wiring — party-greenlit + built + closed:** operator chose BOTH surfaces. **6/6 party GO-WITH-AMENDMENTS before dev** (Winston/John/Amelia/Murat + Cora + Audra; Tier-2 block-mode substrate rule), 16 amendments QLW-1..16 at `epic-q4-party-greenlight-2026-07-20.md`. **Q4.1** operator-surface `quality` tile (additive `operator-surface.v1` in place, NO schema/pack bump; assembler self-populates at the completion choke-point; structural zero-lie validator). **Q4.2** `production_runner` → `quality-final-report.md` run-end hook (atomic write, compute-once fence_state read back from run_summary.yaml, terminal-only structural via the two `status="completed"` sites). **Q4.3** HUD render (public.py allowlist + page.py `_quality_panel` + **client.py POLL_JS mirror** + styles). Each: fresh block-mode dev RED-first → 3-layer adversarial review → RED-first remediation → commit → push. Retrospective at `epic-q4-retro-2026-07-20.md`.
- **Merge:** `--no-ff` `dev/quality-scorecard-epic-2026-07-19` → `master` (`656e6241`), pushed. The full Q1+Q2+Q3+Q4 arc (25 commits) is on master.

## What is next

1. **The R2 operator-steered live trial** (on `tejal-apc-c1m1-p1-call`) — the standing product frontier. It now CLOSES all the OPEN live-equality witnesses: `q1-4b-r2-final-report-projector-witness` (UPDATED-not-closed: wired + offline byte-match-proven; live equality-vs-env-truth rides R2), the NEW `q4-2-r2-hud-quality-tile-witness`, and the Q1–Q3 per-dimension witnesses. **Do NOT run a live trial autonomously** — it rides the operator's shakedown.
2. **The fresh-naive-holdout MEASUREMENT** (`reading-path-fresh-naive-holdout-pre-trial` = DID Leak-4) — the top learner-trust leak the finished scorecard surfaces; recording it flips CAL1 weak→strong. Its own owed epic.
3. **Deferred follow-ons filed** (all OPEN, none reactivated as epic work): `q4-1-report-coverage-gap-underlisting-robustness` (report.py flags only empty leak-lists, not under-listing; enforced-away today by the len==open_leaks identity pins); capability full-trial-artifact-scan; lane coverage-completeness-verifier.

## Unresolved issues / risks

- **The LIVE equality witnesses are UNPROVEN until the operator R2 trial** — the BUILD is done + offline-proven (byte-match, fail-soft, two-walk, no-inflation pins), but no surface claims live-proven. This is honest, intended deferral (GL-10), not a gap to hide.
- **Ambient dirty files** (NOT session-owned, left untouched, listed as worktree state): shadow-monitor `.md`s, `state/config/gamma-styleguide-picks.jsonl`, `workbooks-*`, HAI/tejal corpus dirs, `goal-*.txt`, `state/runtime/notify/`, `tests/fixtures/specialists/texas/fixture_bundle/.texas-hardening.lock`.
- **Pre-existing unrelated test failures confirmed baseline (stash-verified):** ~21 `production_runner` live-preflight failures (`PreflightGateFailed: hud-server-healthz/openai`), 2 `test_run_summary_yaml_emit.py`, 1 `test_health_tiles_prefer_persisted_cost_report` — all identical with this session's edits stashed; NOT introduced by the arc.

## Key lessons

- **The believed-green catalog extended to the wiring/render layer.** The 3-layer adversarial review caught a real defect at every Q4 story the dev had marked "done" — most consequentially the Q4.3 **HIGH**: the server panel rendered fine, but `client.py`'s POLL_JS re-renders the completed brief CLIENT-SIDE every 3s and dropped the tile → it vanished on the first poll, invisible on the surface the operator actually watches. **Verify the DYNAMIC/poll render path, not just cold server load.**
- **Field-level type-defensiveness on a RAW producer projection** — the HUD reads raw `operator-surface.json`; a scalar `top_leaks` crashed the whole render. Never assume an upstream pydantic model's shape; the on-disk artifact can be corrupt.
- **Make honesty invariants structural (a `model_validator`), not by-construction** (Q4.1 available=False⇒band=None). **Atomic durable-artifact writes** that feed a witness + don't-overstate-determinism (Q4.2). **Determinism-as-honesty at the emit** — read the COMMITTED doc, never `app.quality.signals.*` live recompute (QLW-4).
- **Party-greenlight-before-dev on Tier-2 block-mode substrate produced the binding design up front** (additive-v1, wire-at-the-shared-choke-point, kill-the-/100-score) that every story executed without relitigation — no mid-flight kill-switch.

## Validation summary

- Per-story suites all green at close: Q3.4 507 · Q4.1 668 · Q4.2 524 (hook 17) · Q4.3 144 HUD. Ruff clean, import-linter 18 kept / 0 broken, pipeline-lockstep exit 0 throughout. Additive-within-operator-surface.v1 (no schema/pack bump); block-mode hook clean every story (shape-pin + parity + HUD tests the real arbiters).
- Step 0 coherence: L1 deterministic checks run directly and green (lockstep exit 0, ruff clean, sprint-status test 2 passed); L2 covered by the per-story 3-layer adversarial reviews (Blind/Edge/Acceptance) + RED-first remediation. `/harmonize` full-sweep not separately run — the per-story adversarial ceremony + green L1 served the coherence gate for this dev arc.
- Step 0b pre-closure: each `done` story passed its 3-layer review + orchestrator re-verify before flip.
- Merge to master `656e6241` pushed; branch `9cbf2512` pushed.

## Artifact update checklist

Q3.4 + Q4.1/Q4.2/Q4.3 story specs ✓ · Q4 party-greenlight ✓ · Q3 + Q4 retrospectives ✓ · sprint-status.yaml ✓ (all epics/stories done; 12 action items across Q1–Q4; test 2 passed) · deferred-work.md ✓ (q1-4b-r2 updated-not-closed; q4-2-r2 + q4-1-report-robustness filed) · SESSION-HANDOFF ✓ (this + arc-close roll-down) · bmm-workflow-status ✓ · project-context + next-session ✓ (regenerated) · STATE-OF-THE-APP ✓ (banner) · memory ✓ (arc-complete + live-wired) · merge-to-master ✓ (`656e6241`) · guides/KG — reviewed, KG-regen recommended to operator (Epic close + ≥10 files) · push (branch + master) — Step 12.

---

# Session close 2026-07-19 — PROJECT QUALITY SCORECARD epic DESIGNED + GREEN-LIT + RATIFIED (planning; dev deferred to fresh session)

**Final class:** S (strawman code committed: `app/quality/`, a `run_summary.yaml` field in `production_runner`). **Branch:** `dev/quality-scorecard-epic-2026-07-19` (cut off `master` `19a329c0`; 4 commits `4e8b9ed7`→[this wrapup]; **NOT yet merged**). **Opened as:** continuation of the 2026-07-18 session after the status-surface merge to master; operator introduced a new topic — a project-specific quality score.

## What was completed

- **New topic: a customized project quality-reporting system**, first dimension = **Dynamic Intelligence vs Determinism (DID)** (intelligence at the "necks", determinism in the "bones", fences enforced). Consolidated a provided prior-party conversation on the intelligence topic.
- **Process correction (operator-flagged):** the assistant jumped to building a strawman before convening the design party. Corrected — a **fully-spawned design party** (Winston/Murat/John/Mary) + a **landscape survey** redesigned it. Key outputs: runs emit per-run FACTS not the project grade; the scorecard must honor its own fence (per-criterion {judged level + computed signal + evidence_ref}); anti-believed-green = machine-vs-prose honesty-pin tests reusing the Epic-43 RED-first ratchet; report band+leaks+trend not a false-precise /100; Mary caught a **mis-cited reading-path number** (fresh holdout is OWED/unmeasured, not 0.071). Survey: the scorecard doc is the HOME; SOTA §4/§11.5 is complementary (cross-ref, not merge); reuse existing emitters.
- **Epic authored + green-lit + RATIFIED:** `_bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md` — a dedicated epic file (NOT the destructive `epics.md` overwrite the BMAD skill's step-01 would have done). Scope "everything": Q1 engine+DID (foundation) · Q2 ready siblings (cost-efficiency, coverage-honesty, fidelity-trust) · Q3 partial+report-only (capability-honesty, tracker-coherence, lane-discipline, calibration). **`bmad-party-mode` green-light = 4/4 GO-WITH-AMENDMENTS** (Winston/John/Murat/Amelia; no NO-GO, no impasse) → **16 binding amendments GL-1…GL-16** folded in (ordering fix; split Q1.4; protect the `app/quality` clean leaf w/ a structural import test; static breadcrumb no doc-parse on emit; fence_state into all 5 emit sites; dimension-coverage meta-ratchet; Q3.2 not pin-less; nail silent_bypass_events; R2 witness = checkable comparison). Amelia verified every named seam against the repo.
- **Strawman baseline** (`4e8b9ed7`): `app/quality/scorecard.py` fail-soft reader, `docs/quality/project-quality-scorecard.md` (prose + versioned machine block + dimensions container), `scripts/utilities/quality_scorecard.py` CLI + `--check`. **Bones are keepers; content/integration REWORKED by the epic** (the run-summary stamp + hand-transcribed judgment block are explicitly REPLACED per the binding consensus).

## What is next

1. **DEV opens on Epic Q1 (foundation)** in the corrected order **Q1.1 → Q1.4a → Q1.2 → Q1.3 → Q1.5 → Q1.4b**, honoring GL-1…GL-16 (binding). `bmad-code-review` precedes any story `done`. Class S — dev per BMAD dev-story discipline.
2. **Testing doctrine (operator-mandated):** live-test at the component + run-segment level; full E2E runs economically OR **rides the upcoming Operator/HIL R2 trial** (witness `fence_state` + the final-report projection as a checkable comparison, per GL-10). The measure must be VERY reliable — every dimension carries its own honesty-pin ratchet.
3. **The R2 operator-steered live trial** (on `tejal-apc-c1m1-p1-call`) remains the standing product frontier — the quality reporting rides it as part of the shakedown.
4. **Branch disposition:** `dev/quality-scorecard-epic-2026-07-19` merges to master at arc close (or per operator).

## Unresolved issues / risks

- **The strawman is WIP and KNOWN-flawed** (superseded by the party design) — do NOT ship it as-is; the epic reworks it. It's kept only as scaffolding + a clean diff base.
- Ambient dirty files (NOT session-owned, unchanged): shadow-monitor `.md`s, `gamma-styleguide-picks.jsonl`, `workbooks-*`, HAI/tejal corpus dirs, `goal-*.txt`.

## Key lessons

- **Design goes through the party BEFORE building** — the assistant built a strawman first and was rightly stopped; the party then caught a recursive flaw (the scorecard didn't honor the fence it measures), a mis-cited metric, and the believed-green trap. Party-first is not ceremony here; it changed the design materially.
- **The BMAD create-epics skill's step-01 would overwrite the 256KB project `epics.md`** — for an established repo, author a DEDICATED epic file (repo convention), never run the greenfield-template path.

## Validation summary

- ruff clean on `app/quality/` + the CLI; fail-soft reader + runner helper verified (`_quality_scorecard_ref()` returns the ref or the `{status: unavailable}` marker, never raises). No new test suite yet — the epic's Q1.1/Q1.3 stories author the honesty-pin + fail-soft tests (dev phase). Step 0 coherence sweep: not run as a separate `/harmonize` — this was a planning arc (party design + green-light served as the review).

## Artifact update checklist

epic doc ✓ (authored + green-lit + RATIFIED) · strawman baseline ✓ (`4e8b9ed7`, labeled) · SESSION-HANDOFF ✓ (this) · bmm-workflow-status ✓ · project-context + next-session ✓ (regenerated) · sprint-status — deferred to dev-open (bmad-sprint-planning generates Q1-Q3 rows when dev starts) · guides/ONBOARDING/KG — unchanged (planning arc) · push (branch) — Step 12.

---

# Session close 2026-07-18 — DOC CHAIN (ONBOARDING+guides+SOTA) + STATUS-SURFACE CONSOLIDATION arc (bmad-quick-dev, party-confirmed COMPLETE)

**Final class:** S (session-governance protocol + scripts/tests + sprint-status touched). **Branches:** opened on `trial/c1m1-p1-2026-07-17` (doc chain, pushed `6d87f35b`); cut `dev/status-surface-consolidation-2026-07-17` off it for the consolidation arc (4 commits `497eb4dc`→`f382e651`, NOT yet pushed at this section-write — see Step 12). **Opened as:** BMAD session-START (doc chain) → operator-directed party-mode on the status-surface liability → `bmad-quick-dev` consolidation arc.

## What was completed

- **Doc chain (Class D, `trial/c1m1-p1-2026-07-17`, pushed `6d87f35b`):** ONBOARDING regen against the fresh `bfefcc1b` graph (8→7 layers, 2699 nodes; pairing-completion commit `6a7a9bea`); then user-guide → dev-guide → admin-guide → specialist docs (`how-to-add-a-specialist` pitfall #11) → STATE-OF-THE-APP (§11.1/§11.2/§11.5 + top banner) reconciled forward to Epics 41/42/43.
- **Status-surface consolidation arc (Class S, `dev/status-surface-consolidation-2026-07-17`):** party-ratified frozen contract (`spec-status-surface-consolidation.md`). **3 authored SSOTs** (sprint-status/Kanban, SESSION-HANDOFF/chronology, STATE-OF-THE-APP/product-truth) + deferred-inventory (governance, untouched) + **2 fail-loud GENERATED views** (`next-session-start-here.md`, `docs/project-context.md`). Cold history archived to dated `*.history.md` siblings (bmm blob 37KB, SESSION-HANDOFF 547KB→20KB, SOTA 122KB→81KB, project-context addenda). START/WRAPUP session-protocol contract table rewritten (SSOT-of-SSOTs) + arc-close roll-down step. `sprint-status` value-reconciled to SOTA §11 (concierge-substrate→done; stale comments; WAVE_LABELS 41/42/43; tracker-reality note) — no structural reformat, tripwire_events untouched. Two generators built with fail-loud fixtures; a latent `progress_map` case-sensitivity bug (live SESSION-HANDOFF extracted 0 chars) fixed via case-insensitive matching + shared heading constants + integration/live/retention tripwire tests.
- **Fully-spawned 6-voice confirmation party + adversarial patch batch:** Winston/John/Paige/Blind/Edge/Murat reviewed the real diff → no BLOCK, no intent/spec defect. Patch batch `f382e651` (broadened `# Session` match + fail-loud stale-lift; `newline=""` byte-for-byte; idempotent tracked header; anchored bootstrap; +12 tests). Re-convened critics: Murat **VERIFIED-COMPLETE**, Edge + Blind **CONFIRMED-RESOLVED** → full consensus COMPLETE (no Dr. Quinn needed). 201 tests green, ruff clean.

## What is next

1. **Push `dev/status-surface-consolidation-2026-07-17`** to origin (Step 12; new branch, no tracking yet) — consolidation arc is complete + party-confirmed; safe to push.
2. **Merge decision (operator):** the consolidation branch is discrete governance substrate ready to merge to `master` (or fast-forward into the trial branch). Operator's call on timing.
3. **The R2 operator-steered live trial** on `tejal-apc-c1m1-p1-call` remains the standing product frontier (unchanged; operator at the wheel).
4. **Deferred follow-up filed:** `project-context-base-doc-slim` (deferred-work.md) — the 111KB hand-authored base doc is the real 59-skill payload + carries ~12 dated chronology paragraphs; a separate scoped decision (not this structural pass).

## Unresolved issues / risks

- **Two accepted LOWs** (party-dispositioned, by-design): `generate_next_session._carry_forward_class` silently defaults the Expected-class when the label is absent (operator hand-sets it anyway); `next-session-start-here.md` timestamp is non-idempotent (gitignored — no tracked churn).
- **Ambient dirty files** (NOT session-owned, left untouched): shadow-monitor `.md`s, `state/config/gamma-styleguide-picks.jsonl`, `workbooks-*`, HAI/tejal corpus dirs, `goal-*.txt`, `state/runtime/notify/`.
- Pre-existing `progress_map` / `audit_done_bmad_coverage` nonzero exits confirmed baseline (stash-verified), not introduced.

## Key lessons

- **The status-surface consolidation's own thesis (stop hand-maintained drift) was validated by the party:** Murat *reproduced* a live silent-drop (case-sensitive parser + sentence-case live file → 0 chars extracted), which the earlier passing suite masked — the fix (case-insensitive + shared constant + generate→parse integration test) makes the drift mechanically catchable.
- **Discovery-first planning paid off:** the consumer audit corrected two wrong premises (project-context loaded by ~59 skills not 2; deferred-inventory archive section already existed) BEFORE any file moved — avoiding a broken cleanup.
- **The fully-spawned party is a real gate:** it upgraded 3 CONCERNS/CONDITIONAL verdicts to confirmed only after a verified patch batch, not on assertion.

## Validation summary

- 201 targeted tests pass (utilities + progress_map + sprint_status + tripwire audits); ruff clean; +12 new tests (integration, live-file guard, retention tripwire, fail-loud coverage). sprint-status YAML valid, tripwire_events preserved. Base doc byte-identical (111,157 B). Step 0 Cora sweep: NOT run as a separate `/harmonize` — the 6-voice party + adversarial verify + green suite served as the coherence check (Cora dissolved per 2026-04-24; tripwire noted — next `/harmonize` auto-promotes to full-repo).

## Artifact update checklist

spec ✓ (all tasks closed/descoped; Change Log + party record) · SESSION-HANDOFF ✓ (this + post-close addendum) · bmm-workflow-status ✓ · sprint-status ✓ (T8 reconcile) · deferred-work ✓ (base-doc-slim) · protocol docs START+WRAPUP ✓ (rewritten + Cora de-personify) · project-context + next-session ✓ (regenerated) · guides ✓ (hygiene pass — see addendum) · ONBOARDING/KG — unchanged (scripts under `scripts/utilities/` are graph-excluded) · push + merge-to-master — Step 12.

## Post-close follow-ons (operator-directed, same session)

Three operator-directed cleanups landed AFTER the initial WRAPUP (`739f1a72`), each committed + pushed on this branch:

1. **Cora persona dissolution reconciled (`53167408`).** A thorough read-only audit (subagent) confirmed persona-Cora is bindingly DISSOLVED (`DR-SLAB-1-CLOSE-2026-04-24.md` DR-2, party-ratified 5/5; de-registered; generator denylist). But the canonical protocol pair still *invoked* her (dangling) and her WRAPUP ref file contradicted the generated-view regime. Fix: **de-personified** START Step 1a + WRAPUP Step 0 (kept the coherence gate, dropped the persona; tripwire record relocated to the SESSION-HANDOFF Step-0 skip-notes); **archived** `skills/bmad-agent-cora/references/session-{start,wrapup}-protocol.md` → `references/_archive/` with a dissolution header; SKILL.md SS/SW rows marked DISSOLVED. Left untouched (still-live substrate): `preclosure_hook.py`, the `app/cora/` block-mode runtime (a DIFFERENT thing from the persona), and the §Sanctum FR112 anchor.
2. **Guide hygiene pass (`c589afad`).** Brought user/dev/admin guides into the regime's spirit without deleting reference: de-dated the `## Current Status (2026-07-17)` heading → stable reference heading + a **SOTA §11 product-truth pointer**; archived each `## Legacy Context` (pre-migration banners) → `docs/<name>.history.md`. Preserved all durable reference (dev seam maps, admin checklists, user capabilities/fences). `how-to-add-a-specialist.md` was already clean (untouched). Guides remain living reference docs, NOT on the mechanical roll-down.
3. **This WRAPUP re-run + merge to master** (operator-directed close): regenerated the two views off this addendum, then merged the branch to `master`.

**Reporting note (guides regime):** the guides are classified as living reference docs (contract-table row) — reviewed each Class S, updated at Step 9 — deliberately NOT SSOTs-per-question / generated views / roll-down, because they're read on-demand (Step 4) and pay no per-session coherence tax. `STATE-OF-THE-APP.md` §11 is now the single product-truth SSOT the guides point to.

---

---

> History archived to `SESSION-HANDOFF.history.md` (sections 2026-07-17 and older; retention = current arc + newest 1 prior).
