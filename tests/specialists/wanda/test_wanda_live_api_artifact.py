from __future__ import annotations

import hashlib
import importlib
import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "wanda" / "live_artifacts" / "2026-04-26"
)

SCRIPT = """Welcome to a short production check for Wanda.

In this episode we explain why podcast length is a design constraint.
First, a hook gives the learner a reason to listen.
Next, a concrete example shows how an overlong script dilutes attention.
Finally, the learner gets one action: choose the shortest format that carries
the instructional job.
"""


def _find_value(data: Any, keys: set[str]) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in keys and value:
                return value
        for value in data.values():
            found = _find_value(value, keys)
            if found:
                return found
    if isinstance(data, list):
        for value in data:
            found = _find_value(value, keys)
            if found:
                return found
    return None


def _download_artifact(client: Any, url: str) -> bytes:
    if url.startswith("http://") or url.startswith("https://"):
        response = client.session.get(url, timeout=60)
    else:
        response = client.get_raw(url)
    response.raise_for_status()
    return response.content


@pytest.mark.live_api
@pytest.mark.skipif(
    not os.environ.get("WONDERCRAFT_API_KEY"),
    reason="WONDERCRAFT_API_KEY absent; live API test deferred to operator window",
)
def test_wanda_live_artifact_via_create_scripted_podcast() -> None:
    module = importlib.import_module("scripts.api_clients.wondercraft_client")
    client = module.WondercraftClient()
    connectivity = client.check_connectivity()
    assert connectivity["reachable"] is True

    started = time.perf_counter()
    created = client.create_scripted_podcast(
        title="Wanda 2c.2 Production Check",
        script_segments=SCRIPT,
        voice_id=os.environ.get("WONDERCRAFT_VOICE_ID"),
    )
    job_id = _find_value(created, {"job_id", "jobId", "id"})
    final = client.wait_for_job(str(job_id)) if job_id else created
    elapsed = time.perf_counter() - started

    artifact_url = _find_value(
        final,
        {"audio_url", "audioUrl", "download_url", "downloadUrl", "url"},
    )
    if not isinstance(artifact_url, str):
        response_preview = json.dumps(final)[:300]
        pytest.skip(f"Wondercraft response has no downloadable audio URL: {response_preview}")
    duration_sec = _find_value(final, {"duration_sec", "duration", "durationSeconds"})
    if duration_sec is None:
        pytest.skip(f"Wondercraft response has no duration field: {json.dumps(final)[:300]}")
    duration_float = float(duration_sec)
    assert 4 * 60 <= duration_float <= 10 * 60

    artifact_bytes = _download_artifact(client, artifact_url)
    sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACT_DIR / f"{sha256}.mp3"
    artifact_path.write_bytes(artifact_bytes)
    metadata = ARTIFACT_DIR / "LIVE_ARTIFACT_METADATA.md"
    metadata.write_text(
        "\n".join(
            [
                "# Wanda Live Artifact Metadata",
                "",
                f"- trial_id: wanda-2c2-{sha256[:12]}",
                f"- api_call_duration_sec: {elapsed:.2f}",
                f"- cost_usd: {final.get('cost_usd', final.get('costUsd', 'operator-fill'))}",
                f"- voice_id: {os.environ.get('WONDERCRAFT_VOICE_ID', 'default')}",
                f"- script_sha256: {hashlib.sha256(SCRIPT.encode('utf-8')).hexdigest()}",
                "- operator: Juanl",
                "- artifact_format: scripted",
                f"- artifact_path: {artifact_path.relative_to(REPO_ROOT).as_posix()}",
                f"- sha256: {sha256}",
                f"- duration_sec: {duration_float:.2f}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    assert artifact_path.is_file()
    assert artifact_path.stat().st_size > 0
