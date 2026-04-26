import pytest


def test_orchestrator_agent_skill_path():
    """
    BMAD System-Level Acceptance Test:
    Validates orchestrator → agent → skill → script happy path produces expected artifact(s).
    """
    # This is a placeholder for the integration harness call e.g. subprocess/run module invocation
    # Replace with exact orchestrator entry once modularized for test harness consumption.
    try:
        import os
        import subprocess
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{root}{os.pathsep}{env.get('PYTHONPATH', '')}"

        result = subprocess.run(
            [ "python", "scripts/utilities/app_session_readiness.py", "--with-preflight" ],
            capture_output=True,
            text=True,
            cwd=root,
            env=env,
        )
        assert result.returncode == 0, f"Non-zero exit code; stderr: {result.stderr}"
        assert (
            "Session ready" in result.stdout
            or "Ready" in result.stdout
            or "OVERALL: PASS" in result.stdout
        ), "Expected readiness signal not found."
    except Exception as e:
        pytest.fail(f"System-level agent/skill integration failed: {e}")
