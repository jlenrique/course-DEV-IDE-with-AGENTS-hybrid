"""Load batch-eligibility matrix (Batch LLM A3).

Config SSOT: ``runtime/config/llm_batch_eligibility.yaml``.
v1 routing uses ``is_v1_batch_routable`` — only ``vision`` today.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
ELIGIBILITY_PATH = REPO_ROOT / "runtime" / "config" / "llm_batch_eligibility.yaml"

CriterionId = Literal["a", "b", "c", "d", "e"]


class EligibilitySite(BaseModel):
    """One classified LLM (or non-LLM) site."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    batch_eligible: bool
    v1_routed: bool = False
    criteria_met: tuple[CriterionId, ...] = ()
    rationale: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def _v1_implies_eligible(self) -> EligibilitySite:
        if self.v1_routed and not self.batch_eligible:
            raise ValueError("v1_routed=true requires batch_eligible=true")
        return self


class BatchEligibilityMatrix(BaseModel):
    """Full matrix + criteria rubric."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    version: int = Field(..., ge=1)
    criteria: dict[CriterionId, str]
    sites: dict[str, EligibilitySite]

    @model_validator(mode="after")
    def _require_vision_v1(self) -> BatchEligibilityMatrix:
        required = ("a", "b", "c", "d", "e")
        missing = [c for c in required if c not in self.criteria]
        if missing:
            raise ValueError(f"eligibility criteria missing keys: {missing}")
        if "vision" not in self.sites:
            raise ValueError("eligibility sites.vision is required")
        vision = self.sites["vision"]
        if not vision.batch_eligible or not vision.v1_routed:
            raise ValueError("sites.vision must be batch_eligible and v1_routed for v1")
        return self

    def site(self, name: str) -> EligibilitySite:
        try:
            return self.sites[name]
        except KeyError as exc:
            raise KeyError(f"unknown eligibility site {name!r}") from exc

    def is_batch_eligible(self, name: str) -> bool:
        return self.site(name).batch_eligible

    def is_v1_batch_routable(self, name: str) -> bool:
        row = self.site(name)
        return bool(row.batch_eligible and row.v1_routed)

    def v1_routable_sites(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                name
                for name, row in self.sites.items()
                if row.batch_eligible and row.v1_routed
            )
        )


def load_batch_eligibility(path: Path | None = None) -> BatchEligibilityMatrix:
    """Load and validate ``llm_batch_eligibility.yaml``."""

    target = path if path is not None else ELIGIBILITY_PATH
    payload = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("eligibility config must parse to a mapping")
    return BatchEligibilityMatrix.model_validate(payload)


__all__ = [
    "BatchEligibilityMatrix",
    "CriterionId",
    "ELIGIBILITY_PATH",
    "EligibilitySite",
    "load_batch_eligibility",
]
