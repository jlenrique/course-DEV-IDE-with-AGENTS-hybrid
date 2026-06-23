from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision import _act
from app.specialists.vision import provider as provider_mod
from app.specialists.vision.payload_contract import VisionProviderResponse
from app.specialists.vision.provider import (
    VisionProviderError,
    VisionProviderTimeout,
    perceive_png,
)


class _StubChat:
    """Stub for the bound ChatOpenAI handle: records calls, returns scripted content.

    `provider.perceive_png` does `make_chat_model(...).chat.bind(timeout=...)`
    then `.invoke(messages)`. This stub satisfies both: `bind` returns self, and
    `invoke` pops the next scripted response (a str content, or an Exception to
    raise).
    """

    def __init__(self, responses: list[object]) -> None:
        self._responses = list(responses)
        self.calls = 0
        self.message_lengths: list[int] = []

    def bind(self, **_: Any) -> _StubChat:
        return self

    def invoke(self, messages: Any) -> Any:
        self.calls += 1
        # Record the message-list length per invocation so the bounded-repair
        # tests can assert a repair instruction was appended on the retry (S2).
        self.message_lengths.append(len(messages))
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item

        class _Resp:
            content = item

        return _Resp()


def _stub_make_chat_model(stub: _StubChat) -> Any:
    """Return a fake make_chat_model that yields a handle wrapping `stub`."""

    class _Handle:
        chat = stub

    def _factory(*_a: Any, **_k: Any) -> _Handle:
        return _Handle()

    return _factory


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="0" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )


def _png(tmp_path: Path) -> Path:
    path = tmp_path / "slide-01.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    return path


def _response(slide_id: str = "slide-01", coverage: str = "perceived") -> VisionProviderResponse:
    return VisionProviderResponse(
        slide_id=slide_id,
        confidence="HIGH" if coverage == "perceived" else "LOW",
        coverage=coverage,
        provenance="png-grounded" if coverage == "perceived" else "not-covered",
        extracted_text="$4.5T spend. Building photo.",
        layout_description="Three stat callouts beside a building photo.",
        visual_elements=[
            {
                "id": "metric",
                "kind": "callout",
                "text": "$4.5T",
                "bbox": [0.12, 0.12, 0.38, 0.26],
            },
            {
                "id": "building",
                "kind": "photo",
                "label": "building photo",
                "bbox": [0.50, 0.18, 0.90, 0.80],
            },
        ],
        source_png_path="slide-01.png",
        provider_model_id="vision-fixture-v1",
    )


