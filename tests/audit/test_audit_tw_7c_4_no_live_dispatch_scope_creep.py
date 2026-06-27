from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATHS = {
    "scripts/utilities/run_cache_hit_harness.py",
    "scripts/utilities/run_5_api_smoke.py",
}
PERMITTED_PYTHON_DIFFS = {
    *HARNESS_PATHS,
    "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py",
    "tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py",
    "tests/trial/test_trial3_readiness.py",
    # Trial-3-blocking wiring fix 2026-05-21 (sprint-change-proposal-2026-05-21-trial3-wiring.md):
    # §02A LLM-driven composer was authored at Story 7c.3a but never wired into the
    # trial CLI; G0 directive composition was still invoking the legacy Story-7a.1
    # naive corpus-scan fallback. Party-mode-ratified Round 1 4-of-4 APPROVE-with-
    # amendments (Winston W-A1 lifted adapter to app/composers/section_02a/cli_adapter.py
    # so future consumers reuse the call-shape bridge). Bounded 2-path extension;
    # freeze predicates (line 56 + line 65) remain in force for all other paths.
    "app/marcus/cli/trial.py",
    "app/composers/section_02a/cli_adapter.py",
    # SCP 2026-05-21 §7 M-A1: new adapter wiring-contract tests authored as
    # part of C2a; allowlisting per same C1 substrate-amendment scope.
    "tests/marcus_cli/__init__.py",
    "tests/marcus_cli/test_compose_section_02a_directive_adapter.py",
    # Epic 34 §02A downstream-consumer coherence amendment 2026-05-22
    # (sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md):
    # Phase B Quinn-synthesis ratified Option 5 "Round-Trip First, Then Harmonize."
    # 7-story Epic resolving §02A→wrangler→pre_packet schema drift surfaced by
    # Trial-3 attempt-2 (run-id 6a3393f8-...). SCP-ratification party-mode Round
    # 1 (2026-05-22): 4-of-4 APPROVE-with-amendments (W-SCP-A1 + A-A1/A-A2/A-A3
    # + M-Murat-SCP-1..3 + A-John-1/A-John-2). 27-path bounded extension across
    # the §02A composer package + Texas wrangler script + Marcus intake + new
    # integration-test paths + temporary translator scaffolding + §02A test
    # surface for src_id→ref_id migration + legacy composer test surface for
    # Story 34-6 rewire/delete. Freeze predicates (L79 app_scope bind / L84
    # `app_scope == []` assert + L89 unexpected bind / L96 `unexpected == []`
    # assert) remain enforced for all non-allowlisted paths.
    #
    # Story 34-1 — NEW temporary in-tree translator scaffolding (deleted at
    # Story 34-7 per NFR-E34-10 hard AC); integration-test ship-proof.
    "app/composers/section_02a/_wrangler_translator.py",
    "tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py",
    # Story 34-1 fixture-dir defensive (Murat seam): pre-bind in case Codex T1-T9
    # emits any .py under fixture dir (__init__.py / conftest.py). Fixture data
    # files (.yaml/.md/.txt) escape the *.py-scoped predicate at audit-file L64.
    "tests/fixtures/integration/section_02a/__init__.py",
    "tests/fixtures/integration/section_02a/conftest.py",
    # Story 34-2 — wrangler input validator: 6-role union + excluded_reason
    # + cross-field invariants (Winston A1 + Murat M-Murat-3 bindings).
    "skills/bmad-agent-texas/scripts/run_wrangler.py",
    # Trial-3 attempt-3 crash fix 2026-06-11 (run-id 235e0570-...): production
    # dispatch invoked the wrangler subprocess with cwd=REPO_ROOT while the
    # §02A composer emits corpus-relative locators — every local_file fetch
    # failed File-not-found → empty bundle → RetrievalScopeError at Texas
    # hardening (observed_words=7 vs floor=570). Fix mirrors the Story 34-1
    # ratchet's pinned invocation contract (cwd=directive.corpus_dir) in
    # app/specialists/texas/retrieval_dispatch.py + pins the cwd contract in
    # the dispatch test (the prior kwargs-pin only asserted cwd truthy).
    # Bounded 3-path extension; freeze predicates remain in force. Second
    # finding in the same crash arc: _act.py's exit-10 -> "no-results"
    # early-return discarded valid complete_with_warnings bundles (903
    # extracted words dropped); the wrangler taxonomy has no "no-results"
    # status. Exit-10 bundles now parse exactly like exit 0.
    "app/specialists/texas/retrieval_dispatch.py",
    "app/specialists/texas/_act.py",
    "tests/specialists/texas/test_texas_act_node_dispatch.py",
    # Third finding, same trial arc: CANONICAL_SPECIALIST_IDS never adopted
    # irene_pass1 (a distinct §04 specialist package the compiler's
    # SPECIALIST_ALIASES already targets) — first live §04 dispatch crashed
    # at emit_spans with "unknown specialist_id". Roster 11 -> 12 with
    # coordinated shape-pin bump in test_run_summary_yaml_emit.py.
    "app/models/state/specialist_summary_artifacts.py",
    "tests/integration/marcus/test_run_summary_yaml_emit.py",
    # Fifth finding, same trial arc (party-mode 4-of-4 Option-A consensus
    # 2026-06-11): resume_production_trial had NO gate-pause machinery —
    # raised GateBypassError at every gate in live mode; no live trial
    # could advance gate-to-gate. Fix: _pause_at_gate extracted verbatim
    # from the start-path gate branch (commit 1, proven by unmodified
    # marcus suite) and wired into the resume walker (commit 2); the
    # defect-pinning test rewritten to pin pause-at-next-gate.
    "app/marcus/orchestrator/production_runner.py",
    "tests/integration/marcus/test_gate_bypass_refusal.py",
    "tests/integration/marcus/test_production_runner_gate_pause_resume.py",
    # 5-fix batch bmad-code-review remediation 2026-06-11 (party-mode
    # guardrail #3 discharge; findings ledger in deferred-work.md §code
    # review of trial-3-five-fix-batch). Lint-only on graph.py (ruff I001
    # import-sort + F401 unused yaml — pre-existing nits queued into the
    # batch review); env-robustness fixes in the two test files (editor
    # PATH stub + composer seam stub; facade sweep list tracks the Story
    # 34-6 intake.py deletion). No dispatch-surface behavior change.
    "app/specialists/texas/graph.py",
    "tests/integration/marcus/test_directive_confirm_or_edit_prompt.py",
    "tests/integration/marcus/test_facade_identity_invariant.py",
    # Trial-3 finding #9 fix 2026-06-11 (cd-directive-validator-prompt-
    # contract-mismatch, deferred-inventory TRIAL-4-RESUME-BLOCKING): the
    # creative-directive validator's parity rule requires the directive's
    # slide_mode_proportions + 11-key narration_profile_controls to EXACTLY
    # equal the chosen profile's targets in experience-profiles.yaml, but
    # CD's prompt never carried those values — the LLM had to invent them,
    # failing 2/2 live rolls systematically. Fix: prompt embeds the
    # authoritative targets; parse path canonicalizes the directive
    # deterministically from {experience_profile, creative_rationale}
    # (Hourglass: deterministic neck fills parity-bound values); parse
    # failures now capture a raw-response excerpt + validator error list.
    # load_experience_profile_targets() added to the validator module as
    # the single source of truth. Bounded 3-path extension; freeze
    # predicates remain in force.
    "app/specialists/cd/graph.py",
    "scripts/utilities/creative_directive_validator.py",
    "tests/specialists/cd/test_cd_act_node_dispatch.py",
    # Trial-3 finding #10 fix 2026-06-11 (attempt-4 first resume crash):
    # first-ever live Quinn-R dispatch (§07B, open throttle) raised
    # ModeMismatchError('') — two-layer gap: (1) production dispatch never
    # threaded the manifest node's gate context (Texas-only A-R3 seam;
    # resume walker passed no runner payload at all); (2) GATE_MODES only
    # covered 3 of Quinn-R's 5 manifest gates (G2B variant-selection + G2F
    # motion-gate had no bodies). Fix: _runner_payload_for_specialist gains
    # gate_code -> {"gate_id": ...} for quinn-r at both walk sites; Quinn-R
    # gains dedicated minimal G2B/G2F bodies (mapping onto "pre" would write
    # a premature authorized-storyboard at §07B; "post" assumes a composed
    # artifact absent at G2F). Manifest-coverage lockstep test pins against
    # a recurrence. Fourth A23/P5 instance in the trial-launch arc. Bounded
    # 2-path extension (production_runner.py already allowlisted above);
    # freeze predicates remain in force.
    "app/specialists/quinn_r/_act.py",
    "tests/specialists/quinn_r/test_quinn_r_g2b_g2f_gate_modes.py",
    # P2-1 fidelity detector 2026-06-19 (spec-p2-1-fidelity-detector-red-first.md;
    # epics-perception-reading-path-fidelity.md; Tier-3 party green-light 5/5).
    # Fail-loud fidelity detector (RED-first) + shared PerceptionArtifact contract.
    # Detector is pure/deterministic; G5 now requires perception_artifacts. P2-1
    # is lockstep-clean (none of these are block_mode_trigger_paths). Bounded extension.
    "app/models/perception/__init__.py",
    "app/models/perception/perception_artifact.py",
    "app/specialists/quinn_r/fidelity_detector.py",
    "app/specialists/quinn_r/quality_control_dispatch.py",
    "tests/specialists/quinn_r/test_fidelity_detector.py",
    "tests/specialists/test_audio_segment_grounding.py",
    "tests/parity/test_quinn_r_activation_contract.py",
    # P2-2 PNG-grounded perception producer 2026-06-20. Adds the normal
    # house-scaffold vision specialist, additive PerceptionArtifact fields,
    # G5 projection/enforcement pins, and quarantined repeatability/canary
    # tests. Bounded P2 perception arc extension; freeze predicates remain.
    "app/specialists/vision/__init__.py",
    "app/specialists/vision/_act.py",
    "app/specialists/vision/graph.py",
    "app/specialists/vision/payload_contract.py",
    "app/specialists/vision/provider.py",
    "app/specialists/vision/repeatability.py",
    "app/specialists/vision/state.py",
    "tests/models/perception/test_perception_artifact_schema_parity.py",
    "tests/specialists/quinn_r/test_ac12_detector_red_on_produced_artifact.py",
    "tests/specialists/quinn_r/test_quinn_r_g5_perception_enforcement.py",
    "tests/specialists/vision/test_vision_live_roundtrip.py",
    "tests/specialists/vision/test_vision_provider_and_act.py",
    "tests/specialists/vision/test_vision_repeatability.py",
    "tests/specialists/vision/test_vision_silent_drift_canary.py",
    # P1 voice-agnostic WPM floor 2026-06-19 (spec-p1-voice-agnostic-wpm-floor.md;
    # beta-phase-1-closure-ratification-2026-06-19.md §5, party-mode §2 green-light).
    # G5 WPM check changed from deviation-from-target band to a voice-agnostic
    # intelligibility band [110,200] so a non-default voice (Sarah, 128 WPM) is no
    # longer falsely failed. quinn_r/_act.py already allowlisted above (finding #10);
    # this adds only the G5 QA test surface. Bounded 1-path extension.
    "tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py",
    # LOC-budget guard bumped 150->160 for the two new gate bodies (same fix).
    "tests/specialists/quinn_r/test_quinn_r_act_node_dispatch.py",
    # SCP 2026-06-11 segment-data-plane S0 (party-mode 4-of-4 + operator-
    # ratified): fail-loud policy sweep — absence of inputs is a contract
    # violation, never a mode switch. Five dispatch seams converted from
    # silent fixture fallback to typed raise with explicit allow_fixture
    # opt-in (test-harness only; production_runner/dispatch_adapter pinned
    # to never set it). Trial-3 attempt-4 evidence: gary fixture slides
    # entered a production envelope and two gates blessed them. Conversions
    # only — no new implementations (John S0 scope guard).
    "app/specialists/gary/gamma_dispatch.py",
    "app/specialists/kira/kling_dispatch.py",
    "app/specialists/vera/sensory_bridges_dispatch.py",
    "app/specialists/quinn_r/sensory_bridges_dispatch.py",
    "tests/integration/test_dispatch_fail_loud_policy.py",
    "tests/specialists/gary/test_gary_dispatch_wrapper.py",
    "tests/composition/test_tracy_to_texas_chain.py",
    "tests/specialists/vera/test_vera_sensory_bridges_dispatch.py",
    "tests/specialists/quinn_r/test_quinn_r_dispatch_wrappers.py",
    "tests/specialists/kira/test_kira_kling_dispatch.py",
    # Same S0 sweep: kira/_act.py's "legacy_receipt" dispatch existed only to
    # harvest the fixture MP4 path as a silent video-URL fallback — removed;
    # quinn_r two-mode test payload now supplies a real artifact for G3B.
    "app/specialists/kira/_act.py",
    "tests/specialists/quinn_r/test_quinn_r_two_mode_dispatch.py",
    # S1 contract regime (same SCP): CONSUMED_PAYLOAD_KEYS contracts for
    # quinn_r + gary (own modules — quinn_r/_act.py carries a LOC budget) +
    # Ratchet-D manifest<->consumer vocabulary lockstep test with pinned
    # quarantine roster. Manifest 07B edge corrected (upstream_output:vera
    # -> slides:gary) — data-plane-only; generator does not render
    # dependencies; L1 lockstep exit 0; pack file untouched.
    "app/specialists/quinn_r/payload_contract.py",
    "app/specialists/gary/payload_contract.py",
    "tests/contracts/test_manifest_payload_contracts.py",
    # S2 envelope v2 (same SCP): per-node contribution keying. node_id +
    # attempt on SpecialistContribution (nullable -> legacy v1 envelopes
    # deserialize unchanged); schema_version v2 default with v1 read-only;
    # add_contribution: same-(specialist,node) retry overwrites w/ attempt
    # provenance, multi-node specialists accumulate per node (Path-Z
    # per-specialist skip retired — it silently dropped irene_pass1's
    # 05/05B jobs); adapter duplicate-guard node-aware IN THE SAME CHANGE
    # as the walker skip-rule (Amelia live-crash trap); dependency
    # resolution -> latest_for_specialist; resume REJECTS v1 envelopes
    # loudly (LegacyEnvelopeSchemaError; relaunch-as-cycle-2 ruling).
    "app/models/runtime/production_envelope.py",
    "app/marcus/orchestrator/dispatch_adapter.py",
    "tests/integration/marcus/test_production_envelope_node_keying.py",
    "tests/integration/marcus/test_path_z_first_contribution_wins_with_persistence.py",
    "tests/unit/runtime/test_production_envelope_strict.py",
    # S2 mechanical sweep: every walker-test _FakeAdapter gains the node_id
    # kwarg and stamps it (the runner's post-invoke lookup is node-pinned);
    # repeated-specialist test re-pinned to per-node semantics.
    "tests/integration/marcus/test_production_runner_invocation.py",
    "tests/integration/marcus/test_production_runner_dependency_resolution.py",
    "tests/integration/marcus/test_production_runner_resume_continues_execution.py",
    "tests/integration/marcus/test_production_clone_launch_evidence_discipline.py",
    # (test_run_summary_yaml_emit.py already allowlisted above at the
    # irene_pass1 roster fix — S2 touched it again for node_id stamping.)
    # S3 package builders (same SCP): §06 pre-dispatch builder as a pure
    # deterministic module (no LLM in the neck per regime), invoked by both
    # walkers at its manifest node (pre_gate_marcus pattern), emitting a
    # first-class contribution; Gary receives the package via the A-R3 seam
    # (granular keys; dependency-map merge is whole-dict-per-key — spread
    # question filed for party review); Quinn-R receives Gary's slide rows
    # under its declared "slides" key.
    "app/marcus/orchestrator/package_builders.py",
    "tests/integration/marcus/test_package_builders.py",
    # Party-review amendment batch 2026-06-12 (S0-S3 4-voice APPROVE-with-
    # amendments): seam/dependency collision raise in the adapter; 07B
    # shape-lying edge withdrawn pending S4 projection; contract imports
    # bound through act namespaces; presence checks -> latest_for_specialist
    # + bare-get_contribution static pin; spread key-roster pin; seam
    # tombstone; starved-cap §06 regression (finding #8 pinned); platform
    # fixture-grep ratchet (Murat MUST-FIX-BEFORE-S5) — which caught a
    # SEVENTH seam on its first run: wanda's MB music-bed returned a mocked
    # receipt unconditionally (missed in the S0 sweep via grep truncation);
    # now gated behind allow_fixture. Old runner-keys-win collision pin
    # superseded by the refuse-loud pin. Contract imports touched gary/_act.
    "tests/audit/test_no_silent_fixture_fallbacks.py",
    "app/specialists/wanda/wondercraft_dispatch.py",
    "app/specialists/wanda/_act.py",
    "app/specialists/gary/_act.py",
    "tests/integration/marcus/test_production_runner_threads_directive.py",
    # S4 (same SCP; party-review riders executed): ProjectionSpec +
    # dependency_projections + data_plane_vocabulary_version on the manifest
    # schema (Winston S1-B + Deviation-2: projection, not spread); adapter
    # projection resolution with refuse-loud missing-producer/key/collision;
    # provenance real|fixture on contributions with envelope-writer
    # rejection; builder id marcus -> package_builder; seam slimmed to
    # runner context only (tombstone deliberately rewritten).
    "app/manifest/schema.py",
    # S4 part 2 (same SCP; Winston d.2 + Amelia trap 1): shared
    # SpecialistDispatchError base (six S0 seam classes re-based onto it);
    # single _dispatch_specialist_at_node call site for both walkers;
    # typed dispatch failure -> paused-at-error + error-pause.json instead
    # of cycle death; _continue_production_walk shared by resume + the new
    # verdict-less recover_production_trial; `trial recover` CLI subcommand.
    "app/specialists/dispatch_errors.py",
    "app/models/runtime/production_trial_envelope.py",
    "app/marcus/cli/__main__.py",
    "tests/integration/marcus/test_production_runner_error_pause_recover.py",
    # Drift micro-batch 2026-06-12 (party consensus + Dr. Quinn "witness,
    # don't gate" synthesis; operator GO): retired top-level `marcus`
    # namespace strings canonicalized to app.marcus / app/marcus across
    # registries + docstring cross-references (import-linter M5 is blind to
    # strings; the stale rows crashed build_coverage_manifest); two layered
    # string-path pins (importlib resolution + prefix grep-ratchet);
    # composition-spec docs-version lockstep pin; two-mode trial-envelope
    # lifecycle validator (witness default at runtime, strict in tests) +
    # characterization round-trip suite; runner load sites pass the
    # anomaly-sink context.
    "app/marcus/intake/__init__.py",
    "app/marcus/lesson_plan/component_type_registry.py",
    "app/marcus/lesson_plan/coverage_manifest.py",
    "app/marcus/lesson_plan/events.py",
    "app/marcus/lesson_plan/fit_report.py",
    "app/marcus/lesson_plan/gagne_diagnostician.py",
    "app/marcus/lesson_plan/log.py",
    "app/marcus/lesson_plan/modality_registry.py",
    "app/marcus/lesson_plan/schema.py",
    "app/marcus/orchestrator/loop.py",
    "app/marcus/orchestrator/maya_walkthrough.py",
    "app/marcus/orchestrator/write_api.py",
    "tests/test_coverage_manifest_regenerates_on_current_state.py",
    "tests/contracts/test_lesson_plan_string_path_resolution.py",
    "tests/contracts/test_composition_spec_envelope_version_lockstep.py",
    "tests/unit/runtime/test_production_trial_envelope_invariants.py",
    "tests/parity/test_composition_spec_invariants.py",
    # Renderer/L1 story 2026-06-12 (🔴 MUST-FIX-BEFORE-S5, drift-audit fold;
    # Tier-1: classification fix + guard hardening, no pack structural
    # change): shared is_orchestration_only predicate (app/manifest/schema);
    # generator skips runtime-only orchestration nodes instead of fabricating
    # template names (MissingSectionTemplateError raises early); ratified S1
    # pack hand-edits folded back into templates (A12 counter-pattern:
    # header/banner/§0.5 partials, PP-1 enrique, §3.g deletion, xref); L1
    # gains Check 9 regeneration-determinism (render crash → exit 2; SHA
    # mismatch → exit 1; previously NEVER rendered = vacuous guard); Pin A
    # roster-derived render loop + Pin B red-tests; stale 33-node
    # characterizations re-derived through the predicate.
    "scripts/generators/v42/manifest.py",
    "scripts/generators/v42/render.py",
    "scripts/utilities/check_pipeline_manifest_lockstep.py",
    # Pre-S5 recon fix 2026-06-12: §07 exportUrl download/materialize leg in
    # gary _paths_from_generation (generate_deck never downloads; rows landed
    # file_path "" → Storyboard A at G2C would have had no viewable slides).
    "tests/specialists/gary/test_gary_export_url_materialization.py",
    # Trial-3 cycle-2 root cause (2026-06-12, caught AT the G2C pause):
    # Gamma POST ack is camelCase generationId → generate_deck never polled →
    # bare ack → gary's fixture-id sentinel (EIGHTH seam) masked it → seven
    # empty-file_path rows reached G2C. Fixes: camelCase key in client id
    # extraction; sentinel → GammaDispatchError(gamma.generation.id-missing);
    # all-empty file_path → GammaDispatchError(gamma.export.unmaterialized)
    # (both recoverable via error-pause + trial recover); ratchet gains the
    # fabricated fixture-id signature.
    "scripts/api_clients/gamma_client.py",
    "tests/specialists/gary/test_gary_generation_id_fail_loud.py",
    "tests/unit/api_clients/__init__.py",
    "tests/unit/api_clients/test_gamma_client_generation_id.py",
    # Content-plane batch (Trial-3 cycle-2/3 codification, operator-directed
    # 2026-06-12): shared fail-loud source-bundle reader (SpecialistDispatch-
    # Error family → error-pause + recover, proven live twice at §05);
    # irene_pass1 + cd prompts lead with the extracted corpus (cycle-2
    # confabulation root cause); irene_pass1 publishes CONSUMED_PAYLOAD_KEYS
    # (first Ratchet-D quarantine retirement); manifest 05/05B gain
    # bundle_reference projections from texas (dp-v1).
    "app/specialists/source_bundle.py",
    "app/specialists/irene_pass1/_act.py",
    "app/specialists/irene_pass1/graph.py",
    "app/specialists/irene_pass1/payload_contract.py",
    # (test_manifest_payload_contracts.py already rostered above)
    # S5 criterion 7 (operator-ratified 2026-06-12): automatic ONLINE
    # storyboard publication at storyboard review gates — publisher seam
    # invoking the proven legacy generate-storyboard routine; wired into
    # both live gate-pause paths with error-pause on failure; G0
    # auto-confirm flag honored unconditionally (Windows NUL isatty lie).
    "app/marcus/orchestrator/storyboard_publisher.py",
    "tests/integration/marcus/conftest.py",
    "tests/integration/marcus/test_storyboard_publisher.py",
    "tests/integration/marcus/test_storyboard_generator_seam_handshake.py",
    "tests/specialists/irene_pass1/test_irene_pass1_lesson_plan_authoring.py",
    "tests/generators/v42/test_renderer_classification_and_l1_fail_loud.py",
    "tests/generators/v42/test_red_path_fixtures.py",
    "tests/contracts/test_33_1a_verbatim_extraction.py",
    "tests/end_to_end/test_full_pipeline_smoke.py",
    "tests/test_33_3_dc2_resolution.py",
    # dp-v1.1 — Trial-3 cycle-4 08/08B remediation (party consensus
    # 2026-06-12, Winston/Amelia/Murat/John): node 08 grounding (Irene Pass 2
    # received cache_prefix only → sepsis narration from L5 exemplars —
    # fourth ungrounded-prompt instance) + 08B storyboard-B body (G3B "post"
    # mapping crashed live on sensory.input.missing; Storyboard B = A pack +
    # Pass-2 narration overlay, published online per S5 criterion 7).
    "app/specialists/irene/graph.py",
    "app/specialists/irene/payload_contract.py",
    # P5 directed-voice arc Step 2 (2026-06-27): the SEPARATE, pure, post-freeze
    # voice-direction annotation pass (IR-1) wired into graph.py's Pass-2 seam
    # AFTER the figure-citation gate. Pure leaf, no live dispatch; flag-gated
    # (MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE, default OFF ⇒ byte-identical).
    "app/specialists/irene/authoring/voice_direction_annotation.py",
    # P5 directed-voice Step-2 RED-first proof: pure-pass grounding-non-regression
    # (MUR-2 byte-identity) + precedence/provenance/determinism pins, and the
    # emission-wiring pins (flag OFF byte-identical / flag ON attaches / figure-
    # gate firewall stays clean). Offline/deterministic; no live dispatch.
    "tests/specialists/irene/test_voice_direction_annotation.py",
    "tests/specialists/irene/test_voice_direction_emission_wiring.py",
    # dp-v1.2 — audio-segment arc (party consensus 2026-06-12, operator
    # full-delegation completion directive): enrique grounded via Pass-2
    # narration projections (cycle-5 ran §11-12 ungrounded → zero audio);
    # quinn_r G5 grounded + fabricated slide-1 roster killed + content
    # errors re-based to the recoverable dispatch family (the bare
    # ValueError form crashed cycle-5 and lost walk progress); compositor
    # pre-grounded (convicted by construction); shared narration join
    # (one policy home for publisher + enrique + G5).
    "app/specialists/narration_join.py",
    "app/specialists/enrique/_act.py",
    "app/specialists/enrique/payload_contract.py",
    # P5 directed-voice arc Step 4 (2026-06-27): Enrique consumes per-segment
    # voice_direction. The shared 5-tier mapper gained the tier-4/5 default
    # loaders (load_style_guide_tts_defaults / voice_selection_default_tier /
    # normalize_optional_str); the ElevenLabs client surfaces the request-id
    # header (ENRIQUE-A2, additive method, no new live-dispatch call site — the
    # TW-7c-4 semantic detector stays GREEN); Storyboard B's generator gains the
    # effective-voice-source line + honest tier-3/4/5 header (carry). enrique/
    # _act.py + payload_contract.py already rostered above. Bounded, flag-gated
    # (MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE, default OFF ⇒ byte-identical).
    "app/specialists/_shared/voice_direction_map.py",
    "scripts/api_clients/elevenlabs_client.py",
    "skills/bmad-agent-marcus/scripts/generate-storyboard.py",
    "tests/specialists/enrique/test_enrique_directed_voice.py",
    "tests/specialists/enrique/test_enrique_directed_voice_remediation.py",
    "tests/specialists/enrique/_fake_elevenlabs.py",
    "tests/specialists/_shared/test_voice_direction_tier_defaults.py",
    "tests/test_elevenlabs_client.py",
    "tests/integration/marcus/test_storyboard_voice_direction_display.py",
    "app/specialists/compositor/_act.py",
    "app/specialists/compositor/payload_contract.py",
    "app/specialists/quinn_r/graph.py",
    "tests/specialists/test_narration_join_shared.py",
    "tests/contracts/test_specialist_error_taxonomy.py",
    "tests/specialists/irene/conftest.py",
    "tests/specialists/irene/test_irene_pass2_grounding_fail_loud.py",
    "tests/specialists/irene/test_irene_prompt_byte_stability_5x.py",
    "tests/specialists/irene/test_irene_pass_routing.py",
    "tests/specialists/irene/test_irene_act_node_pass2_procedures.py",
    "tests/specialists/irene/test_irene_act_node_llm_invocation.py",
    "tests/specialists/quinn_r/test_quinn_r_g3b_post_composition.py",
    "tests/composition/test_irene_pass_2_template_composition_smoke.py",
    "tests/end_to_end/test_cache_hit_rate_baseline.py",
    "tests/contracts/test_manifest_grounding_contract.py",
    # Taxonomy re-base live-path tranche (WAVE 0, rider
    # tagged-error-taxonomy-systematic-rebase, 2026-06-12): GaryActError /
    # ReceiptParseError / BundleParseError / KiraActError / FTRParseError
    # re-based onto SpecialistDispatchError (crash → error-pause; base is
    # RuntimeError-derived so all existing handlers preserved); gary's
    # fabricated slide-01 roster killed (gamma.slides.starved). Files
    # already rostered above are not repeated; the two new app-layer
    # touches plus the new pin test are:
    "app/specialists/gary/graph.py",
    "app/specialists/vera/_act.py",
    "tests/specialists/gary/test_gary_slides_starvation_pin.py",
    # Story 34-2 wrangler-side test (substrate-audit-corrected path 2026-05-22;
    # co-located with existing test_run_wrangler.py at skills/.../tests/).
    "skills/bmad-agent-texas/scripts/tests/test_run_wrangler_role_enum_union_and_excluded_reason.py",
    # Story 34-4 wrangler-side test (also under skills/.../tests/).
    "skills/bmad-agent-texas/scripts/tests/test_run_wrangler_sme_refs_emission.py",
    # Story 34-3 — §02A composer src_id → ref_id rename + J-A1(a)/(b)
    # cli_adapter completion (Winston A2 binding).
    "app/composers/section_02a/directive_model.py",
    "app/composers/section_02a/composer.py",
    "app/composers/section_02a/_prompt.py",
    "app/composers/section_02a/_cache.py",
    # Story 34-3 / 34-7 — §02A package __init__.py re-export surface
    # (Winston W-SCP-A1 + Amelia A-A2 2-voice consensus); covers both
    # field-rename ripple AND translator-deletion re-export prune.
    "app/composers/section_02a/__init__.py",
    # Story 34-3 — §02A test surface migration for `src_id → ref_id` rename
    # (Amelia A-A1 grep-verified hits across both composer + gate test trees).
    "tests/composers/section_02a/_helpers.py",
    "tests/composers/section_02a/__init__.py",
    "tests/composers/section_02a/test_composer_cache_key_normalization.py",
    "tests/composers/section_02a/test_composer_classification.py",
    "tests/composers/section_02a/test_composer_directive_model_shape.py",
    "tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py",
    "tests/composers/section_02a/test_composer_utf8_write.py",
    "tests/gates/section_02a/_helpers.py",
    "tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py",
    # Story 34-4 — wrangler metadata.json sme_refs additive emission;
    # pre_packet possibly minor touch (consumer side).
    "app/marcus/intake/pre_packet.py",
    # Story 34-5 — translator-shrinkage sequence test (carrier story).
    "tests/integration/test_section_02a_translator_shrinkage_sequence.py",
    # Story 34-7 — final translator deletion + round-trip simplification.
    "docs/dev-guide/specialist-anti-patterns.md",
    # Story 34-6 — legacy directive_composer.py DELETION; 7 test files
    # rewired or deleted (existing tests; deletion still counts as
    # `git diff` touch for the L79/L84 + L89/L96 predicates).
    "app/marcus/orchestrator/directive_composer.py",
    "tests/unit/marcus/orchestrator/test_directive_composer_pure.py",
    "tests/unit/marcus/orchestrator/test_directive_composer_materialization.py",
    "tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py",
    "tests/parity/test_trial_475_texas_hardening_regression.py",
    "tests/parity/test_trial_475_directive_composition_regression.py",
    "tests/composition/test_texas_to_cd_chain.py",
    "tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py",
    # Story 34-6 structural orphan cleanup after deleting the legacy composer.
    "tests/structural/test_directive_io_uses_utf8_explicit.py",
    # Storyboard-correctness fix 2026-06-18 (party-ratified spec-storyboard-
    # correctness-cover-shift; cycle-6 operator review root cause): Gary mapped
    # Gamma-exported pages to slide_ids POSITIONALLY, so the engine cover page
    # consumed slide-01 and shifted every content image down one (operator
    # Glitch #1 + #2 = one bug). Replaced with deterministic bijective
    # CONTAINMENT title matching (≥2-distinctive-token floor, all-edges
    # uniqueness, ambiguity-fatal) in the shared materializer; gary consumes the
    # slide-keyed MatchResult by slide_id (both positional zips dead) and
    # fail-louds brief-unmatched / page-unmatched / title-ambiguous. The
    # positional `_materialize_exported_slide_paths` is left byte-identical for
    # the brief-less standalone Gamma lane. Bounded extension; freeze predicates
    # remain in force for all other paths.
    "skills/gamma-api-mastery/scripts/gamma_operations.py",
    "tests/specialists/gary/test_gamma_title_matching.py",
    "tests/specialists/gary/test_gary_gamma_dispatch.py",
    # Arc 3 measured-durations 2026-06-18 (trial-4 backlog, party-classified
    # additive/low-risk): enrique probes the real synthesized mp3 (dep-free
    # frame-duration parser, no mutagen/ffprobe) and labels it "measured",
    # arming G5's WPM raise; non-mp3 fixtures fall back to the estimate (zero
    # folded/fixture behavior change). enrique/_act.py already allowlisted
    # above (dp-v1.2 audio batch); the new test file is added here.
    "tests/specialists/enrique/test_measured_durations.py",
    # Arc 1a manifest gate-split 2026-06-18 (trial-4 fold-semantics, party-
    # ratified spec-arc1a-manifest-gate-split): the 3 co-located voice/variant
    # HIL gates (G2B@07B, G4A@11, G4B@11B) were split into [content specialist]
    # + [content-free folded gate node] (07B-gate/11-gate/11B-gate) so a woken
    # pause lands AFTER content rather than before it. schema.py (is_folded_gate
    # / is_pack_excluded predicates), the v42 generator, and the L1 lockstep
    # script are already rostered above (S4 + renderer/L1 story). The new
    # touches are the router pass-through skip + the node-count pin bump + the
    # new structural-invariant pin file. Manifest YAML + regenerated pack are
    # not *.py (outside the fence). Bounded; freeze predicates remain in force.
    "app/marcus/orchestrator/routing.py",
    "tests/unit/manifest/test_compiler.py",
    "tests/unit/manifest/test_folded_gate_split.py",
    # Arc-1a A14 Tier-2 pack disposition (party-ratified Option A, Winston/
    # Amelia/Murat unanimous 2026-06-18): the determinism guard was repointed
    # from the now-frozen v4.2 mapping-axis anchor to the live generated witness
    # (`-gen`); a frozen-pack SHA registry (state/config/frozen-pack-shas.json,
    # not *.py) + its broad-suite mirror pin the v4.2 + v5 SHAs. These are the
    # repointed determinism tests + the new pin test (test infra only; no
    # live-dispatch surface). Pack .md / template .j2 / registry .json are
    # outside the *.py fence. Bounded; freeze predicates remain in force.
    "tests/contracts/test_33_3_no_hand_edits_to_v42.py",
    "tests/contracts/test_frozen_pack_shas.py",
    "tests/integration/lockstep/test_companion_assertion_per_path.py",
    "tests/test_33_3_dc1_resolution.py",
    "tests/test_33_3_dc3_resolution.py",
    # Arc-1a code-review remediation 2026-06-18 (3-lane bmad-code-review;
    # Blind Spot + Edge Case MUST/SHOULD-FIX): router pass-through-skip
    # regression tests + repointed the stale legacy `marcus/orchestrator/
    # routing.py` guard path to `app/marcus/...` (was FileNotFound-inert).
    "tests/unit/marcus/test_routing_manifest_driven.py",
    # Arc 2 membership wake of G2B (variant) + G4A (voice) HIL gates
    # (2026-06-18; party green-light APPROVE-WITH-CONDITIONS Winston/Amelia/
    # Murat/John, Claude-direct per operator). Clears fold_with on the two
    # gate nodes (manifest, not *.py) so they surface in production_gate_ids;
    # adds the G2B/G4A decision-card models + _build_decision_card branches the
    # green-light found missing (it raised RuntimeError); extends is_pack_excluded
    # (woken gates stay pack-invisible) + the ProductionGateId literal. Bounded;
    # the live pause path gains two gate ids, no new dispatch surface. Freeze
    # predicates remain in force for all other paths.
    "app/models/decision_cards/g2b.py",
    "app/models/decision_cards/g4a.py",
    "app/models/decision_cards/__init__.py",
    # (production_trial_envelope.py already allowlisted above at the trial-3 block)
    # Arc 2 3-lane review remediation (Blind Spot BLOCKER #1 + MUST-FIX #2/#4):
    # the live-only paths the offline test posture hid — operator CLI shims for
    # the woken gates + the m3_trial divergence note. (Pre-gate-marcus templates
    # g2b.j2/g4a.j2 are .j2, outside the *.py fence.)
    "app/marcus/cli/gate_shims/g2b_shim.py",
    "app/marcus/cli/gate_shims/g4a_shim.py",
    "app/marcus/cli/gate_shims/_shim_parser.py",
    "app/marcus/orchestrator/m3_trial.py",
    "app/models/trial3_transcript.py",
    "tests/unit/marcus/cli/test_shim_parser_factory.py",
    "tests/trial/test_trial3_transcript_shape.py",
    "tests/integration/marcus/test_woken_gate_cards.py",
    "tests/integration/marcus/test_marcus_duality_boundary.py",
    "tests/unit/manifest/test_manifest_fold_with_declarations.py",
    "tests/unit/manifest/test_gate_topology_cli.py",
    "tests/unit/manifest/test_production_gate_ids_derived.py",
    "tests/unit/manifest/test_gate_fold_manifest_emit.py",
}


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def test_tw_7c_4_detector_reports_no_fire() -> None:
    result = _run("scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"status": "PASS", "tripwire_id": "TW-7c-4", "violations": []}


def test_live_dispatch_python_scope_is_bounded() -> None:
    changed = set(_git_lines("diff", "--name-only", "HEAD", "--", "*.py"))
    untracked = set(_git_lines("ls-files", "--others", "--exclude-standard", "--", "*.py"))
    touched_python = changed | untracked

    # SCP 2026-05-21 §4.1 + C1b (Trial-3 wiring fix substrate amendment): the
    # `app_scope` predicate was originally a hard ban on all app/ Python edits,
    # not allowlist-aware. The 2026-05-19 SCP and 2026-05-21 Round-1 party-mode
    # ratification both reasoned only about the line-74 `unexpected` predicate;
    # the dual-predicate structure (line-65 + line-74) was a known-but-
    # underspecified seam. C1b folds line-65 into the same PERMITTED_PYTHON_DIFFS
    # allowlist mechanism so that ratified app/ edits (currently
    # app/marcus/cli/trial.py + app/composers/section_02a/cli_adapter.py) can
    # land without tripwire firing. Defense-in-depth is preserved: app/ edits
    # still require explicit allowlisting; non-app/ edits also still bounded by
    # line 74.
    app_scope = sorted(
        path
        for path in touched_python
        if path.startswith("app/") and path not in PERMITTED_PYTHON_DIFFS
    )
    assert app_scope == [], (
        f"TW-7c-4 fired: unauthorized app-layer Python touched (not in "
        f"PERMITTED_PYTHON_DIFFS): {app_scope}"
    )

    unexpected = sorted(
        path
        for path in touched_python
        if path not in PERMITTED_PYTHON_DIFFS
        and not path.startswith(".venv/")
        and not path.startswith("runs/")
    )
    assert unexpected == [], f"TW-7c-4 fired: unexpected Python scope: {unexpected}"


def test_named_harnesses_have_authored_live_dispatch_not_pending_stub() -> None:
    for rel_path in HARNESS_PATHS:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert "live_dispatch_pending_authoring" not in text
        assert "post-Slab-7c" in text


def test_default_harness_invocations_remain_fail_closed() -> None:
    cache_result = _run("scripts/utilities/run_cache_hit_harness.py", "--all-specialists")
    cache_payload = json.loads(cache_result.stdout)
    assert cache_result.returncode == 1
    assert cache_payload["verdict"] == "not_run"

    smoke_result = _run("scripts/utilities/run_5_api_smoke.py")
    smoke_payload = json.loads(smoke_result.stdout)
    assert smoke_result.returncode == 1
    assert smoke_payload["verdict"] == "not_run"
    assert [row["name"] for row in smoke_payload["apis"]] == [
        "gamma",
        "elevenlabs",
        "canvas",
        "qualtrics",
        "panopto",
    ]


def test_epic3_retirement_and_deferred_inventory_close_are_recorded() -> None:
    epic_text = (
        REPO_ROOT
        / "_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md"
    ).read_text(encoding="utf-8")
    assert "7c.21a retirement record" in epic_text
    assert "retired-via-7a+7b+7c" in epic_text
    for rel_path in (
        "_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md",
        "_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md",
        "_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md",
    ):
        assert rel_path in epic_text

    inventory_text = (
        REPO_ROOT / "_bmad-output/planning-artifacts/deferred-inventory.md"
    ).read_text(encoding="utf-8")
    assert "CLOSED 2026-05-07 via 7c.21a" in inventory_text
    assert "_codex-handoff/7c-21a.ready-for-review.md" in inventory_text
