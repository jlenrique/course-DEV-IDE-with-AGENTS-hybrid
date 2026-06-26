"""workbook_producer consumed-payload contract (Ratchet-D vocabulary).

Published 07W (composition-catalog B3, 2026-06-26): the deterministic in-graph
companion-workbook producer is a TERMINAL sidecar that SELF-RESOLVES its inputs
from the RUN DIR (segment manifest, corpus, assessments are on disk by node 15)
via ``state.run_id`` — it does NOT receive them as payload projections. The
former ``segment_manifest from irene`` projection failed live (irene emits no
such STATE key; the manifest is a disk artifact from the storyboard publisher),
so 07W carries a single resolvable TRIGGER dependency instead. The keys this
producer actually reads from the dispatched payload:

- ``upstream_output`` — the whole-dict trigger dependency (manifest declares
  ``dependencies: {upstream_output: compositor}``); the _act IGNORES its content
  (it self-resolves from the run dir) — it only needs the edge to resolve so 07W
  is dispatched after the pipeline. Mirrors the kira/motion ``upstream_output``
  idiom.
- ``run_dir`` — explicit run-directory override (dev/replay seam); when absent the
  producer resolves ``RUNS_ROOT / run_id`` from RunState.
- ``output_root`` — explicit output-root override (dev/replay seam); defaults to
  ``_bmad-output/artifacts/workbooks``.

(The segment manifest, lesson plan, and corpus are read from the run dir on disk,
NOT projected into the payload — so they are not consumed-payload keys.)
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "output_root",
        "run_dir",
        "upstream_output",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
