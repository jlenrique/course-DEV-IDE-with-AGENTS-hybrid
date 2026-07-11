#!/usr/bin/env python3
"""W1 live evidence — ≥2 consumers resolve the same research packet.

Plants R4 live-minted ``entries.json`` into a minimal ``run.json`` contribution
(foundations SSOT shape), then proves glossary_writer + trends_projector share
``packet_digest``. Also witnesses Irene intake consume on the same entry set
(third consumer path; M3-safe ``_shared``).

Usage::

    python scripts/utilities/run_workbook_w1_live_evidence.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env", override=True)


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
    intake = consume_research_entries(
        entries,
        cluster_id="w1-live",
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
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=(contrib,),
    )
    now = datetime.now(UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="research-r4-live-replay",
        operator_id="w1-live",
        started_at=now,
        completed_at=now,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")
    return str(trial_id)


def main() -> int:
    from app.marcus.lesson_plan import research_packet as rp
    from app.specialists._shared.research_intake import (
        FabricatedCitationError,
        assert_no_fabricated_citations,
        consume_research_entries,
    )

    entries_path = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / "research-r4-20260710T233843Z"
        / "entries.json"
    )
    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"workbook-w1-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    if not entries_path.is_file():
        verdict = {
            "story": "workbook-w1",
            "pass": False,
            "fence": "r4-entries-absent",
            "expected": str(entries_path),
        }
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
        )
        return 2

    entries = json.loads(entries_path.read_text(encoding="utf-8"))
    assert isinstance(entries, list) and entries, "R4 entries must be non-empty"

    run_dir = out_dir / "run"
    trial_id = _plant_run(run_dir, entries)

    glossary = rp.resolve_for_glossary_writer(run_dir, require_usable=True)
    trends = rp.resolve_for_trends_projector(run_dir, require_usable=True)
    shared_digest = glossary.packet_digest == trends.packet_digest
    same_ids = [e["citation_id"] for e in glossary.entries] == [
        e["citation_id"] for e in trends.entries
    ]

    # Third consumer path: Irene intake on the same entry list (not a re-fetch).
    intake = consume_research_entries(
        list(glossary.entries),
        cluster_id="w1-live-irene",
        intake_mode="corroborate",
        evidence_bolster_active=True,
    )
    fabricate_red = False
    try:
        assert_no_fabricated_citations(
            [glossary.entries[0]["source_id"], "10.9999/FAKE-W1"],
            list(glossary.entries),
        )
    except FabricatedCitationError:
        fabricate_red = True

    # Shape pin: every usable entry carries required fields.
    shape_ok = all(
        set(rp.REQUIRED_ENTRY_FIELDS).issubset(entry.keys())
        for entry in glossary.entries
    )

    # Empty require_usable fails closed (negative witness).
    empty_dir = out_dir / "empty-run"
    from datetime import UTC as _UTC
    from uuid import UUID

    from app.models.runtime.production_envelope import (
        ProductionEnvelope,
        SpecialistContribution,
    )
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

    empty_id = UUID("12345678-1234-4234-8234-123456789abc")
    empty_contrib = SpecialistContribution.from_output(
        specialist_id="research_wiring",
        output={"research_entries": []},
        model_used="empty",
        node_id="04.55",
        provenance="fixture",
    )
    empty_env = ProductionEnvelope(
        trial_id=empty_id,
        contributions=(empty_contrib,),
        fixture_run=True,
    )
    empty_now = datetime.now(_UTC)
    empty_trial = ProductionTrialEnvelope(
        trial_id=empty_id,
        preset="explore",
        corpus_path="empty",
        operator_id="w1",
        started_at=empty_now,
        completed_at=empty_now,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=empty_env,
    )
    empty_dir.mkdir(parents=True, exist_ok=True)
    (empty_dir / "run.json").write_text(
        empty_trial.model_dump_json(), encoding="utf-8"
    )
    empty_fail_closed = False
    try:
        rp.resolve_for_glossary_writer(empty_dir, require_usable=True)
    except rp.ResearchPacketShapeError:
        empty_fail_closed = True

    steps = [
        {
            "step": "plant_r4_live_entries",
            "pass": glossary.status in {"ready", "degraded"} and len(glossary.entries) > 0,
            "entry_count": len(glossary.entries),
            "source": str(entries_path.relative_to(ROOT)),
        },
        {
            "step": "dual_consumer_same_digest",
            "pass": shared_digest and same_ids,
            "packet_digest": glossary.packet_digest,
            "consumers": ["glossary_writer", "trends_projector"],
        },
        {
            "step": "irene_intake_same_entries",
            "pass": intake.entries_consumed == len(glossary.entries) and fabricate_red,
            "entries_consumed": intake.entries_consumed,
            "fabricate_cite_path_red": fabricate_red,
        },
        {
            "step": "shape_pin_required_fields",
            "pass": shape_ok,
            "required_fields": sorted(rp.REQUIRED_ENTRY_FIELDS),
        },
        {
            "step": "empty_require_usable_fail_closed",
            "pass": empty_fail_closed,
        },
        {
            "step": "m3_safe_module",
            "pass": "import app.marcus.orchestrator"
            not in Path(rp.__file__).read_text(encoding="utf-8")
            and "from app.marcus.orchestrator"
            not in Path(rp.__file__).read_text(encoding="utf-8"),
            "module": "app.marcus.lesson_plan.research_packet",
        },
    ]
    all_pass = all(bool(s.get("pass")) for s in steps)
    verdict = {
        "story": "workbook-w1",
        "pass": all_pass,
        "trial_id": trial_id,
        "claim": (
            "Thin shared research-packet reader; ≥2 consumers same digest; "
            "no new packet builder; M3-safe"
        ),
        "steps": steps,
        "consumer_matrix_witness": [
            {
                "consumer": "glossary_writer",
                "access_mode": "resolve_for_glossary_writer",
                "artifact": "run.json#research_wiring@04.55",
                "packet_digest": glossary.packet_digest,
                "entry_count": len(glossary.entries),
            },
            {
                "consumer": "trends_projector",
                "access_mode": "resolve_for_trends_projector",
                "artifact": "run.json#research_wiring@04.55",
                "packet_digest": trends.packet_digest,
                "entry_count": len(trends.entries),
            },
            {
                "consumer": "irene_intake",
                "access_mode": "consume_research_entries(packet.entries)",
                "artifact": "same entries list (no re-fetch)",
                "entries_consumed": intake.entries_consumed,
            },
        ],
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# W1 Research packet SSOT — live proof",
                "",
                f"- pass: `{all_pass}`",
                f"- trial_id: `{trial_id}`",
                f"- packet_digest: `{glossary.packet_digest}`",
                f"- entries: `{len(glossary.entries)}` (from R4 live pack)",
                "",
                "## Steps",
                "",
                *[
                    f"- **{s['step']}**: `{'PASS' if s.get('pass') else 'FAIL'}`"
                    for s in steps
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
