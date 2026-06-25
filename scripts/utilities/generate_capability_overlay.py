"""Generate Marcus's capability-overlay honesty map (Braid Story S4 — DP1).

GENERATED, never hand-authored. This module derives a closed-enum
``capability-state`` artifact for every specialist *mechanically* from the live
substrate so the frontier-model orchestrator (Marcus) cannot over-promise a
capability the dispatch graph does not actually route to.

Four signals are computed per specialist (canonical id):

============== ====================================================================
signal         source
============== ====================================================================
``in_manifest``   a ``nodes[].specialist_id`` (canonicalized) appears in the
                  pipeline manifest
``in_dispatch``   a key appears in ``dispatch-registry.yaml::specialists``
``real_module``   ``app/specialists/<id>/graph.py`` exists AND its dispatch builder
                  ref is NOT the ``_stub`` passthrough
                  (``app.specialists._stub.passthrough_specialist``)
``registry_status`` ``status:`` / ``partial-status:`` block membership in
                  ``specialist-registry.yaml``
============== ====================================================================

Closed-enum decision (top-to-bottom, first match wins):

1. ``partial``               — in_manifest AND in_dispatch AND real_module, but the
                               registry flags a contract gap (``partial-status:``).
2. ``wired``                 — in_manifest AND in_dispatch AND real_module, no flag.
3. ``present-but-unrouted``  — in_dispatch AND NOT in_manifest.
4. ``shelf``                 — a skill-on-disk / registry ``specialists:`` entry that
                               is NOT dispatchable AND NOT a manifest specialist_id
                               AND NOT consumed as a persona ``api_mastery_skill``.

``marcus`` is special-cased to ``role: orchestrator`` (NOT one of the four
specialist states): it appears in the manifest but is intentionally absent from
``dispatch-registry::specialists`` because it is the orchestrator, not a
dispatched specialist. (This is the ONLY non-mechanical entry; see
``_MARCUS_ID``.)

A computed value outside the closed enum is a generator bug → ``raise``.

Spec: ``_bmad-output/implementation-artifacts/spec-braid-s4-marcus-capability-overlay.md``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

# Single source of truth for hyphenated id / alias canonicalization (irene-pass1
# -> irene_pass1, quinn-r -> quinn_r, elevenlabs -> enrique). Imported (not
# copied) so manifest<->dispatch membership joins cannot drift from the compiler.
from app.manifest.compiler import SPECIALIST_ALIASES
from scripts.utilities.file_helpers import project_root
from scripts.utilities.pipeline_manifest import load_manifest

# --- closed enum -----------------------------------------------------------

CapabilityState = Literal["wired", "present-but-unrouted", "partial", "shelf"]
CAPABILITY_STATES: frozenset[str] = frozenset(
    {"wired", "present-but-unrouted", "partial", "shelf"}
)
ORCHESTRATOR_ROLE = "orchestrator"

SCHEMA_VERSION = "capability-overlay-v1"

# The orchestrator special-case (spec §"marcus is special-cased"). The ONLY
# hard-coded, non-mechanical entry: in-manifest, not-in-dispatch, by design.
_MARCUS_ID = "marcus"

# The _stub passthrough module that marks a node as NOT a real specialist.
_STUB_MODULE_PACKAGE = "app.specialists._stub"

GENERATOR_REF = "scripts/utilities/generate_capability_overlay.py"
DEFAULT_OVERLAY_PATH = (
    project_root() / "state" / "config" / "capability-overlay.yaml"
)

__all__ = [
    "CAPABILITY_STATES",
    "CapabilityState",
    "DEFAULT_OVERLAY_PATH",
    "MarcusEntry",
    "OverlayModel",
    "SpecialistEntry",
    "compute_content_hash",
    "derive_overlay",
    "is_stale",
    "main",
    "render_overlay_text",
    "validate_live_manifest",
    "write_overlay",
]


# --- Pydantic models -------------------------------------------------------


class SpecialistEntry(BaseModel):
    """One specialist's derived capability state (closed-enum)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_state: CapabilityState
    in_manifest: bool
    in_dispatch: bool
    real_module: bool
    registry_status: str | None = None
    routed_at_nodes: tuple[str, ...] = ()
    rationale: str = ""


