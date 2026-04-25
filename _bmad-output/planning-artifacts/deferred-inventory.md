# Deferred Inventory — Standing Index

**Purpose:** canonical register of every deferred epic, deferred story, and named-but-not-filed follow-on across the project. Single source of truth consulted at:

1. **Every Epic retrospective** — per [CLAUDE.md §Pipeline lockstep regime](../../CLAUDE.md) and §Deferred inventory governance, the retrospective MUST review this inventory against the closing Epic's new substrate / evidence / learnings; flag now-ready-to-reactivate entries to the next sprint-planning round.
2. **Every session hot-start** — `next-session-start-here.md` surfaces the inventory counts so the operator sees "don't overlook" context every session open.
3. **Story authoring** — when a new story spec names a follow-on (e.g., "15-1-lite-irene is a fast-follow after this story"), the author adds the follow-on to §Named-But-Not-Filed Follow-Ons below.

**Maintenance:** update at (a) each Epic retrospective close, (b) each story closure that names a new follow-on, (c) any session-wrapup where the operator flags a new deferred item, (d) each forward-port pass on the hybrid migration branch (see §Forward-Port Deferred below). Last refreshed: **2026-04-24** (upstream severance + Slab 2 roster reconciliation).

---

## Backlog Epics — Full Scope Deferred

