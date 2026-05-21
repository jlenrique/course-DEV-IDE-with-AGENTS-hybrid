"""In-memory cache for Section 02A LLM classification responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ComposerCache(BaseModel):
    """Cache keyed by SHA256(normalized_prompt)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    responses: dict[str, str] = Field(default_factory=dict)

    def get(self, cache_key: str) -> str | None:
        return self.responses.get(cache_key)

    def set(self, cache_key: str, response: str) -> None:
        self.responses[cache_key] = response


__all__ = ["ComposerCache"]

