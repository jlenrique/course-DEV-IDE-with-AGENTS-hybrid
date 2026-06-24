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
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app.gates.section_07c.chooser_html_emitter import render_chooser_html
from app.marcus.orchestrator.slide_variant_selection import run_tag_for_trial
from app.specialists.dispatch_errors import SpecialistDispatchError

CHOOSER_GATES: frozenset[str] = frozenset({"G2B"})
SITE_REPO_URL_ENV = "STORYBOARD_SITE_REPO_URL"
TOKEN_ENV_VAR = "GITHUB_PAGES_TOKEN"
DEFAULT_SITE_REPO = "https://github.com/jlenrique/jlenrique.github.io"


class ChooserPublishError(SpecialistDispatchError):
    """Recoverable failure publishing the per-slide chooser (mirrors storyboard publish family)."""


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
    user = site_repo.split("github.com/", 1)[1].split("/", 1)[0]
    pages_base = f"https://{user}.github.io"
    auth_repo = site_repo.replace("https://", f"https://x-access-token:{token}@", 1)
    temp_repo = Path(tempfile.mkdtemp(prefix="chooser-publish-"))
    try:
        _git(["clone", "--depth", "1", "--branch", "main", auth_repo, str(temp_repo)])
        _git(["config", "user.name", "app-marcus-bot"], cwd=temp_repo)
        _git(["config", "user.email", "app-marcus-bot@users.noreply.github.com"], cwd=temp_repo)
        target = temp_repo / subdir
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(local_dir, target)
        _git(["add", subdir], cwd=temp_repo)
        status = _git(["status", "--short", subdir], cwd=temp_repo)
        if status.strip():
            _git(["commit", "-m", f"Publish per-slide chooser {subdir}"], cwd=temp_repo)
            _git(["push", auth_repo, "HEAD:main"], cwd=temp_repo)
        return f"{pages_base}/{subdir}/index.html"
    except subprocess.CalledProcessError as exc:
        raise ChooserPublishError(
            f"chooser gh-pages publish failed: {exc}", tag="chooser.publish.failed"
        ) from exc
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)


def _git(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, timeout=180
    )
    return result.stdout


__all__ = ["CHOOSER_GATES", "ChooserPublishError", "publish_chooser_for_gate"]
