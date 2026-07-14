"""Shared fail-loud reader: extracted corpus content for planner prompts.

Trial-3 cycle-2 content-plane root cause (2026-06-12): irene_pass1 and cd
received Texas's bundle *metadata* (paths, word counts) through the two
edges Ratchet-D had QUARANTINED as un-contracted — never the extracted
corpus text. With no source in sight, the planner LLMs confabulated a
plausible lesson plan from their reference docs' domain, and the §06→§07
chain faithfully rendered the wrong course. Absence of source content is
a contract violation, never a planning license (S0 fail-loud policy).

``SourceBundleError`` is a ``SpecialistDispatchError``: a failure here
error-pauses the trial for ``trial recover`` instead of killing the cycle.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any

from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)
from app.specialists.dispatch_errors import SpecialistDispatchError


class SourceBundleError(SpecialistDispatchError):
    """Raised when the extracted source corpus cannot be obtained."""


_SLIDE_REF = re.compile(r"^slide-[1-9][0-9]*-.+\.md$")
_SOURCE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
_LOCAL_PROVENANCE_KINDS = frozenset({"local_file", "pdf", "docx", "md"})
_REQUIRED_PUBLISHED_ARTIFACTS = frozenset(
    {
        "extracted.md",
        "metadata.json",
        "extraction-report.yaml",
        "ingestion-evidence.md",
        "result.yaml",
    }
)


@dataclass(frozen=True)
class ExtractedPrimarySection:
    """One metadata-bound primary section in Texas's extracted projection."""

    source_id: str
    ref: str
    section_title: str
    source_content_digest: str
    extracted_content_digest: str
    heading_start: int
    content_start: int
    end: int
    body: str


@dataclass(frozen=True)
class MarkdownLine:
    """One structurally classified CommonMark line with source offsets."""

    text: str
    start: int
    end: int
    heading_level: int | None
    heading_text: str | None
    is_literal: bool
    is_table: bool
    is_structural: bool
    container_key: tuple[int, int | None]


_BLOCKQUOTE_PREFIX = re.compile(r"^(?: {0,3}>[ \t]?)+")
_ONE_BLOCKQUOTE_PREFIX = re.compile(r"^ {0,3}>[ \t]?")
_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_HTML_LITERAL_OPEN = re.compile(r"^ {0,3}<(pre|script|style|textarea)(?:\s|>)", re.I)
_HTML_BLOCK_OPEN = re.compile(
    r"^ {0,3}<(address|article|aside|base|basefont|blockquote|body|caption|center|"
    r"col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|"
    r"footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|"
    r"link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|"
    r"section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul)(?:\s|>|/)",
    re.I,
)
_HTML_COMMENT_OPEN = re.compile(r"^ {0,3}<!--")
_HTML_PROCESSING_OPEN = re.compile(r"^ {0,3}<\?")
_HTML_DECLARATION_OPEN = re.compile(r"^ {0,3}<![A-Z]")
_HTML_CDATA_OPEN = re.compile(r"^ {0,3}<!\[CDATA\[")
_HTML_GENERIC_TAG = re.compile(
    r"^ {0,3}</?[A-Za-z][A-Za-z0-9-]*(?:\s+[^<>]*)?/?>\s*$"
)
_HORIZONTAL_RULE = re.compile(
    r"^ {0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$"
)
_REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*\S+")
_IMAGE_ONLY = re.compile(r"^ {0,3}!\[[^\]]*\]\([^)]*\)\s*$")
_INLINE_CODE_ONLY = re.compile(r"^ {0,3}`+[^`]*`+\s*$")
_LINK_ONLY = re.compile(r"^ {0,3}\[[^\]]*\]\([^)]*\)\s*$")
_BARE_URL = re.compile(r"^ {0,3}(?:https?|ftp)://\S+\s*$", re.I)
_TABLE_DELIMITER = re.compile(
    r"^ {0,3}\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$"
)
_TABLE_ROW = re.compile(r"^ {0,3}\|?.*\|.*\|?\s*$")
_SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)\s*$")
_LIST_MARKER = re.compile(r"^ {0,3}(?P<marker>[-+*]|\d{1,9}[.)])")


@dataclass(frozen=True)
class _ListPrefixMatch:
    marker: str
    marker_start: int
    marker_end: int
    prefix_end: int
    content_column: int
    empty: bool


def _markdown_column(text: str, end: int | None = None) -> int:
    column = 0
    for char in text[:end]:
        column += 4 - (column % 4) if char == "\t" else 1
    return column


