# 7c.5.G4 Contract Diff

T1 artifact for `migration-7c-5-g4-decision-card-extend-and-audit`.

## 0. T0 Frozen-Hash Pre-Check

Recorded and on-disk G4 pre-extension hashes match:

```text
app/models/decision_cards/g4.py sha256: 98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a
FROZEN_AT_SHIP_HASHES["g4"]: 98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a
```

`DecisionCardBase` and `LOCKSTEP_CHECK` import cleanly. Sandbox-AC validator passes for the story spec. T1 class-conformance baseline in this checkout is 16 parity contract files: 11 activation plus 5 decision-card shape-pins.

Dispatch caveat: the operator instructed Codex to proceed after declaring G2C and G3 reviewed/closed. Local sprint status still records G2C/G3 as `in-progress`, and the local G2C/G3 model bodies remain legacy. This G4 T1 pass proceeds under the prompt's operator (E)-elasticity override path and records the local baseline honestly.

## 1. Legacy G4Card Field Disposition

Semantic alignment verdict: the legacy G4 closeout fields fit ADR 0002's "fidelity gate" framing cleanly. `final_status`, `artifact_paths`, and `outcome_summary` describe the trial output posture at closeout, which is the point where fidelity standards are confirmed before final handoff. Unlike G3, no semantic-divergence statement or field-name compromise is required. T2 should preserve the legacy fields verbatim and add `gate_focus: Literal["fidelity_gate"]` as the post-Slab-7c family marker.

| Legacy field | Legacy source | Migrated disposition | Rationale |
| --- | --- | --- | --- |
| `gate_id` | declared on `G4Card` as `Literal["G4"]` | preserve/re-declare as `Literal["G4"]` | Discriminated-union routing, manifest dotted refs, and terminal gate dispatch depend on the `G4` discriminator. |
| `final_status` | declared on `G4Card` as `Literal["completed", "partial", "failed"]` | preserve/re-declare as the same closed three-value Literal | The final-status vocabulary is load-bearing closeout state; T2 must not widen or rename it. |
| `artifact_paths` | declared on `G4Card` as `list[str]` | preserve/re-declare with default empty list | Constructor sites pass produced artifact paths; default-empty behavior remains valid. |
| `outcome_summary` | declared on `G4Card` as `str` | preserve/re-declare with strip-then-non-empty validator | Constructor sites pass the operator-facing closeout summary. The migration ratchets whitespace-only rejection per G2A pattern without renaming the field. |

## 2. Legacy DecisionCard Base Field Disposition

Per AMELIA-P5 V6, every row carries `audit_method`. All DROP rows use `audit_method=heavy` with smoke-pass evidence against `tests/composition/`, `tests/integration/marcus/`, and `tests/integration/replay/`.

