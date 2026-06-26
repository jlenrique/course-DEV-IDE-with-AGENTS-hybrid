"""Unit tests for Kling client authentication mode selection.

Covers the two supported auth schemes:
  - Static ``KLING_API_TOKEN`` Bearer token (newer single-token auth).
  - Legacy JWT built from ``KLING_ACCESS_KEY`` + ``KLING_SECRET_KEY`` (HS256).

These tests do not call the live API.
"""

from __future__ import annotations

import jwt
import pytest

from scripts.api_clients import kling_client
from scripts.api_clients.kling_client import KlingClient


def test_static_api_token_used_directly_no_jwt_built(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When KLING_API_TOKEN is set, the Authorization header is the literal
    Bearer token and no JWT is generated."""
    jwt_calls: list[tuple[str, str]] = []

    def spy_generate(access_key: str, secret_key: str) -> str:
        jwt_calls.append((access_key, secret_key))
        return "SHOULD_NOT_BE_USED"

    monkeypatch.setattr(kling_client, "generate_jwt_token", spy_generate)

    client = KlingClient(
        access_key="ak", secret_key="sk", api_token="static-token-abc"
    )

    assert client.session.headers["Authorization"] == "Bearer static-token-abc"
    assert jwt_calls == []


def test_static_api_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KLING_API_TOKEN", "env-token-xyz")
    monkeypatch.delenv("KLING_ACCESS_KEY", raising=False)
    monkeypatch.delenv("KLING_SECRET_KEY", raising=False)

    def boom(access_key: str, secret_key: str) -> str:
        raise AssertionError("JWT must not be built when KLING_API_TOKEN is set")

    monkeypatch.setattr(kling_client, "generate_jwt_token", boom)

    client = KlingClient()

    assert client.session.headers["Authorization"] == "Bearer env-token-xyz"


def test_legacy_jwt_path_unchanged_when_token_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no KLING_API_TOKEN, the legacy AK/SK -> HS256 JWT path is used and
    the Authorization header carries a real Bearer JWT."""
    monkeypatch.delenv("KLING_API_TOKEN", raising=False)

    client = KlingClient(access_key="my-ak", secret_key="my-sk")

    header = client.session.headers["Authorization"]
    assert header.startswith("Bearer ")
    token = header.removeprefix("Bearer ")
    decoded = jwt.decode(token, "my-sk", algorithms=["HS256"])
    assert decoded["iss"] == "my-ak"


def test_refresh_is_noop_with_static_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_ensure_token returns the static token unchanged and never builds a JWT,
    even when called repeatedly (as the per-request refresh hook does)."""
    jwt_calls: list[tuple[str, str]] = []

    def spy_generate(access_key: str, secret_key: str) -> str:
        jwt_calls.append((access_key, secret_key))
        return "SHOULD_NOT_BE_USED"

    monkeypatch.setattr(kling_client, "generate_jwt_token", spy_generate)

    client = KlingClient(api_token="static-token-abc")

    assert client._ensure_token() == "static-token-abc"
    assert client._ensure_token() == "static-token-abc"
    assert client.session.headers["Authorization"] == "Bearer static-token-abc"
    assert jwt_calls == []
