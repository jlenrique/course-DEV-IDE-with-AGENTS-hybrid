# Trial 4 — Run Log & Post-Trial Capture

**Trial ID:** `d7ad4dac-7e65-4bde-9cb2-88a13fed2adc`
**Started (UTC):** 2026-06-19 ~04:50 (background task `bxrg6h1c0`)
**Branch:** `trial/4-2026-06-12` @ `e855d7d`
**Preset:** production · **Corpus:** `course-content/courses/tejal-apc-c1-m1-p2-trends` (APC C1·M1·P2 — macro healthcare trends; 6 slides / 6 narration segments — the cycle-6 certified lesson)
**Operator id:** `operator_juan` · **Runs root:** `state/config/runs/`
**Run dir:** `state/config/runs/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc/`
**Driver:** Claude acting as operator at G0/G1/G2C/G3/G4; **operator (Juan) tasked at G2B (storyboard-A variant pick) + G4A (voice pick)**.

## Posture (read before interpreting gate decisions)
- This is an **accept/review-posture** trial on the FROZEN certified engine. G2B/G4A surface the specialist evaluation in the card's `pick_context` and are **accept/reject pauses, NOT binding pick-from-N selectors** — an `edit` verdict does not re-route downstream (binding selection is a filed follow-on `g2b`/`g4a` enhancement). Frame operator decisions as "review the evaluation → approve or reject."
- Pause order: **G1 → G2B → G2C → G3 → G4 → G4A**.
- Known carry-forward risk to watch: 🟠 `v5-manifest-coherence-reconciliation` (v5 pack has no manifest-coherence guard by design — highest-probability post-trial bite).

## Commands issued (verbatim, for reproducibility)
| # | Gate | Command | Exit | Notes |
|---|------|---------|------|-------|
| 1 | G0→G1 | `python -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends --operator-id operator_juan --trial-id d7ad4dac-... --auto-confirm-directive --max-specialist-calls 12` | _running_ | bg task `bxrg6h1c0`; G0 directive auto-confirmed by Claude-as-operator |

## Gate ledger
_populated as each gate is reached: card_id, decision_card_digest, pick_context summary, verdict verb, rationale, resume status._

### G0 — Directive composition
- Status: **CONFIRMED** (Claude-as-operator, `--auto-confirm-directive`). Directive `directive.yaml`, digest `eb2cca3c…9d36`. `production_clone_launch_evidence: true`, LangSmith `measured-from-langsmith`.

### G1 — trial_open (Claude-driven) → APPROVED over a drafted-reject
- **card_id:** `78657538-4898-40b0-8f3b-ecb88fd6ea7a` · **outer digest:** `7f63edbe…2c39`
- **Drafted proposal (automated):** `reject` / `halt-for-repair`, confidence 0.73. Signals: `artifact_paths_empty`, `overall_status_complete_with_warnings`, `dispatch_exit_code_10`, `duplicate_output_digest`, `irene_packet_unverifiable`, `g0_word_count_above_floor`.
- **Investigation verdict — drafted-reject is a FALSE NEGATIVE.** Bundle on disk is real & complete: `manifest.json` lists 5 artifacts with real sha256/sizes; `extracted.md` (6.8KB) has all 6 slides fully extracted (narration speaker-notes + visual formats + references + `[evidence: src-001]` provenance). Content is genuinely present.
- **🔴 FINDING T4-F1 (harvest to postmortem):** the G1 drafted-`reject` fires on the **Texas specialist-summary's "Emitted artifacts: none"** list, which is a *provenance-reporting gap* — the summary is not wired to the bundle manifest (which lists 5 real artifacts). Compounded by a **double Texas dispatch**: two identical summaries 1.9s apart (`texas-…045636…` + `…045638…`) → drives `duplicate_output_digest` + `dispatch_exit_code_10`. Net: the gate's auto-recommendation is a false-negative over real content. Candidate fixes: (a) wire Texas summary "Emitted artifacts" to the bundle manifest; (b) de-dupe the Texas dispatch / understand the exit-10 retry; (c) make the G1 drafted-proposal read the bundle manifest, not just the specialist summary.
- **Operator (Claude) decision:** **`approve`** — real content present; this is the certified cycle-6 corpus; weed-clearing posture = continue the probe + log the finding. Verdict at `operator-verdict-G1.json`.
- Resume → next pause **G2B** (operator decision point).

