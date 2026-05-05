# 7c.5.G1 Backward Consumer Audit

T1 artifact for `migration-7c-5-g1-decision-card-extend-and-audit`.

## Grep Commands

Executed:

```powershell
rg -n "G1Card" --type=py
rg -n "from app\.models\.decision_cards\.g1" --type=py
rg -n "from app\.models\.decision_cards import.*G1Card" --type=py
```

## Executable Call-Site Matrix

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `app/models/decision_cards/__init__.py:20` | Flat import from `g1`. | preserved-via-existing-flat-export; no T2 edit expected unless import ordering changes. |
| `app/models/decision_cards/__init__.py:42` | `AnyDecisionCard` discriminated union includes `G1Card`. | preserved-via-re-declaration of `gate_id`; expected to continue routing. |
| `app/models/decision_cards/__init__.py:60` | `__all__` exports `G1Card`. | preserved-via-existing-flat-export. |
| `app/models/decision_cards/g1.py:12` | Class definition currently inherits legacy `DecisionCard`. | requires-update-at-this-story; T2 migrates to `DecisionCardBase`. |
| `app/models/decision_cards/g1.py:38` | Module `__all__` exports `G1Card`. | preserved-via-module-export. |
| `app/marcus/orchestrator/production_runner.py:42` | Imports `G1Card` from flat package. | preserved-via-flat-export. |
| `app/marcus/orchestrator/production_runner.py:411` | Constructs `G1Card(**common, trial_summary=..., opened_by=..., next_nodes=...)`; `common` includes legacy `drafted_proposal`, `evidence`, `risks`, legacy `DecisionCardMeta`, and lacks `decision_card_digest`. | requires-update-at-this-story; remove dropped fields for G1, supply `_base.DecisionCardMeta`, and supply `decision_card_digest`. |
| `marcus/orchestrator/m3_trial.py:18` | Imports `DecisionCardMeta, G1Card, G2CCard, G3Card, G4Card`. | requires-update-at-this-story for G1 path; temporary 2-class regime means G1 must use `_base.DecisionCardMeta` while G2C/G3/G4 remain legacy. |
| `marcus/orchestrator/m3_trial.py:134` | Return type `G1Card \| G2CCard \| G3Card \| G4Card`. | preserved-via-G1-symbol; type union remains valid. |
| `marcus/orchestrator/m3_trial.py:146` | Constructs `G1Card(**common, verb="approve", trial_summary=..., opened_by=..., next_nodes=...)`; `common` includes dropped legacy fields and lacks `decision_card_digest`. | requires-update-at-this-story; mirror production runner G1 construction fix. |
| `tests/unit/models/decision_cards/_helpers.py:10` | Imports G1/G2C/G3/G4. | preserved-via-flat-export. |
| `tests/unit/models/decision_cards/_helpers.py:23` | `GATE_MODELS` includes `("g1", G1Card)`. | preserved-via-G1-symbol; fixture/schema expectations update with new golden/schema at T3/T4. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:8` | Imports G1/G2C/G3/G4. | preserved-via-flat-export. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:17` | Type annotation includes `G1Card`. | preserved-via-G1-symbol. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:27` | Type annotation includes `G1Card`. | preserved-via-G1-symbol. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:38` | Type annotation includes `G1Card`. | preserved-via-G1-symbol. |
| `tests/unit/models/decision_cards/test_per_gate_strict.py:49` | Type annotation includes `G1Card`. | preserved-via-G1-symbol. |
| `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:41` | Dotted ref string `app.models.decision_cards.g1:G1Card`. | preserved-via-module-export, but expected-base assertion below must change. |
| `tests/unit/models/decision_cards/test_discriminated_union_routing.py:5` | Imports `AnyDecisionCardAdapter` and `G1Card`. | preserved-via-flat-export and discriminator. |
| `tests/unit/models/decision_cards/test_discriminated_union_routing.py:16` | Type annotation includes `G1Card`. | preserved-via-G1-symbol. |
| `tests/unit/marcus/test_routing_manifest_driven.py:26` | Manifest fixture uses dotted ref `app.models.decision_cards.g1:G1Card`. | preserved-via-module-export; compile validator must accept 2-class regime. |
| `tests/unit/marcus/test_routing_manifest_driven.py:50` | Asserts same dotted ref string. | preserved-via-module-export/string stability. |
| `tests/unit/gates/_helpers.py:7` | Imports legacy `DecisionCard`, legacy `DecisionCardMeta`, and `G1Card`. | requires-update-at-this-story if G1 remains in this helper; G1 no longer subclasses legacy `DecisionCard` and needs `_base.DecisionCardMeta`. |
| `tests/unit/gates/_helpers.py:12` | `sample_card()` constructs `G1Card` with legacy base fields and returns `DecisionCard`. | requires-update-at-this-story; update type, metadata, constructor payload, and digest handling or defer helper away from migrated G1. |

## Related Non-Grep Consumers Found During Audit

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `app/manifest/compiler.py:328` | `resolve_dotted_ref(..., expected_base_class=DecisionCard)` validates every decision-card schema ref as a legacy `DecisionCard` subclass. | requires-update-at-this-story; temporary 2-class regime needs validation to accept both legacy `DecisionCard` and new `DecisionCardBase`. |
| `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:47` | Test asserts every G1/G2C/G3/G4 dotted ref is a subclass of legacy `DecisionCard`. | requires-update-at-this-story; update expectation for 2-class regime while preserving G2C/G3/G4. |
| `app/gates/resume_api.py:16-79` | Registry/digest API is typed to legacy `DecisionCard`. Runtime uses `card.trial_id`, `card.gate_id`, `card.meta`, and `model_dump`. | requires-update-at-this-story if migrated G1 is registered through this API; accept a protocol/union covering G1 on `DecisionCardBase` plus legacy cards. |

## Documentation References

| Site | Observed pattern | Verdict |
| --- | --- | --- |
| `docs/operator/production-trial-playbook.md:298` | Describes decision-card schemas and names `G1Card`. | requires-deferred-followon if docs are refreshed after all G1-G4 migrations; no executable break. |
| `docs/operator/production-trial-playbook.md:371` | Describes expected `G1Card` content including legacy pipeline summary/contribution fields. | requires-deferred-followon after migrated G1 final content is accepted. |
| `docs/operator/production-trial-playbook.md:373` | Placeholder for actual G1 content shape. | requires-deferred-followon after migrated G1 final content is accepted. |
| `docs/dev-guide/sources-of-truth.md:77` | Names legacy decision card schema package and four-card family. | requires-deferred-followon; no executable break. |

## Field-Access Summary

No audited executable site reads `G1Card.drafted_proposal`, `G1Card.evidence`, `G1Card.risks`, or legacy G1 meta extensions directly after construction.

Constructor sites do pass those fields today. Those constructor payloads are the required T2 update surface:

- `app/marcus/orchestrator/production_runner.py:411`
- `marcus/orchestrator/m3_trial.py:146`
- `tests/unit/gates/_helpers.py:12`

2-class-regime validators are the required T2 compatibility update surface:

- `app/manifest/compiler.py:328`
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:47`
- `app/gates/resume_api.py:16-79` if G1 remains registered through the legacy resume API.
