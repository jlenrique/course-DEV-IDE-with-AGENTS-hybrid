# Codex dispatch: Tier A trial-experience bundle (3 stories — Step 02A defaults + Irene Pass 2 authoring template + HUD per-step summaries)

**Session:** 2026-04-27 (operator-authorized post-Slab-6.1-formal-close, pre-first-tracked-trial)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.1 (`migration-6-1-production-graph-runner.md`) CLOSED; M5 condition #3 RESOLVED; migration unconditionally SHIPPED
- Composition Specification standing at `docs/dev-guide/composition-specification.md` (Option B / Path A-prime)
- Substrate Inventory Checklist standing at `docs/dev-guide/substrate-inventory-checklist.md` (N1–N12 binding)
- Anti-pattern catalog at `docs/dev-guide/specialist-anti-patterns.md` (A1–A17 + P1–P3)
- ~30 deferred-inventory items; this dispatch addresses 3 high-ROI Tier A items per operator decision 2026-04-27

**Mission:** implement three trial-experience-quality stories before the first tracked production trial. The three stories together eliminate the highest-friction operator surfaces identified in trial preparation work (B-Run §08 Irene Pass 2 friction; Step 02A re-entry burden; Step 03 HUD inspection workflow). Operator decision: bundle these three stories rather than land one and trial — friction-relief at-trial is the goal.

## Why this dispatch exists

Three deferred-inventory items surfaced as operator-experience HIGH friction during the 2026-04-19 to 2026-04-21 trial preparation work. Each was deferred because pre-Slab-6 substrate work took precedence; with Slab 6.0 + 6.1 closed and the migration unconditionally SHIPPED, the operator-experience work that was rate-limited by substrate is now unblocked.

The three items in scope:

1. **Step 02A prior-run directives as defaults** (~1pt single-gate; deferred-inventory line 75)
2. **Irene Pass 2 authoring template / schema contract** (~3-5pt dual-gate likely; deferred-inventory line 82) — **operator-flagged HIGHEST friction**
3. **HUD per-step expandable summaries** (~3-5pt single-gate likely; deferred-inventory line 77)

Total: ~7-11pt; ~28-46 hr Codex time. Phased delivery; parallelizable where independent.

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 + A17 + Slab 6.0 + Slab 6.1 instances.

## Phasing

```
Phase 1 ─── bmad-create-story per story (Codex; ~4-6 hr)
            Three story specs authored against seeds below
            Each runs through full bmad-create-story workflow
            Output: three migration-tier-a-* spec files

Phase 2 ─── Party-mode green-light per story (operator; ~1-2 hr per story)
            Operator convenes party-mode rounds via bmad-party-mode
            Each story green-lit with riders applied
            HALT if any story surfaces architectural disagreement requiring re-scope

Phase 3 ─── Implementation per story (Codex; ~24-40 hr total)
            A1 (Step 02A defaults) first — smallest scope; unblocks A2 indirectly
            A2 (Irene Pass 2 template) and A3 (HUD summaries) parallelizable
            Each story honors substrate inventory checklist N-item trace
            Each story honors anti-pattern catalog (A1-A17 + P3)

Phase 4 ─── bmad-code-review per story (separate dispatch; ~6-9 hr Codex)
            One bundled review dispatch covering all three diffs
            Same N-item trace section discipline as Slab 6.0
            Triage: patch / defer / dismiss / decision_needed

Phase 5 ─── Formal close per story (operator; ~30 min total)
            sprint-status flips per story
            deferred-inventory entries flip RESOLVED per story
            Tier A bundle complete; first tracked trial unblocked
```

## Story seeds (Phase 1 input)

### Story A1 — Step 02A prior-run directives as defaults

**Story key candidate:** `tier-a-1-step-02a-prior-run-directives-as-defaults`

**Sprint key seed:** `tier-a-1-step-02a-prior-run-directives`

