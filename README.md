# course-DEV-IDE-with-AGENTS — Hybrid Migration Clone

**Status:** active migration in flight on `dev/langchain-langgraph-foundation` branch (severed from upstream/master @ `3ed7c56` since 2026-04-24). M5 ship verdict pending at Slab 5a close.

**One-line elevator:** Collaborative intelligence platform for course content production — a multi-agent orchestrator (Marcus) + Cora dev-graph + per-specialist 9-node scaffold (gates G1/G2C/G3/G4 with HIL DecisionCard verdicts) + tamper-evident operator-verdict + learning ledger + frozen-graph reproducibility ceremony, built on LangChain/LangGraph.

---

## Repository orientation

| You are... | Read this first |
|---|---|
| **An operator running your first trial run** | [`docs/operator/trial-run-runbook.md`](docs/operator/trial-run-runbook.md) (post-M3 close); run `.venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py` before invoking any trial |
| **A user creating course content** | [`docs/user-guide.md`](docs/user-guide.md) (legacy; pre-migration content production workflow; post-M5 ship will be re-anchored) |
| **A system administrator setting up the environment** | [`docs/admin-guide.md`](docs/admin-guide.md) + [`.env.example`](.env.example) |
| **A developer extending the platform** | [`docs/dev-guide.md`](docs/dev-guide.md) + [`docs/dev-guide/langgraph-migration-guide.md`](docs/dev-guide/langgraph-migration-guide.md) |
| **An agent embodying a BMAD persona** | [`docs/agent-environment.md`](docs/agent-environment.md) + [`CLAUDE.md`](CLAUDE.md) (project instructions) + `skills/bmad-agent-{name}/SKILL.md` (per-persona) |
| **A reviewer auditing the migration** | [`_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`](_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md) + [`_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md`](_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md) + sprint progress at [`_bmad-output/implementation-artifacts/sprint-status.yaml`](_bmad-output/implementation-artifacts/sprint-status.yaml) |

---

## Quick-start (operators)

**Prerequisites:**
- Python 3.11+
- Postgres running natively on the host machine (NOT Dockerized — see [`memory/project_no_docker.md`](C:/Users/juanl/.claude/projects/C--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_no_docker.md) operator preference)
- API credentials per [`.env.example`](.env.example)

**One-time setup:**

```bash
# Create venv + install deps via uv (preferred) or pip
python -m venv .venv
.venv/Scripts/pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your real credentials

# Install pre-commit hooks (recommended)
.venv/Scripts/pre-commit install

# Verify health
.venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py
```

**Run your first trial:**

See [`docs/operator/trial-run-runbook.md`](docs/operator/trial-run-runbook.md) (authored at M3 conditional-close; full polish post-M5 ship).

---

## Migration status (live)

The hybrid clone is mid-migration from primary's prompt-pack + Cursor-IDE workflow to a LangChain/LangGraph orchestrator architecture. **Track progress at [`_bmad-output/implementation-artifacts/sprint-status.yaml`](_bmad-output/implementation-artifacts/sprint-status.yaml).**

| Slab | State | Milestone | Verdict |
|---|---|---|---|
| 1 — Substrate (manifests, registries, gate stubs) | done | M1 | GREEN |
| 2a — Scaffold pilot (Texas + Kira + Irene Pass-2 + generator hardening) | done | — | GREEN |
| 2b — Per-specialist wave (14 inheritors + dispatch hardening + scaffold-conformance framework) | done | — | GREEN |
| 2c — Wondercraft pilot + generator validation | done | M2 | **CONDITIONAL-GREEN** (operator addendum pending) |
| 3 — Marcus orchestration | done | M3 | **CONDITIONAL-GREEN** (Texas live-wire addendum pending) |
| 4 — Lockstep + gates + Cora + ledger + frozen-graph | in flight (Codex) | M4 | TBD |
| 5a — Acceptance (replay + parity + economics + invariant audit + ship verdict) | specs ready | **M5 (THE ship gate)** | TBD |
| 5b — Polish (fork UX + economics dashboard + guide final + generator polish) | cuttable per PRD MVP | post-M5 | TBD |

