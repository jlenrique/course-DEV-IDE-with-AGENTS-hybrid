# S8 Full-Close Proof Preflight - 2026-07-08

## Status

S8 full close is not complete.

Closed checkpoints:

- First S8 selection-edge runtime slice: `282ea82f`.
- Planning-input selection checkpoint: `f69ed471`.
- Lesson-plan prose/workflow checkpoint: `22d63e9d`.

Current branch state at preflight authoring:

- Branch: `dev/workbook-2026-07-06`.
- Branch was level with `origin/dev/workbook-2026-07-06` at HEAD
  `22d63e9d` before this artifact was authored.
- Known untracked strays remain intentionally excluded:
  `workbooks-test/`, `runs/*`, shadow-monitor ledgers, goal launcher files,
  and duplicate evidence workbook output.

## Decision

Do not call S8 complete.

Do not select a proof corpus autonomously.

The 2026-07-06 ratified S8 criterion says the operator names the lesson at
S8-open. The current repository contains no authoritative record naming a
specific S8 proof corpus. A proof run against an inferred or convenient corpus
would weaken the evidence chain and violate the Marcus-SPOC product guardrail.

## BMAD Party Ruling

Follow-up BMAD party round after the two S8 checkpoints were pushed:

- John: `CONCUR-WITH-FINDINGS` - author a full-close proof preflight/runbook
  and hold for operator-named corpus plus HIL; do not call S8 complete.
- Winston: `CONCUR` - corpus selection is an operator-owned gate, not an agent
  inference task; existing local folders must not be promoted into proof
  corpora.
- Murat: `CONCUR` - no current local folder is acceptance-grade for S8 full
  proof; create preflight/runbook and hold for HIL.
- Paige: `CONCUR` - document the stop condition clearly; S8 remains incomplete
  until operator corpus selection and HIL proof exist.

## Ratified Corpus Criteria

From
`_bmad-output/planning-artifacts/canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md`
section 3:

- operator names the lesson at S8-open;
- structurally non-Tejal on the axes S7 generalized;
- literature-rich with DOI-indexed domain material;
- mixed source types: PDF plus DOCX/deck plus image folder, ideally with one
  URL directive;
- at least one genuine adequacy wrinkle that G0R can catch;
- material the operator knows cold;
- fresh to the pipeline, never side-doored, with no cached prefixes;
- standard `course-content/courses/<lesson_slug>/` layout;
- zero corpus-specific production diffs.

## Current Local Corpus Inventory

Inventory command:

```powershell
Get-ChildItem -LiteralPath 'course-content\courses' -Directory |
  ForEach-Object {
    $files = Get-ChildItem -LiteralPath $_.FullName -Recurse -File -ErrorAction SilentlyContinue
    [pscustomobject]@{
      Course=$_.Name
      Files=$files.Count
      Pdf=($files | Where-Object Extension -eq '.pdf').Count
      Docx=($files | Where-Object Extension -eq '.docx').Count
      Deck=($files | Where-Object { $_.Extension -in '.pptx','.ppt' }).Count
      Images=($files | Where-Object { $_.Extension -in '.png','.jpg','.jpeg','.webp' }).Count
      Md=($files | Where-Object Extension -eq '.md').Count
      Yaml=($files | Where-Object { $_.Extension -in '.yaml','.yml' }).Count
    }
  }
```

Observed inventory:

| Course | Files | PDF | DOCX | Deck | Images | MD | YAML | S8 proof disposition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `aziz-nazha-hai-510-generative-ai-in-healthcare` | 22 | 0 | 1 | 0 | 0 | 15 | 6 | Not eligible now: syllabus/reference-only fixture; real videos/slides/readings pending. |
| `juan-leon-phs-620-teaching-learning-seminar` | 66 | 0 | 0 | 0 | 0 | 48 | 17 | Not eligible now: syllabus/reference-only fixture; real Confluence/Canvas course content pending. |
| `tejal-APC-C1` | 13 | 1 | 1 | 1 | 8 | 1 | 0 | Not S8-default: Tejal-family and not operator-named for S8 proof. |
| `tejal-apc-c1-m1-p2-trends` | 12 | 0 | 0 | 0 | 0 | 11 | 0 | Not S8-default: Tejal-family and previously used. |
| `tejal-c1m1-p3-opportunity` | 11 | 0 | 0 | 0 | 0 | 10 | 0 | Not S8-default: Tejal-family and already fed earlier proofing/workbook work. |
| `tejal-c1m1-p3-opportunity-raw` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | Not S8-default: raw Tejal-family source. |
| `tejal-c1m1-fresh-outline` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | Not S8-default: Tejal-family despite DOI-rich outline. |
| `tejal-c1m1-3slide-slice` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | Not eligible: tiny slice/probe shape. |
| `tejal-c1m1-studio-min` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | Not eligible: minimal fixture. |
| `studio-smoke-min` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | Not eligible: smoke fixture. |
| `style-test-strip-v1` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | Not eligible: style test strip. |
| `coverage-faithful-probe` | 2 | 0 | 0 | 0 | 0 | 2 | 0 | Not eligible: probe fixture. |

