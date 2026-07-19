"""Project quality-scorecard reader (leaf package).

Reads the headline numbers from ``docs/quality/project-quality-scorecard.md`` so
the production runner can stamp the current quality posture into a run's final
report, and so operator/dev tooling can surface it. Fail-soft by design: a
missing or malformed scorecard never raises into a production run.
"""

from app.quality.scorecard import did_score_ref, read_scorecard_block

__all__ = ["did_score_ref", "read_scorecard_block"]
