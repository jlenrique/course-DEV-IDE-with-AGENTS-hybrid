"""CLI-side adapter bridging §02A composer to the (path, digest) call contract.

Owned by the §02A composer module (Winston W-A1, 2026-05-21 SCP §7) so that
future consumers — workflow runner, Marcus-interactive Epic, re-run tools —
reuse this call-shape bridge instead of reinventing it.

The §02A composer module exposes:
    compose(corpus_dir, *, llm, cache) -> Directive
    write_directive_yaml(directive, path) -> Path

Callers historically expect:
    compose_legacy(...) -> Composed
    materialize(composed, run_dir) -> (Path, str)  # (path, sha256_digest)

This adapter is the canonical bridge between those shapes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_core.language_models import BaseChatModel

from app.composers.section_02a._cache import ComposerCache
from app.composers.section_02a.composer import compose, write_directive_yaml


def compose_and_write(
    corpus_dir: Path,
    run_dir: Path,
    *,
    llm: BaseChatModel | None = None,
) -> tuple[Path, str]:
    """Compose a §02A directive for ``corpus_dir`` and write it under ``run_dir``.

    Args:
        corpus_dir: corpus root (must be a directory).
        run_dir: per-trial run directory; the directive lands at
            ``run_dir / "directive.yaml"``.
        llm: optional ``BaseChatModel`` instance. When ``None``, the adapter
            resolves Marcus's configured chat model via
            ``make_chat_model("marcus").chat``. Tests inject a fake.

    Returns:
        ``(directive_path, sha256_digest_hex)`` tuple — matches the legacy
        ``materialize_directive`` contract that ``app/marcus/cli/trial.py``
        previously consumed.

    Known seams (TODO(post-trial-3-retro)):
        * The §02A composer's ``Directive`` model carries an internally-
          generated ``run_id = uuid4()`` independent of any caller-supplied
          trial_id. The trial CLI's ``effective_trial_id`` is therefore NOT
          threaded into the directive payload. Filed as deferred-inventory
          entry ``trial-cli-effective-trial-id-vs-section-02a-composer-run-id
          -divergence``; reactivation = post-Trial-3 retrospective.
        * ``make_chat_model("marcus")`` returns a NamedTuple ``ChatModelHandle
          (chat, entry)`` where ``entry`` is the NFR-X4 ``ModelResolutionEntry``
          audit record. This adapter intentionally discards ``entry``; the
          trial CLI does not currently exercise ``RunState.model_resolution_trail``
          append. Filed as deferred-inventory entry ``trial-cli-model-
          resolution-trail-not-appended-from-adapter``; reactivation =
          post-Trial-3 retrospective.
    """
    if llm is None:
        from app.models.adapter import make_chat_model

        llm = make_chat_model("marcus").chat

    directive = compose(corpus_dir, llm=llm, cache=ComposerCache())
    directive_path = run_dir / "directive.yaml"
    write_directive_yaml(directive, directive_path)
    digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    return directive_path, digest


__all__ = ["compose_and_write"]
