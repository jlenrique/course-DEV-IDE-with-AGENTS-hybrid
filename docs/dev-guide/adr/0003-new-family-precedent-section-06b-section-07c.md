# ADR 0003 — NEW Family Precedent for §06B + §07C (no `alias_of` parent)

**Status:** ACCEPTED 2026-05-08 (pre-Trial-3 cleanup S6; ratified by Winston pre-S6 review + party-mode at S6)

**Authors:** Winston (architect; pre-S6 review); operator (final ratification)

**Supersedes / Updates:** ADR 0002 (Slab 7c gate taxonomy) — adds the NEW-family precedent as a recognized pattern alongside the eight-family taxonomy.

## Context

ADR 0002 ratified the **eight-family gate taxonomy** (G0/G1/G2/G2A/G2C/G3/G4/G5/G6) with alias-DSL `alias_of` clause inheritance. Per ADR 0002 §6 worked example, alias gates inherit family semantics from their parent family contract.

During Slab 7c orchestrational tail authoring, two §section poll-surface packages landed that **do NOT have an `alias_of` clause** in their gate code declarations:

- **§06B** Literal-Visual Operator Build — declares its own gate code with no parent family
- **§07C** Storyboard Build + HTML Reviewer — declares its own gate code (G2C runner-pause; in `production_gate_ids(manifest)` set)

These represent a **NEW family precedent** — gate codes that establish their own family semantics rather than inheriting from one of the eight ratified families. The pattern is structurally valid (the eight-family taxonomy doesn't forbid additions) but lacks formal recognition at architecture-tier.

## Decision

**Recognize NEW-family declarations as a valid third option** alongside the eight-family taxonomy and alias-DSL inheritance. Specifically:

1. **Default expectation:** new gate codes declare via `alias_of` clause inheriting from one of the eight families. This is the lowest-cost path; no taxonomy changes; no per-section family-contract authoring.

2. **NEW-family option:** when the gate semantics genuinely diverge from any existing family, the §section package MAY declare a NEW family. NEW-family declarations require:
   - Explicit `family: NEW` declaration in the §section's `gate_code` metadata (not `alias_of: <existing>`)
   - One-paragraph rationale in the §section package's `__init__.py` docstring naming WHY the existing eight families don't fit
   - Cross-reference to this ADR (ADR 0003) plus ADR 0002
   - C6 import-linter contract update if applicable (the §section is added to the `independence` contract's modules list)

3. **NEW-family ratification:** dev-agent authority (no party-mode required) for NEW-family declarations that meet the above three criteria. Party-mode required if the NEW family introduces a runner-pause semantic (i.e., the new code joins `production_gate_ids(manifest)`); otherwise dev-agent authority covers.

## Precedents

- **§06B Literal-Visual Operator Build** (Story 7c.18a): NEW family for operator-supplied literal-visual builds; semantically distinct from G2/G2C visual-direction-vs-storyboard pattern; NOT a runner-pause.
- **§07C Storyboard Build + HTML Reviewer** (Story 7c.18b): G2C-coded but with HTML-reviewer surface that didn't fit existing G2C semantics cleanly. (Note: G2C is in `production_gate_ids(manifest)` so this required party-mode ratification at the time; ADR 0003 codifies the precedent for future cases.)

Both shipped under Slab 7c without explicit ADR codification; ADR 0003 retroactively recognizes the precedent.

## Consequences

**Positive:**
- Future §section authors have a third option (NEW-family) when the existing eight families don't fit; reduces forced-aliasing pressure
- Clear governance: dev-agent authority for non-runner-pause NEW families; party-mode for runner-pause additions
- Eliminates ambiguity that ADR 0002 left open

**Negative:**
- Family count can grow unbounded; future audit may need to consolidate (ADR 0004 candidate)
- C6 import-linter `independence` contract modules list grows linearly with §section packages

**Mitigations:**
- Family-count growth bounded by §section count (~14-20 expected at Trial-N maturity)
- C6 contract growth is mechanical; tooling already supports incremental additions

## Cross-references

- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` — original eight-family taxonomy
- `docs/dev-guide/composition-specification.md §10 Decision Log` — eight-family taxonomy LOCK entry (2026-05-07)
- `pyproject.toml::tool.importlinter` C6 — independence contract enumerating §section modules
- `_bmad-output/implementation-artifacts/migration-7c-18a-section-06b-literal-visual-operator-build.md` — §06B precedent
- `_bmad-output/implementation-artifacts/migration-7c-18b-section-07c-storyboard-build-html-reviewer.md` — §07C precedent

## Open questions (for ADR 0004 candidate)

- Lane-independence canonical form across NEW families (post-Trial-3; informed by trial evidence)
- Family-consolidation policy when NEW families accumulate (post-Trial-N; trigger TBD)
