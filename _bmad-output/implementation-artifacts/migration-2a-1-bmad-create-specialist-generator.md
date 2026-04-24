# Migration Story 2a.1: `bmad-create-specialist` Generator + 9-Node Scaffold Reference

**Status:** ready-for-dev
**Sprint key:** `migration-2a-1-bmad-create-specialist-generator-and-9-node-scaffold-reference`
**Epic:** Slab 2a (migration Epic 2a) — **opening story** (first Slab 2 migration story)
**Milestone anchored:** feeds M2 (17-specialist scaffold + Wondercraft pilot <1 dev-day). First story to land a real LLM-call path → **activates the cache-hit-rate baseline harness** deferred at M1.
**Pts:** 5 | **Gate:** dual (schema_shape) | **K-target:** ~1.8× (raised 2026-04-24 party-mode per Murat R9; floor 15 / target 18–20; three stacked risk surfaces — Pydantic models + CLI parser + four-file atomic emitter)

---

## Party-Mode Amendment Log (2026-04-24)

Green-light consensus `GREEN-with-riders` per Winston / Amelia / Murat / Paige / Mary (5/5). Riders applied below (6 MUST-FIX + 5 SHOULD-FIX; 6 SOFT deferred as noted in orchestrator consolidation). Each AC edit cites the rider number from the party-mode orchestrator note.

- **R1** (Paige+Amelia+Murat) — AC-F explicit "every generated specialist" + 3 verification hooks + pinned target paths
- **R2** (Paige) — AC-G binary Option X/Y criterion (no time-based heuristic)
- **R3** (Paige) — AC-H inline 4-item post-edit sub-checklist + Irene worked before/after
- **R4** (Paige) — AC-I inline four-field template verbatim + format-frozen declaration
- **R5** (Mary+Winston) — AC-I' NEW rider: Slab 2+ T1 epic-doc-vs-framework cross-check requirement
- **R6** (Mary) — AC-C2 NEW stretch AC: generator `--dry-run` against Irene skill tree → FR13 skill-ingest closure at 2a.1
- **R7** (Winston) — `model_config.yaml` template inline comments explaining D2 cascade (SHOULD-FIX)
- **R8** (Winston) — T1 severance reinforcement line (SHOULD-FIX)
- **R9** (Murat) — K target 18–20 / floor 15 + regression ≥304 + 4 added tests (template-var literal-survival + four-file atomicity + collect-only non-collection + regex boundaries) (SHOULD-FIX)
- **R10** (Amelia) — T1 verify action: confirm 1.4 compiler error class before code opens (SHOULD-FIX)
- **R11** (Mary+Winston) — Generator ships `--dry-run` flag (SHOULD-FIX; rides R6)

SOFT riders deferred per operator Option-3 directive: R12 (deferred-inventory follow-on for epic-doc refresh), R13 (Wondercraft forward-pointer), R14 (pin 1.3 import path), R15 (pin AC-K target file), R16 (template-var forward-look on 6th var), R17 (SKILL.md+references delegate + 3-group index).

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order:

