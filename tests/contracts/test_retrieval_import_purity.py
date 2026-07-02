"""Leg-E AC#2 / Winston W-1 — retrieval-package import purity.

import-linter governs only `app` (`pyproject.toml [tool.importlinter]`), so it
cannot police the skills-tree `retrieval` package. This test closes that gap:
importing `retrieval` (which eagerly imports EVERY provider, gamma_docs
included) must load NO `app.*` module — an `app.*` import inside any adapter
would execute inside every production Texas retrieval dispatch
(`app/specialists/texas/retrieval_dispatch.py` shells out to run_wrangler).

Runs in a SUBPROCESS so `sys.modules` starts clean (the in-process pytest run
has long since imported `app.*` for other suites).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_SCRIPTS = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts"

_PURITY_SNIPPET = r"""
import sys

import retrieval  # eager: imports every provider, incl. gamma_docs

bad = sorted(m for m in sys.modules if m == "app" or m.startswith("app."))
if bad:
    print("APP MODULES LOADED: " + ", ".join(bad))
    sys.exit(2)

# Non-vacuous witness (Murat M-2): the import above must have registered the
# Leg-E adapter; a purity pass over a package that silently dropped gamma_docs
# would prove nothing about the new code.
ids = {p.id for p in retrieval.list_providers(shape="retrieval")}
if "gamma_docs" not in ids:
    print("gamma_docs NOT registered after `import retrieval`: " + repr(sorted(ids)))
    sys.exit(3)
print("pure")
"""


def test_importing_retrieval_package_loads_no_app_modules() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(REPO_ROOT), str(RETRIEVAL_SCRIPTS)])
    proc = subprocess.run(
        [sys.executable, "-c", _PURITY_SNIPPET],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"retrieval import-purity subprocess failed (rc={proc.returncode}):\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    assert "pure" in proc.stdout
