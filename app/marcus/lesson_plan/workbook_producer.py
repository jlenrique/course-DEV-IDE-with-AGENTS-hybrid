"""Workbook producer for the braid client deliverable (Braid Slice 1 / S2).

Audience: braid producers + reviewers consuming the 4th concrete
``ModalityProducer`` (after ``BlueprintProducer``). This module emits the
client **workbook companion** to the narrated deck — the dual-coding partner
that carries the transcript + a fuller narrative, exercises, and citations that
were deliberately kept OFF the glance-slides and out of heard-only narration.

Render path (DP3, binding):
    * **Markdown is canonical** — the citation-injection substrate S3 fills.
    * **DOCX is the client deliverable** — rendered FROM the same composed
      markdown model via ``python-docx`` (one source of truth; the deliverable
      cannot diverge from the canonical).
    * **PDF is DEFERRED to v-next** (named; requires a new on-disk dependency —
      pandoc/weasyprint/reportlab — none present). Never author "PDF/DOCX" as a
      single target.

Discipline notes:
    * Mirrors ``BlueprintProducer`` exactly for the deterministic skeleton:
      repo-root output containment, repo-relative asset paths, a default body
      renderer + an injectable seam, ``ProducedAsset`` return with
      ``fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}"``.
    * **Prose-delegation seam (Irene A4-3):** the Pass-2 transcript is the
      workbook's SCAFFOLD, not its text. The deterministic default embeds each
      segment verbatim under its ``segment_id`` AND emits an explicit
      ``REVOICE-REQUIRED`` marker so deixis-laden transcript text is never
      silently passed off as finished read-prose. An injectable
      ``prose_revoicer`` replaces the default body per segment without a
      producer-class change.
    * **L2 audit hook (FAIL-mode):** ``produce`` calls
      ``audit_numeric_provenance`` (read-only; the frozen-neck module is
      UNMODIFIED) and the producer asserts ``unsourced_numeric == 0`` at the
      workbook boundary (G1). The underlying module stays warn-only.
    * **id-uniqueness:** section_id / exercise_id binding boundary rejects
      duplicate ids (filed follow-on ``braid-collateral-id-uniqueness``).
    * **DP6 frozen-Gamma reuse:** slide-independent; the producer records a
      reuse stamp on the returned sidecar (workbook-only diff => reuse-OK).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml
from docx import Document

from app.marcus.lesson_plan.collateral_spec import WorkbookSpec
from app.marcus.lesson_plan.modality_producer import ModalityProducer
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit
from app.specialists._shared.source_fidelity_audit import audit_numeric_provenance
from scripts.utilities.slide_production_gate import (
    fresh_gamma_required,
    reuse_stamp,
)

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
DEFAULT_WORKBOOK_OUTPUT_ROOT: Final[str] = "_bmad-output/artifacts/workbooks"

# Prose-delegation review marker — the honesty guard that "transcript backbone"
# did NOT collapse into "workbook text" (mirrors BlueprintProducer's
# IRENE_REVIEW_MARKER discipline).
REVOICE_REQUIRED_MARKER: Final[str] = (
    "<!-- REVOICE-REQUIRED: writer (Paige/Sophia) -> self-contained read-prose; "
    "Irene validates -->"
)
HUMAN_REVIEW_SECTION_HEADING: Final[str] = "## Human Review Checkpoint"
IRENE_REVIEW_MARKER: Final[str] = "- [ ] Irene workbook review complete"

# Stable per-segment anchor format (AC-5 line-level traceability).
SEGMENT_ANCHOR_PREFIX: Final[str] = "segment:"

# G4 close-out note — this story makes NO reading-path generalization claim.
NO_READING_PATH_HALO_NOTE: Final[str] = (
    "<!-- G4: no reading-path halo; this workbook advances no "
    "fresh-naive-holdout / reading-path generalization claim -->"
)


# ``prose_revoicer`` seam: given a segment's id + verbatim narration text,
# returns the body prose to emit for that segment. The default keeps the
# verbatim text and appends a REVOICE-REQUIRED marker.
ProseRevoicer = Callable[[str, str], str]


class WorkbookScopeError(ValueError):
    """Raised when a plan unit / spec is not eligible for workbook production."""


class WorkbookFidelityError(ValueError):
    """Raised when an honesty-gate assertion fails at the workbook boundary."""


class DuplicateCollateralIdError(ValueError):
    """Raised when a section_id / exercise_id duplicate is detected.

    The asset->objective binding boundary enforces id-uniqueness (filed
    follow-on ``braid-collateral-id-uniqueness``).
    """


# ---------------------------------------------------------------------------
# Transcript-segment backbone (frozen tejal deck input)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TranscriptSegment:
    """One Pass-2 transcript segment read from the frozen segment manifest.

    Read directly from the raw manifest YAML (the on-disk shape is richer than
    the strict authoring projection); only the fields the workbook needs are
    projected here.
    """

    segment_id: str
    narration_text: str
    visual_file: str | None
    visual_references: tuple[dict[str, Any], ...]
    source_ref: str
    # Absolute, on-disk path to the figure image, resolved against the manifest's
    # bundle directory at load time (the manifest ``visual_file`` is
    # bundle-relative, e.g. ``gamma-export/...png`` — it does NOT resolve against
    # the repo root). ``None`` when the segment has no figure.
    visual_file_abs: str | None = None


def load_transcript_segments(manifest_path: str | Path) -> tuple[TranscriptSegment, ...]:
    """Load Pass-2 transcript segments from a segment-manifest YAML.

    Reads the raw manifest (offline, read-only). Each segment's ``id`` is the
    transcript-scaffold anchor (AC-5); ``narration_text`` is the VO/transcript
    text; ``visual_file`` + ``visual_references`` feed the figure embed (AC-7).
    ``source_ref`` defaults to the segment id when the manifest does not carry
    an explicit one (the thin S2 source set; S3 fills real refs).
    """
    path = Path(manifest_path)
    bundle_dir = path.resolve().parent
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "segments" not in data:
        raise WorkbookScopeError(
            f"segment manifest {path} missing top-level 'segments' list"
        )
    raw_segments = data["segments"]
    if not isinstance(raw_segments, list) or not raw_segments:
        raise WorkbookScopeError(f"segment manifest {path} has no segments")

    out: list[TranscriptSegment] = []
    seen_ids: set[str] = set()
    for raw in raw_segments:
        seg_id = raw.get("id")
        if not isinstance(seg_id, str) or not seg_id:
            raise WorkbookScopeError(f"segment manifest {path} has a segment with no 'id'")
        if seg_id in seen_ids:
            raise DuplicateCollateralIdError(
                f"duplicate transcript segment id {seg_id!r} in {path}"
            )
        seen_ids.add(seg_id)
        vrefs = raw.get("visual_references") or []
        visual_file = raw.get("visual_file")
        # Resolve the figure path against the BUNDLE directory (the manifest's
        # parent), NOT the repo root — the manifest path is bundle-relative.
        visual_file_abs: str | None = None
        if isinstance(visual_file, str) and visual_file:
            candidate = Path(visual_file)
            resolved = candidate if candidate.is_absolute() else bundle_dir / candidate
            if resolved.exists():
                visual_file_abs = str(resolved)
        out.append(
            TranscriptSegment(
                segment_id=seg_id,
                narration_text=str(raw.get("narration_text", "")),
                visual_file=visual_file,
                visual_references=tuple(v for v in vrefs if isinstance(v, dict)),
                source_ref=str(raw.get("source_ref") or seg_id),
                visual_file_abs=visual_file_abs,
            )
        )
    return tuple(out)


# ---------------------------------------------------------------------------
# id-uniqueness at the asset->objective binding boundary
# ---------------------------------------------------------------------------


def assert_unique_collateral_ids(spec: WorkbookSpec) -> None:
    """Reject duplicate section_id / exercise_id / goal binding ids.

    This is the agreed enforcement point for the filed follow-on
    ``braid-collateral-id-uniqueness``: the producer binds asset -> objective by
    these ids, so a duplicate would silently collide two bindings.
    """
    section_ids: list[str] = []
    exercise_ids: list[str] = []
    for section in spec.sections:
        section_ids.append(section.section_id)
        for exercise in section.exercises:
            exercise_ids.append(exercise.exercise_id)
    _reject_dupes(section_ids, label="section_id")
    _reject_dupes(exercise_ids, label="exercise_id")


def _reject_dupes(ids: Sequence[str], *, label: str) -> None:
    seen: set[str] = set()
    for value in ids:
        if value in seen:
            raise DuplicateCollateralIdError(
                f"duplicate {label} {value!r} at the workbook binding boundary"
            )
        seen.add(value)


# ---------------------------------------------------------------------------
# L2 audit FAIL-mode gate wrapper (the frozen-neck module stays UNMODIFIED)
# ---------------------------------------------------------------------------


def audit_workbook_numeric_fidelity(
    workbook_body_text: str,
    source_text: str,
    *,
    research_supplements: set[str] | None = None,
) -> dict:
    """Run the L2 numeric audit in FAIL-mode at the workbook boundary (G1).

    Calls the frozen-neck ``audit_numeric_provenance`` READ-ONLY and converts
    the warn-only return into a FAIL-mode gate: ``unsourced_numeric == 0`` must
    hold or :class:`WorkbookFidelityError` is raised. An un-auditable
    zero-denominator FAIL is ALSO raised — but only when the workbook body itself
    carries numeric tokens (a numeral that cannot be cleared against a
    numeral-free source); a genuinely numeral-free workbook is a clean pass. The
    underlying module is unmodified — the FAIL decision lives here.

    HONESTY BOUNDARY — word-form numerals are NOT gated (named gap, do NOT
    over-claim): the L2 figure tokenizer is SYMBOL-ONLY (``42%``, ``$7`` — the
    frozen-neck ``_FIGURE_RE``). Word-form numerals ("forty-two percent",
    "42 percent") are invisible to this gate, so a word-form numeral assertion
    passes un-audited. This is a deliberate, named limitation, not a guarantee of
    full numeric coverage. Filed as deferred follow-on
    ``braid-workbook-wordform-numeral-gap``; not solved here.

    Returns the report (attached to the run record / sidecar).
    """
    report = audit_numeric_provenance(
        workbook_body_text,
        source_text,
        research_supplements=research_supplements,
    )
    # The frozen-neck returns status="FAIL" (count==0) when EITHER side has zero
    # numeric tokens — the audit is UN-AUDITABLE (zero-denominator guard F2), not
    # a clean pass. The credibility risk this gate exists to catch is: the
    # workbook body ASSERTS a numeral but the source set carries NONE, so the
    # numeral cannot be cleared. That case (``narration_token_count > 0`` under a
    # FAIL) must RAISE — the OLD wrapper let it slip as "0 unsourced". When the
    # workbook body itself carries no numeric tokens, there is nothing to gate and
    # the (genuinely numeral-free) workbook passes; a FAIL there is a non-event,
    # not a violation, so we do NOT over-claim a fidelity breach.
    if report.get("status") == "FAIL" and report.get("narration_token_count", 0) > 0:
        raise WorkbookFidelityError(
            "G1 FAIL-mode: the L2 numeric audit is un-auditable for a workbook that "
            "ASSERTS numerals (zero-denominator: "
            f"{report.get('reason', 'source carries no numeric tokens')}). "
            "Treating un-auditable as a gate failure at the workbook boundary — a "
            "workbook numeral cannot be cleared against a numeral-free source set."
        )
    unsourced = report["buckets"]["unsourced_numeric"]["count"]
    if unsourced != 0:
        raise WorkbookFidelityError(
            f"G1 FAIL-mode: workbook body carries {unsourced} unsourced numeric "
            "assertion(s); every numeral must trace to the source set or a "
            "declared research supplement"
        )
    return report


# ---------------------------------------------------------------------------
# Citation-fidelity wiring (G2) — thin in S2; the assertion path is the deliverable
# ---------------------------------------------------------------------------


def audit_citation_fidelity(
    citations: Iterable[dict[str, str]],
    source_ref_manifest: dict[str, str],
) -> dict:
    """Assert every workbook citation resolves to a real ``source_ref`` (G2).

    Each citation is a ``{"source_ref": ...}`` mapping; the manifest maps
    ``source_ref -> source-hash``. FAIL-mode: ``unsourced_citations == 0``.
    Returns a report with the citation->source_ref->hash manifest attached.
    """
    citations = list(citations)
    unresolved: list[str] = []
    resolved: list[dict[str, str]] = []
    for citation in citations:
        ref = citation.get("source_ref", "")
        source_hash = source_ref_manifest.get(ref)
        if not ref or source_hash is None:
            unresolved.append(ref)
        else:
            resolved.append({"source_ref": ref, "source_hash": source_hash})
    report = {
        "buckets": {
            "unsourced_citations": {"count": len(unresolved), "refs": unresolved},
        },
        "resolved": resolved,
        "manifest": dict(source_ref_manifest),
    }
    if unresolved:
        raise WorkbookFidelityError(
            f"G2 FAIL-mode: {len(unresolved)} workbook citation(s) do not resolve "
            f"to a real source_ref: {unresolved!r}"
        )
    return report


def assert_exercise_fidelity(spec: WorkbookSpec) -> None:
    """G3: every exercise carries a Bloom level + a present answer-key source_ref."""
    for section in spec.sections:
        for exercise in section.exercises:
            if not exercise.bloom_level:
                raise WorkbookFidelityError(
                    f"G3: exercise {exercise.exercise_id!r} missing a Bloom level"
                )
            if not (exercise.answer_key_source_ref or "").strip():
                raise WorkbookFidelityError(
                    f"G3: exercise {exercise.exercise_id!r} answer key has no "
                    "resolvable source_ref"
                )


# ---------------------------------------------------------------------------
# Default prose revoicer (deterministic; honesty marker, no silent passthrough)
# ---------------------------------------------------------------------------


def default_prose_revoicer(segment_id: str, narration_text: str) -> str:
    """Embed the verbatim transcript text + the REVOICE-REQUIRED honesty marker.

    The default NEVER asserts deixis-laden transcript text is finished
    read-prose: the verbatim segment is preserved (the scaffold) and the marker
    flags that a writer (Paige/Sophia) must re-voice it into self-contained
    read-prose, with Irene validating behavioral intent.
    """
    return "\n".join(
        [
            REVOICE_REQUIRED_MARKER,
            f"> {narration_text.strip()}",
        ]
    )


# ---------------------------------------------------------------------------
# Markdown composition (canonical) — single source of truth for DOCX
# ---------------------------------------------------------------------------


@dataclass
class _ComposedDoc:
    """The composed canonical model: ordered (heading_level, heading, body) blocks.

    DOCX renders from THIS model so the deliverable cannot diverge from the
    canonical markdown.
    """

    title: str
    blocks: list[tuple[int, str, str]] = field(default_factory=list)
    # (abs_image_path_or_None, caption, source_ref) — abs path is the on-disk
    # image resolved against the bundle dir (None when the figure file is absent,
    # so the DOCX renderer skips the picture but still records the caption).
    figures: list[tuple[str | None, str, str]] = field(default_factory=list)


def _segment_anchor(segment_id: str) -> str:
    return f"<!-- {SEGMENT_ANCHOR_PREFIX}{segment_id} -->"


def compose_workbook(
    plan_unit: PlanUnit,
    context: ProductionContext,
    spec: WorkbookSpec,
    segments: Sequence[TranscriptSegment],
    *,
    prose_revoicer: ProseRevoicer,
) -> _ComposedDoc:
    """Compose the canonical workbook model from the spec + transcript backbone."""
    doc = _ComposedDoc(title=f"Workbook: {plan_unit.event_type}")

    # --- Overview ---
    doc.blocks.append(
        (
            2,
            "Overview",
            "\n".join(
                [
                    f"Unit ID: `{plan_unit.unit_id}`",
                    f"Fulfills target: "
                    f"`{plan_unit.unit_id}@{context.lesson_plan_revision}`",
                    "",
                    "This workbook is the read-in-depth companion to the narrated "
                    "deck: it carries the transcript, the fuller narrative deferred "
                    "off the glance-slides, the exercises, and the citations.",
                ]
            ),
        )
    )

    # --- Transcript-narrative (the prose-delegation seam + segment backbone) ---
    transcript_lines: list[str] = []
    for seg in segments:
        transcript_lines.append(_segment_anchor(seg.segment_id))
        transcript_lines.append(f"#### {seg.segment_id}")
        transcript_lines.append(prose_revoicer(seg.segment_id, seg.narration_text))
        transcript_lines.append("")
    doc.blocks.append((2, "Transcript-narrative", "\n".join(transcript_lines).rstrip()))

    # --- Section depth-deltas (the dual-coding legitimization of the tight VO) ---
    section_lines: list[str] = []
    for section in spec.sections:
        section_lines.append(f"### {section.title}")
        section_lines.append(
            f"Objective: `{section.learning_objective_id}` "
            f"(section `{section.section_id}`)"
        )
        section_lines.append(
            f"Depth deferred off the slide: {section.depth_delta.deferred_depth}"
        )
        if section.narrative_intent:
            section_lines.append(section.narrative_intent)
        section_lines.append("")
    doc.blocks.append((2, "Depth-delta narrative", "\n".join(section_lines).rstrip()))

    # --- Figures (image + caption + source_ref) ---
    figure_lines: list[str] = []
    for seg in segments:
        if not seg.visual_file or not seg.visual_references:
            continue
        vref = seg.visual_references[0]
        caption = str(
            vref.get("description") or vref.get("element") or seg.segment_id
        )
        source_ref = seg.source_ref
        # MD carries the readable bundle-relative ``![caption](path)`` reference;
        # the DOCX renderer embeds the BUNDLE-resolved absolute path (or skips if
        # the file is absent).
        figure_lines.append(_segment_anchor(seg.segment_id))
        figure_lines.append(f"![{caption}]({seg.visual_file})")
        figure_lines.append(f"*Figure — {caption}* (source_ref: `{source_ref}`)")
        figure_lines.append("")
        doc.figures.append((seg.visual_file_abs, caption, source_ref))
    doc.blocks.append((2, "Figures", "\n".join(figure_lines).rstrip()))

    # --- Exercises (Bloom level + source-grounded answer key) ---
    exercise_lines: list[str] = []
    for section in spec.sections:
        for exercise in section.exercises:
            exercise_lines.append(f"### Exercise `{exercise.exercise_id}`")
            exercise_lines.append(f"Bloom level: **{exercise.bloom_level}**")
            exercise_lines.append(exercise.prompt_intent)
            exercise_lines.append(
                f"Answer key (source_ref: `{exercise.answer_key_source_ref}`)"
            )
            exercise_lines.append("")
    doc.blocks.append((2, "Exercises", "\n".join(exercise_lines).rstrip()))

    # --- References (citation substrate; thin in S2, S3 fills it) ---
    reference_lines: list[str] = []
    for seg in segments:
        reference_lines.append(f"- `{seg.segment_id}` -> source_ref `{seg.source_ref}`")
    doc.blocks.append((2, "References", "\n".join(reference_lines).rstrip()))

    return doc


def render_markdown(doc: _ComposedDoc) -> str:
    """Render the canonical Markdown from the composed model."""
    lines: list[str] = [f"# {doc.title}", ""]
    for level, heading, body in doc.blocks:
        lines.append(f"{'#' * level} {heading}")
        lines.append("")
        if body:
            lines.append(body)
        lines.append("")
    lines.append(HUMAN_REVIEW_SECTION_HEADING)
    lines.append(IRENE_REVIEW_MARKER)
    lines.append(NO_READING_PATH_HALO_NOTE)
    lines.append("")
    return "\n".join(lines)


def render_docx_from_model(doc: _ComposedDoc, output_path: Path) -> None:
    """Render the DOCX deliverable FROM the same composed model (not parallel).

    The DOCX heading text is derived from ``doc.blocks`` (the same source the
    canonical Markdown renders from) so the deliverable cannot diverge.
    """
    document = Document()
    document.add_heading(doc.title, level=0)
    for level, heading, body in doc.blocks:
        document.add_heading(heading, level=min(level, 4))
        if body:
            for para in body.split("\n"):
                # SF-2: a figure that embeds as a real picture must NOT also leave
                # the literal ``![caption](path)`` markdown as a visible DOCX
                # paragraph (doubled / ugly chrome). Drop the raw image syntax;
                # the embedded picture + the ``*Figure — …*`` caption line carry it.
                if para.lstrip().startswith("![") and "](" in para:
                    continue
                document.add_paragraph(para)
    # Embed figures (AC-7): real image part (word/media/*) + caption + source_ref.
    for fig_path, caption, source_ref in doc.figures:
        if fig_path and Path(fig_path).exists():
            document.add_picture(str(fig_path))
        document.add_paragraph(f"Figure — {caption} (source_ref: {source_ref})")
    document.add_heading("Human Review Checkpoint", level=2)
    document.add_paragraph(IRENE_REVIEW_MARKER)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


# ---------------------------------------------------------------------------
# Output-root containment (mirror BlueprintProducer)
# ---------------------------------------------------------------------------


def _resolve_output_root(output_root: str | Path) -> Path:
    path = Path(output_root)
    if not path.is_absolute():
        path = REPO_ROOT / path
    # Resolve ``..`` traversal AND follow symlinks before the containment check.
    # ``os.path.normpath`` is LEXICAL — it collapses ``..`` but does NOT follow a
    # symlink, so an in-repo symlink pointing outside the repo would pass a
    # normpath containment check. ``Path.resolve()`` follows the link to its real
    # target, so a symlink escape is caught (mirrors BlueprintProducer discipline,
    # hardened against the symlink case). ``strict=False`` so a not-yet-created
    # output dir still resolves.
    path = path.resolve(strict=False)
    repo_root_resolved = REPO_ROOT.resolve(strict=False)
    try:
        path.relative_to(repo_root_resolved)
    except ValueError as exc:
        raise ValueError(
            f"WorkbookProducer output_root must live under the repo root; got {path}"
        ) from exc
    return path


def _relative_asset_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


# ---------------------------------------------------------------------------
# Sidecar carrying the audits + DOCX path + DP6 reuse stamp
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkbookSidecar:
    """Run-record sidecar returned alongside the ``ProducedAsset``.

    Carries the artifacts + honesty-gate reports + the DP6 frozen-reuse stamp.
    The canonical MD is the ``ProducedAsset.asset_path``; the DOCX path + audits
    ride here.
    """

    asset: ProducedAsset
    markdown_path: str
    docx_path: str
    numeric_audit: dict
    citation_audit: dict
    segment_coverage: dict[str, bool]
    gamma_reuse_justified_by: str | None
    deck_no_regression_eligible: bool


# ---------------------------------------------------------------------------
# WorkbookProducer
# ---------------------------------------------------------------------------


class WorkbookProducer(ModalityProducer):
    """Concrete producer for the ``workbook`` modality (Braid S2)."""

    modality_ref = "workbook"
    status = "ready"

    def __init__(
        self,
        *,
        output_root: str | Path = DEFAULT_WORKBOOK_OUTPUT_ROOT,
        prose_revoicer: ProseRevoicer | None = None,
    ) -> None:
        self._output_root = _resolve_output_root(output_root)
        self._prose_revoicer = prose_revoicer or default_prose_revoicer

    def produce(
        self,
        plan_unit: PlanUnit,
        context: ProductionContext,
        *,
        spec: WorkbookSpec,
        segments: Sequence[TranscriptSegment],
        source_text: str,
        citations: Iterable[dict[str, str]] | None = None,
        source_ref_manifest: dict[str, str] | None = None,
        vo_script_text: str = "",
        diff_files: Iterable[str] | None = None,
        reuse_sha: str = "WORKING",
    ) -> WorkbookSidecar:
        """Produce the workbook artifacts on the frozen deck inputs.

        Returns a :class:`WorkbookSidecar` (carrying the canonical
        :class:`ProducedAsset` + the DOCX path + honesty-gate reports + the DP6
        reuse stamp). Pure of network I/O; deterministic.
        """
        # id-uniqueness at the binding boundary (filed follow-on).
        assert_unique_collateral_ids(spec)
        # G3 exercise fidelity.
        assert_exercise_fidelity(spec)

        # Compose the canonical model (one source of truth).
        doc = compose_workbook(
            plan_unit,
            context,
            spec,
            segments,
            prose_revoicer=self._prose_revoicer,
        )
        markdown = render_markdown(doc)

        # --- G1: L2 numeric audit FAIL-mode over the workbook body. ---
        numeric_audit = audit_workbook_numeric_fidelity(markdown, source_text)

        # --- G2: citation-fidelity wiring (thin S2 set; path is the deliverable). ---
        citation_audit = audit_citation_fidelity(
            citations or [],
            source_ref_manifest or {},
        )

        # --- AC-8: dual-coding non-redundancy (workbook narrative ⊋ VO script). ---
        # The gate ALWAYS rides on the deliverable: when no explicit vo_script is
        # supplied, derive it from the transcript segments (the heard narration is
        # the VO). The comparison is over the NARRATIVE BODY ONLY (depth-delta +
        # re-voiced prose) — structural chrome (headings, "Overview",
        # "References", segment ids) must NOT mask a verbatim-VO body.
        effective_vo = vo_script_text or "\n".join(
            seg.narration_text for seg in segments
        )
        narrative_body = _narrative_body_text(doc)
        self._assert_workbook_superset_of_vo(narrative_body, effective_vo)

        # --- AC-5: segment coverage map (100% coverage, zero phantom). ---
        coverage = self._segment_coverage(markdown, segments)
        # The "no segment dropped" guarantee lives in the PRODUCER, not just the
        # test: every manifest segment must appear in the MD (line-level
        # traceable). Raise if any segment is absent from the deliverable.
        dropped = [seg_id for seg_id, present in coverage.items() if not present]
        if dropped:
            raise WorkbookFidelityError(
                f"AC-5: {len(dropped)} transcript segment(s) dropped from the "
                f"workbook (no coverage anchor): {dropped!r}"
            )

        # --- Write canonical MD + DOCX deliverable. ---
        stem = f"{plan_unit.unit_id}@{context.lesson_plan_revision}"
        md_path = self._output_root / f"{stem}.md"
        docx_path = self._output_root / f"{stem}.docx"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown, encoding="utf-8")
        render_docx_from_model(doc, docx_path)

        asset = ProducedAsset(
            asset_ref=f"workbook-{stem}",
            modality_ref=self.modality_ref,
            source_plan_unit_id=plan_unit.unit_id,
            asset_path=_relative_asset_path(md_path),
            fulfills=stem,
        )

        # --- DP6 reuse stamp: slide-independent => workbook-only diff is reuse-OK. ---
        reuse_justified_by: str | None
        if diff_files is not None and fresh_gamma_required(diff_files):
            reuse_justified_by = None
        else:
            reuse_justified_by = reuse_stamp(reuse_sha)

        return WorkbookSidecar(
            asset=asset,
            markdown_path=_relative_asset_path(md_path),
            docx_path=_relative_asset_path(docx_path),
            numeric_audit=numeric_audit,
            citation_audit=citation_audit,
            segment_coverage=coverage,
            gamma_reuse_justified_by=reuse_justified_by,
            # A frozen-reuse run is, by construction, ineligible to assert deck
            # no-regression (this story makes no deck-regression claim).
            deck_no_regression_eligible=False,
        )

    @staticmethod
    def _segment_coverage(
        markdown: str, segments: Sequence[TranscriptSegment]
    ) -> dict[str, bool]:
        """AC-5: build {segment_id: present} + reject phantom anchors."""
        manifest_ids = {seg.segment_id for seg in segments}
        coverage = {
            seg.segment_id: (_segment_anchor(seg.segment_id) in markdown)
            for seg in segments
        }
        # Phantom check: every anchor in the MD must be a real manifest id.
        anchor_re = re.compile(
            rf"<!--\s*{re.escape(SEGMENT_ANCHOR_PREFIX)}([^\s>]+)\s*-->"
        )
        for match in anchor_re.finditer(markdown):
            anchored = match.group(1)
            if anchored not in manifest_ids:
                raise WorkbookFidelityError(
                    f"AC-5: phantom segment anchor {anchored!r} not in the manifest"
                )
        return coverage

    @staticmethod
    def _assert_workbook_superset_of_vo(markdown: str, vo_script_text: str) -> None:
        """AC-8: workbook narrative is a PROPER superset of the VO script."""
        wb_tokens = set(_tokenize(markdown))
        vo_tokens = set(_tokenize(vo_script_text))
        # Strictly more content than the heard narration alone.
        if not (wb_tokens - vo_tokens):
            raise WorkbookFidelityError(
                "AC-8: workbook narrative carries no depth beyond the VO script "
                "(not a proper superset; dual-coding redundancy)"
            )
        # And the VO content is represented (true superset, not a disjoint rewrite).
        if vo_tokens and not (vo_tokens & wb_tokens):
            raise WorkbookFidelityError(
                "AC-8: workbook does not represent the VO script content "
                "(disjoint rewrite, not a superset)"
            )


# The blocks that constitute the workbook's NARRATIVE body (the dual-coding
# deliverable: re-voiced transcript prose + the depth-delta). Everything else
# ("Overview", "Figures", "Exercises", "References") is structural chrome that
# must NOT count toward the AC-8 superset.
_NARRATIVE_BLOCK_HEADINGS: Final[frozenset[str]] = frozenset(
    {"Transcript-narrative", "Depth-delta narrative"}
)


def _narrative_body_text(doc: _ComposedDoc) -> str:
    """Extract the narrative/depth body text for the AC-8 superset comparison.

    Returns ONLY the prose of the narrative blocks, with structural chrome
    stripped: HTML segment anchors, ``####``/``###`` headings, the
    REVOICE-REQUIRED marker, blockquote markers, and the deterministic
    ``Objective:`` / ``Depth deferred off the slide:`` scaffold lines. What
    remains is the re-voiced prose + the deferred-depth narrative — the content
    that must strictly exceed the heard VO.
    """
    lines: list[str] = []
    for _level, heading, body in doc.blocks:
        if heading not in _NARRATIVE_BLOCK_HEADINGS:
            continue
        for raw in body.split("\n"):
            stripped = raw.strip()
            if not stripped:
                continue
            if stripped.startswith("<!--"):  # segment anchors / markers
                continue
            if stripped.startswith("#"):  # #### segment-id / ### section headings
                continue
            if stripped == REVOICE_REQUIRED_MARKER:
                continue
            if stripped.startswith("Objective:") or stripped.startswith(
                "Depth deferred off the slide:"
            ):
                continue
            # Strip a leading blockquote marker but keep the quoted prose.
            if stripped.startswith(">"):
                stripped = stripped[1:].strip()
            lines.append(stripped)
    return "\n".join(lines)


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]


__all__ = [
    "DEFAULT_WORKBOOK_OUTPUT_ROOT",
    "HUMAN_REVIEW_SECTION_HEADING",
    "IRENE_REVIEW_MARKER",
    "NO_READING_PATH_HALO_NOTE",
    "REVOICE_REQUIRED_MARKER",
    "DuplicateCollateralIdError",
    "ProseRevoicer",
    "TranscriptSegment",
    "WorkbookFidelityError",
    "WorkbookProducer",
    "WorkbookScopeError",
    "WorkbookSidecar",
    "assert_exercise_fidelity",
    "assert_unique_collateral_ids",
    "audit_citation_fidelity",
    "audit_workbook_numeric_fidelity",
    "compose_workbook",
    "default_prose_revoicer",
    "load_transcript_segments",
    "render_docx_from_model",
    "render_markdown",
]
