"""Composition Smoke gate at slab-opener (Story 7a.1, AC-7.1-F, NFR-CG2).

Wires composer → Texas-stub contribution → ProductionEnvelope-append end-to-end.
Asserts: envelope contains exactly one Texas contribution with non-empty SHA256
digest. Exit 0 = PASS.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.marcus.orchestrator.directive_composer import (  # noqa: E402
    compose_directive,
    materialize_directive,
)
from app.models.runtime.production_envelope import (  # noqa: E402
    ProductionEnvelope,
    SpecialistContribution,
)


def main() -> int:
    trial_id = uuid4()
    with tempfile.TemporaryDirectory() as scratch:
        scratch_root = Path(scratch)
        corpus = scratch_root / "corpus"
        corpus.mkdir()
        (corpus / "intro.md").write_text("body", encoding="utf-8")
        (corpus / "chapter-1.md").write_text("body", encoding="utf-8")

        composed = compose_directive(corpus_path=corpus, run_id=str(trial_id))
        run_dir = scratch_root / "runs" / str(trial_id)
        directive_path, digest = materialize_directive(composed, run_dir)
        assert directive_path.exists()
        assert len(digest) == 64

        envelope = ProductionEnvelope(trial_id=trial_id)
        contribution = SpecialistContribution.from_output(
            specialist_id="texas",
            output={
                "bundle_reference": str(run_dir / "bundle"),
                "directive_path": directive_path.as_posix(),
                "smoke": True,
            },
            model_used="test-model-stub",
            cost_usd=0.0,
        )
        envelope.add_contribution(contribution)

        assert len(envelope.contributions) == 1
        only = envelope.contributions[0]
        assert only.specialist_id == "texas"
        assert only.output_digest
        assert len(only.output_digest) == 64

    print("PASS slab-7a-opener composition smoke")
    print(f"  trial_id={trial_id}")
    print(f"  directive_digest={digest[:16]}...")
    print(f"  texas_contribution_digest={only.output_digest[:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