1. **Governance lookup** — [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) — confirms Story 2a-1 is frozen at `expected_gate_mode: "dual-gate"` with `rationale: "schema_shape"`. Do not relitigate.
2. **Canonical 9-node contract** — [`tests/integration/scaffold_conformance/scaffold_contract.py`](../../tests/integration/scaffold_conformance/scaffold_contract.py) → `SCAFFOLD_NODE_IDS` frozenset. **This is the authoritative source of truth for node names** — `receive, plan, act, verify, reflect, emit_spans, gate_decision, finalize, handoff`.
3. **Framework doc** — [`docs/dev-guide/scaffold-conformance-framework.md`](../../docs/dev-guide/scaffold-conformance-framework.md) — 9-node role table + how-to-register pattern.
4. **State contracts** — [`app/models/state/`](../../app/models/state/) (from Story 1.2) — `RunState`, `SpecialistEnvelope`, `SpecialistReturn`, `OperatorVerdict`, `SanctumFingerprint`. Generator-emitted specialists subclass these per 1.2's four-file-lockstep discipline.
5. **Model cascade** — [`docs/dev-guide/model-selection-guide.md`](../../docs/dev-guide/model-selection-guide.md) (from Story 1.7) — three-level resolution D2 + `model_config.yaml` shape.
6. **Passthrough precedent** — [`app/specialists/_stub/passthrough_specialist.py`](../../app/specialists/_stub/passthrough_specialist.py) (from Story 1.6) — returns `{}`, reducer-safe. Generator's `act` node starts as a passthrough by default; real LLM invocation wires in at 2a.2 (Irene), 2a.3 (Kira), 2a.4 (Texas).
7. **Severance posture** — [`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md#81-upstream-severance-slab-2). No `git show upstream/master:…`; no `git fetch upstream` during migration work. Hybrid's working tree is the input surface.
8. **Roster reconciliation** — [`_bmad-output/planning-artifacts/slab-2-roster-reconciliation.md`](../planning-artifacts/slab-2-roster-reconciliation.md). Wondercraft absorbed 2026-04-24; Audra + Cora dissolved (Category D); 6 Category E names deferred post-M5.
9. **Sandbox-AC rule** — [`CLAUDE.md §LangChain/LangGraph migration`](../../CLAUDE.md) + [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json). Dev-agent ACs MUST NOT assume operator-side CLIs (docker, psql, gh, etc.) are on PATH. This story's ACs are all dev-agent-executable (no operator-gated block needed; no live API calls).
10. **⚠️ Epic-vs-reality drift flag** — Epic 2a spec line 555 uses node names `plan → enter_sanctum → load_expertise → reason → act → validate → emit → return → exit_sanctum` (9 nodes but different labels). **That text is stale drift from pre-Slab-1 architecture sketches.** Slab 1 Story 1.7 hardened the framework with the `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff` names per the scaffold-conformance-framework.md + scaffold_contract.py deliverables. **Dev agent follows scaffold_contract.py, not the epic-doc text.** This drift is itself an instance of anti-pattern #3 (architecture-vs-epics drift) seeded in 1.7 — catch is good; resolution is to use the framework's names.
11. **Severance reinforcement (R8):** Input surface is hybrid working tree at commit `835e650` (upstream severance, 2026-04-24); `upstream/master` is historical reference only. No `git show upstream/master:…`, no `git fetch upstream`. Any AC-referenced specialist skill directory is read from hybrid's own `skills/bmad-agent-*/` tree.
12. **Compiler error-class verification (R10 BROADENED to full artifact-existence sweep per round-2 Murat caveat):** At T1 Readiness, confirm the following 5 Slab-1-shipped artifacts exist at stated paths with stated shape (round-2 code-vs-plan alignment caught several drifts; T1 sweep prevents T2 detonations):
    - **A** `app/manifest/compiler.py::compile()` raises `CompileError` (from `app.manifest.exceptions`) on invalid `model_config_ref` — verified 2026-04-24 per round-2 Winston/Amelia finding
    - **B** `app/models/state/` hosts the 9 Pydantic models + separate `validators/<model>_validators.py` modules — NOT `app/state/`
    - **C** `app/specialists/_stub/passthrough_specialist.py::passthrough_node` returns `{}` — Slab 1 generator-emitted `act` default
    - **D** `app/gates/resume_api.py::resume_from_verdict` raises `NotImplementedError` — C3 binding symbol; generator references for import-stability but node body uses `interrupt()` per [`gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md) (landed via round-3 Commit B SP3)
    - **E** `_SPECIALIST_ID_PATTERN` regex for name sanitization lives under `app.models.*` per 1.3 commit `0762911`. **T1 step for 2a.1 specifically:** grep + confirm (a) its path, (b) whether it accepts or rejects `_`-prefix sentinel IDs (e.g., `_passthrough`, `_scaffold`), and (c) whether the generator should reject sentinel-name inputs. Document in Dev Agent Record T1.

    Record all 5 verifications in Dev Agent Record T1 Readiness block BEFORE writing any code at T2. Any drift between spec and code at this step halts T2 until resolved (spec yields to code per DR-1 [GOLDEN foundation ratification 2026-04-24](../planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md)).
