"""Cross-field validators for `PipelineRegistry` (NFR-M5 four-file-lockstep).

The default-model-must-match-an-available-entry invariant is encoded inline
in `PipelineRegistry._check_default_model_id_in_entries` for now; this file
ships a placeholder docstring documenting the lockstep slot. If the
invariant logic grows complex enough to warrant extraction (e.g., when
provider-specific availability rules land), lift it here.
"""
