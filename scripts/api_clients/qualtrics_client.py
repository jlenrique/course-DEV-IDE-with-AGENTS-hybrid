"""Qualtrics API client for survey and assessment management.

API Docs: https://api.qualtrics.com/
Auth: X-API-TOKEN header
Response structure: { "result": { ... }, "meta": { ... } }
"""

from __future__ import annotations

import logging
import os
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


def _resolve_base_url(explicit: str | None = None) -> str:
    """Resolve the Qualtrics API root from either a full base URL or a data center slug."""

    if explicit:
        return explicit.rstrip("/")

    base_url = os.environ.get("QUALTRICS_BASE_URL", "").strip()
    if base_url:
        return base_url.rstrip("/")

    data_center = os.environ.get("QUALTRICS_DATA_CENTER", "").strip()
    if data_center:
        return f"https://{data_center}.qualtrics.com"

    return ""


class QualtricsClient(BaseAPIClient):
    """Client for Qualtrics REST API v3.

    Args:
        api_token: Qualtrics API token.
            Defaults to ``QUALTRICS_API_TOKEN`` env var.
        base_url: Qualtrics data center URL.
            Defaults to ``QUALTRICS_BASE_URL`` env var.
    """

    def __init__(
        self,
        api_token: str | None = None,
        base_url: str | None = None,
    ) -> None:
        api_token = api_token or os.environ.get("QUALTRICS_API_TOKEN", "")
        base_url = _resolve_base_url(base_url)
        super().__init__(
            base_url=f"{base_url.rstrip('/')}/API/v3",
            auth_header="X-API-TOKEN",
            auth_prefix="",
            api_key=api_token,
        )

    def _result(self, data: dict[str, Any]) -> Any:
        """Extract the 'result' field from Qualtrics response envelope."""
        if isinstance(data, dict) and "result" in data:
            return data["result"]
        return data

    # -- User --

    def whoami(self) -> dict[str, Any]:
        """Get authenticated user info."""
        return self._result(self.get("/whoami"))

    # -- Surveys --

    def list_surveys(self, page_size: int = 100) -> list[dict[str, Any]]:
        """List surveys for the authenticated user."""
        data = self.get("/surveys", params={"pageSize": page_size})
        result = self._result(data)
        return result.get("elements", []) if isinstance(result, dict) else []

    def get_survey(self, survey_id: str) -> dict[str, Any]:
        """Get a survey by ID."""
        return self._result(self.get(f"/surveys/{survey_id}"))

    def create_survey(
        self,
        name: str,
        *,
        language: str = "EN",
        project_category: str = "CORE",
    ) -> dict[str, Any]:
        """Create a new survey.

        Args:
            name: Survey name.
            language: Primary language code.
            project_category: "CORE" for standard surveys.

        Returns:
            Created survey metadata including survey ID.
        """
        payload = {
            "SurveyName": name,
            "Language": language,
            "ProjectCategory": project_category,
        }
        return self._result(self.post("/survey-definitions", json=payload))

    def update_survey_options(
        self,
        survey_id: str,
        *,
        question_numbering: bool = True,
        progress_bar: bool = True,
    ) -> dict[str, Any]:
        """Best-effort survey option updates for common assessment defaults."""
        payload = {
            "SurveyOptions": {
                "QuestionNumbering": "ON" if question_numbering else "OFF",
                "ProgressBarDisplay": "Bar" if progress_bar else "None",
            }
        }
        return self._result(
            self.put(f"/survey-definitions/{survey_id}/options", json=payload)
        )

    # -- Questions --

    def list_questions(self, survey_id: str) -> list[dict[str, Any]]:
        """List questions in a survey."""
        data = self.get(
            f"/survey-definitions/{survey_id}/questions"
        )
        result = self._result(data)
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        if isinstance(result, list):
            return result
        return list(result.values()) if isinstance(result, dict) else []

    def create_question(
        self,
        survey_id: str,
        question_text: str,
        question_type: str = "MC",
        *,
        choices: dict[str, dict[str, str]] | None = None,
        selector: str = "SAVR",
    ) -> dict[str, Any]:
        """Add a question to a survey.

        Args:
            survey_id: Target survey ID.
            question_text: The question text/prompt.
            question_type: "MC" (multiple choice), "TE" (text entry), etc.
            choices: Choice map for MC questions.
            selector: Sub-type selector (e.g. "SAVR" for single answer).

        Returns:
            Created question metadata.
        """
        payload: dict[str, Any] = {
            "QuestionText": question_text,
            "QuestionType": question_type,
            "Selector": selector,
        }
        if choices:
            payload["Choices"] = choices
        return self._result(
            self.post(
                f"/survey-definitions/{survey_id}/questions",
                json=payload,
            )
        )

    # -- Distributions --

    def list_distributions(
        self, survey_id: str
    ) -> list[dict[str, Any]]:
        """List distributions for a survey."""
        data = self.get(
            "/distributions",
            params={"surveyId": survey_id},
        )
        result = self._result(data)
        return result.get("elements", []) if isinstance(result, dict) else []

    # -- Response export --

    def start_response_export(
        self,
        survey_id: str,
        file_format: str = "json",
    ) -> str:
        """Start an async response export.

        Returns:
            Progress ID for polling export status.
        """
        payload = {"format": file_format}
        result = self._result(
            self.post(
                f"/surveys/{survey_id}/export-responses",
                json=payload,
            )
        )
        return result.get("progressId", "")

    def get_export_progress(
        self, survey_id: str, progress_id: str
    ) -> dict[str, Any]:
        """Check export progress."""
        return self._result(
            self.get(
                f"/surveys/{survey_id}/export-responses/{progress_id}"
            )
        )


def reproduce_survey_snapshot(page_size: int = 5) -> dict[str, Any]:
    """Capture a read-only Qualtrics inventory snapshot for woodshed.

    This helper supports skills/woodshed/scripts/reproduce_exemplar.py by
    providing a deterministic module-level function for API reproduction.
    """
    client = QualtricsClient()

    if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size < 1:
        return {
            "status": "error",
            "reason": "page_size must be a positive integer",
            "user": None,
            "survey_count": 0,
            "sample_surveys": [],
        }

    try:
        user = client.whoami()
        surveys = client.list_surveys(page_size=page_size)
    except Exception as exc:  # pragma: no cover - defensive API failure path
        return {
            "status": "error",
            "reason": str(exc),
            "user": None,
            "survey_count": 0,
            "sample_surveys": [],
        }

    if not isinstance(user, dict):
        return {
            "status": "error",
            "reason": "Qualtrics whoami response was not an object",
            "user": None,
            "survey_count": 0,
            "sample_surveys": [],
        }

    normalized_surveys: list[dict[str, str]] = []
    for survey in surveys[: min(page_size, 5)]:
        if not isinstance(survey, dict):
            continue
        normalized_surveys.append(
            {
                "id": str(
                    survey.get("id")
                    or survey.get("SurveyID")
                    or ""
                ),
                "name": str(
                    survey.get("name")
                    or survey.get("SurveyName")
                    or ""
                ),
            }
        )

    return {
        "status": "ok",
        "user": {
            "id": user.get("userId") or user.get("id"),
            "name": user.get("userName") or user.get("name"),
        },
        "survey_count": len(surveys),
        "sample_surveys": normalized_surveys,
    }
