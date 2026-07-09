"""Agent-level Gamma operations wrapper.

Bridges Gary's parameter decisions and the GammaClient API layer.
Handles style guide loading, parameter merging, generation execution,
polling, export, and artifact download.
"""

from __future__ import annotations

import base64
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    # Allow running this script directly without requiring manual PYTHONPATH.
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from scripts.api_clients.gamma_client import GammaClient  # noqa: E402

_QC_SCRIPTS = PROJECT_ROOT / "skills" / "quality-control" / "scripts"
if str(_QC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_QC_SCRIPTS))
from visual_fill_validator import validate_visual_fill  # noqa: E402

from app.marcus.orchestrator.gh_pages_publish import (  # noqa: E402
    GhPagesPublishError,
    RetentionConfig,
    SizeGuardConfig,
    SizeGuardRefusal,
    VerifyConfig,
    load_hygiene_config,
    project_published_size,
    prune_retention,
    verify_build_after_push,
)

logger = logging.getLogger(__name__)


REQUIRED_OUTBOUND_FIELDS = {
    "gary_slide_output",
    "quality_assessment",
    "parameter_decisions",
    "recommendations",
    "flags",
    "theme_resolution",
}

REQUIRED_THEME_RESOLUTION_FIELDS = {
    "requested_theme_key",
    "resolved_theme_key",
    "resolved_parameter_set",
    "mapping_source",
    "mapping_version",
    "user_confirmation",
}

_IMAGE_FILE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".heic", ".heif"}


def _require_gamma_api_key() -> None:
    """Fail fast when Gamma credentials are unavailable."""
    if os.environ.get("GAMMA_API_KEY", "").strip():
        return
    raise RuntimeError(
        "GAMMA_API_KEY is not set. Add it to the environment or to .env at the "
        "repository root before running gamma_operations generate commands."
    )


def _log_run_suffix(run_id: str | None) -> str:
    """Optional APP run correlation for logs (additive; no behavior change)."""
    if run_id is None or not str(run_id).strip():
        return ""
    return f" run_id={str(run_id).strip()}"
STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"
STYLE_PRESETS_PATH = PROJECT_ROOT / "state" / "config" / "gamma-style-presets.yaml"
STAGING_DIR = PROJECT_ROOT / "course-content" / "staging"


def _is_remote_http_ref(value: str) -> bool:
    """Return True when a string is an HTTP(S) URL."""
    parsed = urlparse(str(value).strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _sanitize_publish_segment(value: str) -> str:
    """Normalize a path-like segment while preventing traversal."""
    normalized = str(value).replace("\\", "/").strip().strip("/")
    if not normalized:
        raise ValueError("module_lesson_part must be a non-empty path segment")
    parts = [p for p in normalized.split("/") if p]
    if any(part in {".", ".."} for part in parts):
        raise ValueError("module_lesson_part must not contain traversal segments")
    return "/".join(parts)


def _run_git_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    display_args: list[str] | None = None,
) -> str:
    """Run a git command and raise RuntimeError with command context on failure."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            check=True,
            capture_output=True,
            text=True,
            env=full_env,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - exercised via integration
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout or "unknown git error"
        if (
            "requested url returned error: 403" in detail.lower()
            or "permission to" in detail.lower()
        ):
            detail = (
                f"{detail} :: authentication succeeded but write access was denied; "
                "verify GITHUB_PAGES_TOKEN has repository access and 'Contents: Read and write'"
            )
        safe_args = display_args or args
        raise RuntimeError(f"git command failed: {' '.join(safe_args)} :: {detail}") from exc
    return (completed.stdout or "").strip()


def _github_pages_base_url(repo_url: str) -> str:
    """Derive the GitHub Pages base URL from a GitHub repository URL.

    Non-HTTP(S) targets (e.g. a local bare repo used by offline hygiene tests) have no
    ``owner/repo`` Pages shape — fall back to the repo URL itself so callers still get a
    usable base rather than a raise.

    For HTTP(S) URLs the fallback is HOST-CONDITIONED: on a real GitHub host
    (``github.com`` / ``github.io``) a URL missing ``owner/repository`` is a production
    misconfiguration and RAISES fail-loud; any other host keeps the lenient fallback so
    non-github offline seams still work. The valid github.com behavior is unchanged.
    """
    parsed = urlparse(repo_url)
    if parsed.scheme not in {"http", "https"}:
        return repo_url.rstrip("/")
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        host = (parsed.hostname or "").lower()
        if host.endswith("github.com") or host.endswith("github.io"):
            raise ValueError("site_repo_url must include owner/repository")
        return repo_url.rstrip("/")
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if repo.lower() == f"{owner.lower()}.github.io":
        return f"https://{owner}.github.io"
    return f"https://{owner}.github.io/{repo}"


def _git_auth_env(token: str) -> dict[str, str]:
    """Build git environment enforcing non-interactive PAT-based auth."""
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode("ascii")
    return {
        "GIT_TERMINAL_PROMPT": "0",
        "GCM_INTERACTIVE": "Never",
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "credential.interactive",
        "GIT_CONFIG_VALUE_0": "never",
        "GIT_CONFIG_KEY_1": "http.https://github.com/.extraheader",
        "GIT_CONFIG_VALUE_1": f"AUTHORIZATION: basic {basic}",
    }


# ── Gamma export dimensions (16:9 PNG) ──────────────────────
_GAMMA_EXPORT_WIDTH = 2400
_GAMMA_EXPORT_HEIGHT = 1350


def _composite_full_bleed(
    source_png: Path,
    target_png: Path,
    *,
    width: int = _GAMMA_EXPORT_WIDTH,
    height: int = _GAMMA_EXPORT_HEIGHT,
) -> None:
    """Scale *source_png* to fill *width*×*height* and write to *target_png*.

    Used as a post-processing step after Gamma renders a literal-visual slide.
    Gamma's card template applies padding/margins that cannot be overridden via
    ``additionalInstructions``, so we composite the preintegration source image
    at the target resolution to guarantee a full-bleed result.

    The image is resized to cover the canvas (``LANCZOS``), cropping edges if the
    aspect ratio differs.  This preserves the central content at the highest
    quality while filling the entire slide.
    """
    try:
        from PIL import Image
    except ImportError:
        logger.warning(
            "Pillow not available — skipping full-bleed composite for %s",
            source_png.name,
        )
        return

    with Image.open(source_png) as img:
        img = img.convert("RGB")
        src_w, src_h = img.size

        # Cover-crop: scale so both dimensions meet or exceed target, then
        # center-crop to exact target size.
        scale = max(width / src_w, height / src_h)
        new_w = int(src_w * scale + 0.5)
        new_h = int(src_h * scale + 0.5)
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        left = (new_w - width) // 2
        top = (new_h - height) // 2
        cropped = resized.crop((left, top, left + width, top + height))
        cropped.save(target_png, format="PNG")


def publish_preintegration_literal_visuals(
    preintegration_map: dict[int, Path | str],
    module_lesson_part: str,
    *,
    site_repo_url: str,
    site_branch: str = "main",
    target_subdir: str = "assets/gamma",
    run_id: str | None = None,
    mode: str = "default",
    token_env_var: str = "GITHUB_PAGES_TOKEN",
    verify: bool = True,
) -> dict[str, Any]:
    """Publish preintegration literal-visual PNGs into the Git-hosted site.

    Returns additive metadata plus a ``url_map`` used to substitute diagram card URLs.

    Adopts the shared gh-pages hygiene primitives (Task 1b): a blobless clone, a
    retention prune of stale managed packs, a fail-loud published-size guard before
    push, and a verify-build-after-push poll. ``verify=False`` skips only the post-push
    HTTP poll (offline tests point ``site_repo_url`` at a local bare repo with no live
    endpoint); all other hygiene still runs.
    """
    safe_module_part = _sanitize_publish_segment(module_lesson_part)
    safe_target_subdir = _sanitize_publish_segment(target_subdir)
    mode_normalized = str(mode or "default").strip().lower()

    result: dict[str, Any] = {
        "repo_url": site_repo_url,
        "target_subdir": f"{safe_target_subdir}/{safe_module_part}",
        "preintegration_ready": False,
        "copied_count": 0,
        "pushed": False,
        "url_base": "",
        "substituted_cards": [],
        "skipped": [],
        "url_map": {},
    }

    if mode_normalized in {"ad-hoc", "adhoc"}:
        logger.info(
            "Literal-visual preintegration publish skipped in ad-hoc mode%s",
            _log_run_suffix(run_id),
        )
        return result

    if not preintegration_map:
        return result

    resolved_inputs: list[tuple[int, Path, str]] = []
    for card_number, raw_path in sorted(preintegration_map.items()):
        source = Path(str(raw_path).strip())
        if not source.is_absolute():
            source = (PROJECT_ROOT / source).resolve()
        if not source.is_file():
            result["skipped"].append({"card_number": card_number, "reason": "missing_local_path"})
            continue
        filename = source.name
        resolved_inputs.append((card_number, source, filename))

    if not resolved_inputs:
        return result

    token = (
        os.environ.get(token_env_var, "").strip()
        or os.environ.get("GH_PAGES_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    if not token:
        raise RuntimeError(
            "Literal-visual publish requires GITHUB_PAGES_TOKEN "
            "(legacy fallback: GH_PAGES_TOKEN, or GITHUB_TOKEN) in the environment"
        )

    git_auth_env = _git_auth_env(token)
    pages_base = _github_pages_base_url(site_repo_url)
    url_base = f"{pages_base}/{safe_target_subdir}/{safe_module_part}"
    result["url_base"] = url_base

    def _prim_git(git_args: list[str], *, cwd: Path | None = None) -> str:
        """Adapter matching the shared-primitive GitRunner contract (args exclude 'git')."""
        return _run_git_command(["git", *git_args], cwd=cwd, env=git_auth_env)

    publisher_cfg_path = PROJECT_ROOT / "state" / "config" / "storyboard-publisher.yaml"
    publisher_cfg: dict[str, Any] = {}
    if publisher_cfg_path.exists():
        loaded_cfg = yaml.safe_load(publisher_cfg_path.read_text(encoding="utf-8"))
        if isinstance(loaded_cfg, dict):
            publisher_cfg = loaded_cfg
    retention: RetentionConfig | None
    size_guard: SizeGuardConfig
    verify_cfg: VerifyConfig
    retention, size_guard, verify_cfg = load_hygiene_config(publisher_cfg)
    if retention is None:
        logger.warning(
            "gh-pages hygiene: retention pruning DISABLED (no managed_roots configured / "
            "publisher config absent) — published-site growth is unbounded until configured"
        )

    with tempfile.TemporaryDirectory(prefix="gamma-site-publish-") as temp_dir:
        temp_path = Path(temp_dir)
        repo_dir = temp_path / "site-repo"
        _run_git_command(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--branch",
                site_branch,
                site_repo_url,
                str(repo_dir),
            ],
            env=git_auth_env,
            display_args=[
                "git",
                "clone",
                "--filter=blob:none",
                "--branch",
                site_branch,
                site_repo_url,
                str(repo_dir),
            ],
        )
        _run_git_command(["git", "config", "user.name", "app-gamma-bot"], cwd=repo_dir)
        _run_git_command(
            ["git", "config", "user.email", "app-gamma-bot@users.noreply.github.com"],
            cwd=repo_dir,
        )

        # G1 — retention prune (staged; the pack published THIS run is protected by
        # identity). Runs BEFORE copying the new PNGs so stale managed packs are pruned
        # in the same publish commit.
        if retention is not None:
            rep = prune_retention(
                repo_dir,
                config=retention,
                current_subdir=f"{safe_target_subdir}/{safe_module_part}",
                git=_prim_git,
                logger=logger.info,
            )
            result["retention"] = {
                "deleted": len(rep.deleted),
                "reclaim_mb": round(rep.reclaim_bytes / 1048576, 1),
            }

        destination_dir = repo_dir / safe_target_subdir / safe_module_part
        destination_dir.mkdir(parents=True, exist_ok=True)

        tracked_rel_paths: list[str] = []
        for card_number, source, filename in resolved_inputs:
            destination = destination_dir / filename
            shutil.copy2(source, destination)
            rel_path = destination.relative_to(repo_dir).as_posix()
            tracked_rel_paths.append(rel_path)
            hosted_url = f"{url_base}/{filename}"
            result["url_map"][card_number] = hosted_url
            result["substituted_cards"].append(card_number)

        result["copied_count"] = len(tracked_rel_paths)
        _run_git_command(["git", "add", "--", *tracked_rel_paths], cwd=repo_dir)

        # STAGED-ONLY change detection: a whole-repo `git status --porcelain` also reports
        # unstaged/untracked worktree noise (e.g. Windows autocrlf line-ending
        # normalization on a fresh clone), so a no-op re-publish with nothing staged would
        # still enter the commit block and `git commit` would exit nonzero (abort). The
        # staged set (`git diff --cached --name-only`) still catches retention `git rm`
        # staged deletes AND the `git add`-ed new pack, while ignoring worktree noise.
        staged = _run_git_command(["git", "diff", "--cached", "--name-only"], cwd=repo_dir)

        if staged.strip():
            # G2 — size guard on the projected published tree (post-prune + new pack).
            # Runs ONLY when there ARE staged changes, so a no-op re-publish on an
            # over-budget repo does not fail loud. Fail-loud otherwise: SizeGuardRefusal
            # propagates so no commit/push occurs.
            try:
                project_published_size(repo_dir, config=size_guard, logger=logger.warning)
            except SizeGuardRefusal:
                logger.error(
                    "Size guard refused literal-visual publish for %s — no push",
                    result["target_subdir"],
                )
                raise

            message = f"Publish preintegration literal visuals for {safe_module_part}"
            if result.get("retention", {}).get("deleted"):
                message += " (+retention)"
            _run_git_command(["git", "commit", "-m", message], cwd=repo_dir)
            _run_git_command(
                ["git", "push", site_repo_url, f"HEAD:{site_branch}"],
                cwd=repo_dir,
                env=git_auth_env,
                display_args=["git", "push", site_repo_url, f"HEAD:{site_branch}"],
            )
            result["pushed"] = True

            # G3 — verify the pushed page is actually live (skipped offline via verify=False).
            if verify and verify_cfg.enabled and result["url_map"]:
                first_card = result["substituted_cards"][0]
                verify_build_after_push(
                    result["url_map"][first_card],
                    site_repo=site_repo_url,
                    token=token,
                    timeout=verify_cfg.timeout_s,
                    error_cls=GhPagesPublishError,
                    tag_prefix="gamma.publish",
                )
                result["verified_live"] = True

    result["preintegration_ready"] = bool(result["url_map"])
    logger.info(
        "Literal-visual preintegration publish complete: copied=%d pushed=%s target=%s%s",
        result["copied_count"],
        result["pushed"],
        result["target_subdir"],
        _log_run_suffix(run_id),
    )
    return result


def load_style_guide_gamma() -> dict[str, Any]:
    """Load Gamma-specific defaults from the style guide."""
    if not STYLE_GUIDE_PATH.exists():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8"))
    tool_params = data.get("tool_parameters", {})
    return tool_params.get("gamma", {})


def _load_style_guide_templates(path: Path | None = None) -> list[dict[str, Any]]:
    """Load Gamma template registry entries from style_guide.yaml."""
    p = path or STYLE_GUIDE_PATH
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return []
    gamma_cfg = data.get("tool_parameters", {}).get("gamma", {})
    templates = gamma_cfg.get("templates", []) if isinstance(gamma_cfg, dict) else []
    if not isinstance(templates, list):
        return []
    return [t for t in templates if isinstance(t, dict)]


def _matches_scope(candidate: Any, scope: str | None) -> bool:
    if scope is None:
        return True
    if candidate is None:
        return False
    c = str(candidate).strip()
    if not c:
        return False
    if c == "*" or c == scope:
        return True
    return scope.startswith(c)


def _matches_content_type(candidate: Any, content_type: str | None) -> bool:
    if content_type is None:
        return True
    if candidate is None:
        return False
    if isinstance(candidate, list):
        normalized = {str(v).strip() for v in candidate if str(v).strip()}
        return "*" in normalized or content_type in normalized
    c = str(candidate).strip()
    return c == "*" or c == content_type


def list_themes_and_templates(
    *,
    scope: str | None = None,
    content_type: str | None = None,
    limit: int = 20,
    client: GammaClient | None = None,
    style_guide_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Return live Gamma themes and registered templates filtered by context.

    This is the executable TP capability used by Gary to present available
    themes/templates before generation.
    """
    if client is None:
        client = GammaClient()

    templates = [
        t
        for t in _load_style_guide_templates(style_guide_path)
        if _matches_scope(t.get("scope"), scope)
        and _matches_content_type(
            t.get("content_type") or t.get("content_types"),
            content_type,
        )
    ]

    themes: list[dict[str, Any]] = []
    try:
        themes = client.list_themes(limit=limit)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("Gamma theme listing unavailable; continuing with templates only: %s", exc)

    return {
        "themes": themes,
        "templates": templates,
    }


