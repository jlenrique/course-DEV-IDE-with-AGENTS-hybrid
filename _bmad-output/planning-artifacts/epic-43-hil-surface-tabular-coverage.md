# Epic 43 — HIL Surface Tabular Coverage

**Status:** ✅ CLOSED 2026-07-17 — all 12 stories done + reviewed; 14 gate content types have bespoke tabular renderers; ratchet allowlist EMPTY; requirement `hil-operator-surfaces-must-be-tabular` completed (42-1 false-close corrected). Retrospective: `epic-43-retrospective-2026-07-17.md`. Green-lit 5/5 SIGN-WITH-RIDERS (party 2026-07-17 — Winston/John/Amelia/Murat/Sally; record `party-greenlight-epic-43-2026-07-17.md`).
**Author:** Marcus-orchestrator (session 2026-07-17), from operator directive "scope to all gates"
**Class:** S (substrate — operator surface / the product)
**Predecessor:** Epic 42 (Operator Surface Next-Pass). This epic **reopens** the requirement `hil-operator-surfaces-must-be-tabular`, which Epic 42-1 closed against only the G0/G0E slice.

---

## 1. Why this epic exists (honest framing)

The requirement note `_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md §1` ("HIL review surfaces MUST be tabular / containerized") carried an explicit **"Apply to" checklist**: *G0 directive composition printout · G0 enrichment advisory logs · G0E/G0R decision cards · CLI pause summaries · any chat/SPOC narration of the same material.* Epic 42-1 built the tabular projector (`app/marcus/cli/hil_tabular_projector.py`) but wired it only for **G0 identity + G0 enrichment**, then the requirement was marked ✅ done. It was satisfied on **~1 of ~15** operator-facing gate content types.

Live evidence (operator trial `5169a872`, 2026-07-17): the very first HIL review surface — the G0 directive confirm — rendered as a **raw YAML dump** of the directive (run_id / corpus / the full `sources[]` material-partition), the exact failure mode the projector was built to eliminate.

This is operator-surface hardening — **on-goal per the SPOC design guardrail** (the operator surface *is* the product; not proofing-run scaffolding).

## 2. Audited defect inventory (ground truth — two read-only code audits, 2026-07-17)

**Projector coverage today** (`hil_tabular_projector.py`): renderers exist ONLY for `render_gate_identity`, `render_enrichment_metrics`, `render_ungrounded_advisories`, `render_learning_objectives`. Reusable primitive: `_md_table(headers, rows)` at line 47.

**Wiring today** (`trial.py`): `_emit_gate_surface_if_paused` (265–330) returns early unless `status=="paused-at-gate"` and feeds the projector **only** `g0-enrichment.json` (`build_gate_surface` at :309). Net effect:
- G0 / G0E → real tables (the 42-1 slice).
- **Every other gate pause** → a 4-row identity table + a **dense stdout JSON blob** for the actual content.

**Confirmed raw dump:** `trial.py:364` `_confirm_or_edit_directive` → `print_fn(directive_path.read_text())` — pre-walk-synchronous, never reaches the projector. First-felt surface.

**All 14 gate poll-surfaces return machine dicts with NO projector renderer:**

| Gate | Module | Emitter | Content type (needs renderer) |
|---|---|---|---|
| G0 directive | section_02a | poll_surface.py:78 | directive / `sources[]` inventory |
| G1.5 estimator | section_04_5 | :73 | run-budget estimator |
| G1.5 run-constants | section_04_55 | :109 | run-constants lock |
| G1A plan-unit | section_04a | :145 | PlanUnit ratification |
| G2B per-slide mode | section_05_5 | :88 | mode selection |
| G2M A/B variant | section_07b | :90 | variant selection |
| literal-visual | section_06b | :90 | build targets |
| storyboard | section_07c | :92 | build targets |
| G2.5 motion-plan | section_07d | :81 | motion-plan status |
| G2F motion-clip | section_07f | :73 | motion-clip card |
| G3B storyboard/live-URL | section_08b | :73 | G3 card |
| G4A voice | section_11 | :81 | voice-candidate selection |
| G4B input-package | section_11b | :77 | input-package preview |
| G5 final handoff | section_15 | :79 | handoff artifacts + summary |

Plus **research packets** and **workbook** = gate content types with no renderer and no poll_surface.

**Coverage holes:** `recover_trial_cli` (`trial.py:1243–1259`) and `resume_batch_trial_cli` (`trial.py:1372–1379`) **never call** `_emit_gate_surface_if_paused` — re-pause on those front doors = zero tables.

**Drift debt (not a raw dump, but architectural risk):** the SPOC driver (`marcus_spoc.py` `narrate_gate` 1219–1271, `_narrate_g0_enrichment` 1086–1131, `_narrate_g0_refinement` 1185–1216) hand-formats the same G0E/G0R material as prose **independently** of the tabular projector — two renderings that can silently diverge.

**Confirmed NOT a defect:** `operator_surface_assembler.py:418` `yaml.safe_dump(directive)` is a guarded **file write** (directive-override projection), not a display.

## 3. Three non-negotiable pins (operator; generalized across ALL gates)

