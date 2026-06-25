"""Scite MCP OAuth bearer-token store + provider auth-style selection.

Closes the `braid-s3-live-research-credential-gate` mechanism: the Scite MCP
endpoint requires OAuth Bearer (no password grant), so `SciteProvider` must
prefer a persisted OAuth access token over HTTP-Basic. These are offline unit
tests (no live service) — the live AC-O1 dispatch is operator-gated.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from retrieval.scite_provider import SciteProvider
from retrieval import scite_oauth_token


def _write_token(path: Path, **overrides) -> None:
    record = {
        "access_token": "fresh-access-abc",
        "refresh_token": "refresh-xyz",
        "client_id": "oauth_test",
        "expires_at": int(time.time()) + 3600,
    }
    record.update(overrides)
    path.write_text(json.dumps(record), encoding="utf-8")


# ---- load_bearer_token -----------------------------------------------------


def test_no_token_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(tmp_path / "absent.json"))
    assert scite_oauth_token.load_bearer_token() is None


def test_malformed_token_file_returns_none(tmp_path, monkeypatch):
    p = tmp_path / "tok.json"
    p.write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(p))
    assert scite_oauth_token.load_bearer_token() is None


def test_fresh_token_returned_verbatim(tmp_path, monkeypatch):
    p = tmp_path / "tok.json"
    _write_token(p)
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(p))
    assert scite_oauth_token.load_bearer_token() == "fresh-access-abc"


def test_stale_token_refreshed_via_refresh_token(tmp_path, monkeypatch):
    p = tmp_path / "tok.json"
    _write_token(p, access_token="stale", expires_at=int(time.time()) - 10)
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(p))

    captured = {}

    class _Resp:
        status_code = 200

        def json(self):
            return {"access_token": "refreshed-new", "expires_in": 3600}

    def _fake_post(url, data=None, timeout=None):
        captured["grant_type"] = data.get("grant_type")
        captured["refresh_token"] = data.get("refresh_token")
        return _Resp()

    monkeypatch.setattr(scite_oauth_token.httpx, "post", _fake_post)
    token = scite_oauth_token.load_bearer_token()
    assert token == "refreshed-new"
    assert captured["grant_type"] == "refresh_token"
    assert captured["refresh_token"] == "refresh-xyz"
    # New access token persisted back to the file.
    assert json.loads(p.read_text(encoding="utf-8"))["access_token"] == "refreshed-new"


def test_stale_token_refresh_failure_returns_none(tmp_path, monkeypatch):
    p = tmp_path / "tok.json"
    _write_token(p, access_token="stale", expires_at=int(time.time()) - 10)
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(p))

    class _Resp:
        status_code = 401
        text = "nope"

    monkeypatch.setattr(scite_oauth_token.httpx, "post", lambda *a, **k: _Resp())
    assert scite_oauth_token.load_bearer_token() is None


# ---- SciteProvider auth-style selection ------------------------------------


def test_provider_uses_bearer_when_token_present(tmp_path, monkeypatch):
    p = tmp_path / "tok.json"
    _write_token(p)
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(p))

    provider = SciteProvider()
    client = provider._client()
    config = client._servers["scite"]
    assert config.auth_style == "bearer"
    assert config.auth_env == ["SCITE_MCP_BEARER"]
    import os

    assert os.environ.get("SCITE_MCP_BEARER") == "fresh-access-abc"


def test_provider_falls_back_to_basic_without_token(tmp_path, monkeypatch):
    monkeypatch.setenv("SCITE_OAUTH_TOKEN_PATH", str(tmp_path / "absent.json"))
    provider = SciteProvider()
    client = provider._client()
    config = client._servers["scite"]
    assert config.auth_style == "basic"
    assert config.auth_env == ["SCITE_USER_NAME", "SCITE_PASSWORD"]
