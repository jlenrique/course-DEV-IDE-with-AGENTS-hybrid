"""Trial-3 cycle-2 root-cause pins (2026-06-12, caught at the G2C pause).

Chain: Gamma's POST /generations ack uses camelCase ``generationId``;
``generate_deck`` read only snake/bare keys, so it never polled, returned
the bare ack (no exportUrl), and ORPHANED a real server-side generation.
Gary's act then masked the bare ack with a ``fixture-{variant}`` sentinel
(the eighth silent seam) and emitted seven slide rows with empty
file_path — quality theater that flowed through Vera and Quinn-R to G2C.

Three pins: the camelCase ack polls; the sentinel is dead (no id raises,
recoverable family); all-empty file_path raises (recoverable family).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists.gary import _act as gary_act
from app.specialists.gary.gamma_dispatch import GammaDispatchError

# NOTE: the companion camelCase generate_deck pin lives at
# tests/unit/api_clients/test_gamma_client_generation_id.py — the gary test
# tree may not import live API client modules (no-live-api-in-ci policy).


class _BareAckClient:
    def list_themes(self, limit: int = 20):
        return [{"id": "theme-1", "name": "T"}]

    def generate_deck(self, input_text: str, **kwargs):
        return {"credits": {"deducted": 8}}  # ack with no id under any casing


def test_missing_generation_id_raises_recoverable_not_sentinel(tmp_path: Path) -> None:
    with pytest.raises(GammaDispatchError) as excinfo:
        gary_act.generate_gamma_variants(
            {"slides": [{"prompt": "A"}], "export_dir": str(tmp_path)},
            client=_BareAckClient(),
        )
    assert excinfo.value.tag == "gamma.generation.id-missing"


class _NoArtifactClient:
    def list_themes(self, limit: int = 20):
        return [{"id": "theme-1", "name": "T"}]

    def generate_deck(self, input_text: str, **kwargs):
        # Valid id, but nothing materializable: no exported paths, no
        # downloaded path, no exportUrl, no slide rows.
        return {"generation_id": "gen-real-1", "status": "completed"}


def test_all_empty_file_paths_raise_recoverable(tmp_path: Path) -> None:
    with pytest.raises(GammaDispatchError) as excinfo:
        gary_act.generate_gamma_variants(
            {"slides": [{"prompt": "A"}, {"prompt": "B"}], "export_dir": str(tmp_path)},
            client=_NoArtifactClient(),
        )
    assert excinfo.value.tag == "gamma.export.unmaterialized"


def test_fixture_sentinel_is_gone_from_act_source() -> None:
    import inspect

    source = inspect.getsource(gary_act)
    assert 'f"fixture-{' not in source, "the eighth seam is back"
