# Migration Story 3.5: Runtime Model-Override + Cache-Invalidation Warning (FR24 closure)

**Status:** ready-for-dev
**Sprint key:** `migration-3-5-runtime-model-override-and-cache-warning`
**Epic:** Slab 3 (migration Epic 3 — Marcus Orchestration; M3 go/no-go gate).
**Pts:** 3 | **Gate:** single (per governance JSON `3-5.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.4× (target 12 / floor 9; submit_override + compute_cache_impact + OverrideWarning + RunState.model_overrides + DecisionCardMeta cache_state delta + ledger event emission).

**Predecessor:** Stories 3.1 + 3.2 + 3.3 + 3.4 must be `done`. 3.5 builds on 3.4's transport surfaces (override submission via any of 3 transports) + 3.2's DecisionCardMeta cache_state field + 3.3's OperatorVerdict pattern (override is operator-confirmed action with `confirm_token`).

**Lean party-mode amendments applied 2026-04-26 (Murat + Amelia):** 1 BLOCKER + 4 RIDERs integrated:
- **A-BLOCKER-3.5-A (RunState extension safety):** T1 sub-task — verify current `app/state/run_state.py` shape; if RunState is `frozen=True` Pydantic, the field extension is a schema bump requiring (a) `model_overrides: dict[str, str] = Field(default_factory=dict)` field default for backward-compat, (b) backward-compat verification for resumed runs serialized pre-3.5 (test serializing pre-3.5 RunState fixture + assert post-3.5 model parses cleanly with empty `model_overrides`).
- **A-R1-3.5 (OverrideWarning naming collision):** Rename to `ModelOverrideWarning` to avoid collision with stdlib-adjacent `Warning` subclass naming (G6-flaggable cosmetic).
- **A-R2-3.5 (Phase-1 idempotency):** `submit_override` MUST be idempotent on operator re-submission; idempotency key = `(trial_id, node_id, new_model)` tuple OR explicit operator-supplied `idempotency_token`. Add `test_submit_override_idempotent_under_resubmission` (same tuple → same `confirm_token` returned, NOT new one).
- **M-R1-3.5 (token-replay vs token-mismatch separate tests):** AC-C splits `test_apply_override_stale_token_rejected` into 2 ORTHOGONAL tests (NOT collapsed to 1): `test_apply_override_token_replay_rejected` (consumed token re-used) + `test_apply_override_token_mismatch_rejected` (wrong-trial token).
- **M-R2-3.5 (caplog not stdout-sniff):** Cache-warning emission tests use `caplog` fixture / structured-log capture, NOT stdout sniffing (flakes on pytest capture mode changes).

---

## T1 Readiness Block

### Standing Pre-Flight items

1. **Governance lookup** — `3-5.expected_gate_mode = "single-gate"` (rationale: null).
2. **3.2 DecisionCardMeta** — `cache_state: Literal["healthy", "mixed", "cold"]` + `affected_nodes: list[str]` + `override_trail: list[OverrideEvent]` per D2.
3. **3.3 OperatorVerdict pattern** — `confirm_token` mechanism for operator-confirmed actions (override is analogous: warn + confirm + apply).
4. **3.4 transport surfaces** — `submit_override(trial_id, node_id, new_model)` callable via MCP + FastAPI + CLI per transport-parity discipline (3.5 extends transports with override surfaces).
5. **Slab 1 model cascade** — `app/runtime/model_cascade.py` (or equivalent per Slab 1 substrate); cache prefix shape per FR24.
6. **OverrideEvent model** per 3.2 AC-D — used here as the `override_trail` entry shape.
7. **RunState** — `app/state/run_state.py`; this story extends with `model_overrides: dict[str, str]` field (`node_id -> model_name` mapping); preserves existing fields.
8. **Cache state computation** — verify Slab-1 cache-state inference path; if absent, `compute_cache_impact()` is NEW.
9. **Architecture D2** — pre-submission + post-application dual warning per FR24 verbatim.
10. **Severance posture** — hybrid working tree.

### Slab 3.5 artifact-existence sweep (5-point)

- **A** `app/runtime/` exists per Slab-1; cache infrastructure path verified at T1.
- **B** `app/state/run_state.py` exists; this story extends with `model_overrides` field (additive minimal; verify Slab-1 RunState shape allows extension without breaking existing serialization).
- **C** Transport surfaces from 3.4 ready to extend (override surfaces share transport patterns with verdict surfaces).
- **D** Ledger emission infrastructure carries `kind="override"` event shape (Slab-4 owns ledger schema; 3.5 emits proto-events).
- **E** `OverrideEvent` model from 3.2 AC-D present (NEW or reused-from-Slab-1).

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

NONE expected at this story (FR24 closure is well-specified in epic 3.5 + D2).

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope:** scope is (a) `app/runtime/override_api.py::submit_override(trial_id, node_id, new_model) -> OverrideWarning`; (b) `compute_cache_impact()` — estimates cost impact + affected nodes + cache-state delta; (c) `OverrideWarning` Pydantic v2 strict model; (d) `confirm_token` mechanism + `apply_override(verdict, confirm_token)`; (e) `RunState.model_overrides` extension (additive; minimal); (f) `CacheState` updated post-apply; (g) ledger event emission (`kind="override"`); (h) DecisionCardMeta cache_state populated to reflect "mixed" if any overrides in flight; (i) override-submission surfaces on 3 transports per 3.4 transport-parity discipline. NOT in scope: model cascade itself (Slab 1 substrate); ledger schema (Slab 4); E2E trial (3.6).

**Decision #2 — Two-phase submit/confirm pattern (FR24 dual warning):** override is two-phase per D2:
1. **Phase 1 — submit_override:** computes `OverrideWarning(estimated_cost_delta, affected_nodes, cache_state_delta, confirm_token)`; returns warning to operator; does NOT mutate state. `confirm_token` is a sha256 of `(trial_id, node_id, new_model, current_cache_state, timestamp)` — proves the operator saw THIS specific impact when confirming.
2. **Phase 2 — apply_override:** operator submits `(verdict, confirm_token)` via any transport; check `confirm_token` matches a recently-issued one (within 5 min); if match: apply override + update RunState + emit ledger event; if mismatch: raise `OverrideTokenStaleError` + refuse.

**Decision #3 — DecisionCardMeta cache_state computation:** per emitted card, walk the graph for overrides in flight: if ZERO overrides → `"healthy"`; if any node overridden mid-trial → `"mixed"`; if cache prefix invalidated entirely (e.g., cold-start) → `"cold"`. `affected_nodes` enumerates the specific node IDs.

---

## Story

As an **operator choosing to override a specialist's model mid-trial per FR24**,
I want **a submission surface that warns me of cache-invalidation impact BEFORE I confirm the override + a running cache-state surface in every DecisionCard**,
So that **FR24 is met verbatim, D2 pre-submission + post-application dual warning is operator-visible, and override application is tamper-evident via confirm_token mechanism analogous to OperatorVerdict's decision_card_digest**.

---

## Acceptance Criteria

### AC-3.5-A — `OverrideWarning` Pydantic v2 strict model + four-file-lockstep

- **Given** no `app/runtime/override_warning.py` exists
- **When** the dev agent authors `OverrideWarning`:
  - `model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)`
  - Fields: `warning_id: UUID4`, `trial_id: UUID4`, `node_id: str`, `requested_model: str`, `current_model: str`, `estimated_cost_delta_usd: float = Field(ge=0)`, `affected_nodes: list[str]`, `cache_state_delta: dict[str, Literal["healthy", "mixed", "cold"]]` (before/after), `confirm_token: str` (sha256-hex), `issued_at: datetime` (tz-aware), `expires_at: datetime` (issued_at + 5 min)
- **Then** four-file-lockstep present (model + JSON Schema + shape-pin test + golden fixture)
- **Test pin:** `tests/unit/runtime/test_override_warning_strict.py` — 3 tests (strict_config + tz-aware + cost-delta-non-negative).

### AC-3.5-B — `submit_override()` Phase-1 implementation

- **Given** `OverrideWarning` shipped at AC-A
- **When** the dev agent authors `app/runtime/override_api.py::submit_override(trial_id, node_id, new_model) -> OverrideWarning`:
  1. Read current `RunState` for trial
  2. Call `compute_cache_impact(trial_id, node_id, new_model)` → returns dict `{estimated_cost_delta_usd, affected_nodes, cache_state_delta}`
  3. Compute `confirm_token = sha256(f"{trial_id}|{node_id}|{new_model}|{current_cache_state}|{timestamp}")`
  4. Construct + return `OverrideWarning`; STORE the token in a per-trial pending-tokens TTL cache (5-min expiry)
- **Then** `submit_override` does NOT mutate `RunState.model_overrides` (Phase 1 is read-only)
- **Test pins:**
  1. `tests/unit/runtime/test_submit_override_returns_warning.py` — 1 test: invoke + assert returned `OverrideWarning` carries non-null fields + token format.
  2. `tests/unit/runtime/test_submit_override_no_state_mutation.py` — 1 test: capture `RunState` before; invoke `submit_override`; assert post-state byte-equal pre-state.

### AC-3.5-C — `apply_override()` Phase-2 implementation + confirm_token enforcement

- **Given** Phase 1 issued a token
- **When** the dev agent authors `apply_override(verdict, confirm_token) -> None`:
  1. Verify `confirm_token` matches a pending token for this trial+node within 5 min
  2. On match: `RunState.model_overrides[node_id] = new_model`; `CacheState` updated; ledger event emitted (`kind="override"`); pending token consumed (deleted from TTL cache)
  3. On mismatch or expiry: raise `OverrideTokenStaleError` + refuse
- **Test pins:**
  1. `tests/integration/runtime/test_apply_override_match_path.py` — 1 test: full submit → apply round-trip; assert `RunState.model_overrides` populated + ledger event emitted.
  2. `tests/integration/runtime/test_apply_override_stale_token_rejected.py` — 2 tests: (a) wrong token → `OverrideTokenStaleError`; (b) expired token (mock time +6 min) → `OverrideTokenStaleError`.

### AC-3.5-D — `compute_cache_impact()` implementation

- **Given** a model override request for `(trial_id, node_id, new_model)`
- **When** the dev agent authors `compute_cache_impact()`:
  1. Walk graph for downstream nodes that reuse the cache prefix; mark as `affected_nodes`
  2. Compute current per-node cache state from `RunState.cache_state` substrate
  3. Estimate cost delta: `(new_model_cost_per_token - current_model_cost_per_token) * estimated_tokens_remaining`
  4. Compute `cache_state_delta`: `{"before": current_state, "after": projected_state_post_override}`
- **Test pin:** `tests/unit/runtime/test_compute_cache_impact.py` — 2 tests (parametrize-collapsible per M-R18 → 1 K-floor; same property over fixture variants):
  - 3 fixture trials: (a) override on leaf node (affected_nodes = [node_id] only); (b) override on mid-graph node (affected_nodes includes downstream); (c) override on root node (affected_nodes = all downstream).

### AC-3.5-E — DecisionCardMeta cache_state populated per Decision #3

- **Given** `DecisionCardMeta.cache_state` per 3.2 surface
- **When** next gate fires after an override has been applied
- **Then** `meta.cache_state` reflects current state: `"mixed"` if any overrides in flight; `"healthy"` if all nodes on default cascade; `"cold"` if cache prefix invalidated entirely
- **Test pin:** `tests/integration/runtime/test_decision_card_cache_state_post_override.py` — 3 tests: (a) no override → `"healthy"`; (b) one override applied → `"mixed"`; (c) cold-start (no cache prefix) → `"cold"`.

### AC-3.5-F — RunState.model_overrides field extension (additive minimal)

- **Given** `app/state/run_state.py` per Slab-1 substrate
- **When** the dev agent extends RunState with `model_overrides: dict[str, str] = Field(default_factory=dict)` (`node_id -> model_name`)
- **Then** existing RunState fields preserved; serialization round-trips; existing tests pass post-extension
- **Test pin:** `tests/unit/state/test_run_state_model_overrides_field.py` — 2 tests: (a) field present + default-empty-dict; (b) round-trip with overrides populated.

### AC-3.5-G — M3 evidence bullet

- **Given** M3 Required Evidence per architecture D3 + epic 3.5 AC: trial run closes + runtime model-override surface is functional AND warns of cache-invalidation impact
- **When** Slab 3 close (3.6) trial run exercises the override surface
- **Then** M3 evidence bullet validated: at least one override exercised + warning shown + confirm_token round-trip + post-application cache_state surfaces "mixed" in subsequent DecisionCard
- **Test pin:** N/A at 3.5 (evidence gathered at 3.6 trial run); 3.5 ships the substrate + tests + transport surfaces.

### AC-3.5-H — Anti-pattern catalog harvest (per R6)

NO new entries expected.

### AC-3.5-I — TEMPLATE compliance (per R1–R14 v2.4)

R1, R6, R8 honored.

### AC-3.5-J — D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** FR24 verbatim (pre-submission + post-application dual warning); D2 cache-state surface; tamper-evidence via confirm_token analog of decision_card_digest.
2. **Anti-pattern harvest:** N/A.
3. **Migration-guide update:** §"Override Discipline" added with two-phase pattern + confirm_token rationale.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors: 1 OverrideWarning model + 1 submit_override + 1 apply_override + 1 compute_cache_impact + 1 RunState extension + DecisionCardMeta cache_state populated.

### AC-3.5-K — Sprint-status state-flips at filing AND at close

At filing: `migration-3-5-...: ready-for-dev`. At close: `migration-3-5-...: done`.

---

## File Structure Requirements

### NEW files

```
app/runtime/
├── override_api.py                                 # AC-B + AC-C submit_override + apply_override + compute_cache_impact
├── override_warning.py                             # AC-A OverrideWarning model
└── schema/
    └── override_warning.v1.schema.json

