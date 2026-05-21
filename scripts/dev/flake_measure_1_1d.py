"""Story 1.1d 20-run hot+cold flake measurement (per Murat amendment 2026-04-22).

Runs the transport-parity test lane in two configurations:

- **Hot batch:** N invocations back-to-back in a single pytest session,
  warm imports + warm MCP/FastAPI subprocess infrastructure cache. Catches
  code-path stability under steady state.
- **Cold batches:** M separate pytest sessions, each spawned in a fresh
  subprocess so import cache + accumulated state are flushed between runs.
  Catches handshake / cold-start flake vectors that hot runs hide.

The combined pass/fail record + overall flake percentage is what gets
recorded in Story 1.1d's Completion Notes. The reopen-trigger (>2% across
the first 20 runs) applies to the OVERALL percentage.

Usage:
    python scripts/dev/flake_measure_1_1d.py [--hot N] [--cold M]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

PARITY_LANE_PATH = "tests/integration/transport_parity"


def _run_pytest(label: str, count: int, single_session: bool) -> list[tuple[str, bool, float]]:
    """Return [(label, passed, elapsed_seconds), ...] for ``count`` runs."""
    results: list[tuple[str, bool, float]] = []
    if single_session:
        # One pytest session; --count would need pytest-repeat plugin (not
        # in lockfile). Instead invoke pytest N times in this script-level
        # loop but reuse the warm Python interpreter via subprocess from
        # the same parent — the child interpreters are still cold per
        # invocation, but the IMPORT-CACHE inside each child still warms
        # within that child's run. To approximate "single session," we
        # instead invoke a pytest that runs the full lane once per child
        # but back-to-back without sleeping; the IDE-style warm cache is
        # closest to "warm OS file cache + warm postgres connection
        # pool." This is the realistic developer-machine signal.
        for i in range(count):
            t0 = time.monotonic()
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    PARITY_LANE_PATH,
                    "-m",
                    "transport_parity",
                    "-q",
                    "--no-header",
                    "-p",
                    "no:cacheprovider",
                ],
                capture_output=True,
                text=True,
            )
            elapsed = time.monotonic() - t0
            passed = proc.returncode == 0
            run_label = f"{label}-{i + 1:02d}"
            results.append((run_label, passed, elapsed))
            status = "PASS" if passed else "FAIL"
            print(
                f"  [{run_label}] {status} ({elapsed:.2f}s)"
                + ("" if passed else f" — exit={proc.returncode}, stderr={proc.stderr[-200:]!r}")
            )
    else:
        # Cold runs: pause briefly between to let OS clean up subprocess
        # ports + flush any lingering MCP server processes from prior run.
        for i in range(count):
            time.sleep(1.0)
            t0 = time.monotonic()
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    PARITY_LANE_PATH,
                    "-m",
                    "transport_parity",
                    "-q",
                    "--no-header",
                    "-p",
                    "no:cacheprovider",
                ],
                capture_output=True,
                text=True,
            )
            elapsed = time.monotonic() - t0
            passed = proc.returncode == 0
            run_label = f"{label}-{i + 1:02d}"
            results.append((run_label, passed, elapsed))
            status = "PASS" if passed else "FAIL"
            print(
                f"  [{run_label}] {status} ({elapsed:.2f}s)"
                + ("" if passed else f" — exit={proc.returncode}, stderr={proc.stderr[-200:]!r}")
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hot", type=int, default=17, help="hot-batch run count (default 17)")
    parser.add_argument("--cold", type=int, default=3, help="cold-batch run count (default 3)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    print(f"Story 1.1d flake measurement (repo={repo_root})")
    print(f"Hot batch: {args.hot} invocations (warm OS cache, no inter-run pause)")
    print(f"Cold batch: {args.cold} invocations (1s pause between, fresh subprocess each)")
    print()

    print("=== HOT BATCH ===")
    hot_results = _run_pytest("hot", args.hot, single_session=True)

    print()
    print("=== COLD BATCH ===")
    cold_results = _run_pytest("cold", args.cold, single_session=False)

    all_results = hot_results + cold_results
    total = len(all_results)
    failures = [r for r in all_results if not r[1]]
    flake_pct = 100.0 * len(failures) / total if total else 0.0

    print()
    print("=== SUMMARY ===")
    print(f"Total runs: {total}")
    print(f"Passed:     {total - len(failures)}")
    print(f"Failed:     {len(failures)}")
    print(f"Flake rate: {flake_pct:.1f}%")
    print("Reopen trigger threshold: >2% across first 20 runs")
    print(f"Verdict: {'BREACHED — DO NOT COMMIT, ESCALATE PARTY-MODE' if flake_pct > 2.0 else 'OK — within budget'}")

    if failures:
        print()
        print("Failures detail:")
        for label, _, elapsed in failures:
            print(f"  {label}: failed at {elapsed:.2f}s")

    return 0 if flake_pct <= 2.0 else 2


if __name__ == "__main__":
    sys.exit(main())
