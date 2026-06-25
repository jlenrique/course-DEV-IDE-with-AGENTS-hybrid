"""DP6 frozen-Gamma reuse gate — pure operand + predicate.

Authority: ``_bmad-output/planning-artifacts/braid-green-light-ratification-2026-06-24.md``
§DP6 (and §6 carried-NIT 2, the Story-0b DP6-enablement task).

The braid's DP6 decision codifies the operator's frozen-deck reuse rule into a
*checkable* path-intersection gate rather than a policy sentence::

    fresh_gamma_required := (git diff --name-only <base>..<head>)
                             ∩ slide_production_paths ≠ ∅

This module is the pure substrate for that gate: it loads the
``slide_production_paths`` operand and exposes side-effect-free predicates. It
does NOT run ``git``, touch the network, or read run records — callers supply the
diff file list (so the helper stays unit-testable against fixture diffs, per the
spec's offline-dev AC requirement).

WHY A STANDALONE CONFIG (not a pipeline-manifest key)
-----------------------------------------------------
``slide_production_paths`` deliberately lives in its own config file
(``state/config/slide-production-paths.yaml``) rather than as a new key in
``state/config/pipeline-manifest.yaml``. Both the legacy ``PipelineManifest``
model (``scripts/utilities/pipeline_manifest.py``) and the upstream graph
manifest (``app/manifest/schema.py``) use ``ConfigDict(extra="forbid")``, so a
new manifest key would force a coordinated two-model schema extension touching
core ``app/manifest`` — disproportionate for an operand only this gate reads.
Standalone config + pure helper keeps the blast radius at zero.

STALE-PACK RULE
---------------
Even when the path intersection is EMPTY, a frozen deck minted by a
``pack_version`` *older* than the current HEAD pack version counts as
``fresh_required`` — the pack prose itself drives slide output, so an old deck
no longer reflects the current pack. See :func:`pack_version_stale`.
"""

from __future__ import annotations

import fnmatch
from collections.abc import Iterable
from pathlib import Path

import yaml

from scripts.utilities.file_helpers import project_root

DEFAULT_PATHS_CONFIG = (
    project_root() / "state" / "config" / "slide-production-paths.yaml"
)


def load_slide_production_paths(path: str | Path | None = None) -> tuple[str, ...]:
    """Load the ``slide_production_paths`` glob set from the standalone config.

    Returns the globs as an immutable tuple. Raises ``ValueError`` if the config
    is malformed (missing/empty ``paths``, or a non-string / blank entry) so a
    corrupt operand fails loud rather than silently permitting reuse.
    """
    config_path = Path(path) if path is not None else DEFAULT_PATHS_CONFIG
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(
            f"{config_path}: expected a YAML mapping at top level, got {type(data).__name__}"
        )
    raw_paths = data.get("paths")
    if not isinstance(raw_paths, list) or not raw_paths:
        raise ValueError(f"{config_path}: 'paths' must be a non-empty list of globs")
    globs: list[str] = []
    for entry in raw_paths:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"{config_path}: each path entry must be a non-empty string")
        # Validate the glob compiles (mirrors the manifest's trigger-path guard).
        fnmatch.translate(entry)
        globs.append(entry)
    return tuple(globs)


def load_current_pack_version(path: str | Path | None = None) -> str | None:
    """Return the ``current_pack_version`` declared in the paths config, if any."""
    config_path = Path(path) if path is not None else DEFAULT_PATHS_CONFIG
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    value = data.get("current_pack_version")
    return value if isinstance(value, str) else None


def _matches_any(diff_file: str, globs: tuple[str, ...]) -> bool:
    # Normalise to forward slashes so Windows-style git output also matches.
    normalised = diff_file.replace("\\", "/").strip()
    return any(fnmatch.fnmatch(normalised, glob) for glob in globs)


def fresh_gamma_required(
    diff_files: Iterable[str],
    *,
    paths: tuple[str, ...] | None = None,
) -> bool:
    """Return ``True`` iff any diff file intersects ``slide_production_paths``.

    ``True`` -> frozen-Gamma reuse is BLOCKED (mint fresh + run no-regression).
    ``False`` -> reuse is permitted (empty intersection); the caller should stamp
    the run record via :func:`reuse_stamp`.

    Pure: no git invocation, no I/O beyond the optional one-time config load.
    """
    globs = paths if paths is not None else load_slide_production_paths()
    return any(_matches_any(diff_file, globs) for diff_file in diff_files)


def pack_version_stale(
    frozen_pack_version: str | None,
    current_pack_version: str | None,
) -> bool:
    """Return ``True`` if a frozen deck's pack version is older than current HEAD.

    A stale frozen deck counts as ``fresh_required`` *even when the path
    intersection is empty* (the pack prose drives slide output, so an old deck no
    longer reflects current production rules). Comparison is conservative:

    - if either version is unknown (``None``), treat as stale (fresh-required) —
      we cannot prove the frozen deck is current, so take the safe direction;
    - otherwise stale iff the versions differ AND ``frozen < current`` under a
      tuple comparison of the numeric ``vN.M`` components (falling back to plain
      string inequality when the shape is non-numeric).
    """
    if frozen_pack_version is None or current_pack_version is None:
        return True
    if frozen_pack_version == current_pack_version:
        return False
    frozen_key = _version_key(frozen_pack_version)
    current_key = _version_key(current_pack_version)
    if frozen_key is None or current_key is None:
        # Non-numeric shape we cannot order: differ => treat as stale (safe).
        return True
    return frozen_key < current_key


def _version_key(version: str) -> tuple[int, ...] | None:
    """Parse a ``vN.M`` / ``N.M`` pack version into an orderable int tuple."""
    core = version.strip()
    if core.startswith(("v", "V")):
        core = core[1:]
    # Keep only the leading dotted-numeric run (ignore any ``-suffix``).
    head = core.split("-", 1)[0]
    parts = head.split(".")
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return None


def reuse_stamp(sha: str) -> str:
    """Return the run-record justification stamp for a permitted frozen reuse.

    Per DP6: an empty-intersection run stamps
    ``gamma: frozen, reuse_justified_by: empty-intersection@<sha>``. This returns
    the ``reuse_justified_by`` value only.
    """
    return f"empty-intersection@{sha}"
