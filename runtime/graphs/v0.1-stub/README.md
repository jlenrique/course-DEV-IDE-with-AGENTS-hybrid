# frozen-graph / v0.1-stub

Slab 1 substrate stub directory. Anchors the `frozen_graph_version: "v0.1-stub"`
reference in the `state/config/pipeline-manifest.yaml` stub manifest so the
compiler's frozen-graph-version existence check (Story 1.4 AC-1.4-C) has a
real directory to assert.

The full frozen-graph ceremony (manifest snapshot + dispatch-registry snapshot +
compiled-graph-digest under this directory) lands at Slab 4 Story 4.5. Until
then this directory exists purely so compile-time validation returns.

`v42` is the primary-repo equivalent directory used when the full v4.2 manifest
is migrated in Story 1.6.
