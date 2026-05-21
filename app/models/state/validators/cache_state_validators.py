"""Cross-field validators for `CacheState` (NFR-M5 four-file-lockstep).

`CacheState` invariants are field-level only in 1.2 (cache_prefix
non-empty, entries_count ≥ 0, optional tz-aware invalidation timestamp).
Story 1.3 may add cross-field invariants when the model-resolution
cascade wires the cache-prefix-hash relationship; until then this file
ships no module-level functions.
"""
