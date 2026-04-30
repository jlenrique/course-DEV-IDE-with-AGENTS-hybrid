# Legacy v4.2 <-> LangGraph Migrated Operator-Control Parity Table

**Authority.** This table is the operator-readable trace of every legacy v4.2
operator-control lever and its LangGraph-migrated equivalent. **Row count is
SG-2 floor: 33 rows. The CI parity-test suite at
`tests/parity/test_operator_control_parity.py` asserts `len(rows) == 33` and
fails the merge if violated.**

**Source.** Rows derive from the 33-row mapping checklist at
`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`.
Every row in this table corresponds 1:1 to a row in the mapping checklist;
the parity-test suite enforces the bidirectional correspondence.

**Updates.** Adding or removing rows requires (a) updating the mapping
checklist FIRST, (b) updating this table in lockstep, (c) updating the parity
test count assertion, (d) party-mode consensus (not dev-agent authority) per
NFR-V3 (registry-style artifacts are additive-only post-Slab-7a-close).

| # | Legacy v4.2 control lever | LangGraph migrated path / command | Parity test ID |
|---|---|---|---|
| 1 | 01 Activation + Preflight operator GO | `bmad-trial start --input <corpus> --auto-confirm-directive=false` (G0 confirm-or-edit prompt; Story 7a.1) | `test_row_01_g0_directive_composition_confirm` |
| 2 | 02 Source Authority Map pre-map approval | `see _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md#row-2` (awaits Story 7a.3/7a.5 semantics) | `test_row_02_source_authority_map_gate` |
| 3 | 02A Operator Directives poll and confirmation | `see docs/operator/step-02a-prior-run-defaults.md` (legacy defaults doc; migrated capture awaits Story 7a.5) | `test_row_03_operator_directives_capture` |
| 4 | 03 Ingestion + Evidence Log directive handoff | `app.marcus.orchestrator.directive_composer` + Texas directive payload (Story 7a.1; deeper evidence log awaits 7a.5) | `test_row_04_ingestion_evidence_log` |
| 5 | 04 Ingestion Quality Gate + Irene Packet | `OperatorVerdict.decision in {confirm, revise, reject, escape, skip-slide, abort-run}` via vocabulary registry | `test_row_05_ingestion_quality_gate` |
| 6 | 04A Lesson Plan Coauthoring + Scope Lock | `see docs/conversational-gates/_registry/glossary.md` (scope-lock vocabulary substrate; implementation awaits Story 7a.5) | `test_row_06_lesson_plan_scope_lock` |
| 7 | 04.5 Parent Slide Count Polling | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-7` (awaits Story 7a.5) | `test_row_07_parent_slide_count_poll` |
| 8 | 04.55 Estimator + Run Constants Lock | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-8` (awaits Story 7a.5) | `test_row_08_run_constants_lock` |
| 9 | 4.75 Creative Directive Resolution | `see state/config/experience-profiles.yaml` (existing profile substrate; migrated conversation awaits Story 7a.5) | `test_row_09_creative_directive_resolution` |
| 10 | 05 Irene Pass 1 + Gate 1 Fidelity | `see app/specialists/irene/graph.py` (active Irene substrate; gate semantics await Story 7a.3/7a.5) | `test_row_10_irene_pass1_gate` |
| 11 | 05B Cluster Plan G1.5 Gate | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-11` (awaits Story 7a.4) | `test_row_11_cluster_plan_gate` |
| 12 | 06 Pre-Dispatch Package Build | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-12` (awaits Story 7a.5) | `test_row_12_pre_dispatch_package` |
| 13 | 6.2 Cluster Prompt Engineering | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-13` (awaits Story 7a.5) | `test_row_13_cluster_prompt_engineering` |
| 14 | 6.3 Cluster Dispatch Sequencing | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-14` (awaits Story 7a.5) | `test_row_14_cluster_dispatch_sequencing` |
| 15 | 06B Literal-Visual Operator Build | `see skills/bmad-agent-marcus/scripts/validate-literal-visual-pre-dispatch.py` | `test_row_15_literal_visual_operator_build` |
| 16 | 07 Gary Dispatch + Export | `see app/specialists/gary/graph.py` (Gary active-mode parity awaits Slab 7b) | `test_row_16_gary_dispatch_export` |
| 17 | 7.5 Cluster Coherence G2.5 Gate | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-17` (awaits Story 7a.4) | `test_row_17_cluster_coherence_gate` |
| 18 | 07B Variant Selection Gate | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-18` (awaits Story 7a.4) | `test_row_18_variant_selection_gate` |
| 19 | 07C Storyboard A + Gate 2 Approval | `gate_code=G2C` active pause point from `app.manifest.compiler.production_gate_ids(live_manifest)` | `test_row_19_storyboard_a_gate2_approval` |
| 20 | 07D Gate 2M Motion Designation | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-20` (awaits Story 7a.4) | `test_row_20_motion_designation_gate` |
| 21 | 07E Motion Generation / Import | `see app/specialists/kira/graph.py` (Kira active-mode parity awaits Slab 7b) | `test_row_21_motion_generation_import` |
| 22 | 07F Motion Gate | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-22` (awaits Story 7a.4) | `test_row_22_motion_gate` |
| 23 | 08 Irene Pass 2 + Segment Manifest | `see app/specialists/irene/graph.py` (Pass-2 body exists; scaffolding parity awaits Story 7a.5) | `test_row_23_irene_pass2_segment_manifest` |
| 24 | 08B Storyboard B + HIL Review | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-24` (awaits Story 7a.4) | `test_row_24_storyboard_b_hil_review` |
| 25 | 09 Gate 3 Lock Pass 2 Package | `gate_code=G3` active pause point from `app.manifest.compiler.production_gate_ids(live_manifest)` | `test_row_25_gate3_lock_pass2_package` |
| 26 | 10 Fidelity + Quality Pre-Spend | `gate_code=G4` active pause point from `app.manifest.compiler.production_gate_ids(live_manifest)` | `test_row_26_fidelity_quality_pre_spend` |
| 27 | 11 ElevenLabs Voice Selection HIL | `specialist_id=elevenlabs` canonicalizes to `enrique` per `SPECIALIST_ALIASES` | `test_row_27_voice_selection_hil` |
| 28 | 11B ElevenLabs Input Package HIL | `specialist_id=elevenlabs` canonicalizes to `enrique` per `SPECIALIST_ALIASES` | `test_row_28_elevenlabs_input_package_hil` |
| 29 | 12 ElevenLabs Audio Generation | `see app/specialists/enrique/graph.py` (active-mode parity awaits Slab 7b) | `test_row_29_elevenlabs_audio_generation` |
| 30 | 13 Quinn-R Pre-Composition QA | `specialist_id=quinn-r` canonicalizes to `quinn_r` per `SPECIALIST_ALIASES` | `test_row_30_quinn_r_pre_composition_qa` |
| 31 | 14 Compositor Assembly Bundle (legacy Descript GUI + manual file selection) | `skills/compositor/scripts/compositor_operations.py` back-compat CLI and Marcus G3 dispatch via `app.specialists.compositor.graph:build_compositor_graph`; H-Pipeline pointer: `tests/end_to_end/test_compositor_pipeline_determinism.py` | `test_row_31_compositor_assembly_bundle` |
| 32 | 14.5 Desmond Run-Scoped Operator Brief | `see app/specialists/desmond/graph.py` (brief parity awaits later operator-doc story) | `test_row_32_desmond_operator_brief` |
| 33 | 15 Operator Handoff - Descript Ready | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-33` (final handoff parity awaits Story 7a.8) | `test_row_33_operator_handoff_descript_ready` |

