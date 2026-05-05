# 7c.5.G2C Contract Diff

T1 artifact for `migration-7c-5-g2c-decision-card-extend-and-audit`.

## 0. T0 Frozen-Hash Pre-Check

Recorded and on-disk G2C pre-extension hashes match:

```text
app/models/decision_cards/g2c.py sha256: 237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a
FROZEN_AT_SHIP_HASHES["g2c"]: 237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a
```

`DecisionCardBase`, `LOCKSTEP_CHECK`, and `FOUR_FILE_GLOBS` import cleanly. Sandbox-AC validator passes for the story spec. T1 class-conformance baseline is 16 parity contract files: 11 activation plus 5 decision-card shape-pins.

## 1. Legacy G2CCard Field Disposition

| Legacy field | Legacy source | Migrated disposition | Rationale |
| --- | --- | --- | --- |
| `gate_id` | declared on `G2CCard` as `Literal["G2C"]` | preserve/re-declare as `Literal["G2C"]` | Discriminated-union routing, manifest dotted refs, and terminal gate dispatch depend on the `G2C` discriminator. |
| `readiness_status` | declared on `G2CCard` as `Literal["ready", "blocked"]` | preserve/re-declare as `Literal["ready", "blocked"]` | This is the gate-specific G2C readiness verdict and remains the core pre-composition QA payload. |
| `blocking_issues` | declared on `G2CCard` | preserve/re-declare with default empty list | Constructor sites pass the field today; blocked-readiness consumers need the list shape preserved. |
| `ready_nodes` | declared on `G2CCard` | preserve/re-declare with default empty list | Constructor sites pass the field today; downstream pause/resume diagnostics use the ready-node list. |

## 2. Legacy DecisionCard Base Field Disposition

Per AMELIA-P5 V6, every row carries `audit_method`. All DROP rows use `audit_method=heavy` with smoke-pass evidence against `tests/composition/`, `tests/integration/marcus/`, and `tests/integration/replay/`.

