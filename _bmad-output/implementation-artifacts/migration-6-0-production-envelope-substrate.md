# Migration Story 6.0: Production Envelope Substrate — composition contract that admits multi-specialist execution

**Status:** review (implemented 2026-04-27; BMAD code review + operator dual-gate acceptance pending)
**Sprint key:** `migration-6-0-production-envelope-substrate`
**Epic:** Slab 6 — Post-MVP Production Capability (PRECEDES the previously-planned 6.1 production-graph runner; opens with this story).
**Pts:** 8 (~3-5 days; substrate + adapter + envelope + composition fixture + composition-test discipline + A17/P3 governance + Composition Smoke gate operationalization).
**Gate:** dual-gate (rationale: `substrate_shape` + `invariant_preservation` — composition contract is new substrate that downstream Slab 6.1 + 6.2 + ... depend on; preserves specialist isolation invariants from M3 / 5a.4 audit matrix).
**K-target:** ~1.4× (target ~22 / floor ~16; honest K-floor will land per implementation phasing).

**Predecessors:**
- Slab 5a closed as bounded-MVP unconditional SHIP (2026-04-27 ratification).
- Slab 6.1 first-attempt + bmad-code-review + strict-AC HALT (2026-04-27) revealed substrate gap: 14 specialists designed for isolated execution; do not admit composition.
- 5-agent party-mode round 2026-04-27 (Winston + Murat + Amelia + Quinn-R + Mary) ratified Path A-prime (production envelope + adapter + isolated specialists unchanged) + scope-split (Slab 6.0 substrate / Slab 6.1 runner-consumes-substrate) + A17 + P3 anti-pattern entries + Composition Smoke gate amendment.

**Authorship provenance:** authored 2026-04-27 in operator session immediately after 5-agent party-mode ratification. Cite Codex Slab 6.1 strict-AC HALT findings + the 5-agent round verbatim record.

---

## Why this story exists

The M5 SHIP-CONDITIONAL verdict (2026-04-26) and bounded-MVP SHIP reframe (2026-04-27) both implicitly assumed that composing the migrated specialists into a single executing LangGraph was an implementation-distance away. Slab 6.1 first-attempt landed 80% of that work (the composition layer); bmad-code-review caught that the runner composes-without-invoking; operator authorized Option 1 (strict-AC completion); Codex's strict-AC implementation HALTED honestly upon discovering the substrate doesn't actually admit composition.

The substrate gap (per Codex strict-AC halt findings):
1. **Per-specialist gates fire before production-level G1.** Every specialist's 9-node scaffold has its OWN internal `gate_decision` interrupt. The first registry-backed Texas specialist halted the composed graph at its internal gate before the production G1 ever fired.
2. **Two-phase scaffold structure doesn't map to single-node execution.** `make_chat_model(...)` lives in `_plan`; `_act` consumes the resolution trail. Composed execution requires multi-node-per-specialist orchestration the production runner can't naively wrap.
3. **Shared `cache_prefix` carrier is overwritten, not accumulated.** Each specialist overwrites the carrier with specialist-specific JSON. Downstream specialists fail (`CdDirectiveParseError: cd directive cannot be empty`) because upstream output isn't visible in the carrier they expect.

Per A17 (Substrate Designed for Isolation, Composition Assumed) — the contracts themselves don't admit composition. Per A16 (Composition-vs-Component Audit Gap) + P3 (Composition-Shape Vote Without End-to-End Exercise) — this gap could survive multiple multi-agent reviews because no audit step exercised composition end-to-end.

This story closes the substrate gap. It establishes:
- A **production envelope** (NEW state-key alongside `cache_prefix`; canonical accumulator for cross-specialist output)
- A **dispatch adapter** at the runner layer that marshals specialist outputs into the envelope and reads downstream specialist inputs from the envelope
- A **composition fixture** (`ComposedSpecialistChainHarness`) that exercises ≥2 real specialists end-to-end through the production dispatch path
- The **composition-test discipline** (`tests/composition/` tree; every-new-specialist-PR-must-add-to-chain-test rule)
- The **Composition Smoke gate** added to the slab-opener template (governance amendment per Quinn-R Q3)

