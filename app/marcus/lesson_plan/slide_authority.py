"""Exact clustered final-slide to authored source-slide authority.

The final deck can contain more slides than the authored source deck.  This
module deliberately refuses ordinal, title, positional, and fuzzy joins.  It
resolves each final slide through the package-builder unit reference and the
unit's literal source anchors, then records an explicit source identity.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SLIDE_AUTHORITY_FILENAME = "workbook-slide-authority-map.v1.json"
SLIDE_AUTHORITY_RESOLVER_VERSION = "exact-anchor-source-slide.v1"
_SLIDE_NAME = re.compile(r"^slide-(?P<ordinal>[1-9][0-9]*)-.+\.md$")
_FINAL_SLIDE_ID = re.compile(r"^slide-(?P<ordinal>0*[1-9][0-9]*)$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class SlideAuthorityInvalidError(ValueError):
    """The declared final-to-source authority is absent, ambiguous, or stale."""


class SlideAuthorityPersistenceError(RuntimeError):
    """The authority carrier could not be durably persisted."""


def _file_identity(value: os.stat_result) -> tuple[int, int]:
    return value.st_dev, value.st_ino


def _fsync_directory(path: Path) -> None:
    """Durably order authority-map link and cleanup directory entries."""
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
            raise OSError(ctypes.get_last_error(), "cannot open authority directory")
        try:
            if not kernel32.FlushFileBuffers(handle):
                raise OSError(
                    ctypes.get_last_error(), "cannot flush authority directory"
                )
        finally:
            kernel32.CloseHandle(handle)
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read_contained_regular_bytes(root: Path, path: Path, label: str) -> bytes:
    """Read one contained regular file through the handle whose identity was checked."""
    root = Path(root)
    path = Path(path)
    try:
        resolved_root = root.resolve(strict=True)
        with path.open("rb") as handle:
            opened_before = os.fstat(handle.fileno())
            named_before = path.stat(follow_symlinks=False)
            resolved_path = path.resolve(strict=True)
            resolved_path.relative_to(resolved_root)
            if (
                not stat.S_ISREG(opened_before.st_mode)
                or not stat.S_ISREG(named_before.st_mode)
                or _file_identity(opened_before) != _file_identity(named_before)
            ):
                raise ValueError("opened authority is not the named regular file")
            raw = handle.read()
            opened_after = os.fstat(handle.fileno())
        named_after = path.stat(follow_symlinks=False)
        if (
            not stat.S_ISREG(opened_after.st_mode)
            or not stat.S_ISREG(named_after.st_mode)
            or _file_identity(opened_before) != _file_identity(opened_after)
            or _file_identity(opened_before) != _file_identity(named_after)
            or opened_before.st_size != opened_after.st_size
            or opened_before.st_mtime_ns != opened_after.st_mtime_ns
            or len(raw) != opened_after.st_size
        ):
            raise ValueError("authority changed while it was being read")
        return raw
    except (OSError, ValueError) as exc:
        raise SlideAuthorityInvalidError(f"{label} is absent, unsafe, or stale") from exc


def _validate_source_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("source_path must be a canonical POSIX path")
    raw_parts = value.split("/")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or len(raw_parts) < 2
        or raw_parts[0] != "slides"
        or any(part in {"", ".", ".."} for part in raw_parts)
        or path.as_posix() != value
    ):
        raise ValueError("source_path must remain canonically below slides/")
    return value


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SourceSlideInventoryEntryV1(_StrictModel):
    source_slide_id: str
    source_slide_ordinal: int = Field(ge=1)
    source_path: str
    source_sha256: str

    @model_validator(mode="after")
    def _closed(self) -> SourceSlideInventoryEntryV1:
        if self.source_slide_id != f"slide-{self.source_slide_ordinal}":
            raise ValueError("source slide identity/ordinal mismatch")
        if not _SHA256.fullmatch(self.source_sha256):
            raise ValueError("source_sha256 must be a canonical sha256 digest")
        _validate_source_path(self.source_path)
        return self


class WorkbookSlideAuthorityRowV1(_StrictModel):
    final_slide_id: str
    unit_id: str
    source_slide_id: str
    source_slide_ordinal: int = Field(ge=1)
    source_path: str
    source_sha256: str
    matched_anchors: tuple[str, ...]
    cluster_id: str | None = None
    cluster_role: Literal["head", "interstitial"]
    parent_unit_id: str | None = None

    @model_validator(mode="after")
    def _closed(self) -> WorkbookSlideAuthorityRowV1:
        if _FINAL_SLIDE_ID.fullmatch(self.final_slide_id) is None:
            raise ValueError("invalid final_slide_id")
        if not self.unit_id or self.unit_id != self.unit_id.strip():
            raise ValueError("invalid unit_id")
        if self.source_slide_id != f"slide-{self.source_slide_ordinal}":
            raise ValueError("source slide identity/ordinal mismatch")
        _validate_source_path(self.source_path)
        if not _SHA256.fullmatch(self.source_sha256):
            raise ValueError("source_sha256 must be a canonical sha256 digest")
        if not self.matched_anchors or len(set(self.matched_anchors)) != len(
            self.matched_anchors
        ):
            raise ValueError("matched anchors must be nonempty and unique")
        if any(not anchor.strip() for anchor in self.matched_anchors):
            raise ValueError("matched anchors may not be blank")
        if self.cluster_id is not None and not self.cluster_id.strip():
            raise ValueError("cluster_id may not be blank")
        if self.parent_unit_id is not None and not self.parent_unit_id.strip():
            raise ValueError("parent_unit_id may not be blank")
        if self.cluster_role == "interstitial" and not self.parent_unit_id:
            raise ValueError("interstitial requires parent_unit_id")
        if self.cluster_role == "head" and self.parent_unit_id is not None:
            raise ValueError("head cannot carry parent_unit_id")
        return self


class WorkbookSlideAuthorityMapV1(_StrictModel):
    schema_version: Literal["workbook-slide-authority-map.v1"] = (
        "workbook-slide-authority-map.v1"
    )
    resolver_version: Literal["exact-anchor-source-slide.v1"] = (
        "exact-anchor-source-slide.v1"
    )
    manifest_digest: str
    plan_units_digest: str
    plan_sidecar_digest: str
    plan_contribution_digest: str
    package_slides_digest: str
    package_contribution_digest: str
    source_inventory: tuple[SourceSlideInventoryEntryV1, ...]
    source_inventory_digest: str
    rows: tuple[WorkbookSlideAuthorityRowV1, ...]
    map_digest: str

    @model_validator(mode="after")
    def _closed(self) -> WorkbookSlideAuthorityMapV1:
        for value in (
            self.manifest_digest,
            self.plan_units_digest,
            self.plan_sidecar_digest,
            self.plan_contribution_digest,
            self.package_slides_digest,
            self.package_contribution_digest,
            self.source_inventory_digest,
            self.map_digest,
        ):
            if not _SHA256.fullmatch(value):
                raise ValueError("authority map digests must be canonical sha256 values")
        final_ids = tuple(row.final_slide_id for row in self.rows)
        final_ordinals = tuple(
            int(_FINAL_SLIDE_ID.fullmatch(value).group("ordinal"))
            for value in final_ids
        )
        if len(set(final_ids)) != len(final_ids) or len(set(final_ordinals)) != len(
            final_ordinals
        ):
            raise ValueError("duplicate final slide authority row")
        if not self.rows:
            raise ValueError("authority map requires rows")
        unit_ids = tuple(row.unit_id for row in self.rows)
        if len(set(unit_ids)) != len(unit_ids):
            raise ValueError("duplicate plan unit authority row")
        row_by_unit = {row.unit_id: row for row in self.rows}
        for row in self.rows:
            if row.cluster_role != "interstitial":
                continue
            parent = row_by_unit.get(row.parent_unit_id or "")
            if parent is None or parent.cluster_role != "head":
                raise ValueError("interstitial parent must name an authority head")
            if (
                row.source_slide_id,
                row.source_slide_ordinal,
                row.source_path,
                row.source_sha256,
            ) != (
                parent.source_slide_id,
                parent.source_slide_ordinal,
                parent.source_path,
                parent.source_sha256,
            ):
                raise ValueError("interstitial source authority disagrees with parent")
            if row.cluster_id != parent.cluster_id:
                raise ValueError("interstitial cluster authority disagrees with parent")
        inventory_payload = tuple(
            entry.model_dump(mode="json") for entry in self.source_inventory
        )
        if self.source_inventory_digest != _digest(inventory_payload):
            raise ValueError("source inventory digest mismatch")
        inventory_keys = tuple(
            (
                entry.source_slide_id,
                entry.source_slide_ordinal,
                entry.source_path,
                entry.source_sha256,
            )
            for entry in self.source_inventory
        )
        if (
            len({item[0] for item in inventory_keys}) != len(inventory_keys)
            or len({item[1] for item in inventory_keys}) != len(inventory_keys)
            or len({item[2] for item in inventory_keys}) != len(inventory_keys)
        ):
            raise ValueError("source inventory identities must be unique")
        inventory_set = set(inventory_keys)
        for row in self.rows:
            row_key = (
                row.source_slide_id,
                row.source_slide_ordinal,
                row.source_path,
                row.source_sha256,
            )
            if row_key not in inventory_set:
                raise ValueError("authority row does not match source inventory")
        expected = slide_authority_digest(self, exclude_map_digest=True)
        if self.map_digest != expected:
            raise ValueError("authority map self-digest mismatch")
        return self


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def canonical_source_content_digest(value: str) -> str:
    """Digest source text under the authority contract's sole normalization."""
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return _bytes_digest(normalized.encode("utf-8"))