def expand_markdown_tabs(text: str) -> str:
    expanded: list[str] = []
    column = 0
    for char in text:
        if char == "\t":
            spaces = 4 - (column % 4)
            expanded.append(" " * spaces)
            column += spaces
        else:
            expanded.append(char)
            column = 0 if char in "\r\n" else column + 1
    return "".join(expanded)


def _leading_markdown_position(text: str) -> tuple[int, int]:
    index = len(text) - len(text.lstrip(" \t"))
    return index, _markdown_column(text, index)


def _index_at_markdown_column(text: str, target: int) -> int:
    column = 0
    for index, char in enumerate(text):
        if char not in " \t" or column >= target:
            return index
        column += 4 - (column % 4) if char == "\t" else 1
        if column >= target:
            return index + 1
    return len(text)


def _match_list_prefix(text: str) -> _ListPrefixMatch | None:
    marker_match = _LIST_MARKER.match(text)
    if marker_match is None:
        return None
    marker_end = marker_match.end("marker")
    if marker_end == len(text) or not text[marker_end:].strip(" \t"):
        return _ListPrefixMatch(
            marker=marker_match.group("marker"),
            marker_start=marker_match.start("marker"),
            marker_end=marker_end,
            prefix_end=len(text),
            content_column=_markdown_column(text, marker_end) + 1,
            empty=True,
        )
    if text[marker_end] not in " \t":
        return None
    marker_column = _markdown_column(text, marker_end)
    whitespace_end = marker_end
    while whitespace_end < len(text) and text[whitespace_end] in " \t":
        whitespace_end += 1
    padding_columns = _markdown_column(text, whitespace_end) - marker_column
    prefix_end = marker_end + 1 if padding_columns > 4 else whitespace_end
    return _ListPrefixMatch(
        marker=marker_match.group("marker"),
        marker_start=marker_match.start("marker"),
        marker_end=marker_end,
        prefix_end=prefix_end,
        content_column=(
            marker_column + 1
            if padding_columns > 4
            else _markdown_column(text, prefix_end)
        ),
        empty=False,
    )


