# Migration Story 5a.3: Economics Measurement + ≥50% Cost-Reduction Bar

**Status:** ready-for-dev
**Sprint key:** `migration-5a-3-economics-cost-reduction-bar`
**Epic:** Slab 5a — M5 acceptance gate.
**Pts:** 3 | **Gate:** single (per governance JSON `5a-3.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.3× (target 10 / floor 8).

**Predecessor:** 5a.2 done (parity trial supplies the per-trial cost measurement target). Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `5a-3.expected_gate_mode = "single-gate"`.
2. **Substrate:** `app/runtime/economics.py` does NOT exist (verify); `_bmad-output/economics-baselines/` does NOT exist (verify; 5a.3 creates baselines directory).
3. **Cache hit-rate substrate** — Slab-1 cache_state per `app/models/state/cache_state.py` (verified per 3.5 substrate cascade); per-node prefix-warmth tracking.
4. **Token-cost source** — LangSmith trace per-node token counts + per-tier cost from `app/runtime/model_cascade.py` (verify Slab-1 cost-table location).
5. **Primary-repo baseline** — operator-supplied at `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json` (operator captures per epic 5a.3); if absent, T1 halts pre-measurement.
6. **5a.2 head-to-head parity trial** — provides the comparison data point.
7. **PRD §Cost Projection** — ≥50% reduction bar; <30% triggers Revise/Rollback default at M5 ship verdict.
8. Severance posture.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/runtime/economics.py::measure_trial_cost(trial_id) -> TrialEconomicsReport` per-trial cost breakdown by specialist, tier, cache hit/miss; (b) `compute_reduction_percentage(baseline, new) -> float` percentage per FR55+FR56; (c) `cache_hit_rate_per_node(trial_id) -> dict[str, float]` per FR54 substitute metric; (d) baseline storage convention at `_bmad-output/economics-baselines/`; (e) economics dashboard CLI `app.marcus.cli economics report --trial <id>` (small impl; full dashboard at 5b.2). NOT in scope: full dashboard UX (5b.2); cost-projection forecasting beyond ≥50% bar.

**Decision #2 — Cache-hit-rate ≥80% median bar at M5:** if median cache hit rate <80% across all nodes, prefix-stability audit triggers. Audit emits `_bmad-output/economics-baselines/prefix-stability-audit-<date>.md` with per-node hit-rate breakdown + diagnostic recommendations.

**Decision #3 — ≥50% reduction bar enforcement:** `compute_reduction_percentage` returns float in [0, 1]. If <0.50, M5 verdict at 5a.5 defaults to Revise (operator may override). If <0.30, M5 verdict defaults to Revise or Rollback per PRD §Cost Projection.

**Decision #4 — TrialEconomicsReport Pydantic v2 strict** (four-file-lockstep per 31-1 schema-shape precedent): `{trial_id: UUID4, measured_at: datetime tz-aware, total_cost_usd: float ≥ 0, per_specialist_breakdown: dict[str, SpecialistCost], per_tier_breakdown: dict[str, float], cache_hit_rate: float ∈ [0,1], cache_hit_rate_median_per_node: float ∈ [0,1]}`.

---

## Story

As an **operator validating the migration economic argument per FR55+FR56+M5 cost-projection bar**,
I want **`app/runtime/economics.py` measuring cache hit rate + token cost + per-specialist cost + comparison against recorded baseline + ≥50% reduction target confirmed + cache-hit-rate ≥80% median bar**,
So that **FR55 + FR56 + M5 cost-projection bar (≥50% reduction) is met and ship verdict at 5a.5 has economic evidence**.

---

## Acceptance Criteria

### AC-5a.3-A — `app/runtime/economics.py::measure_trial_cost()` impl

- **Given** trial-id from 5a.2 head-to-head parity trial
- **When** dev authors `measure_trial_cost(trial_id) -> TrialEconomicsReport`
- **Then** report includes per-specialist + per-tier + cache hit/miss breakdown.
- **Test pin:** `tests/integration/runtime/test_measure_trial_cost.py` — 1 test asserting report shape + non-zero total_cost.

### AC-5a.3-B — `TrialEconomicsReport` Pydantic v2 strict (four-file-lockstep)

- **Given** Decision #4 schema
- **When** dev authors model + JSON Schema + shape-pin test + golden fixture
- **Then** four-file-lockstep present.
- **Test pin:** `tests/unit/runtime/test_trial_economics_report_strict.py` — 3 tests (strict_config + tz-aware + cost-non-negative).

### AC-5a.3-C — `compute_reduction_percentage()` ≥50% bar enforcement

- **Given** baseline at `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json` (operator-supplied at T1)
- **When** dev authors `compute_reduction_percentage(baseline, new) -> float`
- **Then** function returns float ∈ [0, 1]; ≥0.50 = ship-eligible per PRD; <0.30 = Revise/Rollback default.
- **Test pin:** `tests/unit/runtime/test_compute_reduction_percentage.py` — 3 tests parametrize over 3 scenarios (≥50% pass, 30-50% conditional, <30% fail) → 1 K-floor unit per Murat M-R18 same-property.

### AC-5a.3-D — `cache_hit_rate_per_node()` + ≥80% median bar (Decision #2)

- **Given** cache_state per node from runtime
- **When** dev authors function returning `dict[str, float]` per-node + computes median
- **Then** if median <0.80, prefix-stability audit triggered + audit Markdown emitted.
- **Test pin:** `tests/integration/runtime/test_cache_hit_rate_audit_trigger.py` — 2 tests: ≥80% no audit; <80% triggers audit + Markdown emission.

### AC-5a.3-E — Dashboard CLI minimal impl

- **Given** transports from 3.4
- **When** dev authors `app.marcus.cli economics report --trial <id>` subcommand (small; full dashboard 5b.2)
- **Then** subcommand outputs human-readable summary of TrialEconomicsReport.
- **Test pin:** `tests/integration/runtime/test_economics_cli.py` — 1 test invoking subprocess + assert exit 0 + stdout contains "total_cost".

### AC-5a.3-F — Anti-pattern catalog harvest

NO new entries expected.

### AC-5a.3-G — TEMPLATE compliance

R1, R6, R8 honored.

### AC-5a.3-H — D12 close protocol (single-gate; FOUR-line)

1. Invariant preservation: FR55 + FR56 + ≥50% bar + ≥80% cache-hit-rate median bar.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §"Economics" added.
4. TEMPLATE compliance: R1, R6, R8.

### AC-5a.3-I — Sprint-status state-flips at filing AND close.

---

## File Structure Requirements

### NEW files

- `app/runtime/economics.py` + `app/models/runtime/trial_economics_report.py` + `schema/trial_economics_report.v1.schema.json`
- `_bmad-output/economics-baselines/.gitkeep` (directory established; operator deposits baselines)
- `tests/integration/runtime/{test_measure_trial_cost, test_cache_hit_rate_audit_trigger, test_economics_cli}.py`
- `tests/unit/runtime/{test_trial_economics_report_strict, test_compute_reduction_percentage}.py`
- `tests/fixtures/runtime/trial_economics_report_golden.json`

### MODIFIED files

- `app/marcus/cli/__init__.py` — add `economics` subcommand (extends 3.4 CLI per canonical marcus/cli/ home per Slab-3 substrate-aware adaptation; verify path)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-I.

---

## Testing Requirements

**K-target ~1.3× (target 10 / floor 8).** AC-A:1 + AC-B:3 + AC-C:3→1 + AC-D:2 + AC-E:1 = **8 K-floor**. RIDER: AC-B JSON-schema-parity test → +1; AC-D audit-Markdown-shape test → +1 = honest **10 K-floor**. Within band.

Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
