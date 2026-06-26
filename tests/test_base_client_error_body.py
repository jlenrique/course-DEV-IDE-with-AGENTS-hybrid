"""Unit tests for provider-error-body surfacing in BaseAPIClient.

The base client must include the provider's real response body (parsed
``{code, message, request_id}`` when present, else raw text) in the raised
exception message so billing/expiry signals are not masked as generic
throttle errors.

These tests construct real ``requests.Response`` objects to exercise OUR
status->exception mapping logic. No external API is contacted.
"""

from __future__ import annotations

import json

import requests

from scripts.api_clients.base_client import (
    APIError,
    BaseAPIClient,
    RateLimitError,
)


def _make_response(status_code: int, reason: str, body: object) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status_code
    resp.reason = reason
    resp.url = "https://api.example.com/v1/test"
    if isinstance(body, (dict, list)):
        resp._content = json.dumps(body).encode("utf-8")
        resp.headers["Content-Type"] = "application/json"
    else:
        resp._content = str(body).encode("utf-8")
    return resp


def _client() -> BaseAPIClient:
    return BaseAPIClient(
        base_url="https://api.example.com",
        api_key="k",
        max_retries=1,
        backoff_delays=(0,),
    )


def test_429_surfaces_real_provider_body(monkeypatch) -> None:
    """A 429 carrying Kling's real billing body must surface code + message in
    the RateLimitError, not just the generic throttle text."""
    client = _client()
    resp = _make_response(
        429,
        "Too Many Requests",
        {
            "code": 1102,
            "message": "Account balance not enough",
            "request_id": "x",
        },
    )

    monkeypatch.setattr(client.session, "request", lambda *a, **k: resp)

    raised: RateLimitError | None = None
    try:
        client.get("/test")
    except RateLimitError as exc:
        raised = exc

    assert raised is not None
    text = str(raised)
    assert "1102" in text
    assert "Account balance not enough" in text
    # Body preserved for programmatic access.
    assert raised.response_body == {
        "code": 1102,
        "message": "Account balance not enough",
        "request_id": "x",
    }


def test_400_surfaces_provider_message(monkeypatch) -> None:
    """A non-retryable 4xx with a JSON error body must include the provider
    message in the APIError."""
    client = _client()
    resp = _make_response(
        400,
        "Bad Request",
        {"code": 2000, "message": "Invalid parameter: duration"},
    )

    monkeypatch.setattr(client.session, "request", lambda *a, **k: resp)

    raised: APIError | None = None
    try:
        client.get("/test")
    except APIError as exc:
        raised = exc

    assert raised is not None
    assert raised.status_code == 400
    assert "Invalid parameter: duration" in str(raised)


def test_400_with_raw_text_body_included(monkeypatch) -> None:
    """When the body is not JSON, the raw text is surfaced (truncated)."""
    client = _client()
    resp = _make_response(400, "Bad Request", "upstream gateway exploded")

    monkeypatch.setattr(client.session, "request", lambda *a, **k: resp)

    raised: APIError | None = None
    try:
        client.get("/test")
    except APIError as exc:
        raised = exc

    assert raised is not None
    assert "upstream gateway exploded" in str(raised)
