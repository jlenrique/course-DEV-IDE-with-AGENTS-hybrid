# PROOF — Irene Pass-2 figure-contradiction speakable-contract fix

**Trial:** `22b27500-6e67-4dd7-8308-fd89defe3d99`  
**Evidence:** `irene-figure-contradiction-reenter08-20260710T054100Z`  
**Flag:** `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE=1`  
**Claim:** Generation-side dual-view — spoken digit-form figures ⊆ per-slide perceived speakable set; source provenance does not license speech; unrendered source figures redacted from prompt corpus; always-on gate `irene.pass2.figure-contradiction` unchanged.

## Mechanism (unit)

- `tests/specialists/irene/test_irene_pass2_source_figure_fidelity.py`
- `tests/specialists/irene/test_irene_pass2_perceived_visual_authority.py`
- **Result:** 29 passed (includes Tejal slide-05 empty-deck fixture + gate still fail-loud on injected 10%/90%)

## Gen-context snapshot (pre-live)

See `gen-context-snapshot.json`:

- `slide_05_perceived_figures`: `[]`
- `speakable_header_present`: true
- `slide05_none_line`: true
- `unrendered_token_present`: true
- `source_wins_phrase_absent`: true
- corpus region has no raw `10%` / `90%`

## Field confirmation (reenter@08)

| Check | Result |
| --- | --- |
| `reenter_at_node=08` | → `paused-at-gate` **G3** (Pass-2 cleared) |
| `irene.pass2.figure-contradiction` recur? | **No** |
| Node `08` on envelope | **Yes** (`irene`) |
| Any `10%` / `90%` in narration_script | **No** |
| slide-05 text | Paraphrase without digit-form figures (carrier / human capacity) |
| Downstream | G3→G4→G4A; Enrique 9/9 OK; Desmond handoff parse failed (out of claim) |

## Verdict

**PASS-WITH-FENCES**

- **PASS** for the figure-contradiction / speakable-contract claim (mechanism + field).
- **Fence:** full Tejal walk not completed — paused at G4A after Desmond `HandoffParseError` (Automation Advisory). Separate from this fix.
- **Fence:** single live sample; mechanism pinned in unit (Murat F5-allowed).

## Party amendments honored

- Keep always-on `figure-contradiction` gate (bailiff)
- Speakable block always-on; NFR-I6 carve-out documented in `_assemble_pass_2_prompt`
- No SOURCE WINS / narrate-source-over-slide
- Per-slide speakable; tests updated before liveproof
- Gen-context snapshot required — present
