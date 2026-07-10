"""Mine 4A liveproof: canonical layout + enrichment kind shape-pin.

Validates Tejal lesson leaf + annotated run_dir; banks evidence stamp.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.course_source.canonical_processed_source import (  # noqa: E402
    annotate_typed_components_with_kind,
    validate_canonical_tree,
    write_canonical_contract_doc,
)

TEJAL = (
    REPO
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)
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
    (run_dir / "bundle").mkdir()
    (run_dir / "bundle" / "extracted.md").write_text(
        "# Mine 4A extracted companion\n\nCanonical shape-pin liveproof.\n",
        encoding="utf-8",
    )

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine4a-canonical-shape-pin-{stamp}"
    )
    item_ev = evidence / "canonical-processed-source"
    item_ev.mkdir(parents=True)

    contract_path = (
        REPO
        / "docs"
        / "dev-guide"
        / "canonical-processed-source-structure.md"
    )
    write_canonical_contract_doc(contract_path)
    (item_ev / "canonical-processed-source-structure.md").write_bytes(
        contract_path.read_bytes()
    )

    leaf = validate_canonical_tree(TEJAL, scope="lesson_leaf")

    raw = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    # Negative: legacy enrichment without kind must fail
    (run_dir / "g0-enrichment.json").write_text(
        json.dumps(raw), encoding="utf-8"
    )
    negative_missing_kind = validate_canonical_tree(run_dir, scope="run_dir")
    negative_ok = (not negative_missing_kind.ok) and any(
        "missing required kind" in e for e in negative_missing_kind.errors
    )

    annotated = annotate_typed_components_with_kind(raw)
    (run_dir / "g0-enrichment.json").write_text(
        json.dumps(annotated, indent=2) + "\n", encoding="utf-8"
    )
    run_ok = validate_canonical_tree(run_dir, scope="run_dir")

    incomplete = REPO / "runs" / f"{run_id}-incomplete"
    incomplete.mkdir(parents=True)
    incomplete_result = validate_canonical_tree(incomplete, scope="run_dir")
    incomplete_fail_loud = not incomplete_result.ok

    predicates = {
        "lesson_leaf_ok": leaf.ok,
        "run_dir_ok_with_kind": run_ok.ok,
        "kind_counts_nonempty": bool(run_ok.kind_counts),
        "negative_missing_kind_fail_loud": negative_ok,
        "negative_incomplete_tree_fail_loud": incomplete_fail_loud,
        "contract_doc_present": contract_path.is_file(),
        "run_id": run_id,
        "kind_counts": run_ok.kind_counts,
        "leaf_errors": leaf.errors,
        "run_errors": run_ok.errors,
    }
    passed = all(
        predicates[k]
        for k in (
            "lesson_leaf_ok",
            "run_dir_ok_with_kind",
            "kind_counts_nonempty",
            "negative_missing_kind_fail_loud",
            "negative_incomplete_tree_fail_loud",
            "contract_doc_present",
        )
    )
    verdict = {
        "item": "canonical-processed-source",
        "mine": "4A",
        "pass": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "stamp": stamp,
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (item_ev / "g0-enrichment.annotated.json").write_text(
        json.dumps(annotated, indent=2) + "\n", encoding="utf-8"
    )
    (item_ev / "validation-leaf.json").write_text(
        json.dumps(leaf.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    (item_ev / "validation-run.json").write_text(
        json.dumps(run_ok.to_dict(), indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
