"""Tests for audio sensory bridge."""

from unittest.mock import patch

import pytest

from skills.sensory_bridges.scripts.audio_to_agent import _compute_wpm, transcribe_audio
from skills.sensory_bridges.scripts.bridge_utils import validate_response


class TestComputeWpm:
    def test_normal_wpm(self):
        words = [{"type": "word"}] * 150
        assert _compute_wpm(words, 60.0) == 150.0

    def test_excludes_spacing(self):
        words = [{"type": "word"}] * 100 + [{"type": "spacing"}] * 50
        assert _compute_wpm(words, 60.0) == 100.0

    def test_zero_duration(self):
        assert _compute_wpm([{"type": "word"}], 0.0) == 0.0


class TestTranscribeAudio:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            transcribe_audio("/nonexistent/file.mp3")

    def test_missing_api_key(self, tmp_path):
        f = tmp_path / "test.mp3"
        f.write_bytes(b"\x00")

        with patch.dict("os.environ", {}, clear=True):
            with patch("skills.sensory_bridges.scripts.audio_to_agent.load_dotenv"):
                result = transcribe_audio(f)
                assert result["confidence"] == "LOW"
                assert "ELEVENLABS_API_KEY" in result["confidence_rationale"]
                assert validate_response(result) == []

    @patch("skills.sensory_bridges.scripts.audio_to_agent._call_stt")
    @patch("skills.sensory_bridges.scripts.audio_to_agent._get_api_key")
    def test_successful_transcription(self, mock_key, mock_stt, tmp_path):
        f = tmp_path / "test.mp3"
        f.write_bytes(b"\x00")

        mock_key.return_value = "test-key"
        mock_stt.return_value = {
            "text": "The three macro trends reshaping healthcare delivery",
            "words": [
                {"text": "The", "start": 0.0, "end": 0.2, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 0.2, "end": 0.25, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "three", "start": 0.25, "end": 0.5, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 0.5, "end": 0.55, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "macro", "start": 0.55, "end": 0.9, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 0.9, "end": 0.95, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "trends", "start": 0.95, "end": 1.3, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 1.3, "end": 1.35, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "reshaping", "start": 1.35, "end": 1.8, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 1.8, "end": 1.85, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "healthcare", "start": 1.85, "end": 2.3, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 2.3, "end": 2.35, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "delivery", "start": 2.35, "end": 2.8, "type": "word", "speaker_id": "speaker_0"},
            ],
            "language_code": "en",
        }

        result = transcribe_audio(f)
        assert result["confidence"] == "HIGH"
        assert result["transcript_text"] == "The three macro trends reshaping healthcare delivery"
        assert result["total_duration_ms"] == 2800
        assert result["wpm"] > 0
        assert result["language_code"] == "en"
        assert validate_response(result) == []

    @patch("skills.sensory_bridges.scripts.audio_to_agent._call_stt")
    @patch("skills.sensory_bridges.scripts.audio_to_agent._get_api_key")
    def test_empty_transcript(self, mock_key, mock_stt, tmp_path):
        f = tmp_path / "silence.mp3"
        f.write_bytes(b"\x00")

        mock_key.return_value = "test-key"
        mock_stt.return_value = {"text": "", "words": []}

        result = transcribe_audio(f)
        assert result["confidence"] == "LOW"
        assert validate_response(result) == []
