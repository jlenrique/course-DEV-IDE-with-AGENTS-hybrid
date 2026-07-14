from __future__ import annotations

import hashlib
import json
from pathlib import Path


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


__all__ = ["write_primary_slide_bundle", "write_source_bundle_manifest"]
