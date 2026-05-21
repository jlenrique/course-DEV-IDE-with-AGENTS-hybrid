# Parity Test Layout

## FR105 + Errata 4 layout decision

**VERDICT:** flat naming is canonical for per-specialist activation contract
tests. Per-specialist files live at `tests/parity/` top level using
`test_<specialist_name>_activation_contract.py`.

Do not create `tests/parity/per_specialist/` for Slab 7b parity tests.

**Rationale:** flat naming follows the existing `tests/parity/` convention,
embraces boring technology per Winston's recommendation, and avoids extra
import-graph complexity for class-shaped parity helpers.

**Ratified at:** Story 7b.1 T1, commit `<this-commit-sha>`.

**Inventory follow-on:** `fr105-tests-parity-per-specialist-subdir-decision`
is CLOSED at Story 7b.1 T1 with verdict-flat.
