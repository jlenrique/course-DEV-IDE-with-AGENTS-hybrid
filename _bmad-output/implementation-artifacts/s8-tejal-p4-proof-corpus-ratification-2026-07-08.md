# S8 Tejal Part 4 Proof Corpus Ratification - 2026-07-08

## Operator Declaration

The operator named the S8 full-close proof corpus:

```yaml
lesson_slug: "tejal-c1m1-p4-assessments-bridge"
corpus_path: "course-content/courses/tejal-c1m1-p4-assessments-bridge"
proof_intent: "S8 full-close composed proof"
expected_bundle_id: "narrated-deck-with-workbook"
hil_operator: "juanl"
freshness_attestation: "exception_with_rationale"
allow_tejal_exception: true
no_corpus_specific_diffs_acknowledged: true
```

The operator explicitly ruled out substituting HAI 510, PHS 620, Part 2, Part 3,
or fixture/smoke corpora.

## Party Ratification

- John ratified the Tejal exception because it is explicitly scoped and does
  not broaden product scope or justify proofing-only production changes.
- Winston ratified the exception as proof data availability, with a hard rule
  that production app/runtime code remains corpus-generic and contains zero
  Tejal/HAI/PHS slug literals.
- Murat ratified with gates: preflight green, exact corpus shape, README
  provenance and gaps, local Marcus-SPOC HIL proof, no
  `--auto-confirm-directive`, and no `--allow-offline-cost-report` unless the
  close claim is explicitly downgraded.
- Paige ratified with downstream-consumer requirements: README and evidence
  notes must state source authority, Tejal exception, HAI/PHS deferral,
  expected bundle, known gaps, and the difference between source-backed
  material and missing-source placeholders.

## Done Bar Reconfirmed

S8 full close still requires:

1. Curated Part 4 corpus in the named path.
2. Preflight green against operator attestations and explicit exception flags.
3. Ratified lesson-plan collateral/input wrapper selecting
   `narrated-deck-with-workbook` with present workbook collateral.
4. Local Marcus-SPOC / trial composed proof with real HIL verdicts by `juanl`.
5. Evidence pack.
6. Final BMAD party concurrence that S8 itself is complete.

S8 is not complete at this ratification checkpoint.

## Checkpoint Evidence

Corpus preflight:

- `scripts/utilities/check_s8_proof_corpus.py`
- `tests/utilities/test_check_s8_proof_corpus.py`
- Focused checker tests: `8 passed`.
- Ruff: clean.
- Named corpus preflight: `ready: true` with expected source-gap warnings for
  missing PDF, DOC/deck, image, and DOI accepted only because
  `--allow-source-gaps` was paired with
  `references/source-gap-ledger.md`.

Ratified collateral intent:

- `_bmad-output/implementation-artifacts/s8-tejal-p4-ratified-collateral-intent.yaml`
- Resolver result: `narrated-deck-with-workbook`.
- Component selection: `deck=true`, `motion=true`, `workbook=true`.
- This result is valid because the artifact carries
  `collateral.declaration: present` with a real workbook payload. It does not
  claim workbook selection from `ComponentSelection` alone.

Attempted local trial-start witness:

```powershell
.\.venv\Scripts\python.exe -m app.marcus.cli trial start `
  --preset production `
  --input course-content\courses\tejal-c1m1-p4-assessments-bridge `
  --operator-id juanl `
  --trial-id 8d1d1111-2222-4333-8444-55555555c1e4 `
  --runs-root .tmp\s8-tejal-p4-local-proof `
  --lesson-plan-collateral-intent _bmad-output\implementation-artifacts\s8-tejal-p4-ratified-collateral-intent.yaml
```

The command intentionally did not use `--auto-confirm-directive` and did not use
`--allow-offline-cost-report`. It timed out before producing a trial-start or
run-summary receipt. The only produced file was
`.tmp/s8-tejal-p4-local-proof/8d1d1111-2222-4333-8444-55555555c1e4/model_resolution_trail.json`,
which resolved `gpt-5`. Therefore this is not a completed HIL composed proof and
cannot support an S8-complete claim.
