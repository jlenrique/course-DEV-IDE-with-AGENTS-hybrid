"""Cross-field validators for `ModelSelectionPolicy` (NFR-M5 four-file-lockstep).

The "no silent conflicts" invariant is encoded inline in
`ModelSelectionPolicy._check_no_silent_conflicts` for now; this file ships
a placeholder docstring documenting the lockstep slot. Future Slab 2+
selector enhancements (e.g., per-context-key conflict matrix) can lift the
logic here if it grows beyond the current pair-comparison shape.
"""
