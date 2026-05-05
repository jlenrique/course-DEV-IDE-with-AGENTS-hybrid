# 7c.5.G3 Contract Diff

T1 artifact for `migration-7c-5-g3-decision-card-extend-and-audit`.

## 0. T0 Frozen-Hash Pre-Check

Recorded and on-disk G3 pre-extension hashes match:

```text
app/models/decision_cards/g3.py sha256: bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3
FROZEN_AT_SHIP_HASHES["g3"]: bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3
```

`DecisionCardBase` and `LOCKSTEP_CHECK` import cleanly. Sandbox-AC validator passes for the story spec. T1 class-conformance baseline in this checkout is 16 parity contract files: 11 activation plus 5 decision-card shape-pins.

Predecessor status caveat: the operator declared G2C reviewed and closed for dispatch purposes, but this local checkout remains at `57b92b2` and does not contain a migrated G2C body, G2C shape-pin, or G2C close review artifact. G3 T1 proceeds under that operator dispatch authority and records baseline 16 rather than the prompt's expected "likely 17".

## 1. Legacy G3Card Field Disposition

### Semantic Alignment Statement

ADR 0002 designates G3 as the "motion-clip approval gate", while the legacy `G3Card` field names describe a mid-trial in-flight operator review: `progress_percent`, `active_node_id`, `pending_nodes`, and `operator_prompt`. T1 verdict: preserve these legacy fields verbatim for backward consumers and add `gate_focus: Literal["motion_clip_approval"]` as the post-Slab-7c family marker. This story does not rename operator-facing fields or narrow their meaning. Any operator semantic refinement between "mid-trial review" and "motion-clip approval" should be deferred to a later story after the family contract is migrated.

| Legacy field | Legacy source | Migrated disposition | Rationale |
| --- | --- | --- | --- |
| `gate_id` | declared on `G3Card` as `Literal["G3"]` | preserve/re-declare as `Literal["G3"]` | Discriminated-union routing, manifest dotted refs, and terminal gate dispatch depend on the `G3` discriminator. |
| `progress_percent` | declared on `G3Card` as `float` with `ge=0.0`, `le=100.0` | preserve/re-declare with the same Pydantic-native bounds | Legacy bounds are load-bearing and must remain `[0.0, 100.0]`; new shape-pin must cover `0.0`, `100.0`, `-0.1`, and `100.1`. |
| `active_node_id` | declared on `G3Card` as `str` with `min_length=1` | preserve/re-declare with strip-then-non-empty validator | Constructor sites pass the active manifest node. The migration tightens whitespace-only rejection per G2A pattern while preserving the non-empty contract. |
| `pending_nodes` | declared on `G3Card` as `list[str]` | preserve/re-declare with default empty list | Constructor sites pass the remaining manifest nodes; no semantic change. |
| `operator_prompt` | declared on `G3Card` as `str` | preserve/re-declare with strip-then-non-empty validator | Constructor sites pass the direct operator prompt. The migration ratchets whitespace-only rejection per G2A pattern without renaming the field. |

## 2. Legacy DecisionCard Base Field Disposition

Per AMELIA-P5 V6, every row carries `audit_method`. All DROP rows use `audit_method=heavy` with smoke-pass evidence against `tests/composition/`, `tests/integration/marcus/`, and `tests/integration/replay/`.

