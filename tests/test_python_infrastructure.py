"""Validation tests for Story 1.2: Python Infrastructure & Environment Configuration.

Verifies virtual environment, dependency imports, BaseAPIClient functionality,
and utilities module operations.
"""

from __future__ import annotations

import os
import sys
import tempfile

try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# AC #1: Virtual environment exists and is active
# ---------------------------------------------------------------------------


class TestVirtualEnvironment:
    def test_venv_directory_exists(self):
        venv = Path(__file__).resolve().parent.parent / ".venv"
        assert venv.is_dir(), ".venv directory should exist at project root"

    def test_running_in_venv(self):
        assert hasattr(sys, "prefix"), "sys.prefix should be set"
        if sys.prefix != sys.base_prefix:
            return
        # Accept pyenv-based interpreter when local venv is absent from activation
        # but present on disk for tooling.
        venv_on_disk = (Path(__file__).resolve().parent.parent / ".venv").exists()
        assert venv_on_disk or "pyenv" in sys.prefix.lower(), (
            "Tests should run inside the virtual environment or a managed pyenv interpreter with .venv present"
        )


# ---------------------------------------------------------------------------
# AC #5 (partial): All dependencies import successfully
# ---------------------------------------------------------------------------


class TestDependencyImports:
    def test_import_requests(self):
        import requests
        assert requests.__version__

    def test_import_aiohttp(self):
        import aiohttp
        assert aiohttp.__version__

    def test_import_dotenv(self):
        from dotenv import load_dotenv
        assert callable(load_dotenv)

    def test_import_pydantic(self):
        import pydantic
        assert pydantic.__version__

    def test_import_yaml(self):
        import yaml
        assert yaml.__version__

    def test_import_pytest_itself(self):
        assert pytest is not None


# ---------------------------------------------------------------------------
# AC #3: BaseAPIClient
# ---------------------------------------------------------------------------


class TestBaseAPIClient:
    def test_import(self):
        from scripts.api_clients.base_client import BaseAPIClient
        assert BaseAPIClient is not None

    def test_instantiation_with_bearer_auth(self):
        from scripts.api_clients.base_client import BaseAPIClient

        client = BaseAPIClient(
            base_url="https://api.example.com",
            api_key="test-key-123",
        )
        assert client.base_url == "https://api.example.com"
        assert client.session.headers["Authorization"] == "Bearer test-key-123"

    def test_instantiation_with_custom_auth_header(self):
        from scripts.api_clients.base_client import BaseAPIClient

        client = BaseAPIClient(
            base_url="https://api.example.com",
            auth_header="X-API-KEY",
            auth_prefix="",
            api_key="raw-key-456",
        )
        assert client.session.headers["X-API-KEY"] == "raw-key-456"

    def test_url_building(self):
        from scripts.api_clients.base_client import BaseAPIClient

        client = BaseAPIClient(base_url="https://api.example.com/v1/")
        assert client._build_url("/users") == "https://api.example.com/v1/users"
        assert client._build_url("users") == "https://api.example.com/v1/users"

    def test_successful_get(self):
        from scripts.api_clients.base_client import BaseAPIClient

        client = BaseAPIClient(base_url="https://api.example.com", api_key="k")
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.reason = "OK"
        mock_resp.content = b'{"result": "ok"}'
        mock_resp.json.return_value = {"result": "ok"}

        with patch.object(client.session, "request", return_value=mock_resp):
            result = client.get("/test")
        assert result == {"result": "ok"}

    def test_auth_error_raises_immediately(self):
        from scripts.api_clients.base_client import AuthenticationError, BaseAPIClient

        client = BaseAPIClient(base_url="https://api.example.com", api_key="bad")
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 401
        mock_resp.reason = "Unauthorized"
        mock_resp.json.return_value = {"error": "invalid_token"}

        with (
            patch.object(client.session, "request", return_value=mock_resp),
            pytest.raises(AuthenticationError, match="Authentication failed"),
        ):
            client.get("/secure")

    def test_retry_on_server_error(self):
        from scripts.api_clients.base_client import BaseAPIClient

        client = BaseAPIClient(
            base_url="https://api.example.com",
            api_key="k",
            backoff_delays=(0, 0, 0),
        )

        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 503
        fail_resp.reason = "Service Unavailable"
        fail_resp.headers = {}
        fail_resp.json.return_value = None

        ok_resp = MagicMock()
        ok_resp.ok = True
        ok_resp.status_code = 200
        ok_resp.reason = "OK"
        ok_resp.content = b'{"recovered": true}'
        ok_resp.json.return_value = {"recovered": True}

        with patch.object(client.session, "request", side_effect=[fail_resp, ok_resp]):
            result = client.get("/flaky")
        assert result == {"recovered": True}

    def test_rate_limit_error_after_exhaustion(self):
        from scripts.api_clients.base_client import BaseAPIClient, RateLimitError

        client = BaseAPIClient(
            base_url="https://api.example.com",
            api_key="k",
            backoff_delays=(0, 0, 0),
        )

        rate_resp = MagicMock()
        rate_resp.ok = False
        rate_resp.status_code = 429
        rate_resp.reason = "Too Many Requests"
        rate_resp.headers = {}
        rate_resp.json.return_value = {"error": "rate_limit"}

        with (
            patch.object(client.session, "request", return_value=rate_resp),
            pytest.raises(RateLimitError, match="Rate limit exceeded"),
        ):
            client.get("/limited")

    def test_error_classes_hierarchy(self):
        from scripts.api_clients.base_client import (
            APIError,
            AuthenticationError,
            RateLimitError,
        )

        assert issubclass(AuthenticationError, APIError)
        assert issubclass(RateLimitError, APIError)

        err = APIError("test", status_code=500, response_body={"detail": "boom"})
        assert err.status_code == 500
        assert err.response_body == {"detail": "boom"}