**Pts:** ~1 (single-gate; minor enhancement to existing Marcus PR-* capability OR Step 02A pack procedure)

**Gate mode:** single-gate (governance-JSON entry to be added at filing; rationale: minor enhancement to existing surface with no schema-shape risk)

**Story seed prompt for `bmad-create-story`:**
> Title: "Step 02A surfaces prior-run operator directives as named defaults"
> Context: deferred-inventory line 75 — operator-surfaced 2026-04-19 trial run during Step 02A poll; "hardwire before next run." Marcus currently surfaces prior-run `operator-directives.md` on request only; required: Step 02A always scans prior bundles for the most recent `operator-directives.md` for the same `lesson_slug`, presents them as named defaults with source attribution (`run_id` + date), and requires explicit accept/modify/replace before writing. Eliminates re-entry burden on resumed or repeated runs.
> Architecture decision needed at T1: natural home is either (a) Marcus PR-* capability extension OR (b) Step 02A pack procedure amendment. Operator preference for surface that minimizes cross-Marcus regression risk; party-mode adjudicates if Codex T1 surfaces ambiguity.
> Inheritance: read Marcus PR-* documentation at `skills/bmad-agent-marcus/references/`; read Step 02A pack procedure; read existing Maya prior-run-protocol patterns.
> Substrate inventory checklist: N4 (per-component isolation invariant — Marcus contract preserved); N9 (operator-witnessed evidence — operator confirms defaults workflow at story close).

**Effort estimate:** ~4-6 hr Codex time (single-gate; small surface).

**File structure (hint; final per spec):**
- Modified: either `app/marcus/intake/lesson_plan/orchestrator/facade.py` Step 02A handler OR Marcus PR-* capability surface (T1 ratifies which)
- NEW test: `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py` (~3 tests: present-prior-bundle / no-prior-bundle / explicit-accept-modify-replace)
- Modified docs: `docs/operator/<step-02a-or-marcus-pr-doc>` updated

**K-target:** ~1.4× (target ~6 / floor ~5).

**N-item trace required:** N4, N9 minimum.

---

### Story A2 — Irene Pass 2 authoring template / schema contract

**Story key candidate:** `tier-a-2-irene-pass-2-authoring-template`

**Sprint key seed:** `tier-a-2-irene-pass-2-authoring-template`

**Pts:** ~3-5 (dual-gate likely; new schema surface + Irene authoring contract)

**Gate mode:** dual-gate (governance-JSON entry to be added at filing; rationale: `schema_shape` — new authoring template + JSON Schema constraint; `invariant_preservation` — existing `validate-irene-pass2-handoff.py` validator contract preserved + made explicit via schema)

**Story seed prompt for `bmad-create-story`:**
> Title: "Irene Pass 2 authoring template encodes validator contract as explicit schema constraints"
> Context: deferred-inventory line 82 — operator-flagged 2026-04-20 trial run B-Run §08 after Pass 2 work product required exceptional post-hoc repair across two full sessions. The `validate-irene-pass2-handoff.py` validator's strict contract (exact behavioral-intent form, 4+-char token-level narration pre-seeding, absolute path matching, valid `visual_detail_load` values, bridge-cadence mechanics, cluster arc integrity rules) is implicit in validator code and not surfaced to Irene at composition time. Operator-flagged "single highest-friction step in production pipeline observed this trial."
> Required: structured Irene Pass 2 authoring template that encodes the validator's implicit contract as explicit schema constraints + inline authoring guidance, so `segment-manifest.yaml` and `pass2-envelope.json` can be produced in one pass without post-hoc debugging.
> Architecture decisions needed at T1: (a) authoring-template format — Pydantic v2 model + JSON Schema (four-file-lockstep per `pydantic-v2-schema-checklist.md`)? Markdown template with embedded YAML examples? Both? (b) where the template lives — `app/specialists/irene/authoring/`? `skills/bmad-agent-content-creator/references/`? `state/config/schemas/`? (c) how Irene consumes the template at composition time — sanctum-loaded reference? Run-time validator with helpful errors? Both?
> Inheritance: read existing `validate-irene-pass2-handoff.py`; read `app/specialists/irene/` scaffold; read `skills/bmad-agent-content-creator/references/`; read existing pass-2-authoring-template per Class B forward-port deferred (line 173).
> Substrate inventory checklist: N4 (per-specialist isolation invariant — Irene contract preserved); N5 (cross-component state-flow contract — pass2-envelope shape stable); N7 (replay regression — existing fixtures pass against new schema); N9 (operator-witnessed evidence at story close); N11 (composition mode declared alongside isolated mode — template usable in both M3 harness and production runner contexts).