# ---------------------------------------------------------------------------
# Style Preset Library
# ---------------------------------------------------------------------------

def _load_presets_file(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the raw presets list from YAML."""
    p = path or STYLE_PRESETS_PATH
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    return data.get("presets", [])


def list_style_presets(
    *,
    scope: str | None = None,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    """Return all style presets, optionally filtered by scope.

    Args:
        scope: If provided, return only presets whose scope matches.
            Matching rules: exact match, or preset scope ``"*"`` matches
            everything, or the requested scope starts with the preset
            scope (e.g., request ``"C1 > M1"`` matches preset ``"C1"``).
        path: Override preset file path (for testing).

    Returns:
        List of preset dicts (complete, including parameters and provenance).
    """
    presets = _load_presets_file(path)
    if scope is None:
        return presets
    matched: list[dict[str, Any]] = []
    for preset in presets:
        ps = preset.get("scope", "*")
        if ps == "*" or ps == scope or scope.startswith(ps):
            matched.append(preset)
    return matched


def load_style_preset(
    name: str,
    *,
    path: Path | None = None,
) -> dict[str, Any] | None:
    """Load a single style preset by name and return its parameters dict.

    Args:
        name: The preset name (e.g., ``"hil-2026-apc-nejal"``).
        path: Override preset file path (for testing).

    Returns:
        The ``parameters`` dict from the matching preset (ready for
        merge), or ``None`` if no preset with that name exists.
    """
    for preset in _load_presets_file(path):
        if preset.get("name") == name:
            return preset.get("parameters", {})
    return None


def resolve_style_preset(
    name: str | None = None,
    *,
    theme_id: str | None = None,
    scope: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Resolve the best-matching style preset parameters.

    Resolution order:
    1. If ``name`` is provided, look up by exact name.
    2. If ``theme_id`` is provided, find a preset that matches that theme.
    3. If ``scope`` is provided, find the most specific scope match.
    4. Return empty dict if no match.

    The returned dict contains flattened Gamma API parameters suitable for
    injection into the merge cascade at level 3.

    Returns:
        Parameter dict (may be empty).
    """
    presets = _load_presets_file(path)
    if not presets:
        return {}

    # 1. Exact name match
    if name:
        for p in presets:
            if p.get("name") == name:
                return _flatten_preset_params(p)

    # 2. Theme ID match
    if theme_id:
        for p in presets:
            if p.get("theme_id") == theme_id:
                return _flatten_preset_params(p)

    # 3. Scope match (most specific wins)
    if scope:
        candidates = list_style_presets(scope=scope, path=path)
        if candidates:
            # Sort by scope specificity: longer scope string = more specific
            candidates.sort(key=lambda c: len(c.get("scope", "")), reverse=True)
            # Skip wildcard-only matches unless it's the only option
            specific = [c for c in candidates if c.get("scope", "*") != "*"]
            best = specific[0] if specific else candidates[0]
            return _flatten_preset_params(best)

    return {}


def _flatten_preset_params(preset: dict[str, Any]) -> dict[str, Any]:
    """Extract and flatten parameters from a preset for merge.

    Handles two image style modes:

    **Approach A — Named stylePreset (tile selection):**
        ``imageOptions.stylePreset`` is a named value (e.g., ``illustration``,
        ``lineArt``, ``photorealistic``, ``abstract``, ``3D``).
        ``imageOptions.keywords`` are appended as comma-separated text to
        ``imageOptions.style`` to add specificity (``style`` is ignored by
        the API when stylePreset is named, but Gary can add keywords to
        ``additionalInstructions`` as fallback context).
        ``referenceImagePath`` is stripped — not used in named mode.

    **Approach B — Custom stylePreset (text prompt):**
        ``imageOptions.stylePreset`` is ``"custom"``.
        ``imageOptions.style`` is the full style prompt (1-500 chars).
        ``imageOptions.keywords`` are appended to the style prompt string.
        ``referenceImagePath`` is preserved as a hint for Marcus to use
        when crafting or refining the custom style prompt.

    Also pulls ``theme_id`` from the preset top level into ``themeId``.
    Also strips ``referenceImagePath`` from ``imageOptions`` in named mode
    (it's a design-intent field for Approach B only).
    """
    params = dict(preset.get("parameters", {}))
    if preset.get("theme_id") and "themeId" not in params:
        params["themeId"] = preset["theme_id"]

    img = params.get("imageOptions")
    if isinstance(img, dict):
        img = dict(img)  # shallow copy so we don't mutate the preset
        params["imageOptions"] = img

        style_preset_value = img.get("stylePreset", "")
        keywords = img.pop("keywords", None)
        kw_str = ", ".join(keywords) if keywords and isinstance(keywords, list) else ""

        if style_preset_value == "custom":
            # Approach B: style is the prompt; append keywords to it
            if kw_str:
                style_base = img.get("style", "").strip()
                img["style"] = f"{style_base}, {kw_str}" if style_base else kw_str
            # referenceImagePath stays — Marcus uses it to craft/refine the prompt
        else:
            # Approach A: named tile — style field is ignored by API for named presets.
            # Store keywords as a hint string in a separate key Gary can use in
            # additionalInstructions if needed. Remove referenceImagePath.
            if kw_str:
                img["_keywordsHint"] = kw_str  # Gary reads this, not sent to API
            img.pop("referenceImagePath", None)

    return params


VOCABULARY_TO_TEXTMODE = {
    "generate": "generate",
    "preserve": "preserve",
    "preserve-strict": "preserve",
}

VOCABULARY_TO_IMAGE_SOURCE = {
    "ai-generated": "aiGenerated",
    "no-images": "noImages",
    "theme-accent": "themeAccent",
    "user-provided": "aiGenerated",
}

VOCABULARY_LAYOUT_TEMPLATES = {
    "single-column": "Single column layout. One content area, full width.",
    "two-column": "Two-column parallel layout. Side-by-side comparison.",
    "full-bleed-image": "Full-bleed image layout. Image fills the slide.",
    "data-table": "Data table layout. Clean tabular presentation with headers.",
    "unconstrained": "",
}


def merge_parameters(
    style_defaults: dict[str, Any],
    content_template: dict[str, Any],
    envelope_overrides: dict[str, Any],
    *,
    style_preset: dict[str, Any] | None = None,
    fidelity_class: str = "creative",
) -> dict[str, Any]:
    """Merge parameters following the priority cascade.

    Priority (later wins):
        1. style guide defaults
        2. style preset (if provided)
        3. content type template
        4. context envelope overrides
        5. fidelity vocabulary enforcement (for literal slides)

    When fidelity_class is 'literal-text' or 'literal-visual', the
    fidelity-control vocabulary fields (text_treatment, image_treatment,
    layout_constraint, content_scope) override free-text
    additionalInstructions.
    """
    sources = [style_defaults]
    if style_preset:
        sources.append(style_preset)
    sources.extend([content_template, envelope_overrides])

    merged: dict[str, Any] = {}
    ai_parts: list[str] = []

    for source in sources:
        for key, value in source.items():
            if value is not None and value != "":
                if key == "additionalInstructions":
                    fragment = str(value).strip()
                    if fragment:
                        ai_parts.append(fragment)
                else:
                    merged[key] = value

    if fidelity_class in ("literal-text", "literal-visual"):
        text_treatment = merged.pop("text_treatment", "preserve")
        image_treatment = merged.pop("image_treatment", "no-images")
        layout_constraint = merged.pop("layout_constraint", "unconstrained")
        content_scope = merged.pop("content_scope", "exact-input-only")

        if fidelity_class == "literal-visual":
            layout_constraint = "full-bleed-image"

        merged["textMode"] = VOCABULARY_TO_TEXTMODE.get(text_treatment, "preserve")
        merged["imageOptions"] = {
            "source": VOCABULARY_TO_IMAGE_SOURCE.get(image_treatment, "noImages")
        }

        layout_instruction = VOCABULARY_LAYOUT_TEMPLATES.get(layout_constraint, "")
        scope_instruction = (
            "Output ONLY the provided text. Do not add content, steps, or diagrams."
            if content_scope == "exact-input-only"
            else ""
        )
        deterministic_ai = " ".join(filter(None, [layout_instruction, scope_instruction]))
        if deterministic_ai:
            merged["additionalInstructions"] = deterministic_ai
    else:
        merged.pop("text_treatment", None)
        merged.pop("image_treatment", None)
        merged.pop("layout_constraint", None)
        merged.pop("content_scope", None)
        if ai_parts:
            merged["additionalInstructions"] = " ".join(ai_parts)

    return merged


def execute_generation(
    params: dict[str, Any],
    *,
    slides: list[dict[str, Any]] | None = None,
    module_lesson_part: str = "",
    diagram_cards: list[dict[str, Any]] | None = None,
    client: GammaClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Production entry point for slide generation.

    Routes to mixed-fidelity two-call split when slides contain different
    fidelity classes, or to single-call generation when all slides share
    the same class (or no fidelity data is provided).

    Args:
        params: Merged parameter dict.
        slides: Optional list of slide dicts with 'fidelity' fields. If
            provided and mixed fidelity is detected, routes to two-call split.
        module_lesson_part: Identifier for doc naming (required for mixed fidelity).
        diagram_cards: Optional literal-visual image URL entries.
        client: Optional pre-configured GammaClient.
        run_id: Optional APP production run id for log correlation.

    Returns:
        For single-call: completed generation data.
        For mixed-fidelity: dict with gary_slide_output, provenance, generation_mode, calls_made.
    """
    if slides and bool(params.get("double_dispatch") or params.get("doubleDispatch")):
        base_run_id = run_id or module_lesson_part or "DOUBLE-DISPATCH"
        left_params = dict(params)
        right_params = dict(params)
        left_params.pop("double_dispatch", None)
        left_params.pop("doubleDispatch", None)
        right_params.pop("double_dispatch", None)
        right_params.pop("doubleDispatch", None)

        # Apply deliberate variant strategies if provided
        variant_strategies = params.get("variant_strategies")
        if isinstance(variant_strategies, dict):
            a_diffs = variant_strategies.get("A", {})
            b_diffs = variant_strategies.get("B", {})
            if isinstance(a_diffs, dict) and isinstance(b_diffs, dict):
                left_params.update(a_diffs)
                right_params.update(b_diffs)
                logger.info("Applied deliberate variant strategies: A=%s, B=%s", a_diffs, b_diffs)
            else:
                logger.warning("Invalid variant_strategies format, falling back to uniform stochastic")
        elif variant_strategies is not None:
            logger.warning("variant_strategies not a dict, falling back to uniform stochastic")
        else:
            logger.info("No variant_strategies provided, using uniform stochastic")

        # Set variant-specific export directories so both A and B get local PNGs.
        base_export_dir = (
            params.get("export_dir")
            or params.get("exportDir")
            or ""
        )
        if base_export_dir:
            base_export = Path(str(base_export_dir))
            left_params["export_dir"] = str(base_export)
            # Variant B exports to a sibling directory with -B suffix
            right_params["export_dir"] = str(
                base_export.parent / f"{base_export.name}-B"
            )
            Path(left_params["export_dir"]).mkdir(parents=True, exist_ok=True)
            Path(right_params["export_dir"]).mkdir(parents=True, exist_ok=True)
            logger.info(
                "Double-dispatch export dirs: A=%s, B=%s",
                left_params["export_dir"],
                right_params["export_dir"],
            )

        left = execute_generation(
            left_params,
            slides=slides,
            module_lesson_part=module_lesson_part,
            diagram_cards=diagram_cards,
            client=client,
            run_id=f"{base_run_id}:A",
        )
        right = execute_generation(
            right_params,
            slides=slides,
            module_lesson_part=module_lesson_part,
            diagram_cards=diagram_cards,
            client=client,
            run_id=f"{base_run_id}:B",
        )

        def _variantize_path(path_value: Any, variant: str) -> str:
            raw = str(path_value or "").strip()
            if not raw or _is_remote_http_ref(raw):
                return raw
            candidate = Path(raw)
            if candidate.suffix.lower() not in _IMAGE_FILE_SUFFIXES:
                return raw
            variant_path = candidate.with_name(f"{candidate.stem}_variant_{variant}{candidate.suffix}")
            if candidate.is_file() and variant_path != candidate:
                try:
                    shutil.copy2(candidate, variant_path)
                    return str(variant_path)
                except OSError:
                    return str(variant_path)
            return str(variant_path)

        def _scores(payload: dict[str, Any]) -> tuple[float, float]:
            qa = payload.get("quality_assessment", {}) if isinstance(payload, dict) else {}
            dims = qa.get("dimensions", {}) if isinstance(qa, dict) else {}
            overall = float(qa.get("overall_score", 0.0) or 0.0)
            vera = float(dims.get("embellishment_risk_control", overall) or overall)
            quinn = float(dims.get("layout_integrity", overall) or overall)
            return round(vera, 2), round(quinn, 2)

        def _with_variant(payload: dict[str, Any], variant: str) -> list[dict[str, Any]]:
            vera_score, quinn_score = _scores(payload)
            out: list[dict[str, Any]] = []
            for row in payload.get("gary_slide_output", []):
                if not isinstance(row, dict):
                    continue
                next_row = dict(row)
                next_row["dispatch_variant"] = variant
                next_row["selected"] = False
                next_row["file_path"] = _variantize_path(next_row.get("file_path"), variant)
                next_row["vera_score"] = vera_score
                next_row["quinn_score"] = quinn_score
                findings: list[str] = []
                if vera_score < 0.7:
                    findings.append("vera_below_threshold")
                if quinn_score < 0.7:
                    findings.append("quinn_below_threshold")
                next_row["findings"] = findings
                out.append(next_row)
            return out

        variant_a_rows = _with_variant(left, "A")
        variant_b_rows = _with_variant(right, "B")

        pair_index: dict[int, dict[str, Any]] = {}
        for row in [*variant_a_rows, *variant_b_rows]:
            card_number = int(row.get("card_number") or 0)
            pair = pair_index.setdefault(
                card_number,
                {
                    "card_number": card_number,
                    "slide_id": row.get("slide_id", f"{module_lesson_part}-card-{card_number:02d}"),
                    "variants": {},
                },
            )
            variant_key = str(row.get("dispatch_variant", "")).upper()
            pair["variants"][variant_key] = {
                "variant": variant_key,
                "slide_id": row.get("slide_id"),
                "file_path": row.get("file_path"),
                "vera_score": row.get("vera_score"),
                "quinn_score": row.get("quinn_score"),
                "findings": row.get("findings", []),
            }

        variant_pairs: list[dict[str, Any]] = []
        for key in sorted(pair_index.keys()):
            pair = pair_index[key]
            a = pair["variants"].get("A")
            b = pair["variants"].get("B")
            both_failed = False
            if a and b:
                a_gate = min(float(a.get("vera_score", 0.0) or 0.0), float(a.get("quinn_score", 0.0) or 0.0))
                b_gate = min(float(b.get("vera_score", 0.0) or 0.0), float(b.get("quinn_score", 0.0) or 0.0))
                both_failed = a_gate < 0.7 and b_gate < 0.7
            pair["needs_redispatch_or_manual"] = both_failed
            variant_pairs.append(pair)

        combined_rows = sorted(
            [*variant_a_rows, *variant_b_rows],
            key=lambda item: (int(item.get("card_number") or 0), str(item.get("dispatch_variant") or "")),
        )

        payload = {
            "gary_slide_output": combined_rows,
            "quality_assessment": {
                "overall_score": round(
                    (
                        float(left.get("quality_assessment", {}).get("overall_score", 0.0) or 0.0)
                        + float(right.get("quality_assessment", {}).get("overall_score", 0.0) or 0.0)
                    ) / 2,
                    2,
                ),
                "dimensions": {
                    "layout_integrity": round(
                        (
                            float(left.get("quality_assessment", {}).get("dimensions", {}).get("layout_integrity", 0.0) or 0.0)
                            + float(right.get("quality_assessment", {}).get("dimensions", {}).get("layout_integrity", 0.0) or 0.0)
                        ) / 2,
                        2,
                    ),
                    "parameter_confidence": round(
                        (
                            float(left.get("quality_assessment", {}).get("dimensions", {}).get("parameter_confidence", 0.0) or 0.0)
                            + float(right.get("quality_assessment", {}).get("dimensions", {}).get("parameter_confidence", 0.0) or 0.0)
                        ) / 2,
                        2,
                    ),
                    "embellishment_risk_control": round(
                        (
                            float(left.get("quality_assessment", {}).get("dimensions", {}).get("embellishment_risk_control", 0.0) or 0.0)
                            + float(right.get("quality_assessment", {}).get("dimensions", {}).get("embellishment_risk_control", 0.0) or 0.0)
                        ) / 2,
                        2,
                    ),
                },
                "embellishment_detected": bool(
                    left.get("quality_assessment", {}).get("embellishment_detected")
                    or right.get("quality_assessment", {}).get("embellishment_detected")
                ),
                "embellishment_details": [
                    *list(left.get("quality_assessment", {}).get("embellishment_details", [])),
                    *list(right.get("quality_assessment", {}).get("embellishment_details", [])),
                ],
            },
            "parameter_decisions": {
                **(left.get("parameter_decisions", {}) if isinstance(left, dict) else {}),
                "double_dispatch": True,
            },
            "recommendations": [
                "Double-dispatch enabled: review A/B variants and confirm exactly one winner per slide.",
            ],
            "flags": {
                **(left.get("flags", {}) if isinstance(left, dict) else {}),
                "double_dispatch": True,
                "needs_selection_gate": True,
                "needs_redispatch_pairs": [
                    pair["card_number"]
                    for pair in variant_pairs
                    if pair.get("needs_redispatch_or_manual")
                ],
            },
            "theme_resolution": left.get("theme_resolution", {}),
            "provenance": [
                {
                    "card_number": row.get("card_number"),
                    "source_call": row.get("fidelity", "creative"),
                    "generation_id": row.get("generation_id", ""),
                    "fidelity": row.get("fidelity", "creative"),
                    "dispatch_variant": row.get("dispatch_variant"),
                }
                for row in combined_rows
            ],
            "generation_mode": "double-dispatch",
            "calls_made": int(left.get("calls_made", 0) or 0) + int(right.get("calls_made", 0) or 0),
            "double_dispatch": {
                "enabled": True,
                "selection_progress": {
                    "selected": 0,
                    "total": len(variant_pairs),
                },
                "variant_pairs": variant_pairs,
            },
        }
        validate_outbound_contract(payload)
        return payload

    if slides:
        # Enforce theme-selection handshake for all slide-based dispatches.
        theme_resolution = resolve_theme_mapping_handshake(params)
        validate_theme_mapping_handshake(theme_resolution)

        groups = partition_by_fidelity(slides)
        has_creative = len(groups["creative"]) > 0
        has_literal = len(groups["literal-text"]) > 0 or len(groups["literal-visual"]) > 0

        if has_creative and has_literal:
            return generate_deck_mixed_fidelity(
                slides, params, module_lesson_part,
                client=client, diagram_cards=diagram_cards, run_id=run_id,
            )

    return generate_slide(params, client=client, run_id=run_id)


def validate_outbound_contract(
    payload: dict[str, Any],
    *,
    require_dispatch_paths: bool = False,
) -> None:
    """Validate required outbound fields for Gary mixed-fidelity results.

    Raises:
        ValueError: If required fields are missing or malformed.
    """
    missing = sorted(k for k in REQUIRED_OUTBOUND_FIELDS if k not in payload)
    if missing:
        raise ValueError(
            "Gary outbound contract validation failed. Missing required "
            f"field(s): {', '.join(missing)}"
        )
    if not isinstance(payload.get("recommendations"), list):
        raise ValueError("Gary outbound contract validation failed: recommendations must be a list")
    if not isinstance(payload.get("flags"), dict):
        raise ValueError("Gary outbound contract validation failed: flags must be an object")
    if not isinstance(payload.get("quality_assessment"), dict):
        raise ValueError(
            "Gary outbound contract validation failed: quality_assessment must be an object"
        )
    theme_resolution = payload.get("theme_resolution")
    if not isinstance(theme_resolution, dict):
        raise ValueError(
            "Gary outbound contract validation failed: theme_resolution must be an object"
        )
    validate_theme_mapping_handshake(theme_resolution)

    slide_output = payload.get("gary_slide_output")
    if not isinstance(slide_output, list):
        raise ValueError(
            "Gary outbound contract validation failed: gary_slide_output must be a list"
        )

    for idx, item in enumerate(slide_output, start=1):
        if not isinstance(item, dict):
            raise ValueError(
                "Gary outbound contract validation failed: "
                f"gary_slide_output[{idx}] must be an object"
            )

        slide_id = item.get("slide_id")
        if not isinstance(slide_id, str) or not slide_id.strip():
            raise ValueError(
                "Gary outbound contract validation failed: "
                f"gary_slide_output[{idx}].slide_id must be a non-empty string"
            )

        card_number = item.get("card_number")
        if not isinstance(card_number, int) or card_number <= 0:
            raise ValueError(
                "Gary outbound contract validation failed: "
                f"gary_slide_output[{idx}].card_number must be a positive integer"
            )

        source_ref = item.get("source_ref")
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError(
                "Gary outbound contract validation failed: "
                f"gary_slide_output[{idx}].source_ref must be a non-empty string"
            )

        if require_dispatch_paths:
            file_path = item.get("file_path")
            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError(
                    "Gary outbound contract validation failed: "
                    f"gary_slide_output[{idx}].file_path must be a non-empty string "
                    "for dispatch outputs"
                )


def validate_dispatch_ready(payload: dict[str, Any]) -> None:
    """Validate Gary payload for dispatch/handoff readiness.

    This strict mode enforces non-empty file paths for every slide output.
    Use this at the Marcus pre-dispatch gate before Irene Pass 2 handoff.
    """
    validate_outbound_contract(payload, require_dispatch_paths=True)


def _confirmation_is_true(value: Any) -> bool:
    """Return True when user confirmation is explicitly affirmative."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "approved", "confirmed"}
    return False


def resolve_theme_mapping_handshake(params: dict[str, Any]) -> dict[str, Any]:
    """Resolve theme-mapping handshake from params or embedded theme_resolution.

    Accepts either:
    - params["theme_resolution"] object, or
    - top-level dispatch keys populated by pre-dispatch packaging.
    """
    embedded = params.get("theme_resolution")
    if isinstance(embedded, dict):
        return dict(embedded)

    return {
        "requested_theme_key": params.get("requested_theme_key") or params.get("theme_selection"),
        "resolved_theme_key": params.get("resolved_theme_key")
        or params.get("theme_id")
        or params.get("themeId"),
        "resolved_parameter_set": params.get("resolved_parameter_set")
        or params.get("theme_paramset_key"),
        "mapping_source": params.get("mapping_source"),
        "mapping_version": params.get("mapping_version"),
        "user_confirmation": params.get("user_confirmation"),
    }


def validate_theme_mapping_handshake(theme_resolution: dict[str, Any]) -> None:
    """Fail closed if theme selection -> parameter mapping is incomplete."""
    missing = sorted(
        key
        for key in REQUIRED_THEME_RESOLUTION_FIELDS
        if key not in theme_resolution
        or theme_resolution.get(key) is None
        or (
            isinstance(theme_resolution.get(key), str)
            and not str(theme_resolution.get(key)).strip()
        )
    )
    if missing:
        raise ValueError(
            "Theme mapping handshake failed. Missing required field(s): "
            f"{', '.join(missing)}"
        )
    if not _confirmation_is_true(theme_resolution.get("user_confirmation")):
        raise ValueError(
            "Theme mapping handshake failed. user_confirmation must be explicit "
            "(true/yes/approved/confirmed)."
        )


def generate_slide(
    params: dict[str, Any],
    *,
    client: GammaClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute a single text-based Gamma API call with merged parameters.

    This is the low-level single-call function. For production use with
    fidelity-aware routing, use ``execute_generation()`` instead.

    Args:
        params: Merged parameter dict with at least ``input_text``
            and ``text_mode``.
        client: Optional pre-configured GammaClient.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Completed generation data including ``gammaUrl`` and
        ``exportUrl`` (if export was requested).
    """
    _require_gamma_api_key()

    if client is None:
        client = GammaClient()

    input_text = params.pop("input_text", params.pop("inputText", ""))
    text_mode = params.pop("text_mode", params.pop("textMode", "generate"))

    gen_kwargs: dict[str, Any] = {}
    key_map = {
        "format": "format",
        "numCards": "num_cards",
        "num_cards": "num_cards",
        "cardSplit": "card_split",
        "card_split": "card_split",
        "themeId": "theme_id",
        "theme_id": "theme_id",
        "additionalInstructions": "additional_instructions",
        "additional_instructions": "additional_instructions",
        "textOptions": "text_options",
        "text_options": "text_options",
        "imageOptions": "image_options",
        "image_options": "image_options",
        "cardOptions": "card_options",
        "card_options": "card_options",
        "sharingOptions": "sharing_options",
        "sharing_options": "sharing_options",
        "exportAs": "export_as",
        "export_as": "export_as",
        "folderIds": "folder_ids",
        "folder_ids": "folder_ids",
    }
    for param_key, kwarg_key in key_map.items():
        if param_key in params and params[param_key] is not None:
            gen_kwargs[kwarg_key] = params[param_key]

    image_options = gen_kwargs.get("image_options")
    if isinstance(image_options, dict):
        helper_keys = {"_keywordsHint", "referenceImagePath"}
        keywords_hint = image_options.get("_keywordsHint")
        sanitized_image_options = {
            k: v
            for k, v in image_options.items()
            if k not in helper_keys and not str(k).startswith("_")
        }
        gen_kwargs["image_options"] = sanitized_image_options

        if keywords_hint:
            hint_instruction = f"Visual keyword cues: {keywords_hint}."
            existing_instruction = gen_kwargs.get("additional_instructions", "")
            if existing_instruction:
                if hint_instruction not in existing_instruction:
                    gen_kwargs["additional_instructions"] = (
                        f"{existing_instruction} {hint_instruction}"
                    )
            else:
                gen_kwargs["additional_instructions"] = hint_instruction

    result = client.generate(input_text, text_mode, **gen_kwargs)
    gen_id = result.get("generationId") or result.get("id", "")
    logger.info(
        "Gamma generation started: generation_id=%s%s",
        gen_id,
        _log_run_suffix(run_id),
    )

    completed = client.wait_for_generation(gen_id)
    return completed


def generate_from_template(
    gamma_id: str,
    prompt: str,
    params: dict[str, Any] | None = None,
    *,
    client: GammaClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute a template-based Gamma generation.

    Args:
        gamma_id: The template's gammaId.
        prompt: Content/instructions for the template.
        params: Optional additional params (theme_id, export_as, etc.).
        client: Optional pre-configured GammaClient.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Completed generation data.
    """
    _require_gamma_api_key()

    if client is None:
        client = GammaClient()
    if params is None:
        params = {}

    gen_kwargs: dict[str, Any] = {}
    if params.get("theme_id") or params.get("themeId"):
        gen_kwargs["theme_id"] = params.get("theme_id") or params.get("themeId")
    if params.get("export_as") or params.get("exportAs"):
        gen_kwargs["export_as"] = params.get("export_as") or params.get("exportAs")
    if params.get("folder_ids") or params.get("folderIds"):
        gen_kwargs["folder_ids"] = params.get("folder_ids") or params.get("folderIds")
    if params.get("image_options") or params.get("imageOptions"):
        gen_kwargs["image_options"] = (
            params.get("image_options") or params.get("imageOptions")
        )

    result = client.generate_from_template(gamma_id, prompt, **gen_kwargs)
    gen_id = result.get("generationId") or result.get("id", "")
    logger.info(
        "Gamma template generation started: generation_id=%s template_id=%s%s",
        gen_id,
        gamma_id,
        _log_run_suffix(run_id),
    )

    completed = client.wait_for_generation(gen_id)
    return completed


def download_export(
    export_url: str,
    output_dir: Path | str | None = None,
    filename: str | None = None,
    *,
    run_id: str | None = None,
) -> Path:
    """Download an exported artifact from a signed URL.

    Args:
        export_url: Signed download URL from completed generation.
        output_dir: Directory to save to. Defaults to staging.
        filename: Output filename. Auto-derived from URL if not provided.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Path to the downloaded file.
    """
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = export_url.split("/")[-1].split("?")[0]
        if not filename:
            filename = "gamma-export.pdf"

    output_path = output_dir / filename

    resp = requests.get(export_url, timeout=120)
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
    logger.info(
        "Gamma export downloaded: bytes=%d path=%s%s",
        len(resp.content),
        output_path,
        _log_run_suffix(run_id),
    )

    return output_path


def _gamma_export_sort_key(path: Path) -> tuple[int, str]:
    """Parse the leading numeric prefix from Gamma export filenames.

    Gamma names exported PNGs as ``{N}_{Title}.png`` (e.g.,
    ``1_The-Modern-Clinicians-Dilemma.png``). This key sorts them by
    that leading number so positional mapping to our card numbers is
    correct. Falls back to lexicographic sort if no leading number.
    """
    import re as _re
    match = _re.match(r"^(\d+)", path.stem)
    if match:
        return int(match.group(1)), path.stem
    return 9999, path.stem


# ---------------------------------------------------------------------------
# Title-based page->slide matching (storyboard-correctness fix, party-ratified
# 2026-06-18). Gamma owns the page-set independently of the briefs — it injects
# a cover, merges/drops topics, and REPHRASES titles — so POSITION is not a key
# Gamma honors. Primary match is deterministic bijective containment: a match
# is a structural set-containment relation unique on both sides, or a loud
# failure. Ambiguity is fatal (never a tie-break/pick).
#
# Residual soft bind (party 2026-07-09): AFTER the bijective commit only, when
# exactly one unmatched brief slot and exactly one unmatched page remain,
# allow a cardinality-gated morphological/overlap bind (Completion↔Complete).
# Does NOT soften the bijective graph; multi-residue stays fail-loud.
# ---------------------------------------------------------------------------

# Frozen stopword list (party-ratified; enumerated + pinned, NOT a library
# default that could drift under us). Stripped before the containment test so
# generic function words cannot carry a match.
_TITLE_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "or", "of", "for", "to", "in", "on",
        "with", "at", "by", "from", "as", "into", "is", "are", "this", "that",
    }
)

# Minimum distinctive (non-stopword) tokens the CONTAINED side must carry for a
# containment edge to be admissible. Closes the "short brief accidentally
# supersets an unrelated page" hole (Winston/Amelia). Tunable only by
# party-mode, never by the matcher.
_MIN_DISTINCTIVE_TOKENS = 2

# Residual soft-bind gates (party 2026-07-09). Tunable only by party-mode.
_MIN_RESIDUAL_STRONG_ALIGNMENTS = 2
_RESIDUAL_JACCARD_FLOOR = 0.5
_RESIDUAL_WEAK_TOKENS: frozenset[str] = frozenset(
    {"set", "new", "one", "two", "all", "any", "end", "out"}
)

# Apostrophe family DELETED (joined) by normalize_title — pinned enumerated
# set, ratified amendment (party record §10, 2026-07-07). Gamma's export
# slugger DELETES apostrophes ("Technology's" -> "Technologys-..."), so the
# matcher must join too, never split ("Technology's" -> {technology, s} had
# no containment edge to {technologys, ...} — deterministic brief-unmatched
# on ANY apostrophe-bearing brief title; live trial a18c2a86). Members:
# U+0027 APOSTROPHE ' / U+2018 LEFT ' / U+2019 RIGHT ' single quotes /
# U+02BC MODIFIER LETTER APOSTROPHE / U+0060 GRAVE ACCENT ` /
# U+00B4 ACUTE ACCENT. Fullwidth U+FF07 needs no row: NFKD folds it to
# U+0027, caught by the post-fold deletion pass in normalize_title.
_TITLE_APOSTROPHE_FAMILY = re.compile("[\u0027\u2018\u2019\u02BC\u0060\u00B4]")


def normalize_title(text: str) -> str:
    """Deterministic title normalization (frozen contract, party-ratified;
    apostrophe-family amendment ratified party record §10, 2026-07-07).

    Delete the pinned apostrophe family (``_TITLE_APOSTROPHE_FAMILY``) so
    possessives JOIN (``Technology's`` -> ``technologys``, matching Gamma's
    export slugger) — applied DUAL-PASS: (1) on the raw input BEFORE NFKD
    (U+00B4 would otherwise decompose to space + combining acute) and
    (2) after the combining-strip (catches NFKD-folded forms, e.g. fullwidth
    U+FF07 -> U+0027). Then NFKD + strip accents; lowercase; ``&`` -> ``and``;
    strip the trailing objective after an em/en-dash-with-spaces delimiter
    (brief titles carry ``"Title — objective"``; page slugs do not, so this
    is a no-op on them); replace every non-alphanumeric run (incl. hyphens —
    Gamma slug separators) with a single space; collapse whitespace; trim.
    """
    s = _TITLE_APOSTROPHE_FAMILY.sub("", text or "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = _TITLE_APOSTROPHE_FAMILY.sub("", s)
    # Strip objective: split on the FIRST em/en-dash (or ' -- ') with spaces.
    s = re.split(r"\s+(?:—|–|--)\s+", s, maxsplit=1)[0]
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_from_export_stem(stem: str) -> str:
    """Recover the title from a Gamma export filename stem ``{N}_{Title}``."""
    m = re.match(r"^\d+_(.*)$", stem)
    return m.group(1) if m else stem


def _distinctive_tokens(normalized_title: str) -> frozenset[str]:
    return frozenset(
        t for t in normalized_title.split() if t and t not in _TITLE_STOPWORDS
    )


def _morphological_token_pair(a: str, b: str) -> bool:
    """True when tokens are equal or share a morphological stem family.

    Prefix / shared-prefix rules catch Completion↔Complete without a stemmer
    library. Digits never morph-match (only exact equality elsewhere).
    """
    if a == b:
        return True
    if a.isdigit() or b.isdigit():
        return False
    if len(a) < 4 or len(b) < 4:
        return False
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if longer.startswith(shorter):
        return True
    shared = 0
    for ca, cb in zip(a, b, strict=False):
        if ca != cb:
            break
        shared += 1
    return shared >= 5


def _residual_soft_compatible(slot_toks: frozenset[str], page_toks: frozenset[str]) -> bool:
    """Cardinality-gated soft gate for the 1:1 residual bind.

    Counts strong alignments (exact or morphological) excluding weak/digit-only
    tokens as strong carriers. Also admits Jaccard ≥ floor with ≥2 exact
    intersection tokens. Rejects cover↔unrelated-summary false binds (F8 pin).
    """
    if not slot_toks or not page_toks:
        return False

    page_remaining = set(page_toks)
    strong = 0
    for st in sorted(slot_toks):
        if st.isdigit() or st in _RESIDUAL_WEAK_TOKENS:
            # Consume exact weak/digit matches so they do not block peers, but
            # never count them toward the strong floor.
            if st in page_remaining:
                page_remaining.discard(st)
            continue
        matched: str | None = None
        for pt in sorted(page_remaining):
            if pt.isdigit() or pt in _RESIDUAL_WEAK_TOKENS:
                continue
            if _morphological_token_pair(st, pt):
                matched = pt
                break
        if matched is not None:
            page_remaining.discard(matched)
            strong += 1

    if strong >= _MIN_RESIDUAL_STRONG_ALIGNMENTS:
        return True

    inter = len(slot_toks & page_toks)
    union = len(slot_toks | page_toks)
    return bool(union) and inter >= 2 and (inter / union) >= _RESIDUAL_JACCARD_FLOOR


class SlideMatchResult:
    """Outcome of matching exported pages to briefed slots.

    The match POLICY lives here (shared layer); the consumer (gary, app-side)
    translates the non-empty failure fields into the recoverable
    ``GammaDispatchError`` family. ``matched`` is slide_id -> page path.

    Plain class (NOT a dataclass): this module is loaded via an importlib
    shim, so the module is not registered in ``sys.modules`` under a resolvable
    name and ``@dataclass`` annotation resolution would crash.
    """

    def __init__(self) -> None:
        self.matched: dict[str, str] = {}
        self.dropped_pages: list[dict[str, Any]] = []
        self.unmatched_keys: list[str] = []
        self.unmatched_pages: list[dict[str, Any]] = []
        self.ambiguous: list[dict[str, Any]] = []


def match_pages_to_slots(
    *,
    pages: list[dict[str, Any]],
    expected_slots: list[tuple[str, str]],
) -> SlideMatchResult:
    """Bijective deterministic containment match (party-ratified 2026-06-18).

    ``pages``: ordered list of ``{"page_index": int, "title": str, "path": str}``
    (title = raw, e.g. recovered via ``title_from_export_stem``).
    ``expected_slots``: ordered ``(slide_id, raw_brief_title)``.

    Edge rule: a (slot, page) edge exists iff one's distinctive-token set is a
    subset of the other's (bidirectional — Gamma both drops and appends words)
    AND the smaller (contained) side has >= _MIN_DISTINCTIVE_TOKENS tokens.
    Commit only edges unique on BOTH sides; any multiplicity is ambiguity-fatal
    (surfaced, never resolved). Compute ALL edges before committing — never
    greedy/first-match.

    After the bijective commit, a 1:1 residual soft bind may fire (party
    2026-07-09) when exactly one unmatched slot and one unmatched page remain
    and ``_residual_soft_compatible`` passes. Cover-drop runs only after that
    attempt, so a sole content residue is never muted as a leading cover.
    """
    slot_tokens = {
        sid: _distinctive_tokens(normalize_title(title)) for sid, title in expected_slots
    }
    # Unique per-page id = position in the input list. Keying dicts by
    # page_index would let two pages sharing a numeric prefix (or both falling
    # back to the 9999 sort sentinel) silently OVERWRITE each other — a real
    # page would vanish from the candidate graph entirely, defeating fail-loud
    # (blind + edge review MUST-FIX). page_index is retained only as a sort key
    # for leading-cover classification.
    page_ids = list(range(len(pages)))
    page_tokens = {
        pid: _distinctive_tokens(normalize_title(pages[pid]["title"])) for pid in page_ids
    }

    def _edge(a: frozenset[str], b: frozenset[str]) -> bool:
        if not a or not b:
            return False
        if a <= b:
            return len(a) >= _MIN_DISTINCTIVE_TOKENS
        if b <= a:
            return len(b) >= _MIN_DISTINCTIVE_TOKENS
        return False

    # ALL candidate edges first (no streaming/greedy).
    slot_candidates: dict[str, list[int]] = {sid: [] for sid, _ in expected_slots}
    page_candidates: dict[int, list[str]] = {pid: [] for pid in page_ids}
    for sid, _ in expected_slots:
        for pid in page_ids:
            if _edge(slot_tokens[sid], page_tokens[pid]):
                slot_candidates[sid].append(pid)
                page_candidates[pid].append(sid)

    result = SlideMatchResult()
    # Bijective commit: unique on BOTH sides.
    for sid, _ in expected_slots:
        cands = slot_candidates[sid]
        if len(cands) == 1 and len(page_candidates[cands[0]]) == 1:
            result.matched[sid] = str(pages[cands[0]]["path"])
        elif len(cands) > 1:
            result.ambiguous.append(
                {
                    "kind": "slot",
                    "slide_id": sid,
                    "candidate_pages": sorted(pages[pid].get("page_index") for pid in cands),
                }
            )
        else:
            result.unmatched_keys.append(sid)
    for pid in page_ids:
        if len(page_candidates[pid]) > 1:
            result.ambiguous.append(
                {
                    "kind": "page",
                    "page_index": pages[pid].get("page_index"),
                    "candidate_slots": sorted(page_candidates[pid]),
                }
            )

    # Classify unmatched pages by export order. Only the FIRST (lowest-index)
    # leading unmatched page is the engine cover (drop+record); any ADDITIONAL
    # leading unmatched page is fatal, NOT silently dropped (blind review: do
    # not lose a genuine retitled leading content slide). Non-leading unmatched
    # pages are fatal.
    matched_pids = {
        pid
        for pid in page_ids
        if len(page_candidates[pid]) == 1
        and len(slot_candidates[page_candidates[pid][0]]) == 1
    }

    # Residual soft bind: only when bijective left a strict 1:1 residue.
    # Attempt BEFORE cover-drop so a sole unmatched content page is not muted
    # as unmatched-leading-page (live trial bc0f81c4 Completion↔Complete).
    unmatched_page_pids = [pid for pid in page_ids if len(page_candidates[pid]) == 0]
    if len(result.unmatched_keys) == 1 and len(unmatched_page_pids) == 1:
        sid = result.unmatched_keys[0]
        pid = unmatched_page_pids[0]
        if _residual_soft_compatible(slot_tokens[sid], page_tokens[pid]):
            result.matched[sid] = str(pages[pid]["path"])
            result.unmatched_keys = []
            matched_pids.add(pid)

    min_matched_index = (
        min(pages[pid].get("page_index", 0) for pid in matched_pids) if matched_pids else None
    )
    cover_dropped = False
    for pid in sorted(page_ids, key=lambda i: pages[i].get("page_index", 0)):
        if pid in matched_pids or len(page_candidates[pid]) > 1:
            continue
        p = pages[pid]
        record = {
            "page_index": p.get("page_index"),
            "title": p.get("title"),
            "path": str(p.get("path", "")),
        }
        is_leading = (
            min_matched_index is not None and p.get("page_index", 0) < min_matched_index
        )
        if is_leading and not cover_dropped:
            record["reason"] = "unmatched-leading-page"
            result.dropped_pages.append(record)
            cover_dropped = True
        else:
            result.unmatched_pages.append(record)
    return result


def _materialize_exported_slide_paths(
    downloaded_path: Path,
    *,
    requested_format: str | None,
    expected_card_numbers: list[int],
    module_lesson_part: str,
    export_dir: Path,
    label: str,
) -> list[str]:
    """Resolve a downloaded Gamma export into per-slide artifact paths.

    For PNG exports, Gamma may return either a single image (single-card call)
    or an archive containing one image per card. This helper normalizes both
    into deterministic per-card PNG paths for downstream compositor use.
    """
    if not expected_card_numbers:
        return []

    normalized_format = (requested_format or "").strip().lower() or None
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".heic", ".heif"}

    if normalized_format != "png":
        return [str(downloaded_path)] * len(expected_card_numbers)

    if zipfile.is_zipfile(downloaded_path):
        extract_dir = export_dir / f"{module_lesson_part}_{label}"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(downloaded_path) as archive:
            archive.extractall(extract_dir)

        extracted_images = sorted(
            (
                path
                for path in extract_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in image_extensions
            ),
            key=lambda p: _gamma_export_sort_key(p),
        )
        if len(extracted_images) != len(expected_card_numbers):
            raise ValueError(
                "Gamma PNG export artifact mismatch: "
                f"expected {len(expected_card_numbers)} PNG artifacts for {label}, "
                f"got {len(extracted_images)} from {downloaded_path.name}."
            )

        # Positional mapping: Gamma exports are numbered sequentially (1-N)
        # in the same order the slides were submitted. Our expected_card_numbers
        # list preserves that submission order, so position i in the sorted
        # export maps to expected_card_numbers[i].
        resolved_paths: list[str] = []
        for source_path, card_number in zip(extracted_images, expected_card_numbers):
            target_path = export_dir / f"{module_lesson_part}_slide_{card_number:02d}.png"
            target_path.write_bytes(source_path.read_bytes())
            resolved_paths.append(str(target_path))
        return resolved_paths

    if downloaded_path.suffix.lower() in image_extensions:
        if len(expected_card_numbers) != 1:
            raise ValueError(
                "Gamma PNG export artifact mismatch: "
                f"expected {len(expected_card_numbers)} PNG artifacts for {label}, got 1."
            )
        target_path = export_dir / f"{module_lesson_part}_slide_{expected_card_numbers[0]:02d}.png"
        target_path.write_bytes(downloaded_path.read_bytes())
        return [str(target_path)]

    raise ValueError(
        "Gamma PNG export artifact mismatch: unsupported export payload "
        f"{downloaded_path.name} for {label}."
    )


def materialize_exported_slide_paths_by_title(
    downloaded_path: Path,
    *,
    requested_format: str | None,
    expected_slots: list[tuple[str, str]],
    module_lesson_part: str,
    export_dir: Path,
    label: str,
) -> SlideMatchResult:
    """Title-matched materialization (storyboard-correctness fix, 2026-06-18).

    Extracts the Gamma PNG export, recovers each page's title from its
    ``{N}_{Title}`` filename, and matches pages to briefed slots by
    deterministic bijective containment (``match_pages_to_slots``) — NOT by
    position. Writes a per-slide PNG named by ``slide_id`` for each committed
    match. Returns the ``SlideMatchResult``; the caller (gary) raises the
    recoverable ``GammaDispatchError`` family on ``unmatched_keys`` /
    ``unmatched_pages`` / ``ambiguous``.

    Single-card Gamma exports often land as a lone PNG (not a zip). When
    ``len(expected_slots) == 1``, that lone image binds to the sole slot by
    cardinality bijection — even if the download stem is opaque (e.g.
    ``gary_A``). Opaque-stem N=1 binding is intentional (party rider
    2026-07-08); do not later require title containment for that arm without
    a new party round. When ``len(expected_slots) > 1`` and the payload is
    not a multi-page zip, every slot is unmatched (fail loud — never
    positional broadcast).

    The positional ``_materialize_exported_slide_paths`` is deliberately left
    untouched for brief-less callers (standalone Gamma lane); this is a
    separate, additive function (party DECISION 3 + the byte-identical gate).
    """
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".heic", ".heif"}
    normalized_format = (requested_format or "").strip().lower() or None
    result = SlideMatchResult()

    if normalized_format != "png":
        # Non-PNG cannot be title-matched; fail loud (every slot unmatched).
        result.unmatched_keys = [sid for sid, _ in expected_slots]
        return result

    if not zipfile.is_zipfile(downloaded_path):
        # Lone image export (live single-card Gamma shape). N=1 → bind when
        # title-match succeeds OR the stem is opaque (no ``{N}_{Title}``
        # prefix — e.g. gary_A); a parseable titled stem that fails
        # containment stays unmatched (fail loud — never silent wrong-bind).
        # N>1 → fail loud with the orphan page recorded (no positional broadcast).
        suffix = downloaded_path.suffix.lower()
        if (
            downloaded_path.is_file()
            and suffix == ".png"
            and len(expected_slots) == 1
        ):
            export_dir.mkdir(parents=True, exist_ok=True)
            slide_id, _brief_title = expected_slots[0]
            page_title = title_from_export_stem(downloaded_path.stem)
            stem_is_opaque = page_title == downloaded_path.stem
            pages = [
                {
                    "page_index": 1,
                    "title": page_title,
                    "path": str(downloaded_path),
                }
            ]
            result = match_pages_to_slots(pages=pages, expected_slots=expected_slots)
            if slide_id not in result.matched and stem_is_opaque:
                # Opaque stem yields no title-containment edge; sole-slot
                # cardinality is still a valid bijection (party rider 2026-07-08).
                result.matched[slide_id] = str(downloaded_path)
                result.unmatched_keys = [s for s in result.unmatched_keys if s != slide_id]
                result.unmatched_pages = []
                result.ambiguous = []
            for sid, source in list(result.matched.items()):
                target_path = export_dir / f"{module_lesson_part}_{sid}.png"
                target_path.write_bytes(Path(source).read_bytes())
                result.matched[sid] = str(target_path)
            return result
        if (
            downloaded_path.is_file()
            and suffix == ".png"
            and len(expected_slots) > 1
        ):
            result.unmatched_keys = [sid for sid, _ in expected_slots]
            result.unmatched_pages = [
                {
                    "page_index": 1,
                    "title": title_from_export_stem(downloaded_path.stem),
                    "path": str(downloaded_path),
                    "reason": (
                        f"lone-png-export with {len(expected_slots)} briefed slots "
                        f"(expected multi-page zip for N>1)"
                    ),
                }
            ]
            return result
        result.unmatched_keys = [sid for sid, _ in expected_slots]
        return result

    extract_dir = export_dir / f"{module_lesson_part}_{label}_pages"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(downloaded_path) as archive:
        archive.extractall(extract_dir)
    extracted = sorted(
        (p for p in extract_dir.rglob("*") if p.is_file() and p.suffix.lower() in image_extensions),
        key=_gamma_export_sort_key,
    )
    pages = [
        {
            "page_index": _gamma_export_sort_key(src)[0],
            "title": title_from_export_stem(src.stem),
            "path": str(src),
        }
        for src in extracted
    ]
    result = match_pages_to_slots(pages=pages, expected_slots=expected_slots)
    # Commit matched source pages to stable per-slide artifact paths.
    for slide_id, source in list(result.matched.items()):
        target_path = export_dir / f"{module_lesson_part}_{slide_id}.png"
        target_path.write_bytes(Path(source).read_bytes())
        result.matched[slide_id] = str(target_path)
    return result


