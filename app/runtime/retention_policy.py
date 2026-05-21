"""`RetentionPolicy` — operator-facing checkpoint retention config (Story 1.5).

**Operational-policy config, NOT graph state** — per Winston's amendment
2026-04-22, this model lives under `app.runtime.*` rather than `app.models.state.*`
which is reserved for LangGraph state schema (`RunState`, `OperatorVerdict`,
etc.). Retention policy is operator-side configuration that drives
`app.runtime.cleanup_threads`, not a field that LangGraph persists in a
checkpoint.

Pydantic v2 idioms apply (per `docs/dev-guide/pydantic-v2-schema-checklist.md`):
`extra="forbid"`, `validate_assignment=True`, `cron_hint` validated as a
documentation-only 5-field cron expression (not full parser; see Dev Note).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

DEFAULT_POLICY_PATH: Path = (
    Path(__file__).resolve().parents[2] / "state" / "config" / "retention-policy.yaml"
)

# Five space-separated cron fields; each field accepts digits, `*`, `/`, `-`, `,` tokens.
# Intentionally permissive — this is a documentation field (operator runs cron externally
# per D3), NOT a parser. A full cron grammar would lock us to one library's dialect.
_CRON_HINT_PATTERN = re.compile(r"^\S+\s+\S+\s+\S+\s+\S+\s+\S+$")


class RetentionPolicy(BaseModel):
    """Checkpoint retention + cleanup policy (FR4 / FR5)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    max_thread_age_days: int = Field(
        ...,
        ge=1,
        description=(
            "Threads older than this age (by updated_at timestamp) are eligible for "
            "cleanup. Default policy is 30d; minimum 1d."
        ),
    )
    cleanup_cron_hint: str = Field(
        ...,
        description=(
            "Operator-facing documentation-only cron expression. `app.runtime` does "
            "not schedule itself (D3 discipline); operators implement the cadence "
            "via OS-level cron / Task Scheduler."
        ),
    )
    retain_completed: bool = Field(
        ...,
        description="When False, completed threads older than max_thread_age_days are deleted.",
    )
    retain_failed: bool = Field(
        ...,
        description=(
            "When True, failed threads are kept indefinitely for forensic value. "
            "Default policy retains failed threads."
        ),
    )

    @field_validator("cleanup_cron_hint")
    @classmethod
    def _enforce_cron_shape(cls, value: str) -> str:
        if not _CRON_HINT_PATTERN.match(value):
            raise ValueError(
                f"cleanup_cron_hint must be a 5-field cron expression "
                f"(minute hour day-of-month month day-of-week); got {value!r}"
            )
        return value


def load_policy(path: Path | str | None = None) -> RetentionPolicy:
    """Load a `RetentionPolicy` from YAML. Defaults to the shipped policy file."""
    target = Path(path) if path is not None else DEFAULT_POLICY_PATH
    if not target.is_file():
        raise FileNotFoundError(f"retention policy file not found: {target}")
    raw: Any = yaml.safe_load(target.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(
            f"retention policy root must be a mapping (got {type(raw).__name__}) at {target}"
        )
    return RetentionPolicy.model_validate(raw)


__all__ = ["DEFAULT_POLICY_PATH", "RetentionPolicy", "load_policy"]
