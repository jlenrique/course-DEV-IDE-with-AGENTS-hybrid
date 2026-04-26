# Frozen-Graph-Version Ceremony

Frozen graph versions are audit artifacts, not scratch space. The directory
under `runtime/graphs/v{N}/` records the exact manifest, dispatch registry,
pack version, and compiled-graph digest that a shipped topology binds to.

## Tier-1 Patch

Tier-1 covers prose or connective-tissue edits that do not change topology,
dispatch shape, or gate semantics. These proceed under dev-agent authority.
No frozen-graph version bump occurs; the active version stays `v42`.

## Tier-2 Minor

Tier-2 covers architectural-but-additive changes: a new step, a new edge
kind, a new gate position, or a new dispatch edge. These require
single-gate party-mode consensus and bump the frozen version from `v42` to
`v42.1`. The prior `v42/` directory stays frozen on disk for audit.

## Tier-3 Major

Tier-3 covers structural reshapes: a new pack family, a palette restructure,
or a new manifest-schema top-level section. These require full party-mode
consensus plus operator sign-off and bump the frozen version from `v42` to
`v43`. Both versions remain on disk.

## Worked Example: v42 to v42.1

If the manifest gains a new additive node or edge but the workflow family is
still the same, open a governance story, secure party-mode consensus, copy
the prior frozen directory forward, regenerate the five required artifacts,
and write the new digest under `runtime/graphs/v42.1/`.

## Worked Example: v42 to v43

If the workflow family changes in a way that would confuse a `v42` operator
or invalidate `v42` replay semantics, treat it as a new major graph family.
Open a scoped governance story, secure full party-mode consensus plus
operator sign-off, author the new `runtime/graphs/v43/` directory, and
preserve `v42/` unchanged for audit.

## Rollback

Rollback never mutates a frozen directory in place. Re-point the active run
configuration to the prior frozen version, verify the corresponding manifest
and dispatch snapshots still exist, and re-run the digest check before the
next tracked trial. Any rollback that also changes structure opens a new
governance story rather than editing the frozen version directly.
