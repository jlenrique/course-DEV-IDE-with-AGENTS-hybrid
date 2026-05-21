"""HTTP bridge for gate verdict and override flow."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import ValidationError

from app.gates import GateError
from app.gates.resume_api import build_transport_response, resume_from_verdict
from app.gates.verdict import OperatorVerdict
from app.runtime.override_api import (
    OverrideTokenStaleError,
    apply_override,
    decision_card_meta_for_trial,
    submit_override,
)


def gate_verdict_endpoint(payload: dict[str, Any], *, operator_id: str) -> dict[str, Any]:
    verdict = OperatorVerdict.model_validate({**payload, "operator_id": operator_id})
    command = resume_from_verdict(verdict)
    response = build_transport_response(
        command=command,
        verdict=verdict,
        transport_kind="http",
    )
    return response


def gate_override_submit_endpoint(payload: dict[str, Any], *, operator_id: str) -> dict[str, Any]:
    warning = submit_override(
        trial_id=payload["trial_id"],
        node_id=payload["node_id"],
        new_model=payload["new_model"],
    )
    return {
        "status": "warning",
        "warning": warning.model_dump(mode="json"),
        "operator_id": operator_id,
        "transport_kind": "http",
    }


def gate_override_apply_endpoint(payload: dict[str, Any], *, operator_id: str) -> dict[str, Any]:
    event = apply_override(
        {
            "trial_id": payload["trial_id"],
            "node_id": payload["node_id"],
            "new_model": payload["new_model"],
            "operator_id": operator_id,
        },
        str(payload["confirm_token"]),
    )
    trial_id = payload["trial_id"]
    return {
        "status": "accepted",
        "override_event": event.model_dump(mode="json"),
        "decision_card_meta": decision_card_meta_for_trial(trial_id).model_dump(mode="json"),
        "transport_kind": "http",
    }


def create_gate_app() -> FastAPI:
    app = FastAPI(title="gate verdict endpoint", version="0.1.0-slab3")

    @app.post("/gate/verdict")
    def post_gate_verdict(
        payload: dict[str, Any],
        x_operator_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if not x_operator_id:
            raise HTTPException(status_code=400, detail="missing X-Operator-Id header")
        try:
            return gate_verdict_endpoint(payload, operator_id=x_operator_id)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except GateError as exc:
            if exc.code == "digest_mismatch":
                raise HTTPException(status_code=409, detail=exc.message) from exc
            raise HTTPException(status_code=400, detail=exc.message) from exc

    @app.post("/gate/override/submit")
    def post_gate_override_submit(
        payload: dict[str, Any],
        x_operator_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if not x_operator_id:
            raise HTTPException(status_code=400, detail="missing X-Operator-Id header")
        try:
            return gate_override_submit_endpoint(payload, operator_id=x_operator_id)
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"missing field: {exc.args[0]}") from exc

    @app.post("/gate/override/apply")
    def post_gate_override_apply(
        payload: dict[str, Any],
        x_operator_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if not x_operator_id:
            raise HTTPException(status_code=400, detail="missing X-Operator-Id header")
        try:
            return gate_override_apply_endpoint(payload, operator_id=x_operator_id)
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"missing field: {exc.args[0]}") from exc
        except OverrideTokenStaleError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return app


__all__ = [
    "create_gate_app",
    "gate_override_apply_endpoint",
    "gate_override_submit_endpoint",
    "gate_verdict_endpoint",
]
