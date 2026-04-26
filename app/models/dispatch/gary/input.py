from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class GaryDispatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    directive_path: str | None = None
    export_dir: str | None = None
