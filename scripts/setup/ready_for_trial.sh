#!/usr/bin/env bash
# ready_for_trial.sh - pre-flight one-command harness for first real trial readiness.
#
# Usage:
#   bash scripts/setup/ready_for_trial.sh
#
# Exit 0 only when every required check passes. Prints a per-step summary and a
# final READY FOR TRIAL / BLOCKED banner.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="$REPO_ROOT/.venv/bin/python"
RUFF="$REPO_ROOT/.venv/bin/ruff"
LINT_IMPORTS="$REPO_ROOT/.venv/bin/lint-imports"

declare -a STEP_RESULTS=()
FAILED_STEP=""

run_required_key_check() {
    "$PYTHON" - <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
try:
    from scripts.utilities.env_loader import load_env

    load_env()
except (FileNotFoundError, ImportError):
    pass

from os import environ

missing = [name for name in ("OPENAI_API_KEY", "LANGSMITH_API_KEY") if not environ.get(name)]
assert not missing, f"Missing required keys: {missing}"
print("PASS: required keys present")
PY
}

run_step() {
    local number="$1"
    local name="$2"
    shift 2

    echo ""
    echo "[$number/9] $name..."
    "$@" 2>&1
    local exit_code=$?

    STEP_RESULTS+=("$number|$name|$exit_code")

    if [[ $exit_code -eq 0 ]]; then
        echo "  PASS"
    else
        echo "  FAIL (exit $exit_code)"
        if [[ -z "$FAILED_STEP" ]]; then
            FAILED_STEP="$number|$name"
        fi
    fi
}

cd "$REPO_ROOT"

run_step 1 "trial_run_preflight.py" \
    "$PYTHON" "scripts/utilities/trial_run_preflight.py"

run_step 2 "migration_health_dashboard.py" \
    "$PYTHON" "scripts/utilities/migration_health_dashboard.py"

run_step 3 "m5_pre_vote_audit.py" \
    "$PYTHON" "scripts/utilities/m5_pre_vote_audit.py"

run_step 4 "app.runtime.cascade_config validate" \
    "$PYTHON" -m app.runtime.cascade_config validate

run_step 5 "pytest remediation model-id guards" \
    "$PYTHON" -m pytest \
    "tests/test_no_fictitious_model_ids.py" \
    "tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py" \
    "tests/integration/runtime/test_cascade_config_loading.py" \
    -q --tb=short

run_step 6 "required key presence (OPENAI_API_KEY, LANGSMITH_API_KEY)" \
    run_required_key_check

run_step 7 "ruff check runtime/replay/runtime-model test surfaces" \
    "$RUFF" check \
    "app/runtime" \
    "app/replay" \
    "app/models/runtime" \
    "tests/unit/runtime" \
    "tests/integration/runtime" \
    "tests/integration/replay" \
    "tests/migration" \
    "tests/trial_replay" \
    "tests/test_no_fictitious_model_ids.py"

run_step 8 "lint-imports" \
    "$LINT_IMPORTS" --config "pyproject.toml"

run_step 9 "pytest tests/migration -q --tb=short" \
    "$PYTHON" -m pytest "tests/migration" -q --tb=short

echo ""
echo "=== ready_for_trial summary ==="
for entry in "${STEP_RESULTS[@]}"; do
    IFS='|' read -r number name exit_code <<<"$entry"
    if [[ "$exit_code" -eq 0 ]]; then
        status="PASS"
    else
        status="FAIL"
    fi
    echo "[$number/9] $name: $status"
done

echo ""
if [[ -z "$FAILED_STEP" ]]; then
    echo "YOU ARE READY FOR TRIAL"
    exit 0
fi

IFS='|' read -r failed_number failed_name <<<"$FAILED_STEP"
echo "BLOCKED - see step $failed_number ($failed_name) above."
exit 1
