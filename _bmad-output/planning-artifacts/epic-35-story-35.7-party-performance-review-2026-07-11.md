# Story 35.7 — Party Performance Review of the Operator HUD (Live E2E) — 2026-07-11

**Gate:** terminal performance review of the Operator HUD during a live paid Marcus-SPOC production run.
**Run:** trial `69338610-23bc-4889-9bfb-fb64f0142a95`, corpus `tejal-c1m1-p4-assessments-bridge`, bundle `narrated-deck-with-workbook`, `realtime`, `--hud on`. Reached **status=completed** (terminal_gate G4A, silent_bypass_events 0, cost **$0.60**, `production_clone_launch_evidence=true`). First live integration of the entire HUD stack (contract/assembler/start-path/server/render/notifier).
**Party:** fully-spawned — Winston, John, Amelia, Murat + anti-consensus contrarians Splinter, Level.
**Instrument:** Murat's 10-item checklist (greenlight amendment 14) + scoped-verdict schema (amendment 2). Evidence: `_bmad-output/implementation-artifacts/evidence/hud-35-7-e2e-witness/` (FINDINGS.md + 5 projection snapshots + resume/verdict logs).

## Votes
| Seat | Vote |
|---|---|
| John (PM) | PASS-on-witnessed-surface; F-E2E-1 blocking must-fix before real operator use |
| Winston (architect) | PASS-on-witnessed-surface; architecture VINDICATED (both defects downstream of contract) |
| Murat (TEA) | PASS-on-witnessed-surface; F-E2E-1 = P0 fix-item gated by a cross-process execution test |
| Amelia (dev) | CONDITIONAL; F-E2E-1 kills JTBD#1; concrete fix ~0.5d |
| Splinter (contrarian) | CONDITIONAL; reject unqualified "PASS" as laundering the flagship failure |
| Level (contrarian claim-checker) | PARTIAL/PASS-with-fixes; evidence HONEST (no lie); workbook is flag-only (2-of-3 deliverables) |

## BINDING VERDICT (orchestrator synthesis — consensus, no impasse)

**CORE PROVEN LIVE; FLAGSHIP GATE-COMMAND FAILED — CONDITIONAL / PARTIAL PASS ON THE WITNESSED SURFACE.**

All six seats agree on the substance; the only divergence was whether the *label* may say "PASS" while JTBD#1 scored FAIL. Honoring Splinter's no-laundering fence, the verdict is stated without softening:

**What performed to spec, live (the anti-April core):**
- **Zero-lie held** — projection `envelope.status` matched `run.json` at every witnessed state (verified live at G0E, G2B, error, G4A, completed). *(Snapshot-only re-derivation of intermediate pauses is not possible post-hoc since run.json is now terminal — future witnesses must co-snapshot run.json; noted as a method fix, not a failure.)*
- **Assembler sole-writer emitted every transition** (seq 0→872; AD-2/AD-15 held).
- **Pre-flight** — 10 items incl. live OpenAI + Gamma heartbeats; SPOC spawn gated on all-green (AD-11).
- **Server + render live** — `/healthz` identity, `/projection` ETag `v1:N` + 304, GET-only; page rendered at every state incl. completed (AD-6, 35.4/35.5).
- **All three 35.9 briefing sections populated on real data** — `decision_card` (gate_focus/operator_prompt) at gates, `error_message` (verbatim message + node_index 32) at the error pause, `deliverables` (components + $0.60 + export_paths) at completion.
- **2 of 3 pause classes witnessed LIVE** — paused-at-gate (8 gates), paused-at-error (a real vision fault).
- Reached **completed** with real deck (23 slide PNGs) + motion (`slide-01.mp4`, 1.3MB).

**What FAILED / is not to spec (blocks operator use):**
- **F-E2E-1 [P0, BLOCKING] — flagship next_action command FAILED for the gate pause class.** The gate-class command block emits `gate decide …`, which returns `GateError: card_missing` when pasted cross-process (`gate_cli` reads an in-memory card store). JTBD#1 (the brief's #1-ranked job: the copy-paste-to-act command) is non-functional for the *most common* pause class. The run completed only because the operator used the undocumented `trial resume` path the HUD never showed. A confidently-rendered wrong command manufactures false trust — the April-class failure. (Error/batch classes correctly emit `trial recover`/`resume-batch`.) Root cause: `build_next_action`'s gate branch (35.2), masked by a round-trip test that asserted argparse *acceptance*, not execution.
- **F-E2E-2 [HIGH] — 4 ambient instrument surfaces empty mid-run.** `health`(FR9), `specialists`(FR7), `modalities`(FR10), `trace`(FR8) are null in all snapshots — the assembler's section-update APIs (35.2) exist but the runner never calls them during the walk. The witness-mode lifecycle warning firing on every emit is the spine *correctly detecting* the omission.
- **Deliverable completeness — 2 of 3 (production/pipeline issue, not HUD).** The `workbook` component flag is `true` but `workbook_producer` emitted a cache payload only — no `workbook.md`/`.docx` on disk. Deck + motion are real consumable artifacts; workbook is not.

**Classification (Winston):** both HUD defects are downstream of the contract — F-E2E-1 is producer-logic (wrong verb in a valid field), F-E2E-2 is a wiring gap (valid APIs never called). Neither is an architecture flaw; the spine is vindicated because the failures were *legible through it*, not hidden by it.

