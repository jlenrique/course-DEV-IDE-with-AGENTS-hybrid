"""Generate ``docs/project-context.md`` — a thin generated header over a
hand-authored base doc that is preserved verbatim.

``docs/project-context.md`` is glob-loaded as a persistent fact by ~59 skills,
so it MUST stay at that exact path and no second ``project-context.md`` may be
created anywhere in the tree.

Design (operator-ratified): a THIN generated current-state header ABOVE a
stable ``<!-- BASE-DOC ... -->`` marker; everything from the marker to EOF is
the hand-authored base doc, preserved byte-for-byte.

Two modes:

* BOOTSTRAP (first run — no marker yet, but the base-doc heading
  ``# Project Context: Multi-Agent Course Content Production System`` is
  present): archive the addendum stack ABOVE that heading to
  ``docs/project-context.history.md`` (dated header + verbatim), then rewrite
  ``docs/project-context.md`` = fresh thin header + marker + base doc verbatim.
* STEADY STATE (marker present): regenerate ONLY the text ABOVE the marker;
  preserve the marker and everything below it byte-for-byte.

The thin header is sourced from the latest ``SESSION-HANDOFF.md`` section plus
the current ``### 11.1 You are here`` block of ``docs/STATE-OF-THE-APP.md``.

FAIL-LOUD: a run where NEITHER the marker NOR the base-doc heading is found
prints a named error and exits non-zero WITHOUT overwriting — the base doc is
never dropped.

Usage::

    .venv/Scripts/python.exe scripts/utilities/generate_project_context.py
    .venv/Scripts/python.exe scripts/utilities/generate_project_context.py --check
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parents[2]

BASE_DOC_MARKER = "<!-- BASE-DOC (hand-authored, preserved — do not delete this marker) -->"
BASE_DOC_MARKER_PREFIX = "<!-- BASE-DOC"
BASE_DOC_HEADING = "# Project Context: Multi-Agent Course Content Production System"

_ENV_BRANCH = "GENERATE_VIEW_GIT_BRANCH"
_ENV_HEAD = "GENERATE_VIEW_GIT_HEAD"

_SECTION_RE = re.compile(r"^#\s+Session\s+(?:close|handoff)\b.*$", re.IGNORECASE | re.MULTILINE)


class GenerationError(RuntimeError):
    """Named, fail-loud error surfaced to stderr before a non-zero exit."""


# ---------------------------------------------------------------------------
# Source extraction
# ---------------------------------------------------------------------------


def _git_info(root: Path) -> tuple[str, str]:
    env_branch = os.environ.get(_ENV_BRANCH)
    env_head = os.environ.get(_ENV_HEAD)
    if env_branch and env_head:
        return env_branch, env_head

    def _run(args: list[str]) -> str | None:
        try:
            out = subprocess.run(
                args, cwd=str(root), capture_output=True, text=True, timeout=15
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if out.returncode != 0:
            return None
        return out.stdout.strip() or None

    branch = env_branch or _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    head = env_head or _run(["git", "rev-parse", "--short", "HEAD"]) or "unknown"
    return branch, head


def _latest_handoff(root: Path) -> tuple[str, str]:
    """Return (heading_line, what_is_next_body) from the latest handoff section.

    Missing handoff / missing sections degrade gracefully to placeholders — the
    handoff is not a hard input for project-context (the base doc is the SSOT).
    """
    handoff_path = root / "SESSION-HANDOFF.md"
    if not handoff_path.exists():
        return "(SESSION-HANDOFF.md not found)", ""
    text = handoff_path.read_text(encoding="utf-8")
    matches = list(_SECTION_RE.finditer(text))
    if not matches:
        return "(no session section in SESSION-HANDOFF.md)", ""
    start = matches[0].start()
    end = matches[1].start() if len(matches) > 1 else len(text)
    section = text[start:end]
    heading = section.splitlines()[0].lstrip("# ").strip()
    m = re.search(
        r"^##\s+What is next[^\n]*$(.*?)(?=^#{1,6}\s|\Z)",
        section,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    what_next = m.group(1).strip() if m else ""
    return heading, what_next


def _you_are_here(root: Path) -> str:
    """Extract the current ``### 11.1 You are here`` block (stops at SUPERSEDED)."""
    sota_path = root / "docs" / "STATE-OF-THE-APP.md"
    if not sota_path.exists():
        return ""
    text = sota_path.read_text(encoding="utf-8")
    m = re.search(
        r"^###\s+11\.1\s+You are here[^\n]*$(.*?)(?=^>\s*\*\*\(SUPERSEDED|^#{1,3}\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Header render
# ---------------------------------------------------------------------------


def _render_header(root: Path) -> str:
    branch, head = _git_info(root)
    generated = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
    heading, what_next = _latest_handoff(root)
    you_are_here = _you_are_here(root)

    parts: list[str] = [
        "# Project Context — Current State (GENERATED)",
        "",
        "<!-- GENERATED thin current-state header. Regenerated by "
        "scripts/utilities/generate_project_context.py. Everything from the "
        "BASE-DOC marker to EOF is hand-authored and preserved verbatim. -->",
        "",
        f"**Branch:** `{branch}` · **HEAD (short):** `{head}` · "
        f"**Generated:** {generated}",
        "",
        "## Current Session State",
        "",
        f"Latest session close: **{heading}**",
        "",
    ]
    if what_next:
        parts += ["**What is next:**", "", what_next, ""]
    if you_are_here:
        parts += [
            "## You Are Here (from STATE-OF-THE-APP.md §11.1)",
            "",
            you_are_here,
            "",
        ]
    parts += [
        "> Dated context-addendum history archived to "
        "`docs/project-context.history.md`. The hand-authored base doc is "
        "preserved verbatim below the marker.",
        "",
    ]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Mode dispatch
# ---------------------------------------------------------------------------


def _line_start_of(text: str, index: int) -> int:
    """Return the index of the start of the line containing ``index``."""
    nl = text.rfind("\n", 0, index)
    return 0 if nl == -1 else nl + 1


def build(root: Path) -> tuple[str, str | None]:
    """Return (new_project_context_text, history_text_or_None).

    ``history_text`` is non-None only on the bootstrap split. Raises
    ``GenerationError`` if neither the marker nor the base heading is present.
    """
    target_path = root / "docs" / "project-context.md"
    if not target_path.exists():
        raise GenerationError(
            f"generate_project_context: {target_path} not found — refusing to "
            "create it from scratch (would drop the hand-authored base doc)."
        )
    text = target_path.read_text(encoding="utf-8")
    header = _render_header(root)

    marker_idx = text.find(BASE_DOC_MARKER_PREFIX)
    if marker_idx != -1:
        # STEADY STATE — preserve marker-to-EOF byte-for-byte.
        preserved = text[_line_start_of(text, marker_idx):]
        return header + "\n" + preserved, None

    heading_match = re.search(rf"^{re.escape(BASE_DOC_HEADING)}", text, re.MULTILINE)
    if heading_match is not None:
        # BOOTSTRAP — archive the addendum stack, insert the marker.
        base_start = _line_start_of(text, heading_match.start())
        addendum_stack = text[:base_start]
        base_doc = text[base_start:]
        new_text = header + "\n" + BASE_DOC_MARKER + "\n" + base_doc
        stamp = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
        history = (
            f"# project-context.md — Archived Context Addenda (bootstrapped {stamp})\n"
            "\n"
            "> Verbatim addendum stack lifted above the hand-authored base doc "
            "when `docs/project-context.md` was demoted to a generated view. "
            "This is the archive sibling; it must NOT be named `project-context.md`.\n"
            "\n"
            "---\n"
            "\n"
            f"{addendum_stack.rstrip()}\n"
        )
        return new_text, history

    raise GenerationError(
        "generate_project_context: neither the BASE-DOC marker nor the base-doc "
        f"heading ('{BASE_DOC_HEADING}') was found in docs/project-context.md — "
        "refusing to overwrite (would drop the hand-authored base doc)."
    )


def generate(root: Path, *, check: bool = False) -> Path | None:
    """Build and (unless ``check``) write the target + any history sibling."""
    new_text, history_text = build(root)  # raises on fail-loud condition
    if check:
        return None
    target_path = root / "docs" / "project-context.md"
    if history_text is not None:
        history_path = root / "docs" / "project-context.history.md"
        if history_path.exists():
            # Never lose prior archives — append a fresh dated block.
            prior = history_path.read_text(encoding="utf-8").rstrip()
            history_text = prior + "\n\n---\n\n" + history_text
        history_path.write_text(history_text, encoding="utf-8")
    target_path.write_text(new_text, encoding="utf-8")
    return target_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the thin-header-over-preserved-base docs/project-context.md."
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
        print("generate_project_context: --check OK (would generate cleanly).")
    else:
        print(f"generate_project_context: wrote {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
