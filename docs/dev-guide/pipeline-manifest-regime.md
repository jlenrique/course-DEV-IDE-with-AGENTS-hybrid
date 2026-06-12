# Pipeline Manifest Regime — Operator Doctrine

**Audience:** dev agents opening ANY future story that touches the production pipeline (gates, orchestrator, HUD, prompt pack, learning events, cross-cutting contracts with pipeline visibility).

**Status:** canonical. This document is the operational cheatsheet; the Epic-scope authority is [`_bmad-output/planning-artifacts/epics.md §Epic 33 Standing Regime`](../../_bmad-output/planning-artifacts/epics.md).

**When to read:** at T1 of any story whose diff will touch the paths enumerated in §Block-Mode Trigger Paths below. If your story touches ANY of those paths and you haven't read this document, Cora's pre-closure hook will likely block you.

---

## TL;DR

1. **The pipeline has ONE source of truth**: [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml).
2. **The v4.2 pack is GENERATED**, not hand-authored. Every prose or structural edit flows through manifest + templates + regeneration, not through direct pack edits.
3. **Every commit that touches a manifest-adjacent path** is gated by Cora's block-mode pre-closure hook. The hook runs [`scripts/utilities/check_pipeline_manifest_lockstep.py`](../../scripts/utilities/check_pipeline_manifest_lockstep.py); non-zero exit blocks story closure.
4. **No LLMs in the critical path**. The generator is pure Jinja2. New substrate concerns (learning events, telemetry, future pack versions) follow the same deterministic pattern.
5. **When in doubt**: manifest first, regenerate second, commit both as one logical change.

---

## The Regime's Seven Components

| # | Component | Path | Role |
|---|---|---|---|
| 1 | Pipeline manifest | `state/config/pipeline-manifest.yaml` | Canonical SSOT for gates, order, names, bitmap, insertion-points, emission topology, block-mode trigger paths, section rationale |
| 2 | L1 lockstep check | `scripts/utilities/check_pipeline_manifest_lockstep.py` | 8 deterministic checks, 0/1/2 exit codes, O/I/A trace under `reports/dev-coherence/<ts>/` |
| 3 | v4.2 generator | `scripts/generators/v42/` | Jinja2 template-driven, no LLM. Reads manifest + templates, emits pack byte-identically |
| 4 | Block-mode pre-closure hook | `skills/bmad-agent-cora/scripts/preclosure_hook.py` | Classifies change-window via manifest `block_mode_trigger_paths`; invokes L1 check; blocks closure on non-zero exit |
| 5 | Consumer rewires | `scripts/utilities/run_hud.py`, `scripts/utilities/progress_map.py`, `marcus/orchestrator/workflow_runner.py` | All manifest-sourced at import time; no parallel step lists |
| 6 | Version parameterization | Manifest `pack_version` field + L1 check `--pack-version` arg | Horizontal scaling to v4.3+ via `scripts/generators/v<N>/` siblings |
| 7 | Meta-test template | `_bmad-output/implementation-artifacts/15-1-lite-marcus.md` | Canonical pattern for validating substrate catches new-contract introductions |

---

## Standard Workflow — Every Pipeline-Touching Story

```
1. Edit state/config/pipeline-manifest.yaml (source of truth for new shape)
2. Edit scripts/generators/v42/templates/ if prose changes are paired
3. Run: python -m scripts.generators.v42.render \
        --manifest state/config/pipeline-manifest.yaml \
        --output docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md
4. Run: python scripts/utilities/check_pipeline_manifest_lockstep.py
       (assert exit 0)
5. Commit manifest + templates + regenerated pack + any consumer code as ONE logical change
6. At story close, Cora's block-mode hook runs steps 4 automatically
   - exit 0 -> closure permitted
   - non-zero -> closure BLOCKED with trace path + operator message
```

**All five manifest-adjacent files belong in the same commit.** PR reviewers should reject a PR that ships a manifest edit without the paired template/pack/consumer changes, or vice versa.

---

## Pack Versioning Policy

The regime's `pack_version` field + L1 check `--pack-version` arg are the *mechanism* for multi-version support; this section is the *policy* for when to turn the crank. Three-tier trigger set modeled on SemVer with prompt-pack-specific considerations (operator muscle memory, run-history audit trails, Marcus runtime contracts).

### Tier 1 — Patch (no version bump; stays v4.2)

**Covers**: prose polish, clarification wording, typo fixes, audience-tag refinements that are clarifications (not semantic shifts), `rationale:` field edits, provenance-appendix regeneration, TL;DR crosswalk regeneration.

**Trigger shape**: regenerated pack's diff vs the prior version is bounded to prose/connective-tissue that operators wouldn't notice if section IDs, ordering, and semantic promises stay identical.

**Process**: normal regeneration workflow (manifest or template edit → render → commit). Pack filename unchanged. No new generator sibling. No operator communication.

