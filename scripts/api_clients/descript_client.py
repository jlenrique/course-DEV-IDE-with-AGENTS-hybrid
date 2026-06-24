"""Descript Public API client (Early Access).

API:  https://descriptapi.com/v1
Auth: ``Authorization: Bearer <token>`` — token is Drive-scoped.
Docs: https://docs.descriptapi.com/ (cached: skills/bmad-agent-desmond/references/cache/)

Covers the project build lifecycle:
  import media (URL or direct upload) -> poll job -> Underlord agent edit ->
  publish/export. Direct uploads PUT bytes to signed URLs returned by import.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

from scripts.api_clients.base_client import APIError, BaseAPIClient

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://descriptapi.com/v1"
POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 240  # imports/agent edits can run several minutes

# MIME types for the media we import (slides + narration).
CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".vtt": "text/vtt",
}


def content_type_for(path: Path) -> str:
    """Return the MIME type for a media file by extension."""
    return CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")


class DescriptClient(BaseAPIClient):
    """Client for the Descript Public API.

    Args:
        api_key: Bearer token. Defaults to ``DESCRIPT_API_KEY`` env var.
        base_url: API base URL. Defaults to ``DESCRIPT_BASE_URL`` or
            ``https://descriptapi.com/v1``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        api_key = api_key or os.environ.get("DESCRIPT_API_KEY", "")
        resolved_base = (
            base_url or os.environ.get("DESCRIPT_BASE_URL", DEFAULT_BASE_URL)
        ).rstrip("/")
        super().__init__(
            base_url=resolved_base,
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=api_key,
        )

    # -- Read / connectivity --

    def status(self) -> dict[str, Any]:
        """Validate token + connectivity. Returns ``{drive_id, api_version}``."""
        return self.get("/status")

    def list_projects(self, limit: int = 20, **params: Any) -> list[dict[str, Any]]:
        """List projects in the token's drive."""
        data = self.get("/projects", params={"limit": limit, **params})
        return data.get("data", []) if isinstance(data, dict) else []

    def get_project(self, project_id: str) -> dict[str, Any]:
        """Get project details (media_files + compositions)."""
        return self.get(f"/projects/{project_id}")

    # -- Jobs --

    def get_job(self, job_id: str) -> dict[str, Any]:
        """Get the status of a job."""
        return self.get(f"/jobs/{job_id}")

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
        on_progress: Any = None,
    ) -> dict[str, Any]:
        """Poll a job until ``job_state == 'stopped'`` or failure.

        Raises ``APIError`` if the job stops with a non-success ``result.status``.
        Raises ``TimeoutError`` if it never stops within the attempt budget.
        """
        for attempt in range(max_attempts):
            data = self.get_job(job_id)
            state = data.get("job_state")
            if callable(on_progress):
                on_progress(attempt, data)
            if state == "stopped":
                result = data.get("result") or {}
                status = result.get("status")
                if status and status not in {"success", "partial_success"}:
                    raise APIError(
                        f"Descript job {job_id} stopped with status={status!r}: "
                        f"{result}",
                        status_code=None,
                        response_body=data,
                    )
                logger.info("Job %s stopped after %d polls", job_id, attempt + 1)
                return data
            time.sleep(poll_interval)
        raise TimeoutError(
            f"Descript job {job_id} did not stop within "
            f"{max_attempts * poll_interval}s"
        )

    # -- Import + direct upload --

    def import_media(
        self,
        add_media: dict[str, Any],
        *,
        project_id: str | None = None,
        project_name: str | None = None,
        add_compositions: list[dict[str, Any]] | None = None,
        folder_name: str | None = None,
        team_access: str | None = None,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """POST /jobs/import/project_media.

        Returns ``{job_id, project_id, project_url, drive_id, upload_urls?}``.
        Provide ``project_name`` for a new project or ``project_id`` for an
        existing one (mutually exclusive).
        """
        payload: dict[str, Any] = {"add_media": add_media}
        if project_id:
            payload["project_id"] = project_id
        if project_name:
            payload["project_name"] = project_name
        if add_compositions:
            payload["add_compositions"] = add_compositions
        if folder_name:
            payload["folder_name"] = folder_name
        if team_access:
            payload["team_access"] = team_access
        if callback_url:
            payload["callback_url"] = callback_url
        return self.post("/jobs/import/project_media", json=payload)

    @staticmethod
    def upload_to_signed_url(
        upload_url: str,
        file_path: Path,
        *,
        content_type: str = "application/octet-stream",
        timeout: int = 600,
    ) -> int:
        """PUT raw file bytes to a signed upload URL. Returns status code."""
        with open(file_path, "rb") as fh:
            resp = requests.put(
                upload_url,
                data=fh,
                headers={"Content-Type": content_type},
                timeout=timeout,
            )
        if not resp.ok:
            raise APIError(
                f"Upload to signed URL failed: {resp.status_code} {resp.reason} "
                f"for {file_path.name}",
                status_code=resp.status_code,
                response_body=resp.text[:500],
            )
        return resp.status_code

    # -- Agent (Underlord) + publish --

    def agent_edit(
        self,
        prompt: str,
        *,
        project_id: str | None = None,
        project_name: str | None = None,
        composition_id: str | None = None,
        model: str | None = None,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """POST /jobs/agent — Underlord create/edit. Returns job descriptor."""
        payload: dict[str, Any] = {"prompt": prompt}
        if project_id:
            payload["project_id"] = project_id
        if project_name:
            payload["project_name"] = project_name
        if composition_id:
            payload["composition_id"] = composition_id
        if model:
            payload["model"] = model
        if callback_url:
            payload["callback_url"] = callback_url
        return self.post("/jobs/agent", json=payload)

    def publish(
        self,
        project_id: str,
        *,
        composition_id: str | None = None,
        media_type: str = "Video",
        resolution: str | None = None,
        access_level: str | None = None,
    ) -> dict[str, Any]:
        """POST /jobs/publish — render + publish a composition. Returns job."""
        payload: dict[str, Any] = {
            "project_id": project_id,
            "media_type": media_type,
        }
        if composition_id:
            payload["composition_id"] = composition_id
        if resolution:
            payload["resolution"] = resolution
        if access_level:
            payload["access_level"] = access_level
        return self.post("/jobs/publish", json=payload)
