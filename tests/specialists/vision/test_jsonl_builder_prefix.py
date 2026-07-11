"""T1: vision Batch JSONL builder — stable prompt prefix before image_url."""

from __future__ import annotations

from pathlib import Path

from app.specialists.vision.batch_route import build_vision_batch_rows, custom_id_for
from app.specialists.vision.provider import (
    PERCEPTION_SYSTEM_MESSAGE,
    build_perception_openai_messages,
)


def _png(tmp_path: Path, name: str = "s.png") -> Path:
    path = tmp_path / name
    # Minimal PNG header bytes are enough for file existence; builder only reads bytes.
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0c"
        b"IDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return path


def test_text_precedes_image_url_in_user_content(tmp_path: Path) -> None:
    png = _png(tmp_path)
    messages = build_perception_openai_messages(png, slide_id="slide-01")
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == PERCEPTION_SYSTEM_MESSAGE
    user = messages[1]["content"]
    assert isinstance(user, list)
    assert user[0]["type"] == "text"
    assert user[1]["type"] == "image_url"
    assert "slide-01" in user[0]["text"]


def test_prefix_stable_across_two_pngs_same_slide_id(tmp_path: Path) -> None:
    a_path = _png(tmp_path, "a.png")
    b_path = tmp_path / "b.png"
    b_path.write_bytes(a_path.read_bytes() + b"\x00different")
    a = build_perception_openai_messages(a_path, slide_id="slide-01")
    b = build_perception_openai_messages(b_path, slide_id="slide-01")
    assert a[0] == b[0]
    assert a[1]["content"][0] == b[1]["content"][0]  # text prefix identical
    assert a[1]["content"][1] != b[1]["content"][1]  # image bytes differ


def test_batch_rows_custom_id_and_chat_completions_url(tmp_path: Path) -> None:
    slides = [
        ("slide-01", _png(tmp_path, "1.png")),
        ("slide-02", _png(tmp_path, "2.png")),
    ]
    rows = build_vision_batch_rows(
        slides,
        run_id="run-abc",
        model="gpt-5.5",
        max_completion_tokens=8192,
    )
    assert len(rows) == 2
    assert rows[0]["custom_id"] == custom_id_for("run-abc", "slide-01")
    assert rows[0]["url"] == "/v1/chat/completions"
    assert rows[0]["body"]["model"] == "gpt-5.5"
    assert rows[0]["body"]["max_completion_tokens"] == 8192
    content = rows[0]["body"]["messages"][1]["content"]
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
