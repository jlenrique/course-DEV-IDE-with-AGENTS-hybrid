from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class IreneDispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    irene_lesson_design: dict[str, Any] | None = None
    irene_pass_2_envelope: dict[str, Any] | None = None
