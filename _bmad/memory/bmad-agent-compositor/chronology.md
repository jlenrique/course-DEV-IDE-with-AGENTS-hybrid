# Pipeline-run chronology - compositor

**Specialist:** compositor (Class D2 pipeline-greenfield)

Records every pipeline run; one entry per run. Append-only operational metadata, not persona continuity.

## Format

```text
### YYYY-MM-DDTHH:MM:SSZ - run_id=<run_id> trial_id=<trial_id>

Stages: sync_visuals -> regenerate_assembly_guide -> field_masked_hash
Outcome: PASS | PARTIAL | FAIL
Pipeline-determinism rate: <X.XX> (target >=0.99)
Bytes-identical hashes: <stage>: <sha256_first_8_chars>
Field-masked hashes: assembly_guide: <sha256_first_8_chars>
Notes: <free-prose anomalies or remediation pointers>
```

## Chronology

Initial Story 7b.11 activation. First live pipeline entry lands on the first post-close Compositor invocation.
