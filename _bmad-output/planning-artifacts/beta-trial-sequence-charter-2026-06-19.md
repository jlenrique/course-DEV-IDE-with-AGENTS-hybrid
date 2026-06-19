# BETA Trial-Sequence Charter (2026-06-19)

**Status:** Phase-3 deliverable. Breaks `beta-spec-2026-06-19.md` into a dependency-ordered sequence of stories + trials I execute autonomously toward the §2 "error-free twice" criterion. Governance: dispatch/specialist/runner-tier work = Claude-direct quick-dev + 3-lane self-review + push (Trial-4 cadence). **Manifest-touching work = pipeline-lockstep regime → party-mode green-light BEFORE dev** (flagged ⚠️ below). Each trial validates on the frozen corpus `tejal-apc-c1-m1-p2-trends`.

## Legend
- **Gov:** `light` = dispatch/specialist/runner (no manifest) → autonomous. `⚠️heavy` = manifest-touch → party-mode consensus first.
- **Auto:** can I run it fully autonomously? `yes` / `yes-after-party` (needs a party green-light milestone first).
- **Closes:** deferred-inventory / finding closed.

---

## S0 — FOUNDATION (blocks everything; D2 + D6). Gov: light. Auto: yes.
The universal precondition + the quality bar that makes "error-free" falsifiable. Land + green BEFORE any picker trial.

