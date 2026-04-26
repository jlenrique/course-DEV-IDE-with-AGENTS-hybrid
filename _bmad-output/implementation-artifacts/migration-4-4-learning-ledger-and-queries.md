# Migration Story 4.4: Learning Ledger + G2C/G3/G4 Events + Reject-Rate + Gate-Inventory Queries

**Status:** ready-for-dev
**Sprint key:** `migration-4-4-learning-ledger-and-queries`
**Epic:** Slab 4 — M4 gate.
**Pts:** 4 | **Gate:** dual (per governance JSON `4-4.expected_gate_mode = "dual-gate"`, rationale: `schema_shape`). **K-target:** ~1.4× (target 14 / floor 10).

**Predecessor:** 4.1 + 4.2 + 4.3 done. Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `4-4.expected_gate_mode = "dual-gate"` (schema_shape).
2. **Substrate: `app/ledger/` does NOT exist** (epic 4.4 says "empty"); verify at T1.
3. **Postgres substrate** — Slab-1 substrate per CLAUDE.md `project_no_docker` (Postgres native on operator's machine; psycopg shipped Python dep). Sandbox-AC discipline: dev-agent ACs verify via psycopg + `pytest.skip(...)` on missing service.
4. **Schema-shape story precedent (BINDING)** — 31-1 + 3.2 + 3.3 four-file-lockstep convention; `LedgerEvent` discriminated-union schema follows.
5. **NFR-R4 idempotent emission** — emission deduplication by `idempotency_key`.
6. **G2C/G3/G4 gate substrate** — 3.2 DecisionCard schema family + 3.3 OperatorVerdict + 3.4 transports all stable; gates fire per existing graph wiring; 4.4 EMITS ledger events at each gate fire.
7. **3.5 ledger event proto-events** — submit_override + apply_override emit `kind="override"` proto-events per 3.5 Decision #1 (h); 4.4 LedgerEvent discriminated union absorbs these.
8. Severance posture.

### Substrate sweep

- `app/ledger/` does NOT exist.
- `psycopg` shipped per `pyproject.toml` (verify at T1).
- `app/models/state/operator_verdict.py` per 3.3 substrate-aware adaptation.
- 3.2 DecisionCard family + 3.4 transport surfaces ready.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/ledger/{__init__, events, emitter, queries}.py` + `schema.sql`; (b) `LedgerEvent` discriminated union (per `kind` field: verdict / override / sanctum_mutation / + extensible); (c) Postgres `ledger_events` table; (d) idempotent emission by `idempotency_key`; (e) `reject_rate_per_gate(trial_id)` + `gate_inventory(trial_id)` + `sanctum_mutations(trial_id)` queries; (f) emission failure non-fatal (NFR-I2 parallel) — log + counter, no node fail. NOT in scope: sanctum_watcher (4.6 emits the events 4.4 absorbs); frozen-graph (4.5).

**Decision #2 — `LedgerEvent` discriminated-union per `kind`:** `kind: Literal["verdict", "override", "sanctum_mutation"]`; per-kind subclasses. Future kinds added via extensible enum + new subclass; Pydantic discriminated-union routing.

**Decision #3 — Idempotency key shape:** `idempotency_key = sha256(f"{trial_id}|{gate_id}|{kind}|{event_specific_natural_key}")`. Re-emission with same key = no-op (NFR-R4).

**Decision #4 — Postgres failure mode (NFR-I2 parallel):** if `psycopg.connect(...)` fails, emitter returns `EmissionResult(status="failed", reason=...)` + logs at warning level + increments `ledger_emission_failures_total` counter. Caller-node does NOT raise; trial continues. This is non-fatal per epic 4.4.

---

## Story

As a **governance observer of HIL decisions per FR37+FR36+FR45**,
I want **`app/ledger/{events, emitter, queries}.py` + `schema.sql` Postgres + G2C/G3/G4 event emission + reject_rate + gate_inventory + sanctum_mutations queries + idempotent emission by idempotency_key per NFR-R4 + non-fatal emission failure per NFR-I2 parallel**,
So that **FR37+FR36+FR45 are met and the learning ledger captures HIL decisions for KPI tracking + invariant audit**.

---

## Acceptance Criteria

### AC-4.4-A — `app/ledger/events.py::LedgerEvent` discriminated union (DUAL-GATE schema-shape gate-1)

- **Given** no `app/ledger/` exists
- **When** the dev agent authors `events.py::LedgerEvent` discriminated-union per Decision #2 + per-kind subclasses (`VerdictEvent`, `OverrideEvent`, `SanctumMutationEvent`)
- **Then** four-file-lockstep present per kind: model + JSON Schema + shape-pin test + golden fixture (3 kinds × 4 files = 12 lockstep artifacts).
- **Test pin:** `tests/unit/ledger/test_ledger_event_strict.py` — 3 tests parametrize over 3 kinds → 1 K-floor + 3 tests for discriminated-union routing.

### AC-4.4-B — `emitter.py::emit_ledger_event()` + idempotent dedup

- **Given** events.py shipped
- **When** dev authors `emit_ledger_event(event: LedgerEvent) -> EmissionResult` with idempotency check via `idempotency_key`
- **Then** re-emission at same key = no-op + returns existing event-id; new key = inserts row.
- **Test pin:** `tests/integration/ledger/test_emit_ledger_event_idempotent.py` — 2 tests: first emission inserts; second emission no-ops.

### AC-4.4-C — `queries.py::reject_rate_per_gate + gate_inventory + sanctum_mutations`

- **Given** ledger populated with events
- **When** dev authors the 3 query functions
- **Then**:
  - `reject_rate_per_gate(trial_id)` returns dict mapping gate_id → reject-rate (FR37)
  - `gate_inventory(trial_id)` returns list of gate_ids fired; equality with manifest-declared gate set (FR36)
  - `sanctum_mutations(trial_id)` returns list of `SanctumMutationEvent` for the trial
- **Test pin:** `tests/integration/ledger/test_queries.py` — 3 tests parametrize-collapsible to 1 K-floor (per query, same property = "returns expected shape from fixture rows").

### AC-4.4-D — `schema.sql` Postgres table + idempotency unique constraint

- **Given** no schema.sql exists
- **When** dev authors `app/ledger/schema.sql` with `ledger_events` table (columns: event_id UUID PK, trial_id UUID, gate_id text, kind text, payload jsonb, idempotency_key text UNIQUE, created_at timestamptz)
- **Then** psycopg loads schema cleanly; UNIQUE constraint on idempotency_key enforces dedup at DB layer.
- **Test pin:** `tests/integration/ledger/test_schema_sql_loads.py` — 1 test (skip if Postgres unreachable per sandbox-AC).

### AC-4.4-E — Non-fatal emission failure (NFR-I2 parallel)

- **Given** emitter handles psycopg.OperationalError gracefully
- **When** simulated Postgres-unavailable (mock psycopg connection raise)
- **Then** emitter returns `EmissionResult(status="failed", ...)` + logs warning + counter increment; caller-node does NOT raise; trial continues
- **Test pin:** `tests/integration/ledger/test_emit_failure_non_fatal.py` — 2 tests: connection-failure + return-shape + log-captured + counter-incremented.

### AC-4.4-F — Anti-pattern catalog harvest

NO new entries expected.

### AC-4.4-G — TEMPLATE compliance

R1, R6, R8 honored.

### AC-4.4-H — D12 close protocol (DUAL-gate; schema_shape; FIVE-line)

1. Invariant preservation: FR37+FR36+FR45 met; NFR-R4 idempotency; NFR-I2 non-fatal.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §"Learning Ledger" added.
4. TEMPLATE compliance: R1, R6, R8.
5. Dual-gate gate-2 (operator schema-shape review): operator confirms 3 LedgerEvent kinds + idempotency key shape.

### AC-4.4-I — Sprint-status state-flips.

---

## File Structure Requirements

### NEW files

- `app/ledger/{__init__, events, emitter, queries}.py` + `schema.sql`
- `app/ledger/schema/{verdict_event, override_event, sanctum_mutation_event}.v1.schema.json`
- `tests/unit/ledger/{test_ledger_event_strict, test_ledger_event_discriminated_union}.py`
- `tests/integration/ledger/{test_emit_ledger_event_idempotent, test_queries, test_schema_sql_loads, test_emit_failure_non_fatal}.py`
- `tests/fixtures/ledger/{verdict_event_golden, override_event_golden, sanctum_mutation_event_golden}.json`

### MODIFIED files

- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — 3 entries (one per kind).
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-I.

---

## Testing Requirements

**K-target ~1.4× (target 14 / floor 10).** AC-A:6 (3 strict parametrize → 1 + 3 discriminated-union → 1 = 2 K-floor) + AC-B:2 + AC-C:3 parametrize → 1 + AC-D:1 + AC-E:2 = **honest 8 K-floor**. RIDER: AC-A adds JSON-schema-parity per kind (3 parametrize → 1 K-floor) + AC-B adds emission_result schema test = **honest 10 K-floor**. Within band.

Sandbox-AC PASS (psycopg shipped Python dep + pytest.skip on missing service).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
