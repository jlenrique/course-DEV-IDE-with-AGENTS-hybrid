from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.enrique import _act as enrique_act


class FakeElevenLabsClient:
    def list_voices(self) -> list[dict[str, object]]:
        return [
            {
                "voice_id": "voice-a",
                "name": "Alicia",
                "preview_url": "https://cdn.eleven.test/a.mp3",
                "labels": {"tone": "warm", "pace": "measured"},
            },
            {
                "voice_id": "voice-b",
                "name": "Ben",
                "preview_url": "https://cdn.eleven.test/b.mp3",
                "labels": {"tone": "clear"},
            },
        ]


@pytest.mark.parametrize(
    "selection,expected_voice",
    [
        (
            {"selected_voice_id": "voice-b", "operator_id": "juan", "rationale": "clearer"},
            "voice-b",
        ),
        ({}, "voice-a"),
    ],
)
def test_voice_selection_hil_artifacts(
    tmp_path: Path, selection: dict[str, str], expected_voice: str
) -> None:
    payload = {"bundle_path": str(tmp_path), "voice_selection": selection}

    result = enrique_act.build_voice_selection_contract(
        payload,
        client=FakeElevenLabsClient(),  # type: ignore[arg-type]
    )

    selection_dir = tmp_path / "voice-selection"
    preview_path = selection_dir / "voice-preview-options.json"
    review_path = selection_dir / "voice-selection-review.md"
    selected_path = selection_dir / "voice-selection.json"
    assert preview_path.is_file()
    assert review_path.is_file()
    assert selected_path.is_file()
    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    selected = json.loads(selected_path.read_text(encoding="utf-8"))
    assert preview["voices"][0] == {
        "voice_id": "voice-a",
        "voice_name": "Alicia",
        "sample_audio_url": "https://cdn.eleven.test/a.mp3",
        "characteristics": {"tone": "warm", "pace": "measured"},
        "eta_seconds": 30.0,
        "cost_per_1k_chars": 0.3,
    }
    assert "[recommended]" in review_path.read_text(encoding="utf-8")
    assert selected["selected_voice_id"] == expected_voice
    assert result["voice_selection"]["selected_voice_id"] == expected_voice


def test_voice_selection_uses_configured_default_slate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class ClientThatMustNotList:
        def list_voices(self) -> list[dict[str, object]]:
            raise AssertionError("configured default voice slate should avoid provider list order")

    monkeypatch.setattr(enrique_act, "ElevenLabsClient", ClientThatMustNotList)
    monkeypatch.setattr(
        enrique_act,
        "_load_config",
        lambda: {
            "voice_preview_candidate_count": 4,
            "default_cost_per_1k_chars_usd": 0.3,
            "default_recommended_voice_id": "EXAVITQu4vr4xnSDxMaL",
            "default_candidate_voices": [
                {
                    "voice_id": "EXAVITQu4vr4xnSDxMaL",
                    "voice_name": "Sarah - Mature, Reassuring, Confident",
                    "sample_audio_url": "https://cdn.eleven.test/sarah.mp3",
                    "characteristics": {"gender": "female", "descriptive": "professional"},
                },
                {
                    "voice_id": "0GoLoBHogFMTLhDROxLD",
                    "voice_name": "Shannon - Modern Professional American Woman",
                    "sample_audio_url": "https://cdn.eleven.test/shannon.mp3",
                    "characteristics": {"gender": "female", "descriptive": "professional"},
                },
                {
                    "voice_id": "W6zuQRTYRBdAK8ypjo5V",
                    "voice_name": "Stark - Classic American Voice",
                    "sample_audio_url": "https://cdn.eleven.test/stark.mp3",
                    "characteristics": {"gender": "male", "descriptive": "casual"},
                },
                {
                    "voice_id": "1SM7GgM6IMuvQlz2BwM3",
                    "voice_name": "Mark - ConvoAI",
                    "sample_audio_url": "https://cdn.eleven.test/mark.mp3",
                    "characteristics": {"gender": "male", "descriptive": "casual"},
                },
            ],
        },
    )

    result = enrique_act.build_voice_selection_contract({"bundle_path": str(tmp_path)})

    assert result["voice_preview"]["recommended_voice_id"] == "EXAVITQu4vr4xnSDxMaL"
    assert [voice["voice_id"] for voice in result["voice_preview"]["voices"]] == [
        "EXAVITQu4vr4xnSDxMaL",
        "0GoLoBHogFMTLhDROxLD",
        "W6zuQRTYRBdAK8ypjo5V",
        "1SM7GgM6IMuvQlz2BwM3",
    ]
    assert result["voice_selection"]["selected_voice_id"] == "EXAVITQu4vr4xnSDxMaL"
    review_text = (tmp_path / "voice-selection" / "voice-selection-review.md").read_text(
        encoding="utf-8"
    )
    assert (
        "EXAVITQu4vr4xnSDxMaL | Sarah - Mature, Reassuring, Confident | "
        "https://cdn.eleven.test/sarah.mp3 [recommended]"
    ) in review_text