**Decision authority**: dev agent unilaterally, gated by Cora's block-mode hook on regeneration-determinism + L1 lockstep.

### Tier 2 — Minor (v4.2 → v4.3; new pack file, v4.2 preserved for audit)

**Covers**:
- New pipeline step added (e.g., `04B` inserted between `04A` and `04.5`)
- Existing step removed or renumbered (even with graceful deprecation)
- Gate semantics change (e.g., G2 shifts from HIL-approval to automated-approval-with-HIL-override)
- Sub-phase promotion/demotion (e.g., §4.75 CD goes from `sub_phase_of: "04"` to top-level gate-bearing)
- New `event_type` enum value (additive, backward-compatible)
- New `block_mode_trigger_paths` entry (regime extension)
- Workflow branch added (e.g., new motion-enabled variant path branching from an existing gate)

**Trigger shape**: operators would notice a difference in what they do / see / approve between runs. Marcus's runtime contracts may or may not change, but operator workflow changes.

**Process**:
1. Party-mode consensus round on whether the change justifies a version bump (vs patch).
2. Manifest entries added with `pack_version: "v4.3"`; v4.2 entries preserved unchanged.
3. New generator sibling: `scripts/generators/v43/` (may start as a copy of `v42/` + targeted template edits; shared `manifest.py` and `env.py` seams).
4. New committed pack: `docs/workflow/production-prompt-pack-v4.3-<descriptor>.md`.
5. v4.2 pack stays on disk unchanged — audit artifact for prior runs.
6. L1 check extends 1 line (add `v4.3` to valid `--pack-version` values); no substrate refactor.
7. Operator communication: `next-session-start-here.md` + `SESSION-HANDOFF.md` name the transition so an operator mid-run knows which pack they're executing against.

**Decision authority**: party-mode consensus (stock 4 minimum; Cora for governance-envelope input on run-history audit impact; Audra for lockstep impact).

### Tier 3 — Major (v4.x → v5; new pack family)

**Covers**:
- Core loop restructure that's not additive (gates sequenced differently, removed, or consolidated in ways that break backward audit compatibility)
- Downstream schema-version change that cascades (e.g., learning-event-schema v1 → v2 with field renames or enum removals)
- Marcus's entry contract changes (different input shape from the operator)
- Workflow-family-level change (e.g., "narrated-lesson-with-video-or-animation" becomes "narrated-lesson-unified" as a substantively different product)

**Trigger shape**: a v4 operator running a v5 pack would be lost; a v5 Marcus running a v4 manifest would fail; historical v4 run records become unreadable by v5 tooling without explicit adapters.

**Process**:
1. Party-mode R1 + R2 rounds — treated as Epic-boundary work, not within-Epic scope.
2. New generator family `scripts/generators/v5/` — may share substrate (manifest loader, env factory) but typically has its own template tree + layout.
3. New manifest section or separate manifest file if the shape differs materially — scope-round decision.
4. v4 artifacts preserved under `docs/workflow/archive/v4/` after v5 ships cleanly.
5. Adapter story if historical run records need v5-tooling readability.

**Decision authority**: party-mode round scoped as Epic-boundary work; operator explicitly ratifies before dev opens.

### New pack *types* are NOT version bumps

Podcasts, infographics, slide-deck-only are **different packs, not v5 of narrated-lesson**. Filename stem changes (`production-prompt-pack-podcast-v1-*.md`); new generator sibling (`scripts/generators/podcast-v1/`); manifest likely extends with a `pack_family` discriminator to support multiple families. Backlogged Epic 18 territory — probably Epic 35+ substrate when new content types come online. The regime itself is family-agnostic.

### Recorded determination — per-node `dependencies` edits are data-plane-only (2026-06-12)

The v4.2 generator does not read per-node `dependencies` (no template/render
reference exists), so dependency-edge edits cannot change the rendered pack —
the frozen-at-ship obligation attaches to the PACK artifact, which such edits
leave byte-identical. Do NOT flip an existing node's `pack_version` for a
dependency edit: the L1 filter (`step.pack_version in (None, active)`) would
drop the node from v4.2 validation and rendering. Tier-2 governance for
data-plane vocabulary attaches to the (forthcoming) manifest vocabulary-version
field instead. Party-mode consensus + party review accepted: commits `2a617f5`
(determination) and the 2026-06-12 S0-S3 batch review (Winston Deviation-1
ruling). Note: the manifest vocabulary-version field is mandated before the
next data-plane vocabulary change (deferred-inventory
`manifest-edge-key-projection-s4`).

### Frozen-at-Ship Discipline

**Once a pack ships to an operator AND a tracked trial-run completes against it, the pack becomes frozen at that version.** Prose patches regenerate in place (Tier 1); minor-or-major changes bump the version (Tier 2 / Tier 3).

