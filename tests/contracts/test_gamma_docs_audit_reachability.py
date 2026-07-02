"""Leg-E D-2 reachability pin + SSOT write-guards (Murat M-3 / M-4).

Pins, in order:
1. The audit driver resolves the `gamma_docs` adapter THROUGH
   `provider_directory` dispatch — NEVER direct class instantiation
   (static + behavioral, non-vacuous both ways).
2. The driver is the SOLE module that may write
   `GAMMA_LEARNED_OBSERVATIONS_PATH` (static scan over app/ scripts/ skills/).
3. M-4 static guard: no test module may append to the REAL observations-ledger
   constant anywhere under tests/ (all ledger tests are tmp_path-only, AC#6).
"""

from __future__ import annotations

import re
from pathlib import Path

import responses

REPO_ROOT = Path(__file__).resolve().parents[2]
DRIVER_PATH = REPO_ROOT / "scripts" / "utilities" / "audit_gamma_docs.py"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval" / "gamma_docs"

IMAGE_MODELS_URL = "https://developers.gamma.app/reference/image-model-accepted-values.md"


# ---------------------------------------------------------------------------
# 1. D-2 — driver goes through provider_directory dispatch
# ---------------------------------------------------------------------------


def test_driver_exists_and_never_names_the_adapter_class() -> None:
    """Static half of D-2: the driver source may not touch GammaDocsProvider."""
    assert DRIVER_PATH.exists(), (
        "scripts/utilities/audit_gamma_docs.py missing (Leg-E AC#4)"
    )
    source = DRIVER_PATH.read_text(encoding="utf-8")
    assert "GammaDocsProvider" not in source, (
        "D-2 reachability pin: the driver must resolve the adapter THROUGH "
        "provider_directory dispatch (RetrievalIntent + retrieval.dispatch), "
        "never by naming/instantiating the class"
    )
    # Positive witness that the dispatch path is what the driver uses.
    assert "RetrievalIntent" in source and "dispatch" in source
    assert 'kind="direct_ref"' in source


def test_driver_fetch_resolves_adapter_through_registry() -> None:
    """Behavioral half of D-2, non-vacuous in BOTH directions.

    (a) with the registry intact, the driver's page fetch produces a
        gamma_docs TexasRow for a mocked real URL;
    (b) with the registry cleared, the SAME call degrades to a transport-class
        failure whose error names the missing registration — proving the
        adapter really is resolved via provider_directory, not held directly.
    The autouse registry snapshot fixture (tests/conftest.py) restores state.
    """
    from retrieval.provider_directory import reset_adapter_registry

    from scripts.utilities import audit_gamma_docs as audit

    body = (FIXTURE_DIR / "image_model_accepted_values.md").read_bytes()

    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, body=body)
        page = audit.fetch_page(IMAGE_MODELS_URL, fetch_interval_s=0.0)
    assert page["ok"] is True
    assert page["row"] is not None
    assert page["row"].provider == "gamma_docs"
    assert page["row"].source_id == IMAGE_MODELS_URL

    reset_adapter_registry()
    page2 = audit.fetch_page(IMAGE_MODELS_URL, fetch_interval_s=0.0)
    assert page2["ok"] is False
    assert page2["row"] is None
    assert "No RetrievalAdapter registered" in (page2["error"] or ""), (
        "with the registry cleared the driver must fail through the dispatch "
        "resolution path — anything else means it holds the adapter directly"
    )


# ---------------------------------------------------------------------------
# 2. M-3 — driver is the sole GAMMA_LEARNED_OBSERVATIONS_PATH writer
# ---------------------------------------------------------------------------

_ALLOWED_SSOT_MODULES = {
    # Defines the constant + the append primitive (Leg-B2 store module).
    "app/specialists/gary/learned_dependencies.py",
    # The ONLY writer (Leg-E AC#5 / Murat M-3).
    "scripts/utilities/audit_gamma_docs.py",
}


def _py_files(*roots: str) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        base = REPO_ROOT / root
        if base.exists():
            out.extend(
                p for p in base.rglob("*.py") if "__pycache__" not in p.parts
            )
    return out


def test_driver_is_sole_ledger_writer_static_scan() -> None:
    offenders: list[str] = []
    for path in _py_files("app", "scripts", "skills"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if (
            "append_observation" in text
            and "GAMMA_LEARNED_OBSERVATIONS_PATH" in text
            and rel not in _ALLOWED_SSOT_MODULES
        ):
            offenders.append(rel)
    assert not offenders, (
        "modules referencing BOTH append_observation and "
        f"GAMMA_LEARNED_OBSERVATIONS_PATH outside the allowed set: {offenders} "
        "(Murat M-3: audit_gamma_docs.py is the SOLE ledger writer)"
    )
    # Non-vacuous: the allowed writers actually exist on disk.
    for rel in _ALLOWED_SSOT_MODULES:
        assert (REPO_ROOT / rel).exists(), f"expected SSOT module missing: {rel}"


# ---------------------------------------------------------------------------
# 3. M-4 — no test may append to the real ledger (tmp_path-only, AC#6)
# ---------------------------------------------------------------------------


def test_no_test_appends_to_real_observations_ledger() -> None:
    """Guard-of-absence (born green by design, disclosed in the Leg-E RED log)."""
    # Assemble the tokens at runtime so this guard cannot trip on its own source.
    func_name = "append_" + "observation"
    const_name = "GAMMA_LEARNED_" + "OBSERVATIONS_PATH"
    pattern = re.compile(re.escape(func_name) + r"\(\s*" + re.escape(const_name))
    offenders: list[str] = []
    for path in _py_files("tests"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert not offenders, (
        f"tests writing to the REAL observations ledger: {offenders} "
        "(AC#6: all ledger tests are tmp_path-only)"
    )


def _call_span(text: str, open_paren_index: int, cap: int = 4000) -> str:
    """Best-effort balanced-paren span from an opening '(' (test-source scan)."""
    depth = 0
    end = min(len(text), open_paren_index + cap)
    for i in range(open_paren_index, end):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren_index : i + 1]
    return text[open_paren_index:end]


def test_every_test_run_audit_call_pins_a_ledger_path() -> None:
    """N4 hardening of the M-4 guard (guard-of-absence, born green by design):
    any tests/ call of the driver's run-audit entrypoint MUST pass an explicit
    `ledger_path=` kwarg — the parameter's default is the REAL SSOT ledger
    (AC#6: all ledger tests are tmp_path-only)."""
    call_token = "run_" + "audit("  # assembled so this guard cannot self-trip
    kwarg_token = "ledger_path"
    offenders: list[str] = []
    for path in _py_files("tests"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(re.escape(call_token), text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            prefix = text[line_start : match.start()].lstrip()
            if prefix.startswith("def ") or prefix.startswith("#"):
                continue
            span = _call_span(text, match.end() - 1)
            if kwarg_token not in span:
                line_no = text.count("\n", 0, match.start()) + 1
                offenders.append(
                    f"{path.relative_to(REPO_ROOT).as_posix()}:{line_no}"
                )
    assert not offenders, (
        f"tests calling the audit driver without an explicit ledger_path= "
        f"(default = the REAL SSOT ledger): {offenders} (AC#6 / N4)"
    )
