# Capability overlay — the GENERATED routing-truth Marcus reads

**Ground truth for "is it wired right now":** `state/config/capability-overlay.yaml`

That file is **GENERATED** (never hand-authored) by
`scripts/utilities/generate_capability_overlay.py`, derived mechanically from the
live substrate (pipeline manifest + dispatch-registry + on-disk not-stub check +
specialist-registry status). It classifies every specialist into a closed enum:

| state | meaning |
|---|---|
| `wired` | manifest routes to it + dispatchable + real not-stub module |
| `present-but-unrouted` | built + dispatchable, but **no manifest node routes to it** (the Tracy bug class) |
| `partial` | wired-shaped, but the registry flags a contract gap (e.g. `cd`) |
| `shelf` | a skill on disk, never dispatchable |
| `orchestrator` | `marcus` special-case (in-manifest, not a dispatched specialist) |

## Why this exists (Braid DP1 — the honesty piece)

The static `specialist-registry.yaml` `specialists:` / `personas:` maps are the
**org-chart** — who exists and how they relate. They are **NOT the routing-truth**.
A hand-authored map rots (the canonical smoking gun is the months-stale Tracy line),
and a frontier-model orchestrator reading a stale hand file **over-promises with
total confidence**. The capability overlay is the additive, machine-derived
authority for routing claims: it cannot say `wired` about something the dispatch
graph does not actually route to.

**Marcus reads the overlay as fact for capability claims.** The static registry
stays (org-chart ≠ routing-truth); the overlay is the witness for "is it wired."

A CI parity test (`tests/parity/test_capability_overlay_parity.py`) re-derives from
the live substrate and goes RED the instant the committed overlay diverges from
what the manifest routes. An adversarial over-promise probe
(`tests/marcus/test_capability_overlay_over_promise_probe.py`, G5) asserts **zero
false-`wired` claims**.

> Regenerate after any manifest / dispatch-registry / `app/specialists/` /
> registry-status change: `python -m scripts.utilities.generate_capability_overlay`

Spec: `_bmad-output/implementation-artifacts/spec-braid-s4-marcus-capability-overlay.md`
(v1 = static "is it routed" derivation; v1.1 trial-log `wired-and-proven`
tightening and 26-10 live health-pinging are deferred, NOT built here).
