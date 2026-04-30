from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator.directive_composer import compose_directive
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
    if not corpus.is_dir():
        pytest.skip("trial-475 mini-corpus cassette unavailable")
    composed = compose_directive(corpus_path=corpus, run_id="trial-475-texas")
    payload = composed.to_dict()
    for source in payload["sources"]:
        locator = corpus / source["locator"]
        source["locator"] = locator.resolve().as_posix()
        if source["role"] == "supporting":
            source["role"] = "supplementary"
        source["expected_min_words"] = 1
    directive_path = tmp_path / "directive.yaml"
    directive_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    bundle_dir = tmp_path / "bundle"

    receipt = dispatch_retrieval(directive_path=directive_path, bundle_dir=bundle_dir)

    assert receipt["status"] == "dispatched"
    assert REQUIRED.issubset({path.name for path in bundle_dir.iterdir()})
    assert (bundle_dir / "extracted.md").read_text(encoding="utf-8").split()
