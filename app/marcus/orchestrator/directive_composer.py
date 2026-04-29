"""G0 directive composition for production trials (Story 7a.1).

Closes trial-475 Gap 2 (silent gate-bypass from missing directive composition).
The composer is a pure function of (corpus_path, source_authority_map,
operator_directives) — no LLM, no network, no side-effecting IO beyond what the
caller passes in. Marcus invokes ``compose_directive`` at trial-start, then
``materialize_directive`` writes the composed directive to
``state/runs/<run_id>/directive.yaml`` for operator confirm-or-edit before Texas
dispatches.

Composition Spec §3.1/§3.5/§3.6 honored. ADR-D6 manifest-as-graph-config: a
companion ``directive-composer`` node is declared in
``state/config/pipeline-manifest.yaml`` with ``dependencies: []``.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_EXPECTED_MIN_WORDS = 200
URLS_FILE_BASENAMES = ("urls.txt", "URLS.txt", "Urls.txt")


class EmptyCorpusError(RuntimeError):
    """Corpus dir contains no on-disk files and no urls.txt — refuse silent empty directive."""


class DirectiveCompositionError(RuntimeError):
    """Raised on ambiguous source-authority-map (e.g. duplicate ref_id) per W-R2."""


@dataclass(frozen=True)
class ComposedDirectiveSource:
    """Single ``sources[]`` entry in the composed directive."""

    ref_id: str
    provider: str
    locator: str
    role: str
    description: str
    expected_min_words: int


@dataclass(frozen=True)
class ComposedDirective:
    """Pure-function output of ``compose_directive``.

    Shape mirrors the canonical Texas directive at
    ``tests/fixtures/specialists/texas/fixture_directive.yaml``.
    """

    run_id: str
    sources: tuple[ComposedDirectiveSource, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Round-trip-safe dict for ruamel emission."""
        return {
            "run_id": self.run_id,
            "sources": [asdict(src) for src in self.sources],
        }


def _walk_corpus_files(corpus_path: Path) -> list[Path]:
    """Sorted on-disk file walk under corpus dir (excludes urls.txt sibling)."""
    if not corpus_path.exists():
        raise EmptyCorpusError(
            f"corpus path does not exist: {corpus_path}"
        )
    if not corpus_path.is_dir():
        raise EmptyCorpusError(
            f"corpus path is not a directory: {corpus_path}"
        )
    files = [
        p
        for p in sorted(corpus_path.rglob("*"))
        if p.is_file() and p.name not in URLS_FILE_BASENAMES
    ]
    return files


