from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from app.specialists.texas._act import G0_RUBRIC_DIMENSIONS, act
from tests.specialists.texas.test_texas_act_node_dispatch import _build_state


def _seal_manifest(bundle: Path) -> None:
    names = (
        "extracted.md",
        "metadata.json",
        "extraction-report.yaml",
        "ingestion-evidence.md",
        "result.yaml",
    )
    artifacts = []
    for name in names:
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


def _write_bundle(
    bundle: Path,
    words: str = "claim text carries evidence",
    *,
    run_id: str = "g0",
    directive_path: Path,
) -> None:
    bundle.mkdir()
    (bundle / "extracted.md").write_text(
        f"# Source\n\n## source\n\n{words}\n", encoding="utf-8"
    )
    digest = hashlib.sha256(words.strip().encode("utf-8")).hexdigest()
    directive = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    directive_sha256 = hashlib.sha256(
        yaml.safe_dump(directive, sort_keys=True, allow_unicode=True).encode("utf-8")
    ).hexdigest()
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "directive_sha256": directive_sha256,
                "generated_at": "2026-07-13T00:00:00Z",
                "provenance": [
                    {
                        "ref_id": "src-001",
                        "kind": "local_file",
                        "ref": "source.md",
                        "role": "primary",
                        "section_title": "source",
                    }
                ],
                "source_authority": [
                    {
                        "source_id": "src-001",
                        "path": "source.md",
                        "source_content_digest": digest,
                        "extracted_content_digest": digest,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extraction-report.yaml").write_text(
        f"schema_version: '1.0'\noverall_status: complete\nrun_id: {run_id}\n",
        encoding="utf-8",
    )
    (bundle / "ingestion-evidence.md").write_text("evidence\n", encoding="utf-8")
    (bundle / "result.yaml").write_text(
        f"status: complete\nrun_id: {run_id}\n", encoding="utf-8"
    )
    _seal_manifest(bundle)


def test_g0_evidence_sentence_rubric_anchors_claims(tmp_path: Path) -> None:
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "g0",
                "sources": [
                    {
                        "ref_id": "src-001",
                        "role": "primary",
                        "expected_min_words": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    bundle = tmp_path / "bundle"
    _write_bundle(bundle, directive_path=directive)
    state = _build_state(
        cache_prefix=json.dumps(
            {"directive_path": str(directive), "bundle_dir": str(bundle)}
        )
    )

    update = act(
        state,
        dispatch_func=lambda **_: {
            "bundle_dir": str(bundle),
            "exit_code": 0,
            "command": ["fake-live"],
        },
    )

    extracted = (bundle / "extracted.md").read_text(encoding="utf-8")
    report = yaml.safe_load((bundle / "extraction-report.yaml").read_text())
    assert "[evidence: src-001]" in extracted
    assert set(report["g0_evidence_sentence_rubric"]["dimensions"]) == set(
        G0_RUBRIC_DIMENSIONS
    )
    assert json.loads(update["cache_state"]["cache_prefix"])["g0_word_count"] >= 1
