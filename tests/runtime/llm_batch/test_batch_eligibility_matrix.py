"""A3 hermetic tests: batch-eligibility matrix shape + vision-first v1 routing."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.runtime.llm_batch_eligibility import load_batch_eligibility


def test_load_eligibility_vision_v1_routable() -> None:
    matrix = load_batch_eligibility()
    assert set(matrix.criteria) == {"a", "b", "c", "d", "e"}
    assert matrix.is_batch_eligible("vision") is True
    assert matrix.is_v1_batch_routable("vision") is True
    assert matrix.v1_routable_sites() == ("vision",)


def test_non_llm_sites_not_eligible() -> None:
    matrix = load_batch_eligibility()
    for site in (
        "workbook_producer",
        "workbook_enrichment",
        "mine6_prose_uplift",
        "gary",
        "enrique",
    ):
        assert matrix.is_batch_eligible(site) is False
        assert matrix.is_v1_batch_routable(site) is False


def test_secondary_eligible_but_not_v1_routed() -> None:
    matrix = load_batch_eligibility()
    assert matrix.is_batch_eligible("reading_path_llm") is True
    assert matrix.is_v1_batch_routable("reading_path_llm") is False


def test_monolithic_sites_not_eligible() -> None:
    matrix = load_batch_eligibility()
    for site in ("irene_pass1", "irene_pass2", "g0_extraction", "cd", "marcus_pre_gate"):
        assert matrix.is_batch_eligible(site) is False


def test_v1_routed_requires_eligible(tmp_path: Path) -> None:
    target = tmp_path / "eligibility.yaml"
    target.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "criteria": {
                    "a": "a",
                    "b": "b",
                    "c": "c",
                    "d": "d",
                    "e": "e",
                },
                "sites": {
                    "vision": {
                        "batch_eligible": False,
                        "v1_routed": True,
                        "criteria_met": [],
                        "rationale": "bad",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_batch_eligibility(target)


def test_matrix_requires_vision_v1(tmp_path: Path) -> None:
    target = tmp_path / "eligibility.yaml"
    target.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "criteria": {
                    "a": "a",
                    "b": "b",
                    "c": "c",
                    "d": "d",
                    "e": "e",
                },
                "sites": {
                    "workbook_producer": {
                        "batch_eligible": False,
                        "v1_routed": False,
                        "criteria_met": [],
                        "rationale": "no llm",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="vision"):
        load_batch_eligibility(target)
