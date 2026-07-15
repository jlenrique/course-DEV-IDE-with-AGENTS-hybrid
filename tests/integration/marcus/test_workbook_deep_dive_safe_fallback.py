"""Regression coverage for the deterministic Deep-Dive safe-construction fallback.

Reproduces the three ways node 07W.2 (the live GPT-5 deep-dive writer) is
expected to fail on the real Tejal corpus and pins the operator-ratified
deterministic safe-construction response:

* B1 - a valid live candidate that fails the skeleton gate is upgraded to a
  deterministic authored skeleton instead of degrading the workbook.
* B2 - a fragile bold-parity mismatch degrades to the safe construction instead
  of hard-pausing 07W.1, while genuine structural defects still fail loud.
* B3 - the request is embedded once and span/claim text is de-duplicated so the
  provider input is not inflated toward the completion cap.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveAbilityInput,
    DeepDiveSkeletonRequest,
    NarrationSourceSpan,
    SourceClaim,
    compose_deep_dive_skeleton,
    deep_dive_candidate_would_author,
    deterministic_deep_dive_writer,
)
from app.marcus.orchestrator import workbook_prework_writers
from app.marcus.orchestrator.workbook_prework_writers import (
    DeepDiveProviderOutputError,
    LiveDeepDiveWriter,
    normalize_deep_dive_provider_payload,
)

FIXTURE = Path("tests/fixtures/deep_dive_37_2a")


def _fixture_request() -> DeepDiveSkeletonRequest:
    return DeepDiveSkeletonRequest.model_validate_json(
        (FIXTURE / "request.json").read_text("utf-8")
    )


def _builder_shaped_request(*, with_delta: bool = True) -> DeepDiveSkeletonRequest:
    """A request where every VO claim text equals its span text (build_deep_dive shape)."""
    spans = [
        NarrationSourceSpan(
            span_id=f"vo:{index}",
            text=f"Narration {index}: administrative waste costs the system dearly.",
            source_ref=f"exports/segment-manifest.yaml#segments/seg-{index}/narration_text",
        )
        for index in range(3)
    ]
    claims = [
        SourceClaim(
            claim_id=f"claim:vo:{index}",
            text=span.text,
            source_span_refs=(span.span_id,),
            role="vo",
        )
        for index, span in enumerate(spans)
    ]
    if with_delta:
        spans.append(
            NarrationSourceSpan(
                span_id="delta:0",
                text="Speaker note: no clinician should face burnout without design support.",
                source_ref="slides/slide-2.md#Narration (Speaker Notes)",
            )
        )
        claims.append(
            SourceClaim(
                claim_id="claim:delta:0",
                text=spans[-1].text,
                source_span_refs=("delta:0",),
                role="source_supported_delta",
            )
        )
    return DeepDiveSkeletonRequest(
        lesson_ref="exports/segment-manifest.yaml",
        source_spans=tuple(spans),
        source_claims=tuple(claims),
        abilities=(
            DeepDiveAbilityInput(ability_id="LO-1", text="Name the friction."),
            DeepDiveAbilityInput(ability_id="LO-2", text="Choose a first move."),
        ),
    )


class _RecordingStructured:
    def __init__(self, parsed: object) -> None:
        self._parsed = parsed
        self.messages: list[tuple[str, str]] | None = None

    def invoke(self, messages):
        self.messages = messages
        return {
            "parsed": self._parsed,
            "raw": SimpleNamespace(response_metadata={}),
            "parsing_error": None,
        }


class _RecordingChat:
    def __init__(self, parsed: object) -> None:
        self.structured = _RecordingStructured(parsed)

    def with_structured_output(self, schema, *, include_raw=False):
        assert schema == workbook_prework_writers.DeepDiveSkeletonWriterResult.model_json_schema()
        assert include_raw is True
        return self.structured


def _writer_over(parsed: object) -> LiveDeepDiveWriter:
    chat = _RecordingChat(parsed)
    writer = LiveDeepDiveWriter(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=chat, entry=None)
    )
    writer._recording_chat = chat  # type: ignore[attr-defined]
    return writer


# --------------------------------------------------------------------------- B1


def test_deterministic_writer_authors_delta_bearing_authority() -> None:
    request = _builder_shaped_request(with_delta=True)
    candidate = deterministic_deep_dive_writer(request)
    result = compose_deep_dive_skeleton(request, lambda _: candidate)
    assert result.status == "authored"
    assert result.gate.status == "pass"
    assert len(candidate.sections) == len(request.abilities)
    assert result.gate.covered_vo_claim_ids == ("claim:vo:0", "claim:vo:1", "claim:vo:2")
    assert result.gate.used_delta_claim_ids == ("claim:delta:0",)


def test_deterministic_writer_degrades_vo_only_authority() -> None:
    request = _builder_shaped_request(with_delta=False)
    candidate = deterministic_deep_dive_writer(request)
    result = compose_deep_dive_skeleton(request, lambda _: candidate)
    assert result.status == "degraded"
    assert result.known_losses == ("deep_dive_depth_delta_unavailable",)
    assert deep_dive_candidate_would_author(request, candidate) is False


def test_live_gate_failure_is_upgraded_to_deterministic_authored() -> None:
    request = _fixture_request()
    # A structurally valid but non-conforming live candidate (honest degrade).
    degraded_live = {
        "status": "degraded",
        "sections": [],
        "bold_terms": [],
        "known_losses": ["deep_dive_writer_unavailable"],
        "marker": "deep_dive_skeleton_degraded",
    }
    writer = _writer_over(degraded_live)
    candidate = writer(request)
    # RED before B1: writer returned the degraded live candidate unchanged, so the
    # workbook would degrade. GREEN: the safe construction authors.
    assert deep_dive_candidate_would_author(request, candidate) is True
    assert writer.last_fallback_engaged is True
    assert writer.last_fallback_reason == "live_gate_nonauthored"
    # Provider-evidence invariant: recorded raw normalizes back to the candidate.
    normalized, records = normalize_deep_dive_provider_payload(
        writer.last_raw_provider_payload
    )
    assert records == ()
    assert normalized == candidate.model_dump(mode="json")


def test_live_authored_pass_is_returned_unchanged_with_live_evidence() -> None:
    request = _fixture_request()
    authored = json.loads((FIXTURE / "writer_result.json").read_text("utf-8"))
    writer = _writer_over(authored)
    candidate = writer(request)
    assert candidate.status == "authored"
    assert writer.last_fallback_engaged is False
    assert writer.last_fallback_reason is None
    # Honest live raw is preserved (not overwritten by any construction).
    assert writer.last_raw_provider_payload["status"] == "authored"
    assert writer.last_live_failed_provider_payload is None


# --------------------------------------------------------------------------- B2


def _bold_hostile_payload(request: DeepDiveSkeletonRequest) -> dict:
    """An authored payload whose prose carries an unbalanced ``**`` marker."""
    claim = request.source_claims[0]
    span_ref = claim.source_span_refs[0]
    prose = "The market is worth **$5.2 trillion in unmatched bold."  # odd ** count
    return {
        "status": "authored",
        "sections": [
            {
                "ability_id": request.abilities[0].ability_id,
                "prose": prose,
                "claims": [
                    {
                        "skeleton_claim_id": "s1",
                        "text": prose,
                        "source_claim_refs": [claim.claim_id],
                        "source_span_refs": [span_ref],
                    }
                ],
            }
        ],
        "bold_terms": [],
        "known_losses": [],
        "marker": None,
    }


def test_bold_parity_failure_degrades_to_authored_instead_of_pausing() -> None:
    request = _fixture_request()  # carries a delta -> fallback can author
    payload = _bold_hostile_payload(request)
    writer = _writer_over(payload)
    # RED before B2: model_validate_json raised -> DeepDiveProviderOutputError (pause).
    candidate = writer(request)
    assert deep_dive_candidate_would_author(request, candidate) is True
    assert writer.last_fallback_engaged is True
    assert writer.last_fallback_reason == "bold_parity_degrade"
    # The failed live payload is preserved for telemetry, not silently discarded.
    assert writer.last_live_failed_provider_payload is not None
    assert writer.last_live_failed_provider_payload["sections"][0]["prose"] == payload[
        "sections"
    ][0]["prose"]
    # Provider-evidence invariant holds for the emitted construction.
    normalized, _ = normalize_deep_dive_provider_payload(
        writer.last_raw_provider_payload
    )
    assert normalized == candidate.model_dump(mode="json")


def test_bold_parity_failure_without_authorable_authority_degrades_not_pauses() -> None:
    request = _builder_shaped_request(with_delta=False)  # VO-only -> cannot author
    payload = _bold_hostile_payload(request)
    writer = _writer_over(payload)
    candidate = writer(request)
    assert candidate.status == "degraded"
    assert candidate.known_losses == ("deep_dive_execution_failed",)
    assert candidate.marker == "deep_dive_skeleton_degraded"
    assert writer.last_fallback_reason == "bold_parity_degrade"


def test_non_bold_structural_defect_still_fails_loud() -> None:
    request = _fixture_request()
    authored = json.loads((FIXTURE / "writer_result.json").read_text("utf-8"))
    # An unsafe marker (extra field) is a genuine defect, not a bold-parity slip.
    authored["bold_terms"].append({"term": "two stages", "extra": "planted"})
    writer = _writer_over(authored)
    with pytest.raises(DeepDiveProviderOutputError):
        writer(request)
    assert writer.last_fallback_engaged is False


# --------------------------------------------------------------------------- B3


def test_compact_payload_deduplicates_span_claim_text() -> None:
    request = _builder_shaped_request(with_delta=True)
    payload = workbook_prework_writers._compact_deep_dive_payload(request)
    # Every builder-shaped claim reuses its span text; none repeats it inline.
    for entry in payload["source_claims"]:
        assert entry["source_span_refs"]
        assert "text" not in entry
        assert entry["text_same_as_span"] == entry["source_span_refs"][0]
    # Span text is still present exactly once per span.
    assert [span["text"] for span in payload["source_spans"]] == [
        span.text for span in request.source_spans
    ]


def test_request_is_embedded_once_across_prompt_and_message() -> None:
    request = _builder_shaped_request(with_delta=True)
    authored = deterministic_deep_dive_writer(request).model_dump(mode="json")
    writer = _writer_over(authored)
    writer(request)
    system_message, human_message = (
        writer._recording_chat.structured.messages  # type: ignore[attr-defined]
    )
    system_text = system_message[1]
    human_text = human_message[1]
    needle = request.source_spans[0].text
    # RED before B3: the narration appeared 4x (span+claim text, embedded in both
    # the human message and the re-embedded system prompt). GREEN: exactly once.
    assert (system_text + human_text).count(needle) == 1
    assert needle not in system_text
    assert "text_same_as_span" in human_text
    # The system prompt no longer carries a full request JSON dump.
    assert '"source_claims"' not in system_text
