---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories']
inputDocuments:
  - '_bmad-output/planning-artifacts/prd-perception-reading-path-fidelity.md'
  - '_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md'
authority: 'beta-phase-1-closure-ratification-2026-06-19.md §7'
tier: 'Tier-3 (major) — party green-light required BEFORE dev'
---

# Perception + Reading-Path Narrative-Grounding Restoration — Epic Breakdown

## Overview

Decomposes `prd-perception-reading-path-fidelity.md` into one epic (**Epic P2**) with four stories (**P2-1 … P2-4**), per the ratified forward path (`beta-phase-1-closure-ratification-2026-06-19.md §7`). MVP closes the **grounding leg** (confident-wrong regression); Growth closes the **reading-path leg**. P2 is **Tier-3** — party-mode green-light + major pack version bump before dev.

## Requirements Inventory

### Functional Requirements
- **Perception (PER):** FR1 perceive PNG→`PerceptionArtifact`; FR2 per-slide addressable; FR3 per-claim provenance; FR4 confidence/coverage states + explicit uncovered; FR5 envelope-contribution-as-authority (disk audit-only); FR6 vision-failure taxonomy, no silent brief-fallback.
- **Narration Grounding (GRD):** FR7 Pass-2 grounds on `PerceptionArtifact` (sole authority); FR8 Vera demoted to secondary expectation signal; FR9 references ⊆ perceived elements + numerics match.
- **Fidelity Detection (DET):** FR10 fail-loud Class-A on orphan reference; FR11 fail-loud on contradicted numeric; FR12 typed fidelity-bearing-vs-non-visual classifier; FR13 low-confidence/not-covered ≠ conformance; FR14 detector consumes only the artifact (no independent inference); FR15 verdict names slide+ref, pauses + blocks publish; FR16 deterministic + no-retry.
- **Reading-Path (RDP — Growth):** FR17 classify scan pattern from artifact (closed enum); FR18 verify-node conformance, fail loud; FR19 repertoire incl. triptych/image-dominant-first; FR20 per-cluster cadence coupling.
- **Governance & Verification (GOV):** FR21 RED-first harness vs committed $5.2T evidence; FR22 sized real green corpus + seeded-defect set (specificity+recall); FR23 silent-drift canary; FR24 auditable verdict + evidence.

### NonFunctional Requirements
- NFR1 detector deterministic; NFR2 artifact repeatable within per-field comparator tolerances; NFR3 FP rate 0 on green corpus (merge gate); NFR4 no silent degrade-to-brief + failure attribution; NFR5 vision cost/latency bounded+observed; NFR6 verdict auditable; NFR7 silent-drift canary out-of-CI non-blocking; NFR8 single-source via import-linter contract; NFR9 four-file lockstep + provenance schema-excluded; NFR10 detector tests offline on frozen fixtures only.

### Additional Requirements (from PRD §Domain + §AI-Pipeline)
- Tier-3 pipeline-lockstep regime + party green-light before dev; standalone `vision` manifest node owning the provider dep; thin pinned-endpoint (httpx) client preferred over vendor SDK; two-lane CI (detector blocking / vision quarantined); re-golden protocol + flake budget; migration sandbox-AC (in-process dep + `pytest.skip` on unreachable).

## FR Coverage Map
- FR10–FR16, FR21–FR22, FR24 → **P2-1** (detector + RED-first harness + audit).
- FR1–FR6, FR23 → **P2-2** (vision node + `PerceptionArtifact` producer + full schema richness + canary).
- FR7–FR9 → **P2-3** (Pass-2 consumption — the regression fix).
- FR17–FR20 → **P2-4** (reading-path — Growth).
- NFR1/3/6/8(partial)/10 → P2-1; NFR2/4/5/7/8/9 → P2-2; (grounding NFRs) → P2-3; (reading-path) → P2-4.

## Epic List

### Epic P2: Perception + Reading-Path Narrative-Grounding Restoration & Enhancement
Restore narration that speaks to what is actually on the rendered slide, in scan order, and **prove it** with a fail-loud fidelity detector. Closes the disaster-level confident-wrong regression (grounding leg — MVP: P2-1/2/3) and the lost reading-path scan-order grammar (Growth: P2-4).
**FRs covered:** FR1–FR24. **Tier-3.** **Authority:** ratification §7.

