from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.marcus.orchestrator.directive_composer import compose_directive
from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn
from app.specialists.texas.graph import SANCTUM_DIR, build_texas_graph


def test_slab_7b_wave_1_opener_composition_smoke(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("source body", encoding="utf-8")
    directive = compose_directive(
        corpus_path=corpus,
        run_id=str(UUID("12345678-1234-4234-8234-123456789abc")),
    )
    returned = SpecialistReturn(
        specialist_id="directive-composer",
        verb="proceed",
        payload=directive.to_dict(),
    )
    envelope = SpecialistEnvelope(
        specialist_id="texas",
        payload_in={"directive": returned.model_dump(mode="json")},
    )

    assert build_texas_graph().nodes
    assert envelope.payload_in["directive"]["specialist_id"] == "directive-composer"
    before = json.dumps(sorted(p.name for p in SANCTUM_DIR.iterdir()))
    after = json.dumps(sorted(p.name for p in SANCTUM_DIR.iterdir()))
    assert before == after
