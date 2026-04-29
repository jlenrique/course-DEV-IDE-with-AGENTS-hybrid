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
| 31 | 14 Compositor Assembly Bundle | `specialist_id=compositor` is registry-only until Slab 7b Category-E generation | `test_row_31_compositor_assembly_bundle` |
| 32 | 14.5 Desmond Run-Scoped Operator Brief | `see app/specialists/desmond/graph.py` (brief parity awaits later operator-doc story) | `test_row_32_desmond_operator_brief` |
| 33 | 15 Operator Handoff - Descript Ready | `see docs/operator/legacy-vs-langgraph-control-parity.md#row-33` (final handoff parity awaits Story 7a.8) | `test_row_33_operator_handoff_descript_ready` |