def generate_deck_mixed_fidelity(
    slides: list[dict[str, Any]],
    base_params: dict[str, Any],
    module_lesson_part: str,
    *,
    client: GammaClient | None = None,
    diagram_cards: list[dict[str, Any]] | None = None,
    site_repo_url: str | None = None,
    site_branch: str = "main",
    mode: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Orchestrate two-call split generation for mixed-fidelity decks.

    When a deck contains both creative and literal slides, Gamma's deck-level
    textMode constraint requires two separate API calls: one in generate mode
    for creative slides and one in preserve mode for literal slides. This
    function partitions, generates, and reassembles the output.

    Args:
        slides: List of slide dicts with 'slide_number', 'content', 'fidelity'.
        base_params: Merged parameters from the cascade
            (style guide + preset + template + envelope).
        module_lesson_part: Identifier for doc naming (e.g., "C1-M1-P2-Macro-Trends").
        client: Optional pre-configured GammaClient.
        diagram_cards: Optional list of literal-visual image URL entries.
        site_repo_url: Optional git repo URL for preintegration PNG publish.
        site_branch: Branch for site repo commit/push.
        mode: Execution mode (default/tracked or ad-hoc) for side-effect guardrails.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Dict with 'gary_slide_output', 'provenance', 'generation_mode', 'calls_made'.
    """
    if client is None:
        client = GammaClient()

    theme_resolution = resolve_theme_mapping_handshake(base_params)
    validate_theme_mapping_handshake(theme_resolution)

    groups = partition_by_fidelity(slides)
    creative_slides = groups["creative"]
    literal_text_slides = groups["literal-text"]
    literal_visual_slides = groups["literal-visual"]
    literal_slides = literal_text_slides + literal_visual_slides

    mutable_diagram_cards = [dict(dc) for dc in (diagram_cards or []) if isinstance(dc, dict)]
    card_map = {dc["card_number"]: dc for dc in mutable_diagram_cards if "card_number" in dc}
    literal_visual_publish: dict[str, Any] | None = None

    if literal_visual_slides and mutable_diagram_cards:
        preintegration_map: dict[int, Path | str] = {}
        for dc in mutable_diagram_cards:
            card_number = dc.get("card_number")
            if not isinstance(card_number, int) or card_number <= 0:
                continue
            local_path = str(dc.get("preintegration_png_path", "")).strip()
            image_url = str(dc.get("image_url", "")).strip()
            if local_path:
                preintegration_map[card_number] = local_path
            elif image_url and not _is_remote_http_ref(image_url):
                preintegration_map[card_number] = image_url

        if preintegration_map:
            effective_repo_url = site_repo_url or str(base_params.get("site_repo_url", "")).strip()
            if not effective_repo_url:
                raise RuntimeError(
                    "Local preintegration literal-visual paths were supplied, but site_repo_url "
                    "was not provided for publish/substitution"
                )
            effective_mode = mode or str(
                base_params.get("mode") or base_params.get("execution_mode") or "default"
            )
            literal_visual_publish = publish_preintegration_literal_visuals(
                preintegration_map,
                module_lesson_part,
                site_repo_url=effective_repo_url,
                site_branch=site_branch,
                run_id=run_id,
                mode=effective_mode,
            )
            if not literal_visual_publish.get("preintegration_ready"):
                reason = "ad-hoc mode or unresolved local paths"
                raise RuntimeError(
                    "Literal-visual preintegration URLs are not ready for dispatch "
                    f"({reason})."
                )
            for dc in mutable_diagram_cards:
                card_number = dc.get("card_number")
                if card_number in literal_visual_publish.get("url_map", {}):
                    dc["image_url"] = literal_visual_publish["url_map"][card_number]
            card_map = {
                dc["card_number"]: dc
                for dc in mutable_diagram_cards
                if "card_number" in dc
            }

    creative_results: list[dict[str, Any]] = []
    literal_results: list[dict[str, Any]] = []
    calls_made = 0

    export_dir_value = base_params.get("export_dir") or base_params.get("exportDir")
    export_dir = Path(export_dir_value) if export_dir_value else None

    requested_export_format = str(
        base_params.get("export_as") or base_params.get("exportAs") or ""
    ).strip().lower() or None

    def _resolve_file_paths(
        gen_result: dict[str, Any],
        label: str,
        card_numbers: list[int],
    ) -> list[str]:
        export_url = gen_result.get("exportUrl")
        if export_url and export_dir is not None:
            ext = requested_export_format or "pdf"
            filename = f"{module_lesson_part}_{label}.{ext}"
            downloaded = download_export(
                export_url,
                output_dir=export_dir,
                filename=filename,
                run_id=run_id,
            )
            return _materialize_exported_slide_paths(
                downloaded,
                requested_format=requested_export_format,
                expected_card_numbers=card_numbers,
                module_lesson_part=module_lesson_part,
                export_dir=export_dir,
                label=label,
            )

        for key in ("gammaUrl", "url", "exportUrl"):
            value = gen_result.get(key)
            if isinstance(value, str) and value.strip():
                return [value] * len(card_numbers)

        generation_id = gen_result.get("generationId") or gen_result.get("id") or "unknown"
        return [f"gamma://generation/{generation_id}"] * len(card_numbers)

    if creative_slides:
        creative_params = {**base_params, "textMode": "generate"}
        creative_params.pop("text_mode", None)
        creative_input = "\n---\n".join(s.get("content", "") for s in creative_slides)
        creative_params["input_text"] = creative_input
        creative_params["num_cards"] = len(creative_slides)
        creative_params["card_split"] = "inputTextBreaks"

        gen_result = generate_slide(creative_params, client=client, run_id=run_id)
        calls_made += 1
        creative_gen_id = gen_result.get("generationId", gen_result.get("id", ""))
        creative_card_numbers = [slide["slide_number"] for slide in creative_slides]
        creative_file_paths = _resolve_file_paths(gen_result, "creative", creative_card_numbers)

        for slide, creative_file_path in zip(creative_slides, creative_file_paths, strict=False):
            card_num = slide["slide_number"]
            creative_results.append({
                "slide_id": f"{module_lesson_part}-card-{card_num:02d}",
                "file_path": creative_file_path,
                "card_number": card_num,
                "visual_description": f"[pending export — creative slide {card_num}]",
                "source_ref": slide.get("source_ref", f"slide-brief.md#Slide {card_num}"),
                "generation_id": creative_gen_id,
                "fidelity": "creative",
            })

    def _preserve_instruction(base_instruction: str) -> str:
        guard = (
            "Output ONLY the provided text. Do not add content, steps, "
            "or diagrams beyond what is given. Do not embellish or expand."
        )
        return f"{base_instruction} {guard}".strip() if base_instruction else guard

    if literal_text_slides:
        literal_text_params = {**base_params}
        literal_text_params["textMode"] = "preserve"
        literal_text_params["text_mode"] = "preserve"
        base_instruction = str(
            literal_text_params.pop("additionalInstructions", "")
            or literal_text_params.pop("additional_instructions", "")
        ).strip()
        literal_text_params["additional_instructions"] = _preserve_instruction(base_instruction)
        literal_text_params["image_options"] = {"source": "noImages"}

        literal_text_input_parts = [s.get("content", "") for s in literal_text_slides]
        literal_text_params["input_text"] = "\n---\n".join(literal_text_input_parts)
        literal_text_params["num_cards"] = len(literal_text_slides)
        literal_text_params["card_split"] = "inputTextBreaks"

        gen_result = generate_slide(literal_text_params, client=client, run_id=run_id)
        calls_made += 1
        literal_text_gen_id = gen_result.get("generationId", gen_result.get("id", ""))
        literal_text_card_numbers = [slide["slide_number"] for slide in literal_text_slides]
        literal_text_file_paths = _resolve_file_paths(
            gen_result,
            "literal-text",
            literal_text_card_numbers,
        )

        for slide, literal_text_file_path in zip(
            literal_text_slides,
            literal_text_file_paths,
            strict=False,
        ):
            card_num = slide["slide_number"]
            literal_results.append({
                "slide_id": f"{module_lesson_part}-card-{card_num:02d}",
                "file_path": literal_text_file_path,
                "card_number": card_num,
                "visual_description": f"[pending export — literal-text slide {card_num}]",
                "source_ref": slide.get("source_ref", f"slide-brief.md#Slide {card_num}"),
                "generation_id": literal_text_gen_id,
                "fidelity": "literal-text",
            })

    # ── Literal-visual slides: Template API path ──────────────
    # Literal-visual slides use Gamma's Create from Template API
    # (`POST /generations/from-template`) with a single-page Image
    # card template.  Best-effort: Gamma's AI may classify the
    # image as "accent" (cropped, positioned) rather than
    # "background" (full-bleed) depending on image content —
    # this cannot be controlled via the API (see
    # developers.gamma.app).  We allow one retry before falling
    # back to local compositing via _composite_full_bleed(), which
    # guarantees deterministic full-bleed output.
    _LITERAL_VISUAL_TEMPLATE_ID = "g_gior6s13mvpk8ms"
    _MAX_TEMPLATE_RETRIES = 2
    _TEMPLATE_EXPORT_SETTLE_SECONDS = 15

    if literal_visual_slides:
        for slide in literal_visual_slides:
            card_num = slide["slide_number"]
            if card_num not in card_map:
                raise ValueError(
                    f"literal-visual slide {card_num} requires a diagram_cards entry "
                    "with dispatch-ready image_url"
                )

            card_payload = card_map[card_num]
            img_url = card_payload["image_url"]
            is_valid, reason = validate_image_url(img_url)
            if not is_valid:
                raise ValueError(
                    f"diagram_cards card_number {card_num}: "
                    f"image URL validation failed: {reason} — URL: {img_url}"
                )

            placement_note = str(card_payload.get("placement_note", "")).strip()
            slide_title = f"{module_lesson_part} Slide {card_num:02d}"
            prompt_parts = [
                "Replace the placeholder image with this image at full "
                "opacity (not as background, not faded). The image must "
                "be the primary visual element filling the entire card. "
                "No text overlay.",
                img_url,
            ]
            if placement_note:
                prompt_parts.append(f"Composition constraint: {placement_note}")
            prompt_parts.extend(["", f"Title: {slide_title}"])

            template_params: dict[str, Any] = {}
            if base_params.get("themeId") or base_params.get("theme_id"):
                template_params["theme_id"] = (
                    base_params.get("themeId") or base_params.get("theme_id")
                )
            if base_params.get("export_as") or base_params.get("exportAs"):
                template_params["export_as"] = (
                    base_params.get("export_as") or base_params.get("exportAs")
                )

            # Best-effort template dispatch → one retry → composite fallback.
            # Gamma's AI classifies images as "accent" or "background" based
            # on content characteristics; this is not API-controllable.
            # Images that Gamma treats as background render full-bleed;
            # accent-classified images get cropped/positioned. After one retry,
            # _composite_full_bleed() produces a deterministic full-bleed
            # slide from the source PNG.
            literal_visual_file_path: str | None = None
            literal_visual_gen_id = ""
            literal_visual_source = "template"  # tracks provenance

            for attempt in range(1, _MAX_TEMPLATE_RETRIES + 1):
                gen_result = generate_from_template(
                    _LITERAL_VISUAL_TEMPLATE_ID,
                    "\n".join(prompt_parts),
                    template_params,
                    client=client,
                    run_id=run_id,
                )
                calls_made += 1

                # Gamma reports "completed" before the export renderer
                # finishes baking the image-card content into the PNG.
                # A brief delay lets the export catch up.
                time.sleep(_TEMPLATE_EXPORT_SETTLE_SECONDS)

                literal_visual_gen_id = gen_result.get(
                    "generationId", gen_result.get("id", "")
                )
                literal_visual_file_path = _resolve_file_paths(
                    gen_result,
                    f"literal-visual-{card_num:02d}",
                    [card_num],
                )[0]

                # Quality gate: validate the exported PNG is not blank.
                fill_result = validate_visual_fill(literal_visual_file_path)
                if fill_result.get("passed"):
                    logger.info(
                        "literal-visual card %d passed fill validation on attempt %d",
                        card_num, attempt,
                    )
                    break

                logger.warning(
                    "literal-visual card %d FAILED fill validation on attempt %d/%d: %s",
                    card_num, attempt, _MAX_TEMPLATE_RETRIES,
                    fill_result.get("failures", fill_result.get("error", "unknown")),
                )
            else:
                # Template failed — fall back to local composite.
                # Try preintegration PNG first, then download from URL.
                preint_path_str = str(card_payload.get("preintegration_png_path", "")).strip()
                preint_source = Path(preint_path_str) if preint_path_str else None
                if preint_source and not preint_source.is_absolute():
                    preint_source = PROJECT_ROOT / preint_source

                if preint_source and preint_source.is_file() and literal_visual_file_path:
                    # If file_path is a remote URL (template failed, no local
                    # export), compute a local target in the export directory.
                    if _is_remote_http_ref(str(literal_visual_file_path)):
                        target_path = (
                            export_dir / f"{module_lesson_part}_literal-visual-{card_num:02d}.png"
                            if export_dir
                            else PROJECT_ROOT / f"literal-visual-{card_num:02d}.png"
                        )
                    else:
                        target_path = Path(literal_visual_file_path)
                    _composite_full_bleed(preint_source, target_path)
                    literal_visual_file_path = str(target_path)
                    literal_visual_source = "composite-preintegration"
                    logger.info(
                        "literal-visual card %d: composite from preintegration %s → %s",
                        card_num, preint_source.name, target_path.name,
                    )
                elif img_url and literal_visual_file_path:
                    # No local PNG — download from URL and composite.
                    if _is_remote_http_ref(str(literal_visual_file_path)):
                        target_path = (
                            export_dir / f"{module_lesson_part}_literal-visual-{card_num:02d}.png"
                            if export_dir
                            else PROJECT_ROOT / f"literal-visual-{card_num:02d}.png"
                        )
                    else:
                        target_path = Path(literal_visual_file_path)
                    try:
                        dl_resp = requests.get(img_url, timeout=60)
                        dl_resp.raise_for_status()
                        dl_tmp = target_path.with_suffix(".dl.png")
                        dl_tmp.write_bytes(dl_resp.content)
                        _composite_full_bleed(dl_tmp, target_path)
                        dl_tmp.unlink(missing_ok=True)
                        literal_visual_source = "composite-download"
                        logger.info(
                            "literal-visual card %d: composite from downloaded URL → %s",
                            card_num, target_path.name,
                        )
                    except Exception as exc:
                        logger.error(
                            "literal-visual card %d: download composite failed: %s",
                            card_num, exc,
                        )
                else:
                    logger.error(
                        "literal-visual card %d: template fill validation failed "
                        "and no fallback source available",
                        card_num,
                    )

            literal_results.append({
                "slide_id": f"{module_lesson_part}-card-{card_num:02d}",
                "file_path": literal_visual_file_path,
                "card_number": card_num,
                "visual_description": (
                    f"[literal-visual slide {card_num} — source: {literal_visual_source}]"
                ),
                "source_ref": slide.get(
                    "source_ref", f"slide-brief.md#Slide {card_num}"
                ),
                "generation_id": literal_visual_gen_id,
                "fidelity": "literal-visual",
                "literal_visual_source": literal_visual_source,
            })

    if not creative_slides and not literal_slides:
        empty_payload = {
            "gary_slide_output": [],
            "quality_assessment": {
                "overall_score": 0.0,
                "dimensions": {
                    "layout_integrity": 0.0,
                    "parameter_confidence": 0.0,
                    "embellishment_risk_control": 0.0,
                },
                "embellishment_detected": False,
                "embellishment_details": [],
            },
            "parameter_decisions": {
                "theme_id": theme_resolution["resolved_theme_key"],
                "requested_theme_key": theme_resolution["requested_theme_key"],
                "resolved_parameter_set": theme_resolution["resolved_parameter_set"],
                "text_mode": "generate",
                "card_split": "inputTextBreaks",
                "num_cards": 0,
            },
            "recommendations": [
                "No slides provided for mixed-fidelity generation; verify slide brief inputs.",
            ],
            "flags": {
                "embellishment_control_used": False,
                "constraint_phrasing": "",
                "constraint_effectiveness": 0.0,
                "theme_mapping_verified": True,
                "theme_mapping_source": theme_resolution["mapping_source"],
                "run_validation_artifact_pointer": (
                    f"run://{run_id}/gary/outbound-contract-validation"
                    if run_id
                    else "run://unknown/gary/outbound-contract-validation"
                ),
            },
            "theme_resolution": theme_resolution,
            "provenance": [],
            "generation_mode": "text",
            "calls_made": 0,
        }
        validate_outbound_contract(empty_payload)
        return empty_payload

    unified = reassemble_slide_output(creative_results, literal_results)

    card_numbers = [r.get("card_number", 0) for r in unified]
    sorted_unique = (
        card_numbers == sorted(card_numbers)
        and len(card_numbers) == len(set(card_numbers))
    )
    contiguous = (
        card_numbers == list(range(min(card_numbers), max(card_numbers) + 1))
        if card_numbers
        else True
    )
    layout_integrity = 1.0 if sorted_unique and contiguous else 0.75
    parameter_confidence = 0.9 if calls_made > 0 else 0.0
    literal_count = len(literal_slides)
    embellishment_risk_control = 0.9 if literal_count > 0 else 0.8
    quality_assessment = {
        "overall_score": round(
            (layout_integrity + parameter_confidence + embellishment_risk_control) / 3,
            2,
        ),
        "dimensions": {
            "layout_integrity": round(layout_integrity, 2),
            "parameter_confidence": round(parameter_confidence, 2),
            "embellishment_risk_control": round(embellishment_risk_control, 2),
        },
        "embellishment_detected": False,
        "embellishment_details": [],
    }

    parameter_decisions = {
        "theme_id": theme_resolution["resolved_theme_key"],
        "requested_theme_key": theme_resolution["requested_theme_key"],
        "resolved_parameter_set": theme_resolution["resolved_parameter_set"],
        "text_mode": "mixed (creative=generate, literal-text=preserve, literal-visual=template)",
        "card_split": "inputTextBreaks",
        "num_cards": len(unified),
        "image_options": {
            "literal_default": "noImages",
            "literal_visual_source": "noImages" if literal_visual_slides else "none",
            "literal_visual_call_mode": (
                "per-card" if literal_visual_slides else "none"
            ),
        },
    }
    if base_params.get("export_as") or base_params.get("exportAs"):
        parameter_decisions["export_as"] = (
            base_params.get("export_as") or base_params.get("exportAs")
        )

    recommendations: list[str] = []
    if not contiguous:
        recommendations.append(
            "Card numbers are not contiguous; verify slide brief ordering and "
            "reassembly mapping."
        )
    if not sorted_unique:
        recommendations.append(
            "Duplicate or unsorted card numbers detected; resolve before Irene "
            "Pass 2 handoff."
        )

    flags = {
        "embellishment_control_used": literal_count > 0,
        "constraint_phrasing": (
            "Literal-text slides: source-locked preserve mode. "
            "Literal-visual slides: Gamma-rendered full-bleed image-only, "
            "no on-slide support text."
            if literal_count > 0
            else ""
        ),
        "constraint_effectiveness": round(embellishment_risk_control, 2),
        "theme_mapping_verified": True,
        "theme_mapping_source": theme_resolution["mapping_source"],
        "run_validation_artifact_pointer": (
            f"run://{run_id}/gary/outbound-contract-validation"
            if run_id
            else "run://unknown/gary/outbound-contract-validation"
        ),
    }

    payload = {
        "gary_slide_output": [
            {
                "slide_id": r["slide_id"],
                "file_path": r.get("file_path"),
                "card_number": r["card_number"],
                "visual_description": r.get("visual_description", ""),
                "source_ref": r.get("source_ref", ""),
                "fidelity": r.get("fidelity", "creative"),
                "literal_visual_source": r.get("literal_visual_source"),
            }
            for r in unified
        ],
        "quality_assessment": quality_assessment,
        "parameter_decisions": parameter_decisions,
        "recommendations": recommendations,
        "flags": flags,
        "theme_resolution": theme_resolution,
        "provenance": [
            {
                "card_number": r["card_number"],
                "source_call": r["source_call"],
                "generation_id": r.get("generation_id", ""),
                "fidelity": r.get("fidelity", "creative"),
            }
            for r in unified
        ],
        "generation_mode": "text",
        "calls_made": calls_made,
    }
    if literal_visual_publish is not None:
        payload["literal_visual_publish"] = {
            k: v for k, v in literal_visual_publish.items() if k != "url_map"
        }
    validate_outbound_contract(payload)
    return payload


def partition_by_fidelity(
    slides: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Partition slide brief slides into creative/literal-text/literal-visual groups.

    Args:
        slides: List of slide dicts, each with at minimum 'slide_number',
                'content', and 'fidelity' (defaults to 'creative').

    Returns:
        Dict with keys 'creative', 'literal-text', and 'literal-visual', each
        containing the slides assigned to that group with original slide numbers preserved.
    """
    creative: list[dict[str, Any]] = []
    literal_text: list[dict[str, Any]] = []
    literal_visual: list[dict[str, Any]] = []

    for slide in slides:
        fidelity = slide.get("fidelity", "creative")
        if fidelity == "literal-visual":
            literal_visual.append(slide)
        elif fidelity == "literal-text":
            literal_text.append(slide)
        else:
            creative.append(slide)

    return {
        "creative": creative,
        "literal-text": literal_text,
        "literal-visual": literal_visual,
    }


def normalize_slides_payload(
    slides_payload: Any,
    *,
    default_source_ref: str = "slide-brief.md",
    allow_placeholder_content: bool = False,
) -> list[dict[str, Any]]:
    """Normalize CLI fidelity payloads into dispatch-ready slide rows.

    Accepts either a list of slide dicts or an object containing ``slides``.
    Adds fallback ``source_ref`` when missing.
    By default, missing ``content`` is a hard failure to prevent metadata-only
    dispatches from being sent to Gamma. Placeholder content is available only
    in explicit debug mode via ``allow_placeholder_content=True``.
    """
    if isinstance(slides_payload, list):
        slides = slides_payload
    elif isinstance(slides_payload, dict) and isinstance(slides_payload.get("slides"), list):
        slides = slides_payload["slides"]
    else:
        raise ValueError("Invalid slides payload. Expected list or object with 'slides' array.")

    normalized: list[dict[str, Any]] = []
    missing_content_slides: list[Any] = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue

        row = dict(slide)
        source_ref = str(row.get("source_ref", "")).strip()
        if not source_ref:
            anchors = row.get("source_anchors")
            if isinstance(anchors, list) and anchors:
                source_ref = "; ".join(str(a) for a in anchors)
            elif isinstance(anchors, str) and anchors.strip():
                source_ref = anchors.strip()
            else:
                source_ref = f"{default_source_ref}#Slide {row.get('slide_number', '?')}"
            row["source_ref"] = source_ref

        content = str(row.get("content", "")).strip()
        if not content:
            slide_number = row.get("slide_number", "?")
            if allow_placeholder_content:
                fidelity = row.get("fidelity", "creative")
                title = row.get("title") or row.get("slide_title") or f"Slide {slide_number}"
                row["content"] = (
                    f"{title}\n\n"
                    f"[{fidelity} slide placeholder derived from pre-dispatch artifacts. "
                    f"Source anchors: {source_ref}]"
                )
            else:
                missing_content_slides.append(slide_number)

        normalized.append(row)

    if missing_content_slides:
        missing_str = ", ".join(str(n) for n in missing_content_slides)
        raise ValueError(
            "Slides payload missing required content for slide_number(s): "
            f"{missing_str}. Provide a content-bearing payload via "
            "--slides-content-json (or include content in --fidelity-json). "
            "Use --allow-placeholder-content only for debug workflows."
        )

    return normalized


def merge_slide_content(
    fidelity_slides_payload: Any,
    slide_content_payload: Any,
    *,
    default_source_ref: str = "slide-brief.md",
    allow_placeholder_content: bool = False,
) -> list[dict[str, Any]]:
    """Merge fidelity metadata rows with content-bearing slide rows by number."""
    fidelity_rows = normalize_slides_payload(
        fidelity_slides_payload,
        default_source_ref=default_source_ref,
        allow_placeholder_content=True,
    )
    content_rows = normalize_slides_payload(
        slide_content_payload,
        default_source_ref=default_source_ref,
        allow_placeholder_content=False,
    )

    content_by_slide: dict[Any, dict[str, Any]] = {
        row.get("slide_number"): row for row in content_rows
    }
    merged_rows: list[dict[str, Any]] = []
    missing_content_slides: list[Any] = []

    for row in fidelity_rows:
        merged = dict(row)
        content_row = content_by_slide.get(row.get("slide_number"))
        if content_row:
            if content_row.get("content"):
                merged["content"] = content_row["content"]
            if content_row.get("source_ref"):
                merged["source_ref"] = content_row["source_ref"]
        elif not allow_placeholder_content:
            missing_content_slides.append(row.get("slide_number", "?"))
        merged_rows.append(merged)

    if missing_content_slides:
        missing_str = ", ".join(str(n) for n in missing_content_slides)
        raise ValueError(
            "Slides payload missing required content for slide_number(s): "
            f"{missing_str}. Provide a content-bearing payload via --slides-content-json."
        )

    return normalize_slides_payload(
        merged_rows,
        default_source_ref=default_source_ref,
        allow_placeholder_content=allow_placeholder_content,
    )


def build_doc_title(
    module_lesson_part: str,
    fidelity_class: str,
    slide_numbers: list[int],
) -> str:
    """Build a formulaic Gamma document title for archival integrity.

    Pattern: {module-lesson-part}_{fidelity-class}_{slide-range}
    Examples: C1-M1-P2-Macro-Trends_creative_s01-s09
              C1-M1-P2-Macro-Trends_literal_s10
    """
    if len(slide_numbers) == 1:
        slide_range = f"s{slide_numbers[0]:02d}"
    else:
        slide_range = f"s{min(slide_numbers):02d}-s{max(slide_numbers):02d}"
    return f"{module_lesson_part}_{fidelity_class}_{slide_range}"


def reassemble_slide_output(
    creative_results: list[dict[str, Any]],
    literal_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Reassemble results from Gamma calls into unified slide output.

    Both lists should contain dicts with 'card_number' for ordering.
    Returns a unified list sorted by card_number with provenance metadata.
    """
    all_results = []

    for item in creative_results:
        item["source_call"] = "creative"
        item["fidelity"] = "creative"
        item["visual_description"] = (
            f"Creative slide generated by Gamma for card {item.get('card_number')}; "
            "final visual grounding occurs in perception artifacts."
        )
        all_results.append(item)

    for item in literal_results:
        fidelity = item.get("fidelity", "literal-text")
        item["source_call"] = fidelity
        item["visual_description"] = (
            f"{fidelity} slide generated by Gamma for card {item.get('card_number')}; "
            "source text constraints enforced for literal fidelity."
        )
        all_results.append(item)

    all_results.sort(key=lambda x: x.get("card_number", 0))
    return all_results


def validate_image_url(url: str, timeout: int = 10) -> tuple[bool, str]:
    """Validate that an image URL is HTTPS-accessible with an image content type.

    Returns:
        (is_valid, reason) tuple.
    """
    if not url.startswith("https://"):
        return False, "URL must use HTTPS"

    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
    has_image_ext = any(url.lower().split("?")[0].endswith(ext) for ext in image_extensions)

    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"

        content_type = resp.headers.get("content-type", "")
        if "image/" in content_type or has_image_ext:
            return True, "OK"

        return (
            False,
            f"Content-Type '{content_type}' is not an image type and URL lacks image extension",
        )
    except requests.RequestException as e:
        return False, f"Request failed: {e}"


if __name__ == "__main__":
    import json
    import sys

    usage = (
        "Usage: python gamma_operations.py <command> [args]\n"
        "Commands:\n"
        "  generate <input_text_file> [--params-json <params_json>]\n"
        "    [--style-preset <preset_name>] [--theme-resolution-json <theme_json>]\n"
        "    [--slides-content-json <slides_content_json>]\n"
        "    [--fidelity-json <slides_json>] [--module <id>]\n"
        "    [--allow-placeholder-content]\n"
        "    [--diagram-cards <json>] [--run-id <production_run_id>]\n"
        "  list-themes-templates [--scope <scope>] [--content-type <type>] [--limit <n>]\n"
        "  validate-url <url>\n"
        "  merge-params <style_json> <template_json> <envelope_json> [--fidelity-class <class>]"
    )

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "validate-url" and len(sys.argv) >= 3:
        valid, reason = validate_image_url(sys.argv[2])
        print(json.dumps({"valid": valid, "reason": reason}))
        sys.exit(0 if valid else 1)

    if cmd == "merge-params" and len(sys.argv) >= 5:
        style = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        template = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
        envelope = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
        fc = "creative"
        if "--fidelity-class" in sys.argv:
            fc = sys.argv[sys.argv.index("--fidelity-class") + 1]
        result = merge_parameters(style, template, envelope, fidelity_class=fc)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    if cmd == "generate" and len(sys.argv) >= 3:
        input_text = Path(sys.argv[2]).read_text(encoding="utf-8")
        slides_data = None
        raw_fidelity_data: Any | None = None
        raw_slide_content_data: Any | None = None
        module_id = ""
        diagram_cards_data = None
        params: dict[str, Any] = {"input_text": input_text, "textMode": "generate"}
        allow_placeholder_content = "--allow-placeholder-content" in sys.argv

        if "--params-json" in sys.argv:
            idx = sys.argv.index("--params-json") + 1
            params = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))

        if "--style-preset" in sys.argv:
            idx = sys.argv.index("--style-preset") + 1
            preset_name = sys.argv[idx]
            style_preset_params = resolve_style_preset(preset_name)
            params = merge_parameters({}, {}, params, style_preset=style_preset_params)

        if "--theme-resolution-json" in sys.argv:
            idx = sys.argv.index("--theme-resolution-json") + 1
            theme_resolution = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))
            params["theme_resolution"] = theme_resolution
            # Only set themeId from resolution if --style-preset didn't
            # already resolve it to the actual Gamma API theme ID.
            if "themeId" not in params:
                resolved_theme_key = theme_resolution.get("resolved_theme_key")
                if resolved_theme_key:
                    params["themeId"] = resolved_theme_key

        params.setdefault("input_text", input_text)
        params.setdefault("textMode", "generate")

        if "--slides-content-json" in sys.argv:
            idx = sys.argv.index("--slides-content-json") + 1
            raw_slide_content_data = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))

        if "--fidelity-json" in sys.argv:
            idx = sys.argv.index("--fidelity-json") + 1
            raw_fidelity_data = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))

        if raw_fidelity_data is not None and raw_slide_content_data is not None:
            slides_data = merge_slide_content(
                raw_fidelity_data,
                raw_slide_content_data,
                allow_placeholder_content=allow_placeholder_content,
            )
        elif raw_fidelity_data is not None:
            slides_data = normalize_slides_payload(
                raw_fidelity_data,
                allow_placeholder_content=allow_placeholder_content,
            )
        elif raw_slide_content_data is not None:
            slides_data = normalize_slides_payload(
                raw_slide_content_data,
                allow_placeholder_content=allow_placeholder_content,
            )

        if "--module" in sys.argv:
            idx = sys.argv.index("--module") + 1
            module_id = sys.argv[idx]
        if "--diagram-cards" in sys.argv:
            idx = sys.argv.index("--diagram-cards") + 1
            diagram_cards_data = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))
            if isinstance(diagram_cards_data, dict):
                diagram_cards_data = diagram_cards_data.get(
                    "cards",
                    diagram_cards_data.get("diagram_cards", []),
                )

        run_id_cli: str | None = None
        if "--run-id" in sys.argv:
            idx = sys.argv.index("--run-id") + 1
            if idx < len(sys.argv):
                run_id_cli = sys.argv[idx]

        result = execute_generation(
            params,
            slides=slides_data,
            module_lesson_part=module_id,
            diagram_cards=diagram_cards_data,
            run_id=run_id_cli,
        )
        # Embed content source provenance for Gate 2 audit trail
        if isinstance(result, dict):
            _sc_path: str | None = None
            if "--slides-content-json" in sys.argv:
                _sc_idx = sys.argv.index("--slides-content-json") + 1
                if _sc_idx < len(sys.argv):
                    _sc_path = sys.argv[_sc_idx]
            result["dispatch_metadata"] = {"slides_content_json_path": _sc_path}
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0)

    if cmd == "list-themes-templates":
        scope: str | None = None
        content_type: str | None = None
        limit = 20
        if "--scope" in sys.argv:
            idx = sys.argv.index("--scope") + 1
            if idx < len(sys.argv):
                scope = sys.argv[idx]
        if "--content-type" in sys.argv:
            idx = sys.argv.index("--content-type") + 1
            if idx < len(sys.argv):
                content_type = sys.argv[idx]
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit") + 1
            if idx < len(sys.argv):
                limit = int(sys.argv[idx])

        result = list_themes_and_templates(
            scope=scope,
            content_type=content_type,
            limit=limit,
        )
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0)

    print(usage)
    sys.exit(1)
