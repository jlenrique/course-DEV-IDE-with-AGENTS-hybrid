"""Cross-field validators for `ModelResolutionEntry` (Story 1.3 full schema).

The 1.3 full schema's invariants are field-level only (closed-enum `level`,
non-empty `resolved` + `reason`, tz-aware `timestamp`, sha256-hex
`cache_prefix_hash`). This file ships no module-level functions; the
four-file-lockstep slot is reserved for any future cross-field check that
1.4+ stories may introduce as the cascade semantics deepen.
"""
