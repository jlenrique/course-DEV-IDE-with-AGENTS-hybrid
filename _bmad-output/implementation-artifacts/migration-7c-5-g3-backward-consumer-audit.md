# 7c.5.G3 Backward Consumer Audit

T1 artifact for `migration-7c-5-g3-decision-card-extend-and-audit`.

## Grep Commands

Executed:

```powershell
rg -n "G3Card|g3:G3Card|decision_cards\.g3|G3" --type=py
rg -n "G3Card|g3:G3Card|decision-card-G3|decision_cards\.g3" --type=py tests app marcus scripts
rg -n "G3Card|G3" tests/composition tests/integration/marcus tests/integration/replay
rg -n "G3Card\(|gate_id=\"G3\"|gate_id == \"G3\"" tests/composition tests/integration/marcus tests/integration/replay app/marcus marcus/orchestrator
rg -n "card\.(drafted_proposal|evidence|risks)|getattr\([^\r\n]*(drafted_proposal|evidence|risks)" tests/composition tests/integration/marcus tests/integration/replay
rg -n "progress_percent|active_node_id|pending_nodes|operator_prompt" tests app marcus -g "*.py"
rg -n "party_mode_contributions|consolidated_at|reject_rate|sanctum_warnings" tests/composition tests/integration/marcus tests/integration/replay tests/integration/gates
```