def scan_markdown_lines(text: str) -> tuple[MarkdownLine, ...]:
    """Classify Markdown without interpreting headings inside literal blocks."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    result: list[MarkdownLine] = []
    physical_lines = normalized.splitlines(keepends=True)
    expanded_lines = [
        expand_markdown_tabs(physical.rstrip("\n")) for physical in physical_lines
    ]
    visible_lines = [_BLOCKQUOTE_PREFIX.sub("", line) for line in expanded_lines]
    blockquote_depths = [
        (_BLOCKQUOTE_PREFIX.match(line).group(0).count(">"))
        if _BLOCKQUOTE_PREFIX.match(line)
        else 0
        for line in expanded_lines
    ]
    table_lines: set[int] = set()
    for index, line in enumerate(visible_lines):
        if not _TABLE_DELIMITER.fullmatch(line):
            continue
        table_lines.add(index)
        if (
            index > 0
            and blockquote_depths[index - 1] == blockquote_depths[index]
            and _TABLE_ROW.fullmatch(visible_lines[index - 1])
        ):
            table_lines.add(index - 1)
        cursor_index = index + 1
        while (
            cursor_index < len(physical_lines)
            and blockquote_depths[cursor_index] == blockquote_depths[index]
            and _TABLE_ROW.fullmatch(visible_lines[cursor_index])
        ):
            table_lines.add(cursor_index)
            cursor_index += 1
    cursor = 0
    fence: tuple[str, int, int, int | None] | None = None
    html_close: re.Pattern[str] | None = None
    html_blank_ends = False
    html_depth: int | None = None
    html_list_id: int | None = None
    paragraph_active = False
    prior_depth = 0
    list_stack: list[tuple[int, int, int, int, int]] = []
    list_id_counter = 0
    prior_list_id: int | None = None
    for line_index, physical in enumerate(physical_lines):
        line = physical[:-1] if physical.endswith("\n") else physical
        expanded_line = expanded_lines[line_index]
        raw_depth = blockquote_depths[line_index]
        active_literal_depth = fence[2] if fence is not None else html_depth
        literal_container_stays = bool(
            active_literal_depth is not None and raw_depth >= active_literal_depth
        )
        if active_literal_depth is not None and not literal_container_stays:
            fence = None
            html_close = None
            html_blank_ends = False
            html_depth = None
            html_list_id = None
            active_literal_depth = None
        if active_literal_depth is not None:
            visible = expanded_line
            for _ in range(active_literal_depth):
                visible = _ONE_BLOCKQUOTE_PREFIX.sub("", visible, count=1)
            depth = active_literal_depth
        else:
            raw_visible = _BLOCKQUOTE_PREFIX.sub("", expanded_line)
            raw_list_prefix = _match_list_prefix(raw_visible)
            list_interrupts = False
            if raw_list_prefix is not None:
                raw_marker = raw_list_prefix.marker
                list_interrupts = (
                    not raw_marker[0].isdigit()
                    or int(raw_marker[:-1]) == 1
                )
            lazy_interrupt = bool(
                not raw_visible.strip()
                or _FENCE_OPEN.match(raw_visible)
                or list_interrupts
                or re.match(r"^ {0,3}#{1,6}[ \t]+", raw_visible)
                or _HORIZONTAL_RULE.fullmatch(raw_visible)
                or _HTML_LITERAL_OPEN.match(raw_visible)
                or _HTML_COMMENT_OPEN.match(raw_visible)
                or _HTML_PROCESSING_OPEN.match(raw_visible)
                or _HTML_CDATA_OPEN.match(raw_visible)
                or _HTML_DECLARATION_OPEN.match(raw_visible)
                or _HTML_BLOCK_OPEN.match(raw_visible)
            )
            if raw_depth < prior_depth and paragraph_active and not lazy_interrupt:
                visible = expanded_line
                depth = prior_depth
            else:
                visible = raw_visible
                depth = raw_depth
        if raw_depth > prior_depth and list_stack:
            while list_stack and raw_depth > list_stack[-1][4]:
                entering_surface = expanded_line
                for _ in range(list_stack[-1][4]):
                    entering_surface = _ONE_BLOCKQUOTE_PREFIX.sub(
                        "", entering_surface, count=1
                    )
                quote_marker = entering_surface.find(">")
                if quote_marker < 0 or _markdown_column(
                    entering_surface, quote_marker
                ) >= list_stack[-1][1]:
                    break
                list_stack.pop()
        if depth != prior_depth:
            paragraph_active = False
        prior_depth = depth
        while list_stack and list_stack[-1][4] > depth:
            list_stack.pop()
        _leading_index, leading_column = _leading_markdown_position(visible)
        stripped = visible.strip()
        literal_active = fence is not None or html_close is not None
        literal_list_id = fence[3] if fence is not None else html_list_id
        literal_stays = literal_active
        literal_indent: int | None = None
        if literal_active and literal_list_id is not None:
            literal_entry = next(
                (entry for entry in reversed(list_stack) if entry[3] == literal_list_id),
                None,
            )
            if literal_entry is None:
                literal_stays = False
            else:
                literal_indent = literal_entry[1]
                literal_stays = not (
                    stripped and leading_column < literal_entry[1]
                )
        if literal_active and not literal_stays:
            fence = None
            html_close = None
            html_blank_ends = False
            html_depth = None
            html_list_id = None
            literal_active = False

        list_prefix = None if literal_active else _match_list_prefix(visible)
        if list_prefix is not None and paragraph_active:
            marker = list_prefix.marker
            if marker[0].isdigit() and int(marker[:-1]) != 1:
                list_prefix = None
        if literal_active:
            line_list_id = literal_list_id
            container_visible = (
                visible[_index_at_markdown_column(visible, literal_indent) :]
                if literal_indent is not None and leading_column >= literal_indent
                else visible
            )
        else:
            if list_prefix is not None:
                marker_indent = _markdown_column(visible, list_prefix.marker_start)
                while (
                    list_stack
                    and list_stack[-1][4] == depth
                    and marker_indent < list_stack[-1][1]
                ):
                    list_stack.pop()
                list_id_counter += 1
                content_index = list_prefix.prefix_end
                content_indent = list_prefix.content_column
                list_stack.append(
                    (
                        marker_indent,
                        content_indent,
                        content_index,
                        list_id_counter,
                        depth,
                    )
                )
            elif stripped:
                interrupts_paragraph = bool(
                    _FENCE_OPEN.match(visible)
                    or re.match(r"^ {0,3}#{1,6}[ \t]+", visible)
                    or _HORIZONTAL_RULE.fullmatch(visible)
                    or _HTML_LITERAL_OPEN.match(visible)
                    or _HTML_COMMENT_OPEN.match(visible)
                    or _HTML_PROCESSING_OPEN.match(visible)
                    or _HTML_CDATA_OPEN.match(visible)
                    or _HTML_DECLARATION_OPEN.match(visible)
                    or _HTML_BLOCK_OPEN.match(visible)
                )
                if not (paragraph_active and not interrupts_paragraph):
                    while (
                        list_stack
                        and list_stack[-1][4] == depth
                        and leading_column < list_stack[-1][1]
                    ):
                        list_stack.pop()
            line_list_id = list_stack[-1][3] if list_stack else None
            content_indent = (
                list_stack[-1][1]
                if list_stack and list_stack[-1][4] == depth
                else None
            )
            if list_prefix is not None:
                container_visible = visible[list_prefix.prefix_end :]
            elif content_indent is not None and leading_column >= content_indent:
                container_visible = visible[
                    _index_at_markdown_column(visible, content_indent) :
                ]
            else:
                container_visible = visible
        if line_list_id != prior_list_id:
            paragraph_active = False
        prior_list_id = line_list_id
        is_fence_line = False
        in_literal = fence is not None or html_close is not None
        if fence is not None:
            char, minimum, _depth, _list_indent = fence
            if re.fullmatch(
                rf" {{0,3}}{re.escape(char)}{{{minimum},}}[ \t]*",
                container_visible,
            ):
                fence = None
                is_fence_line = True
        elif html_close is not None:
            if html_close.search(visible) or (html_blank_ends and not stripped):
                html_close = None
                html_blank_ends = False
                html_depth = None
                html_list_id = None
        else:
            opener = _FENCE_OPEN.match(container_visible)
            if opener is not None and not (
                opener.group(1).startswith("`") and "`" in opener.group(2)
            ):
                fence = (
                    opener.group(1)[0],
                    len(opener.group(1)),
                    depth,
                    line_list_id,
                )
                is_fence_line = True
                in_literal = True
            else:
                html = _HTML_LITERAL_OPEN.match(container_visible)
                if html is not None:
                    html_close = re.compile(rf"</{html.group(1)}\s*>", re.I)
                    html_depth = depth
                    html_list_id = line_list_id
                    in_literal = True
                    if html_close.search(container_visible[html.end() :]):
                        html_close = None
                elif _HTML_COMMENT_OPEN.match(container_visible):
                    html_close = re.compile(r"-->")
                    html_depth = depth
                    html_list_id = line_list_id
                    in_literal = True
                    if "-->" in container_visible[container_visible.index("<!--") + 4 :]:
                        html_close = None
                elif _HTML_PROCESSING_OPEN.match(container_visible):
                    html_close = re.compile(r"\?>")
                    html_depth = depth
                    html_list_id = line_list_id
                    in_literal = True
                    if "?>" in container_visible:
                        html_close = None
                elif _HTML_CDATA_OPEN.match(container_visible):
                    html_close = re.compile(r"\]\]>")
                    html_depth = depth
                    html_list_id = line_list_id
                    in_literal = True
                    if "]]>" in container_visible:
                        html_close = None
                elif _HTML_DECLARATION_OPEN.match(container_visible):
                    html_close = re.compile(r">")
                    html_depth = depth
                    html_list_id = line_list_id
                    in_literal = True
                    if ">" in container_visible[2:]:
                        html_close = None
                else:
                    html = _HTML_BLOCK_OPEN.match(container_visible)
                    if html is not None or (
                        not paragraph_active
                        and _HTML_GENERIC_TAG.fullmatch(container_visible)
                    ):
                        in_literal = True
                        html_close = re.compile(r"(?!)")
                        html_blank_ends = True
                        html_depth = depth
                        html_list_id = line_list_id
        if html_close is None:
            html_blank_ends = False
            html_depth = None
            html_list_id = None
        is_indented = bool(
            not paragraph_active
            and (
                container_visible.startswith("\t")
                or container_visible.startswith("    ")
            )
        )
        is_literal = in_literal or is_fence_line or is_indented
        heading_level: int | None = None
        heading_text: str | None = None
        is_heading_line = False
        if not is_literal:
            heading = re.match(
                r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$", container_visible
            )
            if heading is not None:
                is_heading_line = True
                if depth == 0 and line_list_id is None:
                    heading_level = len(heading.group(1))
                    heading_text = re.sub(
                        r"[ \t]+#+[ \t]*$", "", heading.group(2)
                    )
        is_table = not is_literal and line_index in table_lines
        is_structural = bool(
            not stripped
            or is_literal
            or is_heading_line
            or _HORIZONTAL_RULE.fullmatch(visible)
            or _REFERENCE_DEFINITION.match(visible)
            or _IMAGE_ONLY.fullmatch(visible)
            or _INLINE_CODE_ONLY.fullmatch(visible)
            or _LINK_ONLY.fullmatch(visible)
            or _BARE_URL.fullmatch(visible)
            or re.fullmatch(r" {0,3}(?:<[^>]+>\s*)+", visible)
            or stripped.startswith("Run ID:")
        )
        result.append(
            MarkdownLine(
                text=line,
                start=cursor,
                end=cursor + len(physical),
                heading_level=heading_level,
                heading_text=heading_text,
                is_literal=is_literal,
                is_table=is_table,
                is_structural=is_structural,
                container_key=(depth, line_list_id),
            )
        )
        paragraph_active = bool(
            stripped
            and not is_literal
            and not is_heading_line
            and not is_table
            and not _HORIZONTAL_RULE.fullmatch(visible)
            and not _REFERENCE_DEFINITION.match(visible)
        )
        cursor += len(physical)
    for index in range(1, len(result)):
        if (
            not result[index].is_literal
            and _SETEXT_UNDERLINE.fullmatch(
                _BLOCKQUOTE_PREFIX.sub(
                    "", expand_markdown_tabs(result[index].text)
                )
            )
            and blockquote_depths[index - 1] == blockquote_depths[index]
            and _BLOCKQUOTE_PREFIX.sub("", result[index - 1].text).strip()
            and not result[index - 1].is_literal
        ):
            result[index - 1] = replace(result[index - 1], is_structural=True)
            result[index] = replace(result[index], is_structural=True)
    return tuple(result)


def extracted_section_digest(body: str) -> str:
    return canonical_extracted_content_digest(body).removeprefix("sha256:")


def parse_extracted_primary_sections(
    *, metadata: dict[str, Any], text: str
) -> tuple[ExtractedPrimarySection, ...]:
    """Parse Texas primary boundaries once for both producer and consumer.

    This function validates identity and boundary topology but deliberately does
    not compare ``extracted_content_digest``.  The hardener calls it while
    finalizing those digests; the consumer performs the comparison afterwards.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    provenance = metadata.get("provenance")
    authority_rows = metadata.get("source_authority")
    if not isinstance(provenance, list) or not provenance:
        raise SourceBundleError(
            "source bundle metadata has no provenance rows",
            tag="source.bundle.metadata-invalid",
        )
    if not isinstance(authority_rows, list) or not authority_rows:
        raise SourceBundleError(
            "source bundle metadata has no digest-bound source rows",
            tag="source.bundle.metadata-invalid",
        )

    authority_by_id: dict[str, tuple[str | None, str, str]] = {}
    for row in authority_rows:
        if not isinstance(row, dict):
            raise SourceBundleError(
                "source bundle source-digest row is invalid",
                tag="source.bundle.metadata-invalid",
            )
        source_id = row.get("source_id")
        source_path = row.get("path")
        source_digest = row.get("source_content_digest")
        extracted_digest = row.get("extracted_content_digest")
        if (
            not isinstance(source_id, str)
            or _SOURCE_ID.fullmatch(source_id) is None
            or (source_path is not None and not isinstance(source_path, str))
            or not isinstance(source_digest, str)
            or len(source_digest) != 64
            or any(char not in "0123456789abcdef" for char in source_digest)
            or not isinstance(extracted_digest, str)
            or len(extracted_digest) != 64
            or any(char not in "0123456789abcdef" for char in extracted_digest)
            or source_id in authority_by_id
        ):
            raise SourceBundleError(
                "source bundle source-digest authority is invalid or ambiguous",
                tag="source.bundle.metadata-invalid",
            )
        authority_by_id[source_id] = (
            source_path if source_path is not None else None,
            source_digest,
            extracted_digest,
        )

    provenance_ids: set[str] = set()
    primary_rows: list[tuple[str, str, str, tuple[str | None, str, str]]] = []
    seen_refs: set[str] = set()
    seen_titles: set[str] = set()
    for row in provenance:
        if not isinstance(row, dict):
            raise SourceBundleError(
                "source bundle provenance carries an invalid row",
                tag="source.bundle.metadata-invalid",
            )
        source_id = row.get("ref_id")
        ref = row.get("ref")
        if (
            isinstance(source_id, str)
            and source_id in provenance_ids
            and row.get("role") == "primary"
        ):
            raise SourceBundleError(
                "source bundle primary refs are ambiguous",
                tag="source.bundle.metadata-invalid",
            )
        if (
            not isinstance(source_id, str)
            or _SOURCE_ID.fullmatch(source_id) is None
            or source_id in provenance_ids
            or not isinstance(ref, str)
            or not ref.strip()
        ):
            raise SourceBundleError(
                "source bundle provenance identity is invalid or ambiguous",
                tag="source.bundle.metadata-invalid",
            )
        provenance_ids.add(source_id)
        if row.get("role") != "primary":
            continue
        normalized_ref = ref.replace("\\", "/")
        title = row.get("section_title")
        authority = authority_by_id.get(source_id)
        local_ref_is_canonical = True
        kind = row.get("kind")
        if kind in _LOCAL_PROVENANCE_KINDS or (
            authority is not None and authority[0] is not None
        ):
            ref_parts = ref.split("/")
            local_ref_is_canonical = (
                ref == normalized_ref
                and not normalized_ref.startswith("/")
                and re.match(r"^[A-Za-z]:/", normalized_ref) is None
                and all(part not in {"", ".", ".."} for part in ref_parts)
                and PurePosixPath(normalized_ref).as_posix() == normalized_ref
            )
        ref_path = PurePosixPath(normalized_ref)
        is_slide_ref = (
            len(ref_path.parts) == 2
            and ref_path.parts[0] == "slides"
            and _SLIDE_REF.fullmatch(ref_path.name) is not None
        )
        if (
            not isinstance(title, str)
            or not title
            or title != title.strip()
            or normalized_ref in seen_refs
            or title in seen_titles
            or authority is None
            or not local_ref_is_canonical
            or (is_slide_ref and kind not in {"local_file", "md"})
            or (is_slide_ref and authority[0] is None)
            or (authority[0] is not None and authority[0] != normalized_ref)
            or (
                kind in _LOCAL_PROVENANCE_KINDS
                and authority[0] is None
            )
        ):
            raise SourceBundleError(
                "source bundle primary identity/path/title authority is invalid",
                tag="source.bundle.metadata-invalid",
            )
        seen_refs.add(normalized_ref)
        seen_titles.add(title)
        primary_rows.append((source_id, normalized_ref, title, authority))

    if not set(authority_by_id).issubset(provenance_ids):
        raise SourceBundleError(
            "source bundle authority contains an unknown provenance identity",
            tag="source.bundle.metadata-invalid",
        )
    if not primary_rows:
        raise SourceBundleError(
            "source bundle metadata has no declared primary rows",
            tag="source.bundle.metadata-invalid",
        )

    positions: dict[str, list[tuple[int, int]]] = {
        title: [] for _source_id, _ref, title, _authority in primary_rows
    }
    for line in scan_markdown_lines(text):
        if line.heading_level == 2 and line.heading_text in positions:
            positions[line.heading_text].append((line.start, line.end))

    markers: list[
        tuple[int, int, str, str, str, tuple[str | None, str, str]]
    ] = []
    for source_id, ref, title, authority in primary_rows:
        found = positions[title]
        if len(found) != 1:
            raise SourceBundleError(
                f"extracted source boundary for {ref!r} is not unique",
                tag="source.bundle.boundary-invalid",
            )
        heading_start, content_start = found[0]
        markers.append(
            (heading_start, content_start, source_id, ref, title, authority)
        )
    markers.sort()
    if [marker[2] for marker in markers] != [row[0] for row in primary_rows]:
        raise SourceBundleError(
            "extracted primary boundary order disagrees with provenance",
            tag="source.bundle.boundary-invalid",
        )

    sections: list[ExtractedPrimarySection] = []
    for index, marker in enumerate(markers):
        heading_start, content_start, source_id, ref, title, authority = marker
        end = markers[index + 1][0] if index + 1 < len(markers) else len(text)
        sections.append(
            ExtractedPrimarySection(
                source_id=source_id,
                ref=ref,
                section_title=title,
                source_content_digest=authority[1],
                extracted_content_digest=authority[2],
                heading_start=heading_start,
                content_start=content_start,
                end=end,
                body=text[content_start:end],
            )
        )
    return tuple(sections)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate metadata key: {key}")
        result[key] = value
    return result


