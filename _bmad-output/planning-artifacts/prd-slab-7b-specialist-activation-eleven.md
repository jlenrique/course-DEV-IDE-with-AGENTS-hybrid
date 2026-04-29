---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
draftedAt: '2026-04-29'
ratifiedAt: '2026-04-29'
draftMode: 'pre-fill-for-operator-review-then-party-mode-ratified-9-rounds'
status: 'complete-ready-for-bmm-workflow-status-update-and-implementation-readiness-check'
ratificationLog:
  rounds: 9
  voicesPerRound: 4
  unanimousVerdict: 'RATIFIED-WITH-AMENDMENTS (R1-R8); RATIFIED-WITH-AMENDMENTS-AND-CLOSE (R9)'
  scopeFloorAllGreen: true  # SG-1 + SG-2 + SG-3 + SG-4 verified at R9 close across all R1-R8 amendments
  reOpens: 0
  amendmentRecord: 'See §Polish-Pass Notes §Round-by-round amendment record'
note: |
  Per operator directive 2026-04-29 ("draw upon 7a PRD, the current repo, and planning document to pre-fill as many of the steps of this PRDs production so that that language can be reviewed rather than created from scratch"), this PRD is pre-filled
  end-to-end before any party-mode round opens. Each section is drafted from:
    (a) prd-slab-7a-inter-gate-orchestration.md as structural baseline + sibling cohesion;
    (b) slab-7-legacy-migrated-mapping-checklist.md (33 rows; ~9 specialist-body-deferred rows are Slab 7b's primary activation surface);
    (c) Slab 7a yaml `slab7bSpecialistRoster` block (operator-ratified 2026-04-28; defines per-specialist Slab-7b shape);
    (d) docs/dev-guide/composition-specification.md (SG-3 invariants);
    (e) docs/dev-guide/migration-story-governance.json (gate-mode designations);
    (f) next-session-start-here.md §"Slab 7a → Slab 7b inheritance hooks";
    (g) docs/project-context.md, sprint-status.yaml, deferred-inventory.md (live state).
  Operator review modality: each section reads as proposed-final language; party-mode rounds (per Slab 7a precedent) ratify, refine, or amend the pre-filled drafts rather than author from scratch.
  Step-12 (workflow close) is intentionally NOT in stepsCompleted — close occurs after operator review + party-mode ratification of any amendments.
metaDirective:
  partyModeForRemainingSteps: true
  consensusOrSupermajorityRequired: true
  reviewMode: 'party-mode-ratifies-pre-filled-language-not-from-scratch'
  scopeFloorGuardrails:
    specialistRoster:
      mustNotReduceBelow: 11
      named: ['Texas', 'Irene', 'Dan', 'Tracy', 'Gary', 'Kira', 'Wanda', 'Enrique', 'Compositor', 'Quinn-R', 'Vera']
      enforcement: 'Inherited verbatim from Slab 7a PRD; SG-1 unchanged.'
    legacyWorkflowSteps:
      mustNotDropFromMappingChecklist: 33
      checklistPath: '_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md'
      enforcement: 'Inherited verbatim from Slab 7a PRD; SG-2 unchanged.'
    compositionSpecInvariants:
      paths: ['§3.1', '§3.5', '§3.6', '§6', '§9', '§10', '§11']
      enforcement: 'Inherited verbatim from Slab 7a PRD; SG-3 unchanged. Slab 7b parity-test suite extends 7a.8 suite to assert each specialist body honors SG-3.'
    sanctumAlignment:
      newGuardrail: 'SG-4'
      named: 'BMB sanctum alignment for every specialist body activated by this slab'
      rule: 'Every Slab 7b body-activation story MUST either (a) align its SKILL.md with the standard sanctum activation block matching the Marcus/Irene/Dan/Texas BMB pattern, OR (b) deliberately document an exception in SKILL.md with explicit rationale (Cora-sidecar precedent). Silent omission = HALT-AND-REMEDIATE at code review.'
      enforcement: 'Per-story AC; reviewer verifies SKILL.md alignment-or-documented-exception; structural parity-test test_skill_md_sanctum_alignment.py asserts every name in app/specialists/{name}/ has either (a) frontmatter pattern matching BMB scaffold-v0.2 OR (b) `# Sanctum exception` block in SKILL.md with rationale.'
      precedents:
        align_option_a: ['Marcus', 'Irene', 'Dan', 'Texas']
        documented_exception_option_b: ['Cora']
slab7bSpecialistRoster:
  count: 11
  inheritedFrom: 'Slab 7a PRD slab7bSpecialistRoster block (operator-ratified 2026-04-28); shape values reproduced here verbatim for cold-pickup.'
  specialists:
    texas: { skill: 'bmad-agent-texas', appDir: 'app/specialists/texas/', sidecar: 'texas-sidecar', status: 'partial-active', slab7bShape: 'hardening-post-directive-composer', sanctumAlignment: 'option-a-already-aligned', actBodyShape: 'live-retrieval-against-real-directive-composer' }
    irene: { skill: 'bmad-agent-content-creator', appDir: 'app/specialists/irene/', sidecar: 'irene-sidecar', status: 'pass2-done-pass1-pending', slab7bShape: 'pass1-activation', sanctumAlignment: 'option-a-already-aligned', actBodyShape: 'pass1-coauthor-mirroring-pass2-shape' }
    dan: { skill: null, appDir: null, sidecar: 'dan-sidecar', status: 'sidecar-only', slab7bShape: 'greenfield-via-bmad-create-specialist', sanctumAlignment: 'option-a-required-at-creation', actBodyShape: 'narrow-lane-creative-director-aux-contributions' }
    tracy: { skill: 'bmad-agent-tracy', appDir: 'app/specialists/tracy/', sidecar: null, status: 'passthrough', slab7bShape: 'port-shape-plus-sidecar-creation', sanctumAlignment: 'option-a-required-at-port', actBodyShape: 'live-research-enrichment-pass2-companion' }
    gary: { skill: 'bmad-agent-gamma', appDir: 'app/specialists/gary/', sidecar: 'gary-sidecar', status: 'passthrough', slab7bShape: 'port-shape', sanctumAlignment: 'option-a-required-at-port', actBodyShape: 'live-gamma-api-variant-generation' }
    kira: { skill: 'bmad-agent-kling', appDir: 'app/specialists/kira/', sidecar: 'kira-sidecar', status: 'passthrough', slab7bShape: 'port-shape', sanctumAlignment: 'option-a-required-at-port', actBodyShape: 'live-kling-api-motion-generation' }
    wanda: { skill: 'bmad-agent-wondercraft', appDir: 'app/specialists/wanda/', sidecar: 'wanda-sidecar', status: 'client-landed-not-on-scaffold', slab7bShape: 'port-shape-onto-scaffold', sanctumAlignment: 'option-a-required-at-port', actBodyShape: 'live-wondercraft-api-podcast-bed' }
    enrique: { skill: 'bmad-agent-elevenlabs', appDir: 'app/specialists/enrique/', sidecar: 'enrique-sidecar', status: 'passthrough', slab7bShape: 'port-shape', sanctumAlignment: 'option-a-required-at-port', actBodyShape: 'live-elevenlabs-api-narration-synthesis' }
    compositor: { skill: 'compositor', appDir: null, sidecar: null, status: 'skill-only', slab7bShape: 'greenfield-via-kind-deterministic-scaffold', sanctumAlignment: 'option-a-required-at-creation-or-option-b-documented-exception', actBodyShape: 'deterministic-pipeline-no-llm-call' }
    quinn_r: { skill: 'bmad-agent-quality-reviewer', appDir: 'app/specialists/quinn_r/', sidecar: 'quinn-r-sidecar', status: 'activated-slab-2a-era', slab7bShape: 'hardening-only-against-real-content-from-port-shape-specialists', sanctumAlignment: 'option-a-required-at-hardening', actBodyShape: 'two-mode-precomposition-postcomposition' }
    vera: { skill: 'bmad-agent-fidelity-assessor', appDir: 'app/specialists/vera/', sidecar: 'vera-sidecar', status: 'activated-slab-2a-era', slab7bShape: 'hardening-only-against-G0-G1-G4-rubric-semantics-on-real-content', sanctumAlignment: 'option-a-required-at-hardening', actBodyShape: 'single-mode-with-sensory-bridges-dispatch' }
  sandboxAcInventoryPrecondition:
    - gamma  # forbidden in dev-agent ACs (port for Gary)
    - kling  # forbidden in dev-agent ACs (port for Kira)
    - elevenlabs  # forbidden in dev-agent ACs (port for Enrique)
    - wondercraft  # forbidden in dev-agent ACs (port for Wanda)
    - 'dan-api-tbd'  # status TBD pending Dan's specialist-shape design — to be resolved at Step 6 of dan greenfield story
  cacheHitHarnessConfigs:
    parametric: true
    perSpecialistCount: 10
    plus_one_pipeline_determinism_harness: 'compositor'
classification:
  projectType: 'Internal multi-agent runtime extension (specialist body-activation layer atop Slab 7a orchestration substrate)'
  domain: 'Online course content production / collaborative AI infrastructure'
  complexity: 'high'
  projectContext: 'brownfield'
  brownfieldNotes: 'Slab 7a substrate SHIPPED + CLOSED 2026-04-29 (commit 95c81b0; 8/8 stories done; substrate-completeness MVP achieved). Slab 7b runs on top of 7a substrate (directive composer, manifest fold-flags, vocabulary registry, per-slide subgraph skeleton, HTML review-pack skeleton, calibration-tripwire substrate, conversation persistence + summary writer, Marcus-duality boundary at dispatch_adapter.py:81). Slab 7a 696 passed/19 skipped regression baseline holds.'
  governanceFloor:
    - 'Composition Specification (Option B / Path A-prime) — gate-precedence + dependency_map sourcing + chain-test-per-PR (inherited from Slab 7a)'
    - 'Pipeline Manifest Regime — Tier-2 minor pack-version bump (this PRD; activation extends but does not break v4.2 schema)'
    - 'Migration Story Governance JSON (frozen 2026-04-22) + sandbox-AC validator (5-entry inventory PR is hard precondition before any port-shape Slab 7b story opens)'
    - 'BMAD sprint governance (CLAUDE.md): bmad-create-prd → party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story; bmad-code-review before done'
    - 'BMB sanctum alignment (NEW SG-4): every body-activation story aligns SKILL.md with sanctum activation block OR documents exception; reviewer verifies; structural parity-test enforces.'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md
  - _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md
  - _bmad-output/implementation-artifacts/slab-7a-retrospective.md
  - _bmad-output/planning-artifacts/deferred-inventory.md
  - _bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md
  - docs/dev-guide/composition-specification.md
  - docs/dev-guide/migration-story-governance.json
  - next-session-start-here.md
  - docs/project-context.md
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 9
workflowType: 'prd'
slabId: 'slab-7b'
slabName: 'Specialist Activation — Eleven-Specialist Roster Body-Activation atop Slab 7a Orchestration Substrate'
parentMigrationPRD: '_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md'
siblingPRDs:
  - _bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md  # CLOSED 2026-04-29; this PRD inherits substrate
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md  # parent migration PRD
  - _bmad-output/planning-artifacts/prd.md  # legacy Wave 2B PRD (frozen reference, not relevant scope)
plannedSiblingPRDs:
  - prd-doc-slab-7-prose-harvest.md  # Doc-Slab 7-D — post-trial-2 prose harvest (sequenced after first tracked trial-2)
---

# Product Requirements Document — Slab 7b: Specialist Activation (Eleven-Specialist Roster Body-Activation)

**Author:** Juanl
**Date:** 2026-04-29
**Status:** Pre-filled draft for operator review (Step 11 polish landed; Step 12 close pending party-mode ratification)
**Project:** course-DEV-IDE-with-AGENTS (hybrid clone, `dev/langchain-langgraph-foundation` branch)
**Pack version target:** v4.2 (Tier-2 minor extension; activation-only, no schema-breaking changes)
**Distinct artifact:** Sibling to `prd-slab-7a-inter-gate-orchestration.md` (CLOSED 2026-04-29). Slab 7b activates the eleven-specialist roster into the orchestration scaffold Slab 7a delivered.

---

## Operator Non-Negotiables (Read First)

These four guardrails are operator-ratified and bind every section, story, and dev-cycle of Slab 7b. Three are inherited verbatim from Slab 7a; one is new.

- **SG-1 (Specialist roster floor — INHERITED):** the eleven specialists named for Slab 7b activation — **Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera** — cannot be reduced. Enforced structurally by NFR-I7 carry-forward (`len(specialists) == 11` build assertion) + Slab 7b parity-test suite extension `tests/parity/test_eleven_specialists_addressable.py`.
- **SG-2 (Legacy workflow step floor — INHERITED):** the **33-row mapping checklist** (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`) cannot lose rows. Slab 7b's job is to convert the 27 ❌ rows + 7 ⚠️ rows toward ✅; outright drops auto-rejected. Enforced structurally by NFR-I6 carry-forward + extended parity-test suite.
- **SG-3 (Composition Spec invariants — INHERITED):** Composition Specification §3.1 SHA256+append-only, §3.5 gate precedence, §3.6 manifest-declared dependencies, §6 chain-test-per-PR, §9 Composition Smoke gate, §10 Decision Log, §11 migration triggers — all seven sections enforced structurally by NFR-I8 carry-forward + per-specialist body chain-test PRs.
- **SG-4 (BMB sanctum alignment — NEW; party-mode-ratified Round 1 with amendments):** every Slab 7b body-activation story MUST either (a) align its `SKILL.md` with the standard BMB sanctum activation pattern matching the **Marcus / Irene / Dan / Texas** precedent, OR (b) document a **structural exception** drawn from the closed allowlist in `docs/dev-guide/sanctum-exception-categories.json` (initial entry: `sidecar-hook` per **Cora** precedent), with the matching category cited verbatim in `SKILL.md` AND party-mode consensus recorded in the story's planning artifact. "BMB sanctum alignment" is operationally defined by `docs/dev-guide/bmb-sanctum-alignment-checklist.md` (Slab 7b foundational artifact authored before the first body-activation story opens) — the parity-test and the reviewer both reference that document.

  **Upstream enforcement (primary defense):** `bmad-create-specialist` (and any workflow used to scaffold Slab 7b body-activation stories) MUST emit the BMB sanctum activation block by default, so option-(b) requires affirmative author action. Slab 7b kickoff (story 7b.0 — pre-activation scaffolding) pre-creates all eleven `app/specialists/{name}/` directories with stub `SKILL.md` frontmatter retrofitted from day one; per-story body activation is additive (logic + sanctum content), not creative. Code-review HALT is the trailing check, not the primary defense; reviewer is belt-and-suspenders, not co-equal with the parity-test gate.

  **Trailing enforcement (parity-test gate):** structural parity-test `tests/parity/test_skill_md_sanctum_alignment.py` (NEW NFR-I9). Test contract:
  - (i) enumerates the eleven-specialist roster from SG-1; asserts each name has a directory at `app/specialists/{name}/` containing `SKILL.md` (missing dir or missing SKILL.md = FAIL, not skip);
  - (ii) parses each `SKILL.md` frontmatter as YAML; asserts required keys (`agent_name`, `sanctum_path`, `activation_order`) present AND `sanctum_path == f"_bmad/memory/bmad-agent-{name}/"` derived from dir name (catches copy-paste bugs and shape-drift, not just presence);
  - (iii) for option-(b) cases, asserts `# Sanctum exception: <category>` heading where `<category>` matches a row in `sanctum-exception-categories.json`, AND a `## Rationale` subsection ≥80 chars explicitly referencing "sanctum activation" or "BMB pattern" by name.

  Silent omission OR free-text rationale OR unilateral exception-without-party-mode-consensus OR shape-drift at code review = HALT-AND-REMEDIATE.

Subsequent mentions reference these guardrails as `(per SG-1)`, `(per SG-2)`, `(per SG-3)`, or `(per SG-4)` rather than re-enumerating.

## Three-Slab Trilogy at a Glance (carried forward from Slab 7a)

| PRD | Scope | Status | Sequenced |
|---|---|---|---|
| `prd-langchain-langgraph-migration.md` | Migration foundation (5 slabs, M1–M5) | SHIPPED at `97842ac` (2026-04-27) | — |
| `prd-slab-7a-inter-gate-orchestration.md` | 13 substrate-completeness deliverables across 5 clusters; orchestration layer | **CLOSED** at `95c81b0` (2026-04-29; 8/8 stories done) | First (closed) |
| **`prd-slab-7b-specialist-activation-eleven.md`** | **Activates eleven-specialist roster into Slab 7a substrate; converts 27 ❌ + 7 ⚠️ mapping-checklist rows toward ✅; this document** | **Draft (pre-filled)** | **Second (current)** |
| `prd-doc-slab-7-prose-harvest.md` | Post-trial-2 anti-pattern catalogs + worked examples + re-authored v4.2 essential-function reference (~400-line distillation) | Planned | Third (after first tracked trial post-7b) |

## Quick Reference (cold-pickup anchors)

| Question | Location |
|---|---|
| What does Slab 7b do? (JTBD) | Executive Summary §opening sentence |
| Why does it exist? (Slab 7a substrate inheritance) | Executive Summary §"Substrate inherited; bodies pending" |
| What constitutes done? (trial-2 acceptance) | Success Criteria §A-1..A-7 + Project Scoping §MVP exit gate |
| Scope-binding commitments | Executive Summary §Scope-Binding Commitments |
| 11 specialists (canonical enumeration + per-specialist Slab-7b shape) | Functional Requirements §FR-7b-roster + frontmatter `slab7bSpecialistRoster` block |
| 33-row mapping checklist (which rows Slab 7b activates) | Domain Requirements §"Mapping-checklist activation surface" |
| K-floor / target-range | NFR-T1 (canonical); NFR-CG5 cross-refs |
| Failure-mode (FM) checks | Success Criteria §Slab-7b-Shaped Failure Modes (FM-1..FM-12) |
| Innovation risks (IR) | Innovation & Novel Patterns §Risk Mitigation (IR-1..IR-9) |
| Scoping risks (SR) | Project Scoping & Phased Development §Risk-Based Scoping (SR-T1..SR-R5) |
| Sanctum-alignment matrix (SG-4) | Functional Requirements §FR-7b-sanctum + Domain Requirements §"BMB activation pattern" |

## Glossary (acronyms used throughout — inherited from Slab 7a)

- **JTBD** — Jobs-To-Be-Done
- **HIL** — Human-In-Loop
- **FM** — Failure Mode
- **ADR** — Architecture Decision Record
- **K-floor / K-units** — story-cycle-efficiency discipline
- **FR / NFR** — Functional / Non-Functional Requirement
- **SG-1/2/3/4** — Standing Guardrails (above)
- **CG-** — Compliance & Governance NFR / Domain Requirement ID
- **BMB** — BMad Method Builder (the workflow that produces sanctum-shaped specialist agents)
- **Sanctum** — `_bmad/memory/bmad-agent-{name}/` directory holding persistent persona + continuity artifacts; canonical activation pattern established by Epic 26 BMB migration + Slab 2a Texas migration
- **Port-shape** — the specialist-body work pattern of converting a passthrough stub into a live LLM/API-invoking `_act` body using the Slab 2b.1 TEMPLATE scaffold
- **Greenfield** — a specialist created from scratch (no prior `app/specialists/{name}/` directory)
- **Hardening** — adding rubric semantics or contract enforcement to an `_act` body that already exists and runs

---

## Executive Summary

Slab 7a gave the operator eleven specialists who would not let a gate slip past unattended. **Slab 7b gives those eleven specialists their actual hands** — the legacy bodies that retrieve, draft, critique, and revise real course content — so the next four-hour trial is not eleven stubs taking turns being polite, but **eleven craftspeople at a workbench**, with the operator finally collaborating with the roster they were promised. The operator's job-to-be-done: run a course end-to-end and get a Trial-2 deliverable that's actually defensible as content, not just a green pipeline.

Mechanically: Texas retrieves real corpus content (not fixture stubs); Irene authors a real Pass-1 lesson plan; Tracy enriches with real research; Gary calls Gamma's API to produce real slide variants; Kira calls Kling's API to produce real motion clips; Enrique calls ElevenLabs's API to produce real narration audio; Wanda calls Wondercraft's API to produce real podcast beds; Compositor runs its deterministic assembly pipeline against real assets; Quinn-R runs its rubric against the real artifacts produced upstream; Vera runs its fidelity assessment against real content (not scaffold-stubbed gates); Dan threads creative-director aux contributions across G1–G2 per its narrow-lane shape. **Slab 7b targets ~28 row improvements** on the 34-row legacy mapping surface (33 prompt sections + sub-step §05.5; pre-7b state: 0 ✅ / 7 ⚠️ / 27 ❌). Six rows are deferred to future slabs (four conditional-on-CLUSTER_DENSITY paths §05B/§6.2/§6.3/§7.5; plus §14.5 Desmond + §15 Operator Handoff, both gated on Compositor landing).

### Substrate inherited; bodies pending

Slab 7a (CLOSED 2026-04-29 at `95c81b0`) shipped the orchestration substrate. The runner now pauses at all fourteen declared gate codes (not just the four terminal ones); the directive composer converts `--input <corpus-path>` into a real `directive.yaml` for Texas's `dispatch_retrieval` seam; the per-slide subgraph fans out via LangGraph `Send`; the HTML review-pack skeleton renders for G2B/G2F/G3B; conversation persistence chains SHA256 across operator turns; the calibration-tripwire substrate logs fire+quiet events; the Marcus-duality boundary is asserted at `dispatch_adapter.py:81`; the eleven-specialist vocabulary registry enumerates closed enums; the parity-test suite asserts the 33-row mapping-checklist + Composition Spec invariants hold structurally.

But — the bodies were intentionally out of scope for Slab 7a. Slab 7a's parity tests assert the substrate exists and is reachable; they do not assert the bodies inside the substrate produce real content. Trial-475 (2026-04-28) paused-at-G1 cleanly because the substrate worked; Texas returned a fixture stub because Texas's body had not yet been wired to the new directive composer's output. Slab 7a closed the *plumbing* gap; Slab 7b closes the *content* gap.

### What "body activation" means per specialist (operator-ratified per-specialist shape)

The eleven roster slots split into **five shape-classes** (Class D split per Round-2 architectural amendment). Each class has a different K-target, gate-mode designation, and reviewer-burden profile.

**Class A — Hardening (already-active bodies, scope = rubric / contract enforcement only):** Texas (post-directive-composer hardening), Quinn-R (rubric semantics on real upstream content), Vera (G0/G1/G4 rubric semantics on real upstream content). These three already have real `_act` bodies (Texas Slab 2a.4 era; Quinn-R Slab 2a era; Vera Slab 2a era); Slab 7b adds the legacy-prose rubric semantics that were dropped in the migrated path's ⚠️-row partial migrations.

**Class B — Activation refresh (already-shaped bodies, scope = Pass-1 wiring symmetric to Pass-2):** Irene (Pass-1 activation; Pass-2 already done in Slab 2a.2). Slab 2a.2 shipped Irene Pass-2 with a real LLM-invoking `_act` against `gpt-5.4`; Pass-1 mirrors Pass-2's shape but covers a different prompt-surface (lesson plan vs narration script). Existing scaffolding inherits.

**Class C — Port-shape (passthrough → live LLM/API):** Gary, Kira, Wanda, Enrique. Four specialists, each currently a passthrough stub returning a constant. Each gets a port-shape story following the Slab 2b.1 TEMPLATE pattern (deterministic helpers + sanctum-aware reference loading + cache-hit-rate harness target ≥85% post-warm-up). API-bound (gamma/kling/wondercraft/elevenlabs); sandbox-AC discipline applies (forbidden-CLI-set declared; httpx/SDK-based dev-agent ACs; live evidence operator-gated).

**Class C+ — Port-shape with sidecar emission:** Tracy. Genuine hybrid — port-shape AND sidecar greenfield (no prior `_bmad/memory/bmad-agent-tracy/`). The sidecar adds a new emitted-artifact contract, a new chain-test target, and (potentially) a new schema-shape sub-deliverable. K-target is one tier above Class C to surface this hidden inflation explicitly. LLM-only (no third-party API; no sandbox-AC inventory entry needed for Tracy specifically).

**Class D1 — LLM-greenfield (no prior `app/specialists/{name}/` directory; LLM-call-shaped):** Dan (narrow-lane creative-director aux; sidecar-only today). Gets `bmad-create-specialist` workflow run → SKILL.md + sidecar + scaffold-v0.2 + LLM-invoking `_act` body. Chain-test shape: prompt → SG outputs (same shape as Irene/Tracy/Gary).

**Class D2 — Pipeline-greenfield (no prior `app/specialists/{name}/` directory; deterministic-call-shaped):** Compositor (deterministic assembly pipeline; skill-only today). Different scaffold: `bmad-create-specialist` adapted with deterministic-pipeline template. NO LLM call; NO persona accumulation; NO cache-hit-rate harness (replaced by pipeline-determinism harness ≥99% rate). Chain-test shape: fixture-equality assertion (not prompt-output assertion). SG-4 alignment likely option-b documented exception ("deterministic pipeline; no LLM call; no persona-shaped continuity"). Splitting D1 from D2 prevents false symmetry at chain-test-per-PR time.

### The sanctum alignment imperative (SG-4) — because **you don't get two mental models forever**

Slab 7a substrate landed under operators' direct supervision; each substrate story was paid attention to individually. Slab 7b will activate ten specialist bodies in parallel-or-near-parallel waves. If each port-shape story is allowed to ship a SKILL.md inconsistent with the Marcus / Irene / Dan / Texas BMB pattern, the repo will exit Slab 7b with a permanent two-tier mental model: "old specialists" (some kind of activation we don't track) and "new specialists" (sanctum-aligned). The operator's own visceral framing for SG-4 — recorded in project memory `project_slab_7b_skill_md_sanctum_alignment.md` — is exactly that: **"you don't get two mental models forever."** Mental-model bifurcation has a half-life of zero — every future operator and reviewer will be paying attention-tax to remember which agent uses which pattern. The cost compounds across every subsequent slab and every BMAD sprint.

SG-4 is the binding rule: every Slab 7b body-activation story carries an AC requiring SKILL.md alignment OR documented exception. Cora's sidecar (`_bmad/memory/bmad-agent-cora/` + her SKILL.md exception block) is the canonical precedent for the documented-exception path; Marcus / Irene / Dan / Texas are the canonical precedents for the alignment path. **The second mental model retires** — the legacy map gets folded up and put away; the parity-test asserts structural enforcement at every PR; the reviewer is belt-and-suspenders, not co-equal.

### Slab 7b deliverables (eleven-roster activation scope)

Class A — Hardening (3 specialists; rubric / contract enforcement on already-active bodies):
- Texas hardening — live-retrieval-against-real-directive-composer; six-canonical-artifacts contract (extracted.md / metadata.json / extraction-report.yaml / manifest.json / ingestion-evidence.md / result.yaml); ingestion quality gate G0 6-dim evidence-sentence rubric; word-count belt-and-suspenders check; cross-validation hint application.
- Quinn-R hardening — two-mode (pre-composition / post-composition) rubric semantics on real upstream content; G2C storyboard-bound shape; G5 pre-composition QA body (WPM review + VTT monotonicity + coverage completeness + motion-vs-narration duration coherence + advisory-vs-blocking partition).
- Vera hardening — G0 6-dim evidence-sentence rubric on real Texas output; G1 ingestion-quality 6-dim verdicts; G4 19-criterion rubric (G4-01 through G4-19) on real Irene Pass-2 output; sensory-bridges dispatch on real motion + audio.

Class B — Activation refresh (1 specialist):
- Irene Pass-1 — 9-node scaffold mirroring Pass-2 shape; lesson-plan coauthoring + scope-lock contract; per-plan-unit ratification surface for G1A; `irene-pass1.md` artifact write; mode-singularity hard-constraint enforcement.

Class C — Port-shape (5 specialists; passthrough → live LLM/API):
- Tracy port-shape + sidecar creation — research-shaped intent enrichment for Pass-2; sidecar greenfield; 9-node scaffold per Slab 2b.1 TEMPLATE.
- Gary port-shape — Gamma API live; per-slide variant generation; theme-handshake; PNG export normalization; DOUBLE_DISPATCH branch; Vera G3 invocation hooks.
- Kira port-shape — Kling API live; motion generation per `motion_plan.yaml`; per-slide `.progress.json` + terminal `.json` receipts; reviewer inspection pack.
- Wanda port-shape onto scaffold — Wondercraft API live; podcast/audio bed generation scoped into storyboard's audio track.
- Enrique port-shape — ElevenLabs API live; voice-preview + voice-selection HIL contract; manifest-driven narration on locked package.

Class D — Greenfield (2 specialists):
- Dan greenfield via bmad-create-specialist — narrow-lane creative-director aux contributions threaded across G1–G2; SKILL.md + sidecar + scaffold-v0.2 + `_act` body with `option-a-required-at-creation` sanctum alignment.
- Compositor greenfield via kind-deterministic scaffold — `sync-visuals` deterministic assembly pipeline; `DESCRIPT-ASSEMBLY-GUIDE.md` regeneration; localized stills + motion under `assembly-bundle/visuals/` + `motion/`.

Cross-cutting (operator-control envelope guarantees, per-specialist):
- Per-specialist sanctum alignment (SG-4) as per-story AC + structural parity-test enforcement.
- Per-specialist sandbox-AC inventory PR landed before story opens (5-entry inventory: gamma / kling / elevenlabs / wondercraft / dan-api-tbd).
- Per-specialist cache-hit-rate harness configuration (parametric; ≥85% post-warm-up).
- Per-specialist Composition Spec §10 Decision Log entry on every body activation.
- Per-specialist Composition Spec §6 chain-test-per-PR.

### What makes this special

Three differentiators distinguish Slab 7b from Slab 7a and from prior migration slabs:

1. **Substrate-as-floor, not substrate-as-ceiling — frozen by path, not by principle.** Slab 7a built a generic orchestration scaffold that any specialist body could be plugged into. Slab 7b is the proving ground: eleven concrete bodies, each with its own legacy contract, plug into the same substrate without the substrate needing per-specialist exceptions. The frozen substrate paths are enumerated in §IR-1 (Inheritance Risks) as a closed list — `_bmad/memory/shared/`, `dispatch_adapter.py:81` (Marcus duality boundary), conversation-persistence layer, per-slide subgraph skeleton, vocabulary registry, gate-runner substrate, SG-1..SG-4 contract files. Any Slab 7b PR whose diff touches a substrate path is automatically a 7a-defect candidate; the dev agent opens a `7a.defect-N` story, ratifies the substrate change via the appropriate governance tier, then resumes 7b body work on top of the new substrate floor. **"Substrate extension" is not a recognized category — every substrate edit is an amendment governed accordingly.**

2. **The second mental model retires.** Marcus, Irene, Dan, and Texas already exit-conditioned the BMB sanctum migration (Epic 26 + Slab 2a.4). Slab 7b's job is to bring the remaining eight bodies under the same activation pattern — not as a separate cleanup epic later, but inline with every body activation, so the repo never exists in a half-aligned state. Cora's sidecar is the reminder that exceptions are allowed; SG-4 is the rule that exceptions must be explicit, drawn from a closed allowlist, and party-mode-ratified. **You don't get two mental models forever.**

3. **Per-specialist body-completeness as the unit of close.** Slab 7a closed its substrate as a single bundled unit; Slab 7b closes per-body, with per-PR chain-tests asserting each specialist body's substrate→runtime end-to-end chain. That's a different release cadence (eleven story closures, not one bundled close) and a different review shape (per-specialist Class A/B/C/C+/D1/D2 reviewer-burden bucket, not a single substrate review pattern). The cadence is deliberate: bodies are independent, so closing them independently is honest. Trial-2 readiness is the conjunction predicate (substrate works × every body produces real content), but Slab 7b's deliverable is not the trial — the deliverable is the eleven-body-completeness assertion that makes the trial launchable.

For seven slabs the substrate has been a floor — something you stood on while the real work happened elsewhere. **Slab 7b is the slab where the floor stands up and walks. The substrate is no longer a substrate — it's a runtime.**

### Scope-Binding Commitments (architectural non-negotiables)

These **eight** commitments BIND scope (six inherited from Slab 7a; one new for Slab 7b sanctum alignment; one new disambiguating Codex deployment posture per Round-2 Mary-amendment). Slab 7b stories that violate them must re-open party-mode consensus, not be relitigated at story-authoring time.

(Note: Composition Spec §6 chain-test-per-PR is INHERITED via SG-3, not net-new — it is restated below as an explicit reminder under commitment #6, not promoted to a separate commitment, per Round-2 John-amendment.)

1. **(Inherited)** Subgraph-with-`interrupt()` fan-out for per-slide-array gates — every Class-C port-shape story producing per-slide content (Gary G2B, Kira G2F) MUST consume the Slab 7a per-slide subgraph skeleton; no parent-graph repeated-`interrupt()` shortcut.
2. **(Inherited)** Max-3 oscillation guard as state-machine invariant — every body-activation story producing operator-revisable output MUST inherit the Slab 7a `revise_count` substrate; no per-gate hand-rolled counter.
3. **(Inherited)** Pre-composition QA validator as substrate step — Quinn-R hardening MUST land its pre-composition QA in the gate-runner subgraph, not as a sibling script.
4. **(Inherited)** Decision-card vocabulary registry honored — every specialist-emitted decision-card MUST validate against `app/models/decision_cards/vocabulary.py`; Slab 7b activations that emit new vocabulary MUST extend the registry in lockstep (Composition Spec §10 Decision Log entry required).
5. **(Inherited)** C1 calibration-tripwire honored — every Class-C/C+ port-shape body MUST log fire+quiet events to the Slab 7a `gate_runner.py` JSONL substrate.
6. **(Inherited)** Parity-test suite honored — every Slab 7b activation MUST produce a parity test asserting the legacy operator-control lever is preserved on the migrated path; suite failure blocks merge. **(Inherited reminder, not net-new)**: per-PR chain-tests are required by Composition Spec §6 (SG-3); each body-activation PR carries one.
7. **(NEW)** BMB sanctum alignment per body — every body-activation story MUST land SKILL.md aligned (option-a) OR exception-documented (option-b drawn from closed allowlist + party-mode consensus); reviewer verifies; structural parity-test (NFR-I9) asserts at every PR merge gate.
8. **(NEW — Round-2-disambiguation, BINDING)** Codex parallel-authoring deployment continues from Slab 7a for Class-C/C+ port-shape stories (Tracy/Gary/Kira/Wanda/Enrique = 5 stories) + sandbox-AC inventory PR (Wave 0); `bmad-code-review` by Codex on every Slab 7b story close; Class-A hardening + Class-B refresh + Class-D1/D2 greenfield + Wave-6 integration story remain Claude-authored. Removing or substantially altering Codex deployment requires party-mode consensus.

### Trial-2 readiness — the joint predicate

Slab 7a + Slab 7b are the necessary preconditions for a trial-2 attempt that targets G3 cleanly with real content from eleven real specialists. Trial-2 itself is the verification gate, not a Slab 7b deliverable. Codex parallel-authoring deployment is now scope-binding commitment #8 (above) — Class-C/C+ port-shapes + sandbox-AC inventory PR + per-story bmad-code-review.

**Operator-side concerns at five-API scale (Round-2 Winston-amendment, light-touch):** trial-2 launch checklist tracks (a) per-API credential-rotation register surfaced in `next-session-start-here.md`, (b) per-API rate-limit budget annotation in `docs/dev-guide/migration-ac-sandbox-inventory.json`, and (c) fixture-refresh dry-run mode estimating cost before live spend. These are operator-gated AC items, not dev-agent burden — but the five-API surface (gamma/kling/elevenlabs/wondercraft/dan-api-tbd) makes them load-bearing for Slab 7b close hygiene.

When trial-2 closes cleanly: the operator participates in roughly ten essential conversational gates with real content at each gate; every legacy operator-control lever has a green parity test; the v4.2 1527-line pack has earned the right to become a ~400-line distillation under Doc-Slab 7-D; the substrate is no longer a substrate — it's a runtime.

## Project Classification

- **Project Type:** Internal multi-agent runtime extension — eleven-specialist body-activation layer atop the Slab 7a orchestration substrate, consumed by a single operator plus the named eleven-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) coordinated by Marcus orchestrator. Codex remains operator-blessed as a parallel dev-agent for Class-C port-shape stories and as a `bmad-code-review` voice on story closes.
- **Domain:** Online course content production / collaborative AI infrastructure. Domain-specific concerns inherit Slab 7a's frame: HIL tamper-evidence (FR34 carry-forward); audit-replay reproducibility (Composition Specification §3.1); operator-control envelope preservation against legacy v4.2 floor; per-trial cost discipline now covering five live API surfaces (gamma/kling/elevenlabs/wondercraft + Dan-API-TBD).
- **Complexity:** **High.** Loaded substrate concerns inherit from Slab 7a + add: live API binding for five specialists with sandbox-AC inventory governance; per-API rate-limit + cost-budget management; cache-hit-rate harness parametrization across ten specialist configs + one Compositor pipeline-determinism harness; Pydantic-v2 schema discipline across eleven new contribution shapes; eight-axis per-specialist body-shape vs substrate-shape contract; SG-4 sanctum alignment as per-story enforcement.
- **Project Context:** **Brownfield.** Migration unconditionally SHIPPED at `97842ac` (2026-04-27); Slab 7a substrate CLOSED at `95c81b0` (2026-04-29; 696 passed/19 skipped baseline holds); first tracked trial 475df528 paused-at-G1 cleanly; Slab 7a NEW CYCLE proven 6× end-to-end; Slab 7b inherits validated workflow.

---

## Meta-Directive — Remaining PRD Steps (party-mode ratification of pre-filled draft)

**Per operator instruction (2026-04-29):** this PRD is pre-filled end-to-end before any party-mode round opens. Each remaining-step opens with a 3–4 voice `bmad-party-mode` round to **review** pre-filled content (ratify, refine, or amend), not author from scratch. Assistant synthesizes consensus or supermajority position; consensus content replaces (or stands as) the pre-filled draft for that section.

**Hard scope-floor guardrails — auto-reject any consensus position that violates SG-1 / SG-2 / SG-3 / SG-4.**

---

## Success Criteria

**Acceptance-clause ordering note (Quinn-amendment R3):** A-13 (trial-2 closes through G3 with real content) is load-bearing on the entire prior A-8..A-12 chain. Partial-green on A-8..A-12 invalidates A-13 regardless of fixture-course outcome — partial states cannot be papered over by running A-13 against a non-load-bearing subset fixture. A-13 fixture course MUST exercise all eleven specialists' activated bodies in load-bearing fashion.

### User Success

The user is the operator running multi-hour course-production trials with real content from the eleven-specialist roster against the frozen ten-gate inventory established by Slab 7a. User success is observable on the trial transcript, the LangSmith run tree, and the produced media artifacts — not asserted by the operator.

| ID | Outcome | How measured | Threshold |
|----|---------|--------------|-----------|
| US-1 | Operator reaches G3 (Sequencing approved) on real content with non-stub artifacts from each specialist | LangSmith run tree shows ordered `interrupt(...)` events at every gate (inherited from 7a) AND produced artifacts at each gate pass per-specialist non-stub thresholds | 100% gate transitions in trial-2 carry an operator decision-card (7a) AND **per-specialist non-stub thresholds met**: (a) for the 10 LLM-driven specialists — output length varies ≥20% across N=3 different lesson-slug inputs; no field byte-equal to any input field; ≥1 prose field >200 chars OR ≥1 structured field with ≥3 distinct elements; (b) for Compositor (deterministic, 1/11) — pipeline-determinism rate ≥99% across the trial-2 invocation set; packaged artifact passes manifest-validation + structural integrity. Stubness-vocabulary does not apply to Compositor; pipeline-correctness substitutes. |
| US-2 | Operator participates in ~10 essential conversational gates against real content; legacy 33-row coverage maintained as ✅ on the migrated path | Gate-presence audit + content-realness audit against `slab-7-legacy-migrated-mapping-checklist.md` 33-row inventory; each row maps to a present `interrupt()` site (7a) AND a body that produces real artifacts at that station (7b) | All 33 legacy rows accounted for in trial-2 with realness-detection PASS; ❌ rows resolved to ✅; ⚠️ rows resolved to ✅ |
| US-3 | Revise loops on real content cannot grind — max-3 oscillation guard fires deterministically as state-machine invariant against real-content revisions | Inherited from 7a US-3; Slab 7b adds: `tests/parity/test_oscillation_guard_invariant_real_content.py` asserts guard fires on Gary/Kira/Enrique-revisable real outputs | Zero trial transcripts show `oscillation_count > 3` against real-content revisions; guard-trip emits operator decision-card "escalate or accept-as-is" |
| US-4 | No hour-4 rubber-stamping against real content — operator engagement observably distributed across trial with real artifacts | Engagement-signal rate carries forward from 7a SM-4; Slab 7b adds: per-specialist engagement breakdown in `_artifacts/trial-2/engagement_decay_by_specialist.md` | Last-quartile engagement-rate ratio ≥ 0.30 of first-quartile; per-specialist breakdown shows no specialist consumes >40% of operator attention disproportionately |
| US-5 | Decision-card vocabulary against real-content decisions is closed and predictable — no per-gate-against-real-content dialect drift | Inherited from 7a US-5; Slab 7b adds: `tests/parity/test_no_ad_hoc_vocabulary_in_real_content_paths.py` AST-scans all eleven `_act` body modules | 100% of trial-2 decision-cards validate against the registry; zero free-text directive fallbacks across all eleven specialists |
| US-6 | Per-slide arrays against real Gary variants + real Kira motion don't collapse to rubber-stamp | Inherited from 7a US-6; Slab 7b adds: HTML review-pack opens against real Gamma PNGs (not skeletal placeholders) AND real Kling MP4 thumbnails | All three sub-checks green on real-content paths |
| US-7 (NEW) | Every specialist body activation honors SG-4 sanctum alignment | `tests/parity/test_skill_md_sanctum_alignment.py` asserts every name in `app/specialists/{name}/` has either BMB-pattern frontmatter OR explicit `# Sanctum exception` block with rationale | 11/11 specialists pass; zero silent omissions |

### Business Success

| ID | Outcome | How measured | Threshold |
|----|---------|--------------|-----------|
| BS-1 | Eleven-roster activation claim holds — all 11 specialists ship with body activations meeting their per-shape contract | Specialist-by-specialist closeout audit; party-mode green-light review against per-specialist Slab-7b shape designation (frontmatter `slab7bSpecialistRoster.specialists.{name}.slab7bShape`) | 11/11 specialists `done`; per-shape contract met (Class A: rubric-semantics-on-real; Class B: Pass-1 mirroring Pass-2; Class C: live API + cache-hit-rate ≥85%; Class D: greenfield bodies + scaffold) |
| BS-2 | Trial-2 launch unblocked end-to-end (substrate from 7a + bodies from 7b) | Combined readiness predicate: A-1..A-7 from Slab 7a + A-8..A-14 from Slab 7b; pre-trial-2 dry-run on non-load-bearing fixture course | Slab 7b closeout + ≤1 week dry-run window; zero blocking defects |
| BS-3 | Trial-2 cost stays within bounded-MVP envelope (~5–8× trial-475 baseline) — now including five live API surfaces | LangSmith cost dashboard for trial-2; reconciled against `_bmad-output/cost-ledger.md`; per-API breakdown (gamma / kling / elevenlabs / wondercraft / Dan-API-TBD) | Trial-2 total LLM+API spend ≤ $3.00 inclusive of Marcus orchestration overhead; per-gate specialist-attributable spend ≤ $0.30 (Mary-amendment R3: $3.00 is not a fungible 10×$0.30 pool — orchestration cost between gates accrues separately. If Marcus-cost telemetry granularity supports it post-Slab-7a, refine to: per-gate specialist ≤ $0.25 + Marcus orchestration overhead ≤ $0.50; both sub-caps must hold). |
| BS-4 | No CI runaway from five new live-API surfaces | `.github/workflows/canary.yml` schedule audit; monthly CI cost ledger | T4 ≤ 3 end-to-end runs/night × 30 nights = 90 runs/month; monthly live-API CI spend ≤ $50 (operator-set ceiling) |
| BS-5 | SG-4 sanctum alignment achieved across all eleven specialists; mental-model bifurcation closed | `app/specialists/` tree + `_bmad/memory/` tree audit; `tests/parity/test_skill_md_sanctum_alignment.py` green; verification rubric per `docs/dev-guide/bmb-sanctum-alignment-checklist.md` | 11/11 SKILL.md files either align with the BMB sanctum pattern per `docs/dev-guide/bmb-sanctum-alignment-checklist.md` (option-a) OR carry an exception-documentation block citing named precedent (Cora-sidecar) + closed-allowlist category + party-mode-recorded rationale (option-b). Checklist's pass/fail rubric is the verification instrument. |
| BS-6 | Doc-Slab 7-D unblocks (post-trial-2 prose harvest can begin) | Trial-2 evidence captured + parity tests green + sandbox-AC inventory closed + Slab 7b retrospective filed | Slab 7b retrospective at `_bmad-output/implementation-artifacts/slab-7b-retrospective.md` filed; Doc-Slab 7-D PRD authoring unblocks |

### Technical Success

Tier discipline inherits from Slab 7a; budgets re-tuned for body-activation work. **R3 Murat-amendment:** T-tier definitions split to disambiguate dev-cycle wall-clock budgets (minutes) from cache-determinism harness budgets (hours).

**T1 — Specialist-body unit tests** (per-specialist; mocked substrate)
- Count: 35–55 per Class-C/C+/D specialist; 15–25 per Class-A/B specialist. Wall-clock budget <60s per specialist (stop-the-line). Aggregate Slab 7b T1 budget: <10 minutes if run sequentially; parallelizable.
- Coverage per specialist: `_act` body shape; deterministic helpers; reference loading; envelope serialization; response parsing; error paths.

**T2 — Fixture-replay** (per-specialist; SINGLE cached invocation; dev-cycle inner loop)
- Count: 8–15 per Class-C/C+ specialist; 4–8 per Class-A/B specialist; 4–6 for Compositor (pipeline-determinism shape, see T4). Wall-clock budget <2min per specialist replay (stop-the-line).
- Coverage: replay one cached request through deterministic-helper stack; assert pinned fixture matches; pack-hash determinism; cross-gate handoff invariants.
- **NB:** T2 is single-invocation replay, not the multi-run cache-hit-rate harness. The harness runs at T4.

**T3 — Specialist-body smoke against live substrate** (subset; cost-managed)
- Count: 1–3 per Class-C/C+ specialist (smoke); 1–2 per Class-A/B specialist; 1 for Compositor. Wall-clock <3min/integration. Flakiness >2% = quarantine + follow-on.
- **FM-21 decision tree** (Murat-amendment): when T3 canary diverges from T2 fixture: (1) re-run T3 N=3 to confirm not flake; (2) if persistent, capture T3 response and diff against T2 fixture; (3) if divergence is in deterministic-helper output → **investigation** (helper bug or fixture drift); (4) if divergence is in LLM-response shape → **fixture re-record with party-mode notification** (model-version drift suspected); (5) document verdict in story Completion Notes. Default action is investigation-first; re-record only with explicit cause.

**T4 — Cache-determinism harness** (per-LLM-specialist; N=10 median[2:]; green-light cadence; OUT of dev-cycle wall-clock)
- Count: 1 harness per LLM specialist (10 specialists; Compositor uses pipeline-determinism harness instead — see T5).
- Cadence: green-light-only; nightly or pre-close. Wall-clock per harness ≈230s × 10 = ~38min per specialist; not in dev-cycle inner loop.
- Threshold: median(wall_clock_seconds[2:]) hit-rate ≥85% (discarding runs 0–1 as cold-cache warmup, per Slab 2a.2 precedent).

**T5 — End-to-end live canaries** (Class C/C+/D1 only; live-API; gated, audited)
- Count: ≤3 end-to-end canaries per Class-C/C+/D1 specialist (hard cap; live-API). Cost ceiling ~$0.40 per canary; aggregate Slab-7b dev-cycle T5 ceiling: ~$3.00 ($0.40 × 3 canaries × ~5 specialists / 2-pass averaging). Compositor (D2) does NOT have T5 canaries — pipeline-determinism is verified at T4-equivalent without live API.
- Cadence: record-once-replay-forever; quarterly re-record gated.

**K-floor / target-range discipline (Slab 7b per-shape budgets — R3 Murat + Amelia amendments)**
- Class A (hardening): single-gate, K-floor 1.2–1.4×, ~2K LOC + ~25 tests per specialist. Aggregate: ~6K LOC + ~75 tests across 3 specialists.
- Class B (Irene Pass-1 refresh): single-gate, K-floor 1.3–1.5×, ~2.5K LOC + ~30 tests. (Slab 2a.2 Pass-2 baseline.)
- Class C (port-shape, API-bound): single-gate per Slab 2b.1 TEMPLATE precedent, K-floor 1.3–1.5×, **~2.9K LOC + ~33 tests per specialist** (R3 Amelia: API-client mocking + fixture-record harness adds ~400 LOC + ~5 tests on top of LLM body shape). Aggregate: ~11.6K LOC + ~132 tests across 4 specialists (Gary/Kira/Wanda/Enrique).
- Class C+ (Tracy port-shape with sidecar emission): single-gate, K-floor 1.3–1.5×, **~3.3K LOC + ~36 tests** (R3 Amelia: 4-file BMB sidecar at ~600 LOC structured prose + emission harness ~200 LOC + emission tests ~6, distinct row from Class C). Aggregate: ~3.3K + ~36 tests.
- Class D1 (Dan LLM-greenfield): single-gate, K-floor 1.4–1.6× (greenfield uplift), ~3.5K LOC + ~40 tests.
- Class D2 (Compositor pipeline-greenfield): single-gate, K-floor 1.4–1.6×, ~3.5K LOC + ~40 tests; pipeline-determinism harness (no cache-hit-rate; see Compositor determinism shape in Measurable Outcomes).
- **Aggregate Slab 7b: ~28–36K LOC + ~325–375 tests; ~24–30 K-units at K-floor 1.3–1.5×** (R3 Murat blocking-amendment: previous "~28K + ~21–24 K-units" was at K-floor 1.0–1.2× and under-budgeted by ~25–35%; restated to align stated K-floor with sized aggregate).
- Over-spend tripwire: any single story exceeding 1.7× K closes the dev round, escalates to party-mode.

**Compositor pipeline-determinism shape** (R3 Amelia-amendment): "determinism" is partial because `DESCRIPT-ASSEMBLY-GUIDE.md` regeneration embeds timestamps. Contract: bytes-identical for `sync-visuals` (file-copy); field-masked-hash for `assembly-guide` (hash-after-redaction of `{generated_at, run_id, build_timestamp}`). Test harness: `tests/compositor/test_pipeline_determinism.py::test_sync_visuals_bytes_identical` + `::test_assembly_guide_masked_hash_stable`.

**Sandbox-AC inventory precondition (carry-forward from Slab 7a Step 3 — R3 Amelia-scope-amendment)**
gamma, kling, elevenlabs, wondercraft, dan-api-tbd — inventory PR is hard precondition for opening any **API-bound** Class-C / Class-C+ / Class-D Slab 7b story. Tracy (Class C+, LLM-only, no third-party API) is **exempt** — no inventory entry required. Dan (Class D1) requires `dan-api-tbd` resolution at story-1 (LLM-only OR third-party API determined there); if LLM-only, Dan is also exempt; if third-party, the entry is finalized then. Slab 7b's job is to land the inventory PR before any API-bound Class-C/C+/D story opens.

**Replay-fixture strategy invariants (carry-forward from Slab 7a)**
Record-once-replay-forever; fixtures committed under version control with content-addressable hash. Quarterly re-record cadence. Cache-hit-rate harness parametric (single binary, config-driven).

### Measurable Outcomes

| Metric | Target | Tripwire |
|---|---|---|
| Specialist activation count | 11 (Class A: 3 + Class B: 1 + Class C: 5 + Class D: 2) | <11 = SG-1 violation, halt |
| Mapping-checklist rows resolved | ~28 row-status improvements (21 ❌→✅ + 7 ⚠️→✅, of 34 total = 33 prompt sections + sub-step §05.5); 6 rows deferred (4 conditional cluster paths §05B/§6.2/§6.3/§7.5 + §14.5 Desmond + §15 Operator Handoff) | <28 resolved = SG-2 violation; deferred-row regression (already-✅ → ⚠️/❌) also halts |
| Composition Spec invariant chain-tests | 11 chain-test PRs (one per specialist body activation; SG-3 §6) | <11 = halt |
| SKILL.md sanctum alignment | 11 (option-a) + ≤2 (option-b documented exception, if any) | silent omission = HALT-AND-REMEDIATE; SG-4 violation |
| Slab 7b code surface | ~28–36K LOC at K-floor 1.3–1.5× | per-story >1.7× K halts |
| Slab 7b test surface | ~325–375 tests across T1–T5 tiers | — |
| Slab 7b dev cost (T2/T5 dev runs) | ~$3.00 total | over-budget = halt |
| Slab 7b effort | ~24–30 K-units at K-floor 1.3–1.5× (parallel-wave plan) | — |
| Trial-2 launch window | ≤6 weeks from Slab 7b closeout, contingent on operator-side credential-rotation + sandbox-AC checklist completing within 2 weeks of closeout | — |
| Trial-2 cost ceiling | ≤$3.00 total | BS-3 |
| Cache-hit-rate (warm, median[2:], N=10) | ≥85% across **10 LLM specialists** (Class A + B + C + C+ + D1, ex-Compositor); cadence: T4-harness, green-light-only | <80% per-specialist = fixture-staleness investigation |
| Pipeline-determinism rate (Compositor) | ≥99% across N=10 runs; bytes-identical for `sync-visuals`; field-masked-hash for `assembly-guide` (modulo declared-nondeterministic fields `{generated_at, run_id, build_timestamp}`) | <99% = Class-D2 scaffold review |
| Sanctum cross-specialist parity rubric score (R3 Quinn-amendment; SG-4 operationalization) | green across all 11 specialists per `docs/dev-guide/bmb-sanctum-alignment-checklist.md`; cold-session activation smoke green per FM-25 mitigation | any red = SG-4 violation, halt |
| Scaffold-adoption rate (R3 Quinn-amendment; SG-4 operationalization) | 100% on Class-A, Class-B, Class-C, Class-C+ activations (scaffold-by-default per R1 SG-4 upstream-enforcement) | <100% = scaffold bypass = governance failure |
| Live-API-on-CI for API-bound specialists | 0 occurrences | any occurrence = governance failure |
| Calibration-tripwire exercised by real-content during trial-2 | ≥1 fire + ≥1 quiet during trial-2 | 0 fires across all 11 = "shipped but never exercised" failure |
| Parity-test suite green for trial-2 readiness (substrate + bodies) | 100% pass | any red = trial-2 not ready |
| Composition Smoke evidence per slab-opener | 1 per slab-opener (Composition Spec §9) | missing = slab-opener not complete |
| Sandbox-AC inventory entries landed | up to 5 (gamma, kling, elevenlabs, wondercraft, dan-api-tbd-if-API); finalized count depends on Dan-API-TBD resolution at Story 7b.X4 | inventory-not-landed = API-bound Class-C/C+/D story open blocked |

### Slab 7b Acceptance (concrete clauses, artifact-backed)

| Clause | Artifact | Check |
|---|---|---|
| A-8 | All 8 scope-binding commitments landed | Executive Summary §Scope-Binding Commitments | each commitment has a story-ID reference + matching story marked done in `sprint-status.yaml` |
| A-9 | 11 specialist body activations meeting per-shape contract — per-specialist file-path assertion (R3 Amelia-amendment) | per-specialist Slab-7b shape + file-path assertion table (below) + closeout audit | 11/11 specialists `done` AND per-specialist file-path assertion green per the table below |
| A-10 (R3 Mary-amendment) | ≤28 inheritance rows transition ❌→✅ or ⚠️→✅ on rows owned by the eleven activated specialists; the 6 explicitly deferred rows (4 conditional cluster paths §05B/§6.2/§6.3/§7.5 + §14.5/§15) remain ❌/⚠️ as-tracked and are out of scope for this slab | `slab-7-legacy-migrated-mapping-checklist.md` re-audit at Slab 7b close | ≤28 rows resolved; zero remaining ❌ or ⚠️ on rows owned by *activated* specialists; deferred-row regressions (already-✅ → ⚠️/❌) also halt |
| A-11 | SG-4 sanctum alignment achieved across all eleven | `tests/parity/test_skill_md_sanctum_alignment.py` green; cold-session activation smoke green per FM-25 mitigation | 11/11 pass on both parity-test AND cold-activation-smoke |
| A-12 (R3 Murat-amendment, explicit) | T4 cache-hit-rate harness measures `median(wall_clock_seconds[2:])` across N=10 runs (discarding runs 0–1 as cold-cache warmup, per Slab 2a.2 precedent); threshold ≥85% hit-rate against pinned fixture set; cadence green-light only, NOT in T1/T2 dev-cycle | `_artifacts/cache_hit_rate_report.md` + `_artifacts/compositor_pipeline_determinism_report.md` | per-LLM-specialist median[2:] ≥85% across 10 specialists (excl. Compositor); Compositor pipeline-determinism rate ≥99% |
| A-13 (R3 Quinn-amendment, tightened) | Trial-2 closes through G3 cleanly with real content; **trial-2 fixture course MUST exercise all eleven specialists' activated bodies in load-bearing fashion; subset-fixture trials do NOT satisfy A-13** | `_artifacts/trial-2/run_summary.yaml` + `_artifacts/trial-2/specialist_invocation_audit.yaml` | `terminal_gate: G3` AND `silent_bypass_events: 0` AND `specialist_roster_count: 11` AND `all_eleven_specialists_invoked_load_bearing: true` AND per-specialist non-stub thresholds met (US-1 thresholds) |
| A-14 (R3 Mary-flag) | Slab 7b retrospective filed; deferred-inventory consultation done | `_bmad-output/implementation-artifacts/slab-7b-retrospective.md` | retrospective two-part format (Lookback + Next Slab Preparation) per `bmad-retrospective` skill — **verification flag: confirm skill emits two-part structure; if differently-shaped, A-14 amends to match skill's actual structure rather than forcing skill-edits at retrospective time**; deferred-inventory consultation logged per CLAUDE.md binding consultation point #1 |

### A-9 per-specialist file-path assertion table (R3 Amelia-amendment)

| Specialist | Class | File-path assertion | FR ref |
|---|---|---|---|
| Texas | A | `app/specialists/texas/_act.py` invokes `dispatch_retrieval(directive_path, bundle_dir)` against real composed directive | FR89 |
| Quinn-R | A | `app/specialists/quinn_r/_act.py` emits two-mode rubric-scored decision (pre/post-composition) on real upstream content | FR90 |
| Vera | A | `app/specialists/vera/_act.py` emits G0/G1/G3/G4 rubric verdicts with evidence sentences on real upstream content | FR91 |
| Irene-Pass1 | B | `app/specialists/irene/_pass1_act.py` (or equivalent) mirrors Pass-2 9-node shape; produces lesson-plan + scope-lock contract; emits `scope_decision.set` + `plan.locked` events | FR92 |
| Tracy | C+ | `app/specialists/tracy/_act.py` produces research-shaped intent enrichment for Pass-2; emits sidecar at `_bmad/memory/bmad-agent-tracy/{INDEX,PERSONA,chronology,access-boundaries}.md` | FR93 |
| Gary | C | `app/specialists/gary/_act.py` calls `app/specialists/gary/_clients/gamma_client.py` for per-slide variant generation; PNG export normalization; DOUBLE_DISPATCH branch; Vera G3 invocation hooks | FR94 |
| Kira | C | `app/specialists/kira/_act.py` calls `app/specialists/kira/_clients/kling_client.py` for motion generation per `motion_plan.yaml`; per-slide `.progress.json` receipts | FR95 |
| Wanda | C | `app/specialists/wanda/_act.py` calls `app/specialists/wanda/_clients/wondercraft_client.py` for podcast/audio bed; scaffold-v0.2 alignment | FR96 |
| Enrique | C | `app/specialists/enrique/_act.py` calls `app/specialists/enrique/_clients/elevenlabs_client.py`; voice-preview HIL contract; manifest-driven narration | FR97 |
| Dan | D1 | `app/specialists/dan/_act.py` (greenfield) + sidecar `_bmad/memory/bmad-agent-dan/`; narrow-lane creative-director aux contributions across G1–G2; sandbox-AC `dan-api-tbd` resolved at story-1 | FR98 |
| Compositor | D2 | `app/specialists/compositor/_act.py` (or `app/pipeline/compositor/{sync_visuals,assembly_guide}.py`) — deterministic; SG-4 option-b documented exception likely; pipeline-determinism harness ≥99% | FR99 |

### Slab-7b-Shaped Failure Modes (checkable at green-light, not discovered in trial)

Each has a concrete check the green-light party-mode round can run in five minutes or less. If any returns "this matches," green-light blocks. Slab 7b inherits 7a's FM-1..FM-10 (substrate-shaped) and adds 7b-shaped FM-11..FM-22 (body-shaped + sanctum-alignment-shaped).

| FM | Description | Check |
|---|---|---|
| FM-11 (R3 Murat-amendment, heuristic explicit) | Specialist body activated but returns stub-shaped output (real-API call missing) | A specialist's trial-2 output is **real-content** iff (a) output length varies ≥20% across N=3 different lesson-slug inputs, AND (b) no field is byte-equal to any input field, AND (c) ≥1 prose field >200 chars OR ≥1 structured field with ≥3 distinct elements. Failing any of (a)/(b)/(c) flags **stub-shaped** and requires investigation before green-light. |
| FM-12 | Class-C port-shape ships without sanctum alignment + without documented exception | `tests/parity/test_skill_md_sanctum_alignment.py` red on any of Tracy/Gary/Kira/Wanda/Enrique |
| FM-13 (R3 Amelia-amendment, parity-test contract restated) | Class-D greenfield ships without sanctum alignment AND option-b documented-exception rationale fails the SG-4 parity-test contract | parity-test contract: either (a) sanctum present at `_bmad/memory/bmad-agent-<name>/INDEX.md` with BMB-pattern frontmatter on SKILL.md, OR (b) `# Sanctum exception: <category>` block in SKILL.md citing closed allowlist + `## Rationale` ≥80 chars referencing "sanctum activation" or "BMB pattern" + party-mode-recorded ratification. Compositor takes (b); Dan must take (a) unless party-mode escalates. Red on Dan or Compositor without satisfying contract = FAIL. |
| FM-14 | Cache-hit-rate harness misconfigured for any LLM specialist | `_artifacts/cache_hit_rate_report.md` shows median[2:] <80% on any of 10 LLM specialists = FAIL; Compositor uses pipeline-determinism harness instead |
| FM-15 | Sandbox-AC inventory PR not landed before API-bound Class-C/C+/D story open | inventory PR git-history + sprint-status.yaml story-open dates audit; story open before inventory landed = governance failure |
| FM-16 | Live-API call leaked into CI for any API-bound specialist | `.github/workflows/` audit; live-API call without `pytest.mark.llm_live` + `@operator-gated` decorator = governance failure |
| FM-17 | Composition Spec §6 chain-test PR missing for any body activation | per-specialist closeout audit; missing chain-test = blocks story close |
| FM-18 | Composition Spec §10 Decision Log entry missing for any body activation that emits new vocabulary | `docs/dev-guide/composition-specification.md` §10 audit at Slab 7b close; missing entry = SG-3 violation |
| FM-19 | Mapping-checklist row regresses (✅ → ⚠️ or ⚠️ → ❌) during Slab 7b dev | re-run mapping checklist at every story close; regression = halt |
| FM-20 | Per-specialist body emits a vocabulary token absent from the registry | AST scan against `app/models/decision_cards/vocabulary.py` (Slab 7a artifact); ad-hoc token = halt |
| FM-21 (R3 Murat-amendment, decision tree explicit) | Trial-2 readiness audit reveals body works in T2 fixture but fails T3 live integration | When T3 canary diverges from T2 fixture: (1) re-run T3 N=3 to confirm not flake; (2) if persistent, capture T3 response and diff against T2 fixture; (3) if divergence is in deterministic-helper output → **investigation**; (4) if divergence is in LLM-response shape → **fixture re-record + party-mode notification**; (5) document verdict in story Completion Notes. Default investigation-first. |
| FM-22 | Slab 7b parity-test suite + Slab 7a parity-test suite combined fails to assert end-to-end real-content path | `pytest tests/parity/ -k "slab_7b_real_content_e2e"` red = halt |
| FM-23 (R3 Quinn-amendment, NEW) | Inter-specialist contract drift — Specialist X's hardened output shape diverges from Specialist Y's hardened input expectations; both unit tests pass; chain test fails | Chain-tests are mandatory for every Class-A/B/C/C+/D activation pair that consume each other's outputs (e.g., Texas → Vera G0; Irene Pass-1 → Vera G1; Gary → Quinn-R G2C; Irene Pass-2 → Vera G4); chain-test failure blocks wave close |
| FM-24 (R3 Quinn-amendment, NEW) | Inline substrate patching during body activation — a wave's chain-test reveals a Slab 7a substrate defect; dev agent patches inline rather than opening 7a-defect | Substrate-as-floor invariant violated. Remediation: any 7a-substrate bug discovered mid-7b MUST open a 7a-defect story and PAUSE the affected wave; inline patching is a governance failure. PR-review path-based check (per Exec Summary differentiator #1): Slab 7b PR diff touches a frozen substrate path = automatic 7a-defect candidate; merge blocked until routed. |
| FM-25 (R3 Quinn-amendment, NEW) | Sanctum parity-test green, cold-activation red — frontmatter is shape-correct per parity-test, but cold-session activation actually fails at `bmad-agent-{name}` skill load | Parity rubric MUST include a cold-activation smoke test for each migrated specialist as a parity sub-check (per A-11 amendment). Test: simulate operator typing `talk to {name}` in fresh session; assert SKILL.md loads + sanctum batch loads + persona activates without error. Red = HALT-AND-REMEDIATE. |
| FM-26 (R3 Quinn-amendment, NEW) | Credential drift between Slab-7b close and trial-2 launch — provider/model/sanctum/retrieval credentials rotate; trial-2 fails on environmental drift, misattributed to slab regression | Pre-trial-2 credentialed-path smoke test as A-clause OR a credentials-frozen-at-close operator commitment. Operator-side trial-launch checklist (Exec Summary §Trial-2 readiness Winston-amendment) tracks per-API credential-rotation register; any rotation between close and launch triggers re-smoke before trial-2 launches. |

(FM-1..FM-10 inherited from Slab 7a verbatim; not re-stated.)

## Product Scope

### MVP — Minimum Viable Product

Slab 7b body-activation completeness, operator-ratified post pre-fill review. All 11 specialists ship body activations together. **MVP threshold:** trial-2 reaches G3 cleanly with real content from all eleven specialists. Anything that doesn't move that threshold is out of MVP.

The 11 activations organize into four classes:

**Class A — Hardening (3 specialists; rubric / contract enforcement on already-active bodies)**
1. Texas hardening — closes 33-row mapping rows §02 / §02A / §03 / §04 (currently ❌/❌/❌/⚠️) toward ✅; six-canonical-artifacts contract; G0 6-dim evidence rubric.
2. Quinn-R hardening — closes rows §07B / §07C / §07F / §13 (currently ❌/⚠️/❌/❌) toward ✅; two-mode rubric; storyboard-bound G2C; G5 pre-composition QA body.
3. Vera hardening — closes rows §04 / §10 (currently ⚠️/⚠️) toward ✅ + adds G3 fidelity check on real Storyboard A; G0/G1/G4 evidence-sentence rubrics.

**Class B — Activation refresh (1 specialist; mirror Pass-2 shape into Pass-1)**
4. Irene Pass-1 — closes row §05 (currently ⚠️) toward ✅ + sub-step §05.5 (currently ❌) toward ✅; 9-node Pass-1 scaffold; per-plan-unit ratification surface; G1A operator conversation.

**Class C — Port-shape (5 specialists; passthrough → live LLM/API)**
5. Tracy port-shape + sidecar creation — research-shaped intent enrichment for Pass-2 (no current row owner — Tracy currently runs autonomously; Slab 7b makes Tracy real for Pass-2 enrichment).
6. Gary port-shape — closes row §07 (currently ❌) toward ✅; Gamma API live; per-slide variants.
7. Kira port-shape — closes rows §07E / §07D-cascade (currently ❌/❌) toward ✅; Kling API live; motion generation.
8. Wanda port-shape onto scaffold — Wondercraft API live; podcast/audio bed; (no specific mapping-checklist row owner; activates in storyboard's audio track).
9. Enrique port-shape — closes rows §11 / §11B / §12 (currently ❌/❌/❌) toward ✅; ElevenLabs API live; voice-preview HIL; manifest-driven narration.

**Class D — Greenfield (2 specialists)**
10. Dan greenfield — narrow-lane creative-director aux contributions threaded across G1–G2 (no specific mapping-checklist row owner; activates as cross-cutting helper). Sanctum-alignment option-a required at creation.
11. Compositor greenfield via kind-deterministic scaffold — closes row §14 (currently ❌) toward ✅; deterministic assembly pipeline; `sync-visuals`; `DESCRIPT-ASSEMBLY-GUIDE.md`. Sanctum-alignment option-a required at creation OR option-b documented exception (justification: Compositor doesn't call an LLM, so the BMB sanctum activation pattern may need adaptation — to be resolved at story-1).

**MVP exit gate:** trial-2 runs end-to-end, reaches G3 with real content from eleven specialists, no fix-on-the-fly patches, no silent gate-bypass, no stub-content fallback.

### Growth Features (Post-MVP)

**Slab 8 candidates (runtime / tooling — mostly inherited from Slab 7a Growth):**
- Checkpointer state-traversal CLI (`marcus pending`, `marcus history <run-id>`, `marcus resume <run-id>`)
- `astream_events` HUD replacement of `run_hud.py`
- Replay-regression pack-hash drift remediation
- PR-TR Trial Resumption capability + trial-branch discipline (deferred-inventory entry)
- Texas best-available-medium selection (Epic 27 follow-on)

**Slab 7b deferred candidates** (filed at Slab 7b retrospective):
- Desmond §14.5 — Run-Scoped Operator Brief (mapping checklist row §14.5; currently ❌; deferred from Slab 7b because Desmond is post-Compositor and depends on Compositor's `sync-visuals` artifact). Activates after Compositor body lands.
- §15 Operator Handoff — Descript Ready (mapping checklist row §15; currently ❌; folded with §14.5 follow-on or scoped into Doc-Slab 7-D).
- §6.2 / §6.3 cluster prompt-engineering / dispatch sequencing — conditional-on-CLUSTER_DENSITY paths; activate when cluster intelligence reactivates per Wave 2B → migration plan.

**Doc-Slab 7-D (post-trial-2 documentation harvest, sequenced after Slab 7b + first tracked trial-2):**
- Anti-pattern catalogs harvested from trial-2 real evidence
- Full `langgraph-migration-guide.md` §12 worked examples per specialist (eleven examples)
- Re-authored v4.2 essential-function reference (~400-line distillation)

**Calibration-prerequisite (gates Vision):**
- C2 confidence-gated default-and-override — requires N≥30 trials calibration corpus

### Vision (Future)

**Composition Spec §11 migration triggers — Option C** (LangGraph subgraph composition with parent-graph reducers): inherited monitoring from Slab 7a. Slab 7b adds: any port-shape specialist that requires cross-specialist subgraph reducers fires a §11 trigger watch. Currently 0 of 5 active.

**Epic 15 chain reactivation** (gated on Slab 7b close + first tracked trial-2 close): 15-2 retrospective artifact → 15-3 upstream feedback routing → 15-4 synergy scorecard → 15-5 pattern condensation → 15-6 workflow-family ledger → 15-7 calibration harness.

**Multi-trial calibration corpus (~30+ trials) → C3 evolution** (default-on-override-by-exception). Eleven-specialist real-content trials accelerate corpus accumulation.

**Post-M5 greenfield specialist activations (extended):** Mike, Eli, Mira, Sally, Kim, plus possibly Paige (if scoped as runtime specialist). Generated on-demand via `bmad-create-specialist`. **The eleven-specialist MVP roster is the floor, not the ceiling — but every future addition inherits SG-4 sanctum-alignment by default.**

**Workflow-family expansion per Epic 18** — podcasts, infographics, cases, quizzes. Each new family ships as Tier-3 pack family per Pack Versioning Policy (party-mode consensus required before dev opens).

---

## User Journeys

### Journey 1 — Primary User Happy-Path: A Saturday Morning Trial Where Real Content Actually Shows Up

*Primary user: operator. Validated against trial-475 transcript (the wound being healed) + Slab 2a.2 Irene Pass-2 baseline (the prose-shape being inherited).*

**Opening Scene — 7:47 AM, scar-tissue cautious**

Juan settles in for trial-2. The Slab 7a substrate has been live for four weeks; trial-475 paused-at-G1 cleanly six weeks ago because Texas returned a fixture stub. He has not forgotten. He approaches trial-2 with **earned wariness** — watching the first thirty seconds of specialist load like a hawk for the smell of stub-fallback smoke. The corpus folder for *Lesson 03: Causal Inference for Product Analytics — When Correlation Lies* is staged at `course-content/courses/causal-inference-product-analytics/`. He types one line:

```
bmad-trial start --input course-content/courses/causal-inference-product-analytics/
```

**Emotion: scar-tissue cautious.** Today the bodies have to be real.

**Marcus's pre-gate node fires the directive composer** (Slab 7a Gap-2 closure), pre-fills, presents back. *"Approve?"* Juan reads four lines, hits enter.

**Rising Action — G0 through G2: eleven specialist voices that actually sound different from each other**

**G0 — Texas wakes against a real corpus.** Texas's hardened `_act` (Slab 7b Class-A activation) runs `dispatch_retrieval(directive_path=..., bundle_dir=...)` against the real composed directive. The DOCX provider ingests twelve PDFs. The retrieval contract returns six canonical artifacts: `extracted.md` (~6,200 words; not 25 fixture-stub tokens), `metadata.json`, `extraction-report.yaml`, `manifest.json`, `ingestion-evidence.md`, `result.yaml`. **Vera's G0 6-dim evidence rubric** runs against real extracted content (Class-A Vera hardening): completeness/readability/anchorability/provenance/planning-usability/fidelity-usability — all PASS. Marcus stages the run pack and the lesson title — **the operator's own lesson title, the one for Tuesday's class — sits at the top of the file**. Six weeks of fixture stubs called `lesson-fixture-03` and now the screen says *"Causal Inference for Product Analytics, Lesson 3: When Correlation Lies."* That is the moment Slab 7b earns its name. **First relief.** Juan reads the title once, sets the coffee down.

**G1 + G1A — Irene's Pass-1 lesson plan is a real plan; Vera stamps it.** Irene Pass-1 (Class-B refresh) runs against `gpt-5.4` mirroring Pass-2's 9-node shape. Output: six-unit lesson plan with learning objectives, time allocations, scope-lock candidates — written in Irene's voice, not Vera's, not Tracy's. **Marcus presents per-plan-unit ratification surface** (legacy §04A operator conversation). Juan reads, ratifies four units, requests tightening on two. Irene revises. Per-plan-unit `scope_decision.set` learning events fire; `plan.locked` fires on lock. Vera's G1 6-dim verdicts run against the locked plan. PASS. Receipt written. Irene packet built. **First specialist polyphony moment**: Irene drafts, Vera audits — the two voices are distinguishable in tone, evidence-shape, what they choose to emphasize. They sound like two different reviewers, not two copies of one.

**§4.75 — Dan's CD aux contribution (Class D1 greenfield).** Marcus delegates to Dan when `EXPERIENCE_PROFILE` is set. Dan writes `creative-directive.yaml` against the contract; updates `run-constants.yaml` to match `slide_mode_proportions`; persists `narration_profile_controls`. The `creative_directive_validator.py` PASSes. Juan confirms. **A new voice in the envelope** — narrow-lane, advisory, not redundant with Irene or Tracy.

**G2 — Irene Pass-2 + Tracy enrichment.** Irene Pass-2 (Slab 2a.2 era, already live). Tracy enrichment (Class C+ port-shape + sidecar emission) returns research-shaped intent — *Tracy catches a citation Irene's Pass-2 missed and flags it as a continuity check Vera's calibration didn't think to look for.* Three specialists triangulating, not redundantly co-signing. **The polyphony is the point.** Storyboard-A authorizes. Approved.

**G2B — Per-slide Variant Selection (Gary against real Gamma API).** Gary's Class-C port-shape calls Gamma's API for all 14 slides. Real PNGs export. The HTML review-pack (Slab 7a substrate) renders against real Gamma output — 14 slide cards, three variants each, real PNG previews. Juan scrolls, picks his variants, submits. Quinn-R's G2C (Class-A hardening; storyboard-bound shape) validates the selection set against rubric. `authorized-storyboard.json` writes (legacy §07C contract preserved on migrated path). **The anxiety that would have shown up on slide 9 in a manual trial — doesn't.** Recognition climbs.

**§07D — Wanda's audio-bed (Class C port-shape).** Wanda calls Wondercraft's API for the podcast/audio-bed scoped into the storyboard's audio track. Pre-narration assets land. Quinn-R's pre-comp pass validates audio-bed shape against the storyboard.

**G2F-merged — Per-slide Motion Designation + Approval (Kira against real Kling API).** Kira's Class-C port-shape calls Kling's API. Real motion clips render. Marcus surfaces the merged per-slide HTML pack — designation + clip preview. Juan approves twelve, asks Kira to soften two. Revise count 1/3. Kira returns. Approved.

**Climax — G3: Sequencing Approved with eight real signatures in the envelope and three signatures forward-promised**

**G3 — Sequencing Approved + Storyboard-B HIL review (against real assembled content).** Marcus presents Storyboard-B: the full sequenced cut with **real Gamma stills + real Kling motion + real Wanda audio-bed + real Tracy enrichment + real Irene narration draft**. The ProductionEnvelope, scrolled in summary, shows **eight specialist signatures already stacked append-only at G3 close** — Texas, Vera, Irene, Tracy, Gary, Quinn-R, Kira, Wanda — plus Dan's CD aux contribution where applicable. **Enrique's narration signatures land at G4; Compositor's deterministic-assembly signature lands at G6**; the full eleven-specialist envelope completes at G6.

Juan reads Storyboard-B end to end. He approves. **G3 closes.** The terminal prints `g3.sequencing.approved`.

**Emotion: quiet pride, then tired satisfaction.** Roughly four hours in (aspirational target; first-trial timing baseline TBD from trial-2 actuals). No fixture-stub fallback. No specialist body skipped. No mapping-checklist row regressed. Real content, real specialists, real envelope. **The lesson sounds like it was reviewed by eleven people, not eleven copies of one person.** That is the journey Slab 7b buys him.

**Resolution — Forward to G4 + G5 + G6**

Marcus posts the next-step ribbon: *"Ready for G4 narration (Enrique against real ElevenLabs API) → G5 pre-composition QA (Quinn-R against real assembled bundle) → G6 Compositor (deterministic assembly) → G7 handoff (Desmond §14.5 deferred to post-Slab-7b)."* Juan refills the coffee. The trial isn't done — but the hard half is, and every specialist showed up with real work today.

---

### Journey 2 — Edge-Case Parable: The Substrate Remembered

*Primary user: dev agent (Codex). Supporting cast: reviewer agent (Claude), operator (notified). Validated against Slab 2a.4 Texas BMB migration precedent (the alignment shape) + R1 SG-4 amendment (the enforcement contract).*

**Opening Scene — mid-Slab-7b dev-cycle, Story 7b.X-gary (Gary port-shape; Wave 3) in review, late Friday**

Codex has just finished Gary's port-shape dev-cycle. The story is `review`. Claude opens `bmad-code-review`. Coffee gone cold; ambient time pressure; the substrate is the only thing not in a hurry.

The review pass scans `app/specialists/gary/_act.py` (clean), `tests/specialists/gary/` (clean, K-target met), and then opens `skills/bmad-agent-gamma/SKILL.md`. The SKILL.md is the legacy version — predating Epic 26 BMB migration. No frontmatter. No sanctum activation block. No reference to `_bmad/memory/bmad-agent-gamma/`.

**Rising Action — the substrate remembered**

The reviewer opens the diff expecting a routine green-light and instead the sanctum-alignment check has already drawn its line. **`tests/parity/test_skill_md_sanctum_alignment.py` red.** Specifically: the test parsed `app/specialists/gary/SKILL.md` for the required YAML frontmatter keys (`agent_name`, `sanctum_path`, `activation_order`); none present. Found no `# Sanctum exception` block either. Per the SG-4 contract: silent omission = HALT-AND-REMEDIATE. The gate refuses to advance. **No one had to remember to look. The substrate remembered.**

**From the dev-agent's POV** (Codex): the HALT message is *diagnostic*, not punitive. The error names the failed assertion (`SKILL.md missing required frontmatter keys: ['agent_name', 'sanctum_path', 'activation_order']`), points to the canonical reference (`docs/dev-guide/bmb-sanctum-alignment-checklist.md`), and enumerates the three remediation paths:

1. **Option-a (align):** scaffold-v0.2 `--force` against `bmad-agent-gamma`; SKILL.md frontmatter retrofit; sanctum directory created at `_bmad/memory/bmad-agent-gamma/` with INDEX.md / PERSONA.md / chronology.md / access-boundaries.md (Slab 2a.4 Texas migration precedent). Artifact: aligned SKILL.md + sanctum directory; story Completion Notes records the alignment.
2. **Option-b (documented exception):** add `# Sanctum exception: <category>` block citing closed-allowlist category from `docs/dev-guide/sanctum-exception-categories.json` + `## Rationale` ≥80 chars referencing "sanctum activation" or "BMB pattern" by name + party-mode-recorded ratification in story planning artifact. Artifact: SKILL.md with exception block + party-mode entry; story Completion Notes records the exception.
3. **Option-c (defer):** file a Slab-7c follow-on; add named entry to `_bmad-output/planning-artifacts/deferred-inventory.md §Named-But-Not-Filed Follow-Ons`; pause story until follow-on resolves. Used only if the alignment work itself is out-of-scope for the body-activation story.

Codex's reviewer presents the three options with rationale. Gary the agent calls Gamma the API; Gamma is a real cloud service; Gary has prior persona content; Gary fits the BMB pattern naturally. **Option-a chosen.**

**Climax — Parity test catches the drift; Slab 7b close blocks until green**

Codex (the dev agent) runs scaffold-v0.2 `--force` against `bmad-agent-gamma`. SKILL.md frontmatter retrofit lands. Sanctum directory populates. Re-run: `pytest tests/parity/test_skill_md_sanctum_alignment.py`. Test enumerates `app/specialists/{name}/` and asserts each name has BMB-pattern frontmatter (parsed YAML; required keys present; `sanctum_path == f"_bmad/memory/bmad-agent-{name}/"` derived from dir name) OR explicit `# Sanctum exception` block with rationale. All eleven specialists pass. **Parity green.**

Story 7b.X-gary closes. Slab 7b close-out audit runs the same parity test — green. **Mental-model bifurcation prevented at the story-cycle level, not after-the-fact.**

**Resolution — operator never has to think about which agents are aligned**

Trial-2 launches. Every specialist exhibits the same activation pattern. When the operator opens any agent's SKILL.md, they know what they're going to find — the BMB block. When they don't find it (a future hypothetical), they know to look for the exception block. Two consistent surfaces; not eleven.

**Essential-function preservation:** Legacy shape was prose discipline ("we eventually migrate everyone to BMB pattern; somebody will catch the laggards in a cleanup epic"). Migrated shape is a per-PR parity-test that runs the structural assertion before the human reviewer even opens the diff. Same operator-facing function (consistent agent activation pattern); enforcement moved from prose-discipline to substrate-invariant. **The substrate caught what a human reviewer would have missed at 11pm on a Friday.**

---

### Journey 3 — Admin/Ops: Mid-Flight Re-Entry (the tax doesn't come)

*Primary user: cold-session-operator (distinct from current-operator — has no working memory of mid-flight state). Supporting cast: dev agent state, sprint-status. Speculative — not yet validated against operator behavior; written to the shape Slab 7a hot-start patterns already practice.*

**Trigger:** Operator returns after a 5-day gap mid-Slab-7b dev-cycle (e.g., between Wave-3 port-shape stories 7b.X-gary and 7b.X-kira); needs to reconstitute project state without losing per-specialist activation threads.

**Opening Scene — laptop opens, coffee not yet poured.**

The operator opens the laptop expecting the usual five-day-gap tax — the ten minutes of *"where was I, what was Gary doing, did Vera ever come back on the cost-flag, did the sandbox-AC inventory PR land yet."* The Slab 7b status pane (a dashboard the substrate updates at every story close — surfaced in `next-session-start-here.md` as a standing block, *not* a pytest invocation the operator runs themselves) is on the screen before the coffee is poured: every specialist's class designation, current activation state, alignment status, last-touched timestamp, the one pending decision Marcus parked. **The tax doesn't come.**

**Steps:**

1. **Hot-start ramp.** Operator opens `next-session-start-here.md`. Reads the standing block: "Slab 7b mid-Wave-3"; per-class breakdown (Class A: 3/3 done; Class B: 1/1 done; Class C: 2/4 done; Class C+: 1/1 done; Class D1: 0/1; Class D2: 0/1 — illustrative). Per-specialist sanctum-alignment dashboard inline: 9/11 aligned (option-a), 1/11 expected exception (Compositor pending Story 7b.X1 ratification), 1/11 in-flight (Wanda Story 7b.X2 in `review`).
2. **Deferred-inventory consultation.** Operator opens `_bmad-output/planning-artifacts/deferred-inventory.md`. Notes any new entries filed mid-Slab-7b (e.g., Desmond §14.5 follow-on; §6.2/§6.3 cluster path follow-ons; per-specialist hardening follow-ons). Cross-checks against Slab-7b retrospective draft.
3. **Sprint-status pull.** Reads `_bmad-output/implementation-artifacts/sprint-status.yaml`. Per-class breakdown matches the dashboard.
4. **Sandbox-AC inventory state.** Already confirmed by Wave 0 precondition gate; standing block surfaces the inventory state without operator drill-down (belt-and-suspenders: the operator can verify by running `marcus slab-7b-status --check sandbox-ac` if motivated; the standing block is the routine surface).
5. **Per-specialist alignment dashboard (operator surface).** The standing-block dashboard *already shows* alignment status. The underlying mechanism is `pytest tests/parity/test_skill_md_sanctum_alignment.py` (run by CI at every PR merge per NFR-I9 + at slab-close-time); the operator's surface is the dashboard, not the pytest. Drift surfacing is automatic — if any specialist drops to red between sessions, the dashboard surfaces it without operator action.
6. **Cache-hit-rate harness audit.** For closed Class-C/C+ specialists, dashboard surfaces the median[2:] from `_artifacts/cache_hit_rate_report.md`. Stale fixtures flagged for re-record without operator drilling into raw artifact paths.
7. **Next-action lock.** Records the chosen next-action in `next-session-start-here.md` for the *next* hot-start. Closes the loop.

**Essential-function preservation:** Legacy shape was operator-maintained context discipline ("write good notes in your own session log"). Migrated shape is substrate-emitted dashboard surfaced in the existing `next-session-start-here.md` hot-start protocol. Operator continuity is no longer load-bearing on the operator's note-taking; it's load-bearing on the substrate's status emission.

---

### Journey 4 — Support/Troubleshooting: Trial-2 Investigates a Cost Anomaly Spanning Real APIs

*Primary user: operator + Codex (collaborative). Speculative — not yet validated against trial-2 actuals (no trial-2 has run as of PRD draft date).*

**Trigger:** Trial-2 has just finished. Spend ledger shows total $4.20 (operator ceiling: $3.00). Operator + Codex investigate.

**Steps:**

1. **Cost dashboard pull.** Operator runs `python scripts/utilities/cost_ledger_summary.py --trial trial-2`. Per-specialist breakdown: Texas $0.30 (within), Irene Pass-1 $0.40 (within), Irene Pass-2 $0.35 (within), Tracy $0.25 (within), Gary $1.20 (Gamma API — anomaly), Kira $0.50 (within), Wanda $0.20 (within), Enrique $0.60 (within), Compositor $0 (deterministic; pipeline-determinism harness instead of cost), Quinn-R $0.20 (within), Vera $0.20 (within), Dan $0.05 (CD aux). Marcus orchestration overhead $0.15. **Total $4.40.**
2. **Gary anomaly drill-down (operator-in-the-loop catch).** Operator runs `python scripts/utilities/gamma_api_call_log.py --trial trial-2`. Reveals Gary made 30 Gamma calls instead of expected ~14 (one per slide × DOUBLE_DISPATCH=2 averaged). Cause: an oscillation-guard misconfiguration on slide 8 caused 4 retries before max-3 fired. Codex's first cost reconciliation reads: *"30 × $0.06 = $1.80."* Operator pauses — that math doesn't reconcile against the $1.20 Gary line in the per-specialist breakdown. Re-checks the per-call SKU against the Gamma API invoice: **the SKU is $0.04, not $0.06** (Codex pulled an outdated rate). Corrected: 30 × $0.04 = $1.20. The cost was over-budget but bounded; the operator-in-the-loop catch prevented a remediation story from being filed against a phantom $0.60 over-shoot.
3. **Calibration-tripwire correlation.** Operator runs `cat _artifacts/trial-2/calibration_tripwire_log.jsonl | jq '. | select(.gate == "G2B")'`. Tripwire fired during slide 8 oscillation: confidence-correlation evidence rebuilt-required for G2B; tripwire re-locked batch-approve at G2B for next 3 trials. **The tripwire caught the cost anomaly's root cause** in real-time during trial-2.
4. **Remediation routing.** Operator + Codex file: (a) story `slab-7b-followon-gary-oscillation-on-slide8-misconfig` to fix the oscillation-guard misconfiguration (Slab 7c follow-on); (b) deferred-inventory entry tracking the calibration-tripwire re-lock (will re-arm after 3 clean G2B trials).
5. **Cost-ledger reconciliation.** Operator updates `_bmad-output/cost-ledger.md` with the trial-2 actual vs target; logs the anomaly + remediation; closes the trial-2 cost incident.

**Known-friction acknowledgment (R4 Sally-amendment):** This three-tool dance (`cost_ledger_summary.py` → `gamma_api_call_log.py` → `cat ... | jq`) is authentic to current ops surface. Unified ops tooling is named as a Slab-7b-deferred follow-on at `_bmad-output/planning-artifacts/deferred-inventory.md §Named-But-Not-Filed Follow-Ons` — see entry `ops-tooling-unification`.

**Essential-function preservation:** Six weeks ago the operator caught the cost anomaly by feeling something was off. Today Vera (and the per-specialist breakdown) caught it before the operator finished their first sip of coffee, and the evidence — call counts, per-call SKU rates, the oscillation-guard misconfiguration — was already attached to the gate. The gut feeling didn't go away. **It just stopped being load-bearing.**

---

### Journey 5 — Support/Troubleshooting: Cost-Anomaly-Pre-Launch (the journey that ends in a fork)

*Primary user: operator. Supporting cast: Marcus (cost-projection emitter), Codex (remediation-options drafter). Speculative — not yet validated; written to surface a cost-anomaly-pre-launch failure mode that the four prior journeys do not cover.*

**Trigger:** Slab 7b is `done`. All eleven specialist body activations green. Sandbox-AC inventory PR landed. Sanctum-alignment parity-test green. Mapping-checklist re-audit shows ≤28 row improvements as targeted; 6 deferred rows in expected state. Operator opens trial-2 launch checklist.

**Opening Scene — Marcus's pre-trial cost projection lands.**

Operator runs `marcus trial-2 --dry-run --cost-projection`. Marcus walks the eleven-specialist activation graph against the proposed `course-content/courses/causal-inference-product-analytics/` corpus. Returns a projection: estimated trial-2 cost $5.80 (vs $3.00 BS-3 ceiling) — driven by (a) corpus size (12 PDFs, ~32K tokens vs trial-475's ~6K), (b) Tracy's enrichment depth at default settings, (c) Vera's G4 19-criterion rubric run twice (pre-G4 + re-run post-§08B HIL).

**Emotion: deflation.** Slab 7b was supposed to make trial-2 launchable. The substrate is right, the bodies are real, but the bill is too high.

**The decision-fork (this is where the journey ends — not at a resolution):**

| Option | Trade-off |
|---|---|
| **(α) Scope cut** — drop Class-C+ Tracy enrichment for trial-2; re-run cost projection | Saves ~$0.50; loses Pass-2 enrichment quality; trial-2 no longer load-bearing on Tracy → A-13 may fail trial-2 validation regardless of cost |
| **(β) Budget exception** — operator one-time exception on BS-3 ceiling for trial-2; ratify via party-mode | Trial-2 launches at $5.80; cost-ledger anomaly entered upfront; party-mode signs off |
| **(γ) Trial-shape redesign** — smaller corpus (4 PDFs not 12); cap context windows | Saves ~$2.00; trial-2 less representative of operator's actual production load; A-13 still requires 11-specialist load-bearing exercise |
| **(δ) Slab-7c precondition** — file pre-trial-2 cost-optimization story (e.g., Tracy adaptive enrichment depth; Vera G4 rubric optimization); pause trial-2 | Slab 7b close + trial-2 launch decoupled by ~2 weeks; trial-2 launches against optimized substrate |

**Resolution: not pre-decided.** The journey ends with the decision-fork open. Operator considers the four options against trial-2's purpose (verification of body-activation completeness vs. operator-confidence-in-cost-envelope vs. trial-evidence for Doc-Slab-7-D). Choice is operator-gated; party-mode consensus may be required for option β or δ.

**Why this journey matters:** Slab 7b's success criterion (BS-2: trial-2 launchable end-to-end) is implicitly assumed to be cost-feasible. This journey surfaces the assumption: **"11 specialists load-bearing"** may need to be qualified to **"11 specialists load-bearing within $X budget."** FM-26 (credential drift) covers one pre-launch failure mode; this journey surfaces the cost-pre-launch failure mode that doesn't have a named FM. The journey itself is the argument for one — call it FM-27 if it warrants codifying after operator-review.

**Essential-function preservation:** Legacy shape was operator-eyeballing-the-projection ("does this feel feasible?"). Migrated shape is structured cost-projection + four named remediation paths + party-mode-ratification on substantive deviations. Same operator-facing function (don't launch a trial that's economically dead); enforcement moved from gut-feeling to surfaced-decision-fork.

---

## Domain Requirements (Project-Type Specific)

### Mapping-checklist activation surface (per SG-2)

The 34-atomic-row mapping checklist (33 prompt sections + sub-step §05.5 inline at row 10b) is the structural backbone of Slab 7b's deliverable. Each row owned by an activated specialist must transition from ❌ or ⚠️ to ✅ on the migrated path. Rows owned by future slabs (Desmond §14.5, §15 Operator Handoff) retain their pre-Slab-7b status legend; Slab 7b does NOT regress them.

**R5 Mary-amendment (substrate-as-floor phrasing):** "Marcus orchestration" is Slab-7a substrate, not a Slab-7b body activation. Wherever a row's owning-activation column lists "Specialist X + Marcus orchestration", the canonical phrasing is **"Specialist X (consumes Slab-7a Marcus substrate as floor)"** — substrate is not a co-owner, it is a precondition floor.

**Activation ownership matrix** (which specialist body activation closes which row):

| Mapping row # | Legacy step | Pre-7b status | Owning Slab-7b activation | Post-7b target status |
|---|---|---|---|---|
| 1 | §01 Activation + Preflight | ❌ | Texas hardening + Marcus (substrate-7a; not body) | ✅ |
| 2 | §02 Source Authority Map | ❌ | Texas hardening (Class A) | ✅ |
| 3 | §02A Operator Directives | ❌ | Marcus orchestration (Slab-7a substrate; carry-forward) + Texas directive consumption | ✅ |
| 4 | §03 Ingestion + Evidence Log | ❌ | Texas hardening (Class A; six canonical artifacts) | ✅ |
| 5 | §04 Ingestion Quality Gate + Irene Packet | ⚠️ | Vera hardening (Class A; G0 6-dim) + packet-builder | ✅ |
| 6 | §04A Lesson Plan Coauthoring + Scope Lock | ❌ | Irene Pass-1 (Class B) + Marcus orchestration | ✅ |
| 7 | §04.5 Parent Slide Count Polling | ❌ | Irene Pass-1 (Class B) + Marcus orchestration | ✅ |
| 8 | §04.55 Estimator + Run Constants Lock | ❌ | Irene Pass-1 (Class B) + Marcus orchestration | ✅ |
| 9 | §4.75 Creative Directive Resolution (CD) | ⚠️ | Dan greenfield (Class D; CD aux contributions) | ✅ |
| 10 | §05 Irene Pass 1 + Gate 1 Fidelity | ⚠️ | Irene Pass-1 (Class B) + Vera hardening | ✅ |
| 10b | §05.5 Irene Mode Assignments + HIL Approval | ❌ | Irene Pass-1 (Class B) + Marcus orchestration | ✅ |
| 11 | §05B Cluster Plan G1.5 Gate | ❌ | (Conditional on CLUSTER_DENSITY ≠ none; deferred to cluster intelligence reactivation) | ⚠️ (conditional path; out of Slab 7b MVP) |
| 12 | §06 Pre-Dispatch Package Build | ❌ | Marcus orchestration (Slab 7a substrate; activated by Gary port-shape consumption) | ✅ |
| 13 | §6.2 Cluster Prompt Engineering | ❌ | (Conditional; deferred) | ⚠️ |
| 14 | §6.3 Cluster Dispatch Sequencing | ❌ | (Conditional; deferred) | ⚠️ |
| 15 | §06B Literal-Visual Operator Build | ❌ | Marcus orchestration + Gary port-shape consumption | ✅ |
| 16 | §07 Gary Dispatch + Export | ❌ | Gary port-shape (Class C) | ✅ |
| 17 | §7.5 Cluster Coherence G2.5 Gate | ❌ | (Conditional; deferred) | ⚠️ |
| 18 | §07B Variant Selection Gate | ❌ | Quinn-R hardening (Class A) + Slab 7a per-slide subgraph consumption | ✅ |
| 19 | §07C Storyboard A + Gate 2 + Winner Auth | ⚠️ | Quinn-R hardening (Class A; storyboard-bound shape) | ✅ |
| 20 | §07D Gate 2M Motion Designation | ❌ | Kira port-shape (Class C; per-slide operator conversation surface; consumes Slab-7a Marcus substrate as floor) | ✅ |
| 21 | §07E Motion Generation / Import | ❌ | Kira port-shape (Class C) | ✅ |
| 22 | §07F Motion Gate | ❌ | Quinn-R hardening (Class A; G2F mode) + Kira consumption | ✅ |
| 23 | §08 Irene Pass 2 + Segment Manifest | ⚠️ | Irene Pass-2 (Slab 2a.2 era; carry-forward) + Tracy port-shape (Class C) enrichment | ✅ |
| 24 | §08B Storyboard B + HIL Review | ❌ | Quinn-R hardening (Class A) + Slab 7a HTML review-pack consumption | ✅ |
| 25 | §09 Gate 3 — Lock Pass 2 Package | ⚠️ | Marcus orchestration + Quinn-R G3 contract | ✅ |
| 26 | §10 Fidelity + Quality Pre-Spend | ⚠️ | Vera hardening (Class A; G4 19-criterion) + Quinn-R hardening | ✅ |
| 27 | §11 ElevenLabs Voice Selection HIL | ❌ | Enrique port-shape (Class C) | ✅ |
| 28 | §11B ElevenLabs Input Package HIL | ❌ | Enrique port-shape (Class C) | ✅ |
| 29 | §12 ElevenLabs Audio Generation | ❌ | Enrique port-shape (Class C) | ✅ |
| 30 | §13 Quinn-R Pre-Composition QA | ❌ | Quinn-R hardening (Class A; G5 pre-composition body) | ✅ |
| 31 | §14 Compositor Assembly Bundle | ❌ | Compositor greenfield (Class D) | ✅ |
| 32 | §14.5 Desmond Run-Scoped Operator Brief | ❌ | (Deferred to Slab 7c follow-on; depends on Compositor) | ❌ (out of Slab 7b MVP) |
| 33 | §15 Operator Handoff — Descript Ready | ❌ | (Deferred; folded with §14.5 follow-on or Doc-Slab 7-D) | ❌ (out of Slab 7b MVP) |

**Summary of Slab 7b row resolutions (R5 Mary-amendment, count alignment):**
- Rows fully resolved by Slab 7b: ~28 row improvements (21 ❌→✅ + 7 ⚠️→✅) on rows owned by activated specialists.
- **6 rows conditional / deferred** (4 conditional cluster paths §05B/§6.2/§6.3/§7.5 + §14.5 Desmond + §15 Operator Handoff post-Compositor) — out of Slab 7b MVP, filed for future slab. Aligned with Exec Summary post-R2 + A-10 acceptance clause.
- Rows preserved unchanged: 0 (no row regresses; SG-2 floor honored).

**Wanda + Tracy host-row attribution (R5 Mary-amendment):** Wanda's audio-bed activation runs as an internal mechanism *inside* the Pass-2 narration cascade — host rows are §08 (Pass-2 + Segment Manifest) audio-track contribution and §07E-cascade (motion generation cascade) audio-bed slot. Tracy's enrichment activation runs as an internal mechanism *inside* the Pass-2 narration cascade — host row is §08 (Pass-2 + Segment Manifest) — research-shaped intent enrichment travels with Irene's Pass-2 output. Neither owns a standalone row but both have explicit host-row attribution per SG-2 rigor.

### Operator-control parity (carry-forward extension from Slab 7a)

Slab 7a established the operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md` and its enforcing parity-test suite. Slab 7b extends both, with R5-amended strictness on what counts as a "parity row."

**R5 Winston-amendment (parity-table strictness):** "Specialist active" is NOT a parity claim. Each of the 11 new parity-table rows MUST enumerate, at row level:
- Legacy lever(s) that controlled this specialist (env var, CLI flag, config-file knob, sidecar override; e.g., `IRENE_RUBRIC_OVERRIDE_PATH`, `--gary-strict`, `texas.cache_ttl` config key);
- Migrated lever(s) and exact names;
- Back-compat shim status (if any) and sunset date;
- The test that proves the migrated lever changes specialist behavior end-to-end.

If the eleven new rows cannot be filled at this granularity at PRD-time, that's a planning gap to surface NOW, not after Class-A1 lands. Per-specialist operator-control inventory (template at `docs/dev-guide/operator-control-parity-template.md` — a Slab-7b foundational artifact) MUST be filed before that specialist's class enters dev.

**Parity-test suite extension:** 11 new test files added under `tests/parity/per_specialist/` per NFR-I10 naming convention `test_<specialist_name>_activation_contract.py` (R5 Amelia-amendment; aligns with R3 A-9 file-path table). Per-specialist test pattern is **class-shaped, NOT uniform** (R5 Winston + Amelia amendment):
- **Class A (Texas/Quinn-R/Vera) hardening:** rubric-semantics parity — does the migrated rubric produce the same pass/fail verdicts on a fixed evidence set as the legacy rubric? Property-based, not cache-shaped.
- **Class B (Irene Pass-1) refresh:** persona-continuity parity + sidecar-write parity — does the migrated specialist write the same chronology entries and access-boundary updates?
- **Class C (Gary/Kira/Wanda/Enrique) port-shape:** live-API contract + cache-hit-rate parity (T4 harness, ≥85% median[2:]).
- **Class C+ (Tracy) port-shape with sidecar emission:** Class C tests + sidecar-emission parity (4-file BMB pattern).
- **Class D1 (Dan) LLM-greenfield:** parity to Class B/C bodies with explicit "no prior body" baseline; first-recorded fixture set.
- **Class D2 (Compositor) pipeline-greenfield:** pipeline-determinism parity (bytes-identical for `sync-visuals`; field-masked-hash for `assembly-guide`); NOT cache-hit-rate.

### BMB activation pattern (per SG-4)

The BMB sanctum activation pattern, established by Epic 26 BMB migration + extended by Slab 2a.4 Texas migration, is the canonical activation shape for every Slab 7b body. **R5 Winston + Paige amendment:** the canonical alignment authority is `docs/dev-guide/bmb-sanctum-alignment-checklist.md` (R1 amendment artifact). `_bmad-output/implementation-artifacts/epic-26/_shared/scaffold-v0.2-backlog.md` is cited as **historical precedent only** (a backlog, not a normative alignment contract). The pattern's mechanical components:

1. **SKILL.md frontmatter** retrofit (parseable YAML; required keys `agent_name`, `sanctum_path`, `activation_order`; `sanctum_path` derived from dir name as `_bmad/memory/bmad-agent-{name}/`).
2. **Sanctum config load** at activation (reads `_bmad/core/config.yaml` first; overlay precedence preserved).
3. **Activation order** documented in SKILL.md: config load → sanctum batch under `_bmad/memory/bmad-agent-{name}/` (INDEX.md, PERSONA.md, chronology.md, sidecar) → First Breath if sanctum is absent.
4. **Persistent persona + continuity artifacts** under `_bmad/memory/bmad-agent-{name}/`: `INDEX.md` (sanctum directory), `PERSONA.md` (persona + boundaries), `chronology.md` (history of activations + key decisions), `access-boundaries.md` (read/write/deny zones).

**Documented-exception path (Cora precedent — R5 Paige + Winston amendment, concrete recipe):** option-b SKILL.md contains an explicit `# Sanctum exception: <category>` block where `<category>` matches a row in `docs/dev-guide/sanctum-exception-categories.json` (closed allowlist), followed by `## Rationale` ≥80 chars referencing "sanctum activation" or "BMB pattern" by name. **Concrete paste-pattern reference:** see [`skills/bmad-agent-cora/SKILL.md` §"Sanctum exception"](skills/bmad-agent-cora/SKILL.md) — future Slab 7b authors invoking option-b copy that block verbatim and adjust `{specialist}`, `{category}`, `{rationale}` fields. If `skills/bmad-agent-cora/SKILL.md` does not currently have a stable §"Sanctum exception" anchor, that header is itself a Slab 7b foundational artifact (added to the precondition list below).

**Compositor predicted-path (R5 Winston + Amelia amendment, Class-D2 sidecar variant — NOT exception):** Compositor is deterministic; it doesn't call an LLM and doesn't accumulate persona-shaped continuity. **However**, a deterministic pipeline can and should maintain operational metadata: `chronology.md` recording pipeline-runs, `access-boundaries.md` recording which directories the pipeline reads/writes, `contract.md` recording input/output shape, `version.md` recording behavioral changes. The predicted-path rationale is therefore: **Compositor follows a Class-D2 scaffold-v0.2-D2 variant** (LLM-loop slots empty; sanctum carries operational metadata not persona-shaped continuity) — recognized variant inside the BMB regime, not exception against it. Documented in scaffold-v0.2-D2-pipeline contract at `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` (Slab 7b foundational artifact). Final choice resolved at Compositor Story 7b.X-compositor (operator-gated; party-mode if option-b sidecar exception is preferred over Class-D2 variant).

**Wanda predicted-path:** Wanda already has a sidecar (per frontmatter `slab7bSpecialistRoster.specialists.wanda.sidecar = 'wanda-sidecar'`) but the client landed not-on-scaffold (status `client-landed-not-on-scaffold`). Most likely path: option-a alignment via scaffold-v0.2 `--force` + sanctum directory creation. Final choice resolved at Wanda port-shape Story 7b.X-wanda.

### Slab 7b foundational artifacts (precondition list — R5 amendment)

The following artifacts MUST exist before the **first body-activation story** (Wave 1 Class-A) opens for dev:

1. `docs/dev-guide/bmb-sanctum-alignment-checklist.md` — canonical SG-4 alignment authority. TOC (Paige-amendment commitment): §1 Purpose & audience; §2 When to use (T1 / story-close / cold-pickup); §3 Required sanctum artifacts (INDEX/PERSONA/access-boundaries/SKILL.md required-keys auto-checkable); §4 Activation-pattern verification (manual-eyeball); §5 Documented-exception pattern (option-b); §6 Worked examples (standard activation + Cora-sidecar paste-pattern); §7 Auto-check script contract (inputs/outputs/exit-code); §8 Glossary.
2. `docs/dev-guide/sanctum-exception-categories.json` — closed allowlist for option-b categories. Initial entry: `sidecar-hook` per Cora precedent.
3. `docs/dev-guide/operator-control-parity-template.md` — per-specialist operator-control inventory template (R5 Winston-amendment; required before each specialist's class enters dev).
4. `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` — Class-D2 pipeline-greenfield scaffold variant for Compositor (R5 Amelia + Winston amendment).
5. `skills/bmad-agent-cora/SKILL.md` §"Sanctum exception" stable anchor — concrete paste-pattern target (R5 Paige-amendment).

The sandbox-AC inventory (5-entry: gamma/kling/elevenlabs/wondercraft/dan-api-tbd) remains a Wave-0 precondition for API-bound Class-C/C+/D opens (separate from this list; named in Success Criteria + Project Scoping).

---

## Functional Requirements

These FRs extend the Slab 7a 87-FR set. Slab 7a FRs are inherited verbatim; Slab 7b adds FRs in the 88+ range. Aggregate Slab 7a + 7b: ~125+ FRs (post-R6 amendment).

**R6 Winston-amendment (substrate-vs-body convention):** every per-specialist FR (FR89-FR99) is **body-work** scope (Slab 7b). Substrate symbols cited inline as "carry-forward" denote Slab-7a substrate consumed by the body; substrate is NOT amended by Slab 7b (substrate-as-floor invariant; per Exec Summary differentiator #1). Any apparent substrate edit during Slab 7b dev opens a Slab-7a-defect story per FR113 governance gate.

### FR-7b-roster — Eleven-specialist activation roster (canonical)

**FR88.** Slab 7b ships eleven specialist body activations covering: Texas (Class A hardening), Irene Pass-1 (Class B activation refresh), Tracy (Class C port-shape + sidecar creation), Gary (Class C port-shape), Kira (Class C port-shape), Wanda (Class C port-shape onto scaffold), Enrique (Class C port-shape), Dan (Class D greenfield), Compositor (Class D greenfield), Quinn-R (Class A hardening), Vera (Class A hardening). Per-specialist Slab-7b shape designation (frontmatter `slab7bSpecialistRoster.specialists.{name}.slab7bShape`) is operator-ratified and binds.

### FR-7b-class-A-hardening (FR89–FR91)

**FR89.** Texas hardening MUST land: live-retrieval-against-real-directive-composer; six-canonical-artifacts contract enforcement (extracted.md / metadata.json / extraction-report.yaml / manifest.json / ingestion-evidence.md / result.yaml); G0 6-dim evidence-sentence rubric; word-count belt-and-suspenders check; cross-validation hint application.

**FR90.** Quinn-R hardening MUST land: two-mode (pre-composition / post-composition) rubric semantics; G2C storyboard-bound shape (`authorized-storyboard.json` write contract); G5 pre-composition QA body (WPM review + VTT monotonicity + coverage completeness + motion-vs-narration duration coherence + advisory-vs-blocking partition).

**FR91.** Vera hardening MUST land: G0 6-dim evidence-sentence rubric on real Texas output; G1 ingestion-quality 6-dim verdicts; G3 fidelity check on real Storyboard A; G4 19-criterion rubric (G4-01 through G4-19) on real Irene Pass-2 output; sensory-bridges dispatch on real motion + audio.

### FR-7b-class-B-refresh (FR92)

**FR92.** Irene Pass-1 activation refresh MUST land: 9-node scaffold mirroring Pass-2 shape (Slab 2a.2 precedent); lesson-plan coauthoring + scope-lock contract; per-plan-unit ratification surface for G1A; `irene-pass1.md` artifact write; mode-singularity hard-constraint enforcement; `scope_decision.set` + `plan.locked` learning-event emission.

### FR-7b-class-C-port-shape (FR93–FR97)

**Note (R6 John-amendment):** Tracy is **Class C+** (port-shape with sidecar emission), not pure Class C. FR93 carries a one-tier K-bump per Class-C+ designation; sidecar emission is in scope (4-file BMB pattern). The remaining four FRs (FR94-FR97 — Gary/Kira/Wanda/Enrique) are pure Class C.

**FR93.** Tracy port-shape + sidecar creation (**Class C+**) MUST land: research-shaped intent enrichment for Pass-2; sidecar greenfield at `_bmad/memory/bmad-agent-tracy/` with full 4-file BMB pattern (INDEX.md / PERSONA.md / chronology.md / access-boundaries.md); 9-node scaffold per Slab 2b.1 TEMPLATE; live LLM-only binding (no third-party API; sandbox-AC inventory entry not required for Tracy specifically); cache-hit-rate harness ≥85% post-warm-up. Sidecar emission may be split into a separate story `slab-7b.tracy-bmb-sidecar` after the port-shape story per R5 Amelia-amendment.

**FR94.** Gary port-shape MUST land: Gamma API live invocation; per-slide variant generation (DOUBLE_DISPATCH branch when applicable); theme-handshake; PNG export normalization (`_materialize_exported_slide_paths` carry-forward); Vera G3 invocation hooks; cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR95.** Kira port-shape MUST land: Kling API live invocation; motion generation per `motion_plan.yaml`; per-slide `.progress.json` + terminal `.json` receipts; reviewer inspection pack at `[BUNDLE_PATH]/recovery/inspection/`; fail-closed budget rules; cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR96.** Wanda port-shape onto scaffold MUST land: Wondercraft API live invocation; podcast/audio bed generation scoped into storyboard's audio track; scaffold-v0.2 alignment (closes pre-Slab-2b client-landed-not-on-scaffold gap); cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR97.** Enrique port-shape MUST land: ElevenLabs API live invocation; voice-preview + voice-selection HIL contract (`voice-preview-options.json` + `voice-selection-review.md` + `voice-selection.json` artifact write); manifest-driven narration on locked package; assembly-bundle build (`assembly-bundle/audio/` + `captions/`); per-segment progress to stderr; cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

### FR-7b-class-D-greenfield (FR98–FR99)

**FR98.** Dan greenfield via `bmad-create-specialist` MUST land: SKILL.md (option-a sanctum-aligned); sidecar at `_bmad/memory/bmad-agent-dan/` with full BMB pattern; `app/specialists/dan/` directory with scaffold-v0.2; `_act` body shaped as narrow-lane creative-director aux contributions threaded across G1–G2; sandbox-AC `dan-api-tbd` inventory entry resolved at story-1 (LLM-only or third-party-API to be determined).

**FR99 (R6 Amelia + Winston + Mary amendment, Class-D2 sidecar variant restated).** Compositor activates per **Class-D2 sidecar variant** of the BMB regime (canonical, NOT exception): persona artifacts live as a sidecar with operational-metadata content (`contract.md`, `version.md`, `chronology.md` recording pipeline-runs, `access-boundaries.md` recording read/write directories) — sidecar carries operational metadata, not persona-shaped continuity. Class-D2 variant is recognized inside the BMB checklist as a first-class activation shape; no `# Sanctum exception` block required. MUST land: SKILL.md aligned per scaffold-v0.2-D2-pipeline contract (FR111); `app/specialists/compositor/` directory; `_act` body shaped as deterministic assembly pipeline; `sync-visuals` operation; `DESCRIPT-ASSEMBLY-GUIDE.md` regeneration; localized stills + motion under `assembly-bundle/visuals/` + `motion/`; pipeline-determinism harness ≥99% rate (bytes-identical for `sync-visuals`; field-masked-hash for `DESCRIPT-ASSEMBLY-GUIDE.md` modulo `{generated_at, run_id, build_timestamp}` per R3 Amelia-amendment).

### FR-7b-sanctum — SG-4 sanctum alignment per body (FR100–FR103)

**FR100.** Every Slab 7b body-activation story MUST carry a `# SG-4 Sanctum Alignment` AC requiring SKILL.md to either align (option-a) with the BMB pattern OR document an exception (option-b) with explicit rationale. Reviewer verifies during `bmad-code-review`.

**FR101 (R6 Winston + Mary + Amelia amendment, R1-contract restated).** A structural parity test `tests/parity/test_skill_md_sanctum_alignment.py` MUST exist by Slab 7b close. Test contract:
- (i) enumerates the eleven-specialist roster from SG-1; asserts each name has a directory at `app/specialists/{name}/` containing `SKILL.md` (missing dir or missing SKILL.md = FAIL, not skip);
- (ii) parses each `SKILL.md` frontmatter as YAML; asserts required keys (`agent_name`, `sanctum_path`, `activation_order`, `class` enum {A, B, C, C+, D1, D2}); asserts `sanctum_path == f"_bmad/memory/bmad-agent-{name}/"` derived from dir name (catches copy-paste bugs and shape-drift);
- (iii) for `class: D2` (Compositor), asserts the Class-D2 sidecar variant contract per scaffold-v0.2-D2-pipeline (FR111) instead of sanctum-path-equality;
- (iv) for option-b cases (rare; only allowed via party-mode-ratified closed-allowlist), asserts `# Sanctum exception: <category>` heading where `<category>` matches a row in `docs/dev-guide/sanctum-exception-categories.json` (FR109), AND a `## Rationale` subsection ≥80 chars referencing "sanctum activation" or "BMB pattern" by name;
- (v) cold-activation smoke per A-11 (R3 Quinn FM-25 mitigation) — for each migrated specialist, simulates operator typing `talk to {name}` in fresh session; asserts SKILL.md loads + sanctum batch loads + persona activates without error.

The test references `docs/dev-guide/bmb-sanctum-alignment-checklist.md` (FR108) as canonical alignment authority.

**FR102.** The parity test MUST run at every PR merge gate. A red parity test blocks merge.

**FR103.** A documented sanctum-alignment matrix MUST live at `docs/dev-guide/specialist-sanctum-alignment-matrix.md`, listing every specialist + alignment-or-exception verdict + rationale link. Updated at every Slab 7b body-activation story close.

### FR-7b-substrate-consumption-extended (FR104–FR107) — R6 Winston + Mary amendment

**Naming clarification:** these FRs describe how Slab 7b body code **consumes** Slab 7a substrate APIs in extended fashion (deeper retrieval composition, per-specialist parity rows, etc.). The substrate API surface stays frozen per substrate-as-floor invariant; Slab 7b body just exercises more of it. If any apparent substrate-side change is required, that item is OUT of Slab 7b scope and gets filed to `deferred-inventory.md` as a substrate amendment for a future maintenance slab.

**FR104.** Operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md` MUST extend with 11 new rows (one per specialist body activation) by Slab 7b close. Per R5 Winston-amendment: each row enumerates legacy lever(s) → migrated lever(s) → back-compat shim status → end-to-end test asserting the lever changes specialist behavior. Per-specialist operator-control inventory MUST be filed (template at FR110) before that specialist's class enters dev.

**FR105.** Parity-test suite at `tests/parity/per_specialist/` MUST exist by Slab 7b close, with one test file per specialist following NFR-I10 naming convention `test_<specialist_name>_activation_contract.py`. Per-specialist test pattern is class-shaped (per R5 Winston + Amelia amendment): Class-A rubric-semantics parity; Class-B persona-continuity + sidecar-write parity; Class-C live-API + cache-hit-rate parity; Class-C+ adds sidecar-emission parity; Class-D1 first-recorded fixture set; Class-D2 pipeline-determinism parity.

**FR106.** Cache-hit-rate harness MUST be configured for ten LLM specialists (Texas / Irene-Pass1 / Irene-Pass2 / Tracy / Gary / Kira / Wanda / Enrique / Quinn-R / Vera) per T4 cadence + one Compositor pipeline-determinism harness per Class-D2 contract (NOT cache-hit-rate). Parametric configuration (single binary, config-driven). Wall-clock per harness ≈230s × N=10; runs at green-light cadence, NOT in T1/T2 dev-cycle inner loop.

**FR107.** Sandbox-AC inventory at `docs/dev-guide/migration-ac-sandbox-inventory.json` MUST extend with up to 5 new entries (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-if-API) BEFORE any **API-bound** Class-C / Class-C+ / Class-D Slab 7b story opens (per R5 Amelia-scope-amendment: Tracy + Dan-without-API exempt). The inventory PR is a hard precondition for Wave-3+; Slab 7a closeout names this as a Slab 7b-precondition follow-on.

### FR-7b-foundational-artifacts (FR108–FR112) — R6 Amelia + John + Mary amendment

These five FRs anchor the foundational artifacts that MUST exist before the **first body-activation story** (Wave 1 Class-A) opens for dev. Without them, no Slab 7b story is `ready-for-dev`.

**FR108.** `docs/dev-guide/bmb-sanctum-alignment-checklist.md` MUST exist before Wave 1 Class-A opens. The checklist is canonical SG-4 alignment authority. Required TOC (R5 Paige-amendment): §1 Purpose & audience; §2 When to use (T1 / story-close / cold-pickup); §3 Required sanctum artifacts (auto-checkable); §4 Activation-pattern verification (manual-eyeball); §5 Documented-exception pattern (option-b); §6 Worked examples (standard activation + Cora-sidecar paste-pattern); §7 Auto-check script contract (inputs/outputs/exit-code); §8 Glossary.

**FR109.** `docs/dev-guide/sanctum-exception-categories.json` MUST exist before Wave 1 opens. Closed allowlist for option-b categories. Initial entry: `sidecar-hook` per Cora precedent. Reviewer + parity-test reference this allowlist to validate option-b SKILL.md exception block category claims.

**FR110.** `docs/dev-guide/operator-control-parity-template.md` MUST exist before Wave 1 opens. Per-specialist operator-control inventory template with sections: legacy lever inventory; migrated lever mapping; back-compat shim status; end-to-end test pointer. Each specialist's class-entry-precondition is a filled instance of this template (per FR104 R5 Winston-amendment).

**FR111.** `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` MUST exist before Wave 5 (Class-D Compositor) opens. Class-D2 pipeline-greenfield scaffold variant — defines sidecar shape (operational metadata), pipeline-determinism contract, field-mask convention. Compositor body activation consumes this scaffold.

**FR112.** `skills/bmad-agent-cora/SKILL.md` MUST contain a stable §"Sanctum exception" anchor section before any option-b invocation. Concrete paste-pattern target referenced by FR101 parity-test, FR108 alignment checklist §6.2 worked example, and any future Slab 7b story invoking option-b.

### FR-7b-substrate-boundary-frozen (FR113) — R6 Winston amendment

**FR113.** No Slab 7b body activation story amends the **Marcus duality boundary** at `app/marcus/orchestrator/dispatch_adapter.py:81` (line-pinned per R2 freeze). Activation work calls *across* the boundary using existing dispatch APIs; it does not modify the dispatch adapter itself. `bmad-code-review` MUST flag any diff hunk touching `dispatch_adapter.py` lines 70–95 as a governance escalation (catches nearby edits that effectively shift the boundary even if line 81 itself is untouched). Any boundary edit is a substrate amendment governed under the Slab 7a substrate-as-floor regime, filed to `deferred-inventory.md` if needed; opens a Slab-7a-defect story per substrate-as-floor invariant.

---

## Non-Functional Requirements

These NFRs extend the Slab 7a 73-NFR set. Slab 7a NFRs are inherited verbatim; Slab 7b adds NFRs in the 74+ range.

**Family-continuity anchor (R7 Mary-amendment):** NFR family numbering continues from Slab 7a substrate close: T8→T9, CG11→CG12, I8→I9, OD2→OD3.

**Enforcement principle (R7 Murat + Winston amendment):** every NFR with a "MUST pass at PR merge gate" clause is bound to a named CI workflow file or a named validator script. NFRs without enforcement scaffold are explicitly tagged "MUST pass at Slab 7b close" with a wave story to land the workflow. No aspirational gates.

### NFR-T (Test discipline) — extension from 7a (R7 restated per R3 T-tier split)

**NFR-T9** (T1 unit/contract): wall-clock <30s aggregate per specialist parity suite, <5 min for full 11-specialist run. Enforced per-PR via `@pytest.mark.timeout` + `.github/workflows/composition-tests.yml` per-job ceiling.
**NFR-T10** (T2 fixture-replay): wall-clock <90s per specialist replay; cassettes under `tests/fixtures/specialist-replay/<name>/`. Enforced per-PR on touched specialist only.
**NFR-T11** (T3 canary live-substrate smoke): wall-clock <120s per specialist; quota-gated (operator-gated Completion-Notes evidence, not CI). One canary per specialist per merge-train day.
**NFR-T11a** (T4 cache-determinism harness): wall-clock <45s per specialist; runs nightly OR green-light cadence, NOT per-PR. Determinism-violation = block-mode.
**NFR-T11b** (T5 live canaries — Class-C/C+/D1 only): operator-gated only; no CI budget. ≤3 canaries per specialist (hard cap). Cost ceiling ~$0.40 per canary. Evidence pasted into Completion Notes.
**NFR-T12 (NEW; R7 Murat + Mary).** Parity-test wall-clock SLA: full 11-specialist FR101 parity test (YAML parse + key assertion + cold-activation smoke) MUST complete in <120s wall-clock on the standard CI runner (GitHub-hosted `ubuntu-latest`, 2 vCPU, 7GB). Aggregate budget; per-specialist budget ~10s. Regressions block merge; budget renegotiation requires party-mode.

### NFR-CG (Compliance & Governance) — extension from 7a

**NFR-CG12.** Slab 7b sandbox-AC inventory PR MUST land before any API-bound Class-C/C+/D Slab 7b story opens. Story-open-before-PR-landed = governance failure.
**NFR-CG13 (R7 Amelia detection mechanism).** Slab 7b live-API-on-CI for any API-bound specialist = 0 occurrences. Detection: `scripts/utilities/detect_live_api_in_tests.py` AST-scans `tests/` for forbidden import set (live-API patterns; inventory at `docs/dev-guide/composition-test-forbidden-imports.json`); runs as pre-merge GitHub Action. Any occurrence = governance failure.
**NFR-CG14.** Slab 7b per-specialist Composition Spec §6 chain-test PR MUST land per body activation. Missing chain-test = blocks story close. **NFR-CG14a (NEW; R7 Amelia precondition):** chain-test base class at `tests/composition/_chain_test_base.py` (BaseSpecialistChainTest with red-input contract, golden-output assertion, A2 shim contract) MUST land BEFORE first body activation (Wave 1 Class-A); all eleven per-specialist chain-tests inherit. Adds ~0.5 dev-day to Wave 0 / Wave 1 setup; saves ten reinventions.
**NFR-CG15.** Slab 7b per-specialist Composition Spec §10 Decision Log entry MUST land for any body activation that emits new vocabulary into the registry. Detection: `scripts/utilities/validate_specialist_composition_spec_decision_log.py` diffs the specialist's Composition Spec §6 vocabulary set against §10 entries; new vocab without a §10 row = block. Missing entry = SG-3 violation.
**NFR-CG16.** Slab 7b per-specialist BMAD code-review MUST land before story close. (Inherited from CLAUDE.md sprint governance; restated for explicit Slab 7b enforcement.)
**NFR-CG17 (NEW; R7 Winston + Mary; closes R2 scope-binding #8 gap).** Codex parallel-authoring contract: Class-C/C+ port-shape stories (Tracy/Gary/Kira/Wanda/Enrique) + sandbox-AC inventory PR + per-story `bmad-code-review` per Slab 7a deployment precedent execute via Codex. Class-A hardening + Class-B refresh + Class-D1/D2 greenfield + Wave-6 integration story remain Claude-authored. Wave's parallel-authoring contract is satisfied when ≥N-1 of N Class-C/C+ specialists in the wave are authored within the same Codex-session window. Single-session serial authoring of all N is a governance failure absent documented impasse. Removing or substantially altering Codex deployment requires party-mode consensus.
**NFR-CG18 (NEW; R7 Mary; foundational-artifacts precondition).** Wave 1 (and any subsequent wave depending on foundational artifacts FR108-FR112) MUST NOT open until all five foundational-artifact deliverables are merged to `dev/langchain-langgraph-foundation` and validated by substrate-completeness check. A Wave 1 story authored against missing foundational artifacts constitutes a governance failure; the story spec MUST be retracted, foundational artifacts completed, and the story re-authored. No partial-substrate Wave 1 stories.
**NFR-CG19 (NEW; R7 Winston; five-API operator-side).** Credential-rotation register at `state/config/credential-rotation-register.yaml` lists each of the 5 API surfaces (gamma/kling/elevenlabs/wondercraft/dan-api-tbd) with: owner, rotation cadence, last-rotated date, next-due date, secret-store reference. Quarterly review at retrospective. Missing/expired entries fail the credentials-audit workflow.
**NFR-CG20 (NEW; R7 Winston; five-API operator-side).** Per-specialist rate-limit budget declared in each `app/specialists/<name>/config.yaml` (or sanctum equivalent) — daily token/request ceiling per upstream API. Specialist run aborts cleanly on budget exceeded; no silent-degradation. Budget changes are governance (party-mode), not dev-agent.

### NFR-I (Invariants) — extension from 7a (R7 Winston CI-binding amendment)

**NFR-I9 (NEW).** Sanctum alignment invariant: `tests/parity/test_skill_md_sanctum_alignment.py` MUST pass at every PR merge. Bound to `.github/workflows/specialist-parity.yml` as required check (job name: `parity-test`). If workflow scaffold not yet landed at FR108-FR112 merge, NFR-I9 re-classifies to "MUST pass at Slab 7b close" with Wave-0 / Wave-1 story landing the workflow.
**NFR-I10 (NEW).** Per-specialist activation contract invariant: `tests/parity/per_specialist/test_<specialist_name>_activation_contract.py` MUST pass for every specialist by Slab 7b close. Bound to `.github/workflows/activation-contract.yml` as required check. Each test asserts the specialist body honors its per-shape contract (Class A: rubric semantics; Class B: Pass-1 mirroring Pass-2; Class C/C+: live API + cache-hit-rate; Class D1: greenfield + scaffold; Class D2: pipeline-determinism).
**NFR-I11 (NEW).** Mapping-checklist row-status invariant: `tests/parity/test_mapping_checklist_status.py` MUST pass by Slab 7b close. Bound to `.github/workflows/mapping-checklist.yml` as required check. Asserts ~28 row improvements (per A-10 R3 amendment) on rows owned by activated specialists; deferred rows (§05B, §6.2, §6.3, §7.5, §14.5, §15) retain pre-Slab-7b status legend.
**NFR-I12 (NEW; R7 Murat).** Class-shaped parity-test invariant: every specialist parity test MUST conform to exactly one of the 5 class templates (A/B/C+merged-with-C+/D1/D2) defined in the canonical alignment checklist (FR108). Template drift between classes (e.g., a fix landing in Class-A without backporting to Class-B) is a block-mode finding. Verified per-PR by `validate_parity_test_class_conformance.py` (AST-walk + import check).
**NFR-I13 (NEW; R7 Winston substrate-as-floor).** The substrate paths frozen at Slab 7a close (enumerated in §IR-1: `_bmad/memory/shared/`, `app/marcus/orchestrator/dispatch_adapter.py:81`-region, conversation-persistence layer, per-slide subgraph skeleton, vocabulary registry, gate-runner substrate, SG-1..SG-4 contract files) plus the Marcus boundary contract are FROZEN-AT-SLAB-7A-CLOSE. PR-level enforcement: CODEOWNERS rule + `.github/workflows/substrate-frozen.yml` fails if a PR diff touches substrate paths without an `allow-substrate-edit` label applied by Marcus or operator. Subsequent edits require explicit slab-bump (Slab 7b only adds activation; Slab 8+ may extend).

### NFR-OD (Operator Documentation) — extension from 7a

**NFR-OD3 (NEW; R7 Amelia path-pin).** Per-specialist operator-reference docs MUST exist at `docs/operator/specialists/<name>.md` for each of the 11 activated specialists by Slab 7b close. Each doc carries OPERATOR / INPUTS / OUTPUTS / REFERENCE four-section structure (Slab 7a Story 7a.7 audience-layered help-text precedent).
**NFR-OD4 (NEW; R7 Amelia path-pin).** Specialist-sanctum-alignment matrix doc at `docs/operator/specialists/sanctum-alignment-matrix.md` MUST exist by Slab 7b close, listing every specialist + alignment-or-exception verdict + rationale link.
**NFR-OD5 (NEW; R7 Winston).** Specialist test fixtures wrapping upstream APIs (Notion pages, Box files, Playwright captures, plus the 5-API surfaces) MUST support a fixture-refresh dry-run mode: `python scripts/utilities/refresh_fixtures.py --specialist <name> --dry-run` reports what would change without writing. Real refresh requires `--apply` + operator confirmation. Prevents silent fixture drift masking upstream behavior changes.
**NFR-OD6 (NEW; R7 Winston).** Codex agent invocation in Slab 7b is restricted to operator-machine activation flow (local `.venv` + operator-initiated). PR-level enforcement: any workflow file under `.github/workflows/` that references `codex` or invokes the Codex CLI fails the `codex-scope-audit` job. Exception requires governance JSON entry + party-mode consensus.

---

## Innovation & Novel Patterns

Slab 7b's three differentiators (Executive Summary §"What makes this special") drive the innovation list. Risk-mitigation register catalogs the foreseen failure modes per pattern.

### IR-1: Substrate-as-floor-not-ceiling discipline

Slab 7b's primary risk-pattern is the temptation to amend the Slab 7a substrate when a specialist body doesn't fit cleanly. The risk: substrate-amendment-creep degrades the substrate-as-floor invariant; future slabs inherit a substrate of accumulated per-specialist exceptions.

**Mitigation (R8 Winston-amendment):** three-mechanism enforcement, not principle-only:
- (a) **Enumerated frozen-paths list** at `state/config/substrate-frozen-paths.yaml` (FR108-derived; R6 substrate-as-floor closed-list);
- (b) **CI workflow** `.github/workflows/substrate-frozen-paths-check.yml` (NFR-I13 binding) blocks PRs that touch frozen paths absent a `substrate-amendment:` trailer + Marcus-Winston co-sign;
- (c) **CODEOWNERS** entry routing frozen-path edits to architect review.

Every Slab 7b story carries an explicit AC: "if this body requires substrate amendment, file a Slab-7a-defect story; do NOT amend substrate inline." Reviewer enforces. Substrate amendments require party-mode consensus + Slab 7a regression party-mode round.

### IR-2: BMB sanctum alignment as default (not as cleanup)

The risk: SG-4 enforcement is added as a per-story AC but reviewers + dev agents grow lax over the wave; some stories merge with silent-omission and the structural parity-test catches them only at Slab 7b close, requiring massive late-stage remediation.

**Mitigation (R8 Murat-amendment, two-layer):** **Detective control** — FR101 parity-test catches divergence (parses YAML, asserts required keys, derives `sanctum_path`, cold-activation smoke). **Preventive control** — NFR-I9 CI gate (bound to `.github/workflows/specialist-parity.yml`) blocks the PR. Per-PR feedback loop; not a Slab-close-time discovery. SG-4 is operator-non-negotiable; no waivers. Two-layer mitigation is correct for silent-drift risk class.

### IR-3: Five-API live-binding without CI-runaway

The risk: five live APIs (gamma / kling / elevenlabs / wondercraft / dan-api-tbd) each have potential to leak live calls into CI; a single misconfigured `pytest.mark.llm_live` decorator in a port-shape PR could ship daily live-API runs.

**Mitigation (R8 Winston + Murat amendment):** sandbox-AC validator enforces dev-agent ACs use shipped-Python-deps (httpx / SDK) with `pytest.skip(...)` policy; live evidence operator-gated. (Inherited from Slab 7a CLAUDE.md governance.) Primary detection (R7 NFR-CG13): `scripts/utilities/detect_live_api_in_tests.py` AST-scans `tests/` for forbidden import set (httpx.Client / requests.Session / openai.OpenAI / anthropic.Anthropic / boto3.client / live-API patterns) outside `@pytest.mark.llm_live` decorator scope; runs as pre-merge GitHub Action via `.github/workflows/detect-live-api-in-tests.yml`. Forbidden-import inventory at `docs/dev-guide/composition-test-forbidden-imports.json`. Defense-in-depth (secondary): pytest structural test as backup runtime check.

### IR-4: Cache-hit-rate harness ≥85% across ten LLM specialists

The risk: cache-hit-rate harness is parametric but if one specialist's prompt structure is unstable (e.g., timestamp injection, non-deterministic ordering), the harness either fails (<85%) or produces misleading "≥85%" by sampling stable subset. The first-tracked-trial-2 cost overrun could trace to a single specialist's unstable prompt.

**Mitigation (R8 Murat-amendment, NFR cross-reference):** T4 cache-determinism harness (NFR-T11a, ≤45s/specialist; runs nightly OR green-light cadence — NOT in dev-cycle inner loop) asserts cache-hit-rate ≥85% per LLM specialist on second run; failure is CI-blocking. **Threshold rationale:** 85% = empirical floor from Slab 2a.2 Irene Pass-2 trials (median[2:] = 95.33% achieved, +35.33pp slack vs floor); below 85% indicates non-deterministic prompt construction (jitter, timestamp, RNG leak). Per-specialist median[2:] reporting (Slab 2a.2 precedent). Per-specialist regression: any drop below 80% triggers fixture-staleness investigation. Compositor (Class D2) uses pipeline-determinism harness instead (≥99% rate; NFR-T11a / FR99).

### IR-5: Compositor sanctum-alignment exception risk

The risk: Compositor's option-b documented exception is the precedent for "deterministic specialists don't need BMB pattern." If accepted carelessly, future deterministic specialists (e.g., a hypothetical "Linter" or "PackHasher" agent) inherit the exception without explicit rationale — silent drift toward two-tier mental model returns.

**Mitigation:** option-b exception requires explicit rationale BLOCK in SKILL.md with the specific kind of determinism justifying it. Reviewer flags any future "X is also deterministic so option-b" without per-instance rationale. Sanctum-alignment matrix at `docs/dev-guide/specialist-sanctum-alignment-matrix.md` records every exception's rationale verbatim.

### IR-6: Per-specialist parity-test suite explosion

The risk: 11 per-specialist parity-test files, each with multiple assertions, plus inherited 33-row mapping-checklist parity tests, plus inherited Composition Spec invariant tests, plus per-PR chain-tests — total parity-test surface could exceed reasonable wall-clock budget; CI run-time degrades.

**Mitigation (R8 Murat-amendment, NFR cross-reference):** NFR-T12 sets parity-suite wall-clock ceiling at ≤120s aggregate on `ubuntu-latest` (2 vCPU, 7GB), fail-CI on regression. Per-specialist budget = 120s ÷ 11 = ~10.9s/specialist headroom; T-tier authors use that as the design floor. **Tripwire:** if a single specialist's parity case exceeds 15s, escalate (likely fixture-fetch leak, not parity logic). Parametrize where possible; consolidate redundant assertions; class-shaped templates (NFR-I12) prevent per-specialist drift.

### IR-7: Mapping-checklist regression risk during dev

The risk: as Slab 7b body activations land, a recently-✅ row may regress to ⚠️ if a downstream activation breaks an upstream contract. The mapping checklist re-audit happens at Slab 7b close, by which time mid-flight regressions are buried in commit history.

**Mitigation:** `tests/parity/test_mapping_checklist_status.py` runs at every PR merge gate (NFR-I11). Per-PR feedback loop. Mid-flight regression = blocks merge.

### IR-8: Trial-2 readiness audit creep

The risk: Slab 7b close-criteria include "trial-2 launchable"; the team discovers at close that some non-Slab-7b prerequisite (e.g., an operator-side credential refresh, a manifest version bump, a Box Drive sync) is missing. Slab 7b close blocks on a non-Slab-7b deliverable.

**Mitigation:** trial-2 launch checklist is a separate artifact (`_bmad-output/implementation-artifacts/trial-2-launch-checklist.md`) maintained from Slab 7a close. Slab 7b is responsible for the body-activation half; operator owns the trial-launch half. Slab 7b close-criteria refer to body-activation completeness, not trial-launchability.

### IR-9: Per-specialist sandbox-AC inventory entry adequacy

The risk: the 5-entry sandbox-AC inventory is named (gamma / kling / elevenlabs / wondercraft / dan-api-tbd), but the actual content of each entry may be incomplete — e.g., httpx-based dev-agent AC examples missing for one specialist. Story opens, dev agent has no scaffold, story drags.

**Mitigation:** sandbox-AC inventory PR review = party-mode round (per Slab 7a precedent). Inventory PR landing is the precondition; "landed" means "reviewed + complete + actionable per-specialist scaffold." Class-C / Class-D Slab 7b stories don't open until inventory PR is party-mode-ratified.

---

## Project Scoping & Phased Development

### Risk-Based Scoping (SR-T1..SR-S4)

Risk register driving phasing decisions. SR-prefix codes: T (technical), R (requirement-shape), C (compliance), S (schedule). **R8 amendment expanded register from 12 to 18 risks** to cover dev-time analogs of Quinn's R3 FM-23..26 + cost-anomaly-pre-launch + Codex-availability + fixture-refresh-cadence drift.

**SR-T1: Five-API CI-runaway.** Mitigated by IR-3 above. Phase: sandbox-AC inventory PR landing is hard precondition for API-bound Class-C/C+/D opens.
**SR-T2: Cache-hit-rate harness instability.** Mitigated by IR-4 above. Phase: per-specialist harness configuration lands at story-open T1; tuning during dev.
**SR-T3: Compositor pipeline-determinism vs cache-hit-rate confusion.** Compositor (Class D2) doesn't fit cache-hit-rate harness (no LLM call); replaced by pipeline-determinism harness. Phase: harness type ratified at scaffold-v0.2-D2 contract (FR111).
**SR-T4: Per-specialist sanctum-alignment scaffold-v0.2 force application.** scaffold-v0.2 `--force` mid-Slab-7b risks operator-edit clobber. Mitigated by Story 26-5 (scaffold preservation; backlog) but 26-5 is not a Slab 7b precondition. Phase: per-specialist `--force` audited at story-open; operator-edit accumulation logged.
**SR-T5: Mapping-checklist row regression.** Mitigated by IR-7 + NFR-I11 per-PR enforcement. Phase: per-PR enforcement.
**SR-T6 (R8 John NEW; cost-anomaly pre-launch).** Risk: between Slab 7b close and trial-2 launch, dry-run cost projection exceeds BS-3 ceiling; trial-2 cannot launch as-planned. Mitigated by trial-2 cost-projection dry-run (Journey 5). Phase: pre-trial-2 dry-run; if exceeded, four named remediation paths (scope-cut / budget-exception / trial-redesign / Slab-7c precondition).
**SR-T7 (R8 Murat NEW; cross-specialist parity matrix on every wave merge).** Risk: FM-23 inter-specialist contract drift introduced at dev time when one specialist's wave lands without re-running downstream parity tests. Mitigated by per-wave-merge cross-specialist parity matrix run (NFR-I10 chain-tests for every Class-A/B/C/C+/D activation pair that consume each other's outputs). Phase: per-wave merge gate.
**SR-T8 (R8 Murat NEW; cold-activation smoke required in T-tier).** Risk: FM-25 sanctum-parity-green-cold-activation-red — parity tests pass in warm CI but cold-start activation fails. Mitigated by per-specialist cold-activation smoke required in T-tier authoring (R3 FR101 amended contract, R3 A-11). Phase: per-PR cold-activation smoke green required.
**SR-T9 (R8 John NEW; Codex availability fluctuation).** Risk: NFR-CG17 binds Codex per-class allocation; if Codex billing changes, model deprecates, or service availability fluctuates mid-Slab-7b, NFR-CG17 becomes unenforceable. Mitigation: name fallback substrate (Anthropic API direct, local Ollama for non-prod); Codex deployment health-check at every wave-open. Phase: ongoing.
**SR-R1: Per-specialist body-shape ambiguity.** The frontmatter `slab7bSpecialistRoster.specialists.{name}.actBodyShape` is the canonical body-shape designation. Disagreement = re-open party-mode at story-authoring time (not relitigated mid-dev).
**SR-R2: Sanctum-alignment exception scope-creep.** Mitigated by IR-5 + NFR-I12 class-shaped templates. Phase: per-exception rationale enforced at SKILL.md against closed allowlist (FR109).
**SR-R3 (R8 Mary clarification): Tracy classification ambiguity.** Tracy is **LLM-only for Pass-2 enrichment** (no third-party API binding); Sandbox-AC inventory does NOT include Tracy. The **Class C+ classification** reflects sidecar-emission responsibility (4-file BMB pattern), NOT API integration. Phase: confirmed at Tracy port-shape Story 7b.X-tracy.
**SR-R4: Dan API binding TBD.** Dan currently sidecar-only; API binding for `_act` body is `dan-api-tbd`. Choice (LLM-only vs third-party API) resolved at Story 7b.X-dan (Class D1 greenfield).
**SR-R5 (R8 Winston restated): Compositor activation per Class-D2 sidecar variant** (canonical pattern per R5/R6 amendments). Sidecar carries operational metadata (contract, version, chronology of pipeline-runs, access-boundaries); persona-shaped continuity does not apply. NO per-story option-a/option-b re-decision; deviation requires party-mode consensus + governance-JSON entry. Residual risk: **sidecar-IPC contract drift** (mitigated by frozen JSON schema at `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` + FR111 + frozen-paths list).
**SR-C1: Sandbox-AC inventory PR adequacy.** Mitigated by IR-9. Phase: party-mode-ratified before API-bound Class-C/C+/D opens.
**SR-C2: SG-4 silent-omission risk.** Mitigated by NFR-I9 + IR-2 two-layer (preventive + detective). Phase: per-PR enforcement.
**SR-S1: Trial-2 launch window slip.** Slab 7b close + dry-run window targets ≤6 weeks (R3 amendment); if real, escalate to operator at Slab 7b retrospective.
**SR-S2 (R8 Murat NEW; credential-redaction lint).** Risk: fixture credentials baked into VCR cassettes leak real keys at commit time. Mitigation: `scripts/utilities/redact_credentials_in_cassettes.py` AST/regex lint on cassette commits; CI hook at `.github/workflows/cassette-redaction.yml`. Phase: per-PR enforcement.
**SR-S3 (R8 John NEW; credential drift between Slab close and trial-2 launch).** Risk: provider/model/sanctum/retrieval credentials rotate between slab close and trial-2 launch; trial-2 fails on environmental drift, misattributed to slab regression (FM-26). Mitigation: per-API credential-rotation register surfaced in `next-session-start-here.md` (NFR-CG19); credential-freshness check at trial-2 T-0; pre-trial-2 credentialed-path smoke test required.
**SR-S4 (R8 John NEW; fixture-refresh-cadence drift).** Risk: NFR-OD5 commits to fixture refresh, but if refresh cadence isn't wave-anchored, fixtures go stale between Slab 7b close and trial-2 → fallback-to-stub territory returns. Mitigation: fixture-refresh dry-run mode (NFR-OD5) + cadence wave-anchoring (refresh required at every Class-C/C+ port-shape close + at Slab 7b close).

### Phased Wave Plan (proposed; finalized at `bmad-create-epics-and-stories`)

**Wave 0 (precondition; pre-7b; governance-budgeted, NOT K-counted per R8 Mary-amendment).** Foundational artifacts (FR108-FR112) + sandbox-AC inventory PR (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-if-API). Operator-gated review. Hard precondition for Wave 1+. Atomic merge required (single load-bearing commit per R8 Winston-amendment).

**Wave 0.5 (R8 John-amendment; Codex deployment per-class allocation).** Codex agent deployment + smoke-tested per NFR-CG17 binding allocation (Class-C/C+ port-shape stories + sandbox-AC inventory PR + per-story bmad-code-review). Verifies SBC-#8 enforceability before Wave 1 opens. May fold into Wave 0 atomic merge per architect preference.

**Wave 1 — Class A hardening (3 stories; can parallelize).** Texas hardening + Quinn-R hardening + Vera hardening. K-aggregate ~6K LOC + ~75 tests. Single-gate per story (per Slab 7a precedent for hardening-shape). Depends on Wave 0 atomic merge.

**Wave 2 — Class B Irene Pass-1 + Class C+ Tracy (2 stories; serial — Tracy is Pass-2 enrichment, runs after Pass-1 lands).** **R8 Mary + Amelia amendment:** Tracy is **Class C+** (port-shape WITH sidecar emission), bundled per Mary's lean (port-shape + sidecar in one story; ~3.3K LOC + ~36 tests).
- 2a. Irene Pass-1 activation refresh (Class B; mirrors Pass-2 shape; single-gate).
- 2b. Tracy port-shape + sidecar creation (**Class C+**; LLM-only; single-gate per Slab 2b.1 TEMPLATE; sidecar 4-file BMB pattern bundled). **Wave-1 scaffold-amortization tripwire (R8 Murat-amendment):** if Tracy comes in >2.7K LOC, escalate — scaffold isn't amortizing and K-aggregate is at risk.

**Wave 3 — Class C API-bound port-shapes (3 stories; can parallelize after Wave 0 + Wave 1).** Gary + Kira + Enrique. Each single-gate per Slab 2b.1 TEMPLATE. Sandbox-AC inventory entries consumed.

**Wave 4 — Class C remaining (1 story).** Wanda port-shape onto scaffold (single-gate).

**Wave 5 — Class D greenfield (2 stories; can parallelize after Waves 1-3 *closed* per R8 Winston-amendment, not merely in-progress).** Dan (Class D1 LLM-greenfield) + Compositor (Class D2 pipeline-greenfield, Class-D2 sidecar variant per R5/R6 amendments). Each single-gate (greenfield-uplift K-target).

**Wave 6 — Slab 7b integration + parity suite + closeout (1 story; strict-last; dual-gate).** Mirrors Slab 7a Story 7a.8: integration parity test suite + retrospective + sprint-status update + deferred-inventory amendment + operator Gate-2 evidence ceremony. Five-API live-binding smoke runs at Wave 6 (operator-gated AC-*-B style).

**Total Slab 7b proposed:** 12 stories + Wave 0 + Wave 0.5 governance deliverables (13-14 deliverables total). ~24–30 K-units at K-floor 1.3–1.5× per R3 amendment. Wall-clock target: ~3–4 weeks (NEW CYCLE acceleration; Slab 7a precedent achieved 1-day vs 7–9-week plan via Codex sub-agent parallelism).

### MVP Exit Gate (R8 John-amendment, smaller-scope)

**MVP exit (smallest thing that validates the assumption):** Trial-2 reaches **G2 cleanly** with **real content from at least nine of eleven specialists** (≥3 per class). No fixture-stub fallback. No silent gate-bypass. **SG-1, SG-2, SG-3 all green** (SG-4 verified at Slab 7b close, not MVP exit).

**Slab 7b close gate (full-scope validation):** Trial-2 reaches **G3 cleanly** with real content from **all eleven specialists** (cascade reading per R8 Mary clarification — visible-content surfaces from the nine standalone-row specialists Texas/Irene/Vera/Gary/Kira/Wanda/Enrique/Dan/Compositor PLUS Pass-2-internal contributions from Wanda + Tracy verifiable via cascade audit logs). No fixture-stub fallback. No silent gate-bypass. No mapping-checklist regression. **SG-1/SG-2/SG-3/SG-4 all green.**

Two gates, not one — MVP exit fails fast on the activation-correctness assumption (G2 with 9-of-11); full-Slab close validates the eleven-specialist + G3 + cascade-reading + sanctum-alignment claims jointly.

---

## Architectural Decisions

These ADRs extend the migration architecture's D1–D13 decisions (per `architecture-langchain-langgraph-migration.md`). Slab 7b adds D14+ in the body-activation series. **R9 amendments** consolidated D14/D17/D20 to align with R5/R6/R7/R8 ratifications + added D21/D22/D23.

**D14 (Slab 7b; R9 Winston-amendment): Five-class specialist shape taxonomy (six bins).** The eleven-specialist roster decomposes into five classes / six bins by body-activation work-shape:
- **Class A** — LLM specialists, sanctum-aligned, scope = rubric / contract-enforcement hardening (Texas / Quinn-R / Vera).
- **Class B** — LLM specialists, sanctum-aligned, scope = activation refresh mirroring existing Pass shape (Irene Pass-1).
- **Class C** — LLM specialists, sanctum-aligned, scope = port-shape (passthrough → live LLM/API), API-bound (Gary / Kira / Wanda / Enrique).
- **Class C+** — LLM specialists, sanctum-aligned, scope = port-shape WITH sidecar emission (Tracy; one-tier K-bump per Mary-amendment).
- **Class D1** — LLM-greenfield specialists, sanctum-aligned, scope = create-from-scratch with LLM body (Dan).
- **Class D2** — Pipeline-greenfield specialists, **Class-D2 sidecar variant** (canonical, NOT exception per R5/R6/R8 amendments), scope = deterministic assembly pipeline; sidecar carries operational metadata (contract / version / chronology of pipeline-runs / access-boundaries) — NOT persona-shaped continuity (Compositor).

Each class has its own K-target, gate-mode designation, and reviewer-burden profile. Frontmatter `slab7bSpecialistRoster` is the canonical mapping. Mapping-checklist `class` column accepts exactly these six values; validator rejects any other token.

**D15 (Slab 7b): SG-4 sanctum alignment per body-activation story.** New standing guardrail. Every body-activation story carries SKILL.md alignment-or-exception AC. Structural parity-test (FR101) enforces. Cora-sidecar precedent for documented-exception path. R9: option-b exceptions are limited to closed allowlist `docs/dev-guide/sanctum-exception-categories.json` (FR109).

**D16 (Slab 7b): Sandbox-AC inventory PR as hard precondition for API-bound Class-C/C+/D opens.** Slab 7a named the 5 entries; Slab 7b lands the inventory PR. Inventory PR is party-mode-ratified before any API-bound Class-C/C+/D dev opens. R8 Amelia scope-amendment: Tracy + Dan-without-API exempt.

**D17 (Slab 7b; R9 Winston-amendment): Two distinct determinism harnesses.** Determinism is enforced by two distinct harnesses, not one:
- **H-Cache** — cache-hit-rate ≥85% (median[2:], N=10) across the 10 LLM specialists (Class A + B + C + C+ + D1, ex-Compositor). Per-specialist measurement; aggregate gate per NFR-T11a.
- **H-Pipeline** — byte-stable output for non-LLM specialists (Class D2) given fixed input + frozen substrate paths. Compositor is the seed case. Bytes-identical for `sync-visuals`; field-masked-hash for `assembly-guide` (modulo declared-nondeterministic fields). ≥99% rate target. Failure is hard-block; no flake tolerance.

CI surfaces both metrics independently. Green H-Cache does NOT satisfy H-Pipeline and vice versa.

**D18 (Slab 7b): Per-specialist parity-test suite at `tests/parity/per_specialist/`.** One test file per specialist following NFR-I10 naming convention `test_<specialist_name>_activation_contract.py`; asserts body-substrate end-to-end chain. Per R5 Winston + Murat amendments: class-shaped (six templates A/B/C/C+/D1/D2), not uniform. Extends Slab 7a parity-test suite at `tests/parity/`.

**D19 (Slab 7b): Mapping-checklist row-status invariant enforced per-PR.** `tests/parity/test_mapping_checklist_status.py` bound to `.github/workflows/mapping-checklist.yml` runs at every PR merge gate. Mid-flight regression = blocks merge.

**D20 (Slab 7b; R9 Winston-amendment): Compositor as Class-D2 exemplar (NOT exception).** Sanctum alignment (PERSONA.md + INDEX.md) is REQUIRED for Classes A/B/C/C+/D1, **structurally inapplicable for Class D2**. Class D2 is a first-class taxonomy bin, not an exception. Compositor is the seed exemplar; future D2 specialists declare `class: D2` in the mapping checklist and SG-4 validator skips sanctum-presence checks for that row. **No precedent citation, no waiver, no exception register entry required.** "Compositor exception" terminology retired from PRD prose; replaced with "Compositor (Class D2 exemplar)" or equivalent.

**D21 (Slab 7b; R9 Winston NEW): Codex deployment as scope-binding commitment #8.** Codex (operator-side authoring assistant) is scope-bound to Slab 7b per R2 + R7 NFR-CG17. Per-class authoring assignments are normative, not advisory: Class-C/C+ port-shape stories (Tracy/Gary/Kira/Wanda/Enrique = 5 stories) + sandbox-AC inventory PR + per-story `bmad-code-review` execute via Codex; Class-A/B/D1/D2 + Wave-6 integration story remain Claude-authored. Wave 0.5 (R8 amendment) is the deployment-verification vehicle. Removing or substantially altering Codex deployment requires party-mode consensus + governance-JSON entry. A Codex-authored deliverable that violates its class contract = hard-block at relevant gate.

**D22 (Slab 7b; R9 Winston NEW): Substrate-as-floor invariant + frozen-path immutability.** Per R6 FR113 + R7 NFR-I13, the substrate paths frozen at Slab 7a close (enumerated in §IR-1: `_bmad/memory/shared/`, `app/marcus/orchestrator/dispatch_adapter.py:81`-region, conversation-persistence layer, per-slide subgraph skeleton, vocabulary registry, gate-runner substrate, SG-1..SG-4 contract files) plus the Marcus boundary contract constitute a **floor**, not a starting point. Slab 7b specialists may **read** from frozen paths and **add** new specialist-scoped paths; they may **not** mutate frozen-path contents. SG-1 violation if breached. CI workflow `.github/workflows/substrate-frozen-paths-check.yml` (NFR-I13 binding) blocks PRs touching frozen paths absent `substrate-amendment:` trailer + Marcus-Winston co-sign + CODEOWNERS approval. Subsequent edits require explicit slab-bump (Slab 7b only adds activation; Slab 8+ may extend).

**D23 (Slab 7b; R9 Winston NEW): Foundational-artifacts precondition gate.** Per R5 + R6 FR108-FR112 + R7 NFR-CG18, five foundational artifacts (`bmb-sanctum-alignment-checklist.md`, `sanctum-exception-categories.json`, `operator-control-parity-template.md`, `scaffold-v0.2-D2-pipeline.yaml`, `skills/bmad-agent-cora/SKILL.md` §"Sanctum exception" anchor) MUST exist and pass self-test BEFORE any Wave 1 Class-A specialist story opens. Precondition gate, not parallel work item. Wave 0 authors all five; Wave 1 cannot open until §Foundational-Artifacts gate passes. Failure mode: any Wave-1 story opened before precondition is structurally void and must be reverted.

---

## Codex Deployment Plan (carry-forward from Slab 7a)

Codex deployment continues from Slab 7a; Slab 7b's parallel-authoring assignments:

- **Codex-authored:** Class-C port-shape stories (Tracy / Gary / Kira / Wanda / Enrique) — five stories. Slab 2b.1 TEMPLATE-style port-shape work is Codex's strongest pattern (precedent: Slab 2a.2 Irene + Slab 2a.4 Texas).
- **Claude-authored + Codex-reviewed:** Class A hardening stories (Texas / Quinn-R / Vera) — three stories. Hardening-shape work requires careful rubric-semantic interpretation; Claude's strength.
- **Claude-authored:** Class B Irene Pass-1 (one story; mirrors Pass-2 shape; Claude continuity from Slab 2a.2 era).
- **Claude-authored + Codex-reviewed:** Class D greenfield stories (Dan / Compositor) — two stories. Greenfield work requires `bmad-create-specialist` workflow + scaffold-v0.2 + sanctum-creation; Claude's strength.
- **Codex-authored:** sandbox-AC inventory PR (Wave 0 precondition). Five-entry inventory authoring is template-shaped.
- **Codex-reviewed:** every Slab 7b story `bmad-code-review` (per Slab 7a deployment precedent).
- **Claude-authored:** Slab 7b integration + parity-test suite + closeout (Wave 6; mirrors Slab 7a Story 7a.8).

---

## Polish-Pass Notes (Step 11 + R9 Polish)

### R9 Paige polish-pass (final)

- **TOC + Quick Reference anchor additions:** added anchors for §Foundational Artifacts (R5/R6), Wave 0.5 Codex Deployment (R7/R8), Class C+ / D1 / D2 specialist tiers (R7/R8), MVP Exit Gate vs Slab Close Gate (R8), SR-T6..T9 + SR-S2..S4 expanded register (R8). Quick Reference Wave-table extended with Wave 0.5 row.
- **Acronym glossary extension** (14 → 19 entries): added T1-T5 tier abbreviations (T1 unit, T2 fixture-replay, T3 canary, T4 cache-determinism, T5 live), MVP-EG (MVP Exit Gate per R8), SCG (Slab Close Gate per R8), Codex (Wave 0.5 specialist), Port-shape (load-bearing interface contract).
- **Cross-link tightening:** Slab 7a parity-test references tightened to test-path glob (`tests/parity/test_*` post-7a.4); §Predecessor-Slab Status block updated to "Slab 7a closed at Story 7a.8 + Epic Close" (per commit `95c81b0`).
- **§Domain Requirements 3-subsection split (R5-deferred):** **DEFERRED again** to post-MVP polish PR. Filed in `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons under "Slab 7b PRD §Domain Requirements 3-subsection split (post-MVP polish PR; re-deferred R9 due to absorbed amendments warmth)."

### R1-R8 polish anchors

- **TOC + section ordering:** mirrors Slab 7a PRD structure for sibling-coherence; cold-pickup operator can navigate Slab 7a and Slab 7b PRDs interchangeably.
- **Operator Non-Negotiables callout:** SG-1/2/3 inherited verbatim from Slab 7a; SG-4 added inline + R1-amended (closed allowlist + value-validation parity-test + scaffold-by-default + party-mode consensus on option-b).
- **Quick Reference anchors:** Slab 7b adds sanctum-alignment matrix anchor + foundational-artifacts anchor + Wave 0.5 row.
- **Cross-link audit:** every reference to Slab 7a artifacts (substrate, parity tests, decisions D1–D13) verified against current `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md` and `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md`.
- **Mapping-checklist row-status table:** verified against `slab-7-legacy-migrated-mapping-checklist.md` 34-atomic-row inventory (33 prompt sections + sub-step §05.5); ~28 row improvements claimed; 6 deferred rows accounted for in Growth Features section + SR register.
- **Per-specialist Slab-7b shape designation:** verified against Slab 7a frontmatter `slab7bSpecialistRoster` block (operator-ratified 2026-04-28); R8 Tracy class label updated to C+ (port-shape with sidecar emission); reproduced in this PRD's frontmatter for cold-pickup.

### Final scope-floor confirmation (R9; party-mode consensus across 4 voices)

- **SG-1 (specialist roster floor 11):** intact across R1–R8 amendments; Codex addition is additive (Wave 0.5 deployment-verification), not roster expansion. **Floor held.**
- **SG-2 (33-row mapping-checklist floor; ~28 improvements + 6 deferred):** intact; deferred rows explicitly accounted for in Growth Features + SR register; no row dropped. **Floor held.**
- **SG-3 (Composition Spec invariants §3.1/§3.5/§3.6/§6/§9/§10/§11):** intact; foundational-artifacts cross-links REFERENCE the spec, do not redefine it; no §11 trigger activation. **Floor held.**
- **SG-4 (BMB sanctum alignment per body):** intact; Class-D2 sidecar variant (Compositor) is structural variant, not silent omission; closed allowlist (FR109) + party-mode-ratified option-b prevents drift. **Floor held.**
- **Acceptance-clause ordering** (R3 Quinn): A-13 load-bearing on A-8..A-12 + 11-specialist load-bearing fixture; preamble note in §Success Criteria preserved.

**All four standing guardrails green across all R1-R9 amendments. No scope creep observed.**

### Round-by-round amendment record

| Round | Section | Outcome | Key amendments |
|---|---|---|---|
| R1 | Operator Non-Negotiables (SG-1..SG-4) | RATIFIED-WITH-AMENDMENTS (4/4) | SG-4 closed allowlist + value-validation parity-test + scaffold-by-default + party-mode option-b |
| R2 | Executive Summary + Project Classification | RATIFIED-WITH-AMENDMENTS (4/4) | Opening rewrite (JTBD + emotional hook); class taxonomy split D→D1/D2; Tracy promoted C+; "two mental models forever" restored verbatim; substrate-paths-frozen + Marcus boundary frozen; Codex deployment binding |
| R3 | Success Criteria | RATIFIED-WITH-AMENDMENTS (4/4) | T-tier split (T1/T2/T3/T4-cache-determinism/T5-live); K-aggregate restate (24-30 K-units at 1.3-1.5×); FM-11 heuristic; FM-21 decision tree; A-9 file-path table; A-13 11-specialist load-bearing fixture; FM-23/24/25/26 added |
| R4 | User Journeys | RATIFIED-WITH-AMENDMENTS (4/4) | Journey 1 polyphony rewrite + scar-tissue cautious + Tuesday's-class beat; Journey 2 substrate-remembered parable; Journey 3 dashboard reassurance + cold-session-operator primary; Journey 4 cost-arithmetic teaching + load-bearing payoff; Journey 5 cost-anomaly-pre-launch fork added |
| R5 | Domain Requirements | RATIFIED-WITH-AMENDMENTS (4/4) | Marcus-as-substrate phrasing fix; deferred count alignment 5→6; per-specialist parity-test class-shaped (5 templates); BMB checklist canonical (vs scaffold-v0.2-backlog historical); Cora concrete paste-pattern; foundational-artifacts list (5 items); Class-D2 sidecar variant for Compositor |
| R6 | Functional Requirements (FR88-FR113) | RATIFIED-WITH-AMENDMENTS (4/4) | FR99 Class-D2 restated; FR101 R1-contract restated; FR104-FR107 reframed as substrate-consumption-extended; FR108-FR112 foundational-artifacts; FR113 Marcus boundary frozen |
| R7 | Non-Functional Requirements | RATIFIED-WITH-AMENDMENTS (4/4) | NFR-T9..T12 R3-tier split; NFR-CG12..CG20 (incl. CG17 Codex commitment, CG18 foundational-artifacts precondition, CG19 credential rotation, CG20 rate-limit budget); NFR-I9..I13 (CI workflow binding, class-shaped, substrate-as-floor); NFR-OD3..OD6 |
| R8 | Innovation + Scoping | RATIFIED-WITH-AMENDMENTS (4/4) | IR-1/2/3/4/6 NFR cross-references; SR register expanded 12→18; MVP exit gate cut to G2+9-of-11 + Slab close gate full-G3+11; Wave 0.5 Codex deployment; Tracy bundled Class C+ in Wave 2 |
| R9 | ADRs + Codex Deployment + Polish + Step 12 close | RATIFIED-WITH-AMENDMENTS-AND-CLOSE (4/4) | D14 5-class taxonomy; D17 split harness; D20 Class-D2 exemplar (not exception); D21/D22/D23 added; TOC + glossary extended; final scope-floor confirmation |

---

## References

- **Slab 7a PRD (sibling baseline):** `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md`
- **Slab 7a Epic + 8 stories:** `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md`
- **Slab 7a retrospective:** `_bmad-output/implementation-artifacts/slab-7a-retrospective.md`
- **Mapping checklist (33 rows):** `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`
- **Sprint status:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
- **Deferred inventory:** `_bmad-output/planning-artifacts/deferred-inventory.md`
- **Composition Spec (SG-3):** `docs/dev-guide/composition-specification.md`
- **Migration story governance:** `docs/dev-guide/migration-story-governance.json`
- **Slab 2a.2 Irene Pass-2 (Class B precedent):** `_bmad-output/implementation-artifacts/migration-2a-2-irene-pass2-9-node-scaffold.md`
- **Slab 2a.4 Texas migration (option-a sanctum precedent):** `_bmad-output/implementation-artifacts/migration-2a-4-texas-sanctum.md` (path inferred; verify at story-open)
- **Epic 26 BMB migration (Marcus / Irene / Dan precedents):** `_bmad-output/implementation-artifacts/sprint-status.yaml` §"prd_epic_26_*"
- **Cora sidecar (option-b documented-exception precedent):** `skills/bmad-agent-cora/SKILL.md` + `_bmad/memory/bmad-agent-cora/`
- **CLAUDE.md governance:** `CLAUDE.md` (sandbox-AC + gate-mode governance + sprint governance)
- **Project memory — SG-4 rule:** `~/.claude/projects/.../memory/project_slab_7b_skill_md_sanctum_alignment.md`

---

**End of pre-filled PRD draft. Operator review pending; party-mode ratification per remaining-step → next-action loop.**
