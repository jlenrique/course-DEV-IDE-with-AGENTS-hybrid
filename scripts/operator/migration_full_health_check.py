"""Migration full health check (no live API).

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\migration_full_health_check.py

Comprehensive non-live regression across the entire migrated substrate:
- Slab 6.0 substrate (envelope + adapter + composition discipline)
- Slab 6.1 production runner (non-live slices)
- Slab 6.2 manifest dependency_map
- Slab 6.3 / 6.4 / 6.5 trial-experience bundle
- Specialist isolation invariants (all 14 specialists)
- Composition smoke + chain tests
- Pipeline manifest lockstep

Use this before:
- First tracked trial run
- Major substrate changes
- Migration project status checks (ship-state confidence)

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
    ("Slab 6.0 substrate (envelope + adapter + composition)", ["tests/composition/"]),
    ("Slab 6.1 production runner (non-live)", ["tests/integration/marcus/test_production_runner_invocation.py", "tests/integration/marcus/test_production_runner_gate_pause_resume.py", "tests/integration/marcus/test_production_clone_launch_evidence_discipline.py"]),
    ("Slab 6.2 manifest dependencies", ["tests/integration/manifest/test_manifest_dependencies_field.py", "tests/integration/marcus/test_production_runner_dependency_resolution.py"]),
    ("Slab 6.3 Step 02A prior-run directives", ["tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py"]),
    ("Slab 6.4 Irene Pass 2 authoring template", ["tests/unit/specialists/irene/test_pass_2_template_strict.py", "tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py"]),
    ("Slab 6.5 HUD per-step summaries", ["tests/unit/hud/", "tests/integration/hud/"]),
    ("Specialist isolation (all 14)", ["tests/composition/test_specialist_isolation_preserved.py"]),
    ("ProductionEnvelope strict", ["tests/unit/runtime/test_production_envelope_strict.py"]),
    ("ProductionDispatchAdapter", ["tests/integration/marcus/test_dispatch_adapter.py"]),
    ("Manifest compiler real dispatch", ["tests/integration/manifest/test_compiler_real_dispatch.py"]),
]

PIPELINE_LOCKSTEP = ("Pipeline manifest lockstep (both invocation forms per AC-6.5-G)", [
    [str(PYTHON), "-m", "scripts.utilities.check_pipeline_manifest_lockstep"],
    [str(PYTHON), "scripts/utilities/check_pipeline_manifest_lockstep.py"],
])


def run_pytest(label: str, paths: list[str]) -> tuple[bool, str]:
    args = [str(PYTHON), "-m", "pytest", *paths, "-q", "--tb=short"]
    proc = subprocess.run(args, capture_output=True, text=True, cwd=REPO_ROOT)
    last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    return proc.returncode == 0, last_line


def run_lockstep(forms: list[list[str]]) -> tuple[bool, str]:
    results = []
    for cmd in forms:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        results.append(proc.returncode == 0)
    ok = all(results)
    return ok, f"both invocation forms exit {'0' if ok else 'non-zero'} ({len(forms)} forms)"


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    print("=" * 72)
    print("Migration full health check")
    print("=" * 72)
    print(f"Started: {started}")
    print()

    results: list[tuple[str, bool, str]] = []
    overall_ok = True

    for label, paths in SLICES:
        print(f"[{label}]")
        ok, last_line = run_pytest(label, paths)
        results.append((label, ok, last_line))
        if ok:
            print(f"  PASS — {last_line}")
        else:
            print(f"  FAIL — {last_line}")
            overall_ok = False
        print()

    # Pipeline lockstep — both invocation forms
    label, forms = PIPELINE_LOCKSTEP
    print(f"[{label}]")
    ok, msg = run_lockstep(forms)
    results.append((label, ok, msg))
    if ok:
        print(f"  PASS — {msg}")
    else:
        print(f"  FAIL — {msg}")
        overall_ok = False
    print()

    finished = datetime.now(timezone.utc).isoformat()

    print("=" * 72)
    print("Summary:")
    print("=" * 72)
    pass_count = sum(1 for _, ok, _ in results if ok)
    fail_count = sum(1 for _, ok, _ in results if not ok)
    for label, ok, last_line in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}: {last_line}")
    print()
    print(f"Slices: {pass_count} PASS / {fail_count} FAIL of {len(results)} total")
    print(f"Overall: {'PASS — migration substrate healthy' if overall_ok else 'FAIL — substrate regression'}")
    print(f"Started: {started}")
    print(f"Finished: {finished}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
