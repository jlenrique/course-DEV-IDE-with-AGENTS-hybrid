"""Mine-next N6 liveproof: corrupt run.json fails loud; absent is None."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.lesson_plan.workbook_enrichment import (  # noqa: E402
    RunEnvelopeCorruptError,
    load_run_envelope,
)


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine-next-n6-corrupt-envelope-{stamp}"
    )
    item_ev = evidence / "corrupt-envelope"
    item_ev.mkdir(parents=True)

    absent_ok = load_run_envelope(run_dir) is None

    corrupt_path = run_dir / "corrupt-case"
    corrupt_path.mkdir()
    (corrupt_path / "run.json").write_text("{ torn envelope", encoding="utf-8")
    corrupt_raised = False
    try:
        load_run_envelope(corrupt_path)
    except RunEnvelopeCorruptError as exc:
        corrupt_raised = "corrupt" in str(exc).lower()

    invalid_path = run_dir / "invalid-schema"
    invalid_path.mkdir()
    (invalid_path / "run.json").write_text(
        '{"status":"completed","bogus":true}\n', encoding="utf-8"
    )
    invalid_raised = False
    try:
        load_run_envelope(invalid_path)
    except RunEnvelopeCorruptError:
        invalid_raised = True

    # Negative: corrupt must NOT silently return None
    silent_none = False
    try:
        result = load_run_envelope(corrupt_path)
        silent_none = result is None
    except RunEnvelopeCorruptError:
        silent_none = False

    predicates = {
        "absent_returns_none": absent_ok,
        "corrupt_raises": corrupt_raised,
        "invalid_schema_raises": invalid_raised,
        "corrupt_not_silent_none": not silent_none and corrupt_raised,
        "run_id": run_id,
    }
    passed = all(
        predicates[k]
        for k in (
            "absent_returns_none",
            "corrupt_raises",
            "invalid_schema_raises",
            "corrupt_not_silent_none",
        )
    )

    verdict = {
        "lane": "N6",
        "name": "run-envelope-corrupt-vs-absent-fail-loud",
        "passed": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item_ev / "command-transcript.md").write_text(
        f"# N6 corrupt-envelope liveproof\n\nrun_id={run_id}\npassed={passed}\n",
        encoding="utf-8",
    )
    (item_ev / "PROOF.md").write_text(
        "# PROOF N6\n\n- absent → None\n- corrupt JSON → RunEnvelopeCorruptError\n"
        f"- invalid schema → RunEnvelopeCorruptError\n- PASS={passed}\n",
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