**Standalone/dependency note:** Epic P2 is self-contained on the current production substrate. Internal story order is **fixed by RED-first discipline** (P2-1 → P2-2 → P2-3 → P2-4); see each story's dependency line.

---

## Epic P2: Perception + Reading-Path Narrative-Grounding Restoration & Enhancement

Restore perception-grounded, scan-order-faithful narration; install a permanent fail-loud fidelity guardrail.

### Story P2-1: Fail-loud fidelity detector — RED-first vs the $5.2T evidence
As the **production pipeline (and the operator who trusts it)**,
I want a **deterministic, fail-loud fidelity detector that compares narration against a perceived-slide artifact and fails Class-A on any fidelity-bearing reference not present in perception**,
So that **confident-wrong narration can never again pass as "error-free."**

**Gate mode:** dual. **Sequence:** FIRST; lands RED before P2-2/P2-3 exist.
**Dependency:** introduces the **`PerceptionArtifact` *consumed contract* (minimal schema)** + a hand-authored frozen fixture for slide-01 (perceived: `$4.5T` callouts + building photo). It does NOT depend on the vision node (P2-2 builds the producer). This split is what makes RED-first possible — **to be ratified at the green-light.**

**Acceptance Criteria:**
- **Given** the committed un-repaired narration for slide-01 ("$5.2T line + bars") and a frozen `PerceptionArtifact` fixture showing the rendered reality ($4.5T callouts + photo), **When** the detector runs, **Then** it raises a **Class-A** fidelity failure naming slide-01 and the orphan reference — proving RED *before* any repair. (FR10, FR21)
- **Given** a known-good fidelity fixture (narration ⊆ perceived elements), **When** the detector runs, **Then** it returns clean — two-sided, not a stuck alarm. (FR22)
- **Given** the sized real green corpus (≥20–30 faithful slides from committed runs) and a seeded-defect set (figure-swap, element-drop, magnitude-drift), **When** the detector runs, **Then** FP rate = 0 on the green corpus AND it RED-flags every seeded defect. (FR22, NFR3)
- **Given** a narrated numeric that contradicts a perceived figure, **When** the detector runs, **Then** it fails loud. (FR11)
- **Given** references that are non-visual (prior-slide callbacks, abstract concepts), **When** the detector classifies references, **Then** only fidelity-bearing references are checked for orphan status (typed classifier). (FR12)
- **Given** a perceived element marked `low-confidence`/`not-covered`, **When** the detector evaluates it, **Then** it is treated as non-conformance, never a clean pass. (FR13)
- **Given** the detector module, **When** import-linter runs, **Then** the detector imports neither the vision provider nor a PNG path — only the `PerceptionArtifact` schema; a contradiction test proves the verdict tracks the artifact, not pixels; a second-inference injection makes the invariant test RED. (FR14, NFR8)
- **Given** repeated runs on identical inputs, **When** the detector runs, **Then** the verdict is identical (deterministic) and no retry occurs. (FR16, NFR1)
- **Given** a fidelity failure, **When** it surfaces at the gate, **Then** the run pauses, publish is blocked, and the verdict + evidence (perceived elements vs narrated refs) is auditable. (FR15, FR24, NFR6)
- **Given** detector tests, **When** CI runs, **Then** they consume only frozen fixtures (no live vision); detector tests are blocking. (NFR10)

### Story P2-2: PNG-grounded PerceptionArtifact + standalone vision node
As the **pipeline**,
I want a **standalone vision node that perceives each rendered PNG into a per-slide-addressable `PerceptionArtifact` (with provenance + confidence/coverage), published as the authoritative envelope contribution**,
So that **downstream consumers ground on what the audience actually sees, from a single source of truth.**

**Gate mode:** dual. **Sequence:** after P2-1; turns the detector partly green (real artifacts replace the fixture). **Schema-shape story** (scaffold + Pydantic-v2 14-idiom + four-file lockstep).

