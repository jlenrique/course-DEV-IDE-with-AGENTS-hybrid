# Operator HIL display + HUD requirements (captured mid-trial 2026-07-16)

**Trial witness:** `bc747b51-7009-4742-9f65-8de6abc29ca4`  
**Corpus:** `course-content/courses/tejal-apc-c1m1-p1-call`  
**Operator:** Juanl  
**Status at capture:** paused-at-gate **G0E** (trial intact; not crashed)

This note freezes operator requirements issued live during the Marcus-SPOC production trial so a post-trial code story can implement them without relying on chat memory. Canonical register rows live in [`deferred-inventory.md`](../../planning-artifacts/deferred-inventory.md) (§Named-But-Not-Filed + §HUD Next-Pass) and [`deferred-work.md`](../deferred-work.md).

---

## 1. HIL review surfaces MUST be tabular / containerized

**Requirement (binding preference):** Information presented for operator review and response must be structured into **tables or similar containers**. Free-scroll YAML dumps, long prose blobs, and one-line log warnings are **not reviewable** for HIL decisions.

**What worked in-session (reuse as acceptance exemplar):** when the chat agent re-projected G0E material as markdown tables, the operator could review and decide. Capture that shape as the target CLI/HUD pattern:

### Exemplar — gate identity

| Item | Value |
|---|---|
| Trial | `bc747b51-7009-4742-9f65-8de6abc29ca4` |
| Status | `paused-at-gate` |
| Gate | G0E |
| Ask | Confirm source TYPE manifest + candidate provisional LOs |

### Exemplar — enrichment summary metrics

| Metric | Count |
|---|---:|
| Typed components | 64 |
| Flagged ungrounded (advisory) | 12 |
| Provisional LOs | 14 |

### Exemplar — ungrounded advisory rows (one row per flag)

| # | component_id | parent | Kind |
|---|---|---|---|
| 1 | src-003-c005 | src-003 | Narration (Speaker Notes) |
| … | … | … | … |

### Exemplar — provisional LO rows (one row per LO)

| # | Statement |
|---|---|
| 1 | Define intrapreneurship as … |
| … | … |

**Inventory id:** `hil-operator-surfaces-must-be-tabular`  
**Apply to:** G0 directive composition printout, G0 enrichment advisory logs, G0E/G0R decision cards, CLI pause summaries, and any chat/SPOC narration of the same material. Machine JSON on disk may stay dense; **operator-facing display** must project into tables (paginated if >~15 rows per Marcus HIL Display Standards).

**Anti-pattern witnessed tonight:** after G0 confirm, enrichment printed a sheaf of `g0-enrichment: component '…' excerpt is NOT grounded…` log lines with no table, then `trial start` emitted a single JSON blob and returned to PowerShell — operator typed `c` thinking a G0-style prompt was still active (`CommandNotFoundException`). The trial was fine (`paused-at-gate G0E`); the **surface** failed the reviewability bar and the handoff cue.

---

## 2. HUD disconnected when the start walk returned

**Observation:** HUD + notifier launched during `trial start` (`--hud on`). After the start walk paused at G0E and the CLI printed the status JSON / returned to `PS>`, port `8791` was no longer LISTENING. Operator could not keep browsing the run surface across the pause boundary.

**Inventory id:** `hud-lifecycle-survives-gate-pause`  
**Fix intent:** HUD (and public overlay, when present) MUST stay alive across start-walk → gate pause → operator resume. Do not tear down HUD children when `trial start` returns `paused-at-gate`. Couple teardown only to terminal run status (completed / cancelled / abandoned) + explicit operator stop, with a short grace period (aligns with `hud-stable-public-live-url` lifecycle language).

---

## 3. Public read-only HUD page, stable URL, browse from any computer

**Requirement (reaffirmed):** Emit a **public, read-only** HUD page the operator can browse from any computer, ideally at an **unchanging URL**. Localhost remains authority; remote surface is read-only overlay.

**Existing inventory id (do not fork):** `hud-stable-public-live-url` (filed 2026-07-13; §HUD Next-Pass).  
**Tonight’s rider:** activation is overdue relative to this production trial; implement before the next steered HIL session if possible. Preserve: no anonymous quick-tunnel; identity-aware access; no secrets/resume digests on the public surface; same hostname survives run-to-run (`HUD offline / no active run` when idle).

