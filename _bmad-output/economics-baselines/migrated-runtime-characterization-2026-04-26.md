# Migrated Runtime Characterization — 2026-04-26

This characterization captures the 5a.3 cost-engineering foundation on the
migrated runtime for trial `C1-M1-PRES-20260419B`.

This 2026-04-26 refresh corrects the narrow-tier model ID from the earlier
fictional `gpt-5-haiku` placeholder to the live OpenAI catalog ID
`gpt-5.4-nano`, and it refreshes the pricing snapshot to current public rates.

Because the live LangSmith workspace read is operator-window dependent, this
baseline was produced from the synthetic trace fixture at
`tests/fixtures/runtime/trial_cost_trace_fixture.json`, using the same runtime
cost machinery that writes `state/config/runs/C1-M1-PRES-20260419B/cost-report.{json,md}`.

## Total

- Trial ID: `C1-M1-PRES-20260419B`
- Measured at: `2026-04-27T02:00:36.304166Z`
- Total cost USD: `$0.1179275`
- LangSmith trace URL shape: `https://smith.langchain.com/traces/<trace-id>`
- Cascade digest: `1ebeaf6b255f2eeeefea767442dbf71c24969957b4b9c9347cc9fa88a53c4e7e`
- Pricing digest: `9e858ad70b6a6034a7af61932c53c695ed13c0570b7f82bc6c7f27d725d46d96`

## Per-Agent

| Agent | Model | Calls | Cost USD |
| --- | --- | ---: | ---: |
| irene | gpt-5.4 | 2 | 0.040000 |
| quinn_r | gpt-5.4 | 2 | 0.023250 |
| marcus | gpt-5.4 | 1 | 0.022500 |
| enrique | gpt-5.4 | 1 | 0.014000 |
| vera | gpt-5.4 | 1 | 0.009000 |
| cd | gpt-5.4 | 1 | 0.007500 |
| desmond | gpt-5.4-nano | 1 | 0.000515 |
| gary | gpt-5.4-nano | 1 | 0.000445 |
| kira | gpt-5.4-nano | 1 | 0.000387 |
| texas | gpt-5.4-nano | 1 | 0.000330 |

Top contributors were `irene`, `quinn_r`, and `marcus`, which together account
for the majority of spend in this characterized run. That matches the intended
economics profile: higher-judgment editorial, review, and orchestration steps
remain on the stronger tier, while narrow dispatch-style specialists stay
right-sized.

## Per-Model

| Model | Cost USD | Share |
| --- | ---: | ---: |
| gpt-5.4 | 0.116250 | 98.58% |
| gpt-5.4-nano | 0.001677 | 1.42% |

## Cascade Rationale

- `marcus`, `irene`, `vera`, `cd`, `quinn_r`, and `enrique` stay on `gpt-5.4`
  because they own orchestration, editorial synthesis, verification, or
  quality-sensitive packaging.
- `texas`, `gary`, `kira`, `compositor`, and `desmond` are assigned to
  `gpt-5.4-nano` because they are dispatch-heavy or otherwise bounded tasks where
  faster, cheaper inference is appropriate.
- Alias coverage is explicit in config so Marcus specialist-registry IDs resolve
  cleanly against the economics-facing runtime names without renaming persisted
  trial artifacts.

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
