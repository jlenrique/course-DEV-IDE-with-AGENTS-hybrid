# Sources of Truth — comprehensive SSOT registry

**Purpose:** authoritative index of which file/path is the source of truth for which topic, with lockstep partners + change protocols. Use this to (a) avoid divergent edits across files that ought to move in lockstep, (b) trace authority when prose conflicts, (c) keep documentation audits cheap by knowing where to look.

**Scope:** post-SHIP migrated runtime (`dev/langchain-langgraph-foundation` branch). Pre-migration primary-repo SSOTs are historical reference only — see `docs/dev-guide.md` legacy banner for that scope.

**Authorship:** drafted 2026-04-28 immediately after Slab 6 bundle close. Living document — extend as new SSOTs land. To add an entry, append a row + identify lockstep partners + name the change protocol.

---

## How to use this registry

1. **Look up the topic** in §2 below.
2. **Read the SSOT** — this is the authoritative source. Other docs that mention the topic should DEFER to it.
3. **Check lockstep partners** — these files MUST move together with the SSOT under the named change protocol.
4. **Follow the change protocol** before modifying.

If you find a doc claiming authority on a topic where this registry names a different SSOT, **file a stale-doc finding** (open `bmad-code-review` or surface to operator). The registry resolves; the stale doc gets updated.

---

## §2 — Topic-by-topic SSOT registry

### Migration verdict + ship state

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Migration verdict + M5 conditions | `_bmad-output/implementation-artifacts/m5-decision.md` | `_bmad-output/upstream-state.md` (M5 conditions tracker); `README.md` status line | Operator party-mode required for verdict-shape change; mechanical for status annotations |
| Severance posture (upstream/master) | `_bmad-output/upstream-state.md` line 9 (`Frozen reference anchor`) | `README.md` status line; `CLAUDE.md` (no docker; LangGraph migration project memories) | Operator authority; no automated path |
| Story sprint state | `_bmad-output/implementation-artifacts/sprint-status.yaml` | per-story spec files in `_bmad-output/implementation-artifacts/migration-*.md` | Per-story workflow (CLAUDE.md §1-§3); Lesson Planner stories use `lesson-planner-story-governance.json` validator |
| Deferred work registry | `_bmad-output/planning-artifacts/deferred-inventory.md` | per-story spec follow-on entries; sprint-status reactivation triggers | Update at (a) Epic retrospective, (b) story closure naming follow-on, (c) session-WRAPUP per CLAUDE.md §"Deferred inventory governance" |

### Composition + runtime substrate

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Composition shape (Option B / Path A-prime) | `docs/dev-guide/composition-specification.md` | `app/models/runtime/production_envelope.py`; `app/marcus/orchestrator/dispatch_adapter.py`; `tests/composition/`; `docs/dev-guide/substrate-inventory-checklist.md` | §10 Decision Log + §11 Migration Triggers; substrate-affecting changes require party-mode |
| Production envelope contract | `app/models/runtime/production_envelope.py` (Pydantic v2 strict) | `schema/production_envelope.v1.schema.json`; `tests/unit/runtime/test_production_envelope_strict.py`; `tests/fixtures/runtime/production_envelope_golden.json` | Four-file-lockstep per `docs/dev-guide/pydantic-v2-schema-checklist.md`; party-mode for breaking changes |
| Dispatch adapter contract | `app/marcus/orchestrator/dispatch_adapter.py::ProductionDispatchAdapter` | `tests/integration/marcus/test_dispatch_adapter.py`; composition spec §3.3 | Party-mode for input/output signature changes; dev-agent for internal refactor |
| Production runner (composition layer) | `app/marcus/orchestrator/production_runner.py` | `app/marcus/cli/trial.py`; `tests/integration/marcus/test_production_runner_*.py`; `tests/live/test_production_trial_smoke.py`; `tests/live/test_production_trial_smoke_with_gate.py` | Dev-agent for internal; party-mode for adapter-contract or gate-precedence changes |
| Trial envelope persistence shape | `app/models/runtime/production_trial_envelope.py` | `schema/production_trial_envelope.v1.schema.json`; goldens; shape-pin tests | Four-file-lockstep |
| Substrate pre-flight checklist | `docs/dev-guide/substrate-inventory-checklist.md` (N1–N12) | composition-specification.md §7; bmad-code-review template; per-Slab governance docs | Operator authority for new N-items (N13+); propose-don't-unilaterally-add |

