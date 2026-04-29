# Scaffold v0.2 — Class-D2 Pipeline-Greenfield Variant

**Audience:** dev agents authoring Class-D2 pipeline-greenfield specialist stories (Compositor; future deterministic specialists). Read alongside `scaffold.yaml` + `pipeline-determinism.md.template` + `field-mask.yaml`.

**Status:** Slab 7b foundational artifact (FR111). Authored 2026-04-29.

**Authority:** This scaffold is canonical for Class-D2 specialists per Slab 7b PRD D14 + D20 (R9 amendment). Class-D2 = pipeline-greenfield = **deterministic transformation; no LLM call; sidecar carries operational metadata, not persona-shaped continuity**. Class-D2 is recognized inside the BMB regime as a first-class taxonomy bin, NOT an exception.

---

## What "Class-D2 sidecar variant" means (vs Cora-sidecar option-b)

**Two unrelated concepts share the noun "sidecar":**

- **Cora-sidecar (option-b documented exception):** the runtime-hook specialist's persistent state lives at `_bmad/memory/<name>-sidecar/` because the specialist isn't a conversational specialist with persona-shaped continuity. See `bmb-sanctum-alignment-checklist.md` §5 + `sanctum-exception-categories.json` §`sidecar-hook`.
- **Class-D2 sidecar variant (this scaffold):** the deterministic-pipeline specialist's persistent state ALSO lives at `_bmad/memory/bmad-agent-<name>/` (canonical sanctum dir; same convention as Class-A/B/C/C+/D1) BUT carries OPERATIONAL metadata (contract.md / version.md / chronology of pipeline-runs / access-boundaries) rather than persona-shaped continuity (PERSONA / CREED / BOND / MEMORY / CAPABILITIES).

**Disambiguation:** Cora-sidecar is a runtime/parity exception; D2-sidecar-variant is an authoring/scaffold layout. Do not conflate.

## When to use this scaffold

If your specialist's `_act` body:
- ✅ Is a deterministic transformation (input → output is byte-stable given fixed input + frozen substrate paths)
- ✅ Does NOT call an LLM
- ✅ Does NOT accumulate persona-shaped continuity (operator dialogue, voice evolution)
- ✅ DOES need operational metadata (contract documentation, version history, run chronology, read/write access tracking)

→ Use this scaffold. Class-D2.

If your specialist:
- ❌ Calls an LLM → use Class-A (hardening), Class-B (refresh), Class-C/C+ (port-shape), or Class-D1 (LLM-greenfield) per Slab 7b PRD D14
- ❌ Is a runtime hook with no operational metadata to maintain → use option-b documented exception with `sidecar-hook` allowlist category (Cora-precedent)

## Scaffold contents

| File | Role | Status |
|---|---|---|
| `README.md` (this file) | Audience-signposted overview | Required reading |
| `scaffold.yaml` | Declarative scaffold contract (story-shape + AC patterns + K-target) | Required reading |
| `pipeline-determinism.md.template` | Pipeline-determinism contract template (bytes-identical + field-masked-hash recipe) | Per-specialist instance |
| `field-mask.yaml` | Default declared-nondeterministic field set | Per-specialist instance (extend) |
| `contract.md.template` | Sidecar operational metadata: input/output contract | Per-specialist sanctum |
| `version.md.template` | Sidecar operational metadata: behavioral version history | Per-specialist sanctum |
| `chronology.md.template` | Sidecar operational metadata: pipeline-run history | Per-specialist sanctum |
| `access-boundaries.md.template` | Sidecar operational metadata: read/write/deny zones | Per-specialist sanctum |

## Per-specialist instantiation

For specialist `<name>` (e.g., `compositor`):

1. Copy `contract.md.template` → `_bmad/memory/bmad-agent-<name>/contract.md`; fill in input/output schema.
2. Copy `version.md.template` → `_bmad/memory/bmad-agent-<name>/version.md`; record initial version + behavioral baseline.
3. Copy `chronology.md.template` → `_bmad/memory/bmad-agent-<name>/chronology.md`; this file grows on every pipeline-run.
4. Copy `access-boundaries.md.template` → `_bmad/memory/bmad-agent-<name>/access-boundaries.md`; declare read/write paths.
5. Copy `pipeline-determinism.md.template` → `_bmad/memory/bmad-agent-<name>/pipeline-determinism.md`; declare per-stage determinism contract (bytes-identical or field-masked-hash with field-mask reference).
6. Extend `field-mask.yaml` with any specialist-specific declared-nondeterministic fields beyond the defaults `{generated_at, run_id, build_timestamp}`.

The specialist's `SKILL.md` at `skills/bmad-agent-<name>/SKILL.md` carries minimal frontmatter (`name`, `description`) per `bmb-sanctum-alignment-checklist.md` §3.1, with an "On Activation" prose section that names the sanctum operational metadata files (NOT PERSONA/CREED/BOND/MEMORY/CAPABILITIES — those don't apply to D2).

## Class-D2 parity-test branch (FR101 C-4)

The structural parity-test (`tests/parity/test_skill_md_sanctum_alignment.py`, FR101) checks `class: D2` specialists via the C-4 branch:

- C-1 SKILL.md exists ✅ (same as Class-A/B/C/C+/D1)
- C-2 SKILL.md frontmatter parseable + has `name` + `description` ✅
- C-3 SKILL.md `name` matches `bmad-agent-<name>` ✅
- **C-4 If `class: D2`** → skip C-5/C-6/C-7; **assert scaffold-v0.2-D2-pipeline contract** instead:
  - Sanctum directory exists at `_bmad/memory/bmad-agent-<name>/`
  - Sanctum contains operational metadata files: `contract.md` + `version.md` + `chronology.md` + `access-boundaries.md` + `pipeline-determinism.md`
  - Sanctum does NOT need persona files (PERSONA/CREED/BOND/MEMORY/CAPABILITIES are intentionally absent for D2)
- C-8 Cold-activation smoke ✅ (FM-25 mitigation; Compositor smoke = pipeline-determinism harness invocation)

The `class` field is read from the per-specialist registry at `skills/bmad-agent-marcus/references/specialist-registry.yaml` (or equivalent canonical source); SKILL.md frontmatter is NOT amended to add `class` because that violates substrate-as-floor invariant for already-aligned agents.

## See also

- `docs/dev-guide/bmb-sanctum-alignment-checklist.md` — canonical SG-4 alignment authority
- `docs/dev-guide/sanctum-exception-categories.json` §`_explicitly_excluded` — explicitly states Class-D2 is NOT option-b
- `docs/dev-guide/scaffolds/schema-story/` — scaffold-v0.2 base (the LLM-shape variant; for Pydantic-v2 schema-shape stories)
- `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR99 + §D14 + §D20 — Slab 7b D14/D20 ratifications
