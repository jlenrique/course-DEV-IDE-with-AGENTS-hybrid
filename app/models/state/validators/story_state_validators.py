"""Cross-field validators for `StoryState` (NFR-M5 four-file-lockstep).

`StoryState` invariants are field-level only in 1.2. Slab 2+ stories may
introduce cross-field checks (e.g., monotonic step_index across the
node_checkpoints list); the four-file-lockstep slot is reserved here
for that future work.
"""
