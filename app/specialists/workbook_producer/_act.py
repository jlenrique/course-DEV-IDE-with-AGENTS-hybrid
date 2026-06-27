"""workbook_producer act — deterministic in-graph adapter over WorkbookProducer.

The 07W producer is a thin, deterministic adapter (spec-07w §2). Its ``_act``
REUSES the PROVEN assembly in ``scripts/utilities/produce_tejal_workbook.py``
(``build_tejal_workbook_inputs`` + ``_load_segments`` + ``_exercises`` +
further_reading/objectives/answer_keys assembly), **re-pointed to read the
CURRENTLY-RUNNING run** instead of a hardcoded B1 run:

1. resolve the running run's directory (``RUNS_ROOT / run_id`` or an explicit
   ``run_dir`` replay override);
2. load transcript segments from the run's storyboard-B segment manifest and map
   each slide to its Gary deck export (figure embed, when present on disk);
3. build the source set for the G1 numeric gate from the run's
   ``bundle/extracted.md`` + the delivered narration;
4. assemble the WorkbookSpec + learning objectives + exercises + answer keys +
   further-reading deterministically (v1 reuses the proven tejal/corpus-assessment
   assembly — generalizing to an arbitrary corpus is a named follow-on);
5. run ``WorkbookProducer.produce(...)`` → MD + DOCX + G1/G2/AC audits → sidecar.

NO model client is touched here — pinned as a test invariant (mirrors the 07D.5
motion brick). Terminal leaf: emits the DOCX + canonical MD as a sidecar and puts
the ProducedAsset / sidecar refs on RunState; it feeds nothing downstream.

HONESTY BOUNDARY (do NOT over-claim): G1 numeric fidelity is symbol-only,
FAIL-mode. Word-form numerals are NOT gated — named gap
``braid-workbook-wordform-numeral-gap``. General arbitrary-corpus spec authoring
is a named follow-on.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit
from app.marcus.lesson_plan.workbook_enrichment import (
    load_enrichment_card,
    project_enrichment_to_workbook_inputs,
)
from app.marcus.lesson_plan.workbook_producer import (
    DEFAULT_WORKBOOK_OUTPUT_ROOT,
    FurtherReadingEntry,
    LearningObjectiveBrief,
    ResearchEntry,
    TranscriptSegment,
    WorkbookProducer,
    WorkbookSidecar,
)
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.runtime.economics import RUNS_ROOT
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.workbook_producer.payload_contract import CONSUMED_PAYLOAD_KEYS

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "app" / "specialists" / "workbook_producer" / "config.yaml"

_DEFAULT_SEGMENT_MANIFEST_RELPATH = "exports/segment-manifest-storyboard-b.yaml"
_DEFAULT_CORPUS_RELPATH = "bundle/extracted.md"
_DEFAULT_UNIT_ID = "tejal-apc-c1-m1-p2-trends"
_DEFAULT_LESSON_PLAN_REVISION = 1


class WorkbookProducerActError(SpecialistDispatchError):
    """Raised when the in-graph workbook producer cannot assemble/produce.

    Dispatch-family so a mid-walk failure error-pauses recoverably (mirrors the
    kira/texas/motion_planner fail-loud seams) instead of killing the trial.
    """


# ---------------------------------------------------------------------------
# Resolution-trail helper (mirror motion_planner)
# ---------------------------------------------------------------------------


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=last_entry.timestamp,
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise WorkbookProducerActError(
            "workbook_producer envelope cache_prefix is not JSON",
            tag="workbook-producer.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise WorkbookProducerActError(
            "workbook_producer envelope cache_prefix must decode to an object",
            tag="workbook-producer.wrong-type",
        )
    return decoded


def _load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        return {}
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve_run_dir(state: RunState, payload: dict[str, Any]) -> Path:
    """Resolve the CURRENTLY-RUNNING run's directory.

    Replay/dev seam: an explicit ``run_dir`` in the payload or the
    ``WORKBOOK_RUN_DIR`` env var wins (mirrors kira's ``motion_plan_path`` and
    motion_planner's replay affordances); production resolves
    ``RUNS_ROOT / run_id`` from RunState.
    """
    override = (
        payload.get("run_dir")
        or payload.get("workbook_run_dir")
        or os.environ.get("WORKBOOK_RUN_DIR")
    )
    if override:
        return Path(override)
    run_id = getattr(state, "run_id", None)
    if run_id is None:
        raise WorkbookProducerActError(
            "workbook_producer cannot resolve the running run directory: RunState "
            "carries no run_id and no run_dir override was supplied",
            tag="workbook-producer.run-dir.missing",
        )
    return RUNS_ROOT / str(run_id)


# ---------------------------------------------------------------------------
# Run-data readers (PORTED from produce_tejal_workbook, re-pointed to the run)
# ---------------------------------------------------------------------------


def _figure_captions(run_dir: Path) -> dict[int, str]:
    """Map slide number -> human caption from ``exports/gary/A_A_pages`` stems."""
    pages_dir = run_dir / "exports" / "gary" / "A_A_pages"
    captions: dict[int, str] = {}
    if not pages_dir.exists():
        return captions
    for png in pages_dir.glob("*.png"):
        stem = png.stem
        num_part, _, title_part = stem.partition("_")
        try:
            num = int(num_part)
        except ValueError:
            continue
        captions[num] = title_part.replace("-", " ").strip() or f"Slide {num}"
    return captions


def _load_segments(run_dir: Path, manifest_relpath: str) -> tuple[TranscriptSegment, ...]:
    """Build transcript segments from the run's storyboard-B segment manifest.

    Maps each segment's ``slide_id`` (``slide-NN``) to its Gary deck export
    (``exports/gary/A_slide-NN.png``) so the workbook embeds the real slide figure
    with a caption + source_ref (AC-7), when those exports exist on disk.
    """
    manifest_path = run_dir / manifest_relpath
    if not manifest_path.is_file():
        raise WorkbookProducerActError(
            f"workbook_producer segment manifest not found: {manifest_path}",
            tag="workbook-producer.segment-manifest.missing",
        )
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        raise WorkbookProducerActError(
            f"workbook_producer segment manifest {manifest_path} missing a "
            "top-level 'segments' list",
            tag="workbook-producer.segment-manifest.malformed",
        )
    captions = _figure_captions(run_dir)
    gary_dir = run_dir / "exports" / "gary"
    out: list[TranscriptSegment] = []
    for raw in data["segments"]:
        if not isinstance(raw, dict):
            continue
        seg_id = str(raw.get("segment_id") or raw.get("id") or "").strip()
        if not seg_id:
            continue
        slide_id = str(raw.get("slide_id") or seg_id)
        slide_num: int | None = None
        tail = slide_id.rsplit("-", 1)[-1]
        if tail.isdigit():
            slide_num = int(tail)
        figure_abs: Path | None = None
        caption = slide_id
        visual_file_rel: str | None = None
        if slide_num is not None:
            candidate = gary_dir / f"A_slide-{slide_num:02d}.png"
            if candidate.exists():
                figure_abs = candidate
                visual_file_rel = candidate.relative_to(REPO_ROOT).as_posix()
                caption = captions.get(slide_num, f"Slide {slide_num}")
        vrefs: tuple[dict[str, str], ...] = ()
        if figure_abs is not None:
            vrefs = ({"element": slide_id, "description": caption},)
        out.append(
            TranscriptSegment(
                segment_id=seg_id,
                narration_text=str(raw.get("narration_text", "")),
                visual_file=visual_file_rel,
                visual_references=vrefs,
                source_ref=f"src-{slide_id}",
                visual_file_abs=str(figure_abs) if figure_abs else None,
            )
        )
    if not out:
        raise WorkbookProducerActError(
            f"workbook_producer segment manifest {manifest_path} yielded no segments",
            tag="workbook-producer.segment-manifest.empty",
        )
    return tuple(out)


def _build_source_text(
    run_dir: Path, corpus_relpath: str, segments: tuple[TranscriptSegment, ...]
) -> str:
    """The run's source set for the G1 numeric gate.

    = the corpus slides (``bundle/extracted.md``: the authoritative upstream
    numerals) + the delivered transcript of record (the run-delivered,
    fidelity-passed narration). The numeric gate then meaningfully audits the
    AUTHORED content against this set; the verbatim transcript-of-record is
    in-source by definition.
    """
    corpus_path = run_dir / corpus_relpath
    if not corpus_path.is_file():
        raise WorkbookProducerActError(
            f"workbook_producer corpus not found: {corpus_path}",
            tag="workbook-producer.corpus.missing",
        )
    corpus = corpus_path.read_text(encoding="utf-8")
    delivered = "\n".join(seg.narration_text for seg in segments)
    return corpus + "\n\n" + delivered


# ---------------------------------------------------------------------------
# Knowledge-Check ingest -> Exercises + answer keys (PORTED tejal assembly)
# ---------------------------------------------------------------------------

# The corpus Chapter-2 / Chapter-3 Knowledge Checks, ingested backward from the
# sourced assessments (each prompt + correct answer is corpus-grounded). Bloom
# levels are the corpus tags. (exercise_id, bloom, prompt, correct_answer)
_CH2_KC: tuple[tuple[str, str, str, str], ...] = (
    (
        "ex-ch2-q1",
        "remember",
        "Between 2012 and 2022, which major structural shift occurred regarding "
        "physician practice models?",
        "A drastic decrease in independent private practice and a surge in "
        "physicians employed by large health systems.",
    ),
    (
        "ex-ch2-q2",
        "understand",
        "Approximately what percentage of total U.S. healthcare spending is "
        "attributed to administrative costs and waste?",
        "25%",
    ),
    (
        "ex-ch2-q3",
        "analyze",
        "While patient volume and acuity are high, the data shows that the "
        "primary driver of the physician burnout epidemic is:",
        "Bureaucratic tasks and administrative bloat (e.g., EHR charting).",
    ),
    (
        "ex-ch2-q4",
        "evaluate",
        "Based on the 'Healthcare Supply and Demand' concepts, why does simply "
        "hiring more physicians often fail to solve access issues in a poorly "
        "designed system?",
        "Because it adds expensive supply without addressing the underlying "
        "systemic inefficiencies or administrative bottlenecks that limit "
        "throughput.",
    ),
    (
        "ex-ch2-q5",
        "apply",
        "You are an attending physician managing a complex workflow and notice a "
        "recurring delay in patient transport. According to the 'Modern "
        "Clinician's Dilemma,' what is the most likely barrier preventing you "
        "from solving this?",
        "The absence of a structured innovation process and the organizational "
        "authority/safety to redesign the workflow.",
    ),
)

_CH3_KC: tuple[tuple[str, str, str, str], ...] = (
    (
        "ex-ch3-q1",
        "remember",
        "In 1950, medical knowledge doubled every 50 years. What is the "
        "currently projected doubling time?",
        "73 days.",
    ),
    (
        "ex-ch3-q2",
        "understand",
        "While 66% of physicians report using some form of AI in practice, what "
        "is the critical gap identified in the macro trends?",
        "Formal training on how to oversee, evaluate, and safely implement these "
        "tools remains severely limited.",
    ),
    (
        "ex-ch3-q3",
        "apply",
        "A hospital implements a 'Digital Front Door' strategy. Which initiative "
        "best represents this concept?",
        "An AI-driven, mobile-friendly triage system that allows patients to "
        "seamlessly schedule appointments and communicate with their care team "
        "before entering the physical clinic.",
    ),
    (
        "ex-ch3-q4",
        "analyze",
        "The data shows 67% of physicians want to pursue leadership roles, yet "
        "only 18% receive formal business training. What is the most significant "
        "consequence of this gap for Academic Health Centers?",
        "They possess deep clinical expertise but lack the interdisciplinary "
        "management skills required to translate clinical ideas into scalable, "
        "system-wide improvements.",
    ),
    (
        "ex-ch3-q5",
        "evaluate",
        "Referring to Tyler Beauchamp's article, which category of care failure "
        "requires the most urgent intrapreneurial intervention to reduce "
        "macro-level waste?",
        "Administrative complexity and failures of care coordination.",
    ),
)


def _exercises(
    kc: tuple[tuple[str, str, str, str], ...], answer_key_source_ref: str
) -> tuple[list[Exercise], dict[str, str]]:
    exercises: list[Exercise] = []
    answers: dict[str, str] = {}
    for ex_id, bloom, prompt, correct in kc:
        exercises.append(
            Exercise(
                exercise_id=ex_id,
                bloom_level=bloom,  # type: ignore[arg-type]
                prompt_intent=prompt,
                answer_key_source_ref=answer_key_source_ref,
            )
        )
        answers[ex_id] = f"Correct answer: {correct}"
    return exercises, answers


_FURTHER_READING: tuple[FurtherReadingEntry, ...] = (
    FurtherReadingEntry(
        "cit-cms-nhe",
        "CMS National Health Expenditure (NHE) Fact Sheet",
        "src-slide-01",
        "https://www.cms.gov/data-research/statistics-trends-and-reports/"
        "national-health-expenditure-data/nhe-fact-sheet",
        "seg-01",
    ),
    FurtherReadingEntry(
        "cit-ama-ownership",
        "American Medical Association — Physician Practice Ownership Report",
        "src-slide-01",
        None,
        "seg-01",
    ),
    FurtherReadingEntry(
        "cit-shrank-jama-2019",
        "Shrank WH et al. Waste in the US Health Care System. JAMA (2019)",
        "src-slide-02",
        "https://doi.org/10.1001/jama.2019.13978",
        "seg-03",
    ),
    FurtherReadingEntry(
        "cit-medscape-burnout-2024",
        "Medscape Physician Burnout & Depression Report (2024)",
        "src-slide-02",
        None,
        "seg-02",
    ),
    FurtherReadingEntry(
        "cit-densen-2011",
        "Densen P. Challenges and Opportunities Facing Medical Education (2011)",
        "src-slide-03",
        "https://doi.org/10.1043/0027-9684-103.6.48",
        "seg-05",
    ),
    FurtherReadingEntry(
        "cit-isaranuwatchai-jmir-2018",
        "Isaranuwatchai W et al. Remote monitoring, JMIR (2018)",
        "src-slide-03",
        None,
        "seg-08",
    ),
    FurtherReadingEntry(
        "cit-ama-ai-report",
        "AMA Augmented Intelligence in Medicine Report",
        "src-slide-03",
        None,
        "seg-07",
    ),
    FurtherReadingEntry(
        "cit-jackson-2023",
        "Jackson Physician Search — Physician Leadership survey (2023)",
        "src-slide-05",
        None,
        "seg-11",
    ),
    FurtherReadingEntry(
        "cit-rotenstein-acadmed-2021",
        "Rotenstein LS et al. Academic Medicine (2021)",
        "src-slide-05",
        "https://doi.org/10.1097/ACM.0000000000003907",
        "seg-12",
    ),
    FurtherReadingEntry(
        "cit-beauchamp-trillion",
        "Required reading — Beauchamp T. Healthcare's Trillion-Dollar Problem "
        "(Medium)",
        "src-required-reading",
        "https://medium.com/@TylerBeauchamp/"
        "healthcare-s-trillion-dollar-problem-90438f4164dc",
        "seg-03",
    ),
    FurtherReadingEntry(
        "cit-intro-video",
        "Intro video — Healthcare supply & demand (YouTube)",
        "src-intro-video",
        "https://www.youtube.com/watch?v=GjRAHuHIOD0",
        "seg-01",
    ),
)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Author the full tejal WorkbookSpec + produce-time content (PORTED assembly)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkbookInputs:
    """The fully-authored produce() inputs for the in-graph workbook."""

    plan_unit: PlanUnit
    context: ProductionContext
    spec: WorkbookSpec
    segments: tuple[TranscriptSegment, ...]
    source_text: str
    learning_objectives: tuple[LearningObjectiveBrief, ...]
    answer_keys: dict[str, str]
    further_reading: tuple[FurtherReadingEntry, ...]
    research_entries: tuple[ResearchEntry, ...]
    citations: tuple[dict[str, str], ...]
    source_ref_manifest: dict[str, str]
    vo_script_text: str


def _plan_unit_and_context(
    run_dir: Path, run_id: str | None, unit_id: str, revision: int
) -> tuple[PlanUnit, ProductionContext]:
    """The shared (enriched + constant) plan_unit / context construction."""
    digest_seed = str(run_id) if run_id else run_dir.name
    plan_unit = PlanUnit(
        unit_id=unit_id,
        event_type="present-trends",
        source_fitness_diagnosis=(
            f"in-graph composed run {digest_seed} — macro-trends deck (read-only)"
        ),
        weather_band="green",
        modality_ref="workbook",
    )
    context = ProductionContext(
        lesson_plan_revision=revision,
        lesson_plan_digest=digest_seed[:8],
    )
    return plan_unit, context


def _build_enriched_inputs(
    card: dict[str, Any],
    *,
    run_dir: Path,
    run_id: str | None,
    unit_id: str,
    revision: int,
    segments: tuple[TranscriptSegment, ...],
    source_text: str,
    vo_script_text: str,
) -> WorkbookInputs:
    """Author the produce() inputs FROM the frozen G0 enriched card payload (P5-S1).

    The enriched corpus SHAPES the deliverable: sections + Bloom-leveled
    exercises, learning objectives + per-LO Bloom, and gated byte-exact
    further-reading all come from the projection. The run-DATA (segments,
    figures, source set) still rides from ``run_dir`` — the enriched corpus does
    not displace the transcript backbone.
    """
    projection = project_enrichment_to_workbook_inputs(card)
    plan_unit, context = _plan_unit_and_context(run_dir, run_id, unit_id, revision)
    return WorkbookInputs(
        plan_unit=plan_unit,
        context=context,
        spec=projection.spec,
        segments=segments,
        source_text=source_text,
        learning_objectives=projection.learning_objectives,
        answer_keys=projection.answer_keys,
        further_reading=projection.further_reading,
        research_entries=(),
        citations=projection.citations,
        source_ref_manifest=projection.source_ref_manifest,
        vo_script_text=vo_script_text,
    )


def build_workbook_inputs(
    run_dir: Path,
    *,
    config: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> WorkbookInputs:
    """Author the WorkbookSpec + all produce-time content, re-pointed to the run.

    v1 reuses the proven tejal/corpus-assessment assembly (the WorkbookSpec,
    objectives, exercises, and further-reading are corpus-grounded constants);
    the run-DATA (segments, figures, source set) is read from ``run_dir``.
    Generalizing the lesson-plan -> WorkbookSpec adapter to an arbitrary corpus
    is a named follow-on (out of scope for v1).
    """
    cfg = config or _load_config()
    manifest_relpath = str(
        cfg.get("segment_manifest_relpath", _DEFAULT_SEGMENT_MANIFEST_RELPATH)
    )
    corpus_relpath = str(cfg.get("corpus_relpath", _DEFAULT_CORPUS_RELPATH))
    unit_id = str(cfg.get("unit_id", _DEFAULT_UNIT_ID))
    revision = int(cfg.get("lesson_plan_revision", _DEFAULT_LESSON_PLAN_REVISION))

    segments = _load_segments(run_dir, manifest_relpath)
    source_text = _build_source_text(run_dir, corpus_relpath, segments)
    vo_script_text = "\n".join(seg.narration_text for seg in segments)

    # P5-S1 consumption: when the run carries the frozen G0 enriched card payload
    # (``<run_dir>/g0-enrichment.json``), the enriched corpus DISPLACES the
    # hardcoded constants for the slots it covers (sections + Bloom-leveled
    # exercises, learning objectives + per-LO Bloom, gated byte-exact
    # further-reading). Absent the artifact, fall back to the proven constant
    # assembly (backward-compatible non-enrichment runs). READ-ONLY: no network,
    # no model — the frozen verdict is the single source of truth.
    enriched_card = load_enrichment_card(run_dir)
    if enriched_card is not None:
        return _build_enriched_inputs(
            enriched_card,
            run_dir=run_dir,
            run_id=run_id,
            unit_id=unit_id,
            revision=revision,
            segments=segments,
            source_text=source_text,
            vo_script_text=vo_script_text,
        )

    ch2_exercises, ch2_answers = _exercises(_CH2_KC, "src-slide-02")
    ch3_exercises, ch3_answers = _exercises(_CH3_KC, "src-slide-05")
    answer_keys = {**ch2_answers, **ch3_answers}

    spec = WorkbookSpec(
        sections=[
            WorkbookSection(
                section_id="sec-ch2-macro-trends",
                learning_objective_id="obj-lo2-analyze-trends",
                title="Chapter 2 — The Macro Trends (economic & human cost)",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-02",
                    deferred_depth=(
                        "The system-design reframe of burnout the glance-deck "
                        "only gestures at: burnout is not a resilience failure "
                        "but a system-design problem. Over half of physicians "
                        "report a burnout symptom, and the top driver is "
                        "administrative bloat — so the daily workarounds "
                        "clinicians invent are the innovation surface. The deck "
                        "shows the 25% administrative-waste figure; the workbook "
                        "argues WHY that waste is a concrete, redesignable "
                        "innovation target rather than an inevitability."
                    ),
                    retained_on_slide=(
                        "The single perception-tuned statistic per card "
                        "($5.2 trillion NHE; 25% waste)."
                    ),
                ),
                narrative_intent=(
                    "Walk the reader from the economic and structural reality "
                    "(national health expenditure growth and the consolidation "
                    "of physicians into large systems) to the human cost "
                    "(burnout as a system-design problem) and finally to the "
                    "reframe that administrative friction is a targetable "
                    "innovation opportunity. The point a busy clinician should "
                    "leave with: the workarounds you invent to survive a broken "
                    "EHR or admission process are exactly where redesign, "
                    "automation, and AI can recover time and reduce burnout at "
                    "the same time."
                ),
                exercises=ch2_exercises,
            ),
            WorkbookSection(
                section_id="sec-ch3-case-for-change",
                learning_objective_id="obj-lo4-root-cause",
                title="Chapter 3 — The Case for Change (root-cause of failure)",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-05",
                    deferred_depth=(
                        "What safe AI oversight actually requires, and why the "
                        "leadership gap is a root-cause of systemic failure "
                        "rather than a motivation deficit: adoption of clinical "
                        "AI is already ahead of governance training, and "
                        "physicians want influence over strategy but lack formal "
                        "business preparation. The deck glances the gap; the "
                        "workbook traces it to a training-infrastructure cause "
                        "the learner is positioned to close."
                    ),
                    retained_on_slide=(
                        "The leadership-gap contrast (67% want leadership vs "
                        "18% trained)."
                    ),
                ),
                narrative_intent=(
                    "Develop the case for change across the knowledge explosion "
                    "(static training cannot keep pace), the rising adoption of "
                    "clinical AI ahead of oversight, the consumer shift toward a "
                    "digital front door, and the leadership gap. Frame each as a "
                    "root-cause analysis: the failure is structural (training "
                    "infrastructure, governance, service design), and the "
                    "physician who can bridge practice, business, and technology "
                    "is the scarce, needed figure who resolves it."
                ),
                exercises=ch3_exercises,
            ),
            WorkbookSection(
                section_id="sec-ch3-idea-vs-opportunity",
                learning_objective_id="obj-lo3-idea-opportunity",
                title="Bridge — From idea to vetted opportunity (introduced)",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-06",
                    deferred_depth=(
                        "The distinction between a superficial idea and a "
                        "rigorously vetted opportunity — introduced here and "
                        "carried forward into the Opportunity Diagnostic. The "
                        "deck names the forward pull; the workbook seeds the "
                        "vocabulary (scan, size, pressure-test) the learner will "
                        "apply next."
                    ),
                ),
                narrative_intent=(
                    "Close Part 2 by introducing the idea-versus-opportunity "
                    "discipline: awareness of the macro trends is the starting "
                    "point, and choosing to act on them — to pressure-test a gap "
                    "into a vetted opportunity — is the defining move from "
                    "awareness to agency."
                ),
            ),
        ]
    )

    learning_objectives = (
        LearningObjectiveBrief(
            "obj-lo2-analyze-trends",
            "analyze",
            "Analyze the macro-economic and structural trends — administrative "
            "burnout, healthcare consumerism, and technological acceleration — "
            "that necessitate intrapreneurial physician leadership.",
        ),
        LearningObjectiveBrief(
            "obj-lo3-idea-opportunity",
            "analyze",
            "Differentiate between a superficial idea and a rigorously vetted "
            "opportunity using the core tenets of the Intrapreneurship Formula.",
        ),
        LearningObjectiveBrief(
            "obj-lo4-root-cause",
            "evaluate",
            "Evaluate systemic operational failures through root-cause analysis "
            "and defend the findings against the structural evidence.",
        ),
    )

    # G2 citation manifest: every rendered citation resolves to a real source_ref.
    source_ref_manifest: dict[str, str] = {}
    citations: list[dict[str, str]] = []
    for entry in _FURTHER_READING:
        source_ref_manifest[entry.source_ref] = _hash(entry.title)
        citations.append({"source_ref": entry.source_ref})

    plan_unit, context = _plan_unit_and_context(run_dir, run_id, unit_id, revision)

    return WorkbookInputs(
        plan_unit=plan_unit,
        context=context,
        spec=spec,
        segments=segments,
        source_text=source_text,
        learning_objectives=learning_objectives,
        answer_keys=answer_keys,
        further_reading=_FURTHER_READING,
        research_entries=(),  # v1: live-research leg deferred (rendered as a note)
        citations=tuple(citations),
        source_ref_manifest=source_ref_manifest,
        vo_script_text=vo_script_text,
    )


def produce_workbook(state: RunState, payload: dict[str, Any]) -> WorkbookSidecar:
    """Assemble inputs from the running run + run WorkbookProducer.produce()."""
    config = _load_config()
    run_dir = _resolve_run_dir(state, payload)
    if not run_dir.exists():
        raise WorkbookProducerActError(
            f"workbook_producer run directory does not exist: {run_dir}",
            tag="workbook-producer.run-dir.absent",
        )
    run_id = getattr(state, "run_id", None)
    inputs = build_workbook_inputs(
        run_dir, config=config, run_id=str(run_id) if run_id is not None else None
    )
    output_root = (
        payload.get("output_root")
        or config.get("output_root")
        or DEFAULT_WORKBOOK_OUTPUT_ROOT
    )
    producer = WorkbookProducer(output_root=output_root)
    return producer.produce(
        inputs.plan_unit,
        inputs.context,
        spec=inputs.spec,
        segments=inputs.segments,
        source_text=inputs.source_text,
        citations=inputs.citations,
        source_ref_manifest=inputs.source_ref_manifest,
        vo_script_text=inputs.vo_script_text,
        learning_objectives=inputs.learning_objectives,
        answer_keys=inputs.answer_keys,
        further_reading=inputs.further_reading,
        research_entries=inputs.research_entries,
        # DP6 (spec landmine): workbook-only diff justifies reuse; do not force a
        # spurious fresh-gamma. Stamp the in-graph run id.
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha=(str(run_id)[:8] if run_id is not None else "WORKING"),
    )


def _sidecar_refs(sidecar: WorkbookSidecar) -> dict[str, Any]:
    """Project the sidecar into the JSON-safe refs put on RunState."""
    return {
        "asset_ref": sidecar.asset.asset_ref,
        "asset_path": sidecar.asset.asset_path,
        "fulfills": sidecar.asset.fulfills,
        "modality_ref": sidecar.asset.modality_ref,
        "markdown_path": sidecar.markdown_path,
        "docx_path": sidecar.docx_path,
        "numeric_audit_status": sidecar.numeric_audit.get("status"),
        "citation_unsourced": sidecar.citation_audit["buckets"][
            "unsourced_citations"
        ]["count"],
        "segment_coverage": sidecar.segment_coverage,
        "gamma_reuse_justified_by": sidecar.gamma_reuse_justified_by,
    }


def act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError(
            "workbook_producer act invoked before plan; resolution trail is empty"
        )
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    try:
        sidecar = produce_workbook(state, payload)
    except WorkbookProducerActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    output = {
        "workbook": _sidecar_refs(sidecar),
        "workbook_producer": {
            "specialist_id": "workbook_producer",
            "docx_path": sidecar.docx_path,
            "markdown_path": sidecar.markdown_path,
        },
    }
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="workbook-producer.produced.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=json.dumps(
                output, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str
            ),
            entries_count=entries_count + 1,
        ).model_dump(mode="json"),
    }


__all__ = [
    "CONFIG_PATH",
    "CONSUMED_PAYLOAD_KEYS",
    "WorkbookInputs",
    "WorkbookProducerActError",
    "act",
    "build_workbook_inputs",
    "decode_envelope_payload",
    "produce_workbook",
]
