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
from tests._helpers.pass1_bundle import write_primary_slide_bundle
from tests._helpers.pass1_catalog_response import select_catalog_ids


@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        assert messages[0]["role"] == "system"
        assert "plan_units" in messages[1]["content"]
        return SimpleNamespace(
            content=select_catalog_ids(self.response_text, messages),
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
    # Content-plane contract (2026-06-12): plan creation requires the
    # extracted corpus in sight — provide a real tmp bundle.
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nBeta blocker source material.")
    response = json.dumps(
        {
            "lesson_summary": "Teach beta blocker essentials.",
            "plan_units": [
                {
                    "unit_id": "unit-1",
                    "title": "Mechanism",
                    "learning_objective": "Explain beta receptor blockade.",
                    "scope_decision": "in-scope",
                    "source_refs": ["Beta blocker source material."],
                    "rationale": "Core objective.",
                }
            ],
        }
    )
    update = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-123",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
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
    assert pass1_act.assemble_pass1_prompt(
        payload, extracted_source="Corpus body."
    ) == pass1_act.assemble_pass1_prompt(
        dict(reversed(payload.items())), extracted_source="Corpus body."
    )


def test_prompt_leads_with_extracted_corpus() -> None:
    """Content-plane pin (cycle-2 confabulation root cause): at plan creation
    the corpus leads the prompt and is declared the only planning basis."""
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"}, extracted_source="UNIQUE-CORPUS-MARKER body."
    )
    assert user.index("UNIQUE-CORPUS-MARKER") < user.index("Sanctum digest")
    assert "ONLY planning basis" in user


def test_prompt_refinement_pass_without_corpus_names_prior_plan_basis() -> None:
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"}, extracted_source=None
    )
    assert "Refinement pass" in user
    assert "ONLY planning basis" not in user