def _read_urls_file(corpus_path: Path) -> list[str]:
    """Return non-blank, non-comment URL lines if a urls.txt sibling exists."""
    for basename in URLS_FILE_BASENAMES:
        urls_file = corpus_path / basename
        if urls_file.is_file():
            return [
                line.strip()
                for line in urls_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
    return []


def _default_source_authority_map(
    corpus_path: Path,
) -> dict[str, ComposedDirectiveSource]:
    """Build default sources[] from on-disk files + urls.txt sibling.

    First file → ``role: primary``; subsequent → ``role: supporting``.
    URL entries (from a urls.txt flat file) emit ``provider: url`` after files.
    Cross-platform stable: paths are POSIX-form via ``Path.as_posix()`` (W-R6).
    """
    files = _walk_corpus_files(corpus_path)
    urls = _read_urls_file(corpus_path)
    if not files and not urls:
        raise EmptyCorpusError(
            f"no files and no urls.txt under corpus path: {corpus_path}"
        )
    mapping: dict[str, ComposedDirectiveSource] = {}
    seq = 0
    for file_path in files:
        seq += 1
        relative = file_path.relative_to(corpus_path).as_posix()
        ref_id = f"src-{seq:03d}"
        role = "primary" if seq == 1 else "supporting"
        mapping[ref_id] = ComposedDirectiveSource(
            ref_id=ref_id,
            provider="local_file",
            locator=relative,
            role=role,
            description=f"Auto-derived from corpus dir: {relative}",
            expected_min_words=DEFAULT_EXPECTED_MIN_WORDS,
        )
    for url in urls:
        seq += 1
        ref_id = f"src-{seq:03d}"
        role = "primary" if seq == 1 else "supporting"
        mapping[ref_id] = ComposedDirectiveSource(
            ref_id=ref_id,
            provider="url",
            locator=url,
            role=role,
            description=f"URL from urls.txt: {url}",
            expected_min_words=DEFAULT_EXPECTED_MIN_WORDS,
        )
    return mapping


def _apply_operator_overrides(
    base: dict[str, ComposedDirectiveSource],
    operator_directives: dict[str, Any] | None,
) -> dict[str, ComposedDirectiveSource]:
    """Apply per-source operator overrides (e.g. expected_min_words pin).

    ``operator_directives`` shape:
      ``{"sources": {"src-001": {"expected_min_words": 500, "role": "primary"}}}``.
    Unknown ref_ids in operator overrides raise DirectiveCompositionError per W-R2.
    """
    if not operator_directives:
        return dict(base)
    overrides_by_ref = (operator_directives or {}).get("sources", {})
    if not overrides_by_ref:
        return dict(base)
    result: dict[str, ComposedDirectiveSource] = {}
    for ref_id, source in base.items():
        override = overrides_by_ref.get(ref_id, {})
        if not override:
            result[ref_id] = source
            continue
        merged_kwargs = asdict(source)
        for key, value in override.items():
            if key not in merged_kwargs:
                raise DirectiveCompositionError(
                    f"operator override for {ref_id!r} contains unknown field {key!r}"
                )
            merged_kwargs[key] = value
        result[ref_id] = ComposedDirectiveSource(**merged_kwargs)
    unknown = set(overrides_by_ref) - set(base)
    if unknown:
        raise DirectiveCompositionError(
            f"operator overrides reference unknown ref_ids: {sorted(unknown)}"
        )
    return result


def compose_directive(
    *,
    corpus_path: Path,
    run_id: str,
    source_authority_map: dict[str, ComposedDirectiveSource] | None = None,
    operator_directives: dict[str, Any] | None = None,
) -> ComposedDirective:
    """Pure-function directive composer (W-R1; FR1, FR-A1).

    Args:
        corpus_path: corpus directory under ``course-content/courses/<lesson_slug>/``.
        run_id: trial run identifier (typically ``str(trial_id)``).
        source_authority_map: optional pre-built sources mapping. If None, the
            default walker emits one entry per on-disk file plus urls.txt entries.
        operator_directives: optional per-source overrides (e.g. role pin).

    Returns:
        ComposedDirective with deterministic ``sources`` ordering.

    Raises:
        EmptyCorpusError: corpus dir is empty (no files, no urls.txt).
        DirectiveCompositionError: operator override conflict or unknown ref_id.
    """
    base = (
        dict(source_authority_map)
        if source_authority_map is not None
        else _default_source_authority_map(corpus_path)
    )
    if not base:
        raise EmptyCorpusError(
            f"source_authority_map is empty for corpus path: {corpus_path}"
        )
    final = _apply_operator_overrides(base, operator_directives)
    sources = tuple(final[ref_id] for ref_id in sorted(final.keys()))
    return ComposedDirective(run_id=run_id, sources=sources)


def _emit_directive_yaml(payload: dict[str, Any]) -> bytes:
    """Stable PyYAML emission for byte-deterministic digests.

    PyYAML is the shipped YAML lib (pyproject.toml). Settings:
    - default_flow_style=False (block style; readable for operator [e]dit)
    - sort_keys=False (preserve insertion order: run_id then sources)
    - allow_unicode=True
    - explicit_end=False
    - line_break='\\n' (POSIX EOL; cross-platform digest stability per W-R6)
    """
    text = yaml.safe_dump(
        payload,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        line_break="\n",
    )
    return text.encode("utf-8")


def materialize_directive(
    composed: ComposedDirective,
    run_dir: Path,
) -> tuple[Path, str]:
    """Write composed directive to ``<run_dir>/directive.yaml``.

    Args:
        composed: ComposedDirective from ``compose_directive``.
        run_dir: per-trial run directory (typically ``runs_root / str(trial_id)``).

    Returns:
        Tuple of (``directive_path``, ``sha256_hex_digest``).
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    directive_path = run_dir / "directive.yaml"
    payload = composed.to_dict()
    raw = _emit_directive_yaml(payload)
    directive_path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    return directive_path, digest


__all__ = [
    "ComposedDirective",
    "ComposedDirectiveSource",
    "DEFAULT_EXPECTED_MIN_WORDS",
    "DirectiveCompositionError",
    "EmptyCorpusError",
    "compose_directive",
    "materialize_directive",
]
