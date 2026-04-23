"""Cross-field validators for `SpecialistEnvelope` (NFR-M5 four-file-lockstep).

`SpecialistEnvelope` invariants are field-level only in 1.2 (UUID4 request_id +
tz-aware created_at). Slab 2 specialist migrations may add cross-field
checks (e.g., specialist_id must match payload_out.specialist_id when
present); deferred to those stories rather than authored speculatively here.
"""
