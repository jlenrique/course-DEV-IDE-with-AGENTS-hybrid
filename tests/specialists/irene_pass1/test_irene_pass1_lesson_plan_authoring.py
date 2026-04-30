from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act


@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        assert messages[0]["role"] == "system"
        assert "plan_units" in messages[1]["content"]
        return SimpleNamespace(
            content=self.response_text,
            usage_metadata={
                "input_tokens": 1400,
                "input_token_details": {"cached_tokens": 1190},
            },
        )


@dataclass
class _FakeHandle:
    response_text: str

    @property
    def chat(self) -> _FakeChat:
        return _FakeChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=0,
        ),
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5.4",
                resolved="gpt-5.4",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="a" * 64,
            )
        ],
    )


def test_pass1_act_writes_irene_pass1_markdown(tmp_path) -> None:
    response = json.dumps(
        {
            "lesson_summary": "Teach beta blocker essentials.",
            "plan_units": [
                {
                    "unit_id": "unit-1",
                    "title": "Mechanism",
                    "learning_objective": "Explain beta receptor blockade.",
                    "scope_decision": "in-scope",
                    "rationale": "Core objective.",
                }
            ],
        }
    )
    update = pass1_act.act(
        _state({"mode": "pass-1", "run_id": "run-123", "runs_root": str(tmp_path)}),
        handle=_FakeHandle(response),
        model_id="gpt-5.4",
    )

    output = json.loads(update["cache_state"]["cache_prefix"])
    artifact_path = tmp_path / "run-123" / "irene-pass1.md"
    assert artifact_path.is_file()
    assert output["artifact_path"] == str(artifact_path)
    assert output["model_id"] == "gpt-5.4"
    assert output["lesson_plan"]["plan_units"][0]["unit_id"] == "unit-1"
    assert "## unit-1: Mechanism" in artifact_path.read_text(encoding="utf-8")


def test_prompt_assembly_is_byte_stable() -> None:
    payload = {"mode": "pass-1", "topic": "cardiac pharmacology"}
    assert pass1_act.assemble_pass1_prompt(payload) == pass1_act.assemble_pass1_prompt(
        dict(reversed(payload.items()))
    )
