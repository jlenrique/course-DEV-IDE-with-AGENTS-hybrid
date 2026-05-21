from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class RoutingChatModel(BaseChatModel):
    """Fixture-replay chat model that routes responses by filename needle."""

    responses: dict[str, dict[str, Any] | str]
    default_response: dict[str, Any] | str | None = None
    invoke_count: int = 0

    @property
    def _llm_type(self) -> str:
        return "section-02a-routing-fixture"

    def _generate(
        self,
        messages: list,
        stop: list[str] | None = None,
        run_manager: object | None = None,
        **kwargs: object,
    ) -> ChatResult:
        del stop, run_manager, kwargs
        object.__setattr__(self, "invoke_count", self.invoke_count + 1)
        prompt = str(messages[-1].content)
        filename = ""
        for line in prompt.splitlines():
            if line.startswith("filename: "):
                filename = line.removeprefix("filename: ").strip()
                break
        for needle, payload in self.responses.items():
            if needle == filename or needle in filename:
                return self._result(payload)
        if self.default_response is None:
            raise AssertionError(f"no fixture response routed for prompt: {prompt}")
        return self._result(self.default_response)

    def _result(self, payload: dict[str, Any] | str) -> ChatResult:
        content = payload if isinstance(payload, str) else json.dumps(payload)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])


def payload(
    *,
    role: str = "supporting",
    expected_min_words: int | None = None,
    description: str = "Fixture-classified source.",
) -> dict[str, Any]:
    return {
        "role": role,
        "expected_min_words": expected_min_words,
        "description": description,
        "rationale": "Fixture replay classification for deterministic tests.",
    }
