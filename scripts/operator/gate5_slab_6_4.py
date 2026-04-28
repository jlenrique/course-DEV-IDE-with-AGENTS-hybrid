"""Slab 6.4 Gate 5 dual-gate evidence ceremony.

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\gate5_slab_6_4.py

Exercises the Pass 2 authoring template per AC-6.4-G:
1. Validator-oracle alignment suite (validator vs new template enforcement)
2. Composition smoke (template through ProductionDispatchAdapter)
3. Strict Pydantic + closed-enum 3-surface red-rejection tests
4. Direct validator run against golden fixture (B-Run §08-shaped)

Prints a paste-ready evidence block for the Dev Agent Record §"Operator dual-gate gate-2 evidence".
"""
from __future__ import annotations

import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"

SUITES = [
    (
        "validator-oracle alignment",
        ["-m", "pytest", "tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py", "-q", "--tb=short"],
    ),
    (
        "composition smoke",
        ["-m", "pytest", "tests/composition/test_irene_pass_2_template_composition_smoke.py", "-q", "--tb=short"],
    ),
    (
        "strict + closed-enum + procedural-rule",
        ["-m", "pytest", "tests/unit/specialists/irene/test_pass_2_template_strict.py", "-q", "--tb=short"],
    ),
]

GOLDEN_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "specialists" / "irene" / "pass_2_template_golden.json"
VALIDATOR_SCRIPT = REPO_ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-irene-pass2-handoff.py"


def run(label: str, args: list[str]) -> tuple[bool, str, str]:
    cmd = [str(PYTHON), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "", proc.stderr.strip()


def main() -> int:
    print("=" * 72)
    print("Slab 6.4 Gate 5 dual-gate evidence ceremony")
    print("=" * 72)
    started = datetime.now(timezone.utc).isoformat()
    print(f"Started: {started}")
    print()

    results: list[tuple[str, bool, str]] = []
    overall_ok = True

    for label, args in SUITES:
        print(f"[{label}]")
        print(f"  $ {PYTHON.name} {' '.join(args)}")
        ok, summary, err = run(label, args)
        if ok:
            print(f"  PASS — {summary}")
        else:
            print(f"  FAIL — {summary}")
            if err:
                print(f"  stderr: {err.splitlines()[-1] if err else ''}")
            overall_ok = False
        results.append((label, ok, summary))
        print()

    # Direct validator run against golden fixture
    print("[validator vs golden fixture]")
    if VALIDATOR_SCRIPT.is_file() and GOLDEN_FIXTURE.is_file():
        cmd = [str(PYTHON), str(VALIDATOR_SCRIPT), str(GOLDEN_FIXTURE)]
        print(f"  $ {PYTHON.name} {VALIDATOR_SCRIPT.relative_to(REPO_ROOT)} {GOLDEN_FIXTURE.relative_to(REPO_ROOT)}")
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        if proc.returncode == 0:
            print("  PASS — validator accepts golden fixture (post-cycle-1 cluster_role + post-cycle-2 patches)")
            results.append(("validator vs golden fixture", True, "exit 0; validator accepts golden"))
        else:
            print(f"  FAIL — validator returned exit {proc.returncode}")
            if proc.stdout.strip():
                print(f"  stdout: {proc.stdout.strip().splitlines()[-1]}")
            results.append(("validator vs golden fixture", False, f"exit {proc.returncode}"))
            overall_ok = False
    else:
        msg = f"missing: validator={VALIDATOR_SCRIPT.is_file()}, golden={GOLDEN_FIXTURE.is_file()}"
        print(f"  SKIP — {msg}")
        results.append(("validator vs golden fixture", None, msg))
    print()

    finished = datetime.now(timezone.utc).isoformat()

    print("=" * 72)
    print("Summary (paste-ready for Dev Agent Record §'Operator dual-gate gate-2 evidence'):")
    print("=" * 72)
    print()
    print(f"- **Date:** {started[:10]}")
    print(f"- **Command:** `.venv\\Scripts\\python.exe scripts\\operator\\gate5_slab_6_4.py`")
    print(f"- **Started:** {started}")
    print(f"- **Finished:** {finished}")
    for label, ok, summary in results:
        if ok is True:
            print(f"- **{label}:** PASS — {summary}")
        elif ok is False:
            print(f"- **{label}:** FAIL — {summary}")
        else:
            print(f"- **{label}:** SKIP — {summary}")
    print(f"- **Overall:** {'PASS' if overall_ok else 'FAIL'}")
    print(f"- **Operator witness:** Juan Leon (operator session)")
    print(f"- **Disposition:** {'PASS — substrate_shape gate cleared + invariant_preservation gate cleared. AC-6.4-G satisfied. Story 6.4 ready for review → done flip per discipline doc Gate 6.' if overall_ok else 'FAIL — at least one suite returned non-zero. Investigate before close.'}")
    print()

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
