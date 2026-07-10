"""Mine-next N3 liveproof: quiz projector → non-empty Markdown under runs/<uuid>/."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.lesson_plan.quiz_enrichment import (  # noqa: E402
    project_enrichment_to_quiz_inputs,
)
from app.marcus.lesson_plan.quiz_producer import (  # noqa: E402
    QuizProducerError,
    write_quiz_artifact,
)
from app.marcus.lesson_plan.quiz_spec import QuizSpec  # noqa: E402

SAMPLE_ENRICHMENT = (
    REPO
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "coverage-reprove-covered-faithful-20260630T193322Z"
    / "g0-enrichment.json"
)


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine-next-n3-quiz-projector-{stamp}"
    )
    item_ev = evidence / "quiz"
    item_ev.mkdir(parents=True)

    card = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    projection = project_enrichment_to_quiz_inputs(card)
    out = write_quiz_artifact(
        projection.spec, run_dir / "artifacts" / "quizzes" / "practice-quiz.md"
    )
    body = out.read_text(encoding="utf-8")

    empty_proj = project_enrichment_to_quiz_inputs(
        {"typed_components": [], "provisional_los": []}
    )
    empty_warned = empty_proj.empty_source and bool(empty_proj.warnings)
    empty_render_refused = False
    try:
        write_quiz_artifact(empty_proj.spec, run_dir / "artifacts" / "quizzes" / "empty.md")
    except QuizProducerError:
        empty_render_refused = True

    reloaded = QuizSpec.model_validate(projection.spec.model_dump(mode="json"))

    predicates = {
        "projection_nonempty": len(projection.spec.items) >= 1,
        "kind_is_quiz": projection.spec.kind == "deck-companion-quiz",
        "artifact_nonempty": out.stat().st_size > 0,
        "markdown_has_prompt": "**Prompt:**" in body,
        "markdown_has_lo": "Learning objective" in body,
        "markdown_has_focus": "Expected answer focus" in body,
        "not_drill_kind": "deck-companion-drill" not in body,
        "schema_roundtrip": reloaded.kind == "deck-companion-quiz",
        "empty_source_warned": empty_warned,
        "empty_render_refused": empty_render_refused,
        "run_id": run_id,
        "item_count": len(projection.spec.items),
    }
    passed = all(
        predicates[k]
        for k in (
            "projection_nonempty",
            "kind_is_quiz",
            "artifact_nonempty",
            "markdown_has_prompt",
            "markdown_has_lo",
            "markdown_has_focus",
            "not_drill_kind",
            "schema_roundtrip",
            "empty_source_warned",
            "empty_render_refused",
        )
    )

    verdict = {
        "lane": "N3",
        "name": "quiz-projector",
        "passed": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "artifact": str(out),
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item_ev / "command-transcript.md").write_text(
        f"# N3 quiz projector liveproof\n\nrun_id={run_id}\npassed={passed}\n",
        encoding="utf-8",
    )
    (item_ev / "PROOF.md").write_text(
        f"# PROOF N3\n\n- kind=deck-companion-quiz\n- items={predicates['item_count']}\n"
        f"- empty refused={empty_render_refused}\n- PASS={passed}\n",
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
