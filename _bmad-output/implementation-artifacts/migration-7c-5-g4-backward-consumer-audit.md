# 7c.5.G4 Backward Consumer Audit

T1 artifact for `migration-7c-5-g4-decision-card-extend-and-audit`.

## Grep Commands

Executed:

```powershell
rg -n "G4Card|g4:G4Card|decision-card-G4|decision_cards\.g4" --type=py tests app marcus scripts
rg -n "G4Card|G4" tests/composition tests/integration/marcus tests/integration/replay
rg -n "G4Card\(|gate_id=\"G4\"|gate_id == \"G4\"" tests/composition tests/integration/marcus tests/integration/replay app/marcus marcus/orchestrator
rg -n "card\.(drafted_proposal|evidence|risks)|getattr\([^\r\n]*(drafted_proposal|evidence|risks)" tests/composition tests/integration/marcus tests/integration/replay
rg -n "final_status|artifact_paths|outcome_summary" tests app marcus -g "*.py"
rg -n "party_mode_contributions|consolidated_at|reject_rate|sanctum_warnings" tests/composition tests/integration/marcus tests/integration/replay tests/integration/gates
```

## Executable Call-Site Matrix

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `app/models/decision_cards/__init__.py:24` | Flat import from `g4`. | preserved-via-existing-flat-export; no T2 edit expected unless import ordering changes. |
| `app/models/decision_cards/__init__.py:42` | `AnyDecisionCard` discriminated union includes `G4Card`. | preserved-via-re-declaration of `gate_id`; after T2 union should continue routing G4 to `G4Card`. |
| `app/models/decision_cards/__init__.py:64` | `__all__` exports `G4Card`. | preserved-via-existing-flat-export. |
| `app/models/decision_cards/g4.py:12` | Class definition currently inherits legacy `DecisionCard`. | requires-update-at-this-story; T2 migrates to `DecisionCardBase`. |
| `app/models/decision_cards/g4.py:15` | Declares `gate_id: Literal["G4"]`. | preserve/re-declare as `Literal["G4"]`. |
| `app/models/decision_cards/g4.py:19` | Declares `final_status: Literal["completed", "partial", "failed"]`. | preserve/re-declare unchanged; do not widen. |
| `app/models/decision_cards/g4.py:23` | Declares `artifact_paths: list[str]`. | preserve/re-declare unchanged with default empty list. |
| `app/models/decision_cards/g4.py:27` | Declares `outcome_summary: str`. | preserve/re-declare and ratchet to strip-then-non-empty validation. |
| `app/models/decision_cards/g4.py:33` | Module `__all__` exports `G4Card`. | preserved-via-module-export. |
| `app/marcus/orchestrator/production_runner.py:45` | Imports `G4Card` from flat package. | preserved-via-flat-export. |
| `app/marcus/orchestrator/production_runner.py:409` | Builds `common` with legacy `drafted_proposal`, `evidence`, `risks`, legacy `DecisionCardMeta`, and no `decision_card_digest`. | requires-update-at-this-story for G4 branch only. |
| `app/marcus/orchestrator/production_runner.py:449` | Constructs `G4Card(**common, final_status="partial", artifact_paths=[...], outcome_summary=...)`. | requires-update-at-this-story; remove dropped legacy fields, supply `decision_card_digest`, convert meta to `_base.DecisionCardMeta`, add `gate_focus`/`schema_version` through defaults. |
| `marcus/orchestrator/m3_trial.py:18` | Imports `DecisionCardMeta, G1Card, G2CCard, G3Card, G4Card`. | requires-update-at-this-story for the G4 branch; after T2 all legacy gate branches should be on `DecisionCardBase`, while legacy `base.py` remains in place for separate cleanup. |
| `marcus/orchestrator/m3_trial.py:143` | Return type `G1Card | G2CCard | G3Card | G4Card`. | preserved-via-G4-symbol; type union remains valid. |
| `marcus/orchestrator/m3_trial.py:152` | Builds `common` with legacy `drafted_proposal`, `evidence`, `risks`, legacy `DecisionCardMeta`, and no `decision_card_digest`. | requires-update-at-this-story for G4 branch only. |
| `marcus/orchestrator/m3_trial.py:185` | Constructs `G4Card(**common, verb="approve", final_status="completed", artifact_paths=[...], outcome_summary=...)`. | requires-update-at-this-story; remove dropped legacy fields, supply `decision_card_digest`, convert meta to `_base.DecisionCardMeta`, add `gate_focus`/`schema_version` through defaults. |
| `tests/unit/models/decision_cards/_helpers.py:10` | Imports G1/G2C/G3/G4. | preserved-via-flat-export. |
| `tests/unit/models/decision_cards/_helpers.py:26` | `GATE_MODELS` includes `("g4", G4Card)`. | preserved-via-G4-symbol; T3/T4 must regenerate `g4.v1.schema.json` and `g4_golden.json` so generic tests load the migrated shape. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:8` | Imports G1/G2C/G3/G4. | preserved-via-flat-export. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:17` | Type annotation includes `G4Card`. | preserved-via-G4-symbol. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:27` | Type annotation includes `G4Card`. | preserved-via-G4-symbol; migrated G4 must continue rejecting naive datetimes. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:38` | Type annotation includes `G4Card`. | preserved-via-G4-symbol; migrated G4 must continue rejecting invalid `gate_id`. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:49` | Type annotation includes `G4Card`. | preserved-via-G4-symbol; migrated G4 must continue rejecting invalid `verb`. |
| `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:44` | Dotted ref string `app.models.decision_cards.g4:G4Card`. | preserved-via-module-export; post-G1 2-class assertion already accepts `DecisionCard` or `DecisionCardBase`. |
| `tests/unit/models/decision_cards/test_discriminated_union_routing.py:5` | Imports `AnyDecisionCardAdapter` and `G4Card`. | preserved-via-flat-export and discriminator. |
| `tests/unit/models/decision_cards/test_discriminated_union_routing.py:16` | Type annotation includes `G4Card`; generic fixture validates through `AnyDecisionCardAdapter`. | requires T4 fixture refresh; no code update expected in this generic test. |
| `tests/integration/marcus/test_decision_card_emission_per_gate.py:8` | Parametrizes `gate_id` across G1/G2C/G3/G4 and runs `run_local_m3_trial()`. | preserved-via-m3_trial-constructor update; G4 digest emission must remain 64 chars. |
| `tests/integration/marcus/test_marcus_duality_boundary.py:71` | Asserts terminal gate set includes G4. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/integration/marcus/test_run_summary_yaml_emit.py:78` | Asserts emitted run summary terminal gate is G4. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_vera_chain.py:12` | Composition chain declares `gate_id = "G4"` and asserts replay gate id. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_irene_pass1_to_vera_g4_chain.py:16` | Composition chain declares `gate_id = "G4"` and inspects Vera G4 rubric output. | preserved-via-gate-id-string; no DecisionCard body dependency. |

