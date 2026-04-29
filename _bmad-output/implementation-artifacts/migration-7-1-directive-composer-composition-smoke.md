# Composition Smoke Gate Evidence — Story 7a.1 Slab-Opener (NFR-CG2)

**Story:** `migration-7a-1-directive-composer`
**Gate:** Composition Spec §9 Composition Smoke at slab-opener
**Verdict:** **PASS**
**Captured:** 2026-04-28 (Story 7a.1 dev cycle)

## Script

Path: `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py`

The smoke script wires composer → Texas-stub contribution → ProductionEnvelope-append
end-to-end and asserts the envelope contains exactly one Texas contribution
with non-empty SHA256 output digest.

## Run command

```bash
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
```

## Verbatim stdout

```
PASS slab-7a-opener composition smoke
  trial_id=82f2d41a-fcf6-4f1a-a3f7-d3c66bf2d20b
  directive_digest=bbb9d194b6657cb7...
  texas_contribution_digest=a78d373a20b5d5c2...
```

## Verdict

PASS. Exit code 0. Composition Spec §9 slab-opener invariants honored:

- ✅ Composer emits a non-empty `ComposedDirective`.
- ✅ Materializer writes `directive.yaml` to `<run_dir>/`.
- ✅ Stub Texas contribution lands in `ProductionEnvelope` via `add_contribution`.
- ✅ Envelope is append-only (single contribution after one add).
- ✅ SHA256 output digest is non-empty and 64 hex chars (FR-A2 invariant).
- ✅ Specialist isolation preserved (composer is orchestration; Texas body untouched — N4).

## CI wrapper

`tests/composition/test_slab_7a_opener_composition_smoke.py` imports and invokes
the smoke script in CI; failure mode: non-zero exit code OR PASS line absent
from stdout.

## References

- Story spec: `_bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md` AC-7.1-F
- Composition Spec §9: `docs/dev-guide/composition-specification.md`
- NFR-CG2: `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md`
- Slab 6.0 slab-opener precedent: `_bmad-output/implementation-artifacts/codex-handoff-slab-6-0-code-review.md`