Slab 6.1 then becomes "runner consumes substrate" — straightforward composition of the envelope + adapter + FR34 gate machinery into a working production runner. With this substrate in place, Slab 6.1 should land in 1-2 days; without it, Slab 6.1 has been blocked by an A17 substrate gap.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Substrate-aware adaptation is the discipline; halt-and-surface is the right move when substrate disagrees with spec. A17 is the latest such finding; Slab 6.0 is the substrate-aware adaptation that closes it.

---

## T1 Readiness Block

1. **Governance:** dual-gate per `substrate_shape` (production envelope contract is new substrate that downstream 6.1+ depend on) + `invariant_preservation` (specialists keep their existing isolated-execution contract; M3 / 5a.4 invariants preserved). Add to `docs/dev-guide/migration-story-governance.json` as Slab 6 substrate opener (precedes 6.1).

2. **Substrate inheritance (BINDING):**
   - `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` — Slab 6.1 spec; will be RE-SCOPED to "runner consumes substrate" in lockstep with this Slab 6.0 filing.
   - `docs/dev-guide/specialist-anti-patterns.md` A17 entry — substrate gap this story closes; A17 counter-pattern is what this story implements at the substrate level.
   - `docs/dev-guide/specialist-anti-patterns.md` P3 entry — process anti-pattern; this story's "Composition Smoke" gate operationalizes P3's counter-discipline.
   - `_bmad-output/implementation-artifacts/m5-decision.md` Verdict-Integrity Annotation — records the unexercised-composition gap finding for audit-trail honesty.
   - Codex Slab 6.1 strict-AC HALT finding (operator-session record) — primary substrate evidence for the 3 specific gaps named above.

3. **Reusable substrate (existing pieces this story PRESERVES; do NOT mutate):**
   - 14 × `app/specialists/<name>/graph.py` — specialists STAY scaffold-conformant for isolated execution (M3 harness path remains valid). NO modifications to specialist scaffold or `_plan`/`_act` shape.
   - `app/models/state/run_state.py::RunState` — extend with NEW envelope state-key alongside existing `cache_state.cache_prefix` (do NOT replace cache_prefix; per Winston A-prime variant).
   - `app/manifest/compiler.py` — preserved-state from Codex's `c7d6447` commit; production envelope work happens at the runner layer, not in compiler.
   - `app/gates/resume_api.py` — FR34 gate machinery; production gate G1/G2C/G3/G4 path stays intact.
   - `app/runtime/economics.py` — cost reporting; envelope additions are backward-compatible with cost machinery.
   - Codex's preserved-state commits `c7d6447` + `7421f66` — build on top.

4. **NOT-existing substrate (the gap this story closes):**
   - **Production envelope state-key.** No canonical cross-specialist accumulator exists. `cache_state.cache_prefix` is per-specialist scratch.
   - **Dispatch adapter at runner layer.** Composition currently bypasses LangGraph composition or wraps M3 harness; no adapter marshals specialist outputs into envelope.
   - **Composition fixture.** No `ComposedSpecialistChainHarness` exists; no integration test exercises ≥2 real specialists end-to-end.
   - **Composition-test discipline.** No `tests/composition/` tree; no rule that every new specialist PR adds a chain-test entry.
   - **Composition Smoke gate** in slab-opener template. Template currently doesn't require composition-exercise AC at vote time.

5. **Severance posture:** primary repo at `upstream/master @ 3ed7c56` remains frozen reference; FR60 backport stays closed.

## Anti-Pattern Mitigation Trace

Slab 6.0 explicitly reads the post-M5 anti-pattern set before substrate close:

- **A15 — Plausible-Token Substrate Contamination:** no new external-provider model IDs or auth/resource identifiers are introduced by this story; existing OpenAI catalog tests remain outside the Slab 6.0 substrate surface.
- **A16 — Composition-vs-Component Audit Gap:** AC-C adds the Texas -> cd composition chain under `tests/composition/`; the test asserts envelope state-flow and contribution accumulation rather than output equality alone.
- **A17 — Substrate Designed for Isolation, Composition Assumed:** Path A-prime adds a production envelope alongside `cache_state.cache_prefix` and keeps specialist code unchanged; AC-E preserves isolated execution.
- **P3 — Composition-Shape Vote Without End-to-End Exercise:** AC-D amends the create-story template with a required Composition Smoke step and failing-smoke disposition rules.
- **N1-N12 substrate checklist:** Acceptance Auditor must trace all twelve N-items in the Slab 6.0 bmad-code-review artifact before `review -> done`.

