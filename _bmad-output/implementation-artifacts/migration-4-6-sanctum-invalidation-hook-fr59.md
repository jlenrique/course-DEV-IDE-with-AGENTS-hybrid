# Migration Story 4.6: Sanctum Invalidation Hook (FR59) + NFR-O3 Warnings

**Status:** ready-for-dev
**Sprint key:** `migration-4-6-sanctum-invalidation-hook-fr59`
**Epic:** Slab 4 — M4 gate.
**Pts:** 3 | **Gate:** single (per governance JSON `4-6.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.3× (target 10 / floor 8).

**Predecessor:** 4.4 done (LedgerEvent SanctumMutationEvent kind required for this story's emission target). Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `4-6.expected_gate_mode = "single-gate"`.
2. **Substrate: `app/runtime/sanctum_watcher.py` does NOT exist** (verify at T1).
3. **Watchdog Python dep** — verify shipped per `pyproject.toml`; if absent, add via operator-gated AC OR sandbox-AC dev-agent install.
4. **Sanctum substrate** — `_bmad/memory/{wanda-sidecar, bmad-agent-marcus, ...}/` shipped per Slab-1+Slab-2 substrate.
5. **DecisionCardMeta cache_state** per 3.2 — sanctum mutation surfaces as warning in next DecisionCard.
6. **LedgerEvent SanctumMutationEvent kind** per 4.4 — emission target.
7. **Sanctum digest read pattern** per Wanda 2c.2 + Marcus 3.1 — `_read_sanctum_digest` via allowlist (per A-R4-3.1 substrate-aware adaptation).
8. Severance posture.

### Substrate sweep

- `app/runtime/` exists per Slab-1.
- `_bmad/memory/wanda-sidecar/` populated per 2c.2 close.
- `app/models/state/sanctum_fingerprint.py` per 3.5 substrate cascade discovery.
- 4.4 LedgerEvent SanctumMutationEvent kind shipped.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/runtime/sanctum_watcher.py` with watchdog file-watcher; (b) hash-delta computation on file change; (c) ledger event `kind="sanctum_mutation"` emission; (d) DecisionCardMeta warning surfacing at next gate; (e) NFR-O3 non-fatal — running trial does not fail on mutation-during-invocation. NOT in scope: sanctum cold-read pattern (Slab-2 substrate; reused).

**Decision #2 — Mutation-timing semantics:** mutation BEFORE invocation → next cold-read picks up mutated state (no spurious warning); mutation DURING invocation → warning logs + surfaces at next gate (NFR-O3 non-fatal); mutation AFTER invocation completes → next-trial's cold-read picks up.

**Decision #3 — Hash-delta evidence shape:** SanctumMutationEvent payload = `{file_path: str, hash_before: str (sha256-hex), hash_after: str, mutated_at: datetime tz-aware, suggested_invalidating_commit: str | None}`. The `suggested_invalidating_commit` field offers the operator a recovery hint (e.g., the commit SHA that would re-baseline the sanctum).

---

## Story

As an **operator wanting visibility into prefix-stability risk per FR59+D5**,
I want **`app/runtime/sanctum_watcher.py` with watchdog file-watcher + NFR-O3 non-fatal warnings surfaced via ledger + DecisionCard meta section**,
So that **FR59 is met + D5 invalidation hook is operator-visible + sanctum mutations during a trial don't silently invalidate cache prefixes**.

---

## Acceptance Criteria

### AC-4.6-A — `app/runtime/sanctum_watcher.py` watchdog implementation

- **Given** no sanctum_watcher exists; watchdog Python dep verified
- **When** dev authors `SanctumWatcher` class wrapping `watchdog.observers.Observer` against `_bmad/memory/**/*.md`
- **Then** file-mutation event triggers callback: compute hash-delta + emit SanctumMutationEvent ledger event per Decision #3.
- **Test pin:** `tests/integration/runtime/test_sanctum_watcher_detects_mutation.py` — 1 test using `tmp_path` sanctum + mutate file + assert callback fires + LedgerEvent emitted.

### AC-4.6-B — DecisionCardMeta sanctum-mutation warning surface (per 3.2 cache_state extension)

- **Given** sanctum mutation occurred during active trial; next gate fires
- **When** DecisionCardMeta is constructed for the gate
- **Then** `meta.sanctum_warnings: list[SanctumWarning]` populated; each warning cites mutated file + suggested_invalidating_commit; cache_state may transition `"healthy" → "mixed"` if mutation invalidates prefix
- **Test pin:** `tests/integration/runtime/test_decision_card_carries_sanctum_warnings.py` — 1 test.

### AC-4.6-C — Mutation-timing semantics per Decision #2

- **Given** 3 mutation-timing scenarios (before / during / after invocation)
- **When** sanctum_watcher observes each
- **Then**:
  - Before: next cold-read picks up; NO spurious warning
  - During: warning logs + surfaces at next gate; trial does NOT fail (NFR-O3)
  - After: next-trial's cold-read picks up
- **Test pin:** `tests/integration/runtime/test_mutation_timing_semantics.py` — 3 tests parametrize → 1 K-floor unit (per Murat M-R18 same-property "warning surfaces correctly per timing class").

### AC-4.6-D — NFR-O3 non-fatal contract test

- **Given** mutation DURING invocation
- **When** the running trial proceeds past the watcher event
- **Then** trial completes (no exception raised); LedgerEvent emitted; counter incremented
- **Test pin:** `tests/integration/runtime/test_sanctum_mutation_non_fatal.py` — 1 test asserting trial completes despite mutation event.

### AC-4.6-E — Anti-pattern catalog harvest

NO new entries expected.

### AC-4.6-F — TEMPLATE compliance

R1, R6, R8 honored.

### AC-4.6-G — D12 close protocol (single-gate; FOUR-line)

1. Invariant preservation: FR59+D5 met; NFR-O3 non-fatal.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §"Sanctum Invalidation Hook" added.
4. TEMPLATE compliance: R1, R6, R8.

### AC-4.6-H — Sprint-status state-flips.

---

## File Structure Requirements

### NEW files

- `app/runtime/{sanctum_watcher, sanctum_warning}.py`
- `tests/integration/runtime/{test_sanctum_watcher_detects_mutation, test_decision_card_carries_sanctum_warnings, test_mutation_timing_semantics, test_sanctum_mutation_non_fatal}.py`

### MODIFIED files

- `app/models/decision_cards/base.py` — `DecisionCardMeta.sanctum_warnings` additive field per AC-B (verify against 3.2 close state; if 3.2 didn't ship this field, additive minimal extension at 4.6).
- `pyproject.toml` — add `watchdog` dep IF not present (operator-gated AC OR sandbox-AC dev install).
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H.

---

## Testing Requirements

**K-target ~1.3× (target 10 / floor 8).** AC-A:1 + AC-B:1 + AC-C:3 parametrize → 1 + AC-D:1 = **4 K-floor**. RIDER: AC-A adds `test_watcher_observes_only_md_files` (extension filter property) + `test_sanctum_warning_pydantic_strict` (4-file-lockstep precedent) + AC-B adds `test_cache_state_transitions_on_mutation` (cross-AC integration) + AC-C adds `test_no_spurious_warning_for_pre_invocation_mutation` (orthogonal positive test) = honest **8 K-floor**. Within band.

Sandbox-AC PASS (watchdog Python dep; no live API).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