### Pipeline + manifest

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Pipeline topology | `state/config/pipeline-manifest.yaml` | `runtime/graphs/v42/manifest-snapshot.yaml` (frozen snapshot); `runtime/graphs/v42/dispatch-registry-snapshot.yaml`; `runtime/graphs/v42/pack-version.txt`; pipeline manifest regime triggers | Pipeline-lockstep regime per `docs/dev-guide/pipeline-manifest-regime.md`; pack version bumps governance per Tier-1/2/3 policy |
| Manifest schema | `app/manifest/schema.py` (`PipelineManifest`, `NodeSpec`, `EdgeSpec`) | `app/manifest/compiler.py` (validator); `tests/integration/manifest/`; `docs/dev-guide/pipeline-manifest-regime.md` | Schema-shape change requires party-mode; field additions follow Pydantic-v2 four-file-lockstep |
| Manifest dependency declarations | `state/config/pipeline-manifest.yaml` per-node `dependencies:` field (Slab 6.2) | `app/manifest/compiler.py::_validate_dependency_cycles`; `app/marcus/orchestrator/production_runner.py::_resolve_dependency_map`; `app/marcus/orchestrator/production_runner.py::_default_dependency_map_for` (PERMANENT fallback) | Add new specialist's dependency entry at filing time; fallback retention is PERMANENT (not deprecated; not transitional) per Slab 6.2 W-R1+P-R1 ratification |
| Dispatch registry | `state/config/dispatch-registry.yaml` (`_status: production`) | `runtime/graphs/v42/dispatch-registry-snapshot.yaml` (frozen); `app/manifest/compiler.py` (consumer) | Slab-3 promotion completed 2026-04-26; promotions to/from `interim` require party-mode |
| Block-mode trigger paths | `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` | `docs/dev-guide/pipeline-manifest-regime.md`; CLAUDE.md `## Pipeline lockstep regime` section | Operator + party-mode |

### Specialists (9-node scaffold)

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Scaffold contract (9 nodes) | `app/specialists/_scaffold/` + `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS` | All 14 × `app/specialists/<name>/graph.py`; `docs/dev-guide/scaffold-conformance-framework.md`; `docs/dev-guide/specialist-migration-template.md` (R1–R14) | Scaffold-level change requires party-mode + amendment to specialist-migration-template; per-specialist generator (`bmad-create-specialist`) emits scaffold-conformant tree |
| Specialist generator | `skills/bmad_create_specialist/scripts/generate.py` | `skills/bmad-create-specialist/SKILL.md`; `tests/specialists/generator/`; `pyproject.toml` C3 import-linter contract auto-emit | Generator changes require party-mode; auto-emit machinery (Story 2a.5) handles C3 row + scaffold tree atomically |
| Per-specialist contract | `app/specialists/<name>/graph.py` + `app/specialists/<name>/state.py` + `app/specialists/<name>/model_config.yaml` + `app/specialists/<name>/expertise/README.md` | per-specialist `tests/specialists/<name>/`; per-specialist sanctum at `_bmad/memory/bmad-agent-<name>/`; per-specialist skill at `skills/bmad-agent-<name>/SKILL.md` | Per-specialist change requires per-specialist test green + scaffold-conformance test green + isolation invariant preserved (N4) |
| Sanctum reference conventions | `docs/dev-guide/sanctum-reference-conventions.md` | per-specialist `_bmad/memory/bmad-agent-<name>/INDEX.md` + `PERSONA.md`; `expertise/README.md` dotted reference idiom | Operator first-breath ceremony; conventions stable since Slab 2a.2 |

