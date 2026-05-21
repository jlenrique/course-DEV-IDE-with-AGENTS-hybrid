"""CLI bridge helpers for gate verdict and override flow."""

from app.marcus.cli.adhoc_cli import adhoc_ask_cli, run_adhoc_ask
from app.marcus.cli.gate_cli import (
    gate_decide_cli,
    main,
    override_apply_cli,
    override_submit_cli,
    run_gate_decide,
    run_override_apply,
    run_override_submit,
)
from app.marcus.cli.trial import start_trial, start_trial_cli

__all__ = [
    "adhoc_ask_cli",
    "gate_decide_cli",
    "main",
    "override_apply_cli",
    "override_submit_cli",
    "run_gate_decide",
    "run_adhoc_ask",
    "run_override_apply",
    "run_override_submit",
    "start_trial",
    "start_trial_cli",
]
