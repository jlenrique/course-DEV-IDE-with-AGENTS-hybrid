# Migration Story 2a.1: `bmad-create-specialist` Generator + 9-Node Scaffold Reference

**Status:** ready-for-dev
**Sprint key:** `migration-2a-1-bmad-create-specialist-generator-and-9-node-scaffold-reference`
**Epic:** Slab 2a (migration Epic 2a) — **opening story** (first Slab 2 migration story)
**Milestone anchored:** feeds M2 (17-specialist scaffold + Wondercraft pilot <1 dev-day). First story to land a real LLM-call path → **activates the cache-hit-rate baseline harness** deferred at M1.
**Pts:** 5 | **Gate:** dual (schema_shape) | **K-target:** ~1.5×

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order:

1. **Governance lookup** — [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) — confirms Story 2a-1 is frozen at `expected_gate_mode: "dual-gate"` with `rationale: "schema_shape"`. Do not relitigate.
2. **Canonical 9-node contract** — [`tests/integration/scaffold_conformance/scaffold_contract.py`](../../tests/integration/scaffold_conformance/scaffold_contract.py) → `SCAFFOLD_NODE_IDS` frozenset. **This is the authoritative source of truth for node names** — `receive, plan, act, verify, reflect, emit_spans, gate_decision, finalize, handoff`.
3. **Framework doc** — [`docs/dev-guide/scaffold-conformance-framework.md`](../../docs/dev-guide/scaffold-conformance-framework.md) — 9-node role table + how-to-register pattern.
4. **State contracts** — [`app/state/`](../../app/state/) (from Story 1.2) — `RunState`, `SpecialistEnvelope`, `SpecialistReturn`, `OperatorVerdict`, `SanctumFingerprint`. Generator-emitted specialists subclass these per 1.2's four-file-lockstep discipline.
5. **Model cascade** — [`docs/dev-guide/model-selection-guide.md`](../../docs/dev-guide/model-selection-guide.md) (from Story 1.7) — three-level resolution D2 + `model_config.yaml` shape.
6. **Passthrough precedent** — [`app/specialists/_stub/passthrough_specialist.py`](../../app/specialists/_stub/passthrough_specialist.py) (from Story 1.6) — returns `{}`, reducer-safe. Generator's `act` node starts as a passthrough by default; real LLM invocation wires in at 2a.2 (Irene), 2a.3 (Kira), 2a.4 (Texas).
7. **Severance posture** — [`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md#81-upstream-severance-slab-2). No `git show upstream/master:…`; no `git fetch upstream` during migration work. Hybrid's working tree is the input surface.
8. **Roster reconciliation** — [`_bmad-output/planning-artifacts/slab-2-roster-reconciliation.md`](../planning-artifacts/slab-2-roster-reconciliation.md). Wondercraft absorbed 2026-04-24; Audra + Cora dissolved (Category D); 6 Category E names deferred post-M5.
9. **Sandbox-AC rule** — [`CLAUDE.md §LangChain/LangGraph migration`](../../CLAUDE.md) + [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json). Dev-agent ACs MUST NOT assume operator-side CLIs (docker, psql, gh, etc.) are on PATH. This story's ACs are all dev-agent-executable (no operator-gated block needed; no live API calls).
10. **⚠️ Epic-vs-reality drift flag** — Epic 2a spec line 555 uses node names `plan → enter_sanctum → load_expertise → reason → act → validate → emit → return → exit_sanctum` (9 nodes but different labels). **That text is stale drift from pre-Slab-1 architecture sketches.** Slab 1 Story 1.7 hardened the framework with the `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff` names per the scaffold-conformance-framework.md + scaffold_contract.py deliverables. **Dev agent follows scaffold_contract.py, not the epic-doc text.** This drift is itself an instance of anti-pattern #3 (architecture-vs-epics drift) seeded in 1.7 — catch is good; resolution is to use the framework's names.

**Governance pre-flight (single run before T2):**
```bash
python scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-2a-1-bmad-create-specialist-generator.md
```
Expect PASS. If fail, the author introduced a forbidden CLI in a dev-agent AC — remediate structurally, not cosmetically.

---

## Story

As a **dev agent bootstrapping the Slab 2 specialist fleet**,
I want **`skills/bmad-create-specialist/` (SKILL.md + templates/ + scripts/generate.py) that emits a scaffold-conformant 9-node specialist into `app/specialists/<name>/` from a single command, PLUS `app/specialists/_scaffold/` populated as the canonical reference template the generator copies from**,
So that **FR13 is proven end-to-end, the three PR-R-conformant specialists in Epic 2a (Irene Pass 2 / Kira motion / Texas) drop into a consistent creation path at Stories 2a.2–2a.4, Epic 2b's 14-specialist tranche template is ready, and Epic 2c's <1-dev-day Wondercraft validation has a working generator to test against**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). No operator-gated block. The generator stays offline — no live LLM calls, no network, no operator CLIs.

### AC-2a.1-A — `app/specialists/_scaffold/` canonical reference populated

- **Given** `app/specialists/_scaffold/__init__.py` currently has only a model_config.yaml docstring (from Slab 1; no actual files)
- **When** the dev agent populates the directory with a **concrete, working 9-node reference specialist**: `graph.py` (LangGraph `StateGraph` with `SCAFFOLD_NODE_IDS` as node names, each node a pure function over state with a doc-string describing its canonical role), `state.py` (empty subclasses `ScaffoldEnvelope(SpecialistEnvelope)` + `ScaffoldReturn(SpecialistReturn)` — four-file-lockstep MODEL placeholder), `model_config.yaml` (the three-level cascade example per D2: `specialist_id`, `default_model`, `per_node_overrides` showing 1 override, `temperature_default`), `expertise/README.md` (describes the `expertise/` directory's role in the canonical scaffold — loaded at `plan` node, referenced from the specialist's sanctum)
- **Then** `python -c "from app.specialists._scaffold.graph import build_scaffold_graph; g = build_scaffold_graph(); print(sorted(g.nodes.keys()))"` prints the 9-node set exactly; `app/specialists/_scaffold/` imports clean under ruff + import-linter C1 (lane isolation).

### AC-2a.1-B — `skills/bmad-create-specialist/` SKILL.md + generator package

- **Given** no such skill exists on hybrid (verified via `ls skills/bmad-create-specialist/` at T1 → `No such file or directory`)
- **When** the dev agent authors `skills/bmad-create-specialist/SKILL.md` (operator-facing invocation + parameter reference following the specialist-tier SKILL.md pattern, ≤60 lines) PLUS `skills/bmad-create-specialist/templates/` (Jinja2-style or `.template.py`/`.template.yaml` stubs for graph.py, state.py, model_config.yaml, expertise/README.md, __init__.py) PLUS `skills/bmad-create-specialist/scripts/__init__.py` + `skills/bmad-create-specialist/scripts/generate.py`
- **Then** the layout conforms to specialist-tier SKILL.md standards per scaffold-v0.2; SKILL.md names the generator invocation; templates/ are complete (no placeholder holes); scripts/generate.py has module-level docstring + CLI entry per `python -m` invocation convention.

### AC-2a.1-C — Generator emits a conformant specialist end-to-end (green path)

- **Given** AC-2a.1-A + AC-2a.1-B are green
- **When** the dev agent runs `uv run python -m skills.bmad_create_specialist.scripts.generate --name toytest --mcp none --expertise-tier L5-toy`
- **Then** `app/specialists/toytest/` exists with `__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, and `expertise/README.md` — byte-identical to the `_scaffold/` reference except for name substitution (`toytest` replaces `scaffold`/`_scaffold` in module paths, class names, and YAML `specialist_id`); `build_toytest_graph()` compiles; `validate_scaffold("toytest", build_toytest_graph())` returns `.is_conforming is True`; `tests/integration/scaffold_conformance/test_scaffold_toytest.py` emitted by the generator passes.

### AC-2a.1-D — Generator fails loudly on invalid model_config refs (NFR-M2)

- **Given** a specialist is generated with a `model_config.yaml` that references a model id NOT in `app/models/registry.py::MODEL_REGISTRY` (e.g., operator hand-edits `default_model: "gpt-4.9-imaginary"` after generation)
- **When** the compiler (from Story 1.4) is invoked on that specialist's graph
- **Then** graph compile raises `InvalidModelConfigError` (or equivalent named exception from 1.3) whose message surfaces **both** the specialist name AND the invalid model ref; ruff-clean; test covers this explicitly at `tests/specialists/generator/test_generator_invalid_model_config.py` per K-target.

### AC-2a.1-E — Generator CLI arguments + error surface

- **Given** `generate.py` CLI is invoked
- **When** any of these negative paths fire:
  - `--name` missing OR contains non-`[a-z][a-z0-9_]*` characters
  - `--name` collides with an existing `app/specialists/<name>/` directory (without `--force`)
  - `--mcp` is not one of `{none, gamma, elevenlabs, canvas, kling, wondercraft}`
  - `--expertise-tier` does not match `L[3-7]-[a-z0-9-]+`
  - The target `app/specialists/<name>/` would fall outside the workspace root (path-traversal guard per 1.3 precedent)
- **Then** the generator exits 1 with a named error to stderr (`GeneratorInputError: <specific reason>`); no files are created or modified; unit tests cover all five negative paths.

### AC-2a.1-F — Four-file-lockstep compliance for emitted schema-shape (dual-gate)

- **Given** dual-gate schema-shape policy — the generator's `state.py` emission creates new Pydantic model subclasses + the generator itself is a schema-shape-emitting tool
- **When** the dev agent inspects the generator's emission pattern
- **Then** every generated specialist ships **all four lockstep files in the same commit surface** per 1.2 precedent:
  1. **MODEL** — `app/specialists/<name>/state.py` with `<Name>Envelope(SpecialistEnvelope)` + `<Name>Return(SpecialistReturn)` subclasses
  2. **VALIDATOR** — any `@model_validator(mode="after")` bodies inherited from parents verify correctly; no silent validator omission
  3. **TESTS** — `tests/specialists/<name>/test_<name>_state_shape.py` with shape-pin assertions (field names + types + required/optional flags) matching 1.2's precedent pattern
  4. **GOLDEN FIXTURE** — `tests/fixtures/specialists/<name>/golden_envelope.json` + `golden_return.json` with representative valid payloads; round-trip test (`model_validate_json(golden.dumps())`) verifies determinism per NFR-X1
- Validator: `pytest tests/specialists/toytest/ --collect-only` reports ≥4 discoverable tests when `toytest` is generated; all four-file-lockstep paths exist.

### AC-2a.1-G — Toytest cleanup (no pollution)

- **Given** `toytest` was generated by AC-2a.1-C for acceptance verification
- **When** the story closes
- **Then** `toytest` is either:
  - **Option X — fully deleted** from `app/specialists/toytest/` + `tests/specialists/toytest/` + `tests/integration/scaffold_conformance/test_scaffold_toytest.py` (no dangling specialist in the migrated tree), OR
  - **Option Y — moved to `tests/fixtures/specialists/fixture_generated_specialist_for_acceptance_test.py`** as a **fixture-named file (prefix `fixture_` not `test_`)** pytest does NOT auto-collect (per Story 31-3 M-AM-4 precedent), used by a top-level generator regression test at `tests/specialists/generator/test_generator_emits_conformant_toytest.py` that re-runs generation into a `tmp_path` and diffs against the frozen fixture
- **Rationale:** Option Y gives the generator an ongoing regression anchor without polluting `app/specialists/`. Dev agent defaults to Option Y per cascade-forward precedent; flags switch to Option X only if Option Y introduces >30min of cross-coupling.

### AC-2a.1-H — Doc reference added

- **Given** the generator is the authoritative path for Slab 2 specialist creation
- **When** the dev agent updates [`docs/dev-guide/langgraph-migration-guide.md §Specialist Walkthrough`](../../docs/dev-guide/langgraph-migration-guide.md) (currently a section pointer placeholder per 1.7 §11-section skeleton)
- **Then** the §Specialist Walkthrough subsection has a complete operator-cookbook-quality walkthrough: `git pull → skill invocation → generated files listing → conformance test run → manual post-edit checklist (update model_config, author expertise/, wire act node if not passthrough)`; cross-ref to `scaffold-conformance-framework.md` + `specialist-anti-patterns.md`.

### AC-2a.1-I — Anti-pattern harvest (D12 close protocol)

- **Given** Slab 2a opening surfaces the first real instance of Epic-vs-reality drift (captured in T1 readiness flag above) + may surface others during implementation
- **When** the story closes
- **Then** [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) gains **at minimum one** new entry in the four-field format (`name + example + counter-pattern + slab-of-discovery`) from this story's learnings — candidate: "Epic-doc node-name drift from Slab-1-hardened framework" with counter-pattern "dev agent reads scaffold_contract.py, not epic-doc AC text, for node-name source of truth." Additional entries if implementation surfaces more.

### AC-2a.1-J — Cache-hit-rate harness activation check

- **Given** `tests/end_to_end/test_cache_hit_rate_baseline.py` (from Story 1.6) has a `pytest.skip(...)` with a documented re-enablement trigger: first Slab 2 specialist landing a real LLM call
- **When** the dev agent evaluates 2a.1's scope
- **Then** **the skip remains in place at 2a.1 closure** — because 2a.1 emits scaffolds whose `act` node defaults to passthrough (`_stub.passthrough_specialist.passthrough_node`); no real LLM invocation happens yet. The trigger point shifts to 2a.2 (Irene Pass 2) or 2a.4 (Texas), whichever lands a real `act` body first. 2a.1's closure note explicitly states "skip trigger NOT yet met at 2a.1; shifts to 2a.2." **Do not prematurely un-skip.**

### AC-2a.1-K — Close protocol (D12)

- **Given** 2a.1 is Slab 2a's opening story, not a slab-closing story
- **When** the story closes
- **Then** the three-line D12 close stub is recorded in Dev Agent Record:
  1. **Invariant preservation:** #14 generator-from-skill (FR13) proven; 15-invariant audit matrix updated at Slab 2a close (Story 2a.4), not here
  2. **Anti-pattern harvest:** at least one entry added per AC-2a.1-I
  3. **Migration-guide update:** §Specialist Walkthrough populated per AC-2a.1-H

---

## Architecture Compliance

### Decisions the story honors

| Decision | Application |
|---|---|
| **D1 — Sanctum hybrid** | Generator emits `expertise/README.md` that references the specialist's sanctum tree at `_bmad/memory/bmad-agent-<name>/` (hybrid BMB pattern per Epic 26). Sanctum content is NOT generator-authored; operator populates during first-breath. |
| **D2 — Three-level model cascade** | `model_config.yaml` template emits all three levels; 2a.1 tests the shape; 2a.2–2a.4 exercise the resolution. |
| **D3 — HIL invariant tamper-evidence** | Generator's `graph.py` template wires `gate_decision` node to `app.gates.resume_api` (stub from 1.4); no scheduler imports inside `app.gates.**` per Contract C3. |
| **D4 — Lane separation** | Generator targets `app/specialists/<name>/`; import-linter Contract C1 enforces no cross-lane imports. |
| **D8 — Frozen-graph ceremony** | `app/specialists/_scaffold/graph.py` is the frozen reference (Slab 4 Story 4.5 freezes per-specialist graphs; 2a.1 establishes the unfrozen template). |
| **D12 — Cross-slab governance** | Close protocol per AC-2a.1-K; anti-pattern harvest per AC-2a.1-I. |
| **D13 — Registry bump** | Not relevant at 2a.1; Slab 4 ceremony. |

### Architecture-to-code mapping

- **Canonical 9 nodes** per [`tests/integration/scaffold_conformance/scaffold_contract.py`](../../tests/integration/scaffold_conformance/scaffold_contract.py#L22). **Do not add/remove/rename nodes in this story** — any amendment requires party-mode + re-bump scaffold_contract.py version.
- **LangGraph API:** `StateGraph` construction with `.add_node(name, fn)` for each of the 9; `.set_entry_point("receive")`; internal edges `receive → plan → act → verify → reflect → emit_spans → (gate_decision branch) → finalize → handoff`; `gate_decision` uses `Command(goto=...)` for branch logic per langgraph-state-idioms.md §Command patterns.
- **RunState + SpecialistEnvelope + SpecialistReturn** per [`app/state/`](../../app/state/) (Story 1.2). Generator template emits subclasses, not wholesale redefinitions.

---

## File Structure Requirements

### NEW files (generator authors these)

```
skills/bmad-create-specialist/
├── SKILL.md                              # Operator-facing; ≤60 lines specialist-tier
├── templates/
│   ├── __init__.py.template
│   ├── graph.py.template                 # 9-node StateGraph skeleton
│   ├── state.py.template                 # Envelope + Return subclass stubs
│   ├── model_config.yaml.template        # Three-level cascade example
│   └── expertise/
│       └── README.md.template
└── scripts/
    ├── __init__.py
    └── generate.py                       # CLI entry point + Jinja-like renderer

app/specialists/_scaffold/
├── __init__.py                           # EXISTING; updated docstring only
├── graph.py                              # NEW — canonical 9-node reference
├── state.py                              # NEW — ScaffoldEnvelope + ScaffoldReturn
├── model_config.yaml                     # NEW — reference cascade example
└── expertise/
    └── README.md                         # NEW — expertise-layer contract doc

tests/specialists/generator/
├── __init__.py
├── test_generator_emits_conformant_toytest.py   # Green-path end-to-end
├── test_generator_invalid_model_config.py       # NFR-M2 fail-loud
├── test_generator_input_validation.py           # AC-2a.1-E negative paths
└── test_generator_four_file_lockstep.py         # AC-2a.1-F schema-shape gate

tests/fixtures/specialists/  (Option Y only, if chosen)
└── fixture_generated_specialist_for_acceptance_test.py   # Prefix `fixture_` — pytest does NOT auto-collect
```

### MODIFIED files

- [`app/specialists/_scaffold/__init__.py`](../../app/specialists/_scaffold/__init__.py) — docstring update (reference graph.py + state.py + model_config.yaml)
- [`docs/dev-guide/langgraph-migration-guide.md §Specialist Walkthrough`](../../docs/dev-guide/langgraph-migration-guide.md) — AC-2a.1-H
- [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) — AC-2a.1-I
- [`tests/integration/scaffold_conformance/`](../../tests/integration/scaffold_conformance/) — if Option Y cleanup chosen, add `test_scaffold_toytest.py` as a regenerable test (see generator regression test path)
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](sprint-status.yaml) — flip `migration-2a-1-…` from `ready-for-dev` → `in-progress` at T2; → `done` at story close

### NOT modified

- `tests/integration/scaffold_conformance/scaffold_contract.py` — DO NOT touch; architecture amendment required.
- Any primary-repo path — severance in effect; no `git show upstream/master:…`; no cross-branch reads.
- `app/specialists/_stub/passthrough_specialist.py` — kept intact; 2a.1's generator uses passthrough as the default `act` node body for emitted specialists (re-exports or re-references, does not modify).

---

## Technical Requirements

### Dependencies

- Already in lockfile (per Story 1.1a 10-package palette): `langgraph`, `langchain-openai`, `pydantic>=2.8`, `pyyaml`, `click` (or argparse — dev agent choice; prefer stdlib argparse for CLI per Slab-1 precedent). **No new runtime dep required.** Jinja2 is NOT added as a runtime dep — templates use simple `str.replace(...)` or `str.format(...)` substitution, which is sufficient for the 5-variable template whitelist (`name`, `class_name`, `mcp_tool`, `expertise_tier`, `specialist_id`).
- Generator dev-time tooling: standard library only (`pathlib`, `argparse`, `re`, `sys`).

### Invariants preserved (NFR-X1–X5)

- NFR-X1 (byte-for-byte replay) — every generated specialist's `state.py` subclasses `SpecialistEnvelope` / `SpecialistReturn` → inherits round-trip determinism from 1.2.
- NFR-X2 (frozen graph version) — generated `graph.py` declares `GRAPH_VERSION: str = "v0.1-scaffold"` constant that downstream specialist migrations bump when graph shape locks.
- NFR-X3 (sanctum snapshot) — generator emits `expertise/README.md` referencing `_bmad/memory/bmad-agent-<name>/` pattern; sanctum fingerprint computed at 2a.2+ when real sanctum content lands.
- NFR-X4 (model-resolution trail) — `plan` node template includes the resolution-trail append pattern per 1.3 selection policy.
- NFR-X5 (documented temperature variance) — `model_config.yaml` template names `temperature_default: 0.0` with a comment explaining variance rationale.

### FR coverage for this story

- **FR13** (specialist-generator-from-skill) — proven end-to-end.
- **FR14** (programmatic scaffold conformance) — exercised by AC-2a.1-C (`validate_scaffold` pass for generated `toytest`).
- **FR9–FR12** (lane-isolated specialist package, state-subclass discipline, model_config per-specialist, expertise directory) — substrate wired.
- FR15 (sanctum cold-read) + FR16 (resolution trail) substrate stubs referenced but fully exercised at 2a.2+.

---

## Testing Requirements

### K-target policy: ≥1.5×

Per governance JSON `2a-1.expected_k_target` (not explicitly set; inherits from story header `K: ~1.5×`). Interpreted for this story as:

- **Schema-shape models introduced:** `ScaffoldEnvelope`, `ScaffoldReturn`, generator input model (if any) — ~3 models.
- **Minimum test count at K=1.5×:** 3 × 1.5 = ~5 schema-shape tests + broader generator-behavior coverage.
- **Realistic floor:** ≥15 collecting tests at T8 per schema-shape dual-gate precedent (cf. Story 1.2 = 129 tests for 8 models; Story 1.3 = 199; Story 1.6 = 57). 2a.1's scope is narrower: expected ~15–25 tests.

### Test surface

| Test module | Coverage |
|---|---|
| `tests/specialists/generator/test_generator_emits_conformant_toytest.py` | Green-path end-to-end: generate → validate_scaffold → build graph → no errors |
| `tests/specialists/generator/test_generator_input_validation.py` | AC-2a.1-E: 5+ negative path tests (invalid name, name collision, invalid mcp, invalid tier, path traversal) |
| `tests/specialists/generator/test_generator_invalid_model_config.py` | AC-2a.1-D: compile raises named exception on invalid ref |
| `tests/specialists/generator/test_generator_four_file_lockstep.py` | AC-2a.1-F: all 4 artifacts emitted; schema-shape pin tests discoverable |
| `tests/specialists/_scaffold/test_scaffold_reference_conforms.py` | `_scaffold/` itself validates via `validate_scaffold("_scaffold", ...)` → is_conforming |
| `tests/specialists/_scaffold/test_scaffold_state_shape.py` | `ScaffoldEnvelope` + `ScaffoldReturn` shape-pin (field count + types) |
| `tests/integration/scaffold_conformance/test_scaffold_toytest.py` | Emitted by generator per AC-2a.1-C; passes against generated toytest |

### Regression floor (pre-story baseline at M1 close)

- **Slab 1 close:** 286 passed / 5 skipped / 1 deselected / 0 failed.
- **Target at 2a.1 T8:** ≥301 passed (286 baseline + ≥15 new tests) / 5 skipped (cache-hit-rate harness remains skipped per AC-2a.1-J; four Postgres skips inherited) / 1 deselected / 0 failed.
- **Import-linter:** 3/3 KEPT (C1 lane-isolation + C2 gates-no-scheduler + C3 bridge-module-only).
- **Ruff:** clean across all new/modified files.
- **Sandbox-AC validator:** PASS on this story spec.

---

## Previous Story Intelligence

### From Story 1.2 (Pydantic State Base Classes) — 2026-04-23

**Key lesson:** Four-file-lockstep (model + validator + tests + golden fixture) is **non-negotiable for schema-shape stories**. 1.2 landed 8 models × 4 files = 32 artifacts in lockstep; G6 layered review added 4 SHOULD-FIX coverage gaps (UUID4 rejection on envelope/runstate; approve+reject_reason inverse test; proceed+reject_reason inverse). **2a.1 applies the same discipline to EVERY generated specialist** — the generator's emission must produce all four files or fail the emit.

**Late-binding default-arg gotcha** (Slab-1 hot-start #4): `def f(path: Path = MODULE_PATH)` freezes at import time; use `path: Path | None = None` + read the module constant inside the body. Applies to the generator's template-loading code.

### From Story 1.3 (Three-Level Model Selector) — 2026-04-23

**Key lesson:** Path-traversal sanitization on specialist_id (regex `^[a-z][a-z0-9_]*$` per 1.3 `_SPECIALIST_ID_PATTERN`). G6 added 8 parametrized coverage tests. **2a.1's AC-2a.1-E explicitly requires the same regex on `--name`** — reuse 1.3's pattern, don't redefine.

**Model cascade substrate** is landed at `app/models/registry.py` + `app/models/resolver.py`. The generator's `model_config.yaml` template references these by name; generated specialists do NOT re-implement cascade resolution.

### From Story 1.4 (Manifest Loader + Compiler) — 2026-04-23

**Key lesson:** `app/manifest/compiler.py` validates every node's `model_config_ref` at compile time. AC-2a.1-D's "fail loud on invalid model_config ref" rides this existing validation — the dev agent does NOT author a new validator in 2a.1; the generator just emits valid refs and the 1.4 compiler catches hand-edits.

**Contract C3 (bridge-module-only)** currently ignores only `app.mcp_server.tools.gate_decide`. The generator's `gate_decision` node references `app.gates.resume_api` (stub from 1.4) — no new ignore entry needed.

### From Story 1.6 (Passthrough Stub + v4.2 Manifest) — 2026-04-23

**Key lesson:** `_stub.passthrough_specialist.passthrough_node` returns `{}` and is reducer-safe. **The generator's default `act` node body IS this passthrough.** Generated specialists are Slab 1-compatible (run in the existing 33-step manifest via `run_full_smoke()`) until their `act` node is wired to a real LLM at 2a.2+.

**Cache-hit-rate harness skip** has a documented re-enablement trigger keyed to the first real LLM call. 2a.1 does NOT un-skip (AC-2a.1-J).

### From Story 1.7 (Slab 1 Close + Framework) — 2026-04-23

**Key lesson — the authoritative 9-node set is `scaffold_contract.py::SCAFFOLD_NODE_IDS`**, not the epic-doc text. **Epic 2a line 555 is stale drift.** This is anti-pattern #3 from 1.7 in action; the 2a.1 story caught the drift at T1 readiness (per this spec), logged it, and used framework-names everywhere. Harvest to specialist-anti-patterns.md.

**Anti-patterns catalog format:** four fields per entry — `name + example + counter-pattern + slab-of-discovery`. 2a.1 adds ≥1 entry in this format per AC-2a.1-I.

---

## Git Intelligence Summary (recent Slab-1 commits for pattern reference)

- `9526a6c` — Slab 1 close (evidence pack + retrospective).
- `eb2adb0` — Story 1.6 (passthrough stub + v4.2 manifest). **Pattern:** passthrough node shape; `run_full_smoke()` wiring; full-manifest + substrate-stub dual-routing.
- `554f29a` — Story 1.4 (manifest loader + compiler). **Pattern:** compile-time validation; Contract C3 structure; `resume_api.py` stub.
- `1985366` — Story 1.5 (checkpoint retention). **Pattern:** CLI module structure (`python -m app.runtime.cleanup_threads --dry-run|--apply`); the generator's CLI follows the same pattern (`python -m skills.bmad_create_specialist.scripts.generate --name <> …`).
- `5ade9fc` + `0762911` — Story 1.3 (model selector + path-traversal fix). **Pattern:** `_SPECIALIST_ID_PATTERN` regex; security hardening on operator input.
- `7384bdd` + `fcbb42c` — Story 1.2 (Pydantic state base). **Pattern:** four-file-lockstep; schema-shape dual-gate discipline.
- `835e650` — **upstream severance** (2026-04-24, this session). Absorption + Slab 2 roster reconciliation. **Pattern:** 2b.N T1 reads hybrid skill dirs directly; no `git show upstream/master:…`.

---

## Project Context Reference

### Pre-read memory entries

- [`memory/feedback_verify_via_shipped_deps.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_verify_via_shipped_deps.md) — sandbox-AC rule enforcement
- [`memory/project_no_docker.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_no_docker.md) — Postgres runs natively
- [`memory/project_upstream_severance.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_upstream_severance.md) — severance posture; hybrid is source of truth

### Post-story outputs

At 2a.1 close, the following artifacts **directly unblock**:

- **Story 2a.2** (Irene Pass 2 migration) — drops into the generator; wires real LLM at `act` node → **activates cache-hit-rate baseline measurement**.
- **Story 2a.3** (Kira motion migration) — same generator + Kling MCP tool.
- **Story 2a.4** (Texas migration) — same generator + retrieval-contract preservation.
- **Story 2b.1** (Gary TEMPLATE) and 2b.2–2b.14 — same generator; operator-selectable specialist.
- **Story 2c.1** (Wondercraft from-scratch OR migration) — generator validation; <1-dev-day metric; see [`slab-2-roster-reconciliation.md §Wondercraft Decision`](../planning-artifacts/slab-2-roster-reconciliation.md) for the Path A vs Path B choice.

---

## Dev Agent Record

_(Dev agent populates this section during T1–T9 execution.)_

### T1 Readiness

_(Pre-read confirmations; governance-JSON lookup result; sandbox-AC validator result.)_

### T2–T7 Implementation Notes

_(Incremental design choices; late-binding fixes; template-rendering approach chosen; CLI structure.)_

### T8 Regression Evidence

_(Migration-suite regression count; ruff clean; import-linter 3/3 KEPT; sandbox-AC PASS; scaffold-conformance framework green on generated toytest.)_

### G5 Party-Mode Implementation Review

_(Winston / Amelia / Murat / Paige green-lights or riders; adjudication.)_

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

_(Findings triage: APPLY / DEFER / DISMISS per aggressive rubric; four-file-lockstep audit under dual-gate.)_

### D12 Close Stub

1. **Invariant preservation:** _(FR13 proven statement + any Slab-2a invariant touched.)_
2. **Anti-pattern harvest:** _(≥1 new entry link.)_
3. **Migration-guide update:** _(§Specialist Walkthrough populated statement.)_

### Completion Notes

_(Any flags for next session; deferred-work log entries; cache-hit-rate harness skip carry-forward statement per AC-2a.1-J; Option X vs Option Y choice for toytest cleanup.)_

---

## Open Questions / Flags for Operator

1. **Toytest cleanup option** (AC-2a.1-G): dev agent defaults to Option Y (fixture-named regression anchor). Flag if Option X preferred.
2. **Template-variable whitelist**: 5 variables currently (`name`, `class_name`, `mcp_tool`, `expertise_tier`, `specialist_id`). If more are needed during implementation, flag + extend whitelist with explicit rationale (per Story 26-4 scaffold-v0.2 V2-3 preservation pattern).
3. **Wondercraft decision carry-forward**: 2a.1 does not resolve the Path A vs Path B question (that's a Slab 2 kickoff party-mode decision). The generator emitted by 2a.1 is usable for either path.

---

**Status:** ready-for-dev
**Completion note:** Ultimate context engine analysis completed — comprehensive developer guide created. T1 readiness block explicitly flags Epic-vs-reality drift to prevent re-propagation; framework-source-of-truth is `scaffold_contract.py`, not epic doc text. Governance JSON + severance posture pre-baked.
