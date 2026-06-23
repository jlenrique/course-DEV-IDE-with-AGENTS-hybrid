"""P2-4b conformance-finalize RUNNER — drives the built classifier over the 14
held-out slides and scores the emitted tuples against the operator-confirmed gold.

Two layers, deliberately decoupled so the testable core needs no live classifier:

- ``load_gold(json_path)`` + ``score_emitted(emitted_by_slide, gold)`` — pure,
  unit-tested NOW with synthetic emitted tuples (no classifier import).
- ``run_live(...)`` — the post-build bridge: lazily imports the built
  classifier (S1+S2+S3), runs it over the held-out perceptions, builds emitted
  ``ReadingPathTuple``s, and scores. NOT runnable until P2-4c S1/S2/S3 are done;
  the import is lazy so importing THIS module never pulls the in-flight classifier.

Gold source: ``reading-path-holdout-gold-labels.json`` (machine mirror of the
QA-verified ``reading-path-holdout-gold-labels-2026-06-23.md``).
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
            image_role=row["image_role"],  # None | "1"|"2"|"2_5"|"3"|"4"
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
    """Score a dict of emitted tuples (by slide_id) against the gold.

    Pure + unit-testable: pass synthetic emitted tuples, no classifier needed.
    Every gold slide must have an emitted tuple (a missing emission is a hard
    error, not a silent skip — the held-out denominator is fixed at 14).
    """
    gold = gold or load_gold()
    missing = sorted(set(gold) - set(emitted_by_slide))
    if missing:
        raise ValueError(f"emitted tuples missing for held-out slides: {missing}")
    rows = [(sid, emitted_by_slide[sid], gold[sid]) for sid in gold]
    return score(rows)


def run_live(
    perceptions_summary: Path = HOLDOUT_PERCEPTIONS,
    gold_json: Path = GOLD_JSON,
) -> ScoreReport:  # pragma: no cover - requires the built S1/S2/S3 classifier
    """POST-BUILD bridge: run the built classifier over the 14 held-out
    perceptions and score vs gold.

    Lazily imports the classifier so this module is import-safe while S2/S3 are
    in flight. INTEGRATION NOTE: align the emitted-tuple extraction below with
    the final S2 dominant-image-role rule + the S3-merged tuple once the build
    lands (this is a scaffold, not yet exercised).
    """
    from app.models.perception.perception_artifact import PerceptionArtifact
    from scripts.utilities.reading_path_classifier import with_classified_reading_path

    gold = load_gold(gold_json)
    summary = json.loads(Path(perceptions_summary).read_text(encoding="utf-8"))
    emitted: dict[str, ReadingPathTuple] = {}
    for row in summary["rows"]:
        slide_id = row["slide_id"]
        if slide_id not in gold or "error" in row:
            continue
        # Reconstruct the perception artifact from the captured per-slide JSON,
        # then run the built classifier. (Per-slide JSON lives alongside the summary.)
        per_slide = (
            Path(perceptions_summary).parent / "perceptions" / f"{slide_id}.json"
        )
        artifact_dump = json.loads(per_slide.read_text(encoding="utf-8"))[
            "perception_artifact"
        ]
        classified = with_classified_reading_path(
            PerceptionArtifact.model_validate(artifact_dump)
        )
        dump = classified.model_dump()
        emitted[slide_id] = ReadingPathTuple(
            macro_layout=dump.get("macro_layout"),
            image_role=_dominant_image_role(dump.get("image_roles")),
            text_substructure=dump.get("text_substructure"),
            narration_cadence=dump.get("narration_cadence"),
            callout_intent=dump.get("callout_intent"),
            derived_primary=dump.get("reading_path"),
        )
    return score_emitted(emitted, gold)


def _dominant_image_role(image_roles: list | None) -> object:
    """Slide-level dominant scored tier from a per-element image_roles list.

    SCAFFOLD: pick the most-load-bearing present tier (3 > 2_5 > 2 > 4 > 1),
    skipping None sentinels. Align with S2's authoritative dominant-tier rule at
    integration time.
    """
    if not image_roles:
        return None
    priority = {"3": 5, "2_5": 4, "2": 3, "4": 2, "1": 1}
    present = [r for r in image_roles if r is not None]
    if not present:
        return None
    return max(present, key=lambda r: priority.get(str(r), 0))


def main() -> None:  # pragma: no cover
    report = run_live()
    for line in report.summary_lines():
        print(line)


if __name__ == "__main__":  # pragma: no cover
    main()
