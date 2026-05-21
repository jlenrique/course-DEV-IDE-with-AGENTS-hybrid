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


@pytest.mark.serial
def test_texas_dispatch_retrieval_writes_six_artifacts_from_composed_directive(
    tmp_path: Path,
) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    source = corpus / "intro.md"
    source.write_text(" ".join(["anchored evidence sentence"] * 40), encoding="utf-8")
    composed = compose_directive(corpus_path=corpus, run_id="7b1-live")
    payload = composed.to_dict()
    payload["sources"][0]["locator"] = source.resolve().as_posix()
    payload["sources"][0]["expected_min_words"] = 10
    directive_path = tmp_path / "directive.yaml"
    directive_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    receipt = dispatch_retrieval(
        directive_path=directive_path,
        bundle_dir=tmp_path / "bundle",
    )

    bundle_dir = Path(receipt["bundle_dir"])
    assert receipt["status"] == "dispatched"
    assert receipt["command"], "live directive path should not use fixture fallback"
    assert REQUIRED.issubset({path.name for path in bundle_dir.iterdir()})