**Effort estimate:** ~12-20 hr Codex time (dual-gate; new schema; multiple authoring surfaces).

**File structure (hint; final per spec):**
- NEW: `app/specialists/irene/authoring/pass_2_template.py` (Pydantic v2 strict; four-file-lockstep)
- NEW: `schema/irene_pass_2_authoring.v1.schema.json`
- NEW: `tests/unit/specialists/irene/test_pass_2_template_strict.py`
- NEW: `tests/fixtures/specialists/irene/pass_2_template_golden.json`
- NEW: `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py` — proves new template's constraints match `validate-irene-pass2-handoff.py` contract end-to-end
- NEW: `docs/dev-guide/irene-pass-2-authoring.md` — operator-facing authoring guide
- Modified: `app/specialists/irene/graph.py` `_act` body — load template at composition time; use as authoring contract
- Modified: existing `validate-irene-pass2-handoff.py` — refactored to consume new template's constraints (single source of truth)
- Modified: `skills/bmad-agent-content-creator/references/` — pointer to new authoring guide

**K-target:** ~1.4× (target ~16 / floor ~12).

**N-item trace required:** N4, N5, N7, N9, N11.

**Decision_needed candidates surfaced at T1:**
- Template format (Pydantic + JSON Schema vs Markdown vs both)
- Template location
- Run-time validation vs build-time validation vs both

**Halt-and-adapt budget:** built in. Particularly likely surfaces: (1) the validator contract may not cleanly express in schema (rules involving cluster arc continuity may need procedural validation); (2) Irene's `_act` may need scaffold-conformance review if loading template changes the act-body category from pure-LLM to LLM+template-validation.

---

### Story A3 — HUD per-step expandable summaries

**Story key candidate:** `tier-a-3-hud-per-step-expandable-summaries`

**Sprint key seed:** `tier-a-3-hud-per-step-expandable-summaries`

**Pts:** ~3-5 (single-gate likely; new HUD surface; no schema-shape risk; pure operator-experience)

**Gate mode:** single-gate (governance-JSON entry to be added at filing; rationale: HUD enhancement; no schema-shape risk; no substrate-touching contracts)

