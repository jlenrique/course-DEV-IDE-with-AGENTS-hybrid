# Migration Story 2a.2: Migrate Irene Pass 2 to 9-Node Scaffold

**Status:** ready-for-dev
**Sprint key:** `migration-2a-2-migrate-irene-pass-2-to-9-node-scaffold`
**Epic:** Slab 2a (migration Epic 2a) — **second Slab 2a story**; opens post-2a.1-BMAD-CLOSED (commit `e14616c`).
**Milestone anchored:** Feeds M2 (17-specialist scaffold + Wondercraft pilot <1 dev-day). **THIS STORY IS THE CACHE-HIT-RATE HARNESS ACTIVATION POINT** per [`deferred-inventory.md` §Named-Follow-Ons](../planning-artifacts/deferred-inventory.md) trigger — Irene Pass 2 is the first real LLM-invoking specialist to land.
**Pts:** 3 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::2a-2`, rationale: null — follows 2a.1 TEMPLATE pattern, no new schema-shape, no new CI contract) | **K-target:** ~1.4×

---

## Party-Mode Amendment Log (authoring-time)

No party-mode round convened at story-author time; authoring rides [DR-1 GOLDEN ratification](../planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md) (Slab 1 + 2a.1 are immutable-correct substrate; spec yields to code on conflict) + round-3 caveats already landed in Commit B hardening (session 2026-04-24).

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order per [`scaffold-conformance-framework.md §T1 Readiness Pre-Flight`](../../docs/dev-guide/scaffold-conformance-framework.md):

### Standing Pre-Flight items (applies to every Slab 2+ story)

1. **Governance lookup** — [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) — confirms Story 2a-2 is `expected_gate_mode: "single-gate"` with `rationale: null`. Do not relitigate.
2. **Canonical 9-node contract** — [`tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`](../../tests/integration/scaffold_conformance/scaffold_contract.py) frozenset (`receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`). **This is the authoritative source of truth for node names.**
3. **Gate-decision binding** — [`docs/dev-guide/gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md). Generator emits `interrupt()` pattern; `resume_from_verdict` is imported for Contract C3 binding but **NOT invoked at runtime** until Slab 3.3.
4. **State contracts** — [`app/models/state/`](../../app/models/state/) (from Story 1.2). Irene's subclasses (`IreneEnvelope(SpecialistEnvelope)` + `IreneReturn(SpecialistReturn)`) inherit the substrate; any new fields follow 1.2 four-file-lockstep.
5. **Model cascade** — [`docs/dev-guide/model-selection-guide.md`](../../docs/dev-guide/model-selection-guide.md) + [`app/models/selection_policy.yaml`](../../app/models/selection_policy.yaml). **Actual tiers are `reasoning / fast / code` (NOT "long-context balanced" as epic text states — see drift flag #2 below).**
6. **LLM-live skip-fixture** — [`tests/conftest.py`](../../tests/conftest.py) auto-skips `@pytest.mark.llm_live` when `OPENAI_API_KEY` is unset or holds the placeholder sentinel. Cache-hit-rate measurement AC uses this marker.
7. **Severance posture** — [`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md). No `git show upstream/master:…`. Hybrid working tree is sole input surface. Irene's source at `skills/bmad-agent-content-creator/` (hybrid commit `835e650` post-absorption).
8. **Generator entrypoint** — `skills/bmad-create-specialist/` shipped by Story 2a.1 (commit `cc79df5`). Invoke via `uv run python -m skills.bmad_create_specialist.scripts.generate --name irene --mcp none --expertise-tier L5-narration-pass-2 --from-skill skills/bmad-agent-content-creator/`. Generator denylist (DR-2 per Category D dissolution) does NOT block this path (Irene is Category A+B).

### Slab-1 + 2a.1 artifact-existence sweep (per round-3 Murat R10 broadened)

At T1, confirm all 7 artifacts exist at stated paths + shape (grep + one-line-eval each):

- **A** `app/manifest/compiler.py::compile()` raises `CompileError` (additive-only validator per commit `2a336df`)
- **B** `app/models/state/specialist_envelope.py::SpecialistEnvelope` + `specialist_return.py::SpecialistReturn` with `ConfigDict(extra="forbid", validate_assignment=True)`
- **C** `app/specialists/_stub/passthrough_specialist.py::passthrough_node` returns `{}` — generator's default `act` body until real LLM wires in here
- **D** `app/gates/resume_api.py::resume_from_verdict` raises `NotImplementedError`; generator imports for C3 binding, does NOT invoke
- **E** `app/specialists/_scaffold/{graph,state,model_config,expertise}` populated (from 2a.1)
- **F** `skills/bmad-create-specialist/scripts/generate.py` exits 0 on valid invocation (2a.1 generator works)
- **G** `tests/end_to_end/test_cache_hit_rate_baseline.py` exists with `pytest.skip(...)` skip-reason pointing to 2a.2/2a.4 trigger

### Epic-doc-vs-framework cross-check (standing protocol; THREE drifts flagged at this story)

**⚠️ Drift #1 — Node names (Epic 2a.2 lines 584–585):** epic AC text uses `reason/act/validate/emit/return` — **does NOT match** `SCAFFOLD_NODE_IDS` (`receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`). **Follow the framework.** This is anti-pattern #3 re-surfacing identical to 2a.1's Epic 2a line 555 case; harvest as a second A9-style entry (or consolidate into A9 if appropriate at G5 review).

**⚠️ Drift #2 — Model ID + tier (Epic 2a.2 line 587–589):** epic says *"Irene uses model tier 'long-context balanced'... default resolves to `gpt-4.1`"*. **Reality:** [`app/models/registry.yaml`](../../app/models/registry.yaml) has entries `gpt-5.4`, `gpt-5-haiku`, `gpt-5-codex` (NO `gpt-4.1`); [`app/models/selection_policy.yaml`](../../app/models/selection_policy.yaml) has tiers `reasoning / fast / code` (NO "long-context balanced"). **Follow the framework.** Irene's narration-Pass-2 workload maps to `tier_request: reasoning` (long-context reasoning) → resolves to `gpt-5.4` per selection policy. Document mapping rationale in Irene's `model_config.yaml` comments. Harvest as a new anti-pattern entry (epic model-ID drift distinct from node-name drift).

**⚠️ Drift #3 — Sanctum path (Epic 2a.2 line 581):** epic says *"`_bmad/memory/bmad-agent-irene/` sanctum symlink present"*. **Reality:** hybrid sanctum tree is `_bmad/memory/bmad-agent-content-creator/` (follows skill-dir name, NOT short app-side specialist name). Per CLAUDE.md §Custom agents + Epic 26 BMB sanctum migration pattern, hybrid uses direct directory (not symlink). **Follow the framework.** Irene's sanctum lives at `_bmad/memory/bmad-agent-content-creator/` (existing, empty post-severance). App-side specialist `app/specialists/irene/expertise/README.md` references this path by dotted convention.

**All three drifts are expected at Slab 2+ and are exactly what anti-pattern #3 standing-protocol T1 pre-flight is designed to catch.** Dev agent logs all three in Dev Agent Record T1 Readiness block + uses the framework in every case.

**Governance pre-flight (single run before T2):**
```bash
python scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-2a-2-irene-pass-2-scaffold-migration.md
```
Expect PASS.

---

## Story

As a **migration dev agent**,
I want **Irene Pass 2's narration-authoring dispatch rehomed into `app/specialists/irene/` with the 9-node scaffold + model cascade wired to `tier_request: reasoning` → `gpt-5.4` + sanctum reference to `_bmad/memory/bmad-agent-content-creator/` + scaffold-conformance test green + cache-hit-rate baseline harness activated on Irene's second invocation**,
So that **the first REAL LLM-invoking specialist migration proves the scaffold pattern end-to-end, closes FR9–FR16 for Irene, activates FR54 cache-hit-rate measurement that was substrate-deferred at M1 per ACCEPT-WITH-GAP, and validates that 2a.1's generator produces a conformant specialist from a real primary-authored skill directory**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Cache-hit-rate measurement (AC-D) uses `@pytest.mark.llm_live` + a real `OPENAI_API_KEY` — when no key is available, the test auto-skips; operator-gated Completion-Notes evidence block captures the paste on operator machine.

### AC-2a.2-A — Generator emits Irene from skill directory

- **Given** `skills/bmad-agent-content-creator/` contains Irene's Pass-2 scripts + references (38 references + 5 scripts including `perception_contract.py`, `visual_reference_injector.py`, `motion_gate_receipt_reader.py`, `manifest_visual_enrichment.py`, `manual_animation_workflow.py`); generator at `skills/bmad-create-specialist/` is proven (Story 2a.1)
- **When** the dev agent runs `uv run python -m skills.bmad_create_specialist.scripts.generate --name irene --mcp none --expertise-tier L5-narration-pass-2 --from-skill skills/bmad-agent-content-creator/`
- **Then** `app/specialists/irene/` exists with `__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, `expertise/README.md`; `validate_scaffold("irene", build_irene_graph()).is_conforming is True`; ruff clean; import-linter C1 (lane-isolation) PASS.

### AC-2a.2-B — Irene `act` node wires real LLM (replaces passthrough)

- **Given** 2a.1's generator emits `act` node defaulting to `passthrough_node` (returns `{}`)
- **When** the dev agent replaces `app/specialists/irene/graph.py::act_node` body with the real Pass-2 narration-authoring logic (reads input envelope payload with `cluster_plan` + `slide_briefs` + `segment_manifest` draft; invokes LLM via `app.models.adapter.ChatOpenAIAdapter` with `tier_request: reasoning` resolving to `gpt-5.4`; produces narration script + enriched segment_manifest per [`skills/bmad-agent-content-creator/references/pass-2-procedure.md`](../../skills/bmad-agent-content-creator/references/pass-2-procedure.md) contract)
- **Then** invoking `build_irene_graph()` with a realistic `IreneEnvelope` (fixture + real LLM with `OPENAI_API_KEY` set) produces a non-empty `IreneReturn` with a narration script + segment manifest matching 1.2's `SpecialistReturn` shape-pin; `reflect` node self-assesses per pass-2-procedure G4 criteria; `finalize` builds `SpecialistReturn` with `verb="proceed"`; `handoff` returns `Command(goto=<next>, update=...)`. Test tagged `@pytest.mark.llm_live` (auto-skip on placeholder `OPENAI_API_KEY`).

### AC-2a.2-C — Model cascade resolves correctly at Irene's `plan` node

- **Given** Irene's `model_config.yaml` specifies `default_model: "gpt-5.4"` (follows DR-1 spec-yields-to-code rule; epic `gpt-4.1` is drift) + per-node override map + `temperature_default: 0.3` (narration creativity tolerance — rationale documented inline per NFR-X5)
- **When** `app.models.selector.resolve_model()` runs at Irene's `plan` node with no runtime override
- **Then** resolution trail appends a `ModelResolutionEntry` with `resolved_model_id="gpt-5.4"`, `resolution_level="per-specialist-default"`, and a cache-prefix hash per 1.3; with a runtime `RunState.model_overrides={"irene": "gpt-5-haiku"}` set, resolution returns `gpt-5-haiku` at `resolution_level="per-call-override"`.
- **Test pin:** `tests/specialists/irene/test_irene_model_cascade.py` — 2 tests (default + override).

### AC-2a.2-D — Cache-hit-rate baseline harness ACTIVATED (FR54)

- **Given** Irene's `act` node invokes LLM with deterministic cache-prefix (`temperature=0.0` for this test; real production uses 0.3)
- **When** the dev agent un-skips [`tests/end_to_end/test_cache_hit_rate_baseline.py`](../../tests/end_to_end/test_cache_hit_rate_baseline.py) — removing the `pytest.skip(...)` guard; retargets the harness to invoke Irene's scaffold twice with identical envelope input; measures OpenAI prompt-cache hit rate on second invocation via LangSmith trace or OpenAI usage API cache-prefix metric
- **Then** cache hit rate on second invocation is **≥60%** per PRD §M1 acceptance bar. Test tagged `@pytest.mark.llm_live`. Closes the M1 ACCEPT-WITH-GAP deferred clause ([M1 evidence pack](m1-acceptance-evidence-pack.md) §Cache-Hit-Rate Clause).
- **If measurement comes in below 60%:** story does NOT close. Dev agent investigates (cache-prefix stability per NFR-I6; model choice; temperature; invocation-path determinism); amendment party-mode round convenes before retry.
- **Update to M1 evidence pack:** at story close, append "M1 cache-hit-rate gap: CLOSED at Story 2a.2 closure. Measured rate: XX% on second invocation." + link to this story's Completion Notes.

### AC-2a.2-E — Gate-decision node uses `interrupt()` pattern (post-2a.1)

- **Given** 2a.1's generator emits `gate_decision` as interrupt-placeholder per [`gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md)
- **When** the dev agent invokes Irene's graph in a test that routes through `gate_decision` (e.g., post-Pass-2 gate)
- **Then** the graph PAUSES at `gate_decision` via `interrupt()`; does NOT call `resume_from_verdict` (which would raise `NotImplementedError`); test uses Pattern 1 (pre-populate `OperatorVerdict` in state) OR Pattern 2 (assert `InterruptException` fires) from the binding-semantics doc.
- **Test pin:** `tests/specialists/irene/test_irene_gate_decision_interrupt.py` — 2 tests (one per pattern).

### AC-2a.2-F — Sanctum cold-read at `plan` node (FR15 first full exercise)

- **Given** Irene's sanctum at `_bmad/memory/bmad-agent-content-creator/` (hybrid path — DIFFERENT from epic's stale `bmad-agent-irene/` per drift #3)
- **When** Irene's `plan` node runs `load_expertise` (via `app.models.state.sanctum_fingerprint.SanctumFingerprint.compute(...)`) and D1 cold-read discipline is enforced
- **Then** sanctum payload includes Irene's L5 references by dotted convention: `pass-2-procedure.md`, `pass-2-authoring-template.md`, `pass-2-grammar-riders-examples.md`, `retrieval-intake-contract.md`, `cluster-narrative-arc-schema.md` (+ others per Irene's `expertise/README.md`); `SanctumFingerprint` deterministic hash is computed per D1 snapshot-size heuristic.
- **Test pin:** `tests/specialists/irene/test_irene_sanctum_cold_read.py` — 1 test: sanctum fingerprint is deterministic across two reads + L5 refs are present. (At 2a.2, sanctum content may be empty/minimal on hybrid fork point; test asserts fingerprint stability + reference-name shape, not content depth — full content populates at first-breath operator ceremony post-M5.)

### AC-2a.2-G — Resolution trail + LangSmith spans (FR16 first full exercise)

- **Given** Irene's `plan` node appends to `RunState.model_resolution_trail` + Irene's `emit_spans` node publishes LangSmith spans per NFR-O4
- **When** Irene's scaffold runs end-to-end
- **Then** `RunState.model_resolution_trail` has ≥1 `ModelResolutionEntry` naming the resolved model + cache-prefix hash + resolution level; LangSmith spans include `specialist_id="irene"`, `node_id` per 9-node set, `resolution_level`, and the cache-prefix tag.
- **Test pin:** `tests/specialists/irene/test_irene_resolution_trail.py` — 1 test.

### AC-2a.2-H — Irene shape-pin tests (four-file-lockstep per 1.2)

- **Given** the generator emits `app/specialists/irene/state.py` with `IreneEnvelope` + `IreneReturn` subclasses
- **When** the dev agent verifies 1.2 four-file-lockstep discipline on Irene's schema surface
- **Then** all four lockstep files exist:
  1. **MODEL** — `app/specialists/irene/state.py`
  2. **VALIDATOR** — inherited from parents; no Irene-specific separate module needed (follows 2a.1 Resolution B; document rationale in state.py docstring)
  3. **TESTS** — `tests/specialists/irene/test_irene_state_shape.py` with ≥4 tests: envelope field presence + return field presence + round-trip determinism (NFR-X1) + invalid-payload red-rejection
  4. **GOLDEN FIXTURE** — `tests/fixtures/specialists/irene/golden_envelope.json` + `golden_return.json`

### AC-2a.2-I — Scaffold-conformance test registered

- **Given** the scaffold-conformance framework at `tests/integration/scaffold_conformance/`
- **When** Irene migrates
- **Then** new file `tests/integration/scaffold_conformance/test_scaffold_irene.py` imports `build_irene_graph` + calls `validate_scaffold("irene", ...)` + asserts `.is_conforming is True`; file follows the pattern from framework doc.

### AC-2a.2-J — Migration-guide Specialist Walkthrough updated (D12)

- **Given** 2a.1 populated [`docs/dev-guide/langgraph-migration-guide.md §12 Specialist Walkthrough`](../../docs/dev-guide/langgraph-migration-guide.md) with the Irene hypothetical worked example
- **When** Irene actually migrates at 2a.2, the worked example shifts from hypothetical to real
- **Then** §12 is updated (a) replacing the hypothetical Irene CLI invocation + file tree with the actual invocation + actual file tree + actual diff snippets from this story's commit; (b) annotating where real-world execution diverged from the 2a.1 plan (expected areas: `act` node LLM invocation body, sanctum path Drift #3, model-ID Drift #2); (c) keeping the 5-step spine + 4-item post-edit sub-checklist intact as the template for 2a.3 Kira + 2a.4 Texas.

### AC-2a.2-K — Close protocol (D12)

- **Given** 2a.2 is not a slab-closing story
- **When** the story closes
- **Then** the three-line D12 close stub is recorded in Dev Agent Record:
  1. **Invariant preservation:** FR9–FR12 + FR15 + FR16 closed for Irene (per-specialist); FR54 closed at substrate level (first cache-hit-rate measurement on second invocation); Slab-1 substrate intact (regression ≥303 post-close baseline).
  2. **Anti-pattern harvest:** up to 3 new entries — node-name drift (existing A9 gains second example), model-ID drift NEW, sanctum-path drift NEW. Format per [`specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) format-freeze.
  3. **Migration-guide update:** §12 Specialist Walkthrough upgraded to real-Irene worked example per AC-J.

---

## Architecture Compliance

### Decisions the story honors

| Decision | Application |
|---|---|
| **D1 — Sanctum hybrid** | Sanctum path `_bmad/memory/bmad-agent-content-creator/` (follows skill-dir name per CLAUDE.md + Epic 26 pattern; epic drift #3 ignored per DR-1). Cold-read discipline per AC-F. |
| **D2 — Three-level model cascade** | `gpt-5.4` default (not epic's stale `gpt-4.1`); per-call override propagates; resolution trail appended per AC-C. |
| **D3 — HIL tamper-evidence** | `resume_api` import for C3 binding; `interrupt()` pattern per AC-E. |
| **D4 — Lane separation** | `app/specialists/irene/` in `run_graph` lane per import-linter C1; no cross-lane imports. |
| **D5 — Sanctum cold-read + cache-prefix stability** | Cold reads at `plan` node per AC-F; cache-prefix stability per NFR-I6 validated by AC-D cache-hit-rate measurement. |
| **D12 — Cross-slab governance** | D12 close stub per AC-K. |
| **D13 — Registry bump** | Not applicable at 2a.2 (registry unchanged). |

### FR coverage closed by this story

- **FR9** (lane-isolated specialist package) — `app/specialists/irene/` under `run_graph` lane enforced by C1
- **FR10** (state-subclass discipline) — `IreneEnvelope(SpecialistEnvelope)` + `IreneReturn(SpecialistReturn)` per AC-H
- **FR11** (model_config per-specialist) — Irene's `model_config.yaml` shipped per AC-C
- **FR12** (expertise directory per-specialist) — Irene's `expertise/README.md` with L5 refs per AC-F
- **FR15** (sanctum cold-read) — first full exercise per AC-F
- **FR16** (resolution trail) — first full exercise per AC-G
- **FR54** (cache-hit-rate) — **ACTIVATED + MEASURED** per AC-D; closes M1 ACCEPT-WITH-GAP deferred clause

FR13 + FR14 were closed at 2a.1 at substrate level; 2a.2 is the first per-specialist execution of those contracts.

---

## File Structure Requirements

### NEW files (dev agent + generator author these)

```
app/specialists/irene/
├── __init__.py                           # Package marker
├── graph.py                              # 9-node StateGraph (generator-emitted, act body hand-authored)
├── state.py                              # IreneEnvelope + IreneReturn subclasses
├── model_config.yaml                     # Three-level cascade; default_model: "gpt-5.4"
└── expertise/
    └── README.md                         # L5 refs pointer to skills/bmad-agent-content-creator/references/

tests/specialists/irene/
├── __init__.py
├── test_irene_state_shape.py             # 1.2 four-file-lockstep MODEL shape
├── test_irene_model_cascade.py           # AC-C (2 tests: default + override)
├── test_irene_gate_decision_interrupt.py # AC-E (2 tests: pre-populate + assert-fires)
├── test_irene_sanctum_cold_read.py       # AC-F (1 test)
├── test_irene_resolution_trail.py        # AC-G (1 test)
└── test_irene_act_node_llm_invocation.py # AC-B @pytest.mark.llm_live (auto-skip on placeholder key)

tests/integration/scaffold_conformance/
└── test_scaffold_irene.py                # AC-I — validate_scaffold("irene", ...)

tests/fixtures/specialists/irene/
├── golden_envelope.json                  # Representative IreneEnvelope payload
└── golden_return.json                    # Representative IreneReturn payload

_bmad/memory/bmad-agent-content-creator/  # EXISTING empty dir; expertise README references; no writes at 2a.2
```

### MODIFIED files

- [`tests/end_to_end/test_cache_hit_rate_baseline.py`](../../tests/end_to_end/test_cache_hit_rate_baseline.py) — un-skip + retarget at Irene; `@pytest.mark.llm_live`
- [`docs/dev-guide/langgraph-migration-guide.md §12 Specialist Walkthrough`](../../docs/dev-guide/langgraph-migration-guide.md) — real Irene worked example per AC-J
- [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) — up to 3 new entries per AC-K
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](sprint-status.yaml) — flip `migration-2a-2-…` ready-for-dev → in-progress → done
- [`_bmad-output/implementation-artifacts/m1-acceptance-evidence-pack.md`](m1-acceptance-evidence-pack.md) — close the cache-hit-rate deferred clause
- [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md) — remove cache-hit-rate un-skip follow-on (now closed)

### NOT modified

- `tests/integration/scaffold_conformance/scaffold_contract.py` — frozen
- `app/specialists/_scaffold/` — reference remains untouched
- `app/specialists/_stub/passthrough_specialist.py` — stays as generator's default for specialists not yet migrated
- `skills/bmad-create-specialist/` — generator shipped by 2a.1; any bug fix here is a 2a.1 defect story per DR-4 (forward-ratified)
- Primary-repo paths — severance honored

---

## Technical Requirements

### Dependencies

All runtime deps already in lockfile (per 1.1a 10-package palette). No new dep required at 2a.2.

Dev-time: `@pytest.mark.llm_live` marker already registered in `tests/conftest.py` (landed in Commit B SP4).

### Invariants preserved (NFR-X1–X5)

- **NFR-X1** — `IreneEnvelope.model_dump_json() ↔ model_validate_json` round-trip verified in AC-H
- **NFR-X2** — `RunState.graph_version` pins per Slab 1 substrate
- **NFR-X3** — Irene sanctum fingerprint computed per AC-F
- **NFR-X4** — model resolution trail populated per AC-G
- **NFR-X5** — temperature variance documented: `temperature_default: 0.3` (narration creativity) with inline rationale comment in `model_config.yaml`; `temperature: 0.0` for cache-hit-rate test (AC-D) to guarantee deterministic cache key

---

## Testing Requirements

### K-target policy: ~1.4× (floor 8 / target 12)

Per governance JSON `2a-2` inherits header K~1.4×. Realistic breakdown:

- Schema-shape models introduced: `IreneEnvelope`, `IreneReturn` (2 models, inherited from SpecialistEnvelope/Return); K × 2 = ~3 shape-pin tests (AC-H covers 4 per 1.2 precedent)
- Scaffold conformance: 1 test (AC-I)
- Model cascade: 2 tests (AC-C)
- Gate-decision interrupt: 2 tests (AC-E)
- Sanctum cold-read: 1 test (AC-F)
- Resolution trail: 1 test (AC-G)
- Real LLM act-body invocation: 1 `@pytest.mark.llm_live` test (AC-B)
- Cache-hit-rate baseline: 1 `@pytest.mark.llm_live` test (AC-D)
- **Total: ~13 tests.** Floor 8 / target 12 cleared.

### Regression floor

- Pre-2a.2 baseline: 303 passed / 1 skipped / 0 failed (2a.1 BMAD-CLOSE baseline; cache-hit-rate harness = the 1 skipped)
- Target at 2a.2 T8: **≥315 passed** (303 baseline + ~13 new) / 0 skipped (cache-hit-rate harness un-skipped) / 0 failed — when `OPENAI_API_KEY` is set with a real key. With placeholder key: ≥313 passed / 2 skipped (Irene `@llm_live` + cache-hit-rate `@llm_live`) / 0 failed.
- Import-linter: 3/3 KEPT
- Ruff: clean
- Sandbox-AC validator: PASS

### LLM-live test discipline

Tests AC-B + AC-D carry `@pytest.mark.llm_live`. Per conftest fixture (Commit B SP4), these auto-skip when `OPENAI_API_KEY` is unset OR holds the Slab-1 placeholder sentinel `sk-substrate-no-real-key-do-not-invoke`. The dev agent runs these manually with a real key on operator machine + pastes results into Completion Notes per the sandbox-AC split-AC pattern.

**Operator-gated evidence block** (Completion Notes paste template at story close):
```
## AC-2a.2-B/D live-LLM evidence (operator-gated)

Environment: real OPENAI_API_KEY set (redacted)
Model: gpt-5.4 (per model_config.yaml default)
Timestamp: <ISO8601>
Cache-hit-rate on 2nd invocation: <XX%>  ← must be ≥60% per PRD §M1

Test outputs:
<paste `pytest tests/specialists/irene/test_irene_act_node_llm_invocation.py tests/end_to_end/test_cache_hit_rate_baseline.py --run-live -v` tail>
```

---

## Previous Story Intelligence

### From Story 2a.1 (Generator + Scaffold Reference) — 2026-04-24

**Key lesson — generator works but modifies compiler:** 2a.1's review-state surfaced 10 failing Slab-1 tests from overly-strict model-ID validation. The fix (additive-only validator) is a DR-1 application: don't break Slab 1 to improve Slab 2. **2a.2 applies the same discipline:** any compiler / manifest / state-model changes must be strictly additive.

**Key lesson — Option Y fixture discipline:** prefix `fixture_` keeps pytest from auto-collecting test-anchor fixtures. Irene's golden envelope at `tests/fixtures/specialists/irene/golden_*.json` follows this pattern (extensions differ — JSON is fine, not collected by pytest regardless).

**Key lesson — Generator denylist check:** 2a.1 added `GENERATOR_DENYLIST` for audra+cora. Irene is NOT in the denylist; invocation proceeds normally.

### Three drifts from Epic 2a.2 text (captured at T1 per standing protocol)

1. Node names — same as 2a.1's Epic 2a line 555 drift; use `SCAFFOLD_NODE_IDS`
2. Model ID / tier — use `gpt-5.4` + `tier_request: reasoning`; epic's `gpt-4.1` + "long-context balanced" are stale
3. Sanctum path — use `_bmad/memory/bmad-agent-content-creator/`; epic's `bmad-agent-irene/` is stale

### Dev Notes anti-pattern anchor

- **Late-binding default-arg** (Slab-1 gotcha #4): still relevant when authoring Irene's `act` body if any default-arg value references a module-level constant
- **`OPENAI_API_KEY` placeholder sentinel** (Slab-1 gotcha #3): AC-B + AC-D rely on the `@pytest.mark.llm_live` skip-fixture; dev agent verifies conftest fixture fires correctly
- **Passthrough `{}` return shape** (Slab-1 gotcha #6): Irene's real `act` body replaces this; downstream graph code must not assume `{}` anymore post-2a.2 for Irene specifically (other passthrough nodes remain until their 2a/2b migrations)

---

## Git Intelligence

Recent Slab 2 commits for pattern reference:

- `e14616c` — Story 2a.1 flip review → done (status + sprint-status)
- `cc79df5` — Story 2a.1 consolidated dev-story landing (46 files)
- `2a336df` — Story 2a.1 review remediation (compiler validator additive-only per DR-1)
- `2d5142e` — Story 2a.1 round-2 amendments (path + exception + gate-semantics + denylist)
- `aff1119` — Commit B: 9 Slab-2-prereq hardening items (conftest llm_live fixture + gate-decision doc + STUB markers + etc.)
- `f78bd72` — Slab-1 GOLDEN ratification + DR-SLAB-1-CLOSE + Epic 2a KNOWN-DRIFT marker
- `835e650` — Upstream severance

---

## Project Context Reference

### Pre-read memory entries

- [`memory/feedback_verify_via_shipped_deps.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_verify_via_shipped_deps.md) — sandbox-AC rule
- [`memory/project_upstream_severance.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_upstream_severance.md) — severance posture

### Post-story unblocks

- **Story 2a.3** (Kira motion migration) — same generator-emission pattern; `mcp: kling` instead of `none`; `tier_request: multimodal` (needs check against registry + possibly a new multimodal tier entry if registry doesn't support it yet)
- **Story 2a.4** (Texas migration) — preserves retrieval-contract.md verbatim per NFR-I5
- **Cache-hit-rate M1 gap CLOSED** — ACCEPT-WITH-GAP path fulfilled at 2a.2 closure

---

## Dev Agent Record

_(Dev agent populates this section during T1–T9 execution.)_

### T1 Readiness

_(Pre-read confirmations; governance-JSON lookup; sandbox-AC validator; 7-point artifact sweep (A–G); 3 epic-doc-vs-framework drifts logged.)_

### T2–T7 Implementation Notes

_(Generator invocation; `act` body authoring; cache-hit-rate harness retargeting; sanctum cold-read wiring.)_

### T8 Regression Evidence

_(Migration-suite regression count; ruff clean; import-linter 3/3 KEPT; sandbox-AC PASS; scaffold-conformance framework green; cache-hit-rate rate measurement.)_

### G5 Single-Gate Review

_(Single-gate per governance JSON 2a-2.expected_gate_mode = "single-gate". Dev agent self-conducts the layered G6 bmad-code-review; party-mode consult only if Slab-1-invariant breakage surfaces.)_

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

_(Findings triage: APPLY / DEFER / DISMISS per aggressive rubric.)_

### D12 Close Stub

1. **Invariant preservation:** _(FR9–FR16 closure statement + Slab-1 substrate intact.)_
2. **Anti-pattern harvest:** _(up to 3 new entries: node-name drift second example + model-ID drift NEW + sanctum-path drift NEW.)_
3. **Migration-guide update:** _(§12 Specialist Walkthrough upgraded from hypothetical Irene → real Irene.)_

### Completion Notes

- **Cache-hit-rate measurement (operator-gated evidence block):** _(paste live test output here.)_
- **M1 evidence pack update:** _(cache-hit-rate clause CLOSED; paste amended M1 pack §Cache-Hit-Rate line.)_
- **Deferred-inventory update:** _(cache-hit-rate un-skip follow-on REMOVED.)_

---

## Open Questions / Flags for Operator

1. **Does 2a.2 require an operator-gated cache-hit-rate measurement block?** Default: YES per AC-D + Completion Notes paste template. Operator-gated because live LLM invocation requires the operator's `OPENAI_API_KEY`; dev agent cannot self-measure in the sandbox.
2. **If cache-hit-rate measures <60%:** story does NOT close. Per AC-D: party-mode round convenes before retry. Flag to operator if this path fires.
3. **Irene's `act` body complexity:** Pass-2 procedure per [`pass-2-procedure.md`](../../skills/bmad-agent-content-creator/references/pass-2-procedure.md) is substantial; dev agent may surface a scope-slip flag at T4 if the real `act` body exceeds ~150 lines. Split-to-2a.2a considered only if scope-slip is confirmed + party-mode approves.

---

**Status:** ready-for-dev
**Completion note:** Comprehensive spec authored for the first REAL LLM-invoking specialist migration. T1 Readiness explicitly flags three Epic 2a.2 drifts (node names, model ID, sanctum path). Cache-hit-rate harness ACTIVATION lands here per deferred-inventory trigger; M1 ACCEPT-WITH-GAP clause CLOSES at story closure if measurement ≥60%. FR9–FR16 closed for Irene (first per-specialist exercise); FR54 closed at substrate level. Sandbox-AC expected PASS. Follows DR-1 GOLDEN ratification ("spec yields to code on conflict") in every drift-fix direction. Slab 2a momentum: 2a.1 ✅ → 2a.2 opens → 2a.3 (Kira) → 2a.4 (Texas) → Slab 2a close at 2a.4 feeds M2.
