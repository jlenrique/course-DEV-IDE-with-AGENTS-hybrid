from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path

_SLIDE_NAME = re.compile(r"^slide-(?P<ordinal>[1-9][0-9]*)-.+\.md$")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def write_source_bundle_manifest(bundle: Path) -> None:
    defaults = {
        "extraction-report.yaml": "run_id: test\noverall_status: complete\n",
        "ingestion-evidence.md": "# Test ingestion evidence\n",
        "result.yaml": "run_id: test\nstatus: complete\n",
    }
    for name, content in defaults.items():
        path = bundle / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    artifacts = []
    for name in (
        "extracted.md",
        "metadata.json",
        "extraction-report.yaml",
        "ingestion-evidence.md",
        "result.yaml",
    ):
        raw = (bundle / name).read_bytes()
        artifacts.append(
            {
                "path": name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
            }
        )
    (bundle / "manifest.json").write_text(
        json.dumps({"schema_version": "1.0", "artifacts": artifacts}),
        encoding="utf-8",
    )


def write_primary_slide_bundle(
    bundle: Path, text: str, *, raw_source_text: str | None = None
) -> Path:
    """Write the smallest Texas-shaped bundle valid for Pass-1 authority tests."""
    source_text = text if raw_source_text is None else raw_source_text
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-slide-1",
                        "kind": "local_file",
                        "ref": "slides/slide-1-primary.md",
                        "role": "primary",
                        "section_title": "slide-1",
                    },
                ],
                "sme_refs": [
                    {
                        "source_id": "src-slide-1",
                        "path": "slides/slide-1-primary.md",
                        "content_digest": hashlib.sha256(
                            source_text.encode("utf-8")
                        ).hexdigest(),
                    }
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide-1",
                        "path": "slides/slide-1-primary.md",
                        "source_content_digest": hashlib.sha256(
                            source_text.replace("\r\n", "\n")
                            .replace("\r", "\n")
                            .encode("utf-8")
                        ).hexdigest(),
                        "extracted_content_digest": hashlib.sha256(
                            text.replace("\r\n", "\n")
                            .replace("\r", "\n")
                            .strip()
                            .encode("utf-8")
                        ).hexdigest(),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    extracted = bundle / "extracted.md"
    extracted.write_text(f"## slide-1\n{text}", encoding="utf-8")
    write_source_bundle_manifest(bundle)
    return extracted


def write_authenticated_slide_bundle(
    bundle: Path,
    sources: Iterable[tuple[str, str, str]],
) -> Path:
    """Write a multi-slide Texas-shaped bundle for slide-authority resolution.

    ``sources`` is an ordered iterable of ``(ref, raw_text, extracted_text)``:
    ``ref`` is the canonical ``slides/slide-N-*.md`` path, ``raw_text`` is the
    raw slide bytes (its digest binds the source identity), and
    ``extracted_text`` is the Texas-authenticated body that carries any
    ``[evidence: src-NNN]`` provenance markers. ``extracted_text == raw_text``
    reproduces the marker-free case; differing texts reproduce production drift.
    """
    bundle.mkdir(parents=True, exist_ok=True)
    provenance: list[dict[str, object]] = []
    source_authority: list[dict[str, object]] = []
    extracted_parts: list[str] = []
    seen_titles: set[str] = set()
    for ref, raw_text, extracted_text in sources:
        stem = Path(ref).stem
        title = stem
        if title in seen_titles:
            raise AssertionError(f"duplicate bundle section title: {title}")
        seen_titles.add(title)
        source_id = f"src-{stem}"
        raw_norm = _normalize(raw_text)
        extracted_norm = _normalize(extracted_text)
        provenance.append(
            {
                "ref_id": source_id,
                "kind": "local_file",
                "ref": ref,
                "role": "primary",
                "section_title": title,
            }
        )
        source_authority.append(
            {
                "source_id": source_id,
                "path": ref,
                "source_content_digest": _sha256(raw_norm),
                "extracted_content_digest": _sha256(extracted_norm.strip()),
            }
        )
        # A trailing newline before the next ``## `` heading keeps each primary
        # boundary intact; the digest strips it, so it never perturbs identity.
        extracted_parts.append(f"## {title}\n{extracted_norm}\n")
    (bundle / "metadata.json").write_text(
        json.dumps(
            {"provenance": provenance, "source_authority": source_authority}
        ),
        encoding="utf-8",
    )
    extracted = bundle / "extracted.md"
    extracted.write_text("".join(extracted_parts), encoding="utf-8")
    write_source_bundle_manifest(bundle)
    return extracted


def write_authenticated_slide_bundle_from_course(
    run_dir: Path,
    course_source_root: Path,
    *,
    marker_lines: dict[str, str] | None = None,
) -> Path:
    """Write ``<run_dir>/bundle`` from the raw slides under a course source root.

    Bodies default to the raw slide text (marker-free). ``marker_lines`` maps a
    slide filename to a full line already present in that slide; the mapped line
    receives a ``[evidence: src-XXX]`` suffix in the authenticated body only,
    reproducing the Texas provenance-marker drift the resolver must survive.
    """
    slides_dir = Path(course_source_root) / "slides"
    marker_lines = marker_lines or {}
    sources: list[tuple[str, str, str]] = []
    for path in sorted(slides_dir.iterdir(), key=lambda item: item.name):
        if path.is_symlink() or not path.is_file():
            continue
        if _SLIDE_NAME.fullmatch(path.name) is None:
            continue
        raw_text = path.read_text(encoding="utf-8")
        extracted_text = raw_text
        if path.name in marker_lines:
            line = marker_lines[path.name]
            if line not in raw_text:
                raise AssertionError(
                    f"marker anchor line not found in {path.name}: {line!r}"
                )
            extracted_text = raw_text.replace(
                line, f"{line} [evidence: src-006]", 1
            )
        sources.append((f"slides/{path.name}", raw_text, extracted_text))
    if not sources:
        raise AssertionError("no source slides found for authenticated bundle")
    return write_authenticated_slide_bundle(Path(run_dir) / "bundle", sources)


__all__ = [
    "write_authenticated_slide_bundle",
    "write_authenticated_slide_bundle_from_course",
    "write_primary_slide_bundle",
    "write_source_bundle_manifest",
]