**Story seed prompt for `bmad-create-story`:**
> Title: "HUD per-step expandable summaries surface real-time content captured + locked at each step"
> Context: deferred-inventory line 77 — operator-surfaced 2026-04-19 trial run during Step 03 hold. Each pipeline step in the HUD should have an expandable section showing real-time summary of content captured and locked at that step (e.g., Step 01 shows preflight receipt; Step 02 shows source authority map; Step 03 shows extraction quality report). Operator can inspect any completed step without leaving the HUD.
> Architecture decisions needed at T1: (a) summary content per step — derived from existing artifacts in `bundles/<run_id>/` OR new per-step summary emitter? (b) HUD interaction model — keyboard expand/collapse? Always-expanded with collapsed-overflow? Per-step toggle persisted across HUD sessions? (c) live update cadence — pull on HUD refresh OR push from step-completion event? (d) how the per-step summary integrates with `--watch` HUD landing per Batch 3 hud-modernization.
> Inheritance: read existing HUD implementation at `scripts/run_hud.py`; read Batch 3 `hud-modernization` story spec at `_bmad-output/implementation-artifacts/`; read existing per-step bundle artifact conventions at `docs/operator/hud-guide.md`.
> Substrate inventory checklist: N4 (per-component isolation — HUD changes don't affect runtime); N9 (operator-witnessed evidence — operator validates per-step summary readability at story close).

**Effort estimate:** ~12-20 hr Codex time (single-gate; new UI surface; ~14 step types to cover).

**File structure (hint; final per spec):**
- Modified: `scripts/run_hud.py` — add per-step expandable summary rendering
- NEW: `app/hud/per_step_summary.py` (or equivalent; module that derives summaries from existing bundle artifacts)
- NEW: per-step summary derivation functions for each of the 14 manifest step types (likely small functions per step; parametrize tests)
- NEW: `tests/integration/hud/test_per_step_summary_rendering.py` — covers all 14 step types' summary rendering
- NEW: `tests/unit/hud/test_per_step_summary_derivation.py` — covers each derivation function
- Modified: `docs/operator/hud-guide.md` — document the expand/collapse interaction model

**K-target:** ~1.4× (target ~18 / floor ~14).

**N-item trace required:** N4, N9.

**Decision_needed candidates surfaced at T1:**
- Summary derivation source (existing artifacts vs new emitter)
- Interaction model (keyboard / mouse / persisted state)
- Live update cadence

**Halt-and-adapt budget:** built in. Particularly likely surfaces: (1) some step types may not have existing artifacts that yield meaningful summaries — may require additional per-step emission work in the manifest pipeline (out-of-scope for this story; would defer); (2) HUD library / TUI framework may constrain interaction model.

---

## Phase 1 execution rules

For each story (A1, A2, A3), Codex runs `bmad-create-story` with the seed prompt above. The bmad-create-story workflow produces:
- T1 Readiness Block
- TEMPLATE scope decisions
- Story (As-a / I-want / So-that)
- Acceptance Criteria (full set)
- File Structure Requirements
- Testing Requirements
- Effort estimate
- D12 close protocol

**Output paths:**
- A1: `_bmad-output/implementation-artifacts/migration-tier-a-1-step-02a-prior-run-directives.md`
- A2: `_bmad-output/implementation-artifacts/migration-tier-a-2-irene-pass-2-authoring-template.md`
- A3: `_bmad-output/implementation-artifacts/migration-tier-a-3-hud-per-step-expandable-summaries.md`

**Sandbox-AC validator:** run per CLAUDE.md migration-story governance after each story spec lands. PASS expected (no operator-only CLI invocations expected in dev-agent ACs; if surfaced, refactor per CLAUDE.md sandbox-AC rules).

**Governance JSON update:** add three entries to `docs/dev-guide/migration-story-governance.json` per story key with the gate-mode designations above. Version bump to `2026-04-XX-tier-a` (or appropriate date when this dispatch executes).

**Halt rule:** if any story spec surfaces architectural disagreement that the seed didn't anticipate, halt Phase 1 for that story and surface to operator with `decision_needed` framing. The other two stories proceed independently.

## Phase 2 execution rules (operator action; not Codex)

Operator convenes party-mode green-light per story. Standard `bmad-party-mode` invocation; agents include Winston (architect) + Murat (test architect) + Paige (tech writer) + Amelia (dev) at minimum. Per-story rounds; riders applied; spec amended.

**Halt rule:** if any party-mode round impasses on architecture, halt that story; proceed with the others. Re-convene with additional voices as needed.

## Phase 3 execution rules (implementation)

Codex implements per ratified story spec. Standard halt-and-surface discipline:
- **Substrate disagreement:** HALT and surface
- **`decision_needed` items:** name each option + tradeoff; do not silently choose
- **N-item FAIL during dev:** auto-promote to in-story `patch` work; do not defer N-item failures

**Sequencing:**
- A1 first (smallest; quickest). Lands ~4-6 hr.
- A2 + A3 in parallel where Codex environment allows (independent code surfaces; no shared modules)
- If parallel not possible: A2 second (highest operator-priority); A3 third

**Substrate inventory checklist:** read `docs/dev-guide/substrate-inventory-checklist.md` at T1 of each story; identify applicable N-items; trace each in implementation work.

**Anti-pattern catalog:** read `docs/dev-guide/specialist-anti-patterns.md` at T1; honor counter-patterns. Particularly relevant for this dispatch:
- A2 likely touches A12 (procedural-coupling) territory if Irene authoring requires manual step elsewhere — verify generator-emit covers
- A3 likely touches A9 (Epic-doc structural-name drift) if HUD step naming diverges from manifest step naming — verify alignment

## Phase 4 execution rules (separate dispatch; bmad-code-review on Tier A bundle)

Operator authors a separate dispatch at `_bmad-output/implementation-artifacts/codex-handoff-tier-a-code-review.md` after Phase 3 lands. The dispatch follows the same template as `codex-handoff-slab-6-0-code-review.md`:
- Three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) per story
- Per-story N-item trace section as first-class deliverable
- Triage: patch / defer / dismiss / decision_needed
- Required deliverable: `_bmad-output/implementation-artifacts/tier-a-code-review-2026-04-XX.md`