### ⛔ ERROR-PAUSE at node 07 (Gary) — BEFORE reaching G2B
- **status:** `paused-at-error` · `paused_gate: null` · last gate crossed: G1 · node_index 19.
- **Error tag:** `gamma.export.brief-unmatched` — "gamma export left briefed slide(s) unmatched for variant A: `['slide-05','slide-06']`; unmatched pages: `['A-System-Under-Pressure','Closing-the-Leadership-Gap-The-Case-for-Clinician-Leaders']`".
- **🔴 FINDING T4-F2 (major):** this is the **known WAVE-0 storyboard-correctness defect** root-caused in the 2026-06-17 cycle-6 review — Gamma renames/collapses briefed topics, and Gary's **positional page→slide_id mapping** can't match the renamed pages back to `slide-05`/`slide-06`. The taxonomy re-base correctly converted Gary's failure from a CRASH into a recoverable **error-pause** (working as designed). The actual fix is the **title-based page→slide_id matching** code change — which was the *recommended-but-not-yet-landed* WAVE-0 storyboard-correctness dispatch (2026-06-17 handoff "recommended immediate next action"). **It had not landed before this trial launched.**
- Upstream nodes succeeded with `provenance: real`: texas (02/03, double-dispatch exit-10 per T4-F1), CD (04A), irene pass-1 (05). The deck export is where it stops.
- **Decision (operator, 2026-06-19): COMPLETE THE TRIAL ON ITS OWN TERMS** (accept/review posture) to get past it; the real per-slide variant picker becomes the next trial's leap. Clear Gary via `trial recover` (re-roll Gamma; cycle-6 got 6/6 on this corpus). Escalate to the title-matching fix only if recover fails identically.
- **Recover attempt #1 (`trial recover`): FAILED WORSE.** Fresh Gamma layout named pages `Module-1 … Module-6-Case-for-Change`; **5 of 6 briefed slides unmatched** (`slide-02..06`), incl. a merged `Module-4-and-5` page. Disproves the transient/re-roll hypothesis → **systematic defect.** `production_clone_launch_evidence` dropped to `false` on this attempt.
- **🔬 DEEPER ROOT CAUSE (supersedes T4-F2's first read):** the **title-based matcher already landed** (`gary/_act.py:177`, party-ratified 2026-06-18) and is doing its job — it fail-louds because **Gamma free-titles its pages** ('Module-1', 'A-System-Under-Pressure') so they don't title-contain the briefed slide titles, and it sometimes **merges topics** (6 briefed → 5 pages). The matcher correctly refuses a silently-wrong mapping. **The true gap is UPSTREAM in the Gamma *generation* call** (`gary/_act.py:122 _input_text` + `generate_deck`): the brief's slide titles are NOT pinned as the card titles, so Gamma invents its own and may merge. No downstream matcher can fix that. **Real fix = constrain Gamma generation to pin per-card titles to the briefed slide titles (+ decide the topic-merge case).** This is a contained code change in the generation path, not the matcher.

### G2B — NOT REACHED (operator decision: storyboard-A variants)
- ⚠️ **Expectation-reconciliation (operator raised mid-run):** operator's mental model of G2B = *per-slide pick-from-N variant selection from the published Storyboard-A HTML, choosing which variant goes downstream for each slide.* As wired this trial, G2B is **NOT** that — it is an accept/review pause (`selected_*_id` is write-only; an `edit` verdict does not re-route downstream). The interactive per-slide pick-from-N selector is the **filed/deferred follow-on**, not Trial-4 substrate. This mismatch is recorded as **FINDING T4-F3** (the trial cannot satisfy the operator's stated variant-selection goal in its current form).