| field | disposition | audit_method | rationale |
| --- | --- | --- | --- |
| `card_id` | preserve-via-re-declaration | light | Re-declare on migrated `G2CCard` as Pydantic `UUID4`; required by resume registry, operator verdicts, fixture round-trip, and persisted decision-card JSON. |
| `trial_id` | preserve-via-re-declaration | light | Re-declare on migrated `G2CCard` as Pydantic `UUID4`; required by registry, digest, and trial-scoped persistence consumers. |
| `created_at` | preserve-via-re-declaration | light | Re-declare with `enforce_tz_aware`, mirroring G2A/G1; existing generic tests reject naive datetimes. |
| `drafted_proposal` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k drafted_proposal --co -q` collected 0 tests. Targeted field grep found direct reads only in G1-only tests; `pytest tests/composition/test_pre_gate_marcus_precedence_unaltered.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q --tb=short` passed 4 tests. No required-root G2C direct read exists. G2C constructor sites must stop passing this legacy common field at T2. |
| `evidence` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k evidence --co -q` collected 7 tests; execution passed 7 tests. Targeted `card.evidence` grep found direct reads only in G1-only adjacent-summary tests; `pytest tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py -q --tb=short` passed 3 tests. No required-root G2C direct read exists. G2C constructor sites must stop passing this legacy common field at T2. |
| `risks` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k risks --co -q` collected 0 tests. Targeted grep found no `card.risks` or `getattr(..., "risks")` access in the required roots. G2C constructor sites must stop passing this legacy common field at T2. |
| `verb` | preserve-via-re-declaration | light | Re-declare as closed `Literal["approve", "edit", "reject"]`; `m3_trial.py` currently emits `edit` for G2C and generic strict tests reject invalid verbs. |
| `meta` | preserve-via-base | light | Migrate to `_base.DecisionCardMeta` inherited through `DecisionCardBase`; T2 constructor sites must convert legacy meta to the base meta shape as G1 did. |
| `model_config.extra="forbid"` | preserve-via-base | light | Inherited from `DecisionCardBase`; generic strict tests expect extra-field rejection. |
| `model_config.validate_assignment=True` | preserve-via-base | light | Inherited from `DecisionCardBase`; generic strict tests expect assignment validation. |
| `model_config.frozen=False` | change to frozen via `DecisionCardBase` | light | Intentional Slab 7c pattern; new G2C shape-pin must assert mutation rejection. |

## 3. Legacy DecisionCardMeta Field Disposition

Because this section contains DROP rows, it also carries `audit_method` per governance JSON `extend_and_audit_t1_audit_method`.

| field | disposition | audit_method | rationale |
| --- | --- | --- | --- |
| `cache_state` | preserve-via-base | light | Shared metadata remains required on `_base.DecisionCardMeta`; string payloads validate through the base cache-state adapter. |
| `affected_nodes` | preserve-via-base | light | Shared metadata remains required and retains non-empty entry validation. |
| `override_trail` | preserve-via-base | light | Shared override history remains required by the 7c base metadata contract. |
| `reject_rate` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k reject_rate --co -q` collected 0 tests; targeted grep found no required-root reads. |
| `party_mode_contributions` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k party_mode_contributions --co -q` collected 0 tests; targeted grep found no required-root reads. Separate `tests/integration/gates/` tests read this field on `G-PARTY` cards, not G2C. |
| `consolidated_at` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k consolidated_at --co -q` collected 0 tests; targeted grep found no required-root reads. Separate `tests/integration/gates/` tests read this field on `G-PARTY` cards, not G2C. |
| `sanctum_warnings` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k sanctum_warnings --co -q` collected 0 tests; targeted grep found no required-root reads. |

## 4. New Fields Added

| New field | Source | Disposition |
| --- | --- | --- |
| `schema_version: Literal["v1"]` | FR-7c-51 | Add to migrated `G2CCard` with default `"v1"` and schema emission. |
| `decision_card_digest: str` | `DecisionCardBase` | Required lowercase sha256 digest inherited from the 7c base. Constructor sites must supply it at T2. |
| `gate_focus: Literal["pre_composition_qa"]` | ADR 0002 gate-family taxonomy | Add as a new closed one-value G2C family marker. Legacy G2CCard has no `gate_focus`; this is an explicit contract-evolution ADD. |

## 5. Closed-Enum Tightening

`gate_id` remains `Literal["G2C"]`; the effective contract stays closed and must continue rejecting non-G2C discriminator values.

`readiness_status` remains `Literal["ready", "blocked"]`; the effective G2C verdict set stays closed.

`gate_focus` is added as `Literal["pre_composition_qa"]`; shape-pin coverage must reject non-`pre_composition_qa` values.

`schema_version` is added as `Literal["v1"]`; shape-pin coverage must reject non-v1 schema versions.

`verb` remains `Literal["approve", "edit", "reject"]`; generic per-gate strict tests continue to reject invalid verbs.

## 6. Pattern-Parity Ratchets

T2 implementation should mirror `app/models/decision_cards/g2a.py` and post-G1 `app/models/decision_cards/g1.py`:

- Use Pydantic `UUID4` for `card_id` and `trial_id`, not bare `UUID`.
- Validate UUID4 values through `enforce_uuid4_version`.
- Validate `created_at` through `enforce_tz_aware`.
- Keep `readiness_status`, `gate_id`, `gate_focus`, `schema_version`, and `verb` as closed Literals.
- Keep every field described with `Field(..., description=...)`.
- Inherit `extra="forbid"`, `validate_assignment=True`, and `frozen=True` from `DecisionCardBase`.

G2C has no free-text scalar field requiring strip-then-non-empty validation. `blocking_issues` and `ready_nodes` remain list fields with default empty lists.

## 7. Net Diff Summary

Added: `schema_version`, `decision_card_digest`, `gate_focus`.

Preserved by re-declaration: `card_id`, `trial_id`, `gate_id`, `created_at`, `verb`, `readiness_status`, `blocking_issues`, `ready_nodes`.

Preserved by `DecisionCardBase`: strict config, frozen assignment behavior, `meta` shape, digest validation.

Dropped from G2C after heavy audit: `drafted_proposal`, `evidence`, `risks`, and legacy meta extensions `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings`.

Required T2 consumer updates:

- `app/marcus/orchestrator/production_runner.py:434` must construct G2CCard without dropped legacy fields, supply `decision_card_digest`, and convert legacy `DecisionCardMeta` to `_base.DecisionCardMeta`.
- `marcus/orchestrator/m3_trial.py:169` must construct G2CCard without dropped legacy fields, supply `decision_card_digest`, and convert legacy `DecisionCardMeta` to `_base.DecisionCardMeta`.
- Generic fixture/schema consumers must be refreshed through the four-file lockstep: `schema/g2c.v1.schema.json`, `tests/fixtures/decision_cards/g2c_golden.json`, and the new `tests/parity/test_decision_card_g2c_shape.py`.

No edit is expected for the 2-class-regime substrate unless T2 verification exposes a G2C-specific gap: `app/manifest/compiler.py`, `app/manifest/refs.py`, `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py`, and `app/gates/resume_api.py` already accept both legacy `DecisionCard` and new `DecisionCardBase` after G1.

## 8. T1 Baseline Evidence

Commands executed:

```text
.venv/Scripts/python.exe -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/g2c.py','rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; print(FROZEN_AT_SHIP_HASHES['g2c'])"
.venv/Scripts/python.exe -c "from app.models.decision_cards._base import DecisionCardBase; from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK; from app.parity.contracts.tw_7c_3_firing import FOUR_FILE_GLOBS; print(DecisionCardBase.__name__, bool(LOCKSTEP_CHECK), len(FOUR_FILE_GLOBS))"
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k drafted_proposal --co -q
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k evidence --co -q
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k evidence -q --tb=short
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k risks --co -q
.venv/Scripts/python.exe -m pytest tests/composition/test_pre_gate_marcus_precedence_unaltered.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k reject_rate --co -q
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k party_mode_contributions --co -q
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k consolidated_at --co -q
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k sanctum_warnings --co -q
.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q --tb=short
```

T1 regression baseline: `870 passed, 1 failed, 18 skipped`. The sole failure is inherited governance-version drift in `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`, now expecting `2026-04-29-slab7b-twelve-stories` while the governance JSON version is `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` from commit `57b92b2`. No G2C body files were changed before this baseline.