## Related Non-Grep Consumers

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `app/manifest/compiler.py` | Imports `DecisionCard` and `DecisionCardBase`, then passes `(DecisionCard, DecisionCardBase)` to `resolve_dotted_ref`. | already-updated-by-G1; migrated G4 should be accepted with no new edit. |
| `app/manifest/refs.py` | `resolve_dotted_ref` accepts `expected_base_class` as a single class or tuple of classes. | already-updated-by-G1; supports the temporary 2-class regime. |
| `app/gates/resume_api.py` | Stores, digests, and registers `DecisionCard | DecisionCardBase`. | already-updated-by-G1; migrated G4 should register through the same API. |

## Required-Root Smoke Consumers

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `tests/composition/test_pre_gate_marcus_precedence_unaltered.py:28` | Reads `card.drafted_proposal["decision"]` from `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G4 preservation requirement. Executed with `test_runner_threads_pre_fill_to_decision_card.py`: 4 passed. |
| `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py:45` | Reads `card.drafted_proposal` from `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G4 preservation requirement. |
| `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py:66` | Reads default `card.drafted_proposal` from `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G4 preservation requirement. |
| `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:35` | Reads `card.evidence[-1]` from helper `_card()` that calls `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G4 preservation requirement. Executed directly: 3 passed. |
| `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:42` | Reads default `card.evidence` from helper `_card()` with `gate_id="G1"`. | G1-only live consumer; not a G4 preservation requirement. |
| `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:63` | Counts `card.evidence` specialist-summary entries from helper `_card()` with `gate_id="G1"`. | G1-only live consumer; not a G4 preservation requirement. |

## Documentation References

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `docs/operator/production-trial-playbook.md` | Historical decision-card documentation names legacy G1-G4 shapes. | deferred follow-on; covered by existing `slab-7c-g1-g4-decision-card-doc-refresh` after all extend-and-audit stories close. |
| `docs/dev-guide/sources-of-truth.md` | Names the decision-card schema package and shipped G1-G4 family. | deferred follow-on; no executable break. |
| `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` | Defines G4 as fidelity gate. | Cleanly aligns with legacy closeout fields; contract diff records this semantic fit. |

## Field-Access Summary

No audited executable site reads `G4Card.drafted_proposal`, `G4Card.evidence`, `G4Card.risks`, or legacy G4 meta extensions directly after construction.

Required-root smoke and targeted grep found live direct reads of `drafted_proposal` and `evidence`, but all direct reads construct or persist `gate_id="G1"` cards. No `G4Card(` constructor appears under `tests/composition/`, `tests/integration/marcus/`, or `tests/integration/replay/`; the only executable G4 constructors are:

- `app/marcus/orchestrator/production_runner.py:449`
- `marcus/orchestrator/m3_trial.py:185`

Those constructor payloads are the required T2 update surface: remove dropped legacy fields (`drafted_proposal`, `evidence`, `risks`), convert metadata to `_base.DecisionCardMeta`, and supply `decision_card_digest`.

Legacy G4 semantic fields are preserved:

- `final_status` remains the closed three-value Literal `completed | partial | failed`.
- `artifact_paths` remains a default-empty list of repo-relative path strings.
- `outcome_summary` remains required and is ratcheted to strip-then-non-empty validation.

2-class-regime validators are already updated by G1 and verified at T1:

- `app/manifest/compiler.py` accepts `(DecisionCard, DecisionCardBase)`.
- `app/manifest/refs.py` supports tuple base classes.
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` asserts subclassing against either base.
- `app/gates/resume_api.py` stores, digests, and registers either base regime.

T1 broad baseline is red only on an inherited governance-version assertion:

```text
870 passed, 1 failed, 18 skipped
FAILED tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]
expected governance version: 2026-04-29-slab7b-twelve-stories
actual governance version: 2026-05-05-amelia-p5-and-wave-3-lookahead-policy
```

No G4 body file was modified before this baseline.