| Epic | Focus | Stories | Story count | Reactivation trigger |
|---|---|---|---|---|
| **Epic 15** | Learning & Compound Intelligence — convert tracked runs into organizational intelligence | 15-1, 15-2, 15-3, 15-4, 15-5, 15-6, 15-7 | 7 | "At least one tracked trial run completed" (hard dependency per epic seed). 15-1-lite-marcus (Epic 33 meta-test) unlocks the chain's first link via its learning-event ledger infrastructure. 15-2 (retrospective artifact) is the natural next link once the ledger exists. |
| **Epic 16** | Bounded Autonomy Expansion — Marcus autonomous routing on routine decisions | 16-1, 16-2, 16-3, 16-4, 16-5 | 5 | Depends on Epic 15 evidence base for autonomous-routing calibration. |
| **Epic 17** | Research & Reference Services — related-resources + citation injection + hypothesis research | 17-1, 17-2, 17-3, 17-4, 17-5 | 5 | No explicit trigger named; appears to be operator-priority-driven. Re-evaluate at Epic 15/16 retrospectives. |
| **Epic 18** | Additional Assets & Workflow Families — cases, quizzes, discussions, handouts, podcasts, diagrams, workflow-family framework | 18-1, 18-2, 18-3, 18-4, 18-5, 18-6, 18-7 | 7 | **18-7 gates all others** (implementation framework must land first). Trigger for 18-7: operator-priority decision on new content type. Note: 18-5 (podcasts) + 18-6 (infographics) are "new pack types" per [Pipeline Manifest Regime §Pack Versioning Policy](../../docs/dev-guide/pipeline-manifest-regime.md#pack-versioning-policy) — NOT v5 of narrated-lesson; they ship as new families. |
| **Post-M5 Greenfield Specialists** (hybrid migration) | Specialists named in Epic 2b roster that have no skill directory on disk and cannot be migrated (Mike, Eli, Enrique, Mira, Sally, Kim; Paige if scoped as runtime specialist). Empty sidecar stubs exist under `_bmad/memory/<name>-sidecar/` but no code, no prompts, no references. | one per specialist as need materializes (6–7 total) | 6–7 | **Hybrid migration M5 closure.** Generated directly on hybrid via `bmad-create-specialist` (the generator validated in Slab 2c.1) when the operational need for each specialist becomes concrete. No migration; pure greenfield on the migrated platform. See [`slab-2-roster-reconciliation.md §Category E`](slab-2-roster-reconciliation.md) for roster detail. |

**Total deferred-epic story count: 30–31 stories across 5 epic slots.**

---

## Deferred Stories Within Active / Done Epics

| Story | Epic | Status | Reactivation trigger (from sprint-status comments) |
|---|---|---|---|
| **20c-4** Master Arc Composition | Epic 20c (in-progress) | Deferred | "When complexity justifies" — return after profile-driven runs validate clustering. Wave 2 Deferred block in sprint-status.yaml. |
| **20c-5** Pax Agent | Epic 20c (in-progress) | Deferred | Same Wave 2 Deferred gating. |
| **20c-6** Lens Capability | Epic 20c (in-progress) | Deferred | Same Wave 2 Deferred gating; "start as capability" framing. |
| **20a-5** Exemplar Library | Epic 20a (done) | Ready-for-dev with reactivation-choice flag | "Unblocked; re-evaluate against deferred/reactivation choice" per 2026-04-15 decision. Currently staged but not pulled — awaits operator priority call. |

**Reactivation criteria (Epic 20c-native, from sprint-status.yaml line 111-115):** After 20c-14 (E2E validation) reveals specific gaps in clustering quality, reactivate the relevant deferred story to address it. 2026-04-15 decision: 23-1 reactivated as the next implementation target (unlocks the broadest downstream path with less speculation than 20c-4/5/6).

**Total deferred-story count in active epics: 4 stories.**

---

## Named-But-Not-Filed Follow-Ons

Follow-on stories named in existing specs or retrospectives but not yet filed as sprint-status entries. Filed only when their parent story closes and/or the trigger fires.

| Follow-on | Parent story | Condition | Trigger |
|---|---|---|---|
| **Audra + Cora dissolution** (migration branch) | 2026-04-24 operator ratification during Slab 2 roster reconciliation | LangGraph CI stack (import-linter 3 contracts + scaffold-conformance framework + shape-pin tests + LangSmith tracing) covers the code-invariant functions these two agents performed on primary. Session-ritual functions covered by existing BMAD session-START/WRAPUP protocols. | **No migration work.** Leave [`skills/bmad-agent-audra/`](../../skills/bmad-agent-audra/) + [`skills/bmad-agent-cora/`](../../skills/bmad-agent-cora/) as historical-archive directories on hybrid. Cora's `/harmonize` + session-triage CLI wrapper remains scoped to Slab 4 Epic E4 (Lockstep + Gates + Cora) but as a CLI/hook, NOT as a LangGraph runtime node. Audra is fully dissolved — no post-M5 resurrection planned. See [`slab-2-roster-reconciliation.md §Category D`](slab-2-roster-reconciliation.md). |
| **Dev-coherence report generator (hybrid-native Audra replacement)** | 2026-04-24 Audra/Cora dissolution ratification | Audra's historical output under [`reports/dev-coherence/`](../../reports/dev-coherence/) is archived (54 inherited session dirs) but nothing writes new entries post-severance. Audra is dissolved per Category D; hybrid needs a deterministic CLI to populate new timestamped entries at session-WRAPUP. | File as a ~1–2pt story under **Slab 4 Epic E4** (Lockstep + Gates + Cora — natural home since it already scopes Cora's CLI wrapper). Shape: `scripts/governance/dev_coherence_report.py` dumps import-linter output + scaffold-conformance pytest summary + ruff clean check + optional LangSmith trace sample into `reports/dev-coherence/<ts>/`. Optionally wire into a session-WRAPUP hook in `.claude/settings.json` for auto-run. Replaces Audra's conversational interface with deterministic CI output per Option D philosophy. |
| ~~**Cache-hit-rate harness re-enablement (FR54)**~~ | ~~Slab 1 Story 1.6 shipped the harness at `tests/end_to_end/test_cache_hit_rate_baseline.py` with `pytest.skip(...)`. The FR54 M1 acceptance bar (≥60% cache hit rate on second invocation) was deferred per 2026-04-22 set-level consensus because Slab 1 ships passthrough specialists (zero LLM calls → undefined cache rate).~~ | ~~First Slab 2 specialist that lands a real LLM call at its `act` node.~~ | **CLOSED 2026-04-25 at Story 2a.2 T7 waypoint.** Harness retargeted at Irene Pass 2; measured 95.33% median cache-hit-rate (vs 60% floor; +35.33pp slack). M1 ACCEPT-WITH-GAP fully retired. See `m1-acceptance-evidence-pack.md` §M1 Cache-Hit-Rate Clause for evidence block + Story 2a.2 Completion Notes for full measurement protocol. |
| **15-1-lite-irene** | 15-1-lite-marcus | Epic 33 meta-test validates the substrate catches new contracts on Marcus | File when 15-1-lite-marcus closes CLEAN-CLOSE-META-TEST-PASSED. Extends learning-event capture to Irene's Gates. |
| **15-1-lite-gary** | 15-1-lite-marcus | Same as above | File when 15-1-lite-marcus closes CLEAN-CLOSE-META-TEST-PASSED. Extends learning-event capture to Dan/Gary's Gates. |
| **v4.3 substrate extension** | Epic 33 retrospective | No current trigger; mechanism ready per Q1 parameterized-version-hook | File when operator identifies the first Tier-2 pack change per [Pipeline Manifest Regime §Pack Versioning Policy Tier 2](../../docs/dev-guide/pipeline-manifest-regime.md#tier-2--minor-v42--v43-new-pack-file-v42-preserved-for-audit). Ships as `scripts/generators/v43/` sibling + manifest entries with `pack_version: "v4.3"`. |
| **Full Epic 15 chain (15-2 through 15-7)** | 15-1-lite-marcus + first tracked trial run | First tracked trial run completes AND 15-1-lite-marcus's compressed ledger proves viable | Sequence per Epic 15 seed: 15-2 retrospective artifact → 15-3 upstream feedback routing → 15-4 synergy scorecard → 15-5 pattern condensation → 15-6 workflow-family ledger → 15-7 calibration harness. Each story already specced in [epics.md §Epic 15](epics.md). |
| **33-1a follow-on: §4.55 body polish** | 33-1a | Dev agent self-review identifies prose imprecision on §4.55 lock-semantic body | File only if 33-1a dev agent flags ambiguity; otherwise no story needed. |
| **Epic 33 retrospective follow-ons** | Epic 33 retrospective (required) | Retrospective identifies substrate work not yet scoped | TBD per retrospective outcome. Epic 33 spec names "multi-version v4.3 + 15-1-lite-irene/gary fan-outs" as expected candidates. |
| **PR-TR (Trial Resumption capability) + trial-branch discipline + config-reload refinement** | 2026-04-19 session — operator-surfaced during trial-prep discussion | First tracked trial generates evidence of which discipline details matter most | File post-trial-#1. Scope at ~2pt single-gate: (a) PR-TR capability = deterministic pause-hash capture + resumption-delta diff + Green/Yellow/Red classification, additive to existing PR-* scaffold; (b) CREED standing-order refinement for config-reload-on-resumption; (c) hot-start banner template for `trial/<RUN_ID>` branch + clean-working-tree invariant counter. Parked per evidence-driven-before-spec discipline. |
| **Texas best-available-medium selection** | 2026-04-19 trial run — operator-surfaced during Step 02 source map | First trial run completes and operator confirms multi-format source sets are a recurring pattern | Texas currently requires explicit role assignment per source; no logic to auto-select among PDF vs DOCX vs MD for the same content. Desired: given a candidate set of formats for the same SME content, Texas picks the highest-fidelity available format as primary and demotes others to validation automatically. Natural home: Epic 27 follow-on (Texas intake expansion) or Epic 15 learning-intelligence track. ~2-3pt. |
| **Step 02A prior-run directives as defaults** | 2026-04-19 trial run — operator-surfaced during Step 02A poll | Hardwire before next run | Marcus currently surfaces prior-run operator-directives.md on request only. Desired: Step 02A always scans prior bundles for the most recent operator-directives.md for the same lesson_slug, presents them as named defaults with source attribution (run_id + date), and requires explicit accept/modify/replace before writing. Eliminates re-entry burden on resumed or repeated runs. Natural home: Marcus PR-* capability or Step 02A pack procedure amendment. ~1pt. |

| **HUD per-step expandable summaries** | 2026-04-19 trial run — operator-surfaced during Step 03 hold | Post-trial, once `--watch` live HUD lands | Each pipeline step in the HUD should have an expandable section showing real-time summary of content captured and locked at that step (e.g. Step 01 shows preflight receipt, Step 02 shows source authority map, Step 03 shows extraction quality report). Operator can inspect any completed step without leaving the HUD. Natural home: Epic 22 (Storyboard & Review Adaptation) or a new HUD-enhancement story. ~3-5pt. |
| **Converge `cluster-plan.yaml` and `segment-manifest.yaml` to single pre-Gary artifact** | trial-fix-g1.5-cluster-plan-artifact story — party-mode 2026-04-19 | Post first full trial with clusters | Currently two separate files serve the same G1.5 gate at different pipeline stages (Pass 1 structural / Pass 2 full). Desired: single artifact shape emitted at Pass 1 time, enriched (not replaced) by Pass 2 with narration-time fields. Gate mode (`structural` vs `full`) determined by which fields are populated, not by filename. Eliminates dual-artifact ambiguity and simplifies gate runner. ~2pt architecture story. |

| **Production intake_callable for run_4a / Step 04A** | 2026-04-19 trial run — Step 04A programmatic loop not wired for production HIL | Before next production trial run | `Facade.run_4a()` requires an `intake_callable` connecting the 4A loop to Maya's UI. Currently only test stubs / `run_maya_walkthrough` fixture harness exist. Production wiring would drive `run_4a()` from real operator ratification input per unit. Natural home: Marcus CM capability or new PR-4A production-readiness capability. ~3pt single-gate. |

| **Irene Pass 2 authoring template / schema contract** | 2026-04-20 trial run B-Run §08 — operator-flagged after validator remediation across two full sessions | Before next Pass 2 production run | Irene's Pass 2 work product required exceptional post-hoc repair before `validate-irene-pass2-handoff.py` returned STATUS: pass. The validator's strict contract (exact behavioral-intent form, 4+-char token-level narration pre-seeding, absolute path matching, valid `visual_detail_load` values, bridge-cadence mechanics, cluster arc integrity rules) is implicit in validator code and not surfaced to Irene at composition time. Required: a structured Irene Pass 2 authoring template that encodes the validator's implicit contract as explicit schema constraints and inline authoring guidance — so segment-manifest.yaml and pass2-envelope.json can be produced in one pass without post-hoc debugging. HIGH priority: single highest-friction step in the production pipeline observed this trial. Natural home: Epic 20c or new Epic 34 (Irene authoring contract). ~3-5pt. |

| **Theatrical-direction synthesis (Tier 1 + Tier 2)** | 2026-04-21 trial run B §11 — operator explored dials-only ceiling and asked whether per-segment feature specification is part of a "theatrical direction"–capable approach | After C1-M1-PRES-20260419B synthesis output is evaluated; operator decides whether dials-only expressiveness is sufficient or whether escalation is warranted | Current trial is **dials-only amp-up** on `eleven_multilingual_v2` with uniform voice_settings across 14 segments (only `speed` varies per segment via `pace_variability` client-side nudge). This reveals the ceiling of single-parameter-set synthesis. Two escalation tiers for future trials: **Tier 1 — per-segment voice_settings.** Extend `segment-manifest.yaml` and `pass2-envelope.json` to carry per-segment `stability` / `style` / `similarity_boost` hints. Irene authors them alongside narration (e.g., heavy reflection segment → higher stability + lower style; excited call-to-action → lower stability + higher style). Runner builds a per-segment `voice_settings` payload instead of reusing one envelope. Works on v2 model; no API/model change required. Estimated ~70% of theatrical value at ~20% of complexity. ~3-5pt. **Tier 2 — model swap + audio-tag authoring.** Add model selection capability (`eleven_v3` / `v3-alpha` / future tag-capable models) to `voice-selection.json`. Irene Pass 2 authors inline audio tags (`[laughs] [whispers] [shouts] [sighs] [pause]`) at per-segment granularity. Runner detects model capability and passes tags through. Combined with Tier 1 this delivers full director-mode control: per-segment voice parameters + per-utterance performance markers. ~5-8pt. Natural home: new Epic (Director-Mode Synthesis) or Epic 24 extension. Parent-story decision trigger: operator reviews trial B audio output, declares "dials-only ceiling is too flat for category X content." Until then, dials-only remains the cost-effective default. |

| **Generator auto-emit pyproject.toml C3 ignore_imports row (2a.1 follow-on defect)** | Story 2a.2 T2 dev-agent discovery (party-mode 2026-04-24 ratified) | Generator at `skills/bmad_create_specialist/scripts/generate.py` validates that emitted `app/specialists/<name>/graph.py` imports `resume_from_verdict` (line 220–223) but does NOT auto-update `pyproject.toml`'s C3 `ignore_imports` list. Every Slab-2+ specialist migration (2a.3 Kira, 2a.4 Texas, 13× Slab-2b inheritors) must manually add `app.specialists.<name>.graph -> app.gates.resume_api` or import-linter C3 breaks at T2. Status quo carries 14 manual edits + flakiness vector if any dev agent forgets. | **2a.1 follow-on defect, ~2pt, MUST land before Slab 2b.1 TEMPLATE opens.** Extend generator to atomically append the ignore_imports row with a generated comment marker (`# generated by bmad-create-specialist for <name>`) for visual segregation; idempotent (detect "already present" and no-op); add a regression test asserting "for every emitted graph.py, pyproject.toml ignore_imports contains the matching row." Murat (b)-preferred path; Winston path-2; Paige A12 procedural-coupling category. T2 party-mode 2026-04-24 binding. |
| **Replace cache_prefix payload-carrier hack with first-class RunState envelope field (Slab 3 prerequisite)** | Story 2a.2 T4 act-body authoring (party-mode 2026-04-24 ratified) | RunState has no envelope field at Slab 1 substrate. Story 2a.2's `_act` node receives the Pass-2 envelope payload encoded as sorted-keys canonical JSON in `state.cache_state.cache_prefix` (overloads documented field role "Stable prefix derived from sanctum + model + manifest version"). Documented bounded-scope decision; clean substitute requires extending RunState. | **Slab 3 follow-on, ~2-3pt.** Add `RunState.specialist_envelope: SpecialistEnvelope \| None` (or per-specialist sub-state schema). Migrate `_act` to read from the new field; remove cache_prefix overload; update Story 2a.2 spec § Envelope-Carrier-Hack note to "retired". Murat envelope-hack-receipts binding from T4 review (2026-04-24). |
| **Cold-cache nonce-variant test for AC-D measurement realism** (`2a.2-followon-cold-cache-nonce-variant`) | Story 2a.2 T7 cache-hit-rate measurement (party-mode 2026-04-24 Murat T7 binding) | The 2a.2 AC-D run reported inv 1 = 95.33% (already warm) instead of cold-cache 0% because the AC-B live-LLM test fired ~5 min prior with byte-identical prompt prefix, pre-warming OpenAI's cache. The MF1 disposition rule (median[2:] ≥ 60%) is spec-compliant in this scenario by design, but the harness cannot distinguish "cache works" from "cache was already warm and we got lucky." | **TEA follow-on, ~0.5pt, ~$0.03/run.** Add a regression-test variant to `tests/end_to_end/test_cache_hit_rate_baseline.py` that injects `uuid4()` into a non-cached suffix region for inv 1, asserts `cache_read_input_tokens == 0`, then confirms inv 2-10 land at expected ≥60% hit-rate against the non-noisy prefix. Fire-trigger: next time we touch FR54 harness OR retrospective notices a cache-behavior question. Murat T7 review (2026-04-24); explicitly NOT blocking 2a.2 close. |
| **`--require-live-llm` pytest flag wiring** (`2a.2-followon-require-live-llm-flag`) | Story 2a.2 T8 dual-path regression review (party-mode 2026-04-24 Murat T8 binding) | SF3 anti-erosion guard half-shipped at 2a.2: (a) `@pytest.mark.llm_live` auto-skip on placeholder/unset OPENAI_API_KEY is shipped + verified at T8b. Half (b) — operator-facing `--require-live-llm` flag that would FAIL (not skip) if any `@llm_live` test would auto-skip — is unwired. Auto-skip is the load-bearing erosion guard; the flag is operator ergonomics for "debug live path; hard failures, not skips." | **TEA follow-on, ~0.5pt.** Wire the `--require-live-llm` CLI flag in `tests/conftest.py` per the SF3 spec: when set, any `@pytest.mark.llm_live` test that would auto-skip raises a typed failure instead. Operator-pre-merge hook OR a Completion-Notes paste workflow invokes `--require-live-llm`; CI (no real key) does NOT. Prevents silent-skip erosion if @llm_live test coverage grows over Slab 2b. Fire-trigger: when any new @llm_live test lands AND operator wants pre-merge confidence beyond per-story T8 dual-path verification. Murat T8 review (2026-04-24); explicitly NOT blocking 2a.2 close. |

**Total named follow-ons: 17.** (Four new entries added 2026-04-24 from Story 2a.2 T2 + T4 + T7 + T8 party-mode waypoint reviews.)

---

## Wave / Phase Deferreds (Epic-Group Gating)

### Cluster Intelligence Wave 2 (Epic 19-24 + 20c)

Per sprint-status.yaml Wave 2 Deferred block: 20c-4, 20c-5, 20c-6 deferred because profile runs will expose gaps more effectively than isolated A/B trials. Return when creative control iteration stabilizes. **Profile runs serve as the integration test that A/B trials were designed to be.**

### Wave 3 — Codify (epic 23)

- **23-2 G4 Gate Extension** — "codify what good looks like" (waits for Wave 2A + 2B to stabilize)
- **23-3 Bridge Cadence** — finalize stitching rules (same gate)

Wave 3 reactivation trigger: clustering + creative control stabilizes through profile-driven runs.

### Wave 4 — Downstream (epic 22, 24)

- 22-2 Storyboard B + Script
- 22-3 Flat-Play Preview
- 22-4 Generation Script & Publish
- 24-1 Assembly Contract
- 24-2 Descript Guide
- 24-3 ElevenLabs Short Segments

Reactivation trigger: Irene output stabilizes (Wave 3 close).

### Wave 5 — Capstone (epic 24)

- **24-4 Regression Suite** — full end-to-end validation. Depends on all prior waves.

---

## Forward-Port Deferred (hybrid-only, migration branch)

**Context:** the hybrid clone's `dev/langchain-langgraph-foundation` branch runs under FR60 forward-port freeze (ACTIVE since 2026-04-22). Wholesale `git merge upstream/master` is off-policy; per-capability forward-port through the [migration-guide §8 reconciliation checklist](../../docs/dev-guide/langgraph-migration-guide.md) is the convergence path. The inventory below tracks upstream capabilities that SHIPPED on primary after the hybrid branched but are NOT being forward-ported wholesale because the migration's LangChain/LangGraph re-platform IS the replacement.

Last refreshed: **2026-04-23** after Phase 1 forward-port (commit `6364f14`) on the hybrid branch.

### CLASS A — Pre-migration orchestrator work (not forward-ported; migration replaces)

| Upstream file / capability | Migration replacement | Reactivation trigger |
|---|---|---|
| `marcus/orchestrator/workflow_runner.py` | `app.manifest.compiler.compile()` + LangGraph `StateGraph` | Never — migration replaces this runtime path entirely. Closed. |
| `marcus/orchestrator/fanout.py` + `trial_smoke_harness.py` | Slab 3 Marcus orchestration + dispatch graph | Closed by Slab 3 completion. |
| `marcus/facade.py` upstream mutations | `app.marcus.*` (Slab 3) | Closed by Slab 3 completion. |
| `skills/bmad-agent-marcus/scripts/*` | `app.marcus.*` + `app.specialists.marcus.*` (Slab 3) | Closed by Slab 3 completion. |
| `scripts/generators/v42/templates/*.j2` | Migration's prompt-pack shape authored into `app.manifest` (no separate generator in migration) | Closed — pack-version bumps on primary do not cross the forward-port freeze. |
| `docs/workflow/production-prompt-pack-v4.2-*.md` upstream mutations | Migrated manifest at `state/config/pipeline-manifest.yaml` owns v4.2 topology; primary pack docs are pre-migration reference | Closed. |
| `state/config/pipeline-manifest.yaml` upstream content | Migration shape from Slab 1 Story 1.6 owns this file on this branch | Closed — upstream content edits do not cross the freeze. |

### CLASS B — New capabilities deferred to their slab-opening stories

| Upstream capability | Files | Target slab | Reconciliation checklist |
|---|---|---|---|
| **PR-R Marcus dispatch contract + boundary retrofits** | `marcus/dispatch/{__init__,contract}.py`, `scripts/marcus_capabilities/pr_rc.py`, `scripts/validators/check_dispatch_registry_lockstep.py`, `skills/bmad-agent-marcus/references/dispatch-registry.yaml`, `tests/marcus_dispatch/*`, `docs/dev-guide/how-to-add-a-dispatch-edge.md` | **Slab 3 Story 3.x** | Apply full migration-guide §8 reconciliation: Pydantic-v2 four-file-lockstep + dispatch-registry-as-manifest-companion + L1-validator-as-library-function + receipt-shape sanctum-fingerprint |
| **Consensus retrieval adapter (Story 27-2.5)** | `skills/bmad-agent-texas/scripts/retrieval/consensus_provider.py`, `tests/test_retrieval_consensus_provider.py`, `tests/test_retrieval_cross_validation.py`, `tests/test_retrieval_dispatcher.py`, `docs/dev-guide/how-to-add-a-retrieval-provider.md` updates | **Slab 2 Epic 2b (Texas)** | Port into `app.specialists.texas` per scaffold-conformance framework (tests/integration/scaffold_conformance/) |
| **Irene retrieval intake + Pass 2 authoring template (Story 7-1-irene-pass-2)** | `marcus/irene/{__init__,intake}.py`, `skills/bmad-agent-content-creator/references/{pass-2-authoring-template,retrieval-intake-contract}.md`, `state/config/schemas/{irene-retrieval-intake,segment-manifest}.schema.json`, `scripts/validators/pass_2_emission_lint.py`, `tests/irene/test_segment_manifest_schema.py` | **Slab 2 Epic 2b (Irene)** | Port into `app.specialists.irene` with scaffold-conformance check |
| **Evidence-bolster control surface** | `_bmad-output/implementation-artifacts/evidence-bolster-control-surface.md` + schemas/tests | **Slab 2 Epic 2b** | Port within Texas + Irene specialist scope |
| **PDG-3 flake-detection gate (CI infra)** | `scripts/ci/run_flake_gate.py`, `.github/workflows/pdg-flake-gate.yml` | **Slab 2 open (revisit)** | Orthogonal to orchestrator choice; decide at Slab 2 open whether the gate's assumptions still match the migration's test surface |

### CLASS D — Upstream deletions NOT adopted (hybrid keeps)

| Upstream deletion | Hybrid posture | Reason |
|---|---|---|
| `bmad-session-protocol-session-START.md` + `session-WRAPUP.md` | Hybrid keeps | Still canonical for hybrid session protocol; upstream relocated to Cora references. |
| `SESSION-HANDOFF.md` | Hybrid keeps | Hybrid lifecycle still uses it. |
| `next-session-start-here.md` | Hybrid keeps (intentionally gitignored line 96) | Hybrid identity — session guidance is per-clone, not synced with primary. |

### Refresh cadence

This section is refreshed at each forward-port pass (phases named in the session wrap-up notes). Entries marked "Closed" above do not need revisiting unless architecture amendment changes the migration's replacement strategy.

---

## Hygiene / Documentation Deferred (non-story)

| Item | Scope | Reason deferred | Trigger to pick up |
|---|---|---|---|
| **Closed-epic absolute-path rewrite (old repo name)** | ~30 closed-story specs under [_bmad-output/implementation-artifacts/](../implementation-artifacts/) for Epics 19–25 + 33, plus older `_bmad-output/planning-artifacts/` docs, plus some planning research artifacts. Content cross-links other artifacts via absolute `C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\...` URLs. After the 2026-04-22 local folder rename to `course-DEV-IDE-with-AGENTS-hybrid`, those prefixes no longer resolve on disk, though filename segments are still navigable. | Bulk-rewriting closed/frozen story specs for path cosmetics would pollute git history with a large no-behavior commit across epics that are already green. Operational paths were already handled in commit `fe0c314` (.vscode/tasks.json made `${workspaceFolder}`-relative, .pre-commit-config.yaml header renamed). Remaining are documentation-identity only. | (a) Any time a closed story is reopened for a material edit — sweep its stale absolute links in the same patch. (b) At an Epic retrospective where Audra flags unresolved-reference drift on a closed-artifact doc. (c) Operator-priority call during a session with idle capacity. Recommended approach when triggered: a single scripted sweep of `_bmad-output/implementation-artifacts/` replacing `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/` → repo-relative, on a dedicated hygiene branch, with before/after diff review. |

---

## Inventory Summary

| Category | Count | Reactivation posture |
|---|---|---|
| Backlog epics | 4 (Epic 15, 16, 17, 18) | Triggered by Epic 33 meta-test + trial-run evidence |
| Deferred stories in active epics | 4 (20c-4/5/6, 20a-5) | Triggered by profile-driven run gaps |
| Named-but-not-filed follow-ons | 13 | Triggered by parent-story closure + condition |
| Wave 3/4/5 stories (partially deferred via gating) | ~10 | Triggered by prior-wave stabilization |

**Near-term candidates (post-Epic-33):**
1. 15-1-lite-irene + 15-1-lite-gary (immediately after 15-1-lite-marcus meta-test passes)
2. 20a-5 Exemplar Library reactivation (operator priority call)
3. Full Epic 15 chain (after first tracked trial run)
4. Epic 18-7 workflow-family framework (if operator prioritizes new content types)

---

## Governance Hooks (where this inventory gets consulted)

- **[CLAUDE.md §Pipeline lockstep regime](../../CLAUDE.md)** — binds retrospective runs to consult this inventory during "Next Epic Preparation" phase per the `bmad-retrospective` workflow §Two-part format line 15.
- **[next-session-start-here.md](../../next-session-start-here.md)** — standing hot-start line surfaces inventory counts.
- **Each story spec** — when authoring a new story that names a follow-on, the author adds the entry to §Named-But-Not-Filed Follow-Ons above.

---

## References

- [_bmad-output/planning-artifacts/epics.md](epics.md) — per-Epic scope authority; backlog epics declare their stories + ACs there.
- [_bmad-output/implementation-artifacts/sprint-status.yaml](../implementation-artifacts/sprint-status.yaml) — canonical story state; comments carry Wave-group deferral rationale.
- [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) — **different surface**: tracks deferred G6 code-review FINDINGS per story, not deferred stories themselves. Relevant at retrospectives as a sibling input.
- [docs/dev-guide/pipeline-manifest-regime.md §Pack Versioning Policy](../../docs/dev-guide/pipeline-manifest-regime.md#pack-versioning-policy) — relevant for Epic 18 new-pack-type framing.
- [CLAUDE.md](../../CLAUDE.md) — governance umbrella; names the retrospective + session-start consultation requirement.
