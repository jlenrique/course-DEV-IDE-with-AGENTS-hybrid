# Triage: `irene.pass2.figure-contradiction` on S8 Part-4 (trial `62308889`)

**Date:** 2026-07-09  
**Evidence:** `_bmad-output/implementation-artifacts/evidence/s8-tejal-p4-terminal-walk-20260709T001441/`  
**Error:** `scope=narration; slide slide-03 narration figures not present in perceived authority: ['percent:10', 'percent:90']`

## Verdict

**Gate correct. Product defect is upstream of Irene.**  
Not a corpus typo, not a mute matcher flake, not a false-positive figure gate.

## Causal chain (proven)

1. **Source teaches 10%/90%** — `course-content/.../slides/slide-1-summary-bridge-to-module-2.md`:  
   “Having the right idea is only 10% of the battle; the other 90% is …”
2. **Pass-1 / lesson plan retained that contrast** for the matrixed-health-system slide (rationale + source_refs carry `10%` / `90%`).
3. **Gary rendered under styleguide `hil-2026-apc-crossroads-classic` with `text_mode: condense`** (live `variant_gamma_settings`).  
   This **overrides** `DEFAULT_VARIANT_PAIR`’s Fidelity-L1 `text_mode: preserve` (shipped 2026-06-24 to stop Gamma re-minting / dropping figures).
4. **Gamma dropped the teaching numerals** and the illustration invented decorative **`92% PATIENT SATISFACTION`** (perceived HIGH authority).
5. **Vision perceived only `percent:92`** from `A_slide-03.png`.
6. **Irene Pass-2 narrated the source 10%/90%** (legitimate source grounding) →  
   `_assert_figure_citations_within_perceived` correctly raised `irene.pass2.figure-contradiction`.

## What is NOT broken

| Layer | Status |
| --- | --- |
| Figure-citation gate | Working as designed (narration ⊆ perceived deck) |
| Perception | Correctly reported on-slide `92%` |
| Gary title matcher / residue fix | Cleared this trial (`A_slide-01`…`05`) |
| Source corpus 10%/90% | Intentional teaching content |

## Durable fix options (product merit)

| Option | Shape | Merit |
| --- | --- | --- |
| **A (recommended)** | Change standard-A styleguide `text_mode` `condense` → `preserve` (align with L1 + DEFAULT_VARIANT_PAIR); pin regression that bound guide cannot silently demote preserve→condense without an explicit fidelity waiver | Stops figure drop at render; SPOC walks stop dying on honest source narration |
| **B** | Pass-2: never emit source figures absent from perceived (paraphrase without numerals) even when corpus carries them | Softens presenter latitude; treats deck loss as narration constraint rather than fixing render |
| **C** | Add `irene.pass2.figure-contradiction` to retry net | Deferred inventory option (b); absorbs variance, does not fix condense→figure-loss |
| **D** | One-off recover / re-render this trial with preserve override | Proof-only; not durable |

**Recommended:** pick named sibling **`hil-2026-apc-crossroads-classic-preserve`**
(identical to classic except `text_mode=preserve`). **Do not** mutate the approved
classic registry record ad hoc (operator 2026-07-09). B only as belt if preserve
still loses figures; C remains deferred; D forbidden as sole path.

## Next gate

Party green-light **A** via `bmad-quick-dev` → patch styleguide + guard → re-run Part-4 terminal walk (or recover from Gary if party allows narrower re-proof). S8 stays CLOSED until a walk clears Irene (or party redefines COMPLETE).