13. **Epic 2a line 555 drift physically present at T1 (round-2 Mary caveat):** open [`_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md`](../planning-artifacts/epics-langchain-langgraph-migration.md) line ~555, confirm the stale node-name list (`plan/enter_sanctum/load_expertise/reason/act/validate/emit/return/exit_sanctum`) is STILL present as KNOWN-DRIFT exhibit (per the 2026-04-24 KNOWN-DRIFT HTML comment above the line; Commit A of this session preserved it intentionally for anti-pattern #3 live-training). If drift absent (accidentally fixed), escalate — FR64 exercise opportunity lost and anti-pattern harvest at AC-I loses its primary example. Document presence in Dev Agent Record T1.

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

### AC-2a.1-C2 — Generator `--dry-run` against Irene skill tree (FR13 skill-ingest closure) [R6 + R11]

- **Given** `skills/bmad-agent-content-creator/` (Irene's pre-severance skill tree on hybrid) exists with SKILL.md + references/ + scripts/ + the post-severance-absorbed Pass-2 templates
- **When** the dev agent runs `uv run python -m skills.bmad_create_specialist.scripts.generate --name irene --mcp none --expertise-tier L5-narration-pass-2 --from-skill skills/bmad-agent-content-creator/ --dry-run`
- **Then** (a) generator exits 0 with NO writes to `app/specialists/irene/` (verify via `ls app/specialists/irene/ 2>&1` → "No such file or directory" post-run); (b) dry-run stdout enumerates the emission tree (5 files + 4 test/fixture files) the generator WOULD write at wet-run; (c) parse + shape-validation runs against the would-be emission (state.py import-checks; model_config.yaml YAML parses; graph.py 9-node set matches `SCAFFOLD_NODE_IDS`); (d) any parse failure surfaces with file path + line number, exits 1
- **Why this AC exists:** FR13 requires "specialist-generator-from-skill" end-to-end. AC-2a.1-C proves generator emits a conformant SHELL from a synthetic name; AC-2a.1-C2 proves generator INGESTS a real primary-authored skill tree and the shape-validation gates hold. Without C2, FR13 sits half-open until 2a.2 actually writes Irene; with C2, FR13 closes at 2a.1 and 2a.2 focuses on `act` node body wiring, not generator debugging.
- `--dry-run` also preserves Wondercraft Path-A/B optionality at 2c.1 (operator can probe the generator against `skills/bmad-agent-wondercraft/` without committing to either path).

### AC-2a.1-D — Generator fails loudly on invalid model_config refs (NFR-M2)

- **Given** a specialist is generated with a `model_config.yaml` that references a model id NOT in `app/models/registry.py::MODEL_REGISTRY` (e.g., operator hand-edits `default_model: "gpt-4.9-imaginary"` after generation)
- **When** the compiler (from Story 1.4) is invoked on that specialist's graph
- **Then** graph compile raises `CompileError` (from `app.manifest.exceptions`; verified 2026-04-24 in party-mode round 2 code-vs-plan alignment — 1.4 compiler raises `CompileError`, NOT the fictional `InvalidModelConfigError` the original spec named) whose message surfaces **both** the specialist name AND the invalid model ref; ruff-clean; test covers this explicitly at `tests/specialists/generator/test_generator_invalid_model_config.py` per K-target. Test imports: `from app.manifest.exceptions import CompileError`.

### AC-2a.1-E — Generator CLI arguments + error surface

- **Given** `generate.py` CLI is invoked
- **When** any of these negative paths fire:
  - `--name` missing OR contains non-`[a-z][a-z0-9_]*` characters
  - `--name` collides with an existing `app/specialists/<name>/` directory (without `--force`)
  - `--mcp` is not one of `{none, gamma, elevenlabs, canvas, kling, wondercraft}`
  - `--expertise-tier` does not match `L[3-7]-[a-z0-9-]+`
  - The target `app/specialists/<name>/` would fall outside the workspace root (path-traversal guard per 1.3 precedent)
- **Then** the generator exits 1 with a named error to stderr (`GeneratorInputError: <specific reason>`); no files are created or modified; unit tests cover all five negative paths.

### AC-2a.1-F — Four-file-lockstep compliance — emission rule for EVERY generated specialist (dual-gate) [R1]

- **Given** dual-gate schema_shape policy + 1.2 four-file-lockstep precedent — the generator's emission logic produces all four lockstep files in lockstep for **any** specialist it creates (both the `_scaffold/` reference at AC-2a.1-A AND every end-to-end output at AC-2a.1-C/C2). "Every generated specialist" means the rule applies per invocation, with no omissions. If the generator cannot emit all four, it exits 1 with a named error and writes zero files.
- **When** the dev agent inspects the generator's emission pattern
- **Then** every generated specialist ships all four lockstep files at the **pinned target paths below** in the same generator invocation (atomic — all four or none):
  1. **MODEL** — `app/specialists/{name}/state.py` with `{ClassName}Envelope(SpecialistEnvelope)` + `{ClassName}Return(SpecialistReturn)` subclasses (1.2 precedent at `app/models/state/specialist_envelope.py` + `app/models/state/specialist_return.py`)
  2. **VALIDATOR** — any `@model_validator(mode="after")` bodies inherited from parents verify correctly; no silent validator omission; generator does NOT emit a separate validator module unless the specialist introduces custom cross-field validation (then `app/specialists/{name}/validators.py` per 1.2 precedent)
  3. **TESTS** — `tests/specialists/{name}/test_{name}_state_shape.py` with shape-pin assertions (field names + types + required/optional flags) matching 1.2's precedent pattern at `tests/unit/models/state/test_specialist_envelope.py` (round-2 Winston+Amelia path correction: actual 1.2 test path is `tests/unit/models/state/`, NOT `tests/state/`; actual 1.2 filename is `test_<model>.py` without `_shape` suffix — generated specialists adopt `_shape` suffix going forward as a Slab-2-established convention per Murat round-2 caveat C)
  4. **GOLDEN FIXTURE** — `tests/fixtures/specialists/{name}/golden_envelope.json` + `tests/fixtures/specialists/{name}/golden_return.json` with representative valid payloads; round-trip test (`model_validate_json(golden.dumps())`) verifies determinism per NFR-X1
- **Three verification hooks (all three must pass):**
  1. The `_scaffold/` reference tree contains all four file classes (scaffold-local equivalents: `app/specialists/_scaffold/state.py` + inherited validators + `tests/specialists/_scaffold/test_scaffold_state_shape.py` + `tests/fixtures/specialists/_scaffold/golden_envelope.json`/`golden_return.json`).
  2. The `toytest` end-to-end run in AC-2a.1-C produces all four at their pinned paths.
  3. `pytest tests/specialists/toytest/ --collect-only` reports ≥4 discoverable tests at green-path; the generator's own test suite includes `test_generator_four_file_lockstep.py` asserting all four files exist AND a `--force` collision path rolls back cleanly on mid-emission failure (R9 atomicity test — see Testing Requirements).

### AC-2a.1-G — Toytest cleanup (no pollution) [R2 — binary criterion]

- **Given** `toytest` was generated by AC-2a.1-C for acceptance verification
- **When** the story closes
- **Then** `toytest` is either:
  - **Option Y (DEFAULT) — moved to `tests/fixtures/specialists/fixture_generated_specialist_for_acceptance_test.py`** as a **fixture-named file (prefix `fixture_` not `test_`)** pytest does NOT auto-collect (per Story 31-3 M-AM-4 precedent), used by a top-level generator regression test at `tests/specialists/generator/test_generator_emits_conformant_toytest.py` that re-runs generation into a `tmp_path` and diffs against the frozen fixture, OR
  - **Option X (FALLBACK) — fully deleted** from `app/specialists/toytest/` + `tests/specialists/toytest/` + `tests/integration/scaffold_conformance/test_scaffold_toytest.py` (no dangling specialist in the migrated tree)
- **Binary decision criterion (R2 — operationalizable at dev-agent execution time):** **Choose Option Y by default. Choose Option X ONLY if either of the following is true after a good-faith attempt at Option Y**:
  1. Retaining `toytest` as a fixture would require import cycles into `app/specialists/` production code (e.g., a test would need to `from app.specialists.toytest import ...` rather than loading the fixture file via `importlib.util`), OR
  2. Retaining `toytest` would cause `validate_scaffold` to traverse it on CI runs (e.g., `tests/integration/scaffold_conformance/` would still execute `test_scaffold_toytest.py` rather than the generator-regression test).
- Neither condition references wall-clock time. The dev agent makes the call by inspecting the test file structure at T7; no estimation required.

### AC-2a.1-H — Doc reference added (Specialist Walkthrough) [R3 — inline sub-checklist + Irene worked example]

- **Given** the generator is the authoritative path for Slab 2 specialist creation
- **When** the dev agent updates [`docs/dev-guide/langgraph-migration-guide.md §Specialist Walkthrough`](../../docs/dev-guide/langgraph-migration-guide.md) (currently a section pointer placeholder per 1.7 §11-section skeleton)
- **Then** the §Specialist Walkthrough subsection contains:

  **(a) The 5-step spine:** `git pull → skill invocation → generated files listing → conformance test run → manual post-edit checklist`

  **(b) Post-edit sub-checklist (inline in AC-H, frozen format — dev agent must NOT re-derive):**
  1. Set `app/specialists/<name>/model_config.yaml::default_model` to the correct model ID from `app/models/registry.py::MODEL_REGISTRY` (per D2 cascade; see [`model-selection-guide.md`](../../docs/dev-guide/model-selection-guide.md))
  2. Populate `app/specialists/<name>/expertise/` with domain reference documents (L5+ tier content); update `expertise/README.md` to list them
  3. Wire the `act` node body if the specialist is NOT a passthrough (i.e., replace the default `_stub.passthrough_specialist.passthrough_node` reference with a real LLM-invoking function); leave passthrough for Slab 1 compatibility if intentional
  4. Update `app/specialists/<name>/graph.py` state reducers only if the specialist introduces custom state fields beyond `SpecialistEnvelope`/`SpecialistReturn` inheritance; otherwise leave untouched

  **(c) One worked before/after example using Irene (Pass 2):**
  - **CLI invocation verbatim:** `uv run python -m skills.bmad_create_specialist.scripts.generate --name irene --mcp none --expertise-tier L5-narration-pass-2 --from-skill skills/bmad-agent-content-creator/`
  - **File tree after generation** (expected 5–10 lines of `tree app/specialists/irene/` output)
  - **Specific lines in `model_config.yaml`** that the human-in-the-loop edits (typically `default_model:` + `temperature_default:` + `per_node_overrides:`)
  - **Before/after diff fragment for the `act` node** showing transition from passthrough stub to Irene's Pass-2 narration-authoring function (~10–20 lines of unified diff)

  **(d) Cross-references at the end:** [`scaffold-conformance-framework.md`](../../docs/dev-guide/scaffold-conformance-framework.md) + [`specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) + [`model-selection-guide.md`](../../docs/dev-guide/model-selection-guide.md)

**Length budget:** §Specialist Walkthrough target is 80–120 lines (spine + sub-checklist + one worked example + cross-refs). Beyond 150 lines is over-scope.

### AC-2a.1-I — Anti-pattern harvest (D12 close protocol) [R4 — format frozen inline]

- **Given** Slab 2a opening surfaces the first real instance of Epic-vs-reality drift (captured in T1 readiness flag above) + may surface others during implementation
- **When** the story closes
- **Then** [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) gains **at minimum one** new entry in the **frozen four-field format** (format pinned at Paige 2026-04-22 amendment; **format changes require party-mode consensus — do NOT add fields**):

  ```markdown
  ### <name>
  - **Example:** <concrete instance; cite commit/story/line>
  - **Counter-pattern:** <what to do instead; cite framework/doc as source-of-truth>
  - **Slab of discovery:** <Slab N or story ID>
  ```

  No `notes:`, `severity:`, `rationale:`, `owner:`, or other supplementary fields. Four fields. Exactly.

- **Minimum entry (dev agent must file this verbatim as the shape, adapting `<…>` fields to this story's actual harvest):**

  ```markdown
  ### Epic-doc node-name drift from Slab-1-hardened framework
  - **Example:** Epic 2a §Story 2a.1 line 555 uses node names `plan/enter_sanctum/load_expertise/reason/act/validate/emit/return/exit_sanctum`; Slab-1-hardened `scaffold_contract.py::SCAFFOLD_NODE_IDS` (commit `9526a6c`) uses `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`. The 9 names do not map.
  - **Counter-pattern:** Dev agent reads `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS` as node-name source of truth, NOT epic-doc AC text. If the two disagree, the framework always wins. The Slab 2+ T1 Readiness checklist requires an explicit epic-doc-vs-framework cross-check line item (see AC-2a.1-I').
  - **Slab of discovery:** Slab 2a (Story 2a.1 authoring)
  ```

- Additional entries if implementation surfaces more; each follows the four-field format verbatim.

### AC-2a.1-I' — Slab 2+ T1 Readiness epic-doc-vs-framework cross-check (standing protocol) [R5 — two-layer treatment]

- **Given** anti-pattern #3 (architecture-vs-epics drift; Mary 2026-04-22 amendment) is a recurring risk across ALL Slab 2+ stories because epics were authored pre-Slab-1 hardening and no one will retrofit epic-doc prose mid-migration
- **When** this story closes
- **Then** the Slab 2+ T1 Readiness template (shared across 2a.2 / 2a.3 / 2a.4 / 2b.1–2b.17 / 2c.1–2c.4 / Slab 3+ as applicable) gains a standing line item:

  > **Epic-doc-vs-framework cross-check:** identify the authoritative framework source for any contract referenced in the story's ACs (e.g., `scaffold_contract.py` for node names, `app/models/state/` for state shapes, `model_config.yaml` for cascade). Compare against the epic-doc AC text. If drifts exist, flag in T1 Readiness, use the framework, and harvest the drift as a `specialist-anti-patterns.md` entry at close.

- **Landing point:** add this line to [`docs/dev-guide/scaffold-conformance-framework.md`](../../docs/dev-guide/scaffold-conformance-framework.md) §How specialists register as a T1-readiness pre-flight checklist section; future migration story specs reference that section from their T1 readiness blocks (one-line `See scaffold-conformance-framework.md §T1 Readiness Pre-Flight` reference). Story 2a.1 writes the checklist section itself AND the cross-reference pointer from its own T1 block.
- **Verification:** at close, `docs/dev-guide/scaffold-conformance-framework.md` has a §T1 Readiness Pre-Flight section with the cross-check line item AND a worked example showing Story 2a.1's own Epic 2a line 555 catch.

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

### AC-2a.1-L — Gate-decision node binding semantics [round-2 Winston+Amelia]

- **Given** every generator-emitted `gate_decision` node uses [`gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md) (landed in Commit B SP3, 2026-04-24)
- **When** the generator emits `app/specialists/<name>/graph.py`
- **Then** the generated file (a) **imports `resume_from_verdict` from `app.gates.resume_api` at module level** for Contract C3 binding stability (the import IS the C3 binding point, not a runtime call), (b) **the `gate_decision` node body uses `interrupt()` pattern** per [`langgraph-state-idioms.md §5`](../../docs/dev-guide/langgraph-state-idioms.md) — NOT a direct call to `resume_from_verdict` which would explode at runtime with `NotImplementedError` (Slab 1 stub body), (c) the emitted template includes the full reference body + one-line comment `# resume_from_verdict body lands at Slab 3 Story 3.3`.
- **Why this AC exists:** round-2 Winston+Amelia caught a runtime-detonation risk: naively binding `gate_decision` node to `resume_from_verdict` would blow up every Slab 2 smoke test routing through a gate. Generator template MUST emit the `interrupt()` pattern.

### AC-2a.1-M — Template-var `specialist_id` = ClassVar, NOT field redefinition [round-2 Amelia]

- **Given** `SpecialistEnvelope` (from `app.models.state.specialist_envelope`) already defines `specialist_id: str` as a field (inherited by every generated `<Name>Envelope` subclass)
- **When** the generator substitutes `{{specialist_id}}` into emitted `state.py`
- **Then** the substitution writes a **`ClassVar[str]` constant** (e.g., `_SPECIALIST_ID: ClassVar[str] = "{{specialist_id}}"`) on the subclass used by validators for specialist-ID pattern-match pinning, **NOT a field redefinition** (e.g., `specialist_id: str = "{{specialist_id}}"`) which would shadow the inherited field and break `ConfigDict(extra="forbid")` validation on parent.
- **Why this AC exists:** round-2 Amelia caught a silent shadowing hazard — a dev agent reading AC-F could plausibly write `specialist_id: str = "{{specialist_id}}"` which passes Pydantic construction (inherited field type-matches) but breaks `extra="forbid"` at runtime when parent validates assignment. ClassVar-not-field is the correct shape.

### AC-2a.1-N — Category D dissolution generator denylist [round-2 Mary]

- **Given** `skills/bmad-agent-audra/` and `skills/bmad-agent-cora/` are DISSOLVED per [DR-2](../planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md) (Category D, ratified 2026-04-24); neither migrates as a LangGraph runtime node
- **When** the generator's `--from-skill` path is invoked with a denylisted skill directory
- **Then** the generator EXITS 1 with a named `GeneratorInputError: skill directory {skill_dir} is DISSOLVED per DR-2 (Category D). If the dissolution decision should be reversed, raise at party-mode consensus per DR-2 §Reversal protocol — do NOT bypass the denylist by renaming the target directory. See _bmad-output/planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md.` No files are created or modified.
- **Implementation pin:** `GENERATOR_DENYLIST: frozenset[str] = frozenset({"bmad-agent-audra", "bmad-agent-cora"})` at module-level in `skills/bmad-create-specialist/scripts/generate.py`. Denylist checked in the `--from-skill` path's input validation (AC-2a.1-E negative paths).
- **Test pin:** `tests/specialists/generator/test_generator_rejects_category_d.py` — parametrized test with both denylisted paths + asserts `GeneratorInputError` + asserts zero writes to `app/specialists/`. Adds +2 collecting nodes to Murat R9 test count.
- **Why this AC exists:** round-2 Mary governance-preservation argument — without the denylist, a future operator (or confused dev agent) running `python -m skills.bmad_create_specialist.scripts.generate --from-skill skills/bmad-agent-audra/` would emit a conformant `app/specialists/audra/` with a full 4-file scaffold. Category-D-specialist sitting unwired in `app/specialists/` is a future erosion invitation. Denylist is cheap governance-preserving insurance.

### AC-2a.1-O — Template-var substitution is real (not file-copy) [round-2 Murat]

- **Given** R9 test `test_generator_template_var_literal_survival.py` asserts that unknown template vars survive verbatim as literals in emitted files
- **When** the generator is authored
- **Then** the template engine MUST perform **real substitution** (at minimum one `{{var}}` → value replacement per emitted file) rather than raw file-copy with post-process rename. If the generator in 2a.1 is pure file-copy (no template substitution path), the R9 literal-survival test is a no-op and the K-target's 4-file atomicity + literal-survival subset needs to defer to 2a.2.
- **Verification:** T1 Readiness block confirms at least one template var is substituted in the emitted `state.py` and `model_config.yaml` (most plausibly `class_name` into `<Name>Envelope` / `<Name>Return` and `specialist_id` into `_SPECIALIST_ID` ClassVar per AC-M).

### AC-2a.1-Z — Collision-prevention meta-test [round-2 Murat]

- **Given** 2a.1 creates a new `tests/specialists/` subtree (did not exist at Slab 1 close); Slab 1's state model tests live at `tests/unit/models/state/`
- **When** 2a.1 closes
- **Then** a one-line assertion confirms no accidental collision: `pytest --collect-only tests/specialists/` returns ≥18 items + `pytest --collect-only tests/state/` returns 0 items (confirms no accidental parallel subtree was created at the drift-path `tests/state/` from the original stale-path assumption). Verification lands in T8 regression block of Dev Agent Record.

---

## Architecture Compliance

### Decisions the story honors

| Decision | Application |
|---|---|
| **D1 — Sanctum hybrid** | Generator emits `expertise/README.md` that references the specialist's sanctum tree at `_bmad/memory/bmad-agent-<name>/` (hybrid BMB pattern per Epic 26). Sanctum content is NOT generator-authored; operator populates during first-breath. |
| **D2 — Three-level model cascade** | `model_config.yaml` template emits all three levels **with inline comments explaining cascade order** (R7): `# Level 1: per-call override (set via RunState.model_overrides at runtime)` / `# Level 2: per-specialist default (this field)` / `# Level 3: registry default (app/models/registry.py)`. Inline comments protect against downstream editors stripping levels thinking they're unused. 2a.1 tests the shape; 2a.2–2a.4 exercise the resolution. |
| **D3 — HIL invariant tamper-evidence** | Generator's `graph.py` template **imports `resume_from_verdict` for Contract C3 binding stability** + **implements `gate_decision` node body via `interrupt()`** per AC-2a.1-L + [`gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md) (round-3 Commit B SP3). No scheduler imports inside `app.gates.**` per Contract C2. |
| **D4 — Lane separation** | Generator targets `app/specialists/<name>/`; import-linter Contract C1 enforces no cross-lane imports. |
| **D8 — Frozen-graph ceremony** | `app/specialists/_scaffold/graph.py` is the frozen reference (Slab 4 Story 4.5 freezes per-specialist graphs; 2a.1 establishes the unfrozen template). |
| **D12 — Cross-slab governance** | Close protocol per AC-2a.1-K; anti-pattern harvest per AC-2a.1-I. |
| **D13 — Registry bump** | Not relevant at 2a.1; Slab 4 ceremony. |

### Architecture-to-code mapping

- **Canonical 9 nodes** per [`tests/integration/scaffold_conformance/scaffold_contract.py`](../../tests/integration/scaffold_conformance/scaffold_contract.py#L22). **Do not add/remove/rename nodes in this story** — any amendment requires party-mode + re-bump scaffold_contract.py version.
- **LangGraph API:** `StateGraph` construction with `.add_node(name, fn)` for each of the 9; `.set_entry_point("receive")`; internal edges `receive → plan → act → verify → reflect → emit_spans → (gate_decision branch) → finalize → handoff`; `gate_decision` uses `Command(goto=...)` for branch logic per langgraph-state-idioms.md §Command patterns.
- **RunState + SpecialistEnvelope + SpecialistReturn** per [`app/models/state/`](../../app/models/state/) (Story 1.2). Generator template emits subclasses, not wholesale redefinitions.

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

### CLI argument surface (R11 — `--dry-run` + `--from-skill` flags)

Generator CLI (`python -m skills.bmad_create_specialist.scripts.generate`) accepts:

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--name <str>` | string, regex `^[a-z][a-z0-9_]*$` (per R14 1.3 `_SPECIALIST_ID_PATTERN` reuse) | required | Target `app/specialists/<name>/` |
| `--mcp <enum>` | one of `{none, gamma, elevenlabs, canvas, kling, wondercraft}` | required | L7 MCP tool wiring hint for `act` node |
| `--expertise-tier <str>` | regex `L[3-7]-[a-z0-9-]+` | required | Expertise tier label (R9 boundary tests) |
| `--from-skill <path>` | path, must exist, must be under `skills/bmad-agent-*/` | optional | When provided, generator reads the legacy skill tree as a template-variable source (skill-ingest path per AC-C2); when omitted, emits from `_scaffold/` directly (shell-emit path per AC-C) |
| `--dry-run` | boolean flag | optional | **When set:** generator parses + shape-validates the would-be emission tree but writes ZERO files; stdout enumerates the planned file tree + validation results; exit code mirrors what a wet-run would produce. Wet-run is the default (flag absent). |
| `--force` | boolean flag | optional | Allow overwrite of existing `app/specialists/<name>/` target (collision recovery); atomic rollback on any mid-emission failure (R9 atomicity test) |

**Dry-run semantics (AC-C2 + R11 + Wondercraft optionality):** `--dry-run` writes nothing AND still exits with the same code a wet-run would (non-zero on validation failure). This lets 2c.1 probe the generator against `skills/bmad-agent-wondercraft/` without committing to Path A or Path B.

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

### K-target policy: ~1.8× (target 18–20 / floor 15) [R9]

**Amended 2026-04-24 party-mode per Murat R9** — original K=1.5× assumed pure schema-shape. Story 2a.1 has three stacked risk surfaces:

- ~3 Pydantic models (K=1.5× → 4.5 tests floor on models alone, per 1.2 precedent)
- CLI input parser with 4 regex/enum gates + 5 negative paths per AC-E (~5 tests)
- Four-file atomic emitter + template-var semantics (~4 tests at AC-F + R9 additions)
- Scaffold self-conformance + state-shape pinning (~2 tests)
- **Target:** 18–20 collecting tests (not just schema-shape math)
- **Floor:** 15 collecting tests (below this is insufficient dual-gate coverage)

### Test surface (R9-expanded)

| Test module | Coverage |
|---|---|
| `tests/specialists/generator/test_generator_emits_conformant_toytest.py` | Green-path end-to-end: generate → validate_scaffold → build graph → no errors |
| `tests/specialists/generator/test_generator_dry_run_against_irene.py` | **[NEW R6]** AC-C2: `--dry-run --from-skill skills/bmad-agent-content-creator/` emits nothing to disk; dry-run stdout enumerates would-be tree; shape-validation gates hold |
| `tests/specialists/generator/test_generator_input_validation.py` | AC-2a.1-E: 5+ negative path tests (invalid name / collision / bad --mcp / bad --expertise-tier / path traversal) |
| `tests/specialists/generator/test_generator_expertise_tier_regex_boundaries.py` | **[NEW R9]** `--expertise-tier` regex boundaries: `L3-` empty suffix fails; `L3--foo` double-hyphen behavior; `L8-x` out-of-range fails; `L3` no hyphen fails; `l3-foo` lowercase `l` fails |
| `tests/specialists/generator/test_generator_invalid_model_config.py` | AC-2a.1-D: compile raises named exception on invalid ref (error class verified at T1 per R10) |
| `tests/specialists/generator/test_generator_four_file_lockstep.py` | AC-2a.1-F: all 4 artifacts emitted; shape-pin tests discoverable |
| `tests/specialists/generator/test_generator_four_file_atomicity_on_force.py` | **[NEW R9]** `--force` collision semantics: mock `Path.write_text` to raise on file 3; assert either (a) no files written (full rollback) or (b) all 4 files written + rollback marker recorded. Partial-write state forbidden |
| `tests/specialists/generator/test_generator_template_var_literal_survival.py` | **[NEW R9 — HIGHEST PRIORITY per Murat risk assessment]** Emit a specialist from a scaffold containing a deliberately-unknown var `{{retrieval_provider}}`; grep emitted file; assert literal token present (scaffold-v0.2 V2-3 "survive as literal" contract). Catches silent-corruption-on-scaffold-evolution bug class |
| `tests/specialists/_scaffold/test_scaffold_reference_conforms.py` | `_scaffold/` itself validates via `validate_scaffold("_scaffold", ...)` → is_conforming |
| `tests/specialists/_scaffold/test_scaffold_state_shape.py` | `ScaffoldEnvelope` + `ScaffoldReturn` shape-pin (field count + types) |
| `tests/integration/scaffold_conformance/test_scaffold_toytest.py` | Emitted by generator per AC-2a.1-C; passes against generated toytest |
| `tests/specialists/generator/test_option_y_fixtures_not_autocollected.py` | **[NEW R9]** Run `pytest --collect-only tests/fixtures/specialists/`; assert zero items collected (confirms `fixture_` prefix discipline per 31-3 M-AM-4) |
| `tests/end_to_end/test_cache_hit_rate_baseline.py` | **[DOC-IN-TEST per R9 from Murat]** Skip reason string amended to: `"cache-hit-rate harness activates at first real LLM call — see Slab 2 story 2a.2 (Irene Pass 2) or 2a.4 (Texas) trigger"`. `allow_module_level=True`. No un-skip at 2a.1. |

### Regression floor (pre-story baseline at M1 close)

- **Slab 1 close:** 286 passed / 5 skipped / 1 deselected / 0 failed.
- **Target at 2a.1 T8 (R9 amendment):** ≥304 passed (286 + ≥18 new, realistic; stretch target ≥308) / 5 skipped (cache + 4 Postgres unchanged) / 1 deselected / 0 failed.
- **Floor:** ≥301 passed (286 + ≥15 new); below this fails R9 K-floor.
- **Import-linter:** 3/3 KEPT (C1 lane-isolation + C2 gates-no-scheduler + C3 bridge-module-only).
- **Ruff:** clean across all new/modified files.
- **Sandbox-AC validator:** PASS on this story spec.

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

1. **Toytest cleanup option** (AC-2a.1-G): dev agent defaults to Option Y (fixture-named regression anchor). Decision criterion is now binary per R2 (not time-based).
2. **Template-variable whitelist**: 5 variables currently (`name`, `class_name`, `mcp_tool`, `expertise_tier`, `specialist_id`). If Kira/Texas migrations at 2a.3/2a.4 need a 6th var (`retrieval_provider`), extend the whitelist at that story's T1 via the scaffold-v0.2 V2-3 preservation pattern. **R16 SOFT (deferred):** decide now at operator level whether to pre-bake the 6th var into 2a.1 or accept template-extension deferral to 2a.3/2a.4.
3. **Wondercraft decision carry-forward**: 2a.1 does not resolve Path A vs Path B. The generator's `--dry-run` flag (R11) now preserves optionality — operator can probe `skills/bmad-agent-wondercraft/` at any time before 2c.1 decides.

---

**Status:** ready-for-dev (party-mode-amended 2026-04-24)
**Completion note:** Ultimate context engine analysis completed — comprehensive developer guide created. T1 readiness block explicitly flags Epic-vs-reality drift to prevent re-propagation; framework-source-of-truth is `scaffold_contract.py`, not epic doc text. Governance JSON + severance posture pre-baked. Party-mode green-light on 2026-04-24 with 5/5 GREEN-with-riders verdicts; 6 MUST-FIX + 5 SHOULD-FIX riders applied per operator Option-3 directive (6 SOFT riders deferred to dev-agent T1 discretion).
