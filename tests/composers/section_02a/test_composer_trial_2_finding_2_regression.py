from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.composers.section_02a import DirectiveRole, ExcludedReason, compose
from tests.composers.section_02a._helpers import RoutingChatModel, payload

REPO_ROOT = Path(__file__).resolve().parents[3]
TRIAL_2_DIRECTIVE = (
    REPO_ROOT
    / "state"
    / "config"
    / "runs"
    / "db276994-edf4-47a2-83bc-771cc214c3c1"
    / "directive.yaml"
)
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".pdf", ".pptx"}


def _copy_source_names_to_corpus(broken: dict, corpus_dir: Path) -> None:
    for source in broken["sources"]:
        locator = source["locator"]
        path = corpus_dir / locator
        path.parent.mkdir(parents=True, exist_ok=True)
        if Path(locator).suffix.lower() in BINARY_SUFFIXES:
            path.write_bytes(b"binary fixture")
        else:
            path.write_text("text fixture", encoding="utf-8")


def test_trial_2_finding_2_regression_does_not_reproduce_broken_directive(
    tmp_path: Path,
) -> None:
    if not TRIAL_2_DIRECTIVE.exists():
        pytest.skip(f"Trial-2 forensic fixture missing: {TRIAL_2_DIRECTIVE.as_posix()}")

    trial_2_yaml = TRIAL_2_DIRECTIVE.read_text(encoding="utf-8")
    broken = yaml.safe_load(trial_2_yaml)
    _copy_source_names_to_corpus(broken, tmp_path)

    llm = RoutingChatModel(
        responses={
            "APC C1-M1 Tejal 2026-03-29.docx": payload(
                role="primary",
                expected_min_words=500,
                description="Primary Tejal lesson content.",
            ),
            "C1M1Part01.md": payload(
                role="supporting",
                expected_min_words=200,
                description="Supporting markdown source.",
            ),
        },
        default_response=payload(description="Supporting binary or visual reference."),
    )

    directive = compose(tmp_path, llm=llm)
    composed_yaml = yaml.safe_dump(
        directive.model_dump(mode="json"),
        sort_keys=False,
        allow_unicode=True,
    )
    by_locator = {source.locator: source for source in directive.sources}

    assert composed_yaml != trial_2_yaml
    assert by_locator[".gitkeep"].role is DirectiveRole.IGNORED
    assert by_locator[".gitkeep"].excluded_reason is ExcludedReason.GIT_MARKER
    assert by_locator["APC C1-M1 Tejal 2026-03-29.docx"].role is DirectiveRole.PRIMARY
    for source in directive.sources:
        if Path(source.locator).suffix.lower() in BINARY_SUFFIXES:
            assert source.expected_min_words is None, source.locator