| field | disposition | audit_method | rationale |
| --- | --- | --- | --- |
| `card_id` | preserve-via-re-declaration | light | Re-declare on migrated `G4Card` as Pydantic `UUID4`; required by resume registry, operator verdicts, fixture round-trip, and persisted decision-card JSON. |
| `trial_id` | preserve-via-re-declaration | light | Re-declare on migrated `G4Card` as Pydantic `UUID4`; required by registry, digest, and trial-scoped persistence consumers. |
| `created_at` | preserve-via-re-declaration | light | Re-declare with `enforce_tz_aware`, mirroring G2A/G1; existing generic tests reject naive datetimes. |
| `drafted_proposal` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k drafted_proposal --co -q` collected 0 tests. Targeted field grep found direct reads only in G1-only tests; `pytest tests/composition/test_pre_gate_marcus_precedence_unaltered.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q --tb=short` passed 4 tests. No required-root G4 direct read exists. G4 constructor sites must stop passing this legacy common field at T2. |
| `evidence` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k evidence --co -q` collected 7 tests; execution passed 7 tests. Targeted `card.evidence` grep found direct reads only in G1-only adjacent-summary tests; `pytest tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py -q --tb=short` passed 3 tests. No required-root G4 direct read exists. G4 constructor sites must stop passing this legacy common field at T2. |
| `risks` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k risks --co -q` collected 0 tests. Targeted grep found no `card.risks` or `getattr(..., "risks")` access in the required roots. G4 constructor sites must stop passing this legacy common field at T2. |
| `verb` | preserve-via-re-declaration | light | Re-declare as closed `Literal["approve", "edit", "reject"]`; `m3_trial.py` currently emits `approve` for G4 and generic strict tests reject invalid verbs. |
| `meta` | preserve-via-base | light | Migrate to `_base.DecisionCardMeta` inherited through `DecisionCardBase`; T2 constructor sites must convert legacy meta to the base meta shape as G1 did. |
| `model_config.extra="forbid"` | preserve-via-base | light | Inherited from `DecisionCardBase`; generic strict tests expect extra-field rejection. |
| `model_config.validate_assignment=True` | preserve-via-base | light | Inherited from `DecisionCardBase`; generic strict tests expect assignment validation. |
| `model_config.frozen=False` | change to frozen via `DecisionCardBase` | light | Intentional Slab 7c pattern; new G4 shape-pin must assert mutation rejection. |

## 3. Legacy DecisionCardMeta Field Disposition

Because this section contains DROP rows, it also carries `audit_method` per governance JSON `extend_and_audit_t1_audit_method`.

| field | disposition | audit_method | rationale |
| --- | --- | --- | --- |
| `cache_state` | preserve-via-base | light | Shared metadata remains required on `_base.DecisionCardMeta`; string payloads validate through the base cache-state adapter. |
| `affected_nodes` | preserve-via-base | light | Shared metadata remains required and retains non-empty entry validation. |
| `override_trail` | preserve-via-base | light | Shared override history remains required by the 7c base metadata contract. |
| `reject_rate` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k reject_rate --co -q` collected 0 tests; targeted grep found no required-root reads. |
| `party_mode_contributions` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k party_mode_contributions --co -q` collected 0 tests; targeted grep found no required-root reads. Separate `tests/integration/gates/` tests read this field on `G-PARTY` cards, not G4. |
| `consolidated_at` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k consolidated_at --co -q` collected 0 tests; targeted grep found no required-root reads. Separate `tests/integration/gates/` tests read this field on `G-PARTY` cards, not G4. |
| `sanctum_warnings` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k sanctum_warnings --co -q` collected 0 tests; targeted grep found no required-root reads. |

## 4. New Fields Added

| New field | Source | Disposition |
| --- | --- | --- |
| `schema_version: Literal["v1"]` | FR-7c-51 | Add to migrated `G4Card` with default `"v1"` and schema emission. |
| `decision_card_digest: str` | `DecisionCardBase` | Required lowercase sha256 digest inherited from the 7c base. Constructor sites must supply it at T2. |
| `gate_focus: Literal["fidelity_gate"]` | ADR 0002 gate-family taxonomy | Add as a new closed one-value G4 family marker. Legacy G4Card has no `gate_focus`; this is an explicit contract-evolution ADD. |

## 5. Closed-Enum Tightening

`gate_id` remains `Literal["G4"]`; the effective contract stays closed and must continue rejecting non-G4 discriminator values.

`final_status` remains `Literal["completed", "partial", "failed"]`; shape-pin coverage must reject `"in_progress"`, `"unknown"`, `"COMPLETED"`, and non-string values.

`gate_focus` is added as `Literal["fidelity_gate"]`; shape-pin coverage must reject non-`fidelity_gate` values.

`schema_version` is added as `Literal["v1"]`; shape-pin coverage must reject non-v1 schema versions.

`verb` remains `Literal["approve", "edit", "reject"]`; generic per-gate strict tests continue to reject invalid verbs.

## 6. Pattern-Parity Ratchets

T2 implementation should mirror `app/models/decision_cards/g2a.py` and post-G1 `app/models/decision_cards/g1.py`:

- Use Pydantic `UUID4` for `card_id` and `trial_id`, not bare `UUID`.
- Validate UUID4 values through `enforce_uuid4_version`.
- Validate `created_at` through `enforce_tz_aware`.
- Preserve `final_status` as the closed three-value Literal.
- Keep `gate_id`, `gate_focus`, `schema_version`, and `verb` as closed Literals.
- Validate `outcome_summary` with strip-then-non-empty checks.
- Keep every field described with `Field(..., description=...)`.
- Inherit `extra="forbid"`, `validate_assignment=True`, and `frozen=True` from `DecisionCardBase`.

## 7. Net Diff Summary

Added: `schema_version`, `decision_card_digest`, `gate_focus`.

Preserved by re-declaration: `card_id`, `trial_id`, `gate_id`, `created_at`, `verb`, `final_status`, `artifact_paths`, `outcome_summary`.

Preserved by `DecisionCardBase`: strict config, frozen assignment behavior, `meta` shape, digest validation.

Dropped from G4 after heavy audit: `drafted_proposal`, `evidence`, `risks`, and legacy meta extensions `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings`.

Required T2 consumer updates:

- `app/marcus/orchestrator/production_runner.py:449` must construct G4Card without dropped legacy fields, supply `decision_card_digest`, and convert legacy `DecisionCardMeta` to `_base.DecisionCardMeta`.
- `marcus/orchestrator/m3_trial.py:185` must construct G4Card without dropped legacy fields, supply `decision_card_digest`, and convert legacy `DecisionCardMeta` to `_base.DecisionCardMeta`.
- Generic fixture/schema consumers must be refreshed through the four-file lockstep: `schema/g4.v1.schema.json`, `tests/fixtures/decision_cards/g4_golden.json`, and the new `tests/parity/test_decision_card_g4_shape.py`.

No edit is expected for the 2-class-regime substrate unless T2 verification exposes a G4-specific gap: `app/manifest/compiler.py`, `app/manifest/refs.py`, `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py`, and `app/gates/resume_api.py` already accept both legacy `DecisionCard` and new `DecisionCardBase` after G1.

## 8. T1 Baseline Evidence

Commands executed:

```text
.venv/Scripts/python.exe -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/g4.py','rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; print(FROZEN_AT_SHIP_HASHES['g4'])"
.venv/Scripts/python.exe -c "from app.models.decision_cards._base import DecisionCardBase; from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK; print(DecisionCardBase.__name__, bool(LOCKSTEP_CHECK))"
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g4-decision-card-extend-and-audit.md
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

T1 regression baseline: `870 passed, 1 failed, 18 skipped`. The sole failure is inherited governance-version drift in `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`, now expecting `2026-04-29-slab7b-twelve-stories` while the governance JSON version is `2026-05-05-amelia-p5-and-wave-3-lookahead-policy`. No G4 body file was changed before this baseline.
