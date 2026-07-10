"""LiteLLM Batch transport package (Marcus-SPOC).

Research (binding):
``_bmad-output/planning-artifacts/research/technical-litellm-batch-hookup-research-2026-07-10.md``

**Naming trap (MUST):** the cost-savings product path is the provider **Batch API**
via LiteLLM Files + Batches SDK (``create_file`` / ``create_batch`` / retrieve /
``file_content``), with ``custom_llm_provider="openai"`` first and endpoint
``/v1/chat/completions`` for multimodal perception rows.

``litellm.batch_completion`` is a **parallel synchronous** helper — it is **not**
the Batch API and must **never** be used as the product "batch mode" path (B1+).

**Prior live evidence (brief — mine):** OpenAI Batch already produced **good PNG
reads** — ``batch_6a457bcac6488190b79224e61ea89b26`` (``gpt-4.1-mini``, 2/2 usable
JSON). Provider quality baseline only. Product batch model = realtime ``gpt-5.5``
(or nearest GPT-5-family Batch-available member). Dispatch via this package —
kwargs/receipts may differ from the scratchpad raw-OpenAI client.
"""

from __future__ import annotations

from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter
from app.runtime.llm_batch.errors import LlmBatchError, WaitingForProviderBatchError
from app.runtime.llm_batch.join import JoinedBatchRow, JoinResult, join_output_rows
from app.runtime.llm_batch.jsonl import (
    DEFAULT_MAX_JSONL_BYTES,
    encode_batch_jsonl,
    make_chat_completions_row,
)
from app.runtime.llm_batch.receipts import BatchReceipt, read_receipt, write_receipt

__all__ = [
    "BatchReceipt",
    "DEFAULT_MAX_JSONL_BYTES",
    "JoinResult",
    "JoinedBatchRow",
    "LiteLlmBatchAdapter",
    "LlmBatchError",
    "WaitingForProviderBatchError",
    "encode_batch_jsonl",
    "join_output_rows",
    "make_chat_completions_row",
    "read_receipt",
    "write_receipt",
]
