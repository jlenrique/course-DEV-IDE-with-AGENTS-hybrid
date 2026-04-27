from __future__ import annotations

import json
import os
import subprocess
import sys

from app.marcus.cli.__main__ import main
from app.models.runtime import AdhocResponse, TokenCount


def test_adhoc_cli_subprocess_skips_cleanly_without_openai_key() -> None:
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = ""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.marcus.cli",
            "ask",
            "hello",
            "--json",
            "--no-trace",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "skipped"
    assert "OPENAI_API_KEY" in payload["reason"]


def test_adhoc_cli_json_output_shape(monkeypatch, capsys) -> None:
    class FakeFacade:
        def ask(self, *args, **kwargs) -> AdhocResponse:
            return AdhocResponse(
                text="I answer from the fake facade.",
                model_used="gpt-5-nano",
                tokens=TokenCount(input_tokens=4, output_tokens=6, total_tokens=10),
                cost_usd=0.0000026,
            )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr("app.marcus.cli.adhoc_cli.get_facade", lambda: FakeFacade())
    monkeypatch.setattr("app.marcus.cli.adhoc_cli._load_env_if_available", lambda: None)
    exit_code = main(
        [
            "ask",
            "hello",
            "--cascade-override",
            "marcus=gpt-5-nano",
            "--json",
            "--no-trace",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["transport_kind"] == "cli"
    assert payload["response"]["model_used"] == "gpt-5-nano"
    assert payload["response"]["tokens"]["total_tokens"] == 10
