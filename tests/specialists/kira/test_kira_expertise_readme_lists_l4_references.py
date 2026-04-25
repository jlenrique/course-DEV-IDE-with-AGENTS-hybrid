"""AC-F shape pin: Kira's expertise/README.md dotted list MUST match KIRA_REFERENCES.

The `KIRA_REFERENCES` tuple in `app/specialists/kira/graph.py` is the
load-bearing source of truth for the prompt-assembly file-order contract.
The `expertise/README.md` reflects that contract for human readers. If the
two drift, prompt assembly silently changes its file-order signature and
collapses cache-prefix determinism for the FR54 cache-hit-rate AC.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.specialists.kira.graph import KIRA_REFERENCES

REPO_ROOT = Path(__file__).resolve().parents[3]
README_PATH = REPO_ROOT / "app" / "specialists" / "kira" / "expertise" / "README.md"


def test_kira_readme_dotted_list_matches_kira_references() -> None:
    """README's dotted-reference column MUST list every KIRA_REFERENCES entry."""
    text = README_PATH.read_text(encoding="utf-8")
    # Match `<name>` in the first column of the dotted-reference markdown table.
    # Pattern is conservative: backtick-wrapped tokens that end in `.md` and
    # appear inside a table row (line starts with `|`).
    referenced = set(re.findall(r"`([^`]+\.md)`", text))
    missing = set(KIRA_REFERENCES) - referenced
    assert not missing, (
        f"expertise/README.md missing {sorted(missing)} from the dotted-reference list; "
        "KIRA_REFERENCES is the source of truth — README must mirror it"
    )