**Migration-master-status enum** (set at 5a.5 SLAB CLOSING per M5 verdict):
- `shipped` (M5 verdict = SHIP) → forward-port playbook activates per FR61
- `iterate-pending` (M5 verdict = ITERATE) → remediation stories open
- `rolled-back` (M5 verdict = ROLLBACK) → FR62 rollback plan executes; clone archived

---

## Architecture at a glance

```
┌──────────── HIL Operator (CLI / MCP / FastAPI) ─────────────┐
│                                                              │
│  ┌──────────── Marcus (operator-facing facade) ─────────┐    │
│  │  marcus.facade.get_facade()  — single voice          │    │
│  │  ┌─ Marcus Intake (pre-packet)                       │    │
│  │  └─ Marcus Orchestrator (Plan-and-Execute / ReAct)   │    │
│  │       │                                               │    │
│  │       ├── Specialists (app/specialists/<name>/)     │    │
│  │       │   9-node scaffold: receive→plan→act→verify  │    │
│  │       │   →reflect→emit_spans→gate_decision→         │    │
│  │       │   finalize→handoff                           │    │
│  │       │                                               │    │
│  │       └── HIL Gates (G1/G2C/G3/G4) → DecisionCard   │    │
│  │             → OperatorVerdict (digest-bound;         │    │
│  │                anti-replay) → resume_from_verdict    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Cora (dev-graph; story-cycle as graph) ────────────┐    │
│  │  Lane-isolated from Marcus (BIDIRECTIONAL ⊥)        │    │
│  │  Thread namespace: dev/{story_id}                   │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Learning Ledger (Postgres; idempotent) ────────────┐    │
│  │  LedgerEvent kinds: verdict / override /            │    │
│  │     sanctum_mutation / future-extensible            │    │
│  │  Queries: reject_rate_per_gate / gate_inventory /   │    │
│  │     sanctum_mutations                                │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Frozen-Graph v42 (reproducibility ceremony) ────────┐    │
│  │  manifest-snapshot + dev-graph-manifest-snapshot +   │    │
│  │  pack-version + dispatch-registry-snapshot +         │    │
│  │  compiled-graph-digest                               │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Architectural invariants (15 total; full audit at `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` post-5a.4 close):**
- Marcus SPOT (single point of truth via `get_facade()`)
- Cold-start sanctum-read fingerprint (FR30; no in-memory continuity)
- HIL-paused (FR34 architecturally-enforced; tamper-evident; anti-replay digest binding)
- Marcus-first activation discipline
- Lane separation (Cora ⊥ Marcus BIDIRECTIONAL via import-linter)
- Deterministic neck (manifest CI graph-compile-time gate; Slab 4)
- Learning events idempotent emission (NFR-R4)
- Ledger side-effect non-fatal (NFR-I2)
- ...and 7 more enumerated in the audit matrix

---

## Project structure

```
app/
├── marcus/              # Slab-1 namespace stub (canonical home is top-level marcus/)
├── specialists/         # 14 9-node scaffold specialists (Slab 2)
├── models/              # Pydantic v2 strict + four-file-lockstep
│   ├── decision_cards/  # G1/G2C/G3/G4 schema family (Slab 3)
│   ├── state/           # RunState + sanctum_fingerprint + operator_verdict + ...
│   └── ...
├── gates/               # HIL gates (Slab 1 stubs + Slab 3 resume_api impl)
├── ledger/              # Learning ledger (Slab 4)
├── cora/                # Dev-graph (Slab 4; lane-isolated from Marcus)
└── runtime/             # Cache state + override + retry policy + sanctum watcher

marcus/                  # CANONICAL Marcus runtime (Story 30-1 + 31-1 lesson-planner +
                         #  Slab-3 additive: dispatch/contract.py + orchestrator/{supervisor,routing}.py)

