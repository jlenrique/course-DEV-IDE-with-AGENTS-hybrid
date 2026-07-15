"""Hardened Texas act-body for Slab 7b Story 7b.1."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import stat
import tempfile
from collections.abc import Callable
from contextlib import contextmanager, suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.source_bundle import (
    SourceBundleError,
    expand_markdown_tabs,
    extracted_section_digest,
    parse_extracted_primary_sections,
    scan_markdown_lines,
)

REQUIRED_BUNDLE_ARTIFACTS = (
    "extracted.md",
    "metadata.json",
    "extraction-report.yaml",
    "manifest.json",
    "ingestion-evidence.md",
    "result.yaml",
)
G0_RUBRIC_DIMENSIONS = (
    "completeness",
    "readability",
    "anchorability",
    "provenance",
    "planning_usability",
    "fidelity_usability",
)
_EVIDENCE_MARKER = re.compile(r"\[evidence: ([A-Za-z0-9._-]+)\]")
_MARKER_LIKE = re.compile(r"\[\s*evidence\s*:\s*[^\]]*\]", re.IGNORECASE)
_BLOCKQUOTE_PREFIX = re.compile(r"^(?: {0,3}> ?)+")
_LIST_SURFACE = re.compile(
    r"^ {0,3}(?:[-+*]|\d{1,9}[.)])"
    r"(?:(?:[ \t](?=[ \t]{4,}\S))|(?:[ \t]{1,4}(?=\S))|(?:[ \t]*$))"
)
_TRANSACTION_NAME = ".texas-hardening-transaction.json"
_LOCK_NAME = ".texas-hardening.lock"
_PUBLISHED_STATUSES = frozenset({"complete", "complete_with_warnings", "blocked"})


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses ambiguous duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


class BundleParseError(SpecialistDispatchError):  # noqa: N818
    """Raised when Texas's six-artifact bundle cannot be parsed.

    Taxonomy re-base (live-path tranche, 2026-06-12): dispatch-family so a
    mid-walk failure error-pauses recoverably instead of killing the trial.
    """


class BundleDispatchError(SpecialistDispatchError):
    """Raised when the wrangler dispatch receipt is unusable."""


class RetrievalScopeError(Exception):
    """Raised when extracted.md is below the directive word-count floor."""

    def __init__(self, observed_words: int, expected_floor: int) -> None:
        super().__init__(
            "Texas retrieval scope under-floor: "
            f"observed_words={observed_words}, expected_floor={expected_floor}"
        )
        self.observed_words = observed_words
        self.expected_floor = expected_floor


@contextmanager
def _exclusive_hardening_lock(bundle_dir: Path):
    """Serialize publishers with a crash-releasing OS advisory lock."""
    path = bundle_dir / _LOCK_NAME
    descriptor: int | None = None
    locked = False
    try:
        descriptor = os.open(
            path,
            os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        opened = os.fstat(descriptor)
        coordinate = path.stat(follow_symlinks=False)
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(coordinate.st_mode)
            or opened.st_nlink != 1
            or coordinate.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (coordinate.st_dev, coordinate.st_ino)
        ):
            raise OSError("Texas hardening lock coordinate is unsafe")
        if opened.st_size == 0:
            os.write(descriptor, b"1")
            os.fsync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
    except (OSError, RuntimeError, ValueError) as exc:
        if descriptor is not None:
            with suppress(OSError):
                os.close(descriptor)
        raise BundleParseError(
            "Texas hardening transaction is already active or unsafe",
            tag="bundle.parsed.persistence-failed",
        ) from exc
    try:
        yield
    finally:
        if descriptor is not None:
            if locked:
                with suppress(OSError):
                    os.lseek(descriptor, 0, os.SEEK_SET)
                    if os.name == "nt":
                        import msvcrt

                        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(descriptor, fcntl.LOCK_UN)
            with suppress(OSError):
                os.close(descriptor)


def _new_dispatch_trail_entry(
    last_entry: ModelResolutionEntry, *, tag: str
) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise BundleParseError(
            f"texas act envelope-carrier cache_prefix is not valid JSON: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise BundleParseError(
            "texas act envelope-carrier cache_prefix must decode to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return decoded


def _load_yaml_mapping(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = yaml.load(
            path.read_text(encoding="utf-8"), Loader=_UniqueKeySafeLoader
        ) or {}
    except yaml.YAMLError as exc:
        raise BundleParseError(
            f"invalid {label} content: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(payload, dict):
        raise BundleParseError(
            f"{label} must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return payload


def _load_yaml_bytes(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        payload = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeySafeLoader) or {}
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise BundleParseError(
            f"invalid {label} content: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(payload, dict):
        raise BundleParseError(
            f"{label} must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return payload


def _load_bundle_snapshot_locked(
    bundle_dir: Path,
) -> tuple[dict[str, Any], dict[str, bytes]]:
    missing = [
        name for name in REQUIRED_BUNDLE_ARTIFACTS if not (bundle_dir / name).is_file()
    ]
    if missing:
        raise BundleParseError(
            f"missing bundle artifact(s): {missing}",
            tag="bundle.parsed.missing-key",
        )
    snapshots, _manifest_raw = _authenticated_bundle_snapshots(bundle_dir)
    result_payload = _load_yaml_bytes(snapshots["result.yaml"], label="result.yaml")
    report_payload = _load_yaml_bytes(
        snapshots["extraction-report.yaml"], label="extraction-report.yaml"
    )
    metadata_payload = _parse_json_mapping(
        snapshots["metadata.json"], label="metadata.json"
    )
    status = result_payload.get("status")
    if not isinstance(status, str) or not status.strip():
        raise BundleParseError(
            "result.yaml missing non-empty status string",
            tag="bundle.parsed.empty",
        )
    overall_status = report_payload.get("overall_status")
    if not isinstance(overall_status, str) or not overall_status.strip():
        raise BundleParseError(
            "extraction-report.yaml missing non-empty string overall_status",
            tag="bundle.parsed.empty",
        )
    if (
        status not in _PUBLISHED_STATUSES
        or overall_status not in _PUBLISHED_STATUSES
        or status != overall_status
    ):
        raise BundleParseError(
            "result and extraction-report status disagrees or is unknown",
            tag="bundle.parsed.provenance-mismatch",
        )
    run_ids = (
        metadata_payload.get("run_id"),
        report_payload.get("run_id"),
        result_payload.get("run_id"),
    )
    if (
        any(not isinstance(run_id, str) or not run_id.strip() for run_id in run_ids)
        or len(set(run_ids)) != 1
    ):
        raise BundleParseError(
            "metadata and receipt run identities disagree",
            tag="bundle.parsed.provenance-mismatch",
        )
    directive_sha256 = metadata_payload.get("directive_sha256")
    if (
        not isinstance(directive_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", directive_sha256) is None
    ):
        raise BundleParseError(
            "metadata directive binding is missing or invalid",
            tag="bundle.parsed.provenance-mismatch",
        )
    return (
        {
            "result": result_payload,
            "report": report_payload,
            "status": status,
            "overall_status": overall_status,
            "tag": "bundle.parsed.ok",
        },
        snapshots,
    )


def load_bundle_outputs(bundle_dir: Path) -> dict[str, Any]:
    with _exclusive_hardening_lock(bundle_dir):
        parsed, _snapshots = _load_bundle_snapshot_locked(bundle_dir)
    return parsed


def _load_directive(path: str | Path) -> dict[str, Any]:
    directive_path = Path(path)
    try:
        raw = _read_stable_bundle_bytes(
            directive_path.parent, directive_path, "Texas source directive"
        )
        payload = yaml.load(
            raw.decode("utf-8"), Loader=_UniqueKeySafeLoader
        ) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise BundleParseError(
            f"directive cannot be loaded for Texas hardening checks: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(payload, dict):
        raise BundleParseError(
            "directive root must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    payload["_directive_sha256"] = hashlib.sha256(
        yaml.safe_dump(payload, sort_keys=True, allow_unicode=True).encode("utf-8")
    ).hexdigest()
    return payload


def _expected_word_floor(directive: dict[str, Any]) -> int:
    retrieval_intent = directive.get("retrieval_intent")
    if isinstance(retrieval_intent, dict):
        size = retrieval_intent.get("expected_corpus_size")
        if isinstance(size, int):
            return size
    floor = 0
    for source in directive.get("sources", []) or []:
        if not isinstance(source, dict):
            continue
        if source.get("role") not in ("primary", "visual-primary"):
            continue
        value = source.get("expected_corpus_size", source.get("expected_min_words", 0))
        try:
            floor += int(value)
        except (TypeError, ValueError):
            continue
    return max(floor, 0)


def _cross_validation_hints(directive: dict[str, Any]) -> list[str]:
    hints = directive.get("cross_validation_hints", [])
    if not hints:
        for source in directive.get("sources", []) or []:
            if isinstance(source, dict):
                hints.extend(source.get("cross_validation_hints", []) or [])
    return [str(hint) for hint in hints if str(hint).strip()]


def _anchor_extracted_claims(extracted: str, source_ref: str) -> tuple[str, int]:
    """Anchor one already-bounded primary body to its owning source only."""
    anchored: list[str] = []
    claim_count = 0
    retained_final_newline = extracted.endswith("\n")
    markdown_lines = scan_markdown_lines(extracted)
    masked_text, multiline_span_lines, multiline_claim_lines = _mask_inline_code_spans(
        extracted, markdown_lines
    )
    marker_surfaces = masked_text.splitlines()
    for line_index, markdown_line in enumerate(markdown_lines):
        line = markdown_line.text
        marker_surface = marker_surfaces[line_index]
        marker_like = _MARKER_LIKE.findall(marker_surface)
        markers = _EVIDENCE_MARKER.findall(marker_surface)
        if not markdown_line.is_literal and marker_like and (
            len(marker_like) != len(markers)
            or len(markers) != 1
            or markers != [source_ref]
            or not line.rstrip().endswith(f"[evidence: {source_ref}]")
        ):
            raise BundleParseError(
                "primary source section carries foreign or ambiguous evidence",
                tag="bundle.parsed.provenance-mismatch",
            )
        candidate = expand_markdown_tabs(
            _MARKER_LIKE.sub("", marker_surface.strip())
        )
        candidate = _BLOCKQUOTE_PREFIX.sub("", candidate).strip()
        candidate = _LIST_SURFACE.sub("", candidate)
        candidate = re.sub(r"^\[[ xX]\]\s+", "", candidate)
        candidate = candidate.strip("*_~ ")
        ordinary_substantive = bool(
            not markdown_line.is_structural
            and not markdown_line.is_table
            and line_index not in multiline_span_lines
            and re.search(r"[A-Za-z0-9]", candidate)
            and re.fullmatch(r"<[^>]+>", candidate) is None
        )
        substantive = ordinary_substantive or line_index in multiline_claim_lines
        if substantive:
            claim_count += 1
            if not markers:
                line = f"{line} [evidence: {source_ref}]"
        anchored.append(line)
    result = "\n".join(anchored)
    if retained_final_newline:
        result += "\n"
    return result, claim_count


def _mask_inline_code_spans(
    text: str, markdown_lines: tuple[Any, ...]
) -> tuple[str, frozenset[int], frozenset[int]]:
    """Mask CommonMark code spans while preserving escaped visible backticks."""
    runs: list[tuple[Any, bool]] = []
    for match in re.finditer(r"`+", text):
        preceding = match.start() - 1
        backslashes = 0
        while preceding >= 0 and text[preceding] == "\\":
            backslashes += 1
            preceding -= 1
        runs.append((match, backslashes % 2 == 1))
    masked = list(text)
    multiline_span_lines: set[int] = set()
    multiline_ranges: list[tuple[int, int]] = []
    paragraph_ids: list[int | None] = []
    paragraph_id = 0
    prior_container_key: tuple[int, int | None] | None = None
    for line in markdown_lines:
        visible = _BLOCKQUOTE_PREFIX.sub("", expand_markdown_tabs(line.text))
        list_prefix = _LIST_SURFACE.match(visible)
        if line.container_key != prior_container_key:
            paragraph_id += 1
        prior_container_key = line.container_key
        paragraph_surface = (
            visible[list_prefix.end() :] if list_prefix is not None else visible
        )
        inline_code_only = bool(
            re.fullmatch(r" {0,3}`+[^`]*`+\s*", paragraph_surface)
        )
        if (
            not line.text.strip()
            or line.is_literal
            or line.is_table
            or line.heading_level is not None
            or (line.is_structural and not inline_code_only)
        ):
            paragraph_ids.append(None)
            paragraph_id += 1
        else:
            paragraph_ids.append(paragraph_id)
    opener_index = 0
    while opener_index < len(runs):
        opener, opener_is_escaped = runs[opener_index]
        if opener_is_escaped:
            opener_index += 1
            continue
        opener_length = opener.end() - opener.start()
        closer_index = opener_index + 1
        while closer_index < len(runs):
            closer, _closer_is_escaped = runs[closer_index]
            start_line = text.count("\n", 0, opener.start())
            end_line = text.count("\n", 0, closer.end())
            same_paragraph = (
                start_line < len(paragraph_ids)
                and end_line < len(paragraph_ids)
                and paragraph_ids[start_line] is not None
                and paragraph_ids[start_line] == paragraph_ids[end_line]
            )
            if closer.end() - closer.start() == opener_length and same_paragraph:
                if start_line != end_line:
                    multiline_span_lines.update(range(start_line, end_line + 1))
                    multiline_ranges.append((start_line, end_line))
                for index in range(opener.start(), closer.end()):
                    if masked[index] not in {"\n", "\r"}:
                        masked[index] = " "
                opener_index = closer_index + 1
                break
            closer_index += 1
        else:
            opener_index += 1
    masked_lines = "".join(masked).splitlines()
    multiline_claim_lines: set[int] = set()
    ranges_by_paragraph: dict[int, list[tuple[int, int]]] = {}
    for start_line, end_line in multiline_ranges:
        paragraph = paragraph_ids[start_line]
        if paragraph is not None:
            ranges_by_paragraph.setdefault(paragraph, []).append(
                (start_line, end_line)
            )
    for ranges_in_paragraph in ranges_by_paragraph.values():
        start_line = min(start for start, _end in ranges_in_paragraph)
        end_line = max(end for _start, end in ranges_in_paragraph)
        outside = " ".join(masked_lines[start_line : end_line + 1])
        outside = _LIST_SURFACE.sub("", outside)
        if re.search(r"[A-Za-z0-9]", outside):
            multiline_claim_lines.add(end_line)
    return (
        "".join(masked),
        frozenset(multiline_span_lines),
        frozenset(multiline_claim_lines),
    )


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_stable_bundle_bytes(bundle_dir: Path, path: Path, label: str) -> bytes:
    try:
        root = bundle_dir.resolve(strict=True)
        before = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError(f"{label} is not a singly linked regular file")
        path.resolve(strict=True).relative_to(root)
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise OSError(f"{label} changed before read")
            raw = handle.read()
            handle.seek(0)
            if handle.read() != raw or len(raw) != opened.st_size:
                raise OSError(f"{label} changed during read")
        after = path.stat(follow_symlinks=False)
        identity = lambda item: (  # noqa: E731
            item.st_dev,
            item.st_ino,
            item.st_mode,
            item.st_size,
            item.st_mtime_ns,
            item.st_nlink,
        )
        if identity(before) != identity(opened) or identity(opened) != identity(after):
            raise OSError(f"{label} changed during read")
        return raw
    except (OSError, RuntimeError, ValueError) as exc:
        raise BundleParseError(
            f"{label} is unreadable or unsafe",
            tag="bundle.parsed.unsafe-artifact",
        ) from exc


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateFileW(
            str(path),
            0x40000000,
            0x00000007,
            None,
            3,
            0x02000000,
            None,
        )
        if handle == -1:
            raise OSError(ctypes.get_last_error(), "cannot open bundle directory")
        try:
            if not kernel32.FlushFileBuffers(handle):
                raise OSError(
                    ctypes.get_last_error(), "cannot flush bundle directory"
                )
        finally:
            kernel32.CloseHandle(handle)
        return
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _stage_bytes(path: Path, payload: bytes) -> Path:
    temporary: Path | None = None
    descriptor: int | None = None
    created = False
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.texas-hardening-",
            suffix=".tmp",
            dir=path.parent,
        )
        temporary = Path(temporary_name)
        created = True
        os.chmod(temporary, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return temporary
    except (OSError, ValueError) as exc:
        if descriptor is not None:
            with suppress(OSError):
                os.close(descriptor)
        if created and temporary is not None:
            with suppress(OSError):
                temporary.unlink()
        raise BundleParseError(
            f"cannot stage hardened artifact {path.name}",
            tag="bundle.parsed.persistence-failed",
        ) from exc


def _remove_orphaned_staging_files(bundle_dir: Path) -> None:
    """Remove only Texas-reserved crash residue while holding the bundle lock."""
    removed = False
    for artifact in REQUIRED_BUNDLE_ARTIFACTS:
        pattern = f".{artifact}.texas-hardening-*.tmp"
        for candidate in bundle_dir.glob(pattern):
            try:
                coordinate = candidate.stat(follow_symlinks=False)
                candidate.resolve(strict=True).relative_to(bundle_dir.resolve(strict=True))
                if not stat.S_ISREG(coordinate.st_mode) or coordinate.st_nlink != 1:
                    raise OSError("Texas staging residue is unsafe")
                candidate.unlink()
                removed = True
            except (OSError, RuntimeError, ValueError) as exc:
                raise BundleParseError(
                    "cannot remove unsafe Texas hardening crash residue",
                    tag="bundle.parsed.persistence-failed",
                ) from exc
    if removed:
        _fsync_directory(bundle_dir)


def _parse_json_mapping(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_json_object
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise BundleParseError(
            f"{label} is malformed", tag="bundle.parsed.malformed"
        ) from exc
    if not isinstance(payload, dict):
        raise BundleParseError(
            f"{label} must be a mapping", tag="bundle.parsed.wrong-type"
        )
    return payload


def _manifest_inventory(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = manifest.get("artifacts")
    if manifest.get("schema_version") != "1.0" or not isinstance(rows, list):
        raise BundleParseError(
            "source bundle manifest identity is invalid",
            tag="bundle.parsed.manifest-invalid",
        )
    inventory: dict[str, dict[str, Any]] = {}
    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("path"), str)
            or row["path"] in inventory
        ):
            raise BundleParseError(
                "source bundle manifest artifact inventory is ambiguous",
                tag="bundle.parsed.manifest-invalid",
            )
        inventory[row["path"]] = row
    hardened = set(REQUIRED_BUNDLE_ARTIFACTS) - {"manifest.json"}
    if set(inventory) != hardened:
        raise BundleParseError(
            "source bundle manifest artifact inventory is incomplete",
            tag="bundle.parsed.manifest-invalid",
        )
    return inventory


def _authenticated_bundle_snapshots(
    bundle_dir: Path, *, allow_transaction: bool = False
) -> tuple[dict[str, bytes], bytes]:
    """Authenticate one complete bundle generation behind a stable manifest."""
    manifest_path = bundle_dir / "manifest.json"
    transaction_path = bundle_dir / _TRANSACTION_NAME
    if not allow_transaction and os.path.lexists(transaction_path):
        raise BundleParseError(
            "source bundle publication transaction is still present",
            tag="bundle.parsed.manifest-invalid",
        )
    manifest_before = _read_stable_bundle_bytes(
        bundle_dir, manifest_path, "source bundle manifest"
    )
    manifest = _parse_json_mapping(manifest_before, label="source bundle manifest")
    inventory = _manifest_inventory(manifest)
    snapshots: dict[str, bytes] = {}
    for name in REQUIRED_BUNDLE_ARTIFACTS:
        if name == "manifest.json":
            continue
        raw = _read_stable_bundle_bytes(
            bundle_dir, bundle_dir / name, f"bundle artifact {name}"
        )
        row = inventory.get(name)
        if row is not None and (
            row.get("sha256") != hashlib.sha256(raw).hexdigest()
            or row.get("size_bytes") != len(raw)
        ):
            raise BundleParseError(
                f"source bundle manifest does not authenticate {name}",
                tag="bundle.parsed.manifest-invalid",
            )
        snapshots[name] = raw
    manifest_after = _read_stable_bundle_bytes(
        bundle_dir, manifest_path, "source bundle manifest"
    )
    if (
        not allow_transaction
        and os.path.lexists(transaction_path)
        or manifest_before != manifest_after
    ):
        raise BundleParseError(
            "source bundle manifest changed during authentication",
            tag="bundle.parsed.manifest-invalid",
        )
    return snapshots, manifest_before


def _transaction_payload(
    *,
    run_id: str,
    original: dict[str, bytes],
    original_manifest: bytes,
    targets: dict[Path, bytes],
) -> bytes:
    target_by_name = {path.name: payload for path, payload in targets.items()}
    return (
        json.dumps(
            {
                "schema_version": "texas-hardening-transaction.v1",
                "transaction_id": secrets.token_hex(16),
                "run_id": run_id,
                "original_manifest_sha256": hashlib.sha256(
                    original_manifest
                ).hexdigest(),
                "original_manifest_b64": base64.b64encode(original_manifest).decode(
                    "ascii"
                ),
                "original": {
                    name: {
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "payload_b64": base64.b64encode(raw).decode("ascii"),
                    }
                    for name, raw in sorted(original.items())
                },
                "targets": {
                    name: {
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "payload_b64": base64.b64encode(raw).decode("ascii"),
                    }
                    for name, raw in sorted(target_by_name.items())
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _publish_transaction_marker(path: Path, payload: bytes) -> None:
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
    except OSError as exc:
        if descriptor is not None:
            with suppress(OSError):
                os.close(descriptor)
        if created:
            with suppress(OSError):
                path.unlink()
                _fsync_directory(path.parent)
        raise BundleParseError(
            "cannot exclusively acquire Texas hardening transaction",
            tag="bundle.parsed.persistence-failed",
        ) from exc


def _remove_marker_durably(path: Path, *, expected: bytes) -> None:
    if (
        _read_stable_bundle_bytes(
            path.parent, path, "Texas hardening transaction"
        )
        != expected
    ):
        raise BundleParseError(
            "Texas hardening transaction ownership changed",
            tag="bundle.parsed.persistence-failed",
        )
    path.unlink()
    _fsync_directory(path.parent)


def _validate_hardened_target(
    snapshots: dict[str, bytes], *, expected_run_id: str
) -> None:
    """Validate recovered/final target semantics before publishing a manifest."""
    try:
        extracted = snapshots["extracted.md"].decode("utf-8")
        metadata = json.loads(
            snapshots["metadata.json"].decode("utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise BundleParseError(
            "hardened target extraction or metadata is malformed",
            tag="bundle.parsed.persistence-failed",
        ) from exc
    if not isinstance(metadata, dict):
        raise BundleParseError(
            "hardened target metadata root is invalid",
            tag="bundle.parsed.persistence-failed",
        )
    report = _load_yaml_bytes(
        snapshots["extraction-report.yaml"], label="hardened extraction-report.yaml"
    )
    result = _load_yaml_bytes(snapshots["result.yaml"], label="hardened result.yaml")
    try:
        sections = parse_extracted_primary_sections(metadata=metadata, text=extracted)
    except SourceBundleError as exc:
        raise BundleParseError(str(exc), tag=exc.tag) from exc
    if any(
        extracted_section_digest(section.body) != section.extracted_content_digest
        for section in sections
    ):
        raise BundleParseError(
            "hardened target section digest is inconsistent",
            tag="bundle.parsed.persistence-failed",
        )
    validated_claims = 0
    for section in sections:
        anchored, claim_count = _anchor_extracted_claims(section.body, section.source_id)
        if anchored != section.body or claim_count < 1:
            raise BundleParseError(
                "hardened target claim provenance is inconsistent",
                tag="bundle.parsed.persistence-failed",
            )
        validated_claims += claim_count
    run_ids = (metadata.get("run_id"), report.get("run_id"), result.get("run_id"))
    rubric = report.get("g0_evidence_sentence_rubric")
    dimensions = rubric.get("dimensions") if isinstance(rubric, dict) else None
    if (
        not expected_run_id
        or any(value != expected_run_id for value in run_ids)
        or result.get("status") != report.get("overall_status")
        or not isinstance(rubric, dict)
        or rubric.get("passed") is not True
        or not isinstance(dimensions, dict)
        or set(dimensions) != set(G0_RUBRIC_DIMENSIONS)
        or any(
            not isinstance(dimensions[name], dict)
            or dimensions[name].get("passed") is not True
            for name in G0_RUBRIC_DIMENSIONS
        )
        or rubric.get("claim_count") != validated_claims
    ):
        raise BundleParseError(
            "hardened target receipt authority is inconsistent",
            tag="bundle.parsed.persistence-failed",
        )


def _recover_hardening_transaction(bundle_dir: Path) -> None:
    """Converge a manifest-withdrawn owned transaction to its recorded target."""
    transaction_path = bundle_dir / _TRANSACTION_NAME
    if not os.path.lexists(transaction_path):
        return
    transaction_raw = _read_stable_bundle_bytes(
        bundle_dir, transaction_path, "Texas hardening transaction"
    )
    transaction = _parse_json_mapping(
        transaction_raw,
        label="Texas hardening transaction",
    )
    if transaction.get("schema_version") != "texas-hardening-transaction.v1":
        raise BundleParseError(
            "Texas hardening transaction identity is invalid",
            tag="bundle.parsed.persistence-failed",
        )
    original = transaction.get("original")
    targets = transaction.get("targets")
    run_id = transaction.get("run_id")
    transaction_id = transaction.get("transaction_id")
    original_manifest_b64 = transaction.get("original_manifest_b64")
    original_manifest_sha256 = transaction.get("original_manifest_sha256")
    expected_original = set(REQUIRED_BUNDLE_ARTIFACTS) - {"manifest.json"}
    expected_targets = {
        "extracted.md",
        "metadata.json",
        "extraction-report.yaml",
        "result.yaml",
    }
    if (
        not isinstance(original, dict)
        or not isinstance(run_id, str)
        or not isinstance(transaction_id, str)
        or re.fullmatch(r"[0-9a-f]{32}", transaction_id) is None
        or set(original) != expected_original
    ):
        raise BundleParseError(
            "Texas hardening transaction is incomplete",
            tag="bundle.parsed.persistence-failed",
        )
    try:
        original_manifest = base64.b64decode(original_manifest_b64, validate=True)
    except (ValueError, TypeError) as exc:
        raise BundleParseError(
            "Texas hardening transaction manifest binding is invalid",
            tag="bundle.parsed.persistence-failed",
        ) from exc
    if original_manifest_sha256 != hashlib.sha256(original_manifest).hexdigest():
        raise BundleParseError(
            "Texas hardening transaction manifest digest is invalid",
            tag="bundle.parsed.persistence-failed",
        )
    manifest = _parse_json_mapping(original_manifest, label="withdrawn source manifest")
    inventory = _manifest_inventory(manifest)
    decoded_originals: dict[Path, bytes] = {}
    for name, row in inventory.items():
        original_row = original.get(name)
        if not isinstance(original_row, dict):
            raise BundleParseError(
                "Texas hardening transaction original generation is invalid",
                tag="bundle.parsed.persistence-failed",
            )
        try:
            original_payload = base64.b64decode(
                original_row.get("payload_b64", ""), validate=True
            )
        except (ValueError, TypeError) as exc:
            raise BundleParseError(
                "Texas hardening transaction original payload is invalid",
                tag="bundle.parsed.persistence-failed",
            ) from exc
        original_digest = hashlib.sha256(original_payload).hexdigest()
        if (
            original_row.get("sha256") != original_digest
            or row.get("sha256") != original_digest
            or row.get("size_bytes") != len(original_payload)
        ):
            raise BundleParseError(
                "Texas hardening transaction disagrees with withdrawn manifest",
                tag="bundle.parsed.persistence-failed",
            )
        decoded_originals[bundle_dir / name] = original_payload
    current_by_name = {
        name: _read_stable_bundle_bytes(
            bundle_dir, bundle_dir / name, f"transaction artifact {name}"
        )
        for name in expected_original
    }
    all_original = all(
        hashlib.sha256(current_by_name[name]).hexdigest()
        == original[name]["sha256"]
        for name in expected_original
    )
    if not all_original and (
        not isinstance(targets, dict) or set(targets) != expected_targets
    ):
        raise BundleParseError(
            "Texas hardening transaction target generation is incomplete",
            tag="bundle.parsed.persistence-failed",
        )
    for name in REQUIRED_BUNDLE_ARTIFACTS:
        if name == "manifest.json":
            continue
        current = current_by_name[name]
        target_row = targets.get(name) if isinstance(targets, dict) else None
        original_row = original.get(name)
        allowed = {
            original_row.get("sha256") if isinstance(original_row, dict) else None
        }
        if not all_original and isinstance(target_row, dict):
            try:
                target = base64.b64decode(target_row.get("payload_b64", ""), validate=True)
            except (ValueError, TypeError) as exc:
                raise BundleParseError(
                    "Texas hardening transaction target is invalid",
                    tag="bundle.parsed.persistence-failed",
                ) from exc
            if target_row.get("sha256") != hashlib.sha256(target).hexdigest():
                raise BundleParseError(
                    "Texas hardening transaction target digest is invalid",
                    tag="bundle.parsed.persistence-failed",
                )
            allowed.add(target_row["sha256"])
        if not all_original and hashlib.sha256(current).hexdigest() not in allowed:
            raise BundleParseError(
                f"transaction artifact {name} is neither original nor target",
                tag="bundle.parsed.persistence-failed",
            )
    staged: dict[Path, Path] = {}
    try:
        restoration = dict(decoded_originals)
        restoration[bundle_dir / "manifest.json"] = original_manifest
        for path, payload in restoration.items():
            staged[path] = _stage_bytes(path, payload)
        for path in decoded_originals:
            temporary = staged[path]
            os.replace(temporary, path)
        os.replace(staged[bundle_dir / "manifest.json"], bundle_dir / "manifest.json")
        _fsync_directory(bundle_dir)
        _authenticated_bundle_snapshots(bundle_dir, allow_transaction=True)
        _remove_marker_durably(transaction_path, expected=transaction_raw)
    finally:
        for temporary in staged.values():
            with suppress(OSError):
                temporary.unlink()


def _manifest_payload(bundle_dir: Path, run_id: str) -> dict[str, Any]:
    artifacts = []
    for name in REQUIRED_BUNDLE_ARTIFACTS:
        if name in {"manifest.json"}:
            continue
        path = bundle_dir / name
        raw = _read_stable_bundle_bytes(bundle_dir, path, f"bundle artifact {name}")
        artifacts.append(
            {
                "path": name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
            }
        )
    try:
        metadata = json.loads(
            _read_stable_bundle_bytes(
                bundle_dir, bundle_dir / "metadata.json", "source bundle metadata"
            ).decode("utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise BundleParseError(
            "hardened metadata is malformed",
            tag="bundle.parsed.persistence-failed",
        ) from exc
    generated_at = metadata.get("generated_at") if isinstance(metadata, dict) else None
    if not isinstance(generated_at, str) or not generated_at:
        raise BundleParseError(
            "source bundle metadata has no stable generated_at",
            tag="bundle.parsed.malformed",
        )
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "bundle_dir": bundle_dir.resolve().as_posix(),
        "generated_at": generated_at,
        "artifacts": artifacts,
    }


def _refresh_manifest(bundle_dir: Path, run_id: str) -> None:
    path = bundle_dir / "manifest.json"
    payload = (json.dumps(_manifest_payload(bundle_dir, run_id), indent=2) + "\n").encode(
        "utf-8"
    )
    temporary = _stage_bytes(path, payload)
    try:
        os.replace(temporary, path)
        _fsync_directory(bundle_dir)
    except OSError as exc:
        with suppress(OSError):
            temporary.unlink()
        with suppress(OSError):
            path.unlink()
            _fsync_directory(bundle_dir)
        raise BundleParseError(
            "cannot publish hardened manifest",
            tag="bundle.parsed.persistence-failed",
        ) from exc


def _harden_bundle_locked(
    bundle_dir: Path, directive_path: str | Path
) -> dict[str, Any]:
    directive = _load_directive(directive_path)
    try:
        _remove_orphaned_staging_files(bundle_dir)
        _recover_hardening_transaction(bundle_dir)
        snapshots, manifest_raw = _authenticated_bundle_snapshots(bundle_dir)
    except OSError as exc:
        raise BundleParseError(
            "cannot recover or authenticate source bundle publication",
            tag="bundle.parsed.persistence-failed",
        ) from exc
    extracted_path = bundle_dir / "extracted.md"
    metadata_path = bundle_dir / "metadata.json"
    try:
        raw_extracted = snapshots["extracted.md"].decode("utf-8")
        raw_extracted = raw_extracted.replace("\r\n", "\n").replace("\r", "\n")
        metadata = json.loads(
            snapshots["metadata.json"].decode("utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise BundleParseError(
            "source bundle extraction or metadata is malformed",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(metadata, dict):
        raise BundleParseError(
            "source bundle metadata root must be a mapping",
            tag="bundle.parsed.malformed",
        )
    report_path = bundle_dir / "extraction-report.yaml"
    result_path = bundle_dir / "result.yaml"
    report = _load_yaml_bytes(
        snapshots["extraction-report.yaml"],
        label="extraction-report.yaml",
    )
    result = _load_yaml_bytes(
        snapshots["result.yaml"],
        label="result.yaml",
    )
    run_ids = (metadata.get("run_id"), report.get("run_id"), result.get("run_id"))
    statuses = (report.get("overall_status"), result.get("status"))
    directive_run_id = directive.get("run_id")
    directive_sha256 = directive.get("_directive_sha256")
    if (
        any(not isinstance(value, str) or not value for value in run_ids)
        or len(set(run_ids)) != 1
        or any(not isinstance(value, str) or not value for value in statuses)
        or statuses[0] != statuses[1]
        or any(value not in _PUBLISHED_STATUSES for value in statuses)
        or not isinstance(directive_run_id, str)
        or directive_run_id != run_ids[0]
        or not isinstance(directive_sha256, str)
        or metadata.get("directive_sha256") != directive_sha256
    ):
        raise BundleParseError(
            "directive, bundle identity, or status disagrees with authenticated authority",
            tag="bundle.parsed.provenance-mismatch",
        )
    try:
        initial_sections = parse_extracted_primary_sections(
            metadata=metadata, text=raw_extracted
        )
    except SourceBundleError as exc:
        raise BundleParseError(str(exc), tag=exc.tag) from exc
    if any(
        extracted_section_digest(section.body) != section.extracted_content_digest
        for section in initial_sections
    ):
        raise BundleParseError(
            "incoming primary projection digest is inconsistent",
            tag="bundle.parsed.provenance-mismatch",
        )
    observed_words = sum(len(section.body.split()) for section in initial_sections)
    expected_floor = _expected_word_floor(directive)
    if expected_floor and observed_words < expected_floor:
        raise RetrievalScopeError(observed_words, expected_floor)

    claim_count = 0
    section_claim_counts: dict[str, int] = {}
    rebuilt: list[str] = []
    cursor = 0
    for section in initial_sections:
        rebuilt.append(raw_extracted[cursor : section.content_start])
        anchored_body, section_claims = _anchor_extracted_claims(
            section.body, section.source_id
        )
        rebuilt.append(anchored_body)
        claim_count += section_claims
        section_claim_counts[section.source_id] = section_claims
        cursor = section.end
    rebuilt.append(raw_extracted[cursor:])
    anchored_text = "".join(rebuilt)
    try:
        final_sections = parse_extracted_primary_sections(
            metadata=metadata, text=anchored_text
        )
    except SourceBundleError as exc:
        raise BundleParseError(str(exc), tag=exc.tag) from exc
    if [
        (section.source_id, section.ref, section.section_title)
        for section in final_sections
    ] != [
        (section.source_id, section.ref, section.section_title)
        for section in initial_sections
    ]:
        raise BundleParseError(
            "hardening changed primary section identity",
            tag="bundle.parsed.provenance-mismatch",
        )
    if any(section_claim_counts.get(section.source_id, 0) == 0 for section in final_sections):
        raise BundleParseError(
            "every primary source section must contain an anchorable claim",
            tag="bundle.parsed.provenance-mismatch",
        )

    final_digest_by_id = {
        section.source_id: extracted_section_digest(section.body)
        for section in final_sections
    }
    updated_metadata = json.loads(json.dumps(metadata))
    updated_rows = updated_metadata["source_authority"]
    for row in updated_rows:
        source_id = row.get("source_id") if isinstance(row, dict) else None
        if source_id in final_digest_by_id:
            row["extracted_content_digest"] = final_digest_by_id[source_id]

    hints = _cross_validation_hints(directive)
    prior_cross_validation = report.get("cross_validation", [])
    if isinstance(prior_cross_validation, dict):
        prior_entries = prior_cross_validation.get("entries", [])
    else:
        prior_entries = prior_cross_validation
    if not isinstance(prior_entries, list):
        raise BundleParseError(
            "cross-validation entries are malformed",
            tag="bundle.parsed.malformed",
        )
    rubric_checks = {
        "completeness": len(section_claim_counts) == len(final_sections),
        "readability": all(section.body.strip() for section in final_sections),
        "anchorability": all(
            section_claim_counts.get(section.source_id, 0) > 0
            for section in final_sections
        ),
        "provenance": all(
            f"[evidence: {section.source_id}]" in section.body
            for section in final_sections
        ),
        "planning_usability": observed_words >= expected_floor,
        "fidelity_usability": [
            (section.source_id, section.ref, section.section_title)
            for section in final_sections
        ]
        == [
            (section.source_id, section.ref, section.section_title)
            for section in initial_sections
        ],
    }
    if not all(rubric_checks.values()):
        raise BundleParseError(
            "G0 evidence rubric did not pass every checked dimension",
            tag="bundle.parsed.provenance-mismatch",
        )
    report["g0_evidence_sentence_rubric"] = {
        "passed": all(rubric_checks.values()),
        "claim_count": claim_count,
        "dimensions": {
            dim: {
                "passed": rubric_checks[dim],
                "evidence_sentence": (
                    f"{dim} verified against {len(final_sections)} "
                    "bounded primary source section(s)"
                ),
            }
            for dim in G0_RUBRIC_DIMENSIONS
        },
    }
    report["cross_validation"] = {
        "applied": bool(hints),
        "reason": None if hints else "no hints supplied by directive",
        "hints": hints,
        "outcomes": [
            {"hint": hint, "applied": True, "outcome": "recorded-for-vera-g0"}
            for hint in hints
        ],
        "entries": prior_entries,
    }
    result["artifacts"] = list(REQUIRED_BUNDLE_ARTIFACTS)

    payloads = {
        extracted_path: anchored_text.encode("utf-8"),
        metadata_path: (json.dumps(updated_metadata, indent=2) + "\n").encode("utf-8"),
        report_path: yaml.safe_dump(
            report, sort_keys=False, default_flow_style=False
        ).encode("utf-8"),
        result_path: yaml.safe_dump(
            result, sort_keys=False, default_flow_style=False
        ).encode("utf-8"),
    }
    staged: dict[Path, Path] = {}
    transaction_path = bundle_dir / _TRANSACTION_NAME
    try:
        for path, payload in payloads.items():
            staged[path] = _stage_bytes(path, payload)
        run_id = str(result.get("run_id") or report.get("run_id") or "")
        transaction_raw = _transaction_payload(
            run_id=run_id,
            original=snapshots,
            original_manifest=manifest_raw,
            targets=payloads,
        )
        _publish_transaction_marker(transaction_path, transaction_raw)
        manifest_path = bundle_dir / "manifest.json"
        manifest_path.unlink()
        _fsync_directory(bundle_dir)
        for path, temporary in staged.items():
            os.replace(temporary, path)
        _fsync_directory(bundle_dir)
        final_snapshots = {
            name: _read_stable_bundle_bytes(
                bundle_dir, bundle_dir / name, f"hardened artifact {name}"
            )
            for name in set(REQUIRED_BUNDLE_ARTIFACTS) - {"manifest.json"}
        }
        if final_snapshots["extracted.md"] != anchored_text.encode("utf-8"):
            raise BundleParseError(
                "hardened extraction changed before manifest publication",
                tag="bundle.parsed.persistence-failed",
            )
        _validate_hardened_target(final_snapshots, expected_run_id=run_id)
        _refresh_manifest(bundle_dir, run_id)
        _remove_marker_durably(transaction_path, expected=transaction_raw)
    except (OSError, UnicodeDecodeError) as exc:
        raise BundleParseError(
            "cannot publish coherent hardened source bundle",
            tag="bundle.parsed.persistence-failed",
        ) from exc
    finally:
        for temporary in staged.values():
            with suppress(OSError):
                temporary.unlink()
    return {"word_count": observed_words, "expected_floor": expected_floor}


def _harden_bundle(bundle_dir: Path, directive_path: str | Path) -> dict[str, Any]:
    with _exclusive_hardening_lock(bundle_dir):
        return _harden_bundle_locked(bundle_dir, directive_path)


def _require_exit_status_consistency(exit_code: int, status: str) -> None:
    expected_status = {0: "complete", 10: "complete_with_warnings", 20: "blocked"}[
        exit_code
    ]
    if status != expected_status:
        raise BundleDispatchError(
            "texas dispatch exit_code contradicts authenticated bundle status",
            tag="bundle.parsed.provenance-mismatch",
        )


def act(
    state: RunState,
    *,
    dispatch_func: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("texas act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "texas act expected final plan resolution entry with cache_prefix_hash"
        )
    envelope_payload = _decode_envelope_payload(state)
    directive_path = envelope_payload.get("directive_path")
    bundle_target = envelope_payload.get("bundle_dir")
    if directive_path and bundle_target:
        dispatch_receipt = dispatch_func(
            directive_path=directive_path,
            bundle_dir=bundle_target,
        )
    else:
        dispatch_receipt = dispatch_func()
    if not isinstance(dispatch_receipt, dict):
        raise BundleDispatchError(
            "texas dispatch receipt must be a mapping",
            tag="bundle.parsed.wrong-type",
        )
    bundle_path = dispatch_receipt.get("bundle_dir")
    if not bundle_path:
        raise BundleDispatchError(
            "texas dispatch receipt missing bundle_dir",
            tag="bundle.parsed.missing-key",
        )
    bundle_dir = Path(str(bundle_path))
    if "exit_code" not in dispatch_receipt:
        raise BundleDispatchError(
            "texas dispatch receipt missing exit_code",
            tag="bundle.parsed.missing-key",
        )
    raw_exit_code = dispatch_receipt["exit_code"]
    if isinstance(raw_exit_code, bool) or not (
        isinstance(raw_exit_code, int)
        or isinstance(raw_exit_code, str)
        and re.fullmatch(r"\d{1,3}", raw_exit_code) is not None
    ):
        raise BundleDispatchError(
            "texas dispatch receipt exit_code must be an integer",
            tag="bundle.parsed.wrong-type",
        )
    exit_code = int(raw_exit_code)
    if exit_code == 30:
        raise BundleDispatchError(
            "texas wrangler reported hard error (exit 30); bundle not trusted",
            tag="bundle.parsed.exit-30",
        )
    if exit_code not in (0, 10, 20):
        raise BundleDispatchError(
            f"texas wrangler returned unexpected exit code {exit_code}",
            tag="bundle.parsed.unknown-exit",
        )
    if bundle_target:
        try:
            expected_bundle = Path(str(bundle_target)).resolve(strict=True)
            received_bundle = bundle_dir.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise BundleDispatchError(
                "texas dispatch bundle coordinate is unreadable",
                tag="bundle.parsed.unsafe-artifact",
            ) from exc
        if received_bundle != expected_bundle:
            raise BundleDispatchError(
                "texas dispatch receipt substituted a different bundle target",
                tag="bundle.parsed.provenance-mismatch",
            )
    # exit 10 = complete_with_warnings per the wrangler taxonomy
    # (run_wrangler.py EXIT_COMPLETE_WITH_WARNINGS). The bundle is real and
    # hardened below exactly like exit 0; the parsed status surfaces the
    # warning state. The prior exit-10 -> "no-results" early-return discarded
    # a valid bundle (Trial-3 attempt-3 finding 2026-06-11: 903 extracted
    # words dropped) — the wrangler has no "no-results" status in its
    # taxonomy, so that mapping was speculative and is retired.
    try:
        if not directive_path:
            with _exclusive_hardening_lock(bundle_dir):
                parsed, snapshots = _load_bundle_snapshot_locked(bundle_dir)
                _require_exit_status_consistency(exit_code, parsed["status"])
            try:
                extracted = snapshots["extracted.md"].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise BundleParseError(
                    "authenticated extracted.md is not UTF-8",
                    tag="bundle.parsed.malformed",
                ) from exc
            hardening = {"word_count": len(extracted.split()), "expected_floor": 0}
        else:
            with _exclusive_hardening_lock(bundle_dir):
                _remove_orphaned_staging_files(bundle_dir)
                _recover_hardening_transaction(bundle_dir)
                pre_hardening, _snapshots = _load_bundle_snapshot_locked(bundle_dir)
                _require_exit_status_consistency(
                    exit_code, pre_hardening["status"]
                )
                hardening = _harden_bundle_locked(bundle_dir, directive_path)
                parsed, _snapshots = _load_bundle_snapshot_locked(bundle_dir)
    except BundleParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    _require_exit_status_consistency(exit_code, parsed["status"])
    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "bundle_reference": str(bundle_dir),
            "status": parsed["status"],
            "overall_status": parsed["overall_status"],
            "artifacts": parsed["result"].get("artifacts", []),
            "report_schema_version": parsed["report"].get("schema_version"),
            "dispatch_exit_code": exit_code,
            "model_id": last_entry.resolved,
            "g0_word_count": hardening["word_count"],
            "g0_expected_floor": hardening["expected_floor"],
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


__all__ = [
    "BundleDispatchError",
    "BundleParseError",
    "G0_RUBRIC_DIMENSIONS",
    "REQUIRED_BUNDLE_ARTIFACTS",
    "RetrievalScopeError",
    "act",
    "load_bundle_outputs",
]
