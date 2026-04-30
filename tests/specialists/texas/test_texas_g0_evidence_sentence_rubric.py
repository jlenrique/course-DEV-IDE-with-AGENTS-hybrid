from __future__ import annotations

import json
from pathlib import Path

import yaml

from app.specialists.texas._act import G0_RUBRIC_DIMENSIONS, act
from tests.specialists.texas.test_texas_act_node_dispatch import _build_state


def _write_bundle(bundle: Path, words: str = "claim text carries evidence") -> None:
    bundle.mkdir()
    (bundle / "extracted.md").write_text(f"# Source\n\n{words}\n", encoding="utf-8")
    (bundle / "metadata.json").write_text(
        json.dumps({"provenance": [{"ref_id": "src-001", "ref": "source.md"}]}),
        encoding="utf-8",
    )
    (bundle / "extraction-report.yaml").write_text(
        "schema_version: '1.0'\noverall_status: complete\nrun_id: g0\n",
        encoding="utf-8",
    )
    (bundle / "manifest.json").write_text('{"artifacts":[]}', encoding="utf-8")
    (bundle / "ingestion-evidence.md").write_text("evidence\n", encoding="utf-8")
    (bundle / "result.yaml").write_text("status: complete\nrun_id: g0\n", encoding="utf-8")


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
    _write_bundle(bundle)
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