**Rationale**: every production run's audit trail cites the pack version + SHA that was active. Mutating that pack silently breaks audit even if the change is "obviously an improvement." The first tracked trial run against v4.2 is the freeze point; frozen v4.2 + its manifest slice stay on disk as the reference audit logs can resolve to.

**Concrete rule**: after the freeze point, any Tier 2 or Tier 3 class change → v4.3 (or v5); never a structural edit to the frozen v4.2 artifact. A violation of this rule surfaces at Cora's block-mode hook + audit-trail regression tests.

---

## Concrete Examples

### Scenario A — Adding a new pipeline step (e.g., `04B`)

1. Add `04B` entry to manifest `steps` block with `label`, `gate`, `insertion_after`, `sub_phase_of` (if applicable), `hud_tracked`, `pack_section_anchor`, `pack_version: "v4.2"`, `rationale`.
2. Author `scripts/generators/v42/templates/sections/04B-<slug>.md.j2` with section body.
3. Run generator + L1 check.
4. Ensure `insert_between("04A", "04.5", new_step_04B)` call site (or equivalent) exists if orchestrator runtime behavior depends on the step.
5. Commit.

### Scenario B — Renaming a gate

1. Edit manifest `steps[<id>].label` only.
2. Run generator — pack regenerates with new label everywhere it appears (TL;DR crosswalk, section headers, provenance appendix).
3. Run L1 check — catches any parallel label in HUD or orchestrator that didn't auto-sync (should be none post-33-2, but verifies the regime is intact).
4. Commit manifest + regenerated pack.

**Do NOT** hand-edit the HUD's `PIPELINE_STEPS` or the pack's section heading. Those are projections; they auto-sync.

### Scenario C — New emission topology (new event_type for learning events)

1. Edit `state/config/learning-event-schema.yaml` — add new enum value to `event_type`.
2. Edit `scripts/utilities/learning_event_capture.py` — extend `validate_event` `Literal` union.
3. Edit manifest — update the relevant gate's `learning_events.event_types` list.
4. Run `check_learning_event_lockstep.py` (from 15-1-lite-marcus) — assert exit 0.
5. Run `check_pipeline_manifest_lockstep.py` — assert exit 0 (verifies pipeline-side integrity).
6. Commit all three edits + any Marcus call-site updates.

### Scenario D — Shipping v4.3

1. Add manifest entries with `pack_version: "v4.3"` (may coexist with v4.2 entries).
2. Create `scripts/generators/v43/` mirroring `v42/` package shape; extract v4.3 templates.
3. Extend L1 check: no code change required — it already accepts `--pack-version` arg.
4. Run `python -m scripts.generators.v43.render --manifest state/config/pipeline-manifest.yaml --output docs/workflow/production-prompt-pack-v4.3-<slug>.md`.
5. Commit.

**This is horizontal scaling.** The substrate didn't change; only a sibling generator was added.

### Scenario E — Someone hand-edited v4.2.md directly

1. Their pre-closure hook runs.
2. `check_pipeline_manifest_lockstep.py` exits non-zero because regenerating from the current manifest produces a different SHA than the committed pack.
3. Cora's hook blocks closure with an operator message pointing at the trace.
4. The dev agent's options: (a) revert the pack edit and make it through the manifest + regeneration path, (b) if the edit was genuinely needed, edit the manifest/templates and regenerate.

**The regime self-corrects.** This is the FM-A/FM-B/FM-C closure working as designed.

---

## Block-Mode Trigger Paths (as of Epic 33 close)

