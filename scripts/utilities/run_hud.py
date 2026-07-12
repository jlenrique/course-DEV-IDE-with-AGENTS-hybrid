"""Run HUD — RETIRED legacy generator (Epic 35, story 35.8).

The legacy static-HTML HUD generator has been **retired**. The operator HUD is
now the runtime-owned *operator-surface projection*
(``state/config/runs/<trial_id>/operator-surface.json``) served read-only by
``app/hud/server.py`` — launched automatically by the trial start path — and
viewable via ``trial hud``.

What was deleted with this retirement (AD-8 / AD-12):

- the whole HTML rendering surface (``render_html`` / ``collect_hud_data`` /
  the ``_render_*`` panels),
- the ``scripts.utilities.hud_data_sources`` legacy data layer (deleted),
- and, critically, the **silent wrong-run fallback**: the
  ``_query_active_run_id`` (coordination.db reader) → ``_find_latest_bundle``
  (newest-mtime bundle) chain that rendered the *wrong run with no indication*
  in the April failure. That reader chain is gone from the HUD path, not
  bypassed.

What this module still exposes: **only** ``PIPELINE_STEPS`` — the
manifest-derived pipeline-step projection consumed by the L1 pipeline regime
check (``scripts/utilities/check_pipeline_manifest_lockstep.py``) and the
``tests/test_projection_equality.py`` / ``tests/test_marcus_workflow_runner_32_1.py``
lockstep pins. It is derived purely from the pipeline manifest — it reads no
coordination.db, no bundle gates, no run artifacts.

Invoking this module as a CLI prints a deprecation pointer and exits non-zero.
"""

from __future__ import annotations

import sys

from scripts.utilities.pipeline_manifest import hud_steps, load_manifest

# ---------------------------------------------------------------------------
# Pipeline step projection (manifest-derived).
# SYNC-WITH: state/config/pipeline-manifest.yaml
#
# Retained import surface. Consumed by:
#   - scripts/utilities/check_pipeline_manifest_lockstep.py  (L1 regime check)
#   - tests/test_projection_equality.py                      (lockstep pin)
#   - tests/test_marcus_workflow_runner_32_1.py              (lockstep pin)
# Nothing here touches coordination.db, bundle gates, or run.json.
# ---------------------------------------------------------------------------

PIPELINE_STEPS: list[dict[str, str]] = hud_steps(load_manifest())


# ---------------------------------------------------------------------------
# Deprecation CLI
# ---------------------------------------------------------------------------

DEPRECATION_MESSAGE = (
    "scripts.utilities.run_hud is RETIRED (Epic 35, story 35.8).\n"
    "The legacy static-HTML HUD generator no longer produces output.\n"
    "\n"
    "The operator HUD is now the runtime-owned operator-surface projection:\n"
    "  - it launches automatically with the trial start path, and\n"
    "  - you can view a run with:  python -m app.hud.server   (or:  trial hud)\n"
)

DEPRECATION_EXIT_CODE = 2


def main(argv: list[str] | None = None) -> int:
    """Print the deprecation pointer and return a non-zero exit code."""
    print(DEPRECATION_MESSAGE, file=sys.stderr)
    return DEPRECATION_EXIT_CODE


if __name__ == "__main__":
    raise SystemExit(main())
