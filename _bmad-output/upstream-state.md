# Upstream State

- Migration verdict: `SHIP-CONDITIONAL`
- Operator acceptance date: `2026-04-26`
- Conditional window expiry: `2026-05-03`
- Primary repo posture: frozen reference only
- Frozen reference anchor: `upstream/master @ 3ed7c56`
- Backport posture: FR60 remains closed
- Forward-port posture: FR61 may proceed only within the bounded claim set proven by Slab 5a while the conditional window remains open
- Demotion rule: if the 2026-05-03 window lapses unresolved, `migration-master-status` demotes from `shipped` to `iterate-pending`

## Open Conditions

1. M2 Wondercraft live artifact/operator addendum still pending.
2. M3 Texas live retrieval operator window still pending.
3. Story 5a.2 still proves control-plane parity only; a real production clone-launch equivalence pass is still owed.
4. `slab-3-m5-dispatch-registry-swap` remains open because the dispatch registry is still `_status: interim`.
