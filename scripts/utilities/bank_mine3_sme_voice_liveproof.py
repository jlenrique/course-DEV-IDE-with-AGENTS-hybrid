"""Mine 3 liveproof: Tejal vs HAI diverge; unknown SME hard-fail."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.course_source.sme_registry import (  # noqa: E402
    SmeRegistryError,
    profiles_diverge,
    resolve_sme_profile,
)


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine3-per-sme-voice-{stamp}"
    )
    item_ev = evidence / "per-sme-voice"
    item_ev.mkdir(parents=True)

    tejal = resolve_sme_profile("tejal")
    hai = resolve_sme_profile("hai-510")
    phs = resolve_sme_profile("phs-620")
    diverged = profiles_diverge(tejal, hai)
    unknown_failed = False
    try:
        resolve_sme_profile("not-a-real-sme")
    except SmeRegistryError:
        unknown_failed = True

    payload = {
        "tejal": tejal.model_dump(mode="json"),
        "hai-510": hai.model_dump(mode="json"),
        "phs-620": phs.model_dump(mode="json"),
        "diverged_fields": diverged,
    }
    (run_dir / "sme-resolution-witness.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (item_ev / "sme-resolution-witness.json").write_bytes(
        (run_dir / "sme-resolution-witness.json").read_bytes()
    )

    predicates = {
        "tejal_bound": tejal.styleguide_id == "hil-2026-apc-crossroads-classic"
        and not tejal.fallback,
        "hai_unbound_gap": hai.fallback and hai.styleguide_id is None,
        "phs_unbound_gap": phs.fallback and phs.styleguide_id is None,
        "hai_not_tejal_guide": hai.styleguide_id != tejal.styleguide_id,
        "divergence_ge_1": len(diverged) >= 1,
        "attribution_diverges": tejal.attribution != hai.attribution,
        "unknown_sme_hard_fail": unknown_failed,
        "run_id": run_id,
        "diverged_fields": diverged,
    }
    passed = all(
        predicates[k]
        for k in predicates
        if k not in {"run_id", "diverged_fields"}
    )
    verdict = {
        "item": "per-sme-voice",
        "mine": "3",
        "pass": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "stamp": stamp,
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
