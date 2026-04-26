from __future__ import annotations

from typing import Any

import pytest

from app.specialists.wanda.wondercraft_dispatch import (
    CAPABILITY_CODES,
    WondercraftDispatchError,
    dispatch_to_wondercraft,
)


class _FakeClient:
    def create_podcast(
        self,
        *,
        title: str,
        prompt: str,
        voice_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "status": "success",
            "route": "EP",
            "title": title,
            "prompt": prompt,
            "voice_id": voice_id,
        }

    def create_conversation_podcast(self, *, title: str, script: str) -> dict[str, Any]:
        return {"status": "success", "route": "DP", "title": title, "script": script}

    def create_scripted_podcast(
        self,
        *,
        title: str,
        script: str,
        voice_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "status": "success",
            "route": "AS",
            "title": title,
            "script": script,
            "voice_id": voice_id,
        }

    def check_connectivity(self) -> dict[str, Any]:
        return {"reachable": True, "status_code": 200}


def test_wanda_capability_codes_contract() -> None:
    assert {"EP", "DP", "AS", "MB", "CM", "AH"} == CAPABILITY_CODES


def test_wanda_dispatch_rejects_unknown_capability() -> None:
    with pytest.raises(WondercraftDispatchError) as exc_info:
        dispatch_to_wondercraft(capability="ZZ", operation_payload={}, client=_FakeClient())
    assert exc_info.value.tag == "wanda_audio.parsed.missing-key"


def test_wanda_dispatch_ep_route() -> None:
    out = dispatch_to_wondercraft(
        capability="EP",
        operation_payload={"title": "T", "prompt": "P", "voice_id": "v1"},
        client=_FakeClient(),
    )
    assert out["capability"] == "EP"
    assert out["receipt"]["route"] == "EP"


def test_wanda_dispatch_dp_route() -> None:
    out = dispatch_to_wondercraft(
        capability="DP",
        operation_payload={"title": "T", "script": "dialogue"},
        client=_FakeClient(),
    )
    assert out["receipt"]["route"] == "DP"


def test_wanda_dispatch_cm_route() -> None:
    out = dispatch_to_wondercraft(
        capability="CM",
        operation_payload={"chapter_titles": ["Intro", "Body"]},
        client=_FakeClient(),
    )
    assert out["receipt"]["status"] == "success"
    assert len(out["receipt"]["chapter_markers"]) == 2
