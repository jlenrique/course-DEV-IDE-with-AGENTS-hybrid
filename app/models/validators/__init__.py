"""Validator companion package for `app.models` schemas (NFR-M5 four-file-lockstep).

Cross-field validator helpers for `PipelineRegistry`, `ModelSelectionPolicy`,
and other top-level model schemas live here. Models with cross-field
invariants delegate from `@model_validator(mode="after")` into module-level
functions exported from this subpackage so the cross-field logic is testable
in isolation.
"""
