"""T2: batch output row → VisionProviderResponse via shared _parse_response."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision import _act
from app.specialists.vision.batch_route import (
    extract_assistant_text,
    run_vision_batch_perception,
)
from app.specialists.vision.payload_contract import VisionProviderResponse
from app.specialists.vision.provider import VisionProviderError, _parse_response


def _png(tmp_path: Path, name: str = "s.png") -> Path:
    path = tmp_path / name
    path.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    return path


def _valid_content(slide_id: str) -> str:
    return json.dumps(
        {
            "slide_id": slide_id,
            "confidence": "HIGH",
            "coverage": "perceived",
            "confidence_score": 0.9,
            "slide_title": "T",
            "extracted_text": "hello",
            "layout_description": "layout",
            "text_blocks": ["hello"],
            "visual_elements": [],
        }
    )


def test_extract_and_parse_shared_path() -> None:
    content = _valid_content("slide-01")
    raw = {
        "custom_id": "run:slide-01",
        "response": {
            "status_code": 200,
            "body": {"choices": [{"message": {"content": content}}]},
        },
    }
    text = extract_assistant_text(raw, custom_id="run:slide-01")
    parsed = _parse_response(
        text,
        slide_id="slide-01",
        model_id="gpt-5.5",
        source_png_path="/tmp/x.png",
    )
    assert parsed.slide_id == "slide-01"
    assert parsed.provider_model_id == "gpt-5.5"


def test_malformed_batch_row_fail_loud_per_custom_id(tmp_path: Path) -> None:
    from app.runtime.llm_batch.receipts import BatchReceipt, write_receipt

    run_id = "malformed-row-run"
    png = _png(tmp_path)
    custom_id = f"{run_id}:slide-01"
    output = (
        json.dumps(
            {
                "custom_id": custom_id,
                "response": {
                    "status_code": 200,
                    "body": {"choices": [{"message": {"content": "NOT JSON"}}]},
                },
            }
        )
        + "\n"
    ).encode()

    class FakeAdapter:
        def submit_and_receipt(self, rows: Any, **kwargs: Any) -> Any:
            receipt = BatchReceipt(
                run_id=kwargs["run_id"],
                batch_id="batch_bad",
                input_file_id="file_in",
                output_file_id="file_out",
                status="completed",
                submitted_at="2026-07-10T00:00:00Z",
                row_count=len(rows),
                model=kwargs.get("model"),
            )
            write_receipt(kwargs["runs_root"], receipt)
            return receipt

        def join_completed_output(self, receipt: Any, *, expected_custom_ids: Any = None) -> Any:
            from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter

            real = LiteLlmBatchAdapter(
                create_file_fn=lambda **_k: SimpleNamespace(id="f"),
                create_batch_fn=lambda **_k: SimpleNamespace(id="b"),
                retrieve_batch_fn=lambda **_k: None,
                file_content_fn=lambda **_k: output,
                cancel_batch_fn=lambda **_k: None,
            )
            return real.join_completed_output(receipt, expected_custom_ids=expected_custom_ids)

    with pytest.raises(VisionProviderError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", png)],
            run_id=run_id,
            runs_root=tmp_path,
            adapter=FakeAdapter(),  # type: ignore[arg-type]
            sleep_fn=lambda _s: None,
        )
    assert custom_id in str(exc_info.value)
    assert exc_info.value.tag == "vision.provider.malformed-json"


def test_unexpected_custom_ids_fail_loud(tmp_path: Path) -> None:
    from app.runtime.llm_batch.errors import LlmBatchError
    from app.runtime.llm_batch.receipts import BatchReceipt, write_receipt

    run_id = "unexpected-row-run"
    png = _png(tmp_path)
    content = _valid_content("slide-01")
    output = (
        json.dumps(
            {
                "custom_id": f"{run_id}:slide-01",
                "response": {
                    "status_code": 200,
                    "body": {"choices": [{"message": {"content": content}}]},
                },
            }
        )
        + "\n"
        + json.dumps(
            {
                "custom_id": f"{run_id}:extra",
                "response": {
                    "status_code": 200,
                    "body": {"choices": [{"message": {"content": content}}]},
                },
            }
        )
        + "\n"
    ).encode()

    class FakeAdapter:
        def submit_and_receipt(self, rows: Any, **kwargs: Any) -> Any:
            receipt = BatchReceipt(
                run_id=kwargs["run_id"],
                batch_id="batch_x",
                input_file_id="file_in",
                output_file_id="file_out",
                status="completed",
                submitted_at="2026-07-10T00:00:00Z",
                row_count=len(rows),
                model=kwargs.get("model"),
            )
            write_receipt(kwargs["runs_root"], receipt)
            return receipt

        def join_completed_output(self, receipt: Any, *, expected_custom_ids: Any = None) -> Any:
            from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter

            real = LiteLlmBatchAdapter(
                create_file_fn=lambda **_k: SimpleNamespace(id="f"),
                create_batch_fn=lambda **_k: SimpleNamespace(id="b"),
                retrieve_batch_fn=lambda **_k: None,
                file_content_fn=lambda **_k: output,
                cancel_batch_fn=lambda **_k: None,
            )
            return real.join_completed_output(receipt, expected_custom_ids=expected_custom_ids)

    with pytest.raises(LlmBatchError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", png)],
            run_id=run_id,
            runs_root=tmp_path,
            adapter=FakeAdapter(),  # type: ignore[arg-type]
            sleep_fn=lambda _s: None,
        )
    assert exc_info.value.tag == "vision.batch.unexpected-rows"


def test_stale_receipt_row_count_fail_loud(tmp_path: Path) -> None:
    from app.runtime.llm_batch.errors import LlmBatchError
    from app.runtime.llm_batch.receipts import BatchReceipt, write_receipt

    run_id = "stale-receipt-run"
    write_receipt(
        tmp_path,
        BatchReceipt(
            run_id=run_id,
            batch_id="batch_old",
            input_file_id="file_in",
            output_file_id="file_out",
            status="completed",
            submitted_at="2026-07-10T00:00:00Z",
            row_count=1,
            model="gpt-5.5",
        ),
    )

    class BoomAdapter:
        def submit_and_receipt(self, *_a: Any, **_k: Any) -> Any:
            raise AssertionError("must not re-submit on stale receipt")

        def join_completed_output(self, *_a: Any, **_k: Any) -> Any:
            raise AssertionError("must not join on stale receipt")

    with pytest.raises(LlmBatchError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", _png(tmp_path, "1.png")), ("slide-02", _png(tmp_path, "2.png"))],
            run_id=run_id,
            runs_root=tmp_path,
            adapter=BoomAdapter(),  # type: ignore[arg-type]
        )
    assert exc_info.value.tag == "vision.batch.receipt-stale"


def test_duplicate_slide_id_fail_loud(tmp_path: Path) -> None:
    png = _png(tmp_path)
    with pytest.raises(VisionProviderError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", png), ("slide-01", png)],
            run_id="dup-run",
            runs_root=tmp_path,
        )
    assert exc_info.value.tag == "vision.batch.slide-id-invalid"


def test_run_vision_batch_with_mocked_adapter(tmp_path: Path) -> None:
    png1 = _png(tmp_path, "1.png")
    png2 = _png(tmp_path, "2.png")
    run_id = "trial-batch-1"
    content1 = _valid_content("slide-01")
    content2 = _valid_content("slide-02")
    output = (
        json.dumps(
            {
                "custom_id": f"{run_id}:slide-02",
                "response": {
                    "status_code": 200,
                    "body": {"choices": [{"message": {"content": content2}}]},
                },
            }
        )
        + "\n"
        + json.dumps(
            {
                "custom_id": f"{run_id}:slide-01",
                "response": {
                    "status_code": 200,
                    "body": {"choices": [{"message": {"content": content1}}]},
                },
            }
        )
        + "\n"
    ).encode()

    class FakeAdapter:
        def __init__(self) -> None:
            self.create_calls = 0

        def submit_and_receipt(self, rows: Any, **kwargs: Any) -> Any:
            self.create_calls += 1
            from app.runtime.llm_batch.receipts import BatchReceipt, write_receipt

            receipt = BatchReceipt(
                run_id=kwargs["run_id"],
                batch_id="batch_1",
                input_file_id="file_in",
                output_file_id="file_out",
                status="completed",
                submitted_at="2026-07-10T00:00:00Z",
                row_count=len(rows),
                model=kwargs.get("model"),
            )
            write_receipt(kwargs["runs_root"], receipt)
            return receipt

        def retrieve_batch(self, batch_id: str) -> Any:  # noqa: ARG002
            return SimpleNamespace(
                id="batch_1",
                status="completed",
                input_file_id="file_in",
                output_file_id="file_out",
                error_file_id=None,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                request_counts={},
                model="gpt-5.5",
                completed_at="2026-07-10T00:01:00Z",
            )

        def join_completed_output(self, receipt: Any, *, expected_custom_ids: Any = None) -> Any:
            from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter

            real = LiteLlmBatchAdapter(
                create_file_fn=lambda **_k: SimpleNamespace(id="f"),
                create_batch_fn=lambda **_k: SimpleNamespace(id="b"),
                retrieve_batch_fn=lambda **_k: None,
                file_content_fn=lambda **_k: output,
                cancel_batch_fn=lambda **_k: None,
            )
            return real.join_completed_output(receipt, expected_custom_ids=expected_custom_ids)

    fake = FakeAdapter()
    results = run_vision_batch_perception(
        [("slide-01", png1), ("slide-02", png2)],
        run_id=run_id,
        runs_root=tmp_path,
        adapter=fake,  # type: ignore[arg-type]
        sleep_fn=lambda _s: None,
    )
    assert [r.slide_id for r in results] == ["slide-01", "slide-02"]
    assert fake.create_calls == 1

    results2 = run_vision_batch_perception(
        [("slide-01", png1), ("slide-02", png2)],
        run_id=run_id,
        runs_root=tmp_path,
        adapter=fake,  # type: ignore[arg-type]
        sleep_fn=lambda _s: None,
    )
    assert len(results2) == 2
    assert fake.create_calls == 1


def test_act_batch_mode_uses_batch_route(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    png = _png(tmp_path)
    payload = {
        "llm_execution_mode": "batch",
        "slides": [{"slide_id": "slide-01", "file_path": str(png)}],
    }
    state = RunState(
        run_id=uuid4(),
        graph_version="v42",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="0" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )

    called = {"batch": 0, "realtime": 0}

    def fake_batch(*_a: Any, **_k: Any) -> list[VisionProviderResponse]:
        called["batch"] += 1
        return [
            VisionProviderResponse(
                slide_id="slide-01",
                confidence="HIGH",
                coverage="perceived",
                confidence_score=0.9,
                slide_title="T",
                extracted_text="x",
                layout_description="y",
                text_blocks=["x"],
                visual_elements=[],
                provider_model_id="gpt-5.5",
                source_png_path=str(png),
            )
        ]

    def boom_perceive(*_a: Any, **_k: Any) -> VisionProviderResponse:
        called["realtime"] += 1
        raise AssertionError("realtime perceive_png must not run in batch mode")

    monkeypatch.setattr(_act, "run_vision_batch_perception", fake_batch)
    monkeypatch.setattr(_act, "perceive_png", boom_perceive)
    monkeypatch.setattr(_act, "with_llm_primary_reading_path", lambda artifact: artifact)
    out = _act.act(state, runs_root=tmp_path)
    assert called["batch"] == 1
    assert called["realtime"] == 0
    assert '"llm_execution_mode": "batch"' in out["cache_state"]["cache_prefix"]
    assert out["model_resolution_trail"][-1].reason == "vision.batch.parsed.ok"


def test_act_batch_multi_slide_single_submit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    png1 = _png(tmp_path, "a.png")
    png2 = _png(tmp_path, "b.png")
    payload = {
        "llm_execution_mode": "batch",
        "slides": [
            {"slide_id": "slide-01", "file_path": str(png1)},
            {"slide_id": "slide-02", "file_path": str(png2)},
        ],
    }
    state = RunState(
        run_id=uuid4(),
        graph_version="v42",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="0" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )
    calls: list[list[tuple[str, Path]]] = []

    def fake_batch(jobs: Any, **_k: Any) -> list[VisionProviderResponse]:
        calls.append(list(jobs))
        return [
            VisionProviderResponse(
                slide_id=sid,
                confidence="HIGH",
                coverage="perceived",
                confidence_score=0.9,
                slide_title="T",
                extracted_text="x",
                layout_description="y",
                text_blocks=["x"],
                visual_elements=[],
                provider_model_id="gpt-5.5",
                source_png_path=str(path),
            )
            for sid, path in jobs
        ]

    monkeypatch.setattr(_act, "run_vision_batch_perception", fake_batch)
    monkeypatch.setattr(
        _act,
        "perceive_png",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("no realtime")),
    )
    monkeypatch.setattr(_act, "with_llm_primary_reading_path", lambda artifact: artifact)
    out = _act.act(state, runs_root=tmp_path)
    assert len(calls) == 1
    assert [sid for sid, _ in calls[0]] == ["slide-01", "slide-02"]
    artifacts = json.loads(out["cache_state"]["cache_prefix"])["perception_artifacts"]
    assert [a["slide_id"] for a in artifacts] == ["slide-01", "slide-02"]


def test_eligibility_fail_loud(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "app.specialists.vision.batch_route.load_batch_eligibility",
        lambda: SimpleNamespace(is_v1_batch_routable=lambda _n: False),
    )
    with pytest.raises(VisionProviderError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", _png(tmp_path))],
            run_id="r",
            runs_root=tmp_path,
        )
    assert exc_info.value.tag == "vision.batch.ineligible"


def test_corrupt_receipt_fail_loud_no_resubmit(tmp_path: Path) -> None:
    from app.runtime.llm_batch.errors import LlmBatchError

    run_id = "corrupt-receipt-run"
    receipt_dir = tmp_path / run_id / "llm_batch"
    receipt_dir.mkdir(parents=True)
    (receipt_dir / "receipt.json").write_text("{not-json", encoding="utf-8")

    class BoomAdapter:
        def submit_and_receipt(self, *_a: Any, **_k: Any) -> Any:
            raise AssertionError("must not re-submit when receipt exists but corrupt")

    with pytest.raises(LlmBatchError) as exc_info:
        run_vision_batch_perception(
            [("slide-01", _png(tmp_path))],
            run_id=run_id,
            runs_root=tmp_path,
            adapter=BoomAdapter(),  # type: ignore[arg-type]
        )
    assert exc_info.value.tag == "vision.batch.receipt-corrupt"
