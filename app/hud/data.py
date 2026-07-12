"""Projection reader for the HUD view (Story 35.4; ADs 6/8/3/4/12/16).

The ONLY reader on the HUD path. It takes an **explicit** run-dir path (the
injection seam L2 fixtures require — no ambient discovery, no coordination.db,
no run.json parse, no mtime-newest fallback: that fallback is exactly the
April wrong-run defect AD-8 kills). It reads the projection file open-read-
close in one gulp and parses it through the contract's
``read_operator_surface_lenient`` — never the strict producer model (AD-4:
consumers are forbidden from strict-parsing so the HUD survives additive
evolution instead of white-screening).

Public surface:

* :func:`read_operator_surface` — parsed ``Projection | Unrecognized | None``
  (``None`` iff the file is absent).
* :func:`read_snapshot` — the byte snapshot + mtime + parsed value in one
  read, so the server can serve the RAW file bytes (zero-lie) while still
  deriving the ETag / identity guard from the parsed value.
* :func:`projection_etag` — the ``<schema_version>:<seq>`` ETag (AD-6); an
  ``unrecognized:<mtime_ns>`` ETag for an unparseable/unknown snapshot so the
  poll loop still cycles when the file changes on disk.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    Unrecognized,
    read_operator_surface_lenient,
)

#: The single projection filename inside a run dir (AD-1 naming convention).
PROJECTION_FILENAME = "operator-surface.json"


@dataclass(frozen=True)
class ProjectionSnapshot:
    """One open-read-close read of the projection file.

    ``raw`` is the exact bytes on disk (what the server serves — zero-lie).
    ``parsed`` is the lenient-reader result over those same bytes (never a
    second read, so it can never disagree with ``raw``). ``mtime_ns`` feeds
    the fallback ETag for unparseable/unknown snapshots.
    """

    raw: bytes
    mtime_ns: int
    parsed: OperatorSurfaceProjection | Unrecognized


def projection_path(run_dir: Path | str) -> Path:
    """Return the explicit projection-file path for ``run_dir`` (no discovery)."""
    return Path(run_dir) / PROJECTION_FILENAME


def read_snapshot(run_dir: Path | str) -> ProjectionSnapshot | None:
    """Open-read-close the projection once; parse from those same bytes.

    Returns ``None`` iff the projection file is absent (AD-2 consumers never
    hold a handle across polls; this reads then closes immediately). Any other
    read error surfaces as an ``Unrecognized`` snapshot rather than a raise,
    so the view never white-screens (AD-4 fail-loud-but-render).
    """
    path = projection_path(run_dir)
    try:
        with path.open("rb") as handle:
            raw = handle.read()
            mtime_ns = os.fstat(handle.fileno()).st_mtime_ns
    except FileNotFoundError:
        return None
    except OSError as exc:
        # Present-but-unreadable (permission, is-a-directory, …): honest
        # Unrecognized with mtime 0 so the ETag still exists but does not lie
        # about a schema/seq we could not read.
        reason = f"unreadable projection ({type(exc).__name__})"
        return ProjectionSnapshot(
            raw=b"",
            mtime_ns=0,
            parsed=Unrecognized(reason=reason, raw_value=None),
        )
    return ProjectionSnapshot(
        raw=raw,
        mtime_ns=mtime_ns,
        parsed=read_operator_surface_lenient(raw),
    )


def read_operator_surface(
    run_dir: Path | str,
) -> OperatorSurfaceProjection | Unrecognized | None:
    """Explicit-path projection reader (AD-12 injection seam).

    * absent file -> ``None``
    * garbage / unknown schema_version / unknown status -> ``Unrecognized``
    * valid v1 (incl. future ADDED fields) -> ``OperatorSurfaceProjection``

    Never raises (the lenient reader guarantee, AD-4).
    """
    snapshot = read_snapshot(run_dir)
    if snapshot is None:
        return None
    return snapshot.parsed


def projection_etag(
    parsed: OperatorSurfaceProjection | Unrecognized | None,
    *,
    mtime_ns: int | None = None,
) -> str:
    """Compute the ETag (AD-6): ``<schema_version>:<seq>``.

    For a parsed projection the ETag is content-derived (``schema_version`` +
    the write counter ``seq`` that bumps on EVERY write incl. freshness ticks
    — never mtime+size, whose granularity would silently skip same-size
    rewrites). For an ``Unrecognized``/absent snapshot there is no trustworthy
    ``seq``, so the ETag is ``unrecognized:<mtime_ns>`` — still changes when
    the file changes on disk, so the poll loop keeps cycling toward recovery.
    """
    if isinstance(parsed, OperatorSurfaceProjection):
        return f"{parsed.schema_version}:{parsed.seq}"
    return f"unrecognized:{mtime_ns if mtime_ns is not None else 0}"


__all__ = [
    "PROJECTION_FILENAME",
    "ProjectionSnapshot",
    "projection_etag",
    "projection_path",
    "read_operator_surface",
    "read_snapshot",
]
