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

### G2C — _pending_

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
