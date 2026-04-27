"""Unit tests for WondercraftClient.

2026-04-27 OPERATOR-SESSION REMEDIATION: payload + endpoint + status-field
defects discovered when M2 ceremony first ran against real Wondercraft API
(anti-pattern A16 instances; remediated in
`5a-2-wondercraft-client-payload-shape-defect`). Tests updated to assert the
corrected contract:

  - ``create_scripted_podcast`` payload: ``{"script": [{"text", "voice_id"}]}``
    (NOT ``{"title", "script": str, "voiceId": str}``).
  - ``get_job_status`` endpoint: ``/podcast/{job_id}`` (NOT ``/jobs/{job_id}``).
  - ``wait_for_job`` terminal-success: ``finished == True`` AND ``error == False``.
  - ``wait_for_job`` terminal-failure: ``error == True`` OR ``error_details``.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.api_clients.base_client import APIError
from scripts.api_clients.wondercraft_client import WondercraftClient


def test_base_url_normalized_to_v1() -> None:
    client = WondercraftClient(api_key="k", base_url="https://api.wondercraft.ai")
    assert client.base_url.endswith("/v1")


def test_check_connectivity_handles_auth_error_as_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = WondercraftClient(api_key="k")

    def fake_request_raw(method: str, endpoint: str, **kwargs: object) -> SimpleNamespace:
        raise APIError("unauthorized", status_code=401)

    monkeypatch.setattr(client, "_request_raw", fake_request_raw)

    result = client.check_connectivity()
    assert result["reachable"] is True
    assert result["status_code"] == 401


def test_get_job_status_uses_podcast_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Per Wondercraft API: status endpoint is /podcast/{job_id}, NOT /jobs/{job_id}."""
    client = WondercraftClient(api_key="k")
    captured: dict[str, str] = {}

    def fake_get(endpoint: str, params: dict[str, object] | None = None) -> dict[str, object]:
        captured["endpoint"] = endpoint
        return {"finished": False}

    monkeypatch.setattr(client, "get", fake_get)
    client.get_job_status("job-abc")
    assert captured["endpoint"] == "/podcast/job-abc"


def test_wait_for_job_success_on_finished_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """Terminal-success: response['finished'] is True."""
    client = WondercraftClient(api_key="k")
    statuses = iter(
        [
            {"finished": False, "error": False},
            {"finished": True, "error": False, "url": "https://example/audio.mp3"},
        ]
    )

    monkeypatch.setattr(client, "get_job_status", lambda job_id: next(statuses))
    monkeypatch.setattr("scripts.api_clients.wondercraft_client.time.sleep", lambda _: None)

    result = client.wait_for_job("job-1", poll_interval=0, max_attempts=5)
    assert result["finished"] is True
    assert result["url"] == "https://example/audio.mp3"


def test_wait_for_job_failure_on_error_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """Terminal-failure: response['error'] is True OR error_details populated."""
    client = WondercraftClient(api_key="k")

    monkeypatch.setattr(
        client,
        "get_job_status",
        lambda job_id: {"finished": True, "error": True, "error_details": "bad script"},
    )

    with pytest.raises(APIError, match="bad script"):
        client.wait_for_job("job-2", poll_interval=0, max_attempts=2)


def test_wait_for_job_failure_on_error_details_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    """Terminal-failure also fires when error_details is populated even if error flag absent."""
    client = WondercraftClient(api_key="k")

    monkeypatch.setattr(
        client,
        "get_job_status",
        lambda job_id: {"finished": False, "error_details": "voice rejected"},
    )

    with pytest.raises(APIError, match="voice rejected"):
        client.wait_for_job("job-3", poll_interval=0, max_attempts=2)


def test_create_scripted_podcast_segments_form(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preferred form: pass list of {text, voice_id} segments."""
    client = WondercraftClient(api_key="k")
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, json: dict[str, object] | None = None) -> dict[str, object]:
        captured["endpoint"] = endpoint
        captured["json"] = json or {}
        return {"job_id": "pod-1"}

    monkeypatch.setattr(client, "post", fake_post)
    result = client.create_scripted_podcast(
        "Podcast",
        [
            {"text": "Hello world.", "voice_id": "voice-7"},
            {"text": "Second segment.", "voice_id": "voice-9"},
        ],
    )

    assert result == {"job_id": "pod-1"}
    assert captured["endpoint"] == "/podcast/scripted"
    # Per Wondercraft API: ONLY 'script' field; no top-level title or voiceId.
    assert captured["json"] == {
        "script": [
            {"text": "Hello world.", "voice_id": "voice-7"},
            {"text": "Second segment.", "voice_id": "voice-9"},
        ],
    }


def test_create_scripted_podcast_legacy_string_form(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Backward-compat: plain-string form is wrapped as a single segment using voice_id."""
    client = WondercraftClient(api_key="k")
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, json: dict[str, object] | None = None) -> dict[str, object]:
        captured["endpoint"] = endpoint
        captured["json"] = json or {}
        return {"job_id": "pod-2"}

    monkeypatch.setattr(client, "post", fake_post)
    result = client.create_scripted_podcast(
        "Podcast",
        "Hello world.",
        voice_id="voice-7",
    )

    assert result == {"job_id": "pod-2"}
    assert captured["json"] == {
        "script": [{"text": "Hello world.", "voice_id": "voice-7"}],
    }


def test_create_scripted_podcast_legacy_string_form_requires_voice_id() -> None:
    """Backward-compat path raises if voice_id is missing (API requires per-segment voice_id)."""
    client = WondercraftClient(api_key="k")

    with pytest.raises(ValueError, match="voice_id is required"):
        client.create_scripted_podcast("Podcast", "Hello world.")
