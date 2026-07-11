"""Load vision-first LLM execution profiles (Batch LLM A1).

Config SSOT: ``runtime/config/llm_execution.yaml`` (adjacent to
``model_cascade.yaml``). Does **not** mutate the economics cascade — realtime
vision remains ``gpt-5.5`` there. Operator binding (2026-07-10, see the YAML
header): batch model MUST match realtime; ``batch_model_fallback_family``
declares GPT-5-family fallback as policy only — this module does not
auto-substitute — and ``gpt-4.1-*`` is never a product default.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
LLM_EXECUTION_PATH = REPO_ROOT / "runtime" / "config" / "llm_execution.yaml"

ExecutionMode = Literal["realtime", "batch"]


class NodeTransportProfile(BaseModel):
    """Provider/model settings for one transport (realtime or batch)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    provider: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    max_completion_tokens: int = Field(..., gt=0)
    reasoning_effort: str | None = None
    text_verbosity: str | None = None
    prompt_cache_key_strategy: str | None = None
    prompt_cache_retention: str | None = None
    batch_model_fallback_family: str | None = None
    harness_baseline_batch_id: str | None = None


class NodeExecutionProfile(BaseModel):
    """Per-node execution profile with optional batch override."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    default_mode: ExecutionMode = "realtime"
    realtime: NodeTransportProfile
    batch: NodeTransportProfile | None = None

    def profile_for(self, mode: ExecutionMode) -> NodeTransportProfile:
        """Return the transport profile for ``mode``.

        Raises ``ValueError`` if ``mode`` is ``batch`` and the node has no
        batch profile override — there is no silent fallback to realtime.
        """

        if mode == "batch":
            if self.batch is None:
                raise ValueError("node has no batch profile override")
            return self.batch
        return self.realtime


class LlmExecutionConfig(BaseModel):
    """Run-level default mode + per-node profiles (vision-first in v1)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    version: int = Field(..., ge=1)
    default_mode: ExecutionMode = "realtime"
    nodes: dict[str, NodeExecutionProfile]

    @model_validator(mode="after")
    def _require_vision(self) -> LlmExecutionConfig:
        if "vision" not in self.nodes:
            raise ValueError("llm_execution.nodes.vision is required for v1")
        vision = self.nodes["vision"]
        if vision.batch is None:
            raise ValueError("llm_execution.nodes.vision.batch profile is required")
        return self

    def node(self, name: str) -> NodeExecutionProfile:
        try:
            return self.nodes[name]
        except KeyError as exc:
            raise KeyError(f"unknown llm_execution node {name!r}") from exc

    def resolve_profile(
        self, node_name: str, *, mode: ExecutionMode | None = None
    ) -> NodeTransportProfile:
        """Resolve transport profile for a node under run or node default mode."""

        node = self.node(node_name)
        effective: ExecutionMode = mode if mode is not None else node.default_mode
        return node.profile_for(effective)


def load_llm_execution(path: Path | None = None) -> LlmExecutionConfig:
    """Load and validate ``llm_execution.yaml``."""

    target = path if path is not None else LLM_EXECUTION_PATH
    payload = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("llm_execution config must parse to a mapping")
    return LlmExecutionConfig.model_validate(payload)


__all__ = [
    "ExecutionMode",
    "LLM_EXECUTION_PATH",
    "LlmExecutionConfig",
    "NodeExecutionProfile",
    "NodeTransportProfile",
    "load_llm_execution",
]
