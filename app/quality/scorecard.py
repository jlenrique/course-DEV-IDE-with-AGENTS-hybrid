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
#: Story Q2.1 — Dimension 2 (Cost-efficiency / paid-walk discipline).
_COST_KEY = "cost_efficiency"
#: Story Q2.2 — Dimension 3 (Coverage-honesty).
_COVERAGE_KEY = "coverage_honesty"

#: The named canonical dimension-key universe. Q1.3's GL-6 dimension-coverage
#: meta-ratchet consumes this rail (a new dimension cannot be silently added
#: without a human touching this tuple AND registering its honesty-pin). Q1.1
#: established the constant; the meta-ratchet *test* is Q1.3; Q2.1 added
#: ``cost_efficiency``; Q2.2 adds ``coverage_honesty`` here IN LOCKSTEP with
#: registering its honesty-pin.
_EXPECTED_CANONICAL_DIMENSION_KEYS: tuple[str, ...] = (_DID_KEY, _COST_KEY, _COVERAGE_KEY)


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


def dimension_ref(key: str, path: Path | None = None) -> dict[str, Any]:
    """Small, embeddable summary of **any** dimension, keyed by its machine-block key.

    Dimension-agnostic (v2): a future dimension slots in without editing this
    reader. Always returns a dict. On success::

        {"dimension": "<label>", "score": 65, "max": 100, "band": "B-",
         "as_of": "2026-07-19", "source": "docs/quality/project-quality-scorecard.md",
         # "as_verified": "2026-07-19"  # surfaced when the dimension carries it (v2)
        }

    On any failure (missing file · bad YAML · non-mapping · marker/dimension
    absent)::

        {"status": "unavailable", "source": "docs/quality/project-quality-scorecard.md"}
    """
    block = read_scorecard_block(path)
    dim = (
        block.get("dimensions", {}).get(key)
        if isinstance(block, dict) and isinstance(block.get("dimensions"), dict)
        else None
    )
    if not isinstance(dim, dict):
        return {"status": "unavailable", "source": _SCORECARD_REL}
    # v2 carries a dimension-level as_of; fall back to the block-level as_of (v1
    # shape) so the reader stays backward-compatible.
    as_of = dim.get("as_of", block.get("as_of") if isinstance(block, dict) else None)
    as_verified = dim.get("as_verified")
    ref: dict[str, Any] = {
        "dimension": dim.get("label", key),
        "score": dim.get("score"),
        "max": dim.get("max", 100),
        "band": dim.get("band"),
        # yaml parses a bare ISO date into datetime.date; coerce to str so the
        # ref is JSON-clean and stable when embedded in run_summary.yaml.
        "as_of": str(as_of) if as_of is not None else None,
        "source": _SCORECARD_REL,
    }
    # Additive (v2): surface as_verified when present without changing the
    # existing return-key contract the two live consumers depend on.
    if as_verified is not None:
        ref["as_verified"] = str(as_verified)
    return ref


def did_score_ref(path: Path | None = None) -> dict[str, Any]:
    """Thin convenience wrapper: the DID dimension summary for a run's final report.

    Retained for the CLI consumer (``scripts/utilities/quality_scorecard.py``). The
    runtime run-summary no longer reads the doc: Q1.4a (GL-4) removed
    ``production_runner._quality_scorecard_ref`` and emits a static breadcrumb
    pointer instead, decoupling the run from this governance doc. Its **return keys
    are stable** (``dimension``, ``score``, ``max``, ``band``, ``as_of``,
    ``source``) — those keys always appear, so the CLI keeps working — and it may
    additionally surface
    ``as_verified`` (v2). Note this is key-stability, not full value-stability vs v1:
    ``as_of`` now prefers the *dimension-level* ``as_of`` when the v2 block carries one
    (falling back to the block-level date), which is the intended v2 behaviour — the
    per-dimension date is the authoritative "prose last-edited" stamp for this
    dimension. It delegates to :func:`dimension_ref`.
    """
    return dimension_ref(_DID_KEY, path)
