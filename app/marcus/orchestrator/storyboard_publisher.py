"""Automatic ONLINE storyboard publication at storyboard review gates.

Operator-ratified S5 criterion 7 (2026-06-12): G2C approval means operator
approval of Storyboard A in its ONLINE interactive incarnation — publishing
is the pipeline's job, not an operator chore. This seam runs at the gate
pause, BEFORE the decision card is issued, by invoking the proven legacy
``skills/bmad-agent-marcus/scripts/generate-storyboard.py`` routine
(``generate`` + ``publish``) against the envelope's Gary contribution —
exactly the invocation validated by hand at Trial-3 cycle 3
(publish receipt: assets/storyboards/<trial-id>/index.html).

``StoryboardPublishError`` is a ``SpecialistDispatchError``: a publish
failure error-pauses the trial for ``trial recover`` (retry the gate node)
instead of killing the cycle or — worse — pausing at a gate whose review
surface never went up.
"""

from __future__ import annotations

import importlib.util
import json
import os
from argparse import Namespace
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.narration_join import join_narration_segments

REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_SCRIPT = (
    REPO_ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "generate-storyboard.py"
)
# Deployment-specific publishing targets live in state/config, not app code
# (Winston MUST-FIX 2, party review 2026-06-12).
PUBLISHER_CONFIG_PATH = REPO_ROOT / "state" / "config" / "storyboard-publisher.yaml"
# Storyboard review gates and which artifact they review. Keys are PAUSING
# gate codes: the runner fires this seam only where the walk actually pauses.
# Storyboard B publishes at G3 — node 08B (gate G3B) declares fold_with: G3,
# so G3B itself never pauses; cycle-5 live evidence 2026-06-12 (trial
# 036e7ff8) caught the original "G3B" key as unreachable and the G3 pause
# went up without its review surface. A manifest-driven pin now enforces
# that every roster key names a fold-TARGET gate (criterion 7: a storyboard
# gate must never pause blind).
STORYBOARD_GATES: dict[str, str] = {"G2C": "storyboard-A", "G3": "storyboard-B"}
SITE_REPO_URL_ENV = "STORYBOARD_SITE_REPO_URL"
TOKEN_ENV_VAR = "GITHUB_PAGES_TOKEN"


