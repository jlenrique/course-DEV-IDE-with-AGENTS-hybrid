"""Forensic preservation CI guard — Murat post-S3 amendment.

Walks `docs/trials/trial-*/postmortem.md`; extracts the do-not-delete paths
from the §"Forensic evidence pointers (do-not-delete paths)" block; asserts
each path exists on disk.

Failure mode protected against: a future cleanup pass running `_artifacts/`
retention logic deletes a referenced path because the postmortem prose was
not enforceable. This guard converts prose into structural enforcement.

Spec: `_bmad-output/planning-artifacts/deferred-inventory.md` entry
`s3-forensic-preservation-ci-guard` (filed at S3 post-review; landed at S5 T3).
Architecture authority: D17 architecture-of-record entry — Crosswalk-vs-Disk
Parity Test Pattern (this is one instance; v5 Crosswalk parity test is another).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRIALS_DIR = REPO_ROOT / "docs" / "trials"

# Section header that introduces the do-not-delete paths block in postmortem.md
FORENSIC_HEADER = "## Forensic evidence pointers (do-not-delete paths)"

# Captures path-like tokens in bullet items: `path/to/thing`
PATH_TOKEN_PATTERN = re.compile(r"`([^`]+)`")


def _extract_forensic_paths(postmortem_text: str) -> list[str]:
    """Extract do-not-delete path-strings from a postmortem.md."""
    if FORENSIC_HEADER not in postmortem_text:
        return []
    body_after_header = postmortem_text.split(FORENSIC_HEADER, 1)[1]
    # Stop at the next `## ` header or end of file
    next_header_match = re.search(r"\n## ", body_after_header)
    if next_header_match:
        body_after_header = body_after_header[: next_header_match.start()]
    paths: list[str] = []
    for match in PATH_TOKEN_PATTERN.finditer(body_after_header):
        token = match.group(1).strip()
        # Ignore tokens that don't look path-like (e.g., command examples)
        # Heuristic: contains a `/` and ends with `.md`/`.json`/`.py`/`.txt`/`.yaml` OR is a directory path
        if "/" in token and not token.startswith("python ") and not token.startswith("pytest ") and "<" not in token and ">" not in token:
            paths.append(token)
    return paths


def _resolve_path(repo_root: Path, path_str: str) -> Path:
    """Resolve a path-string from a postmortem against the repo root."""
    # Strip placeholder markers like <run-id>
    cleaned = re.sub(r"<[^>]+>", "*", path_str)
    return repo_root / cleaned


def test_forensic_evidence_paths_exist_on_disk() -> None:
    """For every postmortem.md, every do-not-delete path must exist on disk.

    Excludes path tokens containing placeholder markers (<run-id>, <bundle-path>)
    because those are template-shape references, not concrete paths.
    """
    if not TRIALS_DIR.is_dir():
        # No trials dir yet (S3 deliverable just landed); test passes vacuously
        return

    postmortems = list(TRIALS_DIR.glob("trial-*/postmortem.md"))
    if not postmortems:
        # No trial instances yet (Trial-3 not launched); test passes vacuously
        return

    missing: list[tuple[str, str]] = []
    for postmortem in postmortems:
        text = postmortem.read_text(encoding="utf-8")
        paths = _extract_forensic_paths(text)
        for path_str in paths:
            # Skip tokens with placeholder markers (template stubs)
            if "<" in path_str or "*" in path_str:
                continue
            # Skip tokens that are command examples (start with python/pytest)
            if path_str.startswith(("python ", "pytest ", "$env:")):
                continue
            target = REPO_ROOT / path_str
            if not target.exists():
                missing.append((postmortem.name, path_str))

    assert not missing, (
        f"Forensic preservation guard caught {len(missing)} stale do-not-delete path(s):\n"
        + "\n".join(f"  {pm}: {p}" for pm, p in missing)
        + "\n\nEither the path was deleted (restore from git history) OR the postmortem entry was incorrectly authored (correct the path token)."
    )