## Slab 7b Body Activation Rows (FR104; +11 rows)

**Authority.** FR104 +11-row supplement; one row per Slab 7b body-activated specialist. Distinct from the 33-row SG-2 floor above; SG-2 preserved at 33. Party-mode-authorized at Slab 7b epics-and-stories Round-(d) close 2026-04-29 (FR104 binding consensus).

Each row records: legacy v4.2 lever → migrated specialist lane → back-compat shim status → end-to-end test pointer (per FR110 template).

| # | Specialist | Class | Legacy v4.2 lever | LangGraph migrated lane | Back-compat shim | End-to-end test pointer |
|---|---|---|---|---|---|---|
| B1 | Texas | A | `[bundle]/02-source-authority-map.md` Pass-1 retrieval | `app.specialists.texas` 9-node scaffold + `dispatch_retrieval(*, directive_path, bundle_dir)` | None (FR89 hardening; fixture-stub fallback removed) | `tests/parity/test_texas_activation_contract.py`, `tests/specialists/texas/test_texas_six_canonical_artifacts.py` |
| B2 | Quinn-R | A | Pre-composition + post-composition QA (Storyboard-A authorize gate) | `app.specialists.quinn_r` 9-node scaffold + `quality_control_dispatch.py` + `sensory_bridges_dispatch.py` | None (G5 contract preserved via shared dispatch helpers) | `tests/parity/test_quinn_r_activation_contract.py`, `tests/specialists/quinn_r/test_quinn_r_act_node_dispatch.py` |
| B3 | Vera | A | Pass-2 G4 fidelity assessment | `app.specialists.vera` 9-node scaffold + `sensory_bridges_dispatch.py` | None (G4 rubric preserved; consumed by Quinn-R) | `tests/parity/test_vera_activation_contract.py`, `tests/specialists/vera/test_vera_act_node_dispatch.py` |
| B4 | Irene Pass-1 | B | Lesson-plan coauthoring + scope-lock contract | `app.specialists.irene_pass1` 9-node scaffold (NEW dir; separate from Pass-2 `irene/`) + shared sanctum at `bmad-agent-content-creator/` | Pass-2 unchanged at `app.specialists.irene/` | `tests/parity/test_irene_pass1_activation_contract.py`, `tests/specialists/irene_pass1/test_irene_pass1_lesson_plan_coauthor.py` |
| B5 | Tracy | C+ | Pass-2 research-shaped intent enrichment for Texas retrieval | `app.specialists.tracy` 9-node scaffold + `posture_dispatch.py` (consumed) → emits RetrievalIntent shape per `skills/bmad-agent-texas/references/retrieval-contract.md` | Legacy `posture_dispatch.py` consumed unchanged | `tests/parity/test_tracy_activation_contract.py`, `tests/composition/test_tracy_to_texas_chain.py` |
| B6 | Gary | C | Gamma slide generation + export | `app.specialists.gary` 9-node scaffold + `gamma_dispatch.py` (consumed) + `gamma_client.py` API | Legacy `gamma_dispatch.py` consumed unchanged | `tests/parity/test_gary_activation_contract.py`, `tests/specialists/gary/test_gary_storyboard_generation.py` |
| B7 | Kira | C | Kling motion generation (image-to-video / text-to-video) | `app.specialists.kira` 9-node scaffold + `kling_client.py::generate_motion()` submit-and-poll | Legacy fixture-replay path preserved as VCR cassette source | `tests/parity/test_kira_activation_contract.py`, `tests/specialists/kira/test_kira_motion_generation.py` |
| B8 | Enrique | C | ElevenLabs voice-selection HIL + narration synthesis + assembly-bundle audio/captions | `app.specialists.enrique` 9-node scaffold + `elevenlabs_client.py` API + voice-selection HIL artifacts (`voice-preview-options.json` / `voice-selection-review.md` / `voice-selection.json`) | `enrique` ↔ `elevenlabs` SPECIALIST_ALIASES per `app/manifest/compiler.py:43-46` | `tests/parity/test_enrique_activation_contract.py`, `tests/specialists/enrique/test_enrique_voice_selection_hil.py`, `tests/specialists/enrique/test_enrique_assembly_bundle_build.py` |
| B9 | Wanda | C | Wondercraft podcast/audio bed generation | `app.specialists.wanda` 9-node scaffold + `wondercraft_client.py` API → `assembly-bundle/audio/beds/` | Legacy `wondercraft_dispatch.py` consumed unchanged | `tests/parity/test_wanda_activation_contract.py`, `tests/specialists/wanda/test_wanda_audio_bed_generation.py` |
| B10 | Dan | D1 | (greenfield; no legacy lever) | `app.specialists.dan` 9-node scaffold + LLM-only via shared facade; aux contributions at G1/G1A/G2 (creative-director critique on prose only) | None (greenfield; `dan-api-tbd-pending` retired LLM-only at 7b.10 T1) | `tests/parity/test_dan_activation_contract.py`, `tests/specialists/dan/test_dan_aux_contributions_g1_g2.py` |
| B11 | Compositor | D2 | Legacy Descript GUI + manual file selection at G3 (referenced from row 31 above) | `app.specialists.compositor` 9-node scaffold + deterministic pipeline (sync-visuals + DESCRIPT-ASSEMBLY-GUIDE.md regeneration with field-masked-hash modulo `{generated_at, run_id, build_timestamp}`); H-Pipeline ≥99% rate per D17 | `skills/compositor/scripts/compositor_operations.py` back-compat CLI preserved | `tests/parity/test_compositor_activation_contract.py`, `tests/specialists/compositor/test_compositor_sync_visuals_deterministic.py`, `tests/parity/test_pipeline_determinism_harness.py` |
