"""Slab 6.0 dual-gate evidence ceremony (re-runnable).

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\dual_gate_slab_6_0.py

Exercises the production envelope substrate per AC-6.0-I item 5:
- tests/composition/ -- full composition discipline including Texas -> cd chain test
  (the load-bearing test that mirrors the Slab 6.1 strict-AC HALT scenario).

Original close commit: 0a4f868 (closed 2026-04-27 with 17 passed in 1.21s).
This script re-runs the same gate for confidence + future regression check.

No live API; no operator credentials needed. Synthetic specialist outputs
at LLM-call boundary keep cost ~$0.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    print("=" * 72)
    print("Slab 6.0 dual-gate evidence ceremony (production envelope substrate)")
    print("=" * 72)
    print(f"Started: {started}")
    print()
    print(f"$ {PYTHON.name} -m pytest tests/composition/ -q --tb=short")
    print()

    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/composition/", "-q", "--tb=short"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    output = proc.stdout
    print(output)
    if proc.stderr.strip():
        print("--- stderr ---")
        print(proc.stderr)

    finished = datetime.now(timezone.utc).isoformat()
    last_line = output.strip().splitlines()[-1] if output.strip() else "(no output)"
    overall_ok = proc.returncode == 0

    print("=" * 72)
    print("Summary (paste-ready):")
    print("=" * 72)
    print()
    print(f"- **Date:** {started[:10]}")
    print(f"- **Command:** `.venv\\Scripts\\python.exe scripts\\operator\\dual_gate_slab_6_0.py`")
    print(f"- **Equivalent direct command:** `pytest tests/composition/ -q --tb=short`")
    print(f"- **Result:** {last_line}")
    print(f"- **Overall:** {'PASS' if overall_ok else 'FAIL'}")
    print(f"- **Operator witness:** Juan Leon (operator session)")
    print(f"- **Disposition:** {'PASS -- Slab 6.0 substrate (envelope + adapter + composition discipline) verified end-to-end.' if overall_ok else 'FAIL -- substrate regression; investigate before any composition-affecting work proceeds.'}")
    print()

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
