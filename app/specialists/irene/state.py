"""State pins for Irene Pass 2 narration specialist (Story 2a.2).

Irene's envelope + return subclasses pin `specialist_id == "irene"` via
`ClassVar` + `model_validator(mode="after")`. Cross-field invariants
(verb/payload consistency for SpecialistReturn, UUID4/timezone-awareness
for SpecialistEnvelope) are inherited from the parent classes — Resolution B
per Story 2a.1: no Irene-specific separate validator module is needed.
Document new validators only when Irene introduces a constraint not already
expressed at the parent layer.

`payload_in` shape (envelope) and `payload` shape (return) remain
`dict[str, Any]` from the parent classes. Per AC-B + MF4, the Pass 2 act
node is bounded to prompt-assembly + LLM dispatch + parse — no procedural
narration logic in Python — so the runtime payload contract is documented
in [`skills/bmad-agent-content-creator/references/pass-2-procedure.md`](
../../../skills/bmad-agent-content-creator/references/pass-2-procedure.md
)
+ the LLM response parser in `graph.py::_act`. Tightening payload shape via
an Irene-specific Pydantic schema is deferred to a follow-on once 2a.3 + 2a.4
have surfaced any cross-specialist contract requirements.
"""

from __future__ import annotations

import json
from typing import ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class IreneEnvelope(SpecialistEnvelope):
    """Pass-2 narration envelope with specialist-id pin + 50KB payload cap."""

    _SPECIALIST_ID: ClassVar[str] = "irene"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> IreneEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for irene envelope"
            )
        # 50KB cap mirrors the scaffold reference; Pass 2 envelopes that exceed
        # this typically embed full perception_artifacts inline that should be
        # referenced by path instead (FR15 sanctum cold-read pattern).
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for irene envelope")
        return self


class IreneReturn(SpecialistReturn):
    """Pass-2 narration return with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "irene"

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> IreneReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for irene return"
            )
        return self


__all__ = ["IreneEnvelope", "IreneReturn"]
