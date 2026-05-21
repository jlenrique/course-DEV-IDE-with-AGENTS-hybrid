#!/usr/bin/env python3
# ruff: noqa: N999
# Filename `init-sanctum.py` is intentional — matches the sibling forwarder
# convention across all bmad-agent-* skills (content-creator, cd, etc.) so
# operators invoke the same command shape per agent. The hyphen is required
# by the convention; module-name lint is suppressed here file-wide.
"""Thin forwarder to the shared BMB scaffold (Epic 26)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent
SHARED = REPO_ROOT / "scripts" / "bmb_agent_migration" / "init_sanctum.py"


def main() -> int:
    if not SHARED.exists():
        print(
            f"ERROR: shared scaffold not found at {SHARED}\n"
            "Run this from a repository where Epic 26 scaffolding has been installed.",
            file=sys.stderr,
        )
        return 2
    return subprocess.call(
        [
            sys.executable,
            str(SHARED),
            "--skill-path",
            str(SKILL_DIR),
            *sys.argv[1:],
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
