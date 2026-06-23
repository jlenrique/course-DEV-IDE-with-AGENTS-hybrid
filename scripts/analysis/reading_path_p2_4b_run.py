"""P2-4b conformance-finalize runner for reading-path tuple measurement.

Two layers are deliberately decoupled so the testable core needs no live model:

- ``load_gold(json_path)`` + ``score_emitted(emitted_by_slide, gold)`` are pure
  and unit-tested with synthetic emitted tuples.
- ``run_live(...)`` lazily imports the LLM-primary tuple producer, runs it over
  captured held-out perceptions, builds emitted ``ReadingPathTuple``s, and
  scores them against the operator-confirmed gold.

Gold source: ``reading-path-holdout-gold-labels.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.analysis.reading_path_p2_4b_score import (  # noqa: E402
    ReadingPathTuple,
    ScoreReport,
    score,
)

GOLD_JSON = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "reading-path-holdout-gold-labels.json"
)
HOLDOUT_PERCEPTIONS = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "reading-path-holdout-scan"
    / "holdout-perception-summary.json"
)


def load_gold(json_path: Path = GOLD_JSON) -> dict[str, ReadingPathTuple]:
    """Load the operator-confirmed gold tuples keyed by slide_id."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    out: dict[str, ReadingPathTuple] = {}
    for row in data["gold"]:
        out[row["slide_id"]] = ReadingPathTuple(
            macro_layout=row["macro_layout"],
            image_role=row["image_role"],
            text_substructure=row.get("text_substructure"),
            narration_cadence=row.get("narration_cadence"),
            callout_intent=row.get("callout_intent"),
            derived_primary=row.get("primary"),
        )
    return out


def score_emitted(
    emitted_by_slide: dict[str, ReadingPathTuple],
    gold: dict[str, ReadingPathTuple] | None = None,
) -> ScoreReport:
    """Score emitted tuples by slide_id against the fixed gold denominator."""
    gold = gold or load_gold()
    missing = sorted(set(gold) - set(emitted_by_slide))
    if missing:
        raise ValueError(f"emitted tuples missing for held-out slides: {missing}")
    rows = [(sid, emitted_by_slide[sid], gold[sid]) for sid in gold]
    return score(rows)


def run_live(
    perceptions_summary: Path = HOLDOUT_PERCEPTIONS,
    gold_json: Path = GOLD_JSON,
) -> ScoreReport:  # pragma: no cover - requires live gpt-5.5 calls
    """Run the LLM-primary producer over held-out perceptions and score vs gold."""
    from app.models.perception.perception_artifact import PerceptionArtifact
    from scripts.utilities.reading_path_classifier import with_llm_primary_reading_path

    gold = load_gold(gold_json)
    summary = json.loads(Path(perceptions_summary).read_text(encoding="utf-8"))
    emitted: dict[str, ReadingPathTuple] = {}
    for row in summary["rows"]:
        slide_id = row["slide_id"]
        if slide_id not in gold or "error" in row:
            continue
        per_slide = Path(perceptions_summary).parent / "perceptions" / f"{slide_id}.json"
        artifact_dump = json.loads(per_slide.read_text(encoding="utf-8"))[
            "perception_artifact"
        ]
        classified = with_llm_primary_reading_path(
            PerceptionArtifact.model_validate(artifact_dump)
        )
        dump = classified.model_dump()
        emitted[slide_id] = ReadingPathTuple(
            macro_layout=dump.get("macro_layout"),
            image_role=dump.get("dominant_image_role"),
            text_substructure=dump.get("text_substructure"),
            narration_cadence=dump.get("narration_cadence"),
            callout_intent=dump.get("callout_intent"),
            derived_primary=dump.get("reading_path"),
        )
    return score_emitted(emitted, gold)


def main() -> None:  # pragma: no cover
    report = run_live()
    for line in report.summary_lines():
        print(line)


if __name__ == "__main__":  # pragma: no cover
    main()
