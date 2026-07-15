# Workbook live HIL postflight — c1c7135f

- Trial: `c1c7135f-5b0d-4c59-bd5e-0bd58580b54b`
- Outcome: negative acceptance evidence; `paused-at-error`
- Last gate crossed: `G1`
- Stop coordinate: Irene Pass 1 / node `04A`
- Stable error class: `source.bundle.digest-mismatch`
- Observed message: extracted source body for `slides/slide-1-the-economic-structural-reality.md` disagreed with Texas authority
- Workbook produced: no
- Ask-A / Deep Dive reached: no
- Recorded provider cost: `$0.0000105` (two Texas `gpt-5-nano` calls; 50 input and 20 output tokens)
- Frozen run file count: `28`
- `error-pause.json` SHA-256: `1899c8fda1f7d3e233c410449b23536ae06f7a172679da3796f807906f2698ad`
- `run.json` SHA-256: `94eb23e055a5cafa6e720d04fb4045ca77bbb001997dc3c4cdbf56a818616d04`

## Root cause and correction

The run exposed a real Marcus-SPOC production defect at the Texas-to-Irene authority seam: the consumed source bundle could disagree with the authority representation after hardening. The correction now authenticates the full bundle and manifest, verifies exact primary projections and directive identity, uses transaction-safe resealing and recovery, reconciles dispatch results, and binds local-source coordinates plus exact captured bytes before parsing. This work improves the production SPOC runtime; it was not shaped merely to make the proofing vehicle pass.

The failed run remains frozen and was not retried. No provider call was made while implementing or verifying the correction. This record is not passing live acceptance evidence and does not close Story 38.3a.
