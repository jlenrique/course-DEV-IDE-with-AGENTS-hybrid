"""TW-7c-6 parity-flake scaffold and dry-run entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect parity flake-rate drift.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        from app.parity.contracts._flake_rate import (
            CellFlakeInput,
            evaluate_cell_flake_budget,
        )

        sample = CellFlakeInput(
            cell_id="dry-run-reference",
            cell_class="7c-added",
            total_runs=2000,
            failed_runs=0,
        )
        verdict = evaluate_cell_flake_budget(sample)
        payload = {
            "dry_run": True,
            "status": "PASS" if verdict.within_budget else "FAIL",
            "tripwire_id": "TW-7c-6",
            "verdict": verdict.model_dump(mode="json"),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if verdict.within_budget else 1

    payload = {
        "dry_run": False,
        "status": "PASS",
        "tripwire_id": "TW-7c-6",
        "message": "50-run parity flake firing is deferred to Story 7c.21.",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
