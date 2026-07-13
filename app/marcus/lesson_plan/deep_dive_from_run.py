"""M3-safe adapter from frozen lesson authority to the Deep Dive request."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveAbilityInput,
    DeepDiveSkeletonRequest,
    NarrationSourceSpan,
    SourceClaim,
)
from app.marcus.lesson_plan.prework_projection import PromiseProjection

MANIFEST_RELATIVE_PATH = Path("exports/segment-manifest-storyboard-b.yaml")
_SLIDE_NAME = re.compile(r"^slide-(?P<ordinal>[1-9][0-9]*)-.+\.md$")
_SEGMENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SPEAKER_NOTES_HEADER = re.compile(
    r"^\s*(?:[-*\u2022]\s*)?(?:\*\*)?Narration \(Speaker Notes\)\s*:"
    r"(?:\*\*)?[ \t]*(?P<tail>.*)$",
    re.IGNORECASE,
)
_BOLDED_SLIDE_FIELD_HEADER = re.compile(
    r"^\s*(?:[-*\u2022]\s*)?\*\*(?P<label>[^*\n:]{1,80}):\*\*[ \t]*"
)
_UNBOLDED_SLIDE_FIELD_HEADER = re.compile(
    r"^\s*(?:[-*\u2022]\s*)?(?P<label>[^:\r\n]{1,80})\s*:[ \t]*"
)
_GOVERNED_SLIDE_FIELD_LABELS = frozenset(
    {
        "answer",
        "assessment",
        "assessment answer",
        "color palette",
        "correct answer",
        "image prompt",
        "learning objective",
        "narration",
        "narration (speaker notes)",
        "on screen text",
        "on-screen text",
        "prompt to generate image",
        "question",
        "reference",
        "references",
        "required text labels",
        "slide title",
        "source",
        "sources",
        "speaker notes (narration)",
        "subtitle",
        "summary text",
        "the composition",
        "the core message",
        "title",
        "visual",
        "visual format",
        "visual layout",
    }
)
_MARKDOWN_BOUNDARY = re.compile(r"^\s*(?:#{1,6}\s+|---+\s*$)")
_TOKEN = re.compile(r"[^\W_]+", re.UNICODE)


class DeepDiveAuthorityInvalidError(ValueError):
    """Declared source authority exists but violates its closed shape."""


class DeepDiveAuthorityUnavailableError(ValueError):
    """Required source authority is honestly absent or empty."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses authority-overwriting duplicate keys."""


