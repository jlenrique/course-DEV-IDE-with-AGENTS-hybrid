from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn
from app.specialists.texas.graph import SANCTUM_DIR, build_texas_graph


def test_slab_7b_wave_1_opener_composition_smoke(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("source body", encoding="utf-8")
    directive = {
        "run_id": str(UUID("12345678-1234-4234-8234-123456789abc")),
        "sources": [
            {
                "ref_id": "src-001",
                "provider": "local_file",
                "locator": "intro.md",
                "role": "primary",
                "description": "Current Section 02A-compatible smoke directive",
                "expected_min_words": 1,
            }
        ],
    }
    returned = SpecialistReturn(
        specialist_id="section-02a-composer",
        verb="proceed",
        payload=directive,
    )
    envelope = SpecialistEnvelope(
        specialist_id="texas",
        payload_in={"directive": returned.model_dump(mode="json")},
    )

    assert build_texas_graph().nodes
    assert envelope.payload_in["directive"]["specialist_id"] == "section-02a-composer"
    before = json.dumps(sorted(p.name for p in SANCTUM_DIR.iterdir()))
    after = json.dumps(sorted(p.name for p in SANCTUM_DIR.iterdir()))
    assert before == after
