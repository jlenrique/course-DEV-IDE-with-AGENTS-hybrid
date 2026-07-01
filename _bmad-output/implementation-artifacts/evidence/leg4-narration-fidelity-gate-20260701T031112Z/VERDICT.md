# Leg-4 narration-fidelity gate — TEETH WITNESS (offline, REAL Pass-2 artifacts)

**VERDICT: PASS.** The additive SOURCE-direction narration figure-fidelity gate
SAILS on a real gpt-5.5 Pass-2 narration and REJECTS both an unsourced
confabulation and a source-vs-deck conflict injected into the SAME real artifacts.
Flag-OFF firewall holds. "Wired isn't accepted until it rejects something" —
satisfied on real production output, zero live API calls, no full Pass-2 regen.

## Inputs (all REAL, on disk)
- Bundle: `scratchpad/leg3-c-u03-persubslide-bundle/`
- Source corpus: `extracted.md` (1194 chars; in-scope digit figures = `{percent:66}`)
- Narration: `pass2-output.json` (real gpt-5.5 output; in-scope digit figures = `{percent:66}`)
- Deck/perceived: `perception-artifacts.json` (3 slides, all perceived/HIGH)
- Reproduce: `PYTHONPATH=. .venv/Scripts/python.exe teeth_witness.py`
  (full console captured in `witness-output.txt`)

## Results
| Case | Input | Flag | Outcome |
|------|-------|------|---------|
| (i) sail | real narration as-authored | ON | SAILS deck- AND source-direction gates |
| (ii-a) unsourced | real narration + injected `$4.6B` | ON | RAISES `irene.pass2.figure-unsourced` (`money-trillion:0.0046` absent from source) |
| (ii-b) conflict | deck confabulates `60%` vs source `66%`, narration `60%` | ON | RAISES `irene.pass2.figure-source-deck-conflict` (routes repair to Gamma; VO never desynced) |
| firewall | injected-defect narration | OFF | INERT (no raise) — flag is the only seam |

## Real latent finding surfaced (not a witness failure — correct behavior)
Real deck perceived figures per slide from the actual perception artifacts:
- card-01: `{percent:66}`  (matches source — clean)
- card-02: `{}`
- card-03: **`{percent:91, percent:92}`** — **absent from the source corpus (source has only 66%).**

card-03 is a real instance of Gamma confabulating chart numerals (91%/92%) that
have no source provenance. The gpt-5.5 narration for card-03 happened to use only
word-form phrasing, so it did NOT cite them → the gate correctly does not fire
(the gate blocks NARRATED figures, never deck-only ones). This is precisely the
production defect class the Leg-4 reground + gate targets: had the narration
faithfully echoed the deck's 91%/92%, the gate would now block it instead of
shipping invented numbers over source truth.

## Guardrail
This closes a genuine SPOC-runtime defect (Irene narrating Gamma-confabulated
numerals over source truth on every run). It is not shaped to make any proofing
run pass — the proofing bundle here is only the witness vehicle.
