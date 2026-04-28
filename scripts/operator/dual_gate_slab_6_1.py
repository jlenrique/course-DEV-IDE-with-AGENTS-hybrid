"""Slab 6.1 dual-gate evidence ceremony (re-runnable; LIVE API).

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\dual_gate_slab_6_1.py

Exercises the production-graph runner consuming Slab 6.0 substrate per AC-6.1-K item 5:
- tests/live/test_production_trial_smoke_with_gate.py -- live OpenAI specialist invocations
  through ProductionDispatchAdapter + checkpoint pause/resume working end-to-end.

Original close commit: 97842ac (closed 2026-04-27 with 1 passed in 30.54s).

Requires:
- OPENAI_API_KEY (live OpenAI; cost ~$0.10-$0.30 per run)
- LANGSMITH_API_KEY + LANGSMITH_PROJECT (trace upload required per AC-6.1-F evidence discipline)

Auto-loads .env per existing scripts/operator/ pattern.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"


def _load_dotenv() -> None:
    """Best-effort .env load without adding python-dotenv dependency."""
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def main() -> int:
    _load_dotenv()
    started = datetime.now(timezone.utc).isoformat()

    print("=" * 72)
    print("Slab 6.1 dual-gate evidence ceremony (production-graph runner; LIVE)")
    print("=" * 72)
    print(f"Started: {started}")
    print()

    # Pre-flight: required keys
    required = ("OPENAI_API_KEY", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT")
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"PRE-FLIGHT FAIL -- missing env vars: {', '.join(missing)}")
        print("Set these in .env or environment before re-running.")
        print("(scripts/operator/check_keys.py can verify state.)")
        return 2
    print(f"PRE-FLIGHT -- all 3 required env vars present (OPENAI_API_KEY + LANGSMITH_API_KEY + LANGSMITH_PROJECT)")
    print()
    print(f"$ {PYTHON.name} -m pytest tests/live/test_production_trial_smoke_with_gate.py -m live -q --tb=short")
    print()

    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/live/test_production_trial_smoke_with_gate.py", "-m", "live", "-q", "--tb=short"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=os.environ,
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
    print(f"- **Command:** `.venv\\Scripts\\python.exe scripts\\operator\\dual_gate_slab_6_1.py`")
    print(f"- **Equivalent direct command:** `pytest tests/live/test_production_trial_smoke_with_gate.py -m live -q --tb=short`")
    print(f"- **Result:** {last_line}")
    print(f"- **Overall:** {'PASS' if overall_ok else 'FAIL'}")
    print(f"- **Operator witness:** Juan Leon (operator session)")
    print(f"- **Cost note:** real OpenAI invocation ~$0.10-$0.30 expected; check LangSmith dashboard for trace by trial_id metadata")
    print(f"- **Disposition:** {'PASS -- Slab 6.1 production-graph runner verified end-to-end through HIL gate pause/resume.' if overall_ok else 'FAIL -- production runner regression; halt-and-surface before any production trial.'}")
    print()

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