### Models + cascade

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Model cascade | `runtime/config/model_cascade.yaml` (operator-editable) | `runtime/config/openai_pricing.yaml`; `app/models/registry.yaml`; `app/models/selection_policy.yaml` | Operator authority; cascade rebalance requires `tests/test_no_fictitious_model_ids.py` + `tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` GREEN |
| Per-specialist model selection | `app/specialists/<name>/model_config.yaml` | model cascade YAML; selection policy | Per-specialist; defaults to cascade tier per spec; `model_id_override` for explicit pins |
| Pricing | `runtime/config/openai_pricing.yaml` (operator-editable) | per-trial cost reports at `state/config/runs/<trial-id>/cost-report.{json,md}`; `app/runtime/economics.py` | Operator authority for rate updates |
| Catalog membership | `tests/fixtures/openai_catalog_snapshot.json` | `tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py`; `tests/test_no_fictitious_model_ids.py` (lint guard) | A15 counter-pattern: any production model_id MUST appear in the catalog snapshot; refresh per `_provenance.next_refresh_due_by` field |

### Gates + verdicts (FR34)

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Production gates (runner-pause set; current: G1/G2C/G3/G4) | `app/manifest/compiler.py::production_gate_ids(manifest)` (manifest-derived per Slab 7a 7a-2; legacy hardcoded `PRODUCTION_GATE_IDS` frozenset retired) | `app/gates/resume_api.py`; `app/models/decision_cards.py`; `state/config/pipeline-manifest.yaml` (gate nodes + fold-flag metadata FR-A8); `tests/integration/marcus/test_production_runner_gate_pause_resume.py`; ADR 0002 §1 family-contract taxonomy | FR34 invariant; party-mode for gate-set changes; manifest fold-flags drive runtime derivation |
| Decision card schema | `app/models/decision_cards/` package (G0Card, G1Card, G2ACard, G2CCard, G3Card, G4Card, G5Card, G6Card; DecisionCardBase + DecisionCardMeta). Slab 7c expanded the family-contract DecisionCard set per ADR 0002 §1 eight-family taxonomy. | per-card schemas + goldens + shape-pin tests; `tests/unit/models/decision_cards/`; `tests/parity/test_decision_card_*_shape_pin.py` | Pydantic-v2 four-file-lockstep; party-mode for new card families |
| Operator verdict | `app/models/state/operator_verdict.py` | `app/gates/resume_api.py::resume_from_verdict`; tamper-evidence (decision-card-digest binding) | Story 3.3 W-R1-3.3-2 anti-replay tuple discipline; party-mode for contract changes |
| Gate precedence rule | `docs/dev-guide/composition-specification.md` §3.5 | production runner gate handling; `gate_overrides` dict shape; per-specialist `gate_decision` semantics | Composition Spec §10 entry required for changes |

