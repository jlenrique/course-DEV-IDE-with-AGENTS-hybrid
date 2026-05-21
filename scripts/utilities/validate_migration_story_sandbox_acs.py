#!/usr/bin/env python
"""Validate migration story ACs against the dev-agent sandbox inventory.

Enforces the rule "verify via shipped deps, not operator CLIs":
- Dev-agent ACs must not invoke CLIs that aren't on the dev-agent session PATH
  (docker, psql, aws, gh, kubectl, etc.).
- Operator-gated ACs may invoke any CLI — those run on the operator's machine
  and evidence is pasted into Completion Notes once at story closure.

Exit 0 = clean. Exit 1 = at least one violation; exit 2 = usage/IO error.

Classification heuristic for AC blocks:
- Markers "(operator-gated)", "AC-*-B", "**When** the **operator**",
  or "operator (not the dev agent)" => operator-gated.
- Everything else under `## Acceptance Criteria` is dev-agent by default
  (stricter default; operator-gated must be explicit).

Scans shell code fences and inline backtick commands. Matches forbidden CLIs
as the first token of a command, including after |, &&, ||, ;, $( or `.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "docs" / "dev-guide" / "migration-ac-sandbox-inventory.json"

AC_HEADER_RE = re.compile(r"^##+\s*Acceptance Criteria\b", re.MULTILINE)
NEXT_HEADER_RE = re.compile(r"^##+\s+\S", re.MULTILINE)

OPERATOR_GATED_MARKERS = (
    "(operator-gated",
    "operator-gated — ",
    "operator-gated:",
    "the **operator** (not",
    "the operator (not the dev agent)",
    "ac-postgres-b",
    "ac-b ",
    "ac-b:",
    "ac-b(",
    "-b (operator-gated",
)

DEV_AGENT_RESET_MARKERS = (
    "(dev-agent-executable",
    "dev-agent-executable — ",
    "dev-agent-executable:",
    "ac-postgres-a",
    "ac-a ",
    "ac-a:",
    "ac-a(",
    "-a (dev-agent",
)

COMMAND_SEPARATORS = re.compile(r"[|;&]{1,2}|\$\(|\`|^|\n")


class Violation(NamedTuple):
    story_path: Path
    line: int
    cli: str
    reason: str
    snippet: str


def load_inventory() -> dict:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def extract_ac_section(text: str) -> tuple[str, int] | None:
    """Return (ac_section_text, start_line_in_file) or None if not found."""
    header = AC_HEADER_RE.search(text)
    if not header:
        return None
    start = header.end()
    next_header = NEXT_HEADER_RE.search(text, pos=start)
    end = next_header.start() if next_header else len(text)
    section = text[start:end]
    start_line = text[:start].count("\n") + 1
    return section, start_line


def split_ac_blocks(section: str) -> list[tuple[str, int]]:
    """Split AC section into blocks. Each block is (text, relative_start_line).

    A block boundary is a blank line followed by "**Given**", "**AC-",
    a markdown header, or end-of-section. Simpler and good enough:
    split on blank-line groups.
    """
    blocks: list[tuple[str, int]] = []
    lines = section.splitlines()
    buf: list[str] = []
    buf_start = 0
    for idx, line in enumerate(lines):
        if not line.strip():
            if buf:
                blocks.append(("\n".join(buf), buf_start))
                buf = []
            continue
        if not buf:
            buf_start = idx
        buf.append(line)
    if buf:
        blocks.append(("\n".join(buf), buf_start))
    return blocks


def classify_block(block_text: str, current_mode: str) -> str:
    """Return 'operator' or 'dev-agent'. Mode sticks across paragraphs
    until an explicit reset marker appears — this lets a header paragraph
    like '**AC-Postgres-B (operator-gated):**' carry over to the following
    Given/When/Then paragraphs that inherit it.
    """
    lowered = block_text.lower()
    for marker in OPERATOR_GATED_MARKERS:
        if marker in lowered:
            return "operator"
    for marker in DEV_AGENT_RESET_MARKERS:
        if marker in lowered:
            return "dev-agent"
    return current_mode


def extract_shell_commands(block_text: str) -> list[tuple[str, int]]:
    """Pull shell-ish command strings out of a block.

    Returns list of (command_line, line_offset_within_block).
    Sources: ``` fenced blocks (any language; we scan all) AND inline `...`
    commands. Line offset is 1-based within the block.
    """
    commands: list[tuple[str, int]] = []
    lines = block_text.splitlines()
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if stripped and not stripped.startswith("#"):
                commands.append((stripped, idx))
            continue
        # Inline backticks: capture `...` substrings
        for m in re.finditer(r"`([^`\n]+)`", line):
            cmd = m.group(1).strip()
            # Skip non-shell inlines: path fragments, keywords, markdown refs.
            # Heuristic: must contain a space OR start with a known-CLI prefix.
            if " " in cmd or re.match(r"^[a-zA-Z_][\w.-]*\s*$", cmd):
                commands.append((cmd, idx))
    return commands


def first_tokens_of_command(cmd: str) -> list[str]:
    """Return every token that occupies a 'first-of-invocation' position.

    Splits on |, ||, &&, ;, $(, `. Each segment's first non-empty whitespace
    token counts.
    """
    # Replace separators with a single sentinel, then split
    segments = re.split(r"\|{1,2}|&{1,2}|;|\$\(|`", cmd)
    tokens: list[str] = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        # Strip leading env-var assignments like FOO=bar BAZ=x cmd ...
        parts = seg.split()
        i = 0
        while i < len(parts) and re.match(r"^[A-Z_][A-Z0-9_]*=", parts[i]):
            i += 1
        if i < len(parts):
            tokens.append(parts[i])
    return tokens


def check_story(path: Path, inventory: dict) -> list[Violation]:
    text = path.read_text(encoding="utf-8")
    ac = extract_ac_section(text)
    if ac is None:
        return []
    section, section_start_line = ac
    forbidden = inventory.get("dev_agent_forbidden", {})
    warn = inventory.get("flag_with_warning", {})
    violations: list[Violation] = []

    current_mode = "dev-agent"
    for block_text, block_start_rel in split_ac_blocks(section):
        current_mode = classify_block(block_text, current_mode)
        if current_mode == "operator":
            continue
        for cmd, cmd_line_in_block in extract_shell_commands(block_text):
            for tok in first_tokens_of_command(cmd):
                # Normalize: strip quotes and path prefix (e.g. "./bin/docker" -> "docker"
                # but we only forbid by command name, not path — keep basename)
                base = tok.strip("\"'")
                base = base.split("/")[-1].split("\\")[-1]
                if base in forbidden:
                    line = section_start_line + block_start_rel + cmd_line_in_block
                    violations.append(
                        Violation(
                            story_path=path,
                            line=line,
                            cli=base,
                            reason=forbidden[base],
                            snippet=cmd[:140],
                        )
                    )
                elif base in warn:
                    line = section_start_line + block_start_rel + cmd_line_in_block
                    violations.append(
                        Violation(
                            story_path=path,
                            line=line,
                            cli=f"{base} (warning)",
                            reason=warn[base],
                            snippet=cmd[:140],
                        )
                    )
    return violations


def format_violations(violations: list[Violation]) -> str:
    if not violations:
        return ""
    lines = [f"FAIL — {len(violations)} sandbox-AC violation(s):"]
    for v in violations:
        lines.append(f"  {v.story_path}:{v.line}  [{v.cli}]")
        lines.append(f"    cmd: {v.snippet}")
        lines.append(f"    reason: {v.reason}")
        lines.append(
            "    fix: move this AC to an operator-gated block (mark "
            "'(operator-gated)' or 'AC-*-B'), OR replace the CLI with a shipped "
            "Python dep (psycopg / boto3 / PyGithub / httpx / etc.) and make "
            "the test pytest.skip(...) when unreachable."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate migration story ACs do not assume operator-side CLIs."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Story spec markdown file(s) to validate.",
    )
    parser.add_argument(
        "--inventory",
        default=str(INVENTORY_PATH),
        help="Path to sandbox inventory JSON.",
    )
    args = parser.parse_args(argv)

    try:
        inventory_path = Path(args.inventory)
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"ERROR: cannot read inventory: {exc}", file=sys.stderr)
        return 2

    all_violations: list[Violation] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            print(f"ERROR: story file not found: {path}", file=sys.stderr)
            return 2
        all_violations.extend(check_story(path, inventory))

    if all_violations:
        print(format_violations(all_violations))
        return 1
    print(f"PASS — no sandbox-AC violations across {len(args.paths)} story file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