def _read_contained_regular_bytes(root: Path, path: Path, label: str) -> bytes:
    """Read one stable regular file without following bundle-escaping links."""
    try:
        resolved_root = root.resolve(strict=True)
        before = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError(f"{label} is not a singly linked regular file")
        resolved = path.resolve(strict=True)
        resolved.relative_to(resolved_root)
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise OSError(f"{label} changed before read")
            raw = stream.read()
            if len(raw) != opened.st_size:
                raise OSError(f"{label} size disagrees with opened file")
            stream.seek(0)
            if stream.read() != raw:
                raise OSError(f"{label} changed during snapshot")
        after = path.stat(follow_symlinks=False)
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_size,
            before.st_mtime_ns,
            before.st_nlink,
        )
        identity_opened = (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_nlink,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_size,
            after.st_mtime_ns,
            after.st_nlink,
        )
        if identity_before != identity_opened or identity_opened != identity_after:
            raise OSError(f"{label} changed during read")
        return raw
    except (OSError, RuntimeError, ValueError) as exc:
        raise SourceBundleError(
            f"{label} is unreadable or unsafe",
            tag=(
                "source.bundle.metadata-invalid"
                if path.name == "metadata.json"
                else "source.bundle.manifest-invalid"
                if path.name == "manifest.json"
                or path.name in _REQUIRED_PUBLISHED_ARTIFACTS - {"extracted.md"}
                else "source.bundle.extracted-missing"
            ),
        ) from exc


