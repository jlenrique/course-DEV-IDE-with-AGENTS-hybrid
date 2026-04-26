from __future__ import annotations

import pytest

from app.gates.errors import SchedulerImportError
from app.gates.guardrails import assert_no_scheduler_or_bypass_source


@pytest.mark.parametrize(
    "source",
    [
        "import threading\n",
        "import apscheduler\n",
        "import schedule\n",
        "import asyncio\nasyncio.sleep(0)\n",
    ],
)
def test_no_scheduler_import(source: str) -> None:
    with pytest.raises(SchedulerImportError):
        assert_no_scheduler_or_bypass_source(source, source_name="synthetic_violation.py")