1. **No raw dumps to the human.** Every review surface stops dumping raw `read_text()`/JSON to the operator — the **tabular projection is the default** human view. Raw YAML/JSON stays available behind an explicit affordance (e.g. G0's `[e]dit` path). The `c/e/s/x` contract at G0 is preserved.
2. **A renderer per gate content type.** The projector gains an explicit renderer for each gate content type (reusing `_md_table`), starting with the **directive / source-inventory** table: columns `ref_id · role · locator · expected_min_words · excluded · brief-description(truncated)`; sorted primary-first; header line (run_id, corpus, gamma variants); counts footer (`N sources · P primary · S supporting · X excluded`).
3. **ACs name each surface + a structural coverage test.** Every story's ACs **name the specific surface(s)** (e.g. "G0 directive composition", "G4A voice-candidate selection") so a subset/G0E-only replay corpus can never re-close the requirement. The epic ships a **structural coverage test** asserting every gate poll-surface content type has a projector renderer — so a future new gate cannot silently regress.

## 4. Story roster (by slab — party may re-order / re-cut)

**Slab 1 — felt on every run**
- **43-1** G0 directive source-inventory renderer + kill the raw dump (all 3 pins; `c/e/s/x` preserved; `[e]dit` still opens raw YAML). Named surface: *G0 directive composition*.
- **43-2** Generic gate-content table + projector wiring: feed every paused gate's poll-surface dict into `_emit_gate_surface_if_paused` (stop identity-only + JSON blob); make `recover` and `resume-batch` call the projector. Named surfaces: *all paused gates (generic)*, *recover front door*, *resume-batch front door*.

**Slab 2 — structured selection surfaces (bespoke renderers)**
- **43-3** Variant/mode selection: G2B per-slide mode (section_05_5) + G2M A/B variant (section_07b).
- **43-4** G4A voice-candidate selection (section_11).
- **43-5** G1A plan-unit ratification (section_04a) + G1.5 estimator + run-constants (section_04_5 / section_04_55).

**Slab 3 — remaining gate content**
- **43-6** Build-target lists: literal-visual (section_06b) + storyboard targets (section_07c) + G3B storyboard/live-URL (section_08b).
- **43-7** Motion: G2.5 motion-plan (section_07d) + G2F motion-clip (section_07f).
- **43-8** G4B input-package (section_11b) + G5 final handoff (section_15).
- **43-9** Research-packet + workbook content renderers.

**Slab 4 — durability + governance**
- **43-10** Structural coverage test (pin 3): every gate poll-surface content type has a renderer; CI-fails when a new gate lacks one. *Candidate to land RED-first as the epic's acceptance ratchet — each story turns one row green.*
- **43-11** SPOC narration ↔ projector unification: shared builders OR a parity/anti-drift test so the two human renderings cannot diverge.
- **43-12** Governance close: reopen/split `hil-operator-surfaces-must-be-tabular` with each named surface as its own AC; correct the 42-1 closure record honestly; epic retrospective.

## 4b. Green-light riders (party 2026-07-17 — BINDING)

- **R1 (Winston):** Within Slab 1, land **43-2 generic gate-content scaffold + renderer registry FIRST**; 43-1 plugs G0's bespoke directive table into it. Both ship in Slab 1. Scaffold before bespoke — so no gate raw-dumps the instant Slab 1 merges, even if the epic stalls.
- **R2 (Amelia):** **Slab-0 fixtures prerequisite** — capture real `directive.yaml` / `decision-card-*.json` / poll-surface dicts from runs `5169a872` + `bc747b51` as frozen test inputs BEFORE any renderer. The generic renderer must **bound nested-value summarization** (reuse `_summarize_context_entry` 240-char pattern).
- **R3 (Murat):** **43-10 coverage test lands RED-first** as a registry test: enumerate all ~15 gate content types, assert each has a registered renderer, guarded by a **shrinking known-unrendered allowlist** (15→0). Each story closes by deleting its allowlist row; 43-12 fails if the list is non-empty. Pin 3 becomes mechanical, not prose.
- **R4 (Amelia):** **stdout machine-JSON / stderr human-surface split is a HARD INVARIANT** — re-asserted by any story touching the emit path (the 42-1 escape).
- **R5 (Sally):** Define the **raw-access affordance epic-wide** (not just G0's `[e]dit`) — "tabular default, raw one keystroke/path away" true at every gate, documented. Description column is **width-aware / fixed-width** (no ugly wrap at 80 cols).
- **R6 (John):** Sequence low-frequency gates (**43-7 motion, 43-9 research/workbook**) **last**.
- **R7 (Winston):** Operator-surface projection additions are **additive-within-v1** (AD-4/35.9) — new optional section, no schema bump for a render feature.

## 4c. Recommended dispatch order (party)

`Slab-0 fixtures` → **43-2** (generic scaffold + registry) → **43-10** (RED-first coverage test) → **43-1** (G0 directive bespoke) → **43-3** (variant/mode) → **43-4** (voice) → **43-5** (plan-unit + estimator/constants) → **43-6** (target lists) → **43-8** (input-package + handoff) → **43-7** (motion) → **43-9** (research/workbook) → **43-11** (SPOC unification) → **43-12** (governance close + retrospective).

## 5. Constraints

- **Pure-render** changes. Replay-testable against real `directive.yaml` / `decision-card-*.json` / poll-surface dicts from runs `5169a872` and `bc747b51` — **zero live spend** (fits the Paid-Run Economy Protocol).
- **Machine JSON on stdout stays** (wrapper-consumed). The **human surface** (stderr / interactive prompts) is what must tabulate.
- Dev agents read the operator-surface / HIL-projector conventions (Epic 42 / AD-4 / 35.9 additive-within-v1) at **T1 before coding** (per "review dev/admin guides before adding gates/agents/services").
- Pagination per Marcus HIL Display Standards (>~15 rows paginate).

## 6. Governance

Reopens `hil-operator-surfaces-must-be-tabular` (deferred-inventory) — 42-1 satisfied a subset. On epic close: each named surface becomes its own AC in that entry; the 42-1 closure record is corrected honestly (not a retroactive edit of 42-1's own scope — a truthful "requirement exceeded 42-1's delivered slice" note).
