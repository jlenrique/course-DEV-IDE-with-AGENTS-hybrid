"""Canonical processed-source contract + validators (Mine 4A).

Documents and enforces the Amelia greenlight layout:

- Lesson leaf: ``slides/`` · ``references/`` · ``assessments/``
- Run dir: ``bundle/extracted.md`` · ``g0-enrichment.json``
- Enrichment nodes carry a closed ``kind`` (AssetKind) shape-pin for Mine 5

Does not rewrite Texas/G0 ingestion or write typed folders back (Mine 4B).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.marcus.course_source.asset_records import (
    ASSET_KIND_RECONCILIATION,
    AssetKind,
)
from app.marcus.lesson_plan.g0_enrichment import ENRICHMENT_CARD_BASENAME
from app.marcus.lesson_plan.source_type import SOURCE_TYPES, TypedComponent

SCHEMA_VERSION = "0.1"

CanonicalScope = Literal["lesson_leaf", "run_dir"]

LESSON_LEAF_REQUIRED_DIRS: tuple[str, ...] = ("slides", "references", "assessments")
RUN_DIR_REQUIRED_RELATIVE: tuple[str, ...] = (
    "bundle/extracted.md",
    ENRICHMENT_CARD_BASENAME,
)

# source_type → AssetKind (extends ASSET_KIND_RECONCILIATION for consumed types)
SOURCE_TYPE_TO_ASSET_KIND: dict[str, AssetKind] = {
    "slide": AssetKind.lecture,
    "quiz": AssetKind.assessment,
    "workbook": AssetKind.project_artifact,
    "narration": AssetKind.lecture,
    "reference_citation": AssetKind.reading,
    "rubric": AssetKind.assessment,
    "exercise_lab": AssetKind.lab,
    "motion_script_storyboard": AssetKind.project_artifact,
    "discussion_forum": AssetKind.discussion_prompt,
    "assignment_instructions": AssetKind.assignment,
    "other": AssetKind.project_artifact,
}
for _alias, _target in ASSET_KIND_RECONCILIATION.items():
    SOURCE_TYPE_TO_ASSET_KIND.setdefault(_alias, AssetKind(_target))


class CanonicalProcessedSourceError(ValueError):
    """Raised when a tree fails the canonical contract (structured, fail-loud)."""


@dataclass(frozen=True)
class CanonicalPathDigest:
    """Content digest for one required path."""

    relative_path: str
    sha256: str
    present: bool


@dataclass
class CanonicalValidationResult:
    """Structured validation outcome (never a silent partial-success claim)."""

    scope: CanonicalScope
    root: Path
    ok: bool
    errors: list[str] = field(default_factory=list)
    digests: list[CanonicalPathDigest] = field(default_factory=list)
    kind_counts: dict[str, int] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def raise_if_failed(self) -> None:
        if self.ok:
            return
        joined = "; ".join(self.errors) if self.errors else "unknown canonical failure"
        raise CanonicalProcessedSourceError(
            f"canonical processed-source validation failed "
            f"(scope={self.scope}, root={self.root}): {joined}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scope": self.scope,
            "root": str(self.root),
            "ok": self.ok,
            "errors": list(self.errors),
            "digests": [
                {
                    "relative_path": d.relative_path,
                    "sha256": d.sha256,
                    "present": d.present,
                }
                for d in self.digests
            ],
            "kind_counts": dict(self.kind_counts),
        }


def resolve_asset_kind(source_type: str) -> AssetKind:
    """Map a TypedComponent ``source_type`` (or alias) to closed ``AssetKind``."""
    if source_type in SOURCE_TYPE_TO_ASSET_KIND:
        return SOURCE_TYPE_TO_ASSET_KIND[source_type]
    if source_type in ASSET_KIND_RECONCILIATION:
        return AssetKind(ASSET_KIND_RECONCILIATION[source_type])
    raise CanonicalProcessedSourceError(
        f"no AssetKind mapping for source_type={source_type!r}"
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest_path(root: Path, relative: str) -> CanonicalPathDigest:
    path = root / relative
    if not path.is_file():
        return CanonicalPathDigest(relative_path=relative, sha256="", present=False)
    return CanonicalPathDigest(
        relative_path=relative,
        sha256=_file_sha256(path),
        present=True,
    )


def validate_lesson_leaf(root: Path) -> CanonicalValidationResult:
    """Validate curated lesson-leaf layout (slides/references/assessments)."""
    root = Path(root)
    errors: list[str] = []
    digests: list[CanonicalPathDigest] = []
    if not root.is_dir():
        return CanonicalValidationResult(
            scope="lesson_leaf",
            root=root,
            ok=False,
            errors=[f"lesson leaf root is not a directory: {root}"],
        )
    for name in LESSON_LEAF_REQUIRED_DIRS:
        bucket = root / name
        if not bucket.is_dir():
            errors.append(f"missing required directory: {name}/")
            digests.append(
                CanonicalPathDigest(relative_path=f"{name}/", sha256="", present=False)
            )
            continue
        # Directory presence digest: hash of sorted relative file names + sizes
        members = sorted(p for p in bucket.rglob("*") if p.is_file())
        hasher = hashlib.sha256()
        for member in members:
            rel = member.relative_to(root).as_posix()
            hasher.update(rel.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(str(member.stat().st_size).encode("ascii"))
            hasher.update(b"\n")
        digests.append(
            CanonicalPathDigest(
                relative_path=f"{name}/",
                sha256=hasher.hexdigest(),
                present=True,
            )
        )
    ok = not errors
    return CanonicalValidationResult(
        scope="lesson_leaf",
        root=root,
        ok=ok,
        errors=errors,
        digests=digests,
    )


def _enrichment_kind_errors(payload: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    """Shape-pin: every typed_component must carry a valid closed ``kind``."""
    errors: list[str] = []
    counts: dict[str, int] = {}
    components = payload.get("typed_components")
    if components is None:
        return ["g0-enrichment.json missing typed_components"], counts
    if not isinstance(components, list):
        return ["g0-enrichment.json typed_components must be a list"], counts
    for index, raw in enumerate(components):
        if not isinstance(raw, dict):
            errors.append(f"typed_components[{index}] must be an object")
            continue
        # Validate component shape via TypedComponent (source_type closed set)
        try:
            component = TypedComponent.model_validate(raw)
        except Exception as exc:  # pydantic ValidationError
            errors.append(f"typed_components[{index}] invalid TypedComponent: {exc}")
            continue
        kind_raw = raw.get("kind")
        if kind_raw is None or (isinstance(kind_raw, str) and not kind_raw.strip()):
            # Derive expected kind for the error message / optional auto-check path
            expected = resolve_asset_kind(component.source_type)
            errors.append(
                f"typed_components[{index}] ({component.component_id}) "
                f"missing required kind (expected AssetKind "
                f"{expected.value!r} from source_type={component.source_type!r})"
            )
            continue
        try:
            kind = AssetKind(str(kind_raw))
        except ValueError:
            errors.append(
                f"typed_components[{index}] ({component.component_id}) "
                f"kind={kind_raw!r} not in AssetKind closed set"
            )
            continue
        expected = resolve_asset_kind(component.source_type)
        if kind != expected:
            errors.append(
                f"typed_components[{index}] ({component.component_id}) "
                f"kind={kind.value!r} disagrees with source_type="
                f"{component.source_type!r} (expected {expected.value!r})"
            )
            continue
        counts[kind.value] = counts.get(kind.value, 0) + 1
    return errors, counts


def validate_run_dir(root: Path) -> CanonicalValidationResult:
    """Validate run-scoped processed artifacts + enrichment kind shape-pin."""
    root = Path(root)
    errors: list[str] = []
    digests: list[CanonicalPathDigest] = []
    kind_counts: dict[str, int] = {}
    if not root.is_dir():
        return CanonicalValidationResult(
            scope="run_dir",
            root=root,
            ok=False,
            errors=[f"run dir root is not a directory: {root}"],
        )
    for relative in RUN_DIR_REQUIRED_RELATIVE:
        digest = _digest_path(root, relative)
        digests.append(digest)
        if not digest.present:
            errors.append(f"missing required file: {relative}")
    enrichment_path = root / ENRICHMENT_CARD_BASENAME
    if enrichment_path.is_file():
        try:
            payload = json.loads(enrichment_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"g0-enrichment.json unreadable/malformed: {exc}")
        else:
            if not isinstance(payload, dict):
                errors.append("g0-enrichment.json must be a JSON object")
            else:
                kind_errors, kind_counts = _enrichment_kind_errors(payload)
                errors.extend(kind_errors)
    ok = not errors
    return CanonicalValidationResult(
        scope="run_dir",
        root=root,
        ok=ok,
        errors=errors,
        digests=digests,
        kind_counts=kind_counts,
    )


def validate_canonical_tree(
    root: Path,
    *,
    scope: CanonicalScope,
) -> CanonicalValidationResult:
    """Validate a path against the canonical processed-source contract."""
    if scope == "lesson_leaf":
        return validate_lesson_leaf(root)
    if scope == "run_dir":
        return validate_run_dir(root)
    raise CanonicalProcessedSourceError(f"unknown canonical scope: {scope!r}")


def annotate_typed_components_with_kind(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Return a copy of enrichment payload with ``kind`` set on each component.

    Used by liveproof / migration helpers. Does not mutate the input dict.
    """
    import copy

    out = copy.deepcopy(payload)
    components = out.get("typed_components")
    if not isinstance(components, list):
        raise CanonicalProcessedSourceError(
            "annotate: typed_components must be a list"
        )
    for raw in components:
        if not isinstance(raw, dict):
            raise CanonicalProcessedSourceError(
                "annotate: typed_components entry must be an object"
            )
        component = TypedComponent.model_validate(raw)
        raw["kind"] = resolve_asset_kind(component.source_type).value
    return out


