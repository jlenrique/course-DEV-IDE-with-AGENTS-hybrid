"""Story Q1.4b — the deterministic final-report projector (Band + ranked-leaks +
trend + THIS-run fence_state), rendered in the Epic-43 tabular discipline.

At a run's final report the operator must see BOTH the project's quality POSTURE
(Band / ranked leaks / trend — a *project* judgment) AND what THIS run actually
FENCED (the mechanical ``fence_state`` facts Q1.4a emits into ``run_summary.yaml``).
Those are different things; conflating them would let a project grade read as a
per-run claim. So the projector renders two clearly-labelled sections —
**"This run" (facts)** vs **"Project (not this run)" (Band/leaks/trend)**
(consensus rule #1).

Design contract:

  * **Deterministic** (AC4): same inputs → byte-identical output. Dimensions,
    criteria, and leaks are sorted by fixed keys; the fence table uses a fixed
    row order; no ``dict``-iteration-order dependence and no timestamps.
  * **Fail-soft** (AC3 / NFR1): the projector NEVER raises. A degraded/missing
    scorecard, an empty history, or an absent / ``{"status": "unavailable"}``
    fence_state each degrade to an honest rendered marker; a run's final report
    must never fail over the projection. Per-field: a bad scorecard degrades the
    Project section only; a bad fence_state degrades the This-run section only.
  * **Trend is NEVER painted** (AC2): the arrow is derived from the append-only
    history ledger via :func:`app.quality.history.trend_from_history` — the
    projector reads the ledger, it does not accept a hand-supplied arrow. An
    absent/empty ledger degrades honestly to ``▬ baseline``.
  * **Clean leaf** (GL-3 / NFR4): module scope is stdlib only; the trend reader
    is reached by a **relative** intra-package import (``from .history import``),
    which references no foreign ``app.*`` name — the recursive clean-leaf guard
    (:mod:`tests.quality.test_scorecard_clean_leaf`) stays green over this file.

**Tabular discipline (Epic-43).** Rather than a cross-package deferred import of
the private ``app.marcus.cli.hil_tabular_projector._md_table`` symbol, this module
re-expresses the same minimal-markdown-table discipline stdlib-only in
:func:`_md_table` (header row → separator → body; ``None`` cell → empty). The bar
is deterministic + Epic-43-consistent + golden-stable, and a stdlib re-express
keeps ``report.py`` a pure leaf with no coupling to a private cross-package helper.

**GL-13 — ranked leaks are CROSS-dimensional.** :func:`ranked_project_leaks`
aggregates EVERY dimension's machine-block ``leaks`` list into ONE shared project
ranked-leak list (ranked by lane priority paid-walk → learner-trust → governance,
then declared rank). DID is the only contributor today; a future Q2/Q3 dimension
registers simply by adding its own ``leaks`` list to its machine block.
:func:`leak_coverage_gaps` is the structural guard: a dimension declaring
``open_leaks > 0`` but carrying no ``leaks`` list is a coverage gap (a sibling
cannot silently stay off the shared list).

**Scope (GL-10).** This ships the projector FUNCTION + a golden; the LIVE run-end
wiring into ``production_runner`` and the checkable-comparison witness ride the R2
operator-steered trial (filed to deferred-work.md). This module does not touch the
pipeline-lockstep ``production_runner`` emit path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Relative (intra-package) import: references no foreign ``app.*`` name, so the
# clean-leaf guard allows it (intra-package cohesion). The trend arrow is COMPUTED
# from the ledger (never painted): the projector reads it ONCE via
# ``all_history_entries`` and derives each dimension's arrow via ``trend_from_entries``
# — the same shared computation ``trend_from_history`` uses (FIX-5: one file read).
from .history import all_history_entries, trend_from_entries

#: Lane display / ranking priority (consensus outcome-weighting: paid-walk first).
_LANE_PRIORITY: dict[str, int] = {
    "paid-walk": 0,
    "learner-trust": 1,
    "governance": 2,
}
_LANE_PRIORITY_UNKNOWN = 3

#: Trend label → deterministic arrow glyph (▬ baseline today; never painted — the
#: label itself comes from the history ledger via :func:`trend_from_history`).
_TREND_ARROWS: dict[str, str] = {
    "baseline": "▬ baseline",
    "rising": "▲ rising",
    "falling": "▼ falling",
    "flat": "▬ flat",
}

#: The fence_state row order (AC4 — fixed, so output is byte-identical regardless of
#: the emitting dict's key order). Each entry: (display label, path into fence_state).
#: ``("fences_enabled", "fidelity")`` reads ``fence_state["fences_enabled"]["fidelity"]``.
_FENCE_ROWS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Fence enabled — fidelity", ("fences_enabled", "fidelity")),
    ("Fence enabled — coverage", ("fences_enabled", "coverage")),
    ("Fence enabled — UDAC", ("fences_enabled", "udac")),
    ("Silent bypass events", ("silent_bypass_events",)),
    ("HIL allowlist empty", ("hil_allowlist_empty",)),
    ("Cost posture", ("cost_posture",)),
    ("Pack hash binding", ("pack_hash_binding",)),
    ("Conversation chain digest", ("conversation_chain_digest",)),
)

_SCORECARD_UNAVAILABLE = "_quality scorecard unavailable_"
_FENCE_STATE_UNAVAILABLE = "_this run: fence_state unavailable_"


# ------------------------------------------------------------------------------ #
# Tabular discipline (Epic-43 re-express, stdlib-only).
# ------------------------------------------------------------------------------ #
def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Render a minimal GitHub-flavored markdown table (Epic-43 discipline).

    An empty ``rows`` still emits the header + separator so the operator sees the
    (empty) container rather than a silent gap. A ``None`` cell renders empty.
    """
    head = "| " + " | ".join(str(h) for h in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([head, sep, *body])


# ------------------------------------------------------------------------------ #
# Small fail-soft accessors.
# ------------------------------------------------------------------------------ #
def _dimensions(block: Any) -> dict[str, Any]:
    """The ``dimensions`` mapping from a machine block, or ``{}`` when degraded."""
    if not isinstance(block, dict):
        return {}
    dims = block.get("dimensions")
    return dims if isinstance(dims, dict) else {}


def _cell(value: Any) -> str:
    """Honest cell rendering: ``None`` → ``unavailable``; ``bool`` → ``true``/``false``
    (never coerced away); everything else → ``str``. Never invents a clean value.

    FIX-4: a raw ``|`` in an operator-authored value (band_note / label / slug) would
    split the markdown row into spurious columns, and a newline would break the row
    across lines — corrupting the table AND silently defeating row-anchored goldens
    (``out.find(row)`` → -1). Escape ``|`` and collapse CR/LF to a space so every value
    stays inside its own cell on one line.
    """
    if value is None:
        text = "unavailable"
    elif isinstance(value, bool):
        text = "true" if value else "false"
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _dig(state: dict[str, Any], path: tuple[str, ...]) -> Any:
    """Walk ``path`` into ``state``; a missing/non-mapping hop yields ``None`` (honest
    'unavailable' at render time) rather than raising."""
    cur: Any = state
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


# ------------------------------------------------------------------------------ #
# GL-13 — cross-dimensional ranked leaks + coverage guard.
# ------------------------------------------------------------------------------ #
def _rank_key(rank: Any) -> tuple[int, int]:
    """Deterministic sort key for a possibly-malformed ``rank`` (ints first, in
    order; a non-int/absent rank sorts last but stably)."""
    if isinstance(rank, int) and not isinstance(rank, bool):
        return (0, rank)
    return (1, 0)


def ranked_project_leaks(block: Any) -> list[dict[str, Any]]:
    """Aggregate EVERY dimension's ``leaks`` into ONE cross-dimensional ranked list
    (GL-13 — the shared project ranked-leak list).

    Each returned entry mirrors a machine-block leak plus its origin dimension::

        {"rank", "criterion", "slug", "lane", "dimension", "dimension_label"}

    Ranking (deterministic, AC4): lane priority (paid-walk → learner-trust →
    governance → unknown), then the declared ``rank``, then ``slug`` as a final
    tie-break. DID is the sole contributor today; a Q2/Q3 dimension joins simply by
    carrying its own ``leaks`` list. Fail-soft: a degraded block / missing or
    non-list ``leaks`` / non-mapping entry is skipped, never raised.
    """
    collected: list[dict[str, Any]] = []
    dims = _dimensions(block)
    for dim_key in sorted(dims, key=str):  # total-order-safe (mixed key types)
        dim = dims[dim_key]
        if not isinstance(dim, dict):
            continue
        leaks = dim.get("leaks")
        if not isinstance(leaks, list):
            continue
        label = dim.get("label", dim_key)
        for leak in leaks:
            if not isinstance(leak, dict):
                continue
            collected.append(
                {
                    "rank": leak.get("rank"),
                    "criterion": leak.get("criterion"),
                    "slug": leak.get("slug"),
                    "lane": leak.get("lane"),
                    "dimension": dim_key,
                    "dimension_label": label,
                }
            )
    collected.sort(
        key=lambda e: (
            _LANE_PRIORITY.get(str(e["lane"]), _LANE_PRIORITY_UNKNOWN),
            _rank_key(e["rank"]),
            str(e["slug"]),
        )
    )
    return collected


def leak_coverage_gaps(block: Any) -> list[str]:
    """AC5 coverage guard: dimensions that declare ``open_leaks > 0`` but carry no
    ``leaks`` list (so ``ranked_project_leaks`` would silently miss them).

    Returns a sorted list of human-readable gap descriptions — empty means every
    open-leak-declaring dimension is registered on the shared ranked list. A
    non-integer / ``bool`` / ``<= 0`` ``open_leaks`` is not a gap (nothing to
    register); an empty ``leaks`` list under a positive ``open_leaks`` IS a gap.
    """
    gaps: list[str] = []
    dims = _dimensions(block)
    for dim_key in sorted(dims, key=str):  # total-order-safe (mixed key types)
        dim = dims[dim_key]
        if not isinstance(dim, dict):
            continue
        open_leaks = dim.get("open_leaks")
        if not (isinstance(open_leaks, int) and not isinstance(open_leaks, bool)):
            continue
        if open_leaks <= 0:
            continue
        leaks = dim.get("leaks")
        if not isinstance(leaks, list) or len(leaks) == 0:
            gaps.append(
                f"{dim_key}: open_leaks={open_leaks} but no `leaks` list "
                "(register it into the shared ranked-leak list — GL-13)"
            )
    return gaps


# ------------------------------------------------------------------------------ #
# Section renderers.
# ------------------------------------------------------------------------------ #
_DEGRADED_LEAF_VALUES = frozenset({"unavailable", "undetected"})


def _iter_leaves(value: Any):
    """Yield every non-container leaf value in ``value`` (recursing dicts/lists)."""
    if isinstance(value, dict):
        for v in value.values():
            yield from _iter_leaves(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _iter_leaves(v)
    else:
        yield value


def _fence_state_is_marker(fence_state: Any) -> bool:
    """True when the fence_state should render the single honest marker instead of a
    table of noise (FIX-3). Marker cases: not a mapping; the legacy
    ``{"status":"unavailable"}`` shape; an empty ``{}``; OR — mirroring the REAL
    ``production_runner._build_fence_state`` degraded emit, which sets no ``status``
    key and instead fills per-field ``"unavailable"``/``"undetected"`` string VALUES —
    a fence_state whose EVERY leaf value is in ``{"unavailable","undetected"}``.
    """
    if not isinstance(fence_state, dict):
        return True
    if fence_state.get("status") == "unavailable":
        return True
    leaves = list(_iter_leaves(fence_state))
    if not leaves:  # empty {}
        return True
    return all(
        isinstance(v, str) and v.strip().lower() in _DEGRADED_LEAF_VALUES
        for v in leaves
    )


def _render_fence_state(fence_state: Any) -> str:
    """THIS-run section body: the mechanical fence FACTS as a fixed-order 2-col table,
    or an honest single marker when the fence_state is absent / fully degraded."""
    if _fence_state_is_marker(fence_state):
        return _FENCE_STATE_UNAVAILABLE
    rows = [[label, _cell(_dig(fence_state, path))] for label, path in _FENCE_ROWS]
    return _md_table(["Fact", "Value"], rows)


def _sorted_dims(dims: dict[str, Any]) -> list[tuple[str, Any]]:
    """Dimension items in a total-order-safe, deterministic order (mixed key types)."""
    return sorted(dims.items(), key=lambda kv: str(kv[0]))


def _render_band(dims: dict[str, Any]) -> str:
    rows = [
        [_cell(dim.get("label", key)), _cell(dim.get("band")), _cell(dim.get("band_note"))]
        for key, dim in _sorted_dims(dims)
        if isinstance(dim, dict)
    ]
    return _md_table(["Dimension", "Band", "Note"], rows)


def _render_trace(dims: dict[str, Any]) -> str:
    """Compact per-criterion 0–4 trace (NOT a false-precise /100 headline)."""
    rows: list[list[Any]] = []
    for key, dim in _sorted_dims(dims):
        if not isinstance(dim, dict):
            continue
        label = dim.get("label", key)
        criteria = dim.get("criteria")
        if not isinstance(criteria, dict):
            continue
        for crit_key, crit in sorted(criteria.items(), key=lambda kv: str(kv[0])):
            crit = crit if isinstance(crit, dict) else {}
            score = crit.get("score")
            max_score = crit.get("max")
            trace = f"{_cell(score)}/{_cell(max_score)}"
            rows.append([_cell(label), _cell(crit_key), _cell(crit.get("level")), trace])
    return _md_table(["Dimension", "Criterion", "Level", "0–4"], rows)


def _render_leaks(block: Any) -> str:
    ranked = ranked_project_leaks(block)
    rows = [
        [_cell(e["rank"]), _cell(e["dimension_label"]), _cell(e["criterion"]),
         _cell(e["lane"]), _cell(e["slug"])]
        for e in ranked
    ]
    return _md_table(["Rank", "Dimension", "Criterion", "Lane", "Slug"], rows)


def _render_trend(dims: dict[str, Any], history: Path | str | None) -> str:
    """Trend arrow per dimension, DERIVED from the history ledger (never painted).

    FIX-5: read/parse the ledger ONCE (``all_history_entries``) and compute each
    dimension's arrow from the in-memory entries (``trend_from_entries``) — no
    O(dimensions) re-reads as Q2/Q3 dimensions land. Determinism is preserved.
    """
    hist_path = Path(history) if isinstance(history, (str, Path)) else None
    entries = all_history_entries(hist_path)
    rows = []
    for key, dim in _sorted_dims(dims):
        if not isinstance(dim, dict):
            continue
        label = dim.get("label", key)
        trend = trend_from_entries(entries, key)
        rows.append([_cell(label), _TREND_ARROWS.get(trend, _TREND_ARROWS["baseline"])])
    return _md_table(["Dimension", "Trend"], rows)


def _try_section(fn, marker: str, *args: Any) -> str:
    """Render one section under its OWN fail-soft guard (FIX-2): a failure in ONE
    section (e.g. a malformed scorecard) degrades THAT section to its honest marker
    and NEVER discards an already-good sibling section."""
    try:
        return fn(*args)
    except Exception:  # noqa: BLE001 — a section must never fail the whole report
        return marker


def _render_project(block: Any, history: Path | str | None) -> str:
    dims = _dimensions(block)
    if not dims:
        return _SCORECARD_UNAVAILABLE
    parts = [
        "**Band (per dimension)**",
        "",
        _render_band(dims),
        "",
        "**Per-criterion trace (0–4)**",
        "",
        _render_trace(dims),
        "",
        "**Ranked project leaks**",
        "",
        _render_leaks(block),
        "",
        "**Trend**",
        "",
        _render_trend(dims, history),
    ]
    return "\n".join(parts)


# ------------------------------------------------------------------------------ #
# Public entry point.
# ------------------------------------------------------------------------------ #
def render_scorecard_final_report(
    *,
    block: Any,
    history: Path | str | None,
    fence_state: Any,
) -> str:
    """Render the deterministic final-report projection (AC2/AC3/AC4).

    ``block``       — the parsed machine block dict (``read_scorecard_block()``), or
                      ``None`` / degraded → the Project section renders an honest
                      "quality scorecard unavailable" marker.
    ``history``     — the append-only trend ledger PATH (``Path`` / ``str``), or
                      ``None`` to use the repo default. The trend arrow is COMPUTED
                      from it (never painted); an absent/empty ledger → ``▬ baseline``.
    ``fence_state`` — THIS run's mechanical fence facts (the block Q1.4a emits into
                      ``run_summary.yaml``), passed in as plain data; ``None`` /
                      ``{"status": "unavailable"}`` → an honest per-run marker.

    Two clearly-labelled sections (consensus rule #1): **"This run" (facts)** carries
    ``fence_state``; **"Project (not this run)"** carries Band / ranked-leaks / trend
    — so a project grade is never read as a per-run claim. NEVER raises: an outer
    guard degrades the whole projection to a minimal honest marker as a last resort.
    """
    # Each section renders under its OWN guard (FIX-2) so one section's failure never
    # drops the other — "a bad scorecard degrades the Project section only".
    fence_body = _try_section(_render_fence_state, _FENCE_STATE_UNAVAILABLE, fence_state)
    project_body = _try_section(_render_project, _SCORECARD_UNAVAILABLE, block, history)
    try:
        parts = [
            "## Quality Scorecard — Final Report",
            "",
            "### This run (facts)",
            "",
            "_Mechanical fence facts this run actually emitted — not a project grade._",
            "",
            fence_body,
            "",
            "### Project (not this run)",
            "",
            "_Project quality posture — Band, ranked leaks, trend. NOT a claim about this run._",
            "",
            project_body,
        ]
        return "\n".join(parts)
    except Exception:  # noqa: BLE001 — a final report must NEVER fail over the projection
        return (
            "## Quality Scorecard — Final Report\n\n"
            f"{_SCORECARD_UNAVAILABLE}\n\n{_FENCE_STATE_UNAVAILABLE}"
        )
