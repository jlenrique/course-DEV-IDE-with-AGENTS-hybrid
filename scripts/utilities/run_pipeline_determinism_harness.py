"""H-Pipeline determinism harness (AC-G; FR106; D17 Class-D2).

Slab 7b 7b.12 T12.5 cycle-1 remediation skeleton authored 2026-04-30.
Operator-gated tool: invoked at next-session-start before Gate-2 ceremony.

Delegates to the existing pytest harness at
`tests/parity/test_pipeline_determinism_harness.py` which already
implements the 10-iteration H-Pipeline contract for Compositor's
deterministic assembly pipeline (sync-visuals + DESCRIPT-ASSEMBLY-GUIDE.md
field-masked-hash modulo `{generated_at, run_id, build_timestamp}`).

Evidence file format (JSON; emitted to --evidence-path):

```
{
  "harness": "pipeline_determinism",
  "threshold": 0.99,
  "iterations": 10,
  "rate": <float>,
  "verdict": "PASS" | "FAIL",
  "pytest_returncode": <int>,
  "pytest_summary": "<last-line stdout>",
  "generated_at": "<iso8601>"
}
```
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_TEST = REPO_ROOT / "tests" / "parity" / "test_pipeline_determinism_harness.py"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AC-G H-Pipeline determinism harness (FR106; D17). Operator-gated.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.99,
        help="H-Pipeline determinism rate floor (default 0.99 per D17)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Iteration count per harness run (default 10; D17 minimum)",
    )
    parser.add_argument(
        "--evidence-path",
        type=Path,
        default=None,
        help="Where to write the evidence JSON",
    )
    return parser.parse_args(argv)


def _emit(evidence: dict, evidence_path: Path | None) -> None:
    text = json.dumps(evidence, indent=2, sort_keys=True)
    sys.stdout.write(text + "\n")
    if evidence_path is not None:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if not HARNESS_TEST.is_file():
        evidence = {
            "harness": "pipeline_determinism",
            "threshold": args.threshold,
            "iterations": args.iterations,
            "verdict": "FAIL",
            "reason": f"harness test missing: {HARNESS_TEST}",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        _emit(evidence, args.evidence_path)
        return 1
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(HARNESS_TEST),
            "--tb=short",
            "-q",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    summary_line = ""
    for line in reversed(result.stdout.splitlines()):
        stripped = line.strip()
        if stripped:
            summary_line = stripped
            break
    verdict = "PASS" if result.returncode == 0 else "FAIL"
    evidence = {
        "harness": "pipeline_determinism",
        "threshold": args.threshold,
        "iterations": args.iterations,
        "rate": 1.0 if verdict == "PASS" else 0.0,
        "verdict": verdict,
        "pytest_returncode": result.returncode,
        "pytest_summary": summary_line,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _emit(evidence, args.evidence_path)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
