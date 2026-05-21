# Compositor — Deterministic Assembly Pipeline

## OPERATOR

Compositor is your **deterministic assembly pipeline** at G3 lock + Descript handoff. It runs the sync-visuals operation (localized PNG stills + motion clips) and DESCRIPT-ASSEMBLY-GUIDE.md regeneration.

Unlike other specialists, Compositor is **NOT a persona** — it's an operational pipeline. There's no "talk to Compositor as an agent" pattern. You configure it via parameters; it runs deterministically; outputs are bytes-identical across runs given fixed inputs (D17 H-Pipeline contract).

You invoke Compositor implicitly through the trial pipeline at G3 (lock Pass-2 package). It runs after Quinn-R G5 QA, consuming all 11 specialists' outputs into the assembly bundle.

**When you'd interact with Compositor:** running the back-compat CLI at `skills/compositor/scripts/compositor_operations.py` for ad-hoc sync-visuals or assembly-guide regeneration; reviewing the H-Pipeline determinism harness output (`tests/parity/test_pipeline_determinism_harness.py`).

## INPUTS

- **Locked Pass-2 narration script** + storyboard manifest (post-G3 lock).
- **Per-specialist contributions** (Quinn-R QA verdicts + Tracy RetrievalIntent + Enrique audio + Wanda beds + Gary slides + Kira motion + Vera fidelity).
- **Field-mask config** (`docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/field-mask.yaml`): defines which fields are masked at hash-comparison time (modulo `{generated_at, run_id, build_timestamp}`).

## OUTPUTS

- **Sync-visuals**: localized PNG stills at `[bundle]/assembly-bundle/visuals/<slide_id>.png` + motion clips at `[bundle]/assembly-bundle/motion/<slide_id>.{mp4|webm}`. **Bytes-identical across runs** given fixed inputs (D17 H-Pipeline).
- **DESCRIPT-ASSEMBLY-GUIDE.md**: regenerated from manifest + bundle inputs; field-masked-hash modulo `{generated_at, run_id, build_timestamp}`.
- **H-Pipeline determinism rate**: ≥99% (9-of-10 minimum per D17 contract).
- **Compositor summary**: lands at `[bundle]/compositor-summary.md` per 7a.5 specialist-summary-writer integration.

**No LLM. No API. Pure deterministic compute.**

## REFERENCE

- Persona SKILL.md: `skills/compositor/SKILL.md` (NOT `skills/bmad-agent-compositor/`; Class-D2 EXEMPT from sanctum-path-equality per D20)
- Sidecar (NOT 6-file BMB): `_bmad/memory/bmad-agent-compositor/` (4-file operational metadata: `contract.md` / `version.md` / `chronology.md` / `access-boundaries.md`; per scaffold-v0.2-D2-pipeline templates)
- Story spec: [`migration-7b-11-compositor-greenfield.md`](../../../_bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md)
- T11 review report: [`7b-11-code-review-2026-04-30.md`](../../../_bmad-output/implementation-artifacts/7b-11-code-review-2026-04-30.md)
- Code: `app/specialists/compositor/` (9-node scaffold-v0.2; deterministic `_act.py`; greenfield)
- Scaffold templates: `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` (FR111; LANDED Wave 0; Compositor is the seed exemplar)
- Pipeline-determinism harness: `tests/parity/test_pipeline_determinism_harness.py` (10-iteration; ≥99% rate)
- Composition Spec §10 Decision Log entry filed at 7b.11 close: Class-D2 sidecar variant canonical-not-exception per D20
- Class: D2 (sidecar variant; canonical NOT exception; FIRST + ONLY D2 in Slab 7b)
- Pre-T1 K-projection check: 3.45K < 4.0K → single-gate held (Round-(e) E1 binding-hard NOT fired)