def slide_authority_digest(
    authority: WorkbookSlideAuthorityMapV1 | dict[str, Any],
    *,
    exclude_map_digest: bool = False,
) -> str:
    payload = (
        authority.model_dump(mode="json")
        if isinstance(authority, WorkbookSlideAuthorityMapV1)
        else dict(authority)
    )
    if exclude_map_digest:
        payload.pop("map_digest", None)
    return _digest(payload)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_slide_authority_map(run_dir: Path) -> WorkbookSlideAuthorityMapV1:
    """Read one contained, regular, duplicate-key-free authority sidecar."""
    root = Path(run_dir)
    target = root / SLIDE_AUTHORITY_FILENAME
    if target.is_symlink() or not target.is_file():
        raise SlideAuthorityInvalidError("slide authority map is absent or unsafe")
    try:
        raw_bytes = read_contained_regular_bytes(root, target, "slide authority map")
        raw = json.loads(
            raw_bytes.decode("utf-8"), object_pairs_hook=_unique_object
        )
        if not isinstance(raw, dict):
            raise ValueError("authority map root must be an object")
        inventory_raw = raw.get("source_inventory")
        rows_raw = raw.get("rows")
        if not isinstance(inventory_raw, list) or not isinstance(rows_raw, list):
            raise ValueError("authority map collections must be arrays")
        inventory = tuple(
            SourceSlideInventoryEntryV1.model_validate(item) for item in inventory_raw
        )
        normalized_rows: list[dict[str, Any]] = []
        for item in rows_raw:
            if not isinstance(item, dict):
                raise ValueError("authority map rows must be objects")
            matched_anchors = item.get("matched_anchors")
            if not isinstance(matched_anchors, list) or not all(
                isinstance(anchor, str) for anchor in matched_anchors
            ):
                raise ValueError("authority map matched_anchors must be a string array")
            normalized_rows.append(
                {**item, "matched_anchors": tuple(matched_anchors)}
            )
        rows = tuple(
            WorkbookSlideAuthorityRowV1.model_validate(item)
            for item in normalized_rows
        )
        raw["source_inventory"] = inventory
        raw["rows"] = rows
        return WorkbookSlideAuthorityMapV1.model_validate(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SlideAuthorityInvalidError("slide authority map is invalid") from exc


def write_or_validate_slide_authority_map(
    run_dir: Path, expected: WorkbookSlideAuthorityMapV1
) -> Path:
    """Mint the map once without overwrite, or fully reconcile an existing map."""
    root = Path(run_dir)
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise SlideAuthorityInvalidError("run root is unavailable") from exc
    target = root / SLIDE_AUTHORITY_FILENAME
    temporary = root / f".{SLIDE_AUTHORITY_FILENAME}.tmp"
    if target.is_symlink() or temporary.is_symlink():
        raise SlideAuthorityInvalidError("slide authority persistence path is unsafe")
    if temporary.exists():
        try:
            recoverable_link = (
                target.is_file()
                and os.path.samefile(temporary, target)
                and read_slide_authority_map(root) == expected
            )
        except OSError:
            recoverable_link = False
        if recoverable_link:
            try:
                temporary.unlink()
                _fsync_directory(root)
            except OSError as exc:
                raise SlideAuthorityPersistenceError(
                    "slide authority temporary recovery failed"
                ) from exc
            return target
        raise SlideAuthorityPersistenceError(
            "slide authority temporary split-brain exists"
        )
    if target.exists():
        if read_slide_authority_map(root) != expected:
            raise SlideAuthorityInvalidError("persisted slide authority map is stale")
        return target
    payload = expected.model_dump(mode="json")
    created = False
    linked = False
    try:
        with temporary.open("x", encoding="utf-8", newline="") as handle:
            created = True
            handle.write(_canonical_json(payload) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        resolved_temp = temporary.resolve(strict=True)
        resolved_temp.relative_to(resolved_root)
        try:
            os.link(temporary, target)
            linked = True
            _fsync_directory(root)
        except FileExistsError:
            if read_slide_authority_map(root) != expected:
                raise SlideAuthorityInvalidError(
                    "concurrent slide authority map disagrees"
                ) from None
        if linked and read_slide_authority_map(root) != expected:
            raise SlideAuthorityInvalidError("persisted slide authority map disagrees")
    except (OSError, ValueError) as exc:
        if isinstance(exc, SlideAuthorityInvalidError):
            raise
        raise SlideAuthorityPersistenceError(
            "slide authority persistence failed"
        ) from exc
    finally:
        if created and temporary.exists() and not temporary.is_symlink():
            try:
                temporary.unlink()
                _fsync_directory(root)
            except OSError as exc:
                raise SlideAuthorityPersistenceError(
                    "slide authority temporary cleanup failed"
                ) from exc
    return target


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _source_inventory(
    course_source_root: Path,
) -> tuple[tuple[SourceSlideInventoryEntryV1, Path, str], ...]:
    root = Path(course_source_root)
    slides = root / "slides"
    if slides.is_symlink() or not slides.is_dir():
        raise SlideAuthorityInvalidError("slides authority must be a real directory")
    try:
        resolved_root = root.resolve(strict=True)
        resolved_slides = slides.resolve(strict=True)
        children = tuple(slides.iterdir())
    except OSError as exc:
        raise SlideAuthorityInvalidError("slides authority is unreadable") from exc
    if not _within(resolved_slides, resolved_root):
        raise SlideAuthorityInvalidError("slides authority escapes course root")
    entries: list[tuple[SourceSlideInventoryEntryV1, Path, str]] = []
    seen_ordinals: set[int] = set()
    for child in sorted(children, key=lambda item: item.name):
        match = _SLIDE_NAME.fullmatch(child.name)
        if match is None:
            continue
        ordinal = int(match.group("ordinal"))
        if ordinal in seen_ordinals:
            raise SlideAuthorityInvalidError(
                f"source slide ordinal {ordinal} matched multiple files"
            )
        if child.is_symlink() or not child.is_file():
            raise SlideAuthorityInvalidError(f"unsafe source slide: {child.name}")
        try:
            resolved = child.resolve(strict=True)
            raw = read_contained_regular_bytes(
                resolved_slides, child, f"source slide {child.name}"
            )
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise SlideAuthorityInvalidError(
                f"source slide unreadable: {child.name}"
            ) from exc
        if not _within(resolved, resolved_slides):
            raise SlideAuthorityInvalidError(f"source slide escapes root: {child.name}")
        seen_ordinals.add(ordinal)
        entries.append(
            (
                SourceSlideInventoryEntryV1(
                    source_slide_id=f"slide-{ordinal}",
                    source_slide_ordinal=ordinal,
                    source_path=child.relative_to(root).as_posix(),
                    source_sha256=_bytes_digest(raw),
                ),
                child,
                text.replace("\r\n", "\n").replace("\r", "\n"),
            )
        )
    if not entries:
        raise SlideAuthorityInvalidError("source slide inventory is empty")
    return tuple(entries)


def _included(unit: dict[str, Any]) -> bool:
    decision = unit.get("scope_decision")
    if isinstance(decision, dict):
        decision = decision.get("scope")
    if decision not in {"in-scope", "out-of-scope"}:
        raise SlideAuthorityInvalidError(
            "plan unit scope_decision must resolve to in-scope or out-of-scope"
        )
    return decision == "in-scope"


def resolve_exact_anchor_source(
    *,
    unit_id: str,
    raw_anchors: object,
    source_texts: tuple[tuple[str, str], ...],
) -> tuple[str, tuple[str, ...]]:
    """Resolve literal anchors to exactly one declared source identity.

    Matching is case-sensitive substring membership after newline normalization
    only.  This pure core is shared by Pass-1 pre-spend validation and the
    workbook slide-authority resolver so their authority semantics cannot drift.
    """
    if not isinstance(raw_anchors, list) or not raw_anchors:
        raise SlideAuthorityInvalidError(f"unit {unit_id} has no exact source anchors")
    if not source_texts or any(
        not isinstance(identity, str)
        or not identity
        or not isinstance(text, str)
        for identity, text in source_texts
    ):
        raise SlideAuthorityInvalidError("declared source inventory is invalid")
    anchors: list[str] = []
    normalized_anchors: set[str] = set()
    matched_sources: list[str] = []
    normalized_sources = tuple(
        (identity, text.replace("\r\n", "\n").replace("\r", "\n"))
        for identity, text in source_texts
    )
    for raw_anchor in raw_anchors:
        if (
            not isinstance(raw_anchor, str)
            or not raw_anchor.strip()
        ):
            raise SlideAuthorityInvalidError(
                f"unit {unit_id} carries invalid/duplicate source anchor"
            )
        anchor = raw_anchor.replace("\r\n", "\n").replace("\r", "\n")
        if anchor in normalized_anchors:
            raise SlideAuthorityInvalidError(
                f"unit {unit_id} carries invalid/duplicate source anchor"
            )
        matches = [identity for identity, text in normalized_sources if anchor in text]
        if len(matches) != 1:
            raise SlideAuthorityInvalidError(
                f"unit {unit_id} anchor must match exactly one source slide file"
            )
        anchors.append(raw_anchor)
        normalized_anchors.add(anchor)
        matched_sources.append(matches[0])
    if len(set(matched_sources)) != 1:
        raise SlideAuthorityInvalidError(
            f"unit {unit_id} anchors resolve across source slide files"
        )
    return matched_sources[0], tuple(anchors)


def _identity_digest(value: object, label: str) -> str:
    digest = str(value)
    if not _SHA256.fullmatch(digest):
        raise SlideAuthorityInvalidError(f"{label} must be a canonical sha256 digest")
    return digest


def _required_identity(row: dict[str, Any], key: str, label: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value or value != value.strip():
        raise SlideAuthorityInvalidError(f"{label} must be a nonblank string")
    return value


def _optional_identity(row: dict[str, Any], key: str, label: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value or value != value.strip():
        raise SlideAuthorityInvalidError(f"{label} must be null or a nonblank string")
    return value


def build_slide_authority_map(
    *,
    manifest_segments: object,
    plan_units: object,
    package_slides: object,
    authorized_source_ids: object,
    course_source_root: Path,
    manifest_digest: str,
    plan_sidecar_digest: str,
    plan_contribution_digest: str,
    package_contribution_digest: str,
) -> WorkbookSlideAuthorityMapV1:
    """Build an explicit authority map from closed, exact persisted inputs."""
    if not isinstance(manifest_segments, list) or not manifest_segments:
        raise SlideAuthorityInvalidError("manifest segments must be a nonempty list")
    if not isinstance(plan_units, list) or not plan_units:
        raise SlideAuthorityInvalidError("plan units must be a nonempty list")
    if not isinstance(package_slides, list) or not package_slides:
        raise SlideAuthorityInvalidError("package slides must be a nonempty list")
    if not all(isinstance(value, dict) for value in manifest_segments):
        raise SlideAuthorityInvalidError("manifest segments must be objects")
    if not all(isinstance(value, dict) for value in plan_units):
        raise SlideAuthorityInvalidError("plan units must be objects")
    if not all(isinstance(value, dict) for value in package_slides):
        raise SlideAuthorityInvalidError("package slides must be objects")

    manifest_digest = _identity_digest(manifest_digest, "manifest_digest")
    plan_sidecar_digest = _identity_digest(plan_sidecar_digest, "plan_sidecar_digest")
    plan_contribution_digest = _identity_digest(
        plan_contribution_digest, "plan_contribution_digest"
    )
    package_contribution_digest = _identity_digest(
        package_contribution_digest, "package_contribution_digest"
    )

    final_ids = [
        _required_identity(row, "slide_id", "manifest slide_id")
        for row in manifest_segments
    ]
    package_ids = [
        _required_identity(row, "slide_id", "package slide_id")
        for row in package_slides
    ]
    if any(_FINAL_SLIDE_ID.fullmatch(value) is None for value in final_ids):
        raise SlideAuthorityInvalidError("manifest carries invalid final slide identity")
    final_ordinals = [
        int(_FINAL_SLIDE_ID.fullmatch(value).group("ordinal")) for value in final_ids
    ]
    if len(set(final_ids)) != len(final_ids) or len(set(final_ordinals)) != len(
        final_ordinals
    ):
        raise SlideAuthorityInvalidError("manifest carries duplicate final slide identity")
    if package_ids != final_ids:
        raise SlideAuthorityInvalidError(
            "package slide roster/order does not equal the manifest roster"
        )

    included = [unit for unit in plan_units if _included(unit)]
    unit_by_id: dict[str, dict[str, Any]] = {}
    for unit in included:
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id or unit_id != unit_id.strip():
            raise SlideAuthorityInvalidError("plan unit carries invalid unit_id")
        if unit_id in unit_by_id:
            raise SlideAuthorityInvalidError(f"duplicate plan unit_id: {unit_id}")
        unit_by_id[unit_id] = unit
    package_unit_ids = [
        _required_identity(row, "source_ref", "package source_ref")
        for row in package_slides
    ]
    if len(set(package_unit_ids)) != len(package_unit_ids):
        raise SlideAuthorityInvalidError("package carries duplicate unit source_ref")
    if package_unit_ids != list(unit_by_id):
        raise SlideAuthorityInvalidError(
            "package unit roster/order does not equal in-scope plan units"
        )
    if (
        not isinstance(authorized_source_ids, dict)
        or set(authorized_source_ids) != set(unit_by_id)
        or not all(
            isinstance(unit_id, str)
            and isinstance(source_id, str)
            and source_id
            for unit_id, source_id in authorized_source_ids.items()
        )
    ):
        raise SlideAuthorityInvalidError(
            "Pass-1 source authority is not the exact in-scope unit projection"
        )

    inventory = _source_inventory(course_source_root)
    inventory_models = tuple(item[0] for item in inventory)
    inventory_by_path = {entry.source_path: entry for entry, _path, _text in inventory}
    inventory_texts = tuple((entry.source_path, text) for entry, _path, text in inventory)
    inventory_text_by_path = dict(inventory_texts)
    resolved_by_unit: dict[str, SourceSlideInventoryEntryV1] = {}
    anchors_by_unit: dict[str, tuple[str, ...]] = {}
    for unit_id, unit in unit_by_id.items():
        source_path, anchors = resolve_exact_anchor_source(
            unit_id=unit_id,
            raw_anchors=unit.get("source_refs"),
            source_texts=inventory_texts,
        )
        resolved_by_unit[unit_id] = inventory_by_path[source_path]
        anchors_by_unit[unit_id] = anchors
        expected_source_id = (
            f"{source_path}|"
            f"{canonical_source_content_digest(inventory_text_by_path[source_path])}"
        )
        if expected_source_id != authorized_source_ids[unit_id]:
            raise SlideAuthorityInvalidError(
                f"unit {unit_id} resolved source disagrees with Pass-1 authority"
            )

    rows: list[WorkbookSlideAuthorityRowV1] = []
    for final_id, unit_id in zip(final_ids, package_unit_ids, strict=True):
        unit = unit_by_id[unit_id]
        role = unit.get("cluster_role")
        if role not in {"head", "interstitial"}:
            raise SlideAuthorityInvalidError(f"unit {unit_id} has invalid cluster role")
        parent_id = _optional_identity(
            unit, "parent_slide_id", f"unit {unit_id} parent_slide_id"
        )
        cluster_id = _optional_identity(unit, "cluster_id", f"unit {unit_id} cluster_id")
        if role == "head":
            if parent_id is not None:
                raise SlideAuthorityInvalidError(f"head unit {unit_id} carries a parent")
        else:
            parent_unit = unit_by_id.get(parent_id or "")
            if parent_unit is None or parent_unit.get("cluster_role") != "head":
                raise SlideAuthorityInvalidError(
                    f"interstitial unit {unit_id} has no valid head parent"
                )
            if resolved_by_unit[parent_id] != resolved_by_unit[unit_id]:
                raise SlideAuthorityInvalidError(
                    f"interstitial unit {unit_id} source disagrees with parent"
                )
            parent_cluster_id = _optional_identity(
                parent_unit,
                "cluster_id",
                f"unit {parent_id} cluster_id",
            )
            if cluster_id != parent_cluster_id:
                raise SlideAuthorityInvalidError(
                    f"interstitial unit {unit_id} cluster disagrees with parent"
                )
        source = resolved_by_unit[unit_id]
        rows.append(
            WorkbookSlideAuthorityRowV1(
                final_slide_id=final_id,
                unit_id=unit_id,
                source_slide_id=source.source_slide_id,
                source_slide_ordinal=source.source_slide_ordinal,
                source_path=source.source_path,
                source_sha256=source.source_sha256,
                matched_anchors=anchors_by_unit[unit_id],
                cluster_id=cluster_id,
                cluster_role=role,
                parent_unit_id=parent_id,
            )
        )

    source_inventory_payload = tuple(
        entry.model_dump(mode="json") for entry in inventory_models
    )
    payload: dict[str, Any] = {
        "schema_version": "workbook-slide-authority-map.v1",
        "resolver_version": SLIDE_AUTHORITY_RESOLVER_VERSION,
        "manifest_digest": manifest_digest,
        "plan_units_digest": _digest(plan_units),
        "plan_sidecar_digest": plan_sidecar_digest,
        "plan_contribution_digest": plan_contribution_digest,
        "package_slides_digest": _digest(package_slides),
        "package_contribution_digest": package_contribution_digest,
        "source_inventory": source_inventory_payload,
        "source_inventory_digest": _digest(source_inventory_payload),
        "rows": tuple(row.model_dump(mode="json") for row in rows),
    }
    payload["map_digest"] = _digest(payload)
    model_payload = {
        **payload,
        "source_inventory": inventory_models,
        "rows": tuple(rows),
    }
    try:
        return WorkbookSlideAuthorityMapV1.model_validate(model_payload)
    except ValueError as exc:
        raise SlideAuthorityInvalidError(f"slide authority map invalid: {exc}") from exc


__all__ = [
    "SLIDE_AUTHORITY_FILENAME",
    "SLIDE_AUTHORITY_RESOLVER_VERSION",
    "SlideAuthorityInvalidError",
    "SlideAuthorityPersistenceError",
    "SourceSlideInventoryEntryV1",
    "WorkbookSlideAuthorityMapV1",
    "WorkbookSlideAuthorityRowV1",
    "build_slide_authority_map",
    "read_slide_authority_map",
    "read_contained_regular_bytes",
    "slide_authority_digest",
    "write_or_validate_slide_authority_map",
    "resolve_exact_anchor_source",
]
