"""B5: hermetic prompt-cache key stability + drift pins."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.runtime.llm_batch.prompt_cache import (
    derive_prompt_cache_key,
    extract_cached_tokens,
    prompt_cache_extra_body,
    resolve_vision_prompt_cache_key,
)
from app.specialists.vision.batch_route import build_vision_batch_rows


def test_stable_perception_v1_key_is_stable_across_calls() -> None:
    a = derive_prompt_cache_key("stable_perception_v1")
    b = derive_prompt_cache_key("stable_perception_v1")
    assert a == b == "vision:perception:v1"


def test_key_not_per_slide_and_drifts_on_strategy_change() -> None:
    v1 = derive_prompt_cache_key("stable_perception_v1")
    v2 = derive_prompt_cache_key("stable_perception_v2")
    assert v1 != v2
    # Same strategy → same key regardless of slide identity (caller must not
    # bake slide_id into the strategy string).
    assert derive_prompt_cache_key("stable_perception_v1") == v1


def test_empty_strategy_omits_key() -> None:
    assert derive_prompt_cache_key(None) is None
    assert derive_prompt_cache_key("") is None
    assert prompt_cache_extra_body(None) == {}
    assert prompt_cache_extra_body("vision:perception:v1") == {
        "prompt_cache_key": "vision:perception:v1"
    }


def test_resolve_vision_realtime_and_batch_share_key() -> None:
    rt = resolve_vision_prompt_cache_key(mode="realtime")
    bt = resolve_vision_prompt_cache_key(mode="batch")
    assert rt == bt == "vision:perception:v1"


def test_perceive_png_bind_receives_shared_cache_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Realtime path must bind the same shared key as batch (B5 SHOULD)."""

    from types import SimpleNamespace

    from app.specialists.vision import provider as vision_provider

    png = tmp_path / "slide.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    bound: dict[str, object] = {}

    class _FakeChat:
        def bind(self, **kwargs: object) -> _FakeChat:
            bound.update(kwargs)
            return self

        def invoke(self, _messages: object) -> SimpleNamespace:
            return SimpleNamespace(
                content=(
                    '{"slide_id":"s1","confidence":"HIGH","coverage":"perceived",'
                    '"provenance":"png-grounded","visual_elements":[],'
                    '"extracted_text":"x","layout_description":"y",'
                    '"slide_title":"t"}'
                )
            )

    monkeypatch.setattr(
        vision_provider,
        "make_chat_model",
        lambda *_a, **_k: SimpleNamespace(chat=_FakeChat()),
    )
    vision_provider.perceive_png(png, slide_id="s1", model_id="gpt-5.5")
    assert bound.get("model_kwargs") == {
        "prompt_cache_key": "vision:perception:v1"
    }


def test_batch_rows_share_cache_key_across_slides(tmp_path: Path) -> None:
    png_a = tmp_path / "a.png"
    png_b = tmp_path / "b.png"
    # Minimal valid PNG header bytes are enough for message build? build uses
    # read_bytes — any bytes work for base64; use tiny files.
    png_a.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    png_b.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    rows = build_vision_batch_rows(
        [("slide-a", png_a), ("slide-b", png_b)],
        run_id="run-cache",
        model="gpt-5.5",
        max_completion_tokens=128,
    )
    keys = [r["body"].get("prompt_cache_key") for r in rows]
    assert keys == ["vision:perception:v1", "vision:perception:v1"]


def test_extract_cached_tokens_optional_fenced() -> None:
    assert extract_cached_tokens(None) is None
    assert extract_cached_tokens({}) is None
    assert extract_cached_tokens({"cached_tokens": 42}) == 42
    assert (
        extract_cached_tokens({"prompt_tokens_details": {"cached_tokens": 7}}) == 7
    )


def test_forced_override_key_on_batch_rows(tmp_path: Path) -> None:
    png = tmp_path / "x.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    rows = build_vision_batch_rows(
        [("s1", png)],
        run_id="r",
        model="gpt-5.5",
        max_completion_tokens=64,
        prompt_cache_key="forced-override",
    )
    assert rows[0]["body"]["prompt_cache_key"] == "forced-override"