### G2B — variant pick (OPERATOR DECISION: storyboard-A variants)
- Status: _pending_

### 🔧 ENGINE FIX (T4-F2 resolution) — Gamma generation title-pinning + card-count pinning
- **Files:** `app/specialists/gary/_act.py` (+ `tests/specialists/gary/test_gary_gamma_dispatch.py`).
- **Root cause:** Gary's `generate_deck` call let Gamma free-generate card count + titles (`text_mode=generate`, no `card_split`), so Gamma merged 6 briefs → 5 pages and invented titles (`Module-1`, `A-System-Under-Pressure`) that the (correct, frozen) bijective title-matcher couldn't bind.
- **Fix (two coordinated levers):**
  1. **`card_split="inputTextBreaks"`** on the generation call → Gamma emits exactly one card per `\n---\n` chunk (kills the 6→5 merge/cardinality failure).
  2. **`_input_text` leads each chunk with `# {title}`** via a new shared `_slide_title(slide, index)` helper that `expected_slots` ALSO uses → the Gamma card heading and the matcher's expected key are the *same string by construction* (cannot drift). Plus strengthened `additional_instructions` ("use each section heading as the card title verbatim; one card per section; no cover/agenda/summary; don't merge/split").
  3. **Edge hardening:** body sanitizes any embedded `\n---\n` (now load-bearing under inputTextBreaks).
- **Matcher untouched** — its fail-loud guards remain; if Gamma still misbehaves, Gary error-pauses recoverably (no silent regression).
- **Validation:** ruff clean; 57 Gary tests pass (1 new: `test_gary_generation_pins_titles_and_card_split`); 26 package-builder/title-matching regression pass; lint-imports 13 kept. 3-lane self-review: Blind/Edge/Acceptance — 1 edge finding (load-bearing delimiter) applied.
- Spec: `_bmad-output/implementation-artifacts/spec-gamma-title-pinning-card-split.md`.

