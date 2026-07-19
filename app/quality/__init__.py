"""Project quality-scorecard reader (leaf package).

Reads the headline numbers from ``docs/quality/project-quality-scorecard.md`` so
the production runner can stamp the current quality posture into a run's final
report, and so operator/dev tooling can surface it. Fail-soft by design: a
missing or malformed scorecard never raises into a production run.
"""

# Relative (intra-package) import keeps this a clean leaf: the package references
# no foreign ``app.*`` module at import time (GL-3 / NFR4).
from .scorecard import did_score_ref, dimension_ref, read_scorecard_block

__all__ = ["did_score_ref", "dimension_ref", "read_scorecard_block"]
