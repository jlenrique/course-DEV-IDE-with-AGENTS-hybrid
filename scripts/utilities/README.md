# scripts/utilities — Operator + Dev Utility Index

55+ utility scripts categorized by lifecycle phase. Each script's docstring carries
authoritative usage; this index points you at the right script for the right task.

---

## TOP-LEVEL OPERATOR ENTRY POINTS (start here)

### Trial-run readiness
- **[`trial_run_preflight.py`](trial_run_preflight.py)** — 12-point readiness sweep. Run before any trial. Verifies env / Postgres / MCP / sanctums / manifests / frozen-graph / dispatch-registry / sanctum-watcher / Marcus baseline / trial corpus / migration state. Exit codes: 0=ready (warnings allowed), 1=non-required failures, 2=blocking failures.
- **[`migration_health_dashboard.py`](migration_health_dashboard.py)** — single-pane migration status (epic states + conditional milestones + deferred-inventory + import-linter + ruff debt + test collection + ledger + sanctum mutations 7d). Use for daily standup / post-Slab-close audit.
- **[`venv_health_check.py`](venv_health_check.py)** — Python venv health (deps installed; versions match pyproject pins).
- **[`app_session_readiness.py`](app_session_readiness.py)** — operator session-start readiness (legacy from primary repo; pre-migration substrate).

### Operator-window evidence (conditional gate addenda)
- **[`ac_b_op_texas_live_retrieval_evidence.py`](ac_b_op_texas_live_retrieval_evidence.py)** — Texas AC-B-OP M1-M5 live retrieval evidence helper (resolves M3 conditional per Slab 3.6). Operator runs in their window per `docs/operator/conditional-gate-addendum-playbook.md`.

---

## GOVERNANCE VALIDATORS (gate-mode + sandbox-AC + lockstep enforcement)

- **[`validate_migration_story_sandbox_acs.py`](validate_migration_story_sandbox_acs.py)** — sandbox-AC validator per CLAUDE.md (forbidden-CLI scan in dev-agent AC blocks). Run at story `ready-for-dev` and `bmad-dev-story` open.
- **[`validate_lesson_planner_story_governance.py`](validate_lesson_planner_story_governance.py)** — Lesson Planner Epic 28-32 governance enforcement (gate-mode, K-policy, scaffold reference, story-status sync).
- **[`check_pipeline_manifest_lockstep.py`](check_pipeline_manifest_lockstep.py)** — Epic 33 pipeline-manifest lockstep (8 deterministic checks; pre-commit hook integration).
- **[`check_manifest_lockstep.py`](check_manifest_lockstep.py)** — Slab 4.1 graph-compile-time CI hook (complementary to Epic 33; D6 compiler validation).
- **[`check_learning_event_lockstep.py`](check_learning_event_lockstep.py)** — Story 33-3 learning-event schema/capture lockstep (DC2 contract).
- **[`check_raw_http_guardrail.py`](check_raw_http_guardrail.py)** — raw HTTP usage guardrail (sandbox-AC adjacent; flags non-Python-dep HTTP CLI).
- **[`creative_directive_validator.py`](creative_directive_validator.py)** — creative-directive shape validation (legacy primary; pre-migration).
- **[`validate-operator-directives.py`](validate-operator-directives.py)** — operator-directive YAML schema validator.
- **[`validate_marcus_golden_trace_fixture.py`](validate_marcus_golden_trace_fixture.py)** — Marcus envelope baseline schema validation (Slab 3.6 W-R7 baseline).
- **[`validate_source_bundle_confidence.py`](validate_source_bundle_confidence.py)** — source-bundle confidence-score validator (texas adjacent).
- **[`validate_source_directory_scan_gate.py`](validate_source_directory_scan_gate.py)** — source-directory scan-gate validator.

---

## RUNTIME / DISPATCH (executed during trials or post-trial)

- **[`run_constants.py`](run_constants.py)** — runtime constants (per-trial run identifiers; loaded by Slab-1 substrate).
- **[`run_gary_dispatch.py`](run_gary_dispatch.py)** — Gary specialist dispatch invocation (Slab 2b.1 REST-API tool-dispatch precedent).
- **[`cluster_dispatch_trial.py`](cluster_dispatch_trial.py)** — cluster-mode dispatch trial (multi-node parallel dispatch).
- **[`verify_dispatch.py`](verify_dispatch.py)** — dispatch-receipt verification helper.
- **[`prepare-irene-packet.py`](prepare-irene-packet.py)** — Irene Pass-1 / Pass-2 input packet assembly (Slab 2a substrate).
- **[`marcus_prompt_harness.py`](marcus_prompt_harness.py)** — Marcus prompt-rendering harness (development debugging).

---

## OBSERVABILITY / DASHBOARDS

- **[`progress_map.py`](progress_map.py)** — per-trial progress visualization (HTML dashboard generator; pre-migration substrate).
- **[`run_hud.py`](run_hud.py)** — run-time HUD HTML dashboard (pre-migration substrate; long string literals exempt from E501 per pyproject).
- **[`emit_preflight_receipt.py`](emit_preflight_receipt.py)** — preflight receipt emission (legacy primary).
- **[`emit_ingestion_quality_receipt.py`](emit_ingestion_quality_receipt.py)** — ingestion quality receipt emission.
- **[`learning_event_capture.py`](learning_event_capture.py)** — Story 33-3 learning event capture (DC2 contract producer).