### ✅ Recover #2 (post-fix): Gary CLEARED — fix validated on live path
- The title-pinning fix got the walk **past Gary node 07 for the first time** (advanced to node 07B quinn-r). The Gamma generation fix is confirmed working live. (Stale `error-pause.json`/`run.json` still show the old Gary message — the subsequent crash didn't overwrite them.)

### ⛔ NEW BLOCKER #2 — node 07B quinn-r crash (`ModeMismatchError: gate_id ''`)
- **Crash (NOT a recoverable error-pause):** `app/specialists/quinn_r/_act.py:72 ModeMismatchError: unknown Quinn-R gate_id/gate_phase: ''` at node 07B. `ModeMismatchError(ValueError)` is outside the `SpecialistDispatchError` family → it propagated as an uncaught exception (CLI exit 1), so the trial did NOT pause cleanly.
- **🔴 FINDING T4-F4 (major; defect in THIS session's Arc-1a wake):** quinn-r's mode is selected from `payload["gate_id"]` (`GATE_MODES={...,"G2B":"variant",...}`). The dispatch derives that gate_id from the **node's `gate_code`** (`production_runner.py:808` `_runner_payload_for_specialist`). **Arc-1a (2026-06-18) MOVED `gate_code:"G2B"` off node 07B onto the separate `07B-gate` node** to make the wake pack-neutral — which stripped node 07B's quinn-r mode signal. So node 07B (the variant-eval quinn-r) dispatches with empty gate_id → `_mode()` can't resolve → crash. Offline tests missed it (live dispatch path; the structural guard checked template+shim existence, not that 07B passes a gate_id). Same class the Blind Spot lane warned about.
- **Fix locus:** `production_runner.py` dispatch-side (NOT the manifest → not a `block_mode_trigger_paths` edit → same governance tier as the Gamma fix). Make node 07B's quinn-r dispatch resolve gate_id="G2B" (variant mode) — cleanest via deriving it from the associated woken gate (`07B-gate.gate_code`, `insertion_after: 07B`). Secondary hardening candidate: `ModeMismatchError` should arguably be in the recoverable family so a mode-miss error-pauses instead of crashing.
- **Status:** HELD — reported to operator (2nd fix in a cascade; weed-clearing trial surfacing live-only gaps as designed).

### 🔧 ENGINE FIX #2 (T4-F4 resolution) — node 07B Quinn-R variant gate_id
- **File:** `app/marcus/orchestrator/production_runner.py` (+ `tests/unit/marcus/orchestrator/test_quinn_r_variant_gate_code.py`). **NOT a manifest edit** → outside `block_mode_trigger_paths` → same governance tier as the Gamma fix.
- **Fix:** new `_effective_quinn_r_gate_code(node, manifest)` — returns `node.gate_code` when present, else resolves it from the **content-free** woken gate (`specialist_id is None`) inserted after the node. Distinguishes `07B-gate`/G2B from the sibling CONTENT gate `07C`/G2C (both have `insertion_after: 07B`). Threaded `manifest` into the shared `_dispatch_specialist_at_node` (both walkers); dispatch now passes `gate_code=_effective_quinn_r_gate_code(node, manifest)` instead of bare `node.gate_code`. → node 07B Quinn-R now dispatches with `gate_id="G2B"` (variant mode).
- **Deferred hardening (harvest):** `ModeMismatchError(ValueError)` should join the `SpecialistDispatchError` family so a future mode-miss error-pauses recoverably instead of crashing. Not done now (changes quinn_r exception hierarchy; risk of test ripple) — filed as follow-on.
- **Validation:** ruff clean; 23 targeted (new helper test pins 07B→G2B, 07C→G2C, no sibling-borrow) + 303 marcus/quinn_r/gary regression pass (1 skip); lint-imports 13 kept. 3-lane self-review done.
- Spec: `_bmad-output/implementation-artifacts/spec-quinn-r-07b-variant-gate-id.md`.

### ✅ G2B — variant review (OPERATOR DECISION) → APPROVED
- Reached cleanly after both fixes (`status: paused-at-gate, paused_gate: G2B`). **card_id** `5440307b-9caf-4801-8c7e-480ddfb0a3cc` · **digest** `f2ffc60c…c57c`.
- **Deck validated:** 6/6 slides matched bijectively, correctly titled (incl. slide-05 "Leadership Gap" which orphaned twice pre-fix). Real, on-brief renders (operator + Claude viewed slide-01 + slide-05). `single-dispatch` (1 variant/slide; `variant_candidates: []`).
- quinn-r variant-mode eval completed/approved (`qrr.parsed.ok`, gpt-5). Reporting nit (harvest): quinn-r summary "Emitted artifacts: none" (thin pick_context, sibling of T4-F1).
- **Operator (Juan) verdict: `approve`** (2026-06-19) — deck good, nothing to reject, Storyboard-A visual review is at G2C. Verdict at `operator-verdict-G2B.json`.

### ✅ G2C — Storyboard A publish + Gate-2 QA approval → APPROVED (operator-reviewed)
- **card_id** `eeebca99-8998-41ff-935d-d49149a0943d` · **digest** `d5f05c5e…9b1a` · readiness `ready`, blocking_issues `[]`.
- **Storyboard A PUBLISHED ONLINE:** https://jlenrique.github.io/assets/storyboards/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc/index.html (8 files, publish receipt OK). Local: `exports/storyboard-A-pack/storyboard/index.html`. URLs posted to project-root `TRIAL-4-URLS.txt` per operator.
- **Operator reviewed the published Storyboard A: "looks great; Script Notes align with slides."** Verdict `approve` (2026-06-19). `operator-verdict-G2C.json`.

### ⛔ ERROR-PAUSE #3 at node 08 (irene pass-2) — `irene.pass2.slide-join-failed`
- Recoverable error-pause (not a crash). Guard `_assert_narration_joins_roster` (`irene/graph.py:157`): a narration_script exists but its `segment_manifest_deltas[].visual_references[].perception_source` referenced **no** roster slide (`referenced` set empty; orphans `[]`). The prompt already mandates perception_source∈roster (graph.py:271) → looks like LLM-output variance, not a wiring bug.
- **Finding T4-F5:** irene pass-2 (gpt-5.4) produced narration that didn't carry slide-join metadata. Recover-first (re-roll the LLM) is the right action — cycle-5/6 produced 6 conforming segments on this corpus. If recover fails identically → systematic → strengthen the pass-2 prompt/schema-enforcement.
- **Action:** `trial recover` (re-roll node 08).

### ✅ Recover #4 (irene re-roll): CLEARED — T4-F5 was LLM variance
- One `trial recover` re-rolled node 08; irene pass-2 produced conforming narration (perception_source joins roster). Confirms T4-F5 = LLM-output variance, not a wiring bug (prompt already correct). **Storyboard B published:** https://jlenrique.github.io/assets/storyboards/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc-b/index.html. No code fix needed.

### ✅ G3 — motion-clip approval (Claude-driven) → APPROVED
- **card_id** `9a89334d-d2e0-4684-bbdf-4b6b0b49d228` · **digest** `a4e47d46…d35e` · gate_focus `motion_clip_approval` · progress 50% · no blocking issues.
- Narrated-deck deliverable → no motion expected (`motion_receipts: []` is the certified-correct state; motion leg structurally unproven per project-context 2026-06-13, out of scope here). **Claude verdict: `approve`.** `operator-verdict-G3.json`.
- Pending nodes → 10, 11 (elevenlabs narration), 11-gate (**G4A voice**), 11B/11B-gate, 12-15.

### ✅ G4 — fidelity gate (Claude-driven) → APPROVED
- **card_id** `ab77fac7-bcd7-4700-85e0-96d71e8a78e9` · **digest** `9f4e263d…4973` · gate_focus `fidelity_gate` (Vera) · active node 10.
- `final_status: "partial"` = run-completeness (mid-pipeline, audio not yet generated), NOT a fidelity defect. Vera ran real (`ftr.parsed.ok`), fidelity traces written under `fidelity/`; no blocking issues. **Claude verdict: `approve`.** `operator-verdict-G4.json`.
- Resume runs node 11 (ElevenLabs narration) → next pause **G4A (voice)**.

### ✅ G4A — voice selection (OPERATOR DECISION) → APPROVED
- **card_id** `e9f7a534-4186-41d7-9b83-afed23346df4` · **digest** `d5c24f2c…3696` · gate_focus `voice_selection`.
- Enrique (real, `elevenlabs.dispatch.ok`) produced **3 voice options with playable samples** — defaulted to recommended **Roger** (`CwhRBWXzGAHq8TQ4Fs17`, laid-back am. male). Alternates: Sarah, Laura. Sample URLs posted to `TRIAL-4-URLS.txt`. NOTE: unlike G2B, G4A surfaced REAL `voice_preview.voices` (3) with sample_audio_url — the card's `voice_candidates: []` is the structured-parsing gap, but the evidence carried the options (harvest: wire voice_preview.voices → card.voice_candidates).
- **Operator (Juan) verdict: `approve`** (accept Roger). Same accept/review posture — alternate pick non-binding this trial (deferred picker). `operator-verdict-G4A.json`.

### → DRIVE TO COMPLETION (compositor / assembly nodes 11B → 15)

### 🏁 TRIAL 4 COMPLETE — `status: completed` (2026-06-19T06:08:40Z)
- **Full pipeline G0 → completion**, no remaining pause, no error. `production_clone_launch_evidence: true`.
- **Narration synthesized: 6/6 real ElevenLabs segments** (Roger voice): seg-01..06 = 37.0/42.7/43.1/37.3/34.5/34.3s, all OK. MP3s at `enrique-narration/assembly-bundle/audio/seg-0{1..6}.mp3`.
- **Assembly bundle** built (`enrique-narration/assembly-bundle/`) + compositor hand-off summary.
- **Cost: $0.240** total. LangSmith trace: https://smith.langchain.com/traces/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc. Per-model: gpt-5.4 $0.130 (irene_pass1), gpt-5 $0.108, gpt-5-nano $0.003.
- **6 gates crossed:** G1 → G2B → G2C → G3 → G4 → G4A. Operator owned G2B (variant) + G4A (voice); Claude drove G0/G1/G2C/G3/G4.

## OUTCOME SUMMARY
**First operator-in-the-loop Trial-4 run, full pipeline, completed.** Required **2 substrate fixes + 1 LLM re-roll** to get through (the trial did its weed-clearing job — surfaced live-only gaps that the offline suites hid).

### Engine fixes landed + pushed (governance-light, dispatch/specialist tier; NOT manifest)
1. **`10befac` Gamma title-pinning + card-split** (T4-F2) — `card_split=inputTextBreaks` + title-led chunks via shared `_slide_title`. Cleared Gary deck export (was failing `gamma.export.brief-unmatched` on slides 5/6).
2. **`1b629f3` node-07B quinn-r variant gate_id** (T4-F4) — `_effective_quinn_r_gate_code` derives the mode-selecting gate_code from the content-free woken gate. Cleared the `ModeMismatchError('')` crash (a defect in this session's own Arc-1a wake).

### Findings harvested (for postmortem → `docs/trials/cross-trial-learnings.md`)
- **T4-F1** (nit): G1 drafted-`reject` is a false-negative driven by the Texas specialist-summary's "Emitted artifacts: none" (not wired to bundle manifest) + a double Texas dispatch (exit-10). Recurs for quinn-r/vera/enrique summaries (all say "Emitted artifacts: none"). Fix: wire specialist-summary artifact lists to the bundle/output manifest.
- **T4-F2** ✅ fixed (Gamma title-pinning).
- **T4-F3** (design): G2B variant pick is accept/review only (`variant_candidates: []`, `selected_*_id` write-only, edit non-binding). The operator's per-slide pick-from-N picker = the deferred "big leap" for the next trial. Also this run was single-dispatch (one variant/slide).
- **T4-F4** ✅ fixed (07B gate_id). Deferred hardening: put `ModeMismatchError` in the `SpecialistDispatchError` family so a mode-miss error-pauses instead of crashing.
- **T4-F5** (LLM variance): irene pass-2 `slide-join-failed` cleared on one re-roll. Prompt already correct; consider tightening output-schema enforcement of `perception_source` if it recurs.
- **T4-F6** (harvest): G4A surfaced REAL voice options (`voice_preview.voices` ×3 with sample URLs) but `card.voice_candidates: []` — wire `voice_preview.voices` → `card.voice_candidates` so the picker has structured data (prereq for the binding voice picker).

### Recommended next steps
1. **The "big leap" (next trial):** build the binding pick-from-N variant + voice selectors (T4-F3 + T4-F6) so operator picks re-route downstream per slide.
2. File T4-F1/F5/F6 + the two fixes to `docs/trials/cross-trial-learnings.md` and deferred-inventory per trial-postmortem governance.
3. Land the `ModeMismatchError`→recoverable hardening (cheap, deferred from fix #2).

### G3 — _pending_

### G4 — _pending_

### G4A — voice pick (OPERATOR DECISION: narration voices)
- Status: _pending_

## Artifacts to harvest at close (post-trial follow-up)
- [ ] `run.json` final status
- [ ] `trial-start.json`, each `trial-resume.json`
- [ ] every `decision-card-<gate>.json` (card_id + digest + pick_context)
- [ ] every authored verdict JSON
- [ ] cost report (`cost_report_json` / `.md`) — token spend
- [ ] LangSmith trace status / link
- [ ] directive (`directive.json` or composed path) + digest
- [ ] storyboard A + B HTML (publish URLs) — fidelity review input
- [ ] narration mp3 segment paths + voices used
- [ ] any error-pause tags (`paused_error_tag`) + recovery actions
- [ ] anomalies / glitches for the postmortem (cross-trial-learnings.md routing)

## Findings / anomalies (live)
_log as observed_
