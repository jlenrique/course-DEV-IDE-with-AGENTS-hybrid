"""Dan creative-director specialist graph (Story 2b.6)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS
from app.specialists.source_bundle import read_extracted_source
from app.specialists.texas.graph import SanctumLockViolation as _SanctumLockViolation
from app.styleguide.parity import canonical_resolution_digest
from app.styleguide.resolver import (
    GAMMA_STYLE_GUIDES_PATH,
    load_style_guides,
    resolve_styleguide,
)
from scripts.utilities.creative_directive_validator import (
    load_experience_profile_targets,
    validate_creative_directive,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-cd"
CD_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-cd" / "references"
CD_REFERENCES: tuple[str, ...] = (
    "capability-authoring.md",
    "creative-directive-contract.md",
    "first-breath.md",
    "memory-guidance.md",
    "profile-targets.md",
)
CD_SANCTUM_LOCK_BASELINE: dict[str, str] = {
    "BOND.md": "7fd28acbf4ed5e46663559e7a5b8192d6fa6148ca02bda5b4eafa670a9ca8747",
    "CAPABILITIES.md": "ed104320a7c9aee47d8c8808e9de4255b72272775b67d4b8e32ffe009bf36d44",
    "CLONE-FORK-NOTICE.md": "3f217dda8cb9f251277c9cba647c6331c1da166abf43931979da7e75366423aa",
    "CREED.md": "c78c2e7431c1315d32dba8ceb10ac0b899e9ca56f0437e28225f900c98d7573c",
    "INDEX.md": "cc74ce849711e7bbb0f707cf73dcd75ef0922cd35409bec32e63773d6c45337f",
    "MEMORY.md": "43259e9f8d903e2addb92724dde5adfe69399cd7da2cc0f41931e998d7170962",
    "PERSONA.md": "e5404eca64fcc0cecf7a5038cf406cf3b6dcdc1e5eb479cc921c0c5d7f3d9a6e",
}

CD_SYSTEM_MESSAGE = (
    "You are Dan, the creative director. Choose the experience profile for "
    "this run and write its creative rationale. Return only JSON with one "
    "top-level key `cd_directive` whose value is an object carrying "
    "`experience_profile` (one of the configured profile names) and "
    "`creative_rationale` (a non-empty string). `schema_version`, "
    "`slide_mode_proportions`, and `narration_profile_controls` are bound "
    "deterministically to the chosen profile's configured targets."
)

TRANSITIONS: tuple[tuple[str, str], ...] = (
    ("receive", "plan"),
    ("plan", "act"),
    ("act", "verify"),
    ("verify", "reflect"),
    ("reflect", "emit_spans"),
    ("emit_spans", "gate_decision"),
    ("gate_decision", "finalize"),
    ("finalize", "handoff"),
)


class CdDirectiveParseError(RuntimeError):  # noqa: N818
    """Raised when Dan's creative directive cannot be parsed/validated.

    Carries the raw LLM response excerpt (Trial-3 finding #9 raw-response
    capture: the live 2/2 validator failures left no payload evidence) and
    any validator error list so postmortems see the offending output.
    """

    def __init__(
        self,
        message: str,
        *,
        tag: str,
        errors: list[str] | None = None,
        raw_excerpt: str | None = None,
    ) -> None:
        super().__init__(message)
        self.tag = tag
        self.errors = errors or []
        self.raw_excerpt = raw_excerpt


def _new_dispatch_trail_entry(
    last_entry: ModelResolutionEntry, *, tag: str
) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.exists() or not sanctum_dir.is_dir():
        return ""
    files = sorted(
        (p for p in sanctum_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(sanctum_dir).as_posix(),
    )
    if not files:
        return ""
    lines: list[str] = []
    for file_path in files:
        rel = file_path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(
            file_path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return "\n".join(lines)


def _current_sanctum_manifest(sanctum_dir: Path = SANCTUM_DIR) -> dict[str, str]:
    digest = _read_sanctum_digest(sanctum_dir=sanctum_dir)
    if not digest:
        return {}
    manifest: dict[str, str] = {}
    for line in digest.splitlines():
        rel, sha = line.split("\t", 1)
        if rel in CD_SANCTUM_LOCK_BASELINE:
            manifest[rel] = sha
    return manifest


def assert_sanctum_lock(
    expected_manifest: dict[str, str] = CD_SANCTUM_LOCK_BASELINE,
    *,
    sanctum_dir: Path = SANCTUM_DIR,
) -> None:
    current = _current_sanctum_manifest(sanctum_dir=sanctum_dir)
    if current != expected_manifest:
        missing = sorted(set(expected_manifest) - set(current))
        extra = sorted(set(current) - set(expected_manifest))
        mismatched = sorted(
            rel
            for rel in set(expected_manifest).intersection(current)
            if current[rel] != expected_manifest[rel]
        )
        raise _SanctumLockViolation(
            "cd sanctum lock baseline drift detected; "
            f"missing={missing}, extra={extra}, mismatched={mismatched}"
        )


def _read_cd_references(
    references_dir: Path = CD_REFERENCES_DIR,
    names: tuple[str, ...] = CD_REFERENCES,
) -> str:
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        header = f"### Reference: {name}\n"
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(header + body)
    return "\n\n".join(parts)


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        raise CdDirectiveParseError(
            "cd act envelope cache_prefix is missing",
            tag="cd_directive.parsed.missing-key",
        )
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise CdDirectiveParseError(
            f"cd act envelope cache_prefix is not valid JSON: {exc}",
            tag="cd_directive.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise CdDirectiveParseError(
            "cd act envelope cache_prefix must decode to a mapping",
            tag="cd_directive.parsed.wrong-type",
        )
    return decoded


def _profile_targets_prompt_block() -> str:
    profiles = load_experience_profile_targets()
    rendered = {
        name: {
            "slide_mode_proportions": target.get("slide_mode_proportions"),
            "narration_profile_controls": target.get("narration_profile_controls"),
        }
        for name, target in sorted(profiles.items())
        if isinstance(target, dict)
    }
    return json.dumps(rendered, indent=2, sort_keys=True)


def _assemble_cd_prompt(
    envelope_payload: dict[str, Any], *, extracted_source: str
) -> tuple[str, str]:
    payload_json = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    # Trial-3 cycle-2 content-plane fix (2026-06-12): the quarantined 4.75
    # edge delivered bundle METADATA only; the directive choice now sees the
    # actual extracted corpus it is styling.
    user_message = (
        "## Source corpus (extracted) — the material this directive styles\n\n"
        f"{extracted_source}\n\n"
        "## Sanctum digest\n\n"
        f"{_read_sanctum_digest()}\n\n"
        "## CD references\n\n"
        f"{_read_cd_references()}\n\n"
        "## Experience profile targets (authoritative)\n\n"
        f"```json\n{_profile_targets_prompt_block()}\n```\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "Return a single creative directive object under `cd_directive`: "
        "choose `experience_profile` from the targets above and write "
        "`creative_rationale`. The directive's numeric and control values "
        "are bound verbatim to the chosen profile's targets "
        "(validator-enforced parity)."
    )
    return CD_SYSTEM_MESSAGE, user_message


def _extract_json_text(raw_text: str) -> str:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    return stripped


_RAW_EXCERPT_CHARS = 500


def _raw_excerpt(raw_content: Any) -> str:
    if isinstance(raw_content, str):
        text = raw_content
    else:
        text = json.dumps(raw_content, sort_keys=True, default=str)
    return text[:_RAW_EXCERPT_CHARS]


def _canonicalize_cd_directive(
    directive: dict[str, Any], *, raw_excerpt: str
) -> dict[str, Any]:
    """Deterministically bind directive values to the chosen profile's targets.

    The validator's parity rule forbids ANY deviation from the configured
    profile targets in experience-profiles.yaml, so Dan's creative-judgment
    surface is exactly {experience_profile, creative_rationale}; the
    deterministic neck fills the rest (Hourglass model). Trial-3 finding #9:
    the prompt never carried the 11 narration-control target values, so the
    LLM could not emit a parity-passing directive — systematic 2/2 validator
    failure at CD's first live dispatch.
    """
    profiles = load_experience_profile_targets()
    profile = directive.get("experience_profile")
    if not isinstance(profile, str) or profile not in profiles:
        raise CdDirectiveParseError(
            f"cd directive experience_profile must be one of {sorted(profiles)}; "
            f"got {profile!r}; raw response excerpt: {raw_excerpt}",
            tag="cd_directive.parsed.validator-failed",
            raw_excerpt=raw_excerpt,
        )
    rationale = directive.get("creative_rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise CdDirectiveParseError(
            "cd directive creative_rationale must be a non-empty string; "
            f"raw response excerpt: {raw_excerpt}",
            tag="cd_directive.parsed.validator-failed",
            raw_excerpt=raw_excerpt,
        )
    target = profiles[profile]
    if (
        not isinstance(target, dict)
        or "slide_mode_proportions" not in target
        or "narration_profile_controls" not in target
    ):
        raise RuntimeError(
            f"experience profile {profile!r} target block is missing "
            "slide_mode_proportions/narration_profile_controls"
        )
    return {
        "schema_version": "1.0",
        "experience_profile": profile,
        "slide_mode_proportions": dict(target["slide_mode_proportions"]),
        "narration_profile_controls": dict(target["narration_profile_controls"]),
        # Rationale is preserved verbatim (S-2 rationale-verbatim-edges).
        "creative_rationale": rationale,
    }


# --- Canonical-arc S1 (D3): styleguide_resolution deterministic emission -----
# Spec: canonical-arc-s1-cd-styleguide-resolution-emission.md. CD is the
# styleguide-resolution AUDIT point (data emission only); Gary keeps authority
# until the deferred S-flip story.

STYLEGUIDE_RESOLUTION_SCHEMA_VERSION = 1
# F-202 (binding): the no-picks default binds the X5-ratified standard-A guide.
DEFAULT_STYLEGUIDE_NAME = "hil-2026-apc-crossroads-classic"
DEFAULT_STYLEGUIDE_PROVENANCE = (
    "authoring-time default; gary runtime seeds DEFAULT_VARIANT_PAIR until S2/S4"
)
# Remediation T2 (review 2026-07-06): the picker vocabulary — the only variant
# ids a pick may carry after normalization (strip + upper).
_PICK_VARIANT_VOCABULARY = frozenset({"A", "B"})
# 🔒 protected invariant (source-detail→Gamma conveyance), explicit on the record.
_LAYERING_MANIFEST: dict[str, str] = {
    "base_layer": "styleguide_defaults",
    "composition_rule": "source_derived_wins",
}


def _scrub_ssot_path(message: str, ssot_path: Path) -> str:
    """T10 rider: no absolute paths in resolver-error payloads (basename)."""
    return message.replace(str(ssot_path), ssot_path.name)


def _resolver_error_record(
    exc: Exception,
    *,
    variant_id: Any,
    styleguide: Any,
    ssot_path: Path,
) -> dict[str, Any]:
    return {
        "variant_id": variant_id,
        "styleguide": styleguide,
        "tag": getattr(exc, "tag", "gamma.styleguide.unexpected-error"),
        "message": _scrub_ssot_path(str(exc), ssot_path),
    }


def _pick_error_record(
    *, variant_id: Any, styleguide: Any, tag: str, message: str
) -> dict[str, Any]:
    return {
        "variant_id": variant_id,
        "styleguide": styleguide,
        "tag": tag,
        "message": message,
    }


def _bound_guide_entry(
    name: str, record: Any, ssot_digest: str | None
) -> dict[str, Any]:
    """One ``bound_guides`` entry.

    Remediation T6: ``lifecycle`` (and ``visibility`` when the record declares
    one) ride along as DATA so a deprecated/probe guide is VISIBLE at the
    audit point — NO enforcement here (parity with Gary's resolver behavior
    must hold; enforcement stays pick-time A-M1).
    """
    entry: dict[str, Any] = {"name": name, "ssot_digest": ssot_digest}
    if isinstance(record, dict):
        entry["lifecycle"] = record.get("lifecycle")
        presentation = record.get("presentation")
        visibility = (
            presentation.get("visibility") if isinstance(presentation, dict) else None
        )
        if visibility is not None:
            entry["visibility"] = visibility
    else:  # pragma: no cover — resolve_styleguide raises before this can bind
        entry["lifecycle"] = None
    return entry


def _styleguide_resolution_from_projection(
    directive_projection: dict[str, Any] | None,
    *,
    ssot_path: Path | None = None,
) -> dict[str, Any]:
    """Pure deterministic sibling of ``_canonicalize_cd_directive`` (SOP-002 2(b)).

    Emits the ``styleguide_resolution`` block for the ``_act`` output blob —
    a SIBLING of ``cd_directive``, never inside it. The LLM never touches
    resolution; fixed projection + fixed SSOT yaml ⇒ byte-stable output (AC-1).
    UNCONDITIONALLY total — NEVER a raise (CD is load-bearing; §06 must keep
    working mid-arc). ``ssot_path`` (optional) redirects the SSOT read for
    tests/audit replays; default is the production SSOT.

    Honesty-first status semantics (review remediation T2-T4/T7, 2026-07-06):

    - genuinely no picks (projection absent, ``gamma_settings`` null, or no
      entry carries a ``styleguide`` key) AND the F-202 default binds cleanly
      ⇒ ``no_picks_at_authoring`` with the default resolution emitted and
      ``default_provenance`` carrying the F-202 pin string;
    - ANY failure — invalid/blank/non-string pick name, variant id outside
      the picker vocabulary ``{A, B}`` after normalization, post-normalization
      variant collision, unknown/deprecated-surface resolver error, SSOT
      load/parse failure, or a default-bind failure on the no-picks path ⇒
      ``unresolvable_pick`` with EVERY failure recorded in ``errors`` (in pick
      order; T7) and ``default_provenance`` null when the default did not
      bind (T4);
    - ``input_picks`` echoes ALL ``gamma_settings`` entries verbatim
      (including inline-settings entries; T3), or null when the projection
      carries no ``gamma_settings`` list.

    The SSOT is read ONCE (T5): the ``ssot_digest`` in ``bound_guides``
    attests exactly the bytes the resolver parsed (via ``load_style_guides``'s
    additive ``content`` parameter).
    """
    path = Path(ssot_path) if ssot_path is not None else GAMMA_STYLE_GUIDES_PATH
    projection = directive_projection if isinstance(directive_projection, dict) else None
    raw_settings = projection.get("gamma_settings") if projection else None
    entries = list(raw_settings) if isinstance(raw_settings, list) else None
    directive_digest = projection.get("directive_digest") if projection else None
    provenance = (
        projection.get("styleguide_picker_provenance") if projection else None
    )

    errors: list[dict[str, Any]] = []

    # T5: ONE guarded read — digest and resolution from the same bytes.
    ssot_bytes: bytes | None = None
    ssot_digest: str | None = None
    guides: dict[str, Any] | None = None
    try:
        ssot_bytes = path.read_bytes()
    except OSError as exc:
        errors.append(
            _resolver_error_record(exc, variant_id=None, styleguide=None, ssot_path=path)
        )
    if ssot_bytes is not None:
        ssot_digest = hashlib.sha256(ssot_bytes).hexdigest()
        try:
            guides = load_style_guides(path, content=ssot_bytes).get("style_guides", {})
        except Exception as exc:  # noqa: BLE001 — total by contract, never raise
            errors.append(
                _resolver_error_record(
                    exc, variant_id=None, styleguide=None, ssot_path=path
                )
            )

    # T2/T3: normalize + validate picks; every invalid pick is RECORDED, never
    # silently reclassified (a present-but-bad pick is not "no picks").
    picks: list[tuple[str, str]] = []
    pick_attempted = False
    seen_variants: set[str] = set()
    for entry in entries or []:
        if not isinstance(entry, dict) or "styleguide" not in entry:
            continue  # inline-settings entry: echoed via input_picks, not a pick
        pick_attempted = True
        raw_name = entry.get("styleguide")
        raw_variant = entry.get("variant_id")
        if not isinstance(raw_name, str) or not raw_name.strip():
            errors.append(
                _pick_error_record(
                    variant_id=raw_variant,
                    styleguide=raw_name,
                    tag="cd.styleguide_resolution.invalid-pick-name",
                    message=(
                        "pick styleguide must be a non-empty string; got "
                        f"{raw_name!r}"
                    ),
                )
            )
            continue
        variant = str(raw_variant).strip().upper() if raw_variant is not None else ""
        if variant not in _PICK_VARIANT_VOCABULARY:
            errors.append(
                _pick_error_record(
                    variant_id=raw_variant,
                    styleguide=raw_name,
                    tag="cd.styleguide_resolution.invalid-variant-id",
                    message=(
                        f"pick variant_id {raw_variant!r} is outside the picker "
                        f"vocabulary {sorted(_PICK_VARIANT_VOCABULARY)} after "
                        "normalization"
                    ),
                )
            )
            continue
        if variant in seen_variants:
            errors.append(
                _pick_error_record(
                    variant_id=raw_variant,
                    styleguide=raw_name,
                    tag="cd.styleguide_resolution.variant-collision",
                    message=(
                        f"post-normalization variant_id collision on {variant!r} "
                        "— a later pick would silently overwrite an earlier "
                        "resolution (last-wins forbidden)"
                    ),
                )
            )
            continue
        seen_variants.add(variant)
        picks.append((variant, raw_name.strip()))

    resolved: dict[str, Any] = {}
    bound_guides: list[dict[str, Any]] = []
    default_provenance: str | None = None

    if guides is not None:
        for variant, name in picks:
            try:
                resolved[variant] = resolve_styleguide(name, guides=guides)
                bound_guides.append(
                    _bound_guide_entry(name, guides.get(name), ssot_digest)
                )
            except Exception as exc:  # noqa: BLE001 — total by contract
                errors.append(
                    _resolver_error_record(
                        exc, variant_id=variant, styleguide=name, ssot_path=path
                    )
                )

    if pick_attempted:
        input_picks: dict[str, Any] | None = {
            "gamma_settings": entries,
            "styleguide_picker_provenance": provenance,
        }
        status = "resolved" if not errors else "unresolvable_pick"
    else:
        # T3: entries (even pick-less inline-settings ones) are still echoed.
        input_picks = (
            {"gamma_settings": entries, "styleguide_picker_provenance": provenance}
            if entries is not None
            else None
        )
        if guides is not None:
            try:
                resolved["A"] = resolve_styleguide(DEFAULT_STYLEGUIDE_NAME, guides=guides)
                bound_guides.append(
                    _bound_guide_entry(
                        DEFAULT_STYLEGUIDE_NAME,
                        guides.get(DEFAULT_STYLEGUIDE_NAME),
                        ssot_digest,
                    )
                )
            except Exception as exc:  # noqa: BLE001 — total by contract
                errors.append(
                    _resolver_error_record(
                        exc,
                        variant_id="A",
                        styleguide=DEFAULT_STYLEGUIDE_NAME,
                        ssot_path=path,
                    )
                )
        # T4: no_picks_at_authoring may only assert a binding that HAPPENED;
        # any SSOT-load or default-resolve failure ⇒ unresolvable_pick with
        # default_provenance null (the default did not bind).
        if errors:
            status = "unresolvable_pick"
        else:
            status = "no_picks_at_authoring"
            default_provenance = DEFAULT_STYLEGUIDE_PROVENANCE

    return {
        "schema_version": STYLEGUIDE_RESOLUTION_SCHEMA_VERSION,
        "status": status,
        "input_picks": input_picks,
        "bound_guides": bound_guides,
        "resolved": resolved,
        "layering_manifest": dict(_LAYERING_MANIFEST),
        # Canonical-arc S3 D2a: the digest algorithm lives in the SHARED
        # app.styleguide.parity.canonical_resolution_digest (byte-identical
        # extraction of the former private _canonical_json + sha256) so CD's
        # emission and Gary's shadow comparator can never digest differently.
        "resolution_digest": canonical_resolution_digest(resolved),
        "directive_digest": directive_digest,
        "default_provenance": default_provenance,
        # T7: ALL failures recorded, in pick order (schema still v1 pre-commit).
        "errors": errors,
    }


def _parse_cd_directive(raw_content: Any) -> dict[str, Any]:
    excerpt = _raw_excerpt(raw_content)
    parsed: Any
    if isinstance(raw_content, dict):
        parsed = raw_content
    elif isinstance(raw_content, str):
        text = _extract_json_text(raw_content)
        if not text:
            raise CdDirectiveParseError(
                "cd directive cannot be empty",
                tag="cd_directive.parsed.empty",
            )
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise CdDirectiveParseError(
                f"cd directive parse failed: {exc}; raw response excerpt: "
                f"{excerpt}",
                tag="cd_directive.parsed.malformed",
                raw_excerpt=excerpt,
            ) from exc
    else:
        raise CdDirectiveParseError(
            "cd directive must be string-or-mapping",
            tag="cd_directive.parsed.wrong-type",
        )

    if not isinstance(parsed, dict):
        raise CdDirectiveParseError(
            "cd directive payload must be a mapping",
            tag="cd_directive.parsed.wrong-type",
            raw_excerpt=excerpt,
        )

    directive = parsed.get("cd_directive", parsed)
    if not isinstance(directive, dict):
        raise CdDirectiveParseError(
            "cd directive value must be a mapping",
            tag="cd_directive.parsed.wrong-type",
            raw_excerpt=excerpt,
        )
    if not directive:
        raise CdDirectiveParseError(
            "cd directive cannot be empty",
            tag="cd_directive.parsed.empty",
            raw_excerpt=excerpt,
        )

    canonical = _canonicalize_cd_directive(directive, raw_excerpt=excerpt)
    errors = validate_creative_directive(canonical)
    if errors:
        raise CdDirectiveParseError(
            "cd directive validator failed after deterministic "
            f"canonicalization — schema vs experience-profiles config drift? "
            f"errors: {errors}; raw response excerpt: {excerpt}",
            tag="cd_directive.parsed.validator-failed",
            errors=errors,
            raw_excerpt=excerpt,
        )

    return {
        "tag": "cd_directive.parsed.ok",
        "cd_directive": canonical,
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="cd",
        temperature=state.temperature,
        tier_request="fast",
    )
    _ = _read_sanctum_digest()
    _ = _read_cd_references()
    assert_sanctum_lock()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("cd act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "cd act expected final plan resolution entry with cache_prefix_hash"
        )

    try:
        envelope_payload = _decode_envelope_payload(state)
    except CdDirectiveParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    extracted_source = read_extracted_source(envelope_payload)
    # Canonical-arc S1: the directive_projection is DETERMINISTIC-NECK input
    # only — stripped from the LLM prompt (irene_pass1 payload-strip precedent)
    # so the creative surface stays byte-identical and the LLM structurally
    # cannot touch resolution (AC-1).
    prompt_payload = {
        key: value
        for key, value in envelope_payload.items()
        if key != "directive_projection"
    }
    system_message, user_message = _assemble_cd_prompt(
        prompt_payload, extracted_source=extracted_source
    )
    try:
        handle = make_chat_model(
            specialist_id="cd",
            temperature=state.temperature,
            tier_request="fast",
            system_prompt_hash=last_entry.cache_prefix_hash,
        )
        response = handle.chat.invoke(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ]
        )
        raw_content = response.content if hasattr(response, "content") else str(response)
        parsed = _parse_cd_directive(raw_content)
    except CdDirectiveParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = CdDirectiveParseError(
            "cd model invocation failed",
            tag="cd_directive.parsed.malformed",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc

    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "cd_directive": parsed["cd_directive"],
            # Canonical-arc S1 (D3): deterministic SIBLING block — never inside
            # the load-bearing cd_directive (§06 flow FENCED, AC-3).
            "styleguide_resolution": _styleguide_resolution_from_projection(
                envelope_payload.get("directive_projection")
            ),
            "model_id": last_entry.resolved,
            "usage": getattr(response, "usage_metadata", None),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "cd-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_cd_graph() -> StateGraph:
    graph = StateGraph(state_schema=RunState)
    graph.add_node("receive", _receive)
    graph.add_node("plan", _plan)
    graph.add_node("act", _act)
    graph.add_node("verify", _verify)
    graph.add_node("reflect", _reflect)
    graph.add_node("emit_spans", _emit_spans)
    graph.add_node("gate_decision", _gate_decision)
    graph.add_node("finalize", _finalize)
    graph.add_node("handoff", _handoff)
    graph.add_edge(START, "receive")
    for src, dst in TRANSITIONS:
        graph.add_edge(src, dst)
    graph.add_edge("handoff", END)

    present = frozenset(graph.nodes.keys())
    if present != SCAFFOLD_NODE_IDS:
        missing = sorted(SCAFFOLD_NODE_IDS - present)
        extra = sorted(present - SCAFFOLD_NODE_IDS)
        raise RuntimeError(f"generated scaffold drift for cd; missing={missing} extra={extra}")
    return graph


__all__ = [
    "CD_REFERENCES",
    "CD_SANCTUM_LOCK_BASELINE",
    "DEFAULT_STYLEGUIDE_NAME",
    "DEFAULT_STYLEGUIDE_PROVENANCE",
    "STYLEGUIDE_RESOLUTION_SCHEMA_VERSION",
    "CdDirectiveParseError",
    "SANCTUM_DIR",
    "TRANSITIONS",
    "_act",
    "_current_sanctum_manifest",
    "_parse_cd_directive",
    "_plan",
    "_read_cd_references",
    "_read_sanctum_digest",
    "_styleguide_resolution_from_projection",
    "assert_sanctum_lock",
    "build_cd_graph",
    "validate_creative_directive",
]
