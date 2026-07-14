"""M3-safe adapter from frozen lesson authority to the Deep Dive request."""

from __future__ import annotations

import hashlib
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
from app.marcus.lesson_plan.slide_authority import (
    SlideAuthorityInvalidError,
    WorkbookSlideAuthorityMapV1,
    read_contained_regular_bytes,
)

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


def _speaker_note(path: Path, *, verified_bytes: bytes | None = None) -> str | None:
    try:
        raw = path.read_bytes() if verified_bytes is None else verified_bytes
        text = raw.decode("utf-8")
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


def _load_segments(
    run_dir: Path,
    *,
    manifest_bytes: bytes | None = None,
    expected_manifest_digest: str | None = None,
) -> list[dict[str, Any]]:
    path = Path(run_dir) / MANIFEST_RELATIVE_PATH
    try:
        source = (
            read_contained_regular_bytes(
                Path(run_dir), path, "segment manifest"
            )
            if manifest_bytes is None
            else manifest_bytes
        )
        observed_digest = "sha256:" + hashlib.sha256(source).hexdigest()
        if (
            expected_manifest_digest is not None
            and observed_digest != expected_manifest_digest
        ):
            raise DeepDiveAuthorityInvalidError(
                "segment manifest digest disagrees with slide authority map"
            )
        raw = yaml.load(
            source.decode("utf-8"),
            Loader=_UniqueKeySafeLoader,
        )
    except SlideAuthorityInvalidError as exc:
        raise DeepDiveAuthorityInvalidError(str(exc)) from exc
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
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


def load_deep_dive_segments(
    run_dir: Path, *, manifest_bytes: bytes | None = None
) -> list[dict[str, Any]]:
    """Load the exact duplicate-key-free manifest segment authority."""
    return _load_segments(run_dir, manifest_bytes=manifest_bytes)


def _mapped_source_path(
    course_source_root: Path, *, relative_path: str, expected_digest: str
) -> tuple[Path, bytes]:
    root = Path(course_source_root)
    slides = root / "slides"
    candidate = root / Path(relative_path)
    if slides.is_symlink() or not slides.is_dir():
        raise DeepDiveAuthorityInvalidError("mapped slides root is absent or unsafe")
    if candidate.is_symlink() or not candidate.is_file():
        raise DeepDiveAuthorityInvalidError("mapped source slide is absent or unsafe")
    try:
        resolved_slides = slides.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_slides)
        raw = read_contained_regular_bytes(
            resolved_slides, candidate, "mapped source slide"
        )
    except (OSError, ValueError, SlideAuthorityInvalidError) as exc:
        raise DeepDiveAuthorityInvalidError("mapped source slide escapes authority") from exc
    observed = "sha256:" + hashlib.sha256(raw).hexdigest()
    if observed != expected_digest:
        raise DeepDiveAuthorityInvalidError("mapped source slide digest mismatch")
    return candidate, raw


def build_deep_dive_request(
    run_dir: Path,
    course_source_root: Path,
    promise: PromiseProjection,
    authority_map: WorkbookSlideAuthorityMapV1 | None = None,
    manifest_bytes: bytes | None = None,
) -> DeepDiveSkeletonRequest:
    """Build one ordered, closed request from the exact manifest/slides/Promise seam."""
    promise = PromiseProjection.model_validate(promise.model_dump())
    if promise.status != "authored" or not promise.vows:
        raise DeepDiveAuthorityUnavailableError(
            "authored Promise ability authority unavailable"
        )
    segments = _load_segments(
        run_dir,
        manifest_bytes=manifest_bytes,
        expected_manifest_digest=(
            authority_map.manifest_digest if authority_map is not None else None
        ),
    )
    inventory = None if authority_map is not None else _slide_inventory(course_source_root)
    mapped_rows = authority_map.rows if authority_map is not None else ()
    if authority_map is not None and len(mapped_rows) != len(segments):
        raise DeepDiveAuthorityInvalidError(
            "slide authority map roster does not equal segment manifest"
        )
    seen_ids: set[str] = set()
    seen_slide_ordinals: set[int] = set()
    vo_spans: list[NarrationSourceSpan] = []
    vo_claims: list[SourceClaim] = []
    deltas: list[tuple[NarrationSourceSpan, SourceClaim]] = []
    source_groups: dict[str, tuple[Path, bytes | None, list[str]]] = {}
    verified_sources: dict[tuple[str, str], tuple[Path, bytes]] = {}
    for index, row in enumerate(segments):
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
        if authority_map is None:
            assert inventory is not None
            matches = inventory.get(ordinal, ())
            if len(matches) != 1:
                raise DeepDiveAuthorityInvalidError(
                    f"slide authority for {slide_id} matched {len(matches)} files"
                )
            source_path = matches[0]
            source_bytes = None
            source_slide_id = slide_id
        else:
            mapped = mapped_rows[index]
            if mapped.final_slide_id != slide_id:
                raise DeepDiveAuthorityInvalidError(
                    "slide authority map order/identity disagrees with manifest"
                )
            source_key = (mapped.source_path, mapped.source_sha256)
            verified = verified_sources.get(source_key)
            if verified is None:
                verified = _mapped_source_path(
                    course_source_root,
                    relative_path=mapped.source_path,
                    expected_digest=mapped.source_sha256,
                )
                verified_sources[source_key] = verified
            source_path, source_bytes = verified
            source_slide_id = mapped.source_slide_id
        group = source_groups.get(source_slide_id)
        if group is None:
            source_groups[source_slide_id] = (source_path, source_bytes, [narration])
        else:
            if group[0] != source_path or group[1] != source_bytes:
                raise DeepDiveAuthorityInvalidError(
                    "one source slide identity resolved to multiple files"
                )
            group[2].append(narration)

    for source_slide_id, (
        source_path,
        source_bytes,
        descendant_narration,
    ) in source_groups.items():
        note = _speaker_note(source_path, verified_bytes=source_bytes)
        if note is None:
            continue
        normalized_note = _canonical_text(note)
        aggregate_narration = "\n".join(descendant_narration)
        normalized_narration = _canonical_text(aggregate_narration)
        if (
            normalized_note
            and normalized_narration
            and normalized_note != normalized_narration
            and bool(_tokens(note) - _tokens(aggregate_narration))
        ):
            delta_id = f"delta:{source_slide_id}"
            relative = source_path.relative_to(course_source_root).as_posix()
            span = NarrationSourceSpan(
                span_id=delta_id,
                text=note,
                source_ref=f"{relative}#Narration (Speaker Notes)",
            )
            claim = SourceClaim(
                claim_id=f"claim:delta:{source_slide_id}",
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
            slide_authority_map_digest=(
                authority_map.map_digest if authority_map is not None else None
            ),
        )
    except ValueError as exc:
        raise DeepDiveAuthorityInvalidError(f"Deep Dive authority shape invalid: {exc}") from exc


__all__ = [
    "MANIFEST_RELATIVE_PATH",
    "DeepDiveAuthorityInvalidError",
    "DeepDiveAuthorityUnavailableError",
    "build_deep_dive_request",
    "load_deep_dive_segments",
]