---

## TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1; honors A17 + P3 counter-patterns):** This story builds the substrate ONLY:
- Production envelope state-key (NEW alongside `cache_prefix`)
- Dispatch adapter at runner layer (marshals specialist output → envelope; reads downstream input from envelope)
- ONE specialist pair proves the channel end-to-end (suggested: Texas → cd, since the strict-AC HALT showed exactly this pair failing)
- Composition fixture + `tests/composition/` tree + chain-test discipline
- Composition Smoke gate operationalized in slab-opener template

NOT in scope:
- The production runner itself (stays Slab 6.1 work; consumes this substrate)
- Specialist contract changes (per Path A-prime; specialists unchanged)
- Live-OpenAI smoke (Slab 6.1's responsibility; substrate test uses synthetic specialist outputs)
- HIL gate pause/resume (Slab 6.1's responsibility; this substrate just preserves the gate machinery surface)

**Decision #2 — A-prime variant (Winston):** envelope state-key lives ALONGSIDE `cache_prefix`, not replacing or wrapping it. Specialists keep their existing contract (per-specialist scratch in `cache_prefix`); production composition reads from / writes to envelope. Eliminates "is this an adapter bug or a scaffold bug" ambiguity by separating per-specialist scratch from cross-specialist accumulator. Operator-ratified 2026-04-27.

**Decision #3 — Production envelope schema (Pydantic v2 strict; four-file-lockstep per checklist):**

```python
# app/models/runtime/production_envelope.py
class ProductionEnvelope(BaseModel):
    """Canonical cross-specialist accumulator for production composition.

    Distinct from `RunState.cache_state.cache_prefix` (per-specialist scratch).
    Each specialist's output appears as a SpecialistContribution entry; downstream
    specialists read inputs by querying contributions by upstream-specialist-id.
    Envelope is append-only within a trial; specialists can only ADD their own
    contribution, never modify upstream contributions (immutability invariant).
    """
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    schema_version: Literal["production-envelope.v1"] = "production-envelope.v1"
    trial_id: UUID
    contributions: list[SpecialistContribution] = Field(default_factory=list)

    def get_contribution(self, specialist_id: str) -> SpecialistContribution | None:
        """Lookup an upstream specialist's contribution by id; None if absent."""
        ...

    def add_contribution(self, contribution: SpecialistContribution) -> None:
        """Append a specialist's contribution. Raises if specialist_id already present
        (immutability — each specialist contributes exactly once per trial)."""
        ...

class SpecialistContribution(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True, frozen=True)
    specialist_id: str = Field(..., min_length=1)
    contributed_at: datetime  # tz-aware enforced
    output: dict[str, Any]  # specialist-specific output; downstream specialists know their own input shape
    cost_usd: float = Field(..., ge=0.0)
    model_used: str = Field(..., min_length=1)
    output_digest: str  # SHA256 of output for replay-regression
```

Four-file-lockstep:
- Model: `app/models/runtime/production_envelope.py`
- JSON Schema: `schema/production_envelope.v1.schema.json`
- Shape-pin tests: `tests/unit/runtime/test_production_envelope_strict.py`
- Golden fixture: `tests/fixtures/runtime/production_envelope_golden.json`

**Decision #4 — Dispatch adapter contract (the runner-layer translation):**

```python
# app/marcus/orchestrator/dispatch_adapter.py
class ProductionDispatchAdapter:
    """Translates between production envelope and per-specialist scaffold contracts.

    For each specialist invocation in the composed production graph:
      1. INPUT: build the specialist's expected RunState by reading prior contributions
         from envelope (per-specialist input mapping; each specialist declares its
         dependencies via dependency_map).
      2. INVOKE: call the specialist's compiled subgraph with constructed RunState.
      3. OUTPUT: extract the specialist's output from RunState.cache_state and
         add as a contribution to the envelope.

    The adapter is the ONLY surface that knows about envelope-vs-cache_prefix shape
    differences. Specialists are unchanged; the envelope is unchanged; the adapter
    bridges. Per Path A-prime + Mary harvest-gate distinction (A17 counter-pattern).
    """
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],  # downstream-input-key → upstream-specialist-id
    ) -> ProductionEnvelope:
        """Returns updated envelope with new contribution appended."""
        ...
```

**Decision #5 — Composition fixture + tests/composition/ tree (Murat M2):**

NEW directory: `tests/composition/`. Contains:
- `composed_specialist_chain_harness.py` — `ComposedSpecialistChainHarness` fixture that orchestrates ≥2 real specialists through `ProductionDispatchAdapter`; asserts envelope-state propagation (not just output equality); pins envelope contribution accumulation.
- `test_texas_to_cd_chain.py` — exercises Texas → cd chain end-to-end (proves the strict-AC HALT scenario now succeeds); uses synthetic specialist outputs at the LLM-call boundary so cost stays trivial (~$0).
- `__init__.py` — empty.
- Future per-chain tests added by every new specialist PR per the chain-test discipline rule.

**Decision #6 — Composition Smoke gate operationalization (Quinn-R Q3):**

Operationalize as a governance amendment to the slab-opener template. Concretely:
- Add a "Composition Smoke" required step to the bmad-create-story workflow's slab-opener template.
- The smoke is a 30-line throwaway script that wires the slab's primary components together end-to-end.
- The smoke's PASS-or-FAIL becomes vote-evidence-base for the slab opener; if the smoke fails, the vote either RE-SCOPES (bounded-MVP scope excluding composition claim) or DEFERS (until substrate exists) or GREENs explicitly as a composition-shape vote with the substrate gap named.
- Failing smoke is not a slab-blocker; it's a vote-evidence requirement.
- For Slab 6.0 itself: the composition fixture (Texas → cd chain test) IS the Composition Smoke for this slab. Pass = ratification evidence.

---

## Story

As an **operator preparing the migration's production-graph runner per Slab 6.1 + A17 substrate-aware adaptation**,
I want **a production envelope state-key + dispatch adapter at the runner layer + ≥1 composition fixture proving end-to-end specialist chain works + composition-test discipline + Composition Smoke gate amendment to slab-opener template**,
So that **the substrate admits composition (closing the A17 gap), Slab 6.1 can land cleanly without re-discovering substrate problems, and future M-gate audits gain composition-exercise discipline (closing the P3 process gap)**.

---

## Acceptance Criteria

### AC-6.0-A — `ProductionEnvelope` Pydantic v2 strict (four-file-lockstep per checklist)

- **Given** Decision #3 schema family
- **When** dev authors model + JSON Schema + shape-pin tests + golden fixture
- **Then** four-file-lockstep present; tz-aware datetime enforced on `contributed_at`; cost fields ≥0; closed-set `Literal` red-rejection on schema_version; immutability enforced (`add_contribution` raises if specialist_id already present).
- **Test pin:** `tests/unit/runtime/test_production_envelope_strict.py` — 5 tests: strict_config + tz-aware + cost-non-neg + version-literal + immutability.

### AC-6.0-B — `ProductionDispatchAdapter` core invocation contract

- **Given** Decision #4 contract
- **When** dev authors `app/marcus/orchestrator/dispatch_adapter.py::ProductionDispatchAdapter.invoke_specialist(...)`
- **Then** the adapter (a) reads dependency-map → envelope-contributions to construct specialist input RunState; (b) invokes the specialist's compiled subgraph; (c) extracts specialist output from RunState; (d) returns updated envelope with new contribution appended.
- **Test pin:** `tests/integration/marcus/test_dispatch_adapter.py` — 3 tests: input-construction + specialist-invocation (mocked subgraph) + output-extraction-to-envelope.

### AC-6.0-C — `tests/composition/` tree + chain-test discipline (Murat M2)

- **Given** the composition-test discipline established by 5-agent party-mode 2026-04-27
- **When** dev creates `tests/composition/` tree + `ComposedSpecialistChainHarness` fixture + first chain test
- **Then** directory exists with `__init__.py` + harness + ≥1 chain test; chain test exercises ≥2 real specialists end-to-end through `ProductionDispatchAdapter`; asserts envelope-state propagation (NOT just output equality); pins envelope contribution accumulation.
- **Test pin:** `tests/composition/test_texas_to_cd_chain.py` — 1 parametrized test exercising Texas → cd chain (the same pair that failed in Codex's strict-AC HALT); uses synthetic specialist outputs at the LLM-call boundary; asserts post-chain envelope contains both Texas + cd contributions in order; asserts cd's input was constructed from Texas's contribution (proves dependency-map worked).

### AC-6.0-D — Composition Smoke gate amendment (Quinn-R Q3 + P3 counter-pattern)

- **Given** P3 process anti-pattern + Quinn-R "Composition Smoke" recommendation
- **When** dev amends the bmad-create-story slab-opener template to include a "Composition Smoke" required step
- **Then** the template includes (a) explicit Composition Smoke step at slab-opener authoring time; (b) PASS-or-FAIL records as vote-evidence; (c) the failing-smoke disposition rules (re-scope OR defer OR explicit-composition-shape-vote with named gap).
- **Test pin:** `tests/migration/test_composition_smoke_template_present.py` — 1 test asserting slab-opener template contains "Composition Smoke" step + the disposition-rule wording.

### AC-6.0-E — Specialist isolation invariant preserved (per A17 counter-pattern)

- **Given** specialists STAY scaffold-conformant for isolated execution per Path A-prime
- **When** dev verifies that no specialist's contract was modified by Slab 6.0 work
- **Then** all 14 specialists' isolated-execution tests (`tests/specialists/<name>/test_*.py`) remain GREEN; M3 deterministic harness at `marcus/orchestrator/m3_trial.py` remains UNCHANGED + functional; replay-regression suite (5a.1) remains GREEN.
- **Test pin:** `tests/composition/test_specialist_isolation_preserved.py` — 1 parametrized test (1 per specialist; ~14 cases collapsed) asserting per-specialist isolated-execution path still works post-6.0.

### AC-6.0-F — A17 + P3 anti-pattern entries filed (governance evidence)

- **Given** A17 + P3 entries authored by operator session 2026-04-27
- **When** dev verifies the entries are in place per Mary harvest-gate authority
- **Then** `docs/dev-guide/specialist-anti-patterns.md` contains A17 + P3 entries under the appropriate subheadings (A17 under "Post-Cycle Harvest"; P3 under NEW "Process Anti-Patterns" subheading); format-freeze v1 preserved (A1-A16 entries unchanged).
- **Test pin:** `tests/migration/test_a17_p3_entries_present.py` — 1 test asserting both entries present + four-field-format honored.

### AC-6.0-G — Anti-pattern catalog harvest (no NEW entries expected)

A17 + P3 are the precipitating entries for this story; no further new entries expected. If the substrate work surfaces a NEW pattern (e.g., "envelope shape too restrictive for X case"), file as harvest candidate per Mary harvest-gate.

### AC-6.0-H — TEMPLATE compliance

R1, R6, R8 honored. Slab 6 substrate-opener — establishes the post-MVP TEMPLATE precedent for stories that lay substrate before consuming runners.

### AC-6.0-I — D12 close protocol (DUAL-gate; FIVE-line per dual-gate convention)

1. **Invariant preservation:** specialist isolated-execution invariants from M3 / 5a.4 audit matrix preserved (per AC-E). FR34 HIL machinery preserved (envelope is orthogonal to gate machinery). FR43 frozen-graph respected (envelope work is runner-layer; doesn't modify frozen graph artifacts).
2. **Anti-pattern harvest:** A17 + P3 filed (per AC-F); no new entries expected mid-story.
3. **Migration-guide update:** §"Production Envelope Substrate" added — envelope schema + adapter contract + composition-test discipline + Composition Smoke gate operationalization.
4. **TEMPLATE compliance:** R1, R6, R8.
5. **Dual-gate gate-2 (operator acceptance gate):** operator runs `pytest tests/composition/ -q --tb=short` + reads the chain test output + ratifies that the Composition Smoke gate amendment is correctly operationalized.

### AC-6.0-J — Sprint-status state-flips at filing AND close

At filing: `migration-6-0-production-envelope-substrate: ready-for-dev` (NEW). At close: `migration-6-0-production-envelope-substrate: done`. M5 condition #3 in `_bmad-output/upstream-state.md` UPDATED to point at Slab 6.0 + 6.1 sequence (was: "REFRAMED-AS-SLAB-6-OPENER"; becomes: "REFRAMED-AS-SLAB-6.0-SUBSTRATE-+-SLAB-6.1-RUNNER per 5-agent party-mode 2026-04-27"). `migration-epic-6-post-mvp-production` epic stays `in-progress` (multiple stories pending).

---

## File Structure Requirements

### NEW files

- `app/models/runtime/production_envelope.py` — Pydantic v2 `ProductionEnvelope` + `SpecialistContribution`
- `schema/production_envelope.v1.schema.json` — emitted JSON Schema
- `app/marcus/orchestrator/dispatch_adapter.py` — `ProductionDispatchAdapter`
- `tests/unit/runtime/test_production_envelope_strict.py` (AC-A)
- `tests/integration/marcus/test_dispatch_adapter.py` (AC-B)
- `tests/composition/__init__.py`
- `tests/composition/composed_specialist_chain_harness.py` — fixture
- `tests/composition/test_texas_to_cd_chain.py` (AC-C; the strict-AC HALT scenario succeeds here)
- `tests/composition/test_specialist_isolation_preserved.py` (AC-E)
- `tests/migration/test_composition_smoke_template_present.py` (AC-D)
- `tests/migration/test_a17_p3_entries_present.py` (AC-F)
- `tests/fixtures/runtime/production_envelope_golden.json` (AC-A)

### MODIFIED files

- `app/models/state/run_state.py` — extend `RunState` with NEW envelope state-key alongside `cache_state` (NOT replacing); per Decision #2 A-prime variant.
- `docs/dev-guide/migration-story-governance.json` — Slab 6.0 entry + Slab 6.1 re-scope note + version bump.
- `docs/dev-guide/specialist-anti-patterns.md` — A17 + P3 entries (if not yet filed by operator session work; verify state at T1).
- `docs/dev-guide/langgraph-migration-guide.md` — §"Production Envelope Substrate" added per D12.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-J.
- `_bmad-output/upstream-state.md` — per AC-J.
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` — re-scope to "runner consumes substrate" + cross-link to this Slab 6.0.
- `skills/bmad-create-story/templates/slab-opener-template.md` (or equivalent) — Composition Smoke gate amendment per AC-D + Decision #6.

### DO NOT MODIFY (per Path A-prime + AC-E specialist isolation invariant)

- 14 × `app/specialists/<name>/graph.py` — specialists STAY scaffold-conformant for isolated execution
- `marcus/orchestrator/m3_trial.py` — deterministic harness preserved
- `app/manifest/compiler.py` — Codex preserved-state from `c7d6447`; envelope work is runner-layer
- `app/gates/resume_api.py` — FR34 gate machinery preserved
- All `tests/specialists/<name>/test_*.py` — isolated-execution tests must remain GREEN

---

## Testing Requirements

**K-target ~1.4× (target ~22 / floor ~16).**

K-floor calculation:
- AC-A: 5 (strict_config + tz-aware + cost-non-neg + version-literal + immutability)
- AC-B: 3 (input-construction + specialist-invocation + output-extraction)
- AC-C: 1 parametrized (Texas → cd chain; the load-bearing test)
- AC-D: 1 (template-present)
- AC-E: 1 parametrized (~14 cases; collapsed to 1 K-floor unit per Murat M-R18 same-property collapse)
- AC-F: 1 (A17+P3 entries-present)

= **12 K-floor**. RIDER: AC-B add edge cases (specialist-not-in-dependency-map; envelope-immutability-violation; output-not-found-in-state) → +3; AC-C add second chain (Texas → vera, proves adapter generality) → +1 = **honest 16 K-floor (meets floor)**.

Sandbox-AC PASS expected (uses shipped Pydantic v2 + composition tests use synthetic fixtures, no live API).

---

## Effort estimate

**~3-5 days focused Codex time** (per Winston W2 + Amelia A2). Phasing recommendation:
- Day 1: ProductionEnvelope schema (AC-A) + four-file-lockstep + ProductionDispatchAdapter scaffold (AC-B)
- Day 2: Composition fixture + Texas → cd chain test (AC-C; the load-bearing test) + specialist isolation preservation test (AC-E)
- Day 3: Composition Smoke gate template amendment (AC-D) + A17+P3 entries-present test (AC-F) + RunState extension
- Day 4-5: Integration verification + buffer for halt-and-adapt cycles + docs update + close artifacts

Halt-and-adapt budget built in: any phase that hits substrate disagreement HALTS and surfaces (3.1 + 5a.3 + A15 + A16 + A17 + Slab 6.1 strict-AC precedent). Total wall-clock with halt-allowance: 3-5 days; expect at least one halt-and-ratify cycle (probably around the Texas → cd chain test surfacing a real specialist contract that needs careful adapter handling).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness + substrate verification

_(Verify Codex Slab 6.1 strict-AC HALT findings against live tree state at dev start; confirm A17 + P3 entries are in place; confirm specialist isolation invariants intact.)_

### Implementation summary

Implemented Path A-prime substrate:
- `ProductionEnvelope` + `SpecialistContribution` strict Pydantic v2 model family with JSON Schema and golden fixture.
- `RunState.production_envelope` added alongside `cache_state`.
- `ProductionDispatchAdapter` added at runner layer; it marshals envelope contributions into per-specialist `cache_state.cache_prefix`, invokes the compiled specialist graph through the scaffold boundary, records per-specialist gate interrupts, and appends output back into the envelope.
- `tests/composition/` added with `ComposedSpecialistChainHarness`, Texas -> cd composition smoke, and specialist isolation-preservation scaffold build test.
- Composition Smoke step added to the create-story template; A17/P3 presence test added.

### Composition fixture evidence (AC-C)

_(Cite the Texas → cd chain test output. Include envelope-state-after-chain-execution as evidence that the adapter marshals correctly.)_

### Verification

Passed:
- `pytest tests/composition/ -q --tb=short` -> 17 passed
- `pytest tests/unit/runtime/test_production_envelope_strict.py tests/integration/marcus/test_dispatch_adapter.py tests/composition/ tests/migration/test_composition_smoke_template_present.py tests/migration/test_a17_p3_entries_present.py -q --tb=short` -> 35 passed
- `pytest tests/unit/models/state/test_run_state.py tests/unit/models/state/test_schema_pin.py tests/unit/models/state/test_reproducibility_invariants.py tests/unit/state/test_run_state_model_overrides_field.py -q --tb=short` -> 55 passed
- focused isolation slice (`tests/composition/test_specialist_isolation_preserved.py` + per-specialist `test_*_state_shape.py`) -> 78 passed
- `pytest tests/test_no_fictitious_model_ids.py tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py -q --tb=short` -> 2 passed
- `ruff check app/models/runtime app/marcus/orchestrator tests/unit/runtime tests/integration/marcus tests/composition tests/migration` -> clean
- `lint-imports --config pyproject.toml` -> 9 kept, 0 broken
- `python scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-6-0-production-envelope-substrate.md` -> PASS

Not completed locally: full `pytest tests/specialists/ -q --tb=short` timed out at both 2 minutes and 5 minutes on this Windows environment; the focused isolation-preservation slice passed.

### Operator dual-gate gate-2 evidence (AC-I item 5)

- **Date:** 2026-04-27
- **Command:** `.venv\Scripts\python.exe -m pytest tests/composition/ -q --tb=short`
- **Result:** `17 passed in 1.21s`
- **Operator witness:** Juan Leon (operator session)
- **Disposition:** PASS — substrate-shape gate cleared; operator ratifies the Composition Smoke gate amendment is correctly operationalized and the Texas → cd chain test (the load-bearing test that mirrors the Slab 6.1 strict-AC HALT scenario) passes end-to-end through the `ProductionDispatchAdapter`. Gate-2 satisfied. Formal `review → done` flip pending bmad-code-review triage per CLAUDE.md §3.
