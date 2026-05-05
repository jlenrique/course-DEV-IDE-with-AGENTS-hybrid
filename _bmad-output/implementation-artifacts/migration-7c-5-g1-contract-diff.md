# 7c.5.G1 Contract Diff

T1 artifact for `migration-7c-5-g1-decision-card-extend-and-audit`.

## 1. Legacy G1Card Field Disposition

| Legacy field | Legacy source | Migrated disposition | Rationale |
| --- | --- | --- | --- |
| `card_id` | inherited from `DecisionCard` | re-declare on `G1Card` as `UUID4` | Required by operator-verdict and registry consumers; new `DecisionCardBase` does not provide this field. |
| `trial_id` | inherited from `DecisionCard` | re-declare on `G1Card` as `UUID4` | Required by registry and resume consumers; new `DecisionCardBase` does not provide this field. |
| `gate_id` | inherited string field, narrowed in `G1Card` to `Literal["G1"]` | preserve/re-declare as `Literal["G1"]` | Discriminated-union routing and manifest references depend on `G1`. |
| `created_at` | inherited from `DecisionCard` | re-declare on `G1Card` with tz-aware validator | Required by schema/golden parity and legacy construction tests; new `DecisionCardBase` does not provide this field. |
| `verb` | inherited from `DecisionCard` | re-declare on `G1Card` as closed `Literal["approve", "edit", "reject"]` | Required by operator-decision payload shape. |
| `meta` | inherited from `DecisionCard` | preserve via `DecisionCardBase.meta`, but migrate to `_base.DecisionCardMeta` | Shared 7c metadata remains required; legacy-only meta fields are dropped below. |
| `decision_card_digest` | absent | inherit from `DecisionCardBase` | Required by the new Slab 7c base contract. |
| `trial_summary` | declared on `G1Card` | preserve/re-declare with strip-then-non-empty validator | Operator-facing G1 content; constructor consumers pass it today. |
| `gate_focus` | declared on `G1Card` as `Literal["trial_open"]` | preserve/re-declare as `Literal["trial_open"]` | Shape discriminator/family marker remains stable. |
| `opened_by` | declared on `G1Card` | preserve/re-declare with strip-then-non-empty validator | Constructor consumers pass it today. |
| `next_nodes` | declared on `G1Card` | preserve/re-declare with default empty list | Constructor consumers pass it today; no legacy-specific behavior beyond list typing. |

## 2. Legacy DecisionCard Base Field Disposition

| Legacy base field/behavior | Migrated disposition | Consumer verdict |
| --- | --- | --- |
| `drafted_proposal` | drop from migrated `G1Card` | Dropped from G1 because no audited consumer reads `G1Card.drafted_proposal` directly after construction. Existing G1 constructor sites that pass it must be updated at T2. |
| `evidence` | drop from migrated `G1Card` | Dropped from G1 because no audited consumer reads `G1Card.evidence` directly after construction. Existing G1 constructor sites that pass it must be updated at T2. |
| `risks` | drop from migrated `G1Card` | Dropped from G1 because no audited consumer reads `G1Card.risks` directly after construction. Existing G1 constructor sites that pass it must be updated at T2. |
| `card_id` UUID4 enforcement | preserve via direct field + validator | New declaration mirrors G2A with `UUID4` annotation and `enforce_uuid4_version`. |
| `trial_id` UUID4 enforcement | preserve via direct field + validator | New declaration mirrors G2A with `UUID4` annotation and `enforce_uuid4_version`. |
| `created_at` tz-aware enforcement | preserve via direct field + validator | New declaration mirrors G2A with `enforce_tz_aware`. |
| `model_config.extra="forbid"` | preserve via `DecisionCardBase` | Existing strict-model assertions remain valid. |
| `model_config.validate_assignment=True` | preserve via `DecisionCardBase` | Existing strict-model assertions remain valid. |
| `model_config.frozen=False` | change to frozen via `DecisionCardBase` | Intentional 7c pattern. Shape-pin must assert frozen mutation rejection. |

## 3. Legacy DecisionCardMeta Field Disposition

| Legacy meta field | Migrated disposition | Rationale |
| --- | --- | --- |
| `cache_state` | preserve in `_base.DecisionCardMeta` as `CacheState` | Shared metadata field remains required. Existing string payloads validate through the `_base` before-validator. |
| `affected_nodes` | preserve in `_base.DecisionCardMeta` | Shared metadata field remains required. |
| `override_trail` | preserve in `_base.DecisionCardMeta` | Shared metadata field remains required. |
| `reject_rate` | drop for migrated G1 | No audited G1 consumer reads it directly. Existing G1 meta-construction helpers that pass it must be updated at T2. |
| `party_mode_contributions` | drop for migrated G1 | No audited G1 consumer reads it directly. Existing G1 production metadata builder that passes it must be updated at T2. |
| `consolidated_at` | drop for migrated G1 | No audited G1 consumer reads it directly. |
| `sanctum_warnings` | drop for migrated G1 | No audited G1 consumer reads it directly. Existing G1 production metadata builder that passes it must be updated at T2. |

## 4. New Fields Added

| New field | Source | Disposition |
| --- | --- | --- |
| `schema_version: Literal["v1"]` | FR-7c-51 | Add to migrated `G1Card` with default `"v1"` and schema emission. |
| `decision_card_digest: str` | `DecisionCardBase` | Required lowercase sha256 digest inherited from the 7c base. Constructor sites must supply it at T2. |

## 5. Closed-Enum Tightening

`gate_id` remains `Literal["G1"]`; the effective contract stays closed and should continue to reject non-G1 discriminator values.

`gate_focus` remains `Literal["trial_open"]`; the effective contract stays closed and should continue to reject non-`trial_open` values.

`schema_version` is added as `Literal["v1"]`; shape-pin coverage must reject non-v1 schema versions.

## 6. Pattern-Parity Ratchets

T2 implementation should mirror `app/models/decision_cards/g2a.py`:

- Use Pydantic `UUID4` for `card_id` and `trial_id`, not bare `UUID`.
- Validate UUID4 values through `enforce_uuid4_version`.
- Validate `created_at` through `enforce_tz_aware`.
- Validate `trial_summary` and `opened_by` with strip-then-non-empty checks.
- Keep every field described with `Field(..., description=...)`.
- Inherit `extra="forbid"`, `validate_assignment=True`, and `frozen=True` from `DecisionCardBase`.

## 7. Net Diff Summary

Added: `schema_version`, `decision_card_digest`.

Preserved by re-declaration: `card_id`, `trial_id`, `gate_id`, `gate_focus`, `created_at`, `verb`, `trial_summary`, `opened_by`, `next_nodes`.

Preserved by `DecisionCardBase`: strict config, `meta` shape, digest validation, frozen assignment behavior.

Dropped from G1: `drafted_proposal`, `evidence`, `risks`, and legacy G1 meta extensions `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings`.

Required T2 consumer updates: G1 constructor call sites must stop passing dropped legacy fields and must provide `decision_card_digest` plus `_base.DecisionCardMeta`. Manifest dotted-reference validation must accept the temporary 2-class regime while G2C/G3/G4 remain on legacy `DecisionCard`.
