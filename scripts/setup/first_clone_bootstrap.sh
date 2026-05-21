#!/usr/bin/env bash
# first_clone_bootstrap.sh — one-command setup for fresh clone (Linux / macOS)
#
# Usage:
#   bash scripts/setup/first_clone_bootstrap.sh
#   bash scripts/setup/first_clone_bootstrap.sh --skip-postgres
#
# What it does:
#   1. Verify Python 3.11+ + git on PATH
#   2. Create .venv if absent
#   3. Install deps via pip
#   4. Stub .env from .env.example if .env absent
#   5. Install pre-commit hooks
#   6. Optional: Postgres reachability ping
#   7. Run trial_run_preflight.py for sanity verdict

set -euo pipefail

SKIP_POSTGRES=0
SKIP_PRECOMMIT=0
for arg in "$@"; do
    case "$arg" in
        --skip-postgres) SKIP_POSTGRES=1 ;;
        --skip-pre-commit) SKIP_PRECOMMIT=1 ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== first_clone_bootstrap (Unix) ==="
echo "Repo: $REPO_ROOT"
echo ""

# --- Step 1 ---
echo "[1/7] Verifying Python 3.11+ + git on PATH..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "  FAIL: python3 not on PATH"
    exit 2
fi
PYVER=$(python3 --version)
echo "  Python: $PYVER"
if ! command -v git >/dev/null 2>&1; then
    echo "  WARN: git not on PATH (commits/pushes will fail)"
else
    echo "  Git: $(git --version)"
fi

# --- Step 2 ---
echo ""
echo "[2/7] Creating .venv if absent..."
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    echo "  PASS: .venv exists"
else
    echo "  Creating .venv..."
    cd "$REPO_ROOT"
    python3 -m venv .venv
    echo "  PASS: .venv created"
fi

# --- Step 3 ---
echo ""
echo "[3/7] Installing dependencies via pip..."
cd "$REPO_ROOT"
"$REPO_ROOT/.venv/bin/python" -m pip install --upgrade pip >/dev/null
if "$REPO_ROOT/.venv/bin/python" -m pip install -e ".[dev]"; then
    echo "  PASS: deps installed (editable + dev extras)"
else
    echo "  FAIL: pip install failed"
    exit 2
fi

# --- Step 4 ---
echo ""
echo "[4/7] Stubbing .env from .env.example if absent..."
if [[ -f "$REPO_ROOT/.env" ]]; then
    echo "  PASS: .env exists"
elif [[ -f "$REPO_ROOT/.env.example" ]]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo "  PASS: .env stubbed from .env.example"
    echo "  ACTION REQUIRED: edit .env and replace <placeholder> values with real credentials"
else
    echo "  WARN: no .env.example found"
fi

# --- Step 5 ---
echo ""
if [[ $SKIP_PRECOMMIT -eq 1 ]]; then
    echo "[5/7] Skipping pre-commit install (per --skip-pre-commit)"
else
    echo "[5/7] Installing pre-commit hooks..."
    if "$REPO_ROOT/.venv/bin/pre-commit" install >/dev/null 2>&1; then
        echo "  PASS: pre-commit hooks installed"
    else
        echo "  WARN: pre-commit install failed (run manually later)"
    fi
fi

# --- Step 6 ---
echo ""
if [[ $SKIP_POSTGRES -eq 1 ]]; then
    echo "[6/7] Skipping Postgres check (per --skip-postgres)"
else
    echo "[6/7] Pinging Postgres (non-fatal)..."
    "$REPO_ROOT/.venv/bin/python" -c "
import os, sys
db = os.environ.get('DATABASE_URL')
if not db:
    print('SKIP: DATABASE_URL not set'); sys.exit(0)
try:
    import psycopg
    psycopg.connect(db, connect_timeout=5).close()
    print('PASS: Postgres reachable')
except Exception as e:
    print(f'WARN: Postgres ping failed: {e}')
" || true
fi

# --- Step 7 ---
echo ""
echo "[7/7] Running trial_run_preflight.py..."
"$REPO_ROOT/.venv/bin/python" "$REPO_ROOT/scripts/utilities/trial_run_preflight.py"
PREFLIGHT_EXIT=$?

echo ""
echo "=== Bootstrap complete ==="
if [[ $PREFLIGHT_EXIT -eq 0 ]]; then
    echo "Verdict: GREEN — ready for trial-run (warnings may apply)"
elif [[ $PREFLIGHT_EXIT -eq 1 ]]; then
    echo "Verdict: YELLOW — non-required failures detected"
else
    echo "Verdict: RED — blocking failures; resolve before trial-run"
fi
echo ""
echo "Next steps:"
echo "  1. Edit .env to replace <placeholder> values"
echo "  2. Read docs/operator/trial-run-runbook.md"
echo "  3. Read README.md for orientation"
exit $PREFLIGHT_EXIT
