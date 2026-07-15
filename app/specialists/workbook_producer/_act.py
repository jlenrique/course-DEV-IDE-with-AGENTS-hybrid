"""workbook_producer act — deterministic in-graph adapter over WorkbookProducer.

The 07W producer is a thin, deterministic adapter (spec-07w §2). It reads the
CURRENTLY-RUNNING run and CONSUMES Irene's authored ``lesson_plan["collateral"]``
as the authoritative workbook blueprint (S7 canonical-arc generalization). The
sequence:

1. resolve the running run's directory (``RUNS_ROOT / run_id`` or an explicit
   ``run_dir`` replay override);
2. load transcript segments from the run's storyboard-B segment manifest and map
   each slide to its Gary deck export (figure embed, when present on disk);
3. build the source set for the G1 numeric gate from the run's
   ``bundle/extracted.md`` + the delivered narration;
4. read ``lesson_plan["collateral"]`` (from ``<run_dir>/run.json``) as the
   authoritative section / objective / depth-delta blueprint; the frozen G0
   enrichment card is a RESOLUTION OVERLAY (exercises, further-reading, answer
   keys, LO statements) layered on top — it may NOT author sections;
5. read the S6 ``research_entries`` (from ``run.json``) and render them under the
   G2 citation manifest; W2 also projects encyclopedia glossary articles from the
   shared research packet (``resolve_for_glossary_writer``); W3 projects
   research-trends + hot-topics (``resolve_for_trends_projector``);
6. honor the ``declaration`` discriminant (present+blueprint => produce;
   none/absent => explicit no-op skip);
7. run ``WorkbookProducer.produce(...)`` => MD + DOCX + G1/G2/AC audits => sidecar.

NO model client is touched here — pinned as a test invariant (mirrors the 07D.5
motion brick). Terminal leaf: emits the DOCX + canonical MD as a sidecar and puts
the ProducedAsset / sidecar refs on RunState; it feeds nothing downstream.

HONESTY BOUNDARY (do NOT over-claim): G1 numeric fidelity is symbol-only,
FAIL-mode. Word-form numerals are NOT gated — named gap
``braid-workbook-wordform-numeral-gap``. Learner-ready re-voiced prose is the
deferred S8 arc; this producer proves producer-generalization only.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import ValidationError

from app.marcus.lesson_plan.collateral_spec import CollateralSpec, WorkbookSpec
from app.marcus.lesson_plan.glossary_projection import (
    GlossaryArticleBrief,
    glossary_inputs_from_run,
)
from app.marcus.lesson_plan.prework_artifact import (
    WORKBOOK_BRIEF_FILENAME,
    WorkbookBriefArtifactV1,
    read_workbook_brief,
    workbook_brief_contribution_receipt,
)
from app.marcus.lesson_plan.prework_projection import PreWorkBrief, render_prework_markdown
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit
from app.marcus.lesson_plan.trends_projection import (
    ResearchTrendsBrief,
    trends_inputs_from_run,
)
from app.marcus.lesson_plan.workbook_enrichment import (
    corpus_native_further_reading,
    corpus_root_from_run,
    lesson_plan_from_run,
    load_enrichment_card,
    project_enrichment_to_workbook_inputs,
    research_entries_from_run,
)
from app.marcus.lesson_plan.workbook_producer import (
    DEFAULT_WORKBOOK_OUTPUT_ROOT,
    DuplicateCollateralIdError,
    FurtherReadingEntry,
    LearningObjectiveBrief,
    ResearchEntry,
    TranscriptSegment,
    WorkbookFidelityError,
    WorkbookProducer,
    WorkbookSidecar,
)
from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.runtime.economics import RUNS_ROOT
from app.specialists._shared.figure_tokens import _figures
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.workbook_producer.payload_contract import CONSUMED_PAYLOAD_KEYS

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "app" / "specialists" / "workbook_producer" / "config.yaml"

# Q1: the ``[evidence: src-NNN]`` markers Irene leaves on a plan unit's
# ``source_refs`` — the bridge from a collateral plan-unit id (``uNN``) to the
# enrichment source component (``src-NNN``) and thence its overlay LO
# (``lo-g0-NNN``).
_EVIDENCE_SRC_RE = re.compile(r"\[evidence:\s*(src-\d+)\]", re.IGNORECASE)

_DEFAULT_SEGMENT_MANIFEST_RELPATH = "exports/segment-manifest-storyboard-b.yaml"
_DEFAULT_CORPUS_RELPATH = "bundle/extracted.md"
_DEFAULT_LESSON_PLAN_REVISION = 1

# D1: NO tejal defaults. The plan-unit header derives from the run's real lesson
# plan / collateral / corpus (never a baked-in ``tejal…`` / ``present-trends``
# constant). Neutral fallbacks used only when the run carries no derivable label.
_OPEN_ID_SANITIZE_RE = re.compile(r"[^a-z0-9._-]+")
_FALLBACK_EVENT_TYPE = "deck-companion-workbook"
_FALLBACK_UNIT_ID = "deck-companion-workbook-unit"
_DEFAULT_LO_BLOOM = "understand"

# D4: honest recorded-empty reason for a run whose research leg minted no cited
# entries (retires the hardcoded "live-research leg deferred" note).
_RESEARCH_EMPTY_REASON = (
    "no cited research entries recorded on this run's research contribution "
    "(recorded explicitly-empty; no DOI'd entries fabricated)"
)

# S7 remediation item-3 — DOI honesty. A rendered research DOI is emitted as
# ``https://doi.org/{source_id}``; a well-formed DOI is required so a broken /
# fabricated link is NEVER silently rendered. Entries whose ``source_id`` fails
# this shape are EXCLUDED from the rendered DOI list and their omission is
# recorded with visible provenance (degrade-with-record, not fail-loud — one
# bad entry must not kill the workbook).
_DOI_SHAPE_RE = re.compile(r"^10\.\d{4,9}/\S+$")


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
# Run-data readers (segment manifest + corpus)
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
    fidelity-passed narration).
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


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Plan-unit derivation (D1 — generalize off the tejal config default)
# ---------------------------------------------------------------------------


def _sanitize_open_id(text: str | None, *, fallback: str) -> str:
    """Coerce free text to an ``OPEN_ID_REGEX``-valid slug (``^[a-z0-9._-]+$``)."""
    slug = _OPEN_ID_SANITIZE_RE.sub("-", (text or "").lower()).strip("-.")
    slug = slug[:80].strip("-.")
    return slug or fallback


def _derive_plan_unit_fields(
    lesson_plan: dict[str, Any] | None,
    collateral: dict[str, Any] | None,
    run_dir: Path,
) -> tuple[str, str]:
    """Derive ``unit_id`` / ``event_type`` from the run's REAL lesson plan / corpus.

    D1: never the ``tejal-apc-c1-m1-p2-trends`` / ``present-trends`` config
    default. Prefer a real plan-unit id + the lesson summary; degrade to the
    collateral section binding / run name; sanitize to the open-id shape.
    """
    unit_id = ""
    plan_units = lesson_plan.get("plan_units") if isinstance(lesson_plan, dict) else None
    if isinstance(plan_units, list) and plan_units and isinstance(plan_units[0], dict):
        unit_id = str(plan_units[0].get("unit_id") or "").strip()
    if not unit_id and isinstance(collateral, dict):
        sections = (collateral.get("workbook") or {}).get("sections") or []
        if sections and isinstance(sections[0], dict):
            unit_id = str(
                sections[0].get("learning_objective_id") or sections[0].get("section_id") or ""
            ).strip()
    unit_id = _sanitize_open_id(unit_id or run_dir.name, fallback=_FALLBACK_UNIT_ID)

    event_type = ""
    if isinstance(lesson_plan, dict):
        event_type = str(lesson_plan.get("lesson_summary") or "").strip()
    event_type = _sanitize_open_id(event_type, fallback=_FALLBACK_EVENT_TYPE)
    return unit_id, event_type


# D1b: the DISPLAY title is distinct from the open-id ``event_type`` slug. The
# H1 / DOCX heading reads a human-readable label (the raw un-slugged
# ``lesson_summary``, reasonably truncated) instead of the hyphenated 80-char
# open-id (which produced titles like "Workbook:
# this-lesson-builds-a-case-for-change-by-moving-from…").
_DISPLAY_TITLE_MAX = 120


def _derive_display_title(lesson_plan: dict[str, Any] | None, run_dir: Path) -> str:
    """Human-readable workbook title from the run's real ``lesson_summary``.

    Un-slugged (unlike the open-id ``event_type``): whitespace-collapsed and
    truncated at a word boundary. Degrades to the run name when the run carries
    no derivable summary.
    """
    summary = ""
    if isinstance(lesson_plan, dict):
        summary = str(lesson_plan.get("lesson_summary") or "").strip()
    summary = re.sub(r"\s+", " ", summary).strip()
    if not summary:
        return run_dir.name
    if len(summary) > _DISPLAY_TITLE_MAX:
        summary = summary[:_DISPLAY_TITLE_MAX].rsplit(" ", 1)[0].rstrip(" ,.;:—-") + "…"
    return summary


def _plan_unit_and_context(
    run_dir: Path,
    run_id: str | None,
    *,
    unit_id: str,
    event_type: str,
    source_fitness_diagnosis: str,
    revision: int,
) -> tuple[PlanUnit, ProductionContext]:
    digest_seed = str(run_id) if run_id else run_dir.name
    plan_unit = PlanUnit(
        unit_id=unit_id,
        event_type=event_type,
        source_fitness_diagnosis=source_fitness_diagnosis,
        weather_band="green",
        modality_ref="workbook",
    )
    context = ProductionContext(
        lesson_plan_revision=revision,
        lesson_plan_digest=digest_seed[:8],
    )
    return plan_unit, context


# ---------------------------------------------------------------------------
# Author the produce() inputs from Irene's collateral + the enrichment overlay
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkbookInputs:
    """The fully-authored produce() inputs for the in-graph workbook."""

    plan_unit: PlanUnit
    context: ProductionContext
    workbook_title: str
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
    research_empty_reason: str | None
    research_omitted_note: str | None
    glossary_articles: tuple[GlossaryArticleBrief, ...]
    glossary_empty_reason: str | None
    research_trends: ResearchTrendsBrief
    research_supplements: set[str] = field(default_factory=set)
    lo_overlay_loss: dict[str, object] | None = None
    pre_work: PreWorkBrief | None = None
    encounter_mode: Literal["recorded", "live"] = "recorded"
    render_profile: Literal["legacy", "presentation_support"] = "legacy"
    workbook_brief_receipt: dict[str, object] | None = None


def _research_inputs(
    run_dir: Path,
) -> tuple[tuple[ResearchEntry, ...], dict[str, str], str | None, str | None]:
    """Read the S6 cited research entries + build their G2 manifest slice (D4).

    F-2601: every rendered research DOI's ``source_ref`` is added to the G2
    citation manifest so a corrupt/absent research source_ref FAILS G2.
    F-2604: ``supports_segment_id`` is rendered only when present on the entry
    (never inferred). Zero rows -> an explicit recorded-empty reason.

    Remediation item-3 (DOI honesty): an entry whose ``source_id`` is not a
    well-formed DOI is EXCLUDED from the rendered list (its ``source_ref`` is NOT
    added to the manifest — nothing renders for it) and its omission is recorded
    with a visible provenance note. Degrade-with-record; never a broken/fabricated
    ``https://doi.org/`` link, never fail-loud on one bad entry.
    """
    raw = research_entries_from_run(run_dir)
    entries: list[ResearchEntry] = []
    manifest: dict[str, str] = {}
    omitted = 0
    for e in raw:
        if not isinstance(e, dict):
            continue
        source_ref = str(e.get("source_ref") or "")
        source_id = str(e.get("source_id") or "").strip()
        if not _DOI_SHAPE_RE.match(source_id):
            # Malformed / absent DOI -> exclude from the rendered DOI list.
            omitted += 1
            continue
        entries.append(
            ResearchEntry(
                citation_id=str(e.get("citation_id") or ""),
                title=str(e.get("title") or ""),
                source_ref=source_ref,
                provider=str(e.get("provider") or ""),
                source_id=source_id,
                source_hash=e.get("source_hash"),
                # F-2604: only if already present on the entry.
                supports_segment_id=e.get("supports_segment_id"),
                # R4 credibility (additive; absent on pre-R4 envelopes).
                evidence_hierarchy_tier=e.get("evidence_hierarchy_tier"),
                peer_reviewed=e.get("peer_reviewed"),
                provider_provenance=(
                    tuple(e["provider_provenance"])
                    if isinstance(e.get("provider_provenance"), list)
                    else None
                ),
                triangulation_status=e.get("triangulation_status"),
                reliability_score=e.get("reliability_score"),
            )
        )
        if source_ref:
            manifest[source_ref] = str(e.get("source_hash") or _hash(source_ref))
    reason = None if entries else _RESEARCH_EMPTY_REASON
    omitted_note = (
        None
        if omitted == 0
        else (
            f"{omitted} research entr{'y' if omitted == 1 else 'ies'} omitted — "
            "malformed/absent DOI (source_id failed DOI-shape validation); no "
            "broken link rendered"
        )
    )
    return tuple(entries), manifest, reason, omitted_note


def _unit_to_enrichment_lo_map(
    lesson_plan: dict[str, Any] | None, card: dict[str, Any] | None
) -> dict[str, str]:
    """Bridge collateral plan-unit ids (``uNN``) to enrichment LO ids (``lo-g0-NNN``).

    Q1 (LO-id namespace drift): the G0 enrichment overlay is keyed by
    ``lo-g0-NNN`` (one per enumerated corpus component ``src-NNN``); Irene's
    collateral binds sections to plan-unit ids ``uNN``. Both reference the SAME
    source component: a plan unit's ``source_refs`` carry ``[evidence: src-NNN]``
    markers, and each enrichment ``provisional_lo`` carries a structured
    ``source_refs[].source_id == src-NNN``. Compose ``uNN -> src-NNN ->
    lo-g0-NNN`` so ``overlay_lo.get("uNN")`` resolves instead of silently
    degrading. Returns an empty map when either side is absent — backward
    compatible: collateral bound DIRECTLY to ``lo-g0-NNN`` still resolves by the
    unmapped direct key.
    """
    if not isinstance(lesson_plan, dict) or not isinstance(card, dict):
        return {}
    # src-NNN -> lo-g0-NNN (structured; the first LO binding a src wins, stable).
    src_to_lo: dict[str, str] = {}
    for lo in card.get("provisional_los") or []:
        if not isinstance(lo, dict):
            continue
        objective_id = str(lo.get("objective_id") or "")
        if not objective_id:
            continue
        for ref in lo.get("source_refs") or []:
            if isinstance(ref, dict):
                source_id = str(ref.get("source_id") or "")
                if source_id and source_id not in src_to_lo:
                    src_to_lo[source_id] = objective_id
    if not src_to_lo:
        return {}
    # uNN -> lo-g0-NNN via the plan unit's [evidence: src-NNN] markers.
    unit_to_lo: dict[str, str] = {}
    for unit in lesson_plan.get("plan_units") or []:
        if not isinstance(unit, dict):
            continue
        unit_id = str(unit.get("unit_id") or "")
        if not unit_id or unit_id in unit_to_lo:
            continue
        for raw_ref in unit.get("source_refs") or []:
            matched = False
            for match in _EVIDENCE_SRC_RE.finditer(str(raw_ref)):
                lo_id = src_to_lo.get(match.group(1))
                if lo_id is not None:
                    unit_to_lo[unit_id] = lo_id
                    matched = True
                    break
            if matched:
                break
    return unit_to_lo


def _research_figure_supplements(
    research_entries: tuple[ResearchEntry, ...],
    further_reading: tuple[FurtherReadingEntry, ...],
    glossary_articles: tuple[GlossaryArticleBrief, ...],
    research_trends: ResearchTrendsBrief,
) -> set[str]:
    """Normalized figure tokens sourced from the run's research leg (B5).

    The G1 numeric gate audits the FULL workbook body (incl. the W2 glossary, W3
    trends, and S6 research references) against corpus+narration only. A numeral
    that legitimately originates from the research leg (a study title's ``$7``, a
    trend claim's ``30%``) is otherwise flagged ``unsourced_numeric`` and FAILS
    G1 -> a gate-failed pause. Declare those figures as research supplements so
    they clear without inflating the source text. Symbol-only (the named
    word-form gap remains). Tokens are the frozen-neck NORMALIZED forms
    (``percent:30`` / ``money-trillion:4.5``); ``_normalize_figure`` is idempotent
    on them, so they match the audit's narration key space verbatim.
    """
    parts: list[str] = []
    for entry in research_entries:
        parts.append(entry.title or "")
    for reading in further_reading:
        parts.append(reading.title or "")
        parts.append(reading.locator or "")
    for article in glossary_articles:
        parts.append(" ".join(filter(None, (article.term, article.headline, article.body))))
    if research_trends is not None:
        for claim in research_trends.trends:
            parts.append(claim.claim_text or "")
            parts.append(claim.title or "")
        for topic in research_trends.hot_topics:
            parts.append(topic.topic or "")
            parts.append(topic.rationale or "")
    return _figures("\n".join(parts))


def _authored_prose_figure_supplements(
    spec: WorkbookSpec,
    learning_objectives: tuple[LearningObjectiveBrief, ...],
    answer_keys: dict[str, str],
    pre_work: PreWorkBrief | None,
) -> set[str]:
    """Normalized figure tokens sourced from the run's AUTHORED pedagogy prose.

    The G1 numeric gate audits the FULL rendered workbook body against
    corpus+narration (plus the B5 research-leg supplements). But those cover only
    the transcript-derived text — NOT the depth-delta narrative + enrichment LO
    statements, the collateral exercise/answer-key prose, or the prework
    Scene/Promise/Friction prose. A symbol-numeral legitimately authored into any
    of those (e.g. an enrichment LO's ``88%``) but not verbatim in corpus+narration
    is otherwise flagged ``unsourced_numeric`` and HARD-PAUSES a legitimate
    workbook. These blocks are UPSTREAM-authored artifacts (Irene's collateral /
    the enrichment card / the validated prework brief) grounded in the source, not
    producer fabrications, so their figures are declared as G1 supplements —
    exactly the same mechanism the research leg uses (B5). This preserves the
    invariant's intent: a numeral that appears ONLY in producer-composed structural
    chrome (not corpus, narration, research, or these authored blocks) still fails
    G1. Symbol-only; the named word-form gap
    (``braid-workbook-wordform-numeral-gap``) is unchanged.
    """
    parts: list[str] = []
    for section in spec.sections:
        parts.append(section.title or "")
        parts.append(section.depth_delta.deferred_depth or "")
        parts.append(section.narrative_intent or "")
        for exercise in section.exercises:
            parts.append(exercise.prompt_intent or "")
    for lo in learning_objectives:
        parts.append(lo.statement or "")
    for worked in answer_keys.values():
        parts.append(worked or "")
    if pre_work is not None:
        parts.append(render_prework_markdown(pre_work))
    return _figures("\n".join(p for p in parts if p))


def build_workbook_inputs(
    run_dir: Path,
    *,
    config: dict[str, Any] | None = None,
    run_id: str | None = None,
    validated_brief: WorkbookBriefArtifactV1 | None = None,
) -> WorkbookInputs | None:
    """Author the produce() inputs from Irene's collateral blueprint + the run.

    Returns ``None`` when the run declares no workbook (``declaration == "none"``
    or absent collateral) — the caller records an explicit no-op skip (D3). Raises
    :class:`WorkbookProducerActError` when ``declaration == "present"`` but the
    blueprint is absent/unresolvable (D3 fail-loud).
    """
    cfg = config or _load_config()
    manifest_relpath = str(cfg.get("segment_manifest_relpath", _DEFAULT_SEGMENT_MANIFEST_RELPATH))
    corpus_relpath = str(cfg.get("corpus_relpath", _DEFAULT_CORPUS_RELPATH))
    revision = int(cfg.get("lesson_plan_revision", _DEFAULT_LESSON_PLAN_REVISION))

    # Run-DATA first (a run that reached 07W always has segments; absence = a
    # malformed run => fail loud, preserving the recoverable-error seam).
    segments = _load_segments(run_dir, manifest_relpath)
    source_text = _build_source_text(run_dir, corpus_relpath, segments)
    vo_script_text = "\n".join(seg.narration_text for seg in segments)

    # D2: Irene's authored collateral is the section/objective/depth authority
    # (read once off run.json; the collateral rides the irene_pass1 lesson_plan).
    lesson_plan = lesson_plan_from_run(run_dir)
    collateral = lesson_plan.get("collateral") if isinstance(lesson_plan, dict) else None
    if not isinstance(collateral, dict):
        collateral = None
    declaration = collateral.get("declaration") if isinstance(collateral, dict) else None

    # D3 + remediation item-4 (F-2801): the ONLY legal skips are absent
    # collateral or an explicit ``declaration=="none"``. Any OTHER value
    # (typo / garbage / malformed shape) must FAIL-LOUD — never a silent skip.
    # CollateralSpec's closed ``Literal`` + ``extra="forbid"`` red-reject it.
    if not isinstance(collateral, dict) or declaration == "none":
        return None  # explicit no-op skip (deck-only / absent collateral)
    try:
        cspec = CollateralSpec.model_validate(collateral)
    except ValidationError as exc:
        raise WorkbookProducerActError(
            "workbook collateral is malformed or the declaration is not a valid "
            "member of the closed set ('present' | 'none'); the workbook blueprint "
            "is absent or unresolvable",
            tag="workbook-producer.blueprint.unresolvable",
        ) from exc
    blueprint = cspec.workbook
    if blueprint is None or not blueprint.sections:  # defensive (model guards this)
        raise WorkbookProducerActError(
            "workbook collateral declaration is 'present' but carries no sections",
            tag="workbook-producer.blueprint.unresolvable",
        )

    # G0 enrichment overlay (resolution only — it may NOT author sections):
    # exercises (Bloom-leveled) by home objective, LO statements/Bloom, gated
    # further-reading, and the G2 citation/manifest pair.
    exercises_by_objective: dict[str, list[Any]] = {}
    overlay_lo: dict[str, LearningObjectiveBrief] = {}
    further_reading: tuple[FurtherReadingEntry, ...] = ()
    citations: list[dict[str, str]] = []
    source_ref_manifest: dict[str, str] = {}
    answer_keys: dict[str, str] = {}
    card = load_enrichment_card(run_dir)
    if card is not None:
        projection = project_enrichment_to_workbook_inputs(card)
        for sec in projection.spec.sections:
            exercises_by_objective.setdefault(sec.learning_objective_id, []).extend(sec.exercises)
        overlay_lo = {lo.objective_id: lo for lo in projection.learning_objectives}
        further_reading = projection.further_reading
        citations = list(projection.citations)
        source_ref_manifest = dict(projection.source_ref_manifest)
        answer_keys = dict(projection.answer_keys)

    # Q1: bridge collateral plan-unit ids (uNN) to enrichment LO ids (lo-g0-NNN)
    # so the overlay (keyed lo-g0-NNN) resolves against a uNN-bound section. Empty
    # when either side is absent OR the collateral binds lo-g0 ids directly (then
    # the unmapped direct-key lookup already resolves).
    unit_to_lo = _unit_to_enrichment_lo_map(lesson_plan, card)

    def _resolve_overlay_key(objective_id: str) -> str | None:
        """The overlay key for a bound objective: direct id, else the uNN bridge."""
        if objective_id in overlay_lo or objective_id in exercises_by_objective:
            return objective_id
        return unit_to_lo.get(objective_id)

    # Q2: populate the S6 References channel from corpus-native reference sources
    # (references/*.md + per-slide **References:** lines) when the run's corpus
    # carries them. Additive to the enrichment further-reading; de-duplicated by
    # source_ref; folded into the G2 citation manifest so the rendered references
    # pass the citation gate. A run whose corpus root is absent (e.g. a fixture)
    # contributes nothing — backward compatible.
    corpus_root = corpus_root_from_run(run_dir)
    if corpus_root is not None:
        existing_refs = {entry.source_ref for entry in further_reading}
        corpus_refs = tuple(
            entry
            for entry in corpus_native_further_reading(corpus_root)
            if entry.source_ref not in existing_refs
        )
        if corpus_refs:
            further_reading = further_reading + corpus_refs
            for entry in corpus_refs:
                source_ref_manifest.setdefault(entry.source_ref, _hash(entry.title))
                citations.append({"source_ref": entry.source_ref})

    # Sections: collateral is authoritative; overlay exercises (when present)
    # resolve into their HOME section by learning_objective_id.
    #
    # Remediation item-1 (MUST-FIX): two collateral sections may legally bind the
    # SAME learning_objective_id (the model does not forbid it). Attaching the
    # same overlay exercise objects to BOTH would duplicate exercise_id and crash
    # ``assert_unique_collateral_ids``. So overlay exercises attach to the FIRST
    # section binding a given objective only; later sections sharing that
    # objective keep their own collateral-authored exercises.
    sections = []
    bound_objectives: list[str] = []
    overlay_attached: set[str] = set()
    for sec in blueprint.sections:
        oid = sec.learning_objective_id
        bound_objectives.append(oid)
        overlay_key = _resolve_overlay_key(oid)
        overlay_ex = exercises_by_objective.get(overlay_key) if overlay_key else None
        # Dedup by the OVERLAY key (not the section id): two sections resolving the
        # SAME overlay LO must not both attach the same exercise objects (that
        # duplicates exercise_id and crashes assert_unique_collateral_ids).
        if overlay_ex and overlay_key not in overlay_attached:
            sec = sec.model_copy(update={"exercises": list(overlay_ex)})
            overlay_attached.add(overlay_key)
        sections.append(sec)
    # Remediation item-6: carry the blueprint's kind through the rebuild (single
    # value today; explicit so a future closed-set growth cannot silently revert).
    spec = WorkbookSpec(sections=sections, kind=blueprint.kind)

    # LO briefs: exactly one per distinct bound objective (no orphan / no
    # phantom). Statement/Bloom from the overlay; a bound objective with no
    # overlay resolution degrades with recorded in-workbook provenance (D2).
    distinct_objectives = list(dict.fromkeys(bound_objectives))
    resolved_los: list[LearningObjectiveBrief] = []
    unresolved_overlay: list[str] = []
    for oid in distinct_objectives:
        overlay_key = _resolve_overlay_key(oid)
        brief = overlay_lo.get(overlay_key) if overlay_key else None
        if brief is not None:
            # Re-key the resolved overlay brief onto the collateral's BOUND
            # objective id (uNN): the S1 no-orphan/no-phantom binding assertion
            # compares the brief's objective_id against the section bindings, so a
            # brief still keyed lo-g0-NNN would read as an orphan+phantom pair.
            if brief.objective_id != oid:
                brief = LearningObjectiveBrief(
                    objective_id=oid,
                    bloom_level=brief.bloom_level,
                    statement=brief.statement,
                )
            resolved_los.append(brief)
        else:
            unresolved_overlay.append(oid)
            resolved_los.append(
                LearningObjectiveBrief(
                    objective_id=oid,
                    bloom_level=_DEFAULT_LO_BLOOM,
                    statement=(
                        f"(objective statement unresolved for `{oid}` — no enrichment "
                        "overlay resolved this objective on this run)"
                    ),
                )
            )
    learning_objectives = tuple(resolved_los)

    # Q1: RECORD the unresolved-overlay count as a visible loss (never a silent
    # degrade). Only meaningful when an enrichment card was present (an overlay
    # was expected); a card-less run degrades every objective by design.
    lo_overlay_loss: dict[str, object] | None = None
    if card is not None and unresolved_overlay:
        logger.warning(
            "workbook LO overlay: %d of %d bound objective(s) resolved no "
            "enrichment overlay (unresolved: %s)",
            len(unresolved_overlay),
            len(distinct_objectives),
            unresolved_overlay,
        )
        lo_overlay_loss = {
            "unresolved_count": len(unresolved_overlay),
            "bound_count": len(distinct_objectives),
            "unresolved_objectives": list(unresolved_overlay),
            "note": (
                f"{len(unresolved_overlay)} of {len(distinct_objectives)} learning "
                "objective(s) resolved no enrichment overlay (statement/Bloom "
                f"degraded to placeholder): {', '.join(unresolved_overlay)}"
            ),
        }

    # D4: research entries + their G2 manifest slice (folded into the same
    # manifest; produce() adds the research citations to the G2 audit).
    (
        research_entries,
        research_manifest,
        research_empty_reason,
        research_omitted_note,
    ) = _research_inputs(run_dir)
    for source_ref, source_hash in research_manifest.items():
        source_ref_manifest.setdefault(source_ref, source_hash)

    # W2: encyclopedia glossary from shared research packet (same SSOT as W1).
    glossary_articles, glossary_empty_reason, _glossary_losses = glossary_inputs_from_run(run_dir)
    for article in glossary_articles:
        if article.source_ref and article.source_ref not in source_ref_manifest:
            source_ref_manifest[article.source_ref] = _hash(article.source_ref)

    research_trends = trends_inputs_from_run(run_dir)
    for claim in research_trends.trends:
        if claim.source_ref and claim.source_ref not in source_ref_manifest:
            source_ref_manifest[claim.source_ref] = _hash(claim.source_ref)
    for topic in research_trends.hot_topics:
        if topic.confidence == "unusable":
            continue
        for source_ref in topic.source_refs:
            if source_ref and source_ref not in source_ref_manifest:
                source_ref_manifest[source_ref] = _hash(source_ref)

    # D1: generalize the plan-unit header off the run's real lesson plan / corpus.
    unit_id, event_type = _derive_plan_unit_fields(lesson_plan, collateral, run_dir)
    source_fitness_diagnosis = (
        f"companion workbook for in-graph composed run {run_id or run_dir.name}"
    )
    plan_unit, context = _plan_unit_and_context(
        run_dir,
        run_id,
        unit_id=unit_id,
        event_type=event_type,
        source_fitness_diagnosis=source_fitness_diagnosis,
        revision=revision,
    )

    brief = validated_brief

    # B5: declare research-leg figures so G1 does not flag legitimate research
    # numerals (W2 glossary / W3 trends / S6 references) as unsourced.
    research_supplements = _research_figure_supplements(
        research_entries, further_reading, glossary_articles, research_trends
    )
    # G1 hardening: ALSO declare figures authored into the pedagogy prose blocks
    # (depth-delta / LO statements / exercises / answer keys / prework) — those are
    # upstream-authored, source-grounded, and not covered by corpus+narration, so a
    # legitimate numeral there must not hard-pause the workbook (mirrors B5).
    research_supplements = research_supplements | _authored_prose_figure_supplements(
        spec,
        learning_objectives,
        answer_keys,
        brief.payload.pre_work if brief else None,
    )

    display_title = _derive_display_title(lesson_plan, run_dir)

    return WorkbookInputs(
        plan_unit=plan_unit,
        context=context,
        workbook_title=display_title,
        spec=spec,
        segments=segments,
        source_text=source_text,
        learning_objectives=learning_objectives,
        answer_keys=answer_keys,
        further_reading=further_reading,
        research_entries=research_entries,
        citations=tuple(citations),
        source_ref_manifest=source_ref_manifest,
        vo_script_text=vo_script_text,
        research_empty_reason=research_empty_reason,
        research_omitted_note=research_omitted_note,
        glossary_articles=glossary_articles,
        glossary_empty_reason=glossary_empty_reason,
        research_trends=research_trends,
        research_supplements=research_supplements,
        lo_overlay_loss=lo_overlay_loss,
        pre_work=brief.payload.pre_work if brief else None,
        encounter_mode=brief.payload.encounter_mode if brief else "recorded",
        render_profile="presentation_support" if brief else "legacy",
        workbook_brief_receipt=(
            {
                "path": WORKBOOK_BRIEF_FILENAME,
                "payload_digest": brief.payload_digest,
                "status_summary": {
                    "scene": brief.payload.pre_work.scene.status,
                    "promise": brief.payload.pre_work.promise.status,
                },
                "warning_summary": list(brief.payload.warnings),
                "loss_summary": list(brief.payload.known_losses),
                "scene_receipt": brief.payload.scene_receipt.model_dump(mode="json"),
                "promise_receipt": brief.payload.promise_receipt.model_dump(mode="json"),
                "writer_receipts": [
                    receipt.model_dump(mode="json") for receipt in brief.payload.writer_receipts
                ],
            }
            if brief
            else None
        ),
    )


def _skip_output() -> dict[str, Any]:
    """The explicit no-op-skip contribution (D3): recorded, valid, no artifact."""
    marker = "workbook declared none; no artifact produced"
    return {
        "workbook": {
            "skipped": True,
            "reason": marker,
            "modality_ref": "workbook",
        },
        "workbook_producer": {
            "specialist_id": "workbook_producer",
            "skipped": True,
            "reason": marker,
        },
    }


def produce_workbook(state: RunState, payload: dict[str, Any]) -> WorkbookSidecar | None:
    """Assemble inputs from the running run + run WorkbookProducer.produce().

    Returns ``None`` when the run declares no workbook (D3 no-op skip).
    """
    config = _load_config()
    run_dir = _resolve_run_dir(state, payload)
    if not run_dir.exists():
        raise WorkbookProducerActError(
            f"workbook_producer run directory does not exist: {run_dir}",
            tag="workbook-producer.run-dir.absent",
        )
    run_id = getattr(state, "run_id", None)
    brief = _reconcile_workbook_brief_authority(state, run_dir)
    inputs = build_workbook_inputs(
        run_dir,
        config=config,
        run_id=str(run_id) if run_id is not None else None,
        validated_brief=brief,
    )
    if inputs is None:
        return None
    # B6: default the deliverable to a TRIAL-SCOPED path under ``<run_dir>/exports``
    # so the governed run inventory (which scans ``runs/<trial>``) captures + binds
    # the MD/DOCX to this trial, instead of the shared, unbindable, overwrite-prone
    # ``_bmad-output/artifacts/workbooks`` root. Precedence: an explicit payload
    # override wins (orchestrator/replay intent); an operator's genuinely
    # reconfigured ``config.output_root`` (i.e. NOT the shipped legacy default) is
    # honored; otherwise the trial-scoped path is the default. The shipped config
    # value equal to ``DEFAULT_WORKBOOK_OUTPUT_ROOT`` is treated as "not
    # reconfigured" so the legacy shared root no longer forces a non-trial path.
    explicit_output_root = payload.get("output_root")
    configured_output_root = config.get("output_root")
    if explicit_output_root:
        output_root: str = str(explicit_output_root)
    elif configured_output_root and configured_output_root != DEFAULT_WORKBOOK_OUTPUT_ROOT:
        output_root = str(configured_output_root)
    else:
        output_root = str(run_dir / "exports" / "workbooks")
    producer = WorkbookProducer(output_root=output_root)
    try:
        return producer.produce(
            inputs.plan_unit,
            inputs.context,
            workbook_title=inputs.workbook_title,
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
            research_empty_reason=inputs.research_empty_reason,
            research_omitted_note=inputs.research_omitted_note,
            glossary_articles=inputs.glossary_articles,
            glossary_empty_reason=inputs.glossary_empty_reason,
            research_trends=inputs.research_trends,
            research_supplements=inputs.research_supplements,
            lo_overlay_loss=inputs.lo_overlay_loss,
            pre_work=inputs.pre_work,
            encounter_mode=inputs.encounter_mode,
            render_profile=inputs.render_profile,
            workbook_brief_receipt=inputs.workbook_brief_receipt,
            # DP6 (spec landmine): workbook-only diff justifies reuse; do not force
            # a spurious fresh-gamma. Stamp the in-graph run id.
            diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
            reuse_sha=(str(run_id)[:8] if run_id is not None else "WORKING"),
        )
    except (WorkbookFidelityError, DuplicateCollateralIdError) as exc:
        # Remediation item-2: S7 feeds UNTRUSTED upstream collateral/research into
        # G1/G2/AC-5/id-uniqueness. A produce()-gate ValueError must error-PAUSE
        # recoverably (dispatch-family), not hard-kill the walk — re-raise as the
        # recoverable dispatch error (mirrors the kira/texas/motion fail seams).
        raise WorkbookProducerActError(
            f"workbook produce() gate failed on untrusted upstream inputs: {exc}",
            tag="workbook-producer.gate-failed",
        ) from exc


def _load_persisted_production_envelope(run_dir: Path) -> ProductionEnvelope | None:
    """Load the persisted ``ProductionEnvelope`` from ``<run_dir>/run.json``.

    The dispatch adapter NULLS ``state.production_envelope`` for EVERY specialist
    (per-component isolation invariant); workbook_producer is the only specialist
    that reads it (the 07W.1 brief-authority reconcile). But 07W runs AFTER the
    band nodes 07W.1-07W.4, which persist ``run.json`` (07W self-resolves from the
    RUN DIR), so the authoritative envelope is re-loadable from disk. Returns
    ``None`` when ``run.json`` is absent or unreadable so the envelope-absent path
    still degrades cleanly. Guarded: contained (a child of ``run_dir``) and not a
    symlink.
    """
    run_json = run_dir / "run.json"
    if run_json.is_symlink() or not run_json.is_file():
        return None
    try:
        trial = ProductionTrialEnvelope.model_validate_json(
            run_json.read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return None
    return trial.production_envelope


def _reconcile_workbook_brief_authority(
    state: RunState, run_dir: Path
) -> WorkbookBriefArtifactV1 | None:
    """Require exact contribution authority before activating presentation support."""
    envelope = state.production_envelope
    # The dispatch adapter nulls ``production_envelope`` on the isolated RunState;
    # re-load the persisted authority from the run dir so the 07W brief reconcile
    # runs its collision/legacy/real logic against the REAL envelope instead of
    # error-pausing on ``authority-missing``.
    if envelope is None:
        envelope = _load_persisted_production_envelope(run_dir)
    brief_path = run_dir / WORKBOOK_BRIEF_FILENAME
    if brief_path.is_symlink():
        raise WorkbookProducerActError(
            "workbook brief coordinate is a symlink",
            tag="workbook-brief.sidecar-invalid",
        )
    sidecar_exists = brief_path.is_file()
    if envelope is None:
        if sidecar_exists:
            raise WorkbookProducerActError(
                "workbook brief sidecar has no ProductionEnvelope authority",
                tag="workbook-brief.authority-missing",
            )
        return None
    legacy_matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "workbook_brief_stub"
        and contribution.node_id == "07W.1"
    )
    real_matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "workbook_brief"
        and contribution.node_id == "07W.1"
    )
    legacy = legacy_matches[0] if legacy_matches else None
    real = real_matches[0] if real_matches else None
    allowed = {"workbook_brief", "workbook_brief_stub"}
    collisions = tuple(
        contribution
        for contribution in envelope.contributions
        if (
            contribution.node_id == "07W.1"
            and contribution.specialist_id not in allowed
        )
        or (
            contribution.specialist_id in allowed
            and contribution.node_id != "07W.1"
        )
    )
    if (
        collisions
        or len(legacy_matches) > 1
        or len(real_matches) > 1
        or (legacy and real)
    ):
        raise WorkbookProducerActError(
            "workbook brief coordinates are contradictory",
            tag="workbook-brief.sidecar-mismatch",
        )
    if real is None:
        if legacy is not None:
            raise WorkbookProducerActError(
                "legacy workbook brief requires explicit 07W.1 re-entry",
                tag="workbook-brief.legacy-reentry-required",
            )
        if sidecar_exists:
            raise WorkbookProducerActError(
                "workbook brief sidecar has no real contribution authority",
                tag="workbook-brief.authority-missing",
            )
        return None
    try:
        artifact = read_workbook_brief(run_dir)
    except ValueError as exc:
        raise WorkbookProducerActError(str(exc), tag="workbook-brief.sidecar-invalid") from exc
    expected = workbook_brief_contribution_receipt(artifact)
    if real.output != expected:
        raise WorkbookProducerActError(
            "workbook brief contribution and sidecar receipt mismatch",
            tag="workbook-brief.sidecar-mismatch",
        )
    return artifact


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
        "citation_unsourced": sidecar.citation_audit["buckets"]["unsourced_citations"]["count"],
        "segment_coverage": sidecar.segment_coverage,
        "gamma_reuse_justified_by": sidecar.gamma_reuse_justified_by,
        "workbook_brief": sidecar.workbook_brief_receipt,
        "depth_receipt": sidecar.depth_receipt,
        "lo_overlay_loss": sidecar.lo_overlay_loss,
    }


def act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("workbook_producer act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    try:
        sidecar = produce_workbook(state, payload)
    except WorkbookProducerActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    if sidecar is None:
        # D3: declaration=="none" / absent collateral => explicit no-op skip.
        return {
            "model_resolution_trail": [
                *state.model_resolution_trail,
                _trail_entry(last_entry, tag="workbook-producer.skipped.declaration-none"),
            ],
            "cache_state": CacheState(
                cache_prefix=json.dumps(
                    _skip_output(),
                    sort_keys=True,
                    ensure_ascii=True,
                    separators=(",", ":"),
                    default=str,
                ),
                entries_count=entries_count + 1,
            ).model_dump(mode="json"),
        }
    output = {
        "workbook": _sidecar_refs(sidecar),
        "workbook_producer": {
            "specialist_id": "workbook_producer",
            "docx_path": sidecar.docx_path,
            "markdown_path": sidecar.markdown_path,
        },
    }
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
