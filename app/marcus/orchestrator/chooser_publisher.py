"""Publish the per-slide Storyboard-A A/B chooser to GitHub Pages at gate G2B.

At G2B both variants exist (Gary N-dispatched A+B; the per-slide pick has not happened
yet, so the resolver is still a no-op). We render the chooser page (A/B per slide + click
buttons) from Gary's per-slide PNGs and push a self-contained pack to gh-pages so the
client can pick slide-by-slide. The selection code they copy comes back as the G2B verdict
``edit_payload.slide_variant_selections`` and the per-slide resolver applies it on resume.
"""

from __future__ import annotations

import json
import os
import shutil
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.gates.section_07c.chooser_html_emitter import render_chooser_html
from app.marcus.orchestrator import gh_pages_publish as _ghp
from app.marcus.orchestrator.gh_pages_publish import load_hygiene_config
from app.marcus.orchestrator.slide_variant_selection import run_tag_for_trial
from app.specialists.dispatch_errors import SpecialistDispatchError

CHOOSER_GATES: frozenset[str] = frozenset({"G2B"})
SITE_REPO_URL_ENV = "STORYBOARD_SITE_REPO_URL"
TOKEN_ENV_VAR = "GITHUB_PAGES_TOKEN"
DEFAULT_SITE_REPO = "https://github.com/jlenrique/jlenrique.github.io"
_PUBLISHER_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "state" / "config" / "storyboard-publisher.yaml"
)
_TAG_PREFIX = "chooser.publish"


class ChooserPublishError(SpecialistDispatchError):
    """Recoverable failure publishing the per-slide chooser (mirrors storyboard publish family)."""


@lru_cache(maxsize=1)
def _hygiene_config() -> tuple[Any, Any, Any]:
    """(RetentionConfig|None, SizeGuardConfig, VerifyConfig) from the publisher config."""
    loaded: dict[str, Any] = {}
    if _PUBLISHER_CONFIG_PATH.is_file():
        parsed = yaml.safe_load(_PUBLISHER_CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            loaded = parsed
    return load_hygiene_config(loaded)


def _per_slide_options(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    per_slide: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            per_slide.setdefault(slide_id, []).append(row)
    slides: list[dict[str, Any]] = []
    for index, slide_id in enumerate(sorted(per_slide), start=1):
        variants = []
        for row in sorted(per_slide[slide_id], key=lambda r: str(r.get("dispatch_variant") or "A")):
            variant = str(row.get("dispatch_variant") or "A")
            variants.append(
                {
                    "variant": variant,
                    "image_url": f"{variant}_{slide_id}.png",
                    "_src": row.get("file_path"),
                }
            )
        slides.append({"slide_id": slide_id, "slide_index": index, "variants": variants})
    return slides


def publish_chooser_for_gate(
    *,
    gate_id: str,
    trial_id: str,
    production_envelope: Any,
    runs_root: Path,
) -> dict[str, Any] | None:
    """Publish the A/B chooser for ``gate_id``; return the receipt (or ``None`` if N/A)."""
    if gate_id not in CHOOSER_GATES:
        return None
    gary = production_envelope.latest_for_specialist("gary")
    rows = gary.output.get("gary_slide_output") if gary is not None else None
    if not isinstance(rows, list) or not rows:
        return None
    slides = _per_slide_options(rows)
    if not any(len(slide["variants"]) >= 2 for slide in slides):
        return None  # single-variant deck — nothing to choose
    token = os.getenv(TOKEN_ENV_VAR, "").strip()
    if not token:
        raise ChooserPublishError(
            f"{TOKEN_ENV_VAR} is not set; cannot publish the per-slide chooser for {gate_id}",
            tag="chooser.publish.token-missing",
        )

    run_dir = runs_root / str(trial_id)
    pack = run_dir / "exports" / "chooser-pack"
    if pack.exists():
        shutil.rmtree(pack)
    pack.mkdir(parents=True, exist_ok=True)
    emit_slides: list[dict[str, Any]] = []
    for slide in slides:
        variants = []
        for variant in slide["variants"]:
            src = variant.get("_src")
            if src and Path(str(src)).is_file():
                shutil.copyfile(str(src), pack / variant["image_url"])
            variants.append({"variant": variant["variant"], "image_url": variant["image_url"]})
        emit_slides.append(
            {
                "slide_id": slide["slide_id"],
                "slide_index": slide["slide_index"],
                "variants": variants,
            }
        )
    run_tag = run_tag_for_trial(trial_id)
    (pack / "index.html").write_text(render_chooser_html(emit_slides, run_tag), encoding="utf-8")

    site_repo = os.getenv(SITE_REPO_URL_ENV) or DEFAULT_SITE_REPO
    subdir = f"assets/storyboards/{trial_id}-chooser"
    publish_url = _git_publish_dir(pack, site_repo=site_repo, subdir=subdir, token=token)

    # A push that succeeded does NOT prove the page is live: at G2B this URL is handed
    # back to the client as the A/B verdict source — a lagging/errored Pages build would
    # deliver a dead URL (the 2026-07-03 incident). Verify-or-fail-loud (RA4). A not-live
    # result raises ChooserPublishError (recoverable → the gate error-pauses for
    # ``trial recover``). Skipped only when config sets verify_build=false.
    _r, _s, verify_cfg = _hygiene_config()
    if verify_cfg.enabled:
        _ghp.verify_build_after_push(
            publish_url,
            site_repo=site_repo,
            token=token,
            timeout=verify_cfg.timeout_s,
            error_cls=ChooserPublishError,
            tag_prefix=_TAG_PREFIX,
        )
    record = {
        "gate_id": gate_id,
        "label": "storyboard-A-chooser",
        "publish_url": publish_url,
        "run_tag": run_tag,
        "slide_count": len(emit_slides),
    }
    (run_dir / f"chooser-publish-{gate_id}.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


def _git_publish_dir(local_dir: Path, *, site_repo: str, subdir: str, token: str) -> str:
    """Clone the site, prune + size-guard, drop the pack, commit + push.

    Thin wrapper over the shared :func:`gh_pages_publish.git_publish_dir` (Task 1
    consolidation). Delegating fixes the prior TOKEN-LEAK-IN-ERROR (the shared helper
    scrubs ``x-access-token:{token}`` from any raised message) and adds the site-wide
    retention prune + size guard the chooser lacked. Public name preserved so callers
    and tests import it unchanged.
    """
    retention, size_guard, _verify = _hygiene_config()
    return _ghp.git_publish_dir(
        local_dir,
        site_repo=site_repo,
        subdir=subdir,
        token=token,
        retention=retention,
        size_guard=size_guard,
        error_cls=ChooserPublishError,
        tag_prefix=_TAG_PREFIX,
    )


__all__ = ["CHOOSER_GATES", "ChooserPublishError", "publish_chooser_for_gate"]
