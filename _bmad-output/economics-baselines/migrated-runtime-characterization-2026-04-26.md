# Migrated Runtime Characterization — 2026-04-26

This characterization captures the 5a.3 cost-engineering foundation on the
migrated runtime for trial `C1-M1-PRES-20260419B`.

Because the live LangSmith workspace read is operator-window dependent, this
baseline was produced from the synthetic trace fixture at
`tests/fixtures/runtime/trial_cost_trace_fixture.json`, using the same runtime
cost machinery that writes `state/config/runs/C1-M1-PRES-20260419B/cost-report.{json,md}`.

## Total

- Trial ID: `C1-M1-PRES-20260419B`
- Measured at: `2026-04-26T23:11:40.709766Z`
- Total cost USD: `$0.171105`
- LangSmith trace URL shape: `https://smith.langchain.com/traces/<trace-id>`
- Cascade digest: `a1db8b2a0c9b6f86f094fe29d5e9bef6f560257511550144a0983196fe4adce6`
- Pricing digest: `385eb388eeb4e6a998af5df12656df6897b90281a67683f3ecfffd071e2e6dd2`

## Per-Agent

| Agent | Model | Calls | Cost USD |
| --- | --- | ---: | ---: |
| irene | gpt-5.4 | 2 | 0.056000 |
| quinn_r | gpt-5.4 | 2 | 0.033750 |
| marcus | gpt-5.4 | 1 | 0.033000 |
| enrique | gpt-5.4 | 1 | 0.020500 |
| vera | gpt-5.4 | 1 | 0.013500 |
| cd | gpt-5.4 | 1 | 0.011250 |
| desmond | gpt-5-haiku | 1 | 0.000930 |
| gary | gpt-5-haiku | 1 | 0.000820 |
| kira | gpt-5-haiku | 1 | 0.000725 |
| texas | gpt-5-haiku | 1 | 0.000630 |

Top contributors were `irene`, `quinn_r`, and `marcus`, which together account
for the majority of spend in this characterized run. That matches the intended
economics profile: higher-judgment editorial, review, and orchestration steps
remain on the stronger tier, while narrow dispatch-style specialists stay
right-sized.

## Per-Model

| Model | Cost USD | Share |
| --- | ---: | ---: |
| gpt-5.4 | 0.168000 | 98.19% |
| gpt-5-haiku | 0.003105 | 1.81% |

## Cascade Rationale

- `marcus`, `irene`, `vera`, `cd`, `quinn_r`, and `enrique` stay on `gpt-5.4`
  because they own orchestration, editorial synthesis, verification, or
  quality-sensitive packaging.
- `texas`, `gary`, `kira`, `compositor`, and `desmond` are assigned to
  `gpt-5-haiku` because they are dispatch-heavy or otherwise bounded tasks where
  faster, cheaper inference is appropriate.
- Alias coverage is explicit in config so substrate names stay stable across
  branch conventions, notably `quinn-r -> quinn_r` and `elevenlabs -> enrique`.

## Optimization Headroom

The largest remaining cost headroom is not in the already-right-sized
dispatchers; it is in repeat high-judgment passes on the premium tier. The best
next candidates for evidence-driven tuning are:

- Reducing duplicate `irene` editorial passes when one pass is sufficient.
- Testing whether one of the `quinn_r` review passes can be collapsed or moved
  down-tier without weakening acceptance quality.
- Keeping `marcus` and `vera` on the stronger tier unless later evidence shows a
  clear safety margin, because mistakes there would create wider downstream
  rework than the saved token spend justifies.

Soft-cap budgeting remains alert-only by design: `MARCUS_TRIAL_BUDGET_USD`
surfaces over-budget posture without halting a trial mid-run, which keeps M5
governance honest while avoiding operator-hostile partial executions.