class MarcusEntry(BaseModel):
    """The orchestrator special-case (not one of the four specialist states)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    role: Literal["orchestrator"] = ORCHESTRATOR_ROLE
    in_manifest: bool
    in_dispatch: bool
    note: str = (
        "orchestrator special-case per spec-braid-s4; not a dispatched specialist."
    )


class OverlayModel(BaseModel):
    """The full derived overlay (sorted, deterministic)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = SCHEMA_VERSION
    generated_from: dict[str, str]
    generator_ref: str = GENERATOR_REF
    specialists: dict[str, SpecialistEntry]
    marcus: MarcusEntry = Field(...)


# --- canonicalization ------------------------------------------------------


def canonical_id(specialist_id: str | None) -> str | None:
    """Canonicalize a specialist id (mirror of compiler._canonical_specialist_id).

    Resolves hyphenated ids and aliases via the single-source ``SPECIALIST_ALIASES``
    map plus ``-`` -> ``_`` normalization, so manifest (``irene-pass1`` /
    ``quinn-r`` / ``elevenlabs``) joins dispatch (``irene_pass1`` / ``quinn_r`` /
    ``enrique``) correctly.
    """
    if specialist_id is None:
        return None
    normalized = specialist_id.replace("-", "_")
    return SPECIALIST_ALIASES.get(
        specialist_id, SPECIALIST_ALIASES.get(normalized, normalized)
    )


# --- substrate loaders -----------------------------------------------------


