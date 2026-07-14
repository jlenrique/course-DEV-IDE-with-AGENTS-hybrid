from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from app.marcus.lesson_plan.pass1_source_span_catalog import (
    build_pass1_source_span_catalog,
)
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act
from app.specialists.source_bundle import read_extracted_source_with_sections
from tests._helpers.pass1_bundle import write_primary_slide_bundle

EXACT = "We can no longer rely on static training."
NEAR_PARAPHRASE = "cannot rely on static training"


@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        assert '"source_ref_ids"' in messages[1]["content"]
        return SimpleNamespace(
            content=self.response_text,
            usage_metadata={"input_tokens": 10, "output_tokens": 5},
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
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
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


def _bundle_and_catalog(tmp_path):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, f"# Corpus\n\n{EXACT}")
    payload = {"bundle_reference": str(bundle)}
    extracted, sections = read_extracted_source_with_sections(payload)
    catalog = build_pass1_source_span_catalog(sections)
    selected = next(entry for entry in catalog.entries if entry.text == EXACT)
    return bundle, extracted, catalog, selected


def test_catalog_accepts_distinct_authenticated_raw_and_extracted_digests(
    tmp_path,
) -> None:
    raw_source = f"# Corpus\n\n{EXACT}"
    extracted_source = f"# Corpus\n\n{EXACT} [evidence: src-001]"
    bundle = tmp_path / "dual-digest-bundle"
    bundle.mkdir()
    write_primary_slide_bundle(
        bundle,
        extracted_source,
        raw_source_text=raw_source,
    )

    _extracted, sections = read_extracted_source_with_sections(
        {"bundle_reference": str(bundle)}
    )
    catalog = build_pass1_source_span_catalog(sections)

    exact = next(entry for entry in catalog.entries if entry.text == EXACT)
    assert exact.source_digest != exact.extracted_content_digest
    assert exact.source_id.endswith(exact.source_digest)

    update = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-dual-digest-provider-boundary",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=_FakeHandle(_candidate(selected_id=exact.span_id)),
        model_id="gpt-5.4",
    )
    plan = json.loads(update["cache_state"]["cache_prefix"])["lesson_plan"]
    assert plan["plan_units"][0]["source_refs"] == [EXACT]


def _candidate(*, selected_id: str, include_authored_text: bool = False) -> str:
    unit = {
        "unit_id": "u03i1",
        "title": "Static training",
        "learning_objective": "Explain why static training is insufficient.",
        "scope_decision": "in-scope",
        "source_ref_ids": [selected_id],
        "rationale": "The source establishes the adaptation problem.",
        "cluster_id": "c-u03i1",
        "cluster_role": "head",
        "cluster_position": "establish",
        "narrative_arc": "From static knowledge to adaptive practice through evidence",
        "cluster_interstitial_count": 0,
        "fidelity": "creative",
    }
    if include_authored_text:
        unit["source_refs"] = [NEAR_PARAPHRASE]
    return json.dumps({"lesson_summary": "Summary", "plan_units": [unit]})


def test_prompt_exposes_exact_catalog_and_requests_ids_only(tmp_path) -> None:
    _bundle, extracted, catalog, selected = _bundle_and_catalog(tmp_path)

    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"},
        extracted_source=extracted,
        source_span_catalog=catalog,
    )

    assert catalog.catalog_digest in user
    assert selected.span_id in user
    assert EXACT in user
    actionable = user[user.index("Return JSON:") :]
    assert '"source_ref_ids"' in actionable
    assert '"source_refs"' not in actionable
    assert "fuzzy" in actionable.lower()


def test_act_projects_selected_id_to_exact_literal_authority(tmp_path) -> None:
    bundle, _extracted, catalog, selected = _bundle_and_catalog(tmp_path)
    update = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-span-projection",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=_FakeHandle(_candidate(selected_id=selected.span_id)),
        model_id="gpt-5.4",
    )

    output = json.loads(update["cache_state"]["cache_prefix"])
    plan = output["lesson_plan"]
    unit = plan["plan_units"][0]
    assert unit["source_ref_ids"] == [selected.span_id]
    assert unit["source_refs"] == [EXACT]
    assert plan["source_span_catalog_digest"] == catalog.catalog_digest


def test_act_rejects_model_authored_literal_even_when_id_is_valid(tmp_path) -> None:
    bundle, _extracted, _catalog, selected = _bundle_and_catalog(tmp_path)

    with pytest.raises(pass1_act.Pass1AuthorityError, match="model-authored"):
        pass1_act.act(
            _state(
                {
                    "mode": "pass-1",
                    "run_id": "run-authored-text-refused",
                    "runs_root": str(tmp_path),
                    "bundle_reference": str(bundle),
                }
            ),
            handle=_FakeHandle(
                _candidate(selected_id=selected.span_id, include_authored_text=True)
            ),
            model_id="gpt-5.4",
        )