## Executable Call-Site Matrix

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `app/models/decision_cards/__init__.py:23` | Flat import from `g3`. | preserved-via-existing-flat-export; no T2 edit expected unless import ordering changes. |
| `app/models/decision_cards/__init__.py:42` | `AnyDecisionCard` discriminated union includes `G3Card`. | preserved-via-re-declaration of `gate_id`; after T2 union should continue routing G3 to `G3Card`. |
| `app/models/decision_cards/__init__.py:63` | `__all__` exports `G3Card`. | preserved-via-existing-flat-export. |
| `app/models/decision_cards/g3.py:12` | Class definition currently inherits legacy `DecisionCard`. | requires-update-at-this-story; T2 migrates to `DecisionCardBase`. |
| `app/models/decision_cards/g3.py:15` | Declares `gate_id: Literal["G3"]`. | preserve/re-declare as `Literal["G3"]`. |
| `app/models/decision_cards/g3.py:19` | Declares `progress_percent: float` with bounds `ge=0.0`, `le=100.0`. | preserve/re-declare bounds exactly; shape-pin must cover boundary accept/reject cases. |
| `app/models/decision_cards/g3.py:25` | Declares `active_node_id: str` with `min_length=1`. | preserve/re-declare and ratchet to strip-then-non-empty validation. |
| `app/models/decision_cards/g3.py:30` | Declares `pending_nodes: list[str]`. | preserve/re-declare unchanged. |
| `app/models/decision_cards/g3.py:34` | Declares `operator_prompt: str`. | preserve/re-declare and ratchet to strip-then-non-empty validation. |
| `app/models/decision_cards/g3.py:40` | Module `__all__` exports `G3Card`. | preserved-via-module-export. |
| `app/marcus/orchestrator/production_runner.py:44` | Imports `G3Card` from flat package. | preserved-via-flat-export. |
| `app/marcus/orchestrator/production_runner.py:409` | Builds `common` with legacy `drafted_proposal`, `evidence`, `risks`, legacy `DecisionCardMeta`, and no `decision_card_digest`. | requires-update-at-this-story for G3 branch only. |
| `app/marcus/orchestrator/production_runner.py:441` | Constructs `G3Card(**common, progress_percent=50.0, active_node_id=node_id, pending_nodes=pending_nodes, operator_prompt=...)`. | requires-update-at-this-story; remove dropped legacy fields, supply `decision_card_digest`, convert meta to `_base.DecisionCardMeta`, add `gate_focus`/`schema_version` through defaults. |
| `marcus/orchestrator/m3_trial.py:18` | Imports `DecisionCardMeta, G1Card, G2CCard, G3Card, G4Card`. | requires-update-at-this-story for the G3 branch; temporary 2-class regime means G1/G3 use `_base.DecisionCardMeta` while G4 remains legacy until its story. |
| `marcus/orchestrator/m3_trial.py:143` | Return type `G1Card | G2CCard | G3Card | G4Card`. | preserved-via-G3-symbol; type union remains valid. |
| `marcus/orchestrator/m3_trial.py:152` | Builds `common` with legacy `drafted_proposal`, `evidence`, `risks`, legacy `DecisionCardMeta`, and no `decision_card_digest`. | requires-update-at-this-story for G3 branch only. |
| `marcus/orchestrator/m3_trial.py:177` | Constructs `G3Card(**common, verb="approve", progress_percent=72.0, active_node_id=node_id, pending_nodes=..., operator_prompt=...)`. | requires-update-at-this-story; remove dropped legacy fields, supply `decision_card_digest`, convert meta to `_base.DecisionCardMeta`, add `gate_focus`/`schema_version` through defaults. |
| `tests/unit/models/decision_cards/_helpers.py:10` | Imports G1/G2C/G3/G4. | preserved-via-flat-export. |
| `tests/unit/models/decision_cards/_helpers.py:25` | `GATE_MODELS` includes `("g3", G3Card)`. | preserved-via-G3-symbol; T3/T4 must regenerate `g3.v1.schema.json` and `g3_golden.json` so generic tests load the migrated shape. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:8` | Imports G1/G2C/G3/G4. | preserved-via-flat-export. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:17` | Type annotation includes `G3Card`. | preserved-via-G3-symbol. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:27` | Type annotation includes `G3Card`. | preserved-via-G3-symbol; migrated G3 must continue rejecting naive datetimes. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:38` | Type annotation includes `G3Card`. | preserved-via-G3-symbol; migrated G3 must continue rejecting invalid `gate_id`. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:49` | Type annotation includes `G3Card`. | preserved-via-G3-symbol; migrated G3 must continue rejecting invalid `verb`. |
| `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:43` | Dotted ref string `app.models.decision_cards.g3:G3Card`. | preserved-via-module-export; post-G1 2-class assertion already accepts `DecisionCard` or `DecisionCardBase`. |
| `tests/unit/models/decision_cards/test_discriminated_union_routing.py:5` | Imports `AnyDecisionCardAdapter` and `G3Card`. | preserved-via-flat-export and discriminator. |
| `tests/unit/models/decision_cards/test_discriminated_union_routing.py:16` | Type annotation includes `G3Card`; generic fixture validates through `AnyDecisionCardAdapter`. | requires T4 fixture refresh; no code update expected in this generic test. |
| `tests/integration/marcus/test_decision_card_emission_per_gate.py:8` | Parametrizes `gate_id` across G1/G2C/G3/G4 and runs `run_local_m3_trial()`. | preserved-via-m3_trial-constructor update; G3 digest emission must remain 64 chars. |
| `tests/integration/marcus/test_calibration_tripwire.py:56` | Uses `gate_id="G3"` for calibration tripwire events. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/integration/marcus/test_marcus_duality_boundary.py:62` | Emits run summary with `terminal_gate="G3"`. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_gary_to_vera_g3_chain.py:13` | Composition chain declares `gate_id = "G3"`. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_compositor_4_input_chain.py:14` | Composition chain declares `gate_id = "G3"`. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_kira_to_compositor_chain.py:13` | Composition chain declares `gate_id = "G3"`. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_wanda_to_compositor_chain.py:13` | Composition chain declares `gate_id = "G3"`. | preserved-via-gate-id-string; no DecisionCard body dependency. |
| `tests/composition/test_enrique_to_compositor_chain.py:13` | Composition chain declares `gate_id = "G3"`. | preserved-via-gate-id-string; no DecisionCard body dependency. |

