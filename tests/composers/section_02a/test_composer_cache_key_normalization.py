from __future__ import annotations

from pathlib import Path

from app.composers.section_02a import ComposerCache, compose
from app.composers.section_02a._prompt import cache_key_for_prompt
from tests.composers.section_02a._helpers import RoutingChatModel, payload


def test_cache_key_strips_operator_timestamp_and_run_id() -> None:
    prompt_a = (
        "operator_id: juanl\n"
        "generated_at: 2026-05-05T01:02:03Z\n"
        "run_id: 11111111-1111-4111-8111-111111111111\n"
        "filename: lesson.docx"
    )
    prompt_b = (
        "operator_id: someone-else\n"
        "generated_at: 2026-06-07T08:09:10Z\n"
        "run_id: 22222222-2222-4222-8222-222222222222\n"
        "filename: lesson.docx"
    )
    prompt_c = prompt_b.replace("lesson.docx", "other.docx")

    assert cache_key_for_prompt(prompt_a) == cache_key_for_prompt(prompt_b)
    assert cache_key_for_prompt(prompt_b) != cache_key_for_prompt(prompt_c)


def test_compose_cache_hit_avoids_second_llm_invocation(tmp_path: Path) -> None:
    (tmp_path / "lesson.docx").write_bytes(b"fixture")
    cache = ComposerCache()
    llm = RoutingChatModel(
        responses={
            "lesson.docx": payload(
                role="primary",
                expected_min_words=500,
                description="Primary lesson content.",
            )
        }
    )

    compose(tmp_path, llm=llm, cache=cache)
    compose(tmp_path, llm=llm, cache=cache)

    assert llm.invoke_count == 1


def test_compose_cache_miss_invokes_llm_for_new_prompt(tmp_path: Path) -> None:
    (tmp_path / "lesson.docx").write_bytes(b"fixture")
    (tmp_path / "other.docx").write_bytes(b"fixture")
    cache = ComposerCache()
    llm = RoutingChatModel(
        responses={
            "lesson.docx": payload(role="primary", expected_min_words=500),
            "other.docx": payload(role="supporting", expected_min_words=200),
        }
    )

    compose(tmp_path, llm=llm, cache=cache)

    assert llm.invoke_count == 2