May be bundled as one review pass covering all three diffs OR split into per-story reviews. Operator preference: bundle if reviews can fit in one Codex session; split if cumulative diff is too large for productive review.

## Phase 5 execution rules (operator action; formal close per story)

Per story:
1. `sprint-status.yaml` flips `tier-a-N-*: review` → `done`
2. Deferred-inventory entry flips RESOLVED with cite to closing story
3. `next-session-start-here.md` updated if present (likely NOT in repo policy per Slab 6.0 close finding)
4. Composition Spec §10 Decision Log entry per story if any composition-affecting decision was made

When all three close:
- Migration's "first tracked trial" precondition satisfied
- Operator queues first tracked trial per Composition Spec §11 evidence-harvest discipline (different specialist chains; different `_act` body categories; different gate paths)

## Substrate Inventory Checklist application across the bundle

Per-story applicability summary (full per-N trace recorded in each story's spec + each story's bmad-code-review §):

| N-item | A1 | A2 | A3 | Bundle-wide notes |
|---|---|---|---|---|
| N1 — External-provider resource ID validity | N/A | N/A | N/A | No new external resources introduced |
| N2 — Composition exercise before vote | N/A | applicable (party-mode) | N/A | A2 spec amended via party-mode satisfies this |
| N3 — Live-API smoke before MVP close | N/A | N/A | N/A | Migration already SHIPPED; no MVP gate fires |
| N4 — Per-component isolation invariant preserved post-composition | applicable | applicable | applicable | Each story preserves existing isolation invariants |
| N5 — Cross-component state-flow contract | N/A | applicable | N/A | A2 touches Irene→downstream contract |
| N6 — Gate boundary scope hierarchy | N/A | N/A | N/A | No new gates introduced |
| N7 — Replay regression verifies execution path | N/A | applicable | N/A | A2 must preserve existing replay-regression on Pass 2 fixtures |
| N8 — Cost machinery integration with real trace data | N/A | N/A | N/A | No cost-engineering changes |
| N9 — Operator-witnessed evidence at M-gate vote | applicable | applicable | applicable | Each story closes with operator validation |
| N10 — Anti-pattern catalog read at architecture-authoring time | applicable | applicable | applicable | Codex reads catalog at T1 of each story |
| N11 — Composition mode declared alongside isolated mode | N/A | applicable | N/A | A2 template usable in both M3 harness and production runner |
| N12 — Auth model verified via probe | N/A | N/A | N/A | No new external auth introduced |

## Anti-pattern catalog application

