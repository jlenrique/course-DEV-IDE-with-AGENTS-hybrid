"""Story Q1.3 — trend-history substrate (GL-12) + the computed-trend reader.

The scorecard's ``trend`` field must be **computed from a record of past
assessments**, never hand-painted (GL-11). This module owns that record:

  * **The file** — an append-only JSON-lines log at
    ``docs/quality/scorecard-history.jsonl`` (co-located with the prose doc,
    git-tracked). One object per assessment snapshot::

        {"as_of", "dimension", "score", "band",
         "levels": {criterion: score}, "open_leaks", "as_verified"}

    Append-only: file order is chronological (oldest→newest). Q1.3 seeds the
    first (2026-07-19 baseline) entry.

  * **The readers** — :func:`history_entries` (all snapshots for a dimension,
    file order), :func:`newest_snapshot` / :func:`latest_prior_snapshot`
    (selected BY VALIDATED DATE, not raw file order), and
    :func:`trend_from_history` (the trend label the machine block must match).
    **First-run degrade (GL-12):** an absent / empty / all-malformed history — or
    a malformed ``as_of`` on the newest-appended entry — yields ``"baseline"``,
    never a fabricated arrow.

Design contract — **fail-soft and read-only**: a missing file, an unreadable
file, or a malformed JSON line NEVER raises; the malformed line is skipped and
the reader degrades honestly. Stdlib + ``json`` only (**zero** ``app.*`` at
module scope) so ``app.quality`` stays a clean importable leaf (GL-3); the
recursive clean-leaf guard must stay green over this file.

**Honest residual (anti-believed-green, stated plainly):** this ledger records a
JUDGMENT HISTORY, not observed system state. The pins over it enforce a doc↔ledger
mirror, a mandatory append on every doc change, and evidence-gated increases — but
they CANNOT mechanically detect a *coordinated* fabrication of BOTH the doc and
this ledger in the same edit. That residual is a review / governance concern, not
a mechanical guarantee.

Trend vocabulary: ``baseline`` (no prior snapshot to compare), ``rising``
(headline score increased vs the latest prior snapshot), ``falling``
(decreased), ``flat`` (unchanged). The comparison is against the latest *prior*
snapshot by validated date, so the newest snapshot (the current assessment) is
compared to the one dated before it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_HISTORY_REL = "docs/quality/scorecard-history.jsonl"
#: A well-formed ISO calendar date, the only shape we will order/compare on (R4a).
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _repo_root() -> Path:
    # app/quality/history.py -> app/quality -> app -> <repo root>
    return Path(__file__).resolve().parents[2]


def history_path() -> Path:
    return _repo_root() / _HISTORY_REL


def _valid_iso(value: Any) -> bool:
    """True iff ``value`` is a ``YYYY-MM-DD`` string safe to lexicographically
    order (ISO dates sort chronologically). A malformed / missing date is never
    ordered or compared — it degrades the reader honestly."""
    return isinstance(value, str) and bool(_ISO_DATE_RE.match(value))


def history_entries(dimension: str, path: Path | None = None) -> list[dict[str, Any]]:
    """Return every snapshot for ``dimension``, in file order (append-only, so
    oldest→newest by convention).

    Fail-soft: a missing/unreadable file yields ``[]``; a malformed JSON line
    (or a non-mapping / wrong-dimension object) is skipped rather than raising.
    """
    p = path or history_path()
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return []
    entries: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            continue  # skip a malformed line — never raise (fail-soft)
        if isinstance(obj, dict) and obj.get("dimension") == dimension:
            entries.append(obj)
    return entries


def _snapshot_score(snapshot: dict[str, Any]) -> int | None:
    """The headline score of a snapshot as an ``int``, or ``None`` if malformed."""
    score = snapshot.get("score")
    if isinstance(score, bool):  # bool is an int subclass — never a real score
        return None
    return score if isinstance(score, int) else None


def _dated_entries(
    dimension: str, path: Path | None = None
) -> list[tuple[int, dict[str, Any]]]:
    """``(file_index, entry)`` pairs for entries carrying a VALID ISO ``as_of``.

    The file index is retained as a deterministic tie-break when two entries
    share the same ``as_of`` (R4c) — the later-in-file entry wins.
    """
    return [
        (idx, e)
        for idx, e in enumerate(history_entries(dimension, path))
        if _valid_iso(e.get("as_of"))
    ]


def newest_snapshot(dimension: str, path: Path | None = None) -> dict[str, Any] | None:
    """The most-recent snapshot for ``dimension`` BY VALIDATED DATE (not raw file
    order — an out-of-order append cannot mislead), tie-broken by file index.

    Returns ``None`` when no validly-dated snapshot exists.
    """
    dated = _dated_entries(dimension, path)
    if not dated:
        return None
    # max by (validated date, file index): latest date wins; same-date → later-in-file.
    return max(dated, key=lambda t: (t[1]["as_of"], t[0]))[1]


def latest_prior_snapshot(
    dimension: str, as_of: str, path: Path | None = None
) -> dict[str, Any] | None:
    """The most recent snapshot STRICTLY BEFORE ``as_of`` (validated ISO date).

    The current assessment shares the machine block's ``as_of``; the "prior"
    snapshot is therefore the latest validly-dated history entry dated before it.
    Deterministic tie-break by file index. Returns ``None`` when ``as_of`` is
    malformed or no such snapshot exists (honest first-run no-op).
    """
    if not _valid_iso(as_of):
        return None
    prior = [(idx, e) for idx, e in _dated_entries(dimension, path) if e["as_of"] < as_of]
    if not prior:
        return None
    return max(prior, key=lambda t: (t[1]["as_of"], t[0]))[1]


def trend_from_history(dimension: str, path: Path | None = None) -> str:
    """The trend label the machine block's ``trend`` must equal (GL-11).

    Computed from the history log: the newest snapshot's headline score vs the
    latest snapshot dated *before* it. **First-run / fail-soft degrade (GL-12):**
    an absent/empty history, a malformed ``as_of`` on the newest-APPENDED entry,
    fewer than two validly-dated snapshots, or malformed scores → ``"baseline"``.
    """
    entries = history_entries(dimension, path)
    if not entries:
        return "baseline"
    # R4a: if the freshest WRITE (last file line) has a malformed/missing as_of we
    # cannot trust the log — degrade to baseline rather than silently computing a
    # trend off an older entry.
    if not _valid_iso(entries[-1].get("as_of")):
        return "baseline"
    current = newest_snapshot(dimension, path)
    if current is None:
        return "baseline"
    prior = latest_prior_snapshot(dimension, str(current.get("as_of")), path)
    if prior is None:
        return "baseline"
    cur_score = _snapshot_score(current)
    prior_score = _snapshot_score(prior)
    if cur_score is None or prior_score is None:
        return "baseline"  # cannot honestly compare malformed scores
    if cur_score > prior_score:
        return "rising"
    if cur_score < prior_score:
        return "falling"
    return "flat"
