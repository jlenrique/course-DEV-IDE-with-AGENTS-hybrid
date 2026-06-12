"""Gamma API client for AI slide generation.

API Docs: https://developers.gamma.app
Auth: X-API-KEY header
Rate Limit: 50 generations/hour (beta)
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)

GAMMA_BASE_URL = "https://public-api.gamma.app/v1.0"
POLL_INTERVAL = 3
MAX_POLL_ATTEMPTS = 120


class GammaClient(BaseAPIClient):
    """Client for Gamma slide generation API.

    Args:
        api_key: Gamma API key. Defaults to ``GAMMA_API_KEY`` env var.
    """

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("GAMMA_API_KEY", "")
        super().__init__(
            base_url=GAMMA_BASE_URL,
            auth_header="X-API-KEY",
            auth_prefix="",
            api_key=api_key,
            default_headers={"Content-Type": "application/json"},
        )

    def list_themes(self, limit: int = 20) -> list[dict[str, Any]]:
        """List available presentation themes."""
        data = self.get("/themes", params={"limit": limit})
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data.get("themes", [data])

    def generate(
        self,
        input_text: str,
        text_mode: str = "generate",
        *,
        format: str = "presentation",
        num_cards: int | None = None,
        card_split: str | None = None,
        theme_id: str | None = None,
        additional_instructions: str | None = None,
        text_options: dict[str, Any] | None = None,
        image_options: dict[str, Any] | None = None,
        card_options: dict[str, Any] | None = None,
        sharing_options: dict[str, Any] | None = None,
        export_as: str | None = None,
        folder_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Start a text-based AI content generation.

        Args:
            input_text: Content for generation (required). Up to ~100k tokens.
            text_mode: How input is modified: "generate", "condense", or
                "preserve" (required).
            format: Output format: "presentation", "document", "social",
                or "webpage".
            num_cards: Number of cards (1-60 Pro/Teams, 1-75 Ultra).
            card_split: "auto" (use numCards) or "inputTextBreaks"
                (split on ``\\n---\\n``).
            theme_id: Theme ID from ``list_themes()``.
            additional_instructions: Free-text guidance (1-5000 chars).
            text_options: ``{"amount", "tone", "audience", "language"}``.
            image_options: ``{"source", "model", "style"}``.
            card_options: ``{"dimensions", "headerFooter"}``.
            sharing_options: ``{"workspaceAccess", "externalAccess",
                "emailOptions"}``.
            export_as: "pdf", "pptx", or "png". One per request.
            folder_ids: Folder IDs for organizing output.

        Returns:
            Generation response with ``id`` for polling status.
        """
        payload: dict[str, Any] = {
            "inputText": input_text,
            "textMode": text_mode,
            "format": format,
        }
        if num_cards is not None:
            payload["numCards"] = num_cards
        if card_split:
            payload["cardSplit"] = card_split
        if theme_id:
            payload["themeId"] = theme_id
        if additional_instructions:
            payload["additionalInstructions"] = additional_instructions
        if text_options:
            payload["textOptions"] = text_options
        if image_options:
            payload["imageOptions"] = image_options
        if card_options:
            payload["cardOptions"] = card_options
        if sharing_options:
            payload["sharingOptions"] = sharing_options
        if export_as:
            payload["exportAs"] = export_as
        if folder_ids:
            payload["folderIds"] = folder_ids

        return self.post("/generations", json=payload)

    def generate_deck(
        self,
        input_text: str,
        *,
        text_mode: str = "generate",
        num_cards: int | None = None,
        theme_id: str | None = None,
        additional_instructions: str | None = None,
        export_as: str | None = "png",
        wait: bool = True,
        **options: Any,
    ) -> dict[str, Any]:
        """Generate a presentation deck and optionally wait for completion."""
        response = self.generate(
            input_text,
            text_mode=text_mode,
            num_cards=num_cards,
            theme_id=theme_id,
            additional_instructions=additional_instructions,
            export_as=export_as,
            **options,
        )
        # Gamma's POST /generations ack uses camelCase generationId (Trial-3
        # cycle-2 root cause 2026-06-12: the snake/bare keys missed it, so
        # generate_deck never polled and returned the bare ack — no
        # exportUrl, orphaned server-side generation).
        generation_id = (
            response.get("id")
            or response.get("generation_id")
            or response.get("generationId")
        )
        if wait and isinstance(generation_id, str) and generation_id:
            completed = self.wait_for_generation(generation_id)
            completed.setdefault("generation_id", generation_id)
            return completed
        if isinstance(generation_id, str) and generation_id:
            response.setdefault("generation_id", generation_id)
        return response

    def generate_from_template(
        self,
        gamma_id: str,
        prompt: str,
        *,
        theme_id: str | None = None,
        export_as: str | None = None,
        folder_ids: list[str] | None = None,
        image_options: dict[str, Any] | None = None,
        sharing_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Start a template-based generation.

        Args:
            gamma_id: ID of the template gamma (must be single-page).
            prompt: Content and instructions for the template.
            theme_id: Override theme.
            export_as: "pdf", "pptx", or "png".
            folder_ids: Folder IDs for organizing output.
            image_options: Override image settings.
            sharing_options: Sharing configuration.

        Returns:
            Generation response with ``id`` for polling status.
        """
        payload: dict[str, Any] = {
            "gammaId": gamma_id,
            "prompt": prompt,
        }
        if theme_id:
            payload["themeId"] = theme_id
        if export_as:
            payload["exportAs"] = export_as
        if folder_ids:
            payload["folderIds"] = folder_ids
        if image_options:
            payload["imageOptions"] = image_options
        if sharing_options:
            payload["sharingOptions"] = sharing_options

        return self.post("/generations/from-template", json=payload)

    def get_generation(self, generation_id: str) -> dict[str, Any]:
        """Get the current status of a generation."""
        return self.get(f"/generations/{generation_id}")

    def wait_for_generation(
        self,
        generation_id: str,
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
    ) -> dict[str, Any]:
        """Poll until a generation completes or fails.

        Returns:
            Final generation data including output URLs.

        Raises:
            TimeoutError: If generation doesn't complete within max_attempts.
        """
        for attempt in range(max_attempts):
            data = self.get_generation(generation_id)
            status = data.get("status", "")

            if status in ("completed", "complete", "done"):
                logger.info(
                    "Generation %s completed after %d polls",
                    generation_id, attempt + 1,
                )
                return data
            if status in ("failed", "error"):
                raise RuntimeError(
                    f"Generation {generation_id} failed: "
                    f"{data.get('error', 'unknown')}"
                )

            logger.debug(
                "Generation %s status: %s (poll %d/%d)",
                generation_id, status, attempt + 1, max_attempts,
            )
            time.sleep(poll_interval)

        raise TimeoutError(
            f"Generation {generation_id} did not complete "
            f"within {max_attempts * poll_interval}s"
        )
