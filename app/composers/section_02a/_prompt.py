"""Prompt rendering and cache-key normalization for Section 02A.

The cache key strips volatile request identity before hashing:

- ``operator_id`` lines vary by operator session and do not affect semantics.
- ISO-8601 timestamps such as ``generated_at`` vary per render.
- UUID4 ``run_id`` values vary per trial run.

The normalized prompt is hashed with SHA256 so fixture-replay and future live
LLM runs can reuse responses across equivalent corpus classification prompts.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = REPO_ROOT / "docs" / "conversational-gates"
TEMPLATE_NAME = "section-02a-composer.j2"

VOLATILE_PROMPT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"operator_id\s*[:=]\s*[^,\n]+", re.IGNORECASE), "operator_id:<stripped>"),
    (
        re.compile(
            r"generated_at\s*[:=]\s*\d{4}-\d{2}-\d{2}T[0-9:.+-]+Z?",
            re.IGNORECASE,
        ),
        "generated_at:<stripped>",
    ),
    (
        re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-"
            r"[0-9a-f]{12}\b",
            re.IGNORECASE,
        ),
        "<uuid4-stripped>",
    ),
)


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
        autoescape=False,
    )


def corpus_summary_for(files: list[Path], corpus_dir: Path) -> str:
    relative_paths = [path.relative_to(corpus_dir).as_posix() for path in files]
    return "\n".join(f"- {path}" for path in relative_paths)


def binary_sample_hex(file_path: Path, *, sample_bytes: int = 64) -> str:
    return file_path.read_bytes()[:sample_bytes].hex()


def render_classification_prompt(
    *,
    file_path: Path,
    corpus_dir: Path,
    corpus_summary: str,
) -> str:
    template = _environment().get_template(TEMPLATE_NAME)
    relative = file_path.relative_to(corpus_dir).as_posix()
    return template.render(
        filename=relative,
        file_size_bytes=file_path.stat().st_size,
        file_extension=file_path.suffix.lower(),
        binary_sample_hex=binary_sample_hex(file_path),
        corpus_summary=corpus_summary,
    )


def normalize_prompt(prompt: str) -> str:
    normalized = prompt
    for pattern, replacement in VOLATILE_PROMPT_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
    return normalized


def cache_key_for_prompt(prompt: str) -> str:
    return hashlib.sha256(normalize_prompt(prompt).encode("utf-8")).hexdigest()


__all__ = [
    "TEMPLATE_NAME",
    "binary_sample_hex",
    "cache_key_for_prompt",
    "corpus_summary_for",
    "normalize_prompt",
    "render_classification_prompt",
]

