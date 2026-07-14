"""Leg-C R3 AC#15 (D-0, J-3) — hidden-key strip at the REAL Pass-1 surface.

The D1 adjudication's D-0 finding: ``irene_pass1/_act.py`` embedded the FULL
envelope payload into the LLM-visible prompt, so a bound scripted floor LEAKED
to the model — an uncontrolled re-parameterization of the clustering objective
(violates the binding "never re-parameterize the LLM objective" amendment) and
a contamination of the live differential's control-vs-treatment input.

These pin (RED-first):

- a bound ``min_cluster_floor`` reaches NEITHER the key nor the value into the
  prompt (system or user message);
- the model-visible input is BYTE-IDENTICAL with and without a bound floor
  (Dan's byte-identity property — the deterministic post-hoc honoring is the
  ONLY delta);
- the hidden-key set is keyed off the scripted NAMESPACE
  (``SCRIPTED_ENUM_CLASSES``), never a hand-list (Dan D-0);
- the strip holds through the real ``act()`` path (recording fake handle, no
  network) — the Murat-5 zero-floor-bytes control in unit form.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.marcus.lesson_plan.pass1_source_span_catalog import (
    build_pass1_source_span_catalog,
)
from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act
from tests._helpers.pass1_bundle import write_primary_slide_bundle
from tests._helpers.pass1_catalog_response import select_catalog_ids

# A distinctive value that cannot collide with reference-doc/prompt text.
_SENTINEL_FLOOR = 424242


@dataclass
class _RecordingChat:
    response_text: str
    calls: list[list[dict[str, str]]] = field(default_factory=list)

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls.append(messages)
        return SimpleNamespace(
            content=select_catalog_ids(self.response_text, messages),
            usage_metadata=None,
        )


@dataclass
class _RecordingHandle:
    response_text: str
    chat: _RecordingChat = field(init=False)

    def __post_init__(self) -> None:
        self.chat = _RecordingChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


def _minimal_response() -> str:
    return json.dumps(
        {
            "lesson_summary": "s",
            "plan_units": [
                {
                    "unit_id": "u1",
                    "title": "T",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "source_refs": ["anchor one"],
                    "rationale": "r",
                    "cluster_id": "c-u1",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                    "cluster_interstitial_count": 0,
                }
            ],
            "collateral": {"declaration": "none"},
        }
    )


def test_bound_floor_key_and_value_never_reach_prompt() -> None:
    system_msg, user_msg = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1", "topic": "cells", "min_cluster_floor": _SENTINEL_FLOOR},
        extracted_source="Corpus text.",
    )
    for text in (system_msg, user_msg):
        assert "min_cluster_floor" not in text
        assert str(_SENTINEL_FLOOR) not in text


def test_prompt_byte_identical_with_and_without_floor() -> None:
    base = {"mode": "pass-1", "topic": "cells"}
    without = pass1_act.assemble_pass1_prompt(dict(base), extracted_source="Corpus.")
    with_floor = pass1_act.assemble_pass1_prompt(
        {**base, "min_cluster_floor": _SENTINEL_FLOOR}, extracted_source="Corpus."
    )
    assert without == with_floor


def test_hidden_keys_are_the_scripted_namespace() -> None:
    """Dan D-0: the strip keys off the scripted NAMESPACE (the sealed registry),
    not a hand-listed key. A future 2nd scripted class is auto-hidden."""
    from app.specialists.gary.styleguide_library import SCRIPTED_ENUM_CLASSES

    assert frozenset(SCRIPTED_ENUM_CLASSES) == pass1_act._LLM_HIDDEN_PAYLOAD_KEYS


def test_strip_does_not_mutate_the_full_payload() -> None:
    payload = {"mode": "pass-1", "min_cluster_floor": _SENTINEL_FLOOR}
    snapshot = json.dumps(payload, sort_keys=True)
    pass1_act.assemble_pass1_prompt(payload, extracted_source="Corpus.")
    # The FULL payload (floor included) stays available for post-hoc consumption.
    assert json.dumps(payload, sort_keys=True) == snapshot


def test_act_path_prompt_carries_zero_floor_bytes(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nSource.\nanchor one")
    handle = _RecordingHandle(_minimal_response())
    pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-strip",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
                "min_cluster_floor": 1,  # 1 <= any real cluster count: honoring no-op
            }
        ),
        handle=handle,
        model_id="gpt-5.4",
    )
    # EVERY call, not just the last (R6)
    assert handle.chat.calls
    for call in handle.chat.calls:
        for message in call:
            assert "min_cluster_floor" not in message["content"]


# --------------------------------------------------------------------------- #
# R3 (Blind#1) — cross-pass structural-fingerprint scrub                        #
# --------------------------------------------------------------------------- #
# At 05/05B the payload embeds the PRIOR (possibly floored) plan via
# upstream_output.lesson_plan; post-honoring plan_units carry the floor-engine-
# owned ``floor_subdivision_index`` annotation (+ minted ``#f`` cluster ids).
# The annotation key is scrubbed from the MODEL-VISIBLE payload copy (it is
# engine provenance, not plan state); the minted cluster ids are NOT renamed —
# the honored plan IS the real plan the refinement must see. Byte-identity is
# scoped accordingly: it holds for the CREATION pass and for any pass given
# identical incoming plans.
def _floored_prior_plan_payload() -> dict:
    return {
        "mode": "pass-1",
        "topic": "cells",
        "upstream_output": {
            "lesson_plan": {
                "plan_units": [
                    {
                        "unit_id": "u1",
                        "scope_decision": "in-scope",
                        "title": "T1",
                        "cluster_id": "c-u1",
                        "cluster_role": "head",
                        "cluster_interstitial_count": 0,
                        "floor_subdivision_index": 0,
                        "source_ref_ids": ["span:sha256:" + "1" * 64],
                        "source_refs": ["anchor one"],
                    },
                    {
                        "unit_id": "u2",
                        "scope_decision": "in-scope",
                        "title": "T2",
                        "cluster_id": "c-u1#f1",
                        "cluster_role": "head",
                        "cluster_interstitial_count": 0,
                        "floor_subdivision_index": 1,
                        "source_ref_ids": ["span:sha256:" + "2" * 64],
                        "source_refs": ["anchor two"],
                    },
                ]
            }
        },
    }


def test_visible_payload_scrubs_floor_subdivision_index() -> None:
    payload = _floored_prior_plan_payload()
    system_msg, user_msg = pass1_act.assemble_pass1_prompt(
        payload, extracted_source=None
    )
    for text in (system_msg, user_msg):
        assert "floor_subdivision_index" not in text
    # the minted cluster ids are legitimate downstream state and stay visible
    assert "c-u1#f1" in user_msg
    # selection IDs stay visible; deterministic projected bytes do not.
    assert "span:sha256:" + "2" * 64 in user_msg
    assert "anchor two" not in user_msg


def test_scrub_does_not_mutate_the_full_payload() -> None:
    payload = _floored_prior_plan_payload()
    snapshot = json.dumps(payload, sort_keys=True)
    pass1_act.assemble_pass1_prompt(payload, extracted_source=None)
    # the FULL payload (annotation included) stays available post-hoc
    assert json.dumps(payload, sort_keys=True) == snapshot
    units = payload["upstream_output"]["lesson_plan"]["plan_units"]
    assert [u["floor_subdivision_index"] for u in units] == [0, 1]


def test_act_path_prompt_carries_zero_fingerprint_bytes(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    source_text = "# Corpus\n\nSource.\nanchor one\nanchor two"
    write_primary_slide_bundle(bundle, source_text)
    handle = _RecordingHandle(_minimal_response())
    payload = _floored_prior_plan_payload()
    payload.update(
        {
            "run_id": "run-fingerprint",
            "runs_root": str(tmp_path),
            "bundle_reference": str(bundle),
        }
    )
    source_sections = (
        Pass1AuthenticatedSourceSection(
            source_id=(
                "slides/slide-1-primary.md|sha256:"
                + hashlib.sha256(source_text.encode("utf-8")).hexdigest()
            ),
            source_content_digest=(
                "sha256:" + hashlib.sha256(source_text.encode("utf-8")).hexdigest()
            ),
            extracted_content_digest=canonical_extracted_content_digest(source_text),
            body=source_text,
        ),
    )
    catalog = build_pass1_source_span_catalog(source_sections)
    entries = {entry.text: entry.span_id for entry in catalog.entries}
    prior_plan = payload["upstream_output"]["lesson_plan"]
    prior_plan["source_span_catalog_digest"] = catalog.catalog_digest
    prior_plan["plan_units"][0]["source_ref_ids"] = [entries["anchor one"]]
    prior_plan["plan_units"][1]["source_ref_ids"] = [entries["anchor two"]]
    payload["prior_plan_authority_receipt"] = (
        pass1_act.validate_pass1_plan_authority(
            prior_plan,
            source_sections=source_sections,
        )
    )
    pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")
    assert handle.chat.calls
    for call in handle.chat.calls:
        for message in call:
            assert "floor_subdivision_index" not in message["content"]
