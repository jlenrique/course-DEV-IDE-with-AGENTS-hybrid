# BETA Scoping Brief (2026-06-19)

**Purpose:** Phase-1 input for the BMAD-team review that scopes the road from Trial-4 (PASS, narrated-deck pipeline complete with accept/review gates) to a **fully-functional BETA executed error-free twice**. Anchors the BETA spec (Phase 2) and the trial-sequence breakout (Phase 3).

**Operator goal (verbatim intent):** Marcus is the conversational SPOC for the operator/HIL; in conversation with Marcus the operator can, for a production run:
- **(a)** specify/confirm course-content sources + how each is to be treated
- **(b)** review ingestion reports (completeness / errors)
- **(c)** review the lesson plan (Marcus + Irene/ID)
- **(d)** review and influence the research conducted in support of the lesson
- **(e)** review and influence the creative treatment proposed by the CD — incl. **# slide variants to produce for Storyboard-A selection**, and clustering / pace / other CD+Irene settings
- **(f)** review and guide motion (video clip) plans and their integration
- **(g)** other near-term-desirable features (DEFER sophisticated ML/learning).

Success: BETA performs error-free to spec, executed **twice**.

---

## Substrate reality (what exists vs. what the BETA needs)

| BETA capability | Substrate today | Gap to close | Source register |
|---|---|---|---|
| **SPOC — Marcus conversational** | Raw CLI gates (`[c/e/s/x]`, per-gate shims). Marcus-persona is a parallel doc/planning layer, NOT in the runtime path. | Bridge Claude-conversation-space ↔ `app.marcus.cli` subprocess: Marcus narrates each gate w/ sanctum context, invokes the runner under the hood, collects verdicts conversationally. | `deferred-inventory :: marcus-interactive-experience-not-delivered-by-slab-7c` (Epic-level) |
| **(a) sources + treatment** | G0 §02A LLM directive composer (landed 7c.3a); confirm/edit/save/cancel at CLI. | Surface the composed directive conversationally; operator confirms/annotates treatment per source in dialogue. | §02A composer (done) + SPOC bridge |
| **(b) ingestion reports** | Texas emits `extraction-report.yaml` + `ingestion-evidence.md` + `manifest.json`. | Surface a readable completeness/error report at a gate; **fix T4-F1** (specialist-summary "Emitted artifacts: none" not wired to manifest; G1 drafted-reject false-negative). | `trial-4-specialist-summary-artifact-list-reporting-gap` |
| **(c) lesson plan review** | Irene Pass-1 produces lesson plan + plan_units (live). | Conversational review/edit of the lesson plan at a gate (currently no dedicated HIL pause for it). | Irene pass-1 (done) + SPOC bridge |
| **(d) research review/influence** | Epic-28 Tracy "detective" gap-fill lane fully implemented + module-tested, but **integration-orphaned** (no production-runner caller; no manifest node; AC-S3 pre-Pass-2 gate vacuous). | Wire the Irene→Marcus→Tracy→operator→Texas loop onto the trial path; conversational approval of suggested resources. | `tracy-gap-fill-lane-not-adopted-by-production-runner` |
| **(e) creative treatment + # variants** | CD directive + experience profiles (live); Gary single-dispatch (1 variant/slide); G2B is accept/review only, `variant_candidates: []`, picks don't re-route; clustering live. | **The "big leap":** operator sets N (variant count); Gary double-dispatch produces real N variants; G2B surfaces them; operator's per-slide pick re-routes downstream. | `trial-4-binding-variant-voice-picker` (T4-F3/F6) |
| **(f) motion plans** | Motion leg STRUCTURALLY UNPROVEN: kira node input-starved (no manifest motion-plan producer); `motion_receipts: []`; G2F gate groundless; compositor tolerant. | Motion data-plane (producer for the motion plan) + a review/guide HIL surface; honest motion synthesis (kling). dp-v2-class. | project-context 2026-06-13 motion-receipts investigation; `tagged-error-taxonomy-tranche-3` siblings |
| **(g) near-term desirables** | Reading-path narration degraded to "suggest" (enforcement not absorbed at severance); voice picker (T4-F6). | reading-path v2 (declare+check); voice binding picker (folds into (e)'s picker). | `reading-path-enforcement-machinery-not-absorbed-at-severance` |
| **Robustness (cross-cutting)** | Trial-4 needed 2 fixes + 1 re-roll; live-only gaps hidden by offline tests; `ModeMismatchError` crashes vs error-pauses. | Error-family hardening + offline tests that catch live dispatch gaps; drive fix-per-run → 0. | `trial-4-modemismatch-recoverable-family` + Trial-4 cross-trial run-shape learnings |

**Explicitly DEFERRED from BETA:** Epic 15 (Learning & Compound Intelligence), Epic 16 (Bounded Autonomy), sophisticated ML — per operator "(while deferring sophisticated machine learning capabilities for future development)."

---

## Proposed trial sequence (DRAFT — for party refinement)

Each trial is a substrate-verification probe that ALSO adds a BETA capability; exit criterion = the capability works error-free on the certified corpus.

- **Trial 5 — Binding creative treatment (capability e + g-voice).** Operator sets N; Gary double-dispatch → real N variants; G2B per-slide pick re-routes; voice picker binds. Exit: operator's variant+voice choices take effect downstream.
- **Trial 6 — Research + ingestion + lesson-plan review (capabilities b + c + d).** Wire Tracy lane onto trial path; surface ingestion report + lesson plan for conversational review/influence; fix T4-F1. Exit: operator reviews/influences ingestion, lesson plan, and research dispatch.
- **Trial 7 — Marcus SPOC + sources (capabilities SPOC + a + f-review).** Conversational gate surface replaces raw CLI; sources/treatment confirmed in dialogue; motion-plan review surface (even if motion synthesis stays minimal). Exit: a full run driven entirely through Marcus conversation.
- **Trial 8 — Motion data-plane (capability f, full).** Honest motion producer + synthesis + integration; or DEFER to post-BETA if party judges motion-synthesis out of BETA scope (review-only may suffice for (f)).
- **BETA dress rehearsal ×2 — the integrated run, error-free, twice.** All of a–g through Marcus SPOC on the certified corpus; zero fixes mid-run; then a second clean run.

**Robustness work** (T4-F1, modemismatch-recoverable, offline-catches-live-gaps) is folded into the trial it most relates to, not a separate trial.

---

## Open questions for the BMAD team (Phase-1 review)

1. **BETA scope boundary on motion (f):** does BETA require honest motion *synthesis*, or is *review/guide of motion plans* sufficient (synthesis deferred)? Motion is the least-proven leg; this decision sizes Trial 8.
2. **Sequence:** is binding-picker-first (Trial 5) correct, or should the Marcus SPOC surface land first so later trials run through the intended surface from the start?
3. **SPOC architecture:** IPC shape between Claude-conversation-space and `app.marcus.cli` (subprocess narration vs. in-process). Winston call.
4. **"Twice error-free" definition:** same corpus twice, or two corpora? Same use case, or two?
5. **Planning formality:** full `bmad-create-prd` → architecture → epics for the SPOC + binding-picker Epic, or a lighter trial-charter + per-capability stories?
6. **Naming-collision** (3 Marcuses) resolution before SPOC build.

---

## References
- `docs/trials/trial-4/postmortem.md` + `cross-trial-learnings.md §Trial-4`
- `_bmad-output/planning-artifacts/deferred-inventory.md` (post-Trial-3 architecture + Trial-4 sections)
- `_bmad-output/planning-artifacts/epics.md` (Epics 12-18, 28-32 Lesson Planner MVP, 33 lockstep)
- `_bmad-output/implementation-artifacts/epic-28-tracy-detective.md` (research lane)
- `state/config/pipeline-manifest.yaml` (gate topology)
