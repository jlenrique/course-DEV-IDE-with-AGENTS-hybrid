"""A2 perception eval harness — LiteLLM-backed realtime vs batch compare.

Eval sidecar only: does not mutate production defaults, eligibility, or routing.
Hermetic scoring/compare is the done-bar; ``--run-live`` is optional evidence.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.specialists.vision.payload_contract import VisionProviderResponse

REPO_ROOT = Path(__file__).resolve().parents[3]

# Frozen leg3 c-u03 probe PNGs (slide_01 + slide_02 only).
FROZEN_SLIDE_DIR = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "leg3-cu03-subslide-invariant-20260701T021037Z"
    / "gamma-export"
)
FROZEN_SLIDE_IDS: tuple[str, ...] = (
    "c-u03-persubslide-probe_slide_01",
    "c-u03-persubslide-probe_slide_02",
)

# Narrative quality baseline only — non-executable; gpt-4.1-mini historical smoke.
HARNESS_BASELINE_BATCH_ID = "batch_6a457bcac6488190b79224e61ea89b26"

ArmName = Literal["realtime", "batch"]


@dataclass(frozen=True)
class SlideScore:
    """Non-vacuous perception score fields for one slide arm."""

    slide_id: str
    arm: ArmName
    has_title: bool
    has_extracted_text: bool
    visual_element_count: int
    confidence: str
    layout_nonempty: bool

    @property
    def non_vacuous(self) -> bool:
        """True when at least one substantive perception field is present."""

        return (
            self.has_title
            or self.has_extracted_text
            or self.visual_element_count > 0
            or self.layout_nonempty
        )


@dataclass(frozen=True)
class ScoreDelta:
    slide_id: str
    field: str
    realtime: Any
    batch: Any


@dataclass
class CompareReport:
    """Semantic/score compare — never claims byte-identical parity."""

    schema_version: int = 1
    claim: str = (
        "semantic/score deltas only; hermetic green does not prove live quality; "
        "byte-identical / exact-match parity is forbidden"
    )
    harness_baseline_batch_id_narrative: str = HARNESS_BASELINE_BATCH_ID
    model_family: str = "gpt-5.5"
    frozen_slides: list[str] = field(default_factory=list)
    realtime_scores: list[dict[str, Any]] = field(default_factory=list)
    batch_scores: list[dict[str, Any]] = field(default_factory=list)
    deltas: list[dict[str, Any]] = field(default_factory=list)
    both_arms_non_vacuous: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def frozen_slide_paths() -> list[tuple[str, Path]]:
    """Return (slide_id, path) for the two frozen probe PNGs."""

    out: list[tuple[str, Path]] = []
    for slide_id in FROZEN_SLIDE_IDS:
        path = FROZEN_SLIDE_DIR / f"{slide_id}.png"
        out.append((slide_id, path))
    return out


def assert_frozen_fixtures_present() -> list[tuple[str, Path]]:
    """Fail loud if frozen PNGs are missing from the evidence tree."""

    slides = frozen_slide_paths()
    missing = [str(p) for _, p in slides if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "A2 frozen fixtures missing: " + "; ".join(missing)
        )
    return slides


def score_perception(
    response: VisionProviderResponse | Mapping[str, Any],
    *,
    arm: ArmName,
) -> SlideScore:
    """Score one perception response; asserts ≥1 non-vacuous field when used live."""

    if isinstance(response, VisionProviderResponse):
        slide_id = response.slide_id
        title = (response.slide_title or "").strip()
        text = (response.extracted_text or "").strip()
        layout = (response.layout_description or "").strip()
        elements = response.visual_elements
        confidence = str(response.confidence)
    else:
        slide_id = str(response.get("slide_id") or "")
        title = str(response.get("slide_title") or "").strip()
        text = str(response.get("extracted_text") or "").strip()
        layout = str(response.get("layout_description") or "").strip()
        raw_el = response.get("visual_elements") or []
        elements = raw_el if isinstance(raw_el, list) else []
        confidence = str(response.get("confidence") or "")

    return SlideScore(
        slide_id=slide_id,
        arm=arm,
        has_title=bool(title),
        has_extracted_text=bool(text),
        visual_element_count=len(elements),
        confidence=confidence,
        layout_nonempty=bool(layout),
    )


def compare_arm_scores(
    realtime: Sequence[SlideScore],
    batch: Sequence[SlideScore],
    *,
    model_family: str = "gpt-5.5",
) -> CompareReport:
    """Build a compare report from scored arms (semantic deltas only)."""

    rt_by = {s.slide_id: s for s in realtime}
    bt_by = {s.slide_id: s for s in batch}
    slide_ids = sorted(set(rt_by) | set(bt_by))
    deltas: list[ScoreDelta] = []
    for sid in slide_ids:
        rt = rt_by.get(sid)
        bt = bt_by.get(sid)
        if rt is None or bt is None:
            deltas.append(
                ScoreDelta(
                    slide_id=sid,
                    field="arm_presence",
                    realtime=rt is not None,
                    batch=bt is not None,
                )
            )
            continue
        for field_name in (
            "has_title",
            "has_extracted_text",
            "visual_element_count",
            "confidence",
            "layout_nonempty",
        ):
            rv = getattr(rt, field_name)
            bv = getattr(bt, field_name)
            if rv != bv:
                deltas.append(
                    ScoreDelta(
                        slide_id=sid,
                        field=field_name,
                        realtime=rv,
                        batch=bv,
                    )
                )

    both_nv = bool(realtime) and bool(batch) and all(
        s.non_vacuous for s in [*realtime, *batch]
    )
    notes = [
        "Compare is semantic/score deltas only — not byte-identical parity.",
        f"Narrative baseline batch id (non-executable): {HARNESS_BASELINE_BATCH_ID}",
    ]
    if not both_nv:
        notes.append("One or more arms scored vacuous (missing substantive fields).")

    return CompareReport(
        model_family=model_family,
        frozen_slides=list(slide_ids),
        realtime_scores=[asdict(s) for s in realtime],
        batch_scores=[asdict(s) for s in batch],
        deltas=[asdict(d) for d in deltas],
        both_arms_non_vacuous=both_nv,
        notes=notes,
    )


def write_compare_report(path: Path, report: CompareReport) -> Path:
    """Write compare report JSON (creates parent dirs)."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def run_live_compare(
    *,
    runs_root: Path,
    run_id: str,
    model_id: str | None = None,
    output_path: Path | None = None,
) -> CompareReport:
    """Optional live arm: realtime ``perceive_png`` vs batch ``run_vision_batch_perception``.

    Requires network + API keys. Callers gate with ``--run-live``.
    """

    from app.runtime.llm_execution_config import load_llm_execution
    from app.specialists.vision.batch_route import run_vision_batch_perception
    from app.specialists.vision.provider import perceive_png

    slides = assert_frozen_fixtures_present()
    profile = load_llm_execution().resolve_profile("vision", mode="realtime")
    model = model_id or profile.model

    rt_scores: list[SlideScore] = []
    for slide_id, path in slides:
        resp = perceive_png(path, slide_id=slide_id, model_id=model)
        score = score_perception(resp, arm="realtime")
        if not score.non_vacuous:
            raise RuntimeError(f"realtime arm vacuous for {slide_id}")
        rt_scores.append(score)

    batch_resps = run_vision_batch_perception(
        slides,
        run_id=run_id,
        runs_root=runs_root,
        wait_policy="block",
    )
    bt_scores = [score_perception(r, arm="batch") for r in batch_resps]
    for score in bt_scores:
        if not score.non_vacuous:
            raise RuntimeError(f"batch arm vacuous for {score.slide_id}")

    report = compare_arm_scores(rt_scores, bt_scores, model_family=model)
    if output_path is not None:
        write_compare_report(output_path, report)
    return report


__all__ = [
    "FROZEN_SLIDE_DIR",
    "FROZEN_SLIDE_IDS",
    "HARNESS_BASELINE_BATCH_ID",
    "CompareReport",
    "ScoreDelta",
    "SlideScore",
    "assert_frozen_fixtures_present",
    "compare_arm_scores",
    "frozen_slide_paths",
    "run_live_compare",
    "score_perception",
    "write_compare_report",
]