def _load_yaml(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _manifest_specialist_ids(repo_root: Path) -> set[str]:
    """Canonical specialist ids that appear on a manifest node (excluding null)."""
    manifest_path = repo_root / "state" / "config" / "pipeline-manifest.yaml"
    raw = _load_yaml(manifest_path)
    ids: set[str] = set()
    for node in raw.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        canonical = canonical_id(node.get("specialist_id"))
        if canonical is not None:
            ids.add(canonical)
    return ids


def _manifest_routed_nodes(repo_root: Path) -> dict[str, tuple[str, ...]]:
    """Map canonical specialist id -> sorted tuple of manifest node ids routing to it."""
    manifest_path = repo_root / "state" / "config" / "pipeline-manifest.yaml"
    raw = _load_yaml(manifest_path)
    routed: dict[str, list[str]] = {}
    for node in raw.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        canonical = canonical_id(node.get("specialist_id"))
        node_id = node.get("id")
        if canonical is None or node_id is None:
            continue
        routed.setdefault(canonical, []).append(str(node_id))
    return {key: tuple(sorted(value)) for key, value in routed.items()}


def _dispatch_specialists(repo_root: Path) -> dict[str, str]:
    """Canonical specialist id -> builder ref from the dispatch registry."""
    registry_path = repo_root / "state" / "config" / "dispatch-registry.yaml"
    raw = _load_yaml(registry_path)
    specialists = raw.get("specialists")
    if not isinstance(specialists, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in specialists.items():
        canonical = canonical_id(str(key))
        if canonical is not None:
            out[canonical] = str(value)
    return out


def _real_module(repo_root: Path, canonical: str, builder_ref: str | None) -> bool:
    """True iff ``app/specialists/<id>/graph.py`` exists AND builder is not the stub.

    The not-stub check is live: a dispatch entry whose builder module resolves to
    the ``_stub`` passthrough is NOT a real specialist even if the graph.py file
    exists (AC-3).
    """
    graph_path = repo_root / "app" / "specialists" / canonical / "graph.py"
    if not graph_path.is_file():
        return False
    if builder_ref is None:
        return False
    module_name = builder_ref.partition(":")[0]
    # Any reference into the _stub package marks a node as NOT a real specialist
    # — match the exact package or a dotted submodule (e.g. both
    # ``app.specialists._stub:passthrough_node`` via the package re-export AND
    # ``app.specialists._stub.passthrough_specialist:...``) so a re-export cannot
    # bypass the not-stub honesty guard into a false ``wired``.
    is_stub = module_name == _STUB_MODULE_PACKAGE or module_name.startswith(
        _STUB_MODULE_PACKAGE + "."
    )
    return not is_stub


def _registry_views(repo_root: Path) -> tuple[dict, dict, dict, dict, set[str]]:
    """Return (specialists_map, personas_map, partial_status_map, raw, persona_backed_paths).

    ``persona_backed_paths`` is the set of SKILL.md paths that back a dispatched
    persona — every ``persona_skill`` and ``api_mastery_skill`` referenced by the
    ``personas:`` AND ``partial-status:`` blocks. A ``specialists:`` registry entry
    whose ``path`` is in this set is the skill BEHIND a dispatched persona (e.g.
    ``content-creator`` → Irene, ``fidelity-assessor`` → Vera, ``gamma-specialist``
    consumed by Gary) and is therefore NOT ``shelf`` — the conservative
    fuzzy-boundary rule (API-mastery + role skills are consumed-by a persona, not
    standalone shelf capabilities).
    """
    registry_path = (
        repo_root
        / "skills"
        / "bmad-agent-marcus"
        / "references"
        / "specialist-registry.yaml"
    )
    raw = _load_yaml(registry_path)
    specialists = raw.get("specialists") or {}
    personas = raw.get("personas") or {}
    partial_status = raw.get("partial-status") or {}
    persona_backed_paths: set[str] = set()
    for block in (personas, partial_status):
        for persona in block.values():
            if not isinstance(persona, dict):
                continue
            for key in ("persona_skill", "api_mastery_skill"):
                value = persona.get(key)
                if isinstance(value, str):
                    persona_backed_paths.add(value)
    return specialists, personas, partial_status, raw, persona_backed_paths


def _shelf_token(registry_key: str) -> str:
    """Derive the conservative canonical shelf token from a registry specialists key.

    Registry keys are API/skill names (e.g. ``midjourney-specialist``,
    ``canva-specialist``); strip the ``-specialist`` suffix and canonicalize.
    """
    token = registry_key
    if token.endswith("-specialist"):
        token = token[: -len("-specialist")]
    return canonical_id(token) or token


# --- derivation ------------------------------------------------------------


def derive_overlay(repo_root: Path | None = None) -> OverlayModel:
    """Derive the closed-enum capability overlay from the live substrate.

    Pure function: loads manifest + dispatch-registry + on-disk modules +
    specialist-registry status, canonicalizes ids, applies the first-match-wins
    decision table, returns a sorted :class:`OverlayModel`. Raises if any computed
    state falls outside the closed enum.
    """
    root = repo_root if repo_root is not None else project_root()

    manifest_ids = _manifest_specialist_ids(root)
    routed_nodes = _manifest_routed_nodes(root)
    dispatch = _dispatch_specialists(root)
    specialists_map, _personas, partial_status, _raw, persona_backed_paths = (
        _registry_views(root)
    )

    partial_ids = {canonical_id(str(key)) for key in partial_status}

    entries: dict[str, SpecialistEntry] = {}

    # --- 1) dispatchable specialists (the universe that can carry a 4-state) ---
    for canonical, builder_ref in dispatch.items():
        if canonical == _MARCUS_ID:
            # Defensive: marcus is never in dispatch by design; if it ever is,
            # the special-case below still wins. Skip it from the 4-state set.
            continue
        in_manifest = canonical in manifest_ids
        in_dispatch = True
        real_module = _real_module(root, canonical, builder_ref)
        is_partial = canonical in partial_ids
        routed = routed_nodes.get(canonical, ())

        state, rationale, registry_status = _classify_dispatchable(
            canonical=canonical,
            in_manifest=in_manifest,
            real_module=real_module,
            is_partial=is_partial,
        )
        entries[canonical] = SpecialistEntry(
            capability_state=state,
            in_manifest=in_manifest,
            in_dispatch=in_dispatch,
            real_module=real_module,
            registry_status=registry_status,
            routed_at_nodes=routed,
            rationale=rationale,
        )

    # --- 2) shelf specialists (skill on disk / registry entry, NOT dispatchable) ---
    for registry_key, meta in specialists_map.items():
        token = _shelf_token(str(registry_key))
        if token in dispatch or token in manifest_ids:
            continue  # dispatchable or routed → handled above / not shelf
        path = None
        if isinstance(meta, dict):
            path = meta.get("path")
        if isinstance(path, str) and path in persona_backed_paths:
            # Skill BEHIND a dispatched persona — either the persona's role skill
            # (content-creator→Irene, fidelity-assessor→Vera, quality-reviewer→
            # Quinn-R, creative-director→Dan/CD) or an API-mastery skill consumed
            # by one (gamma/kling/elevenlabs/wondercraft). Conservatively NOT shelf.
            continue
        if token in entries:
            continue
        entries[token] = SpecialistEntry(
            capability_state="shelf",
            in_manifest=False,
            in_dispatch=False,
            real_module=(root / "app" / "specialists" / token / "graph.py").is_file(),
            registry_status=(
                meta.get("status") if isinstance(meta, dict) else None
            ),
            routed_at_nodes=(),
            rationale=(
                "skill present in registry/on-disk but not in dispatch-registry "
                "and not a manifest specialist_id (shelf)."
            ),
        )

    # --- closed-enum guard ---
    for canonical, entry in entries.items():
        if entry.capability_state not in CAPABILITY_STATES:
            raise ValueError(
                f"capability_state {entry.capability_state!r} for {canonical!r} is "
                f"outside the closed enum {sorted(CAPABILITY_STATES)} — generator bug"
            )

    sorted_entries = {key: entries[key] for key in sorted(entries)}

    marcus_entry = MarcusEntry(
        in_manifest=_MARCUS_ID in manifest_ids,
        in_dispatch=_MARCUS_ID in dispatch,
    )

    return OverlayModel(
        schema_version=SCHEMA_VERSION,
        generated_from={
            "pipeline_manifest": "state/config/pipeline-manifest.yaml",
            "dispatch_registry": "state/config/dispatch-registry.yaml",
            "specialist_registry": (
                "skills/bmad-agent-marcus/references/specialist-registry.yaml"
            ),
        },
        generator_ref=GENERATOR_REF,
        specialists=sorted_entries,
        marcus=marcus_entry,
    )


def _classify_dispatchable(
    *,
    canonical: str,
    in_manifest: bool,
    real_module: bool,
    is_partial: bool,
) -> tuple[CapabilityState, str, str | None]:
    """Apply the first-match-wins decision table for a dispatchable specialist."""
    # 1) partial — in_manifest AND in_dispatch AND real_module, registry flags a gap.
    if in_manifest and real_module and is_partial:
        return (
            "partial",
            (
                "in-manifest + dispatchable + real module, but registry flags a "
                "contract gap (partial-status block)."
            ),
            "PARTIAL",
        )
    # 2) wired — in_manifest AND in_dispatch AND real_module, no partial flag.
    if in_manifest and real_module:
        return (
            "wired",
            "manifest node + dispatch entry + real not-stub module.",
            "active",
        )
    # 3) present-but-unrouted — in_dispatch AND NOT in_manifest.
    if not in_manifest:
        return (
            "present-but-unrouted",
            (
                "dispatchable + real module, but no manifest node routes to it "
                "(the Tracy bug class)."
            ),
            "active" if real_module else None,
        )
    # Fallthrough: in_manifest + in_dispatch but the module is the stub / missing.
    # Per the not-stub rule this is NOT wired; it is present (dispatchable) but
    # the real module isn't there → treat as present-but-unrouted-equivalent.
    return (
        "present-but-unrouted",
        (
            "in-manifest + dispatchable but the on-disk module is the stub "
            "passthrough or missing — not a real specialist (not wired)."
        ),
        None,
    )


# --- hashing + serialization ----------------------------------------------


def _canonical_facts(overlay: OverlayModel) -> dict:
    """The derived-facts projection the content_hash is computed over.

    Deliberately excludes the ``content_hash`` itself and presentation-only
    metadata; it is the *facts* (states + signals) that must round-trip stably.
    """
    return {
        "schema_version": overlay.schema_version,
        "specialists": {
            sid: {
                "capability_state": entry.capability_state,
                "in_manifest": entry.in_manifest,
                "in_dispatch": entry.in_dispatch,
                "real_module": entry.real_module,
                "registry_status": entry.registry_status,
                "routed_at_nodes": list(entry.routed_at_nodes),
            }
            for sid, entry in sorted(overlay.specialists.items())
        },
        "marcus": {
            "role": overlay.marcus.role,
            "in_manifest": overlay.marcus.in_manifest,
            "in_dispatch": overlay.marcus.in_dispatch,
        },
    }


def compute_content_hash(overlay: OverlayModel) -> str:
    """sha256 over a canonical serialization of the *derived facts*."""
    blob = json.dumps(_canonical_facts(overlay), sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _overlay_to_doc(overlay: OverlayModel) -> dict:
    """Build the deterministic, sorted YAML document (with content_hash)."""
    doc: dict = {
        "schema_version": overlay.schema_version,
        "generated_from": dict(overlay.generated_from),
        "generator_ref": overlay.generator_ref,
        "content_hash": compute_content_hash(overlay),
        "specialists": {
            sid: {
                "capability_state": entry.capability_state,
                "in_manifest": entry.in_manifest,
                "in_dispatch": entry.in_dispatch,
                "real_module": entry.real_module,
                "registry_status": entry.registry_status,
                "routed_at_nodes": list(entry.routed_at_nodes),
                "rationale": entry.rationale,
            }
            for sid, entry in sorted(overlay.specialists.items())
        },
        "marcus": {
            "role": overlay.marcus.role,
            "in_manifest": overlay.marcus.in_manifest,
            "in_dispatch": overlay.marcus.in_dispatch,
            "note": overlay.marcus.note,
        },
    }
    return doc


_HEADER = (
    "# GENERATED by scripts/utilities/generate_capability_overlay.py — "
    "DO NOT HAND-EDIT.\n"
    "# Regenerate after any change to the manifest, dispatch-registry, "
    "app/specialists/,\n"
    "# or specialist-registry.yaml status fields. CI parity test "
    "(tests/parity/test_capability_overlay_parity.py)\n"
    "# fails if this file is stale. Spec: "
    "_bmad-output/implementation-artifacts/spec-braid-s4-marcus-capability-overlay.md\n"
)


def render_overlay_text(overlay: OverlayModel) -> str:
    """Render the deterministic YAML text (header + sorted, stable-key body)."""
    body = yaml.safe_dump(
        _overlay_to_doc(overlay),
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )
    return _HEADER + body


def write_overlay(overlay: OverlayModel, path: Path = DEFAULT_OVERLAY_PATH) -> None:
    """Emit the deterministic YAML artifact to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_overlay_text(overlay), encoding="utf-8")


def validate_live_manifest(repo_root: Path | None = None) -> None:
    """Reuse ``load_manifest`` to validate the live manifest loads structurally.

    Kept separate from :func:`derive_overlay` (which reads raw YAML for the
    lossy-on-projection ``specialist_id`` field) so tmp-mirror drift tests that
    intentionally mutate the manifest are not blocked by full-schema validation.
    """
    root = repo_root if repo_root is not None else project_root()
    load_manifest(root / "state" / "config" / "pipeline-manifest.yaml")


def is_stale(
    repo_root: Path | None = None, path: Path = DEFAULT_OVERLAY_PATH
) -> bool:
    """True iff the committed artifact diverges from a fresh derivation."""
    root = repo_root if repo_root is not None else project_root()
    if not path.is_file():
        return True
    fresh = render_overlay_text(derive_overlay(root))
    return path.read_text(encoding="utf-8") != fresh


# --- CLI -------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Marcus capability-overlay honesty map (Braid S4)."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the on-disk overlay is stale (for the lockstep hook).",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_OVERLAY_PATH,
        help="Overlay artifact path (default: state/config/capability-overlay.yaml).",
    )
    args = parser.parse_args(argv)

    # Validate the live manifest loads structurally (reuse load_manifest) before
    # deriving — surfaces manifest corruption with a clear error.
    validate_live_manifest()
    overlay = derive_overlay()

    if args.check:
        if is_stale(path=args.path):
            print(
                f"capability-overlay STALE: {args.path} diverges from a fresh "
                "derivation — run `python -m scripts.utilities."
                "generate_capability_overlay` to regenerate."
            )
            return 1
        print(f"capability-overlay fresh: {args.path}")
        return 0

    write_overlay(overlay, args.path)
    print(f"wrote capability-overlay: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
