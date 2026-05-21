from __future__ import annotations

from pathlib import Path

import pytest

LLM_CACHE_HARNESS_SPECIALISTS = ("irene_pass1", "tracy", "dan")


@pytest.mark.parametrize("specialist", LLM_CACHE_HARNESS_SPECIALISTS)
def test_llm_specialist_cache_harness_declares_post_warmup_floor(
    specialist: str,
) -> None:
    path = Path("tests") / "end_to_end" / f"test_{specialist}_cache_hit_rate.py"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "median(ratios[2:]) >= 0.85" in text
    assert "prompt_tokens < 1024" in text
    assert "@pytest.mark.llm_live" in text