**Named live-witness DEBT:** `waiting_for_provider_batch` pause class (needs a `--llm-execution-mode batch` / LiteLLM run); live notification-during-run + DOM-preservation (browser→localhost was blocked this session; the 35.6 real ntfy receipt is banked separately); L2-golden promotion of the 5 snapshots.

**Operator-readiness gate (non-negotiable, all seats):** the HUD is **NOT authorized for real operator use** until (1) F-E2E-1 fixed AND re-witnessed end-to-end (gate command pasted → accepted first try, no card_missing) on a live run, and (2) F-E2E-2 emits non-empty ambient sections. SC5 (keep-it-open) remains L4, not decidable here.

## Story 35.7 disposition
The story's deliverable — a live E2E witness + a documented fully-spawned party performance review under the scoped-verdict schema — is COMPLETE. 35.7 is closed on that basis (the review happened and rendered an honest, documented, scoped verdict). The verdict being conditional does not un-author the story. The three findings become the **HUD operator-readiness follow-on** (filed in deferred-inventory), tracked for a fix arc before the HUD is put in front of the operator at a live gate.

---

# RE-WITNESS BINDING VERDICT (operator-readiness fix arc — 2026-07-12)

After the CONDITIONAL verdict above, the two blocking HUD defects were fixed and the run re-witnessed end-to-end on a completed live paid run (trial `31ff847c-78c3-4029-b554-ed34baaf7fc6`, $0.38, all 8 gates + terminal G4A). The SAME fully-spawned 6-seat party (incl. both contrarians) re-reviewed against the operator-readiness gate.

## Fixes landed
- **F-E2E-1 [was P0 BLOCKING] — FIXED (`ffc97f45`).** Gate-class `next_action.command` flipped from the dead-end `gate decide` (in-memory `_CARD_STORE` → `card_missing` cross-process) to `trial resume …` inline-verdict mode, converging on the proven `resume_production_trial` path. Re-witnessed: all 8 gates driven by pasting the HUD's OWN rendered command verbatim → **exit 0, zero `card_missing`**, run advanced to completed. Hermetic execution test added (`test_gate_command_reaches_resume_walk_cross_process`) closing the round-trip-vs-execution gap Murat's fence named.
- **F-E2E-2 [was HIGH] — FIXED (`ed9d1c25`).** Ambient section-update APIs are now called during BOTH walks (`_refresh_operator_surface_ambient`). Re-witnessed: `health`/`specialists`/`modalities`/`trace` NON-NULL at every checkpoint (roster grew 1→3→17; trace 66 events; modalities mode=realtime; health tiles incl. run cost). 18-test witness suite added.
- **2 production bugs (NOT HUD) surfaced by the run, fixed on their own merits per the SPOC-goal guardrail:** vision realtime `prompt_cache_key` bind (`247cf72d`); research `_normalize_figure` crash on non-numeric DOI/retrieval tokens (`5ace59f7`).

## Re-review votes (6 of 6)
| Seat | Vote |
|---|---|
| John (PM / operator stand-in) | **PERFORMED-TO-SPEC** — operator-usable YES; JTBD#1 now functional |
| Murat (test architect) | **PERFORMED-TO-SPEC** — items 3+5 now PASS; roster/trace populated |
| Winston (architect) | **PERFORMED-TO-SPEC** — defects resolved at predicted layers; spine held |
| Amelia (dev) | **PERFORMED-TO-SPEC** — fix plans faithful; execution-test gap closed |
| Splinter (contrarian, consensus-challenger) | **PERFORMED-TO-SPEC** — "my prior fence is CLEARED… a contrarian who rejects a cleared fence is just noise. This one is cleared. I accept it." |
| Level (contrarian, claim-checker) | **PERFORMED-TO-SPEC** — "the re-witness honestly supports it. Not a whitewash." All claims verified against artifacts. |

## BINDING VERDICT — HUD PERFORMED TO SPEC ON THE WITNESSED SURFACE (UNANIMOUS 6/6, no impasse)

Both blocking defects are genuinely cleared, verified live and in code by both contrarians. The operator-readiness gate's two non-negotiable conditions are MET: (1) F-E2E-1 fixed AND re-witnessed end-to-end (gate command pasted → accepted first try, no card_missing across all 8 gates); (2) F-E2E-2 emits non-empty ambient sections throughout. The HUD is authorized for real operator use on the witnessed surface.

**Carried-forward DEBT (non-blocking, contrarian-flagged, unanimously not gating):**
1. `waiting_for_provider_batch` pause class still un-witnessed live (needs a `--llm-execution-mode batch` / LiteLLM run).
2. Live notification-during-run + DOM-preservation browser-un-witnessed (browser→localhost blocked; 35.6 real ntfy receipt banked separately).
3. Workbook remains cache-only — deliverables are **2-of-3 consumable** (deck + motion real; workbook a true-flag with no artifact). Pre-existing PRODUCTION/pipeline gap (F-E2E-4), NOT a HUD defect.
4. Post-fix gate-paused projection JSON not recaptured as a saved artifact (proven by paste-log output-shape + `next_action.py:72` + G0E/G0R captured commands); capture + promote to L2 golden on the next gate-pausing run.

**Goal condition MET:** the active goal's terminal condition — "until the bmad party mode team reviews the performance of the completed HUD during a live E2E runner + Marcus-SPOC orchestrated E2E small production run and finds the HUD performed to spec" — is satisfied. The party reviewed a completed live small production run (3-slide deck + 1 motion video; workbook flag-only per debt #3) and unanimously found the HUD performed to spec on the witnessed surface, with named non-blocking debt.
