"""Base API client with session management, retry logic, and error handling.

All tool-specific clients (Gamma, ElevenLabs, Canvas, etc.) extend this base
to inherit authenticated sessions, exponential backoff retry, and structured
error diagnostics.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from typing import Any

import requests

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
DEFAULT_BACKOFF_DELAYS = (2, 4, 8)
ERROR_BODY_MAX_CHARS = 500


class APIError(Exception):
    """Structured API error with status code and diagnostic context."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(APIError):
    """Raised on 401/403 responses indicating credential issues."""


class RateLimitError(APIError):
    """Raised on 429 responses after retry exhaustion."""


class BaseAPIClient:
    """Base API client with session management, retry logic, and error handling.

    Supports multiple auth patterns across tools:
      - ``Authorization: Bearer {key}`` (Canvas, Botpress)
      - ``X-API-KEY: {key}`` (Gamma, Wondercraft)
      - ``xi-api-key: {key}`` (ElevenLabs)
      - ``X-API-TOKEN: {key}`` (Qualtrics)

    Args:
        base_url: API base URL (no trailing slash).
        auth_header: Header name for authentication.
        auth_prefix: Value prefix (e.g. "Bearer"). Empty string for raw key.
        api_key: The API key or token value.
        timeout: Default request timeout in seconds.
        max_retries: Maximum retry attempts for retryable failures.
        backoff_delays: Tuple of delay seconds between retries.
        default_headers: Extra headers applied to every request.
    """

    def __init__(
        self,
        base_url: str,
        auth_header: str = "Authorization",
        auth_prefix: str = "Bearer",
        api_key: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_delays: tuple[int, ...] = DEFAULT_BACKOFF_DELAYS,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_delays = backoff_delays

        self.session = requests.Session()
        if api_key:
            auth_value = f"{auth_prefix} {api_key}" if auth_prefix else api_key
            self.session.headers[auth_header] = auth_value
        if default_headers:
            self.session.headers.update(default_headers)

    # -- Public HTTP methods --

    def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send GET request, return parsed JSON."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send POST request, return parsed JSON."""
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send PUT request, return parsed JSON."""
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send PATCH request, return parsed JSON."""
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send DELETE request, return parsed JSON."""
        return self._request("DELETE", endpoint, **kwargs)

    def get_raw(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Send GET and return the raw Response (for binary content like audio)."""
        return self._request_raw("GET", endpoint, **kwargs)

    def post_raw(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Send POST and return the raw Response (for binary content)."""
        return self._request_raw("POST", endpoint, **kwargs)

    def get_paginated(
        self,
        endpoint: str,
        results_key: str | None = None,
        max_pages: int = 50,
        **kwargs: Any,
    ) -> Iterator[dict[str, Any]]:
        """Iterate through paginated GET responses.

        Supports two pagination styles:
        - **Link-header** (Canvas): follows ``rel="next"`` in Link header
        - **Offset/cursor**: subclasses override ``_next_page_params()``

        Args:
            endpoint: Starting endpoint.
            results_key: If set, yields items from this key in each page.
            max_pages: Safety limit to prevent infinite pagination.
            **kwargs: Passed to each request.

        Yields:
            Individual items if ``results_key`` is set, otherwise full pages.
        """
        url = self._build_url(endpoint)
        kwargs.setdefault("timeout", self.timeout)

        for _ in range(max_pages):
            response = self.session.get(url, **kwargs)
            self._check_response(response)
            data = response.json()

            if results_key and isinstance(data, dict):
                items = data.get(results_key, [])
            elif isinstance(data, list):
                items = data
            else:
                yield data
                items = None

            if items is not None:
                yield from items
                if not items:
                    return

            next_url = self._extract_next_link(response)
            if not next_url:
                return
            url = next_url

    # -- URL building --

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base and endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    # -- Core request engine --

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Execute HTTP request with retry logic and error handling."""
        response = self._request_raw(method, endpoint, **kwargs)
        return self._parse_response(response)

    def _request_raw(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> requests.Response:
        """Execute HTTP request with retry, return raw Response."""
        url = self._build_url(endpoint)
        kwargs.setdefault("timeout", self.timeout)

        last_exception: Exception | None = None
        last_error_detail: str = ""

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    "%s %s (attempt %d/%d)",
                    method, url, attempt + 1, self.max_retries,
                )
                response = self.session.request(method, url, **kwargs)
                logger.debug(
                    "Response: %d %s (%d bytes)",
                    response.status_code,
                    response.reason,
                    len(response.content),
                )

                if response.ok:
                    return response

                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed: {response.status_code} "
                        f"{response.reason}. "
                        "Check your API key/token in .env.",
                        status_code=response.status_code,
                        response_body=self._safe_json(response),
                    )

                body = self._safe_json(response)
                detail = self._format_error_body(body, response)

                if response.status_code in RETRYABLE_STATUS_CODES:
                    delay = self._get_retry_delay(attempt, response)
                    last_error_detail = detail
                    logger.warning(
                        "%s %s returned %d%s — retrying in %ds "
                        "(attempt %d/%d)",
                        method, url, response.status_code,
                        f" ({detail})" if detail else "",
                        delay, attempt + 1, self.max_retries,
                    )
                    last_exception = APIError(
                        self._compose_error_message(response, detail),
                        status_code=response.status_code,
                        response_body=body,
                    )
                    time.sleep(delay)
                    continue

                message = self._compose_error_message(response, detail)
                logger.error("%s %s failed: %s", method, url, message)
                raise APIError(
                    message,
                    status_code=response.status_code,
                    response_body=body,
                )

            except requests.ConnectionError as exc:
                last_exception = APIError(
                    f"Connection error for {url}: {exc}. "
                    "Check network and service availability."
                )
                if attempt < self.max_retries - 1:
                    delay = self.backoff_delays[
                        min(attempt, len(self.backoff_delays) - 1)
                    ]
                    logger.warning(
                        "Connection failed — retrying in %ds", delay
                    )
                    time.sleep(delay)
                    continue

            except requests.Timeout as exc:
                last_exception = APIError(
                    f"Request timed out after {self.timeout}s "
                    f"for {url}: {exc}"
                )
                if attempt < self.max_retries - 1:
                    delay = self.backoff_delays[
                        min(attempt, len(self.backoff_delays) - 1)
                    ]
                    logger.warning("Timeout — retrying in %ds", delay)
                    time.sleep(delay)
                    continue

        is_rate_limited = (
            last_exception
            and isinstance(last_exception, APIError)
            and last_exception.status_code == 429
        )
        if is_rate_limited:
            message = (
                f"Rate limit exceeded for {url} after "
                f"{self.max_retries} attempts. "
                "Wait before retrying or check your plan's rate limits."
            )
            if last_error_detail:
                message += f" Provider response: {last_error_detail}"
            logger.error(message)
            raise RateLimitError(
                message,
                status_code=429,
                response_body=last_exception.response_body,
            )

        raise last_exception or APIError(
            f"Request failed after {self.max_retries} attempts"
        )

    def _check_response(self, response: requests.Response) -> None:
        """Raise structured errors for non-OK responses (used by pagination)."""
        if response.ok:
            return
        if response.status_code in (401, 403):
            raise AuthenticationError(
                f"Authentication failed: {response.status_code}",
                status_code=response.status_code,
            )
        raise APIError(
            f"HTTP {response.status_code}: {response.reason}",
            status_code=response.status_code,
            response_body=self._safe_json(response),
        )

    # -- Pagination helpers --

    @staticmethod
    def _extract_next_link(response: requests.Response) -> str | None:
        """Extract next page URL from Link header (Canvas-style pagination)."""
        link_header = response.headers.get("Link", "")
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
                return url
        return None

    # -- Response parsing --

    def _get_retry_delay(
        self, attempt: int, response: requests.Response
    ) -> int:
        """Determine retry delay, respecting Retry-After header."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return self.backoff_delays[
            min(attempt, len(self.backoff_delays) - 1)
        ]

    def _parse_response(
        self, response: requests.Response
    ) -> dict[str, Any]:
        """Parse response body as JSON."""
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            logger.debug(
                "Non-JSON response body (%d bytes)", len(response.content)
            )
            return {"_raw": response.text}

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        """Attempt to parse response as JSON for error diagnostics."""
        try:
            return response.json()
        except (ValueError, RuntimeError):
            return None

    @staticmethod
    def _format_error_body(body: Any, response: requests.Response) -> str:
        """Build a short, human-readable detail string from a provider's error
        response body.

        Prefers the conventional ``{code, message, request_id}`` JSON shape
        (so signals like Kling's ``{"code":1102,"message":"Account balance not
        enough"}`` survive instead of being masked as a generic throttle).
        Falls back to a compact JSON dump for other dicts, then to raw text.
        Truncated to ``ERROR_BODY_MAX_CHARS``.
        """
        detail = ""
        if isinstance(body, dict):
            parts = [
                f"{field}={body[field]}"
                for field in ("code", "message", "request_id")
                if body.get(field) not in (None, "")
            ]
            if parts:
                detail = " | ".join(parts)
            else:
                try:
                    detail = json.dumps(body, default=str)
                except (TypeError, ValueError):
                    detail = str(body)
        elif body is not None:
            detail = str(body)
        else:
            raw_text = getattr(response, "text", "")
            detail = raw_text if isinstance(raw_text, str) else ""

        detail = detail.strip()
        if len(detail) > ERROR_BODY_MAX_CHARS:
            detail = detail[:ERROR_BODY_MAX_CHARS] + "…"
        return detail

    @staticmethod
    def _compose_error_message(response: requests.Response, detail: str) -> str:
        """Compose an HTTP error message, appending the provider detail."""
        message = f"HTTP {response.status_code}: {response.reason}"
        if detail:
            message += f" — {detail}"
        return message
