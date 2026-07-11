"""A2: hermetic perception harness scaffolding (offline done-bar)."""

from __future__ import annotations

import json
from pathlib import Path

from app.runtime.llm_batch.perception_harness import (
    HARNESS_BASELINE_BATCH_ID,
    assert_frozen_fixtures_present,
    compare_arm_scores,
    frozen_slide_paths,
    score_perception,
    write_compare_report,
)
from app.specialists.vision.payload_contract import VisionProviderResponse


def _resp(
    slide_id: str,
    *,
    title: str = "Title",
    text: str = "body",
    elements: int = 2,
    confidence: str = "HIGH",
    layout: str = "two-column",
) -> VisionProviderResponse:
    return VisionProviderResponse(
        slide_id=slide_id,
        confidence=confidence,  # type: ignore[arg-type]
        slide_title=title,
        extracted_text=text,
        layout_description=layout,
        visual_elements=[
            {"kind": "title", "role_tier": "2"} for _ in range(elements)
        ],
        provider_model_id="gpt-5.5",
    )


def test_frozen_fixtures_present_on_disk() -> None:
    slides = assert_frozen_fixtures_present()
    assert len(slides) == 2
    assert all(p.is_file() for _, p in slides)
    ids = [sid for sid, _ in frozen_slide_paths()]
    assert ids[0].endswith("slide_01")
    assert ids[1].endswith("slide_02")


def test_score_requires_non_vacuous_fields() -> None:
    rich = score_perception(_resp("s1"), arm="realtime")
    assert rich.non_vacuous is True
    empty = score_perception(
        VisionProviderResponse(
            slide_id="s-empty",
            confidence="LOW",  # type: ignore[arg-type]
            slide_title="",
            extracted_text="",
            layout_description="",
            visual_elements=[],
        ),
        arm="batch",
    )
    assert empty.non_vacuous is False


def test_compare_report_semantic_deltas_not_byte_identical() -> None:
    rt = [
        score_perception(_resp("slide_01", elements=2), arm="realtime"),
        score_perception(_resp("slide_02", elements=3, title="B"), arm="realtime"),
    ]
    bt = [
        score_perception(_resp("slide_01", elements=2), arm="batch"),
        score_perception(
            _resp("slide_02", elements=1, title="B-batch"), arm="batch"
        ),
    ]
    report = compare_arm_scores(rt, bt)
    assert report.schema_version == 1
    assert "byte-identical" in report.claim
    assert report.harness_baseline_batch_id_narrative == HARNESS_BASELINE_BATCH_ID
    assert report.both_arms_non_vacuous is True
    fields = {d["field"] for d in report.deltas}
    assert "visual_element_count" in fields
    # title both non-empty → has_title same True; element count differs on slide_02
    assert any(
        d["slide_id"] == "slide_02" and d["field"] == "visual_element_count"
        for d in report.deltas
    )


def test_write_compare_report_golden_shape(tmp_path: Path) -> None:
    rt = [score_perception(_resp("slide_01"), arm="realtime")]
    bt = [score_perception(_resp("slide_01", elements=1), arm="batch")]
    report = compare_arm_scores(rt, bt)
    out = write_compare_report(tmp_path / "compare-report.json", report)
    payload = json.loads(out.read_text(encoding="utf-8"))
    for key in (
        "schema_version",
        "claim",
        "harness_baseline_batch_id_narrative",
        "model_family",
        "frozen_slides",
        "realtime_scores",
        "batch_scores",
        "deltas",
        "both_arms_non_vacuous",
        "notes",
    ):
        assert key in payload
    assert payload["schema_version"] == 1
    assert payload["harness_baseline_batch_id_narrative"] == HARNESS_BASELINE_BATCH_ID
    golden = (
        Path(__file__).parent
        / "fixtures"
        / "perception_harness"
        / "compare-report.schema.json"
    )
    schema = json.loads(golden.read_text(encoding="utf-8"))
    assert set(schema["required"]) <= set(payload.keys())


def test_baseline_id_is_narrative_constant() -> None:
    assert HARNESS_BASELINE_BATCH_ID.startswith("batch_")
    # Must not be treated as an executable retrieve target in hermetic path.
    assert "6a457bcac6488190b79224e61ea89b26" in HARNESS_BASELINE_BATCH_ID