def _construct_unique_mapping(
    loader: yaml.SafeLoader, node: MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key ({key!r})",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _canonical_text(value: str) -> str:
    return " ".join(
        unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
        .split()
    ).strip()


def _tokens(value: str) -> set[str]:
    return {token.casefold() for token in _TOKEN.findall(_canonical_text(value))}


def _ordinal(slide_id: str) -> int:
    match = re.fullmatch(r"slide-(0*[1-9][0-9]*)", slide_id)
    if match is None:
        raise DeepDiveAuthorityInvalidError(f"invalid slide_id: {slide_id!r}")
    try:
        return int(match.group(1))
    except ValueError as exc:
        raise DeepDiveAuthorityInvalidError(f"invalid slide_id: {slide_id!r}") from exc


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _speaker_note(path: Path) -> str | None:
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DeepDiveAuthorityUnavailableError(
            f"speaker-note source unavailable: {path}"
        ) from exc
    lines = text.splitlines(keepends=True)
    headers: list[tuple[int, re.Match[str], str, str]] = []
    for index, line in enumerate(lines):
        header = line.rstrip("\r\n")
        match = _SPEAKER_NOTES_HEADER.match(header)
        if match is not None:
            headers.append((index, match, header, line[len(header) :]))
    if not headers:
        return None
    if len(headers) != 1:
        raise DeepDiveAuthorityInvalidError(
            f"duplicate speaker-note fields: {path.name}"
        )
    index, match, _header, separator = headers[0]
    note = match.group("tail")
    for following in lines[index + 1 :]:
        candidate = following.rstrip("\r\n")
        bolded_field = _BOLDED_SLIDE_FIELD_HEADER.match(candidate)
        unbolded_field = _UNBOLDED_SLIDE_FIELD_HEADER.match(candidate)
        if (
            (
                bolded_field is not None
                and bolded_field.group("label").strip().casefold()
                in _GOVERNED_SLIDE_FIELD_LABELS
            )
            or (
                unbolded_field is not None
                and unbolded_field.group("label").strip().casefold()
                in _GOVERNED_SLIDE_FIELD_LABELS
            )
            or _MARKDOWN_BOUNDARY.match(candidate)
        ):
            break
        note += separator + candidate
        separator = following[len(candidate) :]
    return note if _canonical_text(note) else None


def _slide_inventory(course_source_root: Path) -> dict[int, tuple[Path, ...]]:
    slides = Path(course_source_root) / "slides"
    if not slides.is_dir():
        raise DeepDiveAuthorityUnavailableError("slides authority directory absent")
    if slides.is_symlink():
        raise DeepDiveAuthorityInvalidError("slides authority directory may not be a symlink")
    inventory: dict[int, list[Path]] = {}
    try:
        children = tuple(slides.iterdir())
    except OSError as exc:
        raise DeepDiveAuthorityUnavailableError(
            "slides authority directory unreadable"
        ) from exc
    resolved_root = Path(course_source_root).resolve(strict=True)
    resolved_slides = slides.resolve(strict=True)
    if not _is_within(resolved_slides, resolved_root):
        raise DeepDiveAuthorityInvalidError("slides authority escapes course root")
    for child in children:
        match = _SLIDE_NAME.fullmatch(child.name)
        if match is None:
            continue
        if child.is_symlink():
            raise DeepDiveAuthorityInvalidError(
                f"slide authority may not be a symlink: {child.name}"
            )
        try:
            resolved_child = child.resolve(strict=True)
        except OSError as exc:
            raise DeepDiveAuthorityInvalidError(
                f"slide authority is unreadable: {child.name}"
            ) from exc
        if not _is_within(resolved_child, resolved_slides) or not child.is_file():
            raise DeepDiveAuthorityInvalidError(
                f"slide authority escapes declared root: {child.name}"
            )
        inventory.setdefault(int(match.group("ordinal")), []).append(child)
    return {
        key: tuple(sorted(value, key=lambda item: item.name))
        for key, value in inventory.items()
    }


def _load_segments(run_dir: Path) -> list[dict[str, Any]]:
    path = Path(run_dir) / MANIFEST_RELATIVE_PATH
    if path.is_symlink():
        raise DeepDiveAuthorityInvalidError("segment manifest may not be a symlink")
    try:
        resolved_run = Path(run_dir).resolve(strict=True)
        resolved_path = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise DeepDiveAuthorityUnavailableError("segment manifest absent") from exc
    except OSError as exc:
        raise DeepDiveAuthorityInvalidError("segment manifest unreadable") from exc
    if not _is_within(resolved_path, resolved_run):
        raise DeepDiveAuthorityInvalidError("segment manifest escapes run root")
    try:
        raw = yaml.load(
            resolved_path.read_text(encoding="utf-8"),
            Loader=_UniqueKeySafeLoader,
        )
    except (OSError, yaml.YAMLError) as exc:
        raise DeepDiveAuthorityInvalidError("segment manifest unreadable or invalid") from exc
    if not isinstance(raw, dict) or "segments" not in raw:
        raise DeepDiveAuthorityInvalidError("segment manifest requires a segments container")
    segments = raw["segments"]
    if not isinstance(segments, list):
        raise DeepDiveAuthorityInvalidError("segments must be a list")
    if not segments:
        raise DeepDiveAuthorityUnavailableError("segments authority is empty")
    if not all(isinstance(row, dict) for row in segments):
        raise DeepDiveAuthorityInvalidError("each segment must be an object")
    return segments


def build_deep_dive_request(
    run_dir: Path,
    course_source_root: Path,
    promise: PromiseProjection,
) -> DeepDiveSkeletonRequest:
    """Build one ordered, closed request from the exact manifest/slides/Promise seam."""
    promise = PromiseProjection.model_validate(promise.model_dump())
    if promise.status != "authored" or not promise.vows:
        raise DeepDiveAuthorityUnavailableError(
            "authored Promise ability authority unavailable"
        )
    segments = _load_segments(run_dir)
    inventory = _slide_inventory(course_source_root)
    seen_ids: set[str] = set()
    seen_slide_ordinals: set[int] = set()
    vo_spans: list[NarrationSourceSpan] = []
    vo_claims: list[SourceClaim] = []
    deltas: list[tuple[NarrationSourceSpan, SourceClaim]] = []
    for row in segments:
        segment_id = row.get("segment_id")
        narration = row.get("narration_text")
        slide_id = row.get("slide_id")
        if not isinstance(segment_id, str) or not _SEGMENT_ID.fullmatch(segment_id):
            raise DeepDiveAuthorityInvalidError(
                "segment_id must be a stable alphanumeric/dot/underscore/hyphen token"
            )
        if segment_id in seen_ids:
            raise DeepDiveAuthorityInvalidError(f"duplicate segment_id: {segment_id}")
        seen_ids.add(segment_id)
        if not isinstance(narration, str) or not narration.strip():
            raise DeepDiveAuthorityUnavailableError(
                f"narration unavailable for {segment_id}"
            )
        if not isinstance(slide_id, str) or not slide_id.strip():
            raise DeepDiveAuthorityInvalidError(f"slide_id invalid for {segment_id}")
        ordinal = _ordinal(slide_id)
        if ordinal in seen_slide_ordinals:
            raise DeepDiveAuthorityInvalidError(
                f"duplicate canonical slide_id: slide-{ordinal}"
            )
        seen_slide_ordinals.add(ordinal)
        vo_id = f"vo:{segment_id}"
        manifest_ref = (
            f"{MANIFEST_RELATIVE_PATH.as_posix()}#segments/{segment_id}/narration_text"
        )
        vo_spans.append(
            NarrationSourceSpan(span_id=vo_id, text=narration, source_ref=manifest_ref)
        )
        vo_claims.append(
            SourceClaim(
                claim_id=f"claim:vo:{segment_id}",
                text=narration,
                source_span_refs=(vo_id,),
                role="vo",
            )
        )
        matches = inventory.get(ordinal, ())
        if len(matches) != 1:
            raise DeepDiveAuthorityInvalidError(
                f"slide authority for {slide_id} matched {len(matches)} files"
            )
        note = _speaker_note(matches[0])
        if note is None:
            continue
        normalized_note = _canonical_text(note)
        normalized_narration = _canonical_text(narration)
        if (
            normalized_note
            and normalized_narration
            and normalized_note != normalized_narration
            and bool(_tokens(note) - _tokens(narration))
        ):
            delta_id = f"delta:{slide_id}"
            relative = matches[0].relative_to(course_source_root).as_posix()
            span = NarrationSourceSpan(
                span_id=delta_id,
                text=note,
                source_ref=f"{relative}#Narration (Speaker Notes)",
            )
            claim = SourceClaim(
                claim_id=f"claim:delta:{slide_id}",
                text=note,
                source_span_refs=(delta_id,),
                role="source_supported_delta",
            )
            deltas.append((span, claim))
    try:
        return DeepDiveSkeletonRequest(
            lesson_ref=MANIFEST_RELATIVE_PATH.as_posix(),
            source_spans=tuple(vo_spans) + tuple(span for span, _ in deltas),
            source_claims=tuple(vo_claims) + tuple(claim for _, claim in deltas),
            abilities=tuple(
                DeepDiveAbilityInput(ability_id=vow.objective_id, text=vow.text)
                for vow in promise.vows
            ),
        )
    except ValueError as exc:
        raise DeepDiveAuthorityInvalidError(f"Deep Dive authority shape invalid: {exc}") from exc


__all__ = [
    "MANIFEST_RELATIVE_PATH",
    "DeepDiveAuthorityInvalidError",
    "DeepDiveAuthorityUnavailableError",
    "build_deep_dive_request",
]
