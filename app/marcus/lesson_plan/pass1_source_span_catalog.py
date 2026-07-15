"""Deterministic exact-source-span selection for Irene Pass-1.

The model chooses stable span identities.  It never authors the literal bytes
that become ``source_refs``; this module projects those bytes from the same
authenticated source sections used by the independent authority validator.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import defaultdict
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)

SCHEMA_VERSION = "pass1-source-span-catalog.v1"
_SOURCE_ID = re.compile(
    r"^(?P<path>slides/slide-[1-9][0-9]*-[^/]+\.md)\|"
    r"(?P<digest>sha256:[0-9a-f]{64})$"
)
_SPAN_ID = re.compile(r"^span:sha256:[0-9a-f]{64}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_WORD = re.compile(r"\S+")
_MAX_FULL_SPAN_CHARS = 400
_MAX_CHUNK_WORDS = 15
_CHUNK_OVERLAP_WORDS = 3
_MAX_CATALOG_ENTRIES = 4096
_MAX_CATALOG_BYTES = 2 * 1024 * 1024
_MAX_SELECTIONS_PER_UNIT = 6


class Pass1SourceSpanCatalogError(ValueError):
    """Authenticated source sections cannot form one unambiguous catalog."""


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise Pass1SourceSpanCatalogError(
            "source-span catalog is not canonical JSON"
        ) from exc


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


class Pass1SourceSpanV1(BaseModel):
    """One exact selectable substring from one authenticated source slide."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    span_id: str
    source_id: str
    source_path: str
    source_digest: str
    extracted_content_digest: str
    start: int
    end: int
    text: str
    text_digest: str

    @model_validator(mode="after")
    def _validate_identity(self) -> Pass1SourceSpanV1:
        source_match = _SOURCE_ID.fullmatch(self.source_id)
        if source_match is None:
            raise ValueError("source span carries invalid source identity")
        if (
            self.source_path != source_match.group("path")
            or self.source_digest != source_match.group("digest")
        ):
            raise ValueError("source span identity fields disagree")
        if _SPAN_ID.fullmatch(self.span_id) is None:
            raise ValueError("source span carries invalid span identity")
        if _DIGEST.fullmatch(self.extracted_content_digest) is None:
            raise ValueError("source span carries invalid extracted-content digest")
        if _DIGEST.fullmatch(self.text_digest) is None:
            raise ValueError("source span carries invalid text digest")
        if self.start < 0 or self.end <= self.start:
            raise ValueError("source span carries invalid offsets")
        if not self.text or self.text != self.text.strip():
            raise ValueError("source span text must be nonblank and boundary-trimmed")
        if self.end - self.start != len(self.text):
            raise ValueError("source span offset range disagrees with exact text")
        if _digest(self.text) != self.text_digest:
            raise ValueError("source span text digest mismatch")
        expected_id = _digest(
            {
                "source_id": self.source_id,
                "extracted_content_digest": self.extracted_content_digest,
                "start": self.start,
                "end": self.end,
                "text": self.text,
            }
        ).replace("sha256:", "span:sha256:", 1)
        if self.span_id != expected_id:
            raise ValueError("source span stable identity mismatch")
        return self