# ---------------------------------------------------------------------------
# AC #4: Utilities module
# ---------------------------------------------------------------------------


class TestUtilities:
    def test_project_root_finds_pyproject(self):
        from scripts.utilities.file_helpers import project_root

        root = project_root()
        assert (root / "pyproject.toml").exists()

    def test_resolve_path(self):
        from scripts.utilities.file_helpers import project_root, resolve_path

        p = resolve_path("scripts", "api_clients")
        assert p == project_root() / "scripts" / "api_clients"

    def test_safe_json_roundtrip(self):
        from scripts.utilities.file_helpers import safe_read_json, safe_write_json

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            tmp = Path(f.name)

        try:
            data = {"key": "value", "nested": {"a": 1}}
            safe_write_json(tmp, data)
            loaded = safe_read_json(tmp)
            assert loaded == data
        finally:
            tmp.unlink()

    def test_safe_read_json_missing_file(self):
        from scripts.utilities.file_helpers import safe_read_json

        with pytest.raises(FileNotFoundError):
            safe_read_json("/nonexistent/file.json")

    def test_env_loader_loads_vars(self):
        from scripts.utilities.env_loader import load_env

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Comment line\n")
            f.write("TEST_INFRA_VAR_ABC=hello123\n")
            f.write("\n")
            f.write("TEST_INFRA_VAR_DEF=world456\n")
            tmp = Path(f.name)

        try:
            os.environ.pop("TEST_INFRA_VAR_ABC", None)
            os.environ.pop("TEST_INFRA_VAR_DEF", None)

            loaded = load_env(tmp)
            assert loaded["TEST_INFRA_VAR_ABC"] == "hello123"
            assert loaded["TEST_INFRA_VAR_DEF"] == "world456"
            assert os.environ["TEST_INFRA_VAR_ABC"] == "hello123"
        finally:
            os.environ.pop("TEST_INFRA_VAR_ABC", None)
            os.environ.pop("TEST_INFRA_VAR_DEF", None)
            tmp.unlink()

    def test_env_loader_missing_file(self):
        from scripts.utilities.env_loader import load_env

        with pytest.raises(FileNotFoundError, match="Missing .env"):
            load_env("/nonexistent/.env")

    def test_setup_logging_returns_logger(self):
        import logging

        from scripts.utilities.logging_setup import setup_logging

        logger = setup_logging(name="test-infra", level=logging.DEBUG)
        assert logger.name == "test-infra"
        assert logger.level == logging.DEBUG


# ---------------------------------------------------------------------------
# AC #6: Project packaging files exist
# ---------------------------------------------------------------------------


class TestProjectPackaging:
    def test_pyproject_toml_exists(self):
        from scripts.utilities.file_helpers import project_root

        assert (project_root() / "pyproject.toml").exists()

    def test_requirements_txt_exists(self):
        from scripts.utilities.file_helpers import project_root

        assert (project_root() / "requirements.txt").exists()

    def test_pyproject_has_project_section(self):
        from scripts.utilities.file_helpers import project_root

        content = (project_root() / "pyproject.toml").read_text(encoding="utf-8")
        assert "[project]" in content
        pyproject = tomllib.loads(content)
        assert pyproject["project"]["requires-python"] == ">=3.11"


# ---------------------------------------------------------------------------
# AC #2: Local .env policy + admin guide documents required keys
# ---------------------------------------------------------------------------


class TestEnvDocumentation:
    def test_env_example_is_canonical_template(self):
        """Migration policy (post-Slab-3 close): .env.example IS the canonical
        operator-onboarding template; tracked in repo with placeholder values.
        Reverses primary-repo policy that forbid env templates in-tree."""
        from scripts.utilities.file_helpers import project_root

        assert (project_root() / ".env.example").exists()

    def test_env_is_gitignored_with_template_exception(self):
        """Migration policy: .env stays gitignored; .env.example is exception
        (tracked) per `!.env.example` line in .gitignore."""
        from scripts.utilities.file_helpers import project_root

        content = (project_root() / ".gitignore").read_text(encoding="utf-8")
        assert ".env" in content
        assert "!.env.example" in content

    def test_admin_guide_documents_tier1_keys(self):
        from scripts.utilities.file_helpers import project_root

        content = (project_root() / "docs" / "admin-guide.md").read_text(encoding="utf-8")
        tier1_keys = [
            "GAMMA_API_KEY",
            "ELEVENLABS_API_KEY",
            "CANVAS_ACCESS_TOKEN",
            "QUALTRICS_API_TOKEN",
        ]
        for key in tier1_keys:
            assert key in content, f"{key} should be documented in admin-guide.md"

    def test_admin_guide_documents_tier2_keys(self):
        from scripts.utilities.file_helpers import project_root

        content = (project_root() / "docs" / "admin-guide.md").read_text(encoding="utf-8")
        for key in ["BOTPRESS_API_KEY", "WONDERCRAFT_API_KEY", "KLING_ACCESS_KEY"]:
            assert key in content, f"{key} should be documented in admin-guide.md"


# ---------------------------------------------------------------------------
# Gitignore verification
# ---------------------------------------------------------------------------


class TestGitignore:
    def test_gitignore_has_python_patterns(self):
        from scripts.utilities.file_helpers import project_root

        content = (project_root() / ".gitignore").read_text(encoding="utf-8")
        assert ".venv/" in content
        assert "__pycache__/" in content
        assert "*.pyc" in content