> **EXECUTION STATUS (2026-06-19, live):**
> - ✅ **S0.1** crash-taxonomy guard — `5c9cbea` (ModeMismatchError→error-pause; closes `trial-4-modemismatch-recoverable-family`).
> - ✅ **S0.2** ingestion-report integrity — `6497514` (summary artifacts wired to producer output; closes G1-false-reject half of T4-F1).
> - ◐ **S0.3** structured-card-binding — `a0d85a8` lands the **candidate-population** half (G2B/G4A cards now carry real variant/voice candidates + structured pick_context; closes T4-F6).
> - ✅ **T5b binding verb `select`** — `c1fc663` (party milestone #2 ratified Option B). The re-route MECHANISM: `_apply_verdict_to_run_state` surgically overlays a `select` verdict's pick onto the envelope (voice nests at voice_selection.selected_voice_id; per-slide variant map; fail-loud on unknown key/missing envelope); `edit` full-replace pins untouched. 7 binding pins + resume-roundtrip twin green.
> - ☐ **T5a LIVE validation** — pending: a trial to G4A + operator `select` non-default voice → assert post-G4A synthesis emits the picked voice (the operator→Enrique→synthesis wiring is the only part the unit tests can't prove; needs a live trial).
> - ☐ **S0.4** live-dispatch contract harness — not started.
>
> **Session note (2026-06-19):** Phases 1-3 complete; Phase 4 foundation + the core picker-binding mechanism landed + pushed (5 commits) across 2 party milestones. The goal gate (BETA error-free ×2 via Marcus SPOC) is a multi-arc build beyond a single session; remaining: T5a live validation, S0.4 harness, T6 review-lanes, T7 Marcus SPOC, T8 motion, dress-rehearsal ×2.

| Story | Scope | Exit | Closes |
|---|---|---|---|
| **S0.1 crash-taxonomy guard** | Re-base `ModeMismatchError` onto `SpecialistDispatchError` (tag `quinn_r.mode.unresolved`); add a test asserting all known failure families → error-pause, not crash. | mode-miss error-pauses + `trial recover`-able; guard test green | `trial-4-modemismatch-recoverable-family` |
| **S0.2 ingestion-report integrity (T4-F1)** | Wire each specialist-summary "Emitted artifacts" to the bundle/output `manifest.json`; G1 drafted-proposal reads the manifest (stop false-rejecting present content); diagnose Texas exit-10 double-dispatch. | G1 no longer drafts-reject over present content; summary==manifest test green | `trial-4-specialist-summary-artifact-list-reporting-gap` (cap b) |
| **S0.3 structured-card-binding (Tier-0)** | `G2BCard.variant_candidates`/`G4ACard.voice_candidates` carry structured candidates; resume reads `selected_*_id` from `edit_payload`; **downstream binding node** consumes the selection. | an `edit` verdict measurably changes the downstream artifact | Tier-0 (D2) |
| **S0.4 live-dispatch contract harness** | Per-woken-gate test that the node *passes* gate_id / emits its manifest node at LIVE dispatch (stub HIL responder); integration-boundary ratchet inventory; flake-budget instrumentation (auto-retry ≤1/node, ≤3/run, fail-loud on exceed). | each manifest-contract-table row (§3) has a green live-dispatch assertion; budget enforced | D6 |

**S0 gate:** all four green + a clean re-run of the Trial-4 path (no Class-A events) → proceed to T5a.

---

## T5a — VOICE PICKER (safe proof of the binding pattern; D3). Gov: light → ⚠️escalated (see contract finding). Auto: yes-after-party.
Voice candidates already exist (`enrique.voice_preview.voices`) — prove `edit`-binding on the easy lane first.
- ✅ **Candidate surfacing done in S0.3** (`a0d85a8`): `voice_preview.voices` → `G4ACard.voice_candidates` + structured pick_context.
- **Scope (remaining):** operator `selected_voice_id` binds the chosen voice into narration synthesis downstream.
- **🔴 CONTRACT FINDING (2026-06-19, blocks the re-route):** the binding seam is `_apply_verdict_to_run_state` (production_runner.py:788). Today a `verb="edit"` verdict **destructively REPLACES** `cache_state.cache_prefix` with `edit_payload` — and this full-replace is **PINNED for G2B** by `test_production_runner_gate_pause_resume.py:382` (`{"slide_count":3}` → `cache_prefix == edit_payload`) and for G2C by `test_production_runner_resume_continues_execution.py:197`. A targeted voice/variant pick needs a **surgical merge** (overlay `selected_*_id` onto the existing envelope, nest `voice_selection.selected_voice_id`) — which CHANGES that pinned contract. **Per governance this is the T5b party-mode milestone (binding-design ratification), not a unilateral change.** Options for the party: (A) gate-scoped merge for G2B/G4A only + re-pin the two tests to the new semantics; (B) a dedicated `pick`/`select` verb distinct from `edit` (no contract change to `edit`); (C) a `selection`-typed edit_payload the runner merges. **Recommend (B)** — a new `select` verb keeps `edit` full-replace intact and makes the picker semantics explicit.
- **Trial T5a (after party ratifies the binding verb/merge):** run to completion; operator picks a NON-default voice; assert the synthesized mp3s use the picked voice.
- **Exit:** voice pick re-routes (Class-A-free); flake budget respected.

---

## T5b — VARIANT PICKER MECHANICS (the big leap, mechanics half; D7). Gov: ⚠️heavy (Gary N-dispatch + distinctness axis likely manifest-adjacent). Auto: yes-after-party.
- **Party-mode milestone #2:** green-light the N-dispatch + distinctness-floor design + any manifest/pack touch (architecture pass scoped here per John/D8).
- **Scope:** operator sets N; Gary N-dispatches → N renders/slide into `variant_candidates`; per-slide `selected_variant_id` re-routes; **distinctness-floor** = vary a non-title axis (experience-profile/image-style/density) per dispatch so variants are materially selectable.
- **Trial T5b:** N=2; operator picks variant B on ≥1 slide; assert the chosen render flows downstream + Storyboard-A shows both.
- **Exit:** per-slide variant pick re-routes; variants visibly differ. **Deep segmentation distinctness explicitly deferred.**
- **Closes (mechanics):** `trial-4-binding-variant-voice-picker` (e/g picker half).

---

## T6 — REVIEW LANES b+c+d. Gov: light (c surface) + ⚠️check (d Tracy attach may need a node). Auto: yes / yes-after-party for (d).
- **(b)** surface the S0.2 ingestion report at G1 via a readable Marcus-facing report.
- **(c)** add a content-free lesson-plan-review pause after Irene Pass-1; operator approves/annotates plan_units.
- **(d)** wire Epic-28 Irene→Tracy plan-lock fanout onto the trial path; Tracy `suggested-resources.yaml`; review-only acknowledgment. **Non-blocking** — if attach slips, (d) defers.
- **Trial T6:** run exercises b+c review pauses + (d) if wired; all reach verdict cleanly.
- **Closes:** `beta-d-research-review-trial-path-attach` (if (d) lands); `tracy-gap-fill-lane-not-adopted-by-production-runner` (partial).

---

## T7 — MARCUS SPOC + SOURCES (a + SPOC; D3). Gov: light (wrapper over the existing seam). Auto: yes.
- **Scope:** conversational Marcus layer over `app.marcus.cli`: narrates each decision-card in persona w/ sanctum context, collects NL decisions, translates to `OperatorVerdict`, submits via shim, narrates resume. Sources/treatment (a) confirmed in dialogue (maps to `[c/e/s/x]`). Naming-collision documented.
- **Trial T7:** a full run driven entirely through Marcus conversation — no raw CLI verbs surfaced to the operator.
- **Exit:** every gate crossed via Marcus dialogue; subprocess seam intact (replayable).
- **Closes:** `marcus-interactive-experience-not-delivered-by-slab-7c` (BETA slice).

---

## T8 — MOTION-PLAN REVIEW (f; review-only). Gov: ⚠️heavy (new manifest motion-plan producer). Auto: yes-after-party.
- **Party-mode milestone #3:** green-light the honest motion-plan producer + manifest node, OR ratify the **carve-out** (f dropped from the BETA claim in writing) if an honest plan artifact isn't feasible in-budget.
- **Scope:** minimal honest `motion_plan` node (declared clips or explicit no-motion+rationale) between §07–§08; G2F reviews it; operator guides. **Synthesis stays deferred.**
- **Exit:** G2F reviews a real artifact (no theater), OR (f) is carved out + documented.

---

## BETA DRESS REHEARSAL ×2 (the goal gate; D4). Gov: light. Auto: yes.
- **Pre-req:** S0–T7 closed; S0.4 quality infra green; (d)/(f) present-or-carved.
- **Run 1 + Run 2:** integrated run on the FROZEN corpus through Marcus-SPOC exercising a+b+c+e (sources, ingestion-review, lesson-plan-review, variant-set + per-slide bind + voice bind), d+f review-only-or-carved. Both must satisfy §2 `error-free` (zero Class-A; Class-B within budget; no substrate change between runs).
- **Breadth (non-gating):** 1 cross-corpus run recorded as generalization evidence.
- **GOAL MET when both qualifying runs are error-free to spec.**

---

## Execution order (linear, with party-mode milestones)
```
S0.1 → S0.2 → S0.3 → S0.4  → [S0 gate]
  → T5a + trial            (light, autonomous)
  → [PARTY #2] → T5b + trial
  → T6 (b,c) + (d check)   (light + party-check for d)
  → T7 SPOC + trial        (light, autonomous)
  → [PARTY #3] → T8 or carve-out
  → DRESS REHEARSAL Run 1 → Run 2  → [GOAL]
```

## Risk register (party top-3, with the owning step)
1. **Live-only gaps / untested integrations (A23/P5, HIGHEST)** → mitigated by **S0.4** before any trial; every gate gets a live-dispatch assertion.
2. **Crash-vs-error-pause taxonomy** → **S0.1**.
3. **Manifest-touch breadth colliding with "twice"** → T5b/T8 carry the only manifest touches; they are gated behind party-mode and their *expensive* halves (deep distinctness, motion synthesis) are OUT of the twice-gate.

## Autonomy note
S0, T5a, T6(b/c), T7, and the dress rehearsals are fully autonomous (quick-dev + 3-lane self-review + trial). T5b and T8 pause for a party-mode green-light (manifest governance) — those are the planned milestone reviews per the goal. I proceed through the rest without pausing.