def write_canonical_contract_doc(path: Path) -> Path:
    """Write the SSOT markdown contract (Mine 4A documentation deliverable)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Canonical processed-source structure (Mine 4A)

**Schema version:** {SCHEMA_VERSION}  
**Authority:** Phase-2 six-mine greenlight (Amelia defaults) + this module.

## Lesson leaf (curated corpus)

Required directories (all must exist):

- `slides/`
- `references/`
- `assessments/`

Optional companions (not required for PASS): `urls.txt`, `README.md`.

## Run directory (processed trial artifacts)

Required files:

- `bundle/extracted.md`
- `{ENRICHMENT_CARD_BASENAME}`

## Enrichment `kind` shape-pin (gates Mine 5 Drill)

Every `typed_components[]` entry in `{ENRICHMENT_CARD_BASENAME}` MUST carry:

- `source_type` ∈ closed SourceType set (existing)
- `kind` ∈ `AssetKind` closed set, reconciled from `source_type` via
  `SOURCE_TYPE_TO_ASSET_KIND` / `ASSET_KIND_RECONCILIATION`

Missing or disagreeing `kind` → structured validation failure (not partial success).

## Closed AssetKind values

{", ".join(repr(k.value) for k in AssetKind)}

## Closed source_type values (reference)

{", ".join(sorted(SOURCE_TYPES))} + `other` escape hatch.

## OUT of Mine 4A

Automated normalize writeback to typed folders; historical backfill; cloud storage;
Drill projector (Mine 5); workbook prose (Mine 6).
"""
    path.write_text(body, encoding="utf-8")
    return path


__all__ = [
    "ASSET_KIND_RECONCILIATION",
    "CanonicalPathDigest",
    "CanonicalProcessedSourceError",
    "CanonicalScope",
    "CanonicalValidationResult",
    "LESSON_LEAF_REQUIRED_DIRS",
    "RUN_DIR_REQUIRED_RELATIVE",
    "SCHEMA_VERSION",
    "SOURCE_TYPE_TO_ASSET_KIND",
    "annotate_typed_components_with_kind",
    "resolve_asset_kind",
    "validate_canonical_tree",
    "validate_lesson_leaf",
    "validate_run_dir",
    "write_canonical_contract_doc",
]