skills/                  # BMAD agent personas (Marcus, Texas, Wanda, Vera, Quinn-R, etc.)
                         # + bmad_create_specialist generator (Slab 2a)

state/config/            # Pipeline manifest + dispatch registry + dev-graph manifest +
                         #  per-domain configs (gamma, elevenlabs, narration, etc.)

_bmad-output/
├── planning-artifacts/  # PRD + architecture doc + epics + deferred-inventory + roster
└── implementation-artifacts/   # Per-story specs + retrospectives + verdict artifacts +
                                #  sprint-status.yaml

docs/
├── user-guide.md        # Legacy; for course-content creators (re-anchored post-M5)
├── admin-guide.md       # Environment + credentials + MCP server config
├── dev-guide.md         # Architecture + extension points
├── agent-environment.md # Agent persona discipline + Marcus-first
├── operator/            # NEW post-M3: trial-run + conditional-gate + post-M5 runbooks
└── dev-guide/           # Migration-specific guides (template, anti-patterns, scaffolds, ...)

scripts/utilities/       # 56+ utilities including:
                         #  - check_pipeline_manifest_lockstep.py (Epic 33)
                         #  - check_manifest_lockstep.py (Slab 4 — Codex in flight)
                         #  - validate_migration_story_sandbox_acs.py
                         #  - ac_b_op_texas_live_retrieval_evidence.py (operator window)
                         #  - trial_run_preflight.py (NEW; first-trial sanity check)

CLAUDE.md                # Project instructions for Claude Code (BMAD governance, sprint
                         #  governance, sandbox-AC discipline, Marcus-first activation)
```

---

## Governance

This project uses **BMAD methodology** for sprint-style migration work. Key non-negotiables (per [`CLAUDE.md`](CLAUDE.md)):

- **Sandbox-AC discipline:** dev-agent ACs verify via shipped Python deps + `pytest.skip(...)` on missing service; NO operator-CLI assumptions on PATH. Validator at `scripts/utilities/validate_migration_story_sandbox_acs.py`.
- **Gate-mode pinned:** per-story dual-gate vs single-gate locked at [`docs/dev-guide/migration-story-governance.json`](docs/dev-guide/migration-story-governance.json).
- **Substrate-aware adaptation:** if T1 readiness reveals substrate mismatches against spec assumptions, HALT + apply substrate-aware adaptation pattern (precedent: Slab-3 3.1 T1 halt; canonical `marcus/` discovery).
- **Deferred inventory governance:** every new follow-on goes to [`_bmad-output/planning-artifacts/deferred-inventory.md`](_bmad-output/planning-artifacts/deferred-inventory.md) (currently 58 entries).
- **Closeout hygiene:** every story close updates `sprint-status.yaml` first, then `next-session-start-here.md`.
- **Pre-commit hooks** at [`.pre-commit-config.yaml`](.pre-commit-config.yaml) enforce regression-proof discipline (orphan-reference detector, co-commit invariant, ruff fast-path).

---

## Hybrid severance posture

This clone is **severed from upstream/master @ `3ed7c56` since 2026-04-24** per `MEMORY.md::project_upstream_severance`. Wholesale `git merge upstream/master` is OFF-POLICY. The migration's LangChain/LangGraph re-platform IS the replacement. Per-capability forward-port post-M5 SHIP verdict per FR61 playbook.

Primary repo serves as **frozen reference** for parity comparison at Slab 5a.2 head-to-head trial; primary baselines mined from `3ed7c56` snapshot.

---

## License

[See LICENSE file if present; otherwise project-internal — confirm with project owner]

---

## Acknowledgments

Migration architected, planned, and executed via BMAD party-mode collaboration across the persona roster (Winston/Murat/Paige/Quinn-R/Amelia/Mary/Sally/John/Dr. Quinn). Built on LangChain + LangGraph (Anthropic + OpenAI model providers). Human-in-the-loop (HIL) discipline per FR34 architectural enforcement.