**Acceptance Criteria:**
- **Given** a rendered slide PNG, **When** the vision node runs, **Then** it emits a `PerceptionArtifact` of perceived visual elements, positions, and numeric figures. (FR1)
- **Given** a multi-slide deck, **When** artifacts are emitted, **Then** they are per-slide-addressable by slide identity, and uncovered slides carry an explicit `not-covered` state — never a missing key. (FR2, FR4)
- **Given** each visual claim, **Then** it carries provenance (`png-grounded | brief-expectation | not-covered`) and a confidence/coverage state. (FR3, FR4)
- **Given** the artifact, **When** published, **Then** it is the authoritative production-envelope contribution (threaded via ProjectionSpec/A-R3); any disk copy is audit-only. (FR5)
- **Given** a vision-step failure (raised/timeout, low-confidence, schema-invalid), **When** it occurs, **Then** it routes per the seam taxonomy with failure attribution, never a silent fallback to the brief. (FR6, NFR4)
- **Given** the schema, **When** the JSON Schema is emitted, **Then** `provenance` is excluded (`Field(exclude=True)+SkipJsonSchema`) and confidence/coverage are closed-enum triple-layer-red-rejected; the four-file lockstep test asserts the deliberate model-vs-schema divergence (not naive equality). (NFR9)
- **Given** identical PNG input at the pinned model, **When** the golden-image repeatability test runs, **Then** the artifact is stable within the per-field comparator tolerances (bbox IoU≥θ, element-set Jaccard=1.0, figure/text edit-distance≤d). (NFR2)
- **Given** the provider dependency, **When** dev-agent ACs run, **Then** live round-trip ACs invoke it in-process (no CLI) with `pytest.skip` on unreachable; golden tests run offline against a recorded fixture. (NFR5, Additional Reqs)
- **Given** the silent-drift canary, **When** scheduled out-of-CI, **Then** it re-runs the golden image, diffs per the comparator table, and alerts on drift even under an unchanged model id (non-blocking). (FR23, NFR7)

### Story P2-3: Pass-2 consumes perceived visuals — the regression fix
As **Irene (Pass-2)**,
I want to **ground narration on the perceived `PerceptionArtifact` instead of the slide brief**,
So that **narration describes the rendered slide and the detector goes regression-green.**

**Gate mode:** dual. **Sequence:** after P2-2; turns the detector **fully** regression-green. Edit sites: `app/specialists/irene/graph.py` (`_assemble_pass_2_prompt`, `_slide_roster`), `irene/authoring/pass_2_template.py`.

**Acceptance Criteria:**
- **Given** the `PerceptionArtifact` for a slide, **When** Pass-2 assembles its prompt, **Then** it grounds on perceived elements as the sole visual authority; Vera's brief-derived perception is available only as a secondary expectation signal. (FR7, FR8)
- **Given** assembled narration, **When** the detector runs, **Then** references ⊆ perceived elements and narrated numerics match perceived figures (slide-01 narrates $4.5T, not $5.2T). (FR9)
- **Given** the repaired pipeline on the frozen corpus + ≥1 held-out slide, **When** a full run completes, **Then** the detector is GREEN (regression-green); the §6 DoD grounding-leg strike + cross-trial harvest is the merge gate. (regression-green; §6)

### Story P2-4: Reading-path native rewrite + verify-node conformance (Growth)
As **Irene**,
I want to **classify each rendered slide's scan pattern from the `PerceptionArtifact` and narrate in that order, with a conformance check**,
So that **narration follows the natural scan of the slide (the founding operator complaint).**

**Gate mode:** single. **Sequence:** last / Growth. Native rewrite — do NOT re-absorb upstream code.

**Acceptance Criteria:**
- **Given** a `PerceptionArtifact`, **When** classified, **Then** the slide receives a `reading_path` drawn from a closed enum (incl. patterns beyond the original 7 where evidence shows mis-fit: triptych, image-dominant-first). (FR17, FR19)
- **Given** narration + the slide's `reading_path`, **When** the verify node runs, **Then** it checks narration order against the scan order and fails loud on non-conformance. (FR18)
- **Given** a held-out set with expected scan order (worked-examples/operator-derived), **Then** narration order matches `reading_path` order on ≥80% of slides (placeholder — finalize in the P2-4 spec); an anti-vacuity fixture (naive-default order known-wrong) must produce the correct non-default order. (correctness bar, not presence)
- **Given** per-cluster cadence, **When** narration is generated, **Then** cadence couples to the scan pattern. (FR20)
- On close: reading-path deferred-leg struck + combined arc entry fully struck; last asterisk dropped. (§6)
