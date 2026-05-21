from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.orchestrator.html_review_pack import (
    BrowserOpenError,
    GateAdvanceBlockedError,
    ReviewPackRow,
    assert_gate_advance_allowed,
    open_review_pack,
    write_review_pack,
)


def _pack(tmp_path: Path) -> Path:
    return write_review_pack(
        trial_id="trial-1",
        gate_id="G2B",
        rows=[
            ReviewPackRow(
                slide_index=0,
                slide_label="Slide 1",
                preview="Selected variant A",
                output={"variant": "A"},
            )
        ],
        runs_root=tmp_path,
    )


def test_browser_open_invoked_and_log_entry_written(tmp_path: Path) -> None:
    opened: list[str] = []
    pack = _pack(tmp_path)

    open_review_pack(
        pack_path=pack,
        trial_id="trial-1",
        gate_id="G2B",
        opener=lambda url: opened.append(url) is None or True,
    )

    assert opened == [pack.resolve().as_uri()]
    assert "trial_id=trial-1 gate_id=G2B" in (pack.parent / "G2B-pack-open.log").read_text(
        encoding="utf-8"
    )


def test_gate_advance_refuses_without_open_log(tmp_path: Path) -> None:
    pack = _pack(tmp_path)

    with pytest.raises(GateAdvanceBlockedError):
        assert_gate_advance_allowed(pack_path=pack, gate_id="G2B")


def test_browser_open_failure_raises(tmp_path: Path) -> None:
    pack = _pack(tmp_path)

    with pytest.raises(BrowserOpenError):
        open_review_pack(
            pack_path=pack,
            trial_id="trial-1",
            gate_id="G2B",
            opener=lambda _url: False,
        )