def _published_bundle_snapshots(
    bundle_ref: Path,
) -> tuple[bytes, bytes, dict[str, Any]]:
    """Read the source carrier behind one stable, hash-valid commit marker."""
    manifest_path = bundle_ref / "manifest.json"
    transaction_path = bundle_ref / ".texas-hardening-transaction.json"
    extracted_path = bundle_ref / "extracted.md"
    metadata_path = bundle_ref / "metadata.json"
    if os.path.lexists(transaction_path):
        raise SourceBundleError(
            "source bundle publication transaction is still present",
            tag="source.bundle.manifest-invalid",
        )
    manifest_before = _read_contained_regular_bytes(
        bundle_ref, manifest_path, "source bundle manifest"
    )
    artifact_raw = {
        name: _read_contained_regular_bytes(
            bundle_ref, bundle_ref / name, f"source bundle artifact {name}"
        )
        for name in _REQUIRED_PUBLISHED_ARTIFACTS
    }
    extracted_raw = artifact_raw[extracted_path.name]
    metadata_raw = artifact_raw[metadata_path.name]
    manifest_after = _read_contained_regular_bytes(
        bundle_ref, manifest_path, "source bundle manifest"
    )
    if os.path.lexists(transaction_path):
        raise SourceBundleError(
            "source bundle publication transaction appeared during read",
            tag="source.bundle.manifest-invalid",
        )
    if manifest_before != manifest_after:
        raise SourceBundleError(
            "source bundle manifest changed during publication read",
            tag="source.bundle.manifest-invalid",
        )
    try:
        manifest = json.loads(
            manifest_before.decode("utf-8"), object_pairs_hook=_unique_object
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceBundleError(
            "source bundle manifest is malformed",
            tag="source.bundle.manifest-invalid",
        ) from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
        raise SourceBundleError(
            "source bundle manifest identity is invalid",
            tag="source.bundle.manifest-invalid",
        )
    artifact_rows = manifest.get("artifacts")
    if not isinstance(artifact_rows, list):
        raise SourceBundleError(
            "source bundle manifest has no artifact inventory",
            tag="source.bundle.manifest-invalid",
        )
    by_path: dict[str, dict[str, Any]] = {}
    for row in artifact_rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("path"), str)
            or row["path"] in by_path
        ):
            raise SourceBundleError(
                "source bundle manifest artifact inventory is ambiguous",
                tag="source.bundle.manifest-invalid",
            )
        by_path[row["path"]] = row
    if set(by_path) != _REQUIRED_PUBLISHED_ARTIFACTS:
        raise SourceBundleError(
            "source bundle manifest artifact inventory is incomplete",
            tag="source.bundle.manifest-invalid",
        )
    for name, raw in artifact_raw.items():
        row = by_path.get(name)
        if (
            row is None
            or row.get("sha256") != hashlib.sha256(raw).hexdigest()
            or row.get("size_bytes") != len(raw)
        ):
            raise SourceBundleError(
                f"source bundle manifest does not bind {name}",
                tag="source.bundle.manifest-invalid",
            )
    return extracted_raw, metadata_raw, manifest