def test_act_emits_per_slide_artifacts_and_not_covered_for_unreadable_slide(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    png = _png(tmp_path)
    calls: list[str] = []

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        calls.append(str(path))
        return _response(slide_id)

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    payload = {
        "gary_slide_output": [
            {"slide_id": "slide-01", "file_path": str(png)},
            {"slide_id": "slide-02", "file_path": str(tmp_path / "missing.png")},
        ]
    }

    result = _act.act(_state(payload))
    output = json.loads(result["cache_state"]["cache_prefix"])

    assert calls == [str(png)]
    assert [row["slide_id"] for row in output["perception_artifacts"]] == [
        "slide-01",
        "slide-02",
    ]
    assert output["perception_artifacts"][0]["coverage"] == "perceived"
    assert output["perception_artifacts"][0]["reading_path"] == "split_image_text"
    assert output["perception_artifacts"][0]["macro_layout"] == "split_image_text"
    assert output["perception_artifacts"][1]["coverage"] == "not-covered"
    assert output["perception_artifacts"][1]["reading_path"] is None


def test_reading_path_classification_failure_converts_to_vision_provider_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # P2-4a T11 (party-mode 5/5, Cluster 3a): a HIGH/perceived artifact whose
    # elements carry no positioned geometry makes the deterministic classifier
    # raise ReadingPathClassificationError (a ValueError). The vision node must
    # convert that to a NON-retryable VisionProviderError routed through the
    # error-pause contract — never let a bare ValueError escape the retry guard.
    png = _png(tmp_path)

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        return VisionProviderResponse(
            slide_id=slide_id,
            confidence="HIGH",
            coverage="perceived",
            provenance="png-grounded",
            extracted_text="Building photo only.",
            layout_description="A single building photo.",
            visual_elements=[{"id": "building", "kind": "photo", "label": "building photo"}],
            source_png_path="slide-01.png",
            provider_model_id="vision-fixture-v1",
        )

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    payload = {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}

    with pytest.raises(VisionProviderError, match="reading-path classification failed"):
        _act.act(_state(payload))


@pytest.mark.parametrize(
    "error",
    [
        VisionProviderTimeout("timeout"),
        VisionProviderError("server error", status_code=500),
        VisionProviderError("busy", status_code=429),
        VisionProviderError("request timeout", status_code=408),
        VisionProviderError("connect reset", tag="vision.provider.transport"),
    ],
)
def test_transport_retry_is_one_retry_for_timeout_5xx_429_408_or_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: VisionProviderError
) -> None:
    png = _png(tmp_path)
    calls = 0

    def flaky(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise error
        return _response(slide_id)

    monkeypatch.setattr(_act, "perceive_png", flaky)
    result = _act.act(
        _state({"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]})
    )

    assert calls == 2
    output = json.loads(result["cache_state"]["cache_prefix"])
    assert output["perception_artifacts"][0]["coverage"] == "perceived"


@pytest.mark.parametrize(
    "error",
    [
        VisionProviderError("bad request", status_code=400),
        VisionProviderError("low fidelity", status_code=None),
    ],
)
def test_act_does_not_retry_4xx_or_quality_failures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    png = _png(tmp_path)
    calls = 0

    def failing(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        nonlocal calls
        calls += 1
        raise error

    monkeypatch.setattr(_act, "perceive_png", failing)

    with pytest.raises(type(error)):
        _act.act(
            _state(
                {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}
            )
        )

    assert calls == 1


def test_perceive_png_parses_valid_model_json_via_stubbed_chat(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Replaces the retired httpx MockTransport endpoint test (Amelia: that path
    # died with the pinned-endpoint provider). The live perceiver calls
    # make_chat_model(...).chat.bind(...).invoke(...); stub that seam and feed a
    # valid VisionProviderResponse-shaped JSON string.
    png = _png(tmp_path)
    valid_json = json.dumps(
        {
            "slide_id": "slide-01",
            "confidence": "HIGH",
            "coverage": "perceived",
            "confidence_score": 0.92,
            "slide_title": "The Economic Reality",
            "extracted_text": "$4.5T spend. Building photo.",
            "layout_description": "Stat callout beside a building photo.",
            "text_blocks": ["$4.5T", "Building photo"],
            "visual_elements": [
                {
                    "id": "metric",
                    "kind": "callout",
                    "text": "$4.5T",
                    "bbox": [0.12, 0.12, 0.38, 0.26],
                },
                {"id": "building", "kind": "photo", "text": "", "bbox": [0.50, 0.18, 0.90, 0.80]},
            ],
        }
    )
    stub = _StubChat([valid_json])
    monkeypatch.setattr(provider_mod, "make_chat_model", _stub_make_chat_model(stub))

    response = perceive_png(png, slide_id="slide-01", model_id="gpt-5.5")

    assert stub.calls == 1
    assert isinstance(response, VisionProviderResponse)
    assert response.slide_id == "slide-01"
    assert response.confidence == "HIGH"
    assert response.provider_model_id == "gpt-5.5"
    assert response.source_png_path == str(png)
    assert "$4.5T" in response.extracted_text
    assert len(response.visual_elements) == 2


def test_perception_prompt_demands_per_element_role_tier() -> None:
    prompt = provider_mod._perception_prompt("slide-01")

    assert '"role_tier": "1" | "2" | "2_5" | "3" | "4"' in prompt
    assert "feel/glance/confirm/trace/tag" in prompt
    assert "tier 3" in prompt


def test_parse_response_accepts_role_tier_and_rejects_out_of_vocab_value() -> None:
    from app.specialists.vision.provider import _parse_response

    raw = json.dumps(
        {
            "slide_id": "slide-01",
            "confidence": "HIGH",
            "coverage": "perceived",
            "confidence_score": 0.9,
            "slide_title": "T",
            "extracted_text": "text",
            "layout_description": "layout",
            "text_blocks": ["text"],
            "visual_elements": [
                {
                    "id": "chart",
                    "kind": "chart",
                    "text": "",
                    "bbox": [0.2, 0.2, 0.8, 0.6],
                    "role_tier": "2_5",
                }
            ],
        }
    )

    response = _parse_response(
        raw, slide_id="slide-01", model_id="gpt-5.5", source_png_path="slide-01.png"
    )
    assert response.visual_elements[0]["role_tier"] == "2_5"

    bad = json.loads(raw)
    bad["visual_elements"][0]["role_tier"] = "2.5"
    with pytest.raises(VisionProviderError) as excinfo:
        _parse_response(
            json.dumps(bad),
            slide_id="slide-01",
            model_id="gpt-5.5",
            source_png_path="slide-01.png",
        )

    assert excinfo.value.tag == "vision.provider.malformed-json"


def test_perceive_png_repairs_malformed_json_bounded_then_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # AC-4: malformed JSON retries through the existing taxonomy, bound <= 3,
    # then raises a vision.provider.malformed-json tagged error (no new ad-hoc
    # retry loop semantics leak; the failure tag is NON-retryable at the _act
    # boundary so it does not stack with the act-level transport retry).
    png = _png(tmp_path)
    stub = _StubChat(["not json", "{ still: broken", "}{nope"])
    monkeypatch.setattr(provider_mod, "make_chat_model", _stub_make_chat_model(stub))

    with pytest.raises(VisionProviderError) as excinfo:
        perceive_png(png, slide_id="slide-01", model_id="gpt-5.5")

    assert excinfo.value.tag == "vision.provider.malformed-json"
    assert stub.calls == 3  # MAX_JSON_REPAIR_ATTEMPTS
    # S2: each malformed attempt appends a repair instruction, so the message
    # list grows monotonically across the 3 attempts (2, then 3, then 4).
    assert stub.message_lengths == [2, 3, 4]


def test_perceive_png_recovers_after_one_malformed_then_valid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The bounded repair loop succeeds if a later attempt returns valid JSON.
    png = _png(tmp_path)
    valid_json = json.dumps(_response("slide-01").model_dump())
    stub = _StubChat(["garbage prose, no json", valid_json])
    monkeypatch.setattr(provider_mod, "make_chat_model", _stub_make_chat_model(stub))

    response = perceive_png(png, slide_id="slide-01", model_id="gpt-5.5")

    assert stub.calls == 2
    assert response.slide_id == "slide-01"
    # S2: the second (repair) invocation carries an appended repair instruction,
    # so its message list is longer than the first attempt's.
    assert stub.message_lengths == [2, 3]


def test_perceive_png_maps_timeout_to_vision_provider_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # AC-3: SDK timeout maps onto the existing VisionProviderTimeout tagged error.
    import openai

    png = _png(tmp_path)
    stub = _StubChat([openai.APITimeoutError(request=None)])  # type: ignore[arg-type]
    monkeypatch.setattr(provider_mod, "make_chat_model", _stub_make_chat_model(stub))

    with pytest.raises(VisionProviderTimeout):
        perceive_png(png, slide_id="slide-01", model_id="gpt-5.5")


def test_perceive_png_maps_model_resolution_failure_to_non_retryable_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # M2 (code-review remediation): a model-resolution/construction failure in
    # make_chat_model (e.g. selector.ModelResolutionError, a RuntimeError) must
    # NOT escape perceive_png as a raw RuntimeError past the _act retry/error-
    # pause taxonomy. It maps to a NON-retryable VisionProviderError tagged
    # vision.provider.model-resolution so _act routes it to error-pause.
    from app.models.selector import ModelResolutionError

    png = _png(tmp_path)

    def boom(*_a: Any, **_k: Any) -> Any:
        raise ModelResolutionError("cascade could not resolve any model_id")

    monkeypatch.setattr(provider_mod, "make_chat_model", boom)

    with pytest.raises(VisionProviderError) as excinfo:
        perceive_png(png, slide_id="slide-01", model_id="gpt-5.5")

    assert excinfo.value.tag == "vision.provider.model-resolution"
    assert excinfo.value.status_code is None
    # And _act must treat it as NON-retryable (routes to error-pause).
    assert _act._is_retryable_provider_error(excinfo.value) is False


def test_parse_response_raises_contract_on_slide_id_mismatch(
    tmp_path: Path,
) -> None:
    # M3 (code-review remediation): a response echoing the WRONG slide_id is a
    # cross-wired image/response and must FAIL LOUD with a NON-retryable
    # vision.provider.contract error — NOT be silently overwritten (the old
    # masking regression). provider_model_id is code-controlled (overwritten).
    from app.specialists.vision.provider import _parse_response

    wrong = json.dumps(
        {
            "slide_id": "slide-99",  # mismatched against requested slide-01
            "confidence": "HIGH",
            "coverage": "perceived",
            "confidence_score": 0.9,
            "slide_title": "Wrong",
            "extracted_text": "text",
            "layout_description": "layout",
            "text_blocks": ["text"],
            "visual_elements": [
                {"id": "a", "kind": "callout", "text": "x", "bbox": [0.1, 0.1, 0.3, 0.3]}
            ],
            "provider_model_id": "evil-model-emitted-id",
        }
    )

    with pytest.raises(VisionProviderError) as excinfo:
        _parse_response(
            wrong, slide_id="slide-01", model_id="gpt-5.5", source_png_path="slide-01.png"
        )

    assert excinfo.value.tag == "vision.provider.contract"
    assert _act._is_retryable_provider_error(excinfo.value) is False


def test_parse_response_overwrites_provider_model_id_with_code_controlled(
    tmp_path: Path,
) -> None:
    # M3: a model-emitted provider_model_id is NOT trusted — code-controlled.
    from app.specialists.vision.provider import _parse_response

    raw = json.dumps(
        {
            "slide_id": "slide-01",
            "confidence": "HIGH",
            "coverage": "perceived",
            "confidence_score": 0.9,
            "slide_title": "T",
            "extracted_text": "text",
            "layout_description": "layout",
            "text_blocks": ["text"],
            "visual_elements": [
                {"id": "a", "kind": "callout", "text": "x", "bbox": [0.1, 0.1, 0.3, 0.3]}
            ],
            "provider_model_id": "model-emitted-lie",
            "source_png_path": "model-emitted-path.png",
        }
    )

    response = _parse_response(
        raw, slide_id="slide-01", model_id="gpt-5.5", source_png_path="real-path.png"
    )

    assert response.provider_model_id == "gpt-5.5"
    assert response.source_png_path == "real-path.png"