---

## 4. HUD must show all ~14–15 run-defining toggles (current settings)

**Requirement (reaffirmed + expanded):** The HUD MUST display **all current settings that define a given run** (~14–15 toggles), not only a subset of modalities.

**Existing inventory id:** `hud-pre-run-settings-confirmation-surface`  
**Tonight’s rider:** standing **readout** of the full toggle set is mandatory for every live run (identity / settings panel), in addition to the already-filed **pre-walk confirm-or-change** gate. Minimum toggle set (from prior filing; keep in sync when new knobs appear):

| # | Toggle / setting |
|---|---|
| 1 | Component selection — deck |
| 2 | Component selection — motion |
| 3 | Component selection — workbook |
| 4 | Preset (`production` / `explore` / …) |
| 5 | Encounter mode (`recorded` / `live`) |
| 6 | LLM execution mode (`realtime` / `batch`) |
| 7 | `MARCUS_G0_DISPATCH_LIVE` |
| 8 | `MARCUS_RESEARCH_DISPATCH_LIVE` |
| 9 | `MARCUS_RESEARCH_DETECTIVE_LIVE` |
| 10 | `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE` |
| 11 | Voice-direction |
| 12 | `MARCUS_DECK_ENRICHMENT_ACTIVE` |
| 13 | `MARCUS_UDAC_ACTIVE` |
| 14 | Coverage-gate family |
| 15 | `MARCUS_TRIAL_BUDGET_USD` |
| 16 | Treatment slots A/B (+ styleguide picks when known) |

Witnessed tonight on operator-surface: only a thin `modalities` slice (e.g. `llm_execution_mode`, styleguide string) — **fails** this bar.

---

## 5. Next-action must NOT preselect Approve

**Requirement (binding):** the machine-emitted “what do I do next?” surface must not bias the operator toward Approve.

**Defect witnessed:** at G0R, `operator-surface.next_action.command` was a single paste string with `--verb approve` hardcoded. Chat agents that relay that string compound the bias. DecisionCard contract for G0R is `approve | edit | reject`; prompt text says *Marcus proposes; you decide*.

**Code pin:** `app/marcus/cli/next_action.py::build_next_action` — for `paused-at-gate` always interpolates `" --verb approve"` (approx. L71–79).

**Fix intent:**

| Do | Don’t |
|---|---|
| Present verb choices (approve / edit / reject) neutrally | Ship one approve-prefilled command as *the* next action |
| Build the concrete `trial resume … --verb <chosen>` only after the operator picks | “Document that approve is just a template” as the fix |
| Keep card-id + digest available for whichever verb is chosen | Imply Marcus/HUD already decided |

**Inventory id:** `next-action-must-not-preselect-approve`

---

## 6. BLOCKING — CD contribution missing before §06 (session end state)

**Trial end state:** `paused-at-error` / `builder.gary.upstream-missing`  
**Message:** `§06 builder missing upstream contribution(s): cd`  
**After:** G1 approve → walk through `04A` … `4.75` → `05` → `05B` → **06**

**Envelope specialists present:** `g0_enrichment`, `irene_pass1`, `irene_refinement`, `research_wiring`, `texas` — **not `cd`**.  
**Trace:** `node-enter 4.75` observed; **no** Creative Director production dispatch in `trace-fixture.json`.

**Inventory id:** `cd-contribution-missing-before-06-builder` — **first action next session.**

Artifacts (do not delete): `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/{error-pause.json,run.json,trace-fixture.json,irene-pass1.lesson-plan.json}`.

---

## Post-trial implementation checklist (for the story author)

1. Party-greenlight a HUD/operator-surface story (touches `operator_surface` assembler → lockstep / block-mode paths).
2. Implement tabular projectors for G0/G0E CLI + HUD gate cards (`hil-operator-surfaces-must-be-tabular`).
3. Fix HUD child lifecycle so pause ≠ teardown (`hud-lifecycle-survives-gate-pause`).
4. Deliver stable public read-only URL (`hud-stable-public-live-url`).
5. Project full run-settings matrix + pre-walk confirm (`hud-pre-run-settings-confirmation-surface`).
6. Neutralize gate next-action verb selection (`next-action-must-not-preselect-approve`).
7. Acceptance: replay tables against this trial’s `g0-enrichment.json` + `operator-surface.json` under `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/`.
