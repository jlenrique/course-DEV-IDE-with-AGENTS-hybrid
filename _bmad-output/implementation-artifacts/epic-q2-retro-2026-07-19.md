# Epic Q2 Retrospective — Project Quality Scorecard: Ready Siblings (cost / coverage / fidelity)

**Date:** 2026-07-19 · **Facilitator:** Amelia (Developer) · **Format:** synthesized (autonomous close per operator direction; the interactive party dialogue is compressed; the binding Next-Epic-Preparation deferred-inventory consultation per CLAUDE.md governance #1 is recorded in full below). · **Branch:** `dev/quality-scorecard-epic-2026-07-19` (`4167e912..db850271`).

## 1. Epic summary + metrics

**3/3 stories done**, serial (all touch the machine block + pin registry → serialize by rule). Each: fresh dev-agent RED-first → 3-layer `bmad-code-review` → RED-first remediation → orchestrator re-verify → commit → push.

| Story | Dimension | Band | Commit |
|---|---|---|---|
| Q2.1 | cost_efficiency (CE1 budget-stop opt-in = the leak) | B− (62) | `4167e912` |
| Q2.2 | coverage_honesty (CV1 coverage-gate default-OFF = the leak) | C (58) | `cd48acd1` |
| Q2.3 | fidelity_trust (FT1 semantic-audit WARN-only-never-gates = the leak) | C (58) | `db850271` |

- The scorecard now carries **4 dimensions** (DID + 3 siblings), each honest about a **real-but-not-default-on fence** — the recurring DID-C3 pattern (mechanism exists, opt-in/WARN-only → the leak, not a pass).
- **FOUR disjoint leak namespaces** (`did_leak:`=5 / `cost_leak:`=1 / `cov_leak:`=1 / `fid_leak:`=1); `ranked_project_leaks` = 8, cross-dimensional.
- **Review findings:** ~20 across the 3 stories; **0 BLOCKER**, and the recurring believed-green classes (below) all caught + reworked RED-first.
- **Test posture:** `tests/quality/` grew to **301 passing**; ruff clean, import-linter 18/0 throughout. DID stayed **65/B−** across the entire epic; each sibling's numbers held once landed.

## 2. What went well

- **Learnings transferred sibling-to-sibling — the review cost dropped each story.** Q2.1's CE1 fence-reader bug (self-clearing env constant → unreachable close-path) was caught in review; I baked the fix into the Q2.2/Q2.3 story specs up front, and **the bug did not recur** — CV1 and FT1 were built reachable + read-only the first time. Q2.2's CV2 "consult the real FAIL predicate, not mere presence" lesson went straight into Q2.3's FT2 spec.
- **The GL-13 authoring contract held.** Three new dimensions slotted in with zero projector changes and no Q1-machinery rewrites — only additive registration (leaks list, registered pin, canonical-key, history snapshot). The `docs/dev-guide/quality-scorecard-dimension-authoring.md` note earned its keep.
- **The equal-weight scoring model stayed consistent** across all four dimensions; honesty was preserved via band_note, not by inventing a per-dimension weighting scheme.
- **Clean-leaf (GL-3) survived four dimensions** — `app/quality` stayed stdlib-only at module scope via deferred imports; Q1.1's recursive guard backstopped every reader.

## 3. Challenges + key lessons (the believed-green catalog, deepened)

The Q1 lesson ("reconcile by content/identity, not by number") **generalized into a family** of believed-green classes the adversarial review kept surfacing — each inside the honesty machinery itself:

- **Over-claim-clean (Q2.2 CV2, Q2.3 FT2).** A signal that reports "clean/pass" from *presence or vacuity* rather than the *real FAIL predicate*: CV2's `is_clean_pass` never called `evaluate_coverage_gate` (clean on a real must-cover FAIL); FT2 certified clean on a degenerate/no-O/I/A/foreign trace. **Lesson:** an honesty signal must consult the code's real fail condition, and must refuse to certify clean on a malformed/degenerate input.
- **Test-toothing gaps (Q2.3 FT2, and Q2.2's toothless test).** A pin that *looks* toothed but can't isolate the property it claims to prove — Q2.3's FT2 fixtures moved `hard_fail` and `verdict_halts` together, so a regression to the verdict-only anti-pattern would ship green. **Lesson:** a pin must be constructed so the *specific* correct-behavior conjunct is isolated (vary one axis while holding the other), or it doesn't deliver its thesis. This is the meta-honesty the scorecard prizes: a green test that can't fail on the real bug is itself believed-green.
- **Reachable-close-path (Q2.1 CE1).** A signal-derived "fence" criterion must track reality in *both* directions — a reader that can never report the leak *closed* would false-RED the operator who fixes it. **Lesson:** read the real source (delegate/consult), never a self-clearing constant; read-only, no global-env mutation.
- **Aggregate-Band honesty (Q2.1 FT-2/CE band_note).** Equal-weight scoring can let post-hoc telemetry outvote a weak pre-spend/enforcement *thesis* criterion, so the headline Band reads better than the load-bearing reality. **Lesson:** the band_note must name what lifts the headline and what the weak thesis is. **(Standing operator flag:** weighted scoring — where a dimension's thesis criterion carries more weight — is a possible future scorecard-wide change; deliberately not taken here to keep the model consistent.)
- **Reconcile-by-identity across namespaces.** Four leak namespaces must be provably disjoint + non-cross-counting, and a count-only reconciliation must be paired with a slug-set-identity check (extended from Q1).

## 4. ⚖️ BINDING deferred-inventory consultation (Next-Epic-Preparation — CLAUDE.md governance #1)

Reviewed `deferred-inventory.md` against Epic Q2's new substrate (3 sibling dimensions + the four-namespace leak structure + the sibling-authoring pattern) for **Q3 readiness**. **Governing principle (epic phasing flag):** Q3 dimensions SCORE/REPORT these honestly; they do NOT build the underlying harnesses. Verdict per entry: "consulted; scored/reported by the mapped Q3 dimension; the underlying fix remains its own separately-triggered follow-on."

| Deferred entry | Q2/DID relation | Mapped Q3 dimension | Reactivation verdict |
|---|---|---|---|
| `workbook-capability-tier-honesty-lag` | DID Leak-5 (registry-tagged); bundle_catalog tier stale vs produced reality | **Q3.1 capability-honesty (auto-reconciliation)** | **Consulted; Q3.1's auto-reconciliation targets exactly this "produced but tier stale" pattern (the DID Leak-5 pattern named in the epic).** The tier-bump stays governance-gated (party). Not reactivated as Q-epic work. |
| `reading-path-fresh-naive-holdout-pre-trial` | DID Leak-4 (registry-tagged); the OWED fresh-naive holdout | **Q3.4 calibration (REPORT-ONLY)** | **Consulted; Q3.4 REPORTS the OWED holdout honestly + does NOT build it (stays this entry).** Cross-link pinned; no double-count. Q3.4's pin fails if it ever implies a fresh number was measured. |
| `braid-workbook-semantic-claim-citation-audit` | DID Leak-2 + Q2.3 FT1 substrate (WARN-only) | (scored by DID-C5 + fidelity FT1 already) | **Consulted; already scored by two dimensions (namespaced, no double-count).** The fuller claim↔source audit stays its own follow-on. |
| `p2-4b-reading-path-repertoire-and-conformance-corpus` | parent of Leak-4 | Q3.4 calibration | **Consulted; Q3.4 reports posture, does not resume the corpus work.** |
| Q2 substrate for Q3.2 / Q3.3 | progress_map.py / doc_drift_monitor.py / deferred-inventory (Q3.2); import-linter contracts + lane-matrix (Q3.3) | **Q3.2 tracker-coherence / Q3.3 lane-discipline** | **Substrate present + healthy** (import-linter 18/0 proven every Q1/Q2 story; the four-namespace leak-registry consistency Q2 built is itself a tracker-coherence signal). Q3.2/Q3.3 SCORE the already-enforced; no new enforcement, no reactivation. |

**Consultation outcome:** no deferred entry is reactivated *as Q-epic work* — Q3 scores/reports them. **Q3.1 (capability-honesty auto-reconciliation) and Q3.4 (calibration report-only) have the highest phasing risk** per the epic's own flag (auto-reconciliation / calibration can over-balloon) — the retro recommends holding both to the epic's "ship the scoring + a manual-reconcile/owed TODO, split the deep harness to a follow-on epic" guidance.

## 5. Next-epic (Q3) readiness + action items

**Q2 UNBLOCKS Q3 cleanly.** The sibling-dimension pattern is proven three times; Q3's four dimensions (capability-honesty, tracker-coherence, lane-discipline, calibration-report-only) follow the same GL-13 contract. **Q3 is partial/report-only by design** — the phasing flag is the main risk to manage.

**Action items (carry to Q3 sprint-planning — the Q1 five PLUS the Q2 additions):**
1. **AI-Q2a: Honesty signals must consult the real FAIL predicate** (not presence/vacuity/verdict-status) AND refuse to certify clean on a malformed/degenerate/foreign input (the CV2/FT2 lesson). Owner: dev + review. Status: open.
2. **AI-Q2b: Every pin must ISOLATE the property it claims** — vary the one axis that distinguishes correct-from-regressed, or the pin is believed-green (the FT2 test-toothing lesson). Owner: dev + review. Status: open.
3. **AI-Q2c: Signal-derived fence criteria must be reachable-close-path + read-only** (delegate to the real source; no self-clearing constant, no global-env mutation) — the CE1 lesson. Owner: dev. Status: open.
4. **AI-Q2d: Honor the Q3 phasing flag** — Q3.1 auto-reconciliation and Q3.4 calibration ship scoring + a manual/owed TODO if the deep harness over-balloons; split to a follow-on epic rather than build the harness. Owner: story author + operator. Status: open.
5. **(Standing) AI-Q1a…e** (GL-13 registration; reconcile-by-identity across namespaces; GL-9 RED-under-seeded; signal-vs-judgment honesty; R2 checkable-comparison witnesses — now 3 more filed: cost/coverage/fidelity). Status: open.

## 6. Readiness assessment

- **Testing & quality:** ✅ 301 hermetic tests green; ruff + import-linter clean; every honesty pin proven RED-under-seeded-edit; the four-namespace leak structure provably disjoint. **Live E2E honestly DEFERRED to R2** for all four dimensions (four witness obligations filed) — the scorecard's posture reflects this.
- **Deployment/integration:** the dimensions + projector are functions + goldens; not yet wired into `production_runner`'s live operator surface (deliberately — the pipeline-lockstep trigger path stays untouched; live wiring rides R2).
- **Branch:** `dev/quality-scorecard-epic-2026-07-19` pushed through `db850271` (Q1 + Q2 = 13 story/retro commits); merge-to-master is the operator's call at arc close.
- **Honest residual (carried):** the trend/history axis is a judgment-ledger (can't catch coordinated doc+ledger fabrication); the equal-weight Band can under-represent a weak-thesis dimension (mitigated by band_note; weighted-scoring flagged as a future option).

**Verdict:** Epic Q2 is complete and solid. Four dimensions, each honest about its fence, no number moved dishonestly, and the review caught progressively subtler believed-green — the machinery is working on itself. Clear to proceed to Q3 planning, with the phasing flag as the item to watch.