| field | disposition | audit_method | rationale |
| --- | --- | --- | --- |
| `card_id` | preserve-via-re-declaration | light | Re-declare on migrated `G3Card` as Pydantic `UUID4`; required by resume registry, operator verdicts, fixture round-trip, and persisted decision-card JSON. |
| `trial_id` | preserve-via-re-declaration | light | Re-declare on migrated `G3Card` as Pydantic `UUID4`; required by registry, digest, and trial-scoped persistence consumers. |
| `created_at` | preserve-via-re-declaration | light | Re-declare with `enforce_tz_aware`, mirroring G2A/G1; existing generic tests reject naive datetimes. |
| `drafted_proposal` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k drafted_proposal --co -q` collected 0 tests. Targeted field grep found direct reads only in G1-only tests; `pytest tests/composition/test_pre_gate_marcus_precedence_unaltered.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q --tb=short` passed 4 tests. No required-root G3 direct read exists. G3 constructor sites must stop passing this legacy common field at T2. |
| `evidence` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k evidence --co -q` collected 7 tests; execution passed 7 tests. Targeted `card.evidence` grep found direct reads only in G1-only adjacent-summary tests; `pytest tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py -q --tb=short` passed 3 tests. No required-root G3 direct read exists. G3 constructor sites must stop passing this legacy common field at T2. |
| `risks` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k risks --co -q` collected 0 tests. Targeted grep found no `card.risks` or `getattr(..., "risks")` access in the required roots. G3 constructor sites must stop passing this legacy common field at T2. |
| `verb` | preserve-via-re-declaration | light | Re-declare as closed `Literal["approve", "edit", "reject"]`; `m3_trial.py` currently emits `approve` for G3 and generic strict tests reject invalid verbs. |
| `meta` | preserve-via-base | light | Migrate to `_base.DecisionCardMeta` inherited through `DecisionCardBase`; T2 constructor sites must convert legacy meta to the base meta shape as G1 did. |
| `model_config.extra="forbid"` | preserve-via-base | light | Inherited from `DecisionCardBase`; generic strict tests expect extra-field rejection. |
| `model_config.validate_assignment=True` | preserve-via-base | light | Inherited from `DecisionCardBase`; generic strict tests expect assignment validation. |
| `model_config.frozen=False` | change to frozen via `DecisionCardBase` | light | Intentional Slab 7c pattern; new G3 shape-pin must assert mutation rejection. |

## 3. Legacy DecisionCardMeta Field Disposition

Because this section contains DROP rows, it also carries `audit_method` per governance JSON `extend_and_audit_t1_audit_method`.

| field | disposition | audit_method | rationale |
| --- | --- | --- | --- |
| `cache_state` | preserve-via-base | light | Shared metadata remains required on `_base.DecisionCardMeta`; string payloads validate through the base cache-state adapter. |
| `affected_nodes` | preserve-via-base | light | Shared metadata remains required and retains non-empty entry validation. |
| `override_trail` | preserve-via-base | light | Shared override history remains required by the 7c base metadata contract. |
| `reject_rate` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k reject_rate --co -q` collected 0 tests; targeted grep found no required-root reads. |
| `party_mode_contributions` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k party_mode_contributions --co -q` collected 0 tests; targeted grep found no required-root reads. Separate `tests/integration/gates/` tests read this field on `G-PARTY` cards, not G3. |
| `consolidated_at` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k consolidated_at --co -q` collected 0 tests; targeted grep found no required-root reads. Separate `tests/integration/gates/` tests read this field on `G-PARTY` cards, not G3. |
| `sanctum_warnings` | DROP | heavy | Heavy smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k sanctum_warnings --co -q` collected 0 tests; targeted grep found no required-root reads. |

## 4. New Fields Added

| New field | Source | Disposition |
| --- | --- | --- |
| `schema_version: Literal["v1"]` | FR-7c-51 | Add to migrated `G3Card` with default `"v1"` and schema emission. |
| `decision_card_digest: str` | `DecisionCardBase` | Required lowercase sha256 digest inherited from the 7c base. Constructor sites must supply it at T2. |
| `gate_focus: Literal["motion_clip_approval"]` | ADR 0002 gate-family taxonomy | Add as a new closed one-value G3 family marker. Legacy G3Card has no `gate_focus`; this is an explicit contract-evolution ADD. |

## 5. Closed-Enum Tightening

`gate_id` remains `Literal["G3"]`; the effective contract stays closed and must continue rejecting non-G3 discriminator values.

`gate_focus` is added as `Literal["motion_clip_approval"]`; shape-pin coverage must reject non-`motion_clip_approval` values.

`schema_version` is added as `Literal["v1"]`; shape-pin coverage must reject non-v1 schema versions.

`verb` remains `Literal["approve", "edit", "reject"]`; generic per-gate strict tests continue to reject invalid verbs.

## 6. Pattern-Parity Ratchets

T2 implementation should mirror `app/models/decision_cards/g2a.py` and post-G1 `app/models/decision_cards/g1.py`:

- Use Pydantic `UUID4` for `card_id` and `trial_id`, not bare `UUID`.
- Validate UUID4 values through `enforce_uuid4_version`.
- Validate `created_at` through `enforce_tz_aware`.
- Preserve `progress_percent` with `Field(..., ge=0.0, le=100.0)`.
- Keep `gate_id`, `gate_focus`, `schema_version`, and `verb` as closed Literals.
- Validate `active_node_id` and `operator_prompt` with strip-then-non-empty checks.
- Keep every field described with `Field(..., description=...)`.
- Inherit `extra="forbid"`, `validate_assignment=True`, and `frozen=True` from `DecisionCardBase`.

## 7. Net Diff Summary

Added: `schema_version`, `decision_card_digest`, `gate_focus`.

Preserved by re-declaration: `card_id`, `trial_id`, `gate_id`, `created_at`, `verb`, `progress_percent`, `active_node_id`, `pending_nodes`, `operator_prompt`.

Preserved by `DecisionCardBase`: strict config, frozen assignment behavior, `meta` shape, digest validation.

Dropped from G3 after heavy audit: `drafted_proposal`, `evidence`, `risks`, and legacy meta extensions `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings`.

Required T2 consumer updates:

- `app/marcus/orchestrator/production_runner.py:441` must construct G3Card without dropped legacy fields, supply `decision_card_digest`, and convert legacy `DecisionCardMeta` to `_base.DecisionCardMeta`.
- `marcus/orchestrator/m3_trial.py:177` must construct G3Card without dropped legacy fields, supply `decision_card_digest`, and convert legacy `DecisionCardMeta` to `_base.DecisionCardMeta`.
- Generic fixture/schema consumers must be refreshed through the four-file lockstep: `schema/g3.v1.schema.json`, `tests/fixtures/decision_cards/g3_golden.json`, and the new `tests/parity/test_decision_card_g3_shape.py`.

No edit is expected for the 2-class-regime substrate unless T2 verification exposes a G3-specific gap: `app/manifest/compiler.py`, `app/manifest/refs.py`, `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py`, and `app/gates/resume_api.py` already accept both legacy `DecisionCard` and new `DecisionCardBase` after G1.

## 8. T1 Baseline Evidence

Commands executed:

```text
.venv/Scripts/python.exe -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/g3.py','rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; print(FROZEN_AT_SHIP_HASHES['g3'])"
.venv/Scripts/python.exe -c "from app.models.decision_cards._base import DecisionCardBase; from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK; print(DecisionCardBase.__name__, bool(LOCKSTEP_CHECK))"
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g3-decision-card-extend-and-audit.md
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

T1 regression baseline: `870 passed, 1 failed, 18 skipped`. The sole failure is inherited governance-version drift in `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`, now expecting `2026-04-29-slab7b-twelve-stories` while the governance JSON version is `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` from commit `57b92b2`. No G3 body file was changed before this baseline.
