"""State pins for generated specialist workbook_producer."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class WorkbookProducerEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "workbook_producer"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> WorkbookProducerEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for "
                "workbook_producer envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for workbook_producer envelope")
        return self


class WorkbookProducerReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "workbook_producer"
    workbook: dict[str, Any] = Field(
        default_factory=dict,
        description="Produced workbook refs (ProducedAsset + DOCX/MD paths + audits).",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> WorkbookProducerReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for "
                "workbook_producer return"
            )
        return self


__all__ = ["WorkbookProducerEnvelope", "WorkbookProducerReturn"]
