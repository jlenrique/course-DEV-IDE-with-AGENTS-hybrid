from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.specialists.texas._act import RetrievalScopeError, act
from tests.specialists.texas.test_texas_act_node_dispatch import _build_state
from tests.specialists.texas.test_texas_g0_evidence_sentence_rubric import _write_bundle


@pytest.mark.parametrize(
    ("observed_words", "floor", "should_raise"),
    [(100, 500, True), (499, 500, True), (500, 500, False), (600, 500, False)],
)
def test_word_count_floor_raises_domain_error(
    tmp_path: Path,
    observed_words: int,
    floor: int,
    should_raise: bool,
) -> None:
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "word-floor",
                "sources": [
                    {
                        "ref_id": "src-001",
                        "role": "primary",
                        "expected_min_words": floor,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    bundle = tmp_path / "bundle"
    _write_bundle(bundle, words=" ".join(["word"] * observed_words))
    (bundle / "extracted.md").write_text(
        " ".join(["word"] * observed_words),
        encoding="utf-8",
    )
    state = _build_state(
        cache_prefix=json.dumps(
            {"directive_path": str(directive), "bundle_dir": str(bundle)}
        )
    )
    def call() -> None:
        act(
            state,
            dispatch_func=lambda **_: {
                "bundle_dir": str(bundle),
                "exit_code": 0,
                "command": ["fake-live"],
            },
        )

    if should_raise:
        with pytest.raises(RetrievalScopeError):
            call()
    else:
        call()
