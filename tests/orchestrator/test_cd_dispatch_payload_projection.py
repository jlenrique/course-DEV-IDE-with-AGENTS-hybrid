"""Canonical-arc S1 D2 — orchestrator-side `directive_projection` at §4.75.

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s1-cd-styleguide-resolution-emission.md`
(RED-5, AC-5/D2).

Wiring altitude (F-203, binding): the projection is supplied by ONE `cd`
branch in `_runner_payload_for_specialist` — the single seam BOTH walk bodies
reach through the shared `_dispatch_specialist_at_node`. No per-walk wiring.
The directive here is patched by the REAL `write_pick_to_directive` (the S2
producer's write shape), so the projection is pinned against the true
directive format, not a hand-rolled imitation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.styleguide_picker import write_pick_to_directive
from app.specialists.dispatch_errors import SpecialistDispatchError

DEFAULT_GUIDE = "hil-2026-apc-crossroads-classic"


def _seed_directive(tmp_path: Path) -> Path:
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "test-run",
                "sources": [
                    {
                        "ref_id": "src-001",
                        "provider": "local_file",
                        "locator": "corpus/intro.md",
                        "role": "primary",
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return directive


def test_475_payload_carries_directive_projection(tmp_path: Path) -> None:
    directive = _seed_directive(tmp_path)
    write_pick_to_directive(directive, {"A": DEFAULT_GUIDE})
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))

    payload = production_runner._runner_payload_for_specialist(
        specialist_id="cd",
        directive_path=directive,
        bundle_dir=None,
    )

    assert payload is not None, "cd received no runner payload — D2 branch missing"
    assert set(payload) == {"directive_projection"}
    projection = payload["directive_projection"]
    # gamma_settings VERBATIM from the run's directive.yaml (picker-patched).
    assert projection["gamma_settings"] == loaded["gamma_settings"]
    assert projection["gamma_settings"][0]["styleguide"] == DEFAULT_GUIDE
    # styleguide_picker_provenance VERBATIM block (present on a picked run).
    assert (
        projection["styleguide_picker_provenance"]
        == loaded["styleguide_picker_provenance"]
    )
    # directive_digest = sha256 of the directive file bytes (the :852-854 pattern).
    assert projection["directive_digest"] == hashlib.sha256(
        directive.read_bytes()
    ).hexdigest()


def test_no_directive_yields_no_projection(tmp_path: Path) -> None:
    assert (
        production_runner._runner_payload_for_specialist(
            specialist_id="cd", directive_path=None, bundle_dir=None
        )
        is None
    )
    assert (
        production_runner._runner_payload_for_specialist(
            specialist_id="cd",
            directive_path=tmp_path / "missing-directive.yaml",
            bundle_dir=None,
        )
        is None
    )


def test_provenance_key_absent_when_directive_carries_none(tmp_path: Path) -> None:
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {"gamma_settings": [{"variant_id": "A", "styleguide": DEFAULT_GUIDE}]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    payload = production_runner._runner_payload_for_specialist(
        specialist_id="cd", directive_path=directive, bundle_dir=None
    )
    assert payload is not None
    projection = payload["directive_projection"]
    assert "styleguide_picker_provenance" not in projection
    assert projection["gamma_settings"] == [
        {"variant_id": "A", "styleguide": DEFAULT_GUIDE}
    ]
    assert projection["directive_digest"] == hashlib.sha256(
        directive.read_bytes()
    ).hexdigest()


def test_directive_without_gamma_settings_projects_null_picks(tmp_path: Path) -> None:
    """A composed-but-unpicked directive still projects (digest + null picks)
    so CD emits an honest `no_picks_at_authoring` presence record."""
    directive = _seed_directive(tmp_path)
    payload = production_runner._runner_payload_for_specialist(
        specialist_id="cd", directive_path=directive, bundle_dir=None
    )
    assert payload is not None
    projection = payload["directive_projection"]
    assert projection["gamma_settings"] is None
    assert projection["directive_digest"] == hashlib.sha256(
        directive.read_bytes()
    ).hexdigest()


# --- T1 remediation (review finding, HIGH): a bad directive at the cd seam
# must NEVER crash the walk un-persisted. Read-once + guarded: any read /
# decode / parse failure raises into the SpecialistDispatchError family
# (`cd.directive.*` tag) so BOTH walkers' `except SpecialistDispatchError`
# routes it through `_pause_at_error` recoverably (the AssetResolutionError /
# CoverageAssuranceError precedent).


def test_unreadable_directive_raises_recoverable_dispatch_error(tmp_path: Path) -> None:
    """T1 RED shape: non-UTF-8 directive bytes previously escaped as a bare
    UnicodeDecodeError past the walkers' SpecialistDispatchError catch."""
    directive = tmp_path / "directive.yaml"
    directive.write_bytes(b"\xff\xfe\x00 not-utf8 \x9c\x9d")
    with pytest.raises(SpecialistDispatchError) as excinfo:
        production_runner._runner_payload_for_specialist(
            specialist_id="cd", directive_path=directive, bundle_dir=None
        )
    assert excinfo.value.tag == "cd.directive.unreadable"


def test_malformed_yaml_directive_raises_recoverable_dispatch_error(
    tmp_path: Path,
) -> None:
    """T1 RED shape: a YAML ParserError previously escaped the seam bare."""
    directive = tmp_path / "directive.yaml"
    directive.write_text("gamma_settings: [", encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as excinfo:
        production_runner._runner_payload_for_specialist(
            specialist_id="cd", directive_path=directive, bundle_dir=None
        )
    assert excinfo.value.tag == "cd.directive.malformed"


def test_projection_reads_directive_once_settings_and_provenance_same_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T1: the cd branch reads the directive ONCE — bytes -> digest -> parse of
    the SAME bytes for settings AND provenance (no TOCTOU between the three)."""
    directive = _seed_directive(tmp_path)
    write_pick_to_directive(directive, {"A": DEFAULT_GUIDE})
    real_read_bytes = Path.read_bytes
    calls: list[str] = []

    def _counting_read_bytes(self: Path) -> bytes:
        if self == directive:
            calls.append(str(self))
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _counting_read_bytes)
    real_read_text = Path.read_text

    def _counting_read_text(self: Path, *args: object, **kwargs: object) -> str:
        if self == directive:
            calls.append(str(self))
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _counting_read_text)
    payload = production_runner._runner_payload_for_specialist(
        specialist_id="cd", directive_path=directive, bundle_dir=None
    )
    assert payload is not None
    assert len(calls) == 1, (
        f"cd seam read the directive {len(calls)} times — must be read ONCE "
        "(digest + settings + provenance from the same bytes)"
    )


def test_seam_docstring_enumerates_directive_projection() -> None:
    """D2 requires the seam docstring's runner-context enumeration to name
    `directive_projection` (never silently ignore the 'content delivery
    forbidden' clause — directive-derived styleguide context is chartered
    runner context per the gary gamma_settings precedent)."""
    doc = production_runner._runner_payload_for_specialist.__doc__ or ""
    assert "directive_projection" in doc