These paths are declared in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`. Any diff intersecting any of these triggers block-mode at pre-closure.

- `state/config/pipeline-manifest.yaml` itself
- `scripts/utilities/check_pipeline_manifest_lockstep.py`
- `scripts/utilities/run_hud.py`
- `scripts/utilities/progress_map.py`
- `marcus/orchestrator/workflow_runner.py`
- `tests/test_run_hud.py`
- `tests/test_progress_map.py`
- `docs/workflow/production-prompt-pack-v4.2-*.md`
- `state/config/learning-event-schema.yaml` (pre-emptive for 15-1-lite-marcus)
- `scripts/utilities/learning_event_capture.py` (pre-emptive for 15-1-lite-marcus)
- `scripts/generators/v42/**` (added by 33-1a)

**To extend the trigger set**: edit the manifest's `block_mode_trigger_paths` list. The change-window detector's classification logic is data, not code — adding a new contract surface is a manifest edit, not a detector-code edit. This is "FM-C medicine applied to Cora's own tool" (33-4 governance mandate).

---

## Forbidden Actions (Binding on All Future Stories)

### ❌ Hand-editing the v4.2 pack

Violates 27-2 anti-pattern. Will trigger Cora's block-mode hook at pre-closure (AC-C.1 regeneration-determinism guard in 33-3 catches it). If the prose needs to change, edit the template + regenerate. No exceptions.

### ❌ Maintaining parallel step lists in code

33-2 broke every parallel list and rewired consumers to read from manifest. Creating a new list literal elsewhere reopens the DC-1..DC-5 drift class. AC-C.1 in 33-2 enforces this via AST scan (`test_no_hardcoded_pipeline_step_lists` in `tests/contracts/`).

### ❌ Shimming legacy insertion helpers

33-2 R1-B ruling: `insert_4a_between_step_04_and_05` was deleted and replaced by `insert_between(before_id, after_id, new_step)`. Do not shim deleted helpers. Murat's AC-C.1 trap: shims make orphan literals resolvable while preserving verb-encoded topology, defeating the no-orphan-literals guard.

### ❌ Smuggling LLMs into the generator or critical path

33-1a R1-33-1a-A ruling + AC-C.1 no-LLM-imports guard. Murat's calculation: 40-60% probability of Cora's hook being disabled by false-positive model-drift storms within two quarters of an LLM-smuggling ship. If you believe an LLM is needed for a specific prose task, the fix is a one-off authoring session (human-written, committed as template), NOT a runtime LLM call.

### ❌ Silent scope creep during implementation

Any substrate-level change (manifest shape, L1 check logic, block-mode trigger paths, generator interface) requires party-mode consensus BEFORE dev opens. Discovery of a substrate gap during implementation triggers the 33-1 kill-switch template: stop, escalate, file a sibling story, ratify scope via party-mode round before resuming.

### ❌ Treating the §4.55 split as special-case

The 04.5 → 04.5 polling + 04.55 lock split (33-1 addendum A-2 + 33-2 R1-A) is the regime's canonical example of how structural splits work. Future splits (e.g., if §7C splits into variant-selection-gate + gate-2-approval) follow the same pattern: manifest entries split first → templates created/extracted → regenerator produces new pack structure → L1 check validates.

---

## When The Regime Hits An Unanticipated Drift Class

Follow the 33-1 kill-switch template (33-1 proved the template works in practice):

1. **Stop** in-flight implementation. Do not silently patch.
2. **Surface** the drift explicitly to the operator + party-mode. Name the class of drift (Omission / Invention / Alteration per Audra's O/I/A taxonomy).
3. **Escalate** to party-mode for consensus on whether the drift is (a) fixable in-story with a small scope adjustment + party sign-off, (b) requires a sibling story filed first (33-1a precedent), or (c) requires reopening a prior story (33-2 / 33-4 etc.).
4. **Ratify** the chosen path via a recorded party-mode vote before resuming.
5. **Document** the escalation in the affected story's Dev Agent Record + deferred-work.md.

**Precedent**: 33-1's Case C escalation (generator didn't exist) → 33-2 DEFER AC-B.15 with YES-WITH-RIDER → 33-1a filed + scoped via party-mode → sprint reshape executed cleanly. That template works; use it.

---

## References

### Story specs (read at T1 for context)

- [33-1 Generator Discovery](../../_bmad-output/implementation-artifacts/33-1-generator-discovery.md) + §Post-Close R1 Addendum
- [33-2 Pipeline Manifest SSOT](../../_bmad-output/implementation-artifacts/33-2-pipeline-manifest-ssot.md) §R1 Resolutions
- [33-1a Build v4.2 Generator](../../_bmad-output/implementation-artifacts/33-1a-build-v42-generator.md) §R1 Scope Resolutions
- [33-3 Regenerate v4.2 + Validate](../../_bmad-output/implementation-artifacts/33-3-regenerate-v42-and-validate.md)
- [33-4 Cora/Audra Block-Mode](../../_bmad-output/implementation-artifacts/33-4-cora-audra-block-mode.md)
- [15-1-lite-marcus META-TEST](../../_bmad-output/implementation-artifacts/15-1-lite-marcus.md)

### Epic-scope authority

- [Epic 33 §Standing Regime](../../_bmad-output/planning-artifacts/epics.md) — the binding framing this cheatsheet operationalizes.

### Related SKILL documents

- [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) — §HZ + §PC capabilities (post-33-4).
- [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) — §Capabilities CA row (post-33-4) + L1/L2 principles informing the deterministic-neck discipline.

### General BMAD governance

- [CLAUDE.md §BMAD sprint governance](../../CLAUDE.md) — party-mode consensus + bmad-code-review requirements.
- [docs/dev-guide/dev-agent-anti-patterns.md](./dev-agent-anti-patterns.md) — full anti-pattern catalog (27-2 hand-edit, 31-1 rename-one-surface, LLM-smuggling).
- [docs/dev-guide/story-cycle-efficiency.md](./story-cycle-efficiency.md) — K-floor discipline + aggressive DISMISS rubric.