def _bundle_reference(payload: dict[str, Any]) -> Path:
    """Resolve the one bundle directory referenced by a delivered payload.

    The bundle reference may sit at the payload top level or inside any
    delivered upstream-output dict (``upstream_output``, ``source_bundle``,
    …) — whichever edge vocabulary the manifest used.
    """
    candidates: list[dict[str, Any]] = [payload]
    candidates.extend(
        value for value in payload.values() if isinstance(value, dict)
    )
    bundle_refs: set[Path] = set()
    for candidate in candidates:
        ref = candidate.get("bundle_reference")
        if isinstance(ref, str) and ref.strip():
            try:
                bundle_refs.add(Path(ref).resolve(strict=True))
            except (OSError, RuntimeError) as exc:
                raise SourceBundleError(
                    "bundle_reference is unreadable or unsafe",
                    tag="source.bundle.reference-missing",
                ) from exc
    if not bundle_refs:
        raise SourceBundleError(
            "no bundle_reference found in payload (top level or delivered "
            f"upstream outputs); payload keys={sorted(payload)}",
            tag="source.bundle.reference-missing",
        )
    if len(bundle_refs) != 1:
        raise SourceBundleError(
            "payload carries conflicting bundle_reference values",
            tag="source.bundle.reference-ambiguous",
        )
    return next(iter(bundle_refs))