---

## TRACE + GOLDEN-FIXTURE OPERATIONS (Marcus baseline + envelope inspection)

- **[`capture_marcus_golden_trace.py`](capture_marcus_golden_trace.py)** — capture Marcus golden-trace fixture for regression baseline (Slab 3.6 W-R7 precedent).

---

## CONTENT PRODUCTION HELPERS (legacy primary repo; pre-migration)

- **[`build_image_source_bundle.py`](build_image_source_bundle.py)** — image source-bundle assembly.
- **[`fidelity_walk.py`](fidelity_walk.py)** — fidelity walk-tree analysis.
- **[`fix_slide_content.py`](fix_slide_content.py)** — slide content repair.
- **[`fix_test_file.py`](fix_test_file.py)** — test file repair.
- **[`slide_count_runtime_estimator.py`](slide_count_runtime_estimator.py)** — Story 20c-15 slide/runtime estimator.
- **[`motion_budgeting.py`](motion_budgeting.py)** — motion-pack budget calculation.
- **[`tracy_vocab_lockstep.py`](tracy_vocab_lockstep.py)** — Tracy vocab lockstep validation.
- **[`structural_walk.py`](structural_walk.py)** — structural walk-tree generator.
- **[`inspect_gary_output.py`](inspect_gary_output.py)** — Gary output inspection helper.

---

## DEV INFRASTRUCTURE (called by other tooling)

- **[`env_loader.py`](env_loader.py)** — .env loader helper (centralized; consumed by other scripts).
- **[`logging_setup.py`](logging_setup.py)** — standardized logging config.
- **[`file_helpers.py`](file_helpers.py)** — common file ops.
- **[`yaml_emitter.py`](yaml_emitter.py)** — YAML emit helper.
- **[`pipeline_manifest.py`](pipeline_manifest.py)** — pipeline manifest helper (re-export adjacent).
- **[`workflow_policy.py`](workflow_policy.py)** — workflow policy helper.
- **[`skill_module_loader.py`](skill_module_loader.py)** — skill module dynamic loading (used by Texas + others).
- **[`ffmpeg.py`](ffmpeg.py)** — ffmpeg wrapper (imageio-ffmpeg helper).
- **[`dev_mode.py`](dev_mode.py)** — development-mode flag helper.
- **[`ad_hoc_persistence_guard.py`](ad_hoc_persistence_guard.py)** — ad-hoc persistence-write guard (Quinn single-writer rule adjacent).
- **[`operator_polling.py`](operator_polling.py)** — operator-poll mechanism (legacy).
- **[`operator_directives_poll.py`](operator_directives_poll.py)** — operator-directives polling.
- **[`repair_validator.py`](repair_validator.py)** — validator-repair helper.
- **[`restore_validator_clean.py`](restore_validator_clean.py)** — clean-validator restoration.

---

## TEXT NORMALIZATION (encoding fixes)

- **[`find_mojibake.py`](find_mojibake.py)** — mojibake detection sweep.
- **[`normalize_mojibake.py`](normalize_mojibake.py)** — mojibake normalization fixes.
- **[`doc_drift_monitor.py`](doc_drift_monitor.py)** — documentation drift monitor.
- **[`archive_agent_quality_scan.py`](archive_agent_quality_scan.py)** — agent quality scan archive.

---

## SCAFFOLD / GENERATOR

- **[`instantiate_schema_story_scaffold.py`](instantiate_schema_story_scaffold.py)** — schema-story scaffold pre-instantiation per `docs/dev-guide/scaffolds/schema-story/` recipe (used at story-author time for schema-shape stories).

---

## DRY-overlap candidates (post-M5 ship cleanup)

The following scripts have functional overlap and should be consolidated post-ship:

- **`operator_polling.py` + `operator_directives_poll.py`** — likely consolidate into one `operator_io.py` with explicit poll-mode argument
- **`emit_preflight_receipt.py` + `emit_ingestion_quality_receipt.py`** — receipt-emission may share machinery; extract `receipt_emitter.py` base
- **`fix_slide_content.py` + `fix_test_file.py` + `repair_validator.py` + `restore_validator_clean.py`** — repair/restore family; consolidate into `repair_toolkit.py`
- **`find_mojibake.py` + `normalize_mojibake.py`** — already a detect/fix pair; could merge with `--mode {detect,normalize}` arg
- **Three lockstep checkers (pipeline-manifest + manifest + learning-event)** — each is its own concern; KEEP separate but consider a `meta_lockstep.py` orchestrator that runs all three (single-command for CI)

Filing as `migration-tech-debt-utility-script-consolidation` deferred-inventory entry post-ship.

---

## Conventions (consistency target post-M5)

- **argparse** for CLI surface; consistent `--json` output flag for machine-readable mode
- **Repo-root resolution** via `Path(__file__).resolve().parents[N]` (no hardcoded absolute paths)
- **Exit codes**: 0=success, 1=non-required failure, 2=blocking failure (preflight pattern)
- **Sandbox-AC discipline**: degrade to skip/warn on missing optional service; never assume operator-CLI on PATH
- **Logging**: import `logging_setup` for consistent format
- **Env vars**: read via `env_loader.py` (centralized .env handling)

Scripts that don't yet conform are flagged as candidates for the consolidation cleanup story.
