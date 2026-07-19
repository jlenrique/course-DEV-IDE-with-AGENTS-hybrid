"""Fail-soft reader for the project quality scorecard.

The authority is the PROSE of ``docs/quality/project-quality-scorecard.md``; this
module parses only the machine-readable YAML block at the bottom (marked
``QUALITY-SCORECARD-MACHINE-BLOCK``) to surface the headline numbers.

Design contract: **never raise into a production run.** Every public function
returns a well-formed dict — an ``{"status": "unavailable", ...}`` marker — when
the scorecard is missing, malformed, or otherwise unreadable. Stdlib + PyYAML
only (no ``app`` imports), so this stays a clean importable leaf.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_SCORECARD_REL = "docs/quality/project-quality-scorecard.md"
_MACHINE_MARKER = "QUALITY-SCORECARD-MACHINE-BLOCK"
# The fenced ```yaml block immediately following the marker comment.
_BLOCK_RE = re.compile(
    r"QUALITY-SCORECARD-MACHINE-BLOCK.*?```yaml\s*(?P<body>.*?)```",
    re.DOTALL,
)
_DID_KEY = "dynamic_intelligence_vs_determinism"


def _repo_root() -> Path:
    # app/quality/scorecard.py -> app/quality -> app -> <repo root>
    return Path(__file__).resolve().parents[2]


def scorecard_path() -> Path:
    return _repo_root() / _SCORECARD_REL


def read_scorecard_block(path: Path | None = None) -> dict[str, Any] | None:
    """Parse the machine-readable YAML block. Returns ``None`` if unavailable.

    Fail-soft: any missing file / missing marker / bad YAML / non-mapping result
    yields ``None`` rather than an exception.
    """
    p = path or scorecard_path()
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    m = _BLOCK_RE.search(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group("body"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def did_score_ref(path: Path | None = None) -> dict[str, Any]:
    """Small, embeddable summary of the DID dimension for a run's final report.

    Always returns a dict. On success::

        {"dimension": "Dynamic Intelligence vs Determinism", "score": 65,
         "max": 100, "band": "B-", "as_of": "2026-07-19",
         "source": "docs/quality/project-quality-scorecard.md"}

    On any failure::

        {"status": "unavailable", "source": "docs/quality/project-quality-scorecard.md"}
    """
    block = read_scorecard_block(path)
    dim = (block or {}).get("dimensions", {}).get(_DID_KEY) if block else None
    if not isinstance(dim, dict):
        return {"status": "unavailable", "source": _SCORECARD_REL}
    as_of = block.get("as_of") if isinstance(block, dict) else None
    return {
        "dimension": dim.get("label", "Dynamic Intelligence vs Determinism"),
        "score": dim.get("score"),
        "max": dim.get("max", 100),
        "band": dim.get("band"),
        # yaml parses a bare ISO date into datetime.date; coerce to str so the
        # ref is JSON-clean and stable when embedded in run_summary.yaml.
        "as_of": str(as_of) if as_of is not None else None,
        "source": _SCORECARD_REL,
    }