def _decode_extracted_source(extracted_raw: bytes, extracted: Path) -> str:
    """Read one non-empty extracted corpus from an already resolved bundle."""
    try:
        text = extracted_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceBundleError(
            f"extracted.md at {extracted.as_posix()} is not UTF-8",
            tag="source.bundle.extracted-missing",
        ) from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        raise SourceBundleError(
            f"extracted.md at {extracted.as_posix()} is empty",
            tag="source.bundle.extracted-empty",
        )
    return text


def _read_extracted_source(bundle_ref: Path) -> str:
    extracted_raw, _metadata_raw, _manifest = _published_bundle_snapshots(bundle_ref)
    return _decode_extracted_source(extracted_raw, bundle_ref / "extracted.md")


def read_extracted_source(payload: dict[str, Any]) -> str:
    """Resolve the Texas bundle referenced by ``payload`` and read extracted.md."""
    return _read_extracted_source(_bundle_reference(payload))


def _extracted_source_sections(
    *, bundle_ref: Path, text: str, metadata_raw: bytes
) -> tuple[Pass1AuthenticatedSourceSection, ...]:
    """Derive exact per-source sections from one already-read corpus snapshot.

    Texas emits one explicit ``## <section_title>`` boundary per primary row.
    Metadata supplies the declared source order, so supporting-source headings
    and source-owned headings never become accidental boundaries.
    """
    try:
        metadata = json.loads(
            metadata_raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceBundleError(
            "source bundle metadata is unreadable",
            tag="source.bundle.metadata-invalid",
        ) from exc
    if not isinstance(metadata, dict):
        raise SourceBundleError(
            "source bundle metadata root is invalid",
            tag="source.bundle.metadata-invalid",
        )
    bounded = parse_extracted_primary_sections(metadata=metadata, text=text)
    sections: list[Pass1AuthenticatedSourceSection] = []
    for section in bounded:
        if extracted_section_digest(section.body) != section.extracted_content_digest:
            raise SourceBundleError(
                f"extracted source body for {section.ref!r} disagrees with Texas authority",
                tag="source.bundle.digest-mismatch",
            )
        ref_path = PurePosixPath(section.ref)
        if not (
            len(ref_path.parts) == 2
            and ref_path.parts[0] == "slides"
            and _SLIDE_REF.fullmatch(ref_path.name) is not None
        ):
            continue
        sections.append(
            Pass1AuthenticatedSourceSection(
                source_id=(
                    f"{section.ref}|sha256:{section.source_content_digest}"
                ),
                source_content_digest=f"sha256:{section.source_content_digest}",
                extracted_content_digest=(
                    f"sha256:{section.extracted_content_digest}"
                ),
                body=section.body,
            )
        )
    if not sections:
        raise SourceBundleError(
            "source bundle metadata has no declared primary slide rows",
            tag="source.bundle.metadata-invalid",
        )
    return tuple(sections)


def read_extracted_source_sections(
    payload: dict[str, Any],
) -> tuple[Pass1AuthenticatedSourceSection, ...]:
    """Return exact per-source sections from one extracted-corpus read."""
    bundle_ref = _bundle_reference(payload)
    extracted_raw, metadata_raw, _manifest = _published_bundle_snapshots(bundle_ref)
    text = _decode_extracted_source(extracted_raw, bundle_ref / "extracted.md")
    return _extracted_source_sections(
        bundle_ref=bundle_ref, text=text, metadata_raw=metadata_raw
    )


def read_extracted_source_with_sections(
    payload: dict[str, Any],
) -> tuple[str, tuple[Pass1AuthenticatedSourceSection, ...]]:
    """Return prompt text and its exact slide sections from identical bytes."""
    bundle_ref = _bundle_reference(payload)
    extracted_raw, metadata_raw, _manifest = _published_bundle_snapshots(bundle_ref)
    text = _decode_extracted_source(extracted_raw, bundle_ref / "extracted.md")
    return text, _extracted_source_sections(
        bundle_ref=bundle_ref, text=text, metadata_raw=metadata_raw
    )


__all__ = [
    "ExtractedPrimarySection",
    "MarkdownLine",
    "SourceBundleError",
    "extracted_section_digest",
    "parse_extracted_primary_sections",
    "read_extracted_source",
    "read_extracted_source_sections",
    "read_extracted_source_with_sections",
    "scan_markdown_lines",
]
