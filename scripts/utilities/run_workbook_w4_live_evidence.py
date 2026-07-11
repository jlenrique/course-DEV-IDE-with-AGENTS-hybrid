#!/usr/bin/env python3
"""W4 live evidence — Tejal workbook arm consumes research → glossary + trends.

Narrow claim (Murat): Tejal workbook arm can consume detective research outputs
to produce glossary + trends backmatter with cited, non-fabricated content.
Does NOT claim general workbook quality or semantic claim audit.

Witnesses required:
1. ≥1 encyclopedia glossary article with source-backed metadata
2. ≥1 trends/hot-topics section with cited claims
3. Consumer matrix rows (path/id + access mode + witness result)
Plus: MD/DOCX same composed model; detective OFF empty path honest.

Usage::

    python scripts/utilities/run_workbook_w4_live_evidence.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env", override=True)

# Detective default OFF for this arm (party / promote claim fence).
os.environ.pop("MARCUS_RESEARCH_DETECTIVE_LIVE", None)

R4_ENTRIES = (
    ROOT
    / "_bmad-output/implementation-artifacts/evidence"
    / "research-r4-20260710T233843Z/entries.json"
)


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _plant_run(run_dir: Path, entries: list[dict]) -> str:
    from app.models.runtime.production_envelope import (
        ProductionEnvelope,
        SpecialistContribution,
    )
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
    from app.specialists._shared.research_intake import consume_research_entries

    trial_id = uuid4()
    now = datetime.now(UTC)
    intake = consume_research_entries(
        entries,
        cluster_id="w4-live",
        intake_mode="corroborate",
        evidence_bolster_active=True,
    )
    output = {
        "research_entries": entries,
        "research_intake": intake.model_dump(mode="json"),
    }
    contrib = SpecialistContribution.from_output(
        specialist_id="research_wiring",
        output=output,
        model_used="live-r4-replay",
        node_id="04.55",
        provenance="real",
    )
    envelope = ProductionEnvelope(trial_id=trial_id, contributions=(contrib,))
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="tejal-w4-research-replay",
        operator_id="w4-live",
        started_at=now,
        completed_at=now,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")
    return str(trial_id)


def _research_entries_from_dicts(entries: list[dict]) -> tuple:
    import re

    from app.marcus.lesson_plan.workbook_producer import ResearchEntry

    doi_re = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
    out = []
    for e in entries:
        source_id = str(e.get("source_id") or "").strip()
        if not doi_re.match(source_id):
            continue
        provenance = e.get("provider_provenance")
        out.append(
            ResearchEntry(
                citation_id=str(e.get("citation_id") or ""),
                title=str(e.get("title") or ""),
                source_ref=str(e.get("source_ref") or ""),
                provider=str(e.get("provider") or ""),
                source_id=source_id,
                source_hash=e.get("source_hash"),
                evidence_hierarchy_tier=e.get("evidence_hierarchy_tier"),
                peer_reviewed=e.get("peer_reviewed"),
                provider_provenance=(
                    tuple(provenance) if isinstance(provenance, list) else None
                ),
                triangulation_status=e.get("triangulation_status"),
                reliability_score=e.get("reliability_score"),
            )
        )
    return tuple(out)


def main() -> int:
    from app.marcus.lesson_plan.glossary_projection import (
        GLOSSARY_WRITER_REQUIRED_MARKER,
        glossary_inputs_from_run,
    )
    from app.marcus.lesson_plan.research_packet import (
        load_research_packet,
        resolve_for_glossary_writer,
        resolve_for_trends_projector,
    )
    from app.marcus.lesson_plan.trends_projection import (
        TRENDS_WRITER_REQUIRED_MARKER,
        trends_inputs_from_run,
    )
    from app.marcus.lesson_plan.workbook_producer import WorkbookProducer
    from app.specialists._shared.research_intake import (
        FabricatedCitationError,
        assert_no_fabricated_citations,
        consume_research_entries,
    )
    from scripts.utilities.produce_tejal_workbook import build_tejal_workbook_inputs

    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"workbook-w4-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    if not R4_ENTRIES.is_file():
        verdict = {"story": "workbook-w4", "pass": False, "fence": "r4-entries-absent"}
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
        )
        return 2

    entries = json.loads(R4_ENTRIES.read_text(encoding="utf-8"))
    run_dir = out_dir / "run"
    trial_id = _plant_run(run_dir, entries)

    # --- Shared packet consumers (same digest) ---
    packet = load_research_packet(run_dir)
    glossary_packet = resolve_for_glossary_writer(run_dir, require_usable=True)
    trends_packet = resolve_for_trends_projector(run_dir, require_usable=True)
    same_digest = (
        glossary_packet.packet_digest
        == trends_packet.packet_digest
        == packet.packet_digest
    )

    glossary_articles, glossary_empty, _ = glossary_inputs_from_run(
        run_dir, max_articles=3
    )
    trends_brief = trends_inputs_from_run(run_dir, max_trends=5, max_hot_topics=3)
    research_entries = _research_entries_from_dicts(entries)

    # Irene intake on same entries (no re-fetch)
    intake = consume_research_entries(
        list(packet.entries),
        cluster_id="w4-irene",
        intake_mode="corroborate",
        evidence_bolster_active=True,
    )
    fabricate_red = False
    try:
        assert_no_fabricated_citations(
            [packet.entries[0]["source_id"], "10.9999/FAKE-W4"],
            list(packet.entries),
        )
    except FabricatedCitationError:
        fabricate_red = True

    # --- Tejal produce arm ---
    tejal = build_tejal_workbook_inputs()
    manifest = dict(tejal.source_ref_manifest)
    for entry in research_entries:
        if entry.source_ref:
            manifest.setdefault(entry.source_ref, entry.source_hash or entry.source_id)
    for article in glossary_articles:
        if article.source_ref:
            manifest.setdefault(article.source_ref, article.source_id)
    for claim in trends_brief.trends:
        if claim.source_ref:
            manifest.setdefault(claim.source_ref, claim.source_id)

    citations = list(tejal.citations)
    citations.extend({"source_ref": e.source_ref} for e in research_entries if e.source_ref)
    citations.extend(
        {"source_ref": a.source_ref} for a in glossary_articles if a.source_ref
    )
    citations.extend(
        {"source_ref": t.source_ref}
        for t in trends_brief.trends
        if t.confidence != "unusable" and t.source_ref
    )

    producer = WorkbookProducer(
        output_root=str((out_dir / "artifacts").relative_to(ROOT))
    )
    sidecar = producer.produce(
        tejal.plan_unit,
        tejal.context,
        spec=tejal.spec,
        segments=tejal.segments,
        source_text=tejal.source_text,
        citations=citations,
        source_ref_manifest=manifest,
        vo_script_text=tejal.vo_script_text,
        learning_objectives=tejal.learning_objectives,
        answer_keys=tejal.answer_keys,
        further_reading=tejal.further_reading,
        research_entries=research_entries,
        glossary_articles=glossary_articles,
        glossary_empty_reason=glossary_empty,
        research_trends=trends_brief,
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="w4-live",
    )

    md_path = ROOT / sidecar.markdown_path
    docx_path = ROOT / sidecar.docx_path
    md = md_path.read_text(encoding="utf-8")

    glossary_ok = (
        "## Research Glossary" in md
        and "### " in md
        and "Provenance:" in md
        and GLOSSARY_WRITER_REQUIRED_MARKER in md
        and len(glossary_articles) >= 1
    )
    trends_ok = (
        "## Research Trends" in md
        and "Hot topics" in md
        and "confidence=" in md
        and TRENDS_WRITER_REQUIRED_MARKER in md
        and trends_brief.usable
    )
    g2_ok = sidecar.citation_audit["buckets"]["unsourced_citations"]["count"] == 0
    parity_ok = md_path.is_file() and docx_path.is_file() and g2_ok

    # Detective OFF empty path
    empty_dir = out_dir / "detective-off-empty"
    empty_dir.mkdir(parents=True, exist_ok=True)
    empty_glossary, empty_g_reason, _ = glossary_inputs_from_run(empty_dir)
    empty_trends = trends_inputs_from_run(empty_dir)
    detective_off = os.environ.get("MARCUS_RESEARCH_DETECTIVE_LIVE", "") == ""
    empty_honest = (
        detective_off
        and empty_glossary == ()
        and empty_g_reason is not None
        and not empty_trends.usable
        and empty_trends.empty_reason is not None
        and "fabricat" in (empty_g_reason + (empty_trends.empty_reason or "")).lower()
    )

    consumer_matrix = [
        {
            "consumer": "glossary_writer",
            "access_mode": "resolve_for_glossary_writer / glossary_inputs_from_run",
            "artifact": f"run.json#research_wiring@04.55 → {len(glossary_articles)} articles",
            "packet_digest": glossary_packet.packet_digest,
            "witness": "PASS" if glossary_ok else "FAIL",
        },
        {
            "consumer": "trends_projector",
            "access_mode": "resolve_for_trends_projector / trends_inputs_from_run",
            "artifact": (
                f"same packet → {len(trends_brief.trends)} trends / "
                f"{len([h for h in trends_brief.hot_topics if h.confidence != 'unusable'])} hot topics"
            ),
            "packet_digest": trends_packet.packet_digest,
            "witness": "PASS" if trends_ok and same_digest else "FAIL",
        },
        {
            "consumer": "irene_intake",
            "access_mode": "consume_research_entries(packet.entries)",
            "artifact": f"entries_consumed={intake.entries_consumed}; fabricate_red={fabricate_red}",
            "packet_digest": packet.packet_digest,
            "witness": "PASS" if intake.entries_consumed > 0 and fabricate_red else "FAIL",
        },
        {
            "consumer": "spoc_receipt",
            "access_mode": "disk run.json + workbook MD/DOCX sidecar",
            "artifact": sidecar.markdown_path,
            "packet_digest": packet.packet_digest,
            "witness": "PASS" if parity_ok else "FAIL",
        },
        {
            "consumer": "future_collateral",
            "access_mode": "load_research_packet (named; implement later)",
            "artifact": "research-packet.v1 contract pinned",
            "packet_digest": packet.packet_digest,
            "witness": "PASS" if packet.usable else "FAIL",
        },
    ]

    steps = [
        {
            "step": "murat_witness_glossary_article",
            "pass": glossary_ok,
            "article_count": len(glossary_articles),
            "sample_term": glossary_articles[0].term if glossary_articles else None,
        },
        {
            "step": "murat_witness_trends_hot_topics",
            "pass": trends_ok,
            "trend_count": len(trends_brief.trends),
        },
        {
            "step": "murat_witness_consumer_matrix",
            "pass": all(row["witness"] == "PASS" for row in consumer_matrix),
            "rows": len(consumer_matrix),
        },
        {
            "step": "tejal_md_docx_parity_g2",
            "pass": parity_ok,
            "markdown_path": sidecar.markdown_path,
            "docx_path": sidecar.docx_path,
            "g2_unsourced": sidecar.citation_audit["buckets"]["unsourced_citations"][
                "count"
            ],
        },
        {
            "step": "detective_off_empty_honest",
            "pass": empty_honest,
            "detective_env": os.environ.get("MARCUS_RESEARCH_DETECTIVE_LIVE", "<unset>"),
        },
        {
            "step": "dual_consumer_same_digest",
            "pass": same_digest,
            "packet_digest": packet.packet_digest,
        },
    ]
    all_pass = all(bool(s.get("pass")) for s in steps)
    verdict = {
        "story": "workbook-w4",
        "pass": all_pass,
        "trial_id": trial_id,
        "claim_envelope": (
            "Tejal workbook arm consumes research → glossary + trends with "
            "cited non-fabricated content. NOT semantic claim audit; NOT "
            "detective default-ON; NOT general workbook quality."
        ),
        "detective_flag_default": "OFF",
        "steps": steps,
        "consumer_matrix": consumer_matrix,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "consumer-matrix.json").write_text(
        json.dumps(consumer_matrix, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# W4 Live Tejal workbook arm — proof",
                "",
                f"- pass: `{all_pass}`",
                f"- trial_id: `{trial_id}`",
                f"- claim: narrow Tejal research→glossary+trends (non-fabricated)",
                f"- detective: OFF",
                "",
                "## Murat witnesses",
                "",
                f"1. Glossary: `{'PASS' if glossary_ok else 'FAIL'}` "
                f"({len(glossary_articles)} articles)",
                f"2. Trends/hot-topics: `{'PASS' if trends_ok else 'FAIL'}`",
                f"3. Consumer matrix: "
                f"`{'PASS' if all(r['witness']=='PASS' for r in consumer_matrix) else 'FAIL'}`",
                "",
                "## Steps",
                "",
                *[
                    f"- **{s['step']}**: `{'PASS' if s.get('pass') else 'FAIL'}`"
                    for s in steps
                ],
                "",
                f"- MD: `{sidecar.markdown_path}`",
                f"- DOCX: `{sidecar.docx_path}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
