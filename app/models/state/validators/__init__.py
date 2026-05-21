"""Cross-field validator helpers for `app.models.state` (NFR-M5 four-file-lockstep).

Per NFR-M5, every Pydantic model in this state package ships with a
companion validator file in this subpackage. The validator file holds
module-level functions that the model's ``@model_validator(mode="after")``
calls into — keeping the cross-field logic testable in isolation while
preserving Pydantic v2's "validators must live on the class" requirement.

For models without cross-field invariants (e.g., `CacheState`,
`SpecialistEnvelope`, `StoryState`, `ModelResolutionEntry`), the validator
file ships a placeholder docstring that documents the lockstep contract
and leaves the function set empty. The lockstep is "the file exists in
the same PR as the model," not "the file has non-trivial code."
"""