### Anti-patterns + governance

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Anti-pattern catalog | `docs/dev-guide/specialist-anti-patterns.md` (A1–A17 + P1–P3) | `docs/dev-guide/dev-agent-anti-patterns.md` (dev-cycle-level); per-specialist counter-pattern citations | Mary harvest-gate authority for new entries; format-freeze v1 preserved (existing entries don't get rewritten) |
| Story gate-mode designations | `docs/dev-guide/migration-story-governance.json` | sprint-status (per-story `expected_gate_mode`); `bmad-create-story` workflow reads this | Party-mode required for additions/demotions; version bump in `_amendment_log` |
| Lesson Planner gate-mode | `docs/dev-guide/lesson-planner-story-governance.json` | `scripts/utilities/validate_lesson_planner_story_governance.py` | Party-mode for changes; validator enforces |
| Story-cycle efficiency rules | `docs/dev-guide/story-cycle-efficiency.md` | K-floor floor enforcement per story; DISMISS rubric in code-review | Operator + party-mode for K-floor policy changes |
| Sandbox-AC inventory | `docs/dev-guide/migration-ac-sandbox-inventory.json` | `scripts/utilities/validate_migration_story_sandbox_acs.py` | `dev_agent_forbidden` additions are dev-agent authority (strict expansion); `dev_agent_available` additions require party-mode |
| Slab 6 governance discipline | `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` | composition-specification.md; substrate-inventory-checklist.md; specialist-anti-patterns.md; CLAUDE.md §1-§4 | Operator party-mode for amendments; binding for all Slab 6.x stories |

### Frozen graph + replay

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Frozen graph artifacts | `runtime/graphs/v42/` (`compiled-graph-digest.txt`, `manifest-snapshot.yaml`, `dispatch-registry-snapshot.yaml`, `pack-version.txt`) | live manifest + dispatch registry; ceremony scripts; `docs/dev-guide/frozen-graph-version-ceremony.md` | FR43 frozen-graph-version-ceremony; pack version bumps require party-mode for Tier-2+ |
| Replay regression suite | `tests/replay/` + `tests/integration/replay/` + `tests/migration/test_compiled_graph_digest_stable.py` | `app/replay/parity_comparison.py`; baseline fixtures at `tests/fixtures/marcus/baseline_envelope/` | Pre-existing pack-hash drift filed as `replay-regression-pack-hash-drift-pre-slab-6.1`; operator-authority for golden refresh |

### Dependencies + environment

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Python dependencies | `pyproject.toml [project.dependencies]` + `[project.optional-dependencies]` | `requirements.txt` (mirror for pip-only operators); `.venv` install state | When pyproject changes, regenerate requirements.txt; date-stamp the "Last reconciled" header |
| Environment variables | `.env.example` (with REQUIRED/RECOMMENDED/OPTIONAL categorization) | `.env` (operator-local; gitignored); `scripts/operator/check_keys.py` | Operator authority for `.env` content; `.env.example` updates require dev-agent + operator review |
| Postgres setup | `docs/dev-guide/local-postgres-setup.md` | `state/runtime/*.db` (gitignored); checkpointer + ledger consumers | Native (NOT Dockerized) per operator preference; setup script `scripts/setup/first_clone_bootstrap.{ps1,sh}` |
| LangSmith integration | env vars `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT` | trace context propagation in production runner; cost machinery filter; `app/runtime/economics.py::measure_trial_cost(trial_id)` | Operator-managed credentials; runner-side trace_id binding deferred per `slab-6-1-langsmith-runner-trace-id-real-binding` |

### Operator-facing surfaces

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Production trial playbook | `docs/operator/production-trial-playbook.md` (skeleton; full fill during first tracked trial) | trial-run-runbook; production-run-swimlane; validation-scripts; hud-guide | Operator authority for fill-in-progress; cross-references to other operator docs maintained |
| Operator validation scripts | `docs/operator/validation-scripts.md` (catalog) | `scripts/operator/*.py` (5 validation + 4 ceremony scripts); each script's paste-ready output format | Add new script row when adding new operator-validation surface |
| HUD operator guide | `docs/operator/hud-guide.md` | `scripts/utilities/run_hud.py`; per-step summary derivation module (Slab 6.5) | Per-step summary changes follow Slab 6.5 close protocol |
| Step 02A prior-run defaults | `docs/operator/step-02a-prior-run-defaults.md` | `scripts/utilities/operator_directives_defaults.py`; Step 02A pack template | Per-Slab-6.3 close shape |

### Documentation indexes

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| **THIS document** (sources-of-truth registry) | `docs/dev-guide/sources-of-truth.md` | none directly; consumed by all docs that need to identify authoritative source | Append rows when new SSOTs land; remove rows when SSOTs retire; party-mode for structural changes |
| Directory responsibilities (config dir tiers) | `docs/directory-responsibilities.md` | `config/`, `state/config/`, `resources/style-bible/` | Operator authority |
| Parameter directory | `docs/parameter-directory.md` | per-parameter consumers; story 20c-7 parameter audit | Operator authority for parameter additions |
| Marcus capabilities | `docs/dev-guide/marcus-capabilities.md` | `skills/bmad-agent-marcus/`; `app/marcus/`; per-capability Story specs | Story-driven (PR-* family); single-source-of-truth across primary + hybrid |

### BMAD framework boundaries

| Topic | SSOT | Lockstep partners | Change protocol |
|---|---|---|---|
| Project instructions for AI agents | `CLAUDE.md` (Claude Code) + `.cursor/rules/bmad-sprint-governance.mdc` (Cursor) + `.github/copilot-instructions.md` (Copilot) + `AGENTS.md` (cross-IDE pointer) | All four are kept aligned; CLAUDE.md is canonical for sprint governance | Operator authority; align all four when one changes |
| Custom BMAD agents (Marcus, Irene, Kira, etc.) | Per-agent `skills/bmad-agent-<name>/SKILL.md` (activation) + `_bmad/memory/bmad-agent-<name>/` (sanctum continuity) | per-agent persona + skill scaffolding; CLAUDE.md "Custom agents vs registered" clarification | Per-agent operator-driven |
| Stock BMAD personas | `_bmad/_config/agent-manifest.csv` | `bmad-party-mode` skill (resolves voices); BMAD module skills | Operator authority; party-mode skill consumes |

---

## §3 — Change protocol vocabulary

- **Four-file-lockstep:** Pydantic v2 model + JSON Schema + shape-pin tests + golden fixture must move together. See `docs/dev-guide/pydantic-v2-schema-checklist.md`.
- **Pipeline-lockstep regime:** any path in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` triggers block-mode at pre-closure hook. See `docs/dev-guide/pipeline-manifest-regime.md`.
- **Composition Spec §10 entry required:** for any substrate-affecting decision (envelope/adapter/dependency_map/gate-precedence/persistence/composition-test discipline). See `docs/dev-guide/composition-specification.md` §7.
- **Mary harvest-gate authority:** new anti-pattern catalog entries; revisited at every story close.
- **Party-mode required:** multi-agent ratification (Winston + Murat + Paige + Amelia minimum; add Quinn-R + Mary for dual-gate or harvest-gate work). See `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md`.
- **Operator authority:** explicit operator decision; can be inline or via party-mode.
- **Dev-agent authority:** dev agent can act unilaterally per CLAUDE.md sprint governance.

---

## §4 — Maintenance protocol

This registry is normative for SSOT identification. Update at:

1. **Each new SSOT addition** — append row + identify lockstep partners + name change protocol
2. **Each SSOT retirement** — remove row OR mark as deprecated with replacement pointer
3. **Each major substrate change** — verify lockstep partners list + change protocol still accurate
4. **Each documentation audit** — use this registry as the audit baseline
5. **Quarterly** — review for stale entries; party-mode evaluate structural changes

Decisions to remove or contract this document require party-mode ratification. Decisions to extend it are dev-agent authority.

---

## §5 — Companion documents (read alongside)

- `docs/dev-guide/composition-specification.md` — Option B governing reference
- `docs/dev-guide/substrate-inventory-checklist.md` — N1–N12 standing pre-flight
- `docs/dev-guide/specialist-anti-patterns.md` — A1–A17 + P1–P3 catalog
- `docs/dev-guide/specialist-migration-template.md` — R1–R14 specialist-migration rules
- `docs/dev-guide/pipeline-manifest-regime.md` — pipeline lockstep regime
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — four-file-lockstep contract
- `docs/dev-guide/migration-story-governance.json` — gate-mode designations
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` — Slab 6 governance
- `CLAUDE.md` — project instructions