@lru_cache(maxsize=1)
def _publisher_config() -> dict[str, Any]:
    if not PUBLISHER_CONFIG_PATH.is_file():
        raise StoryboardPublishError(
            f"publisher config missing at {PUBLISHER_CONFIG_PATH}",
            tag="storyboard.config.missing",
        )
    loaded = yaml.safe_load(PUBLISHER_CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or not loaded.get("site_repo_url"):
        raise StoryboardPublishError(
            f"publisher config at {PUBLISHER_CONFIG_PATH} lacks site_repo_url",
            tag="storyboard.config.missing",
        )
    return loaded


class StoryboardPublishError(SpecialistDispatchError):
    """Raised when the online storyboard cannot be generated or published."""


def _load_generator_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "marcus_generate_storyboard", GENERATOR_SCRIPT
    )
    if spec is None or spec.loader is None:
        raise StoryboardPublishError(
            f"unable to load storyboard generator at {GENERATOR_SCRIPT}",
            tag="storyboard.generator.unloadable",
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_segment_manifest_for_b(
    *, run_dir: Path, irene_output: dict[str, Any]
) -> Path:
    """Transform Irene's Pass-2 contribution into the legacy segment-manifest YAML.

    The legacy routine's ``load_narration_by_slide_id`` expects a top-level
    ``segments:`` list with ``slide_id`` + ``narration_text`` per segment.
    Pass 2 emits ``narration_script`` (id + narration_text) and
    ``segment_manifest_deltas`` (id + metadata + visual_references whose
    ``perception_source`` names the real slide id) — joined here by segment id.
    """
    narration = irene_output.get("narration_script")
    if not isinstance(narration, list) or not narration:
        raise StoryboardPublishError(
            "storyboard-B publish requires Irene Pass-2 narration_script",
            tag="storyboard.input.missing-irene",
        )
    # Audio-segment arc: the join policy lives ONLY in narration_join (the
    # publisher, enrique synthesis, and G5 QA must agree byte-for-byte).
    segments = join_narration_segments(
        narration, irene_output.get("segment_manifest_deltas")
    )
    if not segments:
        raise StoryboardPublishError(
            "Irene Pass-2 deltas joined to zero slides; storyboard-B has no "
            "narration overlay to publish",
            tag="storyboard.input.missing-irene",
        )
    manifest_path = run_dir / "exports" / "segment-manifest-storyboard-b.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump({"segments": segments}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return manifest_path


def publish_storyboard_for_gate(
    *,
    gate_id: str,
    trial_id: str,
    production_envelope: Any,
    runs_root: Path,
) -> dict[str, Any] | None:
    """Generate + publish the gate's storyboard; return the publish receipt.

    Returns ``None`` for gates without a storyboard roster entry. Raises
    ``StoryboardPublishError`` (recoverable family) on any failure — a
    storyboard gate without its online review surface is the quality-theater
    class the operator VOIDed at attempt-4.
    """
    label = STORYBOARD_GATES.get(gate_id)
    if label is None:
        return None
    if not os.getenv(TOKEN_ENV_VAR):
        raise StoryboardPublishError(
            f"{TOKEN_ENV_VAR} is not set; cannot publish {label} for {gate_id}",
            tag="storyboard.publish.token-missing",
        )
    gary = production_envelope.latest_for_specialist("gary")
    if gary is None:
        raise StoryboardPublishError(
            f"{gate_id} reached with no gary contribution; {label} has nothing "
            "to publish (upstream starvation)",
            tag="storyboard.input.missing-gary",
        )

    run_dir = runs_root / str(trial_id)
    payload_path = run_dir / "exports" / "gary-dispatch-payload.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(gary.output, indent=2), encoding="utf-8")
    out_dir = run_dir / "exports" / f"{label}-pack"

    # Storyboard B overlays Pass-2 narration on the A pack and publishes to
    # its OWN slug — the manifest run_id drives both the Pages subdir and the
    # receipt name, so B must never collide with the A pack (Winston risk,
    # party consensus 2026-06-12).
    segment_manifest_path: Path | None = None
    pack_run_id = str(trial_id)
    if label == "storyboard-B":
        pack_run_id = f"{trial_id}-b"
        irene = production_envelope.latest_for_specialist("irene")
        if irene is None:
            raise StoryboardPublishError(
                f"{gate_id} reached with no irene Pass-2 contribution; "
                "storyboard-B has no narration overlay",
                tag="storyboard.input.missing-irene",
            )
        segment_manifest_path = _write_segment_manifest_for_b(
            run_dir=run_dir, irene_output=irene.output
        )

    module = _load_generator_module()
    try:
        generate_rc = module.cmd_generate(
            Namespace(
                payload=payload_path,
                out_dir=out_dir,
                asset_base=None,
                print_summary=False,
                strict=True,
                segment_manifest=segment_manifest_path,
                related_assets=None,
                run_id=pack_run_id,
                cluster_coherence_report=None,
                pass2_envelope=None,
            )
        )
    except Exception as exc:
        raise StoryboardPublishError(
            f"storyboard generate failed for {gate_id}: {exc}",
            tag="storyboard.generate.failed",
        ) from exc
    if generate_rc != 0:
        raise StoryboardPublishError(
            f"storyboard generate exited {generate_rc} for {gate_id}",
            tag="storyboard.generate.failed",
        )

    manifest_path = out_dir / "storyboard" / "storyboard.json"
    config = _publisher_config()
    site_repo_url = os.getenv(SITE_REPO_URL_ENV) or str(config["site_repo_url"])
    try:
        publish_rc = module.cmd_publish(
            Namespace(
                manifest=manifest_path,
                export_root=module.DEFAULT_EXPORTS_DIR,
                export_name=None,
                site_repo_url=site_repo_url,
                publish_subdir=str(
                    config.get("publish_subdir") or module.DEFAULT_PUBLISH_SUBDIR
                ),
                site_branch=str(config.get("site_branch") or "main"),
                token_env_var=TOKEN_ENV_VAR,
            )
        )
    except Exception as exc:
        raise StoryboardPublishError(
            f"storyboard publish failed for {gate_id}: {exc}",
            tag="storyboard.publish.failed",
        ) from exc
    if publish_rc != 0:
        raise StoryboardPublishError(
            f"storyboard publish exited {publish_rc} for {gate_id}",
            tag="storyboard.publish.failed",
        )

    receipt_path = (
        Path(module.DEFAULT_EXPORTS_DIR)
        / f"storyboard-{pack_run_id}-publish-receipt.json"
    )
    if not receipt_path.is_file():
        raise StoryboardPublishError(
            f"publish reported success but receipt is missing at {receipt_path}",
            tag="storyboard.publish.receipt-missing",
        )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    publish_url = receipt.get("publish_url")
    if not publish_url:
        raise StoryboardPublishError(
            "publish receipt carries no publish_url",
            tag="storyboard.publish.receipt-missing",
        )
    # Durable per-gate record beside the decision card.
    record_path = run_dir / f"storyboard-publish-{gate_id}.json"
    record_path.write_text(
        json.dumps(
            {"gate_id": gate_id, "label": label, **receipt}, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    return {"publish_url": publish_url, "record_path": record_path, "label": label}


__all__ = [
    "STORYBOARD_GATES",
    "StoryboardPublishError",
    "publish_storyboard_for_gate",
]