class Pass1SourceSpanCatalogV1(BaseModel):
    """Canonical ordered catalog supplied to and selected by Irene."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["pass1-source-span-catalog.v1"] = SCHEMA_VERSION
    entries: tuple[Pass1SourceSpanV1, ...]
    catalog_digest: str

    @model_validator(mode="after")
    def _validate_catalog(self) -> Pass1SourceSpanCatalogV1:
        if not self.entries:
            raise ValueError("source-span catalog must not be empty")
        span_ids = [entry.span_id for entry in self.entries]
        texts = [entry.text for entry in self.entries]
        if len(span_ids) != len(set(span_ids)):
            raise ValueError("source-span catalog carries duplicate span IDs")
        if len(texts) != len(set(texts)):
            raise ValueError("source-span catalog carries duplicate text mappings")
        ordering = [
            (entry.source_path, entry.start, entry.end, entry.text)
            for entry in self.entries
        ]
        if ordering != sorted(ordering):
            raise ValueError("source-span catalog ordering is not canonical")
        body = {
            "schema_version": self.schema_version,
            "entries": [entry.model_dump(mode="json") for entry in self.entries],
        }
        if self.catalog_digest != _digest(body):
            raise ValueError("source-span catalog self-digest mismatch")
        return self


def _trimmed_range(text: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return (start, end) if start < end else None


def _sentence_ranges(text: str, start: int, end: int) -> tuple[tuple[int, int], ...]:
    """Return exact punctuation-bounded ranges without rewriting their bytes."""
    boundaries: list[int] = [start]
    cursor = start
    while cursor < end:
        if text[cursor] in ".!?;":
            after = cursor + 1
            while after < end and text[after] in "\"')]}\u2019\u201d":
                after += 1
            if after == end or text[after].isspace():
                boundaries.append(after)
        cursor += 1
    boundaries.append(end)
    ranges: list[tuple[int, int]] = []
    for left, right in zip(boundaries, boundaries[1:], strict=False):
        trimmed = _trimmed_range(text, left, right)
        if trimmed is not None:
            ranges.append(trimmed)
    return tuple(ranges)


def _word_chunks(text: str, start: int, end: int) -> tuple[tuple[int, int], ...]:
    matches = list(_WORD.finditer(text, start, end))
    if len(matches) <= _MAX_CHUNK_WORDS:
        return ()
    step = _MAX_CHUNK_WORDS - _CHUNK_OVERLAP_WORDS
    result: list[tuple[int, int]] = []
    index = 0
    while index < len(matches):
        group = matches[index : index + _MAX_CHUNK_WORDS]
        if len(group) < 3:
            break
        result.append((group[0].start(), group[-1].end()))
        if index + _MAX_CHUNK_WORDS >= len(matches):
            break
        index += step
    return tuple(result)


def _candidate_ranges(text: str) -> tuple[tuple[int, int], ...]:
    ranges: set[tuple[int, int]] = set()
    for line in re.finditer(r"[^\n]+", text):
        trimmed = _trimmed_range(text, line.start(), line.end())
        if trimmed is None:
            continue
        line_start, line_end = trimmed
        if (
            len(_WORD.findall(text[line_start:line_end])) >= 1
            and line_end - line_start <= _MAX_FULL_SPAN_CHARS
        ):
            ranges.add((line_start, line_end))
        sentence_ranges = _sentence_ranges(text, line_start, line_end)
        for sentence_start, sentence_end in sentence_ranges:
            sentence = text[sentence_start:sentence_end]
            if len(_WORD.findall(sentence)) < 1:
                continue
            if sentence_end - sentence_start <= _MAX_FULL_SPAN_CHARS:
                ranges.add((sentence_start, sentence_end))
            ranges.update(_word_chunks(text, sentence_start, sentence_end))
    return tuple(sorted(ranges))


def build_pass1_source_span_catalog(
    source_sections: tuple[Pass1AuthenticatedSourceSection, ...],
) -> Pass1SourceSpanCatalogV1:
    """Build a canonical catalog from authenticated per-slide source bodies."""
    if not isinstance(source_sections, tuple) or not source_sections:
        raise Pass1SourceSpanCatalogError("source-span catalog has no source sections")
    seen_sources: set[str] = set()
    seen_source_paths: set[str] = set()
    candidates: list[tuple[str, str, str, str, int, int, str]] = []
    text_sources: dict[str, set[str]] = defaultdict(set)
    for section in source_sections:
        if not isinstance(section, Pass1AuthenticatedSourceSection):
            raise Pass1SourceSpanCatalogError(
                "source-span catalog requires authenticated source-section records"
            )
        source_id = section.source_id
        source_text = section.body
        source_match = _SOURCE_ID.fullmatch(source_id) if isinstance(source_id, str) else None
        if source_match is None:
            raise Pass1SourceSpanCatalogError(
                "source-span catalog carries invalid source identity"
            )
        if source_id in seen_sources:
            raise Pass1SourceSpanCatalogError(
                "source-span catalog carries duplicate source identity"
            )
        seen_sources.add(source_id)
        source_path = source_match.group("path")
        if source_path in seen_source_paths:
            raise Pass1SourceSpanCatalogError(
                "source-span catalog carries duplicate source path"
            )
        seen_source_paths.add(source_path)
        if not isinstance(source_text, str) or not source_text.strip():
            raise Pass1SourceSpanCatalogError(
                "source-span catalog carries empty source text"
            )
        if (
            not isinstance(section.source_content_digest, str)
            or section.source_content_digest != source_match.group("digest")
        ):
            raise Pass1SourceSpanCatalogError(
                "source-span catalog raw-source digest disagrees with source identity"
            )
        if (
            not isinstance(section.extracted_content_digest, str)
            or canonical_extracted_content_digest(source_text)
            != section.extracted_content_digest
        ):
            raise Pass1SourceSpanCatalogError(
                "source-span catalog extracted digest does not match extracted bytes"
            )
        source_digest = source_match.group("digest")
        extracted_content_digest = section.extracted_content_digest
        per_source_texts: set[str] = set()
        for start, end in _candidate_ranges(source_text):
            span_text = source_text[start:end]
            if span_text in per_source_texts:
                continue
            per_source_texts.add(span_text)
            text_sources[span_text].add(source_id)
            candidates.append(
                (
                    source_id,
                    source_path,
                    source_digest,
                    extracted_content_digest,
                    start,
                    end,
                    span_text,
                )
            )
    entries: list[Pass1SourceSpanV1] = []
    for (
        source_id,
        source_path,
        source_digest,
        extracted_content_digest,
        start,
        end,
        span_text,
    ) in candidates:
        if len(text_sources[span_text]) != 1:
            continue
        identity = {
            "source_id": source_id,
            "extracted_content_digest": extracted_content_digest,
            "start": start,
            "end": end,
            "text": span_text,
        }
        entries.append(
            Pass1SourceSpanV1(
                span_id=_digest(identity).replace("sha256:", "span:sha256:", 1),
                source_id=source_id,
                source_path=source_path,
                source_digest=source_digest,
                extracted_content_digest=extracted_content_digest,
                start=start,
                end=end,
                text=span_text,
                text_digest=_digest(span_text),
            )
        )
    entries.sort(key=lambda row: (row.source_path, row.start, row.end, row.text))
    represented_sources = {entry.source_id for entry in entries}
    missing_sources = sorted(seen_sources - represented_sources)
    if missing_sources:
        raise Pass1SourceSpanCatalogError(
            "source-span catalog has no uniquely selectable span for: "
            + ", ".join(missing_sources)
        )
    if len(entries) > _MAX_CATALOG_ENTRIES:
        raise Pass1SourceSpanCatalogError("source-span catalog entry limit exceeded")
    body = {
        "schema_version": SCHEMA_VERSION,
        "entries": [entry.model_dump(mode="json") for entry in entries],
    }
    if len(_canonical_bytes(body)) > _MAX_CATALOG_BYTES:
        raise Pass1SourceSpanCatalogError("source-span catalog byte limit exceeded")
    try:
        return Pass1SourceSpanCatalogV1(
            entries=tuple(entries), catalog_digest=_digest(body)
        )
    except ValueError as exc:
        raise Pass1SourceSpanCatalogError(str(exc)) from exc


def project_pass1_source_ref_ids(
    plan: dict[str, Any], *, catalog: Pass1SourceSpanCatalogV1
) -> dict[str, Any]:
    """Project model-selected span IDs to exact literal refs without repair."""
    if not isinstance(plan, dict) or not isinstance(plan.get("plan_units"), list):
        raise Pass1SourceSpanCatalogError("Pass-1 candidate plan shape is invalid")
    by_id = {entry.span_id: entry for entry in catalog.entries}
    projected = copy.deepcopy(plan)
    for unit in projected["plan_units"]:
        if not isinstance(unit, dict):
            raise Pass1SourceSpanCatalogError("Pass-1 candidate unit is invalid")
        unit_id = unit.get("unit_id")
        if "source_refs" in unit:
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} supplied model-authored source_refs"
            )
        decision = unit.get("scope_decision")
        if isinstance(decision, dict):
            decision = decision.get("scope")
        raw_ids = unit.get("source_ref_ids")
        if decision == "out-of-scope":
            if raw_ids not in (None, []):
                raise Pass1SourceSpanCatalogError(
                    f"out-of-scope unit {unit_id} selected source authority"
                )
            unit["source_ref_ids"] = []
            unit["source_refs"] = []
            continue
        if decision != "in-scope":
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} has invalid scope decision"
            )
        if (
            not isinstance(raw_ids, list)
            or not raw_ids
            or not all(isinstance(span_id, str) and span_id for span_id in raw_ids)
        ):
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} source_ref_ids must be a nonempty string list"
            )
        if len(raw_ids) != len(set(raw_ids)):
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} carries duplicate source_ref_ids"
            )
        if len(raw_ids) > _MAX_SELECTIONS_PER_UNIT:
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} source_ref_ids exceeds the six-span limit"
            )
        try:
            selected = [by_id[span_id] for span_id in raw_ids]
        except KeyError as exc:
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} selected an unknown or stale source span ID"
            ) from exc
        if len({entry.source_id for entry in selected}) != 1:
            raise Pass1SourceSpanCatalogError(
                f"unit {unit_id} selections do not converge on one source"
            )
        unit["source_refs"] = [entry.text for entry in selected]
    projected["source_span_catalog_digest"] = catalog.catalog_digest
    return projected


__all__ = [
    "Pass1SourceSpanCatalogError",
    "Pass1SourceSpanCatalogV1",
    "Pass1SourceSpanV1",
    "build_pass1_source_span_catalog",
    "project_pass1_source_ref_ids",
]
