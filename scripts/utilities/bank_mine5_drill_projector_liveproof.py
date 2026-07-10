"""Mine 5 liveproof: drill projector → non-empty Markdown under runs/<uuid>/."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.lesson_plan.drill_enrichment import (  # noqa: E402
    project_enrichment_to_drill_inputs,
)
from app.marcus.lesson_plan.drill_producer import (  # noqa: E402
    DrillProducerError,
    write_drill_artifact,
)
from app.marcus.lesson_plan.drill_spec import DrillSpec  # noqa: E402

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
        / f"mine5-drill-projector-{stamp}"
    )
    item_ev = evidence / "drill"
    item_ev.mkdir(parents=True)

    card = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    projection = project_enrichment_to_drill_inputs(card)
    out = write_drill_artifact(
        projection.spec, run_dir / "artifacts" / "drills" / "practice-drill.md"
    )
    body = out.read_text(encoding="utf-8")

    empty_proj = project_enrichment_to_drill_inputs(
        {"typed_components": [], "provisional_los": []}
    )
    empty_warned = empty_proj.empty_source and bool(empty_proj.warnings)
    empty_render_refused = False
    try:
        write_drill_artifact(empty_proj.spec, run_dir / "artifacts" / "drills" / "empty.md")
    except DrillProducerError:
        empty_render_refused = True

    # Schema round-trip
    reloaded = DrillSpec.model_validate(projection.spec.model_dump(mode="json"))

    predicates = {
        "projection_nonempty": len(projection.spec.items) >= 1,
        "kind_is_drill": projection.spec.kind == "deck-companion-drill",
        "artifact_nonempty": out.stat().st_size > 0,
        "markdown_has_prompt": "**Prompt:**" in body,
        "markdown_has_lo": "Learning objective" in body,
        "schema_roundtrip": reloaded.kind == "deck-companion-drill",
        "empty_source_warned": empty_warned,
        "empty_render_refused": empty_render_refused,
        "run_id": run_id,
        "item_count": len(projection.spec.items),
    }
    passed = all(
        predicates[k]
        for k in predicates
        if k not in {"run_id", "item_count"}
    )
    verdict = {
        "item": "drill",
        "mine": "5",
        "pass": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "stamp": stamp,
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (item_ev / "practice-drill.md").write_bytes(out.read_bytes())
    (item_ev / "drill-spec.json").write_text(
        json.dumps(projection.spec.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