Codex reads `docs/dev-guide/specialist-anti-patterns.md` at T1 of each story. Particularly relevant entries per story:

**A1 (Step 02A defaults):**
- A8 (workflow assumes single-shot operator input) — counter-pattern: support resumed/repeated runs; this story directly implements that counter-pattern
- A11 (Windows-portability hostile path handling) — Marcus PR-* paths must be portable

**A2 (Irene Pass 2 template):**
- A6 (validator contract implicit in code) — counter-pattern: surface validator contract as explicit schema; this story implements the counter-pattern
- A12 (procedural-coupling between specialist + ancillary surfaces) — verify any new manual step gets generator-emit coverage
- P3 (composition-shape vote without end-to-end exercise) — party-mode green-light at Phase 2 must include composition smoke check (template usable in both isolated + composed contexts)

**A3 (HUD per-step summaries):**
- A9 (Epic-doc structural-name drift from Slab-1-hardened reality) — HUD step naming must align with manifest step naming
- A11 (Windows-portability hostile path handling) — HUD reads from `bundles/<run_id>/` paths

## Disposition rules

Standard halt-and-surface discipline:
- **Substrate disagreement:** HALT and surface
- **`decision_needed` items:** name each option + tradeoff; do not silently choose
- **N-item FAIL during dev:** auto-promote to in-story `patch` work
- **`patch` items in code review:** addressed in commits before close
- **`defer` items in code review:** filed as deferred-inventory entries with explicit reactivation gates
- **`dismiss` items in code review:** justified inline (1-2 sentences)

## Deliverable

When the bundle is complete:
1. Three story specs at `_bmad-output/implementation-artifacts/migration-tier-a-{1,2,3}-*.md`
2. Three party-mode-ratified specs (operator action between Phase 1 and 3)
3. Three implementation surfaces landed via themed commits per story
4. One bundled bmad-code-review deliverable at `_bmad-output/implementation-artifacts/tier-a-code-review-2026-04-XX.md`
5. Three sprint-status flips + three deferred-inventory updates
6. Final Codex report naming: per-story tests passing; per-story N-item trace summary; per-story `decision_needed` items surfaced; cumulative files changed; operator-action checklist for Phase 2 + Phase 5

## Closeout

After all three stories close:
- File entry in `docs/dev-guide/composition-specification.md` §10 Decision Log if any composition-affecting decision was made (likely A2)
- Operator queues first tracked trial run per Composition Spec §11 evidence-harvest discipline
- Tier B / Tier C / Tier D decisions become trial-evidence-driven per Composition Spec §11 migration triggers + N-item trace records

## Substrate Inventory Checklist availability

Per Slab 6.0 governance, every Codex slab dispatch from this point forward must:
1. Read the checklist at T1
2. Identify which N-items apply to the slab in scope
3. Have the Acceptance Auditor (in code review) verify each applicable N-item is honored
4. File N13+ extensions if a NEW substrate concern surfaces

For this Tier A bundle: per-story N-item applicability is named in the table above; honor it.

## What this dispatch does NOT do

- Does NOT touch the Slab 6.0 substrate (envelope + adapter + composition discipline) — out of scope
- Does NOT touch the Slab 6.1 production runner — out of scope (Slab 6.1 is closed; trial-experience work is independent)
- Does NOT add new specialists — the 6 unbuilt specialists (Mike/Eli/Enrique/Mira/Sally/Kim) remain deferred per deferred-inventory `Post-M5 Greenfield Specialists` entry
- Does NOT add Tier B (theatrical-direction synthesis) — operator decision: defer until first trial reveals dials-only ceiling
- Does NOT add Tier C (substrate hardening) — operator decision: defer until first trial reveals substrate stress
- Does NOT add Epic 15 learning intelligence chain — gated on first tracked trial completing (per Epic 15 seed)

These deferrals are deliberate per operator decision 2026-04-27 to bundle three highest-ROI items + run first trial + iterate based on trial evidence.
