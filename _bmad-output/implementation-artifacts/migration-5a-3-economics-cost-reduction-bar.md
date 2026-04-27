# Migration Story 5a.3: Cost-Engineering Foundation (Cascade + Telemetry + Characterization Baseline)

**Status:** ready-for-dev
**Sprint key:** `migration-5a-3-economics-cost-reduction-bar`
**Epic:** Slab 5a — M5 acceptance gate.
**Pts:** 5 | **Gate:** single (per governance JSON `5a-3.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.4× (target 14 / floor 10).

**Predecessor:** 5a.2 done (parity trial supplies the per-trial token-trace target). Drafted-for-queue.

---

## SUBSTRATE-AWARE ADAPTATION (2026-04-26 — operator-ratified)

**Originally authored as:** "Economics Measurement + ≥50% Cost-Reduction Bar" — required `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json` from a primary-repo run + cited a non-existent `app/runtime/model_cascade.py` as the cost-accounting source-of-truth + bound M5 ship to a relative-to-legacy ≥50% reduction percentage.

**Codex T1 halted on 2026-04-26** with two confirmed substrate failures: (a) the primary baseline file does not exist on this branch and the legacy code does not capture per-call token data (operator tracks via service-provider invoices only); (b) `app/runtime/model_cascade.py` does not exist on this branch — the migration's actual cost shape is per-node token counts in LangSmith traces + per-specialist model assignment.

**Operator-ratified amendment (2026-04-26 session, this branch):** the migration ships *new* cost-engineering capability that did not exist on legacy. There is no honest baseline to compare against. The M5 gate is repointed from "prove relative reduction vs legacy" to "ship deliberate cost engineering foundation: documented cascade + per-call telemetry + characterization baseline against which future optimization is measured."

**Operator decisions binding this amendment (D1–D9, ratified 2026-04-26):**
- **D1.** Marcus = frontier-tier model; specialists = right-sized per role with stated rationale per agent.
- **D2.** OpenAI family only (no other API keys available). Models parameterized via config (no hardcoded model IDs in agent code) so cascade can be rebalanced without code change.
- **D3.** Per-specialist model assignment inferred by reading specialist-registry.yaml + specialist code; proposed assignment ratified at this story's close, not pre-locked.
- **D4.** Richer cost-tracking scope: per-trial cost report + per-agent attribution + drift alerts on per-agent cost-per-call deviation from rolling-median.
- **D5.** Parameterize-with-defaults for model picks (no model-ID lock at this story; defaults baked into config; operator swaps via config edit).
- **D6.** Pricing table = config file (`runtime/config/openai_pricing.yaml`); manual update when OpenAI prices change (~quarterly at most).
- **D7.** Soft-cap budget opt-in via env (`MARCUS_TRIAL_BUDGET_USD`); default unset = no cap; when set, trial logs warning + emits span at threshold but does NOT halt mid-trial.
- **D8.** Cost-data persistence at `state/config/runs/<trial-id>/cost-report.{json,md}` colocated with the trial it describes.
- **D9.** Drift alert: rolling 5-trial median per agent; ±50% deviation = informational alert (logged + emitted as span); not blocking.

**LangSmith availability (operator-confirmed 2026-04-26):** both Personal Access Key (local trials) and Service Key (CI/GHA) are now provisioned. Workspace name `course-content-production`. Free-tier limits (5K traces/mo, 14-day retention) are sufficient for migration acceptance; cost-report JSON persisted to disk per D8 gives permanent record independent of LangSmith retention.

**What this amendment does NOT do:** It does not require the operator to run the legacy primary runtime to generate a comparison baseline. It does not retain the ≥50% reduction bar at the M5 gate. The 5a.4 invariant matrix and 5a.5 M5 verdict criteria are amended in lockstep.

---

## T1 Readiness Block

1. Governance: `5a-3.expected_gate_mode = "single-gate"` (governance JSON v2026-04-26 amendment-log entry documents this substrate-aware adaptation).
2. **Substrate (verify on this branch):**
   - `app/runtime/economics.py` does NOT exist (5a.3 creates it).
   - `runtime/config/model_cascade.yaml` does NOT exist (5a.3 creates it).
   - `runtime/config/openai_pricing.yaml` does NOT exist (5a.3 creates it).
   - `_bmad-output/economics-baselines/` may not exist (5a.3 creates it, but for *characterization-on-migrated-runtime* baselines only — NOT primary-repo comparison baselines).
   - `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json` is **explicitly NOT required** per amendment.
   - `app/runtime/model_cascade.py` is **explicitly NOT required** per amendment (this name was a stale spec reference; the actual cost shape is per-node token counts in LangSmith traces + per-agent model assignment in the cascade config).
3. **LangSmith trace token-counts** are the cost source-of-truth. Per-LLM-call `total_tokens` / `prompt_tokens` / `completion_tokens` are emitted by the OpenAI client and captured automatically in LangSmith spans when tracing is enabled. Verify `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` set in `.env` (operator-confirmed available).
4. **Specialist registry** at `skills/bmad-agent-marcus/references/specialist-registry.yaml` (or equivalent — verify path) supplies the list of specialists for cascade assignment.
5. **5a.2 parity trial** exists at `_bmad-output/implementation-artifacts/5a-2-parity-evidence-2026-04-26.md` — provides one concrete trial-id from which to read trace token counts.
6. **Pydantic v2 four-file-lockstep precedent** per 31-1 + 5a.3 four-file checklist at `docs/dev-guide/pydantic-v2-schema-checklist.md`.
7. Severance posture (frozen primary at upstream/master @ 3ed7c56 — *reference only*; not used for cost comparison).

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:**

(a) `app/runtime/economics.py` — public API:
  - `measure_trial_cost(trial_id: str) -> TrialEconomicsReport` reads LangSmith trace + applies pricing table + attributes per-agent;
  - `record_trial_cost_report(trial_id: str, report: TrialEconomicsReport) -> Path` writes JSON + Markdown to `state/config/runs/<trial-id>/`;
  - `compute_per_agent_drift(report: TrialEconomicsReport, history: list[TrialEconomicsReport]) -> dict[str, DriftStatus]` rolling-5-trial median ±50% per D9;
  - `check_trial_budget(running_total_usd: float, budget_usd: float | None) -> BudgetStatus` soft-cap evaluation per D7.

(b) `runtime/config/model_cascade.yaml` — per-agent model assignment + rationale. Loaded via `app/runtime/cascade_config.py::load_cascade() -> CascadeConfig` (Pydantic-validated). Default cascade (per D3, ratified at close):

```yaml
# runtime/config/model_cascade.yaml — operator-editable
marcus:
  model: gpt-5
  rationale: "Orchestrator; large context; synthesizes across specialist outputs"
specialists:
  irene:
    model: gpt-5-mini
    rationale: "Editorial pass; mid-tier reasoning sufficient"
  gary:
    model: gpt-5-mini
    rationale: "Slide generation; structured output; mid-tier"
  vera:
    model: gpt-5-mini
    rationale: "Verification pass; needs careful reasoning"
  texas:
    model: gpt-5-nano
    rationale: "Tool dispatch; narrow task; small model fine"
  quinn_r:
    model: gpt-5-nano
    rationale: "Retrieval orchestration; narrow task"
  tracy:
    model: gpt-5-nano
    rationale: "Linting/structural checks; narrow task"
  # ... etc per discovered specialist registry
```

Dev MUST read the specialist registry at T1 and propose a cascade entry per specialist with rationale derived from that specialist's responsibilities.

(c) `runtime/config/openai_pricing.yaml` — per-model `{input_per_1m_tokens_usd, output_per_1m_tokens_usd}`. Loaded via `app/runtime/cascade_config.py::load_pricing() -> PricingTable`. Initial entries for `gpt-5`, `gpt-5-mini`, `gpt-5-nano` populated with current OpenAI public prices (dev verifies at implementation; manual updates thereafter).

(d) `TrialEconomicsReport` Pydantic v2 strict (four-file-lockstep per Decision #4 below).

(e) Cost-report persistence at `state/config/runs/<trial-id>/cost-report.json` (machine-readable) + `state/config/runs/<trial-id>/cost-report.md` (operator-readable summary).

(f) Soft-cap budget hook called from per-LLM-call layer (likely a wrapper around the OpenAI client invocation) — emits warning span when running total exceeds `MARCUS_TRIAL_BUDGET_USD` env value (no halt).

(g) Drift alert hook emits informational span when per-agent cost-per-call deviates >±50% from rolling-5-trial median.

(h) `migration_health_dashboard.py` extension: include "trials with cost reports", "median trial cost (last 5)", "drift alerts (last 24h)" rows.

**NOT in scope:** comparison against primary-repo baseline (deleted from spec); ≥50% reduction enforcement (deleted); full operator-facing cost dashboard UI (deferred to 5b.2); cost-aware specialist routing / dynamic model selection (post-ship optimization story).

**Decision #2 — Characterization baseline (ON-MIGRATED-RUNTIME):**

Run cost machinery against the existing 5a.2 trial (`C1-M1-PRES-20260419B` per the parity evidence) + at least one fresh trial if launch tooling permits. Capture per-trial cost reports + summarize at `_bmad-output/economics-baselines/migrated-runtime-characterization-<date>.md` with:

- Total cost per trial USD.
- Per-agent attribution (which agent contributed what % of total).
- Per-model attribution (how much spend went to gpt-5 vs gpt-5-mini vs gpt-5-nano).
- Cascade rationale recap (which agent runs which model + why).
- Optimization headroom narrative ("if Marcus drops to gpt-5-mini for orchestration steps that don't require frontier reasoning, projected savings = $X").

This is the M5 evidence artifact — *not* a relative-reduction number, but a quantified characterization the operator can read and decide whether to ship on.

**Decision #3 — Soft-cap budget contract (per D7):**

```python
# Pseudocode
def check_trial_budget(running_total_usd: float, budget_usd: float | None) -> BudgetStatus:
    if budget_usd is None:
        return BudgetStatus(state="no-cap", over_by_usd=0.0)
    if running_total_usd > budget_usd:
        return BudgetStatus(state="over-budget-warning", over_by_usd=running_total_usd - budget_usd)
    return BudgetStatus(state="under-budget", over_by_usd=0.0)
```

Caller emits warning span on `over-budget-warning`; trial continues to completion. Hard halt is **explicitly out of scope** per D7 (data-loss patterns avoided).

**Decision #4 — `TrialEconomicsReport` Pydantic v2 strict (four-file-lockstep per Pydantic checklist):**

```python
# app/models/runtime/trial_economics_report.py
class TrialEconomicsReport(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    trial_id: str = Field(..., min_length=1)
    measured_at: datetime  # tz-aware enforced via validator
    total_cost_usd: float = Field(..., ge=0.0)
    per_agent_breakdown: dict[str, AgentCostEntry]
    per_model_breakdown: dict[str, float]  # model_id -> USD
    cascade_config_digest: str  # SHA256 of cascade YAML at trial time
    pricing_table_digest: str   # SHA256 of pricing YAML at trial time
    langsmith_trace_url: str | None = None
    drift_alerts: list[DriftAlert] = Field(default_factory=list)
    budget_status: BudgetStatus

class AgentCostEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    agent_name: str
    model_assigned: str
    call_count: int = Field(..., ge=0)
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0.0)

class DriftAlert(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    agent_name: str
    rolling_median_usd_per_call: float
    observed_usd_per_call: float
    deviation_pct: float

class BudgetStatus(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    state: Literal["no-cap", "under-budget", "over-budget-warning"]
    over_by_usd: float = Field(..., ge=0.0)
```

Four-file-lockstep:
- Model: `app/models/runtime/trial_economics_report.py`
- JSON Schema: `schema/trial_economics_report.v1.schema.json`
- Shape-pin tests: `tests/unit/runtime/test_trial_economics_report_strict.py`
- Golden fixture: `tests/fixtures/runtime/trial_economics_report_golden.json`

---

## Story

As an **operator establishing the cost-engineering foundation for the migrated runtime per FR55+FR56**,
I want **`app/runtime/economics.py` measuring per-trial cost from LangSmith trace token counts + a documented per-agent model cascade in `runtime/config/model_cascade.yaml` + per-call pricing in `runtime/config/openai_pricing.yaml` + per-trial cost reports + per-agent drift alerts + soft-cap budget telemetry + a characterization baseline on the migrated runtime**,
So that **FR55 + FR56 are met as cost-engineering capability the migration ships (capability that did not exist on legacy), M5 ship verdict has cost-characterization evidence, and post-ship optimization stories iterate against this foundation**.

---

## Acceptance Criteria

### AC-5a.3-A — `app/runtime/economics.py::measure_trial_cost()` impl

- **Given** a trial-id + LangSmith trace data + cascade config + pricing table
- **When** dev authors `measure_trial_cost(trial_id) -> TrialEconomicsReport` reading LangSmith spans, summing per-agent token counts, applying pricing table, attributing per-agent and per-model
- **Then** report includes per-agent + per-model breakdown + total + cascade/pricing digests + langsmith trace URL + drift alerts + budget status.
- **Test pin:** `tests/integration/runtime/test_measure_trial_cost.py` — 2 tests: (a) fixture trace → report shape + non-zero total + per-agent attribution sums to total; (b) trace with one agent over-spending → drift alert populated.

### AC-5a.3-B — `TrialEconomicsReport` Pydantic v2 strict (four-file-lockstep per Pydantic checklist)

- **Given** Decision #4 schema family
- **When** dev authors model + JSON Schema + shape-pin test + golden fixture
- **Then** four-file-lockstep present; emitted JSON Schema parity with model; tz-aware datetime enforced; cost fields ≥ 0; closed-set Literal on BudgetStatus.state with red-rejection.
- **Test pin:** `tests/unit/runtime/test_trial_economics_report_strict.py` — 4 tests: strict_config (extra="forbid" + validate_assignment) + tz-aware (rejects naive datetime) + cost-non-negative (rejects negative) + budget-state-closed (rejects unknown enum).

### AC-5a.3-C — Cascade config + pricing table loading + digest

- **Given** `runtime/config/model_cascade.yaml` + `runtime/config/openai_pricing.yaml` populated per Decision #1(b)+(c)
- **When** dev authors `app/runtime/cascade_config.py::load_cascade()` + `load_pricing()` returning Pydantic-validated structures with stable SHA256 digest
- **Then** loader rejects unknown keys; pricing table covers all models referenced by cascade; digest is byte-stable for unchanged file content.
- **Test pin:** `tests/integration/runtime/test_cascade_config_loading.py` — 3 tests: load OK + unknown-key rejected + digest stable across reads. `tests/integration/runtime/test_pricing_table_covers_cascade.py` — 1 test: every cascade-referenced model has a pricing entry.

### AC-5a.3-D — Soft-cap budget telemetry per D7 + Decision #3

- **Given** running cost during trial + optional `MARCUS_TRIAL_BUDGET_USD` env value
- **When** dev authors `check_trial_budget()` per Decision #3 contract + caller emits warning span on over-budget-warning state
- **Then** trial does NOT halt; warning emitted; budget_status field populated on report.
- **Test pin:** `tests/unit/runtime/test_check_trial_budget.py` — 3 tests: no-cap (returns no-cap), under-budget (returns under-budget), over-budget (returns over-budget-warning + over_by_usd correct).

### AC-5a.3-E — Per-agent drift alert per D9

- **Given** rolling 5-trial history + new trial
- **When** dev authors `compute_per_agent_drift()` evaluating ±50% deviation from rolling median per agent
- **Then** drift alerts populated for any agent exceeding band; informational only (no halt).
- **Test pin:** `tests/unit/runtime/test_compute_per_agent_drift.py` — 3 tests: under-band (no alert), over-band (alert with correct deviation_pct), insufficient history (no alert if <5 prior trials).

### AC-5a.3-F — Cost-report persistence per D8

- **Given** TrialEconomicsReport + trial_id
- **When** dev authors `record_trial_cost_report(trial_id, report)` writing both JSON and Markdown to `state/config/runs/<trial-id>/`
- **Then** both files exist; JSON deserializes back to identical TrialEconomicsReport; Markdown contains operator-readable summary (total + per-agent table + drift alerts + budget status).
- **Test pin:** `tests/integration/runtime/test_record_trial_cost_report.py` — 2 tests: round-trip JSON identity + Markdown contains required §-headers (regex per spec).

### AC-5a.3-G — Characterization baseline on migrated runtime per Decision #2

- **Given** at least one trial-id from 5a.2 (`C1-M1-PRES-20260419B`) with LangSmith trace available
- **When** dev runs the cost machinery against that trial + writes summary to `_bmad-output/economics-baselines/migrated-runtime-characterization-<date>.md`
- **Then** characterization document contains per-trial total + per-agent attribution + per-model attribution + cascade rationale recap + optimization-headroom narrative.
- **Test pin:** `tests/migration/test_5a_3_characterization_baseline_present.py` — 1 test asserting file exists + 5 required §-headers (Total / Per-Agent / Per-Model / Cascade Rationale / Optimization Headroom) + at least one trial-id reference.
- **Note:** if 5a.2 trial trace is not available in LangSmith (operator's account may not yet have backfilled traces from before LangSmith key was provisioned), dev runs against synthetic trace fixture and notes operator-window dependency in Dev Agent Record (mirror 5a.2 operator-window-conditional pattern).

### AC-5a.3-H — `migration_health_dashboard.py` cost rows

- **Given** dashboard at `scripts/utilities/migration_health_dashboard.py`
- **When** dev adds rows: "trials with cost reports", "median trial cost USD (last 5)", "drift alerts (last 24h)"
- **Then** dashboard renders with new rows; each row queries on-disk cost-report files + trial registry.
- **Test pin:** `tests/integration/runtime/test_migration_health_dashboard_cost_rows.py` — 1 test asserting dashboard output contains the 3 new row labels.

### AC-5a.3-I — Anti-pattern catalog harvest

NO new entries expected. If a cost-attribution anti-pattern surfaces (e.g., "treating LangSmith trace timing as a substitute for token counts"), file as candidate per harvest-gate.

### AC-5a.3-J — TEMPLATE compliance

R1, R6, R8 honored.

### AC-5a.3-K — D12 close protocol (single-gate; FOUR-line)

1. **Invariant preservation:** FR55 + FR56 met as cost-engineering-capability-shipped (NOT as relative-reduction-vs-legacy; see SUBSTRATE-AWARE ADAPTATION header). Cascade documented; pricing table maintained; per-trial reports generated; drift telemetry wired; soft-cap available.
2. **Anti-pattern harvest:** N/A unless surfaced.
3. **Migration-guide update:** §"Cost Engineering Foundation" added — cascade rationale + pricing-table maintenance + per-trial cost report shape + soft-cap budget usage + drift alert interpretation.
4. **TEMPLATE compliance:** R1, R6, R8.

### AC-5a.3-L — Sprint-status state-flips at filing AND close

At filing: confirm `migration-5a-3-economics-cost-reduction-bar: ready-for-dev`. At close: `migration-5a-3-economics-cost-reduction-bar: done`. Note in close comment: "scope amended 2026-04-26 from ≥50% reduction bar to cost-engineering foundation per substrate-aware adaptation; legacy comparison baseline not generated."

---

## File Structure Requirements

### NEW files

- `app/runtime/economics.py` — measurement, drift, budget, persistence functions.
- `app/runtime/cascade_config.py` — cascade YAML + pricing YAML loaders with digest.
- `app/models/runtime/trial_economics_report.py` — Pydantic v2 model family.
- `schema/trial_economics_report.v1.schema.json` — emitted JSON Schema.
- `runtime/config/model_cascade.yaml` — per-agent model assignment with rationale (proposed defaults; operator may rebalance).
- `runtime/config/openai_pricing.yaml` — per-model pricing (current OpenAI public prices at implementation time; manual updates thereafter).
- `_bmad-output/economics-baselines/.gitkeep` — directory for characterization baselines (NOT for primary-repo comparison; that requirement is removed).
- `_bmad-output/economics-baselines/migrated-runtime-characterization-<date>.md` — per AC-G.
- `tests/integration/runtime/{test_measure_trial_cost,test_cascade_config_loading,test_pricing_table_covers_cascade,test_record_trial_cost_report,test_migration_health_dashboard_cost_rows}.py`
- `tests/unit/runtime/{test_trial_economics_report_strict,test_check_trial_budget,test_compute_per_agent_drift}.py`
- `tests/migration/test_5a_3_characterization_baseline_present.py`
- `tests/fixtures/runtime/trial_economics_report_golden.json`

### MODIFIED files

- `scripts/utilities/migration_health_dashboard.py` — add 3 cost rows per AC-H.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Cost Engineering Foundation" added per D12.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-L.
- `.env.example` — add `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=<personal-key>`, `LANGSMITH_PROJECT=course-content-production`, `MARCUS_TRIAL_BUDGET_USD=` (optional, comment guidance per D7).
- `pyproject.toml` — verify `langsmith>=0.7,<1` already present (per session memory); add `pyyaml` if not already in dep list (cascade + pricing config readers).

---

## Testing Requirements

**K-target ~1.4× (target 14 / floor 10).**

K-floor calculation:
- AC-A: 2 (measure happy + drift-populating fixture)
- AC-B: 4 (strict_config + tz-aware + cost-non-neg + budget-state-closed)
- AC-C: 4 (load OK + unknown-key + digest stable + pricing-covers-cascade)
- AC-D: 3 (no-cap + under + over)
- AC-E: 3 (under-band + over-band + insufficient-history)
- AC-F: 2 (round-trip + Markdown shape)
- AC-G: 1 (characterization-baseline §-headers)
- AC-H: 1 (dashboard rows)

= **20 K-floor**. K-target 14 / floor 10 — current K-floor exceeds target and floor; this reflects the Richer scope per D4. If overshooting target meaningfully, dev may parametrize-collapse AC-C (4→2) and AC-D (3→1) per Murat M-R18 same-property collapse. **Honest K-floor after parametrize-collapse: 14 (matches target).**

Sandbox-AC PASS (LangSmith trace reads use shipped `langsmith` python dep — `pytest.skip` on missing service if account unavailable; OpenAI pricing reads are pure config-file IO).

---

## Dev Agent Record

Close record completed 2026-04-26 after the amended substrate-aware 5a.3
contract shipped and verified cleanly.

### T1 Readiness + substrate verification

Confirmed the amended 2026-04-26 substrate-aware contract matched the live tree
before implementation. The legacy baseline JSON did not exist, the branch did
not contain `app/runtime/model_cascade.py`, and the economics-facing files
named by the amended story (`app/runtime/economics.py`,
`app/runtime/cascade_config.py`, `runtime/config/model_cascade.yaml`,
`runtime/config/openai_pricing.yaml`) were absent and therefore correctly in
scope to create. Live model substrate on branch was registry-backed
`gpt-5.4` / `gpt-5-haiku` / `gpt-5-codex`, so the shipped cascade uses those
actual ids rather than the older planning shorthand `gpt-5` / `gpt-5-mini` /
`gpt-5-nano`. Specialist roster was verified from
`state/config/pipeline-manifest.yaml`, `app/models/registry.yaml`, and active
specialist config/code; alias normalization was required for `quinn-r` ->
`quinn_r` and `elevenlabs` -> `enrique`. No further substrate adaptation was
required because this story is itself the ratified adaptation.

### Implementation summary

Shipped the migrated-runtime cost-engineering foundation:

- strict `TrialEconomicsReport` Pydantic v2 model family plus pinned JSON
  schema and golden fixture;
- `app/runtime/cascade_config.py` loaders with SHA256 digests, alias-aware
  resolution, and pricing-coverage enforcement;
- `app/runtime/economics.py` for LangSmith trace measurement, per-agent and
  per-model attribution, rolling drift alerts, soft-cap budget posture, and
  JSON/Markdown report persistence under `state/config/runs/<trial-id>/`;
- operator-editable `runtime/config/model_cascade.yaml` and
  `runtime/config/openai_pricing.yaml`;
- synthetic characterization fixture plus persisted cost report artifacts for
  `C1-M1-PRES-20260419B`;
- migration health dashboard cost rows, `.env.example` LangSmith/budget
  guidance, and migration-guide documentation;
- repo-local `tmp_path` override in `tests/conftest.py` so the story-owned
  Windows pytest slice is no longer blocked by the known temp-root ACL defect.

### Cascade Assignment Ratification (per D3)

Proposed shipped cascade, derived from the live specialist substrate:

- `marcus`: `gpt-5.4`
- higher-judgment specialists on `gpt-5.4`: `vera`, `irene`, `cd`, `quinn_r`
  (alias `quinn-r`), `enrique` (alias `elevenlabs`)
- dispatch-heavy / bounded specialists on `gpt-5-haiku`: `texas`, `gary`,
  `kira`, `compositor`, `desmond`

Rationale is recorded per agent in `runtime/config/model_cascade.yaml`. If the
operator wants a different balance after close review, only the cascade config
needs editing; no agent code is hardcoded to a model id.

### Characterization Baseline Captured (per AC-G)

Captured at
`_bmad-output/economics-baselines/migrated-runtime-characterization-2026-04-26.md`.
Because live LangSmith trace access for the historical 5a.2 trial is
operator-window conditional, the characterization used the synthetic fixture at
`tests/fixtures/runtime/trial_cost_trace_fixture.json` and the same shipped
runtime cost machinery used for on-disk report persistence. Measured total was
`$0.171105`; top three contributors were `irene` (`$0.056000`), `quinn_r`
(`$0.033750`), and `marcus` (`$0.033000`). Primary optimization headroom is in
repeat premium-tier editorial/review passes, not in the already-right-sized
dispatch specialists.

### Verification

- `.\.venv\Scripts\python.exe -m pytest tests/unit/runtime tests/integration/runtime tests/migration/test_5a_3_characterization_baseline_present.py -q --tb=short`
  -> `71 passed, 4 skipped`
- `.\.venv\Scripts\python.exe -m ruff check app/runtime app/models/runtime tests/unit/runtime tests/integration/runtime tests/migration/test_5a_3_characterization_baseline_present.py`
  -> clean
- `.\.venv\Scripts\lint-imports.exe --config pyproject.toml`
  -> `Contracts: 9 kept, 0 broken.`
- `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-5a-3-economics-cost-reduction-bar.md`
  -> `PASS`
