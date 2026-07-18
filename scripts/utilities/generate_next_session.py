"""Generate ``next-session-start-here.md`` — a fail-loud convenience view.

This is a GENERATED view, not an authored SSOT. It is (re)built at session
WRAPUP from authoritative sources:

* ``SESSION-HANDOFF.md`` — the LATEST (topmost) session-close section supplies
  the "what is next" and "unresolved issues" prose.
* ``git`` — current branch + short HEAD sha.
* ``_bmad-output/planning-artifacts/deferred-inventory.md`` — a rough deferred
  count (CLAUDE.md mandate).

Contract (parsed by ``scripts/utilities/progress_map.py`` via a case-insensitive
``^##\\s+<heading>`` prefix match): the output MUST carry the Title-Case
headings ``## Immediate Next Action`` and ``## Key Risks / Unresolved Issues``
verbatim (sourced from the shared ``progress_map`` heading constants), plus the
``**Expected class for next session:**`` and deferred-count lines mandated by
CLAUDE.md.

FAIL-LOUD: if ``SESSION-HANDOFF.md`` is missing, no ``# Session`` section is
found, or the latest section has no extractable "what is next" content, the
generator prints a named error to stderr and exits non-zero WITHOUT writing or
overwriting the target — the authored SSOT stays the fallback authority.

Usage::

    .venv/Scripts/python.exe scripts/utilities/generate_next_session.py
    .venv/Scripts/python.exe scripts/utilities/generate_next_session.py --check
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (repo-root derived; --root overrides for hermetic tests)
# ---------------------------------------------------------------------------

_DEFAULT_ROOT = Path(__file__).resolve().parents[2]

# The canonical next-session heading strings live ONCE in progress_map.py (the
# consumer). Import them so producer + consumer cannot drift apart. Ensure the
# repo root is importable when this file is run as a standalone script.
if str(_DEFAULT_ROOT) not in sys.path:
    sys.path.insert(0, str(_DEFAULT_ROOT))
from scripts.utilities.progress_map import (  # noqa: E402
    IMMEDIATE_NEXT_ACTION_HEADING,
    KEY_RISKS_HEADING,
)

DEFAULT_CLASS = "<carry-forward — set at WRAPUP>"

# Env overrides let tests inject deterministic git identity without a real repo.
_ENV_BRANCH = "GENERATE_VIEW_GIT_BRANCH"
_ENV_HEAD = "GENERATE_VIEW_GIT_HEAD"

# Top-level session delimiters in SESSION-HANDOFF.md. Broadened to match ANY
# ``# Session …`` variant (close / Handoff / WRAPUP / Summary / …) so the
# newest section is always the one picked regardless of its suffix.
_SECTION_RE = re.compile(r"^#\s+Session\b.*$", re.IGNORECASE | re.MULTILINE)
# Any top-level (single ``#``) heading — used to assert the FIRST top-level
# heading is a Session section (else an older matching section could be lifted).
_TOP_HEADING_RE = re.compile(r"^#\s+\S[^\n]*$", re.MULTILINE)


class GenerationError(RuntimeError):
    """Named, fail-loud error surfaced to stderr before a non-zero exit."""


# ---------------------------------------------------------------------------
# Source extraction
# ---------------------------------------------------------------------------


def _latest_handoff_section(handoff_text: str) -> str:
    """Return the body of the LATEST (topmost) session section, or raise."""
    matches = list(_SECTION_RE.finditer(handoff_text))
    if not matches:
        raise GenerationError(
            "generate_next_session: no '# Session …' section found in "
            "SESSION-HANDOFF.md (cannot determine latest session)."
        )
    # The newest section MUST be the first top-level heading in the file. If an
    # unrelated `# ` heading precedes it, refuse rather than silently lift an
    # older matching section as if it were current.
    top_headings = list(_TOP_HEADING_RE.finditer(handoff_text))
    if not top_headings or top_headings[0].start() != matches[0].start():
        raise GenerationError(
            "generate_next_session: the first top-level '# ' heading in "
            "SESSION-HANDOFF.md is not a '# Session …' section — refusing to "
            "lift a non-newest section (target NOT overwritten)."
        )
    start = matches[0].start()
    end = matches[1].start() if len(matches) > 1 else len(handoff_text)
    return handoff_text[start:end]


def _extract_subsection(section_text: str, heading: str) -> str:
    """Lift the body under ``## <heading>...`` (case-insensitive prefix match).

    Stops at the next ``##`` heading or end-of-section (matching
    progress_map._extract_section semantics), so ``### sub-steps`` under the
    heading do NOT truncate the body. The HANDOFF file uses sentence-case
    headings (``## What is next`` / ``## Unresolved issues / risks``); this
    reads them case-insensitively.
    """
    pattern = rf"^##\s+{re.escape(heading)}[^\n]*$(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, section_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _git_info(root: Path) -> tuple[str, str]:
    """Return (branch, short_head). Env override wins; else subprocess; else unknown."""
    env_branch = os.environ.get(_ENV_BRANCH)
    env_head = os.environ.get(_ENV_HEAD)
    if env_branch and env_head:
        return env_branch, env_head

    def _run(args: list[str]) -> str | None:
        try:
            out = subprocess.run(
                args,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if out.returncode != 0:
            return None
        return out.stdout.strip() or None

    branch = env_branch or _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    head = env_head or _run(["git", "rev-parse", "--short", "HEAD"]) or "unknown"
    return branch, head


def _deferred_count(deferred_path: Path) -> int | None:
    """Rough LIVE deferred count = ``| **`` register rows BEFORE the archive.

    Rows under ``## Closed Entries — Archived`` are already-closed entries; they
    are excluded so the count reflects the live backlog, not the audit trail.
    """
    if not deferred_path.exists():
        return None
    text = deferred_path.read_text(encoding="utf-8")
    archived = re.search(r"^##\s+Closed Entries", text, re.MULTILINE | re.IGNORECASE)
    region = text[: archived.start()] if archived else text
    return len(re.findall(r"^\|\s*\*\*", region, re.MULTILINE))


def _carry_forward_class(target_path: Path) -> str:
    """Carry an ``**Expected class for next session:**`` value from an existing view."""
    if not target_path.exists():
        return DEFAULT_CLASS
    text = target_path.read_text(encoding="utf-8")
    match = re.search(
        r"^\*\*Expected class for next session:\*\*\s*(.+?)\s*$",
        text,
        re.MULTILINE,
    )
    if match and match.group(1).strip():
        return match.group(1).strip()
    return DEFAULT_CLASS


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def render(
    *,
    what_is_next: str,
    unresolved: str,
    branch: str,
    head: str,
    deferred_count: int | None,
    expected_class: str,
) -> str:
    generated = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
    if deferred_count is None:
        deferred_line = (
            "Consult `_bmad-output/planning-artifacts/deferred-inventory.md` "
            "(register not found at generation time)."
        )
    else:
        deferred_line = (
            "Consult `_bmad-output/planning-artifacts/deferred-inventory.md`. "
            f"Deferred inventory status: ~{deferred_count} register rows "
            "(rough count of `| **…` entries)."
        )
    unresolved_body = unresolved or "_None recorded in the latest handoff section._"

    return (
        "# Next Session — Start Here\n"
        "\n"
        f"**Expected class for next session:** {expected_class}\n"
        "\n"
        f"## {IMMEDIATE_NEXT_ACTION_HEADING}\n"
        "\n"
        f"{what_is_next}\n"
        "\n"
        f"## {KEY_RISKS_HEADING}\n"
        "\n"
        f"{unresolved_body}\n"
        "\n"
        "## Branch Metadata\n"
        "\n"
        f"- Current branch: **`{branch}`**\n"
        f"- HEAD (short): `{head}`\n"
        "\n"
        "## Deferred Inventory Status\n"
        "\n"
        f"{deferred_line}\n"
        "\n"
        "---\n"
        f"_GENERATED by `scripts/utilities/generate_next_session.py` at {generated} "
        "from SESSION-HANDOFF.md (latest section) + `git` + deferred-inventory.md. "
        "Convenience view only — the authored SSOTs (SESSION-HANDOFF.md, "
        "deferred-inventory.md) are the fallback authority._\n"
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build(root: Path) -> str:
    """Read sources under ``root`` and return the rendered view, or raise."""
    handoff_path = root / "SESSION-HANDOFF.md"
    deferred_path = root / "_bmad-output" / "planning-artifacts" / "deferred-inventory.md"
    target_path = root / "next-session-start-here.md"

    if not handoff_path.exists():
        raise GenerationError(
            f"generate_next_session: SESSION-HANDOFF.md not found at {handoff_path} "
            "(cannot generate the next-session view; authored fallback preserved)."
        )

    handoff_text = handoff_path.read_text(encoding="utf-8")
    section = _latest_handoff_section(handoff_text)

    what_is_next = _extract_subsection(section, "What is next")
    if not what_is_next:
        raise GenerationError(
            "generate_next_session: latest SESSION-HANDOFF section has no "
            "extractable '## What is next' content (required input missing; "
            "target NOT overwritten)."
        )
    unresolved = _extract_subsection(section, "Unresolved issues")

    branch, head = _git_info(root)
    deferred_count = _deferred_count(deferred_path)
    expected_class = _carry_forward_class(target_path)

    return render(
        what_is_next=what_is_next,
        unresolved=unresolved,
        branch=branch,
        head=head,
        deferred_count=deferred_count,
        expected_class=expected_class,
    )


def generate(root: Path, *, check: bool = False) -> Path | None:
    """Build and (unless ``check``) write the target. Returns the path written."""
    content = build(root)  # raises GenerationError on any missing required input
    target_path = root / "next-session-start-here.md"
    if check:
        return None
    target_path.write_text(content, encoding="utf-8")
    return target_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the fail-loud next-session-start-here.md view."
    )
    parser.add_argument("--root", type=Path, default=_DEFAULT_ROOT, help="Repo root.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that generation would succeed without writing the target.",
    )
    args = parser.parse_args(argv)

    try:
        result = generate(args.root, check=args.check)
    except GenerationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.check:
        print("generate_next_session: --check OK (would generate cleanly).")
    else:
        print(f"generate_next_session: wrote {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