Conclusion: no current local folder can be promoted to S8 full-close proof
corpus without operator selection or violating the ratified criteria.

## Operator Input Required

To proceed to S8 full proof, the operator must name:

```yaml
s8_operator_named_corpus:
  lesson_slug: "<kebab-case slug under course-content/courses/>"
  corpus_path: "course-content/courses/<lesson_slug>"
  proof_intent: "S8 full-close composed proof"
  expected_bundle_id: "<closed BUNDLE_CATALOG id>"
  hil_operator: "<operator id>"
  freshness_attestation: "fresh_to_pipeline | exception_with_rationale"
  known_adequacy_wrinkle: "<what G0R should catch or pressure-test>"
  no_corpus_specific_diffs_acknowledged: true
```

If the named corpus does not yet exist, the next action is corpus preparation,
not S8 close.

If the operator deliberately chooses an existing Tejal-family or fixture corpus,
the party must explicitly ratify the criteria exception before any S8-complete
claim.

## Runtime Proof Command Template

After operator corpus selection and preflight, launch the local Marcus-SPOC
runtime with the ratified lesson-plan selection input:

```powershell
$trialId = [guid]::NewGuid().ToString()
.\.venv\Scripts\python.exe -m app.marcus.cli trial start `
  --preset production `
  --input course-content/courses/<lesson_slug> `
  --operator-id <operator_id> `
  --trial-id $trialId `
  --lesson-plan-collateral-intent <ratified-intent.yaml>
```

Do not use `--allow-offline-cost-report` for full production proof unless the
BMAD party explicitly downgrades the close claim. Offline cost reports are
acceptable for local selection-edge witnesses, not for full S8 production close.

Do not use `--auto-confirm-directive` for the full S8 HIL proof unless the party
explicitly ratifies a scripted-gate substitute. The close bar requires real HIL
verdicts.

## HIL Evidence Required

The S8 evidence pack must include:

- trial id and run directory;
- trial-start environment/transport attestation;
- input corpus path and operator-named corpus declaration;
- ratified lesson-plan collateral/input wrapper path;
- selected bundle id and `component_selection` receipt;
- directive digest and directive file;
- gate transcript with real operator decisions, not auto-defaulted verdicts;
- per-node receipts for canonical nodes;
- workbook citations traceable to same-run TexasRows when workbook is in scope;
- explicit side-door absence assertion;
- zero corpus-specific production diffs audit;
- final BMAD close concurrence that S8 itself is complete.

## Stop Conditions

Stop and do not claim S8 complete if any of these is true:

- no operator-named corpus exists;
- corpus path is absent or not in standard layout;
- selected corpus requires production-code changes to pass;
- HIL verdicts are missing, scripted without ratification, or incomplete;
- selected bundle does not resolve through the closed catalog;
- trigger-path files are touched without lockstep/Tier governance;
- evidence cannot prove the selected bundle flowed into downstream runtime
  behavior;
- party close is anything other than S8-full concurrence.

## Next Gate

Immediate next gate:

1. Operator names the S8 proof corpus and confirms whether any criteria
   exception is intended.
2. Run corpus preflight against the named path.
3. Launch local Marcus-SPOC runtime proof and collect HIL evidence.
4. Run BMAD close review and final party concurrence.

Post-S8 gates that become ripe only after real S8 close:

- `workbook-learner-ready-prose-uplift`;
- `g0-enrichment-flag-retirement`;
- `research-dispatch-flag-retirement`.

Do not silently absorb those follow-ons into S8.
