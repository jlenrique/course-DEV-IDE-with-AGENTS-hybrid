# Retrieval intake contract

Audience-segmented reference for Irene's retrieval-intake seam (corroborate-only v1). This contract documents how Tracy/Texas retrieval outputs become additive segment metadata and attribution phrasing in Pass 2.

## For Irene authors

### Intake envelope keys

Required keys:

- `run_id`
- `pass_2_cluster_id`
- `suggested_resources_ref`
- `intake_mode`
- `evidence_bolster_active`

Optional key:

- `extraction_report_ref`

### Scope lock

- v1 behavior consumes corroboration outcomes only (`intake_mode: corroborate`, or corroborate branch when `intake_mode: mixed`).
- If no usable corroboration intake is available, do not force retrieval language.

### Additive segment field

When intake is usable, emit:

```yaml
retrieval_provenance:
  - source_id: scite:support-101
    providers: [scite, consensus]
    convergence_signal:
      providers_agreeing: [scite, consensus]
      providers_disagreeing: []
      single_source_only: []
```

### Convergence-to-language table

| Convergence shape | Narration attribution phrase |
|---|---|
| `providers_agreeing` contains both `scite` and `consensus`, and `single_source_only` empty | `Corroborated by multiple independent sources, with support from peer-reviewed citation context and synthesis evidence.` |
| scite-only convergence | `According to scite.ai citation-context analysis.` |
| consensus-only convergence | `Per Consensus research synthesis.` |
| unknown/partial convergence | `According to available retrieval evidence.` |

### Empty retrieval behavior

When suggested resources are empty for a cluster, or extraction report rows do not yield usable retrieval provenance, narration proceeds without intake phrase injection and appends:

```text
retrieval_empty_for_cluster_<cluster_id>
```

to `known_losses`.

## For operators

- `evidence_bolster_active: true` means Pass 2 should consume corroboration intake where available.
- `evidence_bolster_active: false` means retrieval intake may be present but should not be treated as mandatory narration posture.
- `known_losses` sentinel `retrieval_empty_for_cluster_<cluster_id>` indicates graceful fail-closed behavior, not a crash.
- `retrieval_provenance` is additive metadata for auditability and should not break legacy segment consumers.

## For dev-agents

- Runtime seam: `marcus/irene/intake.py`.
- Schema contract: `state/config/schemas/irene-retrieval-intake.schema.json`.
- Segment additive surface: `state/config/schemas/segment-manifest.schema.json` (`retrieval_provenance`).
- Procedure lockstep: `skills/bmad-agent-content-creator/references/pass-2-procedure.md`.
- Contract tests:
  - `tests/irene/test_retrieval_intake.py`
  - `tests/contracts/test_pass_2_procedure_parity.py`

## Worked example (corroborate-only)

Input posture: Tracy `output.posture: corroborate`, evidence found true, extraction report includes dual convergence (`scite` + `consensus`).

Expected outcome:

- Narration may use: `Corroborated by multiple independent sources, with support from peer-reviewed citation context and synthesis evidence.`
- Segment receives additive `retrieval_provenance` with convergence metadata.

## Cross-links

- [`retrieval-contract.md`](../../bmad-agent-texas/references/retrieval-contract.md) — Texas retrieval contract (Shape 3-Disciplined).
- [`pass-2-authoring-template.md`](./pass-2-authoring-template.md) — Pass 2 segment-manifest contract and emission examples.
- [`_bmad-output/implementation-artifacts/irene-retrieval-intake.md`](../../../_bmad-output/implementation-artifacts/irene-retrieval-intake.md) — story spec + party-mode decisions.
