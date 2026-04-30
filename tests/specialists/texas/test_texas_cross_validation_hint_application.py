from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.specialists.texas._act import act
from tests.specialists.texas.test_texas_act_node_dispatch import _build_state
from tests.specialists.texas.test_texas_g0_evidence_sentence_rubric import _write_bundle


@pytest.mark.parametrize("hints", [[], ["check source date", "compare SME appendix"]])
def test_cross_validation_hints_are_logged(tmp_path: Path, hints: list[str]) -> None:
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "hints",
                "cross_validation_hints": hints,
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

    act(
        state,
        dispatch_func=lambda **_: {
            "bundle_dir": str(bundle),
            "exit_code": 0,
            "command": ["fake-live"],
        },
    )

    report = yaml.safe_load((bundle / "extraction-report.yaml").read_text())
    cross_validation = report["cross_validation"]
    assert cross_validation["applied"] is bool(hints)
    if hints:
        assert [item["hint"] for item in cross_validation["outcomes"]] == hints
    else:
        assert cross_validation["reason"] == "no hints supplied by directive"
