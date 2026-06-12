from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.composers.section_02a import cli_adapter
from app.models.state.model_resolution_entry import ModelResolutionEntry


def _entry() -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level="registry_default",
        requested=None,
        resolved="gpt-5.4",
        reason="default model for marcus",
        timestamp=datetime(2026, 5, 22, 12, 0, tzinfo=UTC),
        cache_prefix_hash="0" * 64,
    )


def test_compose_and_write_persists_model_resolution_trail_sidecar(
    tmp_path: Path,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_id = uuid4()
    chat_stub = MagicMock(name="chat_stub")
    handle = SimpleNamespace(chat=chat_stub, entry=_entry())

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model",
        return_value=handle,
    ):
        mock_compose.return_value = SimpleNamespace(
            model_dump=lambda mode="json": {
                "run_id": str(run_id),
                "corpus_dir": corpus_dir.resolve().as_posix(),
                "sources": [],
                "composed_at": "2026-05-22T12:00:00+00:00",
            }
        )
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda _directive, path: path.write_text(
                "directive", encoding="utf-8"
            )
            cli_adapter.compose_and_write(
                corpus_dir=corpus_dir,
                run_dir=run_dir,
                run_id=run_id,
            )

    trail_path = run_dir / "model_resolution_trail.json"
    assert trail_path.exists()
    trail = json.loads(trail_path.read_text(encoding="utf-8"))
    assert trail == [
        {
            "cache_prefix_hash": "0" * 64,
            "level": "registry_default",
            "reason": "default model for marcus",
            "requested": None,
            "resolved": "gpt-5.4",
            "timestamp": "2026-05-22T12:00:00Z",
        }
    ]
