from __future__ import annotations

from pathlib import Path

import yaml

from app.specialists.texas.retrieval_dispatch import dispatch_retrieval

REQUIRED = {
    "extracted.md",
    "metadata.json",
    "extraction-report.yaml",
    "manifest.json",
    "ingestion-evidence.md",
    "result.yaml",
}


def test_trial_475_replay_honors_six_artifact_contract(tmp_path: Path) -> None:
    corpus = Path("tests/fixtures/trials/trial_475_mini_corpus")
    assert corpus.is_dir(), f"missing trial-475 mini-corpus cassette: {corpus}"
    payload = {
        "run_id": "trial-475-texas",
        "sources": [
            {
                "ref_id": f"src-{index:03d}",
                "provider": "local_file",
                "locator": (corpus / name).resolve().as_posix(),
                "role": "primary" if index == 1 else "supporting",
                "description": f"trial-475 fixture source: {name}",
                "expected_min_words": 1,
            }
            for index, name in enumerate(
                ["appendix.md", "chapter-1.md", "intro.md"], start=1
            )
        ],
    }
    directive_path = tmp_path / "directive.yaml"
    directive_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    bundle_dir = tmp_path / "bundle"

    receipt = dispatch_retrieval(directive_path=directive_path, bundle_dir=bundle_dir)

    assert receipt["status"] == "dispatched"
    assert REQUIRED.issubset({path.name for path in bundle_dir.iterdir()})
    assert (bundle_dir / "extracted.md").read_text(encoding="utf-8").split()
