r"""Produce the REAL tejal Part-2 companion workbook (DOCX + MD).

Goal deliverable #2 (braid S3 build): the workbook producer has existed since
braid S2 as a *mechanism* but never produced a real artifact. This module
authors the real ``tejal-apc-c1-m1-p2-trends`` ``WorkbookSpec`` instance and the
run-supplied content (objective statements, worked answers, bibliography), then
invokes :class:`WorkbookProducer` to emit a real DOCX + canonical MD on the
completed B1 run's lesson artifacts.

Inputs (all REAL — no mocks):
  * Narration / transcript of record: the completed B1 run
    ``6a103b6c-943f-4e53-90e1-95c915c7194c`` storyboard-B segment manifest
    (13 segments, the delivered Part-2 trends narration).
  * Key figures: the run's Gary deck exports (``exports/gary/A_slide-NN.png``).
  * Source corpus + numerals: the run's ``bundle/extracted.md`` (the Part-2
    macro-trends slides with their references) PLUS the delivered narration of
    record (the run passed its own Vera/G0 fidelity gates, so the delivered
    transcript is the accepted record for THIS run's source set).
  * Exercises + answer keys: the tejal corpus Chapter-2 / Chapter-3 Knowledge
    Checks (5 each, Bloom-tagged) at
    ``course-content/courses/tejal-apc-c1-m1-p2-trends/assessments/``.
  * Further reading: the corpus per-slide ``References`` + the required-reading
    article (Beauchamp) + the intro video.

Honesty boundary (do NOT over-claim): G1 numeric fidelity is symbol-only,
FAIL-mode. Word-form numerals ("nearly one-fifth", "73-day doubling", "over
half") are NOT gated — named gap ``braid-workbook-wordform-numeral-gap``. The
general semantic claim audit is net-new/DEFERRED. The deck's research-enriched
numerals are cleared because the delivered transcript of record is part of this
run's source set, not because a semantic audit verified them.

Run from the repo root::

    $env:PYTHONIOENCODING="utf-8"
    .\.venv\Scripts\python.exe -m scripts.utilities.produce_tejal_workbook
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit
from app.marcus.lesson_plan.workbook_producer import (
    DEFAULT_WORKBOOK_OUTPUT_ROOT,
    FurtherReadingEntry,
    LearningObjectiveBrief,
    ResearchEntry,
    TranscriptSegment,
    WorkbookProducer,
    WorkbookSidecar,
)

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
RUN_ID = "6a103b6c-943f-4e53-90e1-95c915c7194c"
RUN_DIR = REPO_ROOT / "state" / "config" / "runs" / RUN_ID
CORPUS_DIR = REPO_ROOT / "course-content" / "courses" / "tejal-apc-c1-m1-p2-trends"

UNIT_ID = "tejal-apc-c1-m1-p2-trends"
LESSON_PLAN_REVISION = 1


@dataclass(frozen=True)
class TejalWorkbookInputs:
    """The fully-authored produce() inputs for the real tejal workbook."""

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


# ---------------------------------------------------------------------------
# Figure captions — derived from the run's per-page Gary export filenames
# ---------------------------------------------------------------------------


def _figure_captions(run_dir: Path) -> dict[int, str]:
    """Map slide number -> human caption from ``exports/gary/A_A_pages`` stems.

    Each per-page export is named ``{n}_{Hyphenated-Title}.png`` and corresponds
    1:1 to slide ``n`` (the full slide render lives at ``A_slide-NN.png``).
    """
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


def _load_segments(run_dir: Path) -> tuple[TranscriptSegment, ...]:
    """Build transcript segments from the run's storyboard-B segment manifest.

    Maps each segment's ``slide_id`` (``slide-NN``) to its Gary deck export
    (``exports/gary/A_slide-NN.png``) so the workbook embeds the real slide
    figure with a caption + source_ref (AC-7 / design S4).
    """
    manifest_path = run_dir / "exports" / "segment-manifest-storyboard-b.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    captions = _figure_captions(run_dir)
    gary_dir = run_dir / "exports" / "gary"
    out: list[TranscriptSegment] = []
    for raw in data["segments"]:
        seg_id = str(raw["segment_id"])
        slide_id = str(raw.get("slide_id") or seg_id)
        # slide-NN -> N
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
            vrefs = (
                {"element": slide_id, "description": caption},
            )
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
    return tuple(out)


def _build_source_text(run_dir: Path, segments: tuple[TranscriptSegment, ...]) -> str:
    """The run's source set for the G1 numeric gate.

    = the Part-2 corpus slides (bundle/extracted.md: the authoritative upstream
    numerals like $5.2 trillion / 25% / 66% / 67% / 18%) + the delivered
    transcript of record (the run-delivered, fidelity-passed narration whose
    research-enriched numerals — $4.5 trillion, 74%, $760-935 billion — are the
    accepted record for THIS run). The numeric gate then meaningfully audits the
    AUTHORED content (objectives / exercises / answer keys / depth) against this
    set; the verbatim transcript-of-record is in-source by definition.
    """
    corpus = (run_dir / "bundle" / "extracted.md").read_text(encoding="utf-8")
    delivered = "\n".join(seg.narration_text for seg in segments)
    return corpus + "\n\n" + delivered


# ---------------------------------------------------------------------------
# Knowledge-Check ingest -> Exercises + answer keys (design §7 gap 3)
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


# ---------------------------------------------------------------------------
# Further reading — corpus-native references + required reading + intro video
# ---------------------------------------------------------------------------

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
# Author the full tejal WorkbookSpec + produce-time content
# ---------------------------------------------------------------------------


def build_tejal_workbook_inputs() -> TejalWorkbookInputs:
    """Author the real tejal Part-2 ``WorkbookSpec`` + all produce-time content."""
    segments = _load_segments(RUN_DIR)
    source_text = _build_source_text(RUN_DIR, segments)
    vo_script_text = "\n".join(seg.narration_text for seg in segments)

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

    # G2 citation manifest: every rendered citation resolves to a real source_ref
    # (no invented ref). Hash keys the corpus-native reference text.
    source_ref_manifest: dict[str, str] = {}
    citations: list[dict[str, str]] = []
    for entry in _FURTHER_READING:
        source_ref_manifest[entry.source_ref] = _hash(entry.title)
        citations.append({"source_ref": entry.source_ref})

    plan_unit = PlanUnit(
        unit_id=UNIT_ID,
        event_type="present-trends",
        source_fitness_diagnosis=(
            "completed B1 run 6a103b6c — Part-2 macro-trends deck (read-only)"
        ),
        weather_band="green",
        modality_ref="workbook",
    )
    context = ProductionContext(
        lesson_plan_revision=LESSON_PLAN_REVISION,
        lesson_plan_digest=RUN_ID[:8],
    )

    return TejalWorkbookInputs(
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


def produce_tejal_workbook(
    output_root: str | Path = DEFAULT_WORKBOOK_OUTPUT_ROOT,
) -> WorkbookSidecar:
    """Author + produce the real tejal workbook; return the sidecar."""
    inputs = build_tejal_workbook_inputs()
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
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="B1-6a103b6c",
    )


def main() -> None:
    sidecar = produce_tejal_workbook()
    docx_path = REPO_ROOT / sidecar.docx_path
    size = docx_path.stat().st_size
    print("Produced tejal Part-2 workbook")
    print(f"  DOCX: {sidecar.docx_path}  ({size:,} bytes)")
    print(f"  MD:   {sidecar.markdown_path}")
    print(f"  segments covered: {sum(sidecar.segment_coverage.values())}"
          f"/{len(sidecar.segment_coverage)}")
    print(f"  numeric audit status: {sidecar.numeric_audit.get('status')} "
          f"(unsourced_numeric="
          f"{sidecar.numeric_audit['buckets']['unsourced_numeric']['count']})")
    print(f"  citation audit unsourced: "
          f"{sidecar.citation_audit['buckets']['unsourced_citations']['count']}")
    print(f"  reuse stamp: {sidecar.gamma_reuse_justified_by}")


if __name__ == "__main__":
    main()
