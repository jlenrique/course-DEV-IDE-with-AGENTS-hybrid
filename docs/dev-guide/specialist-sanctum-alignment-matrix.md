# Specialist Sanctum-Alignment Matrix (Slab 7b SG-4 final form)

**Authoritative source for FR103 + NFR-OD4.** Aggregated at Story 7b.12 (Wave 6 closeout). Operator-facing twin lives at [`docs/operator/specialists/sanctum-alignment-matrix.md`](../operator/specialists/sanctum-alignment-matrix.md).

This matrix records, for each of the 11 Slab 7b specialists, the SG-4 sanctum-alignment verdict per FR108 (`docs/dev-guide/bmb-sanctum-alignment-checklist.md`) — alignment-or-exception status, the BMB sanctum directory path, the SKILL.md path(s), and the rationale link.

**Class-C two-SKILL.md convention** (party-mode 4/4 unanimous Round-(f) ratification 2026-04-29): for Class-C API-bound specialists, the persona-skill lives at `skills/bmad-agent-{specialist}/SKILL.md` and the API-mastery skill is preserved at `skills/bmad-agent-{api-name}/SKILL.md`. Both are tracked; matrix lists both paths.

**Class-D2 sanctum-path-equality EXEMPT** per D20: Compositor's sidecar variant uses `_bmad/memory/bmad-agent-compositor/` 4-file operational-metadata pattern (NOT 6-file BMB) AND `skills/compositor/SKILL.md` (NOT `skills/bmad-agent-compositor/`). Documented as canonical-not-exception.

## Matrix

| # | Specialist | Class | Sanctum verdict | Sanctum path | Persona SKILL.md | API-mastery SKILL.md | Rationale |
|---|---|---|---|---|---|---|---|
| 1 | Texas | A | aligned (option-a) | `_bmad/memory/bmad-agent-texas/` (6-file BMB) | `skills/bmad-agent-texas/SKILL.md` | — | [Story 7b.1](../../_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md) — Class-A first-three-GREEN |
| 2 | Quinn-R | A | aligned (option-a) | `_bmad/memory/bmad-agent-quinn-r/` (6-file BMB) | `skills/bmad-agent-quality-reviewer/SKILL.md` | — | [Story 7b.2](../../_bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md) — sanctum-path canonicalized at 7b.8 retrofit |
| 3 | Vera | A | aligned (option-a) | `_bmad/memory/bmad-agent-vera/` (6-file BMB) | `skills/bmad-agent-fidelity-assessor/SKILL.md` | — | [Story 7b.3](../../_bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md) — legacy `vera-sidecar/` preserved out-of-band per `vera-sidecar-cleanup-post-trial-2-validation` follow-on |
| 4 | Irene Pass-1 | B | aligned (option-a; shared) | `_bmad/memory/bmad-agent-content-creator/` (6-file BMB; SHARED with Pass-2) | `skills/bmad-agent-content-creator/SKILL.md` | — | [Story 7b.4](../../_bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md) — Pass-1+Pass-2 share sanctum per Slab 2a.2 era |
| 5 | Tracy | C+ | aligned (4-file sidecar) | `_bmad/memory/bmad-agent-tracy/` (4-file Class-C+: INDEX/PERSONA/access-boundaries/chronology) | `skills/bmad-agent-tracy/SKILL.md` | — | [Story 7b.5](../../_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md) — Class-C+ sidecar pattern canonical (NFR-CG15 Decision Log §10) |
| 6 | Gary | C | aligned (option-a + two-SKILL.md per Round-(f)) | `_bmad/memory/bmad-agent-gary/` (6-file BMB) | `skills/bmad-agent-gary/SKILL.md` | `skills/bmad-agent-gamma/SKILL.md` | [Story 7b.6](../../_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md) — Class-C two-SKILL.md ratified party-mode 4/4 unanimous |
| 7 | Kira | C | aligned (option-a + two-SKILL.md) | `_bmad/memory/bmad-agent-kira/` (6-file BMB) | `skills/bmad-agent-kira/SKILL.md` | `skills/bmad-agent-kling/SKILL.md` | [Story 7b.7](../../_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md) — Class-C inheritance proven 2× |
| 8 | Enrique | C | aligned (option-a + two-SKILL.md) | `_bmad/memory/bmad-agent-enrique/` (6-file BMB) | `skills/bmad-agent-enrique/SKILL.md` | `skills/bmad-agent-elevenlabs/SKILL.md` | [Story 7b.8](../../_bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md) — Wave-3 LAST closer; Class-C inheritance proven 3× |
| 9 | Wanda | C | aligned (option-a + two-SKILL.md) | `_bmad/memory/bmad-agent-wanda/` (6-file BMB; migrated from `wanda-sidecar/` at 7b.9 T2) | `skills/bmad-agent-wanda/SKILL.md` | `skills/bmad-agent-wondercraft/SKILL.md` | [Story 7b.9](../../_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md) — closes `wanda-sanctum-test-expected-files-constant-drift` |
| 10 | Dan | D1 | aligned (option-a; single-SKILL.md) | `_bmad/memory/bmad-agent-dan/` (6-file BMB) | `skills/bmad-agent-dan/SKILL.md` | — (LLM-only; no third-party API) | [Story 7b.10](../../_bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md) — `dan-api-tbd-pending` retired; LLM-only path |
| 11 | Compositor | D2 | **EXEMPT (D20 canonical-not-exception)** | `_bmad/memory/bmad-agent-compositor/` (4-file operational metadata: contract.md/version.md/chronology.md/access-boundaries.md) | `skills/compositor/SKILL.md` (NOT `bmad-agent-compositor/`) | — (deterministic pipeline; no API; no LLM) | [Story 7b.11](../../_bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md) — sanctum-path-equality EXEMPT per D20; FR99 Class-D2 sidecar canonical |

## Verification

The matrix is enforced structurally via:

- **`tests/parity/test_skill_md_sanctum_alignment.py`** — 33 cases (3 per specialist; 11 specialists); FR101 + FR102 binding.
- **`tests/parity/test_eleven_specialists_addressable.py`** — SG-1 aggregator; 11-specialist roster floor; FR105 + NFR-I10.
- **`scripts/utilities/validate_parity_test_class_conformance.py`** — 6 classes (A/B/C+/C/D1/D2); NFR-I12.
- **`.github/workflows/specialist-parity.yml`** — required CI check at PR merge; NFR-I9.
- **`.github/workflows/activation-contract.yml`** — required CI check at PR merge; NFR-I10.

## Cross-references

- FR108 sanctum-alignment checklist: [`bmb-sanctum-alignment-checklist.md`](bmb-sanctum-alignment-checklist.md)
- Sanctum exception categories: [`sanctum-exception-categories.json`](sanctum-exception-categories.json)
- Operator-control parity table: [`../operator/legacy-vs-langgraph-control-parity.md`](../operator/legacy-vs-langgraph-control-parity.md)
- Cora `§Sanctum exception` anchor pattern: [`../../skills/bmad-agent-cora/SKILL.md`](../../skills/bmad-agent-cora/SKILL.md)
- Composition Spec §10 Decision Log: [`composition-specification.md`](composition-specification.md)
