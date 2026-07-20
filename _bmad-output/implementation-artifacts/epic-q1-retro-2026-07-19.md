# Epic Q1 Retrospective — Project Quality Scorecard: Scorecard Engine + DID Reframe (FOUNDATION)

**Date:** 2026-07-19 · **Facilitator:** Amelia (Developer) · **Format:** synthesized (autonomous close per operator direction — the interactive party dialogue is compressed; the binding Next-Epic-Preparation deferred-inventory consultation per CLAUDE.md governance #1 is recorded in full below). · **Branch:** `dev/quality-scorecard-epic-2026-07-19` (`b133b1ef..1c0a5a6a`).

## 1. Epic summary + metrics

**6/6 stories done**, GL-1 dispatch order **Q1.1 → Q1.4a → Q1.2 → Q1.3 → Q1.5 → Q1.4b**. Each story: fresh dev-agent RED-first → 3-layer `bmad-code-review` (Blind Hunter + Edge Case Hunter + Acceptance Auditor) → RED-first remediation → orchestrator re-verify → commit → push.

| Story | Deliverable | Commit |
|---|---|---|
| Q1.1 | schema v2 + generalized fail-soft reader (clean leaf, recursive guard) | `dd2b2bb0` |
| Q1.4a | per-run `fence_state` in run_summary (all 5 emit sites/both walks; honest `silent_bypass_events`) | `0fdc442b` |
| Q1.2 | per-criterion signal readers + honest signal-vs-judgment partition | `f717fba6` |
| Q1.3 | anti-believed-green honesty-pin ratchet framework + GL-6 meta-ratchet + trend-history | `38679e8f` |
| Q1.5 | DID reauthored honestly (Band+ranked-leaks+trend; Mary's corrections; 5-leak registry) | `9a111f1e` |
| Q1.4b | deterministic final-report projector (This-run facts vs Project posture; GL-13 cross-dim) | `1c0a5a6a` |

- **Review findings:** ~40 across the 6 stories, incl. **1 BLOCKER** (Q1.2 C4 `undetected→strong`), **2 HIGH** (Q1.3 upgrade-guard bypass; Q1.5 leak-tag lifecycle), all reworked RED-first. **0 findings shipped unremediated** beyond consciously-deferred/dismissed items.
- **Test posture:** the `tests/quality/` suite grew to **162 passing + 1 intentional design-marker** (an xfail that Q1.5 then promoted to a hard pin). ruff clean, import-linter 18/0 throughout.
- **Outcome:** DID = **65 / B−** (honest baseline). No number moved dishonestly across the epic — honesty clarified *evidence*, not *judgment*.

## 2. What went well

- **The 3-layer adversarial review is a real gate, not ceremony.** It caught believed-green the dev passes missed on 3 separate stories — including inside the very machinery built to prevent believed-green. Each catch was verified (RED-first) before remediation.
- **Story-split discipline (GL-1/GL-2) held.** Every dev agent respected its scope fence exactly; the sequenced split (schema → run-facts → signals → pins → content → projector) meant each story consumed the prior's landed substrate cleanly, with `bmad-create-story` carrying previous-story review learnings forward.
- **Clean-leaf invariant (GL-3) survived contact.** `app/quality` stayed stdlib-only at module scope across 4 new modules (scorecard/signals/history/report) via deferred local imports; Q1.1's recursive AST leaf-guard backstopped every later story.
- **DID numbers never moved dishonestly.** The consensus that "runs emit facts, not the grade" + the mandatory doc↔history mirror + evidence-gated upgrade guard mean the score is now mechanically unable to rise without cited evidence.

## 3. Challenges + key lessons (systems, not blame)

- **⭐ THE epic-defining lesson — "reconcile by content/identity, not by number."** The adversarial layers caught the same class of believed-green three times, each time where a check reconciled a *count* while the *content* could silently diverge:
  - **Q1.2 (BLOCKER):** C4 `_level_c4` mapped `undetected`/`unavailable`→`strong` — an unverified state scored as clean. Fix: no unverified/unknown/proxy signal may ever award a clean level; C2/C4 reclassified from *mechanical* to *judgment-with-evidence* (the manifest has no clean determinism field; `model_config_ref`-nullness is a proxy that node 08 / Pass-1 gates disprove).
  - **Q1.3 (HIGH):** the evidence-gated upgrade guard was inert on real data + bypassable by simply not appending history. Fix: a mandatory doc↔history **mirror** pin makes skipping the append impossible.
  - **Q1.4b (MED):** the leak reconciliation was length-only (count-through-5); slug **identities** were never set-compared. Fix: a slug-set identity pin.
  This is now a **reusable review heuristic**: any "reconcile A vs B" that compares cardinality must also compare identity/content.
- **Honest labeling > preserving the number.** Q1.2's reclassification (only C3 is purely mechanical; C2/C4 are honest judgment-with-imperfect-signal) kept DID at 65/B− while removing the false claim that the levels were mechanically verified. The epic's own escape hatch ("if a derivation can't match today's value without a judgment call, it's not purely mechanical") was the right call and was exercised.
- **The metric-citation discipline is load-bearing.** Mary's binding rule — every reading-path number carries `(subject, substrate@date)` — is now embodied in §1.6: `0.071` is `built-classifier resubstitution@2026-06-23`, and the fresh naive holdout is **OWED/UNMEASURED, never implied**. The two coincidentally-equal `0.93`s (built-classifier escalation vs catalog-approach primary-key) were disambiguated to kill the H4 inherited-green conflation.
- **Fail-soft must be per-field, not top-level.** Recurred as a review finding on Q1.1, Q1.4a, and Q1.4b — one bad sub-reader must degrade one field, never collapse the whole artifact/report.
- **A ratchet's placement matters as much as its logic.** Q1.5's leak tags, first placed *nested under their deferred entries*, would have spuriously red-flagged the hard pin on routine inventory archival. Fix: a stable `## DID Scorecard Leak Registry`, decoupled from entry lifecycle.

## 4. ⚖️ BINDING deferred-inventory consultation (Next-Epic-Preparation — CLAUDE.md governance #1)

Reviewed `deferred-inventory.md` against Epic Q1's new substrate (the scorecard engine, honesty-pin framework, signal readers, GL-13 cross-dimensional leak structure) for Q2/Q3 readiness. **Governing principle (epic phasing flag):** the scorecard *reports/scores* these honestly; it does **not** build their underlying harnesses — so the verdict per entry is "consulted; scored/reported by the mapped Q2/Q3 dimension; the underlying fix remains its own separately-triggered follow-on (NOT reactivated as Q-epic work)."

| Deferred entry | Q1 relation | Mapped Q-dimension | Reactivation verdict |
|---|---|---|---|
| `leg4-narration-fidelity-gate-precision-before-flag-on` | DID Leak 1 (C3), registry-tagged | Q2.3 fidelity-trust (fidelity fence OFF) | **Consulted; scored as a Q2.3/C3 leak.** Not reactivated — the fence-flag-on work stays its own follow-on. |
| `gary-export-llm-brief-to-page-matcher` | DID Leak 3 (C2), registry-tagged | (C2 bone-determinism) | **Consulted; scored as the C2 "determinism-pretending" leak.** Not reactivated. |
| `braid-workbook-semantic-claim-citation-audit` | DID Leak 2 (C5), registry-tagged; PARTIAL (WARN-only tripwire landed) | Q2.2 coverage-honesty / Q2.3 fidelity-trust | **Consulted; scored as the WARN-not-gate leak.** The fuller claim↔source audit stays its own follow-on. |
| `reading-path-fresh-naive-holdout-pre-trial` | DID Leak 4 (C5), registry-tagged | **Q3.4 calibration (REPORT-ONLY)** | **Consulted; Q3.4 REPORTS the OWED fresh-naive holdout honestly.** Q3.4 explicitly does NOT build the holdout harness (stays this entry). Cross-link pinned; no double-count. |
| `workbook-capability-tier-honesty-lag` | DID Leak 5 (C5), registry-tagged; PARTY-GATED | **Q3.1 capability-honesty (auto-reconciliation)** | **Consulted; Q3.1's auto-reconciliation targets exactly this (the "produced but tier stale" pattern).** The tier-bump remains governance-gated (party). |
| `p2-4b-reading-path-repertoire-and-conformance-corpus` | the reading-path calibration mega-entry (parent of Leak 4) | Q3.4 calibration | **Consulted; Q3.4 reports the calibration posture, does not resume the corpus work.** |
| `vision-comparator-anti-vacuity-pass-bar` · `believed-green-tracker-audit` | anti-vacuity / believed-green governance guards | (cross-cutting) | **Consulted; Q1's "reconcile by identity not count" learning REINFORCES these.** Not reactivated; noted as aligned governance. |

**Consultation outcome:** no deferred entry is reactivated *as Q-epic work* — Q2/Q3 SCORE/REPORT them (that is the scorecard's job). The GL-13 registration contract (`docs/dev-guide/quality-scorecard-dimension-authoring.md`) is the mechanism by which each Q2/Q3 dimension registers its own leaks into the shared ranked list.

## 5. Next-epic (Q2/Q3) readiness

**Q1 UNBLOCKS Q2 + Q3 cleanly.** Everything a sibling dimension needs is in place: the versioned schema + generalized reader (Q1.1), the signal-vs-judgment derivation pattern (Q1.2), the honesty-pin framework + GL-6 meta-ratchet + mirror + evidence-gated guard (Q1.3), the per-run fact substrate (Q1.4a), and the cross-dimensional ranked-leak structure + projector + registration contract (Q1.4b).

**Ready siblings (Q2), each with named live seams (verified in the epic green-light):** Q2.1 cost-efficiency (`app/runtime/economics.py::check_trial_budget`/`BudgetStatus`, `cost_posture` on `trial_economics_report.py`), Q2.2 coverage-honesty (`CoverageReceipt`, `coverage_gate_active()` default-OFF), Q2.3 fidelity-trust (Vera trace + `source_fidelity_audit` `SEMANTIC_TRIPWIRE.gates_production=False`).

**Action items (carry to Q2/Q3 sprint-planning):**
1. **AI-Q1: Each Q2/Q3 dimension MUST follow the GL-13 registration contract** — add its `leaks:` list to the machine block + its honesty-pin to the registry, or the GL-6 meta-ratchet + `leak_coverage_gaps` will red it. Owner: story author. Status: open.
2. **AI-Q2: Apply the "reconcile by identity, not count" heuristic** to every new dimension's pins — a count/length reconciliation must be paired with a content/identity check. Owner: dev + review. Status: open.
3. **AI-Q3: Every new dimension pin must be GL-9-compliant** — green by agreeing with reality today AND proven RED under a seeded dishonest edit. Owner: dev. Status: open.
4. **AI-Q4: Preserve the signal-vs-judgment honesty** — only wire a criterion as `signal-derived` if the code genuinely, unambiguously computes it; otherwise `judgment-with-evidence` with an honestly-named signal. Owner: dev + review. Status: open.
5. **AI-Q5 (from the GL-10 obligation): the R2 operator-steered trial witnesses `fence_state` + the projector output** as a checkable comparison (two obligations filed in `deferred-work.md`: `q1-4b-r2-final-report-projector-witness` + the Q1.4a fence_state witness). Owner: operator-gated (R2). Status: open.

## 6. Readiness assessment

- **Testing & quality:** ✅ 162 hermetic tests green; ruff + import-linter clean; every honesty pin proven RED-under-seeded-edit. **Live E2E is honestly DEFERRED to the R2 trial** (GL-10) — the scorecard's own posture reflects this (it does not claim what it hasn't witnessed).
- **Deployment/integration:** the projector is a function + golden; it is **not** yet wired into `production_runner`'s live operator surface (deliberately — the pipeline-lockstep trigger path stays untouched; live wiring rides R2).
- **Branch:** `dev/quality-scorecard-epic-2026-07-19` pushed through `1c0a5a6a`; merge-to-master is the operator's call at arc close.
- **Honest residual (documented, not hidden):** the trend/history axis is a judgment-*history* ledger — the pins enforce doc↔ledger mirror + mandatory append + evidence-gated increases but cannot mechanically detect a coordinated fabrication of *both*; that residual is a review/governance boundary.

**Verdict:** Epic Q1 is complete and solid from a story + quality perspective. The one honest caveat — no live E2E witness yet — is by design (rides R2) and is itself reflected in the scorecard's posture. Clear to proceed to Q2/Q3 planning.
