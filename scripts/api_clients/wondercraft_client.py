"""Wondercraft API client for podcast and audio episode generation.

API: https://api.wondercraft.ai/v1
Auth: X-API-KEY
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from scripts.api_clients.base_client import APIError, BaseAPIClient

logger = logging.getLogger(__name__)

POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 120


class WondercraftClient(BaseAPIClient):
    """Client for Wondercraft REST API.

    Args:
        api_key: Wondercraft API key. Defaults to ``WONDERCRAFT_API_KEY``.
        base_url: API base URL. Defaults to
            ``WONDERCRAFT_BASE_URL`` or ``https://api.wondercraft.ai/v1``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        api_key = api_key or os.environ.get("WONDERCRAFT_API_KEY", "")
        normalized_base = (base_url or os.environ.get(
            "WONDERCRAFT_BASE_URL",
            "https://api.wondercraft.ai/v1",
        )).rstrip("/")
        if not normalized_base.endswith("/v1"):
            normalized_base = f"{normalized_base}/v1"

        super().__init__(
            base_url=normalized_base,
            auth_header="X-API-KEY",
            auth_prefix="",
            api_key=api_key,
        )

    def check_connectivity(self) -> dict[str, Any]:
        """Check basic Wondercraft API reachability without mutating data."""
        try:
            response = self._request_raw("GET", "/podcast", params={"page": 1, "pageSize": 1})
            status_code = response.status_code
            url = response.url
        except APIError as exc:
            status_code = exc.status_code or 0
            url = f"{self.base_url}/podcast"

        return {
            "reachable": bool(status_code) and status_code < 500,
            "status_code": status_code,
            "url": url,
        }

    def list_episodes(self, page: int = 1, page_size: int = 20) -> list[dict[str, Any]]:
        """List generated podcast episodes."""
        data = self.get("/podcast", params={"page": page, "pageSize": page_size})
        if isinstance(data, dict):
            if "items" in data and isinstance(data["items"], list):
                return data["items"]
            if "episodes" in data and isinstance(data["episodes"], list):
                return data["episodes"]
        return data if isinstance(data, list) else []

    def create_podcast(
        self,
        title: str,
        prompt: str,
        *,
        voice_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an AI-scripted podcast from a prompt."""
        payload: dict[str, Any] = {
            "title": title,
            "prompt": prompt,
        }
        if voice_id:
            payload["voiceId"] = voice_id
        return self.post("/podcast", json=payload)

    def create_scripted_podcast(
        self,
        title: str,
        script_segments: list[dict[str, str]] | str,
        *,
        voice_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a podcast episode from a user-provided script.

        Per Wondercraft API docs (verified live 2026-04-27 against real
        ``POST /podcast/scripted`` endpoint), the ``script`` field MUST be an
        array of ``{text, voice_id}`` objects, NOT a plain string. The
        ``title`` field is NOT in the request body — only ``script`` and
        optional ``music_spec`` are spec'd. ``voiceId`` at top level is also
        not honored; voice_id is per-segment.

        ``script_segments`` accepts either:
          * ``list[dict]`` — preferred; each dict requires ``text`` + ``voice_id``.
          * ``str`` — legacy convenience form: wraps as a single segment using
            ``voice_id`` (which then becomes required).

        Operator-session 2026-04-27 (post-A16 remediation): the previous
        signature passed ``script`` as a plain string + top-level ``voiceId``.
        That payload was rejected by the live API with 403 Forbidden (one of
        Wondercraft's payload-validation responses) — defect filed as
        anti-pattern A16 instance ``5a-2-wondercraft-client-payload-shape-defect``
        and remediated here.
        """
        # Backward-compat: if caller passed a plain string, wrap as single segment.
        if isinstance(script_segments, str):
            if not voice_id:
                raise ValueError(
                    "create_scripted_podcast: when script_segments is a plain string, "
                    "voice_id is required (the API requires per-segment voice_id)."
                )
            segments: list[dict[str, str]] = [
                {"text": script_segments, "voice_id": voice_id},
            ]
        else:
            segments = list(script_segments)

        payload: dict[str, Any] = {"script": segments}
        return self.post("/podcast/scripted", json=payload)

    def create_conversation_podcast(
        self,
        title: str,
        script: str,
    ) -> dict[str, Any]:
        """Create a conversation-mode podcast from structured script text."""
        return self.post(
            "/podcast/convo-mode/user-scripted",
            json={"title": title, "script": script},
        )

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Fetch async generation job status.

        Per Wondercraft API docs (verified live 2026-04-27): job status is
        retrieved via ``GET /podcast/{job_id}``, NOT ``GET /jobs/{job_id}``.
        Response shape uses ``finished`` (boolean) + ``url`` (audio download)
        + ``error`` (boolean) + ``error_details``, NOT a ``status`` enum.

        Operator-session 2026-04-27 (post-A16 remediation): the previous
        impl polled the wrong endpoint; same A16 instance as the payload-shape
        defect on ``create_scripted_podcast``.
        """
        return self.get(f"/podcast/{job_id}")

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
    ) -> dict[str, Any]:
        """Poll Wondercraft async job until completion or failure.

        Terminal-success state: ``finished == True`` AND ``error == False``.
        Terminal-failure state: ``error == True`` OR explicit ``error_details``.
        Anything else: job still in progress; sleep + retry.
        """
        for attempt in range(max_attempts):
            data = self.get_job_status(job_id)

            # Terminal failure signal
            if data.get("error") is True or data.get("error_details"):
                logger.warning(
                    "Job %s ended in error after %d polls: %s",
                    job_id,
                    attempt + 1,
                    data.get("error_details"),
                )
                raise APIError(
                    f"Wondercraft job {job_id} failed: {data.get('error_details')}",
                    status_code=None,
                )

            # Terminal success signal
            if data.get("finished") is True:
                logger.info("Job %s completed after %d polls", job_id, attempt + 1)
                return data

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Wondercraft job {job_id} did not complete within {max_attempts * poll_interval}s"
        )
