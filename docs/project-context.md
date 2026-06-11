# Project Context: Multi-Agent Course Content Production System

**Project Name:** course-DEV-IDE-with-AGENTS
**Phase:** 4-Implementation — **Epic 34 §02A Downstream-Consumer Schema Coherence FULLY COMPLETE 2026-05-22** (7/7 stories DONE; Trial-3 attempt-3 launch UNBLOCKED on fully harmonized substrate). Slab 7c brownfield migration completed 2026-05-07 (36/36 dev-stories DONE) and Epic 34 then harmonized the §02A composer ↔ Texas wrangler integration boundary that Trial-3 attempt-2 surfaced as silently broken.
**Architecture Status:** 15 legacy epics complete + Epics 19-21 done + Epic 34 done, **125 FRs + 13 FR-E34**, Complete Architecture with Interstitial Cluster Extensions; **Hybrid LangChain/LangGraph re-platform: SHIPPED at M5 (2026-04-27) + Slab 7c orchestrational tail FULLY COMPLETE 2026-05-07 + Epic 34 §02A coherence FULLY COMPLETE 2026-05-22**

**2026-06-11 Update — 🏆 TRIAL-3 LIVE-FIRE: FIRST MULTI-GATE CROSSING IN PLATFORM HISTORY; ATTEMPT-4 ALIVE AT G1.** Two-day live-fire session (2026-06-10 readiness verification + /goal confidence scrub; 2026-06-11 trial launches). Attempt-3 ran across 3 instances and harvested **9 findings**: 5 substrate fixes landed Claude-direct under party-mode-ratified guardrails (G0 composer no-primary template fix `bb81b6f`; Texas dispatch cwd fork + exit-10 bundle-discard `919b16d`; irene_pass1 roster adoption + `_pause_at_gate` extraction `cd31b33`; resume-walker multi-gate pause wiring `d727248` — closing the known-deferred `7a-2-deferred-resume-mode-multi-gate-pause` follow-on; **no live trial had EVER crossed gate-to-gate before**), 1 config fix (gpt-5.4 pricing row `08d5e34`), 3 filed to deferred-inventory (pause-write atomicity; max_specialist_calls cap semantics — killed instance `a0d31fc0` via quinn_r→kira starvation AFTER it achieved the historic G1→G2C crossing; CD directive-validator mismatch 🔴 — systematic 2/2, blocks attempt-4 resume). **Trial `50b7d353` (attempt-4) is ALIVE, cleanly paused-at-G1, and is the first structurally-completable trial ever** — resume after the CD fix with `--max-specialist-calls 12` per segment. MANDATORY before attempt-5: batch `bmad-code-review` of the 5-fix delta (party-mode guardrail #3). Operator playbook at `trial-3-attempt-3-operator-playbook.md`; interim trial record in `docs/trials/cross-trial-learnings.md §Trial-3 attempts 3-4`; formal postmortem + Epic-34 retrospective pending next session. Marcus runner battery: 133 passed (3 pre-existing env/staleness failures, stash-attributed).

**2026-05-22 Update — 🎉 EPIC 34 §02A DOWNSTREAM-CONSUMER SCHEMA COHERENCE FULLY COMPLETE: 7/7 STORIES DONE.** Single-session marathon closed via Quinn-synthesis Option 5 ("Round-Trip First, Then Harmonize") — story order inverted so integration ratchet test lands BEFORE substrate harmonization, with temporary in-tree translator scaffold bridging during the harmonization arc + deleted at Epic close. Closure ledger: 34-1 forensic integration ratchet @ bc477ed (T11 PASS-WITH-NITS; tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py + forensic-fixture binding sha256 `351a57f...`); 34-2 wrangler 6-role union + excluded_reason + ignored-row filter + cross-field invariants @ cabf850 (T11 PASS / 1 DEFER-NIT); 34-3 §02A src_id→ref_id rename + J-A1(a)/(b) cli_adapter completion (run_id thread-through + model_resolution_trail.json sidecar) @ 08dfc4a (T11 PASS / 1 PATCH applied — `_accept_legacy_source_id_key` docstring); 34-4 wrangler metadata.json sme_refs[] additive emission + Story 34-1 ratchet extension per AC-34-4-A-EXT @ 16e36f7 (T11 PASS / 0 NITs); 34-5 translator-shrinkage carrier ratchet @ e59b0f4 (T11 PASS / 0 NITs); 34-6 legacy `app/marcus/orchestrator/directive_composer.py` DELETION + 7-file test rewire/delete (2 DELETE + 5 REWIRE) + 2 structural-orphan cleanups @ 55a4d25 (T11 PASS / 0 NITs; substrate-audit at session-START predicted ALL 7 hit counts EXACTLY 20/23/5/2/2/2/2); 34-7 translator deletion + A23/P5 anti-pattern entries + Epic close ceremony @ 1b59487 (T11 PASS / 0 NITs; AC-34-7-H forensic grep-sweep PERFECT). Two doctrine entries filed at `docs/dev-guide/specialist-anti-patterns.md`: **A23** "Two-source-of-truth vocab fork latent across N-year-old integration boundary" (sibling-to-A17 but vocab-forked at untested boundary) + **P5** "Schema-coherence Epic without integration-boundary green test is governance failure" (process-tier — any producer-consumer Epic MUST install integration-boundary green test as FIRST story per AC-34-N-EXT extension pattern). Deferred-inventory closures: section-02a-downstream-consumer-compatibility-systemic-drift + J-A1(a) + J-A1(b) all CLOSED at commit range bc477ed..1b59487. Substrate state: §02A composer emits `ref_id` natively (renamed from `src_id`); Texas wrangler accepts 7-role union {primary, supporting, ignored, validation, supplementary, visual-primary, visual-supplementary} + excluded_reason enum + cross-field invariants + sme_refs metadata; no temporary translator; no legacy directive composer; integration-boundary green test installed and EXTENDED through 34-4 + ratified through 34-7's direct-ratchet simplification. **Trial-3 attempt-3 LAUNCH READY** on fully harmonized substrate. Per CLAUDE.md §Deferred-inventory governance #1, `bmad-retrospective` on Epic 34 is a binding consultation point — operator-discretion whether retrospective precedes Trial-3 launch or follows it.

**2026-05-07 Update — SLAB 7C BROWNFIELD MIGRATION FULLY COMPLETE.** All 36 Slab 7c dev-stories closed across 7 Waves (0/1/2/3/4/5/6) under NEW CYCLE discipline (Claude pre-author → Codex T1-T10 → Claude T11). V7 v2 Murat triple-condition gated parallel-dispatch successfully throughout the marathon; AMEND-7c percentage-threshold gap-rate prevented noisy closeouts; AMEND-7d-iii STOP-on-TW-7c-6-fire branch never triggered (ceremony PASS at synthetic-zero-fail-reference baseline). Trial3Transcript schema landed (FR-7c-51); Trial-3 readiness PASS for development closeout. SG-1+SG-2+SG-3+SG-4 standing-guardrails AGGREGATED structurally enforced at slab close. TW-7c-1 (gap-rate detection) verdict: not_fired @ 1.35% combined gap rate across AUDIT-AC trio. TW-7c-6 (parity flake) verdict: not_fired. D12 cross-slab governance protocol three-line set landed at 7c.21: invariant-preservation note + anti-pattern A19 (class-definition substring scanners go stale) + §Slab 7c migration-guide section. 7c.21a strict-last cleanup closed Epic 3 in-place via 7a+7b+7c retirement record + live-dispatch wiring in `run_cache_hit_harness.py` + `run_5_api_smoke.py` (default fail-closed; `--live-runs N` / `--live` operator-gated). **Critical-path next:** operator-driven Gate-2 ceremony for 7c.21 (`bmad-retrospective` + party-mode-ratified mapping-checklist row-flips per FR-7c-42 + per-tripwire firing-rate review per FR-7c-41) → Trial-3 launch (`_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md`) → Epic 15 (Learning) reactivation post-Trial-3 PASS. 4 housekeeping stories pre-authored at lookahead_tier=1/2 for parallel post-Gate-2 dispatch (digest-helpers extract / scanner-staleness AST-rewrite / specialist-side producer models / legacy sidecar cleanup). 3 new anti-pattern entries landed at session-WRAPUP (A20 cross-package helper duplication under import-isolation contracts + P1 facilitator-skill-as-dev-agent-action + P2 DISMISS-thread-as-anti-pattern-signal).
**2026-04-05 Update:** Epics 13 and 14 are now complete, tested, and internally reviewed. Production prompt packs now split by workflow template: `production-prompt-pack-v4.1-narrated-deck-video-export.md` for standard narrated runs and `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` for motion-enabled narrated runs. `DOUBLE_DISPATCH` remains an inline branch in either pack.
**2026-04-08 Update:** Storyboard B and downstream motion contracts are now explicit. Motion segments keep the approved still slide in `visual_file`, the approved MP4 in `motion_asset_path`, Storyboard B renders both for review, and motion-first narration should orient briefly to the slide and then speak primarily to the visible action in the approved clip. First complete motion-enabled production run `C1-M1-PRES-20260406` has been executed through all 15 prompts of prompt pack v4.2, with assembly bundle fully packaged for Descript composition.
**2026-04-11 Update:** **Desmond** (`skills/bmad-agent-desmond/`) — memory-backed agent for Descript-specific operator steps, local Descript doc cache refresh, and mandatory **Automation Advisory** on APP assembly handoffs; `DESCRIPT_API_KEY` used only via `.env` for API verification/tooling (never commit).

**2026-04-12 Update:** Cluster dispatch trial (Storyboard A) validated end-to-end — MVP gate PASSED. Wave 1 foundation complete (20b-3, 22-1, 21-5). Wave 2 Irene intelligence iteration active: Epic 20c (template library, content-aware selection, density intelligence, master arc composition, potential Pax/Lens agents) with A/B trial methodology (`docs/workflow/operator-script-v4.2-irene-ab-loop.md`). Pass 2 initially in structural-coherence-check mode (now superseded — Epic 23 shipped; live mode is cluster-aware-refinement). PRD expanded to FR125. 229 cluster tests passing at time of entry.

**2026-04-14 Update:** **Wave 2 REPLAN** (Party Mode consensus). A/B trials SKIPPED — replaced by experience-profile-driven trial runs. Three parameter families identified: Run Constants (operational), Narration-time (Irene script controls), Assembly-time (Compositor timing). **Creative Director (CD) agent** planned as second pillar alongside Marcus — owns creative frame, parameter orchestration, gate-triggered review ("is this right?" vs Quinn-R's "is this good?"). CD uses Option B interaction: params for deterministic executors + params AND structured briefs for LLM interpreters. Two extreme experience profiles (Visual-Led + Text-Led) as proof of concept. 8 new stories added (20c-7 through 20c-14): parameter registry, assembly timing, narration expansion, CD agent, directive schema, profiles, resolver, E2E validation. 20c-2 marked done. 20c-4/5/6 + 23-1 deferred — reactivate after profile runs reveal gaps. Master parameter directory (`docs/parameter-directory.md`) planned as ongoing reference for CD, specialists, and operators.
**2026-04-14 Closeout Update:** Wave 2B execution advanced from planning into implementation. `20c-7` and `20c-8` are complete; `20c-9/10/11/12` are in-progress with concrete artifacts now present: expanded narration profile controls, CD skill scaffold (`skills/bmad-agent-cd/`), creative directive schemas (`state/config/schemas/creative-directive.schema.*`), experience profile targets (`state/config/experience-profiles.yaml`), strict `slide_mode_proportions` run-constants validation, and a dedicated creative directive validator (`scripts/utilities/creative_directive_validator.py`). Immediate next step: `20c-13` profile resolver wiring.
**2026-04-15 Review Closure Update:** `20c-3`, `20c-13`, and `20c-14` are now formally reviewed clean and complete. Static density resolution is profile-driven through the canonical experience-profile registry, Marcus/profile contract hardening is in place across the Pass 2 seam, proof artifacts now match canonical profile state, and the full repo suite is green at `670 passed, 1 skipped, 27 deselected`. Immediate next focus: formally review the remaining Wave 2B foundation stories (`20c-9` through `20c-12`) before reactivating deferred downstream work.
**2026-04-15 Wave 2B Review Closeout:** `20c-9`, `20c-10`, `20c-11`, and `20c-12` are now formally reviewed and closed. Review fixes hardened `creative_directive_validator.py` to use repo-anchored schema/profile paths and expanded the Creative Director contract seam so the full 11-key `narration_profile_controls` surface is aligned across narration config, parameter registry, creative-directive schemas, and `experience-profiles.yaml`. Focus can now shift to choosing the next deferred/reactivation slice (`23-1` or `20c-4/5/6`).
**2026-04-15 Epic 23 Reactivation Update:** `23-1` is now in implementation as a disciplined BMAD contract-hardening story. Irene Pass 2 is no longer treated as structural-coherence-only in the A/B workflow docs; the live target is cluster-aware refinement with head/interstitial calibration, tension pivots, cluster-boundary seams, and cluster-level behavioral-intent coherence explicitly in scope.
**2026-04-15 23-1 Review Remediation Closure:** `23-1` is now formally reviewed clean and closed to done after a late review-patch pass closed five findings: pivot-only tension bridges, pivot spoken-cue enforcement, master behavioral-intent subordination checks, bridge-type registry/doc parity, and tracker-state reconciliation. The focused closure suite is green at `147 passed`; the next approved implementation target is `23-2`.
**2026-04-15 23-2 Formal Review Closure:** `23-2` is now formally reviewed clean and closed to done after a review-fix pass closed three findings: interstitial master derivation now resolves from the cluster head row, the story AC now matches the authoritative cluster arc schema order (`establish -> tension -> develop -> resolve`), and contract tests now assert `severity` plus `description` for `G4-16..19`. Closure validation is green at `151 passed`; full repo regression is green at `693 passed, 1 skipped, 27 deselected`. Immediate next approved implementation target: `23-3`.
**2026-04-15 Epic 23 Closure:** All three Epic 23 stories (`23-1`, `23-2`, `23-3`) are formally reviewed clean and closed. G4-16 through G4-19 are now codified in `g4-narration-script.yaml` (19 total G4 criteria). Cluster-aware narration rules are production-ready: dual-channel grounding, gate extension, bridge cadence adaptation. Wave 3 (codify) is complete. Next: Wave 4 downstream implementation starting with `22-2`.
**2026-04-16 Closeout Update:** Wave 4 stories `22-2` (Storyboard B cluster view with script context) and `20c-15` (profile-aware parent slide count / runtime estimator, `slide_count_runtime_estimator.py` + `parent_slide_count` propagation) are **done** per `sprint-status.yaml`. Prompt pack **v4.2f** adds extraction-completeness validation and per-dimension gate evidence; trial run `C1-M1-PRES-20260415` paused after Prompt 4 (stub `extracted.md`) — **not resumable**; next operator focus is a **fresh trial** per `next-session-start-here.md`. Source Wrangler agent vision captured in `_bmad-output/planning-artifacts/source-wrangler-agent-vision.md` (future epic). BMAD **done-story coverage** audit script: `maintenance/audit_done_bmad_coverage.py` (optional `reports/audit-done-bmad-coverage.txt` output).

**2026-04-17 Update — Epic 27 Texas Intake Expansion + Shape 3-Disciplined Retrieval Architecture.** Story 27-1 DOCX provider wiring BMAD-closed (python-docx 1.2.0; Tejal cross-validation 100% key-term coverage; full suite 1036/2/0). **Three-round party-mode debate ratified Shape 3-Disciplined retrieval architecture** (Dr. Quinn's knowledge-locality partitioning): Tracy owns editorial (intent + three-tier acceptance criteria + provider choice); per-provider adapters own mechanical query translation + fetch + iteration + normalization; thin Texas dispatcher owns routing + cross-validation merger. Cross-validation is v1 first-class (scite + Consensus convergence_signal). **Story 27-0 Retrieval Foundation** opened + green-lit (ratified-stub → full BMAD spec → unanimous Option Y for Python MCP client: hand-rolled JSON-RPC-over-`requests`, NOT `mcp` PyPI pre-1.0). 27-0 blocks 27-2 / 27-2.5 / 27-3 / 27-4 / 28-1 Tracy. New **shape classification**: retrieval-shape providers (scite / Consensus / YouTube / image) use `RetrievalIntent` contract; locator-shape providers (DOCX done, Notion / Box / Playwright) keep existing directive shape — operator-direct is degenerate case of Shape 3 contract; both shapes route through the same dispatcher. Epic 27 roster: 9 stories, ~31 pts. Critical path: 27-1 done → 27-0 → 27-2 → 27-2.5 → unblocks Epic 28. **Story 28-1 Tracy** reshape banner added (points drop 9 → ~7; scite-DSL knowledge relocates to 27-2 scite adapter).

**2026-04-29 Update (HYBRID CLONE) — Slab 7b PRD RATIFIED + Wave 0 foundational artifacts LANDED.** Slab 7b PRD authored end-to-end via `bmad-create-prd` workflow with 9 party-mode rounds (R1-R9; 4 voices/round; 0 re-opens; 4/4 unanimous on R9 close). Slab 7b activates eleven specialist body roles (Texas/Quinn-R/Vera Class-A hardening; Irene Pass-1 Class-B refresh; Tracy Class-C+ port-shape with sidecar emission; Gary/Kira/Wanda/Enrique Class-C API-bound port-shapes; Dan Class-D1 LLM-greenfield; Compositor Class-D2 pipeline-greenfield) into the Slab 7a orchestration substrate (CLOSED 2026-04-29 at `95c81b0`). 26 new FRs (FR88-FR113); 24 new NFRs (NFR-T9..T12 / NFR-CG12..CG20 / NFR-I9..I13 / NFR-OD3..OD6); 10 new ADRs (D14-D23); SG-4 (BMB sanctum alignment per body) added as 4th standing guardrail with closed-allowlist option-b path. 5-class taxonomy A/B/C/C+/D1/D2 per D14. **Class-D2 sidecar variant (Compositor) is canonical inside BMB regime per D20 — NOT exception.** Implementation-readiness Steps 1-3 closed READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS. Three named preconditions (foundational artifacts FR108-FR112 + sandbox-AC inventory FR107 + scaffold-v0.2-D2-pipeline FR111) ALL LANDED in Wave-0 atomic-merge commit `9ed6fcb`: 6 artifacts (`docs/dev-guide/bmb-sanctum-alignment-checklist.md` 8-section TOC + `docs/dev-guide/sanctum-exception-categories.json` closed allowlist with sidecar-hook initial entry per Cora precedent + `docs/dev-guide/operator-control-parity-template.md` form-not-prose template + `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` 7-file scaffold dir + `skills/bmad-agent-cora/SKILL.md §Sanctum exception` anchor with HTML grep marker + `docs/dev-guide/migration-ac-sandbox-inventory.json` +5 entries gamma/kling/elevenlabs/wondercraft/dan-api-tbd-pending). PRD errata addendum at commit `ddcd1b1` captures P0 path-sweep findings (FR111 path correction + FR101 contract realignment + SanctumParityTestBase Wave-1 deliverable + tests/parity/per_specialist subdir TBD). 696 passed/19 skipped regression baseline holds (no regression). **Wave 1 (Class-A hardening: Texas/Quinn-R/Vera) UNBLOCKED** — next workflow is `bmad-create-epics-and-stories` to produce `epics-slab-7b-specialist-activation-eleven.md` with 1 Epic + 12 stories. NFR-CG17 deviation noted: FR107 sandbox-AC inventory authored by Claude (not Codex) per R1 party-mode scoping consensus — Wave 0 is foundational scaffolding pre-Wave-1, NOT inside Codex's Class-C/C+ port-shape scope; Codex deployment activates at Wave-1 story open.

**2026-04-25 Update (HYBRID CLONE) — Story 2a.2 BMAD-CLOSED + M1 ACCEPT-WITH-GAP CACHE-HIT-RATE CLAUSE RETIRED.** First REAL LLM-invoking specialist migration on the LangChain/LangGraph stack landed. Irene Pass 2 9-node scaffold runs live against `gpt-5.4` via `app/specialists/irene/{__init__,graph,state,model_config,expertise/README}` (`_act` 64 LOC vs AC-B 150 LOC ceiling; 4 deterministic helpers — sanctum digest sorted-by-as_posix + reference bundle + sort_keys+ensure_ascii+separators-pinned envelope serialization + JSON-fenced response parser; Winston discriminator-check on `_act` trail-read). Cache-hit-rate harness retargeted at Irene; T7 measurement: prompt_tokens stable at 9399 across N=10 (>>1024 MF2 floor); **median[2:]=95.33%** (vs 60% MF1 threshold; +35.33pp slack); MF6 sanctum lock-and-verify pre/per/post=0/0/0. Wall-clock 230s. Cost ~$0.30. T8 dual-path regression: real-key 361/5/0 (+40 margin above 321 floor); placeholder-key 360/7/0 (SF3 anti-erosion verified — both `@pytest.mark.llm_live` tests auto-skip on placeholder sentinel). 28 tests across 11 files. Ruff clean; import-linter 3/3 KEPT (Irene C3 ignore_imports row added at T2 per A12 procedural-coupling pattern). Doc deliverables: NEW [`docs/dev-guide/sanctum-reference-conventions.md`](dev-guide/sanctum-reference-conventions.md) (MF7 — activation-baseline-vs-steady-state epoch split); [`specialist-anti-patterns.md`](dev-guide/specialist-anti-patterns.md) augmented (A9 second example + A10/A11/A12 NEW); [`langgraph-migration-guide.md §12`](dev-guide/langgraph-migration-guide.md) real-Irene worked example. Pre-T1 sanctum archived to `_bmad/memory/_archive/bmad-agent-content-creator-pre-2a2-2026-04-24/` (46 files preserved); active sanctum empty per D2 SYNTHESIS verdict. 4 party-mode waypoint reviews honored (T2/T4/T7/T8) + G6 layered self-review (3 PATCH applied / 2 DISMISSED / 4 DEFERRED). FRs closed: FR9–FR12 (per-specialist) + FR15 (first sanctum cold-read) + FR16 (first resolution-trail) + **FR54** (cache-hit-rate ACTIVATED + MEASURED). Slab 2a momentum: 2a.1 ✅ → 2a.2 ✅ → 2a.3 (Kira motion) next → 2a.4 (Texas) → Slab 2b.1 TEMPLATE batch (gated on filing A12 generator-auto-emit follow-on as 2a.1 defect story before 2b.1 opens). Deferred-inventory: 1 CLOSED + 4 NEW (net 17 named follow-ons).

**2026-04-22 Update (HYBRID CLONE) — LangChain + LangGraph Migration Planning Complete.** On the hybrid clone (`dev/langchain-langgraph-foundation` branch, `origin=course-DEV-IDE-with-AGENTS-hybrid`, `upstream=course-DEV-IDE-with-AGENTS` read-only), the full planning chain for the re-platform migration is now complete in one session: (a) implementation-readiness report (`_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-22.md`) — READY-WITH-MINOR-AMENDMENTS verdict, 5 findings staged; (b) migration architecture (`_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`) — 8/8 steps, 13 decisions locked (D1 sanctum hybrid / D2 model cascade / D3 HIL tamper-evidence / D4-D13), party-mode Round 1 green-lit with 9 amendments, 15/15 substrate invariants preserved; (c) epics + stories (`_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md`) — 9 epics / 56 stories / ~184 pts with M1–M5 acceptance bars expressed as story-level ACs. All 65 FRs + 43 NFRs have per-story coverage. PR-R (primary Sprint #1 Marcus dispatch reshaping) staged as forward-port convergence in migration-guide §8. Authoritative NFR count reconciled 38→43. Ready for Slab 1 Story 1.1a kickoff (Runtime Substrate Environment + Dependencies — uv venv + core deps + lockfile) per Amendment F strict-serial split 1a→1b→1c. Legacy primary-repo epics.md / architecture.md / prd.md remain frozen reference; migration artifacts are hybrid-scope and coexist under distinct filenames. Primary repo continues production-shift work unchanged per Decision 2 (bounded big-bang in clone).

**2026-04-18 Update — Story 27-0 Retrieval Foundation BMAD-CLOSED.** Shape 3-Disciplined foundation landed: 8 new retrieval modules under `skills/bmad-agent-texas/scripts/retrieval/` (`contracts`, `base`, `dispatcher`, `mcp_client`, `normalize`, `refinement_registry`, `fake_provider`, `provider_directory`); schema v1.1 additive bump (`extraction-report-schema.md` + new `SCHEMA_CHANGELOG.md` gate artifact); audience-segmented `skills/bmad-agent-texas/references/retrieval-contract.md`; `--list-providers` CLI on `run_wrangler.py`; repo-level `.cursor/mcp.json` + `.mcp.json` scite + Consensus URL entries; CLAUDE.md pointer; Marcus `external-specialist-registry.md` breadcrumb. **Post-green-light operator amendment**: Provider Directory fold added AC-B.8 / B.9 / T.9 / T.10 / T.11 — runtime `list_providers()` surface with 16 entries (11 locator ready/ratified + 5 retrieval including `openai_chatgpt: backlog` forward placeholder per operator directive). Tests +70 collecting (target +34); full suite **1106 passed / 2 skipped / 0 failed / 2 xfailed**. Ruff clean on all 27-0 code. Gates: party-mode implementation review 3 GREEN + 1 YELLOW→GREEN; bmad-code-review layered 5 MUST-FIX + 9 SHOULD-FIX applied, 4 DISMISSED with rationale (AC-B.7 literal dispatcher-wiring deferred to 27-2 per anti-pattern #3 shape-separation; dual-emit writer + log-stream parity + parametrized schema-compliance cascade-deferred), ~22 NITs logged. **UNBLOCKS 27-2 scite adapter and 27-2.5 Consensus adapter.** Forward design note captured in user memory: three distinct parameter knobs for future work — enrichment degree (Irene aspirational depth beyond SME), gap-filling (derivative-artifact content demands), evidence-bolster (corroboration of existing claims via cross-validation).
**Current Implementation Status:** Use the dated update above as the source of truth for epic completion; the detailed historical implementation notes below remain as project chronology.
**Implementation Status:** Epics 1-14 + SB all COMPLETE (75 stories). Epics 19-21 + 23 COMPLETE (cluster schema, Irene planning, Gary dispatch, cluster-aware narration — 20 stories). Epic 20c IN-PROGRESS (cluster intelligence + creative control — iterative; 20c-1 in-progress; 20c-4/5/6 deferred; Wave 2B closure stories including `20c-15` done). Epics 22, 24 IN-PROGRESS (`22-2` done; `22-3`/`22-4` and Epic 24 stories queued). Epics 15-18 BACKLOG (learning, autonomy, research, assets).

## Purpose

Build a persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. A custom master orchestrator agent (created via `bmad-agent-builder`) provides a conversational interface ("general contractor" experience) coordinating specialist agents that manipulate professional media tools through skills backed by Python scripts for API calls, while systematically capturing creative decision-making patterns in BMad memory sidecars for iterative refinement and reuse.

## Critical Implementation Model

**Agents are skill directories** created through `bmad-agent-builder` six-phase conversational discovery process, following BMad SKILL.md standard. They live under `skills/bmad-agent-{name}/` and are discovered through the skills layer.

**Skills are SKILL.md directories** providing tool-specific capabilities with progressive disclosure (`references/`), Python code execution (`scripts/`), and output templates (`assets/`).

**Python infrastructure** provides supporting code for API clients, state management, and file operations - invoked from agent skills when code execution is required.

**Cursor plugin packaging** via `.cursor-plugin/plugin.json` enables native IDE integration with auto-discovery of skills, rules, commands, hooks, and MCP servers.

**BMad memory sidecars** provide persistent agent learning through `_bmad/memory/{skillName}-sidecar/` with index.md (context), patterns.md (learned preferences), chronology.md (history), and access-boundaries.md (scope control).

## Key Decisions From Planning

### Agent Architecture (Confirmed)
- **Custom Master Orchestrator agent** (.md file created via `bmad-agent-builder`) as single conversational point of contact
- **Custom specialist agents** (.md files created via `bmad-agent-builder`) for tool mastery (Gamma, ElevenLabs, Canvas, etc.)
- **Custom skills** (SKILL.md + references/ + scripts/) for tool expertise, parameter intelligence, coordination
- **Reuse existing BMad agents** for writing, editing, review, documentation
- **Python infrastructure** in scripts/ for API clients, state management, file operations

### Cursor Plugin Architecture (Confirmed)
- `.cursor-plugin/plugin.json` manifest with auto-discovery of skills/, rules/
- `.mcp.json` for tool server definitions bundled in plugin
- `hooks/hooks.json` for event-driven automation (sessionStart → pre-flight, afterFileEdit → quality, sessionEnd → reporting)
- `rules/*.mdc` for persistent agent behavior guidance
- `commands/*.md` for agent-executable actions

### BMad Memory System (Confirmed)
- Agent memory sidecars at `_bmad/memory/{skillName}-sidecar/`
- `index.md` for essential context loaded on activation
- `patterns.md` for systematic expertise crystallization (append-only, periodically condensed)
- `chronology.md` for session and production run history
- `access-boundaries.md` for agent scope control (read/write/deny zones)

### Operational Model (Confirmed)
- **Run presets**: `explore`, `draft`, `production`, `regulated` with parameter overrides
- **Asset-lesson pairing invariant**: every educational artifact paired with instructional context
- **Tool parameter mastery**: Specialty agents master complete API parameter spaces, preferences stored in style guide YAML
- **Exemplar-driven development**: Each specialist agent proves competence by reproducing real exemplar artifacts programmatically via API/MCP, scored against a structured rubric. Exemplars serve as both design aids and acceptance tests. See `resources/exemplars/_shared/woodshed-workflow.md`
- **Woodshed skill**: Shared skill (`skills/woodshed/`) provides study → reproduce → compare → reflect → register workflow with detailed run logging, downloaded artifact retention for every attempt (pass/fail), mandatory reflection between failed attempts, and circuit breaker give-up protocol (3/session, 7 total)
- **Two woodshed modes**: Faithful (exact reproduction proving tool control) must be mastered before Creative (enhanced reproduction proving creative judgment) is unlocked per exemplar
- **Progressive mastery**: L1-L4 single artifacts → L5 multi-artifact sets. L-levels with dot extensions. Levels provisional — agents may propose changes. Regression runs ensure mastered exemplars stay mastered
- **Export and download**: All reproductions must download production-quality artifacts (PNG for production, PDF for review, PPTX for editing, MP3 for audio) — screenshots supplementary only
- **Evaluator design requirements** (from Story 3.1): Guide the tool's intelligence (never suppress), extract and compare actual output (not just process compliance), score on content coverage (not exact match), use cheap quality signals per medium, separate woodshed training from production QA, capture know-how from user checkpoint reviews. See `skills/woodshed/SKILL.md` for full reference
- **Gamma API Mastery module**: Double-dispatch variant generation, literal-visual composite fallback, PNG export normalization with `_materialize_exported_slide_paths`
- **HIL gates**: human checkpoints at every stage with rubrics and signoff tracking
- **Pre-flight checks**: Hook-driven MCP/API connectivity verification + tool documentation scanning
- **Production run reporting**: Comprehensive effectiveness analysis with learning capture in agent memory

### State Management (Confirmed)
- **YAML files**: Course context, style guides, policies (human-readable, git-versioned) in `state/config/`
- **SQLite database**: Runtime coordination state, production run tracking in `state/runtime/`
- **BMad memory sidecars**: Agent learning, expertise patterns, session history in `_bmad/memory/`

### Repository Contract (Confirmed)
```
.cursor-plugin/   # Cursor plugin manifest
skills/           # SKILL.md directories with references/ + scripts/ (auto-discovered)
  woodshed/       # Shared exemplar mastery skill (study, reproduce, compare, regress)
rules/            # .mdc rules files for agent guidance
hooks/            # Event-driven automation triggers
commands/         # Agent-executable command files
state/            # YAML configs + SQLite runtime
_bmad/memory/     # Agent memory sidecars for persistent learning
scripts/          # Shared Python infrastructure (API clients, utilities)
tests/            # Unit + integration tests
docs/             # Architecture + agent guides + troubleshooting
resources/
  exemplars/      # Per-tool exemplar libraries with _catalog.yaml, briefs, source, reproductions
    _shared/      # Comparison rubric template, woodshed workflow protocol
    gamma/        # Gamma exemplars (slides/presentations)
    elevenlabs/   # ElevenLabs exemplars (audio/voiceover)
    canvas/       # Canvas exemplars (LMS deployment)
    qualtrics/    # Qualtrics exemplars (surveys/assessments)
    canva/        # Canva exemplars (visual design)
  style-bible/    # Authoritative brand reference
  tool-inventory/ # Tool access matrix
```

## Tool Universe (Researched March 26, 2026)

17 tools classified by programmatic access. Full details in `resources/tool-inventory/tool-access-matrix.md`.

| Tier | Tools | Access |
|------|-------|--------|
| **Tier 1: API + MCP** | Gamma, ElevenLabs, Canvas LMS, Qualtrics, Canva, Notion | Platform capability: REST API and published MCP server |
| **Tier 2: API Only** | Botpress, Wondercraft, Kling, Panopto | REST API, no MCP server |
| **Tier 3: Limited API** | Descript, Midjourney, CapCut | Early access / third-party only |
| **Tier 4: Manual Only** | Vyond, CourseArc, Articulate (Storyline/Rise) | No usable programmatic access for this repo setup |
| **Local FS** | Box Drive | Local filesystem via desktop sync client, no API needed |

- **Live Cursor-verified MCP servers** in `.mcp.json` / `.cursor/mcp.json`: Gamma, Canvas LMS
- **API-verified but MCP-deferred platforms**: ElevenLabs, Qualtrics
- **Documented but currently deferred MCPs**: ElevenLabs (Cursor tool-name filtering), Canva (OAuth redirect rejection), Qualtrics (GitHub-only build step), Fetch (no usable surfaced tools in this setup), Brave Search (not enabled by default)
- **User-level MCPs** already available: Playwright (browser automation), Ref (doc search/reading)
- **API keys** documented in `docs/admin-guide.md`: Tier 1-3 tools with documentation links; values live in local `.env` only
- **Manual tools** require agent-guided workflows where agents provide specs and users execute in tool UI

## Current State

- [x] Repository scaffolded with directory structure, local `.env` pattern, content standards
- [x] BMad Method installed (BMM, Core, CIS modules)
- [x] **BRAINSTORMING COMPLETED**: 10 comprehensive epics defined
- [x] **PRD COMPLETED**: 70 FRs across 11 capability domains (recast for agent .md approach)
- [x] **ARCHITECTURE COMPLETED**: BMad Agent + Cursor Plugin architecture validated (recast)
- [x] **EPICS RECAST**: All 10 epics updated to reflect bmad-agent-builder creation approach
- [x] **Strategic Decisions**: Party Mode team validated and recast for agent .md patterns
- [x] **STORY CREATION COMPLETED**: 31 stories across 10 epics, 100% FR coverage validated
- [x] **API-FIRST SEQUENCING**: API/MCP clients (Gamma, ElevenLabs, Canvas) built in Epic 1 before agent creation
- [x] **TOOL UNIVERSE AUDIT**: 15 tools researched and classified (Tier 1-4), MCP servers configured, credentials documented for local `.env`
- [x] **EPIC 1 COMPLETE**: All 11 stories implemented, tested with live APIs, validated by Party Mode review team
- [x] **STORY 1.1**: Cursor plugin foundation — plugin.json, .mcp.json, hooks, directory structure
- [x] **STORY 1.2**: Python infrastructure — BaseAPIClient with retry/pagination/binary, utilities, venv
- [x] **STORY 1.3**: State management — SQLite (3 tables), YAML configs (3 files), BMad memory sidecars (5 agents)
- [x] **STORY 1.4**: Pre-flight check skill — SKILL.md + Python runner + doc scanner + 3 reference docs
- [x] **STORIES 1.5-1.11**: Testing framework + 5 full-featured API clients (Gamma, ElevenLabs, Canvas, Qualtrics, Panopto) + Canva MCP config
- [x] **LIVE API VALIDATION**: 117 tests pass against real services (Gamma, ElevenLabs, Canvas, Qualtrics), 3 skipped (Panopto — no creds)
- [x] **FR EXPANSION (Party Mode)**: 10 new FRs (FR71-FR80) added for Source Wrangling + Run Mode Management
- [x] **TOOLS EXPANSION**: Notion (API + MCP, source wrangling) and Box Drive (local FS) added to tool universe (17 tools total)
- [x] **SOURCE WRANGLER**: New architectural component for pulling reference materials from Notion/Box into production context; agent vs. skill design decision deferred to story creation
- [x] **AD-HOC MODE**: Binary ad-hoc/default mode switch for Master Orchestrator; ad-hoc routes assets to scratch/staging, suppresses state tracking; QA always runs; future per-level modality matrix deferred
- [x] **STORY 2.1 (Marcus Orchestrator)**: Agent built via bmad-agent-builder (6-phase discovery with Party Mode coaching), quality scan passed (0 critical), 12 interaction test scenarios passed, Party Mode team validation complete. 13 files: SKILL.md + 8 references + 2 scripts + 2 test files. Memory sidecar active with 4 files. First production plan staged (C1-M1-P2S1-VID-001).
- [x] **EPIC 2 COMPLETE**: Stories 2.2–2.6 all done. Production-coordination skill (4 scripts, 4 refs, 40 tests). Marcus references updated for workflow management, delegation, parameter intelligence, pre-flight, and mode management.
- [x] **EXEMPLAR-DRIVEN DEVELOPMENT**: Woodshed skill created (`skills/woodshed/`), exemplar library scaffolded (`resources/exemplars/` per tool), comparison rubric, run logging, reflection protocol, circuit breaker, two-mode woodshed (faithful + creative), doc refresh protocol, and L-level difficulty system all in place. 5 Gamma exemplars provided (L1-L4.2). Smoke test validated: Gamma API produces single-card output, PDF export/download works (205KB), 5 credits/card. GammaClient needs parameter name updates (inputText, textMode, exportAs). Epic 3 stories updated with exemplar reproduction as acceptance criteria.
- [x] **STORY 3.3.1 (Composition Architecture Harmonization + Gary Deck)**: DONE — Party Mode composition decisions implemented: segment manifest as Irene artifact, two-pass Irene model, Irene/Quinn-R/Kira/Marcus/Gary all updated, architecture.md updated with pipeline graph, tool inventory updated (Descript as sole composition platform), Gary deck mode + theme/template preview (TP capability), gary_slide_output return field, GammaClient.list_themes() live-tested (10 themes). Epic 3 re-sequenced to 11 stories: Compositor added as 3.5, Canvas→3.6, Qualtrics→3.7, Canva→3.8, Source Wrangler→3.9, Tech Spec Wrangler→3.10.
- [x] **PROMPT 7 DISPATCH HARDENING (2026-03-30)**: Canonical `gamma_operations.py` generate path now enforces fail-fast for metadata-only slide payloads, supports explicit merge of `gary-fidelity-slides.json` + `gary-slide-content.json`, and keeps placeholder content behind debug-only override (`--allow-placeholder-content`). Regression tests added to prevent recurrence of intent-placeholder slide outputs while preserving parameter, theme-handshake, and export reliability gains.
- [x] **Epic 2A: Fidelity Assurance & APP Intelligence Infrastructure** (9/9 stories DONE — Vera agent covering G0-G5, sensory bridges, perception protocol, source_ref resolver, cumulative drift tracking, fidelity-control vocabulary, maturity audit skill. GOLD document: `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`)
- [x] Epic 3: Core Tool Specialist Agents & Mastery Skills (11/11 stories DONE — Stories 3.1-3.11 complete, including Story 3.8 Canva specialist.)

## APP Design Principles & Fidelity Architecture (Added 2026-03-28)

See `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` (GOLD document) for full analysis.

- **Agentic Production Platform (APP):** Formal naming — the IDE is the runtime environment for a network of specialized agents. The platform gets smarter over time as LLMs improve and agent memory accumulates.
- **Three-Layer Intelligence Model:** L1 deterministic contracts (invariant standards), L2 agentic evaluation (evolves with LLM capability), L3 learning memory (compound improvement via sidecars). Applies to every APP capability.
- **Hourglass Model:** Wide cognitive top (synthesis) → narrow deterministic neck (schema/parameter binding) → wide cognitive bottom (creative execution). Intelligence must not enforce constraints that can be deterministic.
- **Leaky Neck Diagnostic:** Any point where agentic judgment enforces a deterministic constraint is a design defect.
- **Sensory Horizon:** Agents cannot verify what they cannot perceive. Sensory bridges (image, audio, PDF, video) with mandatory confirmation protocol.
- **Fidelity Assessor:** New forensic agent distinct from Quinn-R. Produces Fidelity Trace Reports (Omissions/Inventions/Alterations). Circuit breaker on failure. Runs before quality review.
- **Provenance Protocol:** Mandatory `source_ref` fields in all artifact schemas for traceable provenance chains.
- **Current maturity:** Upgraded from Level 0 — Vera covers G0-G5 with 30 L1 criteria, perception bridges for all modalities, cumulative drift tracking, source_ref resolver, fidelity-control vocabulary enforcement in merge_parameters(). G6 (composition) remains future.
- **Epic 2A** COMPLETE (9/9 stories). Story 3.11 mixed-fidelity system COMPLETE with `execute_generation()` production entry point.

## Roadmap Rebaseline (2026-03-28)

Party Mode consensus + parallel GPT-5.4 architectural review identified significant overlap between completed Epics 1-3/2A work and downstream epic scope. Rebaseline applied:

- **Epic 4A** (Agent Governance, Quality Optimization & APP Observability): **6 stories** — run baton, lane matrix, envelope governance, agent QA gate, perception caching + observability (**`run_mode` tagging; ad-hoc excluded from course-progress metrics**), **ad-hoc ledger & learning enforcement (4A-6, FR91)**. Must complete before Epic 4. FRs FR81–FR91 on PRD.
- **Epic 4 updated**: Dependency on 4A. Stories 4.2 (Quality Gates) and 4.4 (Reporting) updated to assume governance layer + Vera fidelity checks.
- **Epic 5 trimmed**: Story 5.2 (Assembly Coordination) dropped — compositor skill delivers this. Story 5.3 (Style Orchestration) merged into governance. Story 5.4 edited — Panopto and Kling already done. Story 5.1 and 5.4 are now complete.
- **Epic 6 trimmed**: Story 6.2 (Enhanced Canvas) merged into Story 3.6 (Canvas Specialist). Story 6.1 completed.
- **Epics 7, 8, 9 collapsed** into Epic G (Governance Synthesis & Intelligence Optimization): **3 stories** — platform allocation (G.1), tool/doc synthesis (G.2), **APP session readiness & health monitoring** (G.3, 2026-03-30: SQLite/`state`/imports + report; composes with pre-flight-check). Epic G is now complete.
- **2026-04-03:** `scripts.utilities.run_constants` loads frozen **`run-constants.yaml`** per bundle; wired into `app_session_readiness --bundle-dir` and `validate-source-bundle-confidence` when the file exists (contract v1.2).
- **2026-04-03:** Prompt 3 hardening pass added `scripts.utilities.validate_source_bundle_confidence` as stable CLI wrapper, normalized validator parsing for heading/ingestion format variants, and centralized hyphenated skill loading in `scripts.utilities.skill_module_loader`.
- **Epic 10**: Predictive optimization requires Epic 4 + Epic G telemetry. Story 10.1 is now complete.

**Net: 11 epics → 9 epics, 46 stories → 40 stories** (historical rebaseline); **+Story 4A-6 → 41 stories** (2026-03-29); **+Story G.3 → 42 stories** (2026-03-30). Architecture updated with governance section.

## Composition Architecture (Added 2026-03-27)

See `_bmad-output/brainstorming/party-mode-composition-architecture.md` for full decision record.

- **Silent Video + Smart Audio:** Kling always `sound-off`. ElevenLabs owns all audio (narration, SFX, music).
- **Segment manifest:** YAML file produced by Irene Pass 2. Single source of truth. All downstream agents read/write.
- **G4 anti-drift rule:** The G4 fidelity contract references both the narration script template and the segment manifest template so Pass 2 changes cannot drift out of validation coverage.
- **Narration-paced video:** ElevenLabs generates first; narration_duration becomes clip duration target for Kira.
- **Descript:** Sole composition platform (manual-tool pattern). Compositor skill (Story 3.5) generates Descript Assembly Guide and can **`sync-visuals`** to copy Gate-approved stills into the assembly bundle (`visuals/`) next to audio, captions, and summaries.
- **Four HIL gates:** Lesson plan → slides → script+manifest → final video.
- **Quinn-R two-pass:** Pre-composition (asset quality) + post-composition (final export).
- **Irene two-pass:** Pass 1 (lesson plan + slide brief before Gary); Pass 2 (narration script + segment manifest after Gary + HIL Gate 2).
- **2026-04-03 anti-drift hardening:** Prompt 6B now requires literal-visual operator packet + readiness confirmation before Gary dispatch side effects; Storyboard A (post-Gary) and Storyboard B (post-Irene Pass 2) are explicit approval checkpoints before advancing to subsequent pipeline spend.
- **2026-04-05 literal-visual rendering policy:** literal-visual slides are enforced as full-slide image-only at dispatch input. Supporting prose is moved to Irene Pass 2 narration/script, and Gate 2 preflight validation fails on non-URL literal-visual payload content.
- **2026-04-05 literal-visual reliability fix:** Anti-fade prompt ("full opacity, not as background, not faded") + initial attempt plus one retry (`_MAX_TEMPLATE_RETRIES = 2`) + composite fallback (preintegration PNG or URL download). Gamma classifies images as accent/background by content — not API-controllable. `visual_fill_validator` enhanced with variance-based content detection (`content_stddev`). Provenance tracked via `literal_visual_source` field.
- **2026-04-08 motion review contract:** Storyboard B shows both the approved still and the approved motion clip for motion segments. Downstream contracts preserve the still in `visual_file` and the playback asset in `motion_asset_path`; motion-first narration is the expected design when `visual_mode: video`.
- **2026-04-10 Storyboard B HTML redesign:** Summary banner uses 3-column grid (was 2-col with overflow) and is wrapped in a collapsible `<details>` element (open by default). Motion-enabled cards use stacked layout (slide + video in column 1, script spanning column 2) to eliminate dead space. Static cards unchanged. Regression test in `test_generate_storyboard.py`.
- **Gary deck enhancement:** Deck mode (numCards by content type), theme/template preview (TP capability), gary_slide_output return field.
- **Seven instructional use cases:** Narrated deck, dialogue, walkthrough, case study, assessment prompt, concept explainer, module bumper — all one pipeline.

## Key Files

- `_bmad-output/planning-artifacts/prd.md` - Complete PRD (70 FRs, recast)
- `_bmad-output/planning-artifacts/architecture.md` - Complete architecture (recast)
- `_bmad-output/planning-artifacts/epics.md` - Epic breakdown with requirements (recast)
- `_bmad-output/strategic-decisions-collaborative-intelligence.md` - Strategic decisions
- `_bmad-output/brainstorming/brainstorming-session-20260325-150802.md` - Brainstorming session
- `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md` - Marcus coaching doc
- `_bmad-output/brainstorming/party-mode-composition-architecture.md` - **Composition architecture decisions (2026-03-27)**
- `_bmad-output/implementation-artifacts/3-3-1-composition-architecture-harmonization.md` - **Story 3.3.1 (DONE)**
- `skills/bmad-agent-marcus/SKILL.md` - **Marcus orchestrator agent (Story 2.1 DONE)**
- `skills/reports/bmad-agent-marcus/quality-scan/2026-03-26_152243/quality-report.md` - Marcus quality scan
- `tests/agents/bmad-agent-marcus/interaction-test-guide.md` - Marcus interaction tests
- `resources/tool-inventory/tool-access-matrix.md` - **Tool universe access matrix (17 tools)**
- `scripts/heartbeat_check.mjs` - Baseline read-only API heartbeat across configured tools
- `scripts/smoke_elevenlabs.mjs` - Focused ElevenLabs API smoke check
- `scripts/smoke_qualtrics.mjs` - Focused Qualtrics API smoke check
- `skills/woodshed/SKILL.md` - **Shared exemplar mastery skill (study, reproduce, compare, regress)**
- `resources/exemplars/_shared/woodshed-workflow.md` - **Complete woodshed workflow protocol (logging, reflection, circuit breaker)**
- `resources/exemplars/_shared/comparison-rubric-template.md` - **Rubric for scoring exemplar reproductions**
- `resources/exemplars/gamma/_catalog.yaml` - **Gamma exemplar registry**
- `docs/agent-environment.md` - Agent/MCP guidance  
- `docs/operations-context.md` - Compact operations-only context for production sessions
- `docs/workflow/human-in-the-loop.md` - HIL procedure
- `.cursor/rules/course-content-agents.mdc` - Cursor agent rules
