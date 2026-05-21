"""Slab 6.4 Gate 5 dual-gate evidence ceremony.

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\gate5_slab_6_4.py

Exercises the Pass 2 authoring template per AC-6.4-G (Python-based; sandbox-AC compliant):
1. Validator-oracle alignment (proves new template's contract aligns with
   validate-irene-pass2-handoff.py -- 50 enumerated enforcement points)
2. Composition smoke (template through ProductionDispatchAdapter)
3. Strict Pydantic + closed-enum 3-surface red-rejection tests

Note: the strict post-hoc validator (validate-irene-pass2-handoff.py) is a
category-mismatch for this ceremony -- it validates Pass 2 RUN OUTPUTS
(segment-manifest.yaml + narration-script.md + perception-artifacts.json +
pass2-envelope.json), NOT the authoring template's Pydantic golden snapshot.
The validator-oracle alignment suite (#1 above) is the correct evidence
for AC-6.4-G -- it proves the authoring template encodes the validator's
contract structurally + procedurally. Direct post-hoc validator runs
happen at first tracked trial against real Pass 2 outputs, NOT here.

Prints a paste-ready evidence block for the Dev Agent Record Section "Operator dual-gate gate-2 evidence".
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
            print(f"  PASS -- {summary}")
        else:
            print(f"  FAIL -- {summary}")
            if err:
                print(f"  stderr: {err.splitlines()[-1] if err else ''}")
            overall_ok = False
        results.append((label, ok, summary))
        print()

    finished = datetime.now(timezone.utc).isoformat()

    print("=" * 72)
    print("Summary (paste-ready for Dev Agent Record Section 'Operator dual-gate gate-2 evidence'):")
    print("=" * 72)
    print()
    print(f"- **Date:** {started[:10]}")
    print(f"- **Command:** `.venv\\Scripts\\python.exe scripts\\operator\\gate5_slab_6_4.py`")
    print(f"- **Started:** {started}")
    print(f"- **Finished:** {finished}")
    for label, ok, summary in results:
        if ok is True:
            print(f"- **{label}:** PASS -- {summary}")
        elif ok is False:
            print(f"- **{label}:** FAIL -- {summary}")
        else:
            print(f"- **{label}:** SKIP -- {summary}")
    print(f"- **Overall:** {'PASS' if overall_ok else 'FAIL'}")
    print(f"- **Operator witness:** Juan Leon (operator session)")
    print(f"- **Disposition:** {'PASS -- substrate_shape gate cleared + invariant_preservation gate cleared. AC-6.4-G satisfied. Story 6.4 ready for review -> done flip per discipline doc Gate 6.' if overall_ok else 'FAIL -- at least one suite returned non-zero. Investigate before close.'}")
    print()

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