## Related Non-Grep Consumers

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `app/manifest/compiler.py:324` | Imports `DecisionCard` and `DecisionCardBase`, then passes `(DecisionCard, DecisionCardBase)` to `resolve_dotted_ref`. | already-updated-by-G1; migrated G3 should be accepted with no new edit. |
| `app/manifest/refs.py:10` | `resolve_dotted_ref` accepts `expected_base_class` as a single class or tuple of classes. | already-updated-by-G1; supports the temporary 2-class regime. |
| `app/gates/resume_api.py:18` | Imports both `DecisionCard` and `DecisionCardBase`. | already-updated-by-G1; migrated G3 should register through the same API. |
| `app/gates/resume_api.py:23` | `StoredDecisionCard.card` is typed as `DecisionCard | DecisionCardBase`. | already-updated-by-G1; no G3-specific edit expected. |
| `app/gates/resume_api.py:42` | `compute_decision_card_digest` accepts `DecisionCard | DecisionCardBase`. | already-updated-by-G1; no G3-specific edit expected. |
| `app/gates/resume_api.py:58` | `register_decision_card` accepts `DecisionCard | DecisionCardBase`. | already-updated-by-G1; no G3-specific edit expected. |

## Required-Root Smoke Consumers

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `tests/composition/test_pre_gate_marcus_precedence_unaltered.py:28` | Reads `card.drafted_proposal["decision"]` from `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G3 preservation requirement. Executed with `test_runner_threads_pre_fill_to_decision_card.py`: 4 passed. |
| `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py:45` | Reads `card.drafted_proposal` from `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G3 preservation requirement. |
| `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py:66` | Reads default `card.drafted_proposal` from `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G3 preservation requirement. |
| `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py:97` | Reads persisted `decision-card-G1.json` drafted proposal. | G1-only persistence consumer; not a G3 preservation requirement. |
| `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:35` | Reads `card.evidence[-1]` from helper `_card()` that calls `_build_decision_card(gate_id="G1", ...)`. | G1-only live consumer; not a G3 preservation requirement. Executed directly: 3 passed. |
| `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:42` | Reads default `card.evidence` from helper `_card()` with `gate_id="G1"`. | G1-only live consumer; not a G3 preservation requirement. |
| `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:63` | Counts `card.evidence` specialist-summary entries from helper `_card()` with `gate_id="G1"`. | G1-only live consumer; not a G3 preservation requirement. |

## Documentation References

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `docs/operator/production-trial-playbook.md` | Historical decision-card documentation names legacy G1-G4 shapes. | deferred follow-on; covered by existing `slab-7c-g1-g4-decision-card-doc-refresh` after all extend-and-audit stories close. |
| `docs/dev-guide/sources-of-truth.md` | Names the decision-card schema package and shipped G1-G4 family. | deferred follow-on; no executable break. |
| `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md:50` | Defines G3 as motion-clip approval gate. | T1 contract diff resolves semantic alignment by preserving legacy mid-trial fields and adding `gate_focus="motion_clip_approval"`. |

## Field-Access Summary

No audited executable site reads `G3Card.drafted_proposal`, `G3Card.evidence`, `G3Card.risks`, or legacy G3 meta extensions directly after construction.

Required-root smoke and targeted grep found live direct reads of `drafted_proposal` and `evidence`, but all direct reads construct or persist `gate_id="G1"` cards. No `G3Card(` constructor appears under `tests/composition/`, `tests/integration/marcus/`, or `tests/integration/replay/`; the only executable G3 constructors are:

- `app/marcus/orchestrator/production_runner.py:441`
- `marcus/orchestrator/m3_trial.py:177`

Those constructor payloads are the required T2 update surface: remove dropped legacy fields (`drafted_proposal`, `evidence`, `risks`), convert metadata to `_base.DecisionCardMeta`, and supply `decision_card_digest`.

Legacy G3 semantic fields are preserved:

- `progress_percent` remains bounded `[0.0, 100.0]`.
- `active_node_id` remains required and is ratcheted to strip-then-non-empty validation.
- `pending_nodes` remains a default-empty list.
- `operator_prompt` remains required and is ratcheted to strip-then-non-empty validation.

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

No G3 body file was modified before this baseline.
