"""Cross-field validators for `SanctumFingerprint` (NFR-M5 four-file-lockstep).

`SanctumFingerprint` is a frozen value object whose only invariants are
field-level (UUID4 identity + tz-aware timestamp + sha256 hex format), so
this companion validator file ships no module-level functions — the
contract is fully expressible at the field layer.

This file exists to honor NFR-M5's four-file-lockstep ("model + validator +
test + golden fixture, all in one PR") even when no cross-field check is
needed; the lockstep is structural, not load-bearing on every model.
"""
