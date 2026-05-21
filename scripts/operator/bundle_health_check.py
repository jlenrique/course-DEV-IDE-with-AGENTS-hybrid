"""Slab 6 trial-experience bundle health check (no live API).

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\bundle_health_check.py

Runs focused regression slices for each closed bundle story:
- 6.2: manifest dependency_map promotion (schema + compiler + runner resolution)
- 6.3: Step 02A prior-run directives
- 6.4: Irene Pass 2 authoring template (validator alignment + composition smoke + strict)
- 6.5: HUD per-step expandable summaries

Use this for pre-trial confidence checks or post-merge regression sweeps.

No live API; no operator credentials needed.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"

SLICES = [
    (
        "6.2 manifest dependency_map",
        [
            "tests/integration/manifest/test_manifest_dependencies_field.py",
            "tests/integration/marcus/test_production_runner_dependency_resolution.py",
        ],
    ),
    (
        "6.3 Step 02A prior-run directives",
        ["tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py"],
    ),
    (
        "6.4 Irene Pass 2 authoring template",
        [
            "tests/unit/specialists/irene/test_pass_2_template_strict.py",
            "tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py",
            "tests/composition/test_irene_pass_2_template_composition_smoke.py",
        ],
    ),
    (
        "6.5 HUD per-step expandable summaries",
        ["tests/unit/hud/", "tests/integration/hud/"],
    ),
    (
        "Composition substrate (6.0 anchor)",
        ["tests/composition/"],
    ),
]


def run(label: str, paths: list[str]) -> tuple[bool, str]:
    args = [str(PYTHON), "-m", "pytest", *paths, "-q", "--tb=short"]
    proc = subprocess.run(args, capture_output=True, text=True, cwd=REPO_ROOT)
    last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    return proc.returncode == 0, last_line


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    print("=" * 72)
    print("Slab 6 trial-experience bundle health check")
    print("=" * 72)
    print(f"Started: {started}")
    print()

    results: list[tuple[str, bool, str]] = []
    overall_ok = True

    for label, paths in SLICES:
        print(f"[{label}]")
        ok, last_line = run(label, paths)
        results.append((label, ok, last_line))
        if ok:
            print(f"  PASS -- {last_line}")
        else:
            print(f"  FAIL -- {last_line}")
            overall_ok = False
        print()

    finished = datetime.now(timezone.utc).isoformat()

    print("=" * 72)
    print("Summary:")
    print("=" * 72)
    for label, ok, last_line in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}: {last_line}")
    print()
    print(f"Overall: {'PASS' if overall_ok else 'FAIL'}")
    print(f"Started: {started}")
    print(f"Finished: {finished}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
