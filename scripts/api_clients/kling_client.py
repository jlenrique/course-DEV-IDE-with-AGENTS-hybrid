"""Kling AI API client for video generation.

API Docs: https://klingapi.com/docs
Auth: two supported schemes, selected automatically:
  1. Static API token (newer single-token auth). If ``KLING_API_TOKEN`` is
     set (env or ctor arg), it is sent verbatim as ``Authorization: Bearer
     <token>`` and no JWT is built or refreshed.
  2. Legacy JWT (HS256) minted from ``KLING_ACCESS_KEY`` + ``KLING_SECRET_KEY``
     and refreshed before each request. Used only when no API token is set.
Capabilities: text-to-video, image-to-video, lip-sync, video extension
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import jwt
import requests

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)

KLING_BASE_URL = "https://api.klingai.com"
POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 120
TOKEN_LIFETIME = 1800


def generate_jwt_token(access_key: str, secret_key: str) -> str:
    """Generate a JWT token for Kling API authentication.

    Args:
        access_key: Kling access key (AK).
        secret_key: Kling secret key (SK).

    Returns:
        Signed JWT token string valid for 30 minutes.
    """
    now = int(time.time())
    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": access_key,
        "exp": now + TOKEN_LIFETIME,
        "nbf": now - 5,
    }
    return jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)


class KlingClient(BaseAPIClient):
    """Client for Kling AI video generation API.

    Selects one of two auth schemes automatically:

      - **Static API token** (newer single-token auth): if ``api_token`` is
        provided (or ``KLING_API_TOKEN`` is set), it is used verbatim as the
        ``Authorization: Bearer`` value and JWT generation/refresh is skipped
        entirely.
      - **Legacy JWT**: otherwise, a JWT is minted from ``access_key`` +
        ``secret_key`` (HS256) and refreshed before each request.

    Args:
        access_key: Kling access key. Defaults to ``KLING_ACCESS_KEY`` env var.
        secret_key: Kling secret key. Defaults to ``KLING_SECRET_KEY`` env var.
        api_token: Ready-made API token. Defaults to ``KLING_API_TOKEN`` env
            var. When present, takes precedence over the AK/SK JWT path.
    """

    def __init__(
        self,
        access_key: str | None = None,
        secret_key: str | None = None,
        api_token: str | None = None,
    ) -> None:
        self._api_token = api_token or os.environ.get("KLING_API_TOKEN", "")
        self._access_key = access_key or os.environ.get("KLING_ACCESS_KEY", "")
        self._secret_key = secret_key or os.environ.get("KLING_SECRET_KEY", "")
        self._token_expiry = 0

        token = self._ensure_token()
        super().__init__(
            base_url=KLING_BASE_URL,
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=token,
            timeout=60,
            default_headers={"Content-Type": "application/json"},
        )

    def _ensure_token(self) -> str:
        """Return the current auth token, refreshing the JWT if needed.

        When a static API token is configured this is a no-op that returns the
        token unchanged (no JWT is generated). Otherwise the legacy JWT is
        regenerated if expired or nearly expired.
        """
        if self._api_token:
            return self._api_token
        now = int(time.time())
        if now >= self._token_expiry - 60:
            token = generate_jwt_token(self._access_key, self._secret_key)
            self._token_expiry = now + TOKEN_LIFETIME
            if hasattr(self, "session"):
                self.session.headers["Authorization"] = f"Bearer {token}"
            return token
        return self.session.headers.get("Authorization", "").replace("Bearer ", "")

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Override to refresh JWT token before each request."""
        self._ensure_token()
        return super()._request(method, endpoint, **kwargs)

    def _request_raw(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> requests.Response:
        """Override to refresh JWT token before each raw request."""
        self._ensure_token()
        return super()._request_raw(method, endpoint, **kwargs)

    # -- Video Generation --

    def text_to_video(
        self,
        prompt: str,
        *,
        model_name: str = "kling-v2-6",
        duration: str = "5",
        aspect_ratio: str = "16:9",
        mode: str = "std",
        negative_prompt: str | None = None,
        sound: bool | None = None,
    ) -> dict[str, Any]:
        """Generate a video from a text prompt.

        Args:
            prompt: Text description of the video (max 2500 chars).
            model_name: Model version. Options: kling-v1-6, kling-v2-1-master,
                kling-v2-5, kling-v2-6, kling-v3-0. Default: kling-v2-6.
            duration: Video duration as string. "5" or "10" for most models,
                "3"-"15" for kling-v3-0.
            aspect_ratio: Output ratio (16:9, 9:16, 1:1).
            mode: Generation mode (std=720p, pro=1080p).
            negative_prompt: Elements to exclude (max 2500 chars).
            sound: Optional native audio generation toggle where supported.

        Returns:
            Task response with ``task_id`` for polling.
        """
        payload: dict[str, Any] = {
            "model_name": model_name,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if sound is not None:
            payload["sound"] = sound

        return self.post("/v1/videos/text2video", json=payload)

    def image_to_video(
        self,
        image_url: str,
        *,
        prompt: str = "",
        model_name: str = "kling-v2-6",
        duration: str = "5",
        aspect_ratio: str = "16:9",
        mode: str = "std",
        end_image_url: str | None = None,
        negative_prompt: str | None = None,
        sound: bool | None = None,
    ) -> dict[str, Any]:
        """Generate a video from a static image.

        Args:
            image_url: URL of the source image (first frame).
            prompt: Motion description for the animation.
            model_name: Model version (kling-v1-6, kling-v2-6, kling-v3-0).
            duration: Video duration as string (max "10" for image-to-video).
            aspect_ratio: Output ratio (16:9, 9:16, 1:1).
            mode: Generation mode (std or pro).
            end_image_url: End frame image for interpolation.
            negative_prompt: Elements to exclude.
            sound: Optional native audio generation toggle where supported.

        Returns:
            Task response with ``task_id`` for polling.
        """
        payload: dict[str, Any] = {
            "model_name": model_name,
            "image": image_url,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
        }
        if end_image_url:
            payload["end_image"] = end_image_url
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if sound is not None:
            payload["sound"] = sound

        return self.post("/v1/videos/image2video", json=payload)

    def generate_motion(
        self,
        *,
        prompt: str,
        image_url: str | None = None,
        model_name: str = "kling-v2-6",
        duration: str = "5",
        aspect_ratio: str = "16:9",
        mode: str = "std",
        negative_prompt: str | None = None,
        sound: bool | None = None,
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Submit a motion job and return the completed task payload."""
        task_type = "image2video" if image_url else "text2video"
        if image_url:
            submitted = self.image_to_video(
                image_url,
                prompt=prompt,
                model_name=model_name,
                duration=duration,
                aspect_ratio=aspect_ratio,
                mode=mode,
                negative_prompt=negative_prompt,
                sound=sound,
            )
        else:
            submitted = self.text_to_video(
                prompt,
                model_name=model_name,
                duration=duration,
                aspect_ratio=aspect_ratio,
                mode=mode,
                negative_prompt=negative_prompt,
                sound=sound,
            )
        data = submitted.get("data") if isinstance(submitted.get("data"), dict) else {}
        task_id = submitted.get("task_id") or data.get("task_id")
        if not task_id:
            return submitted
        return self.wait_for_completion(
            str(task_id),
            task_type=task_type,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            timeout_seconds=timeout_seconds,
        )

    def lip_sync(
        self,
        video_url: str,
        audio_url: str,
    ) -> dict[str, Any]:
        """Apply lip-sync to a video using an audio track.

        Args:
            video_url: URL of the source video (2-10s, 720p/1080p).
            audio_url: URL of the audio track (2-60s).

        Returns:
            Task response with ``task_id`` for polling.
        """
        return self.post("/v1/videos/lip-sync", json={
            "video_url": video_url,
            "audio_url": audio_url,
        })

    def extend_video(
        self,
        video_url: str,
        *,
        prompt: str = "",
        duration: int = 5,
    ) -> dict[str, Any]:
        """Extend an existing video with generated continuation.

        Args:
            video_url: URL of the video to extend.
            prompt: Description for the extended content.
            duration: Duration of the extension in seconds.

        Returns:
            Task response with ``task_id`` for polling.
        """
        return self.post("/v1/videos/extend", json={
            "video_url": video_url,
            "prompt": prompt,
            "duration": duration,
        })

    # -- Task Management --

    def get_task_status(
        self, task_id: str, task_type: str = "text2video"
    ) -> dict[str, Any]:
        """Get the current status of a video generation task.

        Args:
            task_id: Unique task identifier from a generation request.
            task_type: The generation type used to create the task.
                Must match the original endpoint: "text2video",
                "image2video", "lip-sync", or "extend".

        Returns:
            Task data including status, progress, and result URLs.
        """
        return self.get(f"/v1/videos/{task_type}/{task_id}")

    def wait_for_completion(
        self,
        task_id: str,
        task_type: str = "text2video",
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Poll until a video generation task completes or fails.

        Args:
            task_id: Task identifier to poll.
            task_type: The generation type (text2video, image2video, etc.).
            poll_interval: Seconds between polls.
            max_attempts: Maximum poll attempts before timeout.
            timeout_seconds: Optional wall-clock timeout budget. If provided,
                polling stops when this budget is exceeded even if
                ``max_attempts`` has not been reached.

        Returns:
            Final task data including video URL(s).

        Raises:
            RuntimeError: If the task fails.
            TimeoutError: If the task doesn't complete within polling limits.
        """
        started_at = time.monotonic()

        for attempt in range(max_attempts):
            data = self.get_task_status(task_id, task_type=task_type)
            data_block = data.get("data", {}) if isinstance(data.get("data"), dict) else {}
            status = (
                data.get("status")
                or data_block.get("status")
                or data_block.get("task_status")
                or ""
            )
            status_normalized = str(status).lower()

            if status_normalized in ("completed", "complete", "done", "success", "succeed"):
                logger.info(
                    "Task %s completed after %d polls", task_id, attempt + 1,
                )
                return data
            if status_normalized in ("failed", "error"):
                error_msg = (
                    data.get("error_message")
                    or data_block.get("task_status_msg")
                    or "unknown error"
                )
                raise RuntimeError(
                    f"Task {task_id} failed: {error_msg}"
                )

            elapsed = time.monotonic() - started_at
            if timeout_seconds is not None and elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Task {task_id} did not complete within {timeout_seconds}s"
                )

            logger.debug(
                "Task %s status: %s (poll %d/%d)",
                task_id, status_normalized, attempt + 1, max_attempts,
            )
            time.sleep(poll_interval)

        timeout_window = max_attempts * poll_interval
        if timeout_seconds is not None:
            timeout_window = min(timeout_window, timeout_seconds)

        raise TimeoutError(
            f"Task {task_id} did not complete within {timeout_window}s"
        )

    # -- Download --

    def download_video(
        self,
        video_url: str,
        output_path: str | Path,
    ) -> Path:
        """Download a completed video from its CDN URL.

        Args:
            video_url: CDN URL of the generated video (expires ~7 days).
            output_path: Local path to save the MP4 file.

        Returns:
            Path to the downloaded file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = output_path.stat().st_size
        logger.info(
            "Downloaded video to %s (%d bytes)", output_path, file_size,
        )
        return output_path