tests/unit/runtime/
├── test_override_warning_strict.py                 # 3 tests (AC-A)
├── test_submit_override_returns_warning.py         # 1 test (AC-B)
├── test_submit_override_no_state_mutation.py       # 1 test (AC-B)
└── test_compute_cache_impact.py                    # 2 tests parametrize → 1 K-floor (AC-D)

tests/integration/runtime/
├── test_apply_override_match_path.py               # 1 test (AC-C)
├── test_apply_override_stale_token_rejected.py     # 2 tests (AC-C)
└── test_decision_card_cache_state_post_override.py # 3 tests (AC-E)

tests/unit/state/
└── test_run_state_model_overrides_field.py        # 2 tests (AC-F)

tests/fixtures/runtime/
└── override_warning_golden.json
```

### MODIFIED files

- `app/state/run_state.py` — `model_overrides: dict[str, str] = Field(default_factory=dict)` extension per AC-F (additive minimal).
- 3.4 transport surfaces (`gate_decide.py`, `gate_endpoint.py`, `gate_cli.py`) — extend with `submit_override` + `apply_override` surfaces per Decision #1 (h); transport-parity test from 3.4 extends to cover override surfaces.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — entry for OverrideWarning family.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Override Discipline" added.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-K.

---

## Testing Requirements

**K-target ~1.4× (target 12 / floor 9).** Test count + K-floor:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 3 (strict + tz-aware + cost-non-negative) | **3** |
| B | 2 (returns-warning + no-state-mutation) | **2** |
| C | 3 (match + 2 stale-token rejections) | **2** (match + stale-token-orthogonal) |
| D | 2 parametrize → 1 K-floor (3 fixtures, same property) | **1** |
| E | 3 (healthy + mixed + cold) | **2** (parametrize-collapsible per M-R18 → 1 + cold-state-cold-start orthogonal = 2) |
| F | 2 (field-present + round-trip) | **1** (field-extension single property) |
| **Total** | **15 collected** | **11 K-floor units** |

**Honest K-floor: 11** (above floor 9). Within ~1.4× K-target band (12/9 = 1.33×; 11/9 = 1.22×). Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
